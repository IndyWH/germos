#!/usr/bin/env python3
"""Stage 6 ring 6a acceptance tests 2 (the one-core run), 3 and 4.

One driver owns every booted run bar test 2's two serial runs, as Stage
5's checkgermline.py did: boot stage6/out/esp.img headless under OVMF with
the standard VGA device stating 1440x1440 through its EDID (GLASS.md,
"The screen"), a fresh 16 MB raw notebook image as a virtio disk and the
caged network of stage4/UMBILICAL.md - slirp with restrict=on and one
guestfwd, delivered per connection by netcat to the broker on
127.0.0.1:9999 - the QEMU monitor on stdio and serial to a file; wait for
the guest itself to say "S6: keyboard ready"; type from OUTSIDE via the
monitor's sendkey; read the obs page and the surfaces through the
monitor's xp; screendump; quit. Then judge the broker's record by
GLASS.md's own frame rule, the germline directory by its provenance rule,
the disk image by NOTEBOOK.md, the serial capture byte for byte, the obs
page by GLASS.md's layout, and the screen pixel by pixel from the shared
font - the strip rendered from the obs page, every region from its
surface.

The broker is broker/glass.py --mock, whose pipeline REHEARSES every
candidate in a real headless boot of a copy of the same image
(broker/twin.py) - so a grow costs a second QEMU, on its own port, in its
own scratch directory, while the gate's own guest waits on the wire. The
mock generates from GLASS.md's canned table and calls nothing outside the
repository; the gate never spends a token.

Three modes:

  --one-core     Test 2's third run. Boot at -smp 1 with the monitor;
                 wait for the named ERR: line; screendump. Assert:
                 fourteen S6: lines, no "glass core", no "keyboard
                 ready", and the ERR: line on the screen, rendered from
                 the shared font in the conversation panel's columns,
                 two colours only (plan amendment A3).

  --glass <smp>  Test 3 (item 6).

  --truth        Test 4 (item 7).

Pure standard library on purpose. Everything runs inside QEMU with exactly
two drives per guest, raw image files under stage6/out/, created here or
by the twin; the broker (mock) on 127.0.0.1 only. No real disk is touched;
no Claude call is ever made.

This file is frozen acceptance machinery from plan item 8. See the header
of stage6/test.sh.

Exit 0 on pass, 1 otherwise.
"""

import hashlib
import json
import os
import re
import select
import shutil
import socket
import struct
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "stage6", "out")
ESP = os.path.join(OUT, "esp.img")
NOTES = os.path.join(OUT, "notes.img")
FONT = os.path.join(REPO, "stage2", "font8x8.bin")
BROKER = os.path.join(REPO, "broker", "glass.py")
FIXTURES = os.path.join(REPO, "stage6")
GERMLINE = os.path.join(OUT, "germline")
REHEARSAL = os.path.join(OUT, "rehearsal")
OVMF = "/usr/share/ovmf/OVMF.fd"

sys.path.insert(0, os.path.join(REPO, "broker"))
from glass import (grow_request, app_frame, refusal_frame, parse_response,  # noqa: E402
                   germline_key, regions, parse_obs, strip_rows, choices_row,
                   BLOB_MAX, MACHINE, ABI, LINES, TEST_CHOICES, CELL_BLOCK)
import twin  # noqa: E402
from twin import Driver, keyname, cell_pixels, surface_mismatch, region_background  # noqa: E402
from rehearse import (read_ppm, load_font, render_cell, cell_matches, BG, FG, TOL, CELL)  # noqa: E402

DISK_BYTES = 16 * 1024 * 1024
SECTOR = 512

# The cage, exactly as stage4/UMBILICAL.md spells it, with the harness's MAC.
BROKER_PORT = 9999
REHEARSAL_PORT = 9998
MAC = "52:54:00:a1:06:01"
CAGE_NETDEV = ("user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:%d-cmd:nc -N 127.0.0.1 %d"
               % (BROKER_PORT, BROKER_PORT))
CAGE_DEVICE = "virtio-net-pci,netdev=n0,mac=" + MAC

# The display, exactly as GLASS.md spells it - the twin's flags, asserted.
DISPLAY_EDID = ["-vga", "none", "-device", "VGA,edid=on,xres=1440,yres=1440"]
DISPLAY_NONE = ["-vga", "none", "-device", "VGA,edid=off"]

READY = b"S6: keyboard ready"
ONE_CORE_ERR = "ERR: the glass needs a second core - boot with -smp 2 or more"
NO_ANSWER = "no answer from the broker"
CAP = 1048576

# UMBILICAL.md's canned answers to questions - what must be on the screen.
CANNED = {
    "ping": "pong",
    "hello": "hello from the mock broker\nask me something true at test 5",
}

KEY_GAP = 0.2        # seconds between keys - a monitor can outrun a guest
SETTLE = 2.0         # seconds after an answer is known to have arrived

INDENT = "    "


def say(msg):
    print(INDENT + msg)


# ---------------------------------------------------------------- driver ----

def fresh_disk(path):
    if os.path.exists(path):
        os.remove(path)
    with open(path, "wb") as fh:
        fh.truncate(DISK_BYTES)


def qemu_argv(smp, disk, serial_path, display=DISPLAY_EDID):
    """The one place the QEMU command is spelled. Test 4 inspects this."""
    return [
        "qemu-system-x86_64",
        "-machine", "q35",
        "-m", "256M",
        "-smp", str(smp),
        "-bios", OVMF,
    ] + list(display) + [
        "-drive", "format=raw,file=" + ESP,
        "-drive", "format=raw,file=" + disk + ",if=virtio",
        "-netdev", CAGE_NETDEV,
        "-device", CAGE_DEVICE,
        "-display", "none",
        "-serial", "file:" + serial_path,
        "-monitor", "stdio",
    ]


def record_count(path):
    try:
        return len([l for l in open(path).read().splitlines() if l.strip()])
    except OSError:
        return 0


def drive(smp, disk, steps, serial_path, ready=READY, ready_limit=60.0, display=DISPLAY_EDID):
    """Boot inside the cage, wait for the guest's own ready line, run the
    steps - ("type", text), ("sleep", seconds), ("wait_record", path, count,
    timeout), ("shot", path), ("obs", label), ("surfaces", label) - quit,
    reap. Returns (serial_bytes, reads, error): reads maps each obs label
    to the parsed page and each surfaces label to {name: cells}. Never
    leaves a QEMU running behind us."""
    reads = {}
    if not os.path.isfile(ESP):
        return b"", reads, "no image was built"
    if not os.path.isfile(OVMF):
        return b"", reads, "OVMF firmware not found at " + OVMF
    if os.path.exists(serial_path):
        os.remove(serial_path)
    for step in steps:
        if step[0] == "shot" and os.path.exists(step[1]):
            os.remove(step[1])

    proc = subprocess.Popen(qemu_argv(smp, disk, serial_path, display),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    drv = Driver(proc, serial_path, OUT)

    err = None
    obs_addr = None
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
            time.sleep(1.0)  # let the guest finish its replay, prompt and sti
            for step in steps:
                if step[0] == "type":
                    drv.type_text(step[1])
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
                elif step[0] in ("obs", "surfaces"):
                    if obs_addr is None:
                        text = drv.serial_bytes().decode("utf-8", "replace")
                        m = re.search(r"S6: obs page 0x([0-9a-f]{16})", text)
                        obs_addr = int(m.group(1), 16) if m else 0
                    try:
                        if not obs_addr:
                            raise ValueError("no obs page line on serial")
                        page = drv.read_obs(obs_addr)
                        if step[0] == "obs":
                            reads[step[1]] = page
                        else:
                            reads[step[1]] = {name: drv.read_surface(page[name])
                                              for name in ("strip", "choices", "conversation", "app")}
                            reads[step[1]]["obs"] = page
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
    return drv.serial_bytes(), reads, err


# ------------------------------------------------------- the serial claims --

BOOT_PATTERNS = [
    (r"S6: alive", "S6: alive"),
    (r"S6: edid (?:(\d+)x(\d+)|none)", "S6: edid <W>x<H> | S6: edid none"),
    (r"S6: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})", "S6: gop <W>x<H> fb 0x<16 hex>"),
    (r"S6: boot services exited", "S6: boot services exited"),
    (r"S6: gdt and paging ours", "S6: gdt and paging ours"),
    (r"S6: idt ready", "S6: idt ready"),
    (r"S6: cores found (\d+)", "S6: cores found <N>"),
    (r"S6: cores woken (\d+)", "S6: cores woken <N>"),
    (r"S6: console (\d+)x(\d+)", "S6: console <COLS>x<ROWS>"),
    (r"S6: disk (\d+) sectors", "S6: disk <N> sectors"),
    (r"S6: notebook (formatted|\d+ notes)", "S6: notebook formatted | S6: notebook <N> notes"),
    (r"S6: nic ([0-9a-f]{2}(?::[0-9a-f]{2}){5})", "S6: nic <mac>"),
    (r"S6: component region 0x([0-9a-f]{16}) (\d+) bytes", "S6: component region 0x<16 hex> 1048576 bytes"),
    (r"S6: obs page 0x([0-9a-f]{16})", "S6: obs page 0x<16 hex>"),
    (r"S6: glass core (\d+)", "S6: glass core <id>"),
    (r"S6: keyboard ready", "S6: keyboard ready"),
]


def check_boot_lines(capture, smp, notebook_want, count=LINES):
    """The lines, in order, self-consistent: the EDID's mode taken when
    stated, the geometry from the mode, line thirteen 128 mod 4096, line
    fourteen page-aligned, found = woken = smp. Returns (problems,
    geometry) with geometry = (w, h, cols, rows)."""
    problems = []
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S6: [^\n]*", text)
    if len(got) != count:
        problems.append("expected exactly %d S6: lines, found %d" % (count, len(got)))
        if len(got) > count:
            problems.append("more than expected usually means a reboot loop - and with the IDT "
                            "up it should have been an ERR: exception line instead")
    if count == LINES:
        errs = re.findall(r"ERR: [^\n]*", text)
        if errs:
            problems.append("the guest reported: %s" % "; ".join(errs[:3]))

    w = h = cols = rows = None
    ew = eh = None
    found = woken = None
    for i, (pattern, shape) in enumerate(BOOT_PATTERNS[:count]):
        line = got[i] if i < len(got) else ""
        m = re.fullmatch(pattern, line)
        if not m:
            problems.append("line %d: got '%s', want '%s'" % (i + 1, line, shape))
            continue
        if i == 1 and m.group(1):
            ew, eh = int(m.group(1)), int(m.group(2))
        elif i == 2:
            w, h = int(m.group(1)), int(m.group(2))
            if w <= 0 or h <= 0:
                problems.append("line 3: degenerate mode %dx%d" % (w, h))
            if m.group(3) == "0" * 16:
                problems.append("line 3: framebuffer address is zero")
            if ew and (w, h) != (ew, eh):
                problems.append("line 3: the mode is %dx%d but the EDID prefers %dx%d" % (w, h, ew, eh))
        elif i == 6:
            found = int(m.group(1))
        elif i == 7:
            woken = int(m.group(1))
        elif i == 8:
            cols, rows = int(m.group(1)), int(m.group(2))
        elif i == 9:
            if int(m.group(1)) != DISK_BYTES // SECTOR:
                problems.append("line 10: the guest counted %s sectors, but the image is %d sectors"
                                % (m.group(1), DISK_BYTES // SECTOR))
        elif i == 10:
            if m.group(1) != notebook_want:
                problems.append("line 11: got 'S6: notebook %s', want 'S6: notebook %s'"
                                % (m.group(1), notebook_want))
        elif i == 11:
            if m.group(1) != MAC:
                problems.append("line 12: the guest read MAC %s, but the harness gave the device %s"
                                % (m.group(1), MAC))
        elif i == 12:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32:
                problems.append("line 13: the component region 0x%s is zero or above 4 GB" % m.group(1))
            if addr % 4096 != 128:
                problems.append("line 13: the component region 0x%s is not 128 mod 4096" % m.group(1))
            if int(m.group(2)) != CAP:
                problems.append("line 13: the cap is %s bytes, want %d" % (m.group(2), CAP))
        elif i == 13:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32 or addr % 4096:
                problems.append("line 14: the obs page 0x%s is zero, above 4 GB or not page-aligned" % m.group(1))

    if found is not None and found != smp:
        problems.append("cores found is %d, but the machine was given -smp %d" % (found, smp))
    if woken is not None and woken != smp:
        problems.append("cores woken is %d, but the machine was given -smp %d" % (woken, smp))
    if None not in (w, h, cols, rows):
        if cols != w // 16 or rows != h // 16:
            problems.append("console claims %dx%d cells, but %dx%d pixels / 16 = %dx%d"
                            % (cols, rows, w, h, w // 16, h // 16))
    return problems, (w, h, cols, rows)


def check_echo(capture, want):
    """The bytes after the ready line's CRLF must be exactly `want`: the raw
    echo of what was typed at the prompt, and nothing else - no indicator,
    no answer, no refusal, and nothing an app's keys did."""
    marker = READY + b"\r\n"
    idx = capture.find(marker)
    if idx < 0:
        return ["no '%s' CRLF in the capture" % READY.decode()]
    tail = capture[idx + len(marker):]
    if tail == want:
        return []
    return ["after 'S6: keyboard ready' the serial channel carries %r, want %r" % (tail, want)]


def dump_capture(capture):
    say("whole capture follows (OVMF chatter included, control bytes visible):")
    text = capture.decode("utf-8", "replace")
    shown = "".join(ch if ch == "\n" or 32 <= ord(ch) < 127 else "^" + format(ord(ch), "02x")
                    for ch in text.replace("\r\n", "\n"))
    for line in shown.splitlines()[-40:]:
        say("  " + line)


# ------------------------------------------------------------ the picture ---
# Stage 2's console, unchanged: two colours, 16x16 cells from the shared
# font, each font bit a 2x2 block, the cursor a solid block.

PROMPT = object()    # the row that is "> " and the block cursor


def blank_cell():
    return [bytes(BG) * CELL] * CELL


def cursor_cell():
    return [bytes(FG) * CELL] * CELL


def font_self_check(font, text):
    problems = []
    used = sorted(set(text.replace(" ", "").replace("\n", "")))
    shapes = {}
    for ch in used:
        rows = font[ord(ch) * 8:(ord(ch) + 1) * 8]
        if not any(rows):
            problems.append("glyph %r in the font is blank - the test would prove nothing" % ch)
        shapes.setdefault(bytes(rows), []).append(ch)
    for chars in shapes.values():
        if len(chars) > 1:
            problems.append("glyphs %s are identical in the font" % ", ".join(map(repr, chars)))
    if any(font[ord(" ") * 8:(ord(" ") + 1) * 8]):
        problems.append("the space glyph is not blank")
    return problems


def cell_census(pixels, width, row, col):
    counts = {}
    for dy in range(CELL):
        base = ((row * CELL + dy) * width) * 3 + col * CELL * 3
        for dx in range(CELL):
            off = base + dx * 3
            rgb = (pixels[off], pixels[off + 1], pixels[off + 2])
            counts[rgb] = counts.get(rgb, 0) + 1
    return ", ".join("rgb%s x%d" % kv for kv in sorted(counts.items(), key=lambda kv: -kv[1])[:3])


def check_colour_discipline(pixels, width, height):
    bg_row = bytes(BG) * width
    for y in range(height):
        base = y * width * 3
        row = pixels[base:base + width * 3]
        if row == bg_row:
            continue
        for x in range(width):
            off = x * 3
            p = (row[off], row[off + 1], row[off + 2])
            if all(abs(p[i] - BG[i]) <= TOL for i in range(3)):
                continue
            if all(abs(p[i] - FG[i]) <= TOL for i in range(3)):
                continue
            return ("pixel (%d, %d) is rgb%s - neither the background rgb%s nor the foreground rgb%s"
                    % (x, y, p, BG, FG))
    return None


def strip_matches(pixels, width, font, row, text, col=0):
    return all(cell_matches(pixels, width, row, col + c, render_cell(font, ch))
               for c, ch in enumerate(text))


def open_shot(shot, geometry):
    """The screendump read and checked against the geometry the guest
    claimed. Returns (width, height, pixels, cols, rows, font) or raises."""
    w, h, cols, rows = geometry
    if not os.path.isfile(shot) or os.path.getsize(shot) == 0:
        raise ValueError("qemu produced no screendump")
    width, height, pixels = read_ppm(shot)
    say("serial claims %dx%d (%dx%d cells); screendump is %dx%d" % (w, h, cols, rows, width, height))
    if (width, height) != (w, h):
        raise ValueError("screendump is %dx%d but the guest said the mode was %dx%d" % (width, height, w, h))
    return width, height, pixels, cols, rows, load_font()


def wrap_rows(text, cols):
    """A console line as the panel shows it: wrapped at the panel's width."""
    return [text[i:i + cols] for i in range(0, len(text), cols)] or [""]


def check_region_rows(shot, geometry, region, expected):
    """`expected` is a list of rows within the region (row0, col0, rows,
    cols): strings drawn from the region's column 0 (longer ones wrapped at
    the region's width), or PROMPT. They must appear on consecutive rows of
    the region, the first found exactly once in it, every text row followed
    by a blank cell (unless it fills the width), and nothing but the two
    console colours anywhere on the screen."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    row0, col0, nrows, ncols = region
    flat = []
    for e in expected:
        if e is PROMPT:
            flat.append(PROMPT)
        else:
            flat.extend(wrap_rows(e, ncols))
    texts = [t for t in flat if t is not PROMPT]
    problems = font_self_check(font, "".join(texts) + "> ")
    if problems:
        return problems

    first = flat[0]
    hits = [r for r in range(nrows) if strip_matches(pixels, width, font, row0 + r, first, col0)]
    if len(hits) != 1:
        problems.append("the row %r appears %d times in the region, want exactly once" % (first, len(hits)))
        say("per-row first-cell census, region rows that are not pure background:")
        shown = 0
        for r in range(nrows):
            if cell_matches(pixels, width, row0 + r, col0, blank_cell()):
                continue
            say("  row %3d col %d: %s" % (row0 + r, col0, cell_census(pixels, width, row0 + r, col0)))
            shown += 1
            if shown >= 24:
                say("  ...")
                break
        return problems

    base = hits[0]
    block = set(range(base, base + len(flat)))
    for i, want in enumerate(flat):
        r = base + i
        if r >= nrows:
            problems.append("row %d is off the bottom of the region - no room for %r" % (r, want))
            break
        sr = row0 + r
        if want is PROMPT:
            for col, ch in ((0, ">"), (1, " ")):
                if not cell_matches(pixels, width, sr, col0 + col, render_cell(font, ch)):
                    problems.append("row %d, column %d is not %r - %s" % (sr, col0 + col, ch, cell_census(pixels, width, sr, col0 + col)))
            if not cell_matches(pixels, width, sr, col0 + 2, cursor_cell()):
                problems.append("row %d, column %d is not the block cursor - %s" % (sr, col0 + 2, cell_census(pixels, width, sr, col0 + 2)))
            continue
        if not strip_matches(pixels, width, font, sr, want, col0):
            bad = next((c for c, ch in enumerate(want)
                        if not cell_matches(pixels, width, sr, col0 + c, render_cell(font, ch))), None)
            problems.append("row %d is not %r - column %s is %s"
                            % (sr, want, col0 + bad if bad is not None else "?",
                               cell_census(pixels, width, sr, col0 + bad) if bad is not None else "?"))
            continue
        if len(want) < ncols and not cell_matches(pixels, width, sr, col0 + len(want), blank_cell()):
            problems.append("row %d: the cell after %r is not blank - %s (an indicator left behind?)"
                            % (sr, want, cell_census(pixels, width, sr, col0 + len(want))))
        if i > 0 and want:
            others = [x for x in range(nrows) if x not in block and strip_matches(pixels, width, font, row0 + x, want, col0)]
            if others:
                problems.append("row %r also appears at region row(s) %s" % (want, others))

    stray = check_colour_discipline(pixels, width, height)
    if stray:
        problems.append(stray)
    return problems


# ---------------------------------------------------------------- the wire --
# UMBILICAL.md's request rule and GERMLINE.md's grow rule, applied to the
# broker's recorded bytes.

REQUEST_MAX = 498


def judge_request_bytes(raw):
    """The recorded bytes of one connection, judged by the frame rule alone.
    Returns ("question", text) or ("grow", body); raises ValueError."""
    if len(raw) < 4:
        raise ValueError("only %d byte(s) arrived, not even a length" % len(raw))
    n, = struct.unpack("<I", raw[:4])
    if n > REQUEST_MAX:
        raise ValueError("frame of %d bytes exceeds %d" % (n, REQUEST_MAX))
    if len(raw) != 4 + n:
        raise ValueError("length says %d bytes but %d followed" % (n, len(raw) - 4))
    text = raw[4:]
    if raw == grow_request(text[1:]) and 2 <= len(text) and all(0x20 <= b <= 0x7E for b in text[1:]):
        return "grow", text[1:].decode("ascii")
    if 1 <= len(text) <= REQUEST_MAX and all(0x20 <= b <= 0x7E for b in text):
        return "question", text.decode("ascii")
    raise ValueError("request text is neither a question nor a grow request: %r" % text[:32])


def read_record(path):
    try:
        lines = [l for l in open(path).read().splitlines() if l.strip()]
    except OSError as exc:
        return None, ["no broker record: %s" % exc]
    entries = []
    problems = []
    for i, line in enumerate(lines):
        try:
            entries.append(json.loads(line))
        except ValueError as exc:
            problems.append("record line %d is unreadable: %s" % (i + 1, exc))
    return entries, problems


def check_question_entry(i, entry, want):
    problems = []
    try:
        kind, got = judge_request_bytes(bytes.fromhex(entry["request"]))
    except (ValueError, KeyError) as exc:
        return ["connection %d: bytes are not a valid request frame: %s" % (i, exc)]
    if (kind, got) != ("question", want):
        problems.append("connection %d: the guest sent %s %r, want the question %r" % (i, kind, got, want))
    if entry.get("error") is not None:
        problems.append("connection %d: the broker reports an error: %s" % (i, entry["error"]))
    if entry.get("answer") != CANNED.get(want, "mock: no canned answer for: " + want):
        problems.append("connection %d: the mock answered %r" % (i, entry.get("answer")))
    return problems


def check_grow_entry(i, entry, want, source, calls, rehearsals, answer_kind, answer_frame=None,
                     answer=None, name=None):
    """One grow connection judged: the raw bytes by GERMLINE.md, then every
    record field the test states, GLASS.md's abi and name included."""
    problems = []
    try:
        kind, got = judge_request_bytes(bytes.fromhex(entry["request"]))
    except (ValueError, KeyError) as exc:
        return ["connection %d: bytes are not a valid request frame: %s" % (i, exc)]
    if (kind, got) != ("grow", want):
        problems.append("connection %d: the guest sent %s %r, want the grow request %r" % (i, kind, got, want))
    if bytes.fromhex(entry["request"]) != grow_request(want.encode()):
        problems.append("connection %d: raw bytes %s are not GERMLINE.md's frame for %r" % (i, entry["request"], want))
    fields = {"kind": "grow", "error": None, "text": want, "key": germline_key(want), "source": source,
              "generation_calls": calls, "rehearsals": rehearsals, "answer_kind": answer_kind,
              "abi": ABI, "name": name}
    for k, v in fields.items():
        if entry.get(k) != v:
            problems.append("connection %d: %s is %r, want %r" % (i, k, entry.get(k), v))
    if answer_frame is not None:
        want_sha = hashlib.sha256(answer_frame).hexdigest()
        if entry.get("answer_sha256") != want_sha:
            problems.append("connection %d: answer_sha256 is %r, but the frame GLASS.md gives for it hashes to %s (%d bytes)"
                            % (i, entry.get("answer_sha256"), want_sha, len(answer_frame)))
    if answer is not None and entry.get("answer") != answer:
        problems.append("connection %d: answer is %r, want %r" % (i, entry.get("answer"), answer))
    return problems


# ------------------------------------------------------------ the germline --

def check_germline_entry(root, want, blob, name, choices, model="mock"):
    """The directory for `want` holds the blob and a provenance record that
    tells the truth about it (GERMLINE.md and GLASS.md, "The germline")."""
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
        problems.append("entry %s: rehearsal.log does not hold the twin's sixteen S6: lines" % key)
    if "ERR:" in rlog:
        problems.append("entry %s: rehearsal.log carries an ERR: line" % key)
    return problems


def germline_entries(root):
    try:
        return sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    except OSError:
        return []


def fixture_self_check(name):
    """The frozen source reproduces the frozen binary, byte for byte -
    assembled to stage6/out/, never over the committed file."""
    src = os.path.join(FIXTURES, name + ".asm")
    binary = os.path.join(FIXTURES, name + ".bin")
    check = os.path.join(OUT, name + ".check.bin")
    try:
        r = subprocess.run(["nasm", "-f", "bin", src, "-o", check], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, ["could not assemble %s: %s" % (name, exc)]
    if r.returncode != 0:
        return None, ["%s does not assemble: %s" % (name, r.stderr.strip()[:200])]
    blob = open(binary, "rb").read()
    if open(check, "rb").read() != blob:
        return None, ["stage6/%s.asm does not reproduce stage6/%s.bin byte for byte" % (name, name)]
    if not 16 <= len(blob) <= BLOB_MAX:
        return None, ["%s is %d bytes" % (name, len(blob))]
    try:
        parse_response(app_frame(blob, name.encode())[4:])
    except ValueError as exc:
        return None, ["%s is not a legal app: %s" % (name, exc)]
    return blob, []


# ------------------------------------------------------------ the notebook --

def parse_notebook(data):
    if data[0:8] != b"NOTEBOOK":
        raise ValueError("sector 0 bytes 0-7 are %r, not the NOTEBOOK magic" % data[0:8])
    version, sector, first, length = struct.unpack_from("<IIQQ", data, 8)
    if version != 1 or sector != SECTOR or first != 1:
        raise ValueError("bad header (version %d, sector %d, first %d)" % (version, sector, first))
    if length != len(data) // SECTOR - 1:
        raise ValueError("header journal length is %d, want %d" % (length, len(data) // SECTOR - 1))
    if any(data[0x20:SECTOR]):
        raise ValueError("header padding is not all zero")
    notes = []
    for n in range(1, len(data) // SECTOR):
        rec = data[n * SECTOR:(n + 1) * SECTOR]
        if rec[0:4] != b"NOTE":
            break
        seq, ln, res = struct.unpack_from("<IHH", rec, 4)
        if seq != n or not 1 <= ln <= 500 or res != 0:
            break
        text = rec[12:12 + ln]
        if any(b < 0x20 or b > 0x7E for b in text) or any(rec[12 + ln:]):
            break
        notes.append(text.decode("ascii"))
    return notes


def check_image(path, want):
    try:
        data = open(path, "rb").read()
    except OSError as exc:
        return ["cannot read the notebook image: %s" % exc]
    if len(data) != DISK_BYTES:
        return ["the image is %d bytes, but the harness made it %d" % (len(data), DISK_BYTES)]
    try:
        notes = parse_notebook(data)
    except ValueError as exc:
        return ["the image is not a notebook: %s" % exc]
    problems = []
    if notes != want:
        problems.append("the notebook holds %r, want %r" % (notes, want))
    nxt = (len(want) + 1) * SECTOR
    if data[nxt:nxt + 4] == b"NOTE":
        problems.append("sector %d begins a record - something beyond %r was journaled" % (len(want) + 1, want))
    return problems


# ---------------------------------------------------------------- the mock --

def port_state(port):
    s = socket.socket()
    s.settimeout(1.0)
    try:
        return "open" if s.connect_ex(("127.0.0.1", port)) == 0 else "closed"
    finally:
        s.close()


def start_mock(record_path):
    """Start glass.py --mock with a wiped germline, the gate's image as
    the twin's, its record file; wait for its listening line."""
    for port in (BROKER_PORT, REHEARSAL_PORT):
        if port_state(port) == "open":
            return None, ("something is already listening on 127.0.0.1:%d - the gate talks only "
                          "to its own mock and its own twin; stop it first" % port)
    for path in (GERMLINE, REHEARSAL):
        if os.path.isdir(path):
            shutil.rmtree(path)
    if os.path.exists(record_path):
        os.remove(record_path)
    log = open(os.path.join(OUT, "mock.stderr.txt"), "ab")
    proc = subprocess.Popen(
        [sys.executable, BROKER, "--mock", "--port", str(BROKER_PORT), "--record", record_path,
         "--germline", GERMLINE, "--image", ESP, "--workdir", REHEARSAL,
         "--rehearsal-port", str(REHEARSAL_PORT)],
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


def stop_mock(proc):
    if proc is None:
        return
    if proc.poll() is None:
        proc.send_signal(2)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


# ------------------------------------------------------- the glass's picture -
# The test app's known picture (stage6/app.asm), panel-relative: row,
# column, text - or a run of foreground blocks. The panel line is filled in
# from the geometry of the run; the key from what was typed.

APP_STRIPS = [
    (1, 2, "glass test app"),
    (3, 2, None),                       # "panel <cols>x<rows>"
    (5, 2, "ticks ok"),
    (7, 2, "key: -"),
    (9, 2, "esc exits  tab prompt"),
    (11, 2, bytes([CELL_BLOCK]) * 5),   # five foreground blocks, from fill
]


def app_strips(panel, key):
    _, _, rows, cols = panel
    out = []
    for r, c, text in APP_STRIPS:
        if text is None:
            text = "panel %dx%d" % (cols, rows)
        elif text == "key: -":
            text = "key: " + key
        out.append((r, c, text))
    return out


def expect_cell(font, ch):
    if isinstance(ch, int):
        return cell_pixels(font, ch)
    return render_cell(font, ch)


def check_app_panel(shot, geometry, key):
    """The app panel while the test app runs: its strips at their exact
    cells, and every other cell of the panel blank. Two colours only."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    panel = regions(cols, rows)["app"]
    row0, col0, prows, pcols = panel
    strips = app_strips(panel, key)
    problems = font_self_check(font, "".join(t for _, _, t in strips if isinstance(t, str)))
    if problems:
        return problems
    covered = set()
    for r, c, text in strips:
        for i, ch in enumerate(text):
            sr, sc = row0 + r, col0 + c + i
            if not cell_matches(pixels, width, sr, sc, expect_cell(font, ch)):
                problems.append("app panel row %d, column %d is not %r - %s"
                                % (r, c + i, ch, cell_census(pixels, width, sr, sc)))
                break
            covered.add((r, c + i))
    strays = []
    for r in range(prows):
        for c in range(pcols):
            if (r, c) in covered:
                continue
            if not cell_matches(pixels, width, row0 + r, col0 + c, blank_cell()):
                strays.append((r, c))
    if strays:
        problems.append("%d cell(s) of the app panel outside the app's strips are not blank, the first at panel row %d column %d: %s"
                        % (len(strays), strays[0][0], strays[0][1], cell_census(pixels, width, row0 + strays[0][0], col0 + strays[0][1])))
    stray = check_colour_discipline(pixels, width, height)
    if stray:
        problems.append(stray)
    return problems


def check_app_panel_blank(shot, geometry):
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    panel = regions(cols, rows)["app"]
    if not region_background(shot, panel):
        return ["the app panel is not pure background with no app running"]
    return []


def check_row_text(shot, geometry, region, r, text, label):
    """Row r of a region holds exactly `text` from column 0, blank after."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    row0, col0, nrows, ncols = region
    problems = font_self_check(font, text)
    if problems:
        return problems
    sr = row0 + r
    for c in range(ncols):
        want = render_cell(font, text[c]) if c < len(text) else blank_cell()
        if not cell_matches(pixels, width, sr, col0 + c, want):
            problems.append("%s: column %d is not %r - %s" % (label, c, text[c] if c < len(text) else " ",
                                                                cell_census(pixels, width, sr, col0 + c)))
            break
    return problems


def check_choices(shot, geometry, text):
    """The choices row: row 0 of the region exactly `text`, row 1 blank."""
    regs = regions(geometry[2], geometry[3])
    problems = check_row_text(shot, geometry, regs["choices"], 0, text, "choices row")
    problems += check_row_text(shot, geometry, regs["choices"], 1, "", "choices row, second line")
    return problems


def check_mode_field(shot, geometry, word):
    """The strip's mode field: row 1 of the strip, the first 18 columns."""
    regs = regions(geometry[2], geometry[3])
    row0, col0, _, _ = regs["strip"]
    field = (row0 + 1, col0, 1, 18)
    return check_row_text(shot, geometry, field, 0, word.ljust(18), "mode field")


# ----------------------------------------------------------------- modes ----

def report(title, problems, capture=None):
    if problems:
        say(title + ":")
        for p in problems:
            say("  - " + p)
        if capture is not None:
            dump_capture(capture)
        return False
    return True


def run_one_core():
    """Test 2's third run: -smp 1 - the named error, no glass, and the
    error line on the screen."""
    serial = os.path.join(OUT, "serial.onecore.txt")
    shot = os.path.join(OUT, "screen.onecore.ppm")
    disk = os.path.join(OUT, "serial.onecore.img")
    fresh_disk(disk)
    capture, _, err = drive(1, disk, [("sleep", 1.0), ("shot", shot)], serial,
                            ready=ONE_CORE_ERR.encode(), ready_limit=30.0)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    ok = True
    problems, geometry = check_boot_lines(capture, 1, "formatted", count=14)
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S6: [^\n]*", text)
    if any("glass core" in l or "keyboard ready" in l for l in got):
        problems.append("a glass core or keyboard ready line appeared at -smp 1: %r" % [l for l in got if "glass" in l or "keyboard" in l])
    errs = re.findall(r"ERR: [^\n]*", text)
    if errs != [ONE_CORE_ERR]:
        problems.append("the ERR: lines are %r, want exactly [%r]" % (errs, ONE_CORE_ERR))
    ok &= report("the one-core serial log is not what the spec asks for", problems, capture)
    if not problems:
        say("-smp 1: fourteen S6: lines, then the named error, no glass core, no keyboard")

    if None in geometry:
        say("no picture to judge - the boot lines were wrong")
        return 1
    regs = regions(geometry[2], geometry[3])
    problems = check_region_rows(shot, geometry, regs["conversation"], [ONE_CORE_ERR])
    ok &= report("the error line is not on the screen", problems)
    if not problems:
        say("-smp 1: the error line is on the screen, rendered from the shared font, two colours only")
    say("-smp 1: %s" % ("the machine said why it stopped, on serial and on screen" if ok else "not as the spec asks"))
    return 0 if ok else 1


CHOICES_APP = choices_row(True, 1, TEST_CHOICES)      # "a alpha   b beta   Esc exit   Tab prompt"
CHOICES_PROMPT_APP = choices_row(True, 0, TEST_CHOICES)
CHOICES_NONE = choices_row(False, 0, [])              # "? ask   ! grow"


def run_glass(smp):
    """Test 3 at one -smp value: the glass, mocked."""
    blob, problems = fixture_self_check("app")
    if not report("the test app is not what the repository says", problems):
        return 1
    say("stage6/app.asm reproduces stage6/app.bin: %d bytes, sha256 %s"
        % (len(blob), hashlib.sha256(blob).hexdigest()[:16]))

    record = os.path.join(OUT, "broker.glass.%d.jsonl" % smp)
    serial = os.path.join(OUT, "serial.glass.%d.txt" % smp)
    shots = {k: os.path.join(OUT, "screen.glass.%d.%s.ppm" % (smp, k)) for k in "abc"}
    mock, err = start_mock(record)
    if err:
        say(err)
        return 1
    say("mock broker listening on 127.0.0.1:%d, germline at %s, recording to %s"
        % (BROKER_PORT, os.path.relpath(GERMLINE, REPO), os.path.relpath(record, REPO)))
    try:
        fresh_disk(NOTES)
        steps = [
            ("type", "before\n"), ("sleep", 1.5),
            ("type", "! test app\n"), ("wait_record", record, 1, 150.0), ("sleep", 3.0),
            ("type", "k"), ("sleep", 1.0),
            ("shot", shots["a"]),
            ("type", "\t"), ("sleep", 0.5),
            ("type", "mid\n"), ("sleep", 1.5),
            ("type", "\t"), ("sleep", 0.5),
            ("type", "j"), ("sleep", 1.0),
            ("shot", shots["b"]),
            ("type", "\x1b"), ("sleep", 2.0),
            ("type", "? ping\n"), ("wait_record", record, 2, 20.0), ("sleep", SETTLE),
            ("type", "after\n"), ("sleep", SETTLE),
            ("shot", shots["c"]),
        ]
        capture, _, err = drive(smp, NOTES, steps, serial)
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1

    ok = True
    problems, geometry = check_boot_lines(capture, smp, "formatted")
    problems += check_echo(capture, b"before\r\n! test app\r\nmid\r\n? ping\r\nafter\r\n")
    ok &= report("the serial log is not what the spec asks for", problems, capture)
    if not problems:
        say("sixteen boot lines, nic %s; the wire after ready carries exactly the five typed lines" % MAC)

    entries, problems = read_record(record)
    if entries is not None:
        if len(entries) != 2:
            problems.append("the broker saw %d connection(s), want 2" % len(entries))
        if len(entries) >= 1:
            problems += check_grow_entry(1, entries[0], "test app", "generated", 1, ["pass"], "app",
                                         app_frame(blob, b"test app", TEST_CHOICES, 0), name="test app")
        if len(entries) >= 2:
            problems += check_question_entry(2, entries[1], "ping")
    ok &= report("the broker's record is not what GLASS.md asks for", problems)
    if not problems:
        say("the broker received the grow request byte-exact, generated once, rehearsed once, "
            "and sent the app frame GLASS.md gives for stage6/app.bin; then 'ping'")

    problems = check_germline_entry(GERMLINE, "test app", blob, "test app", TEST_CHOICES)
    names = germline_entries(GERMLINE)
    if len(names) != 1:
        problems.append("the germline holds %d entries %r, want exactly 1" % (len(names), names))
    ok &= report("the germline is not what GLASS.md asks for", problems)
    if not problems:
        say("the germline holds exactly one abi2 entry, the test app with its provenance and rehearsal log")

    problems = check_image(NOTES, ["before", "mid", "after"])
    ok &= report("the notebook is not what it should be", problems)
    if not problems:
        say("the notebook holds exactly 'before', 'mid' and 'after' - the note typed beside the running app journaled")

    if None in geometry:
        say("no picture to judge - the boot lines were wrong")
        return 1
    regs = regions(geometry[2], geometry[3])
    conv = regs["conversation"]

    problems = check_app_panel(shots["a"], geometry, "k")
    problems += check_choices(shots["a"], geometry, CHOICES_APP)
    problems += check_mode_field(shots["a"], geometry, "running test app")
    problems += check_region_rows(shots["a"], geometry, conv, ["> before", "> ! test app", PROMPT])
    ok &= report("screen A does not show the test app running with the keys", problems)
    if not problems:
        say("screen A: the app's strips with 'key: k' and the five blocks, the app's choices row, "
            "'running test app' on the strip, the conversation intact")

    problems = check_app_panel(shots["b"], geometry, "j")
    problems += check_choices(shots["b"], geometry, CHOICES_APP)
    problems += check_region_rows(shots["b"], geometry, conv, ["> before", "> ! test app", "> mid", PROMPT])
    ok &= report("screen B does not show the note beside the running app", problems)
    if not problems:
        say("screen B: '> mid' journaled beside the app, the app then took 'j'")

    problems = check_app_panel_blank(shots["c"], geometry)
    problems += check_choices(shots["c"], geometry, CHOICES_NONE)
    problems += check_mode_field(shots["c"], geometry, "prompt")
    problems += check_region_rows(shots["c"], geometry, conv,
                                  ["> before", "> ! test app", "> mid", "> ? ping", CANNED["ping"], "> after", PROMPT])
    ok &= report("screen C does not show the conversation back after Esc", problems)
    if not problems:
        say("screen C: the app panel blank, the prompt's choices row, 'prompt' on the strip, "
            "'? ping' answered and '> after' with the prompt below")

    say("-smp %d: %s" % (smp, "the glass held - the app ran in its panel, the conversation stayed alive" if ok else "the glass did not hold"))
    return 0 if ok else 1


# --------------------------------------------------------- the truth -------

def check_cage_argv(argv, port, want_mac):
    """A QEMU command inspected for the cage and the display: slirp user
    mode, restrict=on, exactly one guestfwd from 10.0.2.4:9999 delivered by
    nc to 127.0.0.1 on the given port, no hostfwd, no other network option,
    one virtio-net-pci device on n0 (carrying the harness's MAC when one is
    wanted), -vga none and the one standard VGA device with the EDID,
    every drive a file under stage6/out/."""
    problems = []
    netdevs = [argv[i + 1] for i, a in enumerate(argv) if a == "-netdev"]
    devices = [argv[i + 1] for i, a in enumerate(argv) if a == "-device"]
    if len(netdevs) != 1:
        problems.append("expected exactly one -netdev, found %d" % len(netdevs))
    for nd in netdevs:
        if not nd.startswith("user,"):
            problems.append("the netdev is not slirp's user mode: %r" % nd)
        if "restrict=on" not in nd.split(","):
            problems.append("the netdev lacks restrict=on: %r" % nd)
        if nd.count("guestfwd=") != 1:
            problems.append("expected exactly one guestfwd, found %d in %r" % (nd.count("guestfwd="), nd))
        if not re.search(r"guestfwd=tcp:10\.0\.2\.4:9999-cmd:nc -N 127\.0\.0\.1 %d(,|$)" % port, nd):
            problems.append("the guestfwd is not tcp:10.0.2.4:9999 delivered by 'nc -N 127.0.0.1 %d': %r" % (port, nd))
        if "hostfwd" in nd:
            problems.append("the netdev opens a hostfwd: %r" % nd)
    for flag in ("-nic", "-net", "-netdev-add"):
        if flag in argv:
            problems.append("the command carries %s" % flag)
    nics = [d for d in devices if d.startswith("virtio-net-pci")]
    vgas = [d for d in devices if d.startswith("VGA")]
    if len(nics) != 1 or len(vgas) != 1 or len(devices) != 2:
        problems.append("expected exactly two -device options, a virtio-net-pci and the VGA, found %r" % devices)
    for d in nics:
        if "netdev=n0" not in d.split(","):
            problems.append("the NIC is not attached to netdev n0: %r" % d)
        if want_mac and ("mac=" + want_mac) not in d.split(","):
            problems.append("the NIC does not carry the harness's MAC %s: %r" % (want_mac, d))
    for d in vgas:
        if d != DISPLAY_EDID[3]:
            problems.append("the display is not %r: %r" % (DISPLAY_EDID[3], d))
    vga = [argv[i + 1] for i, a in enumerate(argv) if a == "-vga"]
    if vga != ["none"]:
        problems.append("the command does not carry -vga none: %r" % vga)
    drives = [argv[i + 1] for i, a in enumerate(argv) if a == "-drive"]
    for dr in drives:
        m = re.search(r"(?:^|,)file=([^,]*)", dr)
        if not m or not m.group(1).startswith(OUT + os.sep):
            problems.append("a drive is not a file under stage6/out/: %r" % dr)
    return problems


def read_cells(shot, geometry, region, r):
    """Row r of a region, read back cell by cell: a glyph, a block (0x01)
    or a blank, "?" for anything else. The checker's own reading of what
    the glass drew, matched against every glyph of the shared font."""
    width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    row0, col0, nrows, ncols = region
    glyphs = [(chr(v), render_cell(font, chr(v))) for v in range(0x21, 0x7F)]
    out = []
    for c in range(ncols):
        sr, sc = row0 + r, col0 + c
        if cell_matches(pixels, width, sr, sc, blank_cell()):
            out.append(" ")
            continue
        if cell_matches(pixels, width, sr, sc, cursor_cell()):
            out.append("\x01")
            continue
        for ch, want in glyphs:
            if cell_matches(pixels, width, sr, sc, want):
                out.append(ch)
                break
        else:
            out.append("?")
    return "".join(out)


STRIP0 = re.compile(r"up (\d{6}) core (\d{2}) fr (\d{6}) (\d\d\.\d)/(\d\d\.\d) ph (\d\d\.\d)/(\d\d\.\d) "
                    r"k (\d{4}) hw (\d{3}) err (\d{3}) step (\d\d\.\d)/(\d\d\.\d)")


def check_strip(shot, geometry, obs1, obs2, label):
    """The strip on the screen against the obs page read just before and
    just after the screendump: the static fields equal, the moving ones -
    uptime, frames, the worst times - between the two readings, the last
    times well formed. Rendered from the page by GLASS.md's own function."""
    regs = regions(geometry[2], geometry[3])
    strip = regs["strip"]
    try:
        got0 = read_cells(shot, geometry, strip, 0).rstrip()
        got1 = read_cells(shot, geometry, strip, 1).rstrip()
    except (OSError, ValueError) as exc:
        return [str(exc)]
    want1a, want1b = strip_rows(obs1, obs1["now"])
    want2a, want2b = strip_rows(obs2, obs2["now"])
    problems = []
    if want1b != want2b:
        problems.append("%s: the strip's second row changed between the two page reads (%r -> %r) though nothing happened" % (label, want1b, want2b))
    if got1 != want1b.rstrip():
        problems.append("%s: the strip's second row is %r, but the obs page renders %r" % (label, got1, want1b.rstrip()))
    m = STRIP0.fullmatch(got0)
    m1 = STRIP0.fullmatch(want1a)
    m2 = STRIP0.fullmatch(want2a)
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
            pass   # any well-formed time: it changes every frame
        elif g != a or a != b:
            problems.append("%s: the strip's %s is %s, the page says %s then %s" % (label, name, g, a, b))
    return problems


def check_surfaces(shot, reads, label, which=("choices", "conversation", "app")):
    """Every named region of the screen is what its surface says."""
    problems = []
    try:
        font = load_font()
        obs = reads["obs"]
        for name in which:
            at = surface_mismatch(shot, obs[name], reads[name], font)
            if at is not None:
                problems.append("%s: the %s region's cell %r is not what its surface says" % (label, name, at))
    except (OSError, ValueError, KeyError) as exc:
        problems.append("%s: cannot compare the surfaces with the screen: %s" % (label, exc))
    return problems


def check_counts(obs, want, label):
    problems = []
    for k, v in want.items():
        if obs.get(k) != v:
            problems.append("%s: the obs page's %s is %r, want %r" % (label, k, obs.get(k), v))
    return problems


REFUSAL_FAULT = "rehearsal failed: the twin reported an error"
REFUSAL_HOG = "rehearsal failed: the app missed its budget"
REFUSAL_ESCAPEE = "rehearsal failed: the app drew outside its panel"
REFUSAL_HOLD = "mock: held"
REFUSAL_X = "mock: no canned component for: x"
ANSWER_X = "mock: no canned answer for: x"


def run_truth():
    """Test 4: the truth on the strip, at -smp 8."""
    smp = 8
    argv = qemu_argv(smp, NOTES, os.path.join(OUT, "x"))
    problems = check_cage_argv(argv, BROKER_PORT, MAC)
    if twin.VGA_ARGS != DISPLAY_EDID:
        problems.append("the twin's display flags %r are not the harness's %r" % (twin.VGA_ARGS, DISPLAY_EDID))
    if not report("the harness's own QEMU command is not the cage with the display", problems):
        return 1
    say("the checker's QEMU command carries restrict=on, the single guestfwd to 10.0.2.4:9999 via nc to 127.0.0.1:%d, and the VGA device with the EDID" % BROKER_PORT)

    rargv = twin.qemu_argv(ESP, os.path.join(REHEARSAL, "notes.img"), os.path.join(REHEARSAL, "serial.txt"), REHEARSAL_PORT)
    problems = check_cage_argv(rargv, REHEARSAL_PORT, None)
    if twin.DEFAULT_PORT != REHEARSAL_PORT:
        problems.append("the twin's default port is %d, not %d" % (twin.DEFAULT_PORT, REHEARSAL_PORT))
    if not report("the twin's QEMU command is not the cage with the display", problems):
        return 1
    say("the twin's QEMU command carries the same cage and display, its guestfwd via nc to 127.0.0.1:%d" % REHEARSAL_PORT)

    blobs = {}
    for name in ("app", "hog", "escapee"):
        blob, problems = fixture_self_check(name)
        if not report("the %s fixture is not what the repository says" % name, problems):
            return 1
        blobs[name] = blob
    app = blobs["app"]
    big = app + bytes(CAP - len(app))

    record = os.path.join(OUT, "broker.truth.jsonl")
    serial = os.path.join(OUT, "serial.truth.txt")
    shots = {k: os.path.join(OUT, "screen.truth.%s.ppm" % k) for k in ("a", "a2", "b", "h", "d")}
    mock, err = start_mock(record)
    if err:
        say(err)
        return 1
    say("mock broker listening on 127.0.0.1:%d, germline wiped at %s" % (BROKER_PORT, os.path.relpath(GERMLINE, REPO)))
    try:
        fresh_disk(NOTES)
        steps = [
            ("type", "! fault\n"), ("wait_record", record, 1, 240.0), ("sleep", SETTLE),
            ("type", "! hog\n"), ("wait_record", record, 2, 240.0), ("sleep", SETTLE),
            ("type", "! escapee\n"), ("wait_record", record, 3, 240.0), ("sleep", SETTLE),
            ("type", "! test app\n"), ("wait_record", record, 4, 150.0), ("sleep", 3.0),
            ("type", "key"), ("sleep", 1.0),
            ("surfaces", "a"), ("shot", shots["a"]), ("obs", "a2"),
            ("sleep", 1.0),
            ("obs", "a3"), ("shot", shots["a2"]),
            ("type", "\x1b"), ("sleep", 2.0),
            ("type", "! test app\n"), ("wait_record", record, 5, 20.0), ("sleep", 3.0),
            ("type", "\x1b"), ("sleep", 2.0),
            ("type", "! big\n"), ("wait_record", record, 6, 150.0), ("sleep", 3.0),
            ("shot", shots["b"]),
            ("type", "\x1b"), ("sleep", 2.0),
            ("type", "! hold\n"), ("sleep", 3.0),
            ("obs", "h"), ("shot", shots["h"]),
            ("wait_record", record, 7, 20.0), ("sleep", SETTLE),
            ("type", "?\n"), ("sleep", 1.5),
            ("type", "?x\n"), ("wait_record", record, 8, 20.0), ("sleep", SETTLE),
            ("type", "!\n"), ("sleep", 1.5),
            ("type", "!x\n"), ("wait_record", record, 9, 20.0), ("sleep", SETTLE),
            ("type", "last\n"), ("sleep", 1.5),
            ("surfaces", "d"), ("shot", shots["d"]), ("obs", "d2"),
        ]
        capture, reads, err = drive(smp, NOTES, steps, serial)
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    keys_typed = sum(len(s[1]) for s in steps if s[0] == "type")

    ok = True
    problems, geometry = check_boot_lines(capture, smp, "formatted")
    problems += check_echo(capture, b"! fault\r\n! hog\r\n! escapee\r\n! test app\r\n! test app\r\n! big\r\n"
                                    b"! hold\r\n?\r\n?x\r\n!\r\n!x\r\nlast\r\n")
    ok &= report("the serial log is not what the spec asks for", problems, capture)
    if not problems:
        say("sixteen boot lines; the wire after ready carries exactly the twelve typed lines")

    entries, problems = read_record(record)
    if entries is not None:
        if len(entries) != 9:
            problems.append("the broker saw %d connection(s), want 9" % len(entries))
        checks = [
            lambda e: check_grow_entry(1, e, "fault", "refused", 2, ["fail: the twin reported an error"] * 2,
                                       "refusal", refusal_frame(REFUSAL_FAULT.encode()), REFUSAL_FAULT),
            lambda e: check_grow_entry(2, e, "hog", "refused", 4, ["fail: the app missed its budget"] * 2,
                                       "refusal", refusal_frame(REFUSAL_HOG.encode()), REFUSAL_HOG),
            lambda e: check_grow_entry(3, e, "escapee", "refused", 6, ["fail: the app drew outside its panel"] * 2,
                                       "refusal", refusal_frame(REFUSAL_ESCAPEE.encode()), REFUSAL_ESCAPEE),
            lambda e: check_grow_entry(4, e, "test app", "generated", 7, ["pass"], "app",
                                       app_frame(app, b"test app", TEST_CHOICES, 0), name="test app"),
            lambda e: check_grow_entry(5, e, "test app", "germline", 7, [], "app",
                                       app_frame(app, b"test app", TEST_CHOICES, 1), name="test app"),
            lambda e: check_grow_entry(6, e, "big", "generated", 8, ["pass"], "app",
                                       app_frame(big, b"big", TEST_CHOICES, 0), name="big"),
            lambda e: check_grow_entry(7, e, "hold", "refused", 9, [], "refusal",
                                       refusal_frame(REFUSAL_HOLD.encode()), REFUSAL_HOLD),
            lambda e: check_question_entry(8, e, "x"),
            lambda e: check_grow_entry(9, e, "x", "refused", 10, [], "refusal",
                                       refusal_frame(REFUSAL_X.encode()), REFUSAL_X),
        ]
        for check, entry in zip(checks, entries):
            problems += check(entry)
    ok &= report("the broker's record is not what GLASS.md asks for", problems)
    if not problems:
        say("the record: fault, hog and escapee each refused after two failed rehearsals with their phrases "
            "(calls 2, 4, 6); test app generated (7) then served from the germline (still 7, source 1); "
            "big generated (8) as a frame of exactly %d bytes; hold held then refused (9); x asked, then refused (10)"
            % len(app_frame(big, b"big", TEST_CHOICES, 0)))

    problems = check_germline_entry(GERMLINE, "test app", app, "test app", TEST_CHOICES)
    problems += check_germline_entry(GERMLINE, "big", big, "big", TEST_CHOICES)
    names = germline_entries(GERMLINE)
    if len(names) != 2:
        problems.append("the germline holds %d entries %r, want exactly 2" % (len(names), names))
    ok &= report("the germline is not what GLASS.md asks for", problems)
    if not problems:
        say("the germline holds exactly two abi2 entries - the test app and its 1 MB twin - each with provenance and a rehearsal log")

    problems = check_image(NOTES, ["last"])
    ok &= report("the notebook is not what it should be", problems)
    if not problems:
        say("the notebook holds exactly 'last' - no request, question or bare marker was journaled")

    if None in geometry:
        say("no picture to judge - the boot lines were wrong")
        return 1
    regs = regions(geometry[2], geometry[3])
    conv = regs["conversation"]

    # Screen A: the test app running after "key"; the strip against the page.
    problems = []
    if "a" not in reads or "a2" not in reads or "a3" not in reads:
        problems.append("the obs page or the surfaces could not be read around screen A")
    else:
        problems += check_app_panel(shots["a"], geometry, "y")
        problems += check_choices(shots["a"], geometry, CHOICES_APP)
        problems += check_strip(shots["a"], geometry, reads["a"]["obs"], reads["a2"], "screen A")
        problems += check_surfaces(shots["a"], reads["a"], "screen A")
        keys_so_far = sum(len(s[1]) for s in steps[:steps.index(("surfaces", "a"))] if s[0] == "type")
        problems += check_counts(reads["a"]["obs"], {"mode": 3, "name": "test app", "focus": 1, "keys": keys_so_far,
                                                    "questions": 0, "requests": 4, "notes": 0, "errors": 3,
                                                    "grows_generated": 1, "grows_served": 0, "wire_conns": 4,
                                                    "cols": geometry[2], "rows": geometry[3]}, "screen A")
        o1, o2 = reads["a2"], reads["a3"]
        if not o2["frames"] > o1["frames"]:
            problems.append("frames did not increase across a second: %d then %d" % (o1["frames"], o2["frames"]))
        if o1["steps"] < 1 or o1["step_worst"] > 50 * o1["tsc_per_ms"]:
            problems.append("the test app's steps are %d with a worst of %.1f ms" % (o1["steps"], o1["step_worst"] / o1["tsc_per_ms"]))
        problems += check_region_rows(shots["a2"], geometry, conv,
                                      ["> ! fault", REFUSAL_FAULT, "> ! hog", REFUSAL_HOG, "> ! escapee", REFUSAL_ESCAPEE,
                                       "> ! test app", PROMPT])
    ok &= report("screen A is not the truth", problems)
    if not problems:
        say("screen A: the test app with 'key: y'; the strip agrees with the obs page read before and after it, "
            "its counts are the checker's; every region outside the app matches its surface; frames %d -> %d a second later"
            % (reads["a2"]["frames"], reads["a3"]["frames"]))

    problems = check_app_panel(shots["b"], geometry, "-")
    problems += check_choices(shots["b"], geometry, choices_row(True, 1, TEST_CHOICES))
    problems += check_mode_field(shots["b"], geometry, "running big")
    ok &= report("screen B does not show the 1 MB app running", problems)
    if not problems:
        say("screen B: the 1 MB app's strips with 'key: -', 'running big' on the strip - the padding never reached")

    problems = []
    if "h" not in reads:
        problems.append("the obs page could not be read during the hold")
    else:
        problems += check_counts(reads["h"], {"mode": 2, "focus": 0}, "the hold")
        problems += check_mode_field(shots["h"], geometry, "growing")
        problems += check_choices(shots["h"], geometry, CHOICES_NONE)
        problems += check_app_panel_blank(shots["h"], geometry)
    ok &= report("the hold does not show 'growing'", problems)
    if not problems:
        say("during the hold: 'growing' on the strip and in the page, the prompt's choices row, the app panel blank")

    problems = []
    if "d" not in reads or "d2" not in reads:
        problems.append("the obs page or the surfaces could not be read at the end")
    else:
        problems += check_strip(shots["d"], geometry, reads["d"]["obs"], reads["d2"], "screen D")
        problems += check_surfaces(shots["d"], reads["d"], "screen D")
        problems += check_counts(reads["d"]["obs"], {"mode": 0, "name": "", "focus": 0, "keys": keys_typed,
                                                    "questions": 1, "requests": 8, "notes": 1, "errors": 7,
                                                    "grows_generated": 2, "grows_served": 1, "wire_conns": 9},
                                 "screen D")
        problems += check_mode_field(shots["d"], geometry, "prompt")
        problems += check_choices(shots["d"], geometry, CHOICES_NONE)
        problems += check_app_panel_blank(shots["d"], geometry)
        problems += check_region_rows(shots["d"], geometry, conv, [
            "> ! fault", REFUSAL_FAULT,
            "> ! hog", REFUSAL_HOG,
            "> ! escapee", REFUSAL_ESCAPEE,
            "> ! test app", "> ! test app", "> ! big",
            "> ! hold", REFUSAL_HOLD,
            "> ?", "nothing to ask",
            "> ?x", ANSWER_X,
            "> !", "nothing to grow",
            "> !x", REFUSAL_X,
            "> last", PROMPT])
    ok &= report("screen D is not the truth", problems)
    if not problems:
        say("screen D: the strip says k %04d q 001 n 001 g 002/001 err 007 and the obs page agrees; every region "
            "matches its surface; the whole conversation with the refusals and the marker lines, two colours only" % keys_typed)

    say("the truth: %s" % ("told - the strip is the obs page, the page is what happened" if ok else "not told"))
    return 0 if ok else 1


def main(argv):
    if argv == ["--one-core"]:
        return run_one_core()
    if argv == ["--truth"]:
        return run_truth()
    if len(argv) == 2 and argv[0] == "--glass":
        try:
            return run_glass(int(argv[1]))
        except ValueError:
            pass
    say("usage: checkglass.py --one-core | --glass <smp> | --truth")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
