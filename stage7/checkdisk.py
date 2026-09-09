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
  --persist SMP
        test 3: Stage 3's persistence on the notes partition - two notes
        typed on a blank disk, the disk parsed from the host, a reboot with
        both notes back on screen and nothing on the wire.
  --store
        test 4: ring 6b's store test on the home partition at -smp 4 - the
        argv assertions on this checker's command and the twin's as
        broker/metal.py builds it; boot A installs echo through the mock;
        boot B, with no broker, launches it from the partition; boot C
        refuses the liar, replaces the build twice and undoes once - the
        partitions hash-checked from the host.

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

import hashlib
import json
import os
import re
import select
import shutil
import subprocess
import sys
import time

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
from checkglass import (say, report, dump_capture, check_region_rows, record_count, PROMPT,  # noqa: E402
                        read_record, check_image, port_state, stop_mock, check_choices, check_mode_field,
                        check_app_panel_blank, check_strip, check_surfaces, check_counts, germline_entries,
                        fixture_self_check, SETTLE)
from checkplans import (parse_home, check_home, check_one_cell_panel, check_install_entry, DATA_FIRST,  # noqa: E402
                        CHOICES_PROMPT_ECHO, CHOICES_ECHO_RUNNING, ECHO_TESTS_OK, LIAR_TESTS, REFUSAL_LIAR)
from glass import (regions, app_frame, refusal_frame, ABI, MACHINE)  # noqa: E402
import twin  # noqa: E402
from twin import Driver  # noqa: E402
from plans import (plan_keyname, parse_plan, install_key, PAD_BIG)  # noqa: E402
from rehearse import KEY_GAP  # noqa: E402
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


# ------------------------------------------------------------- the driver ---
# The checker's own QEMU command and monitor driver: the Stage 7 machine
# with two drives, S7: for the ready line and the obs page. The step
# vocabulary is ring 6b's: ("type", text), ("sleep", seconds),
# ("wait_record", path, count, timeout), ("shot", path), ("obs", label),
# ("surfaces", label).

def fresh_disk(path):
    """A brand-new all-zero 64 MB raw image: the blank disk the guest
    formats. Removed first, so nothing from an earlier run survives."""
    if os.path.exists(path):
        os.remove(path)
    with open(path, "wb") as fh:
        fh.truncate(DISK_BYTES_7)


def qemu_argv(smp, disk, serial_path):
    """The one place the checker's QEMU command is spelled. Test 4 inspects this."""
    return [
        "qemu-system-x86_64",
        "-machine", "q35",
    ] + list(CPU) + [
        "-m", "256M",
        "-smp", str(smp),
        "-bios", OVMF,
    ] + list(DISPLAY) + [
        "-drive", "format=raw,file=" + ESP,
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


def drive(smp, disk, steps, serial_path, ready=READY, ready_limit=60.0):
    """Boot inside the cage with the SATA disk, wait for the guest's own
    ready line, run the steps, quit, reap. Returns (serial_bytes, reads,
    error). Never leaves a QEMU running behind us."""
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

    proc = subprocess.Popen(qemu_argv(smp, disk, serial_path),
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
                errs = re.findall(rb"ERR: [^\r\n]*", drv.serial_bytes())
                if errs:
                    err += " (the guest said: %s)" % errs[0].decode(errors="replace")
        else:
            time.sleep(1.0)
            for step in steps:
                if step[0] == "type":
                    for ch in step[1]:
                        drv.tell(b"sendkey " + plan_keyname(ch).encode() + b"\n" if ch not in "\n\t\x1b"
                                 else b"sendkey " + twin.keyname(ch).encode() + b"\n")
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
                elif step[0] == "shot":
                    drv.screendump(step[1])
                elif step[0] in ("obs", "surfaces"):
                    if obs_addr is None:
                        text = drv.serial_bytes().decode("utf-8", "replace")
                        m = re.search(r"S7: obs page 0x([0-9a-f]{16})", text)
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


# ------------------------------------------------------- test 3: persist ---
# Stage 3's soul on the notes partition. Run one: a blank disk, two notes
# typed through the monitor, the machine quit; the disk parsed FROM THE
# HOST by DISK.md and NOTEBOOK.md holds exactly those two notes, byte-exact
# per the worked examples, the home partition freshly formatted, the table
# untouched. Run two: the same disk in a fresh machine logs "S7: notebook 2
# notes", puts nothing on the wire after ready, shows both notes above the
# prompt in the conversation panel rendered from the shared font, and
# leaves the disk byte-identical.

NOTES = ["remember me", "on sata"]


def run_persist(smp):
    disk = DISK
    fresh_disk(disk)
    serial_one = os.path.join(OUT, "serial.persist.%d.run1.txt" % smp)
    serial_two = os.path.join(OUT, "serial.persist.%d.run2.txt" % smp)
    shot = os.path.join(OUT, "screen.persist.%d.ppm" % smp)
    ok = True

    say("run one: a blank disk at -smp %d; %r and %r typed" % (smp, NOTES[0], NOTES[1]))
    steps = [("type", NOTES[0] + "\n"), ("sleep", 1.5), ("type", NOTES[1] + "\n"), ("sleep", 1.5)]
    capture, reads, err = drive(smp, disk, steps, serial_one)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    problems, geometry = check_boot_lines(capture, smp, True, "formatted", 0, DISK_SECTORS)
    problems += check_echo(capture, (NOTES[0] + "\r\n" + NOTES[1] + "\r\n").encode())
    if not report("run one's serial log is not what the spec asks for", problems, capture):
        return 1
    say("run one: eighteen lines, the table written, the notebook formatted, the echo exactly the two typed lines")

    data = read_image(disk)
    problems = ["the table: " + p for p in check_table(data)]
    if not problems:
        problems += check_notes_partition(data, NOTES, "run one")
        problems += check_home_partition(data, "run one")
    if not report("the disk after run one is not what DISK.md and NOTEBOOK.md say", problems):
        return 1
    say("the disk: the table byte-exact, the notes partition holding exactly %r per NOTEBOOK.md's worked example, the home partition empty" % (NOTES,))
    image_one = data

    say("run two: the same disk, nothing typed, a screendump")
    capture, reads, err = drive(smp, disk, [("sleep", 1.0), ("shot", shot)], serial_two)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    problems, geometry = check_boot_lines(capture, smp, False, "%d notes" % len(NOTES), 0, DISK_SECTORS)
    problems += check_echo(capture, b"")
    image_two = read_image(disk)
    if image_two != image_one:
        off = next(i for i in range(len(image_one)) if image_one[i] != image_two[i])
        problems.append("the disk changed during run two (first difference at sector %d) - a replay must not write" % (off // SECTOR))
    if not report("run two is not what the spec asks for", problems, capture):
        return 1
    say("run two: seventeen lines, 'S7: notebook %d notes', nothing on the wire after ready, the disk unchanged" % len(NOTES))
    if None in geometry:
        return 1
    regs = regions(geometry[2], geometry[3])
    problems = check_region_rows(shot, geometry, regs["conversation"], NOTES + [PROMPT])
    if not report("the screen after run two does not show the remembered notes", problems):
        return 1
    say("the screen: %r and %r above the prompt in the conversation panel, from the shared font, two colours only" % (NOTES[0], NOTES[1]))
    say("-smp %d: the machine remembered on SATA" % smp)
    return 0 if ok else 1


# ---------------------------------------------------------------- the mock --

def start_mock(record_path, wipe_germline=True):
    """Start broker/metal.py --mock with the gate's germline (wiped unless
    told otherwise), the gate's image as the twin's, the twin's own
    workdir, its record file; wait for its listening line."""
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
    log = open(os.path.join(OUT, "mock.metal.stderr.txt"), "ab")
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


def plan_of(name):
    data = open(os.path.join(PLANS_DIR, name + ".md"), "rb").read()
    return data, parse_plan(data.decode("latin-1"))


def check_install_germline_7(root, plan, blob, amendment=None, tests=None, model="mock"):
    """checkplans.check_install_germline for this ring's twin: the same
    entry, provenance and verdict, and a rehearsal log holding the S7:
    lines of a boot that formats a blank disk."""
    problems = []
    data, parsed = plan_of(plan)
    key = install_key(plan, data, amendment)
    d = os.path.join(root, key)
    if not os.path.isdir(d):
        return ["no germline entry %s for plan %r (amendment %r)" % (key, plan, amendment)]
    try:
        got = open(os.path.join(d, "component.bin"), "rb").read()
    except OSError as exc:
        return ["entry %s: %s" % (key, exc)]
    if got != blob:
        problems.append("entry %s: component.bin is %d bytes, not the %d-byte build the mock serves" % (key, len(got), len(blob)))
    try:
        prov = json.load(open(os.path.join(d, "provenance.json")))
    except (OSError, ValueError) as exc:
        return problems + ["entry %s: provenance.json: %s" % (key, exc)]
    body = "install " + plan + (", " + amendment if amendment else "")
    want = {"request": body, "key": key, "abi": ABI, "machine": MACHINE, "model": model,
            "sha256": hashlib.sha256(blob).hexdigest(), "size": len(blob), "name": plan,
            "choices": [[chr(k), l.decode()] for k, l in parsed["choices"]],
            "plan": plan, "plan_sha256": hashlib.sha256(data).hexdigest(), "amendment": amendment,
            "installed": True}
    if tests is not None:
        want["plan_tests"] = tests
    for k, v in want.items():
        if prov.get(k) != v:
            problems.append("entry %s: provenance %s is %r, want %r" % (key, k, prov.get(k), v))
    reh = prov.get("rehearsal") or {}
    if reh.get("passed") is not True or reh.get("phrases") != []:
        problems.append("entry %s: provenance rehearsal is %r" % (key, reh))
    try:
        rlog = open(os.path.join(d, "rehearsal.log")).read()
    except OSError as exc:
        return problems + ["entry %s: rehearsal.log: %s" % (key, exc)]
    if len(re.findall(r"^S7: ", rlog, re.M)) != len(PATTERNS_BLANK):
        problems.append("entry %s: rehearsal.log does not hold the twin's %d S7: lines" % (key, len(PATTERNS_BLANK)))
    if "ERR:" in rlog:
        problems.append("entry %s: rehearsal.log carries an ERR: line" % key)
    if "ok: the post-delivery hook found nothing" not in rlog:
        problems.append("entry %s: rehearsal.log does not say the plan's tests passed" % key)
    if "virtio notes.img: untouched, all zero" not in rlog:
        problems.append("entry %s: rehearsal.log does not say the twin's virtio disk stayed all zero" % key)
    return problems


def check_argv_7(argv, port, want_mac, want_drives, virtio_allowed):
    """A QEMU command inspected for the cage and THIS ring's machine: slirp
    user mode, restrict=on, one guestfwd from 10.0.2.4:9999 by nc to
    127.0.0.1 on the given port, no hostfwd, no other network option; one
    virtio-net-pci on n0 (with the MAC when wanted); -cpu IvyBridge; -vga
    none and the one VGA device with the 1920x1080 EDID; one ide-hd on
    ide.1 and no other device; exactly want_drives drives, every one a
    file under stage7/out/, none with if=virtio unless allowed (the frozen
    twin's notes disk, plan deviation 2 - then exactly one)."""
    problems = []
    netdevs = [argv[i + 1] for i, a in enumerate(argv) if a == "-netdev"]
    devices = [argv[i + 1] for i, a in enumerate(argv) if a == "-device"]
    drives = [argv[i + 1] for i, a in enumerate(argv) if a == "-drive"]
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
    for flag in ("-nic", "-net", "-netdev-add", "-hda", "-hdb", "-cdrom", "-blockdev", "-pflash"):
        if flag in argv:
            problems.append("the command carries %s" % flag)
    nics = [d for d in devices if d.startswith("virtio-net-pci")]
    vgas = [d for d in devices if d.startswith("VGA")]
    disks = [d for d in devices if d.startswith("ide-hd")]
    if len(nics) != 1 or not nics[0].startswith("virtio-net-pci,netdev=n0"):
        problems.append("expected one virtio-net-pci on n0, found %r" % nics)
    elif want_mac and nics[0] != "virtio-net-pci,netdev=n0,mac=" + want_mac:
        problems.append("the NIC does not carry the harness's MAC %s: %r" % (want_mac, nics[0]))
    if vgas != ["VGA,edid=on,xres=1920,yres=1080"] or "-vga" not in argv or argv[argv.index("-vga") + 1] != "none":
        problems.append("the display is not -vga none with the one VGA device stating 1920x1080: %r" % vgas)
    if disks != ["ide-hd,drive=d0,bus=ide.1"]:
        problems.append("expected exactly one ide-hd on ide.1 as drive d0, found %r" % disks)
    if len(devices) != 3:
        problems.append("expected exactly three devices (the NIC, the display, the disk), found %r" % devices)
    if "-cpu" not in argv or argv[argv.index("-cpu") + 1] != "IvyBridge":
        problems.append("the command does not carry -cpu IvyBridge")
    if len(drives) != want_drives:
        problems.append("expected exactly %d drives, found %d: %r" % (want_drives, len(drives), drives))
    virtio = 0
    for d in drives:
        m = re.search(r"(?:^|,)file=([^,]*)", d)
        path = m.group(1) if m else ""
        if not path.startswith(OUT + os.sep):
            problems.append("a drive is not a file under stage7/out/: %r" % d)
        if "if=virtio" in d.split(","):
            virtio += 1
    if virtio != (1 if virtio_allowed else 0):
        problems.append("expected %d virtio drive(s), found %d: %r" % (1 if virtio_allowed else 0, virtio, drives))
    sata = [d for d in drives if d.startswith("if=none,id=d0,format=raw,file=")]
    if len(sata) != 1:
        problems.append("expected exactly one if=none,id=d0 drive for the ide-hd, found %r" % sata)
    return problems


# ------------------------------------------------------------ test 4: store -
# Ring 6b's test 4 on the home partition. The argv assertions; the fixtures
# and the plans; boot A with the mock installs echo; boot B with NO broker
# launches it from the partition and refuses an undo with nothing to undo;
# boot C with the mock refuses the liar, replaces the build twice and undoes
# once. The step lists and the counts are ring 6b's frozen, passing
# checkplans.run_store's, replayed on SATA at -smp 4, the patient's count.

def check_partitions(image, notes_want, home_want, label):
    """Both stores cut from the disk and judged by the frozen check_image
    and check_home. Returns (problems, home_parsed)."""
    problems = []
    path, table = extract_partition(image, "notes")
    if path is None:
        return table, None
    problems += ["%s: %s" % (label, p) for p in check_image(path, notes_want)]
    path, _ = extract_partition(image, "home")
    more, home = check_home(path, home_want, label)
    return problems + more, home


def run_store():
    smp = 4
    argv = qemu_argv(smp, DISK, os.path.join(OUT, "x"))
    problems = check_argv_7(argv, BROKER_PORT, MAC, 2, False)
    if not report("the checker's own QEMU command is not the cage with this ring's machine", problems):
        return 1
    say("the checker's QEMU command carries restrict=on, the single guestfwd via nc to 127.0.0.1:%d, -cpu IvyBridge, the 1920x1080 device, "
        "the ESP and the SATA disk under stage7/out/ and no virtio disk" % BROKER_PORT)

    rargv = twin.qemu_argv(ESP, os.path.join(TWIN_WORKDIR, "notes.img"), os.path.join(TWIN_WORKDIR, "serial.txt"),
                           REHEARSAL_PORT, extra_args=metal.twin_extra_args(TWIN_WORKDIR))
    problems = check_argv_7(rargv, REHEARSAL_PORT, None, 3, True)
    if twin.VGA_ARGS != DISPLAY or metal.LINES != len(PATTERNS_BLANK) or metal.READY != READY:
        problems.append("the broker module's twin disagrees with this checker: display %r, lines %d, ready %r"
                        % (twin.VGA_ARGS, metal.LINES, metal.READY))
    if twin.DEFAULT_PORT != REHEARSAL_PORT:
        problems.append("the twin's default port is %d, not %d" % (twin.DEFAULT_PORT, REHEARSAL_PORT))
    if not report("the twin's QEMU command, as broker/metal.py builds it, is not the cage with this ring's machine", problems):
        return 1
    say("the twin's command carries the same cage on 127.0.0.1:%d, -cpu IvyBridge, the same display, the frozen virtio notes disk "
        "the guest ignores, and the 64 MB SATA disk under %s" % (REHEARSAL_PORT, os.path.relpath(TWIN_WORKDIR, REPO)))

    blobs = {}
    for name in ("echo", "liar"):
        blob, problems = fixture_self_check(name)
        if not report("the %s fixture is not what the repository says" % name, problems):
            return 1
        blobs[name] = blob
    echo, liar = blobs["echo"], blobs["liar"]
    big = echo + bytes(PAD_BIG - len(echo))
    problems = []
    for name, ntests, choices in (("echo", 5, []), ("liar", 5, []), ("calculator", 10, [(ord("="), b"result"), (ord("c"), b"clear")])):
        try:
            _, p = plan_of(name)
        except (OSError, ValueError) as exc:
            problems.append("plans/%s.md does not parse: %s" % (name, exc))
            continue
        if len(p["tests"]) != ntests or p["choices"] != choices:
            problems.append("plans/%s.md has %d tests and choices %r, want %d and %r" % (name, len(p["tests"]), p["choices"], ntests, choices))
    if not report("the committed plans are not what the spec wrote", problems):
        return 1
    say("the two fixtures reproduce their binaries; the three plans parse")

    # ---------------------------------------------------------- boot A ----
    record_a = os.path.join(OUT, "broker.store.a.jsonl")
    mock, err = start_mock(record_a)
    if err:
        say(err)
        return 1
    say("boot A: mock up, germline wiped, a blank disk; '! install echo'")
    try:
        fresh_disk(DISK)
        steps = [
            ("type", "! install echo\n"), ("wait_record", record_a, 1, 150.0), ("sleep", 3.0),
            ("type", "\x1b"), ("sleep", 1.0),
        ]
        capture, reads, err = drive(smp, DISK, steps, os.path.join(OUT, "serial.store.a.txt"))
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    ok = True
    problems, geometry = check_boot_lines(capture, smp, True, "formatted", 0, DISK_SECTORS)
    problems += check_echo(capture, b"! install echo\r\n")
    entries, more = read_record(record_a)
    problems += more
    if entries is not None:
        if len(entries) != 1:
            problems.append("boot A: the broker saw %d connection(s), want 1" % len(entries))
        if entries:
            problems += check_install_entry(1, entries[0], "install echo", "generated", 1, ["pass"], "app",
                                            app_frame(echo, b"echo", [], 0, installed=1), plan="echo", tests=ECHO_TESTS_OK)
    problems += check_install_germline_7(GERMLINE, "echo", echo, tests=ECHO_TESTS_OK)
    data = read_image(DISK)
    problems += ["boot A: " + p for p in check_table(data)]
    more, home_a = check_partitions(DISK, [], {"echo": {"current": (echo, DATA_FIRST), "previous": None, "choices": []}}, "boot A")
    problems += more
    # The twin's own disk and the frozen twin's virtio image, after the rehearsal.
    tdisk = metal.twin_disk(TWIN_WORKDIR)
    try:
        tdata = read_image(tdisk)
        ttable = parse_gpt(tdata)
        tnotes = parse_notebook(partition_bytes(tdata, ttable["notes"]))
        if tnotes != ["after"]:
            problems.append("the twin's SATA disk holds notes %r, want ['after'] - the twin's note went elsewhere" % (tnotes,))
        problems += ["the twin's table: " + p for p in check_table(tdata)]
    except (OSError, ValueError) as exc:
        problems.append("the twin's SATA disk is not a GermOS disk with a notebook: %s" % exc)
    try:
        if any(read_image(os.path.join(TWIN_WORKDIR, "notes.img"))):
            problems.append("the twin's virtio notes.img was written - virtio-blk code ran in the twin")
    except OSError as exc:
        problems.append("the twin's virtio notes.img: %s" % exc)
    ok &= report("boot A did not install echo on the home partition", problems, capture)
    if not problems:
        say("boot A: eighteen lines, the table written; echo installed at partition sector %d (LBA %d) hash-checked; the record, the germline "
            "with an %d-line S7: rehearsal log; the twin's disk formatted with its note on SATA and its virtio image all zero"
            % (DATA_FIRST, HOME_FIRST + DATA_FIRST, len(PATTERNS_BLANK)))
    shutil.copyfile(DISK, os.path.join(OUT, "disk.after-a.img"))
    if None in geometry:
        return 1
    regs = regions(geometry[2], geometry[3])
    conv = regs["conversation"]

    # ---------------------------------------------------------- boot B ----
    if port_state(BROKER_PORT) == "open":
        say("boot B: something is listening on 127.0.0.1:%d - the no-broker boot cannot run" % BROKER_PORT)
        return 1
    say("boot B: NO broker (127.0.0.1:%d closed); the same disk; '! echo' from the home partition" % BROKER_PORT)
    shots = {k: os.path.join(OUT, "screen.store.%s.ppm" % k) for k in ("p", "l", "u", "e", "d")}
    steps = [
        ("obs", "r"), ("shot", shots["p"]),
        ("type", "! echo\n"), ("sleep", 2.0),
        ("type", "b"), ("sleep", 1.0),
        ("shot", shots["l"]), ("obs", "l"),
        ("type", "\x1b"), ("sleep", 1.0),
        ("type", "! undo install echo\n"), ("sleep", 1.5),
        ("shot", shots["u"]), ("obs", "u"),
    ]
    capture, reads, err = drive(smp, DISK, steps, os.path.join(OUT, "serial.store.b.txt"))
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    problems, _ = check_boot_lines(capture, smp, False, "0 notes", 1, DISK_SECTORS)
    problems += check_echo(capture, b"! echo\r\n! undo install echo\r\n")
    ok &= report("boot B's serial log is not what the spec asks for", problems, capture)
    if not problems:
        say("boot B: seventeen lines, 'S7: home 1 apps'; the serial echo exactly the two typed lines")
    problems = check_choices(shots["p"], geometry, CHOICES_PROMPT_ECHO)
    problems += check_one_cell_panel(shots["l"], geometry, "b")
    problems += check_mode_field(shots["l"], geometry, "running echo")
    problems += check_choices(shots["l"], geometry, CHOICES_ECHO_RUNNING)
    if "r" not in reads or "l" not in reads or "u" not in reads:
        problems.append("the obs page could not be read around the launch")
    else:
        r, l = reads["r"], reads["l"]
        problems += check_counts(l, {"mode": 3, "name": "echo", "focus": 1, "wire_conns": 0, "requests": 0,
                                     "grows_generated": 0, "grows_served": 0, "errors": 0,
                                     "bytes_in": r["bytes_in"], "bytes_out": r["bytes_out"]}, "the launch")
        problems += check_counts(reads["u"], {"mode": 0, "errors": 1, "wire_conns": 0}, "the undo")
    problems += check_region_rows(shots["u"], geometry, conv, ["> ! echo", "> ! undo install echo", "echo has no previous build", PROMPT])
    problems += check_app_panel_blank(shots["u"], geometry)
    if read_image(DISK) != read_image(os.path.join(OUT, "disk.after-a.img")):
        problems.append("the disk changed during boot B - a launch or a refused undo must not write")
    ok &= report("boot B did not launch echo from the partition with nothing on the wire", problems)
    if not problems:
        say("boot B: '! echo' on the choices row; the app ran from the home partition showing 'b'; wire_conns 0 and bytes in/out unchanged "
            "(%d/%d); 'echo has no previous build' counted; the disk untouched" % (reads["r"]["bytes_in"], reads["r"]["bytes_out"]))

    # ---------------------------------------------------------- boot C ----
    record_c = os.path.join(OUT, "broker.store.c.jsonl")
    mock, err = start_mock(record_c, wipe_germline=False)
    if err:
        say(err)
        return 1
    say("boot C: mock up, germline kept; the liar, the amended re-install, the germline re-install, the undo, the launch")
    try:
        steps = [
            ("type", "! install liar\n"), ("wait_record", record_c, 1, 240.0), ("sleep", SETTLE),
            ("type", "! install echo, but big\n"), ("wait_record", record_c, 2, 150.0), ("sleep", 3.0),
            ("type", "\x1b"), ("sleep", 1.0),
            ("type", "! install echo\n"), ("wait_record", record_c, 3, 20.0), ("sleep", 3.0),
            ("type", "\x1b"), ("sleep", 1.0),
            ("type", "! undo install echo\n"), ("sleep", 1.5),
            ("type", "! echo\n"), ("sleep", 2.0),
            ("type", "c"), ("sleep", 1.0),
            ("shot", shots["e"]),
            ("type", "\x1b"), ("sleep", 1.0),
            ("type", "last\n"), ("sleep", 1.5),
            ("surfaces", "d"), ("shot", shots["d"]), ("obs", "d2"),
        ]
        capture, reads, err = drive(smp, DISK, steps, os.path.join(OUT, "serial.store.c.txt"))
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    keys_typed = sum(len(s[1]) for s in steps if s[0] == "type")
    problems, _ = check_boot_lines(capture, smp, False, "0 notes", 1, DISK_SECTORS)
    problems += check_echo(capture, b"! install liar\r\n! install echo, but big\r\n! install echo\r\n"
                                    b"! undo install echo\r\n! echo\r\nlast\r\n")
    ok &= report("boot C's serial log is not what the spec asks for", problems, capture)
    if not problems:
        say("boot C: seventeen lines, 'home 1 apps'; the echo exactly the six typed lines")

    entries, problems = read_record(record_c)
    if entries is not None:
        if len(entries) != 3:
            problems.append("boot C: the broker saw %d connection(s), want 3" % len(entries))
        checks = [
            lambda e: check_install_entry(1, e, "install liar", "refused", 2, ['fail: expect "a"'] * 2, "refusal",
                                          refusal_frame(REFUSAL_LIAR.encode()), REFUSAL_LIAR, plan="liar", tests=LIAR_TESTS),
            lambda e: check_install_entry(2, e, "install echo, but big", "generated", 3, ["pass"], "app",
                                          app_frame(big, b"echo", [], 0, installed=1), plan="echo", amendment="but big",
                                          tests=ECHO_TESTS_OK),
            lambda e: check_install_entry(3, e, "install echo", "germline", 3, [], "app",
                                          app_frame(echo, b"echo", [], 1, installed=1), plan="echo", tests=[]),
        ]
        for check, entry in zip(checks, entries):
            problems += check(entry)
    ok &= report("boot C's record is not what PLANS.md asks for", problems)
    if not problems:
        say("the record: the liar refused naming its failed test after two rehearsals (calls 2 - the mock is restarted between boots); "
            "'echo, but big' generated (3) as a 4096-byte build with installed 1; 'install echo' served from the germline (still 3)")

    problems = check_install_germline_7(GERMLINE, "echo", echo, tests=ECHO_TESTS_OK)
    problems += check_install_germline_7(GERMLINE, "echo", big, amendment="but big", tests=ECHO_TESTS_OK)
    names = germline_entries(GERMLINE)
    if len(names) != 2:
        problems.append("the germline holds %d entries %r, want exactly 2 (the liar never lands)" % (len(names), names))
    ok &= report("the germline is not what PLANS.md asks for", problems)
    if not problems:
        say("the germline holds exactly two entries - echo, and echo with its amendment - and no liar")

    # The sequence: A put echo at 9; "echo, but big" put the padded build
    # at 10-17 (echo at 9 became the previous); the germline re-install put
    # echo at 18 (the padded build became the previous, sector 9 abandoned);
    # the undo swapped them back: the padded build current, echo at 18
    # previous. Both extents still hold their builds, hash-checked. Ring 6b's
    # numbers, on the home partition now.
    data = read_image(DISK)
    problems = ["boot C: " + p for p in check_table(data)]
    more, home_c = check_partitions(DISK, ["last"], {"echo": {"current": (big, DATA_FIRST + 1), "previous": (echo, DATA_FIRST + 9),
                                                              "choices": []}}, "boot C")
    problems += more
    if home_c and home_c["next_free"] != DATA_FIRST + 10:
        problems.append("boot C: the next free sector is %d, want %d" % (home_c["next_free"], DATA_FIRST + 10))
    ok &= report("the disk after the re-installs and the undo is not what DISK.md, HOME.md and NOTEBOOK.md ask for", problems)
    if not problems:
        say("the disk: the table untouched; echo's current build the padded one at partition sector %d and its previous the first build at %d, "
            "both extents hash-checked from the host; the notebook 'last'" % (DATA_FIRST + 1, DATA_FIRST + 9))

    problems = check_one_cell_panel(shots["e"], geometry, "c")
    problems += check_mode_field(shots["e"], geometry, "running echo")
    ok &= report("screen E does not show the restored build running", problems)
    if not problems:
        say("screen E: the restored build ran from the partition and took 'c'")

    problems = []
    if "d" not in reads or "d2" not in reads:
        problems.append("the obs page or the surfaces could not be read at the end")
    else:
        problems += check_strip(shots["d"], geometry, reads["d"]["obs"], reads["d2"], "screen D")
        problems += check_surfaces(shots["d"], reads["d"], "screen D")
        problems += check_counts(reads["d"]["obs"], {"mode": 0, "name": "", "focus": 0, "keys": keys_typed,
                                                    "questions": 0, "requests": 3, "notes": 1, "errors": 1,
                                                    "grows_generated": 1, "grows_served": 1, "wire_conns": 3}, "screen D")
        problems += check_mode_field(shots["d"], geometry, "prompt")
        problems += check_choices(shots["d"], geometry, CHOICES_PROMPT_ECHO)
        problems += check_app_panel_blank(shots["d"], geometry)
        problems += check_region_rows(shots["d"], geometry, conv, [
            "> ! install liar", REFUSAL_LIAR,
            "> ! install echo, but big", "installed echo",
            "> ! install echo", "installed echo",
            "> ! undo install echo", "echo: previous build restored",
            "> ! echo", "> last", PROMPT])
    ok &= report("screen D is not the truth", problems)
    if not problems:
        say("screen D: the strip is the obs page (err 001, g 001/001), every region its surface, '! echo' still on the choices row, "
            "the whole conversation from the liar's refusal to the restored build")

    say("the store on SATA: %s" % ("kept its word" if ok else "did not keep its word"))
    return 0 if ok else 1


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
    if len(argv) == 2 and argv[0] == "--persist":
        try:
            return run_persist(int(argv[1]))
        except ValueError:
            pass
    if argv == ["--store"]:
        return run_store()
    say("usage: checkdisk.py --formatted IMAGE SECTORS NOTES HOME | --recognised IMAGE SECTORS NOTES HOME | "
        "--foreign IMAGE | --esp BEFORE AFTER EFI | --persist SMP | --store")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
