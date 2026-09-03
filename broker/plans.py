#!/usr/bin/env python3
"""The GermOS broker for Stage 6 ring 6b - the store of plans.

Everything ring 6a's broker does, this one does, by IMPORT and never by
edit: the framing, the record, the listener and the question path from the
frozen broker.py and germline.py; the ABI 2 pipeline - generate, rehearse,
cache, deliver - as the frozen glass.Glazier, subclassed here (plan-6a
amendment A2 built it to be); the twin as the frozen twin.rehearse, driven
through the two seams that amendment left open: extra QEMU arguments (the
home drive), the expected line count (seventeen) and the post-delivery
hook (the plan's tests). What this file adds is stage6/PLANS.md:

  - a body "install <name>" or "install <name>, <amendment>" is an
    INSTALL: the plan plans/<name>.md is read, its intent and tests go into
    the generation brief, the candidate is rehearsed in the twin against
    the plan's own five-verb tests on top of GLASS.md's nine criteria, the
    proven build is cached under a key made from the plan's hash, and the
    frame is delivered with the installed byte set - so the guest writes
    it to its home image (stage6/HOME.md) before running it;
  - a refused install names the failed test in the plan's own words:
    "rehearsal failed: expect \"a\"";
  - every other request takes the inherited path unchanged, and questions
    are answered as before.

The display: ring 6b's guest, twin and oracle all run at 1920x1080 (the
owner's decision at ring 6a's oracle), so this module sets twin.VGA_ARGS -
a module constant the frozen file reads at call time - before any
rehearsal. The twin is the exact machine again.

In --mock mode installs come from PLANS.md's canned table (the echo and
liar fixtures, the padded echo), plain requests from GLASS.md's, questions
from UMBILICAL.md's, and nothing outside the repository is ever called:
the acceptance tests use only the mock, so the gate never spends a token.
The rehearsal still boots a real QEMU. Without --mock the answers come from
broker/claude_backend.py - grow(abi=2, plan=...) with the plan brief - the
one unfrozen file.

This file is frozen acceptance machinery from ring 6b plan item 8: its
dispatch, its key, its mock table and its record are criteria the checker
leans on. Standard library only.

Usage:
    python3 broker/plans.py                 # real: questions, requests and installs
    python3 broker/plans.py --mock          # canned; no calls of any kind
    python3 broker/plans.py --rehearse stage6/echo.bin plans/echo.md [--lines 17]
                                            # a hand run of one build against one
                                            # plan in the twin; prints the log

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
from broker import (DEFAULT_PORT, to_wire, mock_answer, log)  # noqa: E402
from germline import serve  # noqa: E402
import glass  # noqa: E402
from glass import (Glazier, app_frame, refusal_frame, glass_lookup, germline_write,  # noqa: E402
                   mock_generate, parse_obs, regions, ABI, CELL_BLOCK)
import twin  # noqa: E402
from rehearse import (read_ppm, load_font, render_cell, BG, FG, CELL, DISK_BYTES, KEY_GAP)  # noqa: E402

# ------------------------------------------------------------ the display -
# Spelled once. The owner's decision at ring 6a's oracle: 1920x1080. The
# frozen twin reads VGA_ARGS when it builds its command, so this is set here
# and the twin rehearses on the machine's own geometry (120x67 cells).

DISPLAY = ["-vga", "none", "-device", "VGA,edid=on,xres=1920,yres=1080"]
twin.VGA_ARGS = DISPLAY

LINES = 17                       # the S6: lines a ring 6b guest prints with two disks
PLANS_DIR = os.path.join(REPO, "plans")
TWIN_HOME = os.path.join(REPO, "stage6", "out", "rehearsal", "home.img")
DEFAULT_WORKDIR = os.path.join(REPO, "stage6", "out", "rehearsal", "twin")
SETTLE = 0.5                     # seconds an expect waits after a press before it looks
PAD_BIG = 4096                   # "install echo, but big": the build padded to this

# --------------------------------------------------------------- the plan -
# stage6/PLANS.md, "Parsing it cold, in Python", verbatim.

NAME_RE = re.compile(r"[a-z][a-z0-9-]{0,31}")
PRESSABLE = set(range(0x20, 0x7F)) - {0x60, 0x7E}      # not ` or ~
EXPECT_MAX = 60
WAIT_MAX = 30000
CHOICES = 4
LABEL_MAX = 12
MACHINE = "qemu-q35-ovmf"


def parse_plan(text):
    """The plan file's text. Returns {"name", "intent", "choices": [(key,
    label bytes)], "tests": [(verb, arg)]} with verbs "press" (arg the
    keys), "wait" (arg the ms), "expect", "expect not" (arg the text) and
    "expect changed" (arg None); raises ValueError("line N: ...")."""
    if not all(b in (0x09, 0x0A) or 0x20 <= b <= 0x7E for b in text.encode("latin-1", "replace")):
        raise ValueError("line 0: the plan is not plain ASCII")
    lines = text.split("\n")
    name = None
    section = None
    seen = []
    intent, choices, tests = [], [], []
    for n, raw in enumerate(lines, 1):
        line = raw.rstrip()
        if not line.strip():
            continue
        if name is None:
            m = re.fullmatch(r"# (%s)" % NAME_RE.pattern, line)
            if not m:
                raise ValueError("line %d: the first line must be '# <name>'" % n)
            name = m.group(1)
            continue
        if line.startswith("#"):
            if line not in ("## Intent", "## Choices", "## Tests") or line in seen \
                    or line != ("## Intent", "## Choices", "## Tests")[len(seen)]:
                raise ValueError("line %d: unexpected heading %r" % (n, line))
            seen.append(line)
            section = line
            continue
        if section == "## Intent":
            intent.append(line.strip())
        elif section == "## Choices":
            m = re.fullmatch(r"(\S) (.{1,%d})" % LABEL_MAX, line.strip())
            if not m or len(choices) >= CHOICES:
                raise ValueError("line %d: a choice is '<key> <label>' (1-12 bytes), four at most" % n)
            choices.append((ord(m.group(1)), m.group(2).strip().encode("ascii")))
        elif section == "## Tests":
            tests.append(parse_test(n, raw.rstrip("\r\n")))
        else:
            raise ValueError("line %d: text before '## Intent'" % n)
    if name is None:
        raise ValueError("line 0: empty plan")
    if len(seen) != 3:
        raise ValueError("line 0: missing section(s) %r" % [s for s in ("## Intent", "## Choices", "## Tests") if s not in seen])
    if not intent:
        raise ValueError("line 0: the intent is empty")
    if not tests:
        raise ValueError("line 0: no tests")
    return {"name": name, "intent": "\n".join(intent), "choices": choices, "tests": tests}


def parse_test(n, line):
    if line.startswith("press "):
        keys = line[6:]
        if not keys or any(ord(c) not in PRESSABLE for c in keys):
            raise ValueError("line %d: press needs one or more keys, printable, not ` or ~" % n)
        return ("press", keys)
    m = re.fullmatch(r"wait (\d+)", line.rstrip())
    if m:
        ms = int(m.group(1))
        if not 1 <= ms <= WAIT_MAX:
            raise ValueError("line %d: wait takes 1 to %d ms" % (n, WAIT_MAX))
        return ("wait", ms)
    if line.rstrip() == "expect changed":
        return ("expect changed", None)
    m = re.fullmatch(r'expect( not)? "([^"]{1,%d})"' % EXPECT_MAX, line.rstrip())
    if m:
        return ("expect not" if m.group(1) else "expect", m.group(2))
    raise ValueError("line %d: not one of the five verbs: %r" % (n, line))


def install_body(body):
    """Is this grow body an install? None if not; else (rest, name,
    amendment) with name None when the rest is not '<name>' or
    '<name>, <amendment>'."""
    if body != "install" and not body.startswith("install "):
        return None
    rest = body[7:].strip()
    name, amendment = rest, None
    if "," in rest:
        name, amendment = (s.strip() for s in rest.split(",", 1))
        if not amendment:
            name = None
    if name is not None and not NAME_RE.fullmatch(name):
        name = None
    return rest, name, amendment


def normalise(body):
    return " ".join(body.lower().split())


def install_key(name, plan_bytes, amendment=None, machine=MACHINE):
    s = "install %s|%s|%s|abi2|%s" % (name, hashlib.sha256(plan_bytes).hexdigest(),
                                      normalise(amendment or ""), machine)
    return hashlib.sha256(s.encode("ascii")).hexdigest()[:16]


def test_line(verb, arg):
    """The verb back as the line it was parsed from - the refusal's words."""
    if verb == "press":
        return "press " + arg
    if verb == "wait":
        return "wait %d" % arg
    if verb == "expect changed":
        return verb
    return '%s "%s"' % (verb, arg)


def read_plan(plans_dir, name):
    """(plan_bytes, parsed) for plans/<name>.md; (None, None) when there is
    no such file; raises ValueError when it does not parse."""
    path = os.path.join(plans_dir, name + ".md")
    if not os.path.isfile(path):
        return None, None
    data = open(path, "rb").read()
    return data, parse_plan(data.decode("latin-1"))


# ------------------------------------------------------- the twin's keys --
# The monitor's key names for every byte a plan may press: the US layout,
# Shift where the guest's shifted map needs it. Measured before the plan:
# 94 of the 96 printables arrive byte-exact; ` and ~ do not, and the grammar
# excludes them.

UNSHIFTED = {
    "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", "0": "0",
    "-": "minus", "=": "equal", "[": "bracket_left", "]": "bracket_right", "\\": "backslash",
    ";": "semicolon", "'": "apostrophe", ",": "comma", ".": "dot", "/": "slash", " ": "spc",
}
SHIFTED = {
    "!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8", "(": "9", ")": "0",
    "_": "minus", "+": "equal", "{": "bracket_left", "}": "bracket_right", "|": "backslash",
    ":": "semicolon", '"': "apostrophe", "<": "comma", ">": "dot", "?": "slash",
}


def plan_keyname(ch):
    if ch in UNSHIFTED:
        return UNSHIFTED[ch]
    if ch in SHIFTED:
        return "shift-" + SHIFTED[ch]
    if "a" <= ch <= "z":
        return ch
    if "A" <= ch <= "Z":
        return "shift-" + ch.lower()
    raise ValueError("no monitor key name for %r" % ch)


# --------------------------------------------------------- the panel read -

class Glyphs:
    """Every cell the glass can draw, rendered once: an exact lookup from a
    cell's 16 pixel rows to its character (" " blank, "\\x01" block)."""

    def __init__(self):
        font = load_font()
        self.table = {}
        for v in range(0x21, 0x7F):
            self.table[tuple(render_cell(font, chr(v)))] = chr(v)
        self.table[tuple([bytes(BG) * CELL] * CELL)] = " "
        self.table[tuple([bytes(FG) * CELL] * CELL)] = "\x01"

    def cell(self, pixels, width, row, col):
        rows = []
        x0 = col * CELL * 3
        for dy in range(CELL):
            base = ((row * CELL + dy) * width) * 3 + x0
            rows.append(pixels[base:base + CELL * 3])
        return self.table.get(tuple(rows), "?")


def panel_rows(shot, region, glyphs):
    """Every row of the region (row0, col0, rows, cols) of a screendump, as
    text read cell by cell through the shared font."""
    width, height, pixels = read_ppm(shot)
    row0, col0, nrows, ncols = region
    out = []
    for r in range(nrows):
        out.append("".join(glyphs.cell(pixels, width, row0 + r, col0 + c) for c in range(ncols)))
    return out


def region_pixels(shot, region):
    """The region's pixel bytes, scanline by scanline, for a comparison."""
    width, height, pixels = read_ppm(shot)
    row0, col0, nrows, ncols = region
    out = []
    for y in range(row0 * CELL, (row0 + nrows) * CELL):
        base = (y * width + col0 * CELL) * 3
        out.append(pixels[base:base + ncols * CELL * 3])
    return b"".join(out)


# ------------------------------------------------------- the tests hook ---

def tests_hook(tests, verdicts):
    """The post-delivery hook for twin.rehearse: runs the plan's tests in
    order while the app has the keys, appends "ok: <line>" or "fail:
    <line>" to verdicts, and returns [] or [the failing line]."""

    def after(drv, xp):
        m = re.search(rb"S6: obs page 0x([0-9a-f]{16})", drv.serial_bytes())
        if not m:
            raise ValueError("no obs page line on the twin's serial")
        obs = drv.read_obs(int(m.group(1), 16))
        regs = regions(obs["cols"], obs["rows"])
        if regs is None:
            raise ValueError("the twin's mode is too small for the glass")
        panel = regs["app"]
        glyphs = Glyphs()
        looks = 0

        def look():
            nonlocal looks
            looks += 1
            path = os.path.join(drv.workdir, "look.%d.ppm" % looks)
            if not drv.screendump(path):
                raise ValueError("no screendump for look %d" % looks)
            return path

        last = look()
        pressed = False
        for verb, arg in tests:
            line = test_line(verb, arg)
            ok = True
            if verb == "press":
                for ch in arg:
                    drv.tell(b"sendkey " + plan_keyname(ch).encode() + b"\n")
                    time.sleep(KEY_GAP)
                pressed = True
            elif verb == "wait":
                time.sleep(arg / 1000.0)
            else:
                if pressed:
                    time.sleep(SETTLE)
                    pressed = False
                shot = look()
                if verb == "expect changed":
                    ok = region_pixels(shot, panel) != region_pixels(last, panel)
                else:
                    rows = panel_rows(shot, panel, glyphs)
                    found = any(arg in row for row in rows)
                    ok = found if verb == "expect" else not found
                last = shot
            verdicts.append(("ok: " if ok else "fail: ") + line)
            if not ok:
                return [line]
        return []

    return after


# ------------------------------------------------------------- the twin ---

def twin_extra_args(home=TWIN_HOME):
    """The home drive the twin boots with - the one QEMU argument this ring
    adds. Test 4 inspects the command it lands in."""
    return ["-drive", "format=raw,file=" + home + ",if=virtio"]


def fresh_home(path=TWIN_HOME):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.truncate(DISK_BYTES)


def rehearse_plan(blob, name, choices, image, workdir, port=twin.DEFAULT_PORT,
                  plan=None, verdicts=None, lines=LINES):
    """The frozen twin at the machine's display with a blank home drive,
    seventeen lines expected, and - for an install - the plan's tests as
    the post-delivery hook. Returns twin.rehearse's (passed, phrase, log)."""
    fresh_home()
    after = None if plan is None else tests_hook(plan["tests"], [] if verdicts is None else verdicts)
    return twin.rehearse(blob, name, choices, image, workdir, port,
                         extra_args=twin_extra_args(), lines=lines, after=after)


# --------------------------------------------------------------- the mock -
# stage6/PLANS.md, "The mock's canned table for installs".

FIXTURES = os.path.join(REPO, "stage6")
NO_CANNED = "mock: no canned build for plan: "


def fixture(name):
    return open(os.path.join(FIXTURES, name + ".bin"), "rb").read()


def mock_install(body, failure, plan=None):
    """The mock backend: GLASS.md's table for a plain request, PLANS.md's
    for an install. Calls nothing."""
    if plan is None:
        return mock_generate(body, failure)
    name = plan["name"].encode("ascii")
    if body == "install echo":
        return ("app", fixture("echo"), name, plan["choices"])
    if body == "install liar":
        return ("app", fixture("liar"), name, plan["choices"])
    if body == "install echo, but big":
        blob = fixture("echo")
        return ("app", blob + bytes(PAD_BIG - len(blob)), name, plan["choices"])
    return ("refusal", NO_CANNED + plan["name"])


# ------------------------------------------------------------ the pipeline -

class Installer(Glazier):
    """glass.Glazier with the install path. generate(body, failure, plan)
    returns ("app", blob, name, choices) or ("refusal", text); plan is None
    on the inherited path."""

    def __init__(self, generate, model, root, image, workdir, rehearsal_port, tries,
                 plans_dir=PLANS_DIR):
        super().__init__(generate, model, root, image, workdir, rehearsal_port, tries,
                         rehearse=rehearse_plan)
        self.plans_dir = plans_dir

    def grow(self, body):
        ib = install_body(body)
        if ib is None:
            return super().grow(body)
        return self.install(body, *ib)

    def install(self, body, rest, name, amendment):
        """Returns (response_frame, record_fields), the record's fields
        GLASS.md's plus plan, plan_sha256, amendment and tests."""
        rehearsals = []
        tests = []
        app = None
        source = None
        answer_text = None
        key = None
        plan_bytes = plan = None
        if name is not None:
            try:
                plan_bytes, plan = read_plan(self.plans_dir, name)
            except ValueError as exc:
                answer_text = "plan %s does not parse: %s" % (name, exc)
        if answer_text is None and plan is None:
            answer_text = "no plan named " + rest
        if answer_text is not None:
            source = "refused"
            log("install %r: %s" % (body, answer_text))
        else:
            key = install_key(name, plan_bytes, amendment)
            pname = name.encode("ascii")
            cached = glass_lookup(self.root, key)
            if cached is not None:
                app = (cached[0], pname, plan["choices"])
                source = "germline"
                log("install %r: served from the germline (%s)" % (body, key))
            else:
                failure = None
                phrase = None
                for attempt in range(1, self.tries + 1):
                    self.calls += 1
                    log("install %r: generation call %d (try %d of %d)" % (body, self.calls, attempt, self.tries))
                    candidate = self.generate(body, failure, dict(plan, amendment=amendment))
                    if candidate[0] == "refusal":
                        answer_text = candidate[1]
                        source = "refused"
                        log("install %r: the backend refused: %s" % (body, answer_text[:80]))
                        break
                    blob = candidate[1]
                    verdicts = []
                    t0 = time.time()
                    passed, phrase, rlog = rehearse_plan(blob, pname, plan["choices"], self.image, self.workdir,
                                                         self.rehearsal_port, plan=plan, verdicts=verdicts)
                    seconds = time.time() - t0
                    rehearsals.append("pass" if passed else "fail: " + phrase)
                    tests = verdicts
                    log("install %r: rehearsal %s in %.0f s; tests %s" % (body, rehearsals[-1], seconds, verdicts))
                    if passed:
                        app = (blob, pname, plan["choices"])
                        germline_write(self.root, key, body, blob, pname, plan["choices"], self.model, attempt,
                                       seconds, rlog, {"plan": name, "plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
                                                       "amendment": amendment, "installed": True,
                                                       "plan_tests": verdicts})
                        source = "generated"
                        break
                    errs = [l for l in rlog.splitlines() if l.startswith("ERR:")]
                    failure = phrase + ((" - " + errs[0]) if errs else "")
                if app is None and answer_text is None:
                    answer_text = "rehearsal failed: " + phrase
                    source = "refused"
        if app is not None:
            blob, pname, choices = app
            response = app_frame(blob, pname, choices, 1 if source == "germline" else 0, installed=1)
            kind = "app"
        else:
            pname = None
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
            "name": pname.decode("ascii") if pname else None,
            "plan": plan["name"] if plan else None,
            "plan_sha256": hashlib.sha256(plan_bytes).hexdigest() if plan_bytes else None,
            "amendment": amendment if plan else None,
            "tests": tests,
        }
        fields.update(self.extra_record)
        return response, fields


# --------------------------------------------------------------- main ------

def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS broker, Stage 6 ring 6b (stage6/PLANS.md).")
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
    ap.add_argument("--rehearse", nargs=2, metavar=("BLOB", "PLAN"), default=None,
                    help="a hand run: rehearse this build against this plan's tests in the twin, print the log, exit")
    ap.add_argument("--lines", type=int, default=LINES, help="with --rehearse: the S6: lines expected (default 17)")
    args = ap.parse_args(argv)

    if args.rehearse:
        blob = open(args.rehearse[0], "rb").read()
        plan = parse_plan(open(args.rehearse[1]).read())
        verdicts = []
        ok, why, text = rehearse_plan(blob, plan["name"].encode(), plan["choices"], args.image, args.workdir,
                                      args.rehearsal_port, plan=plan, verdicts=verdicts, lines=args.lines)
        sys.stdout.write(text)
        for v in verdicts:
            print(v)
        print("PASS" if ok else "FAIL: " + why)
        return 0 if ok else 1

    if args.mock:
        answerer = mock_answer
        generate = mock_install
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

    installer = Installer(generate, model, args.germline, args.image, args.workdir, args.rehearsal_port,
                          args.tries, args.plans)
    log("germline at %s; plans in %s; the twin boots %s at 1920x1080 with %s; rehearsal on 127.0.0.1:%d; %d tries"
        % (args.germline, args.plans, args.image, TWIN_HOME, args.rehearsal_port, installer.tries))
    return serve(args.port, answerer, installer, args.record, read_timeout=10.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
