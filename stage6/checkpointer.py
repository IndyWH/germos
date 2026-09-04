#!/usr/bin/env python3
"""Stage 6 ring 6c acceptance tests 2, 3 and 4 - the pointer.

One driver, ring 6b's shape (stage6/checkplans.py and stage6/checkglass.py,
both frozen and importable, lend their picture, record, germline, notebook,
home-image and mock-lifecycle helpers): boot stage6/out/esp.img headless
under OVMF with the standard VGA device stating 1920x1080 through its EDID,
a fresh 16 MB notebook image and a fresh 16 MB home image as two virtio
disks, the caged network of stage4/UMBILICAL.md, the monitor on stdio,
serial to a file; wait for the guest's own "S6: keyboard ready"; type from
OUTSIDE via sendkey; MOVE AND CLICK from outside via the monitor's
mouse_move and mouse_button - QEMU's PS/2 mouse on the i8042, the path
Stage 7's metal will have; read the obs page (0x2C0 bytes now) and the
surfaces through xp; screendump; quit. Then judge by GLASS.md's ring 6c
section: the serial capture, the obs page's pointer fields, the arrow on
the screen at the page's cell, the strip's third field rendered from the
page, the click's effect in the conversation, on the choices row and in the
app panel, the broker's record, the germline, the home image and the
notebook.

No count in this file is a hand-written literal (plan amendment A2): the
step list is data, and expected_counts() derives packets, clicks, mouse
bytes and keys from it; hits come from a per-step flag set beside the press
it describes. Every move the driver emits fits one packet (|dx|, |dy| <=
127 - measured before the plan), so packets sent is the number of mouse
and button commands, never a splitting model.

The broker is broker/pointer.py --mock, whose pipeline REHEARSES every
candidate in a real headless boot of a copy of the same image at 1920x1080
with a home drive (broker/twin.py through broker/plans.py). The mock
generates from the canned tables and calls nothing outside the repository;
the gate never spends a token. The twin never moves the mouse.

Three modes:
  --serial <smp>   Test 2 (item 5): seventeen lines and the 6a strip and
                   surfaces to the pixel before any packet, the mouse
                   identified in the obs page; one mouse_move; eighteen
                   lines with "S6: mouse ready" eighteenth, the arrow at
                   the page's cell, the strip's third field.
  --point <smp>    Test 3 (item 6): the pointer, driven by the monitor -
                   a click on "? ask" types the marker; "! point app"
                   rehearsed and run; three buttons in its panel reach
                   point; the row's items clicked; the frozen test app
                   clicked on harmlessly; the wire untouched.
  --truth          Test 4 (item 7): the truth about the pointer - the
                   pre-packet screen judged by the frozen 6a checks, a
                   scripted sweep, packets counted equal packets sent, the
                   buttons on an empty spot, the launch by click with and
                   without text on the line, the strip against the page.

Pure standard library. Everything runs inside QEMU with exactly three
drives per guest, raw files under stage6/out/, created here or by the twin;
the broker (mock) on 127.0.0.1 only. No real disk is touched; no Claude
call is ever made.

This file is frozen acceptance machinery from plan item 8. See the header
of stage6/test-6c.sh.

Exit 0 on pass, 1 otherwise.
"""

import hashlib
import json
import os
import re
import select
import shutil
import struct
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "stage6", "out")
ESP = os.path.join(OUT, "esp.img")
NOTES = os.path.join(OUT, "notes.img")
HOME_IMG = os.path.join(OUT, "home.img")
BROKER = os.path.join(REPO, "broker", "pointer.py")
PLANS_DIR = os.path.join(REPO, "plans")
GERMLINE = os.path.join(OUT, "germline")
REHEARSAL = os.path.join(OUT, "rehearsal")
TWIN_WORKDIR = os.path.join(REHEARSAL, "twin")
OVMF = "/usr/share/ovmf/OVMF.fd"

sys.path.insert(0, os.path.join(REPO, "broker"))
sys.path.insert(0, os.path.join(REPO, "stage6"))
from glass import (app_frame, refusal_frame, regions, choices_row, strip_rows, fmt_ms, fmt_n,  # noqa: E402
                   germline_key, TEST_CHOICES, MACHINE, ABI)
import twin  # noqa: E402
from twin import Driver, keyname  # noqa: E402
import plans  # noqa: E402
from plans import plan_keyname, twin_extra_args, TWIN_HOME  # noqa: E402
import pointer  # noqa: E402
from pointer import (parse_obs_6c, point_offset, strip_rows_6c, render_arrow, choice_targets, click_action,  # noqa: E402
                     OBS_PAGE_BYTES_6C, POINT_MAGIC, POINTER_FIELD_COL, POINTER_BUDGET_MS, MOUSE_LINE,
                     POINT_NAME, POINT_CHOICES, BUTTON_OF_MASK)
from checkglass import (check_echo, dump_capture, read_record, record_count, check_image, port_state,  # noqa: E402
                        stop_mock, report, say, check_region_rows, PROMPT, open_shot, blank_cell, cursor_cell,
                        cell_census, check_colour_discipline, check_choices, check_mode_field, check_app_panel,
                        check_app_panel_blank, check_strip, check_surfaces, check_counts, germline_entries,
                        fixture_self_check, check_cage_argv, check_grow_entry, check_question_entry,
                        read_cells, STRIP0, KEY_GAP, SETTLE, CANNED)
from checkplans import (BOOT_PATTERNS, check_home, check_one_cell_panel, check_install_entry,  # noqa: E402
                        check_install_germline, check_argv, CHOICES_PROMPT_ECHO, ECHO_TESTS_OK, DATA_FIRST,
                        SECTOR)
from rehearse import (read_ppm, load_font, render_cell, cell_matches, BG, FG, CELL)  # noqa: E402

DISK_BYTES = 16 * 1024 * 1024

# The cage (UMBILICAL.md), with this ring's MAC.
BROKER_PORT = 9999
REHEARSAL_PORT = 9998
MAC = "52:54:00:a1:06:03"
CAGE_NETDEV = ("user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:%d-cmd:nc -N 127.0.0.1 %d"
               % (BROKER_PORT, BROKER_PORT))
CAGE_DEVICE = "virtio-net-pci,netdev=n0,mac=" + MAC

# The display, spelled once here and asserted against the broker module's.
DISPLAY = ["-vga", "none", "-device", "VGA,edid=on,xres=1920,yres=1080"]

READY = b"S6: keyboard ready"
LINES = 17                       # ring 6b's lines: what a two-disk boot prints before any packet
LINES_MOUSE = 18                 # and after the first packet
PACKET_MAX = 127                 # the most one packet carries per axis (measured)
FRAME_SETTLE = 0.06              # seconds after a move before a screendump: well over two frame slots


# ------------------------------------------------------------- the model ----
# The checker's own account of where the pointer is, and what the guest
# must have counted. The position starts at the screen's centre (GLASS.md,
# "The device") and every emitted move fits one packet.

class Pointer:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.x, self.y = width // 2, height // 2

    def move(self, dx, dy):
        """Apply one mouse_move as the guest will: dx right, dy down the
        screen (the monitor's convention; the packet carries -dy)."""
        assert abs(dx) <= PACKET_MAX and abs(dy) <= PACKET_MAX
        self.x = max(0, min(self.w - 1, self.x + dx))
        self.y = max(0, min(self.h - 1, self.y + dy))

    def cell(self):
        return self.y // CELL, self.x // CELL

    def moves_to(self, row, col):
        """The mouse_move commands, each within one packet, that take the
        pointer from where it is to the centre of a cell."""
        tx, ty = col * CELL + CELL // 2, row * CELL + CELL // 2
        out = []
        x, y = self.x, self.y
        while (x, y) != (tx, ty):
            dx = max(-PACKET_MAX, min(PACKET_MAX, tx - x))
            dy = max(-PACKET_MAX, min(PACKET_MAX, ty - y))
            out.append(("mouse", dx, dy))
            x += dx
            y += dy
        return out


def expected_counts(events):
    """What the guest must have counted after these emitted events (plan
    amendment A2): ("mouse", dx, dy) and ("button", mask[, "hit"]) are one
    packet each; a button event with a non-zero mask is one click, and one
    hit when it carries the flag; ("type", text) is len(text) keys."""
    c = {"packets": 0, "clicks": 0, "hits": 0, "keys": 0}
    for ev in events:
        if ev[0] in ("mouse", "button"):
            c["packets"] += 1
        if ev[0] == "button" and ev[1]:
            c["clicks"] += 1
            if len(ev) > 2 and ev[2] == "hit":
                c["hits"] += 1
        if ev[0] == "type":
            c["keys"] += len(ev[1])
    c["mouse_bytes"] = 3 * c["packets"]
    return c


# ------------------------------------------------------------- the driver ---

def fresh_disk(path):
    if os.path.exists(path):
        os.remove(path)
    with open(path, "wb") as fh:
        fh.truncate(DISK_BYTES)


def qemu_argv(smp, disk, home, serial_path):
    """The one place the QEMU command is spelled. Test 4 inspects this."""
    return [
        "qemu-system-x86_64",
        "-machine", "q35",
        "-m", "256M",
        "-smp", str(smp),
        "-bios", OVMF,
    ] + list(DISPLAY) + [
        "-drive", "format=raw,file=" + ESP,
        "-drive", "format=raw,file=" + disk + ",if=virtio",
        "-drive", "format=raw,file=" + home + ",if=virtio",
        "-netdev", CAGE_NETDEV,
        "-device", CAGE_DEVICE,
        "-display", "none",
        "-serial", "file:" + serial_path,
        "-monitor", "stdio",
    ]


def geometry_of(capture):
    m = re.search(rb"S6: gop (\d+)x(\d+) fb 0x", capture)
    return (int(m.group(1)), int(m.group(2))) if m else None


def drive(smp, disk, home, steps, serial_path, ready=READY, ready_limit=60.0):
    """Boot inside the cage with both disks, wait for the guest's own ready
    line, run the steps, quit, reap. Steps: ("type", text), ("sleep", s),
    ("wait_record", path, count, timeout), ("shot", path), ("obs", label)
    - the 0x2C0-byte page parsed by the 6c section -, ("surfaces", label)
    - the four surfaces plus the page -, ("serial", label) - the capture so
    far -, ("mouse", dx, dy) - one mouse_move within one packet -,
    ("button", mask[, "hit"]) - one mouse_button -, ("moveto", row, col) -
    the model's moves to a cell's centre, each within one packet. Returns
    (serial_bytes, reads, events, error): events is every emitted event in
    order, the moveto steps expanded; reads[label] for an obs, surfaces or
    serial label, plus reads["counts"][label] = expected_counts(events up
    to that read) and reads["model"][label] = the model's (row, col) then.
    Never leaves a QEMU running behind us."""
    reads = {"counts": {}, "model": {}}
    events = []
    if not os.path.isfile(ESP):
        return b"", reads, events, "no image was built"
    if not os.path.isfile(OVMF):
        return b"", reads, events, "OVMF firmware not found at " + OVMF
    if os.path.exists(serial_path):
        os.remove(serial_path)
    for step in steps:
        if step[0] == "shot" and os.path.exists(step[1]):
            os.remove(step[1])

    proc = subprocess.Popen(qemu_argv(smp, disk, home, serial_path),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    drv = Driver(proc, serial_path, OUT)

    err = None
    obs_addr = None
    model = None
    try:
        deadline = time.time() + ready_limit
        got_ready = False
        while time.time() < deadline:
            time.sleep(0.25)
            if proc.poll() is not None:
                break
            if ready in drv.serial_bytes():
                got_ready = True
                break
        if not got_ready:
            err = "the guest never printed %r within %.0fs" % (ready.decode(), ready_limit)
            if proc.poll() is not None:
                err += " (qemu exited %d: %s)" % (proc.returncode,
                                                 proc.stderr.read().decode(errors="replace").strip()[:300])
        else:
            time.sleep(1.0)
            geo = geometry_of(drv.serial_bytes())
            if geo:
                model = Pointer(*geo)

            def note(label):
                reads["counts"][label] = expected_counts(events)
                reads["model"][label] = model.cell() if model else None

            def mouse(dx, dy):
                drv.tell(b"mouse_move %d %d\n" % (dx, dy))
                if model:
                    model.move(dx, dy)
                events.append(("mouse", dx, dy))
                time.sleep(0.02)

            for step in steps:
                if step[0] == "type":
                    for ch in step[1]:
                        if ch in "\n\t\x1b":
                            name = keyname(ch)
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
                elif step[0] == "button":
                    drv.tell(b"mouse_button %d\n" % step[1])
                    events.append(tuple(step))
                    time.sleep(0.05)
                elif step[0] == "serial":
                    reads[step[1]] = drv.serial_bytes()
                    note(step[1])
                elif step[0] in ("obs", "surfaces"):
                    if obs_addr is None:
                        text = drv.serial_bytes().decode("utf-8", "replace")
                        m = re.search(r"S6: obs page 0x([0-9a-f]{16})", text)
                        obs_addr = int(m.group(1), 16) if m else 0
                    try:
                        if not obs_addr:
                            raise ValueError("no obs page line on serial")
                        page = parse_obs_6c(drv.xp(obs_addr, OBS_PAGE_BYTES_6C // 8, "g"))
                        if step[0] == "obs":
                            reads[step[1]] = page
                        else:
                            reads[step[1]] = {name: drv.read_surface(page[name])
                                              for name in ("strip", "choices", "conversation", "app")}
                            reads[step[1]]["obs"] = page
                        note(step[1])
                    except ValueError as exc:
                        say("(xp for %r failed: %s)" % (step[1], exc))
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


# ------------------------------------------------------- the serial claims --

def check_boot_lines(capture, smp, notebook_want, home_want):
    """Ring 6b's seventeen lines, in order, self-consistent, with THIS ring's
    MAC. Returns (problems, geometry) with geometry = (w, h, cols, rows).
    The capture must hold no mouse line (see strip_mouse_line)."""
    problems = []
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S6: [^\n]*", text)
    if len(got) != LINES:
        problems.append("expected exactly %d S6: lines, found %d" % (LINES, len(got)))
    errs = re.findall(r"ERR: [^\n]*", text)
    if errs:
        problems.append("the guest reported: %s" % "; ".join(errs[:3]))
    w = h = cols = rows = None
    ew = eh = None
    found = woken = None
    for i, (pattern, shape) in enumerate(BOOT_PATTERNS):
        line = got[i] if i < len(got) else ""
        m = re.fullmatch(pattern, line)
        if not m:
            problems.append("line %d: got '%s', want '%s'" % (i + 1, line, shape))
            continue
        if i == 1:
            ew, eh = int(m.group(1)), int(m.group(2))
        elif i == 2:
            w, h = int(m.group(1)), int(m.group(2))
            if (w, h) != (ew, eh):
                problems.append("line 3: the mode is %dx%d but the EDID prefers %dx%d" % (w, h, ew, eh))
        elif i == 6:
            found = int(m.group(1))
        elif i == 7:
            woken = int(m.group(1))
        elif i == 8:
            cols, rows = int(m.group(1)), int(m.group(2))
        elif i == 9 and int(m.group(1)) != DISK_BYTES // SECTOR:
            problems.append("line 10: the guest counted %s sectors, but the image is %d sectors" % (m.group(1), DISK_BYTES // SECTOR))
        elif i == 10 and m.group(1) != notebook_want:
            problems.append("line 11: got 'S6: notebook %s', want 'S6: notebook %s'" % (m.group(1), notebook_want))
        elif i == 11 and int(m.group(1)) != home_want:
            problems.append("line 12: got 'S6: home %s apps', want 'S6: home %d apps'" % (m.group(1), home_want))
        elif i == 12 and m.group(1) != MAC:
            problems.append("line 13: the guest read MAC %s, but the harness gave the device %s" % (m.group(1), MAC))
        elif i == 13:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32 or addr % 4096 != 128 or int(m.group(2)) != 1048576:
                problems.append("line 14: the component region line %r is not what GLASS.md asks" % line)
        elif i == 14:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32 or addr % 4096:
                problems.append("line 15: the obs page 0x%s is zero, above 4 GB or not page-aligned" % m.group(1))
    if found is not None and found != smp:
        problems.append("cores found is %d, but the machine was given -smp %d" % (found, smp))
    if woken is not None and woken != smp:
        problems.append("cores woken is %d, but the machine was given -smp %d" % (woken, smp))
    if None not in (w, h, cols, rows) and (cols != w // 16 or rows != h // 16):
        problems.append("console claims %dx%d cells, but %dx%d pixels / 16 = %dx%d" % (cols, rows, w, h, w // 16, h // 16))
    return problems, (w, h, cols, rows)


MOUSE_LINE_BYTES = MOUSE_LINE.encode() + b"\r\n"


def strip_mouse_line(capture):
    """The eighteenth line, once, after the ready line - and the capture
    without it, so the seventeen-line and echo checks judge the rest as
    ring 6b's. Returns (problems, stripped)."""
    problems = []
    n = capture.count(MOUSE_LINE_BYTES)
    if n != 1:
        problems.append("'%s' appears %d time(s) on serial, want exactly once after the first packet" % (MOUSE_LINE, n))
        return problems, capture.replace(MOUSE_LINE_BYTES, b"")
    ready_at = capture.find(READY + b"\r\n")
    mouse_at = capture.find(MOUSE_LINE_BYTES)
    if ready_at < 0 or mouse_at < ready_at:
        problems.append("'%s' came before '%s' - it is not a boot line" % (MOUSE_LINE, READY.decode()))
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S6: [^\n]*", text)
    if len(got) != LINES_MOUSE or got[-1] != MOUSE_LINE:
        problems.append("expected %d S6: lines with '%s' last, found %d ending %r" % (LINES_MOUSE, MOUSE_LINE, len(got), got[-1:] ))
    return problems, capture.replace(MOUSE_LINE_BYTES, b"", 1)


def check_no_mouse_line(capture):
    return ["'%s' appeared on serial before any packet" % MOUSE_LINE] if MOUSE_LINE_BYTES in capture else []


# ---------------------------------------------------------------- the mock --

def start_mock(record_path, wipe_germline=True):
    """Start pointer.py --mock with the gate's germline (wiped unless told
    otherwise), the gate's image as the twin's, the twin's own workdir,
    its record file; wait for its listening line."""
    for port in (BROKER_PORT, REHEARSAL_PORT):
        if port_state(port) == "open":
            return None, ("something is already listening on 127.0.0.1:%d - the gate talks only "
                          "to its own mock and its own twin; stop it first" % port)
    if wipe_germline and os.path.isdir(GERMLINE):
        shutil.rmtree(GERMLINE)
    if os.path.isdir(REHEARSAL):
        shutil.rmtree(REHEARSAL)
    if os.path.exists(record_path):
        os.remove(record_path)
    log = open(os.path.join(OUT, "mock.pointer.stderr.txt"), "ab")
    proc = subprocess.Popen(
        [sys.executable, BROKER, "--mock", "--port", str(BROKER_PORT), "--record", record_path,
         "--germline", GERMLINE, "--image", ESP, "--workdir", TWIN_WORKDIR,
         "--rehearsal-port", str(REHEARSAL_PORT), "--plans", PLANS_DIR],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=log)
    deadline = time.time() + 10.0
    line = b""
    while time.time() < deadline:
        if proc.poll() is not None:
            return proc, "the mock broker exited %d before listening" % proc.returncode
        r, _, _ = select.select([proc.stdout], [], [], 0.2)
        if r:
            line = proc.stdout.readline()
            break
    if line.strip() != ("listening on 127.0.0.1:%d" % BROKER_PORT).encode():
        stop_mock(proc)
        return None, "the mock broker did not say it was listening (got %r)" % line
    return proc, None


# ------------------------------------------------------------ the picture ---

def arrow_rows():
    return render_arrow()


def check_arrow_at(shot, geometry, row, col, label):
    """The arrow is at exactly this cell of the screen."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    if not cell_matches(pixels, width, row, col, arrow_rows()):
        return ["%s: cell (%d, %d) is not the arrow - %s" % (label, row, col, cell_census(pixels, width, row, col))]
    return []


def check_no_arrow(shot, geometry, label):
    """No cell anywhere on the screen renders as the arrow."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    want = arrow_rows()
    for r in range(rows):
        for c in range(cols):
            if cell_matches(pixels, width, r, c, want):
                return ["%s: an arrow is drawn at (%d, %d) before any packet" % (label, r, c)]
    return []


def surface_mismatch_except(shot, desc, cells, font, skip):
    """twin.surface_mismatch with one screen cell excused (the cursor's),
    which must be the arrow instead. Returns the first bad (row, col) or None."""
    width, height, pixels = read_ppm(shot)
    rows, cols = desc["rows"], desc["cols"]
    cur = desc["cursor"]
    cur_on = bool(cur >> 31 & 1)
    cur_row, cur_col = (cur >> 16) & 0x7FFF, cur & 0xFFFF
    for r in range(rows):
        for c in range(cols):
            sr, sc = desc["row0"] + r, desc["col0"] + c
            if (sr + 1) * CELL > height or (sc + 1) * CELL > width:
                return (r, c)
            if (sr, sc) == skip:
                want = arrow_rows()
            else:
                want = twin.cell_pixels(font, cells[r * cols + c], cur_on and (r, c) == (cur_row, cur_col))
            if not cell_matches(pixels, width, sr, sc, want):
                return (r, c)
    return None


def check_surfaces_except(shot, reads, cell, label, which=("choices", "conversation", "app")):
    """Every named region of the screen is what its surface says, bar the
    cursor's cell, which is the arrow."""
    problems = []
    try:
        font = load_font()
        obs = reads["obs"]
        for name in which:
            at = surface_mismatch_except(shot, obs[name], reads[name], font, cell)
            if at is not None:
                problems.append("%s: the %s region's cell %r is not what its surface says (the arrow excused at screen cell %r)"
                                % (label, name, at, cell))
    except (OSError, ValueError, KeyError) as exc:
        problems.append("%s: cannot compare the surfaces with the screen: %s" % (label, exc))
    return problems


def check_cell_restored(shot, geometry, reads, cell, label):
    """One screen cell the arrow has left is what its surface says again."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
        obs = reads["obs"]
        for name in ("strip", "choices", "conversation", "app"):
            desc = obs[name]
            r, c = cell[0] - desc["row0"], cell[1] - desc["col0"]
            if 0 <= r < desc["rows"] and 0 <= c < desc["cols"]:
                if name == "strip":
                    return []       # redrawn every frame; check_strip_6c judges it
                cur = desc["cursor"]
                cur_on = bool(cur >> 31 & 1) and ((cur >> 16) & 0x7FFF, cur & 0xFFFF) == (r, c)
                want = twin.cell_pixels(font, reads[name][r * desc["cols"] + c], cur_on)
                if not cell_matches(pixels, width, cell[0], cell[1], want):
                    return ["%s: the cell the arrow left, %r, is not its surface's - %s"
                            % (label, cell, cell_census(pixels, width, cell[0], cell[1]))]
                return []
        return ["%s: cell %r belongs to no region" % (label, cell)]
    except (OSError, ValueError, KeyError) as exc:
        return ["%s: cannot judge the restored cell: %s" % (label, exc)]


POINTER_FIELD = re.compile(r"pt (\d\d\.\d)/(\d\d\.\d) pk (\d{4}) cl (\d{3})")


def check_strip_6c(shot, geometry, obs1, obs2, label):
    """checkglass.check_strip's logic over the ring 6c strip: the 6a part of
    row 0 field by field, row 1 exactly, and the third field - pk and cl
    equal in both page reads and on the screen, pt's worst between the two
    reads, pt's last well formed, the worst under the budget."""
    regs = regions(geometry[2], geometry[3])
    strip = regs["strip"]
    try:
        got0 = read_cells(shot, geometry, strip, 0).rstrip()
        got1 = read_cells(shot, geometry, strip, 1).rstrip()
    except (OSError, ValueError) as exc:
        return [str(exc)]
    want1a, want1b = strip_rows_6c(obs1, obs1["now"])
    want2a, want2b = strip_rows_6c(obs2, obs2["now"])
    problems = []
    if want1b != want2b:
        problems.append("%s: the strip's second row changed between the two page reads (%r -> %r) though nothing happened" % (label, want1b, want2b))
    if got1 != want1b.rstrip():
        problems.append("%s: the strip's second row is %r, but the obs page renders %r" % (label, got1, want1b.rstrip()))
    if not obs1["packets"]:
        return problems + ["%s: check_strip_6c wants a page with packets; use the frozen check_strip before the first packet" % label]
    head, field = got0[:POINTER_FIELD_COL - 1], got0[POINTER_FIELD_COL:]
    if got0[POINTER_FIELD_COL - 1:POINTER_FIELD_COL] != " ":
        problems.append("%s: column %d of the strip's first row is not blank: %r" % (label, POINTER_FIELD_COL - 1, got0))
    m = STRIP0.fullmatch(head)
    m1 = STRIP0.fullmatch(want1a[:POINTER_FIELD_COL - 1])
    m2 = STRIP0.fullmatch(want2a[:POINTER_FIELD_COL - 1])
    if not m or not m1 or not m2:
        return problems + ["%s: the strip's first row does not parse: screen %r, page %r" % (label, got0, want1a)]
    names = ["up", "core", "frames", "frame_last", "frame_worst", "photon_last", "photon_worst",
             "keys", "hw", "err", "step_last", "step_worst"]
    for i, name in enumerate(names):
        g, a, b = m.group(i + 1), m1.group(i + 1), m2.group(i + 1)
        if name in ("up", "frames", "frame_worst", "step_worst"):
            if not (float(a) <= float(g) <= float(b)):
                problems.append("%s: the strip's %s is %s, but the page read before says %s and after says %s" % (label, name, g, a, b))
        elif name in ("frame_last", "step_last"):
            pass
        elif g != a or a != b:
            problems.append("%s: the strip's %s is %s, the page says %s then %s" % (label, name, g, a, b))
    f = POINTER_FIELD.fullmatch(field)
    f1 = POINTER_FIELD.fullmatch(want1a[POINTER_FIELD_COL:])
    f2 = POINTER_FIELD.fullmatch(want2a[POINTER_FIELD_COL:])
    if not f or not f1 or not f2:
        return problems + ["%s: the strip's third field does not parse: screen %r, page %r" % (label, field, want1a[POINTER_FIELD_COL:])]
    if not (float(f1.group(2)) <= float(f.group(2)) <= float(f2.group(2))):
        problems.append("%s: pt's worst is %s on the screen, the page says %s then %s" % (label, f.group(2), f1.group(2), f2.group(2)))
    for i, name in ((3, "pk"), (4, "cl")):
        if not (f.group(i) == f1.group(i) == f2.group(i)):
            problems.append("%s: the strip's %s is %s, the page says %s then %s" % (label, name, f.group(i), f1.group(i), f2.group(i)))
    t = max(obs2["tsc_per_ms"], 1)
    if obs2["pointer_worst"] / t > POINTER_BUDGET_MS:
        problems.append("%s: pointer input-to-photon's worst is %.1f ms, over the budget of %.1f ms"
                        % (label, obs2["pointer_worst"] / t, POINTER_BUDGET_MS))
    return problems


def check_pointer_counts(obs, counts, label, **more):
    """The page's pointer counters against the counts derived from the
    events, plus any other field the caller names."""
    want = {"packets": counts["packets"], "clicks": counts["clicks"], "hits": counts["hits"],
            "mouse_bytes": counts["mouse_bytes"], "keys": counts["keys"]}
    want.update(more)
    return check_counts(obs, want, label)


def check_i8042(obs, label):
    """The command byte the guest wrote: both interrupts on, both ports
    enabled, translation kept; the read half printed, its bit 6 asserted."""
    v = obs["i8042_cmd"]
    read, written = v & 0xFF, (v >> 8) & 0xFF
    problems = []
    if written & 0x03 != 0x03 or written & 0x30 or not written & 0x40:
        problems.append("%s: the i8042 command byte written is 0x%02x - want bits 0 and 1 set, 4 and 5 clear, 6 set" % (label, written))
    if not read & 0x40:
        problems.append("%s: the i8042 command byte read at boot was 0x%02x - translation was not on" % (label, read))
    if not problems:
        say("%s: the i8042 command byte read 0x%02x, written 0x%02x" % (label, read, written))
    return problems


# --------------------------------------------------------------- serial -----

def run_serial(smp):
    """Test 2 at one -smp value: the lines and the page before and after
    the first packet."""
    serial = os.path.join(OUT, "serial.pointer.%d.txt" % smp)
    shots = {k: os.path.join(OUT, "screen.pointer.%d.%s.ppm" % (smp, k)) for k in ("s0", "s1")}
    fresh_disk(NOTES)
    fresh_disk(HOME_IMG)
    steps = [
        ("serial", "before"),
        ("obs", "r0"),
        ("surfaces", "s0"), ("shot", shots["s0"]), ("obs", "r0b"),
        ("mouse", 1, 0), ("sleep", 0.5),
        ("obs", "r1"),
        ("surfaces", "s1"), ("shot", shots["s1"]), ("obs", "r1b"),
    ]
    capture, reads, events, err = drive(smp, NOTES, HOME_IMG, steps, serial)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1

    ok = True
    # Before the first packet: ring 6b's machine, to the line and to the pixel.
    problems = []
    if "before" not in reads:
        problems.append("the serial capture before the move was not taken")
        geometry = (None,) * 4
    else:
        problems, geometry = check_boot_lines(reads["before"], smp, "formatted", 0)
        problems += check_no_mouse_line(reads["before"])
        problems += check_echo(reads["before"], b"")
    ok &= report("before the first packet, the serial log is not ring 6b's", problems, capture)
    if not problems:
        say("before the move: seventeen S6: lines, home 0 apps, nic %s, nothing after keyboard ready" % MAC)

    if None in geometry:
        say("no geometry to judge - the boot lines were wrong")
        return 1
    w, h, cols, rows = geometry
    problems = []
    if "r0" not in reads or "r0b" not in reads or "s0" not in reads:
        problems.append("the obs page or the surfaces could not be read before the move")
    else:
        r0 = reads["r0"]
        problems += check_pointer_counts(r0, reads["counts"]["r0"], "before the move",
                                         ptr_x=w // 2, ptr_y=h // 2, ptr_cell=((h // 2) // CELL) << 16 | (w // 2) // CELL,
                                         pointer_last=0, pointer_worst=0, resyncs=0, mouse_hw=0, mouse_id=1,
                                         buttons=0, ptr_pending=0)
        problems += check_i8042(r0, "before the move")
        problems += check_strip(shots["s0"], geometry, r0, reads["r0b"], "screen S0")
        problems += check_surfaces(shots["s0"], reads["s0"], "screen S0")
        problems += check_no_arrow(shots["s0"], geometry, "screen S0")
        problems += check_choices(shots["s0"], geometry, choices_row(False, 0, []))
        problems += check_mode_field(shots["s0"], geometry, "prompt")
    ok &= report("before the first packet, the page or the screen is not ring 6a's", problems)
    if not problems:
        say("before the move: the mouse identified at boot (mouse_id 1), the pointer at the centre (%d, %d), no packet; "
            "the frozen 6a strip and surface checks pass on the screendump, no arrow anywhere" % (w // 2, h // 2))

    # After one packet.
    problems, stripped = strip_mouse_line(capture)
    more, _ = check_boot_lines(stripped, smp, "formatted", 0)
    problems += more
    problems += check_echo(stripped, b"")
    ok &= report("after the first packet, the serial log is not what the section asks for", problems, capture)
    if not problems:
        say("after the move: eighteen S6: lines, '%s' eighteenth, and nothing else after keyboard ready" % MOUSE_LINE)

    problems = []
    if "r1" not in reads or "r1b" not in reads or "s1" not in reads:
        problems.append("the obs page or the surfaces could not be read after the move")
    else:
        r1, r1b = reads["r1"], reads["r1b"]
        row, col = reads["model"]["r1"]
        problems += check_pointer_counts(r1, reads["counts"]["r1"], "after the move",
                                         ptr_x=w // 2 + 1, ptr_y=h // 2, ptr_cell=row << 16 | col,
                                         resyncs=0, mouse_hw=1, mouse_id=1, buttons=0, ptr_pending=0)
        t = max(r1["tsc_per_ms"], 1)
        if not 0 < r1["pointer_last"] / t <= POINTER_BUDGET_MS or not 0 < r1["pointer_worst"] / t <= POINTER_BUDGET_MS:
            problems.append("pointer input-to-photon after one move is %.2f ms (worst %.2f), want within (0, %.1f]"
                            % (r1["pointer_last"] / t, r1["pointer_worst"] / t, POINTER_BUDGET_MS))
        problems += check_arrow_at(shots["s1"], geometry, row, col, "screen S1")
        problems += check_surfaces_except(shots["s1"], reads["s1"], (row, col), "screen S1")
        problems += check_strip_6c(shots["s1"], geometry, r1, r1b, "screen S1")
        try:
            width, height, pixels = read_ppm(shots["s1"])
            stray = check_colour_discipline(pixels, width, height)
            if stray:
                problems.append(stray)
        except (OSError, ValueError) as exc:
            problems.append(str(exc))
    ok &= report("after the first packet, the page or the screen is not what the section asks for", problems)
    if not problems:
        r1 = reads["r1"]
        t = max(r1["tsc_per_ms"], 1)
        say("after the move: one packet, three bytes, the pointer at (%d, %d) in cell %r, the arrow there and every other cell "
            "its surface's; pt %.1f ms; the strip's third field 'pt %s/%s pk %s cl %s' equal to the page"
            % (r1["ptr_x"], r1["ptr_y"], reads["model"]["r1"], r1["pointer_last"] / t,
               fmt_ms(r1["pointer_last"], t), fmt_ms(r1["pointer_worst"], t), fmt_n(r1["packets"], 4), fmt_n(r1["clicks"], 3)))

    say("-smp %d: %s" % (smp, "the mouse spoke and the machine said so - on serial, in the page and on the glass" if ok
                         else "the pointer is not as the section asks"))
    return 0 if ok else 1


# ------------------------------------------------------------ the germline --

def check_grow_germline(root, want, blob, name, choices, model="mock"):
    """checkglass.check_germline_entry for a plain grow rehearsed in THIS
    ring's twin: the same provenance rules, a rehearsal log of seventeen
    S6: lines (two disks) and no ERR: line."""
    problems = []
    key = germline_key(want)
    d = os.path.join(root, key)
    if not os.path.isdir(d):
        return ["no germline entry %s for %r" % (key, want)]
    try:
        got = open(os.path.join(d, "component.bin"), "rb").read()
    except OSError as exc:
        return ["entry %s: %s" % (key, exc)]
    if got != blob:
        problems.append("entry %s: component.bin is %d bytes, not the %d-byte blob the mock serves" % (key, len(got), len(blob)))
    try:
        prov = json.load(open(os.path.join(d, "provenance.json")))
    except (OSError, ValueError) as exc:
        return problems + ["entry %s: provenance.json: %s" % (key, exc)]
    want_fields = {"request": want, "normalised": want, "key": key, "abi": ABI, "machine": MACHINE,
                   "model": model, "sha256": hashlib.sha256(blob).hexdigest(), "size": len(blob),
                   "name": name, "choices": [[chr(k), l.decode()] for k, l in choices]}
    for k, v in want_fields.items():
        if prov.get(k) != v:
            problems.append("entry %s: provenance %s is %r, want %r" % (key, k, prov.get(k), v))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(prov.get("date", ""))):
        problems.append("entry %s: provenance date %r is not ISO-8601 UTC" % (key, prov.get("date")))
    if not isinstance(prov.get("tries"), int) or prov["tries"] < 1:
        problems.append("entry %s: provenance tries is %r" % (key, prov.get("tries")))
    reh = prov.get("rehearsal") or {}
    if reh.get("passed") is not True or reh.get("phrases") != [] or not isinstance(reh.get("seconds"), (int, float)):
        problems.append("entry %s: provenance rehearsal is %r, want passed with no phrases and a time" % (key, reh))
    try:
        rlog = open(os.path.join(d, "rehearsal.log")).read()
    except OSError as exc:
        return problems + ["entry %s: rehearsal.log: %s" % (key, exc)]
    if len(re.findall(r"^S6: ", rlog, re.M)) != LINES:
        problems.append("entry %s: rehearsal.log does not hold the twin's seventeen S6: lines" % key)
    if MOUSE_LINE in rlog:
        problems.append("entry %s: the twin's rehearsal log carries '%s' - the twin must never move the mouse" % (key, MOUSE_LINE))
    if "ERR:" in rlog:
        problems.append("entry %s: rehearsal.log carries an ERR: line" % key)
    return problems


# --------------------------------------------------------------- pictures ---

def check_panel_cells(shot, geometry, cells, label):
    """Exactly these app-panel cells (panel-relative (row, col) -> glyph)
    hold their glyphs; every other panel cell is blank; two colours."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    row0, col0, prows, pcols = regions(cols, rows)["app"]
    problems = []
    for (r, c), ch in sorted(cells.items()):
        if not cell_matches(pixels, width, row0 + r, col0 + c, render_cell(font, ch)):
            problems.append("%s: app panel cell (%d, %d) is not %r - %s" % (label, r, c, ch, cell_census(pixels, width, row0 + r, col0 + c)))
    strays = [(r, c) for r in range(prows) for c in range(pcols)
              if (r, c) not in cells and not cell_matches(pixels, width, row0 + r, col0 + c, blank_cell())]
    if strays:
        problems.append("%s: %d other app-panel cell(s) are not blank, the first at %r - %s"
                        % (label, len(strays), strays[0], cell_census(pixels, width, row0 + strays[0][0], col0 + strays[0][1])))
    stray = check_colour_discipline(pixels, width, height)
    if stray:
        problems.append(stray)
    return problems


def title_cells(text, row=0, col=0):
    return {(row, col + i): ch for i, ch in enumerate(text)}


def check_typing_row(shot, geometry, region, after, text, label):
    """The conversation row right below the row `after` reads `text` from
    column 0 with the block cursor in the cell after it: a line being typed
    (here, the marker a click typed)."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    row0, col0, nrows, ncols = region
    hits = [r for r in range(nrows) if all(cell_matches(pixels, width, row0 + r, col0 + c, render_cell(font, ch))
                                           for c, ch in enumerate(after))
            and cell_matches(pixels, width, row0 + r, col0 + len(after), blank_cell())]
    if len(hits) != 1:
        return ["%s: the row %r appears %d times in the conversation, want exactly once" % (label, after, len(hits))]
    r = hits[0] + 1
    problems = []
    for c, ch in enumerate(text):
        if not cell_matches(pixels, width, row0 + r, col0 + c, render_cell(font, ch)):
            problems.append("%s: conversation row %d, column %d is not %r - %s" % (label, r, c, ch, cell_census(pixels, width, row0 + r, col0 + c)))
            break
    if not cell_matches(pixels, width, row0 + r, col0 + len(text), cursor_cell()):
        problems.append("%s: conversation row %d, column %d is not the block cursor after %r - %s"
                        % (label, r, len(text), text, cell_census(pixels, width, row0 + r, col0 + len(text))))
    return problems


def target_col(targets, kind, arg):
    """The middle column of a choices-row target, from the section's
    choice_targets - never arithmetic."""
    for first, last, k, a in targets:
        if (k, a) == (kind, arg):
            return (first + last) // 2
    raise ValueError("no target %r %r in %r" % (kind, arg, targets))


def gap_col(targets):
    """A column in the first three-space gap of the row."""
    return targets[0][1] + 2


def park_cell(geometry):
    """Where the cursor rests for a screendump: the conversation panel's
    last row, last column - a cell no frozen helper reads."""
    regs = regions(geometry[2], geometry[3])
    row0, col0, nrows, ncols = regs["conversation"]
    return row0 + nrows - 1, col0 + ncols - 1


# ----------------------------------------------------------------- point ----

def run_point(smp):
    """Test 3 at one -smp value: the pointer, driven by the monitor."""
    blob, problems = fixture_self_check("pointer")
    if not report("the point app is not what the repository says", problems):
        return 1
    try:
        pt = point_offset(blob)
    except ValueError as exc:
        say("stage6/pointer.bin: %s" % exc)
        return 1
    if pt is None:
        say("stage6/pointer.bin does not announce point")
        return 1
    say("stage6/pointer.asm reproduces stage6/pointer.bin: %d bytes, sha256 %s, point at %d"
        % (len(blob), hashlib.sha256(blob).hexdigest()[:16], pt))
    app, problems = fixture_self_check("app")
    if not report("the test app is not what the repository says", problems):
        return 1
    if point_offset(app) is not None:
        say("the test app announces point - it must not")
        return 1

    # The geometry this ring's tests run at is read from the guest's own log
    # at boot; the driver's moveto steps take screen cells, so the cells are
    # spelled here in terms of the mode the display states (GLASS.md:
    # 1920x1080 is 120x67 cells) and the log is required to agree before
    # anything is judged.
    W, H = 1920, 1080
    cols, rows = W // CELL, H // CELL
    regs = regions(cols, rows)
    crow = regs["choices"][0]
    prow0, pcol0 = regs["app"][0], regs["app"][1]
    park = park_cell((W, H, cols, rows))
    t_prompt = choice_targets(False, 0, [])
    t_app = choice_targets(True, 1, POINT_CHOICES)
    t_papp = choice_targets(True, 0, POINT_CHOICES)
    marks = {(5, 7): 1, (9, 12): 2, (12, 3): 4}          # panel cell -> the monitor's button mask

    record = os.path.join(OUT, "broker.point.%d.jsonl" % smp)
    serial = os.path.join(OUT, "serial.point.%d.txt" % smp)
    shots = {k: os.path.join(OUT, "screen.point.%d.%s.ppm" % (smp, k)) for k in ("a", "b", "c", "f0", "t", "d")}
    mock, err = start_mock(record)
    if err:
        say(err)
        return 1
    say("mock broker listening on 127.0.0.1:%d, germline wiped at %s" % (BROKER_PORT, os.path.relpath(GERMLINE, REPO)))
    try:
        fresh_disk(NOTES)
        fresh_disk(HOME_IMG)
        steps = [
            ("type", "before\n"), ("sleep", 1.5),
            ("mouse", 1, 0), ("sleep", 0.5),                                   # the cursor appears
            ("moveto", crow, target_col(t_prompt, "key", ord("?"))),
            ("button", 1, "hit"), ("button", 0), ("sleep", 1.0),              # "? ask" clicked: types ?
            ("moveto", park[0], park[1]), ("sleep", 0.3),
            ("shot", shots["a"]),
            ("type", " ping\n"), ("wait_record", record, 1, 20.0), ("sleep", SETTLE),
            ("type", "! point app\n"), ("wait_record", record, 2, 150.0), ("sleep", 3.0),
            ("obs", "p"),
        ]
        for (r, c), mask in sorted(marks.items()):
            steps += [("moveto", prow0 + r, pcol0 + c), ("button", mask, "hit"), ("button", 0), ("sleep", 0.3)]
        steps += [
            ("moveto", park[0], park[1]), ("sleep", 1.0),
            ("shot", shots["b"]), ("obs", "b"),
            ("moveto", crow, target_col(t_app, "key", ord("c"))),
            ("button", 1, "hit"), ("button", 0), ("sleep", 0.5),              # "c clear" clicked
            ("moveto", park[0], park[1]), ("sleep", 0.5),
            ("shot", shots["c"]),
            ("moveto", crow, target_col(t_app, "key", 9)),
            ("button", 1, "hit"), ("button", 0), ("sleep", 1.0),              # "Tab prompt" clicked
            ("obs", "f0"),
            ("moveto", park[0], park[1]), ("sleep", 0.3),
            ("shot", shots["f0"]),
            ("type", "mid\n"), ("sleep", 1.5),
            ("moveto", crow, target_col(t_papp, "key", 9)),
            ("button", 1, "hit"), ("button", 0), ("sleep", 1.0),              # "Tab app" clicked
            ("obs", "f1"),
            ("moveto", crow, gap_col(t_app)),
            ("button", 1), ("button", 0), ("sleep", 0.5),                     # a gap: nothing
            ("obs", "g"),
            ("moveto", crow, target_col(t_app, "key", 0x1B)),
            ("button", 1, "hit"), ("button", 0), ("sleep", 2.0),              # "Esc exit" clicked
            ("obs", "x"),
            ("type", "! test app\n"), ("wait_record", record, 3, 150.0), ("sleep", 3.0),
            ("moveto", prow0 + 5, pcol0 + 7),
            ("button", 1), ("button", 0), ("button", 2), ("button", 0), ("sleep", 0.5),   # harmless
            ("moveto", park[0], park[1]), ("sleep", 1.0),
            ("shot", shots["t"]), ("obs", "t"),
            ("type", "\x1b"), ("sleep", 2.0),
            ("type", "after\n"), ("sleep", SETTLE),
            ("shot", shots["d"]), ("surfaces", "d"), ("obs", "d2"),
        ]
        capture, reads, events, err = drive(smp, NOTES, HOME_IMG, steps, serial)
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1

    ok = True
    problems, stripped = strip_mouse_line(capture)
    more, geometry = check_boot_lines(stripped, smp, "formatted", 0)
    problems += more
    problems += check_echo(stripped, b"before\r\n? ping\r\n! point app\r\nmid\r\n! test app\r\nafter\r\n")
    ok &= report("the serial log is not what the section asks for", problems, capture)
    if not problems:
        say("eighteen boot lines with '%s' after the first move, nic %s; the echo after ready is the typed lines "
            "plus the '?' the click typed" % (MOUSE_LINE, MAC))
    if None in geometry or geometry[:2] != (W, H):
        say("the guest's mode %r is not the display's %dx%d - the cells this test computed do not apply" % (geometry, W, H))
        return 1
    conv = regs["conversation"]

    entries, problems = read_record(record)
    if entries is not None:
        if len(entries) != 3:
            problems.append("the broker saw %d connection(s), want 3 - a click must put nothing on the wire" % len(entries))
        if len(entries) >= 1:
            problems += check_question_entry(1, entries[0], "ping")
        if len(entries) >= 2:
            problems += check_grow_entry(2, entries[1], "point app", "generated", 1, ["pass"], "app",
                                         app_frame(blob, POINT_NAME, POINT_CHOICES, 0), name="point app")
        if len(entries) >= 3:
            problems += check_grow_entry(3, entries[2], "test app", "generated", 2, ["pass"], "app",
                                         app_frame(app, b"test app", TEST_CHOICES, 0), name="test app")
    ok &= report("the broker's record is not what GLASS.md asks for", problems)
    if not problems:
        say("the record: 'ping' answered; 'point app' generated once and rehearsed once, the frame GLASS.md gives for "
            "the point app; 'test app' likewise; nothing else reached the wire")

    problems = check_grow_germline(GERMLINE, "point app", blob, "point app", POINT_CHOICES)
    problems += check_grow_germline(GERMLINE, "test app", app, "test app", TEST_CHOICES)
    names = germline_entries(GERMLINE)
    if len(names) != 2:
        problems.append("the germline holds %d entries %r, want exactly 2" % (len(names), names))
    ok &= report("the germline is not what GLASS.md asks for", problems)

    problems = check_image(NOTES, ["before", "mid", "after"])
    ok &= report("the notebook is not what it should be", problems)

    # Screen A: the click on "? ask" typed the marker.
    problems = check_region_rows(shots["a"], geometry, conv, ["> before"])
    problems += check_typing_row(shots["a"], geometry, conv, "> before", "> ?", "screen A")
    problems += check_choices(shots["a"], geometry, choices_row(False, 0, []))
    problems += check_mode_field(shots["a"], geometry, "prompt")
    problems += check_arrow_at(shots["a"], geometry, park[0], park[1], "screen A")
    ok &= report("screen A does not show the marker the click typed", problems)
    if not problems:
        say("screen A: '> ?' with the block cursor after it - the click on '? ask' did what the key does")

    problems = []
    if "p" not in reads:
        problems.append("the obs page could not be read after the point app started")
    else:
        problems += check_counts(reads["p"], {"mode": 3, "name": "point app", "focus": 1, "grows_generated": 1,
                                              "grows_served": 0, "questions": 1, "requests": 1, "errors": 0}, "obs P")
        problems += check_pointer_counts(reads["p"], reads["counts"]["p"], "obs P")
    ok &= report("the point app did not start as the section asks", problems)

    # Screen B: three buttons in the panel, three digits where they landed.
    cells = title_cells("point app")
    for (r, c), mask in marks.items():
        cells[(r, c)] = str(BUTTON_OF_MASK[mask])
    problems = check_panel_cells(shots["b"], geometry, cells, "screen B")
    problems += check_choices(shots["b"], geometry, choices_row(True, 1, POINT_CHOICES))
    problems += check_mode_field(shots["b"], geometry, "running point app")
    if "b" in reads:
        problems += check_pointer_counts(reads["b"], reads["counts"]["b"], "obs B", focus=1)
    else:
        problems.append("the obs page could not be read at screen B")
    ok &= report("screen B does not show point's marks", problems)
    if not problems:
        say("screen B: 'point app' and the digits 1, 2, 3 at the three clicked cells - point received row, column and button; "
            "%d clicks, %d hits so far" % (reads["b"]["clicks"], reads["b"]["hits"]))

    # Screen C: "c clear" clicked - the app's declared key reached key.
    problems = check_panel_cells(shots["c"], geometry, title_cells("point app"), "screen C")
    ok &= report("screen C does not show the panel cleared by the clicked choice", problems)
    if not problems:
        say("screen C: the panel holds only the title again - the click on 'c clear' delivered c to the app")

    # F0, F1, G, X: the focus items, a gap, Esc.
    problems = []
    for label, focus in (("f0", 0), ("f1", 1), ("g", 1)):
        if label not in reads:
            problems.append("the obs page could not be read at %s" % label)
            continue
        problems += check_counts(reads[label], {"mode": 3, "name": "point app", "focus": focus}, "obs " + label.upper())
        problems += check_pointer_counts(reads[label], reads["counts"][label], "obs " + label.upper())
    problems += check_choices(shots["f0"], geometry, choices_row(True, 0, POINT_CHOICES))
    problems += check_mode_field(shots["f0"], geometry, "running point app")
    if "x" in reads:
        problems += check_counts(reads["x"], {"mode": 0, "name": "", "focus": 0}, "obs X")
        problems += check_pointer_counts(reads["x"], reads["counts"]["x"], "obs X")
    else:
        problems.append("the obs page could not be read after the Esc click")
    ok &= report("the row's Tab, gap and Esc clicks did not do what the keys do", problems)
    if not problems:
        say("'Tab prompt' clicked: focus 0 and the prompt's row beside the app; 'Tab app' clicked: focus 1; a gap clicked: "
            "one more click and no hit; 'Esc exit' clicked: the app closed")

    # Screen T: the frozen test app clicked on harmlessly.
    problems = check_app_panel(shots["t"], geometry, "-")
    problems += check_mode_field(shots["t"], geometry, "running test app")
    problems += check_choices(shots["t"], geometry, choices_row(True, 1, TEST_CHOICES))
    if "t" in reads:
        problems += check_counts(reads["t"], {"mode": 3, "name": "test app", "focus": 1}, "obs T")
        problems += check_pointer_counts(reads["t"], reads["counts"]["t"], "obs T")
    else:
        problems.append("the obs page could not be read at screen T")
    ok &= report("screen T: the four-callback test app was not clicked on harmlessly", problems)
    if not problems:
        say("screen T: the test app's known picture untouched by two clicks in its panel - clicks counted, no hit")

    # Screen D: the conversation, the page and the strip at the end.
    problems = []
    if "d" not in reads or "d2" not in reads:
        problems.append("the obs page or the surfaces could not be read at the end")
    else:
        d = reads["d"]["obs"]
        problems += check_mode_field(shots["d"], geometry, "prompt")
        problems += check_choices(shots["d"], geometry, choices_row(False, 0, []))
        problems += check_app_panel_blank(shots["d"], geometry)
        problems += check_region_rows(shots["d"], geometry, conv,
                                      ["> before", "> ? ping", CANNED["ping"], "> ! point app", "> mid", "> ! test app",
                                       "> after", PROMPT])
        problems += check_surfaces_except(shots["d"], reads["d"], park, "screen D")
        problems += check_arrow_at(shots["d"], geometry, park[0], park[1], "screen D")
        problems += check_strip_6c(shots["d"], geometry, d, reads["d2"], "screen D")
        problems += check_counts(d, {"mode": 0, "name": "", "focus": 0, "wire_conns": 3, "questions": 1, "requests": 2,
                                     "notes": 3, "errors": 0, "grows_generated": 2, "grows_served": 0, "resyncs": 0},
                                 "screen D")
        problems += check_pointer_counts(d, reads["counts"]["d"], "screen D")
    ok &= report("screen D is not the truth", problems)
    if not problems:
        d = reads["d"]["obs"]
        say("screen D: the whole conversation intact, the prompt's row, the panel blank; the strip's third field equal to the "
            "page (pk %04d cl %03d), every region its surface's bar the arrow; keys %d (clicks not counted), %d clicks, %d hits"
            % (d["packets"], d["clicks"], d["keys"], d["clicks"], d["hits"]))

    say("-smp %d: %s" % (smp, "the pointer held - a click does what its key does, and point drew the cell it was given" if ok
                         else "the pointer did not hold"))
    return 0 if ok else 1


# ---------------------------------------------------------------- main -----

def main(argv):
    if len(argv) == 2 and argv[0] in ("--serial", "--point"):
        try:
            return (run_serial if argv[0] == "--serial" else run_point)(int(argv[1]))
        except ValueError:
            pass
    say("usage: checkpointer.py --serial <smp> | --point <smp> | --truth")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
