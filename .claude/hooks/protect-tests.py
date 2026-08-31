#!/usr/bin/env python3
"""PreToolUse hook: freeze the Stage 0 acceptance tests.

The foundation document's rule is that guarantees we care about become hooks,
not requests: the implementer is mechanically blocked from editing the
acceptance tests during implementation and fixes.

This hook denies any attempt to MODIFY stage0/test.sh or stage0/checkpixels.py,
by any route - Write, Edit, MultiEdit, NotebookEdit, and Bash. The Bash arm is
the one that matters most, because that is how this session edits files.

Reading and RUNNING the tests stays allowed. They have to remain runnable.

If a test turns out to be genuinely wrong, that is a spec question for the owner,
not something the implementer edits away.

Contract: exit 0 to allow, exit 2 to deny with the reason on stderr.
"""

import json
import os
import re
import sys

PROTECTED = ("stage0/test.sh", "stage0/checkpixels.py")

# Matches either the repo-relative path or the bare basename, so that a command
# run from inside stage0/ is caught too.
FILE_ALT = r"(?:stage0[/\\])?(?:test\.sh|checkpixels\.py)"

# A mention of a protected file is only a problem when it is being mutated.
# Each pattern pairs a mutating verb with the filename, so that redirecting the
# *output* of the tests somewhere (./stage0/test.sh > log) stays allowed.
MUTATIONS = (
    (r">>?\s*['\"]?[^\s;|&<>]*" + FILE_ALT, "redirecting output into it"),
    (r"\bsed\b[^;|&]*-i[^;|&]*" + FILE_ALT, "sed -i"),
    (r"\btee\b[^;|&]*" + FILE_ALT, "tee"),
    (r"\b(?:mv|cp|rm|truncate|shred|patch|dd|install|ln)\b[^;|&]*" + FILE_ALT,
     "moving, copying over, removing or truncating it"),
    (r"\bgit\s+(?:checkout|restore|stash|apply|reset|revert|clean)\b[^;|&]*" + FILE_ALT,
     "rewriting it from git"),
    (r"\bchmod\b[^;|&]*" + FILE_ALT, "changing its mode"),
)

# An interpreter invocation that both mentions a protected file and shows a sign
# of writing (a heredoc script that opens it for writing, say).
INTERPRETER = re.compile(r"\b(?:python3?|perl|ruby|node|awk)\b")
WRITE_HINT = re.compile(
    r"open\s*\(|\bwrite\b|writelines|\bshutil\b|Path\s*\(|['\"][wa]\+?['\"]|"
    r"\bprint\s*\([^)]*file\s*="
)


def deny(target, why):
    sys.stderr.write(
        "BLOCKED by .claude/hooks/protect-tests.py.\n"
        "\n"
        "%s is frozen acceptance machinery for Stage 0, and this call would "
        "modify it (%s).\n"
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
        norm = str(path).replace("\\", "/")
        for prot in PROTECTED:
            if norm.endswith(prot) or os.path.basename(norm) == os.path.basename(prot):
                deny(prot, "a direct %s" % tool)
        sys.exit(0)

    if tool == "Bash":
        cmd = args.get("command", "") or ""
        if not re.search(FILE_ALT, cmd):
            sys.exit(0)  # does not mention the tests at all

        hit = re.search(FILE_ALT, cmd).group(0)
        for pattern, why in MUTATIONS:
            if re.search(pattern, cmd):
                deny(hit, why)
        if INTERPRETER.search(cmd) and WRITE_HINT.search(cmd):
            deny(hit, "a script that writes files")

    sys.exit(0)


if __name__ == "__main__":
    main()
