#!/usr/bin/env python3
"""The GermOS relay - the door on the switch, in front of the frozen broker.

On the metal the guest ARPs for 10.0.2.4 on the home LAN and mlrig's LAN
port answers; this relay is what listens there. It binds exactly 10.0.2.4
(the switch) or 127.0.0.1 (the twin) and nothing else, and forwards each
connection, bytes unchanged both ways, to the frozen broker on
127.0.0.1:<broker-port>. The broker's own bind stays 127.0.0.1 and frozen.
stage7/WIRE.md, "The relay", is the contract; stage7/checkwire.py holds
it to that contract. This file is deliberately NOT frozen (the spec's
word): it is a tool, and a bent relay is a red gate, not a bent criterion.

Usage:
    python3 broker/relay.py                              # the HP's day: 10.0.2.4:9999 -> 127.0.0.1:9999
    python3 broker/relay.py --bind 127.0.0.1 --port 9997 # the twin
    python3 broker/relay.py --bind 127.0.0.1 --port 9997 --log stage7/out/wire/relay.jsonl

Prints "relay listening on <addr>:<port> -> 127.0.0.1:<broker-port>" to
stdout once bound, so a harness can wait for exactly that line. Exits 2
with a message before any socket exists when --bind is neither address;
exits 2 when the host refuses the bind. Standard library only.

One connection is served at a time (the broker's own discipline). Once the
broker has finished - its close forwarded to the guest as a FIN - the
guest is given GRACE seconds to close its side; a guest that dies
mid-connection without closing (a machine powered off on the day) is then
closed from here, so it never holds the relay (ring 7c, plan-7c.md
decision 5). The exchange was complete, so the log line's error is null.
"""

import argparse
import json
import socket
import sys
import threading
import time

ALLOWED = ("10.0.2.4", "127.0.0.1")
BROKER_HOST = "127.0.0.1"
DEFAULT_BIND = "10.0.2.4"
DEFAULT_PORT = 9999
DEFAULT_BROKER_PORT = 9999
CHUNK = 65536
GRACE = 2.0     # seconds the guest may hold its side open after the broker has finished (ring 7c)


def log(msg):
    sys.stderr.write("relay: %s\n" % msg)
    sys.stderr.flush()


def quiet(fn, *args):
    """A shutdown or close on a socket whose peer has gone must never raise."""
    try:
        fn(*args)
    except OSError:
        pass


def pump(src, dst, counter, key, done):
    """Copy src -> dst until EOF, counting bytes; then tell dst there is no more."""
    try:
        while True:
            data = src.recv(CHUNK)
            if not data:
                break
            dst.sendall(data)
            counter[key] += len(data)
    except OSError:
        pass
    finally:
        quiet(dst.shutdown, socket.SHUT_WR)
        done.set()


class Log:
    def __init__(self, path):
        self.path = path
        self.fh = open(path, "a") if path else None

    def add(self, t, peer, up, down, error):
        if self.fh is None:
            return
        self.fh.write(json.dumps({"t": t, "peer": peer, "up": up, "down": down, "error": error}) + "\n")
        self.fh.flush()


def handle(conn, peer, broker_port, logfile):
    t0 = time.time()
    peer_text = "%s:%d" % peer
    counter = {"up": 0, "down": 0}
    error = None
    broker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        broker.settimeout(5.0)
        broker.connect((BROKER_HOST, broker_port))
        broker.settimeout(None)
    except OSError as exc:
        error = "broker refused: %s" % exc
        log("%s: %s" % (peer_text, error))
        quiet(broker.close)
        quiet(conn.close)
        logfile.add(t0, peer_text, counter["up"], counter["down"], error)
        return
    up_done, down_done = threading.Event(), threading.Event()
    t_up = threading.Thread(target=pump, args=(conn, broker, counter, "up", up_done), daemon=True)
    t_down = threading.Thread(target=pump, args=(broker, conn, counter, "down", down_done), daemon=True)
    t_up.start()
    t_down.start()
    t_down.join()                       # the broker has finished: its bytes are forwarded, the guest side has SHUT_WR
    if not up_done.wait(GRACE):
        # Ring 7c (plan-7c.md decision 5): a guest that dies mid-connection
        # without closing would hold this one-connection-at-a-time relay
        # for ever. The exchange is complete - the guest has its whole
        # answer - so after the grace the guest side is closed here, the
        # up pump's recv ends, and the next connection is served. Not an
        # error: the log line carries the bytes as counted and error null.
        log("%s: the guest did not close within %.0f s of the broker's end - closing its side" % (peer_text, GRACE))
        quiet(conn.shutdown, socket.SHUT_RDWR)
        quiet(conn.close)
    t_up.join()
    quiet(broker.close)
    quiet(conn.close)
    log("%s: %d bytes up, %d bytes down in %.1f s" % (peer_text, counter["up"], counter["down"], time.time() - t0))
    logfile.add(t0, peer_text, counter["up"], counter["down"], error)


def serve(bind, port, broker_port, logfile):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # TIME_WAIT only; never two listeners
    try:
        srv.bind((bind, port))
    except OSError as exc:
        log("cannot bind %s:%d (%s)" % (bind, port, exc))
        return 2
    srv.listen(1)
    sys.stdout.write("relay listening on %s:%d -> %s:%d\n" % (bind, port, BROKER_HOST, broker_port))
    sys.stdout.flush()
    try:
        while True:
            conn, peer = srv.accept()
            handle(conn, peer, broker_port, logfile)
    except KeyboardInterrupt:
        log("stopped")
    finally:
        quiet(srv.close)
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS relay (stage7/WIRE.md, the relay).")
    ap.add_argument("--bind", default=DEFAULT_BIND, help="the address to listen on: 10.0.2.4 or 127.0.0.1 only (default 10.0.2.4)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help="the port to listen on (default 9999)")
    ap.add_argument("--broker-port", type=int, default=DEFAULT_BROKER_PORT, help="the frozen broker's port on 127.0.0.1 (default 9999)")
    ap.add_argument("--log", default=None, help="append one JSON line per connection to this file")
    args = ap.parse_args(argv)
    if args.bind not in ALLOWED:
        sys.stderr.write("relay: refusing to bind %s - only 10.0.2.4 (the switch) or 127.0.0.1 (the twin)\n" % args.bind)
        sys.stderr.flush()
        return 2
    return serve(args.bind, args.port, args.broker_port, Log(args.log))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
