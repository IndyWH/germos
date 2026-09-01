#!/usr/bin/env python3
"""Stage 3 acceptance tests 3 and 4 - persistence, and the picture of it.

One driver owns the whole two-boot run, exactly as Stage 2's checktext.py owns
its run: boot stage3/out/esp.img headless under OVMF with a fresh 16 MB raw
notebook image attached as a virtio disk, the QEMU monitor on stdio and serial
to a file; wait for the guest itself to say "S3: keyboard ready"; type
"remember me" and Enter from OUTSIDE via the monitor's sendkey - one key at a
time, with generous gaps; quit. Then parse the disk image FROM THE HOST, by
stage3/NOTEBOOK.md, and demand the note byte for byte. Then boot the SAME
image in a fresh QEMU and demand that the machine remembers.

Two modes, two acceptance tests:

  --persist <smp>  Test 3. Run one: the eleven S3: boot lines with
                   "S3: notebook formatted", the echo after "S3: keyboard
                   ready" EXACTLY b"remember me\\r\\n", and the image holding
                   exactly one record - sector 0 and sector 1 byte-identical to
                   NOTEBOOK.md's worked example, sector 2 not a record. Run
                   two, same image: the eleven lines with "S3: notebook 1
                   notes", NOTHING on the channel after "S3: keyboard ready"
                   (a note is drawn on the console, never sent to serial), and
                   the image byte-identical to what run one left - replay
                   never writes.

  --pixels         Test 4. The same two boots at -smp 8, plus a screendump at
                   the end of run two: "remember me" rendered from
                   stage2/font8x8.bin appears exactly once at column 0, the
                   prompt and cursor sit on the row directly below it, and
                   nothing but the two console colours is anywhere on screen.

Pure standard library on purpose. Everything runs inside QEMU with OVMF as
firmware and exactly two drives, both raw image files under stage3/out/, both
created here. No real disk is touched.

This file is frozen acceptance machinery from plan item 7. See the header of
stage3/test.sh.

Exit 0 on pass, 1 otherwise.
"""

import os
import re
import struct
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "stage3", "out")
ESP = os.path.join(OUT, "esp.img")
NOTES = os.path.join(OUT, "notes.img")
FONT = os.path.join(REPO, "stage2", "font8x8.bin")
OVMF = "/usr/share/ovmf/OVMF.fd"

DISK_BYTES = 16 * 1024 * 1024
SECTOR = 512

READY = b"S3: keyboard ready"
NOTE = "remember me"
ECHO_WANT = NOTE.encode() + b"\r\n"

# The keys, as the QEMU monitor names them, sent one at a time.
KEYS = ["r", "e", "m", "e", "m", "b", "e", "r", "spc", "m", "e", "ret"]
KEY_GAP = 0.2        # seconds between keys - a monitor can outrun a guest
SETTLE = 1.5         # seconds after the last key before we look

INDENT = "    "


def say(msg):
    print(INDENT + msg)


# ------------------------------------------------------------ the format ----
# stage3/NOTEBOOK.md, in code. The parser is the one printed in that document;
# the exact-bytes builders below are the worked example.

def parse_notebook(data):
    """The notes on a recognised disk, in order. Raises ValueError with the
    field that was wrong if the header is not a notebook. The journal ends
    at the first sector that is not a valid record - silently, as the guest's
    scan does."""
    if data[0:8] != b"NOTEBOOK":
        raise ValueError("sector 0 bytes 0-7 are %r, not the NOTEBOOK magic" % data[0:8])
    version, sector, first, length = struct.unpack_from("<IIQQ", data, 8)
    if version != 1:
        raise ValueError("header version is %d, want 1" % version)
    if sector != SECTOR:
        raise ValueError("header sector size is %d, want %d" % (sector, SECTOR))
    if first != 1:
        raise ValueError("header first journal sector is %d, want 1" % first)
    if length != len(data) // SECTOR - 1:
        raise ValueError("header journal length is %d, want %d for this image"
                         % (length, len(data) // SECTOR - 1))
    if any(data[0x20:SECTOR]):
        raise ValueError("header padding (bytes 0x20-0x1ff) is not all zero")
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


def expected_header(disk_bytes):
    hdr = b"NOTEBOOK" + struct.pack("<IIQQ", 1, SECTOR, 1, disk_bytes // SECTOR - 1)
    return hdr + bytes(SECTOR - len(hdr))


def expected_record(seq, text):
    rec = b"NOTE" + struct.pack("<IHH", seq, len(text), 0) + text.encode("ascii")
    return rec + bytes(SECTOR - len(rec))


def hexdump(data, base=0, limit=64):
    lines = []
    for i in range(0, min(len(data), limit), 16):
        chunk = data[i:i + 16]
        hexs = " ".join(chunk[j:j + 2].hex() for j in range(0, len(chunk), 2))
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append("%08x: %-39s  %s" % (base + i, hexs, asc))
    return lines


def check_image_after_run_one(data):
    """Exactly one note, byte-exact per the worked example."""
    problems = []
    if len(data) != DISK_BYTES:
        problems.append("the image is %d bytes, but the harness made it %d" % (len(data), DISK_BYTES))
        return problems
    try:
        notes = parse_notebook(data)
    except ValueError as exc:
        problems.append("the image is not a notebook: %s" % exc)
        problems += ["  " + l for l in hexdump(data[0:SECTOR])]
        return problems
    if notes != [NOTE]:
        problems.append("the notebook holds %r, want [%r]" % (notes, NOTE))

    want0 = expected_header(DISK_BYTES)
    if data[0:SECTOR] != want0:
        off = next(i for i in range(SECTOR) if data[i] != want0[i])
        problems.append("sector 0 differs from NOTEBOOK.md's worked example at byte 0x%x" % off)
        problems += ["  " + l for l in hexdump(data[0:SECTOR])]

    want1 = expected_record(1, NOTE)
    got1 = data[SECTOR:2 * SECTOR]
    if got1 != want1:
        off = next(i for i in range(SECTOR) if got1[i] != want1[i])
        problems.append("sector 1 differs from NOTEBOOK.md's worked example at byte 0x%x" % off)
        problems += ["  " + l for l in hexdump(got1, SECTOR)]

    if data[2 * SECTOR:2 * SECTOR + 4] == b"NOTE":
        problems.append("sector 2 starts a record - there should be exactly one note")
    return problems


# ---------------------------------------------------------------- driver ----

def fresh_disk(path):
    """A brand-new all-zero raw image. Removed first, so no note from an
    earlier run can survive; sparse, which QEMU reads as zeros."""
    if os.path.exists(path):
        os.remove(path)
    with open(path, "wb") as fh:
        fh.truncate(DISK_BYTES)


def read_image(path):
    with open(path, "rb") as fh:
        return fh.read()


def drive(smp, disk, keys, serial_path, shot_path):
    """Boot with the notebook attached, wait for the guest's own ready line,
    type the keys via the monitor (none for a silent boot), optionally
    screendump, quit, reap. Returns (serial_bytes, error). Never leaves a
    QEMU running behind us."""
    if not os.path.isfile(ESP):
        return b"", "no image was built"
    if not os.path.isfile(OVMF):
        return b"", "OVMF firmware not found at " + OVMF

    for path in (serial_path, shot_path):
        if path and os.path.exists(path):
            os.remove(path)

    proc = subprocess.Popen(
        [
            "qemu-system-x86_64",
            "-machine", "q35",
            "-m", "256M",
            "-smp", str(smp),
            "-bios", OVMF,
            "-drive", "format=raw,file=" + ESP,
            "-drive", "format=raw,file=" + disk + ",if=virtio",
            "-display", "none",
            "-serial", "file:" + serial_path,
            "-monitor", "stdio",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

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
        # Wait for the guest itself to say it is listening - the only moment
        # sendkey is meaningful, and the moment the boot log is complete.
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
            err = "the guest never printed 'S3: keyboard ready' within 60s"
        else:
            time.sleep(1.0)  # let the guest finish its replay, prompt and sti
            for key in keys:
                tell(b"sendkey " + key.encode() + b"\n")
                time.sleep(KEY_GAP)
            time.sleep(SETTLE)

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
    (r"S3: alive", "S3: alive"),
    (r"S3: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})", "S3: gop <W>x<H> fb 0x<16 hex>"),
    (r"S3: boot services exited", "S3: boot services exited"),
    (r"S3: gdt and paging ours", "S3: gdt and paging ours"),
    (r"S3: idt ready", "S3: idt ready"),
    (r"S3: cores found (\d+)", "S3: cores found <N>"),
    (r"S3: cores woken (\d+)", "S3: cores woken <N>"),
    (r"S3: console (\d+)x(\d+)", "S3: console <COLS>x<ROWS>"),
    (r"S3: disk (\d+) sectors", "S3: disk <N> sectors"),
    (r"S3: notebook (formatted|\d+ notes)", "S3: notebook formatted | S3: notebook <N> notes"),
    (r"S3: keyboard ready", "S3: keyboard ready"),
]


def check_boot_lines(capture, smp, notebook_want):
    """The eleven lines, in order, self-consistent, with line ten as
    demanded ("formatted" or "1 notes"). Returns (problems, geometry) where
    geometry is (W, H, COLS, ROWS) or Nones."""
    problems = []
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S3: [^\n]*", text)

    if len(got) != 11:
        problems.append("expected exactly 11 S3: lines, found %d" % len(got))
        if len(got) > 11:
            problems.append(
                "more than eleven usually means a reboot loop - and with the IDT "
                "up it should have been an ERR: exception line instead")

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
            sectors = int(m.group(1))
            if sectors != DISK_BYTES // SECTOR:
                problems.append("line 9: the guest counted %d sectors, but the image is %d bytes = %d sectors"
                                % (sectors, DISK_BYTES, DISK_BYTES // SECTOR))
        elif i == 9:
            if m.group(1) != notebook_want:
                problems.append("line 10: got 'S3: notebook %s', want 'S3: notebook %s'"
                                % (m.group(1), notebook_want))

    if found is not None and found != smp:
        problems.append("cores found is %d, but the machine was given -smp %d" % (found, smp))
    if woken is not None and woken != smp:
        problems.append("cores woken is %d, but the machine was given -smp %d" % (woken, smp))
    if None not in (w, h, cols, rows):
        if cols != w // 16:
            problems.append("console claims %d columns, but %d pixels / 16 = %d" % (cols, w, w // 16))
        if rows != h // 16:
            problems.append("console claims %d rows, but %d pixels / 16 = %d" % (rows, h, h // 16))

    return problems, (w, h, cols, rows)


def check_echo(capture, want):
    """The bytes after the ready line's CRLF must be exactly `want` - the raw
    echo of what was typed, or nothing at all on a silent boot."""
    marker = READY + b"\r\n"
    idx = capture.find(marker)
    if idx < 0:
        return ["no '%s' CRLF in the capture" % READY.decode()]
    tail = capture[idx + len(marker):]
    if tail == want:
        return []
    return [
        "after 'S3: keyboard ready' the serial channel carries %r, want %r"
        % (tail, want)
    ]


def dump_capture(capture):
    say("whole capture follows (OVMF chatter included, control bytes visible):")
    text = capture.decode("utf-8", "replace")
    shown = "".join(
        ch if ch == "\n" or 32 <= ord(ch) < 127 else "^" + format(ord(ch), "02x")
        for ch in text.replace("\r\n", "\n")
    )
    for line in shown.splitlines()[-40:]:
        say("  " + line)


# ------------------------------------------------------------ the two boots -

def two_boots(smp, shot_path):
    """The whole of test 3, at one -smp value; with a screendump of run two
    if asked. Returns (problems, capture_two, geometry)."""
    disk = NOTES
    fresh_disk(disk)
    serial_one = os.path.join(OUT, "serial.persist.%d.run1.txt" % smp)
    serial_two = os.path.join(OUT, "serial.persist.%d.run2.txt" % smp)

    # Run one: a blank disk, a note typed, the machine quit.
    capture, err = drive(smp, disk, KEYS, serial_one, None)
    if err:
        say("run one: " + err)
        if capture:
            dump_capture(capture)
        return ["run one did not reach the prompt"], None, (None,) * 4
    problems, _ = check_boot_lines(capture, smp, "formatted")
    problems += check_echo(capture, ECHO_WANT)
    if problems:
        say("run one (fresh disk, typing) is not what the spec asks for:")
        for p in problems:
            say("  - " + p)
        dump_capture(capture)
        return problems, None, (None,) * 4
    say("run one: eleven boot lines, notebook formatted, echo exactly %r" % ECHO_WANT)

    # The disk, from the host, by NOTEBOOK.md.
    image_one = read_image(disk)
    problems = check_image_after_run_one(image_one)
    if problems:
        say("the disk image after run one is not what NOTEBOOK.md says:")
        for p in problems:
            say("  - " + p)
        return problems, None, (None,) * 4
    say("the image holds exactly one note, %r, byte-exact per NOTEBOOK.md" % NOTE)

    # Run two: the same image, a fresh machine, nothing typed.
    capture, err = drive(smp, disk, [], serial_two, shot_path)
    if err:
        say("run two: " + err)
        if capture:
            dump_capture(capture)
        return ["run two did not reach the prompt"], capture, (None,) * 4
    problems, geometry = check_boot_lines(capture, smp, "1 notes")
    problems += check_echo(capture, b"")
    image_two = read_image(disk)
    if image_two != image_one:
        off = next(i for i in range(min(len(image_one), len(image_two)))
                   if image_one[i] != image_two[i]) if len(image_one) == len(image_two) else -1
        problems.append("the image changed during run two (first difference at byte %d) - "
                        "a replay must not write" % off)
    if problems:
        say("run two (same disk, silent boot) is not what the spec asks for:")
        for p in problems:
            say("  - " + p)
        dump_capture(capture)
        return problems, capture, geometry
    say("run two: eleven boot lines, notebook 1 notes, nothing on the wire after ready, image unchanged")
    return [], capture, geometry


# ----------------------------------------------------------------- modes ----

def run_persist(smp):
    """Test 3 at one -smp value."""
    problems, _, _ = two_boots(smp, None)
    if problems:
        say("-smp %d: the machine did not keep what it was told" % smp)
        return 1
    say("-smp %d: the machine remembered" % smp)
    return 0


def main(argv):
    if len(argv) == 2 and argv[0] == "--persist":
        try:
            smp = int(argv[1])
        except ValueError:
            say("usage: checknotes.py --persist <smp> | --pixels")
            return 1
        return run_persist(smp)
    say("usage: checknotes.py --persist <smp> | --pixels")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
