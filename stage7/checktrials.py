#!/usr/bin/env python3
"""Stage 7 ring 7d acceptance checker - the trials: the choices row as
text (layout A) against boxes (layout B), a synthetic human clicking the
cued item in the twin of the HP, the notebook as the case-report form,
the verdict by TRIALS.md's frozen rule.

Modes (all from the repo root, invoked by stage7/test-7d.sh):

  --document   test 1's second half: stage7/TRIALS.md parsed cold by
               stage7/trials.py and both worked examples reproduced.
  --row        test 2: one boot at -smp 4 from a fresh stick copy on a
               fresh disk with the relay and the mock up for one grow:
               "! trial" refused while an app runs ("an app is running",
               nothing journaled); then "! trial" starting sitting 1 -
               the serial line, the mode word, ring 6c's row to the pixel
               on the A block, the cue line; block 1 played; the B block's
               row as TRIALS.md's boxes, in the surface's bytes and on
               the screen.
  --sitting    test 3: five boots on one disk - sitting 1 to done with
               the numbers predicted, the abort, sittings 3 and 4 to the
               verdict B, the default read at boot, the reserved prefix
               refused, the click on a box (plan item 5).
  --cage       test 4: the argv check, the payload table and the spot
               checks (plan item 6).

Every count and every line a run must give is the script expanded by
TRIALS.md's rules through stage7/trials.py; the only literals from a run
are the timing constants below, each dated. Written before the guest
code it judges and frozen behind the hook once written. Everything it
starts is QEMU with OVMF, the patient's CPU model, the display at
1920x1080, the caged network to the relay on 127.0.0.1, the stick copy
over xhci, the SATA disk on ide.1, the PS/2 mouse driven through the
monitor; every drive a raw file under stage7/out/. It talks only to the
mock broker (broker/wire.py --mock, for the one grow) and never spends a
token; the trial itself sends nothing.
"""

import os
import re
import shutil
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "stage7", "out")
TRIALS_OUT = os.path.join(OUT, "trials")
STICK = os.path.join(OUT, "stick.img")
DISK = os.path.join(TRIALS_OUT, "disk.img")
OVMF = "/usr/share/ovmf/OVMF.fd"

sys.path.insert(0, os.path.join(REPO, "stage6"))
sys.path.insert(0, os.path.join(REPO, "stage7"))
sys.path.insert(0, os.path.join(REPO, "broker"))
import checkmetal  # noqa: E402  - ring 7c's frozen checker: the twin of the HP
from checkmetal import (qemu_argv, fresh_disk, fresh_stick, check_boot_lines, strip_mouse_line,  # noqa: E402
                        check_stick_tables_unchanged, start_relay, start_mock, geometry_of,
                        PATTERNS_BLANK, PATTERNS_AGAIN, MOUSE_LINE_BYTES, READY, RELAY_PORT, BROKER_PORT,
                        METAL_OUT)
from checkglass import (say, report, dump_capture, check_region_rows, check_mode_field, check_choices,  # noqa: E402
                        check_counts, check_echo, read_record, check_grow_entry, record_count, port_state,
                        stop_mock, fixture_self_check, open_shot, PROMPT, SETTLE)
from checkpointer import (Pointer, expected_counts, target_col, park_cell, check_arrow_at,  # noqa: E402
                          check_panel_cells, CELL)
import checkdisk  # noqa: E402
from checkdisk import read_image  # noqa: E402
from rehearse import render_cell, cell_matches, BG, FG, KEY_GAP  # noqa: E402
from glass import regions, app_frame, TEST_CHOICES  # noqa: E402
from pointer import choice_targets  # noqa: E402
from checkplans import CHOICES_PROMPT_ECHO  # noqa: E402,F401
import twin  # noqa: E402
from twin import Driver  # noqa: E402
from plans import plan_keyname  # noqa: E402
import metal  # noqa: E402
import trials  # noqa: E402  - TRIALS.md's Python, executed from the document
from trials import (ITEMS, ROW_ITEMS, CUES_PER_BLOCK, BLOCKS, PAUSE_MS, REST_MS, MODE_TRIAL, SOLID, INVERSE,  # noqa: E402
                    order, layout, cue_sequence, median, serial_of, notes_of, parse_note, box_cells, boxes,
                    box_targets, table_of, check_blocks, verdict_of, verdict_detail, sitting_number,
                    default_layout, mode_word_7d, parse_obs_7d, OBS_PAGE_BYTES_7D)

STAGES_SMP = 4
ROW_TEXT = "   ".join(ROW_ITEMS)                       # the four-item row, layout A
ROW_TARGETS = choice_targets(True, 0, [])              # its targets, from the frozen 6c section
assert [t[0:2] for t in ROW_TARGETS] == [(0, 4), (8, 13), (17, 23), (27, 34)]
ROW_KINDS = [(k, a) for _, _, k, a in ROW_TARGETS]
TRIAL_LINE = re.compile(rb"trial: [^\r\n]*")

# ------------------------------------------------- the timing constants --
# The spec's numbers, by rule:
SLACK_MS = 30                 # a block's median against the scripted median: the spec's window, never widened
# From the item 7 run against the private binary (plan decision 10), each
# dated; None until then - the checker refuses to play while any is unset.
OFFSET_MS = None              # the median of (recorded ms - scripted d) over a sitting
HIT_WINDOW_MS = None          # the per-hit sanity window, CC's own (plan: 60 unless the run says wider)
READY_LIMIT_S = None          # the ready window for a boot from the stick copy
SETTLE_S = None               # after ready, before typing (a full notebook's replay)
POLL_S = 0.005                # the serial file's poll (item 1: a key's round trip is 5-20 ms at this poll)
UNSET = [n for n, v in (("OFFSET_MS", OFFSET_MS), ("HIT_WINDOW_MS", HIT_WINDOW_MS),
                        ("READY_LIMIT_S", READY_LIMIT_S), ("SETTLE_S", SETTLE_S)) if v is None]


def require_constants():
    if UNSET:
        say("the timing constants %s are not set - they are written from the item 7 run, never guessed" % ", ".join(UNSET))
        return False
    return True


# ----------------------------------------------------------- the pixels --

def inverse_cell(font, ch):
    """A layout B cell: render_cell with the two colours swapped."""
    fg, bg, tmp = bytes(FG), bytes(BG), b"\x01\x02\x03"
    return [row.replace(fg, tmp).replace(bg, fg).replace(tmp, bg) for row in render_cell(font, ch)]


def cell_want(font, byte):
    if byte & INVERSE:
        return inverse_cell(font, chr(byte & 0x7F))
    if 0x20 <= byte <= 0x7E:
        return render_cell(font, chr(byte))
    return render_cell(font, " ")


def check_choices_bytes(shot, geometry, cells, label, skip=()):
    """The two rows of the choices region on the screen equal to these
    surface bytes cell for cell (the arrow's cell skipped)."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    row0, col0, nrows, ncols = regions(cols, rows)["choices"]
    problems = []
    for r in range(2):
        for c in range(ncols):
            if (row0 + r, col0 + c) in skip:
                continue
            if not cell_matches(pixels, width, row0 + r, col0 + c, cell_want(font, cells[r][c])):
                problems.append("%s: choices row %d column %d is not surface byte 0x%02x" % (label, r, c, cells[r][c]))
                return problems
    return problems


def check_layout_b(shot, reads, geometry, labels, label):
    """The choices surface's bytes are TRIALS.md's boxes for these labels,
    and the screen shows them inverse, cell for cell."""
    cols = geometry[2]
    want0, want1 = box_cells(cols, labels)
    got = reads.get("choices")
    problems = []
    if got is None:
        return ["%s: the choices surface was not read" % label]
    if got[:cols] != want0 or got[cols:2 * cols] != want1:
        problems.append("%s: the choices surface is not TRIALS.md's boxes for %r (row 0 %r..., want %r...)"
                        % (label, labels, got[:40], want0[:40]))
    problems += check_choices_bytes(shot, geometry, (want0, want1), label)
    return problems


# ------------------------------------------------------------ the driver --
# checkmetal.drive's skeleton with one more step, ("play", Human, script,
# results): the synthetic human, which needs the monitor, the serial file
# and the model together, so it cannot be a list of fixed steps.

class Human:
    """The synthetic human (plan decision 6). It knows the cue table and the
    order, so it parks its hand on the next cued target during the pause and
    presses at the scripted delay by the host clock, anchored on the guest's
    own trial: line in the serial file. Every event it emits is counted for
    the page's counters."""

    def __init__(self, drv, model, geometry, events, sitting):
        self.drv, self.model, self.geometry, self.events, self.sitting = drv, model, geometry, events, sitting
        w, h, cols, rows = geometry
        self.cols = cols
        self.crow = regions(cols, rows)["choices"][0]
        self.log = []                       # (host time, what)
        self.offset = 0                     # the serial file, read so far

    # -- the serial file, polled
    def wait_line(self, pattern, limit):
        rx = re.compile(pattern)
        deadline = time.time() + limit
        while time.time() < deadline:
            data = self.drv.serial_bytes()
            m = rx.search(data, self.offset)
            if m:
                self.offset = m.end()
                return m, time.time()
            time.sleep(POLL_S)
        return None, time.time()

    # -- the monitor
    def move(self, dx, dy):
        self.drv.tell(b"mouse_move %d %d\n" % (dx, dy))
        self.model.move(dx, dy)
        self.events.append(("mouse", dx, dy))
        time.sleep(0.02)

    def moveto(self, row, col):
        for _, dx, dy in self.model.moves_to(row, col):
            self.move(dx, dy)

    def press(self, hit):
        self.drv.tell(b"mouse_button 1\n")
        self.events.append(("button", 1, "hit") if hit else ("button", 1))
        time.sleep(0.05)
        self.drv.tell(b"mouse_button 0\n")
        self.events.append(("button", 0))

    def type(self, text):
        for ch in text:
            name = twin.keyname(ch) if ch in "\n\t\x1b" else plan_keyname(ch)
            self.drv.tell(b"sendkey " + name.encode() + b"\n")
            time.sleep(KEY_GAP)
        self.events.append(("type", text))

    # -- the targets
    def target(self, L, idx):
        """(row, col) of the cell the hand rests on for item idx in layout L."""
        if L == "A":
            return self.crow, target_col(ROW_TARGETS, ROW_KINDS[idx][0], ROW_KINDS[idx][1])
        b = boxes(self.cols, len(ROW_ITEMS))[idx]
        return self.crow + 1, (b[2] + b[3]) // 2

    def gap(self, L):
        if L == "A":
            return self.crow, ROW_TARGETS[0][1] + 2          # the first three-space gap
        return self.crow, boxes(self.cols, len(ROW_ITEMS))[0][1]   # the first gap column

    # -- the play
    def play(self, script, results, blocks=None, abort=None, after=None, on_start=None):
        """Play the sitting's script: blocks = how many blocks to play (all
        by default); abort = (block, hits before Esc); after = a callable
        run at each rest (block number) - the obs read; on_start = a
        callable run once the sitting line is on serial, before the first
        press (a screendump of the first cue). Fills results with the host
        times and what was seen. Returns None or a problem."""
        s = self.sitting
        m, t_sit = self.wait_line(rb"trial: sitting %d ([AB]{4} [AB]{4})" % s, 20.0)
        if not m:
            return "no 'trial: sitting %d' line on serial within 20 s" % s
        results["order"] = m.group(1).decode()
        results["sitting_at"] = t_sit
        anchor = t_sit
        if on_start:
            on_start()
        n_blocks = blocks or BLOCKS
        for b in range(1, n_blocks + 1):
            L = layout(s, b)
            seq = cue_sequence(b)
            blk = script["blocks"][b - 1]
            cue_at = anchor + (REST_MS / 1000.0 if b > 1 else 0.0)
            for c in range(1, CUES_PER_BLOCK + 1):
                if abort and abort[0] == b and c == abort[1] + 1:
                    self.type("\x1b")
                    m, t = self.wait_line(rb"trial: sitting %d aborted (\d+)" % s, 10.0)
                    if not m:
                        return "no aborted line after Esc in block %d" % b
                    results["aborted"] = int(m.group(1))
                    results["aborted_at"] = t
                    return None
                idx = ITEMS.index(seq[c - 1])
                d = blk["ms"][c - 1] / 1000.0
                if c in blk.get("miss", ()):
                    self.moveto(*self.gap(L))
                    time.sleep(max(0.0, cue_at + PAUSE_MS / 1000.0 + d - time.time()))
                    self.press(False)
                    m, t = self.wait_line(rb"trial: %d %d %s %d miss" % (s, b, L.encode(), c), 5.0)
                    if not m:
                        return "no miss line for sitting %d block %d cue %d" % (s, b, c)
                    self.moveto(*self.target(L, idx))
                    time.sleep(max(0.0, t + d - time.time()))
                else:
                    self.moveto(*self.target(L, idx))
                    time.sleep(max(0.0, cue_at + PAUSE_MS / 1000.0 + d - time.time()))
                self.press(False)
                m, t = self.wait_line(rb"trial: %d %d %s %d (\d+)" % (s, b, L.encode(), c), 5.0)
                if not m:
                    return "no hit line for sitting %d block %d cue %d" % (s, b, c)
                results.setdefault("hits", {})[(b, c)] = int(m.group(1))
                cue_at = t                        # the next cue follows the pause after this hit
            m, t = self.wait_line(rb"trial: block %d %d %s (\d+) (\d+) (\d+)" % (s, b, L.encode()), 5.0)
            if not m:
                return "no block line for sitting %d block %d" % (s, b)
            results.setdefault("blocks", {})[b] = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            anchor = t
            if after:
                after(b)
        if n_blocks == BLOCKS:
            m, t = self.wait_line(rb"trial: sitting %d done" % s, 5.0)
            if not m:
                return "no done line for sitting %d" % s
            results["done_at"] = t
        return None


def drive_7d(smp, disk, stick_copy, steps, serial_path, ready=READY, ready_limit=60.0, settle=1.0):
    """Boot from the stick copy inside the cage, wait for the guest's own
    ready line, run the steps, quit, reap. The step vocabulary is
    checkmetal.drive's - ("type", text), ("sleep", s), ("wait_record", path,
    count, timeout), ("shot", path), ("obs", label), ("surfaces", label),
    ("serial", label), ("mouse", dx, dy), ("button", mask[, "hit"]),
    ("moveto", row, col) - plus ("play", script, results, kwargs) and
    ("park",). The obs page is parsed by TRIALS.md's parse_obs_7d. Returns
    (serial_bytes, reads, events, error); never leaves a QEMU running."""
    reads = {"counts": {}, "model": {}}
    events = []
    if not os.path.isfile(STICK):
        return b"", reads, events, "no stick was built"
    if not os.path.isfile(OVMF):
        return b"", reads, events, "OVMF firmware not found at " + OVMF
    if os.path.exists(serial_path):
        os.remove(serial_path)
    for step in steps:
        if step[0] == "shot" and os.path.exists(step[1]):
            os.remove(step[1])
    proc = subprocess.Popen(qemu_argv(smp, disk, stick_copy, serial_path),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    drv = Driver(proc, serial_path, TRIALS_OUT)
    err = None
    obs_addr = None
    model = None
    try:
        deadline = time.time() + ready_limit
        got_ready = False
        while time.time() < deadline:
            time.sleep(0.05)
            if proc.poll() is not None:
                break
            if ready in drv.serial_bytes():
                got_ready = True
                break
        if not got_ready:
            err = "the guest never printed %r within %.0fs" % (ready.decode(), ready_limit)
            if proc.poll() is not None:
                err += " (qemu exited %d: %s)" % (proc.returncode, proc.stderr.read().decode(errors="replace").strip()[:300])
            else:
                errs = re.findall(rb"ERR: [^\r\n]*", drv.serial_bytes())
                if errs:
                    err += " (the guest said: %s)" % errs[0].decode(errors="replace")
        else:
            time.sleep(settle)
            geo = geometry_of(drv.serial_bytes())
            if geo:
                model = Pointer(*geo)
                w, h = geo
                geometry = (w, h, w // CELL, h // CELL)
                reads["geometry"] = geometry

            def note(label):
                reads["counts"][label] = expected_counts(events)
                reads["model"][label] = model.cell() if model else None

            def mouse(dx, dy):
                drv.tell(b"mouse_move %d %d\n" % (dx, dy))
                if model:
                    model.move(dx, dy)
                events.append(("mouse", dx, dy))
                time.sleep(0.02)

            def page():
                nonlocal obs_addr
                if obs_addr is None:
                    m = re.search(r"S7: obs page 0x([0-9a-f]+)", drv.serial_bytes().decode("utf-8", "replace"))
                    obs_addr = int(m.group(1), 16) if m else 0
                if not obs_addr:
                    raise ValueError("no obs page line on serial")
                return parse_obs_7d(drv.xp(obs_addr, OBS_PAGE_BYTES_7D // 8, "g"))

            for step in steps:
                if step[0] == "type":
                    for ch in step[1]:
                        if ch in "\n\t\x1b":
                            name = twin.keyname(ch)
                        elif ch == "\b":
                            name = "backspace"
                        else:
                            name = plan_keyname(ch)
                        drv.tell(b"sendkey " + name.encode() + b"\n")
                        time.sleep(KEY_GAP)
                    events.append(("type", step[1]))
                elif step[0] == "sleep":
                    time.sleep(step[1])
                elif step[0] == "wait_record":
                    _, path, count, limit = step
                    until = time.time() + limit
                    while time.time() < until and record_count(path) < count:
                        time.sleep(0.2)
                    if record_count(path) < count:
                        say("(the broker record did not reach %d connection(s) within %.0fs)" % (count, limit))
                elif step[0] == "shot":
                    drv.screendump(step[1])
                elif step[0] == "mouse":
                    mouse(step[1], step[2])
                elif step[0] == "moveto":
                    if model is None:
                        say("(no geometry on serial - cannot move the pointer to a cell)")
                        continue
                    for _, dx, dy in model.moves_to(step[1], step[2]):
                        mouse(dx, dy)
                elif step[0] == "park":
                    if model is not None:
                        pr, pc = park_cell(geometry)
                        for _, dx, dy in model.moves_to(pr, pc):
                            mouse(dx, dy)
                        time.sleep(0.5)
                elif step[0] == "button":
                    drv.tell(b"mouse_button %d\n" % step[1])
                    events.append(tuple(step))
                    time.sleep(0.05)
                elif step[0] == "serial":
                    reads[step[1]] = drv.serial_bytes()
                    note(step[1])
                elif step[0] in ("obs", "surfaces"):
                    try:
                        p = page()
                        if step[0] == "obs":
                            reads[step[1]] = p
                        else:
                            reads[step[1]] = {name: drv.read_surface(p[name])
                                              for name in ("strip", "choices", "conversation", "app")}
                            reads[step[1]]["obs"] = p
                        note(step[1])
                    except ValueError as exc:
                        say("(xp for %r failed: %s)" % (step[1], exc))
                elif step[0] == "play":
                    _, script, results, kwargs = step
                    if model is None:
                        err = "no geometry on serial - the human cannot play"
                        break
                    human = Human(drv, model, geometry, events, script["sitting"])
                    kw = dict(kwargs)
                    start_shot = kw.pop("start_shot", None)
                    if start_shot:
                        def on_start(results=results, path=start_shot):
                            human.moveto(*park_cell(geometry))
                            time.sleep(0.3)
                            drv.screendump(path)
                            try:
                                results["start_obs"] = page()
                            except ValueError as exc:
                                say("(xp at the sitting's start failed: %s)" % exc)
                        kw["on_start"] = on_start
                    if kw.pop("read_at_rest", False):
                        def at_rest(b, results=results):
                            try:
                                results.setdefault("rest_obs", {})[b] = page()
                            except ValueError as exc:
                                say("(xp at the rest after block %d failed: %s)" % (b, exc))
                        kw["after"] = at_rest
                    problem = human.play(script, results, **kw)
                    results["events_after"] = expected_counts(events)
                    if problem:
                        err = problem
                        break
        drv.tell(b"quit\n")
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        try:
            proc.stdin.close()
        except OSError:
            pass
    return drv.serial_bytes(), reads, events, err


def trial_lines(capture):
    """The trial: lines on serial, in order, as notes; and the capture
    without them (and without the mouse line), for the echo check."""
    lines = [m.group(0).decode() for m in TRIAL_LINE.finditer(capture)]
    stripped = TRIAL_LINE.sub(b"", capture).replace(MOUSE_LINE_BYTES, b"")
    stripped = re.sub(rb"(\r\n){2,}", b"\r\n", stripped)
    return [trials.note_of_serial(l) for l in lines], stripped


def notes_on_disk(disk):
    """The notes partition of the gate's disk, by DISK.md and NOTEBOOK.md."""
    data = read_image(disk)
    table = metal.parse_gpt(data)
    return checkdisk.parse_notebook(metal.partition_bytes(data, table["notes"]))


# ----------------------------------------------------- test 1: the document --

def run_document():
    r = subprocess.run([sys.executable, os.path.join(HERE, "trials.py"), "--example"], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True)
    for line in r.stdout.strip().splitlines():
        say(line)
    if r.returncode:
        say("TRIALS.md or trials.py: the worked examples are not reproduced")
        return 1
    problems = []
    if trials.DOCUMENT["cues"] != trials.CUES or len(trials.CUES) != BLOCKS:
        problems.append("the cue table")
    if (order(1), order(2)) != ("ABBA BAAB", "BAAB ABBA"):
        problems.append("the orders")
    if trials.OBS_7D["trial_sitting"] != 0x2E0 or trials.OBS_7D["layout_default"] != 0x338 or OBS_PAGE_BYTES_7D != 0x360:
        problems.append("the obs table")
    if MODE_TRIAL != 5 or mode_word_7d({"mode": 5, "trial_layout": 0, "trial_block": 3, "name": ""}) != "trial A 3/8".ljust(18):
        problems.append("the mode word")
    if [b[:2] for b in boxes(120, 4)] != [(0, 29), (30, 59), (60, 89), (90, 119)] or \
            [trials.label_col(b, l) for b, l in zip(boxes(120, 4), ROW_ITEMS)] != [12, 41, 71, 101]:
        problems.append("the boxes on the twin's 120 columns")
    if serial_of("trial sitting 1 ABBA BAAB") != "trial: sitting 1 ABBA BAAB":
        problems.append("the serial rule")
    if not report("TRIALS.md does not say what the plan says", problems):
        return 1
    say("TRIALS.md parsed cold: eight cue rows, the two orders, the obs fields from 0x2E0 with the zero rule from 0x360, "
        "mode 5's word, the twin's boxes at 0-28/30-58/60-88/90-119 with the labels at 12, 41, 71, 101, the serial rule")
    return 0


# ---------------------------------------------------- test 2: the row --------
# One boot: the mode-3 refusal, then sitting 1's first block on layout A
# and the second block's row on layout B.

SCRIPT_ROW = {"sitting": 1, "blocks": [{"ms": [200] * CUES_PER_BLOCK, "miss": []}] + [{"ms": [200] * CUES_PER_BLOCK}] * 7,
              "abort": None}


def run_row():
    if not require_constants():
        return 1
    smp = STAGES_SMP
    blob, problems = fixture_self_check("app")
    if not report("the app fixture is not what the repository says", problems):
        return 1
    record = os.path.join(TRIALS_OUT, "broker.row.jsonl")
    rlog = os.path.join(TRIALS_OUT, "relay.row.jsonl")
    shots = {k: os.path.join(TRIALS_OUT, "screen.row.%s.ppm" % k) for k in ("refuse", "a", "b")}
    relay, err = start_relay(rlog)
    if err:
        say(err)
        return 1
    mock, err = start_mock(record)
    if err:
        say(err)
        stop_mock(relay)
        return 1
    say("the row: the relay on %d -> the mock on %d for one grow, a fresh disk, a fresh stick copy, -smp %d; '! test app', Tab, "
        "'! trial' refused, Esc, '! trial', block 1 on layout A, block 2's row on layout B" % (RELAY_PORT, BROKER_PORT, smp))
    copy = fresh_stick(os.path.join(TRIALS_OUT, "stick.row.img"))
    results = {}
    try:
        fresh_disk(DISK)
        steps = [
            ("type", "! test app\n"), ("wait_record", record, 1, 150.0), ("sleep", 3.0),
            ("type", "\t"), ("sleep", 1.0),
            ("type", "! trial\n"), ("sleep", 1.5), ("shot", shots["refuse"]), ("obs", "refuse"),
            ("type", "\x1b"), ("sleep", 1.5),
            ("serial", "before"),
            ("play", SCRIPT_ROW, results, {"blocks": 1, "start_shot": shots["a"]}),
            ("sleep", 2.6), ("park",), ("surfaces", "b"), ("shot", shots["b"]), ("obs", "b2"),
        ]
        capture, reads, events, err = drive_7d(smp, DISK, copy, steps, os.path.join(TRIALS_OUT, "serial.row.txt"),
                                               ready_limit=READY_LIMIT_S, settle=SETTLE_S)
    finally:
        stop_mock(mock)
        stop_mock(relay)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    ok = True
    geometry = reads.get("geometry")
    notes_serial, stripped = trial_lines(capture)
    problems, stripped2 = strip_mouse_line(capture)
    problems = []
    more, geometry_b = check_boot_lines(stripped, smp, True, "formatted", 0, checkmetal.DISK_SECTORS)
    problems += more
    problems += check_echo(stripped, b"! test app\r\n! trial\r\n! trial\r\n")
    ok &= report("the row boot's serial log is not what the plan asks for", problems, capture)
    if not problems:
        say("%d S7: lines with the i8042: pair; the wire after ready carries the typed lines and the trial: lines only" % len(PATTERNS_BLANK))

    # the refusal while the app runs
    problems = []
    regs = regions(geometry[2], geometry[3])
    problems += check_region_rows(shots["refuse"], geometry, regs["conversation"], ["! trial", "an app is running", PROMPT])
    problems += check_mode_field(shots["refuse"], geometry, "running test app")
    problems += check_choices(shots["refuse"], geometry, ROW_TEXT)
    if "refuse" in reads:
        problems += check_counts(reads["refuse"], {"mode": 3, "errors": 1, "trial_sitting": 0, "trial_block": 0, "notes": 0,
                                                   "layout_default": 0}, "the refusal")
    else:
        problems.append("the obs page could not be read at the refusal")
    ok &= report("'! trial' with an app running is not refused as TRIALS.md says", problems)
    if not problems:
        say("'an app is running' under '! trial' in the conversation, the prompt back, mode 3 with the four-item row, errors 1, nothing journaled")

    # the sitting's start: layout A's row to the pixel, the cue line, the page
    problems = []
    if results.get("order") != order(1):
        problems.append("the sitting line's order is %r, want %r" % (results.get("order"), order(1)))
    problems += check_region_rows(shots["a"], geometry, regs["conversation"],
                                  ["! trial", "sitting 1 " + order(1), "click: " + cue_sequence(1)[0]])
    problems += check_mode_field(shots["a"], geometry, "trial A 1/8")
    problems += check_choices(shots["a"], geometry, ROW_TEXT)
    if "start_obs" in results:
        problems += check_counts(results["start_obs"], {"mode": MODE_TRIAL, "trial_sitting": 1, "trial_block": 1, "trial_layout": 0,
                                                        "trial_cue": 1, "trial_target": ITEMS.index(cue_sequence(1)[0]),
                                                        "cue_pending": 0, "trial_hits": 0, "trial_misses": 0, "notes": 1,
                                                        "layout_default": 0}, "the sitting's start")
        if results["start_obs"]["cue_stamp"] == 0:
            problems.append("cue_stamp is 0 at the first cue")
    else:
        problems.append("the obs page could not be read at the sitting's start")
    ok &= report("the sitting's start is not what TRIALS.md says", problems)
    if not problems:
        say("'! trial', 'sitting 1 %s' and 'click: %s' in the conversation, 'trial A 1/8' on the strip, ring 6c's four-item row to "
            "the pixel with its margin blank, the page in mode 5 at cue 1" % (order(1), cue_sequence(1)[0]))

    # block 1 on layout A, block 2 on layout B
    problems = []
    want_serial = notes_of({"sitting": 1, "blocks": SCRIPT_ROW["blocks"][:1], "abort": None})[:CUES_PER_BLOCK + 2]
    got = notes_serial[:len(want_serial)]
    for w, g in zip(want_serial, got):
        pw, pg = parse_note(w), parse_note(g)
        if pg is None or pw["kind"] != pg["kind"] or (pw["kind"] != "hit" and w != g) or \
                (pw["kind"] == "hit" and (pw["sitting"], pw["block"], pw["layout"], pw["cue"]) != (pg["sitting"], pg["block"], pg["layout"], pg["cue"])):
            problems.append("serial line %r, want %r" % (g, w))
            break
    if len(notes_serial) < len(want_serial):
        problems.append("%d trial: lines on serial, want at least %d" % (len(notes_serial), len(want_serial)))
    if "b2" in reads:
        problems += check_counts(reads["b2"], {"mode": MODE_TRIAL, "trial_sitting": 1, "trial_block": 2, "trial_layout": 1,
                                               "trial_cue": 1, "trial_target": ITEMS.index(cue_sequence(2)[0]), "cue_pending": 0,
                                               "trial_hits": 0, "trial_misses": 0, "hits": 0, "layout_default": 0,
                                               "notes": CUES_PER_BLOCK + 2}, "block 2")
        if reads["b2"]["cue_stamp"] == 0:
            problems.append("cue_stamp is 0 in block 2")
    else:
        problems.append("the obs page could not be read in block 2")
    problems += check_mode_field(shots["b"], geometry, "trial B 2/8")
    problems += check_layout_b(shots["b"], reads.get("b", {}), geometry, ROW_ITEMS, "block 2")
    problems += check_region_rows(shots["b"], geometry, regs["conversation"],
                                  ["block 1 of 8 - rest", "click: " + cue_sequence(2)[0]])
    ok &= report("the sitting's start, block 1 on layout A or block 2's row on layout B is not what TRIALS.md says", problems)
    if not problems:
        say("'trial: sitting 1 %s' on serial; block 1's ten hits and its block line; block 2: 'trial B 2/8' on the strip, "
            "the choices surface TRIALS.md's boxes for the four items and the screen their inverse rendering cell for cell, "
            "the rest line and the cue in the conversation, the page's trial fields" % order(1))
    say("the row: %s" % ("both layouts as TRIALS.md draws them" if ok else "not what TRIALS.md says"))
    return 0 if ok else 1


# --------------------------------------------------------------- main ------

def main(argv):
    os.makedirs(TRIALS_OUT, exist_ok=True)
    if argv == ["--document"]:
        return run_document()
    if argv == ["--row"]:
        return run_row()
    say("usage: checktrials.py --document | --row | --sitting | --cage")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
