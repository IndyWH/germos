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


def run_shadow():
    say("test 3 is not written yet")
    return 1


def run_cage():
    say("test 4 is not written yet")
    return 1


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
