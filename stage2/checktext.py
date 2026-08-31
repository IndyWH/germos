#!/usr/bin/env python3
"""Stage 2 acceptance tests 3 and 4 - the typing, and the picture of it.

One driver owns the whole interactive run, exactly as Stage 1's checkbands.py
owns its run: boot stage2/out/esp.img headless under OVMF with the QEMU monitor
on stdio and serial to a file, wait for the guest itself to say
"S2: keyboard ready", then type h e l l o Enter from OUTSIDE via the monitor's
sendkey - one key at a time, with generous gaps, because a monitor can outrun a
guest.

Two modes, two acceptance tests:

  --type <smp>   Test 3. Asserts the nine S2: boot lines (a reboot loop cannot
                 slip through) and that the serial bytes after
                 "S2: keyboard ready" CRLF are EXACTLY b"hello\\r\\n" - the raw
                 echo the spec promises, and nothing else on the channel.

  --pixels       Test 4 (added by plan item 5). The same run at -smp 8, plus a
                 screendump: the checker renders "> hello" from
                 stage2/font8x8.bin itself and demands the picture agree.

Pure standard library on purpose - the acceptance machinery should have one
less thing that can break. Everything runs inside QEMU with OVMF as firmware
and exactly one drive, a raw FAT image under stage2/out/. No real disk is
touched.

This file is frozen acceptance machinery from plan item 6. See the header of
stage2/test.sh.

Exit 0 on pass, 1 otherwise.
"""

import os
import re
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "stage2", "out")
ESP = os.path.join(OUT, "esp.img")
FONT = os.path.join(REPO, "stage2", "font8x8.bin")
OVMF = "/usr/share/ovmf/OVMF.fd"

READY = b"S2: keyboard ready"
ECHO_WANT = b"hello\r\n"

# The keys, as the QEMU monitor names them, sent one at a time.
KEYS = ["h", "e", "l", "l", "o", "ret"]
KEY_GAP = 0.2        # seconds between keys - a monitor can outrun a guest
SETTLE = 1.5         # seconds after the last key before we look

INDENT = "    "


def say(msg):
    print(INDENT + msg)


# ---------------------------------------------------------------- driver ----

def drive(smp, shot_path):
    """Boot, wait for the guest's own ready line, type hello+Enter via the
    monitor, optionally screendump, quit, reap. Returns (serial_bytes, error).
    Never leaves a QEMU running behind us."""
    if not os.path.isfile(ESP):
        return b"", "no image was built"
    if not os.path.isfile(OVMF):
        return b"", "OVMF firmware not found at " + OVMF

    serial_path = os.path.join(OUT, "serial.type.%d.txt" % smp)
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
        # sendkey is meaningful. Guessing at a delay instead is how flaky
        # tests are born.
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
            err = "the guest never printed 'S2: keyboard ready' within 60s"
        else:
            time.sleep(1.0)  # let the guest finish its prompt and sti
            for key in KEYS:
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
    (r"S2: alive", "S2: alive"),
    (r"S2: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})", "S2: gop <W>x<H> fb 0x<16 hex>"),
    (r"S2: boot services exited", "S2: boot services exited"),
    (r"S2: gdt and paging ours", "S2: gdt and paging ours"),
    (r"S2: idt ready", "S2: idt ready"),
    (r"S2: cores found (\d+)", "S2: cores found <N>"),
    (r"S2: cores woken (\d+)", "S2: cores woken <N>"),
    (r"S2: console (\d+)x(\d+)", "S2: console <COLS>x<ROWS>"),
    (r"S2: keyboard ready", "S2: keyboard ready"),
]


def check_boot_lines(capture, smp):
    """The nine lines, in order, self-consistent. Returns (problems, geometry)
    where geometry is (W, H, COLS, ROWS) or Nones."""
    problems = []
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S2: [^\n]*", text)

    if len(got) != 9:
        problems.append("expected exactly 9 S2: lines, found %d" % len(got))
        if len(got) > 9:
            problems.append(
                "more than nine usually means a reboot loop - and with the IDT "
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


def check_echo(capture):
    """The bytes after the ready line's CRLF must be exactly the raw echo."""
    marker = READY + b"\r\n"
    idx = capture.find(marker)
    if idx < 0:
        return ["no '%s' CRLF in the capture" % READY.decode()]
    tail = capture[idx + len(marker):]
    if tail == ECHO_WANT:
        return []
    return [
        "after 'S2: keyboard ready' the serial channel carries %r, want %r"
        % (tail, ECHO_WANT)
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


# ----------------------------------------------------------------- modes ----

def run_type(smp):
    """Test 3 at one -smp value: boot lines plus the exact echo."""
    capture, err = drive(smp, shot_path=None)
    if err:
        say("-smp %d: %s" % (smp, err))
        if capture:
            dump_capture(capture)
        return 1

    problems, _ = check_boot_lines(capture, smp)
    problems += check_echo(capture)

    if not problems:
        say("-smp %d: nine boot lines, then the echo is exactly b'hello\\r\\n'" % smp)
        return 0
    say("-smp %d: the typing run is not what the spec asks for" % smp)
    for p in problems:
        say("  - " + p)
    dump_capture(capture)
    return 1


def main(argv):
    if len(argv) == 2 and argv[0] == "--type":
        try:
            smp = int(argv[1])
        except ValueError:
            say("usage: checktext.py --type <smp> | --pixels")
            return 1
        return run_type(smp)
    if argv == ["--pixels"]:
        say("--pixels arrives at plan item 5; nothing to run yet")
        return 1
    say("usage: checktext.py --type <smp> | --pixels")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
