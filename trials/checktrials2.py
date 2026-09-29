#!/usr/bin/env python3
"""Ring 8t acceptance checker - trial two: the choices row, G against B.

Modes (all from the repo root, invoked by trials/test-trial2.sh):

  --document   test 1's second half: the stick as ring 7c's frozen checker
               parses it, with stage8's stick and build as explicit
               arguments; trials/TRIALS2.md read cold by trials/trials2.py
               and every worked example reproduced; the HP's history
               rebuilt as notes from the committed charts (each pinned by
               its SHA-256) meeting every "S7: notebook" checkpoint on
               them; that history and the HP's home store written to a
               host-formatted disk and read back by the frozen parsers
               (stage8/parts.py --disk, stage7/trials.py --disk against
               --serial on the 7d charts, trials2.py --disk); the G rows'
               and trial_number's run values (item 8's) equal to the rule.

Every expected line, count and byte is TRIALS2.md's rule through
trials/trials2.py, or the frozen checkers' own; the numbers only a run can
give are named constants with their date. Written before the guest code it
judges and frozen behind the hook once written (plan item 9). Everything it
starts is QEMU with OVMF, the patient's CPU model, the display at
1920x1080, the caged network (nothing listens behind it), the stick copy
over xhci, the SATA disk on ide.1, the PS/2 mouse driven through the
monitor; every drive a raw file under trials/out/. It starts no broker and
never spends a token.

Run directly, it appends its output to trials/out/gate-8t.log under its own
dated header. Under the gate (GATE_8T=1 in the environment) the gate's own
tee holds the log, and no second header is written.
"""

import datetime
import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
T8 = os.path.join(OUT, "t8")                      # the gate's scratch
LOG = os.path.join(OUT, "gate-8t.log")
S8OUT = os.path.join(REPO, "stage8", "out")
EFI = os.path.join(S8OUT, "BOOTX64.EFI")
STICK = os.path.join(S8OUT, "stick.img")
HISTORY = os.path.join(REPO, "history")
PORTS = (9999, 9998, 9997)

for _d in ("stage3", "stage6", "stage7", "stage8", "broker", "trials"):
    sys.path.insert(0, os.path.join(REPO, _d))
import trials2  # noqa: E402  - TRIALS2.md's Python (and trial one's tool as trials2.T1)
import checkmetal  # noqa: E402  - ring 7c's frozen checker: the twin of the HP
import checkdisk  # noqa: E402
import checknotes  # noqa: E402  - Stage 3's NOTEBOOK.md record builder
import checkplans  # noqa: E402  - HOME.md's parser
import metal  # noqa: E402  - DISK.md's Python
import parts  # noqa: E402  - PARTS.md's and SEED.md's Python
import checktrials  # noqa: E402  - ring 7d's frozen checker: the cell rendering, the boxes' check, the conversation's rows
import twin  # noqa: E402
from checkglass import say, report, dump_capture, check_region_rows, check_mode_field, check_counts, check_choices, PROMPT  # noqa: E402
from checkpointer import Pointer, park_cell, CELL  # noqa: E402
from plans import plan_keyname  # noqa: E402
from rehearse import KEY_GAP  # noqa: E402
from glass import regions  # noqa: E402

T1 = trials2.T1                                   # stage7/trials.py, frozen


class _Unset:
    def __repr__(self):
        return "UNSET"


UNSET = _Unset()

# ------------------------------------------------ the numbers a run gives --
# Item 8's probe (a private build with the guest drafted, played by the
# synthetic human) supplies these; each is written with its date. While one
# is UNSET the mode that needs it fails and names it.

# From item 8's run, 29 September 2026: the draft (61,440 bytes) played by this checker's
# --rows and --sittings, eight sittings and 1,188 timed cues, -smp 4.
G_ROWS_RUN = {                 # (label spans, separator columns) read back from the choices surface
    4: ([(12, 16), (41, 46), (71, 77), (101, 108)], [29, 59, 89]),     # R1, the warm-up's first cue
    2: ([(27, 31), (87, 92)], [59]),                                    # C1, the prompt at verdict G
    3: ([(17, 21), (56, 61), (94, 105)], [39, 79]),                     # W3, the HP's prompt at verdict G
}
TRIAL_NUMBER_AT_RUN = 0x340    # R1's page read at the sitting's start: 2 there, the three words after it 0
READY_LIMIT_S = 60.0           # ready 1.2-5.2 s from QEMU's start (5 s with a part's Esc window): 7c's window kept
READY_FULL_S = 20.0            # W3 with 1,141 notes on the HP's history: ready 1.89 s; ten times that
SETTLE_S = 1.0                 # the replay's end after ready: 0.26 s at 1,250 notes (item 1)
OFFSET_MS = 39                 # a cue timed from a hit's line: 1,048 cues read +31 to +49, median 39
OFFSET_FIRST_MS = -12          # a cue timed from a sitting or block line: 58 cues, median -12
HIT_WINDOW_MS = 60             # CC's own: every hit's residual against the rule was within 15 ms
SITTING_S = 300.0              # a sitting's boot took 186.8-195.0 s; about half as much again

# By rule, never from a run:
SLACK_MS = 30                  # a block's score against the script's: ring 7d's window (its A3), never widened
POLL_S = 0.005                 # the serial file's poll, ring 7d's
SMP = 4
OBS_BYTES = 0x368              # the page through molt_overflows: 0x340 trial_number, 0x348-0x358 zero
REST_S = trials2.REST_MS / 1000.0
PAUSE_S = trials2.PAUSE_MS / 1000.0
MS_RANGE = (100, 999)          # every scripted time and score: three digits, so no zero-padded counter of the
                               # strip can ever read as one (A2's token check)


def unset(names):
    return [n for n in names if isinstance(globals()[n], _Unset) or
            (isinstance(globals()[n], dict) and any(isinstance(v, _Unset) for v in globals()[n].values()))]


RUN_CONSTANTS = ["G_ROWS_RUN", "TRIAL_NUMBER_AT_RUN", "READY_LIMIT_S", "READY_FULL_S", "SETTLE_S", "OFFSET_MS",
                 "OFFSET_FIRST_MS", "HIT_WINDOW_MS", "SITTING_S"]


def apply_sets(pairs):
    """Item 8's run only: an unset constant given as NAME=VALUE (a Python literal). A set one never."""
    for pair in pairs:
        name, _, value = pair.partition("=")
        if name not in RUN_CONSTANTS:
            raise ValueError("--set %s: not a run constant" % name)
        if not unset([name]):
            raise ValueError("--set %s: it is set; only an unset constant may be given" % name)
        globals()[name] = eval(value, {})


def require(names):
    missing = unset(names)
    if missing:
        say("the run constants %s are unset - item 8's run supplies them, never a guess" % ", ".join(missing))
        return False
    return True


# ------------------------------------------------------------- the log ----

def commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return "none"
    d = subprocess.run(["git", "--no-optional-locks", "-C", REPO, "diff", "--quiet", "HEAD"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.stdout.strip() + ("+uncommitted" if d.returncode != 0 else "")


def tee_log(mode):
    if os.environ.get("GATE_8T") == "1":
        return None
    os.makedirs(OUT, exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write("\n=== checktrials2.py %s %s commit %s ===\n"
                 % (mode, datetime.datetime.now().astimezone().isoformat(timespec="seconds"), commit()))
    sys.stdout.flush()
    sys.stderr.flush()
    tee = subprocess.Popen(["tee", "-a", LOG], stdin=subprocess.PIPE)
    os.dup2(tee.stdin.fileno(), 1)
    os.dup2(tee.stdin.fileno(), 2)
    tee.stdin.close()
    return tee


def untee(tee):
    if tee is None:
        return
    sys.stdout.flush()
    sys.stderr.flush()
    os.close(1)
    os.close(2)
    tee.wait()


# ------------------------------------------------- the HP's history --------
# The HP's notebook as the committed charts give it (plan D3): ring 7c's two
# notes as HANDOVER records them; trial one's notes from the four ring 7d
# charts; ring 8a's molt notes and the owner's typed notes from its chart.
# Every chart is pinned by its SHA-256, and the notes must meet every
# "S7: notebook N notes" checkpoint the charts carry.

CHARTS_7D = [
    ("2026-09-24-ring7d-hp-sitting1-serial.log", "206a8a6102dcefa6082061d777af417fabc45f69b645670b59c68d5da4e94ca0"),
    ("2026-09-24-ring7d-hp-sitting2-serial.log", "d5ddb5c38eceea536b94cb73dc3e12446c112937ef020bed934e865897d98095"),
    ("2026-09-24-ring7d-hp-sitting3-serial.log", "a1475db523330b2ce650d3cb84784f1d96a45ee9a2909f25a2a7a30648535497"),
    ("2026-09-25-ring7d-hp-verdict-boot-serial.log", "7d4071e10a2facdcb31fbe1f904fdcb20e77b0449f061c4c508a9ca5653037f2"),
]
CHART_8A = ("2026-09-28-ring8a-hp-serial.log", "b4bfd649c5684b7ef9fee2eb43ee5000481075715066d08209ec9cc4efc9069f")
NOTES_7C = ["hello metal", "Tell me about this machine"]      # HANDOVER, ring 7d's HP sitting 1
HISTORY_COUNTS = {"notes": 355, "trial": 275, "molt": 41, "typed": 37}   # item 1's run, 28 September 2026
HISTORY_LAST = "molt i8042 demoted f0668b687c68cab0 unhealthy"
FIXTURE = os.path.join(REPO, "stage8", "fixtures", "i8042-%s.bin")
FIXTURE_SHA = {"good": "4fe6beefc4bc57d0e9ff23f4c605d85950eb99537371756f1b61ac441f8d2785",
               "hang": "f0668b687c68cab0bed99268bb539d6bfb5d9ab30b2ecbf1013e5b0d5defee77"}
CALCULATOR = os.path.join(REPO, "stage6", "echo.bin")         # the stand-in for the HP's calculator, by that name
STAMP = re.compile(rb"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3} ")
RAW_LINE = re.compile(rb"(molt: [^\r\n]*|S8: [^\r\n]*|S7: mouse ready|part: [^\r\n]*|i8042: [^\r\n]*)\r?\n")
CHECKPOINT = re.compile(rb"S7: notebook (\d+) notes")


def chart_stream(name, sha):
    """A committed chart as the UART sent it: its SHA-256 checked, the host's stamps removed."""
    raw = open(os.path.join(HISTORY, name), "rb").read()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError("history/%s is not the chart this checker was written from" % name)
    return b"".join(STAMP.sub(b"", l.rstrip(b"\r")) + b"\n" for l in raw.split(b"\n") if l)


def chart_boots(data):
    return [b"S7: alive" + p for p in data.split(b"S7: alive")[1:]]


def typed_text(line):
    out = []
    for ch in line:
        if ch == "\b":
            if out:
                out.pop()
        else:
            out.append(ch)
    return "".join(out)


def boot_notes_8a(boot):
    """One ring 8a boot's notes in journal order: the molt notes journaled before
    the handover, then, after ready, each molt note where its raw line starts and
    each typed note at its Enter, the raw lines taken out of the echo wherever
    they land and backspaces applied; '!' and '?' lines are not notes."""
    ready = boot.find(b"S7: keyboard ready\n")
    pre, post = boot[:ready], boot[ready + len(b"S7: keyboard ready\n"):]
    notes = ["molt " + m.decode()[6:] for m in re.findall(rb"molt: [^\r\n]*", pre)]
    echo, pos, events = b"", 0, []
    for m in RAW_LINE.finditer(post):
        echo += post[pos:m.start()]
        if m.group(1).startswith(b"molt: "):
            events.append((len(echo), 0, "molt " + m.group(1).decode()[6:]))
        pos = m.end()
    echo += post[pos:]
    at = 0
    for line in echo.split(b"\n")[:-1]:
        at += len(line) + 1
        text = typed_text(line.decode("latin-1"))
        if text and text[0] not in "!?":
            events.append((at, -1, text))
    events.sort(key=lambda e: (e[0], e[1]))
    return notes + [e[2] for e in events]


def hp_history():
    """(the HP's notes, the checkpoints as (where, the chart's count, the notes built before that boot))."""
    notes, checks = list(NOTES_7C), []
    for name, sha in CHARTS_7D:
        for boot in chart_boots(chart_stream(name, sha)):
            checks.append((name, int(CHECKPOINT.search(boot).group(1)), len(notes)))
            notes += [T1.note_of_serial(m.group(0).decode()) for m in re.finditer(rb"trial:[^\r\n]*", boot)]
    for i, boot in enumerate(chart_boots(chart_stream(*CHART_8A)), 1):
        checks.append(("ring 8a boot %d" % i, int(CHECKPOINT.search(boot).group(1)), len(notes)))
        notes += boot_notes_8a(boot)
    return notes, checks


def check_history():
    problems = []
    try:
        notes, checks = hp_history()
    except (ValueError, OSError) as exc:
        return ["the HP's history: %s" % exc], None
    for where, chart, built in checks:
        if chart != built:
            problems.append("%s: the chart says %d notes, the history built so far holds %d" % (where, chart, built))
    got = {"notes": len(notes), "trial": sum(1 for n in notes if n.startswith("trial ")),
           "molt": sum(1 for n in notes if n.startswith("molt "))}
    got["typed"] = got["notes"] - got["trial"] - got["molt"] - len(NOTES_7C)
    if got != HISTORY_COUNTS:
        problems.append("the history holds %r, item 1's run held %r" % (got, HISTORY_COUNTS))
    if notes and notes[-1] != HISTORY_LAST:
        problems.append("the history ends %r, not %r" % (notes[-1], HISTORY_LAST))
    if parts.state_of(notes, "i8042")[0] != "demoted":
        problems.append("the history leaves i8042 %r, not demoted" % (parts.state_of(notes, "i8042"),))
    return problems, notes


# ------------------------------------------------- disks from the host -----

def fixture(fate):
    blob = open(FIXTURE % fate, "rb").read()
    if hashlib.sha256(blob).hexdigest() != FIXTURE_SHA[fate]:
        raise ValueError("stage8/fixtures/i8042-%s.bin is not the build the HP's notes name" % fate)
    return blob


def hp_home():
    """The HP's home store as its notes left it: the calculator (a stand-in), then
    part-i8042 with hang current and good its previous build."""
    return [("calculator", open(CALCULATOR, "rb").read(), None),
            ("part-i8042", fixture("hang"), fixture("good"))]


def write_home(part, entries):
    """HOME.md's table and data written into a formatted home partition (bytes),
    builds placed in order from the data's first sector: each entry's previous
    build first, then its current, as an install leaves them."""
    part = bytearray(part)
    if part[0:8] != b"GERMHOME":
        raise ValueError("the home partition is not formatted")
    nxt = checkplans.DATA_FIRST
    for i, (name, current, previous) in enumerate(entries):
        rec = bytearray(checkplans.ENTRY)
        rec[0:len(name)] = name.encode("ascii")
        for off, blob in ((0x50, previous), (0x20, current)):
            if blob is None:
                continue
            sectors = (len(blob) + checkplans.SECTOR - 1) // checkplans.SECTOR
            struct.pack_into("<IIII", rec, off, len(blob), nxt, sectors, 0)
            rec[off + 16:off + 48] = hashlib.sha256(blob).digest()
            start = nxt * checkplans.SECTOR
            part[start:start + sectors * checkplans.SECTOR] = blob + bytes(sectors * checkplans.SECTOR - len(blob))
            nxt += sectors
        base = (checkplans.TABLE_FIRST + i // 2) * checkplans.SECTOR + (i % 2) * checkplans.ENTRY
        part[base:base + checkplans.ENTRY] = rec
    return bytes(part)


def write_notes(part, notes):
    """NOTEBOOK.md's records written into a formatted notes partition (bytes), from sequence 1."""
    part = bytearray(part)
    for seq, text in enumerate(notes, 1):
        part[seq * metal.SECTOR:(seq + 1) * metal.SECTOR] = checknotes.expected_record(seq, text)
    return bytes(part)


def write_disk(path, notes, entries, host_format=False):
    """Notes and home entries written into a disk the guest formatted (or, for
    test 1, a disk formatted from the host by DISK.md, NOTEBOOK.md and HOME.md)."""
    if host_format:
        n = metal.DISK_BYTES_7 // metal.SECTOR
        data = bytearray(metal.DISK_BYTES_7)
        for lba, sector in metal.build_gpt(n).items():
            data[lba * metal.SECTOR:(lba + 1) * metal.SECTOR] = sector
        table = metal.parse_gpt(bytes(data))
        nf, ns = table["notes"]
        data[nf * metal.SECTOR:(nf + 1) * metal.SECTOR] = checknotes.expected_header(ns * metal.SECTOR)
        hf, hs = table["home"]
        head = b"GERMHOME" + struct.pack("<IIQQQQ", 1, 512, 1, 8, 9, hs)
        data[hf * metal.SECTOR:(hf + 1) * metal.SECTOR] = head + bytes(metal.SECTOR - len(head))
    else:
        data = bytearray(checkdisk.read_image(path))
    table = metal.parse_gpt(bytes(data))
    for key, fn, arg in (("notes", write_notes, notes), ("home", write_home, entries)):
        first, sectors = table[key]
        lo, hi = first * metal.SECTOR, (first + sectors) * metal.SECTOR
        data[lo:hi] = fn(bytes(data[lo:hi]), arg)
    with open(path, "wb") as fh:
        fh.write(bytes(data))


def notes_on_disk(path):
    data = checkdisk.read_image(path)
    return checkdisk.parse_notebook(metal.partition_bytes(data, metal.parse_gpt(data)["notes"]))


def home_on_disk(path):
    data = checkdisk.read_image(path)
    return checkplans.parse_home(metal.partition_bytes(data, metal.parse_gpt(data)["home"]))


def run_tool(args):
    r = subprocess.run([sys.executable] + args, cwd=REPO, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def check_hp_disk(path, notes):
    """The HP's disk read back by the frozen parsers: the notes, the home store, the
    molt table, trial one's report, and no trial-two sitting."""
    problems = []
    if notes_on_disk(path) != notes:
        problems.append("the notes do not read back")
    home = home_on_disk(path)
    names = [e["name"] for e in home["entries"] if e]
    part = next((e for e in home["entries"] if e and e["name"] == "part-i8042"), None)
    if names != ["calculator", "part-i8042"] or part is None or \
            part["current"]["sha256"] != FIXTURE_SHA["hang"] or (part["previous"] or {}).get("sha256") != FIXTURE_SHA["good"]:
        problems.append("the home store is %r, not the calculator and part-i8042 with hang current and good previous" % names)
    rc, out = run_tool([os.path.join(REPO, "stage8", "parts.py"), "--disk", path])
    if rc != 0 or "i8042 demoted f0668b687c68cab0 unhealthy" not in out or "home: 1 app(s), 1 part(s)" not in out:
        problems.append("stage8/parts.py --disk: exit %d, %r" % (rc, out[-300:]))
    joined = os.path.join(T8, "trial-one-charts.log")
    with open(joined, "wb") as fh:
        for name, sha in CHARTS_7D:
            fh.write(chart_stream(name, sha))
    rc1, out1 = run_tool([os.path.join(REPO, "stage7", "trials.py"), "--disk", path])
    rc2, out2 = run_tool([os.path.join(REPO, "stage7", "trials.py"), "--serial", joined])
    if rc1 != 0 or out1 != out2 or "verdict A:" not in out1:
        problems.append("stage7/trials.py --disk (exit %d) is not its --serial on the ring 7d charts (exit %d): %r"
                        % (rc1, rc2, out1[-200:]))
    rc, out = run_tool([os.path.join(HERE, "trials2.py"), "--disk", path])
    if rc != 0 or not out.startswith("no sittings") or "boot line: none" not in out:
        problems.append("trials2.py --disk: exit %d, %r" % (rc, out[-200:]))
    return problems, out1


# ------------------------------------------------ test 1: the documents ---

def run_document():
    ok = True
    os.makedirs(T8, exist_ok=True)
    problems = checkmetal.check_stick(STICK, EFI)
    if report("the stick is not ring 7c's shape carrying stage8's build", problems):
        say("the stick: a protective MBR, both GPT headers and arrays, one EFI System Partition holding "
            "EFI/BOOT/BOOTX64.EFI byte for byte stage8's build")
    else:
        ok = False
    rc, out = run_tool([os.path.join(HERE, "trials2.py"), "--example"])
    for line in out.strip().splitlines():
        say("trials2.py --example: " + line)
    ok = ok and rc == 0
    problems, notes = check_history()
    if report("the HP's history is not what its charts say", problems):
        say("the HP's history: %d notes from the pinned charts (%d trial, %d molt, %d typed, 2 from ring 7c), every "
            "S7: notebook checkpoint met, ending %r" % (len(notes), HISTORY_COUNTS["trial"], HISTORY_COUNTS["molt"],
                                                        HISTORY_COUNTS["typed"], notes[-1]))
        disk = os.path.join(T8, "disk.hp-host.img")
        try:
            write_disk(disk, notes, hp_home(), host_format=True)
            problems, t1 = check_hp_disk(disk, notes)
        except (ValueError, OSError) as exc:
            problems = ["the host-formatted HP disk: %s" % exc]
        if report("the HP's disk written from the host does not read back", problems):
            say("the HP's disk, formatted and written from the host: the notes read back; the home store the calculator "
                "and part-i8042 (hang current, good previous); parts.py --disk says i8042 demoted f0668b687c68cab0 "
                "unhealthy, 1 app and 1 part; stage7/trials.py --disk equals its --serial on the 7d charts (%s); "
                "trials2.py --disk: no sittings, no boot line" % t1.strip().splitlines()[-1])
        else:
            ok = False
    else:
        ok = False
    missing = unset(["G_ROWS_RUN", "TRIAL_NUMBER_AT_RUN"])
    problems = ["%s is unset: item 8's run supplies it" % n for n in missing]
    if not missing:
        labels = {4: trials2.ROW_ITEMS, 2: ["? ask", "! grow"], 3: ["? ask", "! grow", "! calculator"]}
        for n, got in sorted(G_ROWS_RUN.items()):
            rule = trials2.grouped_columns(120, labels[n])
            if tuple(got) != rule:
                problems.append("the %d-item G row: the run read %r, the rule gives %r" % (n, got, rule))
        if TRIAL_NUMBER_AT_RUN != trials2.OBS_8T["trial_number"]:
            problems.append("trial_number: the run read it at 0x%x, the document says 0x%x"
                            % (TRIAL_NUMBER_AT_RUN, trials2.OBS_8T["trial_number"]))
    if report("the run's G rows or trial_number are not the rule's", problems):
        say("the run's G rows (four, two and three items) and trial_number's offset equal TRIALS2.md's rule")
    else:
        ok = False
    return 0 if ok else 1


# ------------------------------------------------------------ the twin -----
# One boot of the twin of the HP on a copy of stage8's stick: ring 7c's QEMU
# command (checkmetal.qemu_argv, the cage to 127.0.0.1:9997 where nothing
# listens - a trial sends nothing), the guest's own ready line awaited, the
# monitor and the serial file at hand, the PS/2 mouse driven through the
# monitor with the pointer model of ring 6c; quit and reaped at the end.

TRIAL2_LINE = re.compile(rb"trial2: [^\r\n]*")
READY = checkmetal.READY


class Boot:
    def __init__(self, name, disk, full=False):
        self.name, self.disk = name, disk
        self.serial_path = os.path.join(T8, "serial.%s.txt" % name)
        self.copy = os.path.join(T8, "stick.%s.img" % name)
        self.limit = READY_FULL_S if full else READY_LIMIT_S
        self.events = []
        self.offset = 0
        self.proc = self.drv = self.err = self.obs_addr = self.geometry = None
        self.ready_s = None

    def __enter__(self):
        if os.path.exists(self.serial_path):
            os.remove(self.serial_path)
        shutil.copyfile(STICK, self.copy)
        t0 = time.time()
        self.proc = subprocess.Popen(checkmetal.qemu_argv(SMP, self.disk, self.copy, self.serial_path),
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.drv = twin.Driver(self.proc, self.serial_path, T8)
        while time.time() - t0 < self.limit:
            time.sleep(0.02)
            if self.proc.poll() is not None or READY in self.serial():
                break
        if READY not in self.serial():
            self.err = "%s: the guest never printed %r within %.0f s" % (self.name, READY.decode(), self.limit)
            errs = re.findall(rb"ERR: [^\r\n]*", self.serial())
            if errs:
                self.err += " (the guest said: %s)" % errs[0].decode(errors="replace")
            return self
        self.ready_s = time.time() - t0
        m = re.search(rb"S7: notebook (\d+) notes", self.serial())
        say("(%s: ready %.2f s after QEMU's start, %s notes)" % (self.name, self.ready_s, m.group(1).decode() if m else "no"))
        time.sleep(SETTLE_S)
        w, h = checkmetal.geometry_of(self.serial())
        self.geometry = (w, h, w // CELL, h // CELL)
        self.model = Pointer(w, h)
        self.regs = regions(self.geometry[2], self.geometry[3])
        self.crow = self.regs["choices"][0]
        self.offset = self.serial().find(READY)
        return self

    def __exit__(self, *exc):
        if self.proc is None:
            return False
        self.drv.tell(b"quit\n")
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        if self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait()
        for f in (self.proc.stdin,):
            try:
                f.close()
            except OSError:
                pass
        return False

    def serial(self):
        return self.drv.serial_bytes()

    def wait_line(self, pattern, limit):
        """The next match after the last one this boot waited for, by the serial file's poll."""
        rx = re.compile(pattern)
        deadline = time.time() + limit
        while time.time() < deadline:
            m = rx.search(self.serial(), self.offset)
            if m:
                self.offset = m.end()
                return m, time.time()
            time.sleep(POLL_S)
        return None, time.time()

    def type(self, text):
        for i, ch in enumerate(text):
            if i:
                time.sleep(KEY_GAP)
            if ch in "\n\t\x1b":
                name = twin.keyname(ch)
            elif ch == "\b":
                name = "backspace"
            else:
                name = plan_keyname(ch)
            self.drv.tell(b"sendkey " + name.encode() + b"\n")
        self.events.append(("type", text))

    def move(self, dx, dy):
        self.drv.tell(b"mouse_move %d %d\n" % (dx, dy))
        self.model.move(dx, dy)
        self.events.append(("mouse", dx, dy))
        time.sleep(0.02)

    def moveto(self, row, col):
        for _, dx, dy in self.model.moves_to(row, col):
            self.move(dx, dy)

    def press(self):
        self.drv.tell(b"mouse_button 1\n")
        self.events.append(("button", 1))
        time.sleep(0.05)
        self.drv.tell(b"mouse_button 0\n")
        self.events.append(("button", 0))

    def park(self):
        self.moveto(*park_cell(self.geometry))
        time.sleep(0.3)

    def page(self):
        """The obs page by TRIALS2.md's parse_obs_8t, and the three words it keeps zero."""
        if self.obs_addr is None:
            m = re.search(rb"S7: obs page 0x([0-9a-f]+)", self.serial())
            self.obs_addr = int(m.group(1), 16) if m else 0
        if not self.obs_addr:
            raise ValueError("no obs page line on serial")
        raw = self.drv.xp(self.obs_addr, OBS_BYTES // 8, "g")
        obs = trials2.parse_obs_8t(raw)
        obs["zero_8t"] = [struct.unpack_from("<Q", raw, o)[0] for o in range(trials2.OBS_ZERO_8T[0], trials2.OBS_ZERO_8T[1], 8)]
        return obs

    def surfaces(self):
        obs = self.page()
        reads = {name: self.drv.read_surface(obs[name]) for name in ("strip", "choices", "conversation", "app")}
        reads["obs"] = obs
        return reads

    def shot(self, label):
        path = os.path.join(T8, "screen.%s.%s.ppm" % (self.name, label))
        self.drv.screendump(path)
        return path

    def conv(self):
        reads = self.surfaces()
        return checktrials.conv_rows(reads["conversation"], reads["obs"]), reads

    def wait_conv(self, text, limit=10.0):
        """Poll the conversation surface until a row equals text; the rows then, or None."""
        deadline = time.time() + limit
        while time.time() < deadline:
            rows, reads = self.conv()
            if text in rows:
                return rows, reads
            time.sleep(0.2)
        return None, None

    # -- the synthetic human ------------------------------------------------
    def target(self, idx):
        """The cell the hand rests on for item idx: the middle of B's filled span on row R-1, G's and B's target alike."""
        z = trials2.zones(self.geometry[2], len(trials2.ROW_ITEMS))[idx]
        return self.crow + 1, (z[2] + z[3]) // 2

    def gap(self):
        """The first zone's gap column: a '|' in G, background in B - a miss in either."""
        return self.crow, trials2.zones(self.geometry[2], len(trials2.ROW_ITEMS))[0][1]

    def play(self, script, results, start="type", hooks=None, prefer_verdict=False):
        """Play one scripted sitting (TRIALS2.md's script shape). start: "type" types
        '! trial 2', "enter" presses Enter on the empty prompt line. hooks: "start",
        (b, c) before cue c of block b is pressed, "rest" (after block b), "question"
        (the done note on serial, the key not yet pressed), "saved" (the saved line
        shown). Fills results; returns None or a problem."""
        hooks = hooks or {}
        s = script["sitting"]
        self.type("! trial 2\n" if start == "type" else "\n")
        m, t = self.wait_line(rb"trial2: sitting %d ([GB]{4} [GB]{4})" % s, 20.0)
        if not m:
            return "%s: no 'trial2: sitting %d' line on serial within 20 s" % (self.name, s)
        results["order"], results["sitting_at"] = m.group(1).decode(), t
        if "start" in hooks:
            hooks["start"]()
        anchor = t
        abort = script.get("abort")
        for b in range(0, trials2.BLOCKS + 1):
            blk = script["warmup"] if b == 0 else script["blocks"][b - 1]
            seq = trials2.cue_sequence(b)
            cue_at = anchor + (REST_S if b else 0.0)
            for c in range(1, len(seq) + 1):
                if abort and abort == (b, c - 1):
                    self.type("\x1b")
                    m, t = self.wait_line(rb"trial2: sitting %d aborted (\d+)" % s, 10.0)
                    if not m:
                        return "%s: no aborted line after Esc in block %d" % (self.name, b)
                    results["aborted"], results["aborted_at"] = int(m.group(1)), t
                    rows, reads = self.wait_conv(trials2.SAVED)
                    if rows is None:
                        return "%s: no saved line after the abort within 10 s" % self.name
                    results["saved_rows"], results["saved_reads"] = rows, reads
                    if "saved" in hooks:
                        hooks["saved"]()
                    return None
                L = trials2.layout(s, b, c)
                idx = trials2.ITEMS.index(seq[c - 1])
                d = blk["ms"][c - 1] / 1000.0
                if (b, c) in hooks:
                    hooks[(b, c)]()
                if c in blk.get("miss", ()):
                    self.moveto(*self.gap())
                    time.sleep(max(0.0, cue_at + d - time.time()))
                    self.press()
                    m, t = self.wait_line(rb"trial2: %d %d %s %d miss" % (s, b, L.encode(), c), 5.0)
                    if not m:
                        return "%s: no miss line for sitting %d block %d cue %d" % (self.name, s, b, c)
                    self.moveto(*self.target(idx))
                    time.sleep(max(0.0, t + d - time.time()))
                else:
                    self.moveto(*self.target(idx))
                    time.sleep(max(0.0, cue_at + d - time.time()))
                self.press()
                m, t = self.wait_line(rb"trial2: %d %d %s %d (\d+)" % (s, b, L.encode(), c), 5.0)
                if not m:
                    return "%s: no hit line for sitting %d block %d cue %d" % (self.name, s, b, c)
                results.setdefault("hits", {})[(b, c)] = int(m.group(1))
                cue_at = t + PAUSE_S
            if b == 0:
                anchor = t + PAUSE_S
                time.sleep(max(0.0, anchor + 0.1 - time.time()))    # the rest begins at the pause's end
            else:
                m, t = self.wait_line(rb"trial2: block %d %d [GB] (\d+) (\d+) (\d+)" % (s, b), 5.0)
                if not m:
                    return "%s: no block line for sitting %d block %d" % (self.name, s, b)
                anchor = t
            if abort and abort == (b + 1, 0):
                continue
            if b < trials2.BLOCKS and "rest" in hooks:
                hooks["rest"](b)
        if abort:
            return "%s: the script's abort %r was never played" % (self.name, abort)
        m, t = self.wait_line(rb"trial2: sitting %d done" % s, 5.0)
        if not m:
            return "%s: no done line for sitting %d" % (self.name, s)
        results["done_at"] = t
        if prefer_verdict:
            m, t = self.wait_line(rb"trial2: verdict ([GB]) (-?\d+)", 5.0)
            if not m:
                return "%s: no verdict line after sitting %d's done line" % (self.name, s)
            results["verdict"] = (m.group(1).decode(), int(m.group(2)))
        rows, reads = self.wait_conv(trials2.QUESTION)
        if rows is None:
            return "%s: the question never showed after sitting %d's done line" % (self.name, s)
        results["question_rows"], results["question_reads"] = rows, reads
        if "question" in hooks:
            hooks["question"]()
        answer = script.get("prefer")
        if answer is None:
            return None                               # powered off at the question: the caller quits
        self.type("\x1b" if answer == "skip" else answer)
        m, t = self.wait_line(rb"trial2: prefer %d (\w+)" % s, 10.0)
        if not m:
            return "%s: no prefer line after the key" % self.name
        results["prefer"] = m.group(1).decode()
        rows, reads = self.wait_conv(trials2.SAVED)
        if rows is None:
            return "%s: no saved line within 10 s of the preference" % self.name
        results["saved_rows"], results["saved_reads"] = rows, reads
        if "saved" in hooks:
            hooks["saved"]()
        return None


# ------------------------------------------------------ the judgements -----

def expected_script(script):
    """The script with every delay replaced by the ms the guest should record. A cue the
    human times from a hit's line (after a pause, and block 1's first cue, whose rest the
    human times from the warm-up's last hit) records d plus OFFSET_MS: the hit's note is
    journaled before its line anchors the human. A cue timed from a sitting or block line
    (the warm-up's first, and blocks 2-8's first) records d plus OFFSET_FIRST_MS. A cue
    missed first adds a second interval, d plus OFFSET_MS, from the miss's line."""
    def one(blk, first):
        ms = []
        for c, d in enumerate(blk["ms"]):
            v = d + (first if c == 0 else OFFSET_MS)
            if c + 1 in blk.get("miss", ()):
                v += d + OFFSET_MS
            ms.append(v)
        return {"ms": ms, "miss": list(blk.get("miss", ()))}
    out = dict(script)
    out["warmup"] = one(script["warmup"], OFFSET_FIRST_MS)
    out["blocks"] = [one(b, OFFSET_MS if i == 0 else OFFSET_FIRST_MS) for i, b in enumerate(script["blocks"])]
    return out


def check_script_range(script):
    """A2's token check holds only while every time and score is three digits."""
    want = trials2.notes_of(expected_script(script))
    bad = []
    for p in map(trials2.parse_note, want):
        v = p.get("ms") if p else None
        v = p.get("score") if p and v is None else v
        if v is not None and not MS_RANGE[0] <= v <= MS_RANGE[1]:
            bad.append(v)
    return ["sitting %d's script gives %r outside %r" % (script["sitting"], bad[:3], MS_RANGE)] if bad else []


def compare_notes(actual, script, label, untimed=()):
    """The notes a played sitting left against its script: every non-hit note byte for
    byte; every hit note's fields exact and its ms within HIT_WINDOW_MS; every block
    score within SLACK_MS of the rule over the expected ms; the block notes agreeing
    with their own hits exactly (check_blocks)."""
    want = trials2.notes_of(expected_script(script))
    problems = []
    if len(actual) != len(want):
        problems.append("%s: %d notes, want %d" % (label, len(actual), len(want)))
    exp_ms = {}
    for i, (a, w) in enumerate(zip(actual, want)):
        pa, pw = trials2.parse_note(a), trials2.parse_note(w)
        if pa is None or pa["kind"] != pw["kind"]:
            problems.append("%s: note %d is %r, want the shape of %r" % (label, i + 1, a, w))
            break
        if pw["kind"] == "hit":
            if (pa["sitting"], pa["block"], pa["layout"], pa["cue"]) != (pw["sitting"], pw["block"], pw["layout"], pw["cue"]):
                problems.append("%s: note %d is %r, want %r" % (label, i + 1, a, w))
                break
            exp_ms.setdefault(pw["block"], []).append(pw["ms"])
            if (pw["block"], pw["cue"]) not in untimed and abs(pa["ms"] - pw["ms"]) > HIT_WINDOW_MS:
                problems.append("%s: note %d %r - %d ms is outside %d +/- %d" % (label, i + 1, a, pa["ms"], pw["ms"], HIT_WINDOW_MS))
        elif pw["kind"] == "block":
            if (pa["sitting"], pa["block"], pa["layout"], pa["hits"], pa["misses"]) != \
                    (pw["sitting"], pw["block"], pw["layout"], pw["hits"], pw["misses"]):
                problems.append("%s: note %d is %r, want %r but for the score" % (label, i + 1, a, w))
                break
            if abs(pa["score"] - pw["score"]) > SLACK_MS:
                problems.append("%s: block %d's score is %d, the script gives %d +/- %d" % (label, pa["block"], pa["score"], pw["score"], SLACK_MS))
        elif a != w:
            problems.append("%s: note %d is %r, want %r" % (label, i + 1, a, w))
            break
    problems += ["%s: %s" % (label, p) for p in trials2.check_blocks(actual)]
    return problems


def serial_notes(capture):
    """The trial-two notes on serial (the boot lines left out), and the capture without
    every trial2: line and the mouse line, for the echo check."""
    lines = [m.group(0).decode() for m in TRIAL2_LINE.finditer(capture)]
    notes = trials2.notes_of_chart(lines)
    stripped = re.sub(rb"trial2: [^\r\n]*\r\n", b"", capture).replace(checkmetal.MOUSE_LINE_BYTES, b"")
    return notes, stripped


def boot_line_of(capture):
    m = re.findall(rb"trial2: (?:due|concluded) [^\r\n]*", capture)
    return [x.decode() for x in m]


def g_columns_of(cells, cols):
    """(label spans, separator columns) of a G row read from the choices surface's two rows."""
    row0, row1 = cells[:cols], cells[cols:2 * cols]
    seps = [c for c in range(cols) if row0[c] == trials2.SEPARATOR and row1[c] == trials2.SEPARATOR]
    spans, lo = [], 0
    for hi in seps + [cols]:
        idx = [c for c in range(lo, hi) if row0[c] != 0x20]
        if idx:
            spans.append((idx[0], idx[-1]))
        lo = hi + 1
    return spans, seps


def check_layout_g(shot, reads, geometry, labels, label):
    """The choices surface is TRIALS2.md's G row for these labels, in normal cells, and
    the screen shows it cell for cell."""
    cols = geometry[2]
    want0, want1 = trials2.grouped_cells(cols, labels)
    got = reads.get("choices")
    problems = []
    if got is None:
        return ["%s: the choices surface was not read" % label]
    if got[:cols] != want0 or got[cols:2 * cols] != want1:
        problems.append("%s: the choices surface is not TRIALS2.md's G row for %r (row 0 %r, want %r)"
                        % (label, labels, got[:cols], want0))
    if any(b & 0x80 for b in got[:2 * cols]):
        problems.append("%s: a G cell carries bit 7" % label)
    problems += checktrials.check_choices_bytes(shot, geometry, (want0, want1), label)
    return problems


def replay_rows(notes, width):
    """Every row the replay could draw for the notes that are not trial two's: each note
    cut at the conversation's width."""
    rows = set()
    for n in notes:
        if n.startswith(trials2.NOTE_PREFIX):
            continue
        for i in range(0, max(len(n), 1), width):
            rows.add(n[i:i + width].rstrip())
    return rows


STRIP_ROW0 = re.compile(r"up \d{6} core \d\d fr \d{6} \d\d\.\d/\d\d\.\d ph \d\d\.\d/\d\d\.\d k \d{4} hw \d{3} "
                        r"err \d{3} step \d\d\.\d/\d\d\.\d( pt \d\d\.\d/\d\d\.\d pk \d{4} cl \d{3})?")
STRIP_ROW1 = re.compile(r"(.{18}) q \d{3} n \d{3} g \d{3}/\d{3} disk \d{4} \d{6} w \d{3} \d{6} io \d{6}/\d{6}")
MODE_FIELD = re.compile(r"(prompt|asking|growing|installing|running .{1,10}|trial [AB] \d/8|trial2 [ABG] \d/8) *")
CONSOLE_LOG = ("S7: ", "S8: ", "i8042: ", "part: ", "hold Esc")
COUNTS_ROW = re.compile(r"hits \d+ misses \d+")


def hidden_times(reads, secrets, allowed, label):
    """A2: no trial-two time or score anywhere the owner can look. The strip: both rows
    are GLASS.md's template shape - fixed counter fields, none of them a trial time -
    with a mode word from the documents' list. The conversation and the app panel: no
    row holds a recorded time or score as a token, and none is a trial-two note; the
    rows of another note's replay, the boot log and the counts line are passed over."""
    problems = []
    obs = reads["obs"]
    C = obs["strip"]["cols"]
    rows = [reads["strip"][r * C:(r + 1) * C].decode("ascii", "replace").rstrip() for r in range(2)]
    m1 = STRIP_ROW1.fullmatch(rows[1])
    if not STRIP_ROW0.fullmatch(rows[0]) or not m1 or not MODE_FIELD.fullmatch(m1.group(1)):
        problems.append("%s: the strip is not GLASS.md's template with a legal mode word: %r" % (label, rows))
    if not secrets:
        return problems
    for name in ("conversation", "app"):
        C, R = obs[name]["cols"], obs[name]["rows"]
        cells = reads[name]
        for r in range(R):
            row = cells[r * C:(r + 1) * C].decode("ascii", "replace").rstrip()
            if name == "conversation" and (row in allowed or row.startswith(CONSOLE_LOG) or COUNTS_ROW.fullmatch(row)):
                continue
            if row.startswith(trials2.NOTE_PREFIX):
                problems.append("%s: the %s shows a trial-two note: %r" % (label, name, row))
            leak = sorted(set(re.findall(r"(?<![0-9])[1-9][0-9]*", row)) & secrets)
            if leak:
                problems.append("%s: the %s's row %r shows %s, a trial-two time or score" % (label, name, row, leak))
    return problems


def rows_of(reads, name):
    """A surface's non-blank rows, as text."""
    C, R = reads["obs"][name]["cols"], reads["obs"][name]["rows"]
    cells = reads[name]
    rows = [cells[r * C:(r + 1) * C].decode("ascii", "replace").rstrip() for r in range(R)]
    return [r for r in rows if r]


def tail_upto(rows, last, n):
    """The n rows ending at the last row equal to last (the prompt may follow it)."""
    idx = [i for i, r in enumerate(rows) if r == last]
    return rows[idx[-1] - n + 1:idx[-1] + 1] if idx else rows[-n:]


def append_notes(disk, more):
    """Notes appended from the host after the disk's last note, by the notebook's record."""
    notes = notes_on_disk(disk)
    data = bytearray(checkdisk.read_image(disk))
    first, sectors = metal.parse_gpt(bytes(data))["notes"]
    lo, hi = first * metal.SECTOR, (first + sectors) * metal.SECTOR
    data[lo:hi] = write_notes(bytes(data[lo:hi]), notes + more)
    with open(disk, "wb") as fh:
        fh.write(bytes(data))


def parts_disk(disk):
    """stage8/parts.py --disk with its note count masked: the molt table, the home store
    and the door must not change when trial two's notes are added."""
    return re.sub(r"notes \d+;", "notes N;", run_tool([os.path.join(REPO, "stage8", "parts.py"), "--disk", disk])[1])


def secrets_of(notes):
    out = set()
    for p in map(trials2.parse_note, notes):
        if p and p["kind"] == "hit":
            out.add(str(p["ms"]))
        elif p and p["kind"] == "block":
            out.add(str(p["score"]))
    return out


def fresh_formatted(name):
    """A fresh 64 MB disk booted blank once (nineteen lines): the guest's own table, notebook and home."""
    disk = os.path.join(T8, "disk.%s.img" % name)
    checkmetal.fresh_disk(disk)
    with Boot(name + "0", disk) as b:
        if b.err:
            return None, [b.err]
        cap = b.serial()
    _, stripped = checkmetal.strip_mouse_line(cap)
    problems, _ = checkmetal.check_boot_lines(stripped, SMP, True, "formatted", 0, checkmetal.DISK_SECTORS)
    if notes_on_disk(disk):
        problems.append("the blank boot left notes")
    return disk, ["disk %s's blank boot: %s" % (name, p) for p in problems]


def boot_lines(capture, notes_n, home_n, part_live=False):
    """The eighteen S7: lines of a recognising boot; with a live part its part: pair stands
    where the i8042: pair would, so the pair is checked by name and the lines by 7c's rule."""
    _, stripped = checkmetal.strip_mouse_line(capture)
    if part_live:
        want = [b"part: i8042 self-test ok", b"part: i8042 mouse reset ok"]
        problems = [] if all(w in stripped for w in want) else ["the part's pair %r is not on serial" % want]
        stripped = stripped.replace(b"part: i8042 ", b"i8042: ")
    else:
        problems = []
    more, _ = checkmetal.check_boot_lines(stripped, SMP, False, "%d notes" % notes_n, home_n, checkmetal.DISK_SECTORS)
    return problems + more


def s8_lines(capture):
    return [x.decode() for x in re.findall(rb"(?:S8|molt): [^\r\n]*", capture)]


# ----------------------------------------------- test 2: the rows ---------

def _const_blocks(g_ms, b_ms, sitting, misses=()):
    out = []
    for b in range(1, trials2.BLOCKS + 1):
        base = g_ms if trials2.layout(sitting, b) == "G" else b_ms
        out.append({"ms": [base + (c * 37) % 60 for c in range(trials2.CUES_PER_BLOCK)],
                    "miss": [c for (bb, c) in misses if bb == b]})
    return out


SCRIPT_R1 = {"sitting": 1, "warmup": {"ms": [300 + (c * 37) % 60 for c in range(10)], "miss": []},
             "blocks": _const_blocks(320, 260, 1), "abort": (2, 3), "prefer": None}


def rows_r1():
    """R1: a blank disk; no boot line and no offer; '! trial 2' opens sitting 1 with the
    warm-up's G row, then its B row; block 1; Esc in block 2; the saved line; the refusals."""
    disk = os.path.join(T8, "disk.R.img")
    checkmetal.fresh_disk(disk)
    results, reads = {}, {}
    with Boot("R1", disk) as b:
        if b.err:
            return report("R1", [b.err])
        reads["boot"] = b.surfaces()

        def at_start():
            b.park()
            reads["start"] = b.surfaces()
            reads["start_shot"] = b.shot("start")

        def at_b_row():
            deadline = time.time() + 3.0          # cue 6 shows at the pause's end
            while time.time() < deadline:
                obs = b.page()
                if obs["trial_cue"] == 6 and obs["cue_pending"] == 0:
                    break
                time.sleep(0.05)
            b.park()
            reads["wb"] = b.surfaces()
            reads["wb_shot"] = b.shot("wb")

        err = b.play(SCRIPT_R1, results, "type", {"start": at_start, (0, 6): at_b_row})
        if err:
            return report("R1", [err], b.serial())
        for line in ("! trial 2\n", "\n", "trial2 x\n", "trial\n", "trial3 y\n", "trials are fun\n"):
            b.type(line)
            time.sleep(1.0)
        reads["after"] = b.surfaces()
        cap = b.serial()
        geometry = b.geometry
    problems = boot_lines_blank(cap)
    notes_serial, stripped = serial_notes(cap)
    want_echo = b"! trial 2\r\n! trial 2\r\n\r\ntrial2 x\r\ntrial\r\ntrial3 y\r\ntrials are fun\r\n"
    problems += checkdisk.check_echo(stripped, want_echo)
    if boot_line_of(cap):
        problems.append("a boot line on a disk with no trial-two note: %r" % boot_line_of(cap))
    boot_rows = checktrials.conv_rows(reads["boot"]["conversation"], reads["boot"]["obs"])
    if any("press Enter to start" in r for r in boot_rows):
        problems.append("an offer on a disk with no trial-two note: %r" % boot_rows)
    ok = report("R1's boot is not the eighteen-line machine with no trial-two line", problems, cap)

    problems = []
    st = reads["start"]
    if results.get("order") != trials2.order(1):
        problems.append("the sitting's order is %r" % results.get("order"))
    problems += check_mode_field(reads["start_shot"], geometry, "trial2 G 0/8")
    problems += check_layout_g(reads["start_shot"], st, geometry, trials2.ROW_ITEMS, "the warm-up's G row")
    got_g = g_columns_of(st["choices"], geometry[2])
    if isinstance(G_ROWS_RUN[4], _Unset) or tuple(G_ROWS_RUN[4]) != got_g:
        problems.append("the four-item G row reads %r; the run constant is %r" % (got_g, G_ROWS_RUN[4]))
    problems += checktrials.check_conv_tail(st["conversation"], st["obs"],
                                            ["> ! trial 2", "sitting 1 " + trials2.order(1), "click: " + trials2.WARMUP.split()[0]],
                                            "the sitting's start")
    problems += check_counts(st["obs"], {"mode": trials2.MODE_TRIAL, "trial_number": 2, "trial_sitting": 1, "trial_block": 0,
                                         "trial_layout": 2, "trial_cue": 1,
                                         "trial_target": trials2.ITEMS.index(trials2.WARMUP.split()[0]),
                                         "cue_pending": 0, "layout_default": 0, "zero_8t": [0, 0, 0]}, "the sitting's start")
    wb = reads["wb"]
    problems += check_mode_field(reads["wb_shot"], geometry, "trial2 B 0/8")
    problems += checktrials.check_layout_b(reads["wb_shot"], wb, geometry, trials2.ROW_ITEMS, "the warm-up's B row")
    problems += check_counts(wb["obs"], {"trial_block": 0, "trial_layout": 1, "trial_cue": 6,
                                         "trial_target": trials2.ITEMS.index(trials2.WARMUP.split()[5])}, "the warm-up's cue 6")
    ok &= report("the sitting's start or the warm-up's rows are not what TRIALS2.md says", problems)
    if not problems:
        say("R1: '! trial 2' opened 'sitting 1 GBBG BGGB' with 'trial2 G 0/8' on the strip, the warm-up's G row to the pixel "
            "(labels %r, '|' at %r), its B row at cue 6 as trial one's boxes, the page in mode 5 with trial_number 2" % got_g)

    problems = compare_notes(notes_serial[:len(trials2.notes_of(SCRIPT_R1))], SCRIPT_R1, "R1's notes on serial",
                             untimed={(0, 1), (0, 6)})    # the screen read at those cues holds their press
    on_disk = notes_on_disk(disk)
    want_disk = notes_serial[:len(trials2.notes_of(SCRIPT_R1))] + ["trials are fun"]
    if on_disk != want_disk:
        problems.append("the notebook holds %d notes, want the %d on serial and 'trials are fun'" % (len(on_disk), len(want_disk) - 1))
    if results.get("aborted") != 2:
        problems.append("the abort named block %r, want 2" % results.get("aborted"))
    tail = trials2.end_lines(on_disk, 1)
    if tail_upto(results.get("saved_rows", []), trials2.SAVED, len(tail)) != tail:
        problems.append("the conversation at the abort ends %r, want %r"
                        % (tail_upto(results.get("saved_rows", []), trials2.SAVED, len(tail)), tail))
    after = reads["after"]
    rows = checktrials.conv_rows(after["conversation"], after["obs"])
    want_rows = ["> ! trial 2", "one sitting a boot", ">", "one sitting a boot", "> trial2 x", trials2.RESERVED,
                 "> trial", trials2.RESERVED, "> trial3 y", trials2.RESERVED, "> trials are fun", ">"]
    if rows[-len(want_rows):] != want_rows:
        problems.append("the refusals: the conversation ends %r, want %r" % (rows[-len(want_rows):], want_rows))
    problems += check_counts(after["obs"], {"mode": 0, "errors": 5, "trial_number": 2, "notes": len(want_disk)}, "the refusals")
    ok &= report("R1's sitting, its abort or the refusals are not what TRIALS2.md says", problems)
    if not problems:
        say("R1: the warm-up and block 1 journaled as scripted, Esc in block 2 journaled 'aborted 2' and ended in %r; "
            "'! trial 2' and an empty Enter each refused 'one sitting a boot'; 'trial2 x', 'trial', 'trial3 y' refused "
            "'trial is reserved'; 'trials are fun' journaled" % trials2.SAVED)
    return ok


def boot_lines_blank(capture):
    _, stripped = checkmetal.strip_mouse_line(capture)
    problems, _ = checkmetal.check_boot_lines(stripped, SMP, True, "formatted", 0, checkmetal.DISK_SECTORS)
    return problems


def rows_c():
    """C: trial two concluded (worked example D's notes, verdict G): the boot line, no
    offer, the prompt row in G, '! trial 2' refused, an empty Enter plain, the G click."""
    disk, problems = fresh_formatted("C")
    if disk is None or problems:
        return report("disk C", problems)
    notes = trials2.DOCUMENT["d_notes"]
    write_disk(disk, notes, [])
    with Boot("C1", disk) as b:
        if b.err:
            return report("C1", [b.err])
        b.park()
        reads = {"boot": b.surfaces(), "boot_shot": b.shot("boot")}
        b.type("! trial 2\n")
        time.sleep(1.0)
        b.type("\n")
        time.sleep(1.0)
        reads["refused"] = b.surfaces()
        z = trials2.zones(b.geometry[2], 2)
        b.moveto(b.crow + 1, (z[1][2] + z[1][3]) // 2)
        b.press()
        time.sleep(0.8)
        reads["grow"] = b.surfaces()
        b.moveto(b.crow, z[0][1])
        b.press()
        time.sleep(0.8)
        reads["sep"] = b.surfaces()
        cap = b.serial()
        geometry = b.geometry
    problems = boot_lines(cap, len(notes), 0)
    if boot_line_of(cap) != ["trial2: concluded verdict G default G"]:
        problems.append("the boot line is %r" % boot_line_of(cap))
    rows = checktrials.conv_rows(reads["boot"]["conversation"], reads["boot"]["obs"])
    if any("press Enter to start" in r or r.startswith(trials2.NOTE_PREFIX) for r in rows):
        problems.append("an offer or a replayed trial-two note after the verdict: %r" % rows)
    problems += check_counts(reads["boot"]["obs"], {"mode": 0, "layout_default": 2, "trial_number": 0, "notes": len(notes)},
                             "C1's boot")
    problems += check_layout_g(reads["boot_shot"], reads["boot"], geometry, ["? ask", "! grow"], "the prompt row in G")
    got_g = g_columns_of(reads["boot"]["choices"], geometry[2])
    if isinstance(G_ROWS_RUN[2], _Unset) or tuple(G_ROWS_RUN[2]) != got_g:
        problems.append("the two-item G row reads %r; the run constant is %r" % (got_g, G_ROWS_RUN[2]))
    rows = checktrials.conv_rows(reads["refused"]["conversation"], reads["refused"]["obs"])
    if rows[-4:] != ["> ! trial 2", "trial 2 concluded", ">", ">"]:
        problems.append("'! trial 2' then an empty Enter: the conversation ends %r" % rows[-4:])
    problems += check_counts(reads["refused"]["obs"], {"errors": 1}, "the refusal")
    problems += check_counts(reads["grow"]["obs"], {"hits": 1}, "a click on '! grow' in G")
    rows = checktrials.conv_rows(reads["grow"]["conversation"], reads["grow"]["obs"])
    if rows[-1:] != ["> !"]:
        problems.append("a click on '! grow' in G: the prompt is %r, want '> !'" % rows[-1:])
    problems += check_counts(reads["sep"]["obs"], {"hits": 1, "clicks": reads["grow"]["obs"]["clicks"] + 1}, "a click on '|'")
    ok = report("disk C (trial two concluded, verdict G) is not what TRIALS2.md says", problems, cap)
    if ok:
        say("C: 'trial2: concluded verdict G default G', no offer, no trial-two note replayed, layout_default 2 and the "
            "prompt row in G (labels %r, '|' at %r); '! trial 2' refused 'trial 2 concluded', an empty Enter plain; a click on "
            "'! grow' typed '!', a click on '|' only counted" % got_g)
    return ok


def part_disk(name, live):
    disk, problems = fresh_formatted(name)
    if disk is None or problems:
        return None, None, problems
    notes = trials2.DOCUMENT["a_notes"] + ["molt i8042 shadow 4fe6beefc4bc57d0 3 1000 5000"]
    if live:
        notes = notes + ["molt i8042 live 4fe6beefc4bc57d0"]
    write_disk(disk, notes, [("calculator", open(CALCULATOR, "rb").read(), None), ("part-i8042", fixture("good"), None)])
    return disk, notes, []


def rows_s():
    """S: good in shadow, a trial-two sitting done, the calculator: the offer; with the app
    running '! trial 2' and an empty Enter give 'an app is running'; after Esc, the part refusal."""
    disk, notes, problems = part_disk("S", False)
    if disk is None:
        return report("disk S", problems)
    with Boot("S1", disk) as b:
        if b.err:
            return report("S1", [b.err])
        reads = {"boot": b.surfaces()}
        steps = [("! calculator\n", 2.0), ("\t", 1.0), ("! trial 2\n", 1.0), ("\n", 1.0)]
        for text, wait in steps:
            b.type(text)
            time.sleep(wait)
        reads["app"] = b.surfaces()
        for text, wait in (("\x1b", 1.5), ("! trial 2\n", 1.0), ("\n", 1.0)):
            b.type(text)
            time.sleep(wait)
        reads["part"] = b.surfaces()
        cap = b.serial()
    problems = boot_lines(cap, len(notes), 1)
    want8 = ["S8: sha256 ok", "S8: part i8042 shadow 4fe6beefc4bc57d0", "molt: boot 1 i8042 shadow", "S8: watchdog tco 30 s"]
    if s8_lines(cap)[:4] != want8:
        problems.append("the S8: and molt: lines are %r, want %r first" % (s8_lines(cap), want8))
    if boot_line_of(cap) != ["trial2: due sitting 2"]:
        problems.append("the boot line is %r" % boot_line_of(cap))
    rows = checktrials.conv_rows(reads["boot"]["conversation"], reads["boot"]["obs"])
    if trials2.OFFER % 2 not in rows:
        problems.append("no offer at the boot: %r" % rows[-4:])
    rows = checktrials.conv_rows(reads["app"]["conversation"], reads["app"]["obs"])
    if rows[-5:] != ["> ! trial 2", "an app is running", ">", "an app is running", ">"] or reads["app"]["obs"]["mode"] != 3:
        problems.append("with the app running: the conversation ends %r, mode %r" % (rows[-5:], reads["app"]["obs"]["mode"]))
    rows = checktrials.conv_rows(reads["part"]["conversation"], reads["part"]["obs"])
    part_line = trials2.REFUSALS[4]
    if rows[-5:] != ["> ! trial 2", part_line, ">", part_line, ">"]:
        problems.append("with the app closed: the conversation ends %r" % rows[-5:])
    problems += check_counts(reads["part"]["obs"], {"mode": 0, "errors": 4, "trial_number": 0}, "disk S")
    if notes_on_disk(disk)[:len(notes)] != notes or trials2.sittings_of(notes_on_disk(disk))[-1:] != trials2.sittings_of(notes):
        problems.append("disk S: a note was changed, or a trial-two note journaled")
    ok = report("disk S (good in shadow) is not what TRIALS2.md says", problems, cap)
    if ok:
        say("S: good in shadow and the watchdog armed; 'trial2: due sitting 2' and the offer; with the calculator running "
            "'! trial 2' and an empty Enter each 'an app is running'; with it closed each %r" % part_line)
    return ok


def rows_l():
    """L: good live: the part's pair; '! trial 2' and an empty Enter give the part refusal."""
    disk, notes, problems = part_disk("L", True)
    if disk is None:
        return report("disk L", problems)
    with Boot("L1", disk) as b:
        if b.err:
            return report("L1", [b.err])
        for text in ("! trial 2\n", "\n"):
            b.type(text)
            time.sleep(1.0)
        reads = b.surfaces()
        cap = b.serial()
    problems = boot_lines(cap, len(notes), 1, part_live=True)
    want8 = ["S8: sha256 ok", "S8: part i8042 live 4fe6beefc4bc57d0", "molt: boot 1 i8042 live", "S8: watchdog tco 30 s"]
    if s8_lines(cap)[:4] != want8:
        problems.append("the S8: and molt: lines are %r, want %r first" % (s8_lines(cap), want8))
    rows = checktrials.conv_rows(reads["conversation"], reads["obs"])
    part_line = trials2.REFUSALS[4]
    if rows[-5:] != ["> ! trial 2", part_line, ">", part_line, ">"]:
        problems.append("the conversation ends %r" % rows[-5:])
    problems += check_counts(reads["obs"], {"mode": 0, "errors": 2, "trial_number": 0}, "disk L")
    ok = report("disk L (good live) is not what TRIALS2.md says", problems, cap)
    if ok:
        say("L: good live with its part: pair; '! trial 2' and an empty Enter each %r" % part_line)
    return ok


def run_rows():
    if not require(["READY_LIMIT_S", "SETTLE_S", "OFFSET_MS", "OFFSET_FIRST_MS", "HIT_WINDOW_MS"]):
        return 1
    problems = check_script_range(SCRIPT_R1)
    if not report("the rows' script", problems):
        return 1
    ok = True
    for part in (rows_r1, rows_c, rows_s, rows_l):
        t0 = time.time()
        ok &= bool(part())
        say("(%s: %.1f s)" % (part.__name__, time.time() - t0))
    return 0 if ok else 1


# ------------------------------------------- test 3: the sittings ---------
# Disk V, blank: four sittings played to a scripted verdict B, sitting 1
# typed and sittings 2-4 started by Enter at the offer, then the boot after
# the verdict. Disk H, the HP's history (D3): sitting 1 played on it; the
# host then appends sittings 2 and 3 and it is disk W: sitting 4 aborted,
# sitting 5 played to a scripted verdict G over sittings 1, 2, 3 and 5, then
# the boot after the verdict with a full trial on the disk.

def _script(sitting, g_ms, b_ms, misses=(), wmiss=(), prefer="b", abort=None):
    blocks = []
    for b in range(1, trials2.BLOCKS + 1):
        base = g_ms if trials2.layout(sitting, b) == "G" else b_ms
        blocks.append({"ms": [base + (c * 37 + b * 11) % 60 - 30 for c in range(trials2.CUES_PER_BLOCK)],
                       "miss": [c for (bb, c) in misses if bb == b]})
    warm = {"ms": [300 + (c * 37) % 60 - 30 for c in range(trials2.WARMUP_CUES)], "miss": list(wmiss)}
    return {"sitting": sitting, "warmup": warm, "blocks": blocks, "abort": abort, "prefer": prefer}


# V: B faster by about 130 ms a cue - the verdict B whatever the pointer's own slack.
SCRIPTS_V = [_script(1, 360, 230, misses=[(1, 7), (3, 12)], wmiss=[4], prefer="b"),
             _script(2, 360, 230, misses=[(2, 5)], prefer="n"),
             _script(3, 360, 230, prefer="g"),
             _script(4, 360, 230, misses=[(8, 16)], prefer="b")]
# H and W: G faster by about 130 ms a cue - the verdict G.
SCRIPT_H1 = _script(1, 230, 360, misses=[(2, 9)], prefer="g")
SCRIPTS_W_HOST = [_script(2, 270, 400, prefer="n"), _script(3, 270, 400, misses=[(5, 3)], prefer="g")]   # written as recorded
SCRIPT_W4 = _script(4, 230, 360, prefer=None, abort=(3, 4))
SCRIPT_W5 = _script(5, 230, 360, misses=[(6, 2)], prefer="g")
ROW_HP = ["? ask", "! grow", "! calculator"]


class Sittings:
    def __init__(self):
        self.ok = True
        self.captures = {}

    def fail(self, problems, title, capture=None):
        if problems:
            self.ok = False
        return report(title, problems, capture)

    def play_boot(self, name, disk, script, start, full=False, verdict=False, at_boot=None, after=None):
        """One boot playing one sitting, with the save rule and A2 checked at the question and at
        saved, the page at every rest, and the notes compared with the script afterwards."""
        before_notes = notes_on_disk(disk)
        s = script["sitting"]
        results, reads, problems = {}, {}, []
        t0 = time.time()
        with Boot(name, disk, full=full) as b:
            if b.err:
                return self.fail([b.err], name), None
            allowed = replay_rows(before_notes, b.regs["conversation"][3])
            secrets = secrets_of(before_notes)
            reads["boot"] = b.surfaces()
            if at_boot:
                problems += at_boot(b, reads["boot"])
            if not trials2.concluded(before_notes):
                problems += hidden_times(reads["boot"], secrets, allowed, "%s's boot" % name)

            def at_rest(blk):
                try:
                    obs = b.page()
                    want = {"mode": trials2.MODE_TRIAL, "trial_number": 2, "trial_sitting": s, "trial_block": blk,
                            "trial_cue": 0, "zero_8t": [0, 0, 0]}
                    problems.extend(check_counts(obs, want, "%s at the rest after block %d" % (name, blk)))
                    if blk in (0, 4):
                        rd = b.surfaces()
                        problems.extend(hidden_times(rd, secrets | secrets_of(notes_on_disk(disk)), allowed,
                                                     "%s at the rest after block %d" % (name, blk)))
                except ValueError as exc:
                    problems.append("%s: the page at the rest after block %d: %s" % (name, blk, exc))

            def at_question():
                on = notes_on_disk(disk)
                if not any(t == "trial2 sitting %d done" % s for t in on):
                    problems.append("%s: at the question the done note is not on the disk" % name)
                if any((trials2.parse_note(t) or {}).get("kind") == "prefer" and t.split()[2] == str(s) for t in on):
                    problems.append("%s: a prefer note is on the disk before the key" % name)
                if trials2.SAVED in results["question_rows"]:
                    problems.append("%s: the saved line shows before the key" % name)
                if verdict and not trials2.concluded(on):
                    problems.append("%s: the fourth done sitting's verdict note is not on the disk at the question" % name)
                if not verdict:
                    problems.extend(hidden_times(results["question_reads"], secrets_of(on), allowed, "%s at the question" % name))
                reads["question"] = results["question_reads"]

            def at_saved():
                on = notes_on_disk(disk)
                reads["saved_notes"] = on
                if script.get("prefer") and "trial2 prefer %d %s" % (s, script["prefer"]) not in on:
                    problems.append("%s: the saved line shows and the prefer note is not on the disk" % name)
                if not verdict:
                    problems.extend(hidden_times(results["saved_reads"], secrets_of(on), allowed, "%s at saved" % name))

            err = b.play(script, results, start, {"rest": at_rest, "question": at_question, "saved": at_saved},
                         prefer_verdict=verdict)
            if err:
                return self.fail(problems + [err], name, b.serial()), None
            if after:
                problems += after(b)
            cap = b.serial()
        wall = time.time() - t0
        self.captures[name] = cap
        new = notes_on_disk(disk)
        if new[:len(before_notes)] != before_notes:
            problems.append("%s: a note written before the boot changed" % name)
        added = new[len(before_notes):]
        judged = [t for t in added if (trials2.parse_note(t) or {}).get("kind") != "verdict"]
        problems += compare_notes(judged, script, "%s's notes" % name)
        notes_serial, _ = serial_notes(cap)
        if notes_serial != added:
            problems.append("%s: the trial2: lines on serial are not the notes journaled (%d lines, %d notes)"
                            % (name, len(notes_serial), len(added)))
        if cap.count(b"S7: alive") != 1:
            problems.append("%s: %d 'S7: alive' lines in one boot - a reset" % (name, cap.count(b"S7: alive")))
        if wall > SITTING_S:
            problems.append("%s: the sitting's boot took %.0f s, more than SITTING_S %.0f s" % (name, wall, SITTING_S))
        tail = trials2.end_lines(new, s)
        rows = results.get("saved_rows", [])
        if (script.get("prefer") is not None or script.get("abort")) and tail_upto(rows, trials2.SAVED, len(tail)) != tail:
            problems.append("%s: the conversation at saved ends %r, want %r" % (name, tail_upto(rows, trials2.SAVED, len(tail)), tail))
        if not verdict and "saved_reads" in results:
            app = rows_of(results["saved_reads"], "app")
            if app:
                problems.append("%s: the app panel shows %r before the verdict" % (name, app[:3]))
        say("(%s: sitting %d, %d notes journaled, %.1f s)" % (name, s, len(added), wall))
        return problems, (results, reads, cap, new)

    def check_verdict(self, name, notes, results, reads, predicted, layout):
        problems = []
        v = trials2.verdict_detail(notes)
        note = [t for t in notes if (trials2.parse_note(t) or {}).get("kind") == "verdict"]
        if v is None or note != [trials2.verdict_note(notes)]:
            problems.append("%s: the verdict note %r is not the rule's %r" % (name, note, trials2.verdict_note(notes)))
        elif trials2.verdict_of(notes) != layout:
            problems.append("%s: the verdict is %s, the script gives %s" % (name, trials2.verdict_of(notes), layout))
        elif abs(v[3] - predicted[3]) > SLACK_MS:
            problems.append("%s: the mean is %d, the script gives %d +/- %d" % (name, v[3], predicted[3], SLACK_MS))
        if results.get("verdict") != (trials2.verdict_of(notes), v[3] if v else None):
            problems.append("%s: the verdict line on serial is %r" % (name, results.get("verdict")))
        rd = results.get("saved_reads")
        if rd:
            app = rows_of(rd, "app")
            if app != trials2.verdict_panel(notes):
                problems.append("%s: the app panel at the verdict is %r, want %r" % (name, app[:4], trials2.verdict_panel(notes)[:4]))
            want_default = trials2.LAYOUT_VALUE[layout]
            problems += check_counts(rd["obs"], {"layout_default": want_default}, "%s at saved" % name)
        return problems

    def boot_after(self, name, disk, layout, labels, full=False):
        """The boot after the verdict: the concluded line, no offer, the default read at boot,
        the prompt row drawn in it, an empty Enter plain, '! trial 2' refused, a click."""
        notes = notes_on_disk(disk)
        with Boot(name, disk, full=full) as b:
            if b.err:
                return [b.err], None, None
            ready_s = b.ready_s
            b.park()
            rd = b.surfaces()
            shot = b.shot("prompt")
            b.type("\n")
            time.sleep(1.0)
            b.type("! trial 2\n")
            time.sleep(1.0)
            rd2 = b.surfaces()
            z = trials2.zones(b.geometry[2], len(labels))
            b.moveto(b.crow + 1, (z[1][2] + z[1][3]) // 2)
            b.press()
            time.sleep(0.8)
            rd3 = b.surfaces()
            b.moveto(b.crow, z[0][1])
            b.press()
            time.sleep(0.8)
            rd4 = b.surfaces()
            cap = b.serial()
            geometry = b.geometry
        problems = []
        want_line = "trial2: concluded verdict %s default %s" % (layout, layout)
        if boot_line_of(cap) != [want_line]:
            problems.append("%s: the boot line is %r, want %r" % (name, boot_line_of(cap), want_line))
        rows = checktrials.conv_rows(rd["conversation"], rd["obs"])
        if any("press Enter to start" in r for r in rows):
            problems.append("%s: an offer after the verdict" % name)
        problems += check_counts(rd["obs"], {"mode": 0, "layout_default": trials2.LAYOUT_VALUE[layout], "trial_number": 0,
                                             "notes": len(notes)}, "%s's boot" % name)
        if layout == "B":
            problems += checktrials.check_layout_b(shot, rd, geometry, labels, "%s's prompt row" % name)
        else:
            problems += check_layout_g(shot, rd, geometry, labels, "%s's prompt row" % name)
        rows = checktrials.conv_rows(rd2["conversation"], rd2["obs"])
        if rows[-4:] != [">", "> ! trial 2", "trial 2 concluded", ">"]:
            problems.append("%s: an empty Enter then '! trial 2': the conversation ends %r" % (name, rows[-4:]))
        problems += check_counts(rd2["obs"], {"errors": 1}, "%s: the refusal" % name)
        problems += check_counts(rd3["obs"], {"hits": 1}, "%s: a click on '! grow'" % name)
        if checktrials.conv_rows(rd3["conversation"], rd3["obs"])[-1:] != ["> !"]:
            problems.append("%s: a click on '! grow' did not type '!'" % name)
        problems += check_counts(rd4["obs"], {"hits": 1, "clicks": rd3["obs"]["clicks"] + 1}, "%s: a click on the gap" % name)
        return problems, cap, (rd, geometry, ready_s)

    # -- disk V ------------------------------------------------------------
    def disk_v(self):
        disk, problems = fresh_formatted("V")
        if disk is None or problems:
            return self.fail(problems, "disk V")
        predicted = trials2.verdict_detail(trials2.journal_of([expected_script(s) for s in SCRIPTS_V]))
        for i, script in enumerate(SCRIPTS_V, 1):
            name = "V%d" % i
            start = "type" if i == 1 else "enter"

            def at_boot(b, rd, i=i):
                p = []
                cap = b.serial()
                if i == 1:
                    if boot_line_of(cap):
                        p.append("V1: a boot line on a blank disk")
                else:
                    if boot_line_of(cap) != [trials2.DUE_LINE % i]:
                        p.append("%s: the boot line is %r, want %r" % ("V%d" % i, boot_line_of(cap), trials2.DUE_LINE % i))
                    rows = checktrials.conv_rows(rd["conversation"], rd["obs"])
                    if trials2.OFFER % i not in rows:
                        p.append("V%d: no offer %r in the conversation: %r" % (i, trials2.OFFER % i, rows[-3:]))
                    if any(r.startswith(trials2.NOTE_PREFIX) for r in rows):
                        p.append("V%d: the replay drew a trial-two note" % i)
                return p

            problems, got = self.play_boot(name, disk, script, start, verdict=(i == 4), at_boot=at_boot)
            if got is None:
                return False
            results, reads, cap, notes = got
            if i == 4:
                problems += self.check_verdict(name, notes, results, reads, predicted, "B")
            if not self.fail(problems, "%s: sitting %d is not what TRIALS2.md and the script say" % (name, i), cap):
                continue
            say("%s: sitting %d %s, started by %s; its notes as scripted, the save rule held, no time or score shown%s"
                % (name, i, trials2.order(i), "'! trial 2'" if i == 1 else "Enter at the offer",
                   "; verdict %s %d over sittings 1-4" % results.get("verdict", ("?", 0)) if i == 4 else ""))
        problems, cap, extra = self.boot_after("V5", disk, "B", ["? ask", "! grow"])
        notes = notes_on_disk(disk)
        rc, out = run_tool([os.path.join(HERE, "trials2.py"), "--disk", disk])
        if rc != 0 or "\n".join(trials2.verdict_panel(notes)[:11]) not in out:
            problems.append("trials2.py --disk on disk V: exit %d, %r" % (rc, out[-200:]))
        chart = os.path.join(T8, "chart.V1-3.log")
        with open(chart, "wb") as fh:
            for n in ("V1", "V2", "V3"):
                fh.write(self.captures.get(n, b""))
        rc, out = run_tool([os.path.join(HERE, "trials2.py"), "--status", chart])
        leak = sorted(set(re.findall(r"(?<![0-9])[1-9][0-9]*", out)) & secrets_of(notes))
        if rc != 0 or leak or out.count("preference saved") != 3:
            problems.append("trials2.py --status on V1-V3's charts: exit %d, shows %r, %r" % (rc, leak, out[-300:]))
        with open(chart, "ab") as fh:
            fh.write(self.captures.get("V4", b"") + (cap or b""))
        rc, out = run_tool([os.path.join(HERE, "trials2.py"), "--status", chart])
        if "verdict line present" not in out or "verdict B:" not in out:
            problems.append("trials2.py --status after the verdict: %r" % out[-300:])
        if self.fail(problems, "V5: the boot after verdict B is not what TRIALS2.md says", cap):
            say("V5: 'trial2: concluded verdict B default B', no offer, layout_default 1 and the prompt row in B; an empty "
                "Enter plain, '! trial 2' refused; trials2.py --disk the panel's tables; --status on V1-V3 blind")
        return True

    # -- disk H, then W ------------------------------------------------------
    def disk_h(self):
        disk, problems = fresh_formatted("H")
        if disk is None or problems:
            return self.fail(problems, "disk H")
        history, _ = hp_history()
        write_disk(disk, history, hp_home())
        charts = os.path.join(T8, "trial-one-charts.log")
        with open(charts, "wb") as fh:
            for n, sha in CHARTS_7D:
                fh.write(chart_stream(n, sha))
        t1_before = run_tool([os.path.join(REPO, "stage7", "trials.py"), "--serial", charts])[1]
        parts_before = parts_disk(disk)

        def h_boot(b, rd):
            p = []
            cap = b.serial()
            p += boot_lines(cap, len(history), 1)
            if s8_lines(cap) != ["S8: sha256 ok"]:
                p.append("H1: the S8: and molt: lines are %r, want only 'S8: sha256 ok' (no part, no watchdog)" % s8_lines(cap))
            if boot_line_of(cap):
                p.append("H1: a boot line with no trial-two note: %r" % boot_line_of(cap))
            rows = checktrials.conv_rows(rd["conversation"], rd["obs"])
            if any("press Enter to start" in r or "hold Esc" in r for r in rows):
                p.append("H1: an offer or the Esc window on the HP's disk: %r" % rows[-3:])
            p += check_counts(rd["obs"], {"layout_default": 0, "trial_number": 0, "notes": len(history)}, "H1's boot")
            b.park()
            shot = b.shot("prompt")
            p += check_choices(shot, b.geometry, "   ".join(ROW_HP))
            b.type("! molt\n")
            time.sleep(1.0)
            app = rows_of(b.surfaces(), "app")
            if app != ["i8042 demoted f0668b687c68cab0 unhealthy"]:
                p.append("H1: '! molt' shows %r" % app)
            b.type("! trial\n")
            time.sleep(1.0)
            rows, _ = b.conv()
            if rows[-2:] != ["trial concluded", ">"]:
                p.append("H1: '! trial' ends %r, want trial one's 'trial concluded'" % rows[-2:])
            return p

        problems, got = self.play_boot("H1", disk, SCRIPT_H1, "type", full=True, at_boot=h_boot)
        if got is None:
            return False
        results, reads, cap, notes = got
        t1_disk = run_tool([os.path.join(REPO, "stage7", "trials.py"), "--disk", disk])[1]
        if t1_disk != t1_before or "verdict A:" not in t1_disk:
            problems.append("H1: the frozen stage7/trials.py --disk changed after a trial-two sitting: %r" % t1_disk[-200:])
        if parts_disk(disk) != parts_before:
            problems.append("H1: stage8/parts.py --disk changed after a trial-two sitting")
        if self.fail(problems, "H1: the HP's disk and its first trial-two sitting are not what the documents say", cap):
            say("H1: the HP's history, 355 notes: 'S8: sha256 ok' alone, no part loaded, no watchdog and no reset through the "
                "sitting; '! molt' shows the demoted part, '! trial' 'trial concluded', '! trial 2' opened sitting 1; the "
                "frozen stage7/trials.py and parts.py print the same after it")

        # W: the host appends sittings 2 and 3 as recorded
        more = []
        for sc in SCRIPTS_W_HOST:
            more += trials2.notes_of(sc)
        append_notes(disk, more)
        say("W: sittings 2 and 3 appended from the host, %d notes" % len(more))

        def due(n):
            def at_boot(b, rd):
                p = []
                if boot_line_of(b.serial()) != [trials2.DUE_LINE % n]:
                    p.append("W: the boot line is %r, want %r" % (boot_line_of(b.serial()), trials2.DUE_LINE % n))
                rows = checktrials.conv_rows(rd["conversation"], rd["obs"])
                if trials2.OFFER % n not in rows:
                    p.append("W: no offer %r" % (trials2.OFFER % n))
                return p
            return at_boot

        def enter_refused(b):
            b.type("\n")
            time.sleep(1.0)
            rows, rd = b.conv()
            p = [] if rows[-2:] == ["one sitting a boot", ">"] else ["W1: an empty Enter after the abort ends %r" % rows[-2:]]
            return p

        problems, got = self.play_boot("W1", disk, SCRIPT_W4, "enter", full=True, at_boot=due(4), after=enter_refused)
        if got is None:
            return False
        if got[0].get("aborted") != 3:
            problems.append("W1: the abort named block %r, want 3" % got[0].get("aborted"))
        if self.fail(problems, "W1: sitting 4, aborted, is not what TRIALS2.md says", got[2]):
            say("W1: 'trial2: due sitting 4' and the offer, Enter started it, Esc in block 3 journaled 'aborted 3' and the "
                "saved line; an empty Enter then 'one sitting a boot'")
        predicted = trials2.verdict_detail(trials2.journal_of(
            [expected_script(SCRIPT_H1)] + SCRIPTS_W_HOST + [expected_script(SCRIPT_W5)]))
        problems, got = self.play_boot("W2", disk, SCRIPT_W5, "enter", full=True, verdict=True, at_boot=due(5))
        if got is None:
            return False
        results, reads, cap, notes = got
        problems += self.check_verdict("W2", notes, results, reads, predicted, "G")
        v = trials2.verdict_detail(notes)
        if v and v[0] != [1, 2, 3, 5]:
            problems.append("W2: the verdict judged sittings %r, want [1, 2, 3, 5]" % v[0])
        if self.fail(problems, "W2: sitting 5 and the verdict G are not what TRIALS2.md says", cap):
            say("W2: 'trial2: due sitting 5', Enter, the sitting to done, the verdict %s %d over sittings 1, 2, 3 and 5, the "
                "four tables in the app panel" % results.get("verdict", ("?", 0)))
        problems, cap, extra = self.boot_after("W3", disk, "G", ROW_HP, full=True)
        if extra:
            rd, geometry, ready_s = extra
            got_g = g_columns_of(rd["choices"], geometry[2])
            if isinstance(G_ROWS_RUN[3], _Unset) or tuple(G_ROWS_RUN[3]) != got_g:
                problems.append("W3: the three-item G row reads %r; the run constant is %r" % (got_g, G_ROWS_RUN[3]))
            say("(W3: %d notes on the disk, ready %.2f s after QEMU's start)" % (len(notes_on_disk(disk)), ready_s))
        t1_disk = run_tool([os.path.join(REPO, "stage7", "trials.py"), "--disk", disk])[1]
        if t1_disk != t1_before:
            problems.append("W3: the frozen stage7/trials.py --disk changed with trial two concluded on the disk")
        if parts_disk(disk) != parts_before:
            problems.append("W3: stage8/parts.py --disk changed")
        if self.fail(problems, "W3: the boot after verdict G with a full trial on the disk is not what TRIALS2.md says", cap):
            say("W3: 'trial2: concluded verdict G default G' with a full trial on the HP's history; layout_default 2 and the "
                "HP's three-item prompt row in G; the frozen stage7/trials.py still prints trial one's verdict A")
        return True


def run_sittings():
    if not require(["READY_LIMIT_S", "READY_FULL_S", "SETTLE_S", "OFFSET_MS", "OFFSET_FIRST_MS", "HIT_WINDOW_MS",
                    "SITTING_S", "G_ROWS_RUN"]):
        return 1
    problems = []
    for sc in SCRIPTS_V + [SCRIPT_H1, SCRIPT_W4, SCRIPT_W5]:
        problems += check_script_range(sc)
    for sc in SCRIPTS_W_HOST:
        problems += check_script_range(sc)
    pv = trials2.verdict_detail(trials2.journal_of([expected_script(s) for s in SCRIPTS_V]))
    pw = trials2.verdict_detail(trials2.journal_of([expected_script(SCRIPT_H1)] + SCRIPTS_W_HOST + [expected_script(SCRIPT_W5)]))
    if pv[2] <= 16 * SLACK_MS or pw[2] >= -16 * SLACK_MS:
        problems.append("the scripts' margins (S %d for V, %d for W) are inside the slack" % (pv[2], pw[2]))
    if not report("the sittings' scripts", problems):
        return 1
    run = Sittings()
    for part in (run.disk_v, run.disk_h):
        t0 = time.time()
        part()
        say("(%s: %.1f s)" % (part.__name__, time.time() - t0))
    return 0 if run.ok else 1


# ------------------------------------------------ test 4: the cage --------
# (b) the checker's own QEMU command through ring 7c's frozen check_argv_7c,
# with trials/out/ in stage7/out/'s place for that call; (c) the payload
# table whole, 0 wrong, and the spot checks held as data: the four frozen
# paths denied every mutation and readable, trials/ itself protected by the
# owner's directory rule, the builder and the records writable, running the
# gate, the checker and the tool allowed; (d) the frozen stage7/trials.py
# on a disk holding both families prints trial one's report unchanged.
# test-trial2.sh holds (a), its own strings, and (e), ring 8a's gate.

FROZEN_8T = ["trials/TRIALS2.md", "trials/trials2.py", "trials/checktrials2.py", "trials/test-trial2.sh"]
SPOT_DENY_8T = [c for p in FROZEN_8T for c in (
    "echo x > %s" % p, "sed -i 's/a/b/' %s" % p, "cp /tmp/x %s" % p, "rm -f %s" % p,
    "python3 - <<'EOF'\nopen('%s','w').write('x')\nEOF" % p)] + [
    "rm -rf trials", "mv trials old-trials", "git rm -r trials", "rm trials/*.py", "rm -f trials/*.md", "rm -rf trials/",
    "rm -rf %s" % os.path.join(REPO, "trials"), "rmdir trials", "git mv trials old-trials",
]
SPOT_ALLOW_8T = [
    "./trials/test-trial2.sh", "./trials/test-trial2.sh 2>&1 | tail -20",
    "python3 trials/checktrials2.py --document", "python3 trials/checktrials2.py --rows",
    "python3 trials/checktrials2.py --sittings", "python3 trials/checktrials2.py --cage",
    "python3 trials/trials2.py --example", "python3 trials/trials2.py --disk trials/out/t8/disk.V.img",
    "python3 trials/trials2.py --serial trials/out/hp-8t.log", "python3 trials/trials2.py --status trials/out/hp-8t.log",
    "cat trials/TRIALS2.md | head", "grep -n trial2 trials/checktrials2.py", "tail -5 trials/out/gate-8t.log",
    "rm -rf trials/out/t8", "rm -rf trials/out/probe8t/i8", "rm -f trials/out/t8/disk.V.img",
    "qemu-img create -f raw trials/out/t8/scratch.img 64M",
    "./stage8/mkimage.sh", "python3 stage8/mkstick.py", "./stage8/test-8a.sh",
    "git add trials/TRIALS2.md trials/checktrials2.py", "git commit -F msg.txt",
]
WRITE_ALLOW_8T = ["stage8/stage8.asm", "stage8/mkimage.sh", "stage8/mkstick.py", "stage8/seed-record.md",
                  "trials/HP-8t.md", "trials/plan-8t.md", "trials/glass-8t-section.md", "trials/spec-trial2.md", "HANDOVER.md"]
ARGV_REFUSED_8T = ("-icount", "-global", "-action", "-watchdog", "-watchdog-action", "-no-reboot", "-accel", "-enable-kvm")


def tool_verdict(tool, tool_input):
    import json
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input})
    r = subprocess.run([sys.executable, checkmetal.HOOK], input=payload.encode(), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO))
    return {0: "ALLOW", 2: "DENY"}.get(r.returncode, "EXIT %d" % r.returncode)


def check_argv_8t():
    disk = os.path.join(T8, "disk.V.img")
    copy = os.path.join(T8, "stick.V1.img")
    serial = os.path.join(T8, "serial.V1.txt")
    argv = checkmetal.qemu_argv(SMP, disk, copy, serial)
    saved = checkmetal.OUT, checkmetal.STICK
    checkmetal.OUT, checkmetal.STICK = OUT, STICK      # the frozen check's own paths, pointed at this ring's
    try:
        problems = checkmetal.check_argv_7c(argv, PORTS[2], checkmetal.MAC)
    finally:
        checkmetal.OUT, checkmetal.STICK = saved
    for flag in ARGV_REFUSED_8T:
        if flag in argv:
            problems.append("the command carries %s, which check_argv_7c does not inspect" % flag)
    if argv[argv.index("-smp") + 1] != str(SMP):
        problems.append("the boots do not run at -smp %d" % SMP)
    for path in (disk, copy, serial):
        if not path.startswith(T8 + os.sep):
            problems.append("a boot's file is not under trials/out/t8/: %s" % path)
    import wire
    if (checkmetal.BROKER_PORT, checkmetal.REHEARSAL_PORT, checkmetal.RELAY_PORT) != PORTS or PORTS != (9999, 9998, 9997):
        problems.append("the frozen 7c ports are not 9999, 9998 and 9997")
    if twin.DEFAULT_PORT != 9998 or wire.RELAY_PORT != 9997 or twin.VGA_ARGS != checkmetal.DISPLAY:
        problems.append("the frozen modules' ports or display are not ring 7c's")
    return problems


def check_bodyguard_8t():
    problems = []
    r = subprocess.run([sys.executable, checkmetal.PAYLOADS], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    m = re.fullmatch(r"(\d+) payloads: (\d+) must be denied, (\d+) must be allowed, (\d+) wrong", last)
    if r.returncode != 0 or not m or m.group(4) != "0":
        problems.append("the payload table: exit %d, last line %r - want exit 0 and 0 wrong" % (r.returncode, last))
        problems += ["  " + l.strip() for l in r.stdout.splitlines() if l.startswith("  WRONG")]
    else:
        say("the payload table: %s" % last)
    for p in FROZEN_8T:
        for path in (p, os.path.join(REPO, p)):
            for tool, ti in (("Write", {"file_path": path, "content": "x"}),
                             ("Edit", {"file_path": path, "old_string": "a", "new_string": "b"})):
                v = tool_verdict(tool, ti)
                if v != "DENY":
                    problems.append("the hook %ss %s on %s - every ring 8t frozen path must be frozen" % (v.lower(), tool, path))
        v = tool_verdict("Read", {"file_path": os.path.join(REPO, p)})
        if v != "ALLOW":
            problems.append("the hook %ss Read on %s - a frozen file stays readable" % (v.lower(), p))
    for p in WRITE_ALLOW_8T:
        v = tool_verdict("Write", {"file_path": p, "content": "x"})
        if v != "ALLOW":
            problems.append("the hook %ss Write on %s - the builder and the records are never frozen" % (v.lower(), p))
    for c in SPOT_DENY_8T:
        v = checkmetal.hook_verdict(c)
        if v != "DENY":
            problems.append("the hook %ss %r - every mutation of a ring 8t frozen path must be denied" % (v.lower(), c))
    for c in SPOT_ALLOW_8T:
        v = checkmetal.hook_verdict(c)
        if v != "ALLOW":
            problems.append("the hook %ss %r - running the gate, the checker, the tool and the builders must be allowed"
                            % (v.lower(), c))
    return problems


def check_both_families():
    """(d): trial one's HP notes and worked example A's trial-two sitting on one disk,
    written from the host; the frozen stage7/trials.py prints what it prints for the
    ring 7d charts alone."""
    history, _ = hp_history()
    one = [n for n in history if not n.startswith("molt ")][:len(NOTES_7C) + HISTORY_COUNTS["trial"]]
    disk = os.path.join(T8, "disk.families.img")
    write_disk(disk, one + trials2.DOCUMENT["a_notes"], [], host_format=True)
    joined = os.path.join(T8, "trial-one-charts.log")
    with open(joined, "wb") as fh:
        for name, sha in CHARTS_7D:
            fh.write(chart_stream(name, sha))
    rc1, out1 = run_tool([os.path.join(REPO, "stage7", "trials.py"), "--disk", disk])
    rc2, out2 = run_tool([os.path.join(REPO, "stage7", "trials.py"), "--serial", joined])
    if rc1 != 0 or out1 != out2:
        return ["the frozen stage7/trials.py on a disk holding both families (exit %d) is not its report on the 7d charts "
                "(exit %d): %r" % (rc1, rc2, out1[-200:])], out1
    return [], out1


def run_cage():
    ok = True
    problems = check_argv_8t()
    if report("the checker's QEMU command is not the twin of the HP", problems):
        say("the checker's QEMU command is checkmetal.qemu_argv itself: one restricted cage to 127.0.0.1:%d, the e1000e with "
            "%s, -cpu IvyBridge, the display, the stick copy over xhci, the SATA disk on ide.1, both under trials/out/t8/, "
            "no esp.img, -smp %d; none of %s" % (PORTS[2], checkmetal.MAC, SMP, " ".join(ARGV_REFUSED_8T)))
    else:
        ok = False
    problems = check_bodyguard_8t()
    if report("the bodyguard does not freeze ring 8t's paths", problems):
        say("the bodyguard: the %d ring 8t frozen paths denied Write and Edit (relative and absolute) and %d spellings, "
            "readable; trials/ under the owner's directory rule; the builder's %d files writable; %d shapes allowed"
            % (len(FROZEN_8T), len(SPOT_DENY_8T), len(WRITE_ALLOW_8T), len(SPOT_ALLOW_8T)))
    else:
        ok = False
    try:
        problems, out = check_both_families()
    except (ValueError, OSError) as exc:
        problems, out = ["both families: %s" % exc], ""
    if report("trial one's record is disturbed by trial two's notes", problems):
        say("both families on one disk: the frozen stage7/trials.py prints trial one's report unchanged (%s)"
            % out.strip().splitlines()[-1])
    else:
        ok = False
    say("the cage: %s" % ("held, and the criteria frozen" if ok else "not proven"))
    return 0 if ok else 1


MODES = {"--document": run_document, "--rows": run_rows, "--sittings": run_sittings, "--cage": run_cage}


def main(argv):
    sets = []
    while len(argv) >= 3 and argv[-2] == "--set":
        sets.insert(0, argv[-1])
        argv = argv[:-2]
    if len(argv) != 1 or argv[0] not in MODES:
        print("usage: checktrials2.py %s [--set NAME=VALUE ...]" % " | ".join(MODES))
        return 1
    os.makedirs(T8, exist_ok=True)
    tee = tee_log(argv[0])
    try:
        apply_sets(sets)
        return MODES[argv[0]]()
    except ValueError as exc:
        say(str(exc))
        return 1
    finally:
        untee(tee)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
