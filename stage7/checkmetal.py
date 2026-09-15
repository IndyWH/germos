#!/usr/bin/env python3
"""Stage 7 ring 7c acceptance checker - the metal, rehearsed in the twin of
the HP: the stick parsed from the host, the machine booted from a COPY of
the stick over qemu-xhci + usb-storage with a SATA disk and the e1000e, and
every stage re-proven in one scripted run.

Modes (all from the repo root, invoked by stage7/test-7c.sh):

  --stick            test 1's second half: stage7/out/stick.img as
                     stage7/mkstick.py wrote it, before any boot - the
                     protective MBR, both GPT headers and both entry arrays,
                     exactly one partition of the EFI System type, and
                     EFI/BOOT/BOOTX64.EFI read back with mtools at the
                     partition's offset byte-identical to the build.
  --serial MODE SMP  test 2: one boot from a fresh copy of the stick with
                     the SATA disk on ide.1 and the e1000e cage to the relay's
                     port (nothing is asked). MODE blank: a fresh disk,
                     nineteen S7: lines; again: the same disk, eighteen;
                     novga: a fresh disk on a display that is NOT QEMU's VGA
                     (virtio-vga), "S7: edid none" and the highest mode. On
                     every boot: the i8042: pair once each, in order, after
                     "S7: glass core" and before "S7: keyboard ready", and the
                     stick copy's tables unchanged afterwards.
  --stages           test 3: every stage re-proven in one scripted run of
                     two boots at -smp 4 (plan-7c.md deviation 6).
  --cage             test 4: the argv checks, the relay's bind rule, the
                     payload table and the spot checks.

The counts a run must give are the length of a pattern list or the value a
frozen document's rule gives - never a literal typed from arithmetic; the
one literal from a run (the novga mode) is the plan's item 1 measurement.
Written before the guest code it judges and frozen behind the hook once
written. Everything it starts is QEMU with OVMF, the patient's CPU model,
the display, the caged network to the relay on 127.0.0.1, and drives that
are raw files under stage7/out/metal/. It talks only to the mock broker
(broker/wire.py --mock) and never spends a token.
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
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "stage7", "out")
METAL_OUT = os.path.join(OUT, "metal")
STICK = os.path.join(OUT, "stick.img")
EFI = os.path.join(OUT, "BOOTX64.EFI")
ESP = os.path.join(OUT, "esp.img")               # the twin's boot image (broker/wire.py's twin), not this checker's
DISK = os.path.join(METAL_OUT, "disk.img")
BROKER = os.path.join(REPO, "broker", "wire.py")
RELAY = os.path.join(REPO, "broker", "relay.py")
PLANS_DIR = os.path.join(REPO, "plans")
GERMLINE = os.path.join(METAL_OUT, "germline")
REHEARSAL = os.path.join(METAL_OUT, "rehearsal")
TWIN_WORKDIR = os.path.join(REHEARSAL, "twin")
OVMF = "/usr/share/ovmf/OVMF.fd"
HOOK = os.path.join(REPO, ".claude", "hooks", "protect-tests.py")
PAYLOADS = os.path.join(REPO, ".claude", "hooks", "payloads.py")

sys.path.insert(0, os.path.join(REPO, "stage6"))
sys.path.insert(0, os.path.join(REPO, "stage7"))
sys.path.insert(0, os.path.join(REPO, "broker"))
import checkdisk  # noqa: E402  - ring 7a's frozen checker: the disk side
from checkdisk import (check_notes_partition, check_partitions, check_table, read_image, check_echo,  # noqa: E402
                       check_formatted, DISK_SECTORS)
import checkwire  # noqa: E402  - ring 7b's frozen checker: the wire side and the argv rule
from checkwire import (PATTERNS_BLANK as PATTERNS_BLANK_7B, PATTERNS_AGAIN as PATTERNS_AGAIN_7B,  # noqa: E402
                       NIC_LINE, MAC, check_argv_7b, check_bind_rule, check_relay_log, question_bytes,
                       read_relay_log, check_germline_entry_7b, check_install_germline_7b)
from checkglass import (say, report, dump_capture, check_region_rows, record_count, PROMPT,  # noqa: E402
                        NO_ANSWER, SETTLE, CANNED, read_record, check_question_entry, check_grow_entry,
                        check_app_panel, check_mode_field, check_choices, check_counts,
                        fixture_self_check, germline_entries, port_state, stop_mock)
from checkplans import (check_install_entry, check_one_cell_panel, DATA_FIRST, CHOICES_ECHO_RUNNING,  # noqa: E402
                        ECHO_TESTS_OK)
from checkpointer import (Pointer, expected_counts, check_arrow_at, check_pointer_counts, check_i8042,  # noqa: E402
                          check_strip_6c, target_col, park_cell, CELL)
from glass import (regions, app_frame, grow_request, TEST_CHOICES)  # noqa: E402
from pointer import (choice_targets, parse_obs_6c, OBS_PAGE_BYTES_6C)  # noqa: E402
import twin  # noqa: E402
from twin import Driver  # noqa: E402
from plans import plan_keyname  # noqa: E402
from rehearse import KEY_GAP  # noqa: E402
import metal  # noqa: E402
import wire  # noqa: E402
import mkstick  # noqa: E402  - the builder's constants and its table

# ---------------------------------------------------------- the machine ---
# The twin of the HP (plan-7c.md decision 9): q35, the patient's CPU, the
# display, the stick over xhci + usb-storage, the SATA disk on ide.1, the
# e1000e cage to the relay. No esp.img in any command of this checker's own.

CPU = ["-cpu", "IvyBridge"]
DISPLAY = ["-vga", "none", "-device", "VGA,edid=on,xres=1920,yres=1080"]
NOVGA = ["-vga", "none", "-device", "virtio-vga,edid=on"]       # a display that is not QEMU's VGA
NOVGA_MODE = (1920, 1080)        # the highest mode OVMF lists for virtio-vga, measured at item 1
BROKER_PORT = 9999
REHEARSAL_PORT = 9998
RELAY_PORT = 9997
CAGE_NETDEV = ("user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:%d-cmd:nc -N 127.0.0.1 %d"
               % (BROKER_PORT, RELAY_PORT))
CAGE_DEVICE = "e1000e,netdev=n0,mac=" + MAC
READY = b"S7: keyboard ready"
MOUSE_LINE = "S7: mouse ready"
MOUSE_LINE_BYTES = MOUSE_LINE.encode() + b"\r\n"

# ------------------------------------------------------- the serial lines --
# Ring 7b's lists with the EDID line in either form: "S7: edid WxH" under
# QEMU's VGA, "S7: edid none" on any other display (plan-7c.md decision 1).
# The count is the length of the list - never a literal.

EDID_LINE = (r"S7: edid (?:(\d+)x(\d+)|none)", "S7: edid <W>x<H> | S7: edid none")
assert PATTERNS_AGAIN_7B[1][1] == "S7: edid <W>x<H>"
PATTERNS_AGAIN = [PATTERNS_AGAIN_7B[0], EDID_LINE] + PATTERNS_AGAIN_7B[2:]
PATTERNS_BLANK = PATTERNS_AGAIN[:9] + [(r"S7: gpt written", "S7: gpt written")] + PATTERNS_AGAIN[9:]
assert len(PATTERNS_BLANK) == len(PATTERNS_BLANK_7B)
GLASS_LINE = PATTERNS_AGAIN[16][0]
assert GLASS_LINE.startswith("S7: glass core")
DISK_LINE = checkdisk.DISK_LINE
BLOB_MAX = 1048576

# The i8042 cold init's two lines, with their own prefix so no frozen S7:
# counter sees them (decision 1): the controller's self-test, then the
# mouse's reset - "reset ok" in the twin, which always has a mouse.
I8042_LINES = ["i8042: self-test ok", "i8042: mouse reset ok"]


def check_boot_lines(capture, smp, blank, notebook_want, home_want, sectors, vga=True):
    """The S7: lines in order, self-consistent: nineteen on a formatting
    boot, eighteen on a recognising one; the EDID line "WxH" equal to the
    gop line under QEMU's VGA, "none" and the gop line NOVGA_MODE on the
    other display; the nic line the e1000e's MAC; "S7: link up" after it.
    Returns (problems, geometry) with geometry = (w, h, cols, rows)."""
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
    edid_none = False
    found = woken = None
    for i, (pattern, shape) in enumerate(patterns):
        line = got[i] if i < len(got) else ""
        m = re.fullmatch(pattern, line)
        if not m:
            problems.append("line %d: got '%s', want '%s'" % (i + 1, line, shape))
            continue
        if pattern == EDID_LINE[0]:
            if m.group(1) is None:
                edid_none = True
                if vga:
                    problems.append("line %d: 'S7: edid none' under QEMU's VGA, which carries an EDID" % (i + 1))
            else:
                ew, eh = int(m.group(1)), int(m.group(2))
                if not vga:
                    problems.append("line %d: '%s' on a display that is not QEMU's VGA - BAR2 was read as an EDID" % (i + 1, line))
        elif pattern == PATTERNS_AGAIN[2][0]:
            w, h = int(m.group(1)), int(m.group(2))
            if vga and (w, h) != (ew, eh):
                problems.append("line %d: the mode is %dx%d but the EDID prefers %sx%s" % (i + 1, w, h, ew, eh))
            if not vga and (w, h) != NOVGA_MODE:
                problems.append("line %d: the mode is %dx%d, but the highest mode this display lists is %dx%d"
                                % (i + 1, w, h, NOVGA_MODE[0], NOVGA_MODE[1]))
        elif pattern == PATTERNS_AGAIN[6][0]:
            found = int(m.group(1))
        elif pattern == PATTERNS_AGAIN[7][0]:
            woken = int(m.group(1))
        elif pattern == PATTERNS_AGAIN[8][0]:
            cols, rows = int(m.group(1)), int(m.group(2))
        elif pattern == DISK_LINE[0]:
            port, n, notes, home = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            if port != 1:
                problems.append("line %d: the disk is on port %d, but with no boot image on SATA the one disk is on port 1" % (i + 1, port))
            if n != sectors:
                problems.append("line %d: the guest counted %d sectors, but the image is %d sectors" % (i + 1, n, sectors))
            if (notes, home) != (metal.NOTES_FIRST, metal.HOME_FIRST):
                problems.append("line %d: the partitions are at %d and %d, but DISK.md puts them at %d and %d"
                                % (i + 1, notes, home, metal.NOTES_FIRST, metal.HOME_FIRST))
        elif pattern == PATTERNS_AGAIN[10][0] and m.group(1) != notebook_want:
            problems.append("line %d: got 'S7: notebook %s', want 'S7: notebook %s'" % (i + 1, m.group(1), notebook_want))
        elif pattern == PATTERNS_AGAIN[11][0] and int(m.group(1)) != home_want:
            problems.append("line %d: got 'S7: home %s apps', want 'S7: home %d apps'" % (i + 1, m.group(1), home_want))
        elif pattern == NIC_LINE[0] and m.group(1) != MAC:
            problems.append("line %d: the guest read MAC %s, but the e1000e carries %s" % (i + 1, m.group(1), MAC))
        elif pattern == PATTERNS_AGAIN[14][0]:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32 or addr % 4096 != 128 or int(m.group(2)) != BLOB_MAX:
                problems.append("line %d: the component region line %r is not what GLASS.md asks" % (i + 1, line))
        elif pattern == PATTERNS_AGAIN[15][0]:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32 or addr % 4096:
                problems.append("line %d: the obs page 0x%s is zero, above 4 GB or not page-aligned" % (i + 1, m.group(1)))
    if not vga and not edid_none and not problems:
        problems.append("the display is not QEMU's VGA, yet no 'S7: edid none' line")
    if found is not None and found != smp:
        problems.append("cores found is %d, but the machine was given -smp %d" % (found, smp))
    if woken is not None and woken != smp:
        problems.append("cores woken is %d, but the machine was given -smp %d" % (woken, smp))
    if None not in (w, h, cols, rows) and (cols != w // 16 or rows != h // 16):
        problems.append("console claims %dx%d cells, but %dx%d pixels / 16 = %dx%d" % (cols, rows, w, h, w // 16, h // 16))
    problems += check_i8042_lines(text)
    return problems, (w, h, cols, rows)


def check_i8042_lines(text):
    """The cold init's two lines, each exactly once, in order, after the
    glass core's line and before the keyboard's; no i8042: line anywhere
    else (plan-7c.md decision 1, A6)."""
    problems = []
    lines = text.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("i8042: ")]
    got = [lines[i] for i in idx]
    if got != I8042_LINES:
        problems.append("the i8042: lines are %r, want exactly %r in that order" % (got, I8042_LINES))
        return problems
    glass = [i for i, l in enumerate(lines) if re.fullmatch(GLASS_LINE, l)]
    ready = [i for i, l in enumerate(lines) if l == READY.decode()]
    if not glass or not ready:
        problems.append("no glass core line or no ready line to place the i8042: lines between")
    elif not (glass[0] < idx[0] < idx[1] < ready[0]):
        problems.append("the i8042: lines are not between 'S7: glass core' and '%s'" % READY.decode())
    return problems


def strip_mouse_line(capture):
    """The raw line after the ready line, once the first packet has
    arrived - and the capture without it, so the line count and the echo
    check judge the rest (checkpointer's idiom, S7:). Returns (problems,
    stripped)."""
    problems = []
    n = capture.count(MOUSE_LINE_BYTES)
    if n != 1:
        problems.append("'%s' appears %d time(s) on serial, want exactly once after the first packet" % (MOUSE_LINE, n))
        return problems, capture.replace(MOUSE_LINE_BYTES, b"")
    ready_at = capture.find(READY + b"\r\n")
    mouse_at = capture.find(MOUSE_LINE_BYTES)
    if ready_at < 0 or mouse_at < ready_at:
        problems.append("'%s' came before '%s' - it is not a boot line" % (MOUSE_LINE, READY.decode()))
    return problems, capture.replace(MOUSE_LINE_BYTES, b"", 1)


# --------------------------------------------------------------- the stick --
# Test 1's second half (plan-7c.md decision 9, deviation 5): the file as
# built, never a booted copy. The constants are the builder's.

ESP_TYPE = uuid.UUID("C12A7328-F81F-11D2-BA4B-00A0C93EC93B")


def check_stick(path=STICK, efi=EFI):
    problems = []
    try:
        data = read_image(path)
    except OSError as exc:
        return ["the stick: %s" % exc]
    n = len(data) // metal.SECTOR
    if len(data) % metal.SECTOR or n != mkstick.STICK_SECTORS:
        problems.append("the stick is %d bytes, want %d sectors of %d" % (len(data), mkstick.STICK_SECTORS, metal.SECTOR))
        return problems
    S = metal.SECTOR
    mbr = data[:S]
    if mbr[510:512] != b"\x55\xAA":
        problems.append("sector 0 lacks the boot signature")
    entries_mbr = [mbr[446 + 16 * i:462 + 16 * i] for i in range(4)]
    if entries_mbr[0][4] != 0xEE or struct.unpack_from("<I", entries_mbr[0], 8)[0] != 1:
        problems.append("the protective MBR's first entry is not type 0xEE starting at LBA 1: %s" % entries_mbr[0].hex())
    if any(any(e) for e in entries_mbr[1:]):
        problems.append("the protective MBR carries more than one entry")
    # the primary header by DISK.md's own reader; the backup by the same rule mirrored
    try:
        ecrc, usable = metal.parse_header(data[S:2 * S], n)
    except ValueError as exc:
        problems.append("the primary GPT header: %s" % exc)
        return problems
    entries = data[2 * S:(2 + metal.ENTRY_SECTORS) * S]
    if metal.crc32(entries) != ecrc:
        problems.append("the entry array's CRC does not match the header")
    back = data[(n - 1) * S:n * S]
    bh = back[:metal.HEADER_SIZE]
    if bh[0:8] != b"EFI PART":
        problems.append("the backup header at the last LBA has no signature")
    else:
        rev, size, hcrc, res, my, alt, first, last = struct.unpack_from("<IIIIQQQQ", bh, 8)
        elba, count, esize, becrc = struct.unpack_from("<QIII", bh, 72)
        if metal.crc32(bh[:16] + bytes(4) + bh[20:]) != hcrc:
            problems.append("the backup header's CRC does not match")
        if (my, alt, elba, count, esize, becrc) != (n - 1, 1, n - 1 - metal.ENTRY_SECTORS, metal.ENTRIES, metal.ENTRY, ecrc):
            problems.append("the backup header does not mirror the primary: MyLBA %d alt %d entries at %d (%d of %d) crc %#x"
                            % (my, alt, elba, count, esize, becrc))
        if (first, last) != usable:
            problems.append("the backup header's usable range %r differs from the primary's %r" % ((first, last), usable))
        if any(back[metal.HEADER_SIZE:]):
            problems.append("the backup header's tail is not zero")
    if data[(n - 1 - metal.ENTRY_SECTORS) * S:(n - 1) * S] != entries:
        problems.append("the backup entry array differs from the primary")
    try:
        parsed = metal.parse_entries(entries, usable)
    except ValueError as exc:
        problems.append("the entry array: %s" % exc)
        return problems
    if len(parsed) != 1:
        problems.append("the table holds %d partitions, want exactly one (the ESP)" % len(parsed))
    else:
        e = parsed[0]
        if e["type"] != ESP_TYPE:
            problems.append("the one partition's type is %s, want the EFI System Partition's %s" % (e["type"], ESP_TYPE))
        if (e["first"], e["last"]) != (mkstick.ESP_FIRST, mkstick.ESP_LAST):
            problems.append("the ESP spans %d..%d, want %d..%d (64 MB at 1 MiB)" % (e["first"], e["last"], mkstick.ESP_FIRST, mkstick.ESP_LAST))
        if e["sectors"] != mkstick.ESP_SECTORS:
            problems.append("the ESP is %d sectors, want %d" % (e["sectors"], mkstick.ESP_SECTORS))
    if metal.classify(data) != "gpt":
        problems.append("DISK.md's classify says %r, want 'gpt' - a table that is not GermOS's, which the AHCI driver refuses" % metal.classify(data))
    # the table as the builder spells it, sector for sector
    for lba, want in mkstick.build_table(n).items():
        if data[lba * S:(lba + 1) * S] != want:
            problems.append("sector %d is not what the builder's table spells" % lba)
            break
    # the file inside, by mtools at the offset
    at = "%s@@%d" % (path, mkstick.ESP_OFFSET)
    r = subprocess.run(["mdir", "-i", at, "::/EFI/BOOT"], capture_output=True, text=True)
    if r.returncode or not re.search(r"^BOOTX64 +EFI ", r.stdout, re.M):
        problems.append("mdir at the partition's offset does not list BOOTX64.EFI under ::/EFI/BOOT: %s" % (r.stderr.strip() or r.stdout.strip())[:200])
    out = os.path.join(METAL_OUT, "stick.extracted.efi")
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run(["mtype", "-i", at, "::/EFI/BOOT/BOOTX64.EFI"], stdout=open(out, "wb"), stderr=subprocess.PIPE)
    if r.returncode or read_image(out) != read_image(efi):
        problems.append("BOOTX64.EFI read back from the stick's ESP is not byte-identical to %s" % os.path.relpath(efi, REPO))
    return problems


def check_stick_tables_unchanged(copy, label, built=STICK):
    """A booted copy of the stick: its MBR, both headers and both entry
    arrays are the built stick's (the FAT may differ: the firmware's own
    variable store lives there)."""
    try:
        a, b = read_image(built), read_image(copy)
    except OSError as exc:
        return ["%s: %s" % (label, exc)]
    if len(a) != len(b):
        return ["%s: the stick copy is %d bytes after the boot, %d before" % (label, len(b), len(a))]
    S = metal.SECTOR
    for lba in sorted(mkstick.build_table(len(a) // S)):
        if a[lba * S:(lba + 1) * S] != b[lba * S:(lba + 1) * S]:
            return ["%s: sector %d of the stick copy changed during the boot - a table was written on the stick" % (label, lba)]
    return []


def run_stick():
    problems = check_stick()
    if not report("the stick is not what plan-7c.md asks for", problems):
        return 1
    say("stick.img: %d sectors, a protective MBR, both GPT headers and arrays with their CRCs, one EFI System Partition at "
        "%d..%d (%d sectors), classify 'gpt'; EFI/BOOT/BOOTX64.EFI read back at the offset byte-identical to the build"
        % (mkstick.STICK_SECTORS, mkstick.ESP_FIRST, mkstick.ESP_LAST, mkstick.ESP_SECTORS))
    return 0


# ------------------------------------------------------------- the driver ---
# The checker's own QEMU command and monitor driver: the stick copy over
# xhci + usb-storage, the SATA disk, the e1000e cage; the step vocabulary
# is ring 6b's plus ring 6c's mouse steps.

def fresh_disk(path):
    if os.path.exists(path):
        os.remove(path)
    with open(path, "wb") as fh:
        fh.truncate(metal.DISK_BYTES_7)


def fresh_stick(copy):
    """A copy of the built stick for one boot: QEMU locks the file it
    boots from, and the built file is what the owner flashes."""
    shutil.copyfile(STICK, copy)
    return copy


def qemu_argv(smp, disk, stick_copy, serial_path, display=DISPLAY):
    """The one place the checker's QEMU command is spelled. Test 4 inspects this."""
    return [
        "qemu-system-x86_64",
        "-machine", "q35",
    ] + list(CPU) + [
        "-m", "256M",
        "-smp", str(smp),
        "-bios", OVMF,
    ] + list(display) + [
        "-device", "qemu-xhci",
        "-drive", "if=none,id=stick,format=raw,file=" + stick_copy,
        "-device", "usb-storage,drive=stick",
        "-drive", "if=none,id=d0,format=raw,file=" + disk,
        "-device", "ide-hd,drive=d0,bus=ide.1",
        "-netdev", CAGE_NETDEV,
        "-device", CAGE_DEVICE,
        "-display", "none",
        "-serial", "file:" + serial_path,
        "-monitor", "stdio",
    ]


def geometry_of(capture):
    m = re.search(rb"S7: gop (\d+)x(\d+) fb 0x", capture)
    return (int(m.group(1)), int(m.group(2))) if m else None


def drive(smp, disk, stick_copy, steps, serial_path, ready=READY, ready_limit=60.0, display=DISPLAY):
    """Boot from the stick copy inside the cage, wait for the guest's own
    ready line, run the steps, quit, reap. Steps: ("type", text),
    ("sleep", s), ("wait_record", path, count, timeout), ("shot", path),
    ("obs", label) - the page parsed by the 6c section's parser -,
    ("surfaces", label), ("serial", label), ("mouse", dx, dy), ("button",
    mask[, "hit"]), ("moveto", row, col). Returns (serial_bytes, reads,
    events, error); reads["counts"][label] and reads["model"][label] as
    checkpointer's driver keeps them. Never leaves a QEMU running."""
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

    proc = subprocess.Popen(qemu_argv(smp, disk, stick_copy, serial_path, display),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    drv = Driver(proc, serial_path, METAL_OUT)
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
                errs = re.findall(rb"ERR: [^\r\n]*", drv.serial_bytes())
                if errs:
                    err += " (the guest said: %s)" % errs[0].decode(errors="replace")
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
                        m = re.search(r"S7: obs page 0x([0-9a-f]{16})", text)
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


# ------------------------------------------------- test 2: the serial boots --

def run_serial(mode, smp):
    """One boot from a fresh stick copy: blank (a fresh disk, nineteen
    lines), again (the same disk, eighteen), novga (a fresh disk on
    virtio-vga: edid none, the highest mode). On every boot the i8042:
    pair and the stick copy's tables unchanged."""
    if mode not in ("blank", "again", "novga"):
        say("usage: --serial blank|again|novga SMP")
        return 1
    disk = DISK
    if mode != "again":
        fresh_disk(disk)
    elif not os.path.isfile(disk):
        say("--serial again wants the disk the blank boot formatted; none at %s" % os.path.relpath(disk, REPO))
        return 1
    copy = fresh_stick(os.path.join(METAL_OUT, "stick.%s.img" % mode))
    before = read_image(disk)
    serial = os.path.join(METAL_OUT, "serial.%s.%d.txt" % (mode, smp))
    shot = os.path.join(METAL_OUT, "screen.%s.%d.ppm" % (mode, smp))
    display = NOVGA if mode == "novga" else DISPLAY
    say("%s: -smp %d, the stick copy over xhci + usb-storage, the SATA disk on ide.1, the e1000e; display %s"
        % (mode, smp, " ".join(display[3:])))
    capture, reads, events, err = drive(smp, disk, copy, [("sleep", 1.0), ("shot", shot)], serial, display=display)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    ok = True
    blank = mode != "again"
    problems, geometry = check_boot_lines(capture, smp, blank, "formatted" if blank else "0 notes", 0, DISK_SECTORS,
                                          vga=(mode != "novga"))
    problems += check_echo(capture, b"")
    ok &= report("the serial log is not what plan-7c.md asks for", problems, capture)
    if not problems:
        say("%d S7: lines in order, mode %dx%d, found = woken = %d, disk port 1, nic %s, link up; the i8042: pair between "
            "the glass core and the keyboard; nothing on the wire after ready"
            % (len(PATTERNS_BLANK if blank else PATTERNS_AGAIN), geometry[0], geometry[1], smp, MAC))

    problems = check_stick_tables_unchanged(copy, mode)
    if mode == "again":
        if read_image(disk) != before:
            problems.append("the disk changed on a recognising boot - the table was rewritten")
    ok &= report("the stick copy or the disk is not what it should be after the boot", problems)
    if not problems:
        say("the stick copy's MBR, both headers and both arrays unchanged%s" % ("; the disk byte-identical" if mode == "again" else ""))

    if None in geometry:
        return 1
    regs = regions(geometry[2], geometry[3])
    problems = check_region_rows(shot, geometry, regs["conversation"], I8042_LINES + [READY.decode(), PROMPT])
    problems += check_mode_field(shot, geometry, "prompt")
    ok &= report("the screen is not drawn at the mode the guest printed", problems)
    if not problems:
        say("the screen: the boot log's last lines - the i8042: pair and the ready line - above the prompt, 'prompt' on the strip, drawn at %dx%d" % geometry[:2])
    say("%s at -smp %d: %s" % (mode, smp, "the metal configuration booted from the stick" if ok else "not what plan-7c.md asks"))
    return 0 if ok else 1


# --------------------------------------------------------------- main ------

def main(argv):
    os.makedirs(METAL_OUT, exist_ok=True)
    if argv == ["--stick"]:
        return run_stick()
    if len(argv) == 3 and argv[0] == "--serial":
        try:
            return run_serial(argv[1], int(argv[2]))
        except ValueError:
            pass
    say("usage: checkmetal.py --stick | --serial blank|again|novga SMP | --stages | --cage")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
