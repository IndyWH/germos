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
        prot = resolve(path)
        if prot:
            deny(prot, "a direct %s" % tool)
        sys.exit(0)

    if tool == "Bash":
        cmd = args.get("command", "") or ""

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
