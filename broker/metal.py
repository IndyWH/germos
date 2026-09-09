#!/usr/bin/env python3
"""The GermOS broker for Stage 7 ring 7a - the disk.

Everything ring 6c's broker does, this one does, by IMPORT and never by
edit: the framing, the record, the listener and the question path from the
frozen broker.py and germline.py; the ABI 2 pipeline as the frozen
glass.Glazier; the install path and the plan's tests as the frozen
plans.Installer; the fifth callback's check as the frozen pointer.Pointer,
subclassed here. What this file adds is stage7/DISK.md - and a twin that
can read a Stage 7 guest:

  - DISK.md's Python, verbatim: the table the guest writes, the reader,
    the five words of the selection rule, the partition cut;
  - rehearse_metal: broker/twin.py's rehearse transcribed for a guest that
    prints S7: lines and keeps its notebook on a SATA partition. The
    frozen twin finds its lines and its obs page by "S6:" literals and
    reads the note from the virtio image it made; none of the three is a
    seam (plan-7a.md, deviation 1). So the transcription differs in
    exactly those places - the prefix, and the note read from the SATA
    disk's notes partition through DISK.md's reader, wrapped so that any
    failure is a log line and a verdict, never an exception (A2) - and
    calls the frozen twin.judge for the nine criteria, the frozen Driver,
    listener and picture helpers for everything else;
  - the twin's command: the frozen twin.qemu_argv (the boot image on
    SATA, the frozen virtio notes disk the Stage 7 guest has no driver
    for, the cage, the 1920x1080 display plans.py sets) plus, through the
    extra_args seam, -cpu IvyBridge and a blank 64 MB SATA disk on ide.1 -
    twin_extra_args, the one place it is spelled;
  - tests_hook_metal: plans.tests_hook with the S7: obs-page regex;
  - the same canned table as ring 6c's mock: GLASS.md's, PLANS.md's and
    the point app.

In --mock mode nothing outside the repository is ever called: the
acceptance tests use only the mock, so the gate never spends a token. The
rehearsal still boots a real QEMU. Without --mock the answers come from
broker/claude_backend.py, the one unfrozen file.

This file becomes frozen acceptance machinery at ring 7a plan item 10
(amendment A3: after the gate has passed nine of nine through it): its
twin's verdicts, its mock table and the DISK.md Python it carries are
criteria the checker leans on. Standard library only.

Usage:
    python3 broker/metal.py                 # real: questions, requests, installs
    python3 broker/metal.py --mock          # canned; no calls of any kind
    python3 broker/metal.py --rehearse-app stage6/app.bin 'test app'
    python3 broker/metal.py --rehearse stage6/echo.bin plans/echo.md
                                            # hand runs in this module's twin

Prints "listening on 127.0.0.1:<port>" to stdout once bound.
"""

import argparse
import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import uuid
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from broker import (DEFAULT_PORT, mock_answer, log)  # noqa: E402
from germline import serve  # noqa: E402
from glass import (app_frame, regions, ABI)  # noqa: E402
import twin  # noqa: E402
from twin import (Driver, AppListener, judge, qemu_argv, REQUEST, NOTE)  # noqa: E402
from rehearse import (parse_notebook, OVMF, DISK_BYTES, KEY_GAP)  # noqa: E402
import plans  # noqa: E402  - sets twin.VGA_ARGS to the machine's display
from plans import (Installer, Glyphs, panel_rows, region_pixels, test_line, plan_keyname,  # noqa: E402
                   SETTLE, DISPLAY, PLANS_DIR, parse_plan)
import pointer  # noqa: E402
from pointer import (Pointer, mock_point, point_offset, POINT_NAME, POINT_CHOICES)  # noqa: E402

# ----------------------------------------------------------- the document -
# stage7/DISK.md, "Parsing it cold, in Python", verbatim - its three
# imports included, so the block can be matched against the document
# byte for byte.

import struct
import uuid
import zlib

SECTOR = 512
ENTRIES, ENTRY = 128, 128            # the entry array: 128 entries of 128 bytes
ENTRY_SECTORS = ENTRIES * ENTRY // SECTOR            # 32
HEADER_SIZE = 92
FIRST_USABLE = 2 + ENTRY_SECTORS                     # 34: the MBR, the header, the array
NOTES_TYPE = uuid.UUID("50845557-ee34-4731-8b83-d1d6f14fd8c5")   # GermOS notes
HOME_TYPE = uuid.UUID("456d4007-d803-41a0-a661-ca736ddcf96b")    # GermOS home
DISK_GUID = uuid.UUID("2b74a505-e246-469d-8d73-3bfdc52a8df0")
NOTES_GUID = uuid.UUID("6e5d297e-0ecb-48c5-92c8-4a93f4e98d44")
HOME_GUID = uuid.UUID("82bc9169-ce31-4fd9-bf05-63c7521726eb")
PART_SECTORS = 32768                                 # 16 MB, each partition
NOTES_FIRST = 2048                                   # 1 MiB alignment
HOME_FIRST = NOTES_FIRST + PART_SECTORS              # 34816
NOTES_NAME, HOME_NAME = "GermOS notes", "GermOS home"
CRC_CHECK = 0xCBF43926                               # crc32(b"123456789"), the standard's check value


def min_sectors():
    """The smallest disk: the last usable LBA, N - 34, must be the home
    partition's last sector or beyond."""
    return HOME_FIRST + PART_SECTORS - 1 + FIRST_USABLE


def guid_bytes(u):
    """A GUID as GPT stores it: the first three fields little-endian."""
    return u.bytes_le


def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF


def protective_mbr(n):
    entry = struct.pack("<B3sB3sII", 0x00, b"\x00\x02\x00", 0xEE, b"\xff\xff\xff", 1, min(n - 1, 0xFFFFFFFF))
    return bytes(446) + entry + bytes(48) + b"\x55\xaa"


def partition_entries():
    """The 16 KB array: entry 0 the notes partition, entry 1 the home, the rest zero."""
    def entry(type_guid, guid, first, last, name):
        nm = name.encode("utf-16-le")
        return guid_bytes(type_guid) + guid_bytes(guid) + struct.pack("<QQQ", first, last, 0) + nm + bytes(72 - len(nm))
    data = entry(NOTES_TYPE, NOTES_GUID, NOTES_FIRST, NOTES_FIRST + PART_SECTORS - 1, NOTES_NAME)
    data += entry(HOME_TYPE, HOME_GUID, HOME_FIRST, HOME_FIRST + PART_SECTORS - 1, HOME_NAME)
    return data + bytes(ENTRIES * ENTRY - len(data))


def gpt_header(n, my_lba, alt_lba, entries_lba, entries_crc):
    """One header sector; the CRC computed over the 92 bytes with its own field zero."""
    body = b"EFI PART" + struct.pack("<IIIIQQQQ", 0x00010000, HEADER_SIZE, 0, 0,
                                     my_lba, alt_lba, FIRST_USABLE, n - FIRST_USABLE)
    body += guid_bytes(DISK_GUID) + struct.pack("<QIII", entries_lba, ENTRIES, ENTRY, entries_crc)
    body = body[:16] + struct.pack("<I", crc32(body)) + body[20:]
    return body + bytes(SECTOR - HEADER_SIZE)


def build_gpt(n):
    """Every sector the guest writes when it formats a blank disk of n
    sectors, as {lba: 512 bytes}: the MBR, the header, the 32 array
    sectors, the backup array at n-33, the backup header at n-1."""
    if n < min_sectors():
        raise ValueError("a disk of %d sectors is too small; %d is the least" % (n, min_sectors()))
    entries = partition_entries()
    ecrc = crc32(entries)
    out = {0: protective_mbr(n), 1: gpt_header(n, 1, n - 1, 2, ecrc), n - 1: gpt_header(n, n - 1, 1, n - 33, ecrc)}
    for i in range(ENTRY_SECTORS):
        out[2 + i] = entries[i * SECTOR:(i + 1) * SECTOR]
        out[n - 33 + i] = entries[i * SECTOR:(i + 1) * SECTOR]
    return out


def parse_header(hdr, n):
    """A header sector by the recognition rule: the signature, revision 1.0,
    size 92, its own CRC, MyLBA 1, 128 entries of 128 bytes at LBA 2, the
    usable range inside the disk, the tail zero. Returns the entries' CRC."""
    if hdr[0:8] != b"EFI PART":
        raise ValueError("no EFI PART signature")
    rev, size, hcrc, res, my, alt, first, last = struct.unpack_from("<IIIIQQQQ", hdr, 8)
    elba, count, esize, ecrc = struct.unpack_from("<QIII", hdr, 72)
    if rev != 0x00010000 or size != HEADER_SIZE or res != 0:
        raise ValueError("header revision %#x size %d reserved %d" % (rev, size, res))
    if crc32(hdr[:16] + bytes(4) + hdr[20:HEADER_SIZE]) != hcrc:
        raise ValueError("header CRC does not match")
    if my != 1 or elba != 2 or count != ENTRIES or esize != ENTRY:
        raise ValueError("MyLBA %d entries at %d, %d of %d bytes" % (my, elba, count, esize))
    if alt >= n or first < FIRST_USABLE or last >= n or last < first:
        raise ValueError("alternate %d usable %d..%d on a disk of %d" % (alt, first, last, n))
    if any(hdr[HEADER_SIZE:]):
        raise ValueError("header tail not zero")
    return ecrc, (first, last)


def parse_entries(entries, usable):
    out = []
    for i in range(ENTRIES):
        e = entries[i * ENTRY:(i + 1) * ENTRY]
        if not any(e[0:16]):
            if any(e):
                raise ValueError("entry %d: unused but not zero" % i)
            continue
        t = uuid.UUID(bytes_le=e[0:16])
        g = uuid.UUID(bytes_le=e[16:32])
        first, last, attrs = struct.unpack_from("<QQQ", e, 32)
        name = e[56:128].decode("utf-16-le").split("\0", 1)[0]
        if first < usable[0] or last > usable[1] or last < first:
            raise ValueError("entry %d: %d..%d outside the usable range" % (i, first, last))
        out.append({"index": i, "type": t, "guid": g, "first": first, "last": last,
                    "sectors": last - first + 1, "attrs": attrs, "name": name})
    return out


def parse_gpt(data):
    """The whole disk, by the guest's recognition rule (the primary header,
    the array, both type GUIDs present). Returns {"sectors", "disk_guid",
    "entries", "notes": (first, sectors), "home": (first, sectors)}.
    ValueError on anything the document forbids."""
    if len(data) % SECTOR:
        raise ValueError("not a whole number of sectors")
    n = len(data) // SECTOR
    if n < 2 + ENTRY_SECTORS:
        raise ValueError("too short to hold a table")
    ecrc, usable = parse_header(data[SECTOR:2 * SECTOR], n)
    entries = data[2 * SECTOR:(2 + ENTRY_SECTORS) * SECTOR]
    if crc32(entries) != ecrc:
        raise ValueError("entry array CRC does not match")
    parsed = parse_entries(entries, usable)
    found = {}
    for e in parsed:
        for key, t in (("notes", NOTES_TYPE), ("home", HOME_TYPE)):
            if e["type"] == t and key not in found:
                found[key] = (e["first"], e["sectors"])
    if "notes" not in found or "home" not in found:
        raise ValueError("a valid table without both GermOS partitions (found %s)" % sorted(found))
    return {"sectors": n, "disk_guid": uuid.UUID(bytes_le=data[SECTOR + 56:SECTOR + 72]),
            "entries": parsed, "notes": found["notes"], "home": found["home"]}


def classify(data):
    """What a disk holds, in the guest's five words: germos, blank, gpt (a
    valid table without both GermOS partitions), torn (the signature with
    an invalid header or array), other (an MBR, a boot sector, data)."""
    if len(data) >= 2 * SECTOR and not any(data[:2 * SECTOR]):
        return "blank"
    try:
        parse_gpt(data)
        return "germos"
    except ValueError as exc:
        if data[SECTOR:SECTOR + 8] != b"EFI PART":
            return "other"
        return "gpt" if "without both" in str(exc) else "torn"


def partition_bytes(data, part):
    first, sectors = part
    return data[first * SECTOR:(first + sectors) * SECTOR]


def check_table(data):
    """A disk the guest formatted, from the host: every sector build_gpt
    names byte-identical, the backup included. Returns a list of problems."""
    n = len(data) // SECTOR
    problems = []
    try:
        want = build_gpt(n)
    except ValueError as exc:
        return [str(exc)]
    for lba in sorted(want):
        got = data[lba * SECTOR:(lba + 1) * SECTOR]
        if got != want[lba]:
            off = next(i for i in range(SECTOR) if got[i] != want[lba][i])
            problems.append("sector %d differs from the document's table at byte 0x%x" % (lba, off))
    return problems


# --------------------------------------------------------------- Stage 7 --

DISK_BYTES_7 = 64 * 1024 * 1024      # the twin's and the gate's SATA disk
LINES = 18                           # the S7: lines a Stage 7 guest prints on a disk it formats
READY = b"S7: keyboard ready"
LINE_RE = r"S7: [^\n]*"
OBS_RE = r"S7: obs page 0x([0-9a-f]{16})"
CPU = ["-cpu", "IvyBridge"]          # the twin's processor is the patient's (spec decision 4)
STAGE7_OUT = os.path.join(REPO, "stage7", "out")
DEFAULT_IMAGE = os.path.join(STAGE7_OUT, "esp.img")
DEFAULT_WORKDIR = os.path.join(STAGE7_OUT, "rehearsal", "twin")
ECHO_WANT = (REQUEST + "\r\n" + NOTE + "\r\n").encode()


def twin_disk(workdir):
    return os.path.join(workdir, "disk.img")


def twin_extra_args(workdir):
    """The Stage 7 additions to the frozen twin's command, spelled once:
    the patient's CPU and a SATA disk on q35's own controller, ide.1, the
    file under the twin's scratch directory. Test 4 inspects the command
    they land in."""
    return CPU + ["-drive", "if=none,id=d0,format=raw,file=" + twin_disk(workdir),
                  "-device", "ide-hd,drive=d0,bus=ide.1"]


def read_sata_notes(path, say):
    """The notebook on the SATA disk's notes partition, or None with the
    reason said (A2: a short read or anything DISK.md or NOTEBOOK.md
    forbids is a log line, never an exception)."""
    try:
        data = open(path, "rb").read()
    except OSError as exc:
        say("notebook: cannot read the SATA disk: %s" % exc)
        return None
    if len(data) != DISK_BYTES_7:
        say("notebook: the SATA disk is %d bytes, not %d" % (len(data), DISK_BYTES_7))
        return None
    try:
        table = parse_gpt(data)
        notes = parse_notebook(partition_bytes(data, table["notes"]))
    except ValueError as exc:
        say("notebook: %s (the SATA disk holds %s)" % (exc, classify(data)))
        return None
    say("notebook: %r on the notes partition at LBA %d" % (notes, table["notes"][0]))
    return notes


def rehearse_metal(blob, name, choices, image, workdir, port=twin.DEFAULT_PORT,
                   extra_args=(), lines=LINES, after=None):
    """broker/twin.py's rehearse, transcribed for a Stage 7 guest: the same
    listener, the same driver, the same screens, the same nine criteria
    judged by the frozen twin.judge. The differences, and nothing else:
    the S7: prefix for the ready line, the lines and the obs page; the
    twin's disk.img created blank beside the frozen shape's notes.img and
    esp.img copy, and handed to QEMU through the extra_args seam with the
    patient's CPU; the note read from the SATA disk's notes partition
    (A2: any failure a log line and notes None). Returns (passed, phrase,
    log_text)."""
    t_start = time.time()
    log_lines = []

    def say(msg):
        log_lines.append(msg)

    say("rehearsal at %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    say("image %s" % image)
    say("blob sha256 %s size %d name %r choices %r" % (hashlib.sha256(blob).hexdigest(), len(blob), name, choices))

    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    disk = os.path.join(workdir, "notes.img")   # the frozen twin's virtio disk: present, never driven
    sata = twin_disk(workdir)                   # the Stage 7 disk: blank, formatted by the guest
    twin_copy = os.path.join(workdir, "esp.img")  # a private, byte-identical copy: QEMU locks the
                                                  # file a guest boots from
    serial_path = os.path.join(workdir, "serial.txt")
    shot_b = os.path.join(workdir, "b.ppm")
    shot_c = os.path.join(workdir, "c.ppm")
    with open(disk, "wb") as fh:
        fh.truncate(DISK_BYTES)
    with open(sata, "wb") as fh:
        fh.truncate(DISK_BYTES_7)
    if os.path.isfile(image):
        shutil.copyfile(image, twin_copy)

    ev = {"ready": False, "lines": [], "errs": [], "echo": None, "delivered": False,
          "b": False, "c": False, "notes": None, "listener_error": None,
          "obs_b": None, "obs_c": None, "conversation": None, "choices": None,
          "name": name, "after": None, "lines_want": lines}

    try:
        reply = app_frame(blob, name, choices)
    except ValueError as exc:
        say("candidate is not a legal app frame: %s" % exc)
        return judge(ev, time.time() - t_start, log_lines)
    if not os.path.isfile(image):
        say("no image at %s" % image)
        return judge(ev, time.time() - t_start, log_lines)
    if not os.path.isfile(OVMF):
        say("no firmware at %s" % OVMF)
        return judge(ev, time.time() - t_start, log_lines)

    listener = AppListener(port, reply)
    if not listener.bind():
        say("listener: %s" % listener.error)
        ev["listener_error"] = listener.error
        return judge(ev, time.time() - t_start, log_lines)
    listener.start()

    argv = qemu_argv(twin_copy, disk, serial_path, port, twin_extra_args(workdir) + list(extra_args))
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    drv = Driver(proc, serial_path, workdir)

    try:
        deadline = time.time() + 60.0
        while time.time() < deadline:
            time.sleep(0.25)
            if proc.poll() is not None:
                say("qemu exited %d: %s" % (proc.returncode,
                                           proc.stderr.read().decode(errors="replace").strip()[:200]))
                break
            if READY in drv.serial_bytes():
                ev["ready"] = True
                break
        if ev["ready"]:
            time.sleep(1.0)
            drv.type_text(REQUEST + "\n")
            if listener.delivered.wait(30.0):
                ev["delivered"] = True
                say("delivered: the twin asked %r and was sent %d bytes" % (listener.request, len(listener.reply)))
                time.sleep(3.0)
                text = drv.serial_bytes().decode("utf-8", "replace").replace("\r", "")
                m = re.search(OBS_RE, text)
                if m:
                    obs_addr = int(m.group(1), 16)
                    try:
                        ev["obs_b"] = drv.read_obs(obs_addr)
                        ev["conversation"] = drv.read_surface(ev["obs_b"]["conversation"])
                        ev["choices"] = drv.read_surface(ev["obs_b"]["choices"])
                    except ValueError as exc:
                        say("xp: %s" % exc)
                else:
                    say("no obs page line on serial")
                ev["b"] = drv.screendump(shot_b)
                if after is not None:
                    try:
                        ev["after"] = list(after(drv, drv.xp) or [])
                    except Exception as exc:  # a hook that raises is a failed hook
                        ev["after"] = ["the post-delivery hook failed: %s" % exc]
                drv.tell(b"sendkey esc\n")
                time.sleep(2.0)
                drv.type_text(NOTE + "\n")
                time.sleep(2.0)
                if m:
                    try:
                        ev["obs_c"] = drv.read_obs(obs_addr)
                    except ValueError as exc:
                        say("xp after esc: %s" % exc)
                ev["c"] = drv.screendump(shot_c)
            else:
                say("not delivered: %s" % (listener.error or "the twin never connected"))
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
        listener.stop.set()

    cap = drv.serial_bytes()
    text = cap.decode("utf-8", "replace").replace("\r", "")
    ev["lines"] = re.findall(LINE_RE, text)
    ev["errs"] = re.findall(r"ERR: [^\n]*", text)
    marker = READY + b"\r\n"
    idx = cap.find(marker)
    ev["echo"] = cap[idx + len(marker):] if idx >= 0 else None
    ev["listener_error"] = listener.error
    ev["notes"] = read_sata_notes(sata, say)
    try:
        virtio = open(disk, "rb").read()
        say("virtio notes.img: %s" % ("untouched, all zero" if not any(virtio)
                                      else "WRITTEN - %d non-zero bytes" % sum(1 for b in virtio if b)))
    except OSError as exc:
        say("virtio notes.img: %s" % exc)
    ev["shot_b"] = shot_b
    ev["shot_c"] = shot_c

    for line in ev["lines"]:
        say(line)
    for line in ev["errs"]:
        say(line)
    if ev["obs_b"]:
        o = ev["obs_b"]
        t = max(o["tsc_per_ms"], 1)
        say("obs after delivery: mode %d name %r steps %d step_worst %.1f ms frames %d frame_worst %.1f ms"
            % (o["mode"], o["name"], o["steps"], o["step_worst"] / t, o["frames"], o["frame_worst"] / t))
    if ev["obs_c"]:
        say("obs after esc: mode %d frames %d" % (ev["obs_c"]["mode"], ev["obs_c"]["frames"]))
    return judge(ev, time.time() - t_start, log_lines)


def tests_hook_metal(tests, verdicts):
    """plans.tests_hook with the S7: obs-page line: the plan's tests run
    in order while the app has the keys, "ok: <line>" or "fail: <line>"
    appended to verdicts, [] or [the failing line] returned."""

    def after(drv, xp):
        m = re.search(OBS_RE.encode(), drv.serial_bytes())
        if not m:
            raise ValueError("no obs page line on the twin's serial")
        obs = drv.read_obs(int(m.group(1), 16))
        regs = regions(obs["cols"], obs["rows"])
        if regs is None:
            raise ValueError("the twin's mode is too small for the glass")
        panel = regs["app"]
        glyphs = Glyphs()
        looks = 0

        def look():
            nonlocal looks
            looks += 1
            path = os.path.join(drv.workdir, "look.%d.ppm" % looks)
            if not drv.screendump(path):
                raise ValueError("no screendump for look %d" % looks)
            return path

        last = look()
        pressed = False
        for verb, arg in tests:
            line = test_line(verb, arg)
            ok = True
            if verb == "press":
                for ch in arg:
                    drv.tell(b"sendkey " + plan_keyname(ch).encode() + b"\n")
                    time.sleep(KEY_GAP)
                pressed = True
            elif verb == "wait":
                time.sleep(arg / 1000.0)
            else:
                if pressed:
                    time.sleep(SETTLE)
                    pressed = False
                shot = look()
                if verb == "expect changed":
                    ok = region_pixels(shot, panel) != region_pixels(last, panel)
                else:
                    rows = panel_rows(shot, panel, glyphs)
                    found = any(arg in row for row in rows)
                    ok = found if verb == "expect" else not found
                last = shot
            verdicts.append(("ok: " if ok else "fail: ") + line)
            if not ok:
                return [line]
        return []

    return after


def rehearse_metal_plan(blob, name, choices, image, workdir, port=twin.DEFAULT_PORT,
                        plan=None, verdicts=None, lines=LINES):
    """This module's twin behind ring 6c's check: a blob that announces
    point with an offset outside [28, L) is refused before any boot; then
    rehearse_metal, with the plan's tests as the hook for an install and
    no hook for a plain request. Returns (passed, phrase, log)."""
    try:
        point_offset(blob)
    except ValueError as exc:
        return False, str(exc), "fail: %s (no twin boot)\n" % exc
    after = None if plan is None else tests_hook_metal(plan["tests"], [] if verdicts is None else verdicts)
    return rehearse_metal(blob, name, choices, image, workdir, port, lines=lines, after=after)


# ------------------------------------------------------------ the pipeline -

class Metal(Pointer):
    """pointer.Pointer with this module's twin in front of every rehearsal.
    The install path, the germline, the record and the dispatch are the
    frozen ones."""

    def __init__(self, generate, model, root, image, workdir, rehearsal_port, tries,
                 plans_dir=PLANS_DIR):
        super().__init__(generate, model, root, image, workdir, rehearsal_port, tries, plans_dir)
        self.rehearse = rehearse_metal_plan

    def install(self, body, rest, name, amendment):
        # The frozen install path calls plans.rehearse_plan by name; the
        # module attribute is swapped for this module's twin for the
        # duration of the call and restored after - Installer.install
        # directly, since Pointer.install would swap in ring 6c's twin.
        saved = plans.rehearse_plan
        plans.rehearse_plan = rehearse_metal_plan
        try:
            return Installer.install(self, body, rest, name, amendment)
        finally:
            plans.rehearse_plan = saved


# --------------------------------------------------------------- main ------

def main(argv):
    ap = argparse.ArgumentParser(description="The GermOS broker, Stage 7 ring 7a (stage7/DISK.md, the disk).")
    ap.add_argument("--mock", action="store_true", help="canned answers, apps and installs; call nothing")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port on 127.0.0.1 (default 9999)")
    ap.add_argument("--record", default=None, help="append one JSON line per connection to this file")
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds allowed for one claude -p call (default 120)")
    ap.add_argument("--germline", default=os.path.join(REPO, "germline"), help="the cache root (default germline/)")
    ap.add_argument("--image", default=DEFAULT_IMAGE,
                    help="the guest image the twin boots (default stage7/out/esp.img)")
    ap.add_argument("--workdir", default=DEFAULT_WORKDIR,
                    help="the twin's scratch directory (default stage7/out/rehearsal/twin)")
    ap.add_argument("--rehearsal-port", type=int, default=twin.DEFAULT_PORT, help="the twin's listener port (default 9998)")
    ap.add_argument("--tries", type=int, default=2, help="candidates a request may cost (default 2)")
    ap.add_argument("--model", default=None, help="passed to claude -p --model (real mode only)")
    ap.add_argument("--plans", default=PLANS_DIR, help="the plans directory (default plans/)")
    ap.add_argument("--rehearse-app", nargs=2, metavar=("BLOB", "NAME"), default=None,
                    help="a hand run: rehearse this blob under this name in the twin, print the log, exit")
    ap.add_argument("--rehearse", nargs=2, metavar=("BLOB", "PLAN"), default=None,
                    help="a hand run: rehearse this build against this plan's tests in the twin, print the log, exit")
    ap.add_argument("--lines", type=int, default=LINES, help="with a hand run: the S7: lines expected (default 18)")
    args = ap.parse_args(argv)

    if args.rehearse_app:
        blob = open(args.rehearse_app[0], "rb").read()
        name = args.rehearse_app[1].encode("ascii")
        choices = list(POINT_CHOICES) if name == POINT_NAME else []
        ok, why, text = rehearse_metal_plan(blob, name, choices, args.image, args.workdir, args.rehearsal_port,
                                            lines=args.lines)
        sys.stdout.write(text)
        print("PASS" if ok else "FAIL: " + why)
        return 0 if ok else 1

    if args.rehearse:
        blob = open(args.rehearse[0], "rb").read()
        plan = parse_plan(open(args.rehearse[1]).read())
        verdicts = []
        ok, why, text = rehearse_metal_plan(blob, plan["name"].encode(), plan["choices"], args.image, args.workdir,
                                            args.rehearsal_port, plan=plan, verdicts=verdicts, lines=args.lines)
        sys.stdout.write(text)
        for v in verdicts:
            print(v)
        print("PASS" if ok else "FAIL: " + why)
        return 0 if ok else 1

    if args.mock:
        answerer = mock_answer
        generate = mock_point
        model = "mock"
        log("mock mode: canned answers, apps and installs, no calls of any kind")
    else:
        from claude_backend import ask, grow, model_name  # imported only here

        def answerer(question, _ask=ask, _timeout=args.timeout):
            return _ask(question.decode("ascii"), _timeout)

        def generate(body, failure, plan=None, _grow=grow, _timeout=args.timeout, _model=args.model):
            return _grow(body, failure, _timeout, _model, abi=ABI, plan=plan)

        model = model_name(args.model)
        log("real mode: relaying to claude -p with a %.0f s limit per call" % args.timeout)

    metal = Metal(generate, model, args.germline, args.image, args.workdir, args.rehearsal_port,
                  args.tries, args.plans)
    log("germline at %s; plans in %s; the twin boots %s at 1920x1080 on IvyBridge with a 64 MB SATA disk under %s; "
        "rehearsal on 127.0.0.1:%d; %d tries"
        % (args.germline, args.plans, args.image, args.workdir, args.rehearsal_port, metal.tries))
    return serve(args.port, answerer, metal, args.record, read_timeout=10.0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
