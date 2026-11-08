#!/usr/bin/env python3
"""The GermOS broker for Stage 8 ring 8a - the molt.

Everything ring 7b's broker does, this one does, by IMPORT and never by
edit: the framing, the record, the listener, the install path and the
twin are the frozen wire.Wire's. What this file adds is stage8/PARTS.md's
request and part frame: a grow body beginning "molt " is claimed here (as
plans.Installer claims "install "), and everything else falls through to
wire.Wire, so "! test app", "! install echo" and the relay behave as at
ring 7c.

The frame and the key are never spelled here. They are PARTS.md's own
Python, read cold through stage8/parts.py: request_body, molt_key,
part_frame, check_part, and the fixture table's thresholds.

In --mock mode nothing outside the repository is ever called.
"! molt i8042" is answered with one of the five committed fixtures,
stage8/fixtures/i8042-<part>.bin, in a part frame with the fixture
table's threshold and source 0; nothing is rehearsed. A slot other than
i8042, or a body that is not PARTS.md's request, gets a refusal frame.
--part-file and --part-threshold serve any part the same way, for ring
8b's rehearsal.

Ring 8b, the first molt (stage8/plan-8b.md):

--grow SLOT is the pipeline, run on the host before the machine asks,
because it takes longer than the guest's 600 s wait: a candidate from the
real backend by the plan (or --canned, the gate's), the door, the bench,
the differential, the measures, the rehearsal, the verdict by the plan's
rule, all to stdout; on "beats" the part is stored in the germline under
the key the plan's identity builds.

--collect serves the germline and calls no backend at all: "! molt i8042"
is answered at once from it, with source 1, if the guest's own identity
builds a key that holds a part, and refused otherwise. A stray "? x" or
"! x" typed during the HP's free use spends nothing. The identity is still
read by the guest at the request, so a part reaches only the machine it
was grown for.

Neither --grow nor anything else in this file ever touches an API key:
refuse_api_keys ends the process first if one is in the environment.

--hold-s S holds the answer to one question, "? hold", for S seconds
before sending it (plan amendment A1). The checker never relies on it: it
measures the wait itself, from the guest's side.

This file is NOT frozen (ring 8a plan decision 14, deviation 5): ring
8b's real grow path lives here. The criterion stays frozen because the
checker never trusts the mock - it rebuilds every expected frame from
PARTS.md and the frozen .bin and compares it with this file's record,
byte for byte. Standard library only.

Usage:
    python3 broker/molt.py --mock                 # serves i8042-good
    python3 broker/molt.py --mock --part hang     # serves i8042-hang
    python3 broker/molt.py --mock --hold-s 60     # "? hold" answered after 60 s

Prints "listening on 127.0.0.1:<port>" to stdout once bound.
"""

import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "stage8"))
from broker import (DEFAULT_PORT, mock_answer, to_wire, log)  # noqa: E402
from germline import serve, refusal_frame  # noqa: E402
from glass import ABI as ABI2  # noqa: E402
import twin  # noqa: E402
from plans import PLANS_DIR  # noqa: E402
from pointer import mock_point  # noqa: E402
import wire  # noqa: E402
from wire import Wire, LINES  # noqa: E402
import bench  # noqa: E402  - stage8/bench.py, the plan read cold and the verdict
import parts  # noqa: E402  - PARTS.md's Python, checked against its prose at import

# --------------------------------------------------------------- the molt --
# stage8/PARTS.md, "The request and the part frame".

STAGE8_OUT = os.path.join(REPO, "stage8", "out")
DEFAULT_IMAGE = os.path.join(STAGE8_OUT, "esp.img")
DEFAULT_WORKDIR = os.path.join(STAGE8_OUT, "molt", "rehearsal", "twin")
IDENT_RE = re.compile(r"cpu [0-9a-f]{8} pci [0-9a-f]{4}:[0-9a-f]{4}:[0-9a-f]{2}")
HOLD_QUESTION = b"hold"


def is_molt(body):
    return body == "molt" or body.startswith("molt ")


def molt_request(body):
    """(slot, identity) from a molt body, or (None, why) when it is not
    PARTS.md's request byte for byte."""
    words = body.split(" ", 2)
    if len(words) != 3 or not words[1]:
        return None, "molt request malformed: want molt <slot> cpu <8 hex> pci <vvvv:dddd:rr>"
    slot, ident = words[1], words[2]
    if not IDENT_RE.fullmatch(ident) or parts.request_body(slot, ident) != body:
        return None, "molt request malformed: want molt <slot> cpu <8 hex> pci <vvvv:dddd:rr>"
    return slot, ident


def mock_part(fate):
    """The fixture the mock serves, checked by PARTS.md's own rules before
    the listener opens: its frame must parse back to the same part and
    the fixture table's threshold."""
    part = parts.fixture(fate)
    frame = parts.part_frame(part, parts.FIXTURES[fate], 0)
    kind, fields, back, threshold, source = parts.parse_frame(frame, "i8042")
    if kind != "part" or back != part or threshold != parts.FIXTURES[fate] or source != 0:
        raise ValueError("fixture %s does not round-trip through PARTS.md's frame" % fate)
    if fields["name"] != fate:
        raise ValueError("fixture %s carries the name field %r" % (fate, fields["name"]))
    return part, frame


# ------------------------------------------------------------ the germline -
# A part's entry: germline/molt-<16 hex of the key's SHA-256>/ holding
# part.bin and provenance.json, or provenance.json alone for "the generic
# stays". The key itself is in the record.

def part_dir(root, key):
    return os.path.join(root, "molt-" + hashlib.sha256(key.encode()).hexdigest()[:16])


def part_lookup(root, key):
    """(part, provenance), (None, provenance) for a recorded "generic stays",
    or (None, None). A record that does not match its part is a miss."""
    d = part_dir(root, key)
    try:
        prov = json.load(open(os.path.join(d, "provenance.json")))
    except (OSError, ValueError):
        return None, None
    if prov.get("key") != key:
        return None, None
    if prov.get("verdict") != "beats":
        return None, prov
    try:
        part = open(os.path.join(d, "part.bin"), "rb").read()
    except OSError:
        return None, None
    if hashlib.sha256(part).hexdigest() != prov.get("sha256"):
        log("germline entry %s does not match its record - treated as a miss" % key)
        return None, None
    return part, prov


def part_write(root, key, prov, part=None):
    d = part_dir(root, key)
    os.makedirs(d, exist_ok=True)
    if part is not None:
        with open(os.path.join(d, "part.bin"), "wb") as fh:
            fh.write(part)
    with open(os.path.join(d, "provenance.json"), "w", encoding="utf-8") as fh:
        json.dump(prov, fh, indent=2)
        fh.write("\n")


# ------------------------------------------------------------ the pipeline -

class Molt(Wire):
    """wire.Wire with PARTS.md's molt request in front of its dispatch.
    fate is the fixture served in mock mode, or None when real. part_file
    serves a part from a file in mock mode (ring 8b's rehearsal). collect
    answers molt requests from the germline and everything else with a
    refusal: no backend at all."""

    def __init__(self, generate, model, root, image, workdir, rehearsal_port, tries,
                 plans_dir=PLANS_DIR, fate=None, part_file=None, part_threshold=None, collect=False):
        super().__init__(generate, model, root, image, workdir, rehearsal_port, tries, plans_dir)
        self.fate = fate
        self.part_file = part_file
        self.part_threshold = part_threshold
        self.collect = collect
        self.germline_root = root

    def grow(self, body):
        if not is_molt(body):
            if self.collect:
                text = "the broker is only collecting today; nothing is grown"
                response = refusal_frame(to_wire(text))
                log("collect: %r refused" % body)
                return response, {"text": body, "key": None, "source": "refused", "generation_calls": 0, "rehearsals": [],
                                  "answer_kind": "refusal", "answer_sha256": hashlib.sha256(response).hexdigest(), "answer": text}
            return super().grow(body)
        return self.molt(body)

    def molt(self, body):
        """Returns (response_frame, record_fields), GERMLINE.md's fields
        plus slot, identity, fixture, threshold, build and the frame."""
        slot, ident = molt_request(body)
        key = None
        part = response = None
        fate = threshold = None
        answer_text = None
        if slot is None:
            answer_text = ident
            ident = None
        else:
            key = parts.molt_key(slot, ident)
            if slot not in parts.SLOTS:
                answer_text = "no part for slot %s: ring 8a's slot table holds %s alone" % (slot, ", ".join(parts.SLOTS))
            elif self.collect:
                part, prov = part_lookup(self.germline_root, key)
                if part is None:
                    if prov is not None:
                        answer_text = "the generic stays: this part did not beat it"
                    else:
                        answer_text = "no part grown for this machine"
                else:
                    t = prov["threshold"]
                    threshold = (t["boots"], t["keyboard bytes"], t["mouse packets"])
                    fate = prov.get("name")
                    response = parts.part_frame(part, threshold, 1)
            elif self.part_file:
                part = open(self.part_file, "rb").read()
                threshold = self.part_threshold
                fate = "file"
                response = parts.part_frame(part, threshold, 0)
            elif self.fate is None:
                answer_text = "no part for slot %s: the pipeline runs with --grow, the machine collects with --collect" % slot
            else:
                fate = self.fate
                threshold = parts.FIXTURES[fate]
                part, response = mock_part(fate)
        if response is None:
            response = refusal_frame(to_wire(answer_text))
            log("molt %r: refused: %s" % (body, answer_text))
        else:
            log("molt %r: %s, %d bytes, threshold %s, key %r" % (body, fate, len(part), threshold, key))
        fields = {
            "text": body,
            "key": key,
            "source": ("germline" if self.collect else "fixture") if part is not None else "refused",
            "generation_calls": self.calls,
            "rehearsals": [],
            "answer_kind": "part" if part is not None else "refusal",
            "answer_sha256": hashlib.sha256(response).hexdigest(),
            "answer": answer_text,
            "slot": slot,
            "identity": ident,
            "fixture": fate,
            "threshold": list(threshold) if threshold else None,
            "build": hashlib.sha256(part).hexdigest() if part is not None else None,
            "frame": response.hex(),
        }
        return response, fields


def held(answerer, seconds):
    """The answerer with "? hold" answered after the given wait (A1)."""
    def answer(question):
        if question != HOLD_QUESTION:
            return answerer(question)
        log("? hold: holding the answer for %.0f s" % seconds)
        time.sleep(seconds)
        return b"hold: the mock held this answer for %d s" % round(seconds)
    return answer


# --------------------------------------------------------------- the grow --

REHEARSE = os.path.join(REPO, "stage8", "rehearse8b.py")
DEFAULT_PLAN = os.path.join(REPO, "plans", "parts", "%s.md")


def say(line):
    print(line, flush=True)


def wrap_body(body, name):
    """A flat body from the model: its first 12 bytes are the offsets of
    init, byte and health from the body's start. The host adds the header."""
    if len(body) < 13:
        raise ValueError("the body is too short to hold its three offsets")
    offs = struct.unpack_from("<III", body, 0)
    if any(not 12 <= o < len(body) for o in offs):
        raise ValueError("the body's three offsets do not lie inside it: %r" % (offs,))
    return parts.part_header("i8042", name, body, offs[0] + 96, offs[1] + 96, offs[2] + 96) + body


def candidate(n, plan, key, failure, args):
    """The n-th candidate: (part, source note) or (None, why)."""
    if args.canned:
        if n > len(args.canned):
            return None, "no canned candidate %d" % n
        return open(args.canned[n - 1], "rb").read(), "canned " + os.path.basename(args.canned[n - 1])
    from claude_backend import grow_part
    result = grow_part(plan["text"], key, failure, args.timeout or 900.0, args.model, args.backend_cmd)
    if isinstance(result, str):
        return None, result
    body, src = result
    try:
        part = wrap_body(body, "grown%d" % n)
    except ValueError as exc:
        return None, str(exc)
    d = os.path.join(args.workdir_grow, "candidate-%d" % n)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "source.asm"), "w", encoding="utf-8") as fh:
        fh.write(src)
    return part, "the backend, %d bytes of source" % len(src)


def rehearse(part, n, args):
    d = os.path.join(args.workdir_grow, "candidate-%d" % n)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "part.bin")
    with open(path, "wb") as fh:
        fh.write(part)
    say("rehearsal: starting (the twin; the spec's gates 1 and 3)")
    p = subprocess.run([sys.executable, REHEARSE, path, "--workdir", os.path.join(d, "rehearsal"), "--stick", args.stick],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout.splitlines():
        if line.startswith("rehearsal:"):
            say(line)
    last = [l for l in p.stdout.splitlines() if l.startswith("rehearsal: ")][-1:] or [""]
    return p.returncode == 0, last[0]


def run_grow(slot, args):
    """The pipeline. Exit 0 "beats", 1 "the generic stays", 2 no verdict."""
    from claude_backend import refuse_api_keys, model_name
    refuse_api_keys()
    path = args.plan or (DEFAULT_PLAN % slot)
    plan = bench.read_plan(path)
    identity = args.identity or plan["identity"]
    key = parts.molt_key(slot, identity)
    t = plan["threshold"]
    model = "canned" if args.canned else (model_name(args.model) if not args.backend_cmd else "stub")
    tries = plan["candidates"] if not args.canned else min(plan["candidates"], len(args.canned))
    say("grow: slot %s, identity %r, key %r" % (slot, identity, key))
    say("grow: plan %s, sha256 %s, corpus %d bytes %s, at most %d candidates, model %s"
        % (os.path.relpath(path, REPO), hashlib.sha256(plan["text"].encode()).hexdigest(), len(plan["pairs"]),
           plan["sha256"], plan["candidates"], model))
    failure = None
    outcome = None
    for n in range(1, tries + 1):
        say("candidate %d: asking" % n)
        part, note = candidate(n, plan, key, failure, args)
        if part is None:
            failure = "no candidate: %s" % note
            say("candidate %d: %s" % (n, failure))
            continue
        say("candidate %d: %d bytes from %s, sha256 %s" % (n, len(part), note, hashlib.sha256(part).hexdigest()))
        try:
            fields = parts.check_part(part, slot)
        except ValueError as exc:
            failure = "the door refused it: %s" % exc
            say("candidate %d: %s" % (n, failure))
            continue
        say("candidate %d: the door passed it, name %s" % (n, fields["name"]))
        try:
            m = bench.run_bench(part, plan, workdir=os.path.join(args.workdir_grow, "candidate-%d" % n, "bench"))
        except RuntimeError as exc:
            failure = "the bench: %s" % exc
            say("candidate %d: %s" % (n, failure))
            continue
        say("bench: corpus %d bytes, null decoder %d instructions, %.1f s" % (m["n"], m["null"], m["wall"]))
        diff = bench.differential(m)
        if diff:
            failure = "the differential failed at corpus byte %d: the generic gave %r, the part gave %r" % (
                diff["index"], diff["generic"], diff["part"])
            say("differential: " + failure)
            outcome = {"verdict": "the generic stays", "reason": failure}
            continue
        say("differential: every event identical")
        res = bench.judge(m, plan)
        for line in res["lines"]:
            say("measure: " + line)
        if res["verdict"] != "beats":
            failure = "the measures: " + "; ".join(res["lines"])
            outcome = dict(res, reason="the measures")
            say("candidate %d: the generic stays by the measures" % n)
            continue
        ok, last = rehearse(part, n, args)
        if not ok:
            failure = "the rehearsal in the twin: %s" % last
            outcome = dict(res, verdict="the generic stays", reason=failure)
            say("candidate %d: %s" % (n, failure))
            continue
        prov = {"key": key, "slot": slot, "identity": identity, "plan": os.path.relpath(path, REPO),
                "plan_sha256": hashlib.sha256(plan["text"].encode()).hexdigest(), "corpus_sha256": plan["sha256"],
                "model": model, "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "sha256": hashlib.sha256(part).hexdigest(), "size": len(part), "name": fields["name"],
                "threshold": t, "candidate": n, "null": m["null"],
                "generic": res["generic"], "part": res["part"], "lines": res["lines"], "verdict": "beats"}
        part_write(args.germline, key, prov, part)
        say("verdict: beats")
        say("grow: stored at %s" % os.path.relpath(part_dir(args.germline, key), REPO))
        return 0
    prov = {"key": key, "slot": slot, "identity": identity, "plan": os.path.relpath(path, REPO),
            "plan_sha256": hashlib.sha256(plan["text"].encode()).hexdigest(),
            "model": model, "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "verdict": "the generic stays", "failure": failure, "detail": outcome}
    part_write(args.germline, key, prov)
    say("verdict: the generic stays")
    say("grow: the finding is recorded at %s" % os.path.relpath(part_dir(args.germline, key), REPO))
    return 1


# --------------------------------------------------------------- main ------

def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS broker, Stage 8 ring 8a (stage8/PARTS.md, the molt).")
    ap.add_argument("--mock", action="store_true", help="canned answers, apps, installs and parts; call nothing")
    ap.add_argument("--part", choices=parts.FATES, default="good",
                    help="with --mock: the fixture '! molt i8042' is answered with (default good)")
    ap.add_argument("--part-file", default=None, help="with --mock: serve this part file instead of a fixture")
    ap.add_argument("--part-threshold", default=None, metavar="B,K,M", help="with --part-file: the frame's threshold")
    ap.add_argument("--grow", default=None, metavar="SLOT", help="run the pipeline for SLOT, then exit (ring 8b)")
    ap.add_argument("--collect", action="store_true", help="serve the germline; call no backend at all")
    ap.add_argument("--canned", action="append", default=[], metavar="PART", help="with --grow: a canned candidate (the gate's)")
    ap.add_argument("--backend-cmd", default=None, help="with --grow: this command in place of the word claude (the gate's stub)")
    ap.add_argument("--identity", default=None, help="with --grow: this identity instead of the plan's")
    ap.add_argument("--plan", default=None, help="with --grow: the plan (default plans/parts/<slot>.md)")
    ap.add_argument("--stick", default=os.path.join(STAGE8_OUT, "stick.img"), help="with --grow: the stick the rehearsal boots")
    ap.add_argument("--workdir-grow", default=os.path.join(STAGE8_OUT, "grow"), help="with --grow: its scratch directory")
    ap.add_argument("--hold-s", type=float, default=None, metavar="S",
                    help="hold the answer to '? hold' for S seconds (plan amendment A1)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port on 127.0.0.1 (default 9999)")
    ap.add_argument("--record", default=None, help="append one JSON line per connection to this file")
    ap.add_argument("--timeout", type=float, default=None, help="seconds allowed for one claude -p call (default 120, 900 with --grow)")
    ap.add_argument("--germline", default=os.path.join(REPO, "germline"), help="the cache root (default germline/)")
    ap.add_argument("--image", default=DEFAULT_IMAGE,
                    help="the guest image the twin boots (default stage8/out/esp.img)")
    ap.add_argument("--workdir", default=DEFAULT_WORKDIR,
                    help="the twin's scratch directory (default stage8/out/molt/rehearsal/twin)")
    ap.add_argument("--rehearsal-port", type=int, default=twin.DEFAULT_PORT, help="the twin's listener port (default 9998)")
    ap.add_argument("--tries", type=int, default=2, help="candidates a request may cost (default 2)")
    ap.add_argument("--model", default=None, help="passed to claude -p --model (real mode only)")
    ap.add_argument("--plans", default=PLANS_DIR, help="the plans directory (default plans/)")
    args = ap.parse_args(argv)

    if args.grow:
        return run_grow(args.grow, args)
    timeout = args.timeout or 120.0
    if args.collect:
        def answerer(question):
            return b"the broker is only collecting today; nothing is asked"

        def generate(*_a, **_k):
            raise RuntimeError("--collect calls no backend")

        model = "collect"
        fate = None
        log("collect mode: the germline only; no calls of any kind")
    elif args.mock:
        answerer = mock_answer
        generate = mock_point
        model = "mock"
        fate = args.part
        mock_part(fate)
        log("mock mode: canned answers, apps and installs, and i8042-%s for '! molt i8042'; no calls of any kind" % fate)
    else:
        from claude_backend import ask, grow, model_name  # imported only here

        def answerer(question, _ask=ask, _timeout=timeout):
            return _ask(question.decode("ascii"), _timeout)

        def generate(body, failure, plan=None, _grow=grow, _timeout=timeout, _model=args.model):
            return _grow(body, failure, _timeout, _model, abi=ABI2, plan=plan)

        model = model_name(args.model)
        fate = None
        log("real mode: relaying to claude -p with a %.0f s limit per call; molt requests answered with --grow and --collect"
            % timeout)
    if args.hold_s is not None:
        answerer = held(answerer, args.hold_s)

    molt = Molt(generate, model, args.germline, args.image, args.workdir, args.rehearsal_port,
                args.tries, args.plans, fate, part_file=args.part_file, collect=args.collect,
                part_threshold=tuple(int(x) for x in args.part_threshold.split(",")) if args.part_threshold else None)
    log("germline at %s; plans in %s; the twin boots %s at 1920x1080 on IvyBridge with a 64 MB SATA disk and an e1000e "
        "(%s) on a second cage under %s; rehearsal on 127.0.0.1:%d, %d lines; %d tries"
        % (args.germline, args.plans, args.image, wire.MAC, args.workdir, args.rehearsal_port, LINES, molt.tries))
    return serve(args.port, answerer, molt, args.record, read_timeout=10.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
