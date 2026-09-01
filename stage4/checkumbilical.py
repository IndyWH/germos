#!/usr/bin/env python3
"""Stage 4 acceptance tests 3 and 4 - the question round trip, and the cage.

One driver owns every booted run bar test 2's, as Stage 3's checknotes.py
did: boot stage4/out/esp.img headless under OVMF with a fresh 16 MB raw
notebook image as a virtio disk and the caged network of stage4/UMBILICAL.md
- slirp with restrict=on and one guestfwd, delivered per connection by netcat
to the broker on 127.0.0.1:9999 - the QEMU monitor on stdio and serial to a
file; wait for the guest itself to say "S4: keyboard ready"; type from
OUTSIDE via the monitor's sendkey; screendump; quit. Then judge the broker's
record by UMBILICAL.md's own frame rule, the disk image by NOTEBOOK.md, the
serial capture byte for byte, and the screen pixel by pixel from the shared
font.

Two modes, two acceptance tests:

  --question <smp>  Test 3. Start the MOCK broker (broker/broker.py --mock,
                    which calls nothing) with a record file; boot; type
                    "? ping" Enter, wait for the record to show the request;
                    type "keep this" Enter; type "? hello" Enter, wait for the
                    second request; screendump; quit; stop the mock. Assert:
                    the twelve boot lines with the harness's MAC; the echo
                    after "S4: keyboard ready" EXACTLY the three typed lines
                    with their CRLFs and nothing else; the record holding
                    exactly two connections whose raw bytes ARE the frames
                    for "ping" and "hello"; the image holding exactly the note
                    "keep this" and nothing for the questions; and the screen
                    showing "> ? ping", "pong", "> keep this", "> ? hello",
                    the mock's two-line hello answer, and "> " with the block
                    cursor, on seven consecutive rows, in the two console
                    colours only.

  --cage            Test 4. First the harness inspects its OWN QEMU command:
                    exactly one -netdev, of type user, with restrict=on and
                    exactly one guestfwd to tcp:10.0.2.4:9999 delivered by
                    "cmd:nc -N 127.0.0.1 9999", no hostfwd, no -nic, no -net,
                    one virtio-net-pci device. Then the mock-down run: with
                    NOTHING listening on the broker's port (checked - the
                    checker must never be the thing that talks to a real
                    broker), boot, type "? ping" Enter, wait a fixed 6 s, type
                    "still here" Enter, screendump, quit. Assert the twelve
                    lines, the echo exactly the two typed lines, the image
                    holding exactly "still here", and the screen showing
                    "> ? ping", "no answer from the broker", "> still here",
                    and the prompt. The 6 s is a timing assertion: a guest
                    still waiting would have discarded the note.

Pure standard library on purpose. Everything runs inside QEMU with exactly
two drives, both raw image files under stage4/out/, both created here, and
the broker (mock or absent) on 127.0.0.1 only. No real disk is touched; no
Claude call is ever made.

This file is frozen acceptance machinery from plan item 7. See the header of
stage4/test.sh.

Exit 0 on pass, 1 otherwise.
"""

import json
import os
import re
import select
import socket
import struct
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "stage4", "out")
ESP = os.path.join(OUT, "esp.img")
NOTES = os.path.join(OUT, "notes.img")
FONT = os.path.join(REPO, "stage2", "font8x8.bin")
BROKER = os.path.join(REPO, "broker", "broker.py")
OVMF = "/usr/share/ovmf/OVMF.fd"

DISK_BYTES = 16 * 1024 * 1024
SECTOR = 512

# The cage, exactly as stage4/UMBILICAL.md spells it, with the harness's MAC.
BROKER_PORT = 9999
MAC = "52:54:00:a1:04:01"
CAGE_NETDEV = ("user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:%d-cmd:nc -N 127.0.0.1 %d"
               % (BROKER_PORT, BROKER_PORT))
CAGE_DEVICE = "virtio-net-pci,netdev=n0,mac=" + MAC

READY = b"S4: keyboard ready"
NO_ANSWER = "no answer from the broker"

# UMBILICAL.md, "The mock's canned table" - what must be on the screen.
CANNED = {
    "ping": "pong",
    "hello": "hello from the mock broker\nask me something true at test 5",
}

KEY_GAP = 0.2        # seconds between keys - a monitor can outrun a guest
SETTLE = 2.0         # seconds after an answer is known to have arrived

INDENT = "    "


def say(msg):
    print(INDENT + msg)


# ---------------------------------------------------------------- the wire --
# stage4/UMBILICAL.md, "Parsing it cold, in Python", applied to recorded bytes.

REQUEST_MAX, RESPONSE_MAX = 498, 4096


def judge_request_bytes(raw):
    """The recorded bytes of one connection, judged by the frame rule alone.
    Returns the request text, or raises ValueError naming what was wrong."""
    if len(raw) < 4:
        raise ValueError("only %d byte(s) arrived, not even a length" % len(raw))
    n, = struct.unpack("<I", raw[:4])
    if n > REQUEST_MAX:
        raise ValueError("frame of %d bytes exceeds %d" % (n, REQUEST_MAX))
    if len(raw) != 4 + n:
        raise ValueError("length says %d bytes but %d followed" % (n, len(raw) - 4))
    text = raw[4:]
    if not (1 <= len(text) <= REQUEST_MAX and all(0x20 <= b <= 0x7E for b in text)):
        raise ValueError("request text is not 1-498 printable ASCII bytes: %r" % text)
    return text.decode("ascii")


def check_record(path, expected):
    """Exactly len(expected) connections, each carrying exactly the frame for
    the expected question, answered from the canned table."""
    problems = []
    try:
        lines = [l for l in open(path).read().splitlines() if l.strip()]
    except OSError as exc:
        return ["no broker record: %s" % exc]
    if len(lines) != len(expected):
        problems.append("the broker saw %d connection(s), want %d" % (len(lines), len(expected)))
    for i, (line, want) in enumerate(zip(lines, expected)):
        try:
            entry = json.loads(line)
            raw = bytes.fromhex(entry["request"])
        except (ValueError, KeyError) as exc:
            problems.append("record line %d is unreadable: %s" % (i + 1, exc))
            continue
        try:
            got = judge_request_bytes(raw)
        except ValueError as exc:
            problems.append("connection %d: bytes %s are not a valid request frame: %s"
                            % (i + 1, raw.hex(), exc))
            continue
        if got != want:
            problems.append("connection %d: the guest sent %r, want %r" % (i + 1, got, want))
        if entry.get("error") is not None:
            problems.append("connection %d: the broker reports an error: %s" % (i + 1, entry["error"]))
        if entry.get("answer") != CANNED[want]:
            problems.append("connection %d: the mock answered %r, want %r"
                            % (i + 1, entry.get("answer"), CANNED[want]))
    return problems


# ------------------------------------------------------------ the notebook --
# stage3/NOTEBOOK.md's parser, verbatim: the notebook must be exactly what
# Stage 3 left it, questions and all.

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
    """The notebook holds exactly `want`, and the sector after the last note
    does not even begin a record."""
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
        problems.append("sector %d begins a record - something beyond %r was journaled"
                        % (len(want) + 1, want))
    return problems


# ---------------------------------------------------------------- the mock --

def port_state(port):
    """'open' if something accepts on 127.0.0.1:port, else 'closed'."""
    s = socket.socket()
    s.settimeout(1.0)
    try:
        return "open" if s.connect_ex(("127.0.0.1", port)) == 0 else "closed"
    finally:
        s.close()


def start_mock(record_path):
    """Start broker.py --mock with a record file; wait for its listening
    line. Returns (proc, error)."""
    if port_state(BROKER_PORT) == "open":
        return None, ("something is already listening on 127.0.0.1:%d - the gate talks only "
                      "to its own mock; stop the real broker first" % BROKER_PORT)
    if os.path.exists(record_path):
        os.remove(record_path)
    log = open(os.path.join(OUT, "mock.stderr.txt"), "ab")
    proc = subprocess.Popen(
        [sys.executable, BROKER, "--mock", "--port", str(BROKER_PORT), "--record", record_path],
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


def record_count(path):
    try:
        return len([l for l in open(path).read().splitlines() if l.strip()])
    except OSError:
        return 0


# ---------------------------------------------------------------- driver ----

def fresh_disk(path):
    if os.path.exists(path):
        os.remove(path)
    with open(path, "wb") as fh:
        fh.truncate(DISK_BYTES)


def qemu_argv(smp, disk, serial_path):
    """The one place the QEMU command is spelled. Test 4 inspects this."""
    return [
        "qemu-system-x86_64",
        "-machine", "q35",
        "-m", "256M",
        "-smp", str(smp),
        "-bios", OVMF,
        "-drive", "format=raw,file=" + ESP,
        "-drive", "format=raw,file=" + disk + ",if=virtio",
        "-netdev", CAGE_NETDEV,
        "-device", CAGE_DEVICE,
        "-display", "none",
        "-serial", "file:" + serial_path,
        "-monitor", "stdio",
    ]


# The keys, as the QEMU monitor names them. Only what the tests type.
KEYNAMES = {" ": "spc", "?": "shift-slash", "\n": "ret"}


def keyname(ch):
    if ch in KEYNAMES:
        return KEYNAMES[ch]
    if ch.islower() and ch.isalpha():
        return ch
    raise ValueError("no monitor key name for %r" % ch)


def drive(smp, disk, steps, serial_path, shot_path):
    """Boot inside the cage, wait for the guest's own ready line, run the
    steps - ("type", text), ("sleep", seconds), ("wait_record", path, count,
    timeout) - screendump if asked, quit, reap. Returns (serial_bytes,
    error). Never leaves a QEMU running behind us."""
    if not os.path.isfile(ESP):
        return b"", "no image was built"
    if not os.path.isfile(OVMF):
        return b"", "OVMF firmware not found at " + OVMF
    for path in (serial_path, shot_path):
        if path and os.path.exists(path):
            os.remove(path)

    proc = subprocess.Popen(qemu_argv(smp, disk, serial_path),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def tell(line):
        try:
            proc.stdin.write(line)
            proc.stdin.flush()
        except (BrokenPipeError, ValueError, OSError):
            pass

    def serial_bytes():
        try:
            with open(serial_path, "rb") as fh:
                return fh.read()
        except OSError:
            return b""

    err = None
    try:
        deadline = time.time() + 60.0
        ready = False
        while time.time() < deadline:
            time.sleep(0.25)
            if proc.poll() is not None:
                break
            if READY in serial_bytes():
                ready = True
                break
        if not ready:
            err = "the guest never printed 'S4: keyboard ready' within 60s"
            if proc.poll() is not None:
                err += " (qemu exited %d: %s)" % (proc.returncode,
                                                 proc.stderr.read().decode(errors="replace").strip()[:300])
        else:
            time.sleep(1.0)  # let the guest finish its replay, prompt and sti
            for step in steps:
                if step[0] == "type":
                    for ch in step[1]:
                        tell(b"sendkey " + keyname(ch).encode() + b"\n")
                        time.sleep(KEY_GAP)
                elif step[0] == "sleep":
                    time.sleep(step[1])
                elif step[0] == "wait_record":
                    _, path, count, limit = step
                    until = time.time() + limit
                    while time.time() < until and record_count(path) < count:
                        time.sleep(0.2)
                    if record_count(path) < count:
                        say("(the broker record did not reach %d connection(s) within %.0fs)" % (count, limit))
            if shot_path:
                tell(b"screendump " + shot_path.encode() + b"\n")
                shot_deadline = time.time() + 15.0
                last = -1
                while time.time() < shot_deadline:
                    time.sleep(0.2)
                    if os.path.exists(shot_path):
                        size = os.path.getsize(shot_path)
                        if size > 0 and size == last:
                            break
                        last = size
        tell(b"quit\n")
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
    return serial_bytes(), err


# ------------------------------------------------------- the serial claims --

BOOT_PATTERNS = [
    (r"S4: alive", "S4: alive"),
    (r"S4: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})", "S4: gop <W>x<H> fb 0x<16 hex>"),
    (r"S4: boot services exited", "S4: boot services exited"),
    (r"S4: gdt and paging ours", "S4: gdt and paging ours"),
    (r"S4: idt ready", "S4: idt ready"),
    (r"S4: cores found (\d+)", "S4: cores found <N>"),
    (r"S4: cores woken (\d+)", "S4: cores woken <N>"),
    (r"S4: console (\d+)x(\d+)", "S4: console <COLS>x<ROWS>"),
    (r"S4: disk (\d+) sectors", "S4: disk <N> sectors"),
    (r"S4: notebook (formatted|\d+ notes)", "S4: notebook formatted | S4: notebook <N> notes"),
    (r"S4: nic ([0-9a-f]{2}(?::[0-9a-f]{2}){5})", "S4: nic <mac>"),
    (r"S4: keyboard ready", "S4: keyboard ready"),
]


def check_boot_lines(capture, smp, notebook_want):
    """The twelve lines, in order, self-consistent, with line ten as demanded
    and line eleven carrying the harness's MAC. Returns (problems, geometry)."""
    problems = []
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S4: [^\n]*", text)
    if len(got) != 12:
        problems.append("expected exactly 12 S4: lines, found %d" % len(got))
        if len(got) > 12:
            problems.append("more than twelve usually means a reboot loop - and with the IDT "
                            "up it should have been an ERR: exception line instead")
    errs = re.findall(r"ERR: [^\n]*", text)
    if errs:
        problems.append("the guest reported: %s" % "; ".join(errs[:3]))

    w = h = cols = rows = None
    found = woken = None
    for i, (pattern, shape) in enumerate(BOOT_PATTERNS):
        line = got[i] if i < len(got) else ""
        m = re.fullmatch(pattern, line)
        if not m:
            problems.append("line %d: got '%s', want '%s'" % (i + 1, line, shape))
            continue
        if i == 1:
            w, h = int(m.group(1)), int(m.group(2))
            if w <= 0 or h <= 0:
                problems.append("line 2: degenerate mode %dx%d" % (w, h))
            if m.group(3) == "0" * 16:
                problems.append("line 2: framebuffer address is zero")
        elif i == 5:
            found = int(m.group(1))
        elif i == 6:
            woken = int(m.group(1))
        elif i == 7:
            cols, rows = int(m.group(1)), int(m.group(2))
        elif i == 8:
            if int(m.group(1)) != DISK_BYTES // SECTOR:
                problems.append("line 9: the guest counted %s sectors, but the image is %d sectors"
                                % (m.group(1), DISK_BYTES // SECTOR))
        elif i == 9:
            if m.group(1) != notebook_want:
                problems.append("line 10: got 'S4: notebook %s', want 'S4: notebook %s'"
                                % (m.group(1), notebook_want))
        elif i == 10:
            if m.group(1) != MAC:
                problems.append("line 11: the guest read MAC %s, but the harness gave the device %s"
                                % (m.group(1), MAC))

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
    echo of what was typed, and nothing else - no indicator, no answer, no
    error text ever reaches the wire."""
    marker = READY + b"\r\n"
    idx = capture.find(marker)
    if idx < 0:
        return ["no '%s' CRLF in the capture" % READY.decode()]
    tail = capture[idx + len(marker):]
    if tail == want:
        return []
    return ["after 'S4: keyboard ready' the serial channel carries %r, want %r" % (tail, want)]


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

BG = (16, 16, 24)
FG = (224, 224, 224)
TOL = 4
CELL = 16
PROMPT = object()    # the row that is "> " and the block cursor


def read_ppm(path):
    data = open(path, "rb").read()
    if not data.startswith(b"P6"):
        raise ValueError("not a binary PPM (P6), starts with %r" % data[:8])
    idx = 2
    fields = []
    while len(fields) < 3:
        while idx < len(data) and data[idx:idx + 1].isspace():
            idx += 1
        if data[idx:idx + 1] == b"#":
            while idx < len(data) and data[idx:idx + 1] != b"\n":
                idx += 1
            continue
        start = idx
        while idx < len(data) and not data[idx:idx + 1].isspace():
            idx += 1
        fields.append(int(data[start:idx]))
    idx += 1
    width, height, maxval = fields
    if maxval != 255:
        raise ValueError("expected 8-bit PPM (maxval 255), got %d" % maxval)
    pixels = data[idx:]
    need = width * height * 3
    if len(pixels) < need:
        raise ValueError("truncated PPM: %d bytes of pixel data, expected %d" % (len(pixels), need))
    return width, height, pixels[:need]


def load_font():
    data = open(FONT, "rb").read()
    if len(data) != 1024:
        raise ValueError("font8x8.bin is %d bytes, expected 1024" % len(data))
    return data


def glyph_rows(font, ch):
    return font[ord(ch) * 8:(ord(ch) + 1) * 8]


def render_cell(font, ch):
    rows = []
    for byte in glyph_rows(font, ch):
        row = b"".join(bytes(FG if byte >> x & 1 else BG) * 2 for x in range(8))
        rows.append(row)
        rows.append(row)
    return rows


def cursor_cell():
    return [bytes(FG) * CELL] * CELL


def blank_cell():
    return [bytes(BG) * CELL] * CELL


def font_self_check(font, text):
    problems = []
    used = sorted(set(text.replace(" ", "").replace("\n", "")))
    shapes = {}
    for ch in used:
        rows = glyph_rows(font, ch)
        if not any(rows):
            problems.append("glyph %r in the font is blank - the test would prove nothing" % ch)
        shapes.setdefault(bytes(rows), []).append(ch)
    for chars in shapes.values():
        if len(chars) > 1:
            problems.append("glyphs %s are identical in the font" % ", ".join(map(repr, chars)))
    if any(glyph_rows(font, " ")):
        problems.append("the space glyph is not blank")
    return problems


def cell_matches(pixels, width, row, col, want_rows):
    x0 = col * CELL * 3
    for dy in range(CELL):
        base = ((row * CELL + dy) * width) * 3 + x0
        got = pixels[base:base + CELL * 3]
        want = want_rows[dy]
        if got == want:
            continue
        for i in range(CELL * 3):
            if abs(got[i] - want[i]) > TOL:
                return False
    return True


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


def strip_matches(pixels, width, font, row, text):
    return all(cell_matches(pixels, width, row, col, render_cell(font, ch))
               for col, ch in enumerate(text))


def check_screen(shot, geometry, expected):
    """`expected` is a list of rows: strings drawn from column 0, or PROMPT.
    They must appear on consecutive rows, the first found exactly once on
    screen, every text row followed by a blank cell, and nothing but the two
    console colours anywhere."""
    w, h, cols, rows = geometry
    if not os.path.isfile(shot) or os.path.getsize(shot) == 0:
        return ["qemu produced no screendump"]
    try:
        width, height, pixels = read_ppm(shot)
    except ValueError as exc:
        return ["could not read the screendump: %s" % exc]
    say("serial claims %dx%d (%dx%d cells); screendump is %dx%d" % (w, h, cols, rows, width, height))
    if (width, height) != (w, h):
        return ["screendump is %dx%d but the guest said the mode was %dx%d" % (width, height, w, h)]
    try:
        font = load_font()
    except (OSError, ValueError) as exc:
        return ["the shared font is unusable: %s" % exc]
    texts = [t for t in expected if t is not PROMPT]
    problems = font_self_check(font, "".join(texts) + "> ")
    if problems:
        return problems
    for t in texts:
        if len(t) >= cols:
            return ["expected row %r is %d cells wide but the console has only %d columns" % (t, len(t), cols)]

    first = expected[0]
    hits = [r for r in range(rows) if strip_matches(pixels, width, font, r, first)]
    if len(hits) != 1:
        problems.append("the row %r appears %d times on screen, want exactly once" % (first, len(hits)))
        say("per-row first-cell census, rows that are not pure background:")
        shown = 0
        for r in range(rows):
            if cell_matches(pixels, width, r, 0, blank_cell()):
                continue
            say("  row %3d col 0: %s" % (r, cell_census(pixels, width, r, 0)))
            shown += 1
            if shown >= 24:
                say("  ...")
                break
        return problems

    base = hits[0]
    for i, want in enumerate(expected):
        r = base + i
        if r >= rows:
            problems.append("row %d is off the bottom of the screen - no room for %r" % (r, want))
            break
        if want is PROMPT:
            for col, ch in ((0, ">"), (1, " ")):
                if not cell_matches(pixels, width, r, col, render_cell(font, ch)):
                    problems.append("row %d, column %d is not %r - %s" % (r, col, ch, cell_census(pixels, width, r, col)))
            if not cell_matches(pixels, width, r, 2, cursor_cell()):
                problems.append("row %d, column 2 is not the block cursor - %s" % (r, cell_census(pixels, width, r, 2)))
            continue
        if not strip_matches(pixels, width, font, r, want):
            bad = next((c for c, ch in enumerate(want)
                        if not cell_matches(pixels, width, r, c, render_cell(font, ch))), None)
            problems.append("row %d is not %r - column %s is %s"
                            % (r, want, bad, cell_census(pixels, width, r, bad) if bad is not None else "?"))
            continue
        if not cell_matches(pixels, width, r, len(want), blank_cell()):
            problems.append("row %d: the cell after %r is not blank - %s (an indicator left behind?)"
                            % (r, want, cell_census(pixels, width, r, len(want))))
        if i > 0:
            others = [x for x in range(rows) if x != r and strip_matches(pixels, width, font, x, want)]
            if others:
                problems.append("row %r also appears at row(s) %s" % (want, others))

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


def run_question(smp):
    """Test 3 at one -smp value."""
    record = os.path.join(OUT, "broker.%d.jsonl" % smp)
    serial = os.path.join(OUT, "serial.question.%d.txt" % smp)
    shot = os.path.join(OUT, "screen.question.%d.ppm" % smp)
    mock, err = start_mock(record)
    if err:
        say(err)
        return 1
    say("mock broker listening on 127.0.0.1:%d, recording to %s" % (BROKER_PORT, os.path.relpath(record, REPO)))
    try:
        fresh_disk(NOTES)
        steps = [
            ("type", "? ping\n"), ("wait_record", record, 1, 20.0), ("sleep", SETTLE),
            ("type", "keep this\n"), ("sleep", 1.5),
            ("type", "? hello\n"), ("wait_record", record, 2, 20.0), ("sleep", SETTLE),
        ]
        capture, err = drive(smp, NOTES, steps, serial, shot)
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1

    ok = True
    problems, geometry = check_boot_lines(capture, smp, "formatted")
    problems += check_echo(capture, b"? ping\r\nkeep this\r\n? hello\r\n")
    ok &= report("the serial log is not what the spec asks for", problems, capture)
    if ok:
        say("twelve boot lines, nic %s; the wire after ready carries exactly the three typed lines" % MAC)

    problems = check_record(record, ["ping", "hello"])
    ok &= report("the broker's record is not what UMBILICAL.md asks for", problems)
    if not problems:
        say("the broker received exactly two frames, 'ping' and 'hello', byte-exact per UMBILICAL.md")

    problems = check_image(NOTES, ["keep this"])
    ok &= report("the notebook is not what it should be", problems)
    if not problems:
        say("the notebook holds exactly 'keep this' - neither question was journaled")

    if None in geometry:
        say("no picture to judge - the boot lines were wrong")
        return 1
    expected = ["> ? ping", CANNED["ping"], "> keep this", "> ? hello"] + CANNED["hello"].split("\n") + [PROMPT]
    problems = check_screen(shot, geometry, expected)
    ok &= report("the screen does not show the conversation", problems)
    if not problems:
        say("the screen shows both questions, both answers and the prompt, pixel-correct, two colours only")

    say("-smp %d: %s" % (smp, "the machine asked and was answered" if ok else "the round trip failed"))
    return 0 if ok else 1


def check_cage_argv(argv):
    """The harness inspects its own QEMU command."""
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
        if not re.search(r"guestfwd=tcp:10\.0\.2\.4:9999-cmd:nc -N 127\.0\.0\.1 9999(,|$)", nd):
            problems.append("the guestfwd is not tcp:10.0.2.4:9999 delivered by 'nc -N 127.0.0.1 9999': %r" % nd)
        if "hostfwd" in nd:
            problems.append("the netdev opens a hostfwd: %r" % nd)
    for flag in ("-nic", "-net", "-netdev-add"):
        if flag in argv:
            problems.append("the command carries %s" % flag)
    nics = [d for d in devices if d.startswith("virtio-net-pci")]
    if len(nics) != 1 or len(devices) != 1:
        problems.append("expected exactly one -device, a virtio-net-pci, found %r" % devices)
    for d in nics:
        if "netdev=n0" not in d.split(","):
            problems.append("the NIC is not attached to netdev n0: %r" % d)
        if ("mac=" + MAC) not in d.split(","):
            problems.append("the NIC does not carry the harness's MAC %s: %r" % (MAC, d))
    return problems


def run_cage():
    """Test 4: the cage asserted, then the mock-down run at -smp 8."""
    smp = 8
    argv = qemu_argv(smp, NOTES, os.path.join(OUT, "x"))
    problems = check_cage_argv(argv)
    if not report("the harness's own QEMU command is not the cage", problems):
        return 1
    say("the QEMU command carries restrict=on and the single guestfwd to 10.0.2.4:9999 via nc to 127.0.0.1:9999")

    if port_state(BROKER_PORT) != "closed":
        say("something is listening on 127.0.0.1:%d - the mock-down run needs the port refused, "
            "and this checker must never talk to a live broker" % BROKER_PORT)
        return 1
    say("nothing listens on 127.0.0.1:%d - a connect is refused, as the mock-down run needs" % BROKER_PORT)

    serial = os.path.join(OUT, "serial.cage.%d.txt" % smp)
    shot = os.path.join(OUT, "screen.cage.%d.ppm" % smp)
    fresh_disk(NOTES)
    steps = [("type", "? ping\n"), ("sleep", 6.0), ("type", "still here\n"), ("sleep", SETTLE)]
    capture, err = drive(smp, NOTES, steps, serial, shot)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1

    ok = True
    problems, geometry = check_boot_lines(capture, smp, "formatted")
    problems += check_echo(capture, b"? ping\r\nstill here\r\n")
    ok &= report("the serial log is not what the spec asks for", problems, capture)
    if not problems:
        say("twelve boot lines; the wire after ready carries exactly the two typed lines")

    problems = check_image(NOTES, ["still here"])
    ok &= report("the notebook is not what it should be", problems)
    if not problems:
        say("the notebook holds exactly 'still here' - the machine was listening again within 6 s")

    if None in geometry:
        return 1
    problems = check_screen(shot, geometry, ["> ? ping", NO_ANSWER, "> still here", PROMPT])
    ok &= report("the screen does not show the failure honestly", problems)
    if not problems:
        say("the screen shows '%s' and the prompt, pixel-correct, two colours only" % NO_ANSWER)
    say("the cage: %s" % ("held, and failure was a message, not a hang" if ok else "not proven"))
    return 0 if ok else 1


def main(argv):
    if len(argv) == 2 and argv[0] == "--question":
        try:
            return run_question(int(argv[1]))
        except ValueError:
            pass
    if argv == ["--cage"]:
        return run_cage()
    say("usage: checkumbilical.py --question <smp> | --cage")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
