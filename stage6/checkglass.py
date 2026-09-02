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


def main(argv):
    if argv == ["--one-core"]:
        return run_one_core()
    say("usage: checkglass.py --one-core | --glass <smp> | --truth")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
