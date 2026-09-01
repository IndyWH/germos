#!/usr/bin/env python3
"""Stage 5 acceptance tests 3 and 4 - the growth, and the germline.

One driver owns every booted run bar test 2's, as Stage 4's
checkumbilical.py did: boot stage5/out/esp.img headless under OVMF with a
fresh 16 MB raw notebook image as a virtio disk and the caged network of
stage4/UMBILICAL.md - slirp with restrict=on and one guestfwd, delivered per
connection by netcat to the broker on 127.0.0.1:9999 - the QEMU monitor on
stdio and serial to a file; wait for the guest itself to say "S5: keyboard
ready"; type from OUTSIDE via the monitor's sendkey; screendump; quit. Then
judge the broker's record by stage5/GERMLINE.md's own frame rule, the
germline directory by its provenance rule, the disk image by NOTEBOOK.md,
the serial capture byte for byte, and the screen pixel by pixel from the
shared font.

The broker is the Stage 5 one, broker/germline.py --mock, whose grow
pipeline REHEARSES every candidate in a real headless boot of the same
image (broker/rehearse.py) - so a grow costs a second QEMU, on its own
port, in its own scratch directory, while the gate's own guest waits on
the wire. The mock generates from GERMLINE.md's canned table and calls
nothing outside the repository; the gate never spends a token.

Two modes, two acceptance tests:

  --grow <smp>   Test 3. The mock up with a wiped germline; boot; type
                 "before", "? ping", then "! test component"; wait for
                 the grow to be recorded (it rehearses); type "k" while
                 the component runs; screendump A; Esc; type "after";
                 screendump B; quit. Assert: the thirteen boot lines; the
                 echo after ready EXACTLY the four typed lines (the k and
                 the Esc never reach serial); the record holding ping ->
                 pong and one grow whose raw bytes ARE GERMLINE.md's frame,
                 generated, one generation call, one passing rehearsal, a
                 component whose frame hash the checker rebuilds from
                 stage5/component.bin; the germline holding exactly that
                 one entry; the notebook holding exactly "before" and
                 "after"; screen A the test component's five strips at
                 their cells with "key: k" and nothing else on a cleared
                 screen; screen B the conversation restored with the
                 prompt below "> after".

  --germline     Test 4. Item 7.

Pure standard library on purpose. Everything runs inside QEMU with exactly
two drives per guest, raw image files under stage5/out/, created here or
by the rehearsal; the broker (mock) on 127.0.0.1 only. No real disk is
touched; no Claude call is ever made.

This file is frozen acceptance machinery from plan item 8. See the header
of stage5/test.sh.

Exit 0 on pass, 1 otherwise.
"""

import hashlib
import json
import os
import re
import select
import shutil
import socket
import struct
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "stage5", "out")
ESP = os.path.join(OUT, "esp.img")
NOTES = os.path.join(OUT, "notes.img")
FONT = os.path.join(REPO, "stage2", "font8x8.bin")
BROKER = os.path.join(REPO, "broker", "germline.py")
COMPONENT_ASM = os.path.join(REPO, "stage5", "component.asm")
COMPONENT_BIN = os.path.join(REPO, "stage5", "component.bin")
GERMLINE = os.path.join(OUT, "germline")
REHEARSAL = os.path.join(OUT, "rehearsal")
OVMF = "/usr/share/ovmf/OVMF.fd"

sys.path.insert(0, os.path.join(REPO, "broker"))
from germline import (grow_request, component_frame, refusal_frame,  # noqa: E402
                      parse_response, germline_key, BLOB_MAX, MACHINE, ABI)

DISK_BYTES = 16 * 1024 * 1024
SECTOR = 512

# The cage, exactly as stage4/UMBILICAL.md spells it, with the harness's MAC.
BROKER_PORT = 9999
REHEARSAL_PORT = 9998
MAC = "52:54:00:a1:05:01"
CAGE_NETDEV = ("user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:%d-cmd:nc -N 127.0.0.1 %d"
               % (BROKER_PORT, BROKER_PORT))
CAGE_DEVICE = "virtio-net-pci,netdev=n0,mac=" + MAC

READY = b"S5: keyboard ready"
NO_ANSWER = "no answer from the broker"
CAP = 1048576

# UMBILICAL.md's canned answers to questions - what must be on the screen.
CANNED = {
    "ping": "pong",
    "hello": "hello from the mock broker\nask me something true at test 5",
}

# The test component's known picture (stage5/component.asm): row, column,
# text. The console line is filled in from the geometry of the run.
STRIPS = [
    (2, 4, "germline test component"),
    (4, 4, None),                       # "console <cols>x<rows>"
    (6, 4, "ticks ok"),
    (8, 4, "key: -"),
    (10, 4, "esc returns to the prompt"),
]

KEY_GAP = 0.2        # seconds between keys - a monitor can outrun a guest
SETTLE = 2.0         # seconds after an answer is known to have arrived

INDENT = "    "


def say(msg):
    print(INDENT + msg)


# ---------------------------------------------------------------- the wire --
# UMBILICAL.md's request rule and GERMLINE.md's grow rule, applied to the
# broker's recorded bytes.

REQUEST_MAX = 498


def judge_request_bytes(raw):
    """The recorded bytes of one connection, judged by the frame rule alone.
    Returns ("question", text) or ("grow", body); raises ValueError."""
    if len(raw) < 4:
        raise ValueError("only %d byte(s) arrived, not even a length" % len(raw))
    n, = struct.unpack("<I", raw[:4])
    if n > REQUEST_MAX:
        raise ValueError("frame of %d bytes exceeds %d" % (n, REQUEST_MAX))
    if len(raw) != 4 + n:
        raise ValueError("length says %d bytes but %d followed" % (n, len(raw) - 4))
    text = raw[4:]
    if raw == grow_request(text[1:]) and 2 <= len(text) and all(0x20 <= b <= 0x7E for b in text[1:]):
        return "grow", text[1:].decode("ascii")
    if 1 <= len(text) <= REQUEST_MAX and all(0x20 <= b <= 0x7E for b in text):
        return "question", text.decode("ascii")
    raise ValueError("request text is neither a question nor a grow request: %r" % text[:32])


def read_record(path):
    try:
        lines = [l for l in open(path).read().splitlines() if l.strip()]
    except OSError as exc:
        return None, ["no broker record: %s" % exc]
    entries = []
    problems = []
    for i, line in enumerate(lines):
        try:
            entries.append(json.loads(line))
        except ValueError as exc:
            problems.append("record line %d is unreadable: %s" % (i + 1, exc))
    return entries, problems


def check_question_entry(i, entry, want):
    problems = []
    try:
        kind, got = judge_request_bytes(bytes.fromhex(entry["request"]))
    except (ValueError, KeyError) as exc:
        return ["connection %d: bytes are not a valid request frame: %s" % (i, exc)]
    if (kind, got) != ("question", want):
        problems.append("connection %d: the guest sent %s %r, want the question %r" % (i, kind, got, want))
    if entry.get("error") is not None:
        problems.append("connection %d: the broker reports an error: %s" % (i, entry["error"]))
    if entry.get("answer") != CANNED.get(want, "mock: no canned answer for: " + want):
        problems.append("connection %d: the mock answered %r" % (i, entry.get("answer")))
    return problems


def check_grow_entry(i, entry, want, source, calls, rehearsals, answer_kind, answer_frame=None, answer=None):
    """One grow connection judged: the raw bytes by GERMLINE.md, then every
    record field the test states."""
    problems = []
    try:
        kind, got = judge_request_bytes(bytes.fromhex(entry["request"]))
    except (ValueError, KeyError) as exc:
        return ["connection %d: bytes are not a valid request frame: %s" % (i, exc)]
    if (kind, got) != ("grow", want):
        problems.append("connection %d: the guest sent %s %r, want the grow request %r" % (i, kind, got, want))
    if bytes.fromhex(entry["request"]) != grow_request(want.encode()):
        problems.append("connection %d: raw bytes %s are not GERMLINE.md's frame for %r" % (i, entry["request"], want))
    if entry.get("kind") != "grow":
        problems.append("connection %d: kind is %r, want 'grow'" % (i, entry.get("kind")))
    if entry.get("error") is not None:
        problems.append("connection %d: the broker reports an error: %s" % (i, entry["error"]))
    if entry.get("text") != want:
        problems.append("connection %d: text is %r, want %r" % (i, entry.get("text"), want))
    if entry.get("key") != germline_key(want):
        problems.append("connection %d: key is %r, want %r" % (i, entry.get("key"), germline_key(want)))
    if entry.get("source") != source:
        problems.append("connection %d: source is %r, want %r" % (i, entry.get("source"), source))
    if entry.get("generation_calls") != calls:
        problems.append("connection %d: generation_calls is %r, want %d" % (i, entry.get("generation_calls"), calls))
    if entry.get("rehearsals") != rehearsals:
        problems.append("connection %d: rehearsals is %r, want %r" % (i, entry.get("rehearsals"), rehearsals))
    if entry.get("answer_kind") != answer_kind:
        problems.append("connection %d: answer_kind is %r, want %r" % (i, entry.get("answer_kind"), answer_kind))
    if answer_frame is not None:
        want_sha = hashlib.sha256(answer_frame).hexdigest()
        if entry.get("answer_sha256") != want_sha:
            problems.append("connection %d: answer_sha256 is %r, but the frame GERMLINE.md gives for it hashes to %s (%d bytes)"
                            % (i, entry.get("answer_sha256"), want_sha, len(answer_frame)))
    if answer is not None and entry.get("answer") != answer:
        problems.append("connection %d: answer is %r, want %r" % (i, entry.get("answer"), answer))
    return problems


# ------------------------------------------------------------ the germline --

def check_germline_entry(root, want, blob, model="mock"):
    """The directory for `want` holds the blob and a provenance record that
    tells the truth about it (GERMLINE.md, "The germline")."""
    problems = []
    key = germline_key(want)
    d = os.path.join(root, key)
    if not os.path.isdir(d):
        return ["no germline entry %s for %r" % (key, want)]
    try:
        got = open(os.path.join(d, "component.bin"), "rb").read()
    except OSError as exc:
        return ["entry %s: %s" % (key, exc)]
    if got != blob:
        problems.append("entry %s: component.bin is %d bytes, not the %d-byte blob the mock serves" % (key, len(got), len(blob)))
    try:
        prov = json.load(open(os.path.join(d, "provenance.json")))
    except (OSError, ValueError) as exc:
        return problems + ["entry %s: provenance.json: %s" % (key, exc)]
    want_fields = {"request": want, "normalised": want, "key": key, "abi": ABI, "machine": MACHINE,
                   "model": model, "sha256": hashlib.sha256(blob).hexdigest(), "size": len(blob)}
    for k, v in want_fields.items():
        if prov.get(k) != v:
            problems.append("entry %s: provenance %s is %r, want %r" % (key, k, prov.get(k), v))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(prov.get("date", ""))):
        problems.append("entry %s: provenance date %r is not ISO-8601 UTC" % (key, prov.get("date")))
    if not isinstance(prov.get("tries"), int) or prov["tries"] < 1:
        problems.append("entry %s: provenance tries is %r" % (key, prov.get("tries")))
    reh = prov.get("rehearsal") or {}
    if reh.get("passed") is not True or reh.get("phrases") != [] or not isinstance(reh.get("seconds"), (int, float)):
        problems.append("entry %s: provenance rehearsal is %r, want passed with no phrases and a time" % (key, reh))
    try:
        rlog = open(os.path.join(d, "rehearsal.log")).read()
    except OSError as exc:
        return problems + ["entry %s: rehearsal.log: %s" % (key, exc)]
    if len(re.findall(r"^S5: ", rlog, re.M)) != 13:
        problems.append("entry %s: rehearsal.log does not hold the twin's thirteen S5: lines" % key)
    if "ERR:" in rlog:
        problems.append("entry %s: rehearsal.log carries an ERR: line" % key)
    return problems


def germline_entries(root):
    try:
        return sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    except OSError:
        return []


def component_self_check():
    """The frozen source reproduces the frozen binary, byte for byte -
    assembled to stage5/out/, never over the committed file."""
    check = os.path.join(OUT, "component.check.bin")
    try:
        r = subprocess.run(["nasm", "-f", "bin", COMPONENT_ASM, "-o", check], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, ["could not assemble the test component: %s" % exc]
    if r.returncode != 0:
        return None, ["the test component does not assemble: %s" % r.stderr.strip()[:200]]
    blob = open(COMPONENT_BIN, "rb").read()
    if open(check, "rb").read() != blob:
        return None, ["stage5/component.asm does not reproduce stage5/component.bin byte for byte"]
    if not 1 <= len(blob) <= BLOB_MAX:
        return None, ["the test component is %d bytes" % len(blob)]
    return blob, []


# ------------------------------------------------------------ the notebook --

def parse_notebook(data):
    if data[0:8] != b"NOTEBOOK":
        raise ValueError("sector 0 bytes 0-7 are %r, not the NOTEBOOK magic" % data[0:8])
    version, sector, first, length = struct.unpack_from("<IIQQ", data, 8)
    if version != 1 or sector != SECTOR or first != 1:
        raise ValueError("bad header (version %d, sector %d, first %d)" % (version, sector, first))
    if length != len(data) // SECTOR - 1:
        raise ValueError("header journal length is %d, want %d" % (length, len(data) // SECTOR - 1))
    if any(data[0x20:SECTOR]):
        raise ValueError("header padding is not all zero")
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


def check_image(path, want):
    try:
        data = open(path, "rb").read()
    except OSError as exc:
        return ["cannot read the notebook image: %s" % exc]
    if len(data) != DISK_BYTES:
        return ["the image is %d bytes, but the harness made it %d" % (len(data), DISK_BYTES)]
    try:
        notes = parse_notebook(data)
    except ValueError as exc:
        return ["the image is not a notebook: %s" % exc]
    problems = []
    if notes != want:
        problems.append("the notebook holds %r, want %r" % (notes, want))
    nxt = (len(want) + 1) * SECTOR
    if data[nxt:nxt + 4] == b"NOTE":
        problems.append("sector %d begins a record - something beyond %r was journaled" % (len(want) + 1, want))
    return problems


# ---------------------------------------------------------------- the mock --

def port_state(port):
    s = socket.socket()
    s.settimeout(1.0)
    try:
        return "open" if s.connect_ex(("127.0.0.1", port)) == 0 else "closed"
    finally:
        s.close()


def start_mock(record_path):
    """Start germline.py --mock with a wiped germline, the gate's image as
    the twin, its record file; wait for its listening line."""
    for port in (BROKER_PORT, REHEARSAL_PORT):
        if port_state(port) == "open":
            return None, ("something is already listening on 127.0.0.1:%d - the gate talks only "
                          "to its own mock and its own rehearsal; stop it first" % port)
    for path in (GERMLINE, REHEARSAL):
        if os.path.isdir(path):
            shutil.rmtree(path)
    if os.path.exists(record_path):
        os.remove(record_path)
    log = open(os.path.join(OUT, "mock.stderr.txt"), "ab")
    proc = subprocess.Popen(
        [sys.executable, BROKER, "--mock", "--port", str(BROKER_PORT), "--record", record_path,
         "--germline", GERMLINE, "--image", ESP, "--workdir", REHEARSAL,
         "--rehearsal-port", str(REHEARSAL_PORT)],
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


def stop_mock(proc):
    if proc is None:
        return
    if proc.poll() is None:
        proc.send_signal(2)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def record_count(path):
    try:
        return len([l for l in open(path).read().splitlines() if l.strip()])
    except OSError:
        return 0


# ---------------------------------------------------------------- driver ----

def fresh_disk(path):
    if os.path.exists(path):
        os.remove(path)
    with open(path, "wb") as fh:
        fh.truncate(DISK_BYTES)


def qemu_argv(smp, disk, serial_path):
    """The one place the QEMU command is spelled. Test 4 inspects this."""
    return [
        "qemu-system-x86_64",
        "-machine", "q35",
        "-m", "256M",
        "-smp", str(smp),
        "-bios", OVMF,
        "-drive", "format=raw,file=" + ESP,
        "-drive", "format=raw,file=" + disk + ",if=virtio",
        "-netdev", CAGE_NETDEV,
        "-device", CAGE_DEVICE,
        "-display", "none",
        "-serial", "file:" + serial_path,
        "-monitor", "stdio",
    ]


# The keys, as the QEMU monitor names them. Only what the tests type.
KEYNAMES = {" ": "spc", "?": "shift-slash", "!": "shift-1", "\n": "ret", "\x1b": "esc"}


def keyname(ch):
    if ch in KEYNAMES:
        return KEYNAMES[ch]
    if ch.islower() and ch.isalpha():
        return ch
    raise ValueError("no monitor key name for %r" % ch)


def drive(smp, disk, steps, serial_path):
    """Boot inside the cage, wait for the guest's own ready line, run the
    steps - ("type", text), ("sleep", seconds), ("wait_record", path, count,
    timeout), ("shot", path) - quit, reap. Returns (serial_bytes, error).
    Never leaves a QEMU running behind us."""
    if not os.path.isfile(ESP):
        return b"", "no image was built"
    if not os.path.isfile(OVMF):
        return b"", "OVMF firmware not found at " + OVMF
    if os.path.exists(serial_path):
        os.remove(serial_path)
    for step in steps:
        if step[0] == "shot" and os.path.exists(step[1]):
            os.remove(step[1])

    proc = subprocess.Popen(qemu_argv(smp, disk, serial_path),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
            err = "the guest never printed 'S5: keyboard ready' within 60s"
            if proc.poll() is not None:
                err += " (qemu exited %d: %s)" % (proc.returncode,
                                                 proc.stderr.read().decode(errors="replace").strip()[:300])
        else:
            time.sleep(1.0)  # let the guest finish its replay, prompt and sti
            for step in steps:
                if step[0] == "type":
                    for ch in step[1]:
                        tell(b"sendkey " + keyname(ch).encode() + b"\n")
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
                    tell(b"screendump " + step[1].encode() + b"\n")
                    shot_deadline = time.time() + 15.0
                    last = -1
                    while time.time() < shot_deadline:
                        time.sleep(0.2)
                        if os.path.exists(step[1]):
                            size = os.path.getsize(step[1])
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
    (r"S5: alive", "S5: alive"),
    (r"S5: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})", "S5: gop <W>x<H> fb 0x<16 hex>"),
    (r"S5: boot services exited", "S5: boot services exited"),
    (r"S5: gdt and paging ours", "S5: gdt and paging ours"),
    (r"S5: idt ready", "S5: idt ready"),
    (r"S5: cores found (\d+)", "S5: cores found <N>"),
    (r"S5: cores woken (\d+)", "S5: cores woken <N>"),
    (r"S5: console (\d+)x(\d+)", "S5: console <COLS>x<ROWS>"),
    (r"S5: disk (\d+) sectors", "S5: disk <N> sectors"),
    (r"S5: notebook (formatted|\d+ notes)", "S5: notebook formatted | S5: notebook <N> notes"),
    (r"S5: nic ([0-9a-f]{2}(?::[0-9a-f]{2}){5})", "S5: nic <mac>"),
    (r"S5: component region 0x([0-9a-f]{16}) (\d+) bytes", "S5: component region 0x<16 hex> 1048576 bytes"),
    (r"S5: keyboard ready", "S5: keyboard ready"),
]


def check_boot_lines(capture, smp, notebook_want):
    """The thirteen lines, in order, self-consistent, with line ten as
    demanded, line eleven carrying the harness's MAC and line twelve the
    component region by GERMLINE.md's rule. Returns (problems, geometry)."""
    problems = []
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S5: [^\n]*", text)
    if len(got) != 13:
        problems.append("expected exactly 13 S5: lines, found %d" % len(got))
        if len(got) > 13:
            problems.append("more than thirteen usually means a reboot loop - and with the IDT "
                            "up it should have been an ERR: exception line instead")
    errs = re.findall(r"ERR: [^\n]*", text)
    if errs:
        problems.append("the guest reported: %s" % "; ".join(errs[:3]))

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
            if int(m.group(1)) != DISK_BYTES // SECTOR:
                problems.append("line 9: the guest counted %s sectors, but the image is %d sectors"
                                % (m.group(1), DISK_BYTES // SECTOR))
        elif i == 9:
            if m.group(1) != notebook_want:
                problems.append("line 10: got 'S5: notebook %s', want 'S5: notebook %s'"
                                % (m.group(1), notebook_want))
        elif i == 10:
            if m.group(1) != MAC:
                problems.append("line 11: the guest read MAC %s, but the harness gave the device %s"
                                % (m.group(1), MAC))
        elif i == 11:
            addr = int(m.group(1), 16)
            if addr == 0 or addr >= 1 << 32:
                problems.append("line 12: the component region 0x%s is zero or above 4 GB" % m.group(1))
            if addr % 4096 != 64:
                problems.append("line 12: the component region 0x%s is not 64 mod 4096" % m.group(1))
            if int(m.group(2)) != CAP:
                problems.append("line 12: the cap is %s bytes, want %d" % (m.group(2), CAP))

    if found is not None and found != smp:
        problems.append("cores found is %d, but the machine was given -smp %d" % (found, smp))
    if woken is not None and woken != smp:
        problems.append("cores woken is %d, but the machine was given -smp %d" % (woken, smp))
    if None not in (w, h, cols, rows):
        if cols != w // 16 or rows != h // 16:
            problems.append("console claims %dx%d cells, but %dx%d pixels / 16 = %dx%d"
                            % (cols, rows, w, h, w // 16, h // 16))
    return problems, (w, h, cols, rows)


def check_echo(capture, want):
    """The bytes after the ready line's CRLF must be exactly `want`: the raw
    echo of what was typed at the prompt, and nothing else - no indicator,
    no answer, no refusal, and nothing a component's keys did."""
    marker = READY + b"\r\n"
    idx = capture.find(marker)
    if idx < 0:
        return ["no '%s' CRLF in the capture" % READY.decode()]
    tail = capture[idx + len(marker):]
    if tail == want:
        return []
    return ["after 'S5: keyboard ready' the serial channel carries %r, want %r" % (tail, want)]


def dump_capture(capture):
    say("whole capture follows (OVMF chatter included, control bytes visible):")
    text = capture.decode("utf-8", "replace")
    shown = "".join(ch if ch == "\n" or 32 <= ord(ch) < 127 else "^" + format(ord(ch), "02x")
                    for ch in text.replace("\r\n", "\n"))
    for line in shown.splitlines()[-40:]:
        say("  " + line)


# ------------------------------------------------------------ the picture ---
# Stage 2's console, unchanged: two colours, 16x16 cells from the shared
# font, each font bit a 2x2 block, the cursor a solid block.

BG = (16, 16, 24)
FG = (224, 224, 224)
TOL = 4
CELL = 16
PROMPT = object()    # the row that is "> " and the block cursor


def read_ppm(path):
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
    idx += 1
    width, height, maxval = fields
    if maxval != 255:
        raise ValueError("expected 8-bit PPM (maxval 255), got %d" % maxval)
    pixels = data[idx:]
    need = width * height * 3
    if len(pixels) < need:
        raise ValueError("truncated PPM: %d bytes of pixel data, expected %d" % (len(pixels), need))
    return width, height, pixels[:need]


def load_font():
    data = open(FONT, "rb").read()
    if len(data) != 1024:
        raise ValueError("font8x8.bin is %d bytes, expected 1024" % len(data))
    return data


def glyph_rows(font, ch):
    return font[ord(ch) * 8:(ord(ch) + 1) * 8]


def render_cell(font, ch):
    rows = []
    for byte in glyph_rows(font, ch):
        row = b"".join(bytes(FG if byte >> x & 1 else BG) * 2 for x in range(8))
        rows.append(row)
        rows.append(row)
    return rows


def cursor_cell():
    return [bytes(FG) * CELL] * CELL


def blank_cell():
    return [bytes(BG) * CELL] * CELL


def font_self_check(font, text):
    problems = []
    used = sorted(set(text.replace(" ", "").replace("\n", "")))
    shapes = {}
    for ch in used:
        rows = glyph_rows(font, ch)
        if not any(rows):
            problems.append("glyph %r in the font is blank - the test would prove nothing" % ch)
        shapes.setdefault(bytes(rows), []).append(ch)
    for chars in shapes.values():
        if len(chars) > 1:
            problems.append("glyphs %s are identical in the font" % ", ".join(map(repr, chars)))
    if any(glyph_rows(font, " ")):
        problems.append("the space glyph is not blank")
    return problems


def cell_matches(pixels, width, row, col, want_rows):
    x0 = col * CELL * 3
    for dy in range(CELL):
        base = ((row * CELL + dy) * width) * 3 + x0
        got = pixels[base:base + CELL * 3]
        want = want_rows[dy]
        if got == want:
            continue
        for i in range(CELL * 3):
            if abs(got[i] - want[i]) > TOL:
                return False
    return True


def cell_census(pixels, width, row, col):
    counts = {}
    for dy in range(CELL):
        base = ((row * CELL + dy) * width) * 3 + col * CELL * 3
        for dx in range(CELL):
            off = base + dx * 3
            rgb = (pixels[off], pixels[off + 1], pixels[off + 2])
            counts[rgb] = counts.get(rgb, 0) + 1
    return ", ".join("rgb%s x%d" % kv for kv in sorted(counts.items(), key=lambda kv: -kv[1])[:3])


def check_colour_discipline(pixels, width, height):
    bg_row = bytes(BG) * width
    for y in range(height):
        base = y * width * 3
        row = pixels[base:base + width * 3]
        if row == bg_row:
            continue
        for x in range(width):
            off = x * 3
            p = (row[off], row[off + 1], row[off + 2])
            if all(abs(p[i] - BG[i]) <= TOL for i in range(3)):
                continue
            if all(abs(p[i] - FG[i]) <= TOL for i in range(3)):
                continue
            return ("pixel (%d, %d) is rgb%s - neither the background rgb%s nor the foreground rgb%s"
                    % (x, y, p, BG, FG))
    return None


def strip_matches(pixels, width, font, row, text, col=0):
    return all(cell_matches(pixels, width, row, col + c, render_cell(font, ch))
               for c, ch in enumerate(text))


def open_shot(shot, geometry):
    """The screendump read and checked against the geometry the guest
    claimed. Returns (width, height, pixels, cols, rows, font) or raises."""
    w, h, cols, rows = geometry
    if not os.path.isfile(shot) or os.path.getsize(shot) == 0:
        raise ValueError("qemu produced no screendump")
    width, height, pixels = read_ppm(shot)
    say("serial claims %dx%d (%dx%d cells); screendump is %dx%d" % (w, h, cols, rows, width, height))
    if (width, height) != (w, h):
        raise ValueError("screendump is %dx%d but the guest said the mode was %dx%d" % (width, height, w, h))
    return width, height, pixels, cols, rows, load_font()


def check_screen(shot, geometry, expected):
    """`expected` is a list of rows: strings drawn from column 0, or PROMPT.
    They must appear on consecutive rows, the first found exactly once on
    screen, every text row followed by a blank cell, and nothing but the two
    console colours anywhere."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    texts = [t for t in expected if t is not PROMPT]
    problems = font_self_check(font, "".join(texts) + "> ")
    if problems:
        return problems
    for t in texts:
        if len(t) >= cols:
            return ["expected row %r is %d cells wide but the console has only %d columns" % (t, len(t), cols)]

    first = expected[0]
    hits = [r for r in range(rows) if strip_matches(pixels, width, font, r, first)]
    if len(hits) != 1:
        problems.append("the row %r appears %d times on screen, want exactly once" % (first, len(hits)))
        say("per-row first-cell census, rows that are not pure background:")
        shown = 0
        for r in range(rows):
            if cell_matches(pixels, width, r, 0, blank_cell()):
                continue
            say("  row %3d col 0: %s" % (r, cell_census(pixels, width, r, 0)))
            shown += 1
            if shown >= 24:
                say("  ...")
                break
        return problems

    base = hits[0]
    for i, want in enumerate(expected):
        r = base + i
        if r >= rows:
            problems.append("row %d is off the bottom of the screen - no room for %r" % (r, want))
            break
        if want is PROMPT:
            for col, ch in ((0, ">"), (1, " ")):
                if not cell_matches(pixels, width, r, col, render_cell(font, ch)):
                    problems.append("row %d, column %d is not %r - %s" % (r, col, ch, cell_census(pixels, width, r, col)))
            if not cell_matches(pixels, width, r, 2, cursor_cell()):
                problems.append("row %d, column 2 is not the block cursor - %s" % (r, cell_census(pixels, width, r, 2)))
            continue
        if not strip_matches(pixels, width, font, r, want):
            bad = next((c for c, ch in enumerate(want)
                        if not cell_matches(pixels, width, r, c, render_cell(font, ch))), None)
            problems.append("row %d is not %r - column %s is %s"
                            % (r, want, bad, cell_census(pixels, width, r, bad) if bad is not None else "?"))
            continue
        if not cell_matches(pixels, width, r, len(want), blank_cell()):
            problems.append("row %d: the cell after %r is not blank - %s (an indicator left behind?)"
                            % (r, want, cell_census(pixels, width, r, len(want))))
        if i > 0:
            others = [x for x in range(rows) if x != r and strip_matches(pixels, width, font, x, want)]
            if others:
                problems.append("row %r also appears at row(s) %s" % (want, others))

    stray = check_colour_discipline(pixels, width, height)
    if stray:
        problems.append(stray)
    return problems


def component_strips(cols, rows, key):
    """The test component's five strips as (row, col, text), with the
    console line filled in and the key it should be showing."""
    out = []
    for r, c, text in STRIPS:
        if text is None:
            text = "console %dx%d" % (cols, rows)
        elif text == "key: -":
            text = "key: " + key
        out.append((r, c, text))
    return out


def check_component_screen(shot, geometry, key):
    """The screen while the test component runs: its five strips at their
    exact cells, and every other cell blank - the loader cleared the
    console, and nothing else was drawn. Two colours only."""
    try:
        width, height, pixels, cols, rows, font = open_shot(shot, geometry)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    strips = component_strips(cols, rows, key)
    problems = font_self_check(font, "".join(t for _, _, t in strips))
    if problems:
        return problems
    covered = set()
    for r, c, text in strips:
        if not strip_matches(pixels, width, font, r, text, c):
            bad = next((i for i, ch in enumerate(text)
                        if not cell_matches(pixels, width, r, c + i, render_cell(font, ch))), None)
            problems.append("row %d, column %d is not %r - column %s is %s"
                            % (r, c, text, c + bad if bad is not None else "?",
                               cell_census(pixels, width, r, c + bad) if bad is not None else "?"))
        for i in range(len(text)):
            covered.add((r, c + i))
    strays = []
    for r in range(rows):
        for c in range(cols):
            if (r, c) in covered:
                continue
            if not cell_matches(pixels, width, r, c, blank_cell()):
                strays.append((r, c))
    if strays:
        problems.append("%d cell(s) outside the component's strips are not blank, the first at row %d column %d: %s"
                        % (len(strays), strays[0][0], strays[0][1], cell_census(pixels, width, *strays[0])))
    stray = check_colour_discipline(pixels, width, height)
    if stray:
        problems.append(stray)
    return problems


# ----------------------------------------------------------------- modes ----

def report(title, problems, capture=None):
    if problems:
        say(title + ":")
        for p in problems:
            say("  - " + p)
        if capture is not None:
            dump_capture(capture)
        return False
    return True


def run_grow(smp):
    """Test 3 at one -smp value."""
    blob, problems = component_self_check()
    if not report("the test component is not what the repository says", problems):
        return 1
    say("stage5/component.asm reproduces stage5/component.bin: %d bytes, sha256 %s"
        % (len(blob), hashlib.sha256(blob).hexdigest()[:16]))

    record = os.path.join(OUT, "broker.grow.%d.jsonl" % smp)
    serial = os.path.join(OUT, "serial.grow.%d.txt" % smp)
    shot_a = os.path.join(OUT, "screen.grow.%d.a.ppm" % smp)
    shot_b = os.path.join(OUT, "screen.grow.%d.b.ppm" % smp)
    mock, err = start_mock(record)
    if err:
        say(err)
        return 1
    say("mock broker listening on 127.0.0.1:%d, germline at %s, recording to %s"
        % (BROKER_PORT, os.path.relpath(GERMLINE, REPO), os.path.relpath(record, REPO)))
    try:
        fresh_disk(NOTES)
        steps = [
            ("type", "before\n"), ("sleep", 1.5),
            ("type", "? ping\n"), ("wait_record", record, 1, 20.0), ("sleep", SETTLE),
            ("type", "! test component\n"), ("wait_record", record, 2, 150.0), ("sleep", 3.0),
            ("type", "k"), ("sleep", 1.0),
            ("shot", shot_a),
            ("type", "\x1b"), ("sleep", 2.0),
            ("type", "after\n"), ("sleep", SETTLE),
            ("shot", shot_b),
        ]
        capture, err = drive(smp, NOTES, steps, serial)
    finally:
        stop_mock(mock)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1

    ok = True
    problems, geometry = check_boot_lines(capture, smp, "formatted")
    problems += check_echo(capture, b"before\r\n? ping\r\n! test component\r\nafter\r\n")
    ok &= report("the serial log is not what the spec asks for", problems, capture)
    if not problems:
        say("thirteen boot lines, nic %s; the wire after ready carries exactly the four typed lines" % MAC)

    entries, problems = read_record(record)
    if entries is not None:
        if len(entries) != 2:
            problems.append("the broker saw %d connection(s), want 2" % len(entries))
        if len(entries) >= 1:
            problems += check_question_entry(1, entries[0], "ping")
        if len(entries) >= 2:
            problems += check_grow_entry(2, entries[1], "test component", "generated", 1, ["pass"],
                                         "component", component_frame(blob))
    ok &= report("the broker's record is not what GERMLINE.md asks for", problems)
    if not problems:
        say("the broker received 'ping' and the grow request byte-exact, generated once, rehearsed once, "
            "and sent the component frame GERMLINE.md gives for stage5/component.bin")

    problems = check_germline_entry(GERMLINE, "test component", blob)
    names = germline_entries(GERMLINE)
    if len(names) != 1:
        problems.append("the germline holds %d entries %r, want exactly 1" % (len(names), names))
    ok &= report("the germline is not what GERMLINE.md asks for", problems)
    if not problems:
        say("the germline holds exactly one entry, the test component with its provenance and rehearsal log")

    problems = check_image(NOTES, ["before", "after"])
    ok &= report("the notebook is not what it should be", problems)
    if not problems:
        say("the notebook holds exactly 'before' and 'after' - neither the question nor the request was journaled")

    if None in geometry:
        say("no picture to judge - the boot lines were wrong")
        return 1
    problems = check_component_screen(shot_a, geometry, "k")
    ok &= report("screen A does not show the test component", problems)
    if not problems:
        say("screen A: the five strips at their cells with 'key: k', every other cell blank, two colours only")

    problems = check_screen(shot_b, geometry, ["> before", "> ? ping", CANNED["ping"], "> ! test component", "> after", PROMPT])
    ok &= report("screen B does not show the conversation restored", problems)
    if not problems:
        say("screen B: the conversation back, '> after' and the prompt below the request, two colours only")

    say("-smp %d: %s" % (smp, "the machine grew, ran, and came back" if ok else "the growth failed"))
    return 0 if ok else 1


def main(argv):
    if len(argv) == 2 and argv[0] == "--grow":
        try:
            return run_grow(int(argv[1]))
        except ValueError:
            pass
    say("usage: checkgermline.py --grow <smp> | --germline")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
