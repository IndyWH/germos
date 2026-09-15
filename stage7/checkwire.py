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
    say("usage: checkwire.py --down SMP | --question SMP | --cage")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
