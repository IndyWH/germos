#!/usr/bin/env python3
"""stage8/checkmolt8b.py - ring 8b's acceptance checks (stage8/plan-8b.md).

Modes: --document (test 1), --pipeline (test 2), --shadow (test 3), --cage
(test 4's own checks; test-8b.sh then runs ring 8t's gate), and --stub, which
stands in for the word `claude` in test 1 and spends nothing.

Mock and collect only: nothing here spends a token. Frozen at item 14. The
numbers are from runs, never from arithmetic.
"""

import hashlib
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "stage8", "out")
WORK = os.path.join(OUT, "molt8b")
EFI = os.path.join(OUT, "BOOTX64.EFI")
STICK = os.path.join(OUT, "stick.img")
ESP = os.path.join(OUT, "esp.img")
PLAN = os.path.join(REPO, "plans", "parts", "i8042.md")
PARTS_MD = os.path.join(HERE, "PARTS.md")
BENCH_ASM = os.path.join(HERE, "bench.asm")
MOLT_PY = os.path.join(REPO, "broker", "molt.py")
FIX = os.path.join(HERE, "fixtures")
HP_IDENTITY = "cpu 000306a9 pci 8086:1e47:04"
SLOT = "i8042"
CANNED = ("fast", "slow", "sick")

# From the runs of items 5 and 12, never from arithmetic.
RUN_FAST = {"generic": {"median": 17, "worst": 27, "size": 1152}, "part": {"median": 13, "worst": 20, "size": 1160}}
RUN_SLOW = {"median": 21, "worst": 31, "size": 1152}
RUN_NULL = 13
RUN_CORPUS_BYTES = 7896

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "broker"))


def say(line):
    print("    " + line, flush=True)


def report(problems, ok_line):
    if problems:
        for p in problems:
            print("    - " + p, flush=True)
        return False
    say(ok_line)
    return True


def grow(args, env=None):
    """broker/molt.py --grow, whole output returned."""
    cmd = [sys.executable, MOLT_PY, "--grow", SLOT] + args
    e = dict(os.environ) if env is None else env
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=e, cwd=REPO)
    return p.returncode, p.stdout


# ------------------------------------------------- test 1: the documents ---

def check_pe(path):
    data = open(path, "rb").read()
    problems = []
    if data[:2] != b"MZ":
        return ["%s does not begin MZ" % path]
    lfa, = struct.unpack_from("<I", data, 60)
    if data[lfa:lfa + 4] != b"PE\0\0":
        return ["no PE signature at e_lfanew"]
    machine, = struct.unpack_from("<H", data, lfa + 4)
    chars, = struct.unpack_from("<H", data, lfa + 22)
    magic, = struct.unpack_from("<H", data, lfa + 24)
    subsystem, = struct.unpack_from("<H", data, lfa + 92)
    if machine != 0x8664 or magic != 0x20B or subsystem != 10 or chars & 3 != 3:
        problems.append("the PE fields are not an x86-64 PE32+ EFI application with relocations stripped")
    return problems


def corpus_problems(plan):
    pairs = plan["pairs"]
    p = []
    kb = [b for s, b in pairs if s == 0x15]
    ms = [b for s, b in pairs if s == 0x35]
    if len(kb) + len(ms) != len(pairs):
        p.append("a status is neither the keyboard's 0x15 nor the mouse's 0x35")
    if abs(len(kb) - len(ms)) > 3:
        p.append("keyboard %d and mouse %d bytes are not near equal" % (len(kb), len(ms)))
    if set(range(256)) - set(kb):
        p.append("not every byte value occurs on the keyboard")
    e0 = {kb[i + 1] for i in range(len(kb) - 1) if kb[i] == 0xE0}
    if set(range(256)) - e0:
        p.append("E0 is not before every byte value")
    if not any(kb[i:i + 6] == [0xE1, 0x1D, 0x45, 0xE1, 0x9D, 0xC5] for i in range(len(kb) - 5)):
        p.append("no E1 pause sequence")
    if not any(kb[i:i + 4] == [0x2A, 0x10, 0x90, 0xAA] for i in range(len(kb) - 3)) or \
            not any(kb[i:i + 4] == [0x36, 0x10, 0x90, 0xB6] for i in range(len(kb) - 3)):
        p.append("the shifts do not surround a make")
    if not any(all(kb[i + j] == 0x1E for j in range(24)) for i in range(len(kb) - 24)):
        p.append("no typematic run")
    firsts = {b for b in ms if b & 8}
    for bit in (0x01, 0x02, 0x04, 0x10, 0x20, 0x40, 0x80):
        if not any(b & bit for b in firsts):
            p.append("no first byte with bit 0x%02x" % bit)
    if not {0x00, 0x01, 0x02} <= set(ms):
        p.append("no byte that cannot begin a packet")
    interleaved = sum(1 for i in range(len(pairs) - 1) if pairs[i][0] != pairs[i + 1][0])
    if interleaved < 100:
        p.append("too few changes of device: %d" % interleaved)
    if len(pairs) != RUN_CORPUS_BYTES:
        p.append("the corpus has %d bytes, the run had %d" % (len(pairs), RUN_CORPUS_BYTES))
    return p


def verdict_problems(plan):
    v, m, p = plan["verdict"], plan["margins"], []
    g = {"median": 20, "worst": 40, "size": 1000}
    cases = [({"median": 19, "worst": 40, "size": 1000}, "beats"),
             ({"median": 20, "worst": 40, "size": 1000}, "the generic stays"),
             ({"median": 19, "worst": 42, "size": 1050}, "beats"),
             ({"median": 19, "worst": 43, "size": 1000}, "the generic stays"),
             ({"median": 19, "worst": 40, "size": 1051}, "the generic stays")]
    for part, want in cases:
        got, lines = v(g, part, m)
        if got != want or len(lines) != 3:
            p.append("the verdict rule on %r gave %r, want %r" % (part, got, want))
    return p


def run_document():
    problems = check_pe(EFI)
    import checkmolt
    problems += checkmolt.checkmetal.check_stick(STICK, EFI)
    if not report(problems, "the artefact: an x86-64 PE32+ EFI application; the stick as ring 7c's checker reads it"):
        return 1
    import bench
    import parts
    try:
        plan = bench.read_plan(PLAN)
    except (ValueError, KeyError, OSError) as exc:
        say("the plan does not read cold: %s" % exc)
        return 1
    problems = []
    if plan["identity"] != HP_IDENTITY:
        problems.append("the plan's identity is %r, not the HP's" % plan["identity"])
    if plan["margins"] != {"primary": 5, "worst": 5, "size": 5}:
        problems.append("the margins are %r" % plan["margins"])
    t = plan["threshold"]
    if (t["boots"], t["keyboard bytes"], t["mouse packets"], t["disagreements"], t["probation"]) != (3, 1000, 5000, 0, 3):
        problems.append("the threshold is %r" % t)
    if plan["candidates"] != 2:
        problems.append("candidates %r" % plan["candidates"])
    problems += corpus_problems(plan)
    problems += verdict_problems(plan)
    if not report(problems, "the plan, read cold: the HP's identity, margins 5, 5 and 5, threshold 3, 1,000, 5,000, 0 and "
                  "probation 3, at most 2 candidates, the corpus of %d bytes hashing to its pin and covering the spec's "
                  "list, the verdict rule worked through" % len(plan["pairs"])):
        return 1
    # The canned parts, byte for byte, each through the door.
    problems = []
    for name in CANNED:
        asm, bin_ = (os.path.join(FIX, "i8042-%s.%s" % (name, e)) for e in ("asm", "bin"))
        out = os.path.join(OUT, "check8b.%s.bin" % name)
        r = subprocess.run(["nasm", "-f", "bin", asm, "-o", out], capture_output=True, text=True)
        if r.returncode or open(out, "rb").read() != open(bin_, "rb").read():
            problems.append("i8042-%s.bin is not what its .asm assembles to %s" % (name, r.stderr))
            continue
        os.remove(out)
        try:
            f = parts.check_part(open(bin_, "rb").read(), SLOT)
        except ValueError as exc:
            problems.append("i8042-%s: the door: %s" % (name, exc))
            continue
        if f["name"] != name:
            problems.append("i8042-%s's name field is %r" % (name, f["name"]))
    # The bench: the same inputs give the same image, twice.
    shas = []
    for tag in ("a", "b"):
        d = os.path.join(OUT, "check8b.bench." + tag)
        shutil.rmtree(d, ignore_errors=True)
        esp = bench.build(d, open(bench.GENERIC, "rb").read(), open(os.path.join(FIX, "i8042-fast.bin"), "rb").read(), plan["corpus"])
        shas.append(hashlib.sha256(open(os.path.join(d, "BOOTX64.EFI"), "rb").read()).hexdigest())
        shutil.rmtree(d, ignore_errors=True)
    if shas[0] != shas[1]:
        problems.append("the bench does not build to the same bytes twice")
    if not report(problems, "the three canned parts reassembled byte for byte, each through the door with its own name; "
                  "the bench builds to the same bytes twice"):
        return 1
    # The PARTS.md section.
    text = open(PARTS_MD, encoding="utf-8").read()
    m = re.search(r"^## Ring 8b:.*?(?=^## |\Z)", text, re.S | re.M)
    problems = []
    if not m:
        problems.append("PARTS.md has no section headed 'Ring 8b:'")
    else:
        sec = m.group(0)
        for word in (plan["sha256"], "plans/parts/i8042.md", "germos molt", "germos molt i8042", "germos molt take i8042",
                     "germos molt undo", "germos restart", "germos count", "order: count", "order: busy", "order: ?",
                     "order: not healthy yet", "order: restart", "order: reset failed", "order: done",
                     "restarting in 3 s", "0xCF9", "tsc: i8042", "supersede"):
            if word not in sec:
                problems.append("the Ring 8b section does not say %r" % word)
    if not report(problems, "the PARTS.md section: the corpus's pointer and hash, the six orders and their answers, the restart, the medians"):
        return 1
    return 0 if check_refusal_and_brief(plan, parts) else 1


STUB_SOURCE = """bits 64
default rel
        dd init, byte_entry, health
init:   ret
byte_entry:
        ret
health: xor eax, eax
        ret
"""


def run_stub(argv):
    """Stands in for `claude`: records its argv, prints a small flat part."""
    capture = argv[0]
    with open(capture, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(argv[1:]) + "\n")
    sys.stdout.write(STUB_SOURCE)
    return 0


def check_refusal_and_brief(plan, parts):
    problems = []
    d = os.path.join(WORK, "brief")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    cap = os.path.join(d, "stub.jsonl")
    stub = "%s %s --stub %s" % (sys.executable, os.path.abspath(__file__), cap)
    base = ["--backend-cmd", stub, "--germline", os.path.join(d, "germline"), "--workdir-grow", os.path.join(d, "grow"),
            "--model", "claude-opus-5-5"]
    clean = {k: v for k, v in os.environ.items() if "API_KEY" not in k.upper() and k != "ANTHROPIC_AUTH_TOKEN"}
    for name in ("ANTHROPIC_API_KEY", "SOME_OTHER_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        rc, out = grow(base, dict(clean, **{name: "not-a-real-key"}))
        if rc != 3 or "refusing to run" not in out or name not in out:
            problems.append("with %s set the grow exited %d and said %r" % (name, rc, out[-200:]))
        if os.path.exists(cap):
            problems.append("with %s set the backend was spawned" % name)
    rc, out = grow(base, clean)
    if rc != 1:
        problems.append("the stub's part should lose on the differential: exit %d: %s" % (rc, out[-400:]))
    calls = [json.loads(l) for l in open(cap, encoding="utf-8")] if os.path.exists(cap) else []
    if len(calls) != 2:
        problems.append("the backend was called %d times for 2 candidates" % len(calls))
    else:
        a = calls[0]
        brief = a[a.index("--system-prompt") + 1]
        prompt = a[a.index("--") + 1]
        if a[0] != "-p" or a[a.index("--tools") + 1] != "" or a[a.index("--model") + 1] != "claude-opus-5-5":
            problems.append("the backend's flags are not -p, no tools, the model: %r" % a[:8])
        if plan["text"] not in prompt:
            problems.append("the prompt does not carry the plan verbatim")
        if parts.molt_key(SLOT, HP_IDENTITY) not in prompt:
            problems.append("the prompt does not carry the HP's key")
        if "for this machine only" not in prompt or "for this machine only" not in brief:
            problems.append("the brief does not say the part is for this machine only")
        for words in ("Two devices on one i8042", "An i8042 self-test may re-enable both ports",
                      "A 0xE0 scancode prefix swallows its successor"):
            if words not in prompt:
                problems.append("the prompt lacks the gotcha %r" % words)
        for words in ("## A part", "## ABI 3's service table", "`RDI` = the status byte"):
            if words not in brief:
                problems.append("the brief lacks %r" % words)
        if "differential" not in calls[1][calls[1].index("--") + 1]:
            problems.append("the second candidate's prompt does not carry the first's failure")
    return report(problems, "the API-key refusal under three names with nothing spawned; through the stub the brief carries "
                  "the plan verbatim, the HP's key, ABI 3, the gotchas and 'for this machine only'; the second candidate "
                  "was told the first's failure")


# ------------------------------------------------ test 2: the pipeline -----

def seams(work):
    """The frozen helpers' module paths, pointed at this test's files."""
    import checkmolt as cm
    os.makedirs(work, exist_ok=True)
    cm.OUT = work
    cm.MOLT_OUT = work
    cm.STICK = STICK
    cm.EFI = EFI
    cm.ESP = ESP
    cm.MOLT_GERMLINE = os.path.join(work, "germline")
    cm.MOLT_TWIN = os.path.join(work, "twin")
    cm.point_molt_seams()
    cm.checktrials.STICK = STICK
    cm.checktrials.TRIALS_OUT = work
    return cm


def fixture(name):
    return os.path.join(FIX, "i8042-%s.bin" % name)


def conv(reads, label):
    import checktrials
    return checktrials.conv_rows(reads[label]["conversation"], reads[label]["obs"])


def collect_argv(cm, germline):
    def argv(fate, record, hold_s=None):
        return [sys.executable, MOLT_PY, "--collect", "--port", "9999", "--record", record, "--germline", germline,
                "--image", ESP, "--workdir", os.path.join(cm.MOLT_OUT, "twin"), "--rehearsal-port", "9998"]
    return argv


def serve_boot(cm, f, disk, tag, germline, steps):
    cm.molt_argv = collect_argv(cm, germline)
    reads, problems = f.boot(disk, tag, steps, fate="good")
    return reads, problems


def blank_disk(cm, f, name):
    disk = os.path.join(cm.MOLT_OUT, "disk.%s.img" % name)
    cm.checkmetal.fresh_disk(disk)
    reads, problems = f.boot(disk, name + "-blank", [("ready", "ready"), ("sleep", 1.0)])
    if problems:
        raise RuntimeError("; ".join(problems))
    return disk


def fetch_steps(cm, wait_rx):
    return [("ready", "ready"), ("keys", "! molt %s\n" % SLOT)] + wait_rx + [("sleep", cm.WORD_S), ("surfaces", "w")]


def spinning_init(part):
    """fast with `jmp $` at its init, rehashed: the bench never calls init."""
    init, = struct.unpack_from("<I", part, 20)
    b = bytearray(part)
    b[init:init + 2] = b"\xeb\xfe"
    b[32:48] = b"spin".ljust(16, b"\0")
    b[48:80] = hashlib.sha256(bytes(b[96:])).digest()
    return bytes(b)


def lines_of(out, prefix):
    return [l for l in out.splitlines() if l.startswith(prefix)]


def run_pipeline():
    import molt
    import parts
    work = os.path.join(WORK, "pipeline")
    shutil.rmtree(work, ignore_errors=True)
    cm = seams(work)
    f = cm.Fates(parts)
    twin_id = f.identity
    problems = []
    ok = True

    # fast: every step, beats, stored, delivered with source 1.
    g1 = os.path.join(work, "germline.fast")
    rc, out = grow(["--canned", fixture("fast"), "--identity", twin_id, "--germline", g1,
                    "--workdir-grow", os.path.join(work, "grow.fast")])
    print(out, flush=True)
    order = ["the door passed it", "bench:", "differential: every event identical", "measure: primary",
             "rehearsal: PASS", "verdict: beats"]
    at = -1
    for word in order:
        i = out.find(word, at + 1)
        if i < 0:
            problems.append("fast: %r is missing, or out of order" % word)
        at = max(at, i)
    if rc != 0:
        problems.append("fast: exit %d" % rc)
    e = RUN_FAST
    want = ["measure: primary: median %d against %d, at least 5%% lower: yes" % (e["part"]["median"], e["generic"]["median"]),
            "measure: secondary worst: %d against %d, no more than 5%% higher: yes" % (e["part"]["worst"], e["generic"]["worst"]),
            "measure: secondary size: %d against %d, no more than 5%% higher: yes" % (e["part"]["size"], e["generic"]["size"])]
    if lines_of(out, "measure: ") != want:
        problems.append("fast: the measures are %r" % lines_of(out, "measure: "))
    if ("null decoder %d instructions" % RUN_NULL) not in out:
        problems.append("fast: the null decoder's count is not the run's")
    key = parts.molt_key(SLOT, twin_id)
    part, prov = molt.part_lookup(g1, key)
    fast = open(fixture("fast"), "rb").read()
    if part != fast or prov.get("verdict") != "beats":
        problems.append("fast: the germline does not hold the part under the twin's key")
    ok &= report(problems, "fast: door, bench, differential, measures, rehearsal, 'beats', every number the run's; stored under the twin's key")
    problems = []
    if ok:
        disk = blank_disk(cm, f, "fast")
        before = f.notes(disk)
        sha = parts.sha16(hashlib.sha256(fast).hexdigest())
        rx = [("await", rb"molt: %s shadow %s 3 1000 5000\r\n" % (SLOT.encode(), sha.encode()), cm.ANSWER_S, "installed", None)]
        reads, problems = serve_boot(cm, f, disk, "fast-fetch", g1, fetch_steps(cm, rx))
        if reads:
            rec = [json.loads(l) for l in open(reads["record"]) if l.strip()]
            grows = [r for r in rec if r.get("frame")]
            if len(grows) != 1 or bytes.fromhex(grows[0]["frame"]) != parts.part_frame(fast, (3, 1000, 5000), 1):
                problems.append("fast: the frame sent is not part_frame(fast, the plan's threshold, source 1)")
            if grows and grows[0].get("source") != "germline":
                problems.append("fast: the record's source is %r" % grows[0].get("source"))
            notes = f.notes(disk)
            if notes != before + ["molt %s shadow %s 3 1000 5000" % (SLOT, sha)]:
                problems.append("fast: the notebook's new notes are %r" % notes[len(before):])
        ok &= report(problems, "'! molt i8042' through the relay: the part delivered from the germline, source 1, in shadow, the plan's threshold")

    # slow: measured, loses, stays out.
    problems = []
    g2 = os.path.join(work, "germline.slow")
    rc, out = grow(["--canned", fixture("slow"), "--identity", twin_id, "--germline", g2,
                    "--workdir-grow", os.path.join(work, "grow.slow")])
    print(out, flush=True)
    if rc != 1 or "verdict: the generic stays" not in out or "rehearsal:" in out:
        problems.append("slow: exit %d, and the output is not 'the generic stays' with no rehearsal" % rc)
    r = RUN_SLOW
    if ("measure: primary: median %d against 17, at least 5%% lower: no" % r["median"]) not in out:
        problems.append("slow: the primary is not the run's")
    part, prov = molt.part_lookup(g2, key)
    if part is not None or (prov or {}).get("verdict") != "the generic stays":
        problems.append("slow: a part is stored, or no finding is")
    if ok and not problems:
        disk = blank_disk(cm, f, "slow")
        before = f.notes(disk)
        reads, p = serve_boot(cm, f, disk, "slow-fetch", g2, fetch_steps(cm, [("sleep", 6.0)]))
        problems += p
        if reads:
            if "the generic stays: this part did not beat it" not in conv(reads, "w"):
                problems.append("slow: the guest's answer is %r" % conv(reads, "w")[-3:])
            if f.notes(disk) != before:
                problems.append("slow: the refusal journaled %r" % f.notes(disk)[len(before):])
            if re.search(rb"molt: ", reads["capture"]):
                problems.append("slow: a molt: line on serial")
    ok &= report(problems, "slow: 'the generic stays' by the plan's rule, recorded; the guest told so, no note, nothing stored")

    # wrong and hang: the two later gates.
    problems = []
    rc, out = grow(["--canned", fixture("wrong"), "--identity", twin_id, "--germline", os.path.join(work, "germline.wrong"),
                    "--workdir-grow", os.path.join(work, "grow.wrong")])
    print(out, flush=True)
    if rc != 1 or "differential: the differential failed at corpus byte" not in out or "rehearsal:" in out:
        problems.append("wrong: exit %d, not the differential's failure" % rc)
    # The frozen hang loses on the measures, so the rehearsal is asked directly;
    # the grow's own rehearsal gate is met by fast with an init that spins.
    r = subprocess.run([sys.executable, os.path.join(HERE, "rehearse8b.py"), fixture("hang"), "--workdir", os.path.join(work, "r.hang")],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=REPO)
    print(r.stdout[-600:], flush=True)
    if r.returncode != 1 or "rehearsal: FAIL" not in r.stdout:
        problems.append("hang: the rehearsal exited %d, not its failure" % r.returncode)
    spin = os.path.join(work, "i8042-spin.bin")
    with open(spin, "wb") as fh:
        fh.write(spinning_init(open(fixture("fast"), "rb").read()))
    g4 = os.path.join(work, "germline.spin")
    rc, out = grow(["--canned", spin, "--identity", twin_id, "--germline", g4, "--workdir-grow", os.path.join(work, "grow.spin")])
    print(out, flush=True)
    if rc != 1 or "measure: primary: median 13 against 17, at least 5% lower: yes" not in out or \
            "the rehearsal in the twin" not in out or "verdict: the generic stays" not in out:
        problems.append("spin: exit %d, not beaten on the bench and failed at the rehearsal" % rc)
    if molt.part_lookup(g4, key)[0] is not None:
        problems.append("spin: a part that failed its rehearsal was stored")
    rc, out = grow(["--canned", fixture("wrong"), "--canned", fixture("wrong"), "--canned", fixture("fast"),
                    "--identity", twin_id, "--germline", os.path.join(work, "germline.twice"),
                    "--workdir-grow", os.path.join(work, "grow.twice")])
    if rc != 1 or "candidate 3" in out or len(re.findall(r"^candidate \d: asking", out, re.M)) != 2:
        problems.append("the plan's two candidates are not the limit: exit %d" % rc)
    ok &= report(problems, "wrong fails the differential; hang fails the rehearsal; a part that beats the bench and fails the rehearsal is not stored; a third candidate is never asked for")

    # Another identity, and --collect calling nothing.
    problems = []
    g3 = os.path.join(work, "germline.hp")
    hp_key = parts.molt_key(SLOT, HP_IDENTITY)
    molt.part_write(g3, hp_key, dict(prov or {}, key=hp_key, verdict="beats", sha256=hashlib.sha256(fast).hexdigest(),
                                     name="fast", threshold={"boots": 3, "keyboard bytes": 1000, "mouse packets": 5000}), fast)
    bindir = os.path.join(work, "bin")
    os.makedirs(bindir, exist_ok=True)
    marker = os.path.join(work, "claude.was.run")
    fake = os.path.join(bindir, "claude")
    with open(fake, "w") as fh:
        fh.write("#!/bin/sh\necho x > %s\nexit 1\n" % marker)
    os.chmod(fake, 0o755)
    if ok:
        old = os.environ["PATH"]
        os.environ["PATH"] = bindir + os.pathsep + old
        try:
            disk = blank_disk(cm, f, "other")
            before = f.notes(disk)
            steps = fetch_steps(cm, [("sleep", 6.0)]) + [("keys", "? is anyone there\n"), ("sleep", 6.0), ("surfaces", "q"),
                                                         ("keys", "! build me a thing\n"), ("sleep", 6.0), ("surfaces", "g")]
            reads, p = serve_boot(cm, f, disk, "other", g3, steps)
            problems += p
            if reads:
                if "no part grown for this machine" not in conv(reads, "w"):
                    problems.append("another identity: the guest's answer is %r" % conv(reads, "w")[-3:])
                if not [r for r in conv(reads, "q") if "collecting" in r]:
                    problems.append("--collect: the question's answer is %r" % conv(reads, "q")[-3:])
                if not [r for r in conv(reads, "g") if "collecting" in r]:
                    problems.append("--collect: the grow's answer is %r" % conv(reads, "g")[-3:])
                if [n for n in f.notes(disk)[len(before):] if n.startswith("molt ")]:
                    problems.append("another identity: a molt note was journaled")
            if os.path.exists(marker):
                problems.append("--collect ran the claude command")
        finally:
            os.environ["PATH"] = old
    ok &= report(problems, "a guest of another identity refused with no note; --collect answered '?' and '!' and ran nothing")
    say("the pipeline: %s" % ("as the plan says" if ok else "NOT as the plan says"))
    return 0 if ok else 1


# ------------------------------------------------ test 3: the orders ------

ORDER_S = 5.0           # an order's answer on serial
GAP_S = 6.0             # longer than the guest's 5 s since the last key
NOTICE_S = 3.0          # order: restart to the firmware's first byte, at least
NOTICE_LIMIT_S = 15.0   # and at most, from the runs of items 3 and 12
SICK_RESET_S = 35.0     # the sick part's ready line to the next boot's first OVMF byte
CHAIN_T_S = 1200        # one QEMU carries six boots
NOTE_A = "this line crosses a reboot"
NOTE_B = "more words through the part so that it decodes well past a hundred bytes"
RX_COUNT = rb"order: count (\d+) (\d+) (\d+)\r\n"
RX_TSC = rb"tsc: i8042 (\d+) generic (\d+) part (\d+) bytes (\d+)\r\n"


def chardev(cm):
    """Serial through a socket and its log, so the human can send orders.
    The drain thread matters: a client that does not read stops the UART."""
    real = cm.boot_argv

    def argv(smp, disk, stick_copy, serial_path, t):
        a = real(smp, disk, stick_copy, serial_path, t)
        i = a.index("-serial")
        sock = serial_path + ".sock"
        if os.path.exists(sock):
            os.remove(sock)
        a[i:i + 2] = ["-chardev", "socket,id=s0,path=%s,server=on,wait=off,logfile=%s" % (sock, serial_path),
                      "-serial", "chardev:s0"]
        Human.sock_path = sock
        return a

    class Human(cm.Human8a):
        sock_path = None
        sk = None

        def step(self, s):
            if s[0] != "order":
                return super().step(s)
            if self.sk is None:
                self.sk = socket.socket(socket.AF_UNIX)
                self.sk.connect(self.sock_path)
                threading.Thread(target=self.drain, args=(self.sk,), daemon=True).start()
            for b in s[1].encode() + b"\n":
                self.sk.send(bytes([b]))
                time.sleep(0.005)
            return None

        @staticmethod
        def drain(sk):
            try:
                while sk.recv(65536):
                    pass
            except OSError:
                pass

        def run(self, *a, **k):
            try:
                return super().run(*a, **k)
            finally:
                if self.sk is not None:
                    self.sk.close()

    cm.boot_argv = argv
    cm.Human8a = Human


def order(text, rx, label):
    return [("order", text), ("await", rx, ORDER_S, label, None)]


def restart(i, wiggles=0):
    """The order, the notice on the console, the firmware's first byte."""
    steps = order("germos restart", rb"order: restart\r\n", "rs%d" % i) + [("surfaces", "notice%d" % i)]
    if wiggles:
        steps.append(("wiggle", wiggles))
    return steps + [("banner", NOTICE_LIMIT_S, "reset%d" % i, "rs%d" % i)]


def even(n):
    return n + (n % 2)


def table_of(disk):
    r = subprocess.run([sys.executable, os.path.join(HERE, "parts.py"), "--disk", disk], capture_output=True, text=True)
    return r.stdout


def count_notes(notes, boot=None):
    out = []
    for n in notes:
        m = re.fullmatch(r"molt i8042 count (\d+) (\d+) (\d+) (\d+)", n)
        if m and (boot is None or int(m.group(1)) == boot):
            out.append(tuple(int(x) for x in m.groups()))
    return out


def run_inert(cm, f, problems):
    disk = blank_disk(cm, f, "inert")
    before = f.notes(disk)
    steps = [("ready", "ready"), ("order", "germos count"), ("order", "germos restart"), ("order", "germos molt i8042"),
             ("order", "banana"), ("sleep", GAP_S), ("keys", "hello there\n"), ("sleep", cm.WORD_S), ("surfaces", "w")]
    reads, p = f.boot(disk, "inert", steps)
    problems += p
    if reads:
        if b"order:" in reads["capture"] or b"tsc:" in reads["capture"]:
            problems.append("inert: an order was answered on a boot with no molt note")
        if reads["capture"].count(b"S7: keyboard ready") != 1:
            problems.append("inert: the machine restarted, or never came up")
        if f.notes(disk) != before + ["hello there"]:
            problems.append("inert: the notes are %r" % f.notes(disk)[len(before):])
    return not problems


def run_chain(cm, f, parts, problems):
    """Fetch, undo, fetch by order; three shadow boots; the take; three live."""
    import molt
    import rehearse8b
    work = cm.MOLT_OUT
    fast = open(fixture("fast"), "rb").read()
    sha = parts.sha16(hashlib.sha256(fast).hexdigest())
    germline = os.path.join(work, "germline.fast")
    key = parts.molt_key(SLOT, f.identity)
    molt.part_write(germline, key, {"key": key, "verdict": "beats", "sha256": hashlib.sha256(fast).hexdigest(), "name": "fast",
                                    "threshold": {"boots": 3, "keyboard bytes": 1000, "mouse packets": 5000}}, fast)
    disk = blank_disk(cm, f, "chain")
    shadow_rx = rb"molt: i8042 shadow %s 3 1000 5000\r\n" % sha.encode()

    reads, p = serve_boot(cm, f, disk, "c-fetch", germline, fetch_steps(cm, [("await", shadow_rx, cm.ANSWER_S, "fetched", None)]))
    problems += p
    if not reads:
        return None

    # A shadow boot: every refusal, and the undo by order.
    steps = [("ready", "ready")] + order("germos banana", rb"order: \?\r\n", "q1") + order("germos", rb"order: \?\r\n", "q2") + \
        order("germos restart", rb"order: not healthy yet\r\n", "nh") + [("sleep", GAP_S)] + \
        order("germos molt undo", rb"molt: i8042 undo generic\r\n", "undone") + [("await", rb"order: done\r\n", ORDER_S, "d0", None), ("sleep", cm.WORD_S)]
    reads, p = f.boot(disk, "c-undo", steps)
    problems += p
    if not reads:
        return None

    # A boot with a molt note and no part: the main loop's orders.
    steps = [("ready", "ready"), ("sleep", GAP_S)] + \
        order("germos molt i8042", shadow_rx, "refetched") + [("await", rb"order: done\r\n", ORDER_S, "d1", None), ("keys", "half a line")] + \
        order("germos molt", rb"order: busy\r\n", "busy") + [("sleep", GAP_S)] + \
        order("germos molt", rb"order: done\r\n", "d2") + [("sleep", cm.WORD_S), ("surfaces", "t")]
    reads, p = serve_boot(cm, f, disk, "c-refetch", germline, steps)
    problems += p
    if not reads:
        return None
    rows = conv(reads, "t")
    if any("half a line" in r for r in rows) or rows[-2:] != ["> ! molt", ">"]:
        problems.append("c-refetch: the half line was not rubbed out: %r" % rows[-4:])
    if any("order:" in r for r in rows):
        problems.append("c-refetch: an order line reached the conversation")

    # Three shadow boots and three live boots, each by restart, in one QEMU.
    steps, start, kb_each, pk_each = [], 0, 334, even(1667)
    for i in (1, 2, 3):
        notes, start = cm.typed_notes(kb_each, start, parts)
        steps += [("ready", "r%d" % i), ("mark", "a%d" % i)]
        if i == 1:
            steps += [("sleep", GAP_S)] + order("germos molt take i8042", rb"order: done\r\n", "early") + [("sleep", cm.WORD_S), ("surfaces", "early")]
        steps += [("keys", t + "\n") for t in notes] + [("wiggle", pk_each),
                  ("await", rb"S8: healthy \d+\r\n", parts.HEALTH_S + cm.HEALTH_SLACK_S, "h%d" % i, "r%d" % i),
                  ("sleep", 1.0), ("mark", "b%d" % i)] + order("germos count", RX_COUNT, "c%d" % i) + \
            [("await", RX_TSC, ORDER_S, "t%d" % i, None)]
        if i < 3:
            steps += restart(i, wiggles=40 if i == 2 else 0)
    steps += [("sleep", GAP_S)] + order("germos molt take i8042", rb"molt: i8042 live %s\r\n" % sha.encode(), "taken") + \
        [("await", rb"order: done\r\n", ORDER_S, "d3", None), ("sleep", cm.WORD_S)] + restart(3)
    for i in (4, 5, 6):
        steps += [("ready", "r%d" % i)]
        if i == 4:
            steps += [("keys", NOTE_A + "\n"), ("keys", NOTE_B + "\n"), ("wiggle", 60), ("click", "key", ord("!")), ("keys", " molt\n"),
                      ("sleep", cm.WORD_S), ("surfaces", "w4")]
        else:
            steps += [("surfaces", "w%d" % i), ("keys", "another line on boot %d\n" % i), ("wiggle", 20)]
        steps += [("await", rb"S8: healthy \d+\r\n", parts.HEALTH_S + cm.HEALTH_SLACK_S, "h%d" % i, "r%d" % i), ("sleep", 1.0)]
        steps += order("germos count", RX_COUNT, "c%d" % i)
        if i < 6:
            steps += restart(i)
    before = f.notes(disk)
    t_saved = cm.BOOT_T_S
    cm.BOOT_T_S = CHAIN_T_S
    try:
        reads, p = f.boot(disk, "c-chain", steps)
    finally:
        cm.BOOT_T_S = t_saved
    problems += p
    if not reads:
        return None
    problems += judge_chain(cm, f, parts, reads, disk, before, sha)
    if problems:
        return None
    # A sitting through the live part, by ring 7d's own human.
    rehearse8b.point_seams(work, STICK)
    r = rehearse8b.Rehearsal(fixture("fast"), work, say)
    _, p = r.sitting(disk, NOTE_A)
    problems += p
    return disk


def judge_chain(cm, f, parts, reads, disk, before, sha):
    """Everything the chain's one serial capture and one notebook must show."""
    p = []
    cap, at, found, marks = reads["capture"], reads["at"], reads["found"], reads["marks"]
    if re.search(rb"ERR:|S8: recovery|exception", cap):
        p.append("the chain: the guest said an error or a recovery")
    got = conv(reads, "early")
    if got[-2:-1] != ["below threshold: boots 0/3 keys 0/1000 mouse 0/5000"]:
        p.append("the take below threshold left %r" % got[-3:])
    notes = f.notes(disk)
    new = notes[len(before):]
    if [n for n in new if " disagree " in n]:
        p.append("a disagreement was journaled: %r" % [n for n in new if " disagree " in n][:3])
    loaded = [re.fullmatch(r"molt boot (\d+) i8042 (shadow|live)", n) for n in new if n.startswith("molt boot ")]
    states = [m.group(2) for m in loaded]
    boots = [int(m.group(1)) for m in loaded]
    if states != ["shadow"] * 3 + ["live"] * 3:
        p.append("the six boots loaded %r" % states)
    if len(boots) != 6:
        return p + ["the chain's boots are %r" % boots]
    for i in (1, 2, 3, 4, 5):
        rows = conv(reads, "notice%d" % i)
        if "restarting in 3 s" not in rows:
            p.append("boot %d: 'restarting in 3 s' is not on the conversation: %r" % (i, rows[-3:]))
        if any("order:" in r for r in rows):
            p.append("boot %d: an order line reached the conversation" % i)
        gap = at["reset%d" % i] - at["rs%d" % i]
        if gap < NOTICE_S - cm.POLL_S or gap > NOTICE_LIMIT_S:
            p.append("boot %d: %.2f s from 'order: restart' to the firmware's first byte" % (i, gap))
    # Each germos count against the human's counts and against the disk's note.
    for i in (1, 2, 3, 4, 5, 6):
        m = re.fullmatch(RX_COUNT, found["c%d" % i][1])
        k, pk, d = (int(x) for x in m.groups())
        if i <= 3:
            a, b = marks["a%d" % i], marks["b%d" % i]
            if (k, pk, d) != (b["kb"] - a["kb"], b["packets"] - a["packets"], 0):
                p.append("boot %d: germos count said %d %d %d, the human sent %d %d" % (i, k, pk, d, b["kb"] - a["kb"], b["packets"] - a["packets"]))
            t = re.fullmatch(RX_TSC, found["t%d" % i][1])
            if int(t.group(1)) != boots[i - 1] or int(t.group(2)) <= 0 or int(t.group(3)) <= 0 or int(t.group(4)) <= 0:
                p.append("boot %d: the tsc line is %r" % (i, found["t%d" % i][1]))
        cn = count_notes(new, boots[i - 1])
        if i in (1, 2, 4, 5):
            extra = 40 if i == 2 else 0
            if not cn or cn[-1] != (boots[i - 1], k, pk + extra, d):
                p.append("boot %d: the disk's last count note is %r, the order said %d %d %d (+%d in the notice)" % (i, cn[-1:], k, pk, d, extra))
    live_segment = cap[reads["segments"][3]:]
    if b"tsc:" in live_segment:
        p.append("a tsc: line on a live boot")
    table = table_of(disk)
    if "i8042 live " + sha not in table or "probation 3/3" not in table:
        p.append("the disk's table does not say live and probation 3/3: %s" % table[:300])
    rows = conv(reads, "w5")
    if not [r for r in rows if NOTE_A in r]:
        p.append("the note did not come back across the reboot: %r" % rows[-4:])
    if NOTE_A not in new or NOTE_B not in new:
        p.append("the notes typed through the part are not on the disk")
    rows = conv(reads, "w4")
    if rows[-2:] != ["> ! molt", ">"]:
        p.append("the click on the choices row left %r" % rows[-3:])
    return p


def run_sick(cm, f, parts, problems):
    """A part whose health fails: the pets stop, the watchdog, the recovery."""
    import molt
    work = cm.MOLT_OUT
    sick = open(fixture("sick"), "rb").read()
    sha = parts.sha16(hashlib.sha256(sick).hexdigest())
    germline = os.path.join(work, "germline.sick")
    key = parts.molt_key(SLOT, f.identity)
    molt.part_write(germline, key, {"key": key, "verdict": "beats", "sha256": hashlib.sha256(sick).hexdigest(), "name": "sick",
                                    "threshold": {"boots": 1, "keyboard bytes": 100, "mouse packets": 100}}, sick)
    disk = blank_disk(cm, f, "sick")
    rx = rb"molt: i8042 shadow %s 1 100 100\r\n" % sha.encode()
    reads, p = serve_boot(cm, f, disk, "s-fetch", germline, fetch_steps(cm, [("await", rx, cm.ANSWER_S, "fetched", None)]))
    problems += p
    if not reads:
        return
    notes, _ = cm.typed_notes(100, 0, parts)
    steps = [("ready", "ready")] + [("keys", t + "\n") for t in notes] + [("wiggle", 100),
             ("await", rb"S8: healthy \d+\r\n", parts.HEALTH_S + cm.HEALTH_SLACK_S, "h", "ready"), ("sleep", GAP_S)] + \
        order("germos molt take i8042", rb"molt: i8042 live %s\r\n" % sha.encode(), "taken") + [("sleep", cm.WORD_S)] + restart(1)
    steps += [("ready", "r2"), ("banner", SICK_RESET_S, "wd", "r2"),
              ("await", rb"S8: recovery i8042 watchdog\r\n", cm.RECOVER_S, "rec", "wd"),
              ("ready", "r3"), ("keys", "typed after the recovery\n"), ("sleep", cm.WORD_S)]
    before = f.notes(disk)
    reads, p = f.boot(disk, "s-chain", steps)
    problems += p
    if not reads:
        return
    new = f.notes(disk)[len(before):]
    if ("molt i8042 demoted %s watchdog" % sha) not in new:
        problems.append("sick: no demoted note: %r" % new[-6:])
    if "typed after the recovery" not in new:
        problems.append("sick: the generic did not serve after the recovery")
    if "i8042 demoted %s watchdog" % sha not in table_of(disk):
        problems.append("sick: the disk's table does not say demoted")


def run_shadow():
    import parts
    work = os.path.join(WORK, "shadow")
    shutil.rmtree(work, ignore_errors=True)
    cm = seams(work)
    chardev(cm)
    f = cm.Fates(parts)
    problems = []
    ok = run_inert(cm, f, problems)
    ok = report(problems, "with no molt note the machine reads no order: ring 7d's machine") and ok
    if not ok:
        return 1
    run_chain(cm, f, parts, problems)
    ok = report(problems, "a fetch typed, an undo and a fetch by order, every refusal; three shadow boots by restart with 'restarting in 3 s' "
                "and at least 3 s to the firmware; germos count against the human and the disk; the tsc lines; the take; three live boots "
                "to probation 3/3; a note across a reboot, a click, a sitting through the part")
    if not ok:
        return 1
    run_sick(cm, f, parts, problems)
    if not report(problems, "sick: taken, live, health fails, the pets stop, the watchdog resets, recovery, demoted; the generic serves"):
        return 1
    say("shadow to live: as the plan says")
    return 0


# ---------------------------------------------- test 4: the cage -----------

FROZEN_8B = ["plans/parts/i8042.md", "stage8/bench.asm", "stage8/bench.py", "stage8/rehearse8b.py", "stage8/test-8b.sh", "stage8/checkmolt8b.py"] + \
    ["stage8/fixtures/i8042-%s.%s" % (n, e) for n in CANNED for e in ("asm", "bin")]
ALLOWED_8B = ["python3 broker/molt.py --grow i8042 --model claude-opus-5-5 2>&1 | tee stage8/out/grow-8b.log",
              "python3 stage8/hp-day.py", "python3 broker/molt.py --collect",
              "PATH=stage8/out/toolchain/nasm-3.02/bin:$PATH python3 stage8/parts.py --seed",
              "python3 stage8/bench.py --plan plans/parts/i8042.md --candidate stage8/fixtures/i8042-fast.bin"]


def run_cage():
    import bench
    cm = seams(os.path.join(WORK, "cage"))
    problems = []
    for rel in FROZEN_8B:
        path = os.path.join(REPO, rel)
        if cm.tool_verdict("Write", {"file_path": path, "content": "x"}) != "DENY":
            problems.append("the hook lets Write reach %s" % rel)
        if cm.tool_verdict("Edit", {"file_path": path, "old_string": "a", "new_string": "b"}) != "DENY":
            problems.append("the hook lets Edit reach %s" % rel)
    for cmd in ALLOWED_8B:
        if cm.tool_verdict("Bash", {"command": cmd}) != "ALLOW":
            problems.append("the hook denies %r" % cmd)
    r = subprocess.run([sys.executable, os.path.join(REPO, ".claude", "hooks", "payloads.py")], capture_output=True, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    if r.returncode or " 0 wrong" not in last:
        problems.append("the payload table: %s" % last)
    else:
        say(last)
    if not report(problems, "the new paths frozen against Write and Edit; the day's commands allowed"):
        return 1
    chardev(cm)
    d = os.path.join("stage8", "out", "molt8b", "cage")
    disk, copy, serial = (os.path.join(REPO, d, n) for n in ("disk.c.img", "stick.c.img", "serial.c.txt"))
    argv = cm.boot_argv(cm.FATES_SMP, disk, copy, serial, "600")
    qemu = argv[4:]
    problems += cm.checkmetal.check_argv_7c(qemu, cm.RELAY_PORT_8A, cm.checkmetal.MAC)
    for flag in cm.ARGV_REFUSED_8A:
        if flag in qemu:
            problems.append("a gate boot carries %s" % flag)
    if qemu.count("-serial") != 1 or qemu[qemu.index("-serial") + 1] != "chardev:s0" or qemu.count("-chardev") != 1:
        problems.append("the serial is not one chardev: %r" % qemu)
    ch = qemu[qemu.index("-chardev") + 1]
    if not ch.startswith("socket,id=s0,path=") or ",server=on,wait=off,logfile=" not in ch or "host=" in ch or "port=" in ch:
        problems.append("the chardev is not a unix socket with a log: %s" % ch)
    b = bench.qemu_argv(os.path.join(REPO, d, "esp.img"), os.path.join(REPO, d, "bench.log"))
    if "-icount" not in b or b[b.index("-smp") + 1] != "1" or "-netdev" in b or "-nic" in b:
        problems.append("the bench's command is not -icount at -smp 1 with no network: %r" % b)
    if not report(problems, "the order line's command passes ring 7c's argv check; -icount is the bench's alone, with no network"):
        return 1
    return 0


def main(argv):
    if argv[:1] == ["--stub"]:
        return run_stub(argv[1:])
    modes = {"--document": run_document, "--pipeline": run_pipeline, "--shadow": run_shadow, "--cage": run_cage}
    if len(argv) != 1 or argv[0] not in modes:
        say("usage: checkmolt8b.py --document | --pipeline | --shadow | --cage")
        return 1
    os.makedirs(WORK, exist_ok=True)
    return modes[argv[0]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
