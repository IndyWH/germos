#!/usr/bin/env python3
"""The GermOS broker - the far end of the umbilical, on mlrig.

Listens on 127.0.0.1 only, speaks the length-prefixed protocol of
stage4/UMBILICAL.md, and answers one question per connection. In --mock mode
the answer comes from the canned table in that document and nothing else is
called, ever: the acceptance tests use only the mock, so the gate never
spends a token or needs the internet. Without --mock the answer comes from
broker/claude_backend.py, the one small swappable function that shells out
to `claude -p` - the Max subscription, no API keys anywhere.

This file is frozen acceptance machinery from Stage 4 plan item 7 (plan
decision 13): the framing, the listener, the record and the canned table are
criteria that the checker leans on, so they sit behind the hook with the
tests. broker/claude_backend.py is deliberately NOT frozen - it is the part
the automated gate never runs, and its flags are its own business.

Usage:
    python3 broker/broker.py                       # real: relays to claude -p
    python3 broker/broker.py --mock                # canned answers, no calls
    python3 broker/broker.py --mock --port 9999 --record stage4/out/broker.jsonl

Prints "listening on 127.0.0.1:<port>" to stdout once bound, so a harness can
wait for exactly that line. Exits non-zero if the port cannot be bound: a busy
port is a loud exit, never a shared one.

Standard library only.
"""

import argparse
import json
import socket
import struct
import sys
import time

HOST = "127.0.0.1"
DEFAULT_PORT = 9999

# ---------------------------------------------------------------- the frame -
# stage4/UMBILICAL.md, "Parsing it cold, in Python", verbatim.

REQUEST_MAX, RESPONSE_MAX = 498, 4096


def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ValueError("connection closed after %d of %d bytes" % (len(data), n))
        data += chunk
    return data


def read_frame(sock, limit):
    n, = struct.unpack("<I", recv_exact(sock, 4))
    if n > limit:
        raise ValueError("frame of %d bytes exceeds %d" % (n, limit))
    return recv_exact(sock, n)


def valid_request(text):
    return 1 <= len(text) <= REQUEST_MAX and all(0x20 <= b <= 0x7E for b in text)


def valid_response(text):
    return len(text) <= RESPONSE_MAX and all(0x20 <= b <= 0x7E or b == 0x0A for b in text)


def frame(text):
    return struct.pack("<I", len(text)) + text


# ------------------------------------------------------- the canned table --
# UMBILICAL.md, "The mock's canned table", exact bytes.

CANNED = {
    b"ping": b"pong",
    b"hello": b"hello from the mock broker\nask me something true at test 5",
}


def mock_answer(question):
    return CANNED.get(question, b"mock: no canned answer for: " + question)


# ------------------------------------------------------------ the contract --

def to_wire(text):
    """The response contract, enforced here whatever the backend did: only
    0x20-0x7E and LF reach the wire, at most RESPONSE_MAX bytes."""
    if isinstance(text, str):
        text = text.encode("ascii", "replace")
    text = text.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    text = bytes(b for b in text if 0x20 <= b <= 0x7E or b == 0x0A)
    if len(text) > RESPONSE_MAX:
        text = text[:RESPONSE_MAX - 3].rstrip() + b"..."
    return text


class RecordingSocket:
    """Wraps a connection so every byte read is kept for the record."""

    def __init__(self, sock):
        self.sock = sock
        self.seen = b""

    def recv(self, n):
        chunk = self.sock.recv(n)
        self.seen += chunk
        return chunk


class Recorder:
    def __init__(self, path):
        self.path = path

    def add(self, t, request, question, answer, error):
        if not self.path:
            return
        entry = {
            "t": t,
            "request": request.hex(),
            "question": question.decode("ascii") if question is not None else None,
            "answer": answer.decode("ascii") if answer is not None else None,
            "error": error,
        }
        with open(self.path, "a") as fh:
            fh.write(json.dumps(entry) + "\n")


def log(msg):
    sys.stderr.write("broker: %s\n" % msg)
    sys.stderr.flush()


# --------------------------------------------------------------- one call ---

def handle(conn, answerer, recorder, read_timeout):
    """One connection: one request frame, one response frame, close."""
    t0 = time.time()
    rs = RecordingSocket(conn)
    question = answer = None
    error = None
    try:
        conn.settimeout(read_timeout)
        question = read_frame(rs, REQUEST_MAX)
        if not valid_request(question):
            error = "request is not 1-498 printable ASCII bytes"
            question_shown = question
            question = None
            log("bad request %r" % question_shown[:64])
        else:
            conn.settimeout(None)
            answer = to_wire(answerer(question))
            conn.sendall(frame(answer))
            log("%r -> %d byte answer in %.1f s" % (question.decode("ascii"), len(answer), time.time() - t0))
    except (ValueError, socket.timeout, OSError) as exc:
        error = str(exc) if not isinstance(exc, socket.timeout) else "request did not arrive within %d s" % read_timeout
        log("connection closed without an answer: %s" % error)
    finally:
        try:
            conn.close()
        except OSError:
            pass
        recorder.add(t0, rs.seen, question, answer, error)


def serve(port, answerer, recorder, read_timeout):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # TIME_WAIT only; never two listeners
    try:
        srv.bind((HOST, port))
    except OSError as exc:
        log("cannot bind %s:%d (%s) - is another broker running?" % (HOST, port, exc))
        return 2
    srv.listen(1)
    sys.stdout.write("listening on %s:%d\n" % (HOST, port))
    sys.stdout.flush()
    try:
        while True:
            conn, peer = srv.accept()
            handle(conn, answerer, recorder, read_timeout)
    except KeyboardInterrupt:
        log("stopped")
    finally:
        srv.close()
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS broker (stage4/UMBILICAL.md).")
    ap.add_argument("--mock", action="store_true", help="answer from the canned table; call nothing")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port on 127.0.0.1 (default 9999)")
    ap.add_argument("--record", default=None, help="append one JSON line per connection to this file")
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds allowed for a real answer (default 120)")
    args = ap.parse_args(argv)

    if args.mock:
        answerer = mock_answer
        log("mock mode: canned answers, no calls of any kind")
    else:
        from claude_backend import ask  # the one swappable function; imported only here

        def answerer(question, _ask=ask, _timeout=args.timeout):
            return _ask(question.decode("ascii"), _timeout)
        log("real mode: relaying to claude -p with a %.0f s limit" % args.timeout)

    return serve(args.port, answerer, Recorder(args.record), read_timeout=10.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
