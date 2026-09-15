#!/usr/bin/env python3
"""The GermOS broker for Stage 7 ring 7b - the wire.

Everything ring 7a's broker does, this one does, by IMPORT and never by
edit: the framing, the record and the listener from the frozen broker.py
and germline.py; the ABI 2 pipeline as the frozen glass.Glazier; the
install path and the plan's tests as the frozen plans.Installer; the
fifth callback's check as the frozen pointer.Pointer; DISK.md's Python,
the SATA disk and the twin that reads a Stage 7 guest as the frozen
metal.Metal and metal.rehearse_metal. What this file adds is
stage7/WIRE.md's twin: an e1000e on a SECOND restricted cage beside the
frozen twin's virtio-net, handed to the frozen twin's command through
rehearse_metal's extra_args seam, and nineteen S7: lines expected through
its lines seam - the guest chooses the e1000e, prints "S7: link up", and
reaches the rehearsal's listener on 127.0.0.1:9998 through the second
cage. metal.py's own twin command and metal.twin_extra_args are not
touched: ring 7a's frozen gate keeps judging them.

In --mock mode nothing outside the repository is ever called: the
acceptance tests use only the mock, so the gate never spends a token. The
rehearsal still boots a real QEMU. Without --mock the answers come from
broker/claude_backend.py, the one unfrozen backend.

This file becomes frozen acceptance machinery at ring 7b plan item 10
(deviation 10, A3's precedent: after the gate has passed nine of nine
through it): its twin's command and its verdicts are criteria the checker
leans on. Standard library only.

Usage:
    python3 broker/wire.py                  # real: questions, requests, installs
    python3 broker/wire.py --mock           # canned; no calls of any kind
    python3 broker/wire.py --rehearse-app stage6/app.bin 'test app'
    python3 broker/wire.py --rehearse stage6/echo.bin plans/echo.md
                                            # hand runs in this module's twin

Prints "listening on 127.0.0.1:<port>" to stdout once bound.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from broker import (DEFAULT_PORT, mock_answer, log)  # noqa: E402
from germline import serve  # noqa: E402
from glass import ABI  # noqa: E402
import twin  # noqa: E402
import plans  # noqa: E402  - sets twin.VGA_ARGS to the machine's display
from plans import (Installer, PLANS_DIR, parse_plan)  # noqa: E402
from pointer import (mock_point, point_offset, POINT_NAME, POINT_CHOICES)  # noqa: E402
import metal  # noqa: E402
from metal import (Metal, rehearse_metal, tests_hook_metal, READY)  # noqa: E402

# --------------------------------------------------------------- the wire --
# stage7/WIRE.md, "The serial lines" and "The twin".

LINES = 19                           # the S7: lines a ring 7b guest prints on a disk it formats
LINES_7A = metal.LINES               # ring 7a's eighteen, the virtio path's - kept for the record
MAC = "6c:3b:e5:3b:86:45"            # the patient's 82579LM; the twin's e1000e carries it
RELAY_PORT = 9997                    # the relay in the twin (9999 the broker, 9998 the rehearsal listener)
NETDEV_ID = "n1"                     # the second cage, beside the frozen twin's n0
STAGE7_OUT = os.path.join(REPO, "stage7", "out")
DEFAULT_IMAGE = os.path.join(STAGE7_OUT, "esp.img")
DEFAULT_WORKDIR = os.path.join(STAGE7_OUT, "wire", "rehearsal", "twin")


def e1000e_netdev(port=twin.DEFAULT_PORT):
    """UMBILICAL.md's cage on the second netdev, its guestfwd landing on
    the given port on 127.0.0.1."""
    return "user,id=%s,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 %d" % (NETDEV_ID, port)


def e1000e_device(mac=MAC):
    return "e1000e,netdev=%s,mac=%s" % (NETDEV_ID, mac)


def wire_extra_args(port=twin.DEFAULT_PORT):
    """What this ring appends to the twin's command after metal's own
    additions: the second cage and the e1000e on it. The one place the
    twin's NIC is spelled."""
    return ["-netdev", e1000e_netdev(port), "-device", e1000e_device()]


def twin_extra_args(workdir, port=twin.DEFAULT_PORT):
    """Everything the twin's frozen command gains in this ring - ring 7a's
    CPU and SATA disk, then this ring's cage and NIC - exactly as
    rehearse_metal assembles it. Test 4 inspects the command it lands in."""
    return metal.twin_extra_args(workdir) + wire_extra_args(port)


def rehearse_wire_plan(blob, name, choices, image, workdir, port=twin.DEFAULT_PORT,
                       plan=None, verdicts=None, lines=LINES):
    """This module's twin behind ring 6c's check: a blob that announces
    point with an offset outside [28, L) is refused before any boot; then
    the frozen-to-be rehearse_metal with the e1000e's cage appended and
    nineteen lines expected, the plan's tests as the hook for an install
    and no hook for a plain request. Returns (passed, phrase, log)."""
    try:
        point_offset(blob)
    except ValueError as exc:
        return False, str(exc), "fail: %s (no twin boot)\n" % exc
    after = None if plan is None else tests_hook_metal(plan["tests"], [] if verdicts is None else verdicts)
    return rehearse_metal(blob, name, choices, image, workdir, port,
                          extra_args=wire_extra_args(port), lines=lines, after=after)


# ------------------------------------------------------------ the pipeline -

class Wire(Metal):
    """metal.Metal with this module's twin in front of every rehearsal.
    The install path, the germline, the record and the dispatch are the
    frozen ones."""

    def __init__(self, generate, model, root, image, workdir, rehearsal_port, tries,
                 plans_dir=PLANS_DIR):
        super().__init__(generate, model, root, image, workdir, rehearsal_port, tries, plans_dir)
        self.rehearse = rehearse_wire_plan

    def install(self, body, rest, name, amendment):
        # The frozen install path calls plans.rehearse_plan by name; the
        # module attribute is swapped for this module's twin for the
        # duration of the call and restored after - Installer.install
        # directly, since Metal.install would swap in ring 7a's twin.
        saved = plans.rehearse_plan
        plans.rehearse_plan = rehearse_wire_plan
        try:
            return Installer.install(self, body, rest, name, amendment)
        finally:
            plans.rehearse_plan = saved


# --------------------------------------------------------------- main ------

def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS broker, Stage 7 ring 7b (stage7/WIRE.md, the wire).")
    ap.add_argument("--mock", action="store_true", help="canned answers, apps and installs; call nothing")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port on 127.0.0.1 (default 9999)")
    ap.add_argument("--record", default=None, help="append one JSON line per connection to this file")
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds allowed for one claude -p call (default 120)")
    ap.add_argument("--germline", default=os.path.join(REPO, "germline"), help="the cache root (default germline/)")
    ap.add_argument("--image", default=DEFAULT_IMAGE,
                    help="the guest image the twin boots (default stage7/out/esp.img)")
    ap.add_argument("--workdir", default=DEFAULT_WORKDIR,
                    help="the twin's scratch directory (default stage7/out/wire/rehearsal/twin)")
    ap.add_argument("--rehearsal-port", type=int, default=twin.DEFAULT_PORT, help="the twin's listener port (default 9998)")
    ap.add_argument("--tries", type=int, default=2, help="candidates a request may cost (default 2)")
    ap.add_argument("--model", default=None, help="passed to claude -p --model (real mode only)")
    ap.add_argument("--plans", default=PLANS_DIR, help="the plans directory (default plans/)")
    ap.add_argument("--rehearse-app", nargs=2, metavar=("BLOB", "NAME"), default=None,
                    help="a hand run: rehearse this blob under this name in the twin, print the log, exit")
    ap.add_argument("--rehearse", nargs=2, metavar=("BLOB", "PLAN"), default=None,
                    help="a hand run: rehearse this build against this plan's tests in the twin, print the log, exit")
    ap.add_argument("--lines", type=int, default=LINES, help="with a hand run: the S7: lines expected (default 19)")
    args = ap.parse_args(argv)

    if args.rehearse_app:
        blob = open(args.rehearse_app[0], "rb").read()
        name = args.rehearse_app[1].encode("ascii")
        choices = list(POINT_CHOICES) if name == POINT_NAME else []
        ok, why, text = rehearse_wire_plan(blob, name, choices, args.image, args.workdir, args.rehearsal_port,
                                           lines=args.lines)
        sys.stdout.write(text)
        print("PASS" if ok else "FAIL: " + why)
        return 0 if ok else 1

    if args.rehearse:
        blob = open(args.rehearse[0], "rb").read()
        plan = parse_plan(open(args.rehearse[1]).read())
        verdicts = []
        ok, why, text = rehearse_wire_plan(blob, plan["name"].encode(), plan["choices"], args.image, args.workdir,
                                           args.rehearsal_port, plan=plan, verdicts=verdicts, lines=args.lines)
        sys.stdout.write(text)
        for v in verdicts:
            print(v)
        print("PASS" if ok else "FAIL: " + why)
        return 0 if ok else 1

    if args.mock:
        answerer = mock_answer
        generate = mock_point
        model = "mock"
        log("mock mode: canned answers, apps and installs, no calls of any kind")
    else:
        from claude_backend import ask, grow, model_name  # imported only here

        def answerer(question, _ask=ask, _timeout=args.timeout):
            return _ask(question.decode("ascii"), _timeout)

        def generate(body, failure, plan=None, _grow=grow, _timeout=args.timeout, _model=args.model):
            return _grow(body, failure, _timeout, _model, abi=ABI, plan=plan)

        model = model_name(args.model)
        log("real mode: relaying to claude -p with a %.0f s limit per call" % args.timeout)

    wire = Wire(generate, model, args.germline, args.image, args.workdir, args.rehearsal_port,
                args.tries, args.plans)
    log("germline at %s; plans in %s; the twin boots %s at 1920x1080 on IvyBridge with a 64 MB SATA disk and an e1000e "
        "(%s) on a second cage under %s; rehearsal on 127.0.0.1:%d; %d tries"
        % (args.germline, args.plans, args.image, MAC, args.workdir, args.rehearsal_port, wire.tries))
    return serve(args.port, answerer, wire, args.record, read_timeout=10.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
