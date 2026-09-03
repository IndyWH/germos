#!/usr/bin/env python3
"""Stage 6 ring 6b acceptance tests 3 and 4 - the store of plans.

One driver, ring 6a's shape (stage6/checkglass.py, whose picture, record,
germline, notebook and mock-lifecycle helpers are imported where they fit
- it is frozen, and importable): boot stage6/out/esp.img headless under
OVMF with the standard VGA device stating 1920x1080 through its EDID (the
owner's decision at ring 6a's oracle - the gate, the twin and the oracle
are the same machine), a fresh 16 MB notebook image AND a 16 MB home image
(stage6/HOME.md) as two virtio disks, the caged network of
stage4/UMBILICAL.md, the monitor on stdio, serial to a file; wait for the
guest's own "S6: keyboard ready"; type from OUTSIDE via sendkey; read the
obs page and the surfaces through xp; screendump; quit. Then judge the
broker's record by GLASS.md's frame rule and PLANS.md's fields, the
germline by its provenance, the home image by HOME.md parsed from the
host (the guest's own SHA-256 against hashlib's), the notebook, the serial
capture byte for byte, and the screen pixel by pixel from the shared font.

The broker is broker/plans.py --mock, whose pipeline REHEARSES every
candidate in a real headless boot of a copy of the same image at
1920x1080 with a home drive (broker/twin.py through its post-delivery
hook) and runs the plan's own five-verb tests there. The mock generates
from PLANS.md's canned table and calls nothing outside the repository; the
gate never spends a token.

Two modes:

  --install <smp>  Test 3 (item 6): "! install echo" - the twin runs the
                   plan's tests and passes; the frame carries the name and
                   the installed flag; the app runs in its panel; home.img
                   holds exactly that build with its hash; the germline's
                   provenance names the plan and its hash; the choices row
                   names the installed app at the prompt.

  --store          Test 4 (item 7): the store keeps its word - a reboot
                   with no broker, the launch from disk with nothing on
                   the wire, the liar refused naming its failed test, the
                   amended re-install and the undo, hash-checked.

Pure standard library. Everything runs inside QEMU with exactly three
drives per guest, raw files under stage6/out/, created here or by the
twin; the broker (mock) on 127.0.0.1 only. No real disk is touched; no
Claude call is ever made.

This file is frozen acceptance machinery from plan item 8. See the header
of stage6/test-6b.sh.

Exit 0 on pass, 1 otherwise.
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

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "stage6", "out")
ESP = os.path.join(OUT, "esp.img")
NOTES = os.path.join(OUT, "notes.img")
HOME_IMG = os.path.join(OUT, "home.img")
BROKER = os.path.join(REPO, "broker", "plans.py")
PLANS_DIR = os.path.join(REPO, "plans")
GERMLINE = os.path.join(OUT, "germline")
REHEARSAL = os.path.join(OUT, "rehearsal")
TWIN_WORKDIR = os.path.join(REHEARSAL, "twin")
OVMF = "/usr/share/ovmf/OVMF.fd"

sys.path.insert(0, os.path.join(REPO, "broker"))
sys.path.insert(0, os.path.join(REPO, "stage6"))
from glass import (app_frame, refusal_frame, parse_response, regions, choices_row,  # noqa: E402
                   ABI, MACHINE)
import twin  # noqa: E402
from twin import Driver  # noqa: E402
import plans  # noqa: E402
from plans import (parse_plan, install_key, twin_extra_args, TWIN_HOME, PAD_BIG, LINES)  # noqa: E402
from checkglass import (check_echo, dump_capture, judge_request_bytes, read_record, record_count,  # noqa: E402
                        parse_notebook, check_image, port_state, stop_mock, report, say,
                        check_region_rows, PROMPT, open_shot, blank_cell, cell_census,
                        check_colour_discipline, check_choices, check_mode_field, check_app_panel_blank,
                        check_strip, check_surfaces, check_counts, germline_entries, fixture_self_check,
                        check_cage_argv, KEY_GAP, SETTLE)
from rehearse import (read_ppm, load_font, render_cell, cell_matches)  # noqa: E402

DISK_BYTES = 16 * 1024 * 1024

# The cage, exactly as stage4/UMBILICAL.md spells it, with this ring's MAC.
BROKER_PORT = 9999
REHEARSAL_PORT = 9998
MAC = "52:54:00:a1:06:02"
CAGE_NETDEV = ("user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:%d-cmd:nc -N 127.0.0.1 %d"
               % (BROKER_PORT, BROKER_PORT))
CAGE_DEVICE = "virtio-net-pci,netdev=n0,mac=" + MAC

# The display, spelled once here and asserted against the broker module's.
DISPLAY = ["-vga", "none", "-device", "VGA,edid=on,xres=1920,yres=1080"]

READY = b"S6: keyboard ready"


# ------------------------------------------------------------- HOME.md ------
# stage6/HOME.md, "Parsing it cold, in Python", verbatim.

SECTOR = 512
MAGIC = b"GERMHOME"
TABLE_FIRST, TABLE_SECTORS, DATA_FIRST = 1, 8, 9
ENTRY = 256
ENTRIES = 16
NAME_RE = re.compile(rb"[a-z][a-z0-9-]{0,31}")
BLOB_MIN, BLOB_MAX = 16, 1048576


def parse_choice_slots(slots):
    """GLASS.md's four 13-byte slots -> [(key, label bytes)]; ValueError."""
    choices = []
    for i in range(4):
        slot = slots[i * 13:(i + 1) * 13]
        if slot[0] == 0:
            if any(slot):
                raise ValueError("an empty choice slot is not all zero")
            continue
        if len(choices) < i:
            raise ValueError("choice slots are not packed from the first")
        label = slot[1:].split(b"\0", 1)[0]
        if not (0x20 <= slot[0] <= 0x7E) or not 1 <= len(label) <= 12 \
                or not all(0x20 <= b <= 0x7E for b in label) or any(slot[1 + len(label):]):
            raise ValueError("a choice is a printable key and a 1..12 byte printable label")
        choices.append((slot[0], label))
    return choices


def parse_build(rec, off, capacity, required):
    size, first, sectors, zero = struct.unpack_from("<IIII", rec, off)
    digest = rec[off + 16:off + 48]
    if not required and size == 0:
        if first or sectors or zero or any(digest):
            raise ValueError("an absent build is not all zero")
        return None
    if not BLOB_MIN <= size <= BLOB_MAX or sectors != (size + SECTOR - 1) // SECTOR or zero \
            or first < DATA_FIRST or first + sectors > capacity:
        raise ValueError("build fields size %d first %d sectors %d are not valid" % (size, first, sectors))
    return {"size": size, "first": first, "sectors": sectors, "sha256": digest.hex()}


def parse_home(data):
    """The whole image. Returns {"capacity", "entries": [entry or None] * 16,
    "next_free"}; an entry is {"name", "current", "previous", "choices"}.
    Raises ValueError on anything the document forbids."""
    if data[0:8] != MAGIC:
        raise ValueError("no GERMHOME magic")
    version, sector, tfirst, tsectors, dfirst, capacity = struct.unpack_from("<IIQQQQ", data, 8)
    if (version, sector, tfirst, tsectors, dfirst) != (1, SECTOR, TABLE_FIRST, TABLE_SECTORS, DATA_FIRST):
        raise ValueError("bad header")
    if capacity != len(data) // SECTOR:
        raise ValueError("header capacity %d, image has %d sectors" % (capacity, len(data) // SECTOR))
    if any(data[0x30:SECTOR]):
        raise ValueError("header padding not zero")
    entries = []
    next_free = DATA_FIRST
    for i in range(ENTRIES):
        base = (TABLE_FIRST + i // 2) * SECTOR + (i % 2) * ENTRY
        rec = data[base:base + ENTRY]
        if rec[0] == 0:
            if any(rec):
                raise ValueError("entry %d: empty slot not all zero" % i)
            entries.append(None)
            continue
        name = rec[0:32].split(b"\0", 1)[0]
        if not NAME_RE.fullmatch(name) or any(rec[len(name):32]):
            raise ValueError("entry %d: bad name %r" % (i, rec[0:32]))
        try:
            current = parse_build(rec, 0x20, capacity, True)
            previous = parse_build(rec, 0x50, capacity, False)
            choices = parse_choice_slots(rec[0x80:0xB4])
        except ValueError as exc:
            raise ValueError("entry %d (%s): %s" % (i, name.decode(), exc))
        if any(rec[0xB4:ENTRY]):
            raise ValueError("entry %d: padding not zero" % i)
        for b in (current, previous):
            if b:
                next_free = max(next_free, b["first"] + b["sectors"])
        entries.append({"name": name.decode("ascii"), "current": current, "previous": previous,
                        "choices": choices})
    return {"capacity": capacity, "entries": entries, "next_free": next_free}


def blob_of(data, build):
    """The build's bytes, from its extent."""
    start = build["first"] * SECTOR
    return data[start:start + build["size"]]


# ---------------------------------------------------------------- driver ----

def fresh_disk(path):
    if os.path.exists(path):
        os.remove(path)
    with open(path, "wb") as fh:
        fh.truncate(DISK_BYTES)


def qemu_argv(smp, disk, home, serial_path):
    """The one place the QEMU command is spelled. Test 4 inspects this."""
    return [
        "qemu-system-x86_64",
        "-machine", "q35",
        "-m", "256M",
        "-smp", str(smp),
        "-bios", OVMF,
    ] + list(DISPLAY) + [
        "-drive", "format=raw,file=" + ESP,
        "-drive", "format=raw,file=" + disk + ",if=virtio",
        "-drive", "format=raw,file=" + home + ",if=virtio",
        "-netdev", CAGE_NETDEV,
        "-device", CAGE_DEVICE,
        "-display", "none",
        "-serial", "file:" + serial_path,
        "-monitor", "stdio",
    ]


def drive(smp, disk, home, steps, serial_path, ready=READY, ready_limit=60.0):
    """Boot inside the cage with both disks, wait for the guest's own ready
    line, run the steps - ("type", text), ("sleep", seconds),
    ("wait_record", path, count, timeout), ("shot", path), ("obs", label),
    ("surfaces", label) - quit, reap. Returns (serial_bytes, reads, error).
    Never leaves a QEMU running behind us."""
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

    proc = subprocess.Popen(qemu_argv(smp, disk, home, serial_path),
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
            time.sleep(1.0)
            for step in steps:
                if step[0] == "type":
                    for ch in step[1]:
                        drv.tell(b"sendkey " + plans.plan_keyname(ch).encode() + b"\n" if ch not in "\n\t\x1b"
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
                        m = re.search(r"S6: obs page 0x([0-9a-f]{16})", text)
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


# ------------------------------------------------------- the serial claims --

BOOT_PATTERNS = [
    (r"S6: alive", "S6: alive"),
    (r"S6: edid (\d+)x(\d+)", "S6: edid <W>x<H>"),
    (r"S6: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})", "S6: gop <W>x<H> fb 0x<16 hex>"),
    (r"S6: boot services exited", "S6: boot services exited"),
    (r"S6: gdt and paging ours", "S6: gdt and paging ours"),
    (r"S6: idt ready", "S6: idt ready"),
    (r"S6: cores found (\d+)", "S6: cores found <N>"),
    (r"S6: cores woken (\d+)", "S6: cores woken <N>"),
    (r"S6: console (\d+)x(\d+)", "S6: console <COLS>x<ROWS>"),
    (r"S6: disk (\d+) sectors", "S6: disk <N> sectors"),
    (r"S6: notebook (formatted|\d+ notes)", "S6: notebook formatted | S6: notebook <N> notes"),
    (r"S6: home (\d+) apps", "S6: home <N> apps"),
    (r"S6: nic ([0-9a-f]{2}(?::[0-9a-f]{2}){5})", "S6: nic <mac>"),
    (r"S6: component region 0x([0-9a-f]{16}) (\d+) bytes", "S6: component region 0x<16 hex> 1048576 bytes"),
    (r"S6: obs page 0x([0-9a-f]{16})", "S6: obs page 0x<16 hex>"),
    (r"S6: glass core (\d+)", "S6: glass core <id>"),
    (r"S6: keyboard ready", "S6: keyboard ready"),
]


def check_boot_lines(capture, smp, notebook_want, home_want):
    """HOME.md's seventeen lines, in order, self-consistent. Returns
    (problems, geometry) with geometry = (w, h, cols, rows)."""
    problems = []
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S6: [^\n]*", text)
    if len(got) != LINES:
        problems.append("expected exactly %d S6: lines, found %d" % (LINES, len(got)))
    errs = re.findall(r"ERR: [^\n]*", text)
    if errs:
        problems.append("the guest reported: %s" % "; ".join(errs[:3]))
    w = h = cols = rows = None
    ew = eh = None
    found = woken = None
    for i, (pattern, shape) in enumerate(BOOT_PATTERNS):
        line = got[i] if i < len(got) else ""
        m = re.fullmatch(pattern, line)
        if not m:
            problems.append("line %d: got '%s', want '%s'" % (i + 1, line, shape))
            continue
        if i == 1:
            ew, eh = int(m.group(1)), int(m.group(2))
        elif i == 2:
            w, h = int(m.group(1)), int(m.group(2))
            if (w, h) != (ew, eh):
                problems.append("line 3: the mode is %dx%d but the EDID prefers %dx%d" % (w, h, ew, eh))
        elif i == 6:
            found = int(m.group(1))
        elif i == 7:
            woken = int(m.group(1))
        elif i == 8:
            cols, rows = int(m.group(1)), int(m.group(2))
        elif i == 9 and int(m.group(1)) != DISK_BYTES // SECTOR:
            problems.append("line 10: the guest counted %s sectors, but the image is %d sectors" % (m.group(1), DISK_BYTES // SECTOR))
        elif i == 10 and m.group(1) != notebook_want:
            problems.append("line 11: got 'S6: notebook %s', want 'S6: notebook %s'" % (m.group(1), notebook_want))
        elif i == 11 and int(m.group(1)) != home_want:
            problems.append("line 12: got 'S6: home %s apps', want 'S6: home %d apps'" % (m.group(1), home_want))
        elif i == 12 and m.group(1) != MAC:
            problems.append("line 13: the guest read MAC %s, but the harness gave the device %s" % (m.group(1), MAC))
        elif i == 13:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32 or addr % 4096 != 128 or int(m.group(2)) != BLOB_MAX:
                problems.append("line 14: the component region line %r is not what GLASS.md asks" % line)
        elif i == 14:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32 or addr % 4096:
                problems.append("line 15: the obs page 0x%s is zero, above 4 GB or not page-aligned" % m.group(1))
    if found is not None and found != smp:
        problems.append("cores found is %d, but the machine was given -smp %d" % (found, smp))
    if woken is not None and woken != smp:
        problems.append("cores woken is %d, but the machine was given -smp %d" % (woken, smp))
    if None not in (w, h, cols, rows) and (cols != w // 16 or rows != h // 16):
        problems.append("console claims %dx%d cells, but %dx%d pixels / 16 = %dx%d" % (cols, rows, w, h, w // 16, h // 16))
    return problems, (w, h, cols, rows)


# ---------------------------------------------------------------- the mock --

def start_mock(record_path, wipe_germline=True):
    """Start plans.py --mock with the gate's germline (wiped unless told
    otherwise), the gate's image as the twin's, the twin's own workdir,
    its record file; wait for its listening line."""
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
    log = open(os.path.join(OUT, "mock.plans.stderr.txt"), "ab")
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


# ---------------------------------------------------------------- the wire --

def plan_of(name):
    data = open(os.path.join(PLANS_DIR, name + ".md"), "rb").read()
    return data, parse_plan(data.decode("latin-1"))


def check_install_entry(i, entry, body, source, calls, rehearsals, answer_kind, answer_frame,
                        answer=None, plan=None, amendment=None, tests=None):
    """One install connection judged: the raw bytes by GERMLINE.md, then
    GLASS.md's fields and PLANS.md's - plan, plan_sha256, amendment, tests."""
    problems = []
    try:
        kind, got = judge_request_bytes(bytes.fromhex(entry["request"]))
    except (ValueError, KeyError) as exc:
        return ["connection %d: bytes are not a valid request frame: %s" % (i, exc)]
    if (kind, got) != ("grow", body):
        problems.append("connection %d: the guest sent %s %r, want the grow request %r" % (i, kind, got, body))
    key = plan_sha = None
    if plan is not None:
        data, _ = plan_of(plan)
        key = install_key(plan, data, amendment)
        plan_sha = hashlib.sha256(data).hexdigest()
    fields = {"kind": "grow", "error": None, "text": body, "key": key, "source": source,
              "generation_calls": calls, "rehearsals": rehearsals, "answer_kind": answer_kind,
              "abi": ABI, "name": plan if answer_kind == "app" else None, "plan": plan,
              "plan_sha256": plan_sha, "amendment": amendment}
    if tests is not None:
        fields["tests"] = tests
    for k, v in fields.items():
        if entry.get(k) != v:
            problems.append("connection %d: %s is %r, want %r" % (i, k, entry.get(k), v))
    want_sha = hashlib.sha256(answer_frame).hexdigest()
    if entry.get("answer_sha256") != want_sha:
        problems.append("connection %d: answer_sha256 is %r, but the frame PLANS.md gives hashes to %s (%d bytes)"
                        % (i, entry.get("answer_sha256"), want_sha, len(answer_frame)))
    if answer is not None and entry.get("answer") != answer:
        problems.append("connection %d: answer is %r, want %r" % (i, entry.get("answer"), answer))
    return problems


# ------------------------------------------------------------ the germline --

def check_install_germline(root, plan, blob, amendment=None, tests=None, model="mock"):
    """The entry for an installed plan: the blob, GLASS.md's provenance
    with PLANS.md's extra fields, a seventeen-line rehearsal log with the
    hook's verdict."""
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
    if len(re.findall(r"^S6: ", rlog, re.M)) != LINES:
        problems.append("entry %s: rehearsal.log does not hold the twin's seventeen S6: lines" % key)
    if "ERR:" in rlog:
        problems.append("entry %s: rehearsal.log carries an ERR: line" % key)
    if "ok: the post-delivery hook found nothing" not in rlog:
        problems.append("entry %s: rehearsal.log does not say the plan's tests passed" % key)
    return problems


# ------------------------------------------------------------ the home ------

def check_home(path, want, label):
    """The home image parsed by HOME.md against `want`: {name: {"current":
    (blob, first or None), "previous": (blob, first or None) or None,
    "choices": [...]}}, every other entry empty; each build's extent holds
    its bytes and its hash is hashlib's. Returns (problems, parsed)."""
    try:
        data = open(path, "rb").read()
    except OSError as exc:
        return ["%s: cannot read the home image: %s" % (label, exc)], None
    if len(data) != DISK_BYTES:
        return ["%s: the image is %d bytes, but the harness made it %d" % (label, len(data), DISK_BYTES)], None
    try:
        home = parse_home(data)
    except ValueError as exc:
        return ["%s: the image is not a home (HOME.md): %s" % (label, exc)], None
    problems = []
    names = [e["name"] for e in home["entries"] if e]
    if sorted(names) != sorted(want):
        problems.append("%s: the home holds %r, want %r" % (label, names, sorted(want)))
    for e in home["entries"]:
        if not e or e["name"] not in want:
            continue
        w = want[e["name"]]
        for which in ("current", "previous"):
            got = e[which]
            wb = w.get(which)
            if wb is None:
                if got is not None:
                    problems.append("%s: %s has a %s build, want none" % (label, e["name"], which))
                continue
            blob, first = wb
            if got is None:
                problems.append("%s: %s has no %s build, want %d bytes" % (label, e["name"], which, len(blob)))
                continue
            if got["size"] != len(blob) or got["sectors"] != (len(blob) + 511) // 512:
                problems.append("%s: %s's %s build is %d bytes in %d sectors, want %d" % (label, e["name"], which, got["size"], got["sectors"], len(blob)))
            if got["sha256"] != hashlib.sha256(blob).hexdigest():
                problems.append("%s: %s's %s build hash is %s, but hashlib says %s - the guest's SHA-256 disagrees"
                                % (label, e["name"], which, got["sha256"][:16], hashlib.sha256(blob).hexdigest()[:16]))
            if blob_of(data, got) != blob:
                problems.append("%s: the bytes at %s's %s extent (sector %d) are not the build" % (label, e["name"], which, got["first"]))
            if first is not None and got["first"] != first:
                problems.append("%s: %s's %s build is at sector %d, want %d" % (label, e["name"], which, got["first"], first))
            end = (got["first"] * SECTOR + got["size"], (got["first"] + got["sectors"]) * SECTOR)
            if any(data[end[0]:end[1]]):
                problems.append("%s: %s's %s build has a non-zero tail after its bytes" % (label, e["name"], which))
        if e["choices"] != w.get("choices", []):
            problems.append("%s: %s's choices are %r, want %r" % (label, e["name"], e["choices"], w.get("choices", [])))
    return problems, home


# ------------------------------------------------------------ the picture ---

def check_one_cell_panel(shot, geometry, ch):
    """The echo app's panel: cell (1, 1) is `ch`, every other panel cell
    blank, two colours only."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    row0, col0, prows, pcols = regions(cols, rows)["app"]
    problems = []
    if not cell_matches(pixels, width, row0 + 1, col0 + 1, render_cell(font, ch)):
        problems.append("app panel cell (1, 1) is not %r - %s" % (ch, cell_census(pixels, width, row0 + 1, col0 + 1)))
    strays = [(r, c) for r in range(prows) for c in range(pcols)
              if (r, c) != (1, 1) and not cell_matches(pixels, width, row0 + r, col0 + c, blank_cell())]
    if strays:
        problems.append("%d other app-panel cell(s) are not blank, the first at %r" % (len(strays), strays[0]))
    stray = check_colour_discipline(pixels, width, height)
    if stray:
        problems.append(stray)
    return problems


CHOICES_NONE = choices_row(False, 0, [])                 # "? ask   ! grow"
CHOICES_ECHO_RUNNING = choices_row(True, 1, [])           # "Esc exit   Tab prompt"
CHOICES_PROMPT_ECHO = CHOICES_NONE + "   ! echo"           # HOME.md, "The choices row"
ECHO_TESTS_OK = ["ok: press a", 'ok: expect "a"', "ok: press b", 'ok: expect "b"', 'ok: expect not "a"']
LIAR_TESTS = ["ok: press a", 'fail: expect "a"']
REFUSAL_LIAR = 'rehearsal failed: expect "a"'


# ----------------------------------------------------------------- install --

def run_install(smp):
    """Test 3 at one -smp value: the install, mocked."""
    echo, problems = fixture_self_check("echo")
    if not report("the echo fixture is not what the repository says", problems):
        return 1
    say("stage6/echo.asm reproduces stage6/echo.bin: %d bytes, sha256 %s" % (len(echo), hashlib.sha256(echo).hexdigest()[:16]))
    plan_bytes, plan = plan_of("echo")
    if plan["tests"] != [("press", "a"), ("expect", "a"), ("press", "b"), ("expect", "b"), ("expect not", "a")] or plan["choices"]:
        say("plans/echo.md is not the plan this test expects: %r" % plan)
        return 1

    record = os.path.join(OUT, "broker.install.%d.jsonl" % smp)
    serial = os.path.join(OUT, "serial.install.%d.txt" % smp)
    shots = {k: os.path.join(OUT, "screen.install.%d.%s.ppm" % (smp, k)) for k in ("i", "a", "b", "c")}
    mock, err = start_mock(record)
    if err:
        say(err)
        return 1
    say("mock broker listening on 127.0.0.1:%d, germline wiped at %s" % (BROKER_PORT, os.path.relpath(GERMLINE, REPO)))
    try:
        fresh_disk(NOTES)
        fresh_disk(HOME_IMG)
        steps = [
            ("type", "before\n"), ("sleep", 1.5),
            ("type", "! install echo\n"), ("sleep", 3.0),
            ("obs", "i"), ("shot", shots["i"]),
            ("wait_record", record, 1, 150.0), ("sleep", 3.0),
            ("type", "q"), ("sleep", 1.0),
            ("shot", shots["a"]), ("obs", "a"),
            ("type", "\t"), ("sleep", 0.5),
            ("type", "mid\n"), ("sleep", 1.5),
            ("type", "\t"), ("sleep", 0.5),
            ("type", "z"), ("sleep", 1.0),
            ("shot", shots["b"]),
            ("type", "\x1b"), ("sleep", 2.0),
            ("type", "after\n"), ("sleep", SETTLE),
            ("shot", shots["c"]),
        ]
        capture, reads, err = drive(smp, NOTES, HOME_IMG, steps, serial)
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1

    ok = True
    problems, geometry = check_boot_lines(capture, smp, "formatted", 0)
    problems += check_echo(capture, b"before\r\n! install echo\r\nmid\r\nafter\r\n")
    ok &= report("the serial log is not what the spec asks for", problems, capture)
    if not problems:
        say("seventeen boot lines, home 0 apps, nic %s; the wire after ready carries exactly the four typed lines" % MAC)

    entries, problems = read_record(record)
    if entries is not None:
        if len(entries) != 1:
            problems.append("the broker saw %d connection(s), want 1" % len(entries))
        if entries:
            problems += check_install_entry(1, entries[0], "install echo", "generated", 1, ["pass"], "app",
                                            app_frame(echo, b"echo", [], 0, installed=1),
                                            plan="echo", amendment=None, tests=ECHO_TESTS_OK)
    ok &= report("the broker's record is not what PLANS.md asks for", problems)
    if not problems:
        say("the broker received 'install echo' byte-exact, generated once, rehearsed once with the plan's five tests passing, "
            "and sent the app frame with installed 1")

    problems = check_install_germline(GERMLINE, "echo", echo, tests=ECHO_TESTS_OK)
    names = germline_entries(GERMLINE)
    if len(names) != 1:
        problems.append("the germline holds %d entries %r, want exactly 1" % (len(names), names))
    ok &= report("the germline is not what PLANS.md asks for", problems)
    if not problems:
        say("the germline holds exactly one entry under the plan's key, with the plan, its hash, installed and the tests in its provenance")

    problems, home = check_home(HOME_IMG, {"echo": {"current": (echo, DATA_FIRST), "previous": None, "choices": []}}, "the home image")
    ok &= report("the home image is not what HOME.md asks for", problems)
    if not problems:
        say("the home image holds exactly echo: %d bytes at sector %d, the guest's SHA-256 equal to hashlib's, no previous build" % (len(echo), DATA_FIRST))

    problems = check_image(NOTES, ["before", "mid", "after"])
    ok &= report("the notebook is not what it should be", problems)
    if not problems:
        say("the notebook holds exactly 'before', 'mid' and 'after'")

    if None in geometry:
        say("no picture to judge - the boot lines were wrong")
        return 1
    regs = regions(geometry[2], geometry[3])
    conv = regs["conversation"]

    problems = []
    if "i" not in reads:
        problems.append("the obs page could not be read during the install")
    else:
        problems += check_counts(reads["i"], {"mode": 4, "focus": 0, "requests": 1}, "screen I")
        problems += check_mode_field(shots["i"], geometry, "installing")
        problems += check_choices(shots["i"], geometry, CHOICES_NONE)
        problems += check_app_panel_blank(shots["i"], geometry)
    ok &= report("screen I does not show 'installing'", problems)
    if not problems:
        say("screen I: 'installing' on the strip and in the page while the twin rehearses, the prompt's row, the panel blank")

    problems = check_one_cell_panel(shots["a"], geometry, "q")
    problems += check_choices(shots["a"], geometry, CHOICES_ECHO_RUNNING)
    problems += check_mode_field(shots["a"], geometry, "running echo")
    problems += check_region_rows(shots["a"], geometry, conv, ["> before", "> ! install echo", "installed echo", PROMPT])
    if "a" in reads:
        problems += check_counts(reads["a"], {"mode": 3, "name": "echo", "focus": 1, "grows_generated": 1,
                                              "grows_served": 0, "errors": 0}, "screen A")
    else:
        problems.append("the obs page could not be read at screen A")
    ok &= report("screen A does not show the installed app running", problems)
    if not problems:
        say("screen A: the app's one cell is 'q', 'running echo' on the strip, 'installed echo' in the conversation")

    problems = check_one_cell_panel(shots["b"], geometry, "z")
    problems += check_choices(shots["b"], geometry, CHOICES_ECHO_RUNNING)
    problems += check_region_rows(shots["b"], geometry, conv, ["> before", "> ! install echo", "installed echo", "> mid", PROMPT])
    ok &= report("screen B does not show the note beside the running app", problems)
    if not problems:
        say("screen B: '> mid' journaled beside the app, the app then took 'z'")

    problems = check_app_panel_blank(shots["c"], geometry)
    problems += check_choices(shots["c"], geometry, CHOICES_PROMPT_ECHO)
    problems += check_mode_field(shots["c"], geometry, "prompt")
    problems += check_region_rows(shots["c"], geometry, conv,
                                  ["> before", "> ! install echo", "installed echo", "> mid", "> after", PROMPT])
    ok &= report("screen C does not show the prompt back with the installed app on the choices row", problems)
    if not problems:
        say("screen C: the panel blank, the choices row '%s', 'prompt' on the strip, the conversation intact" % CHOICES_PROMPT_ECHO)

    say("-smp %d: %s" % (smp, "the install held - rehearsed against the plan, kept on the home image, run in its panel" if ok else "the install did not hold"))
    return 0 if ok else 1


# ------------------------------------------------------------------- store --

def check_argv(argv, port, want_mac, want_drives):
    """A QEMU command inspected for the cage and THIS ring's display: slirp
    user mode, restrict=on, one guestfwd from 10.0.2.4:9999 by nc to
    127.0.0.1 on the given port, no hostfwd, one virtio-net-pci on n0 (with
    the MAC when wanted), -vga none and the one VGA device with the
    1920x1080 EDID, exactly want_drives drives, every one a file under
    stage6/out/."""
    problems = check_cage_argv(argv, port, want_mac)
    problems = [p for p in problems if "the display is not" not in p]      # 6a's check wants 1440x1440
    devices = [argv[i + 1] for i, a in enumerate(argv) if a == "-device"]
    vgas = [d for d in devices if d.startswith("VGA")]
    if vgas != [DISPLAY[3]]:
        problems.append("the display is not %r: %r" % (DISPLAY[3], vgas))
    drives = [argv[i + 1] for i, a in enumerate(argv) if a == "-drive"]
    if len(drives) != want_drives:
        problems.append("expected exactly %d drives, found %d: %r" % (want_drives, len(drives), drives))
    return problems


def run_store():
    """Test 4: the store keeps its word, at -smp 8."""
    smp = 8
    argv = qemu_argv(smp, NOTES, HOME_IMG, os.path.join(OUT, "x"))
    problems = check_argv(argv, BROKER_PORT, MAC, 3)
    if plans.DISPLAY != DISPLAY or twin.VGA_ARGS != DISPLAY:
        problems.append("the broker module's display %r or the twin's %r is not the harness's %r"
                        % (plans.DISPLAY, twin.VGA_ARGS, DISPLAY))
    if not report("the harness's own QEMU command is not the cage with this ring's display", problems):
        return 1
    say("the checker's QEMU command carries restrict=on, the single guestfwd via nc to 127.0.0.1:%d, the 1920x1080 device and three drives under stage6/out/" % BROKER_PORT)

    rargv = twin.qemu_argv(ESP, os.path.join(TWIN_WORKDIR, "notes.img"), os.path.join(TWIN_WORKDIR, "serial.txt"),
                           REHEARSAL_PORT, extra_args=twin_extra_args())
    problems = check_argv(rargv, REHEARSAL_PORT, None, 3)
    if not TWIN_HOME.startswith(OUT + os.sep):
        problems.append("the twin's home image %r is not under stage6/out/" % TWIN_HOME)
    if twin.DEFAULT_PORT != REHEARSAL_PORT:
        problems.append("the twin's default port is %d, not %d" % (twin.DEFAULT_PORT, REHEARSAL_PORT))
    if not report("the twin's QEMU command, as broker/plans.py builds it, is not the cage with this ring's display", problems):
        return 1
    say("the twin's command carries the same cage on 127.0.0.1:%d, the same display, and the home drive %s"
        % (REHEARSAL_PORT, os.path.relpath(TWIN_HOME, REPO)))

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
    say("the three plans parse: echo and liar with five tests, the calculator with ten and two choices")

    # ---------------------------------------------------------- boot A ----
    record_a = os.path.join(OUT, "broker.store.a.jsonl")
    mock, err = start_mock(record_a)
    if err:
        say(err)
        return 1
    say("boot A: mock up, germline wiped; '! install echo'")
    try:
        fresh_disk(NOTES)
        fresh_disk(HOME_IMG)
        steps = [
            ("type", "! install echo\n"), ("wait_record", record_a, 1, 150.0), ("sleep", 3.0),
            ("type", "\x1b"), ("sleep", 1.0),
        ]
        capture, reads, err = drive(smp, NOTES, HOME_IMG, steps, os.path.join(OUT, "serial.store.a.txt"))
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    ok = True
    problems, geometry = check_boot_lines(capture, smp, "formatted", 0)
    problems += check_echo(capture, b"! install echo\r\n")
    entries, more = read_record(record_a)
    problems += more
    if entries is not None:
        if len(entries) != 1:
            problems.append("boot A: the broker saw %d connection(s), want 1" % len(entries))
        if entries:
            problems += check_install_entry(1, entries[0], "install echo", "generated", 1, ["pass"], "app",
                                            app_frame(echo, b"echo", [], 0, installed=1), plan="echo", tests=ECHO_TESTS_OK)
    more, home_a = check_home(HOME_IMG, {"echo": {"current": (echo, DATA_FIRST), "previous": None, "choices": []}}, "boot A")
    problems += more
    ok &= report("boot A did not install echo", problems, capture)
    if not problems:
        say("boot A: echo installed at sector %d, the record and the home image as PLANS.md and HOME.md say" % DATA_FIRST)
    shutil.copyfile(HOME_IMG, os.path.join(OUT, "home.after-a.img"))
    if None in geometry:
        return 1
    regs = regions(geometry[2], geometry[3])
    conv = regs["conversation"]

    # ---------------------------------------------------------- boot B ----
    if port_state(BROKER_PORT) == "open":
        say("boot B: something is listening on 127.0.0.1:%d - the no-broker boot cannot run" % BROKER_PORT)
        return 1
    say("boot B: NO broker (127.0.0.1:%d closed); the same home image; '! echo' from disk" % BROKER_PORT)
    shots = {k: os.path.join(OUT, "screen.store.%s.ppm" % k) for k in ("p", "l", "u", "e", "d")}
    fresh_disk(NOTES)
    steps = [
        ("obs", "r"), ("shot", shots["p"]),
        ("type", "! echo\n"), ("sleep", 2.0),
        ("type", "b"), ("sleep", 1.0),
        ("shot", shots["l"]), ("obs", "l"),
        ("type", "\x1b"), ("sleep", 1.0),
        ("type", "! undo install echo\n"), ("sleep", 1.5),
        ("shot", shots["u"]), ("obs", "u"),
    ]
    capture, reads, err = drive(smp, NOTES, HOME_IMG, steps, os.path.join(OUT, "serial.store.b.txt"))
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    problems, _ = check_boot_lines(capture, smp, "formatted", 1)
    problems += check_echo(capture, b"! echo\r\n! undo install echo\r\n")
    ok &= report("boot B's serial log is not what the spec asks for", problems, capture)
    if not problems:
        say("boot B: seventeen lines, 'S6: home 1 apps'; the serial echo exactly the two typed lines")
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
    problems += check_image(NOTES, [])
    if open(HOME_IMG, "rb").read() != open(os.path.join(OUT, "home.after-a.img"), "rb").read():
        problems.append("the home image changed during boot B - a launch or a refused undo must not write it")
    ok &= report("boot B did not launch echo from disk with nothing on the wire", problems)
    if not problems:
        say("boot B: '! echo' on the choices row; the app ran from disk showing 'b'; wire_conns 0 and bytes in/out unchanged "
            "(%d/%d) between the read after ready and the read after the launch; 'echo has no previous build' counted; the image untouched"
            % (reads["r"]["bytes_in"], reads["r"]["bytes_out"]))

    # ---------------------------------------------------------- boot C ----
    record_c = os.path.join(OUT, "broker.store.c.jsonl")
    mock, err = start_mock(record_c, wipe_germline=False)
    if err:
        say(err)
        return 1
    say("boot C: mock up, germline kept; the liar, the amended re-install, the germline re-install, the undo, the launch")
    try:
        fresh_disk(NOTES)
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
        capture, reads, err = drive(smp, NOTES, HOME_IMG, steps, os.path.join(OUT, "serial.store.c.txt"))
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    keys_typed = sum(len(s[1]) for s in steps if s[0] == "type")
    problems, _ = check_boot_lines(capture, smp, "formatted", 1)
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
            "'echo, but big' generated (3) as a 4096-byte build with installed 1; 'install echo' served from the germline (still 3) with source 1 and installed 1")

    problems = check_install_germline(GERMLINE, "echo", echo, tests=ECHO_TESTS_OK)
    problems += check_install_germline(GERMLINE, "echo", big, amendment="but big", tests=ECHO_TESTS_OK)
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
    # previous. Both extents still hold their builds, hash-checked.
    problems, home_c = check_home(HOME_IMG, {"echo": {"current": (big, DATA_FIRST + 1), "previous": (echo, DATA_FIRST + 9),
                                                      "choices": []}}, "boot C")
    if home_c and home_c["next_free"] != DATA_FIRST + 10:
        problems.append("boot C: the next free sector is %d, want %d" % (home_c["next_free"], DATA_FIRST + 10))
    ok &= report("the home image after the re-installs and the undo is not what HOME.md asks for", problems)
    if not problems:
        say("the home image: echo's current build is the padded one at sector %d and its previous the first build at sector %d - "
            "the undo swapped them, both extents hash-checked from the host" % (DATA_FIRST + 1, DATA_FIRST + 9))

    problems = check_image(NOTES, ["last"])
    ok &= report("the notebook is not what it should be", problems)

    problems = check_one_cell_panel(shots["e"], geometry, "c")
    problems += check_mode_field(shots["e"], geometry, "running echo")
    ok &= report("screen E does not show the restored build running", problems)
    if not problems:
        say("screen E: the restored build ran from disk and took 'c'")

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

    say("the store: %s" % ("kept its word" if ok else "did not keep its word"))
    return 0 if ok else 1


def main(argv):
    if argv == ["--store"]:
        return run_store()
    if len(argv) == 2 and argv[0] == "--install":
        try:
            return run_install(int(argv[1]))
        except ValueError:
            pass
    say("usage: checkplans.py --install <smp> | --store")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
