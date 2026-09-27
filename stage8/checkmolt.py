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
import os
import re
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

LINE_8A = re.compile(rb"(?<![A-Za-z0-9_-])((?:S8|part|molt): [^\r\n]*)")   # anywhere, not only at a line's start
ANSI = re.compile(rb"\x1b\[[0-9;?]*[A-Za-z]")                                  # the firmware's escapes, read as line breaks


def lines_8a(data):
    return [m.group(1) for m in LINE_8A.finditer(ANSI.sub(b"\n", data))]


# ------------------------------------------------------------- the log ----

def commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else "none"


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


# --------------------------------------------------------------- main ------

def main(argv):
    modes = {"--document": run_document, "--seven": run_seven}
    if len(argv) != 1 or argv[0] not in modes:
        say("usage: checkmolt.py --document | --seven")
        return 1
    os.makedirs(OUT, exist_ok=True)
    tee = tee_log(argv[0])
    try:
        return modes[argv[0]]()
    finally:
        untee(tee)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
