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
if os.environ.get("CHECKTRIALS_PROBE"):          # the item 7 run against the private binary: "offset,hit,ready,settle"
    OFFSET_MS, HIT_WINDOW_MS, READY_LIMIT_S, SETTLE_S = [float(x) for x in os.environ["CHECKTRIALS_PROBE"].split(",")]
    OFFSET_MS, HIT_WINDOW_MS = int(OFFSET_MS), int(HIT_WINDOW_MS)
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
            cue_at = anchor + (REST_MS / 1000.0 if b > 1 else 0.0)     # the first cue: at the sitting line, or after the rest
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
                    time.sleep(max(0.0, cue_at + d - time.time()))
                    self.press(False)
                    m, t = self.wait_line(rb"trial: %d %d %s %d miss" % (s, b, L.encode(), c), 5.0)
                    if not m:
                        return "no miss line for sitting %d block %d cue %d" % (s, b, c)
                    self.moveto(*self.target(L, idx))
                    time.sleep(max(0.0, t + d - time.time()))
                else:
                    self.moveto(*self.target(L, idx))
                    time.sleep(max(0.0, cue_at + d - time.time()))
                self.press(False)
                m, t = self.wait_line(rb"trial: %d %d %s %d (\d+)" % (s, b, L.encode(), c), 5.0)
                if not m:
                    return "no hit line for sitting %d block %d cue %d" % (s, b, c)
                results.setdefault("hits", {})[(b, c)] = int(m.group(1))
                cue_at = t + PAUSE_MS / 1000.0    # the next cue follows the pause after this hit
            m, t = self.wait_line(rb"trial: block %d %d %s (\d+) (\d+) (\d+)" % (s, b, L.encode()), 5.0)
            if not m:
                return "no block line for sitting %d block %d" % (s, b)
            results.setdefault("blocks", {})[b] = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            anchor = t
            if after and b < BLOCKS:
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


# --------------------------------------------------- test 3: the sittings ---
# Five boots on one disk (plan decision 8, deviations 4 and 8): sitting 1 to
# done with the numbers predicted; sitting 2 aborted in block 3; sittings 3
# and 4 to done and the verdict B; then a boot with no trial - the default
# read from the notebook, the reserved prefix refused (A1), a click on a box.
# The scripts: ten delays a block in ms and the cues missed first; every
# expected note is notes_of(script) through TRIALS.md's rules; every block
# median is the rule over the scripted delays plus OFFSET_MS.

def _blocks(*lists, miss=()):
    m = dict(miss)
    return [{"ms": list(l), "miss": list(m.get(i + 1, ()))} for i, l in enumerate(lists)]


SCRIPT_1 = {"sitting": 1, "abort": None, "blocks": _blocks(
    [280, 320, 300, 340, 260, 310, 330, 290, 300, 270],     # 1 A
    [180, 220, 200, 240, 160, 210, 230, 190, 200, 170],     # 2 B  - cue 4 missed first
    [190, 210, 170, 230, 200, 180, 220, 160, 240, 200],     # 3 B
    [300, 330, 270, 310, 290, 340, 280, 320, 300, 260],     # 4 A  - cue 7 missed first
    [170, 200, 190, 220, 180, 240, 160, 230, 210, 200],     # 5 B
    [290, 310, 300, 280, 340, 320, 260, 330, 270, 300],     # 6 A
    [310, 280, 300, 340, 290, 260, 330, 320, 270, 300],     # 7 A  - cue 2 missed first
    [200, 170, 230, 190, 210, 160, 240, 180, 220, 200],     # 8 B
    miss={2: (4,), 4: (7,), 7: (2,)})}
SCRIPT_ABORT = {"sitting": 2, "abort": (3, 3), "blocks": _blocks(
    [200, 220, 180, 210, 190, 230, 170, 200, 240, 160],     # 1 B
    [300, 280, 320, 290, 310, 260, 340, 300, 270, 330],     # 2 A
    [290, 300, 310, 280, 320, 270, 330, 260, 340, 300])}    # 3 A - three hits, then Esc
SCRIPT_3 = {"sitting": 3, "abort": None, "blocks": _blocks(
    [270, 300, 330, 290, 310, 260, 340, 280, 320, 300],     # 1 A
    [160, 200, 240, 180, 220, 170, 230, 190, 210, 200],     # 2 B
    [200, 180, 220, 160, 240, 190, 210, 170, 230, 200],     # 3 B
    [330, 290, 310, 270, 340, 300, 260, 320, 280, 300],     # 4 A
    [230, 190, 210, 170, 240, 200, 160, 220, 180, 200],     # 5 B
    [260, 320, 280, 340, 300, 270, 330, 290, 310, 300],     # 6 A
    [300, 260, 340, 280, 320, 290, 310, 270, 330, 300],     # 7 A
    [240, 180, 220, 200, 160, 230, 190, 210, 170, 200])}    # 8 B
SCRIPT_4 = {"sitting": 4, "abort": None, "blocks": _blocks(
    [210, 170, 230, 190, 200, 240, 160, 220, 180, 200],     # 1 B
    [320, 280, 300, 260, 340, 290, 310, 330, 270, 300],     # 2 A
    [280, 340, 260, 320, 300, 310, 270, 330, 290, 300],     # 3 A
    [220, 160, 240, 200, 180, 210, 170, 230, 190, 200],     # 4 B
    [310, 270, 330, 290, 300, 260, 340, 280, 320, 300],     # 5 A
    [190, 230, 170, 210, 200, 160, 240, 180, 220, 200],     # 6 B
    [170, 210, 190, 230, 200, 240, 160, 220, 180, 200],     # 7 B
    [340, 300, 260, 320, 280, 330, 270, 310, 290, 300])}    # 8 A
SCRIPTS_DONE = (SCRIPT_1, SCRIPT_3, SCRIPT_4)


def expected_script(script):
    """The script with every delay replaced by the ms the guest should record:
    d for a hit at the first press, 2d for a cue missed first, plus OFFSET_MS."""
    out = {"sitting": script["sitting"], "abort": script.get("abort"), "blocks": []}
    for blk in script["blocks"]:
        ms = [d * (2 if c + 1 in blk.get("miss", ()) else 1) + OFFSET_MS for c, d in enumerate(blk["ms"])]
        out["blocks"].append({"ms": ms, "miss": list(blk.get("miss", ()))})
    return out


def compare_notes(actual, script, label):
    """The notes a script left against the notes on the record: every non-hit
    note byte for byte; every hit note's five fields exact and its ms inside
    the per-hit window; every block note's median inside SLACK_MS of the
    rule over the expected ms; the block notes agreeing with their own hits
    (A2)."""
    want = notes_of(expected_script(script))
    problems = []
    if len(actual) != len(want):
        problems.append("%s: %d notes, want %d" % (label, len(actual), len(want)))
    exp_ms = {}
    for i, (a, w) in enumerate(zip(actual, want)):
        pa, pw = parse_note(a), parse_note(w)
        if pa is None or pa["kind"] != pw["kind"]:
            problems.append("%s: note %d is %r, want the shape of %r" % (label, i + 1, a, w))
            break
        if pw["kind"] == "hit":
            key = (pa["sitting"], pa["block"], pa["layout"], pa["cue"])
            if key != (pw["sitting"], pw["block"], pw["layout"], pw["cue"]):
                problems.append("%s: note %d is %r, want %r" % (label, i + 1, a, w))
                break
            exp_ms.setdefault(pw["block"], []).append(pw["ms"])
            if abs(pa["ms"] - pw["ms"]) > HIT_WINDOW_MS:
                problems.append("%s: note %d %r - %d ms is outside %d +/- %d" % (label, i + 1, a, pa["ms"], pw["ms"], HIT_WINDOW_MS))
        elif pw["kind"] == "block":
            if (pa["sitting"], pa["block"], pa["layout"], pa["hits"], pa["misses"]) != \
                    (pw["sitting"], pw["block"], pw["layout"], pw["hits"], pw["misses"]):
                problems.append("%s: note %d is %r, want %r but for the median" % (label, i + 1, a, w))
                break
            want_med = median(exp_ms.get(pw["block"], [0] * CUES_PER_BLOCK))
            if abs(pa["median"] - want_med) > SLACK_MS:
                problems.append("%s: block %d's median is %d ms, the scripted delays give %d +/- %d (the spec's window)"
                                % (label, pa["block"], pa["median"], want_med, SLACK_MS))
        elif a != w:
            problems.append("%s: note %d is %r, want %r" % (label, i + 1, a, w))
            break
    problems += ["%s: %s" % (label, p) for p in check_blocks(actual)]
    return problems


def check_serial_notes(capture, notes, label):
    got, _ = trial_lines(capture)
    if got != notes:
        n = next((i for i, (a, b) in enumerate(zip(got, notes)) if a != b), min(len(got), len(notes)))
        return ["%s: the trial: lines on serial are not the notes: %d lines against %d notes, first difference at %d: %r vs %r"
                % (label, len(got), len(notes), n + 1, got[n] if n < len(got) else None, notes[n] if n < len(notes) else None)]
    return []


def check_rests(results, script, label):
    problems = []
    s = script["sitting"]
    for b in range(1, BLOCKS):
        o = results.get("rest_obs", {}).get(b)
        if o is None:
            problems.append("%s: no obs page read at the rest after block %d" % (label, b))
            continue
        problems += check_counts(o, {"mode": MODE_TRIAL, "trial_sitting": s, "trial_block": b, "trial_cue": 0,
                                     "trial_layout": "AB".index(layout(s, b)), "trial_hits": CUES_PER_BLOCK,
                                     "trial_misses": len(script["blocks"][b - 1].get("miss", ())), "hits": 0},
                                 "%s, the rest after block %d" % (label, b))
    return problems


def panel_cells(rows):
    return {(r, c): ch for r, row in enumerate(rows) for c, ch in enumerate(row)}


def check_table_panel(shot, geometry, notes, sitting, label):
    rows = dict(table_of(notes)).get(sitting)
    if rows is None:
        return ["%s: no table for sitting %d in the notes" % (label, sitting)]
    return check_panel_cells(shot, geometry, panel_cells(rows), label)


def boot_and_play(smp, disk, copy, serial, script, tag, extra_before=(), extra_after=(), **kw):
    results = {}
    steps = list(extra_before) + [("type", "! trial\n"), ("play", script, results, kw), ("sleep", 1.5), ("park",),
                                  ("surfaces", "end"), ("shot", os.path.join(TRIALS_OUT, "screen.sitting.%s.ppm" % tag)),
                                  ("obs", "end2"), ("serial", "end")] + list(extra_after)
    capture, reads, events, err = drive_7d(smp, disk, copy, steps, serial, ready_limit=READY_LIMIT_S, settle=SETTLE_S)
    return results, capture, reads, events, err


def run_sitting():
    if not require_constants():
        return 1
    smp = STAGES_SMP
    for port in (BROKER_PORT, RELAY_PORT):
        if port_state(port) == "open":
            say("something is listening on 127.0.0.1:%d - the trial needs nothing on the wire and asserts it" % port)
            return 1
    copy = fresh_stick(os.path.join(TRIALS_OUT, "stick.sitting.img"))
    fresh_disk(DISK)
    ok = True
    notes = []
    shots = {}

    # ------------------------------------------------ boot 1: sitting 1 --
    say("boot 1: a fresh disk, -smp %d, nothing on the wire; '! trial', sitting 1 (%s) to done - %d cues, three misses "
        "(blocks 2, 4, 7), the page at every rest" % (smp, order(1), BLOCKS * CUES_PER_BLOCK))
    results, capture, reads, events, err = boot_and_play(smp, DISK, copy, os.path.join(TRIALS_OUT, "serial.sitting.1.txt"),
                                                         SCRIPT_1, "1", read_at_rest=True)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    geometry = reads["geometry"]
    regs = regions(geometry[2], geometry[3])
    _, stripped = trial_lines(capture)
    problems, geometry_1 = check_boot_lines(stripped, smp, True, "formatted", 0, checkmetal.DISK_SECTORS)
    problems += check_echo(stripped, b"! trial\r\n")
    ok &= report("boot 1's serial log is not what the plan asks for", problems, capture)
    notes = notes_on_disk(DISK)
    problems = compare_notes(notes, SCRIPT_1, "sitting 1")
    problems += check_serial_notes(capture, notes, "sitting 1")
    problems += check_rests(results, SCRIPT_1, "sitting 1")
    end = reads.get("end2")
    if end is None:
        problems.append("the obs page could not be read after done")
    else:
        problems += check_counts(end, {"mode": 0, "trial_sitting": 1, "trial_block": 0, "trial_cue": 0, "layout_default": 0,
                                       "notes": len(notes), "hits": 0, "errors": 0, "wire_conns": 0,
                                       "clicks": reads["counts"]["end2"]["clicks"], "packets": reads["counts"]["end2"]["packets"]},
                                 "after done")
    shot = os.path.join(TRIALS_OUT, "screen.sitting.1.ppm")
    problems += check_table_panel(shot, geometry, notes, 1, "sitting 1's table")
    problems += check_mode_field(shot, geometry, "prompt")
    problems += check_choices(shot, geometry, "? ask   ! grow")
    problems += check_region_rows(shot, geometry, regs["conversation"], ["click: " + cue_sequence(BLOCKS)[-1], "sitting 1 done", PROMPT])
    if geometry_1 != geometry:
        problems.append("the geometry differs")
    ok &= report("sitting 1 is not what TRIALS.md predicts for the script", problems)
    if not problems:
        say("sitting 1: %d notes on the notebook exactly as the script expands - the three misses where scripted, every block's "
            "median within %d ms of the scripted delays' median plus %d, the block notes agreeing with their hits; the same lines "
            "on serial; the page at the seven rests; after done mode 0, layout_default 0, the table in the app panel, layout A's row"
            % (len(notes), SLACK_MS, OFFSET_MS))
    disk_after_1 = read_image(DISK)

    # ------------------------------------------------ boot 2: the abort --
    say("boot 2: the same disk; sitting 2 (%s), blocks 1-2, three cues of block 3, Esc" % order(2))
    n_before = len(notes)
    results, capture, reads, events, err = boot_and_play(smp, DISK, copy, os.path.join(TRIALS_OUT, "serial.sitting.2.txt"),
                                                         SCRIPT_ABORT, "2", abort=(3, 3))
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    _, stripped = trial_lines(capture)
    problems, _ = check_boot_lines(stripped, smp, False, "%d notes" % n_before, 0, checkmetal.DISK_SECTORS)
    problems += check_echo(stripped, b"! trial\r\n")
    ok &= report("boot 2's serial log is not what the plan asks for", problems, capture)
    notes_before, notes = notes, notes_on_disk(DISK)
    problems = []
    if notes[:n_before] != notes_before:
        problems.append("the earlier notes changed on the journal")
    new = notes[n_before:]
    problems += compare_notes(new, SCRIPT_ABORT, "sitting 2")
    problems += check_serial_notes(capture, new, "sitting 2")
    if results.get("aborted") != 3 or results.get("order") != order(2):
        problems.append("the abort line says block %r and the order %r" % (results.get("aborted"), results.get("order")))
    end = reads.get("end2")
    if end is not None:
        problems += check_counts(end, {"mode": 0, "trial_sitting": 2, "notes": len(notes), "layout_default": 0, "hits": 0}, "after the abort")
    shot = os.path.join(TRIALS_OUT, "screen.sitting.2.ppm")
    problems += check_table_panel(shot, geometry, notes, 2, "sitting 2's table")
    problems += check_region_rows(shot, geometry, regs["conversation"], ["click: " + cue_sequence(3)[2], "sitting 2 aborted 3", PROMPT])
    problems += check_mode_field(shot, geometry, "prompt")
    if read_image(DISK)[:len(disk_after_1)] == disk_after_1:
        problems.append("the disk did not change during sitting 2")
    ok &= report("the abort is not what TRIALS.md says", problems)
    if not problems:
        say("sitting 2: 'S7: notebook %d notes' at boot, the order %s, blocks 1-2 stand, block 3's three hits on the journal with no "
            "block note, 'trial sitting 2 aborted 3', its table with 'aborted 3', the prompt back" % (n_before, order(2)))

    # ------------------------------------- boots 3 and 4: to the verdict --
    for script, tag in ((SCRIPT_3, "3"), (SCRIPT_4, "4")):
        s = script["sitting"]
        n_before = len(notes)
        say("boot %s: the same disk; sitting %d (%s) to done%s" % (tag, s, order(s), " - the third done sitting: the verdict" if s == 4 else ""))
        results, capture, reads, events, err = boot_and_play(smp, DISK, copy, os.path.join(TRIALS_OUT, "serial.sitting.%s.txt" % tag),
                                                             script, tag)
        if err:
            say(err)
            if capture:
                dump_capture(capture)
            return 1
        _, stripped = trial_lines(capture)
        problems, _ = check_boot_lines(stripped, smp, False, "%d notes" % n_before, 0, checkmetal.DISK_SECTORS)
        problems += check_echo(stripped, b"! trial\r\n")
        ok &= report("boot %s's serial log is not what the plan asks for" % tag, problems, capture)
        notes = notes_on_disk(DISK)
        new = notes[n_before:]
        verdict_note = []
        if s == 4:
            if new and new[-1].startswith("trial verdict "):
                verdict_note = [new[-1]]
                new = new[:-1]
            else:
                problems = ["no verdict note after the third done sitting: the record ends %r" % (new[-1:],)]
        problems = compare_notes(new, script, "sitting %d" % s)
        problems += check_serial_notes(capture, new + verdict_note, "sitting %d" % s)
        end = reads.get("end2")
        shot = os.path.join(TRIALS_OUT, "screen.sitting.%s.ppm" % tag)
        problems += check_table_panel(shot, geometry, notes, s, "sitting %d's table" % s)
        problems += check_mode_field(shot, geometry, "prompt")
        if s == 3:
            if verdict_of(notes) is not None:
                problems.append("a verdict after two done sittings")
            if end is not None:
                problems += check_counts(end, {"mode": 0, "trial_sitting": 3, "notes": len(notes), "layout_default": 0}, "after sitting 3")
            problems += check_choices(shot, geometry, "? ask   ! grow")
            problems += check_region_rows(shot, geometry, regs["conversation"], ["click: " + cue_sequence(BLOCKS)[-1], "sitting 3 done", PROMPT])
        else:
            want_v = verdict_of(notes)
            d = verdict_detail(notes)
            if want_v != "B" or verdict_note != ["trial verdict B"] or d is None or d[0] != [1, 3, 4]:
                problems.append("the verdict: the rule gives %r over %r, the record says %r" % (want_v, d, verdict_note))
            if end is not None:
                problems += check_counts(end, {"mode": 0, "trial_sitting": 4, "notes": len(notes), "layout_default": 1}, "after the verdict")
            problems += check_layout_b(shot, reads.get("end", {}), geometry, ["? ask", "! grow"], "the row after the verdict")
            problems += check_region_rows(shot, geometry, regs["conversation"],
                                          ["click: " + cue_sequence(BLOCKS)[-1], "sitting 4 done", "verdict B", PROMPT])
        ok &= report("sitting %d is not what TRIALS.md predicts" % s, problems)
        if not problems and s == 3:
            say("sitting 3: %d notes as the script expands, no verdict yet, layout A" % len(new))
        elif not problems:
            say("sitting 4: the third done sitting; 'trial verdict B' on the notebook by %d wins of 12 with misses A %d B %d over sittings "
                "%s; 'verdict B' in the panel and the conversation; layout_default 1; the row two boxes at the prompt" % (d[1], d[2], d[3], d[0]))
    disk_after_4 = read_image(DISK)

    # ----------------------------------------- boot 5: the default, no trial --
    say("boot 5: the same disk, no trial: layout B at the prompt, 'trial verdict A' typed and refused, a click on the '! grow' box")
    n_before = len(notes)
    grow_box = boxes(geometry[2], 2)[1]
    crow = regs["choices"][0]
    steps = [
        ("sleep", 0.5), ("surfaces", "boot"), ("shot", os.path.join(TRIALS_OUT, "screen.sitting.5a.ppm")),
        ("type", "trial verdict A\n"), ("sleep", 1.5),
        ("shot", os.path.join(TRIALS_OUT, "screen.sitting.5b.ppm")), ("obs", "reserved"),
        ("mouse", 1, 0), ("sleep", 0.5),
        ("moveto", crow + 1, (grow_box[2] + grow_box[3]) // 2),
        ("button", 1, "hit"), ("button", 0), ("sleep", 1.5),
        ("park",), ("shot", os.path.join(TRIALS_OUT, "screen.sitting.5c.ppm")), ("obs", "click"), ("serial", "end"),
    ]
    capture, reads, events, err = drive_7d(smp, DISK, copy, steps, os.path.join(TRIALS_OUT, "serial.sitting.5.txt"),
                                           ready_limit=READY_LIMIT_S, settle=SETTLE_S)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    problems, stripped = strip_mouse_line(capture)
    more, _ = check_boot_lines(stripped, smp, False, "%d notes" % n_before, 0, checkmetal.DISK_SECTORS)
    problems += more
    problems += check_echo(stripped, b"trial verdict A\r\n!")
    ok &= report("boot 5's serial log is not what the plan asks for", problems, capture)
    problems = []
    boot = reads.get("boot", {})
    problems += check_counts(boot.get("obs", {}), {"mode": 0, "layout_default": 1, "trial_sitting": 0, "notes": n_before}, "at boot") \
        if boot.get("obs") else ["the page was not read at boot"]
    problems += check_layout_b(os.path.join(TRIALS_OUT, "screen.sitting.5a.ppm"), boot, geometry, ["? ask", "! grow"], "the row at boot")
    problems += check_region_rows(os.path.join(TRIALS_OUT, "screen.sitting.5b.ppm"), geometry, regs["conversation"],
                                  ["trial verdict A", "trial is reserved", PROMPT])
    if "reserved" in reads:
        problems += check_counts(reads["reserved"], {"errors": 1, "notes": n_before, "layout_default": 1, "mode": 0}, "the reserved prefix")
    else:
        problems.append("the page was not read after the reserved line")
    if notes_on_disk(DISK) != notes:
        problems.append("the notebook changed on the no-trial boot - the reserved prefix was journaled, or something else was")
    problems += check_layout_b(os.path.join(TRIALS_OUT, "screen.sitting.5b.ppm"), boot, geometry, ["? ask", "! grow"], "the row after the refusal")
    if "click" in reads:
        c = reads["counts"]["click"]
        problems += check_counts(reads["click"], {"hits": 1, "clicks": 1, "packets": c["packets"], "mode": 0, "layout_default": 1,
                                                  "notes": n_before}, "the click")
        row, col = reads["model"]["click"]
        problems += check_arrow_at(os.path.join(TRIALS_OUT, "screen.sitting.5c.ppm"), geometry, row, col, "screen 5c")
    else:
        problems.append("the page was not read after the click")
    if read_image(DISK) != disk_after_4:
        problems.append("the disk changed during the no-trial boot")
    problems += check_stick_tables_unchanged(copy, "the sitting boots")
    r = subprocess.run([sys.executable, os.path.join(HERE, "trials.py"), "--disk", DISK], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True)
    if r.returncode != 0 or "verdict B:" not in r.stdout:
        problems.append("trials.py --disk on the image: exit %d, %r" % (r.returncode, r.stdout.strip().splitlines()[-1:]))
    else:
        for sitting, rows in table_of(notes):
            if "\n".join(rows) not in r.stdout:
                problems.append("trials.py --disk does not print sitting %d's table as the panel showed it" % sitting)
    ok &= report("the default read at boot, the reserved prefix or the click on a box is not what TRIALS.md says", problems)
    if not problems:
        say("boot 5: 'S7: notebook %d notes', layout_default 1 and the two boxes at the prompt before any packet; 'trial verdict A' "
            "refused with 'trial is reserved', errors 1, the notebook unchanged, the row still layout B; the click on the '! grow' box "
            "typed '!' (hits 1); the disk and the stick copy untouched; trials.py --disk prints the four tables and 'verdict B'" % n_before)
    say("the sittings: %s" % ("three sittings to a verdict as TRIALS.md predicts, and the DE's default follows it" if ok else "not what TRIALS.md predicts"))
    return 0 if ok else 1


# ---------------------------------------------------- test 4: the cage ------
# (a) is test-7d.sh's own strings and (d) its run of the three earlier
# gates. Here: (b) the argv check - this checker's command IS
# checkmetal.qemu_argv, passed through the frozen check_argv_7c; the ports
# the frozen modules hold; (c) the payload table as a subprocess, 0 wrong,
# and the spot checks held as data: the four frozen paths of this ring
# denied every mutation, running them allowed.

FROZEN_7D = ["stage7/TRIALS.md", "stage7/test-7d.sh", "stage7/checktrials.py", "stage7/trials.py"]
SPOT_DENY_7D = [c for p in FROZEN_7D for c in (
    "echo x > %s" % p, "sed -i 's/a/b/' %s" % p, "cp /tmp/x %s" % p, "rm -f %s" % p,
    "python3 - <<'EOF'\nopen('%s','w').write('x')\nEOF" % p)]
SPOT_ALLOW_7D = [
    "./stage7/test-7d.sh", "./stage7/test-7d.sh 2>&1 | tail -20",
    "python3 stage7/checktrials.py --document", "python3 stage7/checktrials.py --row",
    "python3 stage7/checktrials.py --sitting", "python3 stage7/checktrials.py --cage",
    "python3 stage7/trials.py --example", "python3 stage7/trials.py --disk stage7/out/trials/disk.img",
    "python3 stage7/trials.py --serial stage7/out/metal.log",
    "cat stage7/TRIALS.md | head", "grep -n 'trial' stage7/checktrials.py",
    "tail -5 stage7/out/gate-7d.log", "echo x >> stage7/out/gate-7d.log",
    "rm -rf stage7/out/trials stage7/out/probe7d",
    "git commit -F msg.txt",
]


def check_bodyguard_7d():
    problems = []
    r = subprocess.run([sys.executable, checkmetal.PAYLOADS], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    m = re.fullmatch(r"(\d+) payloads: (\d+) must be denied, (\d+) must be allowed, (\d+) wrong", last)
    if r.returncode != 0 or not m or m.group(4) != "0":
        problems.append("the payload table: exit %d, last line %r - want exit 0 and 0 wrong" % (r.returncode, last))
        for line in r.stdout.splitlines():
            if line.startswith("  WRONG"):
                problems.append("  " + line.strip())
    else:
        say("the payload table: %s" % last)
    for p in FROZEN_7D:
        for tool, ti in (("Write", {"file_path": p, "content": "x"}), ("Edit", {"file_path": p, "old_string": "a", "new_string": "b"})):
            payload = {"tool_name": tool, "tool_input": ti}
            rr = subprocess.run([sys.executable, checkmetal.HOOK], input=__import__("json").dumps(payload).encode(),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO))
            if rr.returncode != 2:
                problems.append("the hook allows %s on %s - the four files of this ring must be frozen" % (tool, p))
    for c in SPOT_DENY_7D:
        v = checkmetal.hook_verdict(c)
        if v != "DENY":
            problems.append("the hook %ss %r - every mutation of this ring's frozen files must be denied" % (v.lower(), c))
    for c in SPOT_ALLOW_7D:
        v = checkmetal.hook_verdict(c)
        if v != "ALLOW":
            problems.append("the hook %ss %r - running the gate, the checker and the tool must be allowed" % (v.lower(), c))
    return problems


def run_cage():
    argv = qemu_argv(4, DISK, os.path.join(TRIALS_OUT, "stick.x.img"), os.path.join(TRIALS_OUT, "x"))
    problems = checkmetal.check_argv_7c(argv, RELAY_PORT, checkmetal.MAC)
    import wire
    if twin.DEFAULT_PORT != checkmetal.REHEARSAL_PORT or wire.RELAY_PORT != RELAY_PORT or twin.VGA_ARGS != checkmetal.DISPLAY:
        problems.append("the frozen modules' ports or display are not ring 7c's")
    if not report("the checker's QEMU command is not the twin of the HP", problems):
        return 1
    say("the checker's QEMU command is checkmetal.qemu_argv itself: one restricted cage to the relay on %d, the e1000e with %s, "
        "-cpu IvyBridge, the display, the stick copy over xhci, the SATA disk on ide.1, two drives under stage7/out/, no esp.img"
        % (RELAY_PORT, checkmetal.MAC))
    problems = check_bodyguard_7d()
    ok = report("the bodyguard does not freeze this ring's four files", problems)
    if ok:
        say("the bodyguard: the four frozen files of this ring denied every mutation (%d spellings), the gate, the checker and the tool "
            "allowed (%d shapes)" % (len(SPOT_DENY_7D) + 2 * len(FROZEN_7D), len(SPOT_ALLOW_7D)))
    say("the cage: %s" % ("held, and the criteria frozen" if ok else "not proven"))
    return 0 if ok else 1


# --------------------------------------------------------------- main ------

def main(argv):
    os.makedirs(TRIALS_OUT, exist_ok=True)
    if argv == ["--document"]:
        return run_document()
    if argv == ["--row"]:
        return run_row()
    if argv == ["--sitting"]:
        return run_sitting()
    if argv == ["--cage"]:
        return run_cage()
    say("usage: checktrials.py --document | --row | --sitting | --cage")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
