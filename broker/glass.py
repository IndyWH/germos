#!/usr/bin/env python3
"""The GermOS broker for Stage 6 ring 6a - the far end of the umbilical,
with the glass.

Listens on 127.0.0.1 only and speaks stage4/UMBILICAL.md's frame and
stage5/GERMLINE.md's grow request exactly as broker/germline.py does - the
framing, the request rule, the mock's canned answers, the record, the
germline lookup, the connection handler and the listener are IMPORTED from
those two frozen files, so there is one implementation of each. What this
file adds is stage6/GLASS.md: the response to a grow request is an APP
frame (kind 0x02) - a 96-byte header carrying the name, the source and the
declared choices, then an ABI 2 blob of four callbacks - and the pipeline
rehearses every candidate in the Stage 6 twin (broker/twin.py) under the
nine criteria. A repeat request is served from the germline, keyed with
abi2 so nothing cached at Stage 5 is ever served here, with the source
byte set. Questions are answered as before.

In --mock mode the generation backend is GLASS.md's canned table - the
three committed fixtures, the 18-byte fault blob, the 8 s hold - and
nothing outside the repository is called, ever: the acceptance tests use
only the mock, so the gate never spends a token or needs the internet. The
rehearsal still boots a real QEMU, because the rehearsal is what test 4
judges. Without --mock the answers come from broker/claude_backend.py -
ask() for a question, grow(abi=2) for a request - the one unfrozen file:
claude -p on the Max subscription, no API keys.

Built to be subclassed by later rings, never forked (plan amendment A2):
Glazier takes its rehearse callable as a constructor argument (default
twin.rehearse) and dictionaries of extra record and provenance fields.

This file is frozen acceptance machinery from ring 6a plan item 8: its
mock table, its record, its cache and its dispatch are criteria the
checker leans on. Standard library only.

Usage:
    python3 broker/glass.py                 # real: questions and requests to claude -p
    python3 broker/glass.py --mock          # canned answers and apps, no calls
    python3 broker/glass.py --mock --port 9999 --germline stage6/out/germline \
        --record stage6/out/broker.glass.jsonl

Prints "listening on 127.0.0.1:<port>" to stdout once bound. Exits non-zero
if the port cannot be bound.
"""

import argparse
import datetime
import hashlib
import json
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from broker import (HOST, DEFAULT_PORT, to_wire, mock_answer, log)  # noqa: E402
from germline import (germline_lookup, record_grow, handle, serve)  # noqa: E402

# ---------------------------------------------------------------- the wire -
# stage6/GLASS.md, "Parsing it cold, in Python", verbatim.

ABI = 2
GROW_MARKER = 0x01
KIND_REFUSAL, KIND_COMPONENT, KIND_APP = 0x00, 0x01, 0x02
HEADER = 96                      # the kind byte and the 95 bytes after it
BLOB_MAX = 1048576
BLOB_HEADER = 16                 # four u32 offsets: init, step, key, exit
NAME_MAX = 32
CHOICES = 4
LABEL_MAX = 12
CHOICES_SHOWN = 3
REFUSAL_MAX = 4096
BODY_MAX = 497
MACHINE = "qemu-q35-ovmf"
STEP_BUDGET_MS = 50
FRAME_HZ = 60
LINES = 16

OBS_MAGIC = b"OBSPAGE2"
OBS = {                          # u64 fields at these byte offsets
    "magic": 0x00, "tsc_per_ms": 0x08, "tsc_boot": 0x10, "mode": 0x18,
    "glass_apic": 0x20, "frames": 0x28, "frame_last": 0x30, "frame_worst": 0x38,
    "photon_last": 0x40, "photon_worst": 0x48, "keys": 0x50, "keys_hw": 0x58,
    "errors": 0x60, "questions": 0x68, "requests": 0x70, "notes": 0x78,
    "disk_reqs": 0x80, "disk_wait": 0x88, "wire_conns": 0x90, "bytes_in": 0x98,
    "bytes_out": 0xA0, "wire_wait": 0xA8, "grows_generated": 0xB0,
    "grows_served": 0xB8, "steps": 0xC0, "step_last": 0xC8, "step_worst": 0xD0,
    "tt_last": 0xD8, "tt_worst": 0xE0, "focus": 0xE8, "cols": 0xF0, "rows": 0xF8,
    "name": 0x100, "echo_stamp": 0x120, "echo_pending": 0x128,
}
SURFACES = {"strip": 0x140, "choices": 0x180, "conversation": 0x1C0, "app": 0x200}
SURFACE = {"cells": 0, "dirty": 8, "row0": 16, "col0": 24, "rows": 32, "cols": 40, "cursor": 48}
MODES = {0: "prompt", 1: "asking", 2: "growing", 3: "running", 4: "installing"}
CELL_BLOCK = 0x01


def printable(data):
    return all(0x20 <= b <= 0x7E for b in data)


def is_grow(request):
    return (2 <= len(request) <= 1 + BODY_MAX and request[0] == GROW_MARKER
            and printable(request[1:]))


def grow_request(body):
    return struct.pack("<I", 1 + len(body)) + bytes([GROW_MARKER]) + body


def refusal_frame(text):
    return struct.pack("<I", 1 + len(text)) + bytes([KIND_REFUSAL]) + text


def app_header(length, name, choices, source=0, installed=0):
    if not 1 <= len(name) <= NAME_MAX or not printable(name):
        raise ValueError("name must be 1..32 printable bytes")
    if len(choices) > CHOICES:
        raise ValueError("at most four choices")
    slots = b""
    for key, label in choices:
        if not (0x20 <= key <= 0x7E) or not 1 <= len(label) <= LABEL_MAX or not printable(label):
            raise ValueError("a choice is a printable key and a 1..12 byte printable label")
        slots += bytes([key]) + label.ljust(LABEL_MAX, b"\0")
    slots = slots.ljust(CHOICES * (1 + LABEL_MAX), b"\0")
    return (bytes([KIND_APP, ABI, source, 0]) + struct.pack("<I", length)
            + name.ljust(NAME_MAX, b"\0") + bytes([installed, 0, 0, 0]) + slots)


def app_frame(blob, name, choices=(), source=0, installed=0):
    body = app_header(len(blob), name, choices, source, installed) + blob
    return struct.pack("<I", len(body)) + body


def blob_offsets(blob):
    """The four callback offsets, or a ValueError naming what is wrong."""
    if len(blob) < BLOB_HEADER:
        raise ValueError("blob shorter than its 16-byte header")
    offs = struct.unpack_from("<IIII", blob, 0)
    if any(o >= len(blob) for o in offs):
        raise ValueError("a callback offset lies beyond the blob")
    return offs


def parse_response(content):
    """The bytes after the length prefix. Returns ("refusal", text) or
    ("app", blob, name, choices, source, installed); raises ValueError."""
    if not content:
        raise ValueError("empty response")
    kind = content[0]
    if kind == KIND_REFUSAL:
        text = content[1:]
        if len(text) > REFUSAL_MAX or not all(0x20 <= b <= 0x7E or b == 0x0A for b in text):
            raise ValueError("refusal text is not printable ASCII or LF within 4096 bytes")
        return "refusal", text
    if kind == KIND_COMPONENT:
        raise ValueError("kind 0x01 is a Stage 5 component - ABI 1 has no callbacks")
    if kind != KIND_APP:
        raise ValueError("unknown response kind 0x%02x" % kind)
    if len(content) < HEADER:
        raise ValueError("app frame shorter than its header")
    if content[1] != ABI:
        raise ValueError("ABI version %d, want %d" % (content[1], ABI))
    source = content[2]
    if source not in (0, 1) or content[3] != 0:
        raise ValueError("source byte or byte 3 is not what the document says")
    length, = struct.unpack_from("<I", content, 4)
    if not 1 <= length <= BLOB_MAX:
        raise ValueError("blob length %d is outside 1..%d" % (length, BLOB_MAX))
    raw = content[8:8 + NAME_MAX]
    name = raw.split(b"\0", 1)[0]
    if not name or not printable(name) or any(raw[len(name):]):
        raise ValueError("name is not 1..32 printable bytes, NUL-padded")
    installed = content[40]
    if installed not in (0, 1) or any(content[41:44]):
        raise ValueError("installed byte or bytes 41-43 are not what the document says")
    choices = []
    for i in range(CHOICES):
        slot = content[44 + i * 13:44 + (i + 1) * 13]
        if slot[0] == 0:
            if any(slot):
                raise ValueError("an empty choice slot is not all zero")
            continue
        if choices and len(choices) < i:
            raise ValueError("choice slots are not packed from the first")
        label = slot[1:].split(b"\0", 1)[0]
        if not (0x20 <= slot[0] <= 0x7E) or not label or not printable(label) or any(slot[1 + len(label):]):
            raise ValueError("a choice is a printable key and a 1..12 byte printable label")
        choices.append((slot[0], label))
    if len(content) != HEADER + length:
        raise ValueError("frame carries %d bytes, header says %d" % (len(content) - HEADER, length))
    blob = content[HEADER:]
    blob_offsets(blob)
    return "app", blob, name, choices, source, installed


def normalise(body):
    return " ".join(body.lower().split())


def germline_key(body, machine=MACHINE):
    s = "%s|abi%d|%s" % (normalise(body), ABI, machine)
    return hashlib.sha256(s.encode("ascii")).hexdigest()[:16]


def regions(cols, rows):
    """The four regions as (row0, col0, rows, cols); None if too small."""
    if cols < 8 or rows < 8:
        return None
    half = cols // 2
    return {"strip": (0, 0, 2, cols), "choices": (rows - 2, 0, 2, cols),
            "conversation": (2, 0, rows - 4, half), "app": (2, half, rows - 4, cols - half)}


def parse_obs(page):
    """The obs page's bytes (at least 0x240). Returns a dict of the fields,
    the name as a string, and each surface as a dict."""
    if page[0:8] != OBS_MAGIC:
        raise ValueError("no obs page magic")
    obs = {}
    for field, off in OBS.items():
        if field == "magic":
            continue
        if field == "name":
            obs[field] = page[off:off + NAME_MAX].split(b"\0", 1)[0].decode("ascii", "replace")
        else:
            obs[field], = struct.unpack_from("<Q", page, off)
    for name, base in SURFACES.items():
        obs[name] = {k: struct.unpack_from("<Q", page, base + o)[0] for k, o in SURFACE.items()}
    return obs


def fmt_n(value, width):
    return "%0*d" % (width, min(value, 10 ** width - 1))


def fmt_ms(ticks, tsc_per_ms):
    tenths = min(ticks * 10 // max(tsc_per_ms, 1), 999)
    return "%02d.%d" % (tenths // 10, tenths % 10)


def mode_word(mode, name):
    word = MODES.get(mode, "?")
    if mode == 3:
        word = "running " + name[:10]
    return word.ljust(18)


def strip_rows(obs, now_ticks):
    """The two strip rows, exactly as the glass core draws them."""
    t = max(obs["tsc_per_ms"], 1)
    up = (now_ticks - obs["tsc_boot"]) // t // 1000
    row0 = "up %s core %s fr %s %s/%s ph %s/%s k %s hw %s err %s step %s/%s" % (
        fmt_n(up, 6), fmt_n(obs["glass_apic"], 2), fmt_n(obs["frames"], 6),
        fmt_ms(obs["frame_last"], t), fmt_ms(obs["frame_worst"], t),
        fmt_ms(obs["photon_last"], t), fmt_ms(obs["photon_worst"], t),
        fmt_n(obs["keys"], 4), fmt_n(obs["keys_hw"], 3), fmt_n(obs["errors"], 3),
        fmt_ms(obs["step_last"], t), fmt_ms(obs["step_worst"], t))
    row1 = "%s q %s n %s g %s/%s disk %s %s w %s %s io %s/%s" % (
        mode_word(obs["mode"], obs["name"]),
        fmt_n(obs["questions"], 3), fmt_n(obs["notes"], 3),
        fmt_n(obs["grows_generated"], 3), fmt_n(obs["grows_served"], 3),
        fmt_n(obs["disk_reqs"], 4), fmt_n(obs["disk_wait"] // t, 6),
        fmt_n(obs["wire_conns"], 3), fmt_n(obs["wire_wait"] // t, 6),
        fmt_n(obs["bytes_in"], 6), fmt_n(obs["bytes_out"], 6))
    return row0, row1


def choices_row(app_running, focus, choices):
    """Row R-2 of the choices region, from column 0."""
    if not app_running:
        return "? ask   ! grow"
    if focus == 0:
        return "? ask   ! grow   Tab app   Esc exit"
    items = ["%s %s" % (chr(k), label.decode("ascii")) for k, label in choices[:CHOICES_SHOWN]]
    return "   ".join(items + ["Esc exit", "Tab prompt"])


# ------------------------------------------------------- the canned table --
# GLASS.md, "The mock's canned table for requests". The fixtures are read at
# call time, so the files the repository holds are what is served. A
# candidate is ("app", blob, name, choices); a refusal is ("refusal", text).

FIXTURES = os.path.join(REPO, "stage6")
FAULT_BLOB = struct.pack("<IIII", 16, 16, 16, 16) + b"\x0f\x0b"     # ud2 in init
TEST_CHOICES = [(ord("a"), b"alpha"), (ord("b"), b"beta")]
HOLD_SECONDS = 8.0


def fixture(name):
    return open(os.path.join(FIXTURES, name + ".bin"), "rb").read()


def mock_generate(body, failure):
    """The mock backend. Calls nothing."""
    if body == "test app":
        return ("app", fixture("app"), b"test app", TEST_CHOICES)
    if body == "big":
        blob = fixture("app")
        return ("app", blob + bytes(BLOB_MAX - len(blob)), b"big", TEST_CHOICES)
    if body == "fault":
        return ("app", FAULT_BLOB, b"fault", [])
    if body == "hog":
        return ("app", fixture("hog"), b"hog", [])
    if body == "escapee":
        return ("app", fixture("escapee"), b"escapee", [])
    if body == "hold":
        time.sleep(HOLD_SECONDS)
        return ("refusal", "mock: held")
    return ("refusal", "mock: no canned component for: " + body)


# ------------------------------------------------------------ the germline -

def glass_lookup(root, key):
    """The cached blob, name and choices for a key - the blob hash-checked
    by the frozen germline_lookup - or None on a miss."""
    blob = germline_lookup(root, key)
    if blob is None:
        return None
    try:
        prov = json.load(open(os.path.join(root, key, "provenance.json")))
        if prov.get("abi") != ABI:
            log("germline entry %s is abi %r, not %d - treated as a miss" % (key, prov.get("abi"), ABI))
            return None
        name = prov["name"].encode("ascii")
        choices = [(int(k) if isinstance(k, int) else ord(k), l.encode("ascii")) for k, l in prov.get("choices", [])]
        app_header(len(blob), name, choices)       # the record must still be a legal header
    except (OSError, ValueError, KeyError, TypeError) as exc:
        log("germline entry %s has an unusable record (%s) - treated as a miss" % (key, exc))
        return None
    return blob, name, choices


def germline_write(root, key, body, blob, name, choices, model, tries, rehearsal_seconds,
                   rehearsal_log, extra=None):
    """GERMLINE.md's entry, with GLASS.md's abi, name and choices, and any
    extra fields a later ring's pipeline passes."""
    d = os.path.join(root, key)
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
        "name": name.decode("ascii"),
        "choices": [[chr(k), l.decode("ascii")] for k, l in choices],
    }
    prov.update(extra or {})
    with open(os.path.join(d, "provenance.json"), "w") as fh:
        json.dump(prov, fh, indent=2)
        fh.write("\n")


# ------------------------------------------------------------ the pipeline -

class Glazier:
    """The grow pipeline with its state: the backend, its running call
    count, the germline root, the twin's image, the rehearsal's port and
    scratch directory, how many candidates a request may cost, the
    rehearse callable, and extra fields for the record and the provenance.
    generate(body, failure) returns ("app", blob, name, choices) or
    ("refusal", text). rehearse(blob, name, choices, image, workdir, port)
    returns (passed, phrase, log_text)."""

    def __init__(self, generate, model, root, image, workdir, rehearsal_port, tries,
                 rehearse=None, extra_record=None, extra_provenance=None):
        self.generate = generate
        self.model = model
        self.root = root
        self.image = image
        self.workdir = workdir
        self.rehearsal_port = rehearsal_port
        self.tries = max(1, tries)
        self.calls = 0
        self.rehearse = rehearse
        self.extra_record = dict(extra_record or {})
        self.extra_provenance = dict(extra_provenance or {})

    def rehearsal(self):
        if self.rehearse is None:
            from twin import rehearse   # the twin driver; imported here, not at module load
            self.rehearse = rehearse
        return self.rehearse

    def grow(self, body):
        """Returns (response_frame, record_fields)."""
        key = germline_key(body)
        rehearsals = []
        app = None
        source = None
        answer_text = None
        cached = glass_lookup(self.root, key)
        if cached is not None:
            app = cached
            source = "germline"
            log("grow %r: served from the germline (%s)" % (body, key))
        else:
            failure = None
            phrase = None
            for attempt in range(1, self.tries + 1):
                self.calls += 1
                log("grow %r: generation call %d (try %d of %d)" % (body, self.calls, attempt, self.tries))
                candidate = self.generate(body, failure)
                if candidate[0] == "refusal":
                    answer_text = candidate[1]
                    source = "refused"
                    log("grow %r: the backend refused: %s" % (body, answer_text[:80]))
                    break
                _, blob, name, choices = candidate
                t0 = time.time()
                passed, phrase, rlog = self.rehearsal()(blob, name, choices, self.image, self.workdir,
                                                        self.rehearsal_port)
                seconds = time.time() - t0
                rehearsals.append("pass" if passed else "fail: " + phrase)
                log("grow %r: rehearsal %s in %.0f s" % (body, rehearsals[-1], seconds))
                if passed:
                    app = (blob, name, choices)
                    germline_write(self.root, key, body, blob, name, choices, self.model, attempt,
                                   seconds, rlog, self.extra_provenance)
                    source = "generated"
                    break
                errs = [l for l in rlog.splitlines() if l.startswith("ERR:")]
                failure = phrase + ((" - " + errs[0]) if errs else "")
            if app is None and answer_text is None:
                answer_text = "rehearsal failed: " + phrase
                source = "refused"
        if app is not None:
            blob, name, choices = app
            response = app_frame(blob, name, choices, 1 if source == "germline" else 0)
            kind = "app"
        else:
            name = None
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
            "abi": ABI,
            "name": name.decode("ascii") if name else None,
        }
        fields.update(self.extra_record)
        return response, fields


# --------------------------------------------------------------- main ------

def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS broker, Stage 6 ring 6a (stage6/GLASS.md).")
    ap.add_argument("--mock", action="store_true", help="canned answers and apps; call nothing")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port on 127.0.0.1 (default 9999)")
    ap.add_argument("--record", default=None, help="append one JSON line per connection to this file")
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds allowed for one claude -p call (default 120)")
    ap.add_argument("--germline", default=os.path.join(REPO, "germline"), help="the cache root (default germline/)")
    ap.add_argument("--image", default=os.path.join(REPO, "stage6", "out", "esp.img"),
                    help="the guest image the twin boots (default stage6/out/esp.img)")
    ap.add_argument("--workdir", default=os.path.join(REPO, "stage6", "out", "rehearsal"),
                    help="the twin's scratch directory (default stage6/out/rehearsal)")
    ap.add_argument("--rehearsal-port", type=int, default=9998, help="the twin's listener port (default 9998)")
    ap.add_argument("--tries", type=int, default=2, help="candidates a request may cost (default 2)")
    ap.add_argument("--model", default=None, help="passed to claude -p --model (real mode only)")
    args = ap.parse_args(argv)

    if args.mock:
        answerer = mock_answer
        generate = mock_generate
        model = "mock"
        log("mock mode: canned answers and apps, no calls of any kind")
    else:
        from claude_backend import ask, grow, model_name  # imported only here

        def answerer(question, _ask=ask, _timeout=args.timeout):
            return _ask(question.decode("ascii"), _timeout)

        def generate(body, failure, _grow=grow, _timeout=args.timeout, _model=args.model):
            return _grow(body, failure, _timeout, _model, abi=ABI)

        model = model_name(args.model)
        log("real mode: relaying to claude -p with a %.0f s limit per call" % args.timeout)

    glazier = Glazier(generate, model, args.germline, args.image, args.workdir, args.rehearsal_port, args.tries)
    log("germline at %s; the twin boots %s; rehearsal on 127.0.0.1:%d; %d tries"
        % (args.germline, args.image, args.rehearsal_port, glazier.tries))
    return serve(args.port, answerer, glazier, args.record, read_timeout=10.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
