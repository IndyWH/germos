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
                        CHOICES_PROMPT_ECHO,
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


# ------------------------------------------------ the relay and the mock ---
# checkwire's lifecycles, bound to this ring's scratch: the relay on 9997
# logging, forwarding to the mock on 9999; broker/wire.py --mock with the
# metal germline (wiped), the gate's esp.img as the twin's image, the
# twin's own workdir, its record file.

def start_relay(log_path):
    if port_state(RELAY_PORT) == "open":
        return None, "something is already listening on 127.0.0.1:%d - the gate talks only to its own relay" % RELAY_PORT
    if os.path.exists(log_path):
        os.remove(log_path)
    errlog = open(os.path.join(METAL_OUT, "relay.stderr.txt"), "ab")
    proc = subprocess.Popen(
        [sys.executable, RELAY, "--bind", "127.0.0.1", "--port", str(RELAY_PORT),
         "--broker-port", str(BROKER_PORT), "--log", log_path],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=errlog)
    deadline = time.time() + 10.0
    line = b""
    while time.time() < deadline:
        if proc.poll() is not None:
            return proc, "the relay exited %d before listening" % proc.returncode
        r, _, _ = select.select([proc.stdout], [], [], 0.2)
        if r:
            line = proc.stdout.readline()
            break
    want = "relay listening on 127.0.0.1:%d -> 127.0.0.1:%d" % (RELAY_PORT, BROKER_PORT)
    if line.strip() != want.encode():
        stop_mock(proc)
        return None, "the relay did not say it was listening (got %r, want %r)" % (line, want)
    return proc, None


def start_mock(record_path, wipe_germline=True):
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
    log = open(os.path.join(METAL_OUT, "mock.wire.stderr.txt"), "ab")
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


# ------------------------------------- test 3: every stage in one run -----
# plan-7c.md deviation 6: two boots at -smp 4 from one stick copy on one
# disk. Boot A, the relay and the mock up: Stage 2's typing and the note,
# Stage 4's "? ping", ring 6a's "! test app" in its panel, ring 6b's
# "! install echo" rehearsed in wire.py's twin. Boot B, nothing on the
# wire: the note back (Stage 3), the arrow on the first move and a click on
# "! echo" launching it from the home partition (ring 6c's click, ring 6b's
# launch), a key to it, the strip with the pointer field, Esc.

STAGES_SMP = 4
FIRST_NOTE = "first note"


def run_stages():
    smp = STAGES_SMP
    blobs = {}
    for name in ("app", "echo"):
        blob, problems = fixture_self_check(name)
        if not report("the %s fixture is not what the repository says" % name, problems):
            return 1
        blobs[name] = blob
    app, echo = blobs["app"], blobs["echo"]
    say("the two fixtures reproduce their binaries")

    record = os.path.join(METAL_OUT, "broker.stages.jsonl")
    rlog = os.path.join(METAL_OUT, "relay.stages.jsonl")
    shots = {k: os.path.join(METAL_OUT, "screen.stages.%s.ppm" % k) for k in ("a", "n", "l")}
    relay, err = start_relay(rlog)
    if err:
        say(err)
        return 1
    mock, err = start_mock(record)
    if err:
        say(err)
        stop_mock(relay)
        return 1
    say("boot A: the relay on %d -> the mock on %d (germline wiped), a fresh disk, a fresh stick copy, -smp %d; "
        "%r, '? ping', '! test app', a key, Esc, '! install echo', Esc" % (RELAY_PORT, BROKER_PORT, smp, FIRST_NOTE))
    copy = fresh_stick(os.path.join(METAL_OUT, "stick.stages.img"))
    try:
        fresh_disk(DISK)
        steps = [
            ("type", FIRST_NOTE + "\n"), ("sleep", 1.5),
            ("type", "? ping\n"), ("wait_record", record, 1, 20.0), ("sleep", SETTLE),
            ("type", "! test app\n"), ("wait_record", record, 2, 150.0), ("sleep", 3.0),
            ("type", "k"), ("sleep", 1.0), ("shot", shots["a"]),
            ("type", "\x1b"), ("sleep", 2.0),
            ("type", "! install echo\n"), ("wait_record", record, 3, 150.0), ("sleep", 3.0),
            ("type", "\x1b"), ("sleep", 1.0),
            ("obs", "e"),
        ]
        capture, reads, events, err = drive(smp, DISK, copy, steps, os.path.join(METAL_OUT, "serial.stages.a.txt"))
    finally:
        stop_mock(mock)
        entries_relay = read_relay_log(rlog, want=3)
        stop_mock(relay)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1

    ok = True
    problems, geometry = check_boot_lines(capture, smp, True, "formatted", 0, DISK_SECTORS)
    problems += check_echo(capture, (FIRST_NOTE + "\r\n? ping\r\n! test app\r\n! install echo\r\n").encode())
    ok &= report("boot A's serial log is not what plan-7c.md asks for", problems, capture)
    if not problems:
        say("boot A: %d S7: lines with the i8042: pair, nic %s, link up; the wire after ready carries exactly the four typed lines"
            % (len(PATTERNS_BLANK), MAC))

    app_answer = app_frame(app, b"test app", TEST_CHOICES, 0)
    echo_answer = app_frame(echo, b"echo", [], 0, installed=1)
    entries, problems = read_record(record)
    if entries is not None:
        if len(entries) != 3:
            problems.append("the broker saw %d connection(s), want 3" % len(entries))
        if len(entries) >= 1:
            problems += check_question_entry(1, entries[0], "ping")
        if len(entries) >= 2:
            problems += check_grow_entry(2, entries[1], "test app", "generated", 1, ["pass"], "app", app_answer, name="test app")
        if len(entries) >= 3:
            problems += check_install_entry(3, entries[2], "install echo", "generated", 2, ["pass"], "app", echo_answer,
                                            plan="echo", tests=ECHO_TESTS_OK)
    ok &= report("the record is not what UMBILICAL.md, GLASS.md and PLANS.md ask for", problems)
    if not problems:
        say("the record: 'ping' answered; 'test app' generated (call 1), rehearsed once, the app frame; 'install echo' generated "
            "(call 2), rehearsed once against the plan's five tests, the frame with installed 1")

    wants = [question_bytes("ping"),
             (len(grow_request(b"test app")), len(app_answer)),
             (len(grow_request(b"install echo")), len(echo_answer))]
    problems = check_relay_log(entries_relay, wants, "the relay")
    if entries is not None and len(entries_relay) != len(entries):
        problems.append("the relay logged %d connection(s) but the broker recorded %d" % (len(entries_relay), len(entries)))
    ok &= report("the relay's log does not agree with the record (WIRE.md, the relay)", problems)
    if not problems:
        say("the relay logged the same three connections: the question's frames, GERMLINE.md's two request frames and the two app frames")

    problems = check_germline_entry_7b(GERMLINE, "test app", app, "test app", TEST_CHOICES)
    problems += check_install_germline_7b(GERMLINE, "echo", echo, tests=ECHO_TESTS_OK)
    names = germline_entries(GERMLINE)
    if len(names) != 2:
        problems.append("the germline holds %d entries %r, want exactly 2" % (len(names), names))
    ok &= report("the germline is not what WIRE.md asks for", problems)
    if not problems:
        say("the germline holds exactly two entries, each with a %d-line S7: rehearsal log carrying 'S7: link up' and the virtio disk untouched"
            % len(PATTERNS_BLANK))

    data = read_image(DISK)
    problems = ["the disk: " + p for p in check_table(data)]
    if not problems:
        problems += check_notes_partition(data, [FIRST_NOTE], "the notebook")
    more, _ = check_partitions(DISK, [FIRST_NOTE], {"echo": {"current": (echo, DATA_FIRST), "previous": None, "choices": []}}, "the install")
    problems += more
    tdisk = metal.twin_disk(TWIN_WORKDIR)
    try:
        tdata = read_image(tdisk)
        ttable = metal.parse_gpt(tdata)
        tnotes = checkdisk.parse_notebook(metal.partition_bytes(tdata, ttable["notes"]))
        if tnotes != ["after"]:
            problems.append("the twin's SATA disk holds notes %r, want ['after']" % (tnotes,))
        problems += ["the twin's table: " + p for p in check_table(tdata)]
    except (OSError, ValueError) as exc:
        problems.append("the twin's SATA disk is not a GermOS disk with a notebook: %s" % exc)
    try:
        if any(read_image(os.path.join(TWIN_WORKDIR, "notes.img"))):
            problems.append("the twin's virtio notes.img was written - virtio-blk code ran in the twin")
    except OSError as exc:
        problems.append("the twin's virtio notes.img: %s" % exc)
    problems += check_stick_tables_unchanged(copy, "boot A")
    ok &= report("the disks after boot A are not what DISK.md, NOTEBOOK.md, HOME.md and the twin ask for", problems)
    if not problems:
        say("the notes partition holds exactly %r - the question and the requests were not journaled; the home partition holds echo at "
            "partition sector %d hash-checked; the twin's disk formatted with 'after' on SATA and its virtio image all zero; "
            "the stick copy's tables unchanged" % (FIRST_NOTE, DATA_FIRST))
    shutil.copyfile(DISK, os.path.join(METAL_OUT, "disk.after-a.img"))

    if None in geometry:
        say("no picture to judge - boot A's boot lines were wrong")
        return 1
    problems = check_app_panel(shots["a"], geometry, "k")
    problems += check_mode_field(shots["a"], geometry, "running test app")
    if "e" not in reads:
        problems.append("the obs page could not be read after the install")
    else:
        problems += check_counts(reads["e"], {"mode": 0, "questions": 1, "notes": 1, "wire_conns": len(entries_relay),
                                              "grows_generated": 2, "grows_served": 0, "errors": 0}, "after the install")
        problems += check_i8042(reads["e"], "after the install")
    ok &= report("screen A or the obs page after the install is not the truth", problems)
    if not problems:
        say("screen A: the test app's strips with 'key: k' and 'running test app'; the obs page: questions 1, notes 1, wire_conns %d = "
            "the relay's connections, grows_generated 2, grows_served 0 (GLASS.md: frames whose source byte is 1 - both were generated), "
            "the i8042 command byte as GLASS.md says" % len(entries_relay))

    # ------------------------------------------------ boot B: nothing on the wire
    for port in (BROKER_PORT, RELAY_PORT):
        if port_state(port) == "open":
            say("something is listening on 127.0.0.1:%d - the no-wire boot cannot run" % port)
            return 1
    w, h, cols, rows = geometry
    regs = regions(cols, rows)
    crow = regs["choices"][0]
    park = park_cell(geometry)
    launch_col = target_col(choice_targets(False, 0, [], ["echo"]), "launch", "echo")
    say("boot B: %d and %d closed; the same disk and stick copy; the arrow, a click on '! echo' at (%d, %d), 'b', a screendump, Esc"
        % (BROKER_PORT, RELAY_PORT, crow, launch_col))
    steps = [
        ("sleep", 0.5), ("shot", shots["n"]),
        ("obs", "r"),
        ("mouse", 1, 0), ("sleep", 0.5),
        ("moveto", crow, launch_col),
        ("button", 1, "hit"), ("button", 0), ("sleep", 2.0),
        ("type", "b"), ("sleep", 1.0),
        ("moveto", park[0], park[1]), ("sleep", 0.5),
        ("obs", "l"), ("shot", shots["l"]), ("obs", "l2"),
        ("type", "\x1b"), ("sleep", 1.0),
    ]
    capture, reads, events, err = drive(smp, DISK, copy, steps, os.path.join(METAL_OUT, "serial.stages.b.txt"))
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    problems, stripped = strip_mouse_line(capture)
    more, geometry_b = check_boot_lines(stripped, smp, False, "1 notes", 1, DISK_SECTORS)
    problems += more
    problems += check_echo(stripped, b"! echo\r\n")          # the click types the launch line, as ring 6c made it
    if geometry_b != geometry:
        problems.append("boot B's geometry %r differs from boot A's %r" % (geometry_b, geometry))
    ok &= report("boot B's serial log is not what plan-7c.md asks for", problems, capture)
    if not problems:
        say("boot B: %d lines with 'S7: notebook 1 notes' and 'S7: home 1 apps', the i8042: pair, '%s' once after ready, and the wire "
            "carrying exactly '! echo' - the line the click typed" % (len(PATTERNS_AGAIN), MOUSE_LINE))

    problems = check_region_rows(shots["n"], geometry, regs["conversation"], [FIRST_NOTE, PROMPT])
    problems += check_choices(shots["n"], geometry, CHOICES_PROMPT_ECHO)
    problems += check_mode_field(shots["n"], geometry, "prompt")
    ok &= report("screen N does not show the remembered note and the installed app", problems)
    if not problems:
        say("screen N: %r above the prompt (Stage 3), '! echo' on the choices row (ring 6b), before any packet" % FIRST_NOTE)

    problems = check_one_cell_panel(shots["l"], geometry, "b")
    problems += check_mode_field(shots["l"], geometry, "running echo")
    problems += check_choices(shots["l"], geometry, CHOICES_ECHO_RUNNING)
    if "r" not in reads or "l" not in reads or "l2" not in reads:
        problems.append("the obs page could not be read around the launch")
    else:
        r, l, l2 = reads["r"], reads["l"], reads["l2"]
        problems += check_counts(l, {"mode": 3, "name": "echo", "focus": 1, "wire_conns": 0, "requests": 0,
                                     "errors": 0, "bytes_in": r["bytes_in"], "bytes_out": r["bytes_out"]}, "the launch")
        problems += check_pointer_counts(l, reads["counts"]["l"], "the launch", mouse_id=1)
        problems += check_i8042(l, "the launch")
        row, col = reads["model"]["l"]
        problems += check_arrow_at(shots["l"], geometry, row, col, "screen L")
        problems += check_strip_6c(shots["l"], geometry, l, l2, "screen L")
    if read_image(DISK) != read_image(os.path.join(METAL_OUT, "disk.after-a.img")):
        problems.append("the disk changed during the no-wire boot - a launch must not write")
    problems += check_stick_tables_unchanged(copy, "boot B")
    ok &= report("the launch by a click with nothing on the wire is not what plan-7c.md asks for", problems)
    if not problems:
        l = reads["l"]
        say("screen L: echo launched by the click from the home partition, showing 'b' with 'running echo' and its choices; the page: "
            "wire_conns 0, the byte counters unchanged, %d packets, 1 click, 1 hit, mouse_id 1; the arrow at %r and the strip's pointer "
            "field the page's; the disk and the stick copy untouched" % (l["packets"], reads["model"]["l"]))

    say("the stages: %s" % ("every stage re-proven in the twin of the HP in one run" if ok else "not re-proven"))
    return 0 if ok else 1


# ------------------------------------------------- test 4: the bodyguard ---
# (a) is test-7c.sh's own strings. Here: (b) the argv assertions on this
# checker's command (the stick over xhci, no esp.img) and the twin's as
# broker/wire.py builds it, through the frozen check_argv_7b; (c) the
# relay's bind rule, the frozen battery; (d) the payload table as a
# subprocess, 0 wrong, and the spot checks held as data - the flash's words
# and every /dev spelling denied, the harmless sources and sinks allowed.

def check_argv_7c(argv, port, want_mac):
    """A QEMU command inspected for the twin of the HP: one restricted cage
    to the relay on the given port; the e1000e on n0 with the patient's MAC;
    -cpu IvyBridge; -vga none and one display device; a qemu-xhci and a
    usb-storage on a drive named stick; one ide-hd on ide.1; exactly two
    drives, both raw files under stage7/out/, neither if=virtio, neither
    the boot image esp.img, one the stick's copy and one the SATA disk."""
    problems = []
    netdevs = [argv[i + 1] for i, a in enumerate(argv) if a == "-netdev"]
    devices = [argv[i + 1] for i, a in enumerate(argv) if a == "-device"]
    drives = [argv[i + 1] for i, a in enumerate(argv) if a == "-drive"]
    if len(netdevs) != 1:
        problems.append("expected exactly one -netdev, found %d: %r" % (len(netdevs), netdevs))
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
    for flag in ("-nic", "-net", "-hda", "-hdb", "-cdrom", "-blockdev", "-pflash", "-usb", "-usbdevice"):
        if flag in argv:
            problems.append("the command carries %s" % flag)
    nics = [d for d in devices if d.startswith("e1000e")]
    if nics != ["e1000e,netdev=n0,mac=%s" % want_mac]:
        problems.append("expected one e1000e on n0 with the patient's MAC %s, found %r" % (want_mac, nics))
    if [d for d in devices if d.startswith("virtio-net")]:
        problems.append("a virtio-net device on the twin of the HP: %r" % devices)
    vgas = [d for d in devices if d.startswith("VGA") or d.startswith("virtio-vga")]
    if len(vgas) != 1 or "-vga" not in argv or argv[argv.index("-vga") + 1] != "none":
        problems.append("the display is not -vga none with exactly one display device: %r" % vgas)
    if [d for d in devices if d == "qemu-xhci"] != ["qemu-xhci"]:
        problems.append("expected exactly one qemu-xhci, found %r" % devices)
    if [d for d in devices if d.startswith("usb-storage")] != ["usb-storage,drive=stick"]:
        problems.append("expected exactly one usb-storage on the drive named stick, found %r" % devices)
    if [d for d in devices if d.startswith("ide-hd")] != ["ide-hd,drive=d0,bus=ide.1"]:
        problems.append("expected exactly one ide-hd on ide.1 as drive d0, found %r" % devices)
    if len(devices) != 5:
        problems.append("expected exactly five devices (the display, the xhci, the usb-storage, the ide-hd, the e1000e), found %r" % devices)
    if "-cpu" not in argv or argv[argv.index("-cpu") + 1] != "IvyBridge":
        problems.append("the command does not carry -cpu IvyBridge")
    if len(drives) != 2:
        problems.append("expected exactly two drives, found %d: %r" % (len(drives), drives))
    for d in drives:
        m = re.search(r"(?:^|,)file=([^,]*)", d)
        path = m.group(1) if m else ""
        if not path.startswith(OUT + os.sep):
            problems.append("a drive is not a file under stage7/out/: %r" % d)
        if os.path.basename(path) == "esp.img":
            problems.append("the boot image esp.img is on the twin of the HP - the stick is the only boot medium: %r" % d)
        if os.path.abspath(path) == os.path.abspath(STICK):
            problems.append("the drive is stick.img itself - every boot is of a copy: %r" % d)
        if "if=virtio" in d.split(","):
            problems.append("a virtio drive on the twin of the HP: %r" % d)
        if "format=raw" not in d.split(","):
            problems.append("a drive that is not format=raw: %r" % d)
    if len([d for d in drives if d.startswith("if=none,id=stick,")]) != 1:
        problems.append("expected exactly one if=none,id=stick drive for the usb-storage, found %r" % drives)
    if len([d for d in drives if d.startswith("if=none,id=d0,")]) != 1:
        problems.append("expected exactly one if=none,id=d0 drive for the ide-hd, found %r" % drives)
    return problems


# The bodyguard's spot checks, held as data (never on a command line): the
# flash's words and every /dev spelling plan-7c.md decision 7 and A4 name,
# each fed to the hook as a Bash payload. The device directory's name is
# assembled so that this file's own text never spells a path the hook
# would deny in a command that mentions it.
_D = "/" + "dev"
SPOT_DENY = [
    "ls %s/sda" % _D, "ls /%s/sda" % _D, "ls %s//sda" % _D, "ls %s/./sda" % _D,
    "ls %s/disk/by-id/usb-x" % _D, "ls %s/serial/by-id/x" % _D,
    'ls "%s"/sda' % _D, 'ls "%s/sda"' % _D, "ls '%s/'sda" % _D, "ls /de\\v/sda", "ls \\/dev\\/sda",
    "ls $'%s/sda'" % _D, "ls %s" % _D, "ls %s/" % _D,
    "ls %s/ttyUSB0" % _D, "ls %s/ttyS0" % _D, "ls %s/ttyACM0" % _D,
    "echo dd", "dd if=stage7/out/stick.img of=stage7/out/x.img", "echo of=x", "echo by-id", "echo ttyUSB", "echo nmcli",
    "git commit -m 'flashed with dd by the by-id path'",
]
SPOT_ALLOW = [
    "cat %s/null" % _D, "head -c 16 %s/urandom" % _D, "cat %s/zero" % _D, "cat %s/random" % _D,
    "cmd < %s/stdin" % _D, "cmd > %s/stdout" % _D, "cmd 2> %s/stderr" % _D, "ls %s/fd/0" % _D,
    "echo x > %s/tty" % _D, "ls %s/pts/3" % _D, "cmd </dev/null >x", 'echo x > "/dev/null"',
    "ls /devel/x", "cat stage7/out/devices.txt",
    "echo add odd dd-x", "echo lsblk", "python3 stage7/mkstick.py", "python3 broker/chart.py",
    "mformat -i stage7/out/stick.img@@1048576 -F -T 131072 -v GERMOS ::",
    "cp stage7/out/stick.img stage7/out/metal/stick.blank.img",
    "./stage7/test-7c.sh", "python3 stage7/checkmetal.py --stages", "git commit -F msg.txt",
]


def hook_verdict(command):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    r = subprocess.run([sys.executable, HOOK], input=payload.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO))
    return {0: "ALLOW", 2: "DENY"}.get(r.returncode, "EXIT %d" % r.returncode)


def check_bodyguard():
    problems = []
    r = subprocess.run([sys.executable, PAYLOADS], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    m = re.fullmatch(r"(\d+) payloads: (\d+) must be denied, (\d+) must be allowed, (\d+) wrong", last)
    if r.returncode != 0 or not m or m.group(4) != "0":
        problems.append("the payload table: exit %d, last line %r - want exit 0 and 0 wrong" % (r.returncode, last))
        for line in r.stdout.splitlines():
            if line.startswith("  WRONG"):
                problems.append("  " + line.strip())
    else:
        say("the payload table: %s" % last)
    for c in SPOT_DENY:
        v = hook_verdict(c)
        if v != "DENY":
            problems.append("the hook %ss %r - the flash's words and every device spelling must be denied" % (v.lower(), c))
    for c in SPOT_ALLOW:
        v = hook_verdict(c)
        if v != "ALLOW":
            problems.append("the hook %ss %r - the harmless sources and sinks and this ring's tools must be allowed" % (v.lower(), c))
    return problems


def run_cage():
    # ------------------------------------------------ (b) the argv checks --
    argv = qemu_argv(4, DISK, os.path.join(METAL_OUT, "stick.x.img"), os.path.join(METAL_OUT, "x"))
    problems = check_argv_7c(argv, RELAY_PORT, MAC)
    if not report("the checker's own QEMU command is not the twin of the HP", problems):
        return 1
    say("the checker's QEMU command carries one restricted cage to the relay on %d, the e1000e on n0 with %s, -cpu IvyBridge, "
        "the display, the stick copy on usb-storage behind qemu-xhci, the SATA disk on ide.1, two drives under stage7/out/, "
        "no esp.img, no virtio" % (RELAY_PORT, MAC))
    rargv = twin.qemu_argv(ESP, os.path.join(TWIN_WORKDIR, "notes.img"), os.path.join(TWIN_WORKDIR, "serial.txt"),
                           REHEARSAL_PORT, extra_args=wire.twin_extra_args(TWIN_WORKDIR, REHEARSAL_PORT))
    problems = check_argv_7b(rargv, REHEARSAL_PORT, MAC, 3, True, 2, "n1")
    if wire.LINES != len(PATTERNS_BLANK) or wire.MAC != MAC or wire.RELAY_PORT != RELAY_PORT or metal.READY != READY:
        problems.append("the broker module disagrees with this checker: lines %d, mac %r, relay port %d, ready %r"
                        % (wire.LINES, wire.MAC, wire.RELAY_PORT, metal.READY))
    if twin.VGA_ARGS != DISPLAY:
        problems.append("the twin's display is %r" % (twin.VGA_ARGS,))
    if twin.DEFAULT_PORT != REHEARSAL_PORT:
        problems.append("the twin's default port is %d, not %d" % (twin.DEFAULT_PORT, REHEARSAL_PORT))
    if not report("the twin's QEMU command, as broker/wire.py builds it, is not ring 7b's", problems):
        return 1
    say("the twin's command is ring 7b's, unchanged: two restricted cages to 127.0.0.1:%d, the frozen virtio-net on n0, the e1000e "
        "on n1 with %s, -cpu IvyBridge, the same display, esp.img, the frozen virtio notes disk and the SATA disk" % (REHEARSAL_PORT, MAC))

    # ------------------------------------------------ (c) the bind rule ----
    os.makedirs(checkwire.WIRE_OUT, exist_ok=True)     # the frozen battery logs under ring 7b's scratch
    problems = check_bind_rule()
    if not report("the relay's bind rule is not WIRE.md's", problems):
        return 1
    say("the relay refuses %s before any socket exists and listens on 127.0.0.1:%d" % (", ".join(checkwire.BAD_BINDS), RELAY_PORT))

    # ------------------------------------------------ (d) the bodyguard ----
    problems = check_bodyguard()
    ok = report("the bodyguard is not what plan-7c.md decision 7 and A4 ask for", problems)
    if ok:
        say("the bodyguard: %d spellings and words denied, %d harmless sources, sinks and tools allowed" % (len(SPOT_DENY), len(SPOT_ALLOW)))
    say("the cage: %s" % ("held on the twin of the HP, and the flash denied to CC" if ok else "not proven"))
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
    if argv == ["--stages"]:
        return run_stages()
    if argv == ["--cage"]:
        return run_cage()
    say("usage: checkmetal.py --stick | --serial blank|again|novga SMP | --stages | --cage")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
