#!/usr/bin/env python3
"""PreToolUse hook: freeze the acceptance tests, and guard the real disks.

The foundation document's rule is that guarantees we care about become hooks,
not requests. This hook carries two of them.

THE FREEZE. The implementer is mechanically blocked from editing the acceptance
tests during implementation and fixes. Any attempt to MODIFY a file in
PROTECTED, by any route - Write, Edit, MultiEdit, NotebookEdit, and Bash - is
denied. Reading and RUNNING the tests stays allowed; they have to remain
runnable. If a test turns out to be genuinely wrong, that is a spec question for
the owner, not something the implementer edits away.

Matching is PATH-PRECISE, and that is deliberate. An earlier version matched the
bare basename anywhere, which caught a command run from inside stage0/ but also
denied the *creation* of stage1/test.sh - a different file, in a different stage,
that did not exist yet. Protecting a file we have not written is not a freeze, it
is a wall. So a candidate path is resolved before it is judged:

  - a path with a directory part is protected only if it ends with one of the
    PROTECTED repo-relative paths (so absolute paths are caught, and
    stage1/test.sh is not);
  - a BARE basename with no directory part is still treated as protected, since
    it may be a command run from inside the protected file's own directory.
    Conservative on purpose: a false deny costs a reworded command, a false
    allow costs an edited acceptance test.

Everything is derived from PROTECTED, so freezing a new stage's tests is a
one-line change to that tuple.

THE STORAGE BODYGUARD (Stage 3, plan item 1). The foundation's hard safety
rule, verbatim: "storage code touches only QEMU disk images until Stage 7, and
never any disk holding real data." For an unattended overnight stage that rule
is made mechanical here, on EVERY Bash call, before and independently of the
freeze:

  - any mention of a /dev path is denied unless it is one of the harmless
    sources and sinks (/dev/zero, /dev/urandom, /dev/random, /dev/null, the
    standard streams, /dev/fd/, /dev/tty*). That covers the spec's four
    (/dev/sd*, /dev/nvme*, /dev/disk*, /dev/mapper) and every sibling
    (/dev/hd*, /dev/vd*, /dev/loop*, /dev/mmcblk*, /dev/md*, /dev/dm-*, ...)
    without a list that could fall behind;
  - the words mount, umount, losetup, mkfs (which covers mkfs.ext4 and kin),
    and the partitioning and wiping tools - fdisk, sfdisk, gdisk, parted,
    wipefs, blkdiscard - are denied wherever they appear;
  - sudo is denied outright;
  - a QEMU -drive whose file= is not a literal path inside one of the repo's
    out/ directories is denied - relative like stage3/out/notes.img, or
    absolute under the repo; never a path with .., never a shell variable,
    since the hook cannot resolve one and must not guess;
  - the QEMU shorthands that name a disk another way (-hda..-hdd, -cdrom,
    -fda, -fdb, -blockdev, -pflash, -mtdblock, -sd) are denied: say it with
    -drive file= under out/ instead;
  - qemu-img is held to the same out/ rule on every path-shaped argument;
  - a Write or Edit aimed at anything under /dev is denied.

This matches PROSE deliberately, as the freeze does. A commit message that says
"no loop mount" is denied and goes in through `git commit -F` from a file
written with the Write tool. A false deny costs a reworded command; a false
allow costs a real disk.

Contract: exit 0 to allow, exit 2 to deny with the reason on stderr.
"""

import json
import os
import re
import sys

# The plan-approval marker (see require-plan-approval.py). Only Wajira's own
# hand, outside this session, may create it - so every route this session has
# to it is denied: Write/Edit below, and any Bash mention at all. Prose
# included, deliberately: there is no honest reason for a command here to
# name it.
PLAN_MARKER = "PLAN_APPROVED"

# The frozen acceptance machinery, as repo-relative paths. Add to this tuple to
# freeze another stage's tests; nothing else needs to change.
#
# Deliberately NOT frozen: stage1/mkimage.sh and stage2/mkimage.sh. They build
# and pack the artefact; they are not criteria. Each stage's test 1 judges the
# artefact that comes out - the PE fields, and esp.img read back with
# mdir/mtype - so the packing recipe has to stay fixable without disturbing a
# frozen file. stage2/FONT.md (paperwork) is not frozen either.
#
# stage2/font8x8.bin IS frozen: the pixel checker renders its expected text
# from that file, so an editable font would be an editable criterion - an
# all-blank font would pass a blank screen.
#
# stage3/NOTEBOOK.md IS frozen for the same reason: the assembler implements
# the on-disk format it describes and the checker parses by it, so an editable
# format would be an editable criterion. stage3/mkimage.sh stays unfrozen.
#
# Stage 4 (plan decision 13) freezes stage4/UMBILICAL.md for the NOTEBOOK.md
# reason, and broker/broker.py with it: the mock's framing, its record and
# its canned table are what test 3 judges the guest by, so an editable mock
# would be an editable criterion - it could learn to tolerate a malformed
# frame, or record a question it never received. broker/claude_backend.py,
# the one function that shells out to claude -p, is deliberately NOT frozen:
# the automated gate never runs it, and its flags must stay fixable at test
# 5. stage4/mkimage.sh stays unfrozen as every builder has.
#
# Stage 5 (plan decision 15) freezes stage5/GERMLINE.md for the UMBILICAL.md
# reason; stage5/component.asm AND stage5/component.bin because the test
# component's picture is what test 3 demands pixel by pixel and the checker
# holds the source to the binary; broker/germline.py because its mock
# table, its record, its cache and its dispatch are what tests 3 and 4
# judge by; and broker/rehearse.py because a bent rehearsal could pass a
# faulting blob - its verdicts are criteria. broker/broker.py stands
# untouched and still frozen: germline.py imports its framing. Deliberately
# NOT frozen: stage5/mkimage.sh (the recipe), stage5/stage5.asm (the thing
# under test) and broker/claude_backend.py (the one file the gate never
# runs, whose brief must stay fixable at test 5).
#
# Stage 6 ring 6a (plan decision 18) freezes stage6/GLASS.md for the
# GERMLINE.md reason - the assembler, the fixtures, the broker, the twin
# and the checker all implement or parse by it, the obs page's layout and
# the strip's text included; the three fixtures' sources AND binaries
# (stage6/app.asm and app.bin - test 3's known picture; hog and escapee,
# the two bad apps whose refusal test 4 demands, and a bent hog or escapee
# would be a passing one); broker/glass.py because its mock table, its
# record, its cache and its dispatch are what tests 3 and 4 judge by; and
# broker/twin.py because its nine verdicts are criteria - a bent twin could
# pass a hog. broker/germline.py and broker/rehearse.py stand untouched and
# still frozen: glass.py and twin.py import from them. Deliberately NOT
# frozen: stage6/mkimage.sh (the recipe), stage6/stage6.asm (the thing
# under test), broker/claude_backend.py (never run by the gate) and
# stage6/plan-6a.md (paperwork).
#
# Stage 6 ring 6b (plan decision 13) freezes stage6/PLANS.md and
# stage6/HOME.md for the GLASS.md reason - the broker parses plans by the
# one and the assembler and the checker implement and parse the home
# image by the other, so an editable document would be an editable
# criterion; the three plans plans/echo.md, plans/liar.md and
# plans/calculator.md because the twin's tests ARE those files (an edited
# plan would be an edited test, and the calculator is the owner's approved
# oracle); the two fixtures' sources AND binaries (stage6/echo.asm and
# echo.bin - test 3's known picture and the build the home image must
# hold hash for hash; liar.asm and liar.bin - the build test 4 demands be
# refused, and a bent liar would be an honest one); broker/plans.py
# because its dispatch, its key, its mock table and its record are what
# tests 3 and 4 judge by; and stage6/test-6b.sh and stage6/checkplans.py,
# the gate itself. Everything ring 6a froze stands. Deliberately NOT
# frozen: stage6/mkimage.sh, stage6/stage6.asm, broker/claude_backend.py
# and stage6/plan-6b.md, for the same reasons as before.
#
# Stage 6 ring 6c (plan decision 14) freezes the point app's source AND
# binary (stage6/pointer.asm and pointer.bin - test 3's known picture, the
# one five-callback fixture, and a bent one would be a passing one);
# broker/pointer.py because its mock row, its refusal of a bad point
# offset and the ring 6c section's Python it carries verbatim are what
# tests 2 to 4 judge by; and stage6/test-6c.sh and stage6/checkpointer.py,
# the gate itself. stage6/GLASS.md was frozen at ring 6a and stays so: its
# ring 6c section went in by the owner's own hand. Everything rings 6a and
# 6b froze stands. Deliberately NOT frozen: stage6/mkimage.sh,
# stage6/stage6.asm, broker/claude_backend.py, stage6/plan-6c.md and the
# section's draft under stage6/out/, for the same reasons as before.
PROTECTED = (
    "stage0/test.sh",
    "stage0/checkpixels.py",
    "stage1/test.sh",
    "stage1/checkbands.py",
    "stage2/test.sh",
    "stage2/checktext.py",
    "stage2/font8x8.bin",
    "stage3/test.sh",
    "stage3/checknotes.py",
    "stage3/NOTEBOOK.md",
    "stage4/test.sh",
    "stage4/checkumbilical.py",
    "stage4/UMBILICAL.md",
    "broker/broker.py",
    "stage5/test.sh",
    "stage5/checkgermline.py",
    "stage5/GERMLINE.md",
    "stage5/component.asm",
    "stage5/component.bin",
    "broker/germline.py",
    "broker/rehearse.py",
    "stage6/test.sh",
    "stage6/checkglass.py",
    "stage6/GLASS.md",
    "stage6/app.asm",
    "stage6/app.bin",
    "stage6/hog.asm",
    "stage6/hog.bin",
    "stage6/escapee.asm",
    "stage6/escapee.bin",
    "broker/glass.py",
    "broker/twin.py",
    "stage6/PLANS.md",
    "stage6/HOME.md",
    "plans/echo.md",
    "plans/liar.md",
    "plans/calculator.md",
    "stage6/echo.asm",
    "stage6/echo.bin",
    "stage6/liar.asm",
    "stage6/liar.bin",
    "broker/plans.py",
    "stage6/test-6b.sh",
    "stage6/checkplans.py",
    "stage6/pointer.asm",
    "stage6/pointer.bin",
    "broker/pointer.py",
    "stage6/test-6c.sh",
    "stage6/checkpointer.py",
)

BASENAMES = sorted({os.path.basename(p) for p in PROTECTED})
NAME_ALT = "|".join(re.escape(b) for b in BASENAMES)

# A path-shaped token ending in one of the protected basenames. The greedy
# prefix is what stops "mytest.sh" from matching as "test.sh".
CANDIDATE = re.compile(r"[\w./\\-]*(?:%s)" % NAME_ALT)

# A mention of a protected file is only a problem when it is being mutated.
# Each pattern pairs a mutating verb with the specific path that was found, so
# that redirecting the *output* of the tests somewhere (./stage0/test.sh > log)
# stays allowed. "%s" is filled with the escaped path literal.
MUTATIONS = (
    (r">>?\s*['\"]?%s", "redirecting output into it"),
    (r"\bsed\b[^;|&]*-i[^;|&]*%s", "sed -i"),
    (r"\btee\b[^;|&]*%s", "tee"),
    (r"\b(?:mv|cp|rm|truncate|shred|patch|dd|install|ln)\b[^;|&]*%s",
     "moving, copying over, removing or truncating it"),
    (r"\bgit\s+(?:checkout|restore|stash|apply|reset|revert|clean)\b[^;|&]*%s",
     "rewriting it from git"),
    (r"\bchmod\b[^;|&]*%s", "changing its mode"),
    # An assembler's or compiler's output flag aimed at it. Found at Stage 5:
    # with stage5/component.bin frozen, "nasm ... -o stage5/component.bin" was
    # a side door none of the patterns above knew.
    (r"(?:^|\s)-o\s*=?\s*['\"]?%s", "writing a tool's output (-o) over it"),
)

# An interpreter invocation that both mentions a protected file and shows a sign
# of writing (a heredoc script that opens it for writing, say).
INTERPRETER = re.compile(r"\b(?:python3?|perl|ruby|node|awk)\b")
WRITE_HINT = re.compile(
    r"open\s*\(|\bwrite\b|writelines|\bshutil\b|Path\s*\(|['\"][wa]\+?['\"]|"
    r"\bprint\s*\([^)]*file\s*="
)

# ----------------------------------------------------------- the bodyguard --

# The repo root: what the hook registration passes, or two directories up from
# this file. Used to judge absolute drive paths.
REPO = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO = os.path.abspath(REPO)

FOUNDATION_RULE = (
    "storage code touches only QEMU disk images until Stage 7, and never any "
    "disk holding real data")

# Every /dev mention in a command, with whatever path follows it.
DEV_MENTION = re.compile(r"/dev/[\w./+-]*")

# The /dev paths that are not disks: sources of bytes, sinks for them, and the
# terminal. Everything else under /dev is denied, block device or not.
DEV_ALLOWED = re.compile(
    r"^/dev/(?:zero|urandom|random|null|stdin|stdout|stderr|fd(?:/\d+)?|"
    r"tty\w*|pts(?:/\d+)?)/?$")

# Verbs that take a disk, wherever they appear - prose included.
STORAGE_VERBS = (
    (r"\b(?:mount|umount)\b", "mounting or unmounting a filesystem"),
    (r"\blosetup\b", "attaching a loop device"),
    (r"\bmkfs\b", "making a filesystem with mkfs"),
    (r"\b(?:fdisk|sfdisk|gdisk|parted)\b", "partitioning"),
    (r"\b(?:wipefs|blkdiscard)\b", "wiping a device"),
    (r"\bsudo\b", "sudo - nothing in this project needs root"),
)

# QEMU shorthands that attach a disk without saying file= under out/.
QEMU_SHORTHANDS = re.compile(
    r"(?<![\w-])-(?:hda|hdb|hdc|hdd|cdrom|fda|fdb|blockdev|pflash|mtdblock|sd)\b")

# Each -drive argument, quoted or bare; then the file= inside it.
DRIVE_ARG = re.compile(r"(?<![\w-])-drive\s+(?:\"([^\"]*)\"|'([^']*)'|(\S+))")
DRIVE_FILE = re.compile(r"(?:^|,)file=([^,]*)")

# qemu-img, up to the end of the pipeline stage it sits in.
QEMU_IMG = re.compile(r"\bqemu-img\b([^;|&]*)")
IMAGE_EXT = re.compile(r"\.(?:img|raw|qcow2?|vmdk|vdi|vhd|vhdx|iso|bin)$", re.I)


def inside_out(path):
    """Is this a literal path to a file inside one of the repo's out/
    directories? Returns (ok, why-not)."""
    p = path.strip().strip("'\"")
    if not p:
        return False, "an empty path"
    if "$" in p or "`" in p or "~" in p:
        return False, "a path with a shell variable or expansion the hook cannot resolve"
    p = p.replace("\\", "/")
    if p.startswith("/"):
        norm = os.path.normpath(p)
        if not norm.startswith(REPO + "/"):
            return False, "an absolute path outside the repository"
        rel = norm[len(REPO) + 1:]
    else:
        rel = p
    parts = [c for c in rel.split("/") if c not in ("", ".")]
    if ".." in parts:
        return False, "a path that climbs with .."
    if "out" not in parts[:-1]:
        return False, "a path that is not inside an out/ directory"
    return True, ""


def deny_storage(what, why):
    sys.stderr.write(
        "BLOCKED by .claude/hooks/protect-tests.py - the storage bodyguard.\n"
        "\n"
        "This call mentions %s (%s).\n"
        "\n"
        "The foundation's hard safety rule: %s. The only disks in this "
        "project's world are raw image files the test harness creates under a "
        "stage's out/ directory, attached to QEMU with -drive file=. Nothing "
        "else is a disk we are allowed to touch, in a command or in prose.\n"
        "\n"
        "If this is a false deny - a word in a commit message, say - reword "
        "the command, or put the text in a file with the Write tool and pass "
        "the file. Do not work around this hook.\n"
        % (what, why, FOUNDATION_RULE)
    )
    sys.exit(2)


def storage_guard(cmd):
    """The bodyguard's Bash arm. Returns only if the command is clean."""
    for m in DEV_MENTION.finditer(cmd):
        dev = m.group(0).rstrip(".,;:")
        if not DEV_ALLOWED.match(dev):
            deny_storage(dev, "a /dev path that is not one of the harmless "
                              "sources or sinks")

    for pattern, why in STORAGE_VERBS:
        m = re.search(pattern, cmd)
        if m:
            deny_storage("'%s'" % m.group(0), why)

    m = QEMU_SHORTHANDS.search(cmd)
    if m:
        deny_storage("'%s'" % m.group(0),
                     "a QEMU option that attaches a disk without a file= "
                     "under out/ - use -drive format=raw,file=<stage>/out/...")

    for m in DRIVE_ARG.finditer(cmd):
        arg = next(g for g in m.groups() if g is not None)
        for fm in DRIVE_FILE.finditer(arg):
            ok, why = inside_out(fm.group(1))
            if not ok:
                deny_storage("-drive file=%s" % fm.group(1), why)

    for m in QEMU_IMG.finditer(cmd):
        for tok in m.group(1).split():
            t = tok.strip("'\"")
            if not t or t.startswith("-"):
                continue
            if "/" in t or IMAGE_EXT.search(t):
                ok, why = inside_out(t)
                if not ok:
                    deny_storage("qemu-img on %s" % t, why)


# ---------------------------------------------------------------- the freeze --

def resolve(token):
    """Return the PROTECTED entry this token refers to, or None.

    A bare basename resolves to itself: we cannot tell which directory the
    command will run in, so we assume the worst.
    """
    t = str(token).replace("\\", "/")
    while t.startswith("./"):
        t = t[2:]
    if not t:
        return None

    base = t.rsplit("/", 1)[-1]
    if base not in BASENAMES:
        return None

    if "/" not in t:
        return base  # bare name - could be a command run from inside stage0/

    for prot in PROTECTED:
        if t == prot or t.endswith("/" + prot):
            return prot
    return None  # some other directory's file of the same name - not ours


def deny(target, why):
    sys.stderr.write(
        "BLOCKED by .claude/hooks/protect-tests.py.\n"
        "\n"
        "%s is frozen acceptance machinery, and this call would modify it "
        "(%s).\n"
        "\n"
        "The acceptance tests are written before the code and cannot be edited "
        "during implementation or a fix - that is the whole point of writing "
        "them first. Fix the implementation instead.\n"
        "\n"
        "If the TEST itself is genuinely wrong, stop and raise it with Wajira as "
        "a spec question. Do not work around this hook.\n" % (target, why)
    )
    sys.exit(2)


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # never break the session on a malformed payload

    tool = event.get("tool_name", "")
    args = event.get("tool_input") or {}

    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = args.get("file_path") or args.get("notebook_path") or ""
        if str(path).replace("\\", "/").startswith("/dev/"):
            deny_storage(path, "a device node as the target of a file edit")
        if os.path.basename(str(path).replace("\\", "/")) == PLAN_MARKER:
            deny(PLAN_MARKER, "the plan-approval marker - only Wajira's own "
                              "hand, outside this session, may create it")
        prot = resolve(path)
        if prot:
            deny(prot, "a direct %s" % tool)
        sys.exit(0)

    if tool == "Bash":
        cmd = args.get("command", "") or ""

        if PLAN_MARKER in cmd:
            deny(PLAN_MARKER, "a Bash command that mentions the plan-approval "
                              "marker - only Wajira's own hand, outside this "
                              "session, may touch it")

        # The bodyguard first, on every command, whatever else it mentions.
        storage_guard(cmd)

        # Every path-shaped mention of a protected basename, with the literal
        # text as it appeared, so the mutation check can target it exactly.
        hits = []
        for m in CANDIDATE.finditer(cmd):
            literal = m.group(0)
            prot = resolve(literal)
            if prot:
                hits.append((literal, prot))
        if not hits:
            sys.exit(0)

        for literal, prot in hits:
            esc = re.escape(literal)
            for pattern, why in MUTATIONS:
                if re.search(pattern % esc, cmd):
                    deny(prot, why)

        if INTERPRETER.search(cmd) and WRITE_HINT.search(cmd):
            deny(hits[0][1], "a script that writes files")

    sys.exit(0)


if __name__ == "__main__":
    main()
