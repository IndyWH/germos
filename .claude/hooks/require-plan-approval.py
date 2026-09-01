#!/usr/bin/env python3
"""PreToolUse hook: the plan-approval gate.

The build loop's rule: plan.md is committed and approved by Wajira BEFORE any
implementation code is written. In full-auto permission mode, Claude Code
approves its own exit from plan mode, so the rule was a request, not a
guarantee. This hook makes it mechanical, in the project's own style.

Exiting plan mode is allowed only when the owner has placed his approval on
disk: a file named PLAN_APPROVED at the repo root. Wajira creates it himself,
from his own terminal, after the plan has been committed and reviewed:

    echo approved > PLAN_APPROVED

The hook consumes the marker as it lets the exit through - one approval opens
the gate exactly once. The implementer cannot forge it: protect-tests.py denies
every Write, Edit, or Bash mention of PLAN_APPROVED, so the only hand that can
create the file is one outside this session. That is the point.

Contract: exit 0 to allow, exit 2 to deny with the reason on stderr.
"""

import json
import os
import sys

REPO = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARKER = os.path.join(os.path.abspath(REPO), "PLAN_APPROVED")


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # never break the session on a malformed payload

    if event.get("tool_name", "") != "ExitPlanMode":
        sys.exit(0)

    if os.path.isfile(MARKER):
        try:
            os.remove(MARKER)  # one approval, one exit
        except OSError:
            pass
        sys.exit(0)

    sys.stderr.write(
        "BLOCKED by .claude/hooks/require-plan-approval.py - the plan gate.\n"
        "\n"
        "The plan is not yet approved. The build loop: commit plan.md, then\n"
        "STOP. Wajira pastes the plan to Cowork for review, and approves by\n"
        "running, in his own terminal at the repo root:\n"
        "\n"
        "    echo approved > PLAN_APPROVED\n"
        "\n"
        "Only then does plan mode open. Do not create PLAN_APPROVED yourself\n"
        "- the other hook denies it, and working around either hook is\n"
        "working around the owner. Tell Wajira the plan is ready and wait.\n"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
