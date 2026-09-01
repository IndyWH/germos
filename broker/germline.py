#!/usr/bin/env python3
"""The GermOS broker for Stage 5 - the far end of the umbilical, grown.

Listens on 127.0.0.1 only and speaks stage4/UMBILICAL.md's frame, exactly
as broker/broker.py does - the framing, the request rule, the response
contract, the mock's canned answers and the record are IMPORTED from that
frozen file, so there is one implementation of the wire. What this file
adds is stage5/GERMLINE.md: a request frame whose first byte is 0x01 is a
grow request, and it runs the pipeline - generate, rehearse in the twin,
cache in the germline, deliver - answering with a component frame or a
refusal. A repeat request is served from the germline and the generation
backend is never invoked. Questions are answered as before.

In --mock mode the generation backend is GERMLINE.md's canned table and
nothing outside the repository is called, ever - the acceptance tests use
only the mock, so the gate never spends a token or needs the internet. The
rehearsal still boots a real QEMU (broker/rehearse.py), because the
rehearsal is what test 4 judges. Without --mock the answers come from
broker/claude_backend.py - ask() for a question, grow() for a request - the
one unfrozen file: claude -p on the Max subscription, no API keys.

This file is frozen acceptance machinery from Stage 5 plan item 8: its
mock table, its record, its cache and its dispatch are criteria the checker
leans on. Standard library only.

Usage:
    python3 broker/germline.py                 # real: questions and requests to claude -p
    python3 broker/germline.py --mock          # canned answers and components, no calls
    python3 broker/germline.py --mock --port 9999 --germline stage5/out/germline \
        --record stage5/out/broker.8.jsonl

Prints "listening on 127.0.0.1:<port>" to stdout once bound. Exits non-zero
if the port cannot be bound.
"""

import argparse
import datetime
import hashlib
import json
import os
import socket
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from broker import (HOST, DEFAULT_PORT, REQUEST_MAX, read_frame, valid_request,  # noqa: E402
                    frame, to_wire, mock_answer, RecordingSocket, Recorder, log)

# ---------------------------------------------------------------- the wire -
# stage5/GERMLINE.md, "Parsing it cold, in Python", verbatim.

ABI = 1
GROW_MARKER = 0x01
KIND_REFUSAL, KIND_COMPONENT = 0x00, 0x01
HEADER = 32                      # the kind byte and the 31 bytes after it
BLOB_MAX = 1048576
REFUSAL_MAX = 4096
BODY_MAX = 497
MACHINE = "qemu-q35-ovmf"


def is_grow(request):
    """True if a valid request frame's text is a grow request."""
    return (2 <= len(request) <= 1 + BODY_MAX and request[0] == GROW_MARKER
            and all(0x20 <= b <= 0x7E for b in request[1:]))


def grow_request(body):
    return struct.pack("<I", 1 + len(body)) + bytes([GROW_MARKER]) + body


def refusal_frame(text):
    return struct.pack("<I", 1 + len(text)) + bytes([KIND_REFUSAL]) + text


def component_frame(blob):
    body = (bytes([KIND_COMPONENT, 0, 0, 0]) + struct.pack("<II", ABI, len(blob))
            + bytes(20) + blob)
    return struct.pack("<I", len(body)) + body


def parse_response(content):
    """The bytes after the length prefix. Returns ("refusal", text) or
    ("component", blob); raises ValueError naming what was wrong."""
    if not content:
        raise ValueError("empty response")
    kind = content[0]
    if kind == KIND_REFUSAL:
        text = content[1:]
        if len(text) > REFUSAL_MAX or not all(0x20 <= b <= 0x7E or b == 0x0A for b in text):
            raise ValueError("refusal text is not printable ASCII or LF within 4096 bytes")
        return "refusal", text
    if kind == KIND_COMPONENT:
        if len(content) < HEADER:
            raise ValueError("component frame shorter than its header")
        if any(content[1:4]) or any(content[12:32]):
            raise ValueError("reserved header bytes are not zero")
        abi, length = struct.unpack_from("<II", content, 4)
        if abi != ABI:
            raise ValueError("ABI version %d, want %d" % (abi, ABI))
        if not 1 <= length <= BLOB_MAX:
            raise ValueError("blob length %d is outside 1..%d" % (length, BLOB_MAX))
        if len(content) != HEADER + length:
            raise ValueError("frame carries %d bytes, header says %d" % (len(content) - HEADER, length))
        return "component", content[HEADER:]
    raise ValueError("unknown response kind 0x%02x" % kind)


def normalise(body):
    return " ".join(body.lower().split())


def germline_key(body, machine=MACHINE):
    s = "%s|abi%d|%s" % (normalise(body), ABI, machine)
    return hashlib.sha256(s.encode("ascii")).hexdigest()[:16]


# ------------------------------------------------------- the canned table --
# GERMLINE.md, "The mock's canned table for requests". The component is read
# at call time, so the file the repository holds is what is served.

COMPONENT_BIN = os.path.join(REPO, "stage5", "component.bin")
FAULT_BLOB = b"\x0f\x0b"                 # ud2


def mock_generate(body, failure):
    """The mock backend: a blob, or ("refusal", text). Calls nothing."""
    if body == "test component":
        return open(COMPONENT_BIN, "rb").read()
    if body == "big":
        blob = open(COMPONENT_BIN, "rb").read()
        return blob + bytes(BLOB_MAX - len(blob))
    if body == "fault":
        return FAULT_BLOB
    return ("refusal", "mock: no canned component for: " + body)


# ------------------------------------------------------------ the germline -

def germline_dir(root, key):
    return os.path.join(root, key)


def germline_lookup(root, key):
    """The cached blob for a key, after its hash is checked against the
    record; None on a miss or a mismatch."""
    d = germline_dir(root, key)
    try:
        prov = json.load(open(os.path.join(d, "provenance.json")))
        blob = open(os.path.join(d, "component.bin"), "rb").read()
    except (OSError, ValueError):
        return None
    if prov.get("sha256") != hashlib.sha256(blob).hexdigest() or not 1 <= len(blob) <= BLOB_MAX:
        log("germline entry %s does not match its record - treated as a miss" % key)
        return None
    return blob


def germline_write(root, key, body, blob, model, tries, rehearsal_seconds, rehearsal_log):
    d = germline_dir(root, key)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "component.bin"), "wb") as fh:
        fh.write(blob)
    with open(os.path.join(d, "rehearsal.log"), "w") as fh:
        fh.write(rehearsal_log)
    prov = {
        "request": body,
        "normalised": normalise(body),
        "key": key,
        "abi": ABI,
        "machine": MACHINE,
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": model,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "size": len(blob),
        "tries": tries,
        "rehearsal": {"passed": True, "phrases": [], "seconds": round(rehearsal_seconds, 1)},
    }
    with open(os.path.join(d, "provenance.json"), "w") as fh:
        json.dump(prov, fh, indent=2)
        fh.write("\n")


# ------------------------------------------------------------ the pipeline -

class Grower:
    """The grow pipeline with its state: the backend, its running call
    count, the germline root, the twin's image, the rehearsal's port and
    scratch directory, and how many candidates a request may cost."""

    def __init__(self, generate, model, root, image, workdir, rehearsal_port, tries):
        self.generate = generate
        self.model = model
        self.root = root
        self.image = image
        self.workdir = workdir
        self.rehearsal_port = rehearsal_port
        self.tries = max(1, tries)
        self.calls = 0

    def grow(self, body):
        """Returns (response_frame, record_fields)."""
        from rehearse import rehearse  # the twin driver; imported here, not at module load
        key = germline_key(body)
        rehearsals = []
        blob = germline_lookup(self.root, key)
        source = None
        answer_text = None
        if blob is not None:
            source = "germline"
            log("grow %r: served from the germline (%s)" % (body, key))
        else:
            failure = None
            phrase = None
            for attempt in range(1, self.tries + 1):
                self.calls += 1
                log("grow %r: generation call %d (try %d of %d)" % (body, self.calls, attempt, self.tries))
                candidate = self.generate(body, failure)
                if isinstance(candidate, tuple):
                    answer_text = candidate[1]
                    source = "refused"
                    log("grow %r: the backend refused: %s" % (body, answer_text[:80]))
                    break
                t0 = time.time()
                passed, phrase, rlog = rehearse(candidate, self.image, self.workdir, self.rehearsal_port)
                seconds = time.time() - t0
                rehearsals.append("pass" if passed else "fail: " + phrase)
                log("grow %r: rehearsal %s in %.0f s" % (body, rehearsals[-1], seconds))
                if passed:
                    blob = candidate
                    germline_write(self.root, key, body, blob, self.model, attempt, seconds, rlog)
                    source = "generated"
                    break
                errs = [l for l in rlog.splitlines() if l.startswith("ERR:")]
                failure = phrase + ((" - " + errs[0]) if errs else "")
            if blob is None and answer_text is None:
                answer_text = "rehearsal failed: " + phrase
                source = "refused"
        if blob is not None:
            response = component_frame(blob)
            kind = "component"
        else:
            response = refusal_frame(to_wire(answer_text))
            kind = "refusal"
        fields = {
            "text": body,
            "key": key,
            "source": source,
            "generation_calls": self.calls,
            "rehearsals": rehearsals,
            "answer_kind": kind,
            "answer_sha256": hashlib.sha256(response).hexdigest(),
            "answer": answer_text,
        }
        return response, fields


# --------------------------------------------------------------- one call ---

def record_grow(path, t, raw, fields, error):
    if not path:
        return
    entry = {"t": t, "kind": "grow", "request": raw.hex(), "text": None, "key": None,
             "source": None, "generation_calls": None, "rehearsals": [],
             "answer_kind": None, "answer_sha256": None, "answer": None, "error": error}
    entry.update(fields)
    with open(path, "a") as fh:
        fh.write(json.dumps(entry) + "\n")


def handle(conn, answerer, grower, recorder, record_path, read_timeout):
    """One connection: one request frame, one response frame, close."""
    t0 = time.time()
    rs = RecordingSocket(conn)
    request = None
    error = None
    grow_fields = None
    question = answer = None
    try:
        conn.settimeout(read_timeout)
        request = read_frame(rs, REQUEST_MAX)
        conn.settimeout(None)
        if is_grow(request):
            body = request[1:].decode("ascii")
            response, grow_fields = grower.grow(body)
            conn.sendall(response)
            log("grow %r -> %s, %d bytes in %.1f s" % (body, grow_fields["answer_kind"], len(response), time.time() - t0))
        elif valid_request(request):
            question = request
            answer = to_wire(answerer(question))
            conn.sendall(frame(answer))
            log("%r -> %d byte answer in %.1f s" % (question.decode("ascii"), len(answer), time.time() - t0))
        else:
            error = "request is neither a question (1-498 printable bytes) nor a grow request"
            log("bad request %r" % request[:64])
    except (ValueError, socket.timeout, OSError) as exc:
        error = ("request did not arrive within %d s" % read_timeout
                 if isinstance(exc, socket.timeout) else str(exc))
        log("connection closed without an answer: %s" % error)
    finally:
        try:
            conn.close()
        except OSError:
            pass
        if request is not None and is_grow(request):
            record_grow(record_path, t0, rs.seen, grow_fields or {}, error)
        else:
            recorder.add(t0, rs.seen, question, answer, error)


def serve(port, answerer, grower, record_path, read_timeout):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind((HOST, port))
    except OSError as exc:
        log("cannot bind %s:%d (%s) - is another broker running?" % (HOST, port, exc))
        return 2
    srv.listen(1)
    sys.stdout.write("listening on %s:%d\n" % (HOST, port))
    sys.stdout.flush()
    recorder = Recorder(record_path)
    try:
        while True:
            conn, _ = srv.accept()
            handle(conn, answerer, grower, recorder, record_path, read_timeout)
    except KeyboardInterrupt:
        log("stopped")
    finally:
        srv.close()
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS broker, Stage 5 (stage5/GERMLINE.md).")
    ap.add_argument("--mock", action="store_true", help="canned answers and components; call nothing")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port on 127.0.0.1 (default 9999)")
    ap.add_argument("--record", default=None, help="append one JSON line per connection to this file")
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds allowed for one claude -p call (default 120)")
    ap.add_argument("--germline", default=os.path.join(REPO, "germline"), help="the cache root (default germline/)")
    ap.add_argument("--image", default=os.path.join(REPO, "stage5", "out", "esp.img"),
                    help="the guest image the rehearsal boots (default stage5/out/esp.img)")
    ap.add_argument("--workdir", default=os.path.join(REPO, "stage5", "out", "rehearsal"),
                    help="the rehearsal's scratch directory (default stage5/out/rehearsal)")
    ap.add_argument("--rehearsal-port", type=int, default=9998, help="the rehearsal listener's port (default 9998)")
    ap.add_argument("--tries", type=int, default=2, help="candidates a request may cost (default 2)")
    ap.add_argument("--model", default=None, help="passed to claude -p --model (real mode only)")
    args = ap.parse_args(argv)

    if args.mock:
        answerer = mock_answer
        generate = mock_generate
        model = "mock"
        log("mock mode: canned answers and components, no calls of any kind")
    else:
        from claude_backend import ask, grow, model_name  # imported only here

        def answerer(question, _ask=ask, _timeout=args.timeout):
            return _ask(question.decode("ascii"), _timeout)

        def generate(body, failure, _grow=grow, _timeout=args.timeout, _model=args.model):
            return _grow(body, failure, _timeout, _model)

        model = model_name(args.model)
        log("real mode: relaying to claude -p with a %.0f s limit per call" % args.timeout)

    grower = Grower(generate, model, args.germline, args.image, args.workdir, args.rehearsal_port, args.tries)
    log("germline at %s; the twin boots %s; rehearsal on 127.0.0.1:%d; %d tries"
        % (args.germline, args.image, args.rehearsal_port, grower.tries))
    return serve(args.port, answerer, grower, args.record, read_timeout=10.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
