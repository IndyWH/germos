#!/usr/bin/env python3
"""PreToolUse hook: freeze the acceptance tests.

The foundation document's rule is that guarantees we care about become hooks,
not requests: the implementer is mechanically blocked from editing the
acceptance tests during implementation and fixes.

This hook denies any attempt to MODIFY a file in PROTECTED, by any route -
Write, Edit, MultiEdit, NotebookEdit, and Bash. The Bash arm is the one that
matters most, because that is how this session edits files.

Reading and RUNNING the tests stays allowed. They have to remain runnable.

If a test turns out to be genuinely wrong, that is a spec question for the owner,
not something the implementer edits away.

Matching is PATH-PRECISE, and that is deliberate. An earlier version matched the
bare basename anywhere, which caught a command run from inside stage0/ but also
denied the *creation* of stage1/test.sh - a different file, in a different stage,
that did not exist yet. Protecting a file we have not written is not a freeze, it
is a wall. So a candidate path is now resolved before it is judged:

  - a path with a directory part is protected only if it ends with one of the
    PROTECTED repo-relative paths (so absolute paths are caught, and
    stage1/test.sh is not);
  - a BARE basename with no directory part is still treated as protected, since
    it may be a command run from inside the protected file's own directory.
    Conservative on purpose: a false deny costs a reworded command, a false
    allow costs an edited acceptance test.

Everything is derived from PROTECTED, so freezing a new stage's tests is a
one-line change to that tuple.

Contract: exit 0 to allow, exit 2 to deny with the reason on stderr.
"""

import json
import os
import re
import sys

# The frozen acceptance machinery, as repo-relative paths. Add to this tuple to
# freeze another stage's tests; nothing else needs to change.
#
# Deliberately NOT frozen: stage1/mkimage.sh. It builds and packs the artefact,
# it is not a criterion. Stage 1's test 1 judges the artefact that comes out -
# the PE fields, and esp.img read back with mdir/mtype - so the packing recipe
# has to stay fixable without disturbing a frozen file.
PROTECTED = (
    "stage0/test.sh",
    "stage0/checkpixels.py",
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
        prot = resolve(path)
        if prot:
            deny(prot, "a direct %s" % tool)
        sys.exit(0)

    if tool == "Bash":
        cmd = args.get("command", "") or ""

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
