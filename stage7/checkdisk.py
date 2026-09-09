#!/usr/bin/env python3
"""Stage 7 ring 7a acceptance checks - the disk, from the host and through
the monitor.

Implements the host-side halves of acceptance test 2 and the whole of
tests 3 and 4 from stage7/spec.md (ring 7a), as stage7/plan-7a.md and its
amendments fix them:

  --formatted IMAGE SECTORS NOTES HOME
        a disk the guest formatted on a blank 64 MB image, parsed cold:
        the thirty-six table sectors byte-identical to DISK.md's build_gpt,
        the notes partition a freshly formatted NOTEBOOK.md disk, the home
        partition a freshly formatted HOME.md disk, every other sector of
        the disk zero; the guest's disk line (the sector count and the two
        LBAs, handed in by the harness) agreeing with the image and the
        document.
  --recognised IMAGE SECTORS NOTES HOME
        the same disk line on a later boot of the same disk.
  --foreign IMAGE
        writes a 64 MB image carrying a valid table with another type
        GUID - the disk the guest must refuse by name and never write.
  --esp BEFORE AFTER EFI
        the boot image across one boot: sector 0 byte-identical, still
        "other" to DISK.md's classify (no table written over it), the
        packed BOOTX64.EFI extracted byte-identical to the build, the size
        unchanged. OVMF writes its NvVars file into the ESP on every boot
        (ring 7a item 1's measurement), so a whole-image identity cannot
        be the criterion; what the guest must never do is the criterion.
  --persist SMP     (test 3, item 6)
  --store           (test 4, item 7)

Everything runs inside QEMU with the caged network and the 1920x1080
display, on the patient's CPU model; the only disks are raw files under
stage7/out/. The mock broker is broker/metal.py --mock, which calls
nothing. DISK.md's Python comes from broker/metal.py, which carries it
verbatim; NOTEBOOK.md's and HOME.md's parsers from the frozen Stage 3 and
ring 6b checkers, and every prefix-free helper from the frozen Stage 6
checkers. What is spelled here is what those cannot say: the S7: lines,
the Stage 7 machine, the partition cut.

This file is frozen acceptance machinery from ring 7a plan item 8.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "stage7", "out")
ESP = os.path.join(OUT, "esp.img")
DISK = os.path.join(OUT, "disk.img")
EFI = os.path.join(OUT, "BOOTX64.EFI")
BROKER = os.path.join(REPO, "broker", "metal.py")
PLANS_DIR = os.path.join(REPO, "plans")
GERMLINE = os.path.join(OUT, "germline")
REHEARSAL = os.path.join(OUT, "rehearsal")
TWIN_WORKDIR = os.path.join(REHEARSAL, "twin")
OVMF = "/usr/share/ovmf/OVMF.fd"

for sub in ("broker", "stage3", "stage6"):
    sys.path.insert(0, os.path.join(REPO, sub))
import metal  # noqa: E402  - DISK.md's Python, verbatim
from metal import (SECTOR, NOTES_FIRST, HOME_FIRST, PART_SECTORS, DISK_BYTES_7, build_gpt, parse_gpt,  # noqa: E402
                   classify, partition_bytes, check_table, partition_entries, gpt_header, crc32, guid_bytes)
from checknotes import parse_notebook, expected_header, expected_record  # noqa: E402
from checkglass import say, report, dump_capture  # noqa: E402
from checkplans import parse_home  # noqa: E402
import uuid  # noqa: E402

PART_BYTES = PART_SECTORS * SECTOR                   # 16 MB: what NOTEBOOK.md's and HOME.md's parsers expect
DISK_SECTORS = DISK_BYTES_7 // SECTOR
FOREIGN_TYPE = uuid.UUID("9e9c5e3d-0a3a-4a2c-8f52-6b8e6d3e2a11")   # someone else's partition type

# The Stage 7 machine, spelled once for the checker (test.sh spells its own
# and test 4 inspects both): q35, the patient's CPU, the display.
CPU = ["-cpu", "IvyBridge"]
DISPLAY = ["-vga", "none", "-device", "VGA,edid=on,xres=1920,yres=1080"]
BROKER_PORT = 9999
REHEARSAL_PORT = 9998
MAC = "52:54:00:a1:07:01"
CAGE_NETDEV = ("user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:%d-cmd:nc -N 127.0.0.1 %d"
               % (BROKER_PORT, BROKER_PORT))
CAGE_DEVICE = "virtio-net-pci,netdev=n0,mac=" + MAC
READY = b"S7: keyboard ready"

# ------------------------------------------------------- the serial lines --
# DISK.md, "The serial lines": a boot that formats a blank disk prints
# eighteen lines, a boot that recognises the disk seventeen. The expected
# count is the length of the list - never a literal.

DISK_LINE = (r"S7: disk port (\d+) (\d+) notes (\d+) home (\d+)", "S7: disk port <p> <N> notes <lba> home <lba>")
PATTERNS_AGAIN = [
    (r"S7: alive", "S7: alive"),
    (r"S7: edid (\d+)x(\d+)", "S7: edid <W>x<H>"),
    (r"S7: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})", "S7: gop <W>x<H> fb 0x<16 hex>"),
    (r"S7: boot services exited", "S7: boot services exited"),
    (r"S7: gdt and paging ours", "S7: gdt and paging ours"),
    (r"S7: idt ready", "S7: idt ready"),
    (r"S7: cores found (\d+)", "S7: cores found <N>"),
    (r"S7: cores woken (\d+)", "S7: cores woken <N>"),
    (r"S7: console (\d+)x(\d+)", "S7: console <COLS>x<ROWS>"),
    DISK_LINE,
    (r"S7: notebook (formatted|\d+ notes)", "S7: notebook formatted | S7: notebook <N> notes"),
    (r"S7: home (\d+) apps", "S7: home <N> apps"),
    (r"S7: nic ([0-9a-f]{2}(?::[0-9a-f]{2}){5})", "S7: nic <mac>"),
    (r"S7: component region 0x([0-9a-f]{16}) (\d+) bytes", "S7: component region 0x<16 hex> 1048576 bytes"),
    (r"S7: obs page 0x([0-9a-f]{16})", "S7: obs page 0x<16 hex>"),
    (r"S7: glass core (\d+)", "S7: glass core <id>"),
    (r"S7: keyboard ready", "S7: keyboard ready"),
]
PATTERNS_BLANK = PATTERNS_AGAIN[:9] + [(r"S7: gpt written", "S7: gpt written")] + PATTERNS_AGAIN[9:]
BLOB_MAX = 1048576


def check_boot_lines(capture, smp, blank, notebook_want, home_want, sectors):
    """DISK.md's lines, in order, self-consistent: eighteen on a formatting
    boot (blank True), seventeen on a recognising one. The disk line must
    name the sector count of the image the harness made and DISK.md's two
    LBAs. Returns (problems, geometry) with geometry = (w, h, cols, rows)."""
    patterns = PATTERNS_BLANK if blank else PATTERNS_AGAIN
    problems = []
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S7: [^\n]*", text)
    if len(got) != len(patterns):
        problems.append("expected exactly %d S7: lines, found %d" % (len(patterns), len(got)))
    errs = re.findall(r"ERR: [^\n]*", text)
    if errs:
        problems.append("the guest reported: %s" % "; ".join(errs[:3]))
    w = h = cols = rows = None
    ew = eh = None
    found = woken = None
    for i, (pattern, shape) in enumerate(patterns):
        line = got[i] if i < len(got) else ""
        m = re.fullmatch(pattern, line)
        if not m:
            problems.append("line %d: got '%s', want '%s'" % (i + 1, line, shape))
            continue
        if pattern == PATTERNS_AGAIN[1][0]:
            ew, eh = int(m.group(1)), int(m.group(2))
        elif pattern == PATTERNS_AGAIN[2][0]:
            w, h = int(m.group(1)), int(m.group(2))
            if (w, h) != (ew, eh):
                problems.append("line %d: the mode is %dx%d but the EDID prefers %dx%d" % (i + 1, w, h, ew, eh))
        elif pattern == PATTERNS_AGAIN[6][0]:
            found = int(m.group(1))
        elif pattern == PATTERNS_AGAIN[7][0]:
            woken = int(m.group(1))
        elif pattern == PATTERNS_AGAIN[8][0]:
            cols, rows = int(m.group(1)), int(m.group(2))
        elif pattern == DISK_LINE[0]:
            n, notes, home = int(m.group(2)), int(m.group(3)), int(m.group(4))
            if n != sectors:
                problems.append("line %d: the guest counted %d sectors, but the image is %d sectors" % (i + 1, n, sectors))
            if (notes, home) != (NOTES_FIRST, HOME_FIRST):
                problems.append("line %d: the partitions are at %d and %d, but DISK.md puts them at %d and %d"
                                % (i + 1, notes, home, NOTES_FIRST, HOME_FIRST))
        elif pattern == PATTERNS_AGAIN[10][0] and m.group(1) != notebook_want:
            problems.append("line %d: got 'S7: notebook %s', want 'S7: notebook %s'" % (i + 1, m.group(1), notebook_want))
        elif pattern == PATTERNS_AGAIN[11][0] and int(m.group(1)) != home_want:
            problems.append("line %d: got 'S7: home %s apps', want 'S7: home %d apps'" % (i + 1, m.group(1), home_want))
        elif pattern == PATTERNS_AGAIN[12][0] and m.group(1) != MAC:
            problems.append("line %d: the guest read MAC %s, but the harness gave the device %s" % (i + 1, m.group(1), MAC))
        elif pattern == PATTERNS_AGAIN[13][0]:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32 or addr % 4096 != 128 or int(m.group(2)) != BLOB_MAX:
                problems.append("line %d: the component region line %r is not what GLASS.md asks" % (i + 1, line))
        elif pattern == PATTERNS_AGAIN[14][0]:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32 or addr % 4096:
                problems.append("line %d: the obs page 0x%s is zero, above 4 GB or not page-aligned" % (i + 1, m.group(1)))
    if found is not None and found != smp:
        problems.append("cores found is %d, but the machine was given -smp %d" % (found, smp))
    if woken is not None and woken != smp:
        problems.append("cores woken is %d, but the machine was given -smp %d" % (woken, smp))
    if None not in (w, h, cols, rows) and (cols != w // 16 or rows != h // 16):
        problems.append("console claims %dx%d cells, but %dx%d pixels / 16 = %dx%d" % (cols, rows, w, h, w // 16, h // 16))
    return problems, (w, h, cols, rows)


def check_echo(capture, want):
    """The bytes after the ready line's CRLF must be exactly `want`."""
    marker = READY + b"\r\n"
    idx = capture.find(marker)
    if idx < 0:
        return ["no '%s' CRLF in the capture" % READY.decode()]
    tail = capture[idx + len(marker):]
    if tail == want:
        return []
    return ["after '%s' the serial channel carries %r, want %r" % (READY.decode(), tail, want)]


# ------------------------------------------------------------ the disk -----

def read_image(path):
    with open(path, "rb") as fh:
        return fh.read()


def extract_partition(image, which):
    """The partition's 16 MB written to stage7/out/<which>.part.img, so the
    frozen check_image and check_home judge it exactly as they judged an
    image; returns (path, table) or (None, problems)."""
    data = read_image(image)
    try:
        table = parse_gpt(data)
    except ValueError as exc:
        return None, ["the disk holds no GermOS table (DISK.md): %s - it is %s" % (exc, classify(data))]
    part = partition_bytes(data, table[which])
    if len(part) != PART_BYTES:
        return None, ["the %s partition is %d bytes, but DISK.md makes it %d" % (which, len(part), PART_BYTES)]
    path = os.path.join(OUT, which + ".part.img")
    with open(path, "wb") as fh:
        fh.write(part)
    return path, table


def check_notes_partition(data, notes, label):
    """The notes partition holds exactly these notes, byte-exact per
    NOTEBOOK.md's worked example, and nothing after them."""
    problems = []
    part = partition_bytes(data, parse_gpt(data)["notes"])
    try:
        got = parse_notebook(part)
    except ValueError as exc:
        return ["%s: the notes partition is not a notebook: %s" % (label, exc)]
    if got != notes:
        problems.append("%s: the notes partition holds %r, want %r" % (label, got, notes))
    want = expected_header(PART_BYTES)
    for i, text in enumerate(notes, 1):
        want += expected_record(i, text)
    want += bytes(SECTOR)                       # the sector after the last note: zero (or the format's zeroed sector 1)
    if part[:len(want)] != want:
        off = next(i for i in range(len(want)) if part[i] != want[i])
        problems.append("%s: the notes partition differs from NOTEBOOK.md's worked example at byte 0x%x" % (label, off))
    if any(part[len(want):]):
        problems.append("%s: the notes partition has bytes beyond its notes" % label)
    return problems


def check_home_partition(data, label, want=None):
    """The home partition parses by HOME.md; with want None it is freshly
    formatted - the header, sixteen empty entries, nothing else."""
    problems = []
    part = partition_bytes(data, parse_gpt(data)["home"])
    try:
        home = parse_home(part)
    except ValueError as exc:
        return ["%s: the home partition is not a home (HOME.md): %s" % (label, exc)]
    if want is None:
        if any(e for e in home["entries"]):
            problems.append("%s: the home partition holds entries after a format" % label)
        if any(part[9 * SECTOR:]):
            problems.append("%s: something beyond the home's table was written on a fresh partition" % label)
    return problems


def check_formatted(image, sectors, notes, home, label):
    """A blank disk after the guest's first boot: the table byte-exact, the
    two stores freshly formatted, everything else zero, the disk line's
    numbers the image's and the document's."""
    data = read_image(image)
    problems = []
    if len(data) // SECTOR != sectors:
        problems.append("%s: the guest's disk line says %d sectors, the image has %d" % (label, sectors, len(data) // SECTOR))
    if (notes, home) != (NOTES_FIRST, HOME_FIRST):
        problems.append("%s: the guest's disk line puts the partitions at %d and %d, DISK.md at %d and %d"
                        % (label, notes, home, NOTES_FIRST, HOME_FIRST))
    problems += ["%s: %s" % (label, p) for p in check_table(data)]
    if problems:
        return problems
    problems += check_notes_partition(data, [], label)
    problems += check_home_partition(data, label)
    # Everything the guest may have written, blanked; the rest must be zero.
    rest = bytearray(data)
    for lba in build_gpt(len(data) // SECTOR):
        rest[lba * SECTOR:(lba + 1) * SECTOR] = bytes(SECTOR)
    rest[NOTES_FIRST * SECTOR:(NOTES_FIRST + 2) * SECTOR] = bytes(2 * SECTOR)
    rest[HOME_FIRST * SECTOR:(HOME_FIRST + 9) * SECTOR] = bytes(9 * SECTOR)
    if any(rest):
        off = next(i for i in range(len(rest)) if rest[i])
        problems.append("%s: sector %d was written on a blank disk and is neither the table nor a store's header" % (label, off // SECTOR))
    return problems


def check_recognised(image, sectors, notes, home, label):
    data = read_image(image)
    problems = []
    if len(data) // SECTOR != sectors:
        problems.append("%s: the guest's disk line says %d sectors, the image has %d" % (label, sectors, len(data) // SECTOR))
    try:
        table = parse_gpt(data)
    except ValueError as exc:
        return problems + ["%s: the disk holds no GermOS table: %s" % (label, exc)]
    if (notes, home) != (table["notes"][0], table["home"][0]):
        problems.append("%s: the guest's disk line puts the partitions at %d and %d, the table at %d and %d"
                        % (label, notes, home, table["notes"][0], table["home"][0]))
    return problems


def write_foreign(image):
    """A 64 MB image with a valid table whose entry 0 carries another type
    GUID: DISK.md's classify says "gpt", and the guest must refuse it by
    that word and write nothing."""
    n = DISK_SECTORS
    entries = bytearray(partition_entries())
    entries[0:16] = guid_bytes(FOREIGN_TYPE)
    ecrc = crc32(bytes(entries))
    img = bytearray(DISK_BYTES_7)
    table = build_gpt(n)
    table[1] = gpt_header(n, 1, n - 1, 2, ecrc)
    table[n - 1] = gpt_header(n, n - 1, 1, n - 33, ecrc)
    for i in range(32):
        table[2 + i] = table[n - 33 + i] = bytes(entries[i * SECTOR:(i + 1) * SECTOR])
    for lba, b in table.items():
        img[lba * SECTOR:(lba + 1) * SECTOR] = b
    with open(image, "wb") as fh:
        fh.write(img)
    return classify(bytes(img))


def check_esp(before, after, efi, label):
    """The boot image across one boot: the guest wrote no table over it."""
    problems = []
    b, a = read_image(before), read_image(after)
    if len(a) != len(b):
        problems.append("%s: esp.img is %d bytes after the boot, %d before" % (label, len(a), len(b)))
    if a[:SECTOR] != b[:SECTOR]:
        problems.append("%s: esp.img's sector 0 changed during the boot" % label)
    word = classify(a)
    if word != "other":
        problems.append("%s: esp.img classifies as %r after the boot, want 'other' - a table was written over the boot image" % (label, word))
    out = os.path.join(OUT, "esp.after.efi")
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run(["mtype", "-i", after, "::/EFI/BOOT/BOOTX64.EFI"], stdout=open(out, "wb"), stderr=subprocess.PIPE)
    if r.returncode != 0 or read_image(out) != read_image(efi):
        problems.append("%s: BOOTX64.EFI read back from esp.img after the boot is not the build" % label)
    return problems


# --------------------------------------------------------------- main ------

def main(argv):
    if len(argv) == 5 and argv[0] in ("--formatted", "--recognised"):
        image, sectors, notes, home = argv[1], int(argv[2]), int(argv[3]), int(argv[4])
        fn = check_formatted if argv[0] == "--formatted" else check_recognised
        problems = fn(image, sectors, notes, home, os.path.basename(image))
        for p in problems:
            say("  - " + p)
        return 1 if problems else 0
    if len(argv) == 2 and argv[0] == "--foreign":
        word = write_foreign(argv[1])
        say("wrote %s: a valid table with a foreign type GUID, classified %r" % (argv[1], word))
        return 0 if word == "gpt" else 1
    if len(argv) == 4 and argv[0] == "--esp":
        problems = check_esp(argv[1], argv[2], argv[3], "esp")
        for p in problems:
            say("  - " + p)
        return 1 if problems else 0
    say("usage: checkdisk.py --formatted IMAGE SECTORS NOTES HOME | --recognised IMAGE SECTORS NOTES HOME | "
        "--foreign IMAGE | --esp BEFORE AFTER EFI | --persist SMP | --store")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
