#!/usr/bin/env python3
"""Stage 7 ring 7b acceptance checks - the wire, through the monitor and
from the host.

Implements the link-down boot of acceptance test 2 and the whole of tests
3 and 4 from stage7/spec.md (ring 7b), as stage7/plan-7b.md and its
amendments fix them:

  --down SMP
        test 2's fourth boot: the e1000e's link taken down through the
        monitor before the guest runs (the machine started paused,
        "set_link e1000e.0 off", "cont"); the S7: lines to "S7: nic", then
        exactly "ERR: nic link did not come up within 10 s" inside this
        checker's own clock, no "S7: link up", no keyboard, and the guest
        halted - no line printed twice (a rebooting guest prints "S7:
        alive" again).
  --question SMP
        test 3: Stage 4's round trip on the e1000e through the relay -
        "? ping", a note, "? hello" - the record, the relay's log agreeing
        with it, the notebook on the notes partition, the screen, and the
        strip's wire counters against the obs page and the log.
  --cage
        test 4: the argv assertions on this checker's command and the
        twin's as broker/wire.py builds it; the relay's bind rule on the
        host; the mock-down run ending in a message; "! test app" and
        "! install echo" through the relay at -smp 4; the reboot with
        nothing on the wire.

Everything runs inside QEMU with the caged network on the e1000e, the
1920x1080 display, the patient's CPU model and the SATA disk; the only
disks are raw files under stage7/out/. The relay is broker/relay.py on
127.0.0.1:9997 (unfrozen: held to stage7/WIRE.md here); the mock broker is
broker/wire.py --mock on 9999, which calls nothing. Every prefix-free
helper comes from the frozen Stage 6 and ring 7a checkers; what is
spelled here is what those cannot say: the nineteen lines, the e1000e
cage, the relay's log.

This file is frozen acceptance machinery from ring 7b plan item 8.
"""

import hashlib
import json
import os
import re
import select
import shutil
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "stage7", "out")
WIRE_OUT = os.path.join(OUT, "wire")
ESP = os.path.join(OUT, "esp.img")
EFI = os.path.join(OUT, "BOOTX64.EFI")
DISK = os.path.join(WIRE_OUT, "disk.img")
BROKER = os.path.join(REPO, "broker", "wire.py")
RELAY = os.path.join(REPO, "broker", "relay.py")
PLANS_DIR = os.path.join(REPO, "plans")
GERMLINE = os.path.join(WIRE_OUT, "germline")
REHEARSAL = os.path.join(WIRE_OUT, "rehearsal")
TWIN_WORKDIR = os.path.join(REHEARSAL, "twin")
OVMF = "/usr/share/ovmf/OVMF.fd"

for sub in ("broker", "stage3", "stage6", "stage7"):
    sys.path.insert(0, os.path.join(REPO, sub))
import checkdisk  # noqa: E402  - ring 7a's frozen checker: the machine's disk side
from checkdisk import (check_notes_partition, check_partitions, check_table, read_image, check_echo,  # noqa: E402
                       fresh_disk, DISK_SECTORS, PATTERNS_AGAIN as PATTERNS_AGAIN_7A, DISK_LINE)
from checkglass import (say, report, dump_capture, check_region_rows, record_count, PROMPT,  # noqa: E402
                        read_record, port_state, stop_mock, check_choices, check_mode_field, check_app_panel,
                        check_app_panel_blank, check_strip, check_counts, germline_entries, fixture_self_check,
                        check_question_entry, check_grow_entry, SETTLE, NO_ANSWER, CANNED)
from checkplans import (check_install_entry, check_one_cell_panel, DATA_FIRST, CHOICES_ECHO_RUNNING,  # noqa: E402
                        ECHO_TESTS_OK)
from glass import (regions, app_frame, grow_request, germline_key, TEST_CHOICES, ABI, MACHINE)  # noqa: E402
from broker import (frame, mock_answer)  # noqa: E402
import twin  # noqa: E402
from twin import Driver  # noqa: E402
from plans import (plan_keyname, parse_plan, install_key)  # noqa: E402
from rehearse import KEY_GAP  # noqa: E402
import metal  # noqa: E402
import wire  # noqa: E402

# The Stage 7 machine with the NIC the metal has, spelled once for the
# checker (test-7b.sh spells its own and test 4 inspects both).
CPU = ["-cpu", "IvyBridge"]
DISPLAY = ["-vga", "none", "-device", "VGA,edid=on,xres=1920,yres=1080"]
BROKER_PORT = 9999
REHEARSAL_PORT = 9998
RELAY_PORT = 9997
MAC = "6c:3b:e5:3b:86:45"
NIC_NAME = "e1000e.0"                # the monitor's name for an e1000e given no id
CAGE_NETDEV = ("user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:%d-cmd:nc -N 127.0.0.1 %d"
               % (BROKER_PORT, RELAY_PORT))
CAGE_DEVICE = "e1000e,netdev=n0,mac=" + MAC
READY = b"S7: keyboard ready"
LINK_ERR = "ERR: nic link did not come up within 10 s"
LINK_LIMIT = 45.0                    # this checker's clock on the bounded wait, seconds from the start

# ------------------------------------------------------- the serial lines --
# WIRE.md, "The serial lines": ring 7a's lists with "S7: link up" after the
# nic line. The expected count is the length of the list - never a literal.

NIC_LINE = PATTERNS_AGAIN_7A[12]
assert NIC_LINE[1] == "S7: nic <mac>"
LINK_LINE = (r"S7: link up", "S7: link up")
PATTERNS_AGAIN = PATTERNS_AGAIN_7A[:13] + [LINK_LINE] + PATTERNS_AGAIN_7A[13:]
PATTERNS_BLANK = PATTERNS_AGAIN[:9] + [(r"S7: gpt written", "S7: gpt written")] + PATTERNS_AGAIN[9:]
BLOB_MAX = 1048576


def check_boot_lines(capture, smp, blank, notebook_want, home_want, sectors):
    """WIRE.md's lines, in order, self-consistent: nineteen on a formatting
    boot (blank True), eighteen on a recognising one; the nic line the
    e1000e's MAC; "S7: link up" right after it. Returns (problems,
    geometry) with geometry = (w, h, cols, rows)."""
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
    if found is not None and found != smp:
        problems.append("cores found is %d, but the machine was given -smp %d" % (found, smp))
    if woken is not None and woken != smp:
        problems.append("cores woken is %d, but the machine was given -smp %d" % (woken, smp))
    if None not in (w, h, cols, rows) and (cols != w // 16 or rows != h // 16):
        problems.append("console claims %dx%d cells, but %dx%d pixels / 16 = %dx%d" % (cols, rows, w, h, w // 16, h // 16))
    return problems, (w, h, cols, rows)


# ------------------------------------------------------------- the driver ---
# The checker's own QEMU command and monitor driver: ring 7a's machine and
# disk with the e1000e cage; started paused when the link is to be taken
# down first. The step vocabulary is ring 6b's.

def qemu_argv(smp, disk, serial_path, paused=False):
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
    ] + (["-S"] if paused else []) + [
        "-display", "none",
        "-serial", "file:" + serial_path,
        "-monitor", "stdio",
    ]


def drive(smp, disk, steps, serial_path, ready=READY, ready_limit=60.0, link_down=False):
    """Boot inside the cage on the e1000e, wait for the guest's own ready
    line, run the steps, quit, reap. With link_down the machine starts
    paused, the NIC's link is set off through the monitor and the machine
    continued - so the guest never sees a link. Returns (serial_bytes,
    reads, error, seconds_to_ready). Never leaves a QEMU running."""
    reads = {}
    if not os.path.isfile(ESP):
        return b"", reads, "no image was built", None
    if not os.path.isfile(OVMF):
        return b"", reads, "OVMF firmware not found at " + OVMF, None
    if os.path.exists(serial_path):
        os.remove(serial_path)
    for step in steps:
        if step[0] == "shot" and os.path.exists(step[1]):
            os.remove(step[1])

    proc = subprocess.Popen(qemu_argv(smp, disk, serial_path, paused=link_down),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    drv = Driver(proc, serial_path, WIRE_OUT)
    t0 = time.time()
    if link_down:
        time.sleep(0.5)
        drv.tell(b"set_link " + NIC_NAME.encode() + b" off\n")
        drv.tell(b"cont\n")
        t0 = time.time()

    err = None
    t_ready = None
    obs_addr = None
    try:
        deadline = t0 + ready_limit
        got_ready = False
        while time.time() < deadline:
            time.sleep(0.25)
            if proc.poll() is not None:
                break
            if ready in drv.serial_bytes():
                got_ready = True
                t_ready = time.time() - t0
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
    return drv.serial_bytes(), reads, err, t_ready


# ------------------------------------------------------- the relay ---------
# WIRE.md, "The relay": started on 127.0.0.1:9997 with a log, forwarding
# to the broker's 9999; its listening line awaited; its log read back by
# the document's five fields.

def start_relay(log_path):
    if port_state(RELAY_PORT) == "open":
        return None, "something is already listening on 127.0.0.1:%d - the gate talks only to its own relay" % RELAY_PORT
    if os.path.exists(log_path):
        os.remove(log_path)
    errlog = open(os.path.join(WIRE_OUT, "relay.stderr.txt"), "ab")
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


def read_relay_log(path, want=None, limit=3.0):
    """The relay's entries, in order; with want, waits up to limit seconds
    for that many (the line is written as the connection ends, and the
    guest's close is the last event)."""
    deadline = time.time() + limit
    while True:
        try:
            entries = [json.loads(l) for l in open(path) if l.strip()]
        except OSError:
            entries = []
        if want is None or len(entries) >= want or time.time() > deadline:
            return entries


def check_relay_log(entries, wants, label):
    """Every connection the relay saw, in order: up and down the frame
    lengths the test computes from its own requests and the mock's
    answers, no error. wants is [(up, down), ...]."""
    problems = []
    if len(entries) != len(wants):
        problems.append("%s: the relay logged %d connection(s), want %d" % (label, len(entries), len(wants)))
    for i, (e, (up, down)) in enumerate(zip(entries, wants), 1):
        for k in ("t", "peer", "up", "down", "error"):
            if k not in e:
                problems.append("%s: connection %d: the log line lacks %r" % (label, i, k))
        if e.get("error") is not None:
            problems.append("%s: connection %d: the relay reports an error: %s" % (label, i, e["error"]))
        if e.get("up") != up or e.get("down") != down:
            problems.append("%s: connection %d: the relay copied %s bytes up and %s down, want %d and %d"
                            % (label, i, e.get("up"), e.get("down"), up, down))
    return problems


def question_bytes(question):
    """(up, down) for a canned question: the request frame and the
    response frame, both by the frozen framing."""
    q = question.encode()
    return len(frame(q)), len(frame(mock_answer(q)))


# --------------------------------------------------------------- the mock --

def start_mock(record_path, wipe_germline=True):
    """Start broker/wire.py --mock with the gate's germline (wiped unless
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
    log = open(os.path.join(WIRE_OUT, "mock.wire.stderr.txt"), "ab")
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


# --------------------------------------------------- test 2: the link down --

def run_down(smp):
    """The e1000e's link taken down before the guest runs: the lines to
    the nic line, then the named error inside this checker's clock, no
    link line, no keyboard, no reboot."""
    disk = os.path.join(WIRE_OUT, "disk.down.img")
    fresh_disk(disk)
    serial = os.path.join(WIRE_OUT, "serial.down.%d.txt" % smp)
    say("the link down: -smp %d, the machine started paused, 'set_link %s off', then 'cont'" % (smp, NIC_NAME))
    capture, reads, err, t_err = drive(smp, disk, [("sleep", 3.0)], serial, ready=LINK_ERR.encode(),
                                        ready_limit=LINK_LIMIT, link_down=True)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    problems = []
    text = capture.decode("utf-8", "replace").replace("\r", "")
    got = re.findall(r"S7: [^\n]*", text)
    errs = re.findall(r"ERR: [^\n]*", text)
    want = PATTERNS_BLANK[:PATTERNS_BLANK.index(NIC_LINE) + 1]
    if len(got) != len(want):
        problems.append("expected exactly %d S7: lines before the error, found %d" % (len(want), len(got)))
    for i, (pattern, shape) in enumerate(want):
        line = got[i] if i < len(got) else ""
        m = re.fullmatch(pattern, line)
        if not m:
            problems.append("line %d: got '%s', want '%s'" % (i + 1, line, shape))
        elif pattern == NIC_LINE[0] and m.group(1) != MAC:
            problems.append("line %d: the guest read MAC %s, but the e1000e carries %s" % (i + 1, m.group(1), MAC))
    if errs != [LINK_ERR]:
        problems.append("the error lines are %r, want exactly [%r]" % (errs, LINK_ERR))
    if any(l.startswith("S7: link up") for l in got):
        problems.append("the guest printed 'S7: link up' with the link down")
    if READY in capture:
        problems.append("the guest reached the keyboard with the link down")
    if text.count("S7: alive") != 1:
        problems.append("'S7: alive' appears %d times - the guest rebooted after the error instead of halting" % text.count("S7: alive"))
    if not report("the link-down boot is not what WIRE.md asks for", problems, capture):
        return 1
    say("the link down: %d lines to 'S7: nic %s', then %r at %.1f s from the start (the bound: %.0f s); no link line, "
        "no keyboard, one 'S7: alive' - the guest halted" % (len(want), MAC, LINK_ERR, t_err, LINK_LIMIT))
    return 0


# -------------------------------------------------- test 3: the question ----

def run_question(smp):
    record = os.path.join(WIRE_OUT, "broker.question.%d.jsonl" % smp)
    rlog = os.path.join(WIRE_OUT, "relay.question.%d.jsonl" % smp)
    serial = os.path.join(WIRE_OUT, "serial.question.%d.txt" % smp)
    shot = os.path.join(WIRE_OUT, "screen.question.%d.ppm" % smp)
    relay, err = start_relay(rlog)
    if err:
        say(err)
        return 1
    mock, err = start_mock(record)
    if err:
        say(err)
        stop_mock(relay)
        return 1
    say("relay on 127.0.0.1:%d -> 127.0.0.1:%d, logging to %s; mock broker on %d, recording to %s"
        % (RELAY_PORT, BROKER_PORT, os.path.relpath(rlog, REPO), BROKER_PORT, os.path.relpath(record, REPO)))
    try:
        fresh_disk(DISK)
        steps = [
            ("type", "? ping\n"), ("wait_record", record, 1, 20.0), ("sleep", SETTLE),
            ("type", "keep this\n"), ("sleep", 1.5),
            ("type", "? hello\n"), ("wait_record", record, 2, 20.0), ("sleep", SETTLE),
            ("obs", "r1"), ("shot", shot), ("obs", "r2"),
        ]
        capture, reads, err, _ = drive(smp, DISK, steps, serial)
    finally:
        stop_mock(mock)
        entries_relay = read_relay_log(rlog, want=2)
        stop_mock(relay)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1

    ok = True
    problems, geometry = check_boot_lines(capture, smp, True, "formatted", 0, DISK_SECTORS)
    problems += check_echo(capture, b"? ping\r\nkeep this\r\n? hello\r\n")
    ok &= report("the serial log is not what WIRE.md asks for", problems, capture)
    if not problems:
        say("%d boot lines, nic %s, link up; the wire after ready carries exactly the three typed lines" % (len(PATTERNS_BLANK), MAC))

    entries, problems = read_record(record)
    if entries is not None:
        if len(entries) != 2:
            problems.append("the broker saw %d connection(s), want 2" % len(entries))
        for i, q in enumerate(("ping", "hello")):
            if i < len(entries):
                problems += check_question_entry(i + 1, entries[i], q)
    ok &= report("the broker's record is not what UMBILICAL.md asks for", problems)
    if not problems:
        say("the broker received exactly two frames, 'ping' and 'hello', byte-exact per UMBILICAL.md")

    wants = [question_bytes("ping"), question_bytes("hello")]
    problems = check_relay_log(entries_relay, wants, "the relay")
    if entries is not None and len(entries_relay) != len(entries):
        problems.append("the relay logged %d connection(s) but the broker recorded %d" % (len(entries_relay), len(entries)))
    ok &= report("the relay's log does not agree with the record (WIRE.md, the relay)", problems)
    if not problems:
        say("the relay logged the same two connections: up %d/%d bytes, down %d/%d, no error - the request and response frames"
            % (wants[0][0], wants[1][0], wants[0][1], wants[1][1]))

    data = read_image(DISK)
    problems = ["the table: " + p for p in check_table(data)]
    if not problems:
        problems += check_notes_partition(data, ["keep this"], "the notebook")
    ok &= report("the notebook is not what it should be", problems)
    if not problems:
        say("the notes partition holds exactly 'keep this' - neither question was journaled")

    if None in geometry:
        say("no picture to judge - the boot lines were wrong")
        return 1
    regs = regions(geometry[2], geometry[3])
    expected = ["> ? ping", CANNED["ping"], "> keep this", "> ? hello"] + CANNED["hello"].split("\n") + [PROMPT]
    problems = check_region_rows(shot, geometry, regs["conversation"], expected)
    ok &= report("the screen does not show the conversation", problems)
    if not problems:
        say("the screen shows both questions, both answers and the prompt, from the shared font")

    problems = []
    if "r1" not in reads or "r2" not in reads:
        problems.append("the obs page could not be read around the screendump")
    else:
        r1, r2 = reads["r1"], reads["r2"]
        problems += check_strip(shot, geometry, r1, r2, "the strip")
        up_total = sum(e.get("up", 0) for e in entries_relay)
        down_total = sum(e.get("down", 0) for e in entries_relay)
        problems += check_counts(r2, {"questions": 2, "notes": 1, "errors": 0,
                                      "wire_conns": len(entries_relay)}, "the wire counters")
        if r2["bytes_out"] < up_total:
            problems.append("the obs page counts %d bytes out, fewer than the %d the relay received" % (r2["bytes_out"], up_total))
        if r2["bytes_in"] < down_total:
            problems.append("the obs page counts %d bytes in, fewer than the %d the relay sent" % (r2["bytes_in"], down_total))
    ok &= report("the strip and the wire counters are not the truth", problems)
    if not problems:
        say("the strip is the obs page; wire_conns %d = the relay's connections, %d bytes out >= %d up, %d bytes in >= %d down"
            % (reads["r2"]["wire_conns"], reads["r2"]["bytes_out"], up_total, reads["r2"]["bytes_in"], down_total))

    say("-smp %d: %s" % (smp, "the machine asked and was answered on the e1000e through the relay" if ok else "the round trip failed"))
    return 0 if ok else 1


# ------------------------------------------------- test 4: the cage holds ---
# (a) is test-7b.sh's own strings. Here: (b) the argv assertions on this
# checker's command and the twin's as broker/wire.py builds it; (c) the
# relay's bind rule on the host, no guest; (d) the mock-down run through
# the relay ending in a message; (e) "! test app" (ring 6a's grow, ABI 2)
# and "! install echo" (ring 6b's install) through the relay at -smp 4, the
# record, the germline, the home partition, the twin's disk, the relay's
# log against the frames; (f) the reboot with nothing on the wire.

BAD_BINDS = ("0.0.0.0", "10.0.2.2", "192.0.2.1")     # A3: three fixed addresses, no hostname lookup


def check_argv_7b(argv, port, want_mac, want_drives, virtio_allowed, netdevs_want, nic_netdev):
    """A QEMU command inspected for the cage and THIS ring's machine: every
    netdev slirp user mode, restrict=on, exactly one guestfwd from
    10.0.2.4:9999 by nc to 127.0.0.1 on the given port, no hostfwd, no
    other network option; exactly netdevs_want of them; one e1000e on
    nic_netdev with the patient's MAC; a virtio-net only in the twin's
    frozen shape (netdevs_want 2, on n0); -cpu IvyBridge; -vga none and the
    one VGA device with the 1920x1080 EDID; one ide-hd on ide.1; exactly
    want_drives drives, every one under stage7/out/, none if=virtio unless
    allowed (the frozen twin's notes disk - then exactly one)."""
    problems = []
    netdevs = [argv[i + 1] for i, a in enumerate(argv) if a == "-netdev"]
    devices = [argv[i + 1] for i, a in enumerate(argv) if a == "-device"]
    drives = [argv[i + 1] for i, a in enumerate(argv) if a == "-drive"]
    if len(netdevs) != netdevs_want:
        problems.append("expected exactly %d -netdev, found %d: %r" % (netdevs_want, len(netdevs), netdevs))
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
    ids = [re.search(r"(?:^|,)id=([^,]*)", nd) for nd in netdevs]
    ids = [m.group(1) for m in ids if m]
    if len(set(ids)) != len(netdevs):
        problems.append("the netdevs do not carry distinct ids: %r" % ids)
    for flag in ("-nic", "-net", "-netdev-add", "-hda", "-hdb", "-cdrom", "-blockdev", "-pflash"):
        if flag in argv:
            problems.append("the command carries %s" % flag)
    nics = [d for d in devices if d.startswith("e1000e")]
    vnics = [d for d in devices if d.startswith("virtio-net-pci")]
    vgas = [d for d in devices if d.startswith("VGA")]
    disks = [d for d in devices if d.startswith("ide-hd")]
    if nics != ["e1000e,netdev=%s,mac=%s" % (nic_netdev, want_mac)]:
        problems.append("expected one e1000e on %s with the patient's MAC %s, found %r" % (nic_netdev, want_mac, nics))
    want_vnics = ["virtio-net-pci,netdev=n0"] if netdevs_want == 2 else []
    if vnics != want_vnics:
        problems.append("expected the virtio-net devices %r, found %r" % (want_vnics, vnics))
    if vgas != ["VGA,edid=on,xres=1920,yres=1080"] or "-vga" not in argv or argv[argv.index("-vga") + 1] != "none":
        problems.append("the display is not -vga none with the one VGA device stating 1920x1080: %r" % vgas)
    if disks != ["ide-hd,drive=d0,bus=ide.1"]:
        problems.append("expected exactly one ide-hd on ide.1 as drive d0, found %r" % disks)
    if len(devices) != 3 + len(want_vnics):
        problems.append("expected exactly %d devices, found %r" % (3 + len(want_vnics), devices))
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


def check_bind_rule():
    """WIRE.md's bind rule, on the host: every address but the two is
    refused before any socket exists; 127.0.0.1 listens."""
    problems = []
    for addr in BAD_BINDS:
        r = subprocess.run([sys.executable, RELAY, "--bind", addr, "--port", str(RELAY_PORT)],
                           capture_output=True, text=True, timeout=10)
        if r.returncode != 2 or "refusing to bind" not in r.stderr:
            problems.append("--bind %s: exit %d, stderr %r - want exit 2 and the refusal" % (addr, r.returncode, r.stderr.strip()[:120]))
        if port_state(RELAY_PORT) == "open":
            problems.append("--bind %s: something listens on 127.0.0.1:%d after the refusal" % (addr, RELAY_PORT))
    relay, err = start_relay(os.path.join(WIRE_OUT, "relay.bind.jsonl"))
    if err:
        problems.append("--bind 127.0.0.1 --port %d: %s" % (RELAY_PORT, err))
    else:
        if port_state(RELAY_PORT) != "open":
            problems.append("the relay said it was listening on %d but nothing answers there" % RELAY_PORT)
        stop_mock(relay)
    return problems


def check_germline_entry_7b(root, want, blob, name, choices, model="mock"):
    """checkglass.check_germline_entry for this ring's twin: the same entry
    and provenance, and a rehearsal log holding WIRE.md's nineteen lines
    with the link line and the virtio disk untouched."""
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
                   "model": model, "sha256": hashlib.sha256(blob).hexdigest(), "size": len(blob),
                   "name": name, "choices": [[chr(k), l.decode()] for k, l in choices]}
    for k, v in want_fields.items():
        if prov.get(k) != v:
            problems.append("entry %s: provenance %s is %r, want %r" % (key, k, prov.get(k), v))
    reh = prov.get("rehearsal") or {}
    if reh.get("passed") is not True or reh.get("phrases") != []:
        problems.append("entry %s: provenance rehearsal is %r, want passed with no phrases" % (key, reh))
    try:
        rlog = open(os.path.join(d, "rehearsal.log")).read()
    except OSError as exc:
        return problems + ["entry %s: rehearsal.log: %s" % (key, exc)]
    return problems + check_rehearsal_log_7b(key, rlog)


def check_rehearsal_log_7b(key, rlog):
    problems = []
    if len(re.findall(r"^S7: ", rlog, re.M)) != len(PATTERNS_BLANK):
        problems.append("entry %s: rehearsal.log does not hold the twin's %d S7: lines" % (key, len(PATTERNS_BLANK)))
    if not re.search(r"^S7: nic %s$" % re.escape(MAC), rlog, re.M) or not re.search(r"^S7: link up$", rlog, re.M):
        problems.append("entry %s: rehearsal.log lacks 'S7: nic %s' and 'S7: link up' - the twin did not use the e1000e" % (key, MAC))
    if "ERR:" in rlog:
        problems.append("entry %s: rehearsal.log carries an ERR: line" % key)
    if "virtio notes.img: untouched, all zero" not in rlog:
        problems.append("entry %s: rehearsal.log does not say the twin's virtio disk stayed all zero" % key)
    return problems


def check_install_germline_7b(root, plan, blob, amendment=None, tests=None, model="mock"):
    """checkdisk.check_install_germline_7 for this ring's twin: the same
    entry, provenance and verdict, and WIRE.md's rehearsal log."""
    problems = []
    data, parsed = checkdisk.plan_of(plan)
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
    if "ok: the post-delivery hook found nothing" not in rlog:
        problems.append("entry %s: rehearsal.log does not say the plan's tests passed" % key)
    return problems + check_rehearsal_log_7b(key, rlog)


def run_cage():
    smp = 4
    # ------------------------------------------------ (b) the argv checks --
    argv = qemu_argv(smp, DISK, os.path.join(WIRE_OUT, "x"))
    problems = check_argv_7b(argv, RELAY_PORT, MAC, 2, False, 1, "n0")
    if not report("the checker's own QEMU command is not the cage with this ring's machine", problems):
        return 1
    say("the checker's QEMU command carries one restricted cage to the relay on %d, the e1000e on n0 with %s, -cpu IvyBridge, "
        "the 1920x1080 device, the ESP and the SATA disk under stage7/out/, no virtio" % (RELAY_PORT, MAC))

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
    if not report("the twin's QEMU command, as broker/wire.py builds it, is not the cage with this ring's machine", problems):
        return 1
    say("the twin's command carries two restricted cages both to 127.0.0.1:%d, the frozen virtio-net on n0, the e1000e on n1 with %s, "
        "-cpu IvyBridge, the same display, the frozen virtio notes disk and the 64 MB SATA disk under %s"
        % (REHEARSAL_PORT, MAC, os.path.relpath(TWIN_WORKDIR, REPO)))

    # ------------------------------------------------ (c) the bind rule ----
    problems = check_bind_rule()
    if not report("the relay's bind rule is not WIRE.md's", problems):
        return 1
    say("the relay refuses %s before any socket exists and listens on 127.0.0.1:%d" % (", ".join(BAD_BINDS), RELAY_PORT))

    blobs = {}
    for name in ("app", "echo"):
        blob, problems = fixture_self_check(name)
        if not report("the %s fixture is not what the repository says" % name, problems):
            return 1
        blobs[name] = blob
    app, echo = blobs["app"], blobs["echo"]
    say("the two fixtures reproduce their binaries")

    # ------------------------------------------------ (d) the mock down ----
    if port_state(BROKER_PORT) != "closed":
        say("something is listening on 127.0.0.1:%d - the mock-down run needs the port refused" % BROKER_PORT)
        return 1
    rlog = os.path.join(WIRE_OUT, "relay.down.jsonl")
    relay, err = start_relay(rlog)
    if err:
        say(err)
        return 1
    say("the mock down: the relay up on %d, nothing on %d; '? ping' then a note, at -smp 8" % (RELAY_PORT, BROKER_PORT))
    try:
        fresh_disk(DISK)
        shot = os.path.join(WIRE_OUT, "screen.cage.down.ppm")
        steps = [("type", "? ping\n"), ("sleep", 6.0), ("type", "still here\n"), ("sleep", SETTLE), ("shot", shot)]
        capture, reads, err, _ = drive(8, DISK, steps, os.path.join(WIRE_OUT, "serial.cage.down.txt"))
    finally:
        entries_relay = read_relay_log(rlog, want=1)
        stop_mock(relay)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    ok = True
    problems, geometry = check_boot_lines(capture, 8, True, "formatted", 0, DISK_SECTORS)
    problems += check_echo(capture, b"? ping\r\nstill here\r\n")
    ok &= report("the mock-down serial log is not what WIRE.md asks for", problems, capture)
    data = read_image(DISK)
    problems = ["the table: " + p for p in check_table(data)]
    if not problems:
        problems += check_notes_partition(data, ["still here"], "the mock down")
    ok &= report("the notebook after the mock-down run is not what it should be", problems)
    if len(entries_relay) != 1 or entries_relay[0].get("error") is None:
        problems = ["the relay logged %r, want exactly one connection with a non-null error (the bytes are a race, never asserted)" % (entries_relay,)]
    else:
        problems = []
    ok &= report("the relay's log of the refused broker is not what WIRE.md asks for", problems)
    if None in geometry:
        return 1
    regs = regions(geometry[2], geometry[3])
    conv = regs["conversation"]
    problems = check_region_rows(shot, geometry, conv, ["> ? ping", NO_ANSWER, "> still here", PROMPT])
    ok &= report("the screen does not show the failure honestly", problems)
    if ok:
        say("the mock down: %d lines; '%s' on the screen and the note journaled within 6 s; the relay logged one refused connection: %s"
            % (len(PATTERNS_BLANK), NO_ANSWER, entries_relay[0]["error"]))

    # ------------------------------------- (e) the grow and the install ----
    record = os.path.join(WIRE_OUT, "broker.cage.jsonl")
    rlog = os.path.join(WIRE_OUT, "relay.cage.jsonl")
    relay, err = start_relay(rlog)
    if err:
        say(err)
        return 1
    mock, err = start_mock(record)
    if err:
        say(err)
        stop_mock(relay)
        return 1
    say("the grow and the install: relay and mock up, germline wiped, a blank disk, -smp %d; '! test app', a key, Esc, '! install echo', Esc" % smp)
    shots = {k: os.path.join(WIRE_OUT, "screen.cage.%s.ppm" % k) for k in ("a", "l")}
    try:
        fresh_disk(DISK)
        steps = [
            ("type", "! test app\n"), ("wait_record", record, 1, 150.0), ("sleep", 3.0),
            ("type", "k"), ("sleep", 1.0), ("shot", shots["a"]),
            ("type", "\x1b"), ("sleep", 2.0),
            ("type", "! install echo\n"), ("wait_record", record, 2, 150.0), ("sleep", 3.0),
            ("type", "\x1b"), ("sleep", 1.0),
            ("obs", "e"),
        ]
        capture, reads, err, _ = drive(smp, DISK, steps, os.path.join(WIRE_OUT, "serial.cage.grow.txt"))
    finally:
        stop_mock(mock)
        entries_relay = read_relay_log(rlog, want=2)
        stop_mock(relay)
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    problems, geometry = check_boot_lines(capture, smp, True, "formatted", 0, DISK_SECTORS)
    problems += check_echo(capture, b"! test app\r\n! install echo\r\n")
    ok &= report("the grow-and-install serial log is not what WIRE.md asks for", problems, capture)

    app_answer = app_frame(app, b"test app", TEST_CHOICES, 0)
    echo_answer = app_frame(echo, b"echo", [], 0, installed=1)
    entries, problems = read_record(record)
    if entries is not None:
        if len(entries) != 2:
            problems.append("the broker saw %d connection(s), want 2" % len(entries))
        if len(entries) >= 1:
            problems += check_grow_entry(1, entries[0], "test app", "generated", 1, ["pass"], "app", app_answer, name="test app")
        if len(entries) >= 2:
            problems += check_install_entry(2, entries[1], "install echo", "generated", 2, ["pass"], "app", echo_answer,
                                            plan="echo", tests=ECHO_TESTS_OK)
    ok &= report("the record is not what GLASS.md and PLANS.md ask for", problems)
    if not problems:
        say("the record: 'test app' generated (call 1), rehearsed once, the app frame; 'install echo' generated (call 2), rehearsed once "
            "against the plan's five tests, the frame with installed 1")

    wants = [(len(grow_request(b"test app")), len(app_answer)), (len(grow_request(b"install echo")), len(echo_answer))]
    problems = check_relay_log(entries_relay, wants, "the relay")
    ok &= report("the relay's log does not agree with the two frames (WIRE.md, the relay)", problems)
    if not problems:
        say("the relay logged the two connections: up %d and %d bytes (GERMLINE.md's request frames), down %d and %d (the two app frames)"
            % (wants[0][0], wants[1][0], wants[0][1], wants[1][1]))

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
    more, _ = check_partitions(DISK, [], {"echo": {"current": (echo, DATA_FIRST), "previous": None, "choices": []}}, "the install")
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
    ok &= report("the disks after the install are not what DISK.md, HOME.md and the twin ask for", problems)
    if not problems:
        say("the home partition holds echo at partition sector %d hash-checked; the twin's disk formatted with 'after' on SATA and its virtio image all zero"
            % DATA_FIRST)
    shutil.copyfile(DISK, os.path.join(WIRE_OUT, "disk.after-install.img"))

    if None in geometry:
        return 1
    problems = check_app_panel(shots["a"], geometry, "k")
    problems += check_mode_field(shots["a"], geometry, "running test app")
    if "e" not in reads:
        problems.append("the obs page could not be read after the install")
    else:
        problems += check_counts(reads["e"], {"mode": 0, "wire_conns": len(entries_relay), "grows_generated": 2,
                                              "grows_served": 2, "errors": 0}, "after the install")
    ok &= report("screen A or the obs page after the install is not the truth", problems)
    if not problems:
        say("screen A: the test app's strips with 'key: k' and 'running test app'; the obs page: wire_conns %d = the relay's connections, "
            "two grows generated and served" % len(entries_relay))

    # ------------------------------------- (f) nothing on the wire ---------
    for port in (BROKER_PORT, RELAY_PORT):
        if port_state(port) == "open":
            say("something is listening on 127.0.0.1:%d - the no-wire boot cannot run" % port)
            return 1
    say("the reboot with nothing on the wire: %d and %d closed; the same disk; '! echo' from the home partition" % (BROKER_PORT, RELAY_PORT))
    steps = [
        ("obs", "r"),
        ("type", "! echo\n"), ("sleep", 2.0),
        ("type", "b"), ("sleep", 1.0),
        ("shot", shots["l"]), ("obs", "l"),
        ("type", "\x1b"), ("sleep", 1.0),
    ]
    capture, reads, err, _ = drive(smp, DISK, steps, os.path.join(WIRE_OUT, "serial.cage.launch.txt"))
    if err:
        say(err)
        if capture:
            dump_capture(capture)
        return 1
    problems, _ = check_boot_lines(capture, smp, False, "0 notes", 1, DISK_SECTORS)
    problems += check_echo(capture, b"! echo\r\n")
    ok &= report("the no-wire serial log is not what WIRE.md asks for", problems, capture)
    problems = check_one_cell_panel(shots["l"], geometry, "b")
    problems += check_mode_field(shots["l"], geometry, "running echo")
    problems += check_choices(shots["l"], geometry, CHOICES_ECHO_RUNNING)
    if "r" not in reads or "l" not in reads:
        problems.append("the obs page could not be read around the launch")
    else:
        r, l = reads["r"], reads["l"]
        problems += check_counts(l, {"mode": 3, "name": "echo", "focus": 1, "wire_conns": 0, "requests": 0,
                                     "errors": 0, "bytes_in": r["bytes_in"], "bytes_out": r["bytes_out"]}, "the launch")
    if read_image(DISK) != read_image(os.path.join(WIRE_OUT, "disk.after-install.img")):
        problems.append("the disk changed during the no-wire boot - a launch must not write")
    ok &= report("the launch with nothing on the wire is not what it should be", problems)
    if not problems:
        say("the launch: %d lines with 'home 1 apps'; echo ran from the home partition showing 'b' with wire_conns 0 and the byte "
            "counters unchanged; the disk untouched" % len(PATTERNS_AGAIN))

    say("the cage: %s" % ("held on the e1000e through the relay" if ok else "not proven"))
    return 0 if ok else 1


# --------------------------------------------------------------- main ------

def main(argv):
    os.makedirs(WIRE_OUT, exist_ok=True)
    if len(argv) == 2 and argv[0] == "--down":
        try:
            return run_down(int(argv[1]))
        except ValueError:
            pass
    if len(argv) == 2 and argv[0] == "--question":
        try:
            return run_question(int(argv[1]))
        except ValueError:
            pass
    if argv == ["--cage"]:
        return run_cage()
    say("usage: checkwire.py --down SMP | --question SMP | --cage")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
