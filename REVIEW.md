# REVIEW.md

How Cowork reviews CC's work, per the foundation's build loop. Kept light on
purpose. The reviewer reads the actual files from the repo, never only the log.

## Order of review

1. **Bugs first.** Trace the logic by hand where it is cheap (flag tricks,
   segment arithmetic, off-by-ones, concurrency). Anything touching storage or
   memory maps gets a disassembly-level read.
2. **Safety second.** QEMU only; nothing written outside the repo; no real disk
   device anywhere in a command; frozen files (acceptance tests, umbilical,
   crypto when they exist) untouched during implementation and fixes.
3. **Spec alignment third.** Behaviour against the stage spec.md, line by line;
   the done-when; exact bytes where the spec names exact bytes.
4. **Process fourth.** Tests written and committed red before code; one commit
   per numbered item; tests green before each commit; HANDOVER.md and CLAUDE.md
   updated as we go, not after.

## Verdicts

One of three, stated plainly at the top of the review:

- **clean** — proceed to the oracle test.
- **fix first** — named defects go back to CC before Wajira spends his time.
- **stop** — a safety rule was crossed; work halts and Wajira decides.

## Rules for the reviewer

- Nits are capped at two per review, marked non-blocking, and never delay a
  clean verdict.
- Honest caveats from CC (a hook not yet live, a test weaker than it looks) are
  credited, verified, and recorded — never punished. Bad news travelling fast is
  a feature of this team.
- The reviewer checks claims, not vibes: green tests are re-read as code, and at
  least one claim per review is verified independently.
