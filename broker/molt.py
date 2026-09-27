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
table's threshold and source 0; nothing is rehearsed (the pipeline is
ring 8b's). A slot other than i8042, or a body that is not PARTS.md's
request, gets a refusal frame. Without --mock a molt body is refused
too: the real grow path arrives with ring 8b.

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
import os
import re
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


# ------------------------------------------------------------ the pipeline -

class Molt(Wire):
    """wire.Wire with PARTS.md's molt request in front of its dispatch.
    fate is the fixture served in mock mode, or None when real."""

    def __init__(self, generate, model, root, image, workdir, rehearsal_port, tries,
                 plans_dir=PLANS_DIR, fate=None):
        super().__init__(generate, model, root, image, workdir, rehearsal_port, tries, plans_dir)
        self.fate = fate

    def grow(self, body):
        if not is_molt(body):
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
            elif self.fate is None:
                answer_text = "no part for slot %s: the molt pipeline is ring 8b's" % slot
            else:
                fate = self.fate
                threshold = parts.FIXTURES[fate]
                part, response = mock_part(fate)
        if response is None:
            response = refusal_frame(to_wire(answer_text))
            log("molt %r: refused: %s" % (body, answer_text))
        else:
            log("molt %r: fixture i8042-%s, %d bytes, threshold %s, key %r" % (body, fate, len(part), threshold, key))
        fields = {
            "text": body,
            "key": key,
            "source": "fixture" if part is not None else "refused",
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


# --------------------------------------------------------------- main ------

def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS broker, Stage 8 ring 8a (stage8/PARTS.md, the molt).")
    ap.add_argument("--mock", action="store_true", help="canned answers, apps, installs and parts; call nothing")
    ap.add_argument("--part", choices=parts.FATES, default="good",
                    help="with --mock: the fixture '! molt i8042' is answered with (default good)")
    ap.add_argument("--hold-s", type=float, default=None, metavar="S",
                    help="hold the answer to '? hold' for S seconds (plan amendment A1)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port on 127.0.0.1 (default 9999)")
    ap.add_argument("--record", default=None, help="append one JSON line per connection to this file")
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds allowed for one claude -p call (default 120)")
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

    if args.mock:
        answerer = mock_answer
        generate = mock_point
        model = "mock"
        fate = args.part
        mock_part(fate)
        log("mock mode: canned answers, apps and installs, and i8042-%s for '! molt i8042'; no calls of any kind" % fate)
    else:
        from claude_backend import ask, grow, model_name  # imported only here

        def answerer(question, _ask=ask, _timeout=args.timeout):
            return _ask(question.decode("ascii"), _timeout)

        def generate(body, failure, plan=None, _grow=grow, _timeout=args.timeout, _model=args.model):
            return _grow(body, failure, _timeout, _model, abi=ABI2, plan=plan)

        model = model_name(args.model)
        fate = None
        log("real mode: relaying to claude -p with a %.0f s limit per call; molt requests refused until ring 8b"
            % args.timeout)
    if args.hold_s is not None:
        answerer = held(answerer, args.hold_s)

    molt = Molt(generate, model, args.germline, args.image, args.workdir, args.rehearsal_port,
                args.tries, args.plans, fate)
    log("germline at %s; plans in %s; the twin boots %s at 1920x1080 on IvyBridge with a 64 MB SATA disk and an e1000e "
        "(%s) on a second cage under %s; rehearsal on 127.0.0.1:%d, %d lines; %d tries"
        % (args.germline, args.plans, args.image, wire.MAC, args.workdir, args.rehearsal_port, LINES, molt.tries))
    return serve(args.port, answerer, molt, args.record, read_timeout=10.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
