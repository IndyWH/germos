#!/usr/bin/env python3
"""Stage 1 acceptance test 4 - the pixels.

Boots stage1/out/esp.img in a headless QEMU under OVMF at -smp 8, waits for the
guest to say "S1: done" on serial, takes a screendump from the QEMU monitor, and
confirms the screen is exactly eight equal solid bands in the expected colours,
at the resolution the serial log claimed.

The same run yields both the picture and the claim it must match, which is the
point: nothing here hard-codes a resolution. Whatever GOP mode the firmware
offered, the guest reports it and the screendump has to agree.

Pure standard library on purpose - the acceptance machinery should have one less
thing that can break. Everything runs inside QEMU with OVMF as firmware and
exactly one drive, a raw FAT image under stage1/out/. No real disk is touched.

This file is frozen acceptance machinery. See the header of stage1/test.sh.

Exit 0 if the bands are right, 1 otherwise.
"""

import os
import re
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "stage1", "out")
ESP = os.path.join(OUT, "esp.img")
SHOT = os.path.join(OUT, "screen.ppm")
SERIAL = os.path.join(OUT, "serial.px.txt")
OVMF = "/usr/share/ovmf/OVMF.fd"

SMP = 8

# The cycling band colours, as RGB. Neighbours differ strongly, and so does the
# wrap from the last back to the first, which is what keeps the picture readable
# at the -smp 32 mirror run.
COLOURS = [
    (0xFF, 0x00, 0x00),  # red
    (0x00, 0xFF, 0xFF),  # cyan
    (0xFF, 0xFF, 0x00),  # yellow
    (0x00, 0x00, 0xFF),  # blue
    (0x00, 0xFF, 0x00),  # green
    (0xFF, 0x00, 0xFF),  # magenta
    (0xFF, 0x7F, 0x00),  # orange
    (0xFF, 0xFF, 0xFF),  # white
]
NAMES = ["red", "cyan", "yellow", "blue", "green", "magenta", "orange", "white"]
TOL = 4

INDENT = "    "


def say(msg):
    print(INDENT + msg)


def band_rows(index, height, count):
    """Row range for one band. The guest uses the same rule, so 'equal bands'
    means one formula applied twice rather than two that have to agree."""
    return (index * height) // count, ((index + 1) * height) // count


def capture():
    """Boot under OVMF, wait for S1: done, screendump. Returns (path, error)."""
    if not os.path.isfile(ESP):
        return None, "no image was built"
    if not os.path.isfile(OVMF):
        return None, "OVMF firmware not found at " + OVMF

    for path in (SHOT, SERIAL):
        if os.path.exists(path):
            os.remove(path)

    proc = subprocess.Popen(
        [
            "qemu-system-x86_64",
            "-machine", "q35",
            "-m", "256M",
            "-smp", str(SMP),
            "-bios", OVMF,
            "-drive", "format=raw,file=" + ESP,
            "-display", "none",
            "-serial", "file:" + SERIAL,
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

    err = None
    try:
        # Wait for the guest to finish painting, rather than guessing at a delay.
        deadline = time.time() + 45.0
        done = False
        while time.time() < deadline:
            time.sleep(0.25)
            if proc.poll() is not None:
                break
            if os.path.exists(SERIAL):
                try:
                    with open(SERIAL, "rb") as fh:
                        if b"S1: done" in fh.read():
                            done = True
                            break
                except OSError:
                    pass

        if not done:
            err = "the guest never printed 'S1: done' within 45s"

        # Screendump anyway - a wrong picture is more useful than no picture.
        tell(b"screendump " + SHOT.encode() + b"\n")
        shot_deadline = time.time() + 15.0
        last = -1
        while time.time() < shot_deadline:
            time.sleep(0.2)
            if os.path.exists(SHOT):
                size = os.path.getsize(SHOT)
                if size > 0 and size == last:
                    break
                last = size

        tell(b"quit\n")
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    finally:
        # Never leave a QEMU running behind us.
        if proc.poll() is None:
            proc.kill()
            proc.wait()

    if err:
        return None, err
    if not os.path.isfile(SHOT) or os.path.getsize(SHOT) == 0:
        detail = proc.stderr.read().decode("utf-8", "replace").strip()
        return None, "qemu produced no screendump" + ((": " + detail) if detail else "")
    return SHOT, None


def claimed_resolution():
    """The W and H the guest itself reported, from this run's serial log."""
    try:
        with open(SERIAL, "rb") as fh:
            text = fh.read().decode("utf-8", "replace").replace("\r", "")
    except OSError:
        return None, None, "no serial log was captured"
    m = re.search(r"S1: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})", text)
    if not m:
        return None, None, "the serial log has no 'S1: gop <W>x<H> fb 0x...' line"
    return int(m.group(1)), int(m.group(2)), None


def read_ppm(path):
    """Parse a binary PPM by hand. Returns (width, height, bytes)."""
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
    idx += 1  # exactly one whitespace byte after maxval

    width, height, maxval = fields
    if maxval != 255:
        raise ValueError("expected 8-bit PPM (maxval 255), got %d" % maxval)
    pixels = data[idx:]
    need = width * height * 3
    if len(pixels) < need:
        raise ValueError(
            "truncated PPM: %d bytes of pixel data, expected %d" % (len(pixels), need)
        )
    return width, height, pixels[:need]


def row_census(pixels, width, y, limit=4):
    """The commonest colours on one row, as (rgb, count) pairs."""
    base = y * width * 3
    counts = {}
    for x in range(width):
        off = base + x * 3
        rgb = (pixels[off], pixels[off + 1], pixels[off + 2])
        counts[rgb] = counts.get(rgb, 0) + 1
    return sorted(counts.items(), key=lambda kv: -kv[1])[:limit]


def check_band(pixels, width, lo, hi, want):
    """Return None if every row in [lo, hi) is solid `want`, else a complaint."""
    exact = bytes(want) * width
    for y in range(lo, hi):
        base = y * width * 3
        row = pixels[base:base + width * 3]
        if row == exact:
            continue
        # Slow path only for a row that is not already perfect: allow tolerance,
        # and if it still fails, say precisely what is on that row instead.
        for x in range(width):
            off = x * 3
            if any(abs(row[off + i] - want[i]) > TOL for i in range(3)):
                census = row_census(pixels, width, y)
                return (
                    "row %d is not solid rgb%s - first bad pixel at x=%d is rgb%s; "
                    "commonest on that row: %s"
                    % (
                        y, want, x,
                        (row[off], row[off + 1], row[off + 2]),
                        ", ".join("rgb%s x%d" % (c, n) for c, n in census),
                    )
                )
    return None


def main():
    shot, err = capture()
    if err:
        say("test 4: " + err)
        if os.path.exists(SERIAL) and os.path.getsize(SERIAL):
            say("serial log tail:")
            with open(SERIAL, "rb") as fh:
                tail = fh.read().decode("utf-8", "replace").replace("\r", "")
            for line in tail.strip().splitlines()[-12:]:
                say("  " + line)
        return 1

    want_w, want_h, serr = claimed_resolution()
    if serr:
        say("test 4: " + serr)
        return 1

    try:
        width, height, pixels = read_ppm(shot)
    except ValueError as exc:
        say("test 4: could not read the screendump: %s" % exc)
        return 1

    say("serial claims %dx%d; screendump is %dx%d" % (want_w, want_h, width, height))

    problems = []

    if (width, height) != (want_w, want_h):
        msg = "screendump is %dx%d but the guest said the mode was %dx%d" % (
            width, height, want_w, want_h)
        if want_w and want_h and width % want_w == 0 and height % want_h == 0:
            msg += (
                " - an exact %dx%d multiple, which is what QEMU does when it "
                "line-doubles a low-resolution VGA mode (Stage 0's gotcha); a "
                "linear GOP framebuffer should not be scaled at all"
                % (width // want_w, height // want_h)
            )
        problems.append(msg)
        for p in problems:
            say("test 4: " + p)
        return 1

    if height < SMP:
        say("test 4: the mode is only %d rows tall, too few for %d bands"
            % (height, SMP))
        return 1

    # Every row belongs to exactly one band, so checking all of them is the same
    # as saying "exactly eight bands and nothing else on the screen".
    observed = []
    for i in range(SMP):
        lo, hi = band_rows(i, height, SMP)
        want = COLOURS[i % len(COLOURS)]
        observed.append((i, lo, hi, want))
        complaint = check_band(pixels, width, lo, hi, want)
        if complaint:
            problems.append(
                "band %d (%s, rows %d-%d): %s" % (i, NAMES[i % len(NAMES)], lo, hi - 1, complaint)
            )

    # A screen that is one flat colour must not pass, whatever the table says.
    for i in range(1, SMP):
        if COLOURS[i % len(COLOURS)] == COLOURS[(i - 1) % len(COLOURS)]:
            problems.append("bands %d and %d are the same colour" % (i - 1, i))

    if not problems:
        say("test 4: exactly %d equal solid bands at %dx%d, colours in order: %s"
            % (SMP, width, height, ", ".join(NAMES[i % len(NAMES)] for i in range(SMP))))
        return 0

    for p in problems:
        say("test 4: " + p)

    say("band census (row range, expected colour, commonest colour on the first row):")
    for i, lo, hi, want in observed:
        census = row_census(pixels, width, lo, limit=2)
        say("  band %d  rows %4d-%-4d  want %-8s rgb%-16s got %s"
            % (i, lo, hi - 1, NAMES[i % len(NAMES)], str(want),
               ", ".join("rgb%s x%d" % (c, n) for c, n in census)))
    return 1


if __name__ == "__main__":
    sys.exit(main())
