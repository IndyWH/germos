#!/usr/bin/env python3
"""Stage 0 acceptance test 3 - the pixels.

Boots stage0/out/stage0.img in a headless QEMU, takes a `screendump` from the
QEMU monitor a few seconds after boot, and confirms the Spectrum loading stripes
are there: all four palette colours present within tolerance, red and cyan only
in the top half, blue and yellow only in the bottom half.

Pure standard library on purpose - the acceptance machinery should have one less
thing that can break. Everything runs inside QEMU; no real disk is touched.

This file is frozen acceptance machinery. See the header of stage0/test.sh.

Exit 0 if the pixels are right, 1 otherwise.
"""

import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "stage0", "out")
IMG = os.path.join(OUT, "stage0.img")
SHOT = os.path.join(OUT, "screen.ppm")

# The VGA default palette entries the spec names, and the tolerance we allow.
RED = (170, 0, 0)        # colour 4
CYAN = (0, 170, 170)     # colour 3
BLUE = (0, 0, 170)       # colour 1
YELLOW = (255, 255, 85)  # colour 14

TOP_COLOURS = {RED: "red", CYAN: "cyan"}
BOTTOM_COLOURS = {BLUE: "blue", YELLOW: "yellow"}
NAMES = dict(TOP_COLOURS)
NAMES.update(BOTTOM_COLOURS)
TOL = 24

INDENT = "    "


def say(msg):
    print(INDENT + msg)


def capture():
    """Boot the image headless and screendump it. Returns (path, error)."""
    if not os.path.isfile(IMG):
        return None, "no image was built"

    if os.path.exists(SHOT):
        os.remove(SHOT)

    proc = subprocess.Popen(
        [
            "qemu-system-x86_64",
            "-drive", "format=raw,file=" + IMG,
            "-display", "none",
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

    try:
        time.sleep(3.0)  # let the guest finish painting
        tell(b"screendump " + SHOT.encode() + b"\n")

        # Wait for the file to appear and stop growing.
        deadline = time.time() + 10.0
        last = -1
        while time.time() < deadline:
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

    if not os.path.isfile(SHOT) or os.path.getsize(SHOT) == 0:
        err = proc.stderr.read().decode("utf-8", "replace").strip()
        return None, "qemu produced no screendump" + ((": " + err) if err else "")
    return SHOT, None


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


def classify(rgb):
    """Name the colour, or None if it is not one of the four."""
    for want, name in NAMES.items():
        if all(abs(rgb[i] - want[i]) <= TOL for i in range(3)):
            return name
    return None


def main():
    shot, err = capture()
    if err:
        say("test 3: " + err)
        return 1

    try:
        width, height, pixels = read_ppm(shot)
    except ValueError as exc:
        say("test 3: could not read the screendump: %s" % exc)
        return 1

    say("screendump: %dx%d, %s" % (width, height, os.path.relpath(shot, REPO)))

    # Census: for every row, how many pixels of each colour (and of anything else).
    rows = []
    strangers = {}
    for y in range(height):
        base = y * width * 3
        counts = {}
        for x in range(width):
            off = base + x * 3
            rgb = (pixels[off], pixels[off + 1], pixels[off + 2])
            name = classify(rgb)
            if name is None:
                name = "other"
                strangers[rgb] = strangers.get(rgb, 0) + 1
            counts[name] = counts.get(name, 0) + 1
        rows.append(counts)

    half = height // 2
    problems = []

    # Every pixel must be one of the four stripe colours.
    if strangers:
        worst = sorted(strangers.items(), key=lambda kv: -kv[1])[:4]
        problems.append(
            "pixels that are none of the four stripe colours: "
            + ", ".join("rgb%s x%d" % (rgb, n) for rgb, n in worst)
        )

    # All four colours present.
    seen = set()
    for counts in rows:
        seen.update(k for k in counts if k != "other")
    for name in ("red", "cyan", "blue", "yellow"):
        if name not in seen:
            problems.append("%s is not on the screen at all" % name)

    # Red and cyan only in the top half; blue and yellow only in the bottom half.
    def stray(names, lo, hi, where):
        bad = [y for y in range(lo, hi) for n in names if rows[y].get(n)]
        if bad:
            problems.append(
                "%s found in the %s half, on row%s %s%s"
                % (
                    " / ".join(sorted(set(
                        n for y in bad for n in names if rows[y].get(n)
                    ))),
                    where,
                    "" if len(bad) == 1 else "s",
                    ", ".join(str(y) for y in sorted(set(bad))[:6]),
                    "" if len(set(bad)) <= 6 else " ...",
                )
            )

    stray(("red", "cyan"), half, height, "bottom")
    stray(("blue", "yellow"), 0, half, "top")

    if not problems:
        say("test 3: all four stripe colours present, correctly split at row %d" % half)
        return 0

    for p in problems:
        say("test 3: " + p)

    # Per-row census, so a wrong band width or a wrong colour index is diagnosed
    # from the test output alone. Runs of identical rows are collapsed.
    say("row census:")
    start = 0
    for y in range(1, height + 1):
        if y == height or rows[y] != rows[start]:
            desc = ", ".join(
                "%s x%d" % (n, c) for n, c in sorted(rows[start].items())
            )
            label = "row %d" % start if y - 1 == start else "rows %d-%d" % (start, y - 1)
            say("  %-14s %s" % (label, desc))
            start = y
    return 1


if __name__ == "__main__":
    sys.exit(main())
