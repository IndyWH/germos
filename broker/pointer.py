#!/usr/bin/env python3
"""The GermOS broker for Stage 6 ring 6c - the pointer.

Everything ring 6b's broker does, this one does, by IMPORT and never by
edit: the framing, the record, the listener and the question path from the
frozen broker.py and germline.py; the ABI 2 pipeline as the frozen
glass.Glazier; the install path, the plan's tests as the twin's hook, the
home drive and the machine's display (1920x1080) as the frozen
plans.Installer, subclassed here. Importing plans sets twin.VGA_ARGS, so
every rehearsal this module runs is ring 6b's twin: the home drive,
seventeen lines, the machine's geometry. What this file adds is GLASS.md's
ring 6c section:

  - the section's Python, verbatim: the obs page's pointer fields from
    0x240, the fifth callback's header (POINTER2 at 16, the u32 point
    offset at 24), the arrow, the strip's third field, the choices row's
    click targets;
  - a candidate blob that announces point with an offset outside [28, L)
    is refused BEFORE the twin boots: "the point offset lies beyond the
    blob";
  - the mock's one new canned request, "point app" - stage6/pointer.bin
    with the choice "c clear" - beside GLASS.md's and PLANS.md's tables;
  - a hand run of one blob under one name through this module's twin.

The twin never moves the mouse (the section, "The rehearsal"): a rehearsal
here is exactly ring 6b's, and point is proven on the machine by the gate.

In --mock mode nothing outside the repository is ever called: the
acceptance tests use only the mock, so the gate never spends a token. The
rehearsal still boots a real QEMU. Without --mock the answers come from
broker/claude_backend.py, the one unfrozen file.

This file is frozen acceptance machinery from ring 6c plan item 8: its
dispatch, its mock table, its refusal and the section's Python it carries
are criteria the checker leans on. Standard library only.

Usage:
    python3 broker/pointer.py                 # real: questions, requests, installs
    python3 broker/pointer.py --mock          # canned; no calls of any kind
    python3 broker/pointer.py --rehearse-app stage6/pointer.bin 'point app'
                                              # a hand run of one blob under one
                                              # name in this module's twin

Prints "listening on 127.0.0.1:<port>" to stdout once bound.
"""

import argparse
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from broker import (DEFAULT_PORT, mock_answer, log)  # noqa: E402
from germline import serve  # noqa: E402
from glass import (parse_obs, strip_rows, fmt_ms, fmt_n, CHOICES_SHOWN)  # noqa: E402
import twin  # noqa: E402
import plans  # noqa: E402  - sets twin.VGA_ARGS to the machine's display
from plans import (Installer, mock_install, rehearse_plan, twin_extra_args,  # noqa: E402
                   DISPLAY, TWIN_HOME, DEFAULT_WORKDIR, LINES, PLANS_DIR)
from rehearse import FG, BG  # noqa: E402

# ------------------------------------------------------------ the section -
# stage6/GLASS.md, "Ring 6c - the pointer", "Parsing it cold, in Python",
# verbatim.

OBS_6C = {                       # u64 fields at these byte offsets
    "ptr_x": 0x240, "ptr_y": 0x248, "ptr_cell": 0x250, "packets": 0x258,
    "buttons": 0x260, "mouse_hw": 0x268, "ptr_stamp": 0x270, "ptr_pending": 0x278,
    "pointer_last": 0x280, "pointer_worst": 0x288, "clicks": 0x290, "hits": 0x298,
    "mouse_bytes": 0x2A0, "resyncs": 0x2A8, "mouse_id": 0x2B0, "i8042_cmd": 0x2B8,
}
OBS_PAGE_BYTES_6C = 0x2C0        # what parse_obs_6c needs
POINT_MAGIC = b"POINTER2"        # blob bytes 16-23 announce the fifth callback
POINT_HEADER = 28                # four offsets, the magic, the point offset
POINTER_FIELD_COL = 88           # the strip's third field, row 0
POINTER_BUDGET_MS = 2 * 1000 / 60   # two frame slots
MOUSE_LINE = "S6: mouse ready"
ARROW = bytes([0x01, 0x03, 0x07, 0x0F, 0x1F, 0x0D, 0x19, 0x30])   # bit 0 leftmost
BUTTON_OF_MASK = {1: 1, 2: 2, 4: 3}  # the monitor's mouse_button mask -> point's button
KEY_ESC, KEY_TAB, KEY_ENTER = 0x1B, 9, 13


def parse_obs_6c(page):
    """The obs page's bytes (at least 0x2C0): parse_obs plus the pointer's
    fields, and ptr_row / ptr_col from the cell word."""
    obs = parse_obs(page)
    for field, off in OBS_6C.items():
        obs[field], = struct.unpack_from("<Q", page, off)
    obs["ptr_row"], obs["ptr_col"] = obs["ptr_cell"] >> 16, obs["ptr_cell"] & 0xFFFF
    return obs


def point_offset(blob):
    """None for a four-callback blob; the fifth offset for one that announces
    point; a ValueError when the magic is there with an offset outside [28, L)."""
    if len(blob) < POINT_HEADER or blob[16:24] != POINT_MAGIC:
        return None
    off, = struct.unpack_from("<I", blob, 24)
    if off < POINT_HEADER or off >= len(blob):
        raise ValueError("the point offset lies beyond the blob")
    return off


def pointer_cell(x, y):
    return y // 16, x // 16


def pointer_field(obs):
    t = max(obs["tsc_per_ms"], 1)
    return "pt %s/%s pk %s cl %s" % (fmt_ms(obs["pointer_last"], t), fmt_ms(obs["pointer_worst"], t),
                                     fmt_n(obs["packets"], 4), fmt_n(obs["clicks"], 3))


def strip_rows_6c(obs, now_ticks):
    """The two strip rows exactly as the glass core draws them this ring."""
    row0, row1 = strip_rows(obs, now_ticks)
    if obs["packets"]:
        row0 = row0.ljust(POINTER_FIELD_COL) + pointer_field(obs)
    return row0, row1


def render_arrow():
    """The arrow's 16 pixel rows, as render_cell renders a glyph."""
    rows = []
    for b in ARROW:
        line = b"".join(bytes(FG) * 2 if b >> i & 1 else bytes(BG) * 2 for i in range(8))
        rows += [line, line]
    return rows


def choice_targets(app_running, focus, choices, installed=()):
    """The choices row's click targets for the state, (first column, last
    column, kind, argument): kind "key" with the byte a press types or
    delivers, or "launch" with the installed app's name. Built from the same
    items the row shows (6a's choices_row and HOME.md's extension)."""
    if not app_running:
        items = [("? ask", "key", ord("?")), ("! grow", "key", ord("!"))]
        items += [("! " + name, "launch", name) for name in list(installed)[:CHOICES_SHOWN]]
    elif focus == 0:
        items = [("? ask", "key", ord("?")), ("! grow", "key", ord("!")),
                 ("Tab app", "key", KEY_TAB), ("Esc exit", "key", KEY_ESC)]
    else:
        items = [("%s %s" % (chr(k), label.decode("ascii")), "key", k) for k, label in choices[:CHOICES_SHOWN]]
        items += [("Esc exit", "key", KEY_ESC), ("Tab prompt", "key", KEY_TAB)]
    out = []
    col = 0
    for text, kind, arg in items:
        out.append((col, col + len(text) - 1, kind, arg))
        col += len(text) + 3
    return out


def click_action(targets, col, line_empty=True):
    """What a left press at this column of row R-2 does: None for a gap or
    the tail (and for a launch item while the prompt line holds text);
    ("key", byte) or ("launch", name) otherwise."""
    for first, last, kind, arg in targets:
        if first <= col <= last:
            if kind == "launch" and not line_empty:
                return None
            return kind, arg
    return None


def launch_keys(name):
    """The bytes a launch item types: "! <name>" and Enter."""
    return b"! " + name.encode("ascii") + bytes([KEY_ENTER])


# --------------------------------------------------------------- the mock -
# The section's "canned table for requests, ring 6c": one row beside the
# frozen tables, which are consulted for everything else.

FIXTURES = os.path.join(REPO, "stage6")
POINT_NAME = b"point app"
POINT_CHOICES = [(ord("c"), b"clear")]
POINT_REFUSAL = "the point offset lies beyond the blob"


def fixture(name):
    return open(os.path.join(FIXTURES, name + ".bin"), "rb").read()


def mock_point(body, failure, plan=None):
    """The mock backend: the 6c row for "point app", else PLANS.md's table
    for an install and GLASS.md's for a plain request. Calls nothing."""
    if plan is None and body == "point app":
        return ("app", fixture("pointer"), POINT_NAME, list(POINT_CHOICES))
    return mock_install(body, failure, plan)


# ------------------------------------------------------------- the twin ---

def rehearse_point(blob, name, choices, image, workdir, port=twin.DEFAULT_PORT,
                   plan=None, verdicts=None, lines=LINES):
    """The frozen rehearse_plan - ring 6b's twin - after one check the
    section adds: a blob that announces point with an offset outside
    [28, L) is refused before the twin boots. Returns (passed, phrase, log)."""
    try:
        point_offset(blob)
    except ValueError as exc:
        return False, str(exc), "fail: %s (no twin boot)\n" % exc
    return rehearse_plan(blob, name, choices, image, workdir, port, plan=plan, verdicts=verdicts, lines=lines)


# ------------------------------------------------------------ the pipeline -

class Pointer(Installer):
    """plans.Installer with the section's one check in front of every
    rehearsal. The install path, the germline, the record and the
    dispatch are the frozen ones."""

    def __init__(self, generate, model, root, image, workdir, rehearsal_port, tries,
                 plans_dir=PLANS_DIR):
        super().__init__(generate, model, root, image, workdir, rehearsal_port, tries, plans_dir)
        self.rehearse = rehearse_point

    def install(self, body, rest, name, amendment):
        # The frozen install path calls plans.rehearse_plan by name; an
        # install's candidate gets the same header check by wrapping the
        # module attribute for the duration of the call, restored after.
        saved = plans.rehearse_plan
        plans.rehearse_plan = rehearse_point
        try:
            return super().install(body, rest, name, amendment)
        finally:
            plans.rehearse_plan = saved


# --------------------------------------------------------------- main ------

def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS broker, Stage 6 ring 6c (stage6/GLASS.md, the pointer).")
    ap.add_argument("--mock", action="store_true", help="canned answers, apps and installs; call nothing")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port on 127.0.0.1 (default 9999)")
    ap.add_argument("--record", default=None, help="append one JSON line per connection to this file")
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds allowed for one claude -p call (default 120)")
    ap.add_argument("--germline", default=os.path.join(REPO, "germline"), help="the cache root (default germline/)")
    ap.add_argument("--image", default=os.path.join(REPO, "stage6", "out", "esp.img"),
                    help="the guest image the twin boots (default stage6/out/esp.img)")
    ap.add_argument("--workdir", default=DEFAULT_WORKDIR,
                    help="the twin's scratch directory (default stage6/out/rehearsal/twin)")
    ap.add_argument("--rehearsal-port", type=int, default=twin.DEFAULT_PORT, help="the twin's listener port (default 9998)")
    ap.add_argument("--tries", type=int, default=2, help="candidates a request may cost (default 2)")
    ap.add_argument("--model", default=None, help="passed to claude -p --model (real mode only)")
    ap.add_argument("--plans", default=PLANS_DIR, help="the plans directory (default plans/)")
    ap.add_argument("--rehearse-app", nargs=2, metavar=("BLOB", "NAME"), default=None,
                    help="a hand run: rehearse this blob under this name in the twin, print the log, exit")
    ap.add_argument("--lines", type=int, default=LINES, help="with --rehearse-app: the S6: lines expected (default 17)")
    args = ap.parse_args(argv)

    if args.rehearse_app:
        blob = open(args.rehearse_app[0], "rb").read()
        name = args.rehearse_app[1].encode("ascii")
        choices = list(POINT_CHOICES) if name == POINT_NAME else []
        ok, why, text = rehearse_point(blob, name, choices, args.image, args.workdir, args.rehearsal_port,
                                       lines=args.lines)
        sys.stdout.write(text)
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
            return _grow(body, failure, _timeout, _model, abi=2, plan=plan)

        model = model_name(args.model)
        log("real mode: relaying to claude -p with a %.0f s limit per call" % args.timeout)

    pointer = Pointer(generate, model, args.germline, args.image, args.workdir, args.rehearsal_port,
                      args.tries, args.plans)
    log("germline at %s; plans in %s; the twin boots %s at 1920x1080 with %s; rehearsal on 127.0.0.1:%d; %d tries"
        % (args.germline, args.plans, args.image, TWIN_HOME, args.rehearsal_port, pointer.tries))
    return serve(args.port, answerer, pointer, args.record, read_timeout=10.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
