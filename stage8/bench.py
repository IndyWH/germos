#!/usr/bin/env python3
"""stage8/bench.py - ring 8b's bench, the host's half (stage8/plan-8b.md).

Reads a part's plan cold, builds stage8/bench.asm around the generic, the
candidate and the plan's corpus, boots it once under -icount at -smp 1 and
does every piece of arithmetic: the costs, the differential, the measures and
the plan's verdict. The guest computes nothing.

Frozen at ring 8b item 14, beside the plan it reads: a bent bench is a bent
verdict. Standard library only.

    python3 stage8/bench.py --plan plans/parts/i8042.md --candidate PART.bin

Exit 0 when the verdict is "beats", 1 for "the generic stays" or a failed
differential, 2 when the bench itself failed and there is no verdict.
"""

import argparse
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BENCH_ASM = os.path.join(HERE, "bench.asm")
GENERIC = os.path.join(HERE, "fixtures", "i8042-good.bin")
OVMF = "/usr/share/ovmf/OVMF.fd"
LIMIT_S = 180
ESP_BYTES = 48 << 20                 # FAT32 needs at least about 33 MB for OVMF to see it
BLOCKS = {"N": 2, "G": 4, "C": 4}


# ------------------------------------------------------------- the plan ----

def section(text, name):
    m = re.search(r"^## %s\n(.*?)(?=^## |\Z)" % re.escape(name), text, re.S | re.M)
    if not m:
        raise ValueError("the plan has no section %r" % name)
    return m.group(1)


def python_block(body, name):
    m = re.search(r"^```python\n(.*?)^```", body, re.S | re.M)
    if not m:
        raise ValueError("the plan's %s has no Python block" % name)
    return m.group(1)


def fields(body, name, want):
    out = {}
    for line in body.splitlines():
        m = re.fullmatch(r"- ([a-z ]+): (\d+)", line.strip())
        if m:
            out[m.group(1)] = int(m.group(2))
    missing = [w for w in want if w not in out]
    if missing:
        raise ValueError("the plan's %s lacks %s" % (name, ", ".join(missing)))
    return out


def corpus_bytes(pairs):
    return bytes(x for p in pairs for x in p)


def read_plan(path):
    """The plan parsed cold: every value the pipeline uses, and the corpus
    run and checked against its pinned hash."""
    text = open(path, encoding="utf-8").read()
    identity = re.search(r"`(cpu [0-9a-f]{8} pci [0-9a-f]{4}:[0-9a-f]{4}:[0-9a-f]{2})`", section(text, "Identity"))
    if not identity:
        raise ValueError("the plan's Identity holds no identity")
    body = section(text, "Corpus")
    scope = {}
    exec(compile(python_block(body, "Corpus"), path + ":Corpus", "exec"), scope)
    pairs = scope["corpus"]()
    data = corpus_bytes(pairs)
    pinned = re.search(r"`([0-9a-f]{64})`", body)
    if not pinned:
        raise ValueError("the plan's Corpus pins no SHA-256")
    if hashlib.sha256(data).hexdigest() != pinned.group(1):
        raise ValueError("the corpus does not hash to its pinned SHA-256")
    margins = fields(section(text, "Margins"), "Margins", ("primary", "worst", "size"))
    threshold = fields(section(text, "Threshold"), "Threshold",
                       ("boots", "keyboard bytes", "mouse packets", "disagreements", "probation"))
    candidates = fields(section(text, "Candidates"), "Candidates", ("at most",))["at most"]
    scope = {}
    exec(compile(python_block(section(text, "Verdict rule"), "Verdict rule"), path + ":Verdict", "exec"), scope)
    return {"text": text, "identity": identity.group(1), "pairs": pairs, "corpus": data, "sha256": pinned.group(1),
            "margins": margins, "threshold": threshold, "candidates": candidates, "verdict": scope["verdict"]}


# ------------------------------------------------------------ the boot -----

def build(workdir, generic, candidate, corpus):
    os.makedirs(workdir, exist_ok=True)
    paths = {}
    for name, data in (("generic.bin", generic), ("candidate.bin", candidate), ("corpus.dat", corpus)):
        paths[name] = os.path.join(workdir, name)
        with open(paths[name], "wb") as fh:
            fh.write(data)
    efi = os.path.join(workdir, "BOOTX64.EFI")
    r = subprocess.run(["nasm", "-f", "bin", '-DGENERIC="%s"' % paths["generic.bin"],
                        '-DCANDIDATE="%s"' % paths["candidate.bin"], '-DCORPUS="%s"' % paths["corpus.dat"],
                        BENCH_ASM, "-o", efi], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("nasm failed on the bench: " + r.stderr.strip())
    esp = os.path.join(workdir, "esp.img")
    with open(esp, "wb") as fh:
        fh.truncate(ESP_BYTES)
    for cmd in (["mformat", "-i", esp, "-F", "-v", "ESP", "::"],
                ["mmd", "-i", esp, "::/EFI", "::/EFI/BOOT"],
                ["mcopy", "-i", esp, efi, "::/EFI/BOOT/BOOTX64.EFI"]):
        subprocess.run(cmd, check=True, capture_output=True)
    return esp


def qemu_argv(esp, log):
    return ["timeout", "-k", "5", str(LIMIT_S), "qemu-system-x86_64", "-machine", "q35", "-cpu", "IvyBridge",
            "-m", "256M", "-smp", "1", "-icount", "shift=0,sleep=off", "-bios", OVMF,
            "-drive", "format=raw,file=" + esp, "-device", "isa-debug-exit,iobase=0xf4,iosize=1",
            "-display", "none", "-vga", "none", "-net", "none", "-serial", "file:" + log]


def parse_log(log):
    data = open(log, "rb").read().decode("latin-1").replace("\r", "")
    at = data.rfind("bench: corpus ")
    if at < 0:
        raise RuntimeError("the bench printed no banner")
    lines = data[at:].split("\n")
    n = int(lines[0].split()[2], 16)
    blocks, cur, pending, done = [], None, [], False
    for line in lines[1:]:
        if line == "bench: done":
            done = True
            break
        if line.startswith("B "):
            cur = {"tag": line.split()[2], "costs": [], "events": []}
            blocks.append(cur)
        elif line[:2] in ("k ", "p "):
            pending.append(line)
        elif line:
            cur["costs"].append(int(line, 16))
            cur["events"].append(tuple(pending))
            pending = []
    if not done:
        raise RuntimeError("the bench did not finish: it hung, faulted or ran out of time")
    return n, blocks


def run_bench(candidate, plan, generic=None, workdir=None):
    """One boot. Returns the measured dict, or raises RuntimeError when the
    bench itself failed (no verdict can be given)."""
    generic = open(GENERIC, "rb").read() if generic is None else generic
    own = workdir is None
    tmp = tempfile.TemporaryDirectory(dir=os.path.join(HERE, "out")) if own else None
    workdir = tmp.name if own else workdir
    t0 = time.time()
    try:
        esp = build(workdir, generic, candidate, plan["corpus"])
        log = os.path.join(workdir, "bench.log")
        if os.path.exists(log):
            os.remove(log)
        p = subprocess.run(qemu_argv(esp, log), capture_output=True)
        if p.returncode != 99:                   # isa-debug-exit: (0x31 << 1) | 1
            raise RuntimeError("the bench did not exit cleanly: QEMU exit %d (a hang or a fault in the part)" % p.returncode)
        n, blocks = parse_log(log)
        if n != len(plan["pairs"]):
            raise RuntimeError("the bench fed %d bytes, the corpus has %d" % (n, len(plan["pairs"])))
        by = {t: [b for b in blocks if b["tag"] == t] for t in BLOCKS}
        for tag, count in BLOCKS.items():
            if len(by[tag]) != count or any(len(b["costs"]) != n for b in by[tag]):
                raise RuntimeError("block %s: the bench's blocks are not whole" % tag)
            if any(b["costs"] != by[tag][0]["costs"] or b["events"] != by[tag][0]["events"] for b in by[tag]):
                raise RuntimeError("block %s: blocks of one decoder differ: the bench is not exact" % tag)
        null = by["N"][0]["costs"]
        if len(set(null)) != 1:
            raise RuntimeError("the null decoder's cost varied")
        base = null[0]
        return {"n": n, "null": base, "wall": time.time() - t0,
                "generic_costs": [c - base for c in by["G"][0]["costs"]],
                "part_costs": [c - base for c in by["C"][0]["costs"]],
                "generic_events": by["G"][0]["events"], "part_events": by["C"][0]["events"],
                "generic_size": len(generic), "part_size": len(candidate)}
    finally:
        if own:
            tmp.cleanup()


# ----------------------------------------------------------- the verdict ---

def differential(m):
    """The first byte whose events differ from the generic's, or None."""
    for i, (a, b) in enumerate(zip(m["generic_events"], m["part_events"])):
        if a != b:
            return {"index": i, "generic": list(a), "part": list(b)}
    return None


def measures(costs, size):
    return {"median": statistics.median_low(costs), "worst": max(costs), "size": size}


def judge(m, plan):
    """The plan's verdict over one measured boot, with every number."""
    gen = measures(m["generic_costs"], m["generic_size"])
    part = measures(m["part_costs"], m["part_size"])
    word, lines = plan["verdict"](gen, part, plan["margins"])
    return {"generic": gen, "part": part, "verdict": word, "lines": lines}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan", default=os.path.join(REPO, "plans", "parts", "i8042.md"))
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--generic", default=GENERIC)
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--json", default=None, help="write the numbers to this file")
    args = ap.parse_args(argv)
    try:
        plan = read_plan(args.plan)
    except (ValueError, KeyError, OSError) as exc:
        print("bench: the plan: %s" % exc)
        return 2
    candidate = open(args.candidate, "rb").read()
    generic = open(args.generic, "rb").read()
    try:
        m = run_bench(candidate, plan, generic, args.workdir)
    except RuntimeError as exc:
        print("bench: no verdict: %s" % exc)
        return 2
    print("bench: corpus %d bytes, sha256 %s; null decoder %d instructions; %.1f s"
          % (m["n"], plan["sha256"], m["null"], m["wall"]))
    diff = differential(m)
    out = {"n": m["n"], "null": m["null"], "differential": diff}
    code = 0
    if diff:
        print("differential: byte %d differs: generic %r, part %r" % (diff["index"], diff["generic"], diff["part"]))
        print("verdict: the generic stays (the differential failed)")
        out["verdict"] = "the generic stays"
        code = 1
    else:
        print("differential: every event identical")
        res = judge(m, plan)
        for line in res["lines"]:
            print(line)
        print("verdict: %s" % res["verdict"])
        out.update(res)
        code = 0 if res["verdict"] == "beats" else 1
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
