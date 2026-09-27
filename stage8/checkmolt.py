#!/usr/bin/env python3
"""Stage 8 ring 8a acceptance checker - the floor: a part can fail
without taking the machine with it.

Modes (all from the repo root, invoked by stage8/test-8a.sh):

  --document   test 1's second half: the stick as ring 7c's frozen
               checker parses it, with stage8's stick and build as explicit
               arguments; stage8/PARTS.md and stage8/SEED.md read cold by
               stage8/parts.py and every worked example reproduced byte for
               byte; the five fixtures reassembled into stage8/out/ and
               byte-identical to the committed binaries, each header valid
               by PARTS.md; SHA-256's known answer against the host's, and
               the 64 round constants in the built EFI equal to PARTS.md's
               rule; the seed record parsed and append-only against its own
               git history.
  --seven      test 2: no part, no change. Ring 7c's and ring 7d's frozen
               checks, pointed at stage8's build through their module
               seams as ring 8a item 1 (D3) found them by a run: three
               serial boots (blank 8, again 4, novga 2), the stages run, the
               row and the sittings. Each must return success, nothing
               outside stage8/out/ may change, and no capture under
               stage8/out/seven/ may carry a line of ring 8a's own
               ("S8:", "part:", "molt:").
  --fates      test 3: the five fixtures meet their fates in the twin at
               -smp 4, driven by the synthetic human (plan decision 16) on
               five disks, each booted blank and given a ring-7d-like
               notebook from the host: G (good: the install, three shadow
               boots, the take, live with a held request and the idle
               wait - 300 paced moves during the hold, more than the raw
               ring holds, and no reset - the undo, Esc, live again), W (wrong: the
               disagreement, the take refused), H (hang in good's place:
               the watchdog's reset and the recovery), F (fault: the blame
               line, the reset and the recovery) and L (liar: the torn
               write refused at the door). Every note, line, count, table
               and answer is PARTS.md's rule through stage8/parts.py; every
               frame the mock served is compared with parts.fixture_frame.
               The run constants are item 12's: while one is unset the mode
               refuses to run and names it. For item 12's run only, an
               unset one may be given as --set NAME=VALUE; a set one never.
  --cage       test 4's (b) and (c): a fates boot's command, `timeout -k 5
               <T>` before checkmetal.qemu_argv itself with the stage8
               paths, through ring 7c's frozen check_argv_7c, with -icount,
               noreboot and -action refused here since that check does not
               inspect them (D4); the mock's command; the frozen modules'
               ports. Then the payload table as a subprocess, 0 wrong, and
               the spot checks held as data: every ring 8a frozen path,
               stage8/loader.asm among them, denied Write, Edit, `>`,
               sed -i, cp, rm and a heredoc, and still readable; the owner's
               directory rule in every category of his decision (the repo
               root, a directory holding a frozen file by name, trailing
               slash and absolute path, a glob covering one, rm, rmdir, mv,
               git rm and git mv) and on its allowed side (an ordinary file
               beside frozen ones, stage8/out wiped); the gate, the checker,
               the tools and the builders allowed. test-8a.sh holds (a),
               its own strings, and (d), ./stage7/test-7d.sh.

Every expected line, count and byte is PARTS.md's or SEED.md's rule
through stage8/parts.py, or the frozen 7c and 7d checkers' own. Written
before the guest code it judges and frozen behind the hook once written
(ring 8a plan item 13). Everything it starts is QEMU with OVMF, the
patient's CPU model, the display at 1920x1080, the caged network to the
relay on 127.0.0.1, the stick copy over xhci, the SATA disk on ide.1, the
PS/2 mouse driven through the monitor; every drive a raw file under
stage8/out/. It talks only to the mock brokers and never spends a token.

Run directly, it appends its output to stage8/out/gate-8a.log under its
own dated header. Under the gate (GATE_8A=1 in the environment) the gate's
own tee holds the log, and no second header is written.
"""

import datetime
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
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "stage8", "out")
LOG = os.path.join(OUT, "gate-8a.log")
EFI = os.path.join(OUT, "BOOTX64.EFI")
STICK = os.path.join(OUT, "stick.img")
ESP = os.path.join(OUT, "esp.img")
SEVEN = os.path.join(OUT, "seven")               # test 2's scratch: the frozen checkers' own files, moved here
SEVEN_METAL = os.path.join(SEVEN, "metal")
SEVEN_TRIALS = os.path.join(SEVEN, "trials")
PORTS = (9999, 9998, 9997)

sys.path.insert(0, os.path.join(REPO, "stage6"))
sys.path.insert(0, os.path.join(REPO, "stage7"))
sys.path.insert(0, os.path.join(REPO, "stage8"))
sys.path.insert(0, os.path.join(REPO, "broker"))
import checkmetal  # noqa: E402  - ring 7c's frozen checker: the twin of the HP
import checktrials  # noqa: E402  - ring 7d's frozen checker: the row and the sittings
import checkdisk  # noqa: E402  - ring 7a's: extract_partition writes through its OUT
import checkglass  # noqa: E402  - ring 6a's: fixture_self_check writes through its OUT
from checkglass import say, report  # noqa: E402
import checknotes  # noqa: E402  - Stage 3's frozen NOTEBOOK.md record builder (checkdisk put stage3 on the path)
import twin  # noqa: E402
from twin import Driver  # noqa: E402
from plans import plan_keyname, PLANS_DIR  # noqa: E402
from rehearse import KEY_GAP  # noqa: E402
from glass import regions  # noqa: E402
from pointer import choice_targets  # noqa: E402
from checkpointer import Pointer, expected_counts, target_col, CELL  # noqa: E402
import trials  # noqa: E402  - TRIALS.md's Python: the seed notebook's trial notes
import metal  # noqa: E402  - DISK.md's Python
import checkplans  # noqa: E402  - HOME.md's parser

LINE_8A = re.compile(rb"(?<![A-Za-z0-9_-])((?:S8|part|molt): [^\r\n]*)")   # anywhere, not only at a line's start
ANSI = re.compile(rb"\x1b\[[0-9;?]*[A-Za-z]")                                  # the firmware's escapes, read as line breaks


def lines_8a(data):
    return [m.group(1) for m in LINE_8A.finditer(ANSI.sub(b"\n", data))]


# ------------------------------------------------------------- the log ----

def commit():
    """HEAD's short hash, with +uncommitted when the tracked files differ from
    it (Cowork's review of item 9: a run before its commit named the previous
    item's hash). Read-only: --no-optional-locks, so git writes no index."""
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return "none"
    d = subprocess.run(["git", "--no-optional-locks", "-C", REPO, "diff", "--quiet", "HEAD"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.stdout.strip() + ("+uncommitted" if d.returncode != 0 else "")


def tee_log(mode):
    """Run directly: a dated header in the log, then every byte this process
    and its children write goes to the terminal and the log alike. Under the
    gate the gate's tee does both, so nothing is done here."""
    if os.environ.get("GATE_8A") == "1":
        return None
    os.makedirs(OUT, exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write("\n=== checkmolt.py %s %s commit %s ===\n"
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
    null = os.open(os.devnull, os.O_WRONLY)
    os.dup2(null, 1)
    os.dup2(null, 2)
    os.close(null)
    tee.wait()


def ports_free():
    busy = []
    for port in PORTS:
        s = socket.socket()
        s.settimeout(1.0)
        try:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                busy.append(port)
        finally:
            s.close()
    if busy:
        say("something is already listening on 127.0.0.1:%s. The checker talks only to its own mock broker, its own twin "
            "and its own relay; stop whatever holds the port, then run this again." % ", ".join(map(str, busy)))
        return False
    return True


# ------------------------------------------------ test 1: the documents --

def check_fixtures(parts):
    """Each fixture's source reassembled into stage8/out/, byte-identical to
    the committed binary; its banner names its own build line; its header
    valid by PARTS.md for the i8042 slot, its name field its fate."""
    problems = []
    for fate in parts.FATES:
        src, binary = parts.fixture_path(fate, ".asm"), parts.fixture_path(fate)
        rel = os.path.relpath(src, REPO)
        check = os.path.join(OUT, "i8042-%s.check.bin" % fate)
        try:
            text = open(src, encoding="utf-8").read()
            blob = open(binary, "rb").read()
        except OSError as exc:
            problems.append("%s: %s" % (fate, exc))
            continue
        line = "nasm -f bin %s -o %s" % (rel, os.path.relpath(binary, REPO))
        if line not in text:
            problems.append("%s's banner does not give its build line %r" % (rel, line))
        if os.path.exists(check):
            os.remove(check)
        try:
            r = subprocess.run(["nasm", "-f", "bin", src, "-o", check], capture_output=True, text=True, timeout=60, cwd=REPO)
        except (OSError, subprocess.TimeoutExpired) as exc:
            problems.append("could not assemble %s: %s" % (rel, exc))
            continue
        if r.returncode != 0:
            problems.append("%s does not assemble: %s" % (rel, r.stderr.strip()[:200]))
            continue
        if open(check, "rb").read() != blob:
            problems.append("%s does not reproduce %s byte for byte" % (rel, os.path.relpath(binary, REPO)))
            continue
        try:
            f = parts.check_part(blob, "i8042")
        except ValueError as exc:
            problems.append("%s is not a part for the i8042 slot by PARTS.md: %s" % (os.path.relpath(binary, REPO), exc))
            continue
        if f["name"] != fate:
            problems.append("%s's name field is %r, not its fate" % (os.path.relpath(binary, REPO), f["name"]))
        try:
            pf = parts.parse_frame(parts.fixture_frame(fate), "i8042")
            if pf[0] != "part" or pf[2] != blob or pf[3] != tuple(parts.FIXTURES[fate]) or pf[4] != 0:
                problems.append("%s's frame does not parse back to its part and its threshold" % fate)
        except ValueError as exc:
            problems.append("%s's frame is refused by PARTS.md's install checks: %s" % (fate, exc))
    return problems


def check_sha(parts):
    problems = []
    if not parts.sha256_kat():
        problems.append("PARTS.md's abc digest is not the host's SHA-256 of abc")
    if not parts.seed_kat():
        problems.append("SEED.md's known answers are not the host's SHA-256")
    try:
        efi = open(EFI, "rb").read()
    except OSError as exc:
        return problems + ["the build: %s" % exc], []
    at = parts.sha_k_in(efi)
    if len(at) != 1:
        problems.append("the 64 round constants by PARTS.md's rule lie at %d place(s) in the build, want exactly one: %s"
                        % (len(at), ", ".join("0x%x" % a for a in at) or "none"))
    return problems, at


def check_record(parts):
    problems = []
    try:
        versions = parts.record_versions()
        seeds = parts.parse_seed_record(versions[-1][1])
        parts.append_only([t for _, t in versions])
    except (ValueError, OSError) as exc:
        return ["the seed record %s: %s" % (parts.RECORD, exc)], None
    if not seeds or seeds[0]["n"] != 0:
        problems.append("the seed record does not begin with seed 0")
    return problems, seeds


def run_document():
    problems = checkmetal.check_stick(STICK, EFI)
    ok = report("the stick is not what ring 7c's frozen checker asks for", problems)
    if ok:
        say("stick.img as ring 7c's checker reads it, with stage8's stick and build as its arguments: a protective MBR, both "
            "GPT headers and arrays with their CRCs, one EFI System Partition, EFI/BOOT/BOOTX64.EFI read back byte-identical "
            "to stage8/out/BOOTX64.EFI")
    r = subprocess.run([sys.executable, os.path.join(HERE, "parts.py"), "--example"], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, cwd=REPO)
    for line in r.stdout.strip().splitlines():
        say(line)
    if r.returncode:
        say("PARTS.md or SEED.md: the documents do not read cold, or a worked example is not reproduced")
        return 1
    try:
        import parts
    except (ValueError, KeyError, IndexError, TypeError, AttributeError, OSError) as exc:
        say("stage8/parts.py does not load the documents: %s" % exc)
        return 1
    problems = check_fixtures(parts)
    if report("the fixtures are not what PARTS.md and the repository say", problems):
        say("the five fixtures reassembled into stage8/out/ byte-identical to their committed binaries, each a part for "
            "the i8042 slot by PARTS.md with its fate as its name, each frame parsing back to its part and the fixture "
            "table's threshold")
    else:
        ok = False
    problems, at = check_sha(parts)
    if report("SHA-256 is not what PARTS.md and SEED.md say", problems):
        say("SHA-256: PARTS.md's abc digest %s... and SEED.md's known answers are the host's; the 64 round constants by "
            "PARTS.md's rule lie once in the build, at 0x%x" % (parts.KAT_ABC[:16], at[0]))
    else:
        ok = False
    problems, seeds = check_record(parts)
    if report("the seed record is not what SEED.md says", problems):
        say("the seed record: %d line(s) by SEED.md's rules, append-only against its git history, the witness's seed %d"
            % (len(seeds), parts.current_seed(seeds)["n"]))
    else:
        ok = False
    return 0 if ok else 1


# ------------------------------------------------ test 2: no part, no change --
# The seams as ring 8a item 1 found them by a run (HANDOVER.md, D3, attempt
# 2): the module paths the frozen 7c and 7d checkers read at call time,
# rebound to stage8's build and to stage8/out/seven/; the two bound
# defaults; and the two modules that write through their own OUT.

def point_seams():
    for mod, name, value in (
            (checkmetal, "OUT", OUT),
            (checkmetal, "METAL_OUT", SEVEN_METAL),
            (checkmetal, "STICK", STICK),
            (checkmetal, "EFI", EFI),
            (checkmetal, "ESP", ESP),
            (checkmetal, "DISK", os.path.join(SEVEN_METAL, "disk.img")),
            (checkmetal, "GERMLINE", os.path.join(SEVEN_METAL, "germline")),
            (checkmetal, "REHEARSAL", os.path.join(SEVEN_METAL, "rehearsal")),
            (checkmetal, "TWIN_WORKDIR", os.path.join(SEVEN_METAL, "rehearsal", "twin")),
            (checktrials, "OUT", OUT),
            (checktrials, "TRIALS_OUT", SEVEN_TRIALS),
            (checktrials, "STICK", STICK),
            (checktrials, "DISK", os.path.join(SEVEN_TRIALS, "disk.img")),
            (checktrials, "METAL_OUT", SEVEN_METAL),
            (checkdisk, "OUT", SEVEN_METAL),
            (checkglass, "OUT", SEVEN)):
        setattr(mod, name, value)
    checkmetal.check_stick.__defaults__ = (STICK, EFI)
    checkmetal.check_stick_tables_unchanged.__defaults__ = (STICK,)


SEVEN_ENTRIES = [
    ("checkmetal.run_serial('blank', 8)", lambda: checkmetal.run_serial("blank", 8)),
    ("checkmetal.run_serial('again', 4)", lambda: checkmetal.run_serial("again", 4)),
    ("checkmetal.run_serial('novga', 2)", lambda: checkmetal.run_serial("novga", 2)),
    ("checkmetal.run_stages()", lambda: checkmetal.run_stages()),
    ("checktrials.run_row()", lambda: checktrials.run_row()),
    ("checktrials.run_sitting()", lambda: checktrials.run_sitting()),
]


def outside_files():
    """Every file under an out/ directory of another stage, and the repo's
    germline, with its mtime and size: nothing of test 2 may land there."""
    seen = {}
    roots = [os.path.join(REPO, d, "out") for d in sorted(os.listdir(REPO))
             if re.fullmatch(r"stage\d+", d) and d != "stage8"]
    roots.append(os.path.join(REPO, "germline"))
    for root in roots:
        for dp, _, fn in os.walk(root):
            for f in fn:
                p = os.path.join(dp, f)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                seen[os.path.relpath(p, REPO)] = (st.st_mtime_ns, st.st_size)
    return seen


def captures():
    """Every serial capture under stage8/out/seven/, with its mtime."""
    found = {}
    for dp, _, fn in os.walk(SEVEN):
        for f in fn:
            if f.startswith("serial") and f.endswith(".txt"):
                p = os.path.join(dp, f)
                found[p] = os.stat(p).st_mtime_ns
    return found


def run_seven():
    if not (os.path.exists(STICK) and os.path.exists(EFI) and os.path.exists(ESP)):
        say("stage8/out/ lacks the stick, the build or esp.img - build with stage8/mkimage.sh and stage8/mkstick.py first")
        return 1
    if not ports_free():
        return 1
    shutil.rmtree(SEVEN, ignore_errors=True)
    os.makedirs(SEVEN_METAL)
    os.makedirs(SEVEN_TRIALS)
    point_seams()
    before_outside = outside_files()
    problems = []
    t_all = time.time()
    for label, entry in SEVEN_ENTRIES:
        before = captures()
        say("--- %s on stage8's build ---" % label)
        t0 = time.time()
        try:
            rc = entry()
        except BaseException as exc:  # noqa: BLE001 - a frozen check that raises has not returned success
            rc = "%s: %s" % (type(exc).__name__, exc)
            for line in traceback.format_exc().strip().splitlines()[-6:]:
                say("  " + line)
        dt = time.time() - t0
        after = captures()
        fresh = sorted(p for p in after if before.get(p) != after[p])
        say("--- %s returned %r in %.1f s; %d capture(s): %s ---"
            % (label, rc, dt, len(fresh), ", ".join(os.path.relpath(p, SEVEN) for p in fresh) or "none"))
        if rc != 0:
            problems.append("%s returned %r, not 0" % (label, rc))
        if not fresh:
            problems.append("%s left no serial capture under stage8/out/seven/" % label)
        if not ports_free():
            problems.append("a port is still held after %s" % label)
            break
    after_outside = outside_files()
    moved = sorted(p for p in set(before_outside) | set(after_outside) if before_outside.get(p) != after_outside.get(p))
    if moved:
        problems.append("test 2 changed %d file(s) outside stage8/out/: %s" % (len(moved), ", ".join(moved[:8])))
    seen = []
    every = sorted(captures())
    for p in every:
        for line in lines_8a(open(p, "rb").read()):
            seen.append("%s: %r" % (os.path.relpath(p, SEVEN), line[:60]))
    if seen:
        problems.append("a line of ring 8a's own in a capture with no part installed: %s" % "; ".join(seen[:8]))
    if not report("no part is not no change", problems):
        return 1
    say("no part, no change: ring 7c's three serial boots, its stages run, ring 7d's row and sittings, each returning 0 on "
        "stage8's build through D3's seams, in %.1f s; nothing outside stage8/out/ changed; %d capture(s) under "
        "stage8/out/seven/ and not one S8:, part: or molt: line among them" % (time.time() - t_all, len(every)))
    return 0


# ------------------------------------------------ test 3: the fates -------
# Plan decision 16 and deviation 12: five disks in the twin at -smp 4, each
# a fresh 64 MB file booted blank once and then given a ring-7d-like
# notebook from the host, driven by the synthetic human. Every expectation
# is a rule's output through stage8/parts.py; only the run constants below
# come from a run (item 12's).

FATES_SMP = 4
MOLT_OUT = os.path.join(OUT, "molt")             # the gate's scratch (plan decision 1)
MOLT_GERMLINE = os.path.join(MOLT_OUT, "germline")
MOLT_TWIN = os.path.join(MOLT_OUT, "rehearsal", "twin")
MOLT_BROKER = os.path.join(REPO, "broker", "molt.py")
SLOT = "i8042"

# The run constants (plan item 10: named placeholders), written at item 12
# from its run of 27 September 2026 - `checkmolt.py --fates --set ...` on
# the probe's draft (stage8/out/gate-8a.log; all five fates ok in 875.1 s)
# and the draft's timing probe - each a bound with its margin over what the
# run measured. The checker refuses to run while any is None.
READY_S = 30.0          # QEMU's start, or a reset's first OVMF byte, to "S7: keyboard ready": 1.4-1.5 s with no
                        # part to load, 4.4-4.5 s with one (the 3 s Esc window), 0.8 s after a reset's first byte
SETTLE_S = 1.0          # after the ready line, before the first input: ring 7d's (checktrials.SETTLE_S); no key lost
WORD_S = 2.0            # a word's answer on the console and its note on the disk: every word's note within one
                        # key gap (0.2 s, the probe's resolution) of its Enter
ANSWER_S = 10.0         # "! molt i8042" to its install note on serial, through the relay and the mock: within
                        # one key gap (0.2 s) of its Enter
HEALTH_SLACK_S = 10.0   # beyond PARTS.md's 60 s, the wait from the ready line for "S8: healthy <n>": the mark
                        # came 60.0-60.2 s after the ready line on all eight boots that awaited it
HOLD_SLACK_S = 10.0     # beyond HOLD_S, the wait for the held answer in the conversation: 60.9 s after its Enter
RESET_S = 35.0          # the triggering input to the next boot's first OVMF byte: PARTS.md's three terms sum
                        # to 32.14 s (30 + 1 + 1.14); the run gave 30.3 s (hang) and 31.0 s (fault), the
                        # draft's four reset probes 30.2-31.0 s
RECOVER_S = 10.0        # that first OVMF byte to "S8: recovery i8042 watchdog": 0.8 s both times
WIGGLE_PACE_S = 0.005   # between two mouse_moves of a wiggle: one packet each (D4: from 1 ms); the run's
                        # shadow counts equal to the model's on every boot (1,677 packets at G2-G4)
BOOT_T_S = 600          # each boot's `timeout -k 5 <T>` (plan decision 15); exit 124 means the steps overran:
                        # the longest boot was G5, 151.6 s (the idle health mark, the held request, two words)
RUN_CONSTANTS = ("READY_S", "SETTLE_S", "WORD_S", "ANSWER_S", "HEALTH_SLACK_S", "HOLD_SLACK_S", "RESET_S", "RECOVER_S",
                 "WIGGLE_PACE_S", "BOOT_T_S")

# CC's own, not criteria:
POLL_S = 0.01           # the serial file's poll
ASK_POLL_S = 1.0        # the conversation's poll while a held answer is awaited
MOVE_S = 0.02           # between the moves that take the hand to a target (7d's pace)
DRAIN_EVERY = 64        # monitor commands between two drains of its output (a full pipe stalls the monitor)
HOLD_WIGGLES = 300      # G5: the moves during the held request, more than PARTS.md's raw ring holds (the owner's
                        # decision on Cowork's review of item 12: an overflow inside a bounded wait never blocks the pet)

# Typed texts never carry a colon, so a line of ring 8a's own is never in
# an echo, and none begins "molt " or "trial " or carries a q (W's note
# alone does, on purpose).
RAW_8A = re.compile(rb"(?:S8|part|molt): [^\r\n]*")
TYPED = [
    "remember the dentist on friday at ten",
    "Call the bank about the direct debit",
    "bins go out on tuesday night",
    "the calculator lives in the home store now",
    "Buy bread, milk and eggs",
    "the printer needs a new cartridge",
    "ring mum on sunday afternoon",
    "the stick is flashed and the disk is fine",
    "Check the tyre pressure before the long drive",
    "book the car in for its service",
    "the garden fence wants a coat of paint",
    "Water the tomatoes every other day",
    "the library books are due back on the tenth",
    "pick up the parcel from the post office",
    "Send the photos to the family",
    "the boiler service is in march",
]
Q_NOTE = "a quiet word with the plumber"      # W's note: one q, the wrong part's w

OVMF_START = b"\x1b"    # after the ready line the guest writes no escape; OVMF's first bytes are one


def unset_constants():
    names = []
    for name in RUN_CONSTANTS:
        if globals()[name] is None:
            names.append(name)
    return names


def apply_overrides(args):
    """--set NAME=VALUE for item 12's run: only a constant that is still
    None may be given, never one already written."""
    for a in args:
        m = re.fullmatch(r"([A-Z_]+)=([0-9.]+)", a)
        if not m or m.group(1) not in RUN_CONSTANTS:
            return "not a run constant: %r (the constants are %s)" % (a, ", ".join(RUN_CONSTANTS))
        if globals()[m.group(1)] is not None:
            return "%s is written (%r); a written constant is never overridden" % (m.group(1), globals()[m.group(1)])
        globals()[m.group(1)] = float(m.group(2))
    return None


def keyname_8a(ch):
    """drive_7d's spelling of a character as a monitor key."""
    if ch in "\n\t\x1b":
        return twin.keyname(ch)
    if ch == "\b":
        return "backspace"
    return plan_keyname(ch)


def seed_notes():
    """A ring-7d-like notebook of 40 notes, like the HP's: typed notes, ring
    7d's aborted sitting as TRIALS.md expands it, and the verdict A last."""
    trial = trials.notes_of(checktrials.SCRIPT_ABORT)
    typed = [t for t in TYPED][:40 - 1 - len(trial)]
    return typed + trial + ["trial verdict A"]


def typed_notes(bytes_wanted, start=0, parts_mod=None):
    """Whole notes from TYPED, from index start, until their keyboard bytes
    reach bytes_wanted by PARTS.md's key-byte rule. Returns (notes, next)."""
    out, i, kb = [], start, 0
    while kb < bytes_wanted:
        t = TYPED[i % len(TYPED)]
        out.append(t)
        kb += parts_mod.keyboard_bytes(t + "\n")
        i += 1
    return out, i


# ---------------------------------------------------------- the human ----

class Human8a:
    """The synthetic human (plan decision 16): ring 7d's drive_7d step
    loop, spelled here with its own helpers imported (Driver, Pointer,
    expected_counts, parse_obs_7d, KEY_GAP), because drive_7d waits for
    one ready line and can host neither a step before it (the Esc hold) nor
    a reset inside one process (the watchdog's recovery). Its vocabulary is
    7d's ("sleep", "mouse", "button", "moveto", "obs", "surfaces",
    "serial") plus ring 8a's: ("ready", label), ("keys", text[, label]),
    ("wiggle", n[, label]), ("click", kind, arg), ("mark", label),
    ("await", regex, s, label, since), ("banner", s, label, since),
    ("hold_esc", ms), ("sleep_since", label, s), ("ask_held", label[,
    moves, kept]).
    ("flip", disk, offset) is the host's, between boots (flip())."""

    def __init__(self, parts_mod):
        self.parts = parts_mod
        self.reads = {"at": {}, "marks": {}, "segments": [0]}
        self.events = []
        self.kb = 0
        self.lost = 0            # packets the raw ring's overflow lost (G5's held request)
        self.offset = 0
        self.model = None
        self.geometry = None
        self.obs_addr = None
        self.tells = 0

    # -- the monitor
    def tell(self, line):
        self.drv.tell(line)
        self.tells += 1
        if self.tells % DRAIN_EVERY == 0:
            self.drv._drain()

    def mouse(self, dx, dy, pace=MOVE_S):
        self.tell(b"mouse_move %d %d\n" % (dx, dy))
        if self.model:
            self.model.move(dx, dy)
        self.events.append(("mouse", dx, dy))
        time.sleep(pace)

    def button(self, mask, hit=False):
        self.tell(b"mouse_button %d\n" % mask)
        self.events.append(("button", mask, "hit") if hit else ("button", mask))
        time.sleep(0.05)

    # -- the serial file
    def wait_for(self, rx, limit_at):
        while True:
            data = self.drv.serial_bytes()
            m = rx.search(data, self.offset)
            if m:
                return m, time.time()
            if time.time() > limit_at or self.proc.poll() is not None:
                return None, time.time()
            time.sleep(POLL_S)

    def page(self):
        if self.obs_addr is None:
            seg = self.drv.serial_bytes()[self.reads["segments"][-1]:]
            m = re.search(rb"S7: obs page 0x([0-9a-f]+)", seg)
            if not m:
                raise ValueError("no obs page line on serial in this boot")
            self.obs_addr = int(m.group(1), 16)
        return trials.parse_obs_7d(self.drv.xp(self.obs_addr, trials.OBS_PAGE_BYTES_7D // 8, "g"))

    def counts(self):
        return {"kb": self.kb, "packets": expected_counts(self.events)["packets"] - self.lost,
                "pos": len(self.drv.serial_bytes()), "t": time.time()}

    # -- the steps
    def step(self, s):
        k = s[0]
        at = self.reads["at"]
        if k == "ready":
            m, t = self.wait_for(re.compile(re.escape(checkmetal.READY + b"\r\n")), time.time() + READY_S)
            if not m:
                return "no %r within %.0f s" % (checkmetal.READY.decode(), READY_S)
            self.offset = m.end()
            at[s[1]] = t
            seg = self.drv.serial_bytes()[self.reads["segments"][-1]:m.end()]
            geo = checkmetal.geometry_of(seg)
            if not geo:
                return "no gop line before the ready line"
            self.model = Pointer(*geo)
            self.geometry = (geo[0], geo[1], geo[0] // CELL, geo[1] // CELL)
            self.reads["geometry"] = self.geometry
            self.obs_addr = None
            time.sleep(SETTLE_S)
        elif k == "keys":
            for i, ch in enumerate(s[1]):
                self.tell(b"sendkey " + keyname_8a(ch).encode() + b"\n")
                self.kb += self.parts.key_bytes(ch)
                if len(s) > 2 and i == len(s[1]) - 1:
                    at[s[2]] = time.time()
                time.sleep(KEY_GAP)
            self.events.append(("type", s[1]))
        elif k == "wiggle":
            for i in range(s[1]):
                if len(s) > 2 and i == 0:
                    at[s[2]] = time.time()
                self.mouse(1 if i % 2 == 0 else -1, 0, WIGGLE_PACE_S)
            self.drv._drain()
        elif k == "click":
            if self.model is None:
                return "no geometry: the human cannot click"
            row = regions(self.geometry[2], self.geometry[3])["choices"][0]
            col = target_col(choice_targets(False, 0, []), s[1], s[2])
            for _, dx, dy in self.model.moves_to(row, col):
                self.mouse(dx, dy)
            time.sleep(0.2)
            self.button(1, hit=True)
            self.button(0)
            time.sleep(0.3)
        elif k == "mark":
            self.reads["marks"][s[1]] = self.counts()
        elif k == "await":
            _, rx, limit, label, since = s
            m, t = self.wait_for(re.compile(rx), (at[since] if since else time.time()) + limit)
            if not m:
                return "no %r within %.0f s of %s" % (rx.decode(errors="replace"), limit, since or "the step")
            self.offset = m.end()
            at[label] = t
            self.reads.setdefault("found", {})[label] = (m.start(), m.group(0))
        elif k == "banner":
            _, limit, label, since = s
            m, t = self.wait_for(re.compile(re.escape(OVMF_START)), at[since] + limit)
            if not m:
                return "no OVMF byte (a reset) within %.0f s of %s" % (limit, since)
            self.offset = m.start()
            self.reads["segments"].append(m.start())
            at[label] = t
            self.model = None
        elif k == "hold_esc":
            self.tell(b"sendkey esc %d\n" % s[1])
            at["esc"] = time.time()
        elif k == "sleep_since":
            time.sleep(max(0.0, at[s[1]] + s[2] - time.time()))
        elif k == "sleep":
            time.sleep(s[1])
        elif k == "mouse":
            self.mouse(s[1], s[2])
        elif k == "button":
            self.button(s[1], len(s) > 2)
        elif k == "moveto":
            for _, dx, dy in self.model.moves_to(s[1], s[2]):
                self.mouse(dx, dy)
        elif k in ("obs", "surfaces"):
            try:
                p = self.page()
                if k == "obs":
                    self.reads[s[1]] = p
                else:
                    self.reads[s[1]] = {name: self.drv.read_surface(p[name]) for name in ("conversation", "app")}
                    self.reads[s[1]]["obs"] = p
            except ValueError as exc:
                return "xp for %r failed: %s" % (s[1], exc)
        elif k == "serial":
            self.reads[s[1]] = self.drv.serial_bytes()
        elif k == "ask_held":
            return self.ask_held(*s[1:])
        else:
            return "unknown step %r" % (s,)
        return None

    def ask_held(self, label, moves=0, kept=0):
        """A1: "? hold" and Enter, the host time of the Enter, then the
        conversation polled until the answer lands and the prompt is back;
        the elapsed wait and the serial positions go to the reads. With
        `moves`, that many paced wiggles are sent while the request is held:
        nothing drains the raw ring during the wait, so the part is given
        the first `kept` packets when the wait ends and the rest are lost,
        as the generic's drop-on-full loses them (PARTS.md, "Overflows")."""
        pos0 = len(self.drv.serial_bytes())
        self.step(("keys", "? hold\n", label + "_enter"))
        t0 = self.reads["at"][label + "_enter"]
        for i in range(moves):
            dx = 1 if i % 2 == 0 else -1
            self.tell(b"mouse_move %d 0\n" % dx)
            if self.model and i < kept:
                self.model.move(dx, 0)
            self.events.append(("mouse", dx, 0))
            time.sleep(WIGGLE_PACE_S)
        if moves:
            self.lost += moves - kept
            self.drv._drain()
            self.reads[label + "_moves"] = (moves, kept)
        limit = t0 + self.parts.HOLD_S + HOLD_SLACK_S
        while time.time() < limit:
            time.sleep(ASK_POLL_S)
            try:
                p = self.page()
                cells = self.drv.read_surface(p["conversation"])
            except ValueError:
                continue
            rows = checktrials.conv_rows(cells, p)
            if len(rows) >= 3 and rows[-3] == "> ? hold" and rows[-1] == ">" and rows[-2] not in ("", ">"):
                self.reads[label] = {"t0": t0, "t1": time.time(), "answer": rows[-2], "pos0": pos0,
                                     "pos1": len(self.drv.serial_bytes())}
                return None
        return "the held answer never landed in the conversation within %.0f s" % (limit - t0)

    def run(self, smp, disk, stick_copy, steps, serial_path, tag):
        """One QEMU process under timeout: the steps, then quit and reap.
        Returns (serial bytes, reads, error); never leaves a QEMU running."""
        if os.path.exists(serial_path):
            os.remove(serial_path)
        errlog = open(os.path.join(MOLT_OUT, "qemu.%s.stderr.txt" % tag), "wb")
        argv = boot_argv(smp, disk, stick_copy, serial_path, "%d" % BOOT_T_S)
        self.proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errlog)
        self.drv = Driver(self.proc, serial_path, MOLT_OUT)
        err = None
        t_start = time.time()
        self.reads["at"]["start"] = t_start
        try:
            for s in steps:
                try:
                    err = self.step(s)
                except (KeyError, ValueError, OSError) as exc:
                    err = "step %r: %s: %s" % (s[0], type(exc).__name__, exc)
                if err:
                    err = "%s: %s" % (tag, err)
                    break
                if self.proc.poll() is not None:
                    err = "%s: QEMU exited %s during step %r" % (tag, self.proc.returncode, s[0])
                    break
            self.drv.tell(b"quit\n")
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        finally:
            if self.proc.poll() is None:
                self.proc.kill()
                self.proc.wait()
            try:
                self.proc.stdin.close()
            except OSError:
                pass
            errlog.close()
        self.reads["rc"] = self.proc.returncode
        self.reads["wall"] = time.time() - t_start
        if err is None and self.proc.returncode == 124:
            err = "%s: the boot ran past its timeout of %d s" % (tag, BOOT_T_S)
        return self.drv.serial_bytes(), self.reads, err


# ------------------------------------------------------- the notebook ----

class Book:
    """One boot as the rules say it goes: every note it journals and every
    ring 8a line it prints, in order. notes is the notebook so far."""

    def __init__(self, parts_mod, notes, boot=None):
        self.p = parts_mod
        self.notes = list(notes)
        self.items = []
        self.n = boot            # the boot's molt boot number when it loaded a part
        self.d = 0               # disagreements this boot

    def line(self, text):
        self.items.append(("line", text))

    def note(self, text):
        self.notes.append(text)
        self.items.append(("note", text))

    def loaded(self, state, build, live_pair):
        """Steps 1, 5, 6 and 7 of PARTS.md's boot with a molt note, for a
        boot that loads the slot's part."""
        self.line("S8: sha256 ok")
        self.line("S8: part %s %s %s" % (SLOT, state, build))
        self.note("molt boot %d %s %s" % (self.n, SLOT, state))
        self.line("S8: watchdog tco %d s" % self.p.DEADLINE_S)
        if state == "live":
            for text in live_pair:
                self.line(text)

    def count(self, kb, packets):
        if self.n is not None:
            self.note("molt %s count %d %d %d %d" % (SLOT, self.n, kb, packets, self.d))

    def health(self, kb, packets):
        self.note("molt healthy %d" % self.n)
        self.count(kb, packets)
        self.line("S8: healthy %d" % self.n)

    def word(self, body, kb, packets, fetched=None, previous16=None):
        """A molt word: its count note first on a boot that loaded a part,
        then its answer. Returns the console's answer (None for the table)."""
        self.count(kb, packets)
        if body == "molt":
            return None
        if body == "molt " + SLOT:
            note = self.p.install_note(SLOT, fetched, self.p.FIXTURES[self.p.check_part(fetched, SLOT)["name"]])
            self.note(note)
            return "part %s shadow %s" % (SLOT, note.split(" ")[3])
        if body == "molt take " + SLOT:
            answer = self.p.take_of(self.notes, SLOT)
        elif body == "molt undo":
            answer, _ = self.p.undo_of(self.notes, previous16)
        else:
            raise ValueError("not a word the checker types: %r" % body)
        if answer.startswith("molt "):
            self.note(answer)
        return answer

    def lines(self):
        """The ring 8a lines the boot prints, in order: each line, and each
        molt note's serial mirror."""
        return [t if k == "line" else self.p.serial_of(t) for k, t in self.items if k == "line" or t.startswith("molt ")]

    def new_notes(self):
        return [t for k, t in self.items if k == "note"]


def word_count(mark, text, parts_mod):
    """A word's count note carries the boot's keyboard bytes up to its
    Enter's make, not its break: sendkey holds a key 100 ms, and the word
    has run long before the break arrives."""
    return mark["kb"] + parts_mod.keyboard_bytes(text) - 1, mark["packets"]


def echo_of(texts):
    return b"".join(t.replace("\n", "\r\n").encode("ascii") for t in texts)


def notes_region(data):
    return metal.partition_bytes(data, metal.parse_gpt(data)["notes"])


def flip(disk, offset):
    """The liar's torn write from the host, between boots (plan decision 16's
    ("flip", offset)): bit 0 of one byte of the disk image."""
    with open(disk, "r+b") as fh:
        fh.seek(offset)
        b = fh.read(1)
        fh.seek(offset)
        fh.write(bytes([b[0] ^ 0x01]))


def app_rows(cells, obs):
    C, R = obs["app"]["cols"], obs["app"]["rows"]
    return [cells[r * C:(r + 1) * C].decode("ascii", "replace").rstrip() for r in range(R)]


# ------------------------------------------------------------ the judge --

class Fates:
    def __init__(self, parts_mod):
        self.p = parts_mod
        text = re.sub(r"\s+", " ", open(parts_mod.PARTS_DOC, encoding="utf-8").read())
        self.identity = re.search(r"The twin's identity is `(cpu [0-9a-f]{8} pci [0-9a-f]{4}:[0-9a-f]{4}:[0-9a-f]{2})`",
                                  text).group(1)                        # PARTS.md's worked example, D4's run
        self.esc_hold_ms = int(re.search(r"The checker's hold, `sendkey esc (\d+)`", text).group(1))   # D4's
        self.raw_entries = int(re.search(r"a \*\*raw ring\*\* of (\d+) entries", text).group(1))
        self.part_pair = ["part: %s %s" % (SLOT, l.split(": ", 1)[1]) for l in checkmetal.I8042_LINES]
        self.timings = []

    # -- around every boot
    def boot(self, disk, tag, steps, fate=None, hold_s=None):
        """Plan test 3's "around every boot": the ports free, the mock and
        the relay only for a boot that makes a request, a fresh stick copy;
        after it, the ports free again, the stick copy's tables unchanged,
        every note present before it unchanged byte for byte."""
        problems = []
        if not ports_free():
            return None, ["%s: a port is held before the boot" % tag]
        mock = relay = None
        record = os.path.join(MOLT_OUT, "broker.%s.jsonl" % tag)
        if fate is not None:
            relay, err = checkmetal.start_relay(os.path.join(MOLT_OUT, "relay.%s.jsonl" % tag))
            if err is None:
                mock, err = start_molt(fate, record, hold_s)
            if err:
                checkglass.stop_mock(mock)
                checkglass.stop_mock(relay)
                return None, ["%s: %s" % (tag, err)]
        copy = checkmetal.fresh_stick(os.path.join(MOLT_OUT, "stick.%s.img" % tag))
        before = checkdisk.read_image(disk)
        n_before = None if metal.classify(before) == "blank" else len(checkdisk.parse_notebook(notes_region(before)))
        human = Human8a(self.p)
        broker = "nothing listening"
        if fate is not None:
            broker = "the relay and molt.py --mock --part %s%s" % (fate, " --hold-s %d" % hold_s if hold_s else "")
        say("--- boot %s: -smp %d, %s, %s ---" % (tag, FATES_SMP, os.path.relpath(disk, REPO), broker))
        capture, reads, err = human.run(FATES_SMP, disk, copy, steps, os.path.join(MOLT_OUT, "serial.%s.txt" % tag), tag)
        checkglass.stop_mock(mock)
        checkglass.stop_mock(relay)
        reads["record"] = record
        if err:
            problems.append(err)
            checkglass.dump_capture(capture)
        if not ports_free():
            problems.append("%s: a port is still held after the boot" % tag)
        if err:
            reads = None                         # a step failed: its error and the capture are the judgement
        problems += checkmetal.check_stick_tables_unchanged(copy, tag, STICK)
        os.remove(copy)                          # 64 MB a boot; its tables are judged
        if n_before is not None:
            a, b = notes_region(before), notes_region(checkdisk.read_image(disk))
            if a[:(1 + n_before) * metal.SECTOR] != b[:(1 + n_before) * metal.SECTOR]:
                problems.append("%s: a note present before the boot changed" % tag)
        at = human.reads["at"]
        self.timings.append("%s %.1f s%s" % (tag, human.reads.get("wall", 0), "".join(
            ", %s +%.1f s" % (k, v - at["start"]) for k, v in at.items() if k != "start")))
        if reads is None:
            return None, problems
        reads["capture"] = capture
        reads["n_before"] = n_before
        reads["tag"] = tag
        return reads, problems

    def notes(self, disk):
        return checkdisk.parse_notebook(notes_region(checkdisk.read_image(disk)))

    # -- the judgements
    def segment(self, reads, i, end=None):
        cap = reads["capture"]
        segs = reads["segments"] + [len(cap)]
        return cap[segs[i]:segs[i + 1] if end is None else end]

    def judge(self, seg, book, notebook_want, echo, live=False, packets=False, blank=False, label=""):
        """One boot's serial segment: the S7: lines by the frozen 7c check
        (the part's pair standing where the generic's stands on a live
        boot), the ring 8a lines exactly as the book says, the echo."""
        problems = []
        if packets:
            p, seg = checkmetal.strip_mouse_line(seg)
            problems += p
        elif checkmetal.MOUSE_LINE_BYTES in seg:
            problems.append("%s: '%s' with no packet sent" % (label, checkmetal.MOUSE_LINE))
        text = seg.decode("utf-8", "replace").replace("\r", "").split("\n")
        generic = [l for l in text if l.startswith("i8042: ")]
        got = [m.group(0).decode("ascii", "replace") for m in RAW_8A.finditer(seg)]    # before the pair is swapped
        if live:
            if generic:
                problems.append("%s: the generic's i8042: lines on a live boot: %r" % (label, generic))
            for pl, gl in zip(self.part_pair, checkmetal.I8042_LINES):
                seg = seg.replace((pl + "\r\n").encode(), (gl + "\r\n").encode(), 1)
        more, geometry = checkmetal.check_boot_lines(seg, FATES_SMP, blank, notebook_want, 0, checkmetal.DISK_SECTORS)
        problems += ["%s: %s" % (label, m) for m in more]
        want = book.lines()
        if got != want:
            problems.append("%s: the ring 8a lines are %r, want %r" % (label, got, want))
        marker = checkmetal.READY + b"\r\n"
        at = seg.find(marker)
        if at >= 0:
            tail = seg[at + len(marker):]
            tail = re.sub(rb"(?:S8|molt): [^\r\n]*\r\n", b"", tail)
            if echo is not None and tail != echo:
                problems.append("%s: after the ready line the serial channel carries %r, want %r" % (label, tail[:200], echo[:200]))
        return problems

    def conv(self, reads, label, want):
        r = reads.get(label)
        where = "%s %s" % (reads.get("tag"), label)
        if not r:
            return ["%s: the surfaces were not read" % where]
        return checktrials.check_conv_tail(r["conversation"], r["obs"], want, where)

    def table(self, reads, label, rows):
        r = reads.get(label)
        where = "%s %s" % (reads.get("tag"), label)
        if not r:
            return ["%s: the app panel was not read" % where]
        got = app_rows(r["app"], r["obs"])
        if got[:len(rows)] != rows or any(got[len(rows):]):
            return ["%s: the app panel holds %r, want the table %r" % (where, [g for g in got if g], rows)]
        return []

    def check_notes(self, disk, before, book, label):
        got = self.notes(disk)
        want = before + book.new_notes()
        if got != want:
            return ["%s: the notebook's new notes are %r, want %r" % (label, got[len(before):], want[len(before):])]
        return []

    def check_fetch(self, reads, fate, label):
        """The mock's record: the request by PARTS.md's rule with the twin's
        identity, the key, and the frame it sent equal to
        parts.fixture_frame(fate) byte for byte - the mock never trusted."""
        entries = []
        try:
            entries = [json.loads(l) for l in open(reads["record"]).read().splitlines() if l.strip()]
        except (OSError, ValueError) as exc:
            return ["%s: the mock's record: %s" % (label, exc)]
        grows = [e for e in entries if "frame" in e]
        if len(grows) != 1:
            return ["%s: the mock recorded %d molt request(s), want 1" % (label, len(grows))]
        e = grows[0]
        problems = []
        if e.get("text") != self.p.request_body(SLOT, self.identity):
            problems.append("%s: the request was %r, want %r" % (label, e.get("text"), self.p.request_body(SLOT, self.identity)))
        if e.get("identity") != self.identity or e.get("key") != self.p.molt_key(SLOT, self.identity):
            problems.append("%s: the identity %r and key %r are not the twin's" % (label, e.get("identity"), e.get("key")))
        if bytes.fromhex(e.get("frame") or "") != self.p.fixture_frame(fate):
            problems.append("%s: the frame the mock sent is not parts.fixture_frame(%r)" % (label, fate))
        return problems

    def fail(self, problems, what):
        return report(what, problems)

    # -- a disk
    def new_disk(self, name):
        """A fresh 64 MB file booted blank once (nineteen lines), then the
        seed notebook written from the host by NOTEBOOK.md's format."""
        disk = os.path.join(MOLT_OUT, "disk.%s.img" % name)
        checkmetal.fresh_disk(disk)
        reads, problems = self.boot(disk, name + "0", [("ready", "ready"), ("sleep", 1.0)])
        if reads:
            book = Book(self.p, [])
            problems += self.judge(reads["capture"], book, "formatted", b"", blank=True, label=name + "0")
        if not self.fail(problems, "disk %s's blank boot is not ring 7d's" % name):
            return None
        data = bytearray(checkdisk.read_image(disk))
        first = metal.parse_gpt(bytes(data))["notes"][0]
        if checkdisk.parse_notebook(notes_region(bytes(data))):
            self.fail(["disk %s: the blank boot left notes" % name], "the seed notebook")
            return None
        for seq, text in enumerate(seed_notes(), 1):
            at = (first + seq) * metal.SECTOR
            data[at:at + metal.SECTOR] = checknotes.expected_record(seq, text)
        with open(disk, "wb") as fh:
            fh.write(bytes(data))
        if self.notes(disk) != seed_notes():
            self.fail(["disk %s: the seed notebook does not read back" % name], "the seed notebook")
            return None
        say("disk %s: formatted by its blank boot; %d notes written from the host, ending %r"
            % (name, len(seed_notes()), seed_notes()[-1]))
        return disk

    def build16(self, fate):
        return self.p.sha16(hashlib.sha256(self.p.fixture(fate)).hexdigest())

    def install_boot(self, disk, tag, fate, boot=None, live_build=None):
        """The fetch: "! molt i8042" through the relay to the mock, the part
        stored and its install note. On a boot that loaded a live part (H's
        first), its lines and its count note come first."""
        before = self.notes(disk)
        line = "! molt %s\n" % SLOT
        steps = [("ready", "ready"), ("mark", "w"), ("keys", line),
                 ("await", rb"molt: %s shadow [0-9a-f]{16} " % SLOT.encode(), ANSWER_S, "installed", None),
                 ("sleep", WORD_S), ("surfaces", "w")]
        reads, problems = self.boot(disk, tag, steps, fate=fate)
        if reads is None:
            return self.fail(problems, "%s: the install" % tag)
        book = Book(self.p, before, boot)
        if boot is not None:
            book.loaded("live", live_build, self.part_pair)
        kb, pk = word_count(reads["marks"]["w"], line, self.p)
        answer = book.word(line[2:-1], kb, pk, fetched=self.p.fixture(fate))
        problems += self.judge(reads["capture"], book, "%d notes" % len(before), echo_of([line]), live=boot is not None, label=tag)
        problems += self.conv(reads, "w", ["> " + line[:-1], answer, ">"])
        problems += self.check_notes(disk, before, book, tag)
        problems += self.check_fetch(reads, fate, tag)
        ok = self.fail(problems, "%s: the install is not what PARTS.md says" % tag)
        if ok:
            say("%s: 'part %s shadow %s' on the console, its install note journaled, the frame the mock sent "
                "parts.fixture_frame(%r) byte for byte, the request and key the twin's (%s)"
                % (tag, SLOT, self.build16(fate), fate, self.identity))
        return ok

    def shadow_boot(self, disk, tag, n, fate, take=False, with_q=False, start=0):
        """A shadow boot: a third of good's threshold, or all of a one-boot
        threshold, typed as notes and wiggled; a click on "! grow" and
        " molt" (the table); the health mark; the take if asked."""
        before = self.notes(disk)
        B, K, M = self.p.FIXTURES[fate]
        kb_want, pk_want = -(-K // B), -(-M // B)
        notes, _ = typed_notes(kb_want, start, self.p)
        if with_q:
            notes = [Q_NOTE] + notes
        wiggles = pk_want + (pk_want % 2)
        steps = [("ready", "ready")] + [("keys", t + "\n") for t in notes] + [
            ("wiggle", wiggles), ("click", "key", ord("!")), ("mark", "w1"), ("keys", " molt\n"),
            ("sleep", WORD_S), ("surfaces", "w1"), ("mark", "idle"),
            ("await", rb"S8: healthy %d\r\n" % n, self.p.HEALTH_S + HEALTH_SLACK_S, "healthy", "ready")]
        take_line = "! molt take %s\n" % SLOT
        if take:
            steps += [("mark", "w2"), ("keys", take_line), ("sleep", WORD_S), ("surfaces", "w2")]
        reads, problems = self.boot(disk, tag, steps)
        if reads is None:
            return self.fail(problems, "%s: the shadow boot" % tag), None
        build = self.build16(fate)
        book = Book(self.p, before, n)
        book.loaded("shadow", build, self.part_pair)
        text = ""
        for t in notes:
            for ch in t + "\n":
                text += ch
                if ch == "q" and fate == "wrong":
                    book.d += 1
                    book.note("molt %s disagree %d %d %s %s" % (SLOT, n, len(text), self.p.ev_key(ord("q")), self.p.ev_key(ord("w"))))
            book.note(t)
        kb, pk = word_count(reads["marks"]["w1"], " molt\n", self.p)
        book.word("molt", kb, pk)
        table = self.p.table_of(book.notes)
        idle = reads["marks"]["idle"]
        book.health(idle["kb"], idle["packets"])
        answer = None
        if take:
            kb, pk = word_count(reads["marks"]["w2"], take_line, self.p)
            answer = book.word(take_line[2:-1], kb, pk)
        echo = echo_of([t + "\n" for t in notes]) + b"!" + echo_of([" molt\n"] + ([take_line] if take else []))
        problems += self.judge(reads["capture"], book, "%d notes" % len(before), echo, packets=True, label=tag)
        found = reads.get("found", {}).get("healthy")
        if found and found[0] < idle["pos"]:
            problems.append("%s: the health mark came before the input ended - the boot's counts are not the model's" % tag)
        problems += self.conv(reads, "w1", ["> ! molt", ">"])
        problems += self.table(reads, "w1", table)
        if take:
            problems += self.conv(reads, "w2", ["> " + take_line[:-1], answer, ">"])
        problems += self.check_notes(disk, before, book, tag)
        ok = self.fail(problems, "%s: the shadow boot is not what PARTS.md says" % tag)
        if ok:
            c = [p for p in self.p.notes_molt(book.notes) if p["kind"] == "count"][-1]
            say("%s: shadow %s, boot %d: %d keyboard bytes and %d packets fed, %d disagreement(s), the generic's pair; "
                "the notes journaled as typed; a click on '! grow' and the table %r; 'S8: healthy %d'%s"
                % (tag, build, n, c["keys"], c["packets"], c["disagree"], table, n,
                   "; the take: %r" % answer if take else ""))
        return ok, answer

    def trigger_boot(self, disk, tag, n, fate):
        """The live boot of hang or fault: the trigger, the reset within
        RESET_S, the recovery within RECOVER_S, the generic serving after."""
        before = self.notes(disk)
        build = self.build16(fate)
        if fate == "hang":
            keys = "".join(chr(ord("a") + i % 26) for i in range(self.p.HANG_BYTE // self.p.key_bytes("a")))
            trigger = [("mark", "trigger_at"), ("keys", keys, "trigger")]
        else:
            trigger = [("mark", "trigger_at"), ("wiggle", 1, "trigger")]
        note = TYPED[0]
        steps = [("ready", "ready")] + trigger + [
            ("banner", RESET_S, "banner", "trigger"),
            ("await", rb"S8: recovery %s watchdog\r\n" % SLOT.encode(), RECOVER_S, "recovered", "banner"),
            ("ready", "ready2"), ("keys", note + "\n"), ("click", "key", ord("!")), ("mark", "w1"), ("keys", " molt\n"),
            ("sleep", WORD_S), ("surfaces", "w1")]
        reads, problems = self.boot(disk, tag, steps)
        if reads is None:
            return self.fail(problems, "%s: the %s boot" % (tag, fate))
        at = reads["at"]
        pos = reads["marks"]["trigger_at"]["pos"]
        live = Book(self.p, before, n)
        live.loaded("live", build, self.part_pair)
        seg1 = self.segment(reads, 0)
        problems += self.judge(seg1[:pos], live, "%d notes" % len(before), b"", live=True, label=tag + " before the trigger")
        after_trigger = seg1[pos:]
        errs = [m.group(0).decode() for m in re.finditer(rb"ERR: [^\r\n]*", after_trigger)]
        if fate == "hang":
            echo = re.sub(rb"(?:S8|molt): [^\r\n]*\r\n", b"", after_trigger)
            done = (self.p.HANG_BYTE - 1) // self.p.key_bytes("a")
            if errs or not (keys.encode()[:done] == echo[:done] and keys.encode().startswith(echo)):
                problems.append("%s: after the trigger the capture holds %r, want the echo of at least the first %d keys "
                                "and nothing else" % (tag, after_trigger[:120], done))
        else:
            want = self.p.blame_line(6, SLOT, self.p.ud2_offset(self.p.fixture(fate)))
            if len(errs) != 2 or not re.fullmatch(r"ERR: exception 6 at 0x[0-9a-f]+", errs[0]) or errs[1] != want:
                problems.append("%s: the lines after the first packet are %r, want exc_common's then %r" % (tag, errs, want))
        rec_notes = before + live.new_notes()
        decision = self.p.recovery_of(rec_notes, True)
        rec = Book(self.p, rec_notes)
        rec.line("S8: sha256 ok")
        for t in self.p.recovery_notes(decision):
            rec.note(t)
        rec.line(self.p.recovery_line(decision))
        rec.note(note)
        kb, pk = word_count(reads["marks"]["w1"], " molt\n", self.p)
        rec.word("molt", kb, pk)
        problems += self.judge(self.segment(reads, 1), rec, "%d notes" % len(rec_notes), echo_of([note + "\n"]) + b"!" + echo_of([" molt\n"]),
                               packets=True, label=tag + " after the reset")
        problems += self.table(reads, "w1", self.p.table_of(rec.notes))
        if at["banner"] - at["trigger"] > RESET_S:
            problems.append("%s: the reset came %.1f s after the trigger, RESET_S is %.1f" % (tag, at["banner"] - at["trigger"], RESET_S))
        want_notes = Book(self.p, before)
        want_notes.items = live.items + rec.items
        problems += self.check_notes(disk, before, want_notes, tag)
        ok = self.fail(problems, "%s: %s's fate is not what PARTS.md says" % (tag, fate))
        if ok:
            say("%s: %s live at boot %d; the trigger%s; OVMF's first byte %.1f s after it (RESET_S %.1f); '%s' %.1f s after "
                "that (RECOVER_S %.1f); '%s' journaled; the generic's pair; a note and a click; the table %r"
                % (tag, build, n, " (%s)" % errs[-1] if errs else "", at["banner"] - at["trigger"], RESET_S,
                   self.p.recovery_line(decision), at["recovered"] - at["banner"], RECOVER_S,
                   self.p.recovery_notes(decision)[0], self.p.table_of(rec.notes)))
        return ok

    def live_boot(self, disk, tag, n, build, words=(), held=False, fate="good"):
        """A live boot: the part's pair, the idle wait to the health mark,
        then a note and a click through the part, the table, and the words
        asked (and A1's held request)."""
        before = self.notes(disk)
        note = TYPED[1]
        steps = [("ready", "ready"),
                 ("await", rb"S8: healthy %d\r\n" % n, self.p.HEALTH_S + HEALTH_SLACK_S, "healthy", "ready"),
                 ("keys", note + "\n"), ("click", "key", ord("!")), ("mark", "w1"), ("keys", " molt\n"),
                 ("sleep", WORD_S), ("surfaces", "w1")]
        if held:
            # The wiggle during the hold: the raw ring holds raw_entries, and the
            # Enter's break takes one of them (sendkey holds a key 100 ms, and the
            # first move comes a key gap after the Enter), so the part is given
            # (raw_entries - 1) // 3 whole packets and the rest are lost.
            steps += [("ask_held", "held", HOLD_WIGGLES, (self.raw_entries - 1) // 3)]
        for i, w in enumerate(words, 2):
            steps += [("mark", "w%d" % i), ("keys", "! %s\n" % w), ("sleep", WORD_S), ("surfaces", "w%d" % i)]
        reads, problems = self.boot(disk, tag, steps, fate=fate if held else None,
                                    hold_s=self.p.HOLD_S if held else None)
        if reads is None:
            return self.fail(problems, "%s: the live boot" % tag)
        book = Book(self.p, before, n)
        book.loaded("live", build, self.part_pair)
        book.health(0, 0)
        book.note(note)
        kb, pk = word_count(reads["marks"]["w1"], " molt\n", self.p)
        book.word("molt", kb, pk)
        table = self.p.table_of(book.notes)
        echo = echo_of([note + "\n"]) + b"!" + echo_of([" molt\n"])
        if held:
            echo += echo_of(["? hold\n"])
        answers = []
        for i, w in enumerate(words, 2):
            kb, pk = word_count(reads["marks"]["w%d" % i], "! %s\n" % w, self.p)
            answers.append(book.word(w, kb, pk))
            echo += echo_of(["! %s\n" % w])
        cap = reads["capture"]
        problems += self.judge(cap, book, "%d notes" % len(before), echo, live=True, packets=True, label=tag)
        ready_at = cap.find(checkmetal.READY)
        found = reads.get("found", {}).get("healthy")
        if found and OVMF_START in cap[ready_at:found[0]]:
            problems.append("%s: an OVMF byte between the ready line and the health mark - the idle wait reset the machine" % tag)
        problems += self.conv(reads, "w1", ["> ! molt", ">"])
        problems += self.table(reads, "w1", table)
        for i, (w, a) in enumerate(zip(words, answers), 2):
            problems += self.conv(reads, "w%d" % i, ["> ! " + w, a, ">"])
        if held:
            h = reads.get("held")
            if not h:
                problems.append("%s: the held request was not measured" % tag)
            else:
                waited = h["t1"] - h["t0"]
                if waited < self.p.HOLD_S:
                    problems.append("%s: the held answer landed %.1f s after the Enter, under HOLD_S %d" % (tag, waited, self.p.HOLD_S))
                if OVMF_START in cap[h["pos0"]:h["pos1"]] or cap.count(b"S7: alive") != 1:
                    problems.append("%s: the machine reset during the held request%s"
                                    % (tag, " and its %d moves" % HOLD_WIGGLES if reads.get("held_moves") else ""))
                if reads.get("held_moves") != (HOLD_WIGGLES, (self.raw_entries - 1) // 3):
                    problems.append("%s: the held request's %d moves were not sent" % (tag, HOLD_WIGGLES))
                try:
                    entries = [json.loads(l) for l in open(reads["record"]).read().splitlines() if l.strip()]
                except (OSError, ValueError) as exc:
                    entries = []
                    problems.append("%s: the mock's record: %s" % (tag, exc))
                qs = [e for e in entries if e.get("question") == "hold"]
                if len(qs) != 1 or qs[0].get("answer") != h["answer"]:
                    problems.append("%s: the conversation's answer %r is not the one the mock recorded for 'hold'" % (tag, h["answer"]))
        problems += self.check_notes(disk, before, book, tag)
        ok = self.fail(problems, "%s: the live boot is not what PARTS.md says" % tag)
        if ok:
            say("%s: live %s, boot %d: the part's pair, idle to 'S8: healthy %d' with no reset; a note and a click "
                "through the part; the table %r%s%s"
                % (tag, build, n, n, table,
                   "; '? hold' answered %.1f s after its Enter (HOLD_S %d), %d moves during it (%d packets kept), "
                   "with no reset" % (reads["held"]["t1"] - reads["held"]["t0"], self.p.HOLD_S, HOLD_WIGGLES,
                                      (self.raw_entries - 1) // 3) if held else "",
                   "; %s" % "; ".join("%r -> %r" % (w, a) for w, a in zip(words, answers)) if words else ""))
        return ok

    # -- the five disks
    def disk_G(self):
        disk = self.new_disk("G")
        if not disk:
            return None
        good = self.build16("good")
        # G1, the install: the words on a boot that loaded nothing.
        before = self.notes(disk)
        lines = ["! molt\n", "molt x\n", "! molt %s\n" % SLOT, "! part-%s\n" % SLOT, "! molt take %s\n" % SLOT]
        steps = [("ready", "ready")]
        for i, l in enumerate(lines, 1):
            steps += [("mark", "w%d" % i), ("keys", l)]
            if l == "! molt %s\n" % SLOT:
                steps += [("await", rb"molt: %s shadow [0-9a-f]{16} " % SLOT.encode(), ANSWER_S, "installed", None)]
            steps += [("sleep", WORD_S), ("surfaces", "w%d" % i)]
        reads, problems = self.boot(disk, "G1", steps, fate="good")
        if reads is None:
            self.fail(problems, "G1")
            return None
        book = Book(self.p, before)
        table0 = self.p.table_of(book.notes)
        book.word("molt", 0, 0)
        problems += self.conv(reads, "w1", ["> ! molt", ">"]) + self.table(reads, "w1", table0)
        problems += self.conv(reads, "w2", ["> molt x", "molt is reserved", ">"])
        a3 = book.word("molt " + SLOT, 0, 0, fetched=self.p.fixture("good"))
        problems += self.conv(reads, "w3", ["> ! molt " + SLOT, a3, ">"])
        problems += self.conv(reads, "w4", ["> ! part-" + SLOT, "part-%s is a part" % SLOT, ">"])
        a5 = book.word("molt take " + SLOT, 0, 0)
        problems += self.conv(reads, "w5", ["> ! molt take " + SLOT, a5, ">"])
        if not a5.startswith("below threshold: "):
            problems.append("G1: the rules give the take %r, not the below-threshold refusal" % a5)
        if reads.get("w5", {}).get("obs", {}).get("errors") != 3:
            problems.append("G1: errors is %r after 'molt x', '! part-%s' and the take, want 3"
                            % (reads.get("w5", {}).get("obs", {}).get("errors"), SLOT))
        problems += self.judge(reads["capture"], book, "%d notes" % len(before), echo_of(lines), label="G1")
        problems += self.check_notes(disk, before, book, "G1")
        problems += self.check_fetch(reads, "good", "G1")
        if not self.fail(problems, "G1: the words and the install are not what PARTS.md says"):
            return None
        say("G1: '! molt' drew %r; 'molt x' refused 'molt is reserved'; '%s'; '! part-%s' refused; the take refused %r; "
            "errors 3; the frame the mock sent parts.fixture_frame('good'), the twin's request and key" % (table0, a3, SLOT, a5))
        # G2-G4, shadow; the take at G4.
        start = 0
        for n in (1, 2, 3):
            ok, answer = self.shadow_boot(disk, "G%d" % (n + 1), n, "good", take=(n == 3), start=start)
            if not ok:
                return None
            start += 5
        if answer != "molt %s live %s" % (SLOT, good):
            self.fail(["G4: the take answered %r, want the live note" % answer], "G4: the take")
            return None
        # G5, live: the idle wait, a held request, the undo and the take again.
        if not self.live_boot(disk, "G5", 4, good, words=("molt undo", "molt take " + SLOT), held=True):
            return None
        # G6, Esc held at power-on.
        before = self.notes(disk)
        note = TYPED[2]
        steps = [("await", rb"S8: sha256 ok\r\n", READY_S, "sha", "start"), ("hold_esc", self.esc_hold_ms),
                 ("ready", "ready"), ("sleep_since", "esc", self.esc_hold_ms / 1000.0 + SETTLE_S),
                 ("keys", note + "\n"), ("click", "key", ord("!")), ("mark", "w1"), ("keys", " molt\n"),
                 ("sleep", WORD_S), ("surfaces", "w1")]
        reads, problems = self.boot(disk, "G6", steps)
        if reads is None:
            self.fail(problems, "G6")
            return None
        book = Book(self.p, before)
        book.line("S8: sha256 ok")
        book.note("molt recovery owner")
        book.line("S8: recovery owner")
        book.note(note)
        book.word("molt", 0, 0)
        problems += self.judge(reads["capture"], book, "%d notes" % len(before), echo_of([note + "\n"]) + b"!" + echo_of([" molt\n"]),
                               packets=True, label="G6")
        problems += self.table(reads, "w1", self.p.table_of(book.notes))
        problems += self.check_notes(disk, before, book, "G6")
        if self.p.state_of(book.notes, SLOT) != ("live", good):
            problems.append("G6: the rules say the slot is %r after Esc, want still live" % (self.p.state_of(book.notes, SLOT),))
        if not self.fail(problems, "G6: Esc at power-on is not what PARTS.md says"):
            return None
        say("G6: Esc held from 'S8: sha256 ok' (sendkey esc %d): 'S8: recovery owner', 'molt recovery owner', no part, no "
            "watchdog, the generic's pair; a note and a click; nothing demoted: %r" % (self.esc_hold_ms, self.p.table_of(book.notes)))
        disk_h = os.path.join(MOLT_OUT, "disk.H.img")
        shutil.copyfile(disk, disk_h)
        say("disk H: copied from disk G after G6")
        # G7, live again: probation 2.
        if not self.live_boot(disk, "G7", 5, good):
            return None
        if self.p.probation_of(self.notes(disk), SLOT) != 2:
            self.fail(["G7: probation is %d by the rules, want 2" % self.p.probation_of(self.notes(disk), SLOT)], "G7")
            return None
        return disk_h

    def disk_W(self):
        disk = self.new_disk("W")
        if not disk or not self.install_boot(disk, "W1", "wrong"):
            return False
        ok, answer = self.shadow_boot(disk, "W2", 1, "wrong", take=True, with_q=True)
        if not ok:
            return False
        problems = []
        if answer != "disagreements 1":
            problems.append("W2: the rules give the take %r, want 'disagreements 1'" % answer)
        if self.p.state_of(self.notes(disk), SLOT)[0] != "shadow":
            problems.append("W2: the slot is not in shadow after the refused take")
        return self.fail(problems, "W: the wrong part's fate")

    def disk_H(self, disk):
        good, hang = self.build16("good"), self.build16("hang")
        if not self.install_boot(disk, "H1", "hang", boot=5, live_build=good):
            return False
        if self.p.state_of(self.notes(disk), SLOT) != ("shadow", hang):
            return self.fail(["H1: the slot is not hang's shadow by the rules"], "H1")
        ok, answer = self.shadow_boot(disk, "H2", 6, "hang", take=True, start=3)
        if not ok:
            return False
        if answer != "molt %s live %s" % (SLOT, hang):
            return self.fail(["H2: the take answered %r" % answer], "H2")
        return self.trigger_boot(disk, "H3", 7, "hang")

    def disk_F(self):
        disk = self.new_disk("F")
        if not disk or not self.install_boot(disk, "F1", "fault"):
            return False
        ok, answer = self.shadow_boot(disk, "F2", 1, "fault", take=True, start=7)
        if not ok:
            return False
        if answer != "molt %s live %s" % (SLOT, self.build16("fault")):
            return self.fail(["F2: the take answered %r" % answer], "F2")
        return self.trigger_boot(disk, "F3", 2, "fault")

    def disk_L(self):
        disk = self.new_disk("L")
        if not disk or not self.install_boot(disk, "L1", "liar"):
            return False
        data = checkdisk.read_image(disk)
        home = metal.parse_gpt(data)["home"]
        part, parsed = metal.partition_bytes(data, home), None
        problems = []
        try:
            parsed = checkplans.parse_home(part)
        except ValueError as exc:
            problems.append("L1: the home partition: %s" % exc)
        entry = next((e for e in (parsed or {}).get("entries", []) if e and e["name"] == "part-" + SLOT), None)
        liar = self.p.fixture("liar")
        if entry is None:
            problems.append("L1: no part-%s entry in the home store" % SLOT)
        elif checkplans.blob_of(part, entry["current"]) != liar:
            problems.append("L1: the stored build is not i8042-liar.bin")
        if not self.fail(problems, "L1: the stored part"):
            return False
        offset = (home[0] + entry["current"]["first"]) * metal.SECTOR + self.p.PART_HEADER
        flip(disk, offset)
        data = checkdisk.read_image(disk)
        stored = checkplans.blob_of(metal.partition_bytes(data, home), entry["current"])
        before = self.notes(disk)
        door = self.p.door_of(before, SLOT, entry, stored)
        if stored != self.p.liar_stored(liar) or door != "S8: part %s bad hash" % SLOT:
            return self.fail(["L1: the host's flip gave %r at the door, want the liar's stored bytes and 'bad hash'" % door], "the flip")
        say("L1: the host flipped bit 0 of the part's byte 96 on the image: stored %s..., the entry keeps %s...; by the "
            "rules the door says %r" % (hashlib.sha256(stored).hexdigest()[:16], entry["current"]["sha256"][:16], door))
        note = TYPED[3]
        steps = [("ready", "ready"), ("keys", note + "\n"), ("click", "key", ord("!")), ("mark", "w1"), ("keys", " molt\n"),
                 ("sleep", WORD_S), ("surfaces", "w1")]
        reads, problems = self.boot(disk, "L2", steps)
        if reads is None:
            return self.fail(problems, "L2")
        book = Book(self.p, before)
        book.line("S8: sha256 ok")
        book.line(door)
        book.note(note)
        book.word("molt", 0, 0)
        problems += self.judge(reads["capture"], book, "%d notes" % len(before), echo_of([note + "\n"]) + b"!" + echo_of([" molt\n"]),
                               packets=True, label="L2")
        problems += self.table(reads, "w1", self.p.table_of(book.notes))
        problems += self.check_notes(disk, before, book, "L2")
        ok = self.fail(problems, "L2: the liar at the door is not what PARTS.md says")
        if ok:
            say("L2: 'S8: sha256 ok', '%s', no watchdog, no boot note, the generic's pair; a note and a click; nothing "
                "demoted: %r" % (door, self.p.table_of(book.notes)))
        return ok


def boot_argv(smp, disk, stick_copy, serial_path, t):
    """The one place a fates boot's command is spelled: `timeout -k 5 <T>`
    before checkmetal.qemu_argv itself (plan decision 15). Test 4 (b)
    inspects this."""
    return ["timeout", "-k", "5", t] + checkmetal.qemu_argv(smp, disk, stick_copy, serial_path)


def molt_argv(fate, record, hold_s=None):
    """The one place the mock's command is spelled. Test 4 (b) inspects this."""
    argv = [sys.executable, MOLT_BROKER, "--mock", "--part", fate, "--port", str(checkmetal.BROKER_PORT),
            "--record", record, "--germline", MOLT_GERMLINE, "--image", ESP, "--workdir", MOLT_TWIN,
            "--rehearsal-port", str(checkmetal.REHEARSAL_PORT), "--plans", PLANS_DIR]
    if hold_s is not None:
        argv += ["--hold-s", "%d" % hold_s]
    return argv


def start_molt(fate, record, hold_s=None):
    """broker/molt.py --mock --part <fate> on 9999 with the gate's own
    germline, image and twin workdir (checkmetal.start_mock's lifecycle)."""
    for port in (checkmetal.BROKER_PORT, checkmetal.REHEARSAL_PORT):
        if checkglass.port_state(port) == "open":
            return None, "something is already listening on 127.0.0.1:%d" % port
    if os.path.exists(record):
        os.remove(record)
    log = open(os.path.join(MOLT_OUT, "mock.molt.stderr.txt"), "ab")
    proc = subprocess.Popen(molt_argv(fate, record, hold_s), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=log)
    deadline = time.time() + 10.0
    line = b""
    while time.time() < deadline:
        if proc.poll() is not None:
            return proc, "molt.py exited %d before listening" % proc.returncode
        r, _, _ = select.select([proc.stdout], [], [], 0.2)
        if r:
            line = proc.stdout.readline()
            break
    if line.strip() != ("listening on 127.0.0.1:%d" % checkmetal.BROKER_PORT).encode():
        checkglass.stop_mock(proc)
        return None, "molt.py did not say it was listening (got %r)" % line
    return proc, None


def point_molt_seams():
    """The frozen 7c helpers this test calls read their module paths at call
    time: the stick, the build and the relay's scratch go to stage8's."""
    for name, value in (("OUT", OUT), ("METAL_OUT", MOLT_OUT), ("STICK", STICK), ("EFI", EFI), ("ESP", ESP)):
        setattr(checkmetal, name, value)


def run_fates(overrides=()):
    err = apply_overrides(overrides)
    if err:
        say(err)
        return 1
    missing = unset_constants()
    if missing:
        say("the run constants %s are not set - they are written from item 12's run (plan item 10), never guessed"
            % ", ".join(missing))
        return 1
    if not (os.path.exists(STICK) and os.path.exists(EFI) and os.path.exists(ESP)):
        say("stage8/out/ lacks the stick, the build or esp.img - build with stage8/mkimage.sh and stage8/mkstick.py first")
        return 1
    if not ports_free():
        return 1
    try:
        import parts
    except (ValueError, KeyError, IndexError, TypeError, AttributeError, OSError) as exc:
        say("stage8/parts.py does not load the documents: %s" % exc)
        return 1
    bad = [t for t in TYPED + [Q_NOTE] if ":" in t or t.startswith(("molt ", "trial ", "!", "?"))]
    bad += [t for t in TYPED if "q" in t.lower()] + ([Q_NOTE] if Q_NOTE.lower().count("q") != 1 else [])
    if bad or len(seed_notes()) != 40:
        say("the checker's own texts break its rules: %r, %d seed notes" % (bad, len(seed_notes())))
        return 1
    shutil.rmtree(MOLT_OUT, ignore_errors=True)
    os.makedirs(MOLT_OUT)
    point_molt_seams()
    f = Fates(parts)
    t0 = time.time()
    results = {}
    say("=== disk G: good ===")
    disk_h = f.disk_G()
    results["G"] = disk_h is not None
    say("=== disk W: wrong ===")
    results["W"] = f.disk_W()
    say("=== disk H: hang in good's place ===")
    results["H"] = f.disk_H(disk_h) if disk_h else False
    if not disk_h:
        say("disk H was not made: disk G did not reach G6")
    say("=== disk F: fault ===")
    results["F"] = f.disk_F()
    say("=== disk L: liar ===")
    results["L"] = f.disk_L()
    say("the boots, wall time and the stamps from QEMU's start:")
    for t in f.timings:
        say("  " + t)
    say("the fates: %s in %.1f s" % (", ".join("%s %s" % (k, "ok" if v else "FAILED") for k, v in results.items()),
                                     time.time() - t0))
    return 0 if all(results.values()) else 1


# ---------------------------------------------------- test 4: the cage ------
# (a) is test-8a.sh's own strings and (d) its run of ./stage7/test-7d.sh.
# Here: (b) the argv check - a fates boot's command is `timeout -k 5 <T>`
# before checkmetal.qemu_argv itself with the stage8 paths, passed through
# the frozen check_argv_7c; the flags check_argv_7c does not inspect (D4:
# -icount, noreboot, -action) refused here; the mock's command; the ports
# the frozen modules hold. (c) the payload table as a subprocess, 0 wrong,
# and the spot checks held as data: every ring 8a frozen path, loader.asm
# among them, denied every mutation and readable; the owner's directory
# rule of 25 September 2026 in his own examples; running the gate, the
# checker, the tools and the builders allowed, and writing the builder.

FIXTURES_8A = ["stage8/fixtures/i8042-%s.%s" % (f, x) for f in ("good", "wrong", "hang", "fault", "liar") for x in ("asm", "bin")]
FROZEN_8A = ["stage8/PARTS.md", "stage8/SEED.md", "stage8/parts.py", "stage8/test-8a.sh", "stage8/checkmolt.py"] + FIXTURES_8A \
    + ["stage8/loader.asm"]
SPOT_DENY_8A = [c for p in FROZEN_8A for c in (
    "echo x > %s" % p, "sed -i 's/a/b/' %s" % p, "cp /tmp/x %s" % p, "rm -f %s" % p,
    "python3 - <<'EOF'\nopen('%s','w').write('x')\nEOF" % p)] + [
    "nasm -f bin stage8/fixtures/i8042-%s.asm -o stage8/fixtures/i8042-%s.bin" % (f, f)
    for f in ("good", "wrong", "hang", "fault", "liar")] + [
    # the owner's directory rule (HANDOVER, ring 8a item 3), every category of
    # the decision (Cowork's review of item 11): a directory holding a frozen file
    "rm -rf stage7", "mv stage7 old7", "git rm -r stage8/fixtures", "rm -rf stage8/fixtures", "rm -rf stage8",
    "rm -r broker",
    # the repo root, relative and absolute
    "rm -rf .", "rm -rf %s" % REPO,
    # a glob that covers a frozen file
    "rm -rf stage*", "rm stage8/fixtures/*", "rm -f stage8/*.md", "mv stage8/fixtures/* /tmp",
    # rmdir and git mv
    "rmdir stage8/fixtures", "git mv stage7 old7", "git mv stage8/fixtures old",
    # a directory by a trailing slash and by its absolute path
    "rm -r stage7/", "rm -rf %s" % os.path.join(REPO, "stage8", "fixtures"),
]
SPOT_ALLOW_8A = [
    "./stage8/test-8a.sh", "./stage8/test-8a.sh 2>&1 | tail -20",
    "python3 stage8/checkmolt.py --document", "python3 stage8/checkmolt.py --seven",
    "python3 stage8/checkmolt.py --fates", "python3 stage8/checkmolt.py --cage",
    "python3 stage8/parts.py --example", "python3 stage8/parts.py --disk stage8/out/molt/disk.G.img",
    "python3 stage8/parts.py --serial stage8/out/hp-8a.log", "python3 stage8/parts.py --seed",
    "cat stage8/PARTS.md | head", "grep -n 'molt' stage8/checkmolt.py", "xxd stage8/fixtures/i8042-liar.bin | head",
    "nasm -f bin stage8/fixtures/i8042-good.asm -o stage8/out/i8042-good.check.bin",
    "tail -5 stage8/out/gate-8a.log", "echo x >> stage8/out/gate-8a.log",
    "./stage8/mkimage.sh", "python3 stage8/mkstick.py", "python3 broker/molt.py --mock --part hang",
    "rm -rf stage8/out/molt stage8/out/probe8a", "rm -rf stage8/out", "rm -f stage8/out/i8042-good.check.bin",
    "mv stage8/HP-8a.md stage8/HP-8a.draft.md",
    # the allowed side of the owner's directory rule: an ordinary file beside
    # frozen files removed or moved, and stage8/out wiped by a glob
    "rm -f stage8/HP-8a.md", "git mv stage8/HP-8a.md stage8/HP-8a.old.md", "mv broker/molt.py /tmp/molt.py.bak",
    "rm -rf stage8/out/*",
    "git add stage8/PARTS.md stage8/checkmolt.py", "git commit -F msg.txt", "./stage7/test-7d.sh",
]
WRITE_ALLOW_8A = ["stage8/stage8.asm", "stage8/mkimage.sh", "stage8/mkstick.py", "broker/molt.py", "stage8/seed-record.md",
                  "stage8/HP-8a.md", "stage8/plan-8a.md", "HANDOVER.md"]
RELAY_PORT_8A = PORTS[2]
ARGV_REFUSED_8A = ("-icount", "-global", "-action", "-watchdog", "-watchdog-action", "-no-reboot", "-accel", "-enable-kvm")


def tool_verdict(tool, tool_input):
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input})
    r = subprocess.run([sys.executable, checkmetal.HOOK], input=payload.encode(), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO))
    return {0: "ALLOW", 2: "DENY"}.get(r.returncode, "EXIT %d" % r.returncode)


def check_argv_8a():
    """(b): the fates' own commands, built by the functions the fates call."""
    point_molt_seams()
    disk = os.path.join(MOLT_OUT, "disk.G.img")
    copy = os.path.join(MOLT_OUT, "stick.G1.img")
    serial = os.path.join(MOLT_OUT, "serial.G1.txt")
    t = "%d" % BOOT_T_S if BOOT_T_S is not None else "BOOT_T_S"
    argv = boot_argv(FATES_SMP, disk, copy, serial, t)
    problems = []
    if argv[:3] != ["timeout", "-k", "5"] or argv.count("timeout") != 1:
        problems.append("a boot's command does not begin 'timeout -k 5 <T>' once: %r" % argv[:5])
    if BOOT_T_S is not None and not (isinstance(BOOT_T_S, int) and BOOT_T_S > 0):
        problems.append("BOOT_T_S is not a positive whole number of seconds: %r" % BOOT_T_S)
    qemu = argv[4:]
    if qemu != checkmetal.qemu_argv(FATES_SMP, disk, copy, serial):
        problems.append("after the timeout prefix, a boot's command is not checkmetal.qemu_argv itself")
    problems += checkmetal.check_argv_7c(qemu, RELAY_PORT_8A, checkmetal.MAC)
    for flag in ARGV_REFUSED_8A:
        if flag in qemu:
            problems.append("the command carries %s - check_argv_7c does not inspect it (D4), so it is refused here" % flag)
    for word in ("noreboot", "i6300esb"):
        if [a for a in qemu if word in a]:
            problems.append("the command names %s - D1 chose the ICH9 TCO with no flag" % word)
    if "-smp" not in qemu or qemu[qemu.index("-smp") + 1] != "4":
        problems.append("the fates do not run at -smp 4")
    for path in (disk, copy, serial):
        if not path.startswith(MOLT_OUT + os.sep):
            problems.append("a boot's file is not under stage8/out/molt/: %s" % path)
    m = molt_argv("hang", os.path.join(MOLT_OUT, "broker.H1.jsonl"), 60)
    opt = {m[i]: m[i + 1] for i in range(2, len(m) - 1) if m[i].startswith("--") and not m[i + 1].startswith("--")}
    if m[1] != MOLT_BROKER or "--mock" not in m:
        problems.append("the broker is not broker/molt.py --mock: %r" % m[:3])
    if opt.get("--port") != "9999" or opt.get("--rehearsal-port") != "9998" or opt.get("--part") != "hang":
        problems.append("the mock is not on 9999 with its twin on 9998: %r" % m)
    for key in ("--record", "--germline", "--image", "--workdir"):
        if not opt.get(key, "").startswith(OUT + os.sep):
            problems.append("the mock's %s is not under stage8/out/: %r" % (key, opt.get(key)))
    if opt.get("--plans") != PLANS_DIR or "--model" in m:
        problems.append("the mock reads plans other than the repository's, or names a model: %r" % m)
    import wire
    if (checkmetal.BROKER_PORT, checkmetal.REHEARSAL_PORT, checkmetal.RELAY_PORT) != PORTS or PORTS != (9999, 9998, 9997):
        problems.append("the frozen 7c ports are not 9999, 9998 and 9997")
    if twin.DEFAULT_PORT != 9998 or wire.RELAY_PORT != 9997 or twin.VGA_ARGS != checkmetal.DISPLAY:
        problems.append("the frozen modules' ports or display are not ring 7c's")
    return problems


def check_bodyguard_8a():
    """(c): the payload table whole, then the spot checks as data."""
    problems = []
    r = subprocess.run([sys.executable, checkmetal.PAYLOADS], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    m = re.fullmatch(r"(\d+) payloads: (\d+) must be denied, (\d+) must be allowed, (\d+) wrong", last)
    if r.returncode != 0 or not m or m.group(4) != "0":
        problems.append("the payload table: exit %d, last line %r - want exit 0 and 0 wrong" % (r.returncode, last))
        for line in r.stdout.splitlines():
            if line.startswith("  WRONG"):
                problems.append("  " + line.strip())
    else:
        say("the payload table: %s" % last)
    for p in FROZEN_8A:
        for path in (p, os.path.join(REPO, p)):
            for tool, ti in (("Write", {"file_path": path, "content": "x"}),
                             ("Edit", {"file_path": path, "old_string": "a", "new_string": "b"})):
                v = tool_verdict(tool, ti)
                if v != "DENY":
                    problems.append("the hook %ss %s on %s - every ring 8a frozen path must be frozen" % (v.lower(), tool, path))
        v = tool_verdict("Read", {"file_path": os.path.join(REPO, p)})
        if v != "ALLOW":
            problems.append("the hook %ss Read on %s - a frozen file stays readable" % (v.lower(), p))
    for p in WRITE_ALLOW_8A:
        v = tool_verdict("Write", {"file_path": p, "content": "x"})
        if v != "ALLOW":
            problems.append("the hook %ss Write on %s - the builder, the mock and the records are never frozen" % (v.lower(), p))
    for c in SPOT_DENY_8A:
        v = checkmetal.hook_verdict(c)
        if v != "DENY":
            problems.append("the hook %ss %r - every mutation of a ring 8a frozen path must be denied" % (v.lower(), c))
    for c in SPOT_ALLOW_8A:
        v = checkmetal.hook_verdict(c)
        if v != "ALLOW":
            problems.append("the hook %ss %r - running the gate, the checker, the tools and the builders must be allowed"
                            % (v.lower(), c))
    return problems


def run_cage():
    problems = check_argv_8a()
    if not report("the checker's commands are not the twin of the HP", problems):
        return 1
    say("the checker's QEMU command is 'timeout -k 5 %s' before checkmetal.qemu_argv itself: one restricted cage to the relay "
        "on %d, the e1000e with %s, -cpu IvyBridge, the display, the stick copy over xhci, the SATA disk on ide.1, two drives "
        "under stage8/out/molt/, no esp.img, -smp %d; none of %s, no noreboot, no i6300esb; the mock on %d with its twin on %d, "
        "its files under stage8/out/"
        % (BOOT_T_S if BOOT_T_S is not None else "<BOOT_T_S, item 12's>", RELAY_PORT_8A, checkmetal.MAC, FATES_SMP,
           " ".join(ARGV_REFUSED_8A), checkmetal.BROKER_PORT, checkmetal.REHEARSAL_PORT))
    problems = check_bodyguard_8a()
    ok = report("the bodyguard does not freeze ring 8a's paths", problems)
    if ok:
        say("the bodyguard: the %d ring 8a frozen paths denied Write and Edit (relative and absolute) and %d spellings, readable; "
            "the builder's %d files writable; %d shapes of running and building allowed"
            % (len(FROZEN_8A), len(SPOT_DENY_8A), len(WRITE_ALLOW_8A), len(SPOT_ALLOW_8A)))
    say("the cage: %s" % ("held, and the criteria frozen" if ok else "not proven"))
    return 0 if ok else 1


# --------------------------------------------------------------- main ------

def main(argv):
    modes = {"--document": run_document, "--seven": run_seven, "--fates": run_fates, "--cage": run_cage}
    sets = argv[1:]
    if not argv or argv[0] not in modes or (sets and (argv[0] != "--fates" or len(sets) % 2
                                                      or any(a != "--set" for a in sets[0::2]))):
        say("usage: checkmolt.py --document | --seven | --fates [--set NAME=VALUE ...] | --cage")
        return 1
    os.makedirs(OUT, exist_ok=True)
    tee = tee_log(" ".join(argv))
    try:
        if argv[0] == "--fates":
            return run_fates(sets[1::2])
        return modes[argv[0]]()
    finally:
        untee(tee)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
