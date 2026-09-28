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
import struct
import subprocess
import sys

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
from checkglass import say, report  # noqa: E402

T1 = trials2.T1                                   # stage7/trials.py, frozen


class _Unset:
    def __repr__(self):
        return "UNSET"


UNSET = _Unset()

# ------------------------------------------------ the numbers a run gives --
# Item 8's probe (a private build with the guest drafted, played by the
# synthetic human) supplies these; each is written with its date. While one
# is UNSET the mode that needs it fails and names it.

G_ROWS_RUN = {                 # (label spans, separator columns) read from the probe's surface and screendump
    4: UNSET,
    2: UNSET,
    3: UNSET,
}
TRIAL_NUMBER_AT_RUN = UNSET    # the offset the probe's page read showed trial_number at


def unset(names):
    return [n for n in names if isinstance(globals()[n], _Unset) or
            (isinstance(globals()[n], dict) and any(isinstance(v, _Unset) for v in globals()[n].values()))]


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


MODES = {"--document": run_document}


def main(argv):
    if len(argv) != 1 or argv[0] not in MODES:
        print("usage: checktrials2.py %s" % " | ".join(MODES))
        return 1
    os.makedirs(T8, exist_ok=True)
    tee = tee_log(argv[0])
    try:
        return MODES[argv[0]]()
    finally:
        untee(tee)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
