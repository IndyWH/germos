#!/usr/bin/env python3
"""The GermOS probe - the chart with a way back in (Stage 7 ring 7c, item
20, the serial monitor's tool on mlrig).

It does what broker/chart.py does - reads the HP's serial port at 115200
8N1, prints every line as it arrives and tees it to a log file with a
timestamp - and it also listens on 127.0.0.1:9995 for one client at a
time: every line the client sends goes to the serial port, and every line
the port sends goes to the client as well as to the log. So once the
guest's serial monitor has answered "mon: ready" after a transmit timeout,
a Claude Code session drives the investigation through that socket -
questions over the wire, many per boot, with no flash between them. The
client's own lines are logged too, marked "> ", so the log reads as the
dialogue. Standard library only. Unfrozen: a tool, not a criterion.

Usage:
    python3 broker/probe.py <serial port> <log file>

The port is argv[1], the adapter's port exactly as chart.py names it
(stage7/METAL.md, step 5); no path is spelled here. Start it in place of
the chart, BEFORE the HP is powered on. Ctrl-C ends it with the file
complete; a port or a log that cannot be opened is a loud exit 2. The
port's open is chart.py's own (non-blocking first, CLOCAL, then blocking).
"""

import os
import socket
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart import open_port, stamp  # noqa: E402

HOST = "127.0.0.1"
PORT = 9995


class Probe:
    def __init__(self, fd, log):
        self.fd = fd
        self.log = log
        self.lock = threading.Lock()
        self.client = None

    def emit(self, raw):
        """A line from the port: the terminal, the log, the client if any."""
        line = raw.replace(b"\r", b"").decode("utf-8", "replace")
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        with self.lock:
            self.log.write("%s %s\n" % (stamp(), line))
            self.log.flush()
            client = self.client
        if client is not None:
            try:
                client.sendall((line + "\n").encode("utf-8"))
            except OSError:
                pass                     # the client has gone; the port goes on

    def reader(self):
        buf = b""
        while True:
            try:
                chunk = os.read(self.fd, 4096)
            except InterruptedError:
                continue
            except OSError:
                break
            if not chunk:
                break                    # the adapter went away
            buf += chunk
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                self.emit(raw)
        if buf:
            self.emit(buf)               # a partial line at the end is kept

    def send(self, line):
        """A line from the client: the log, marked, then the port."""
        with self.lock:
            self.log.write("%s > %s\n" % (stamp(), line))
            self.log.flush()
        os.write(self.fd, (line + "\n").encode("utf-8"))

    def serve(self, srv):
        while True:
            conn, peer = srv.accept()
            sys.stderr.write("probe: client %s:%d connected\n" % peer)
            sys.stderr.flush()
            with self.lock:
                self.client = conn
            buf = b""
            try:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    buf += data
                    while b"\n" in buf:
                        raw, buf = buf.split(b"\n", 1)
                        self.send(raw.replace(b"\r", b"").decode("utf-8", "replace"))
            except OSError:
                pass
            finally:
                with self.lock:
                    self.client = None
                try:
                    conn.close()
                except OSError:
                    pass
                sys.stderr.write("probe: client %s:%d gone\n" % peer)
                sys.stderr.flush()


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: python3 broker/probe.py <serial port> <log file>\n")
        return 2
    port, log_path = argv
    try:
        fd = open_port(port)
    except OSError as exc:
        sys.stderr.write("probe: cannot open %s: %s\n" % (port, exc))
        return 2
    try:
        log = open(log_path, "a", encoding="utf-8")
    except OSError as exc:
        sys.stderr.write("probe: cannot open %s: %s\n" % (log_path, exc))
        os.close(fd)
        return 2
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind((HOST, PORT))
    except OSError as exc:
        sys.stderr.write("probe: cannot bind %s:%d (%s)\n" % (HOST, PORT, exc))
        log.close()
        os.close(fd)
        return 2
    srv.listen(1)
    sys.stderr.write("probe: reading %s at 115200 8N1, teeing to %s, listening on %s:%d (Ctrl-C ends it)\n"
                     % (port, log_path, HOST, PORT))
    sys.stderr.flush()
    probe = Probe(fd, log)
    t = threading.Thread(target=probe.reader, daemon=True)
    t.start()
    try:
        probe.serve(srv)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            srv.close()
        except OSError:
            pass
        with probe.lock:
            log.close()
        os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
