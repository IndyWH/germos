# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 31 August 2026 — repository created, Stage 0 starting.

---

## Where we are

| | |
|---|---|
| Stage | 0 — First pixel |
| Status | Plan approved and committed. Acceptance tests 1-3 written and frozen. Boot sector next. |
| Repo | `/home/indy/Projects/ai-os` (branch `main`) |
| Machine | mlrig, native Ubuntu 26.04 |
| Toolchain | NASM 3.01, QEMU 10.2.1, Python 3 (PIL available) — all confirmed present |

## The project in three lines

An operating system grown on each machine rather than shipped to it. A small
frozen core boots the machine and connects it to Claude, which writes everything
else as machine code fitted to that exact hardware. Nothing touches real
hardware until it has survived a rehearsal in the twin (QEMU).

## Today's goal — Stage 0 done-when

**Spectrum loading stripes visible in QEMU, plus the two serial lines**, byte-exact:

```
S0: alive
S0: stripes drawn, hello from the boot sector
```

One 512-byte boot sector, NASM, BIOS path, VGA mode 13h. Everything runs inside
QEMU only. No real disk is in reach at any point.

## Decisions recorded (Stage 0 spec, approved by Wajira 31 August 2026)

1. **Environment.** Native Ubuntu 26.04 on mlrig. WSL2 is retired and removed
   from the project documents. Repo lives at `/home/indy/Projects/ai-os`.
2. **Repo name.** Neutral placeholder `ai-os` until the owner names the project.
3. **Stripe pattern.** The two-band pilot-and-data pattern as specced, not the
   plainer single pattern:
   - Rows 0–99: red (4) and cyan (3), swapping every 4 rows — slow pilot bands.
   - Rows 100–199: blue (1) and yellow (14), swapping every 2 rows — fast data bands.
4. **Boot path.** BIOS (SeaBIOS), 16-bit real mode, load address 0x7C00. Stage 0
   only; from Stage 1 the project takes the UEFI road.

Decisions carried from the foundation document: Fable specs and Opus-at-high
implements; no API spend; the stage order; the name is reserved for the owner.

## Acceptance tests (from the spec — these are the gate)

1. **Artefact.** `stage0.img` is exactly 512 bytes, last two bytes `0x55 0xAA`.
2. **Serial.** Headless run captures both serial lines, byte-exact and in order.
3. **Pixels.** Scripted `screendump` shows all four stripe colours, red/cyan only
   in the top half, blue/yellow only in the bottom half.
4. **Oracle.** Wajira runs the windowed command and confirms it looks like a
   Spectrum loading. **His word is the gate for the stage.** Manual, always.

Tests 1–3 live in `stage0/test.sh` and are written *before* the boot sector code,
so they exist and fail first.

## Open questions for the owner

None currently.

## The frozen acceptance machinery

`stage0/test.sh` and `stage0/checkpixels.py` are the gate, and they are frozen.
`.claude/hooks/protect-tests.py` is a `PreToolUse` hook, registered in
`.claude/settings.json`, that denies any attempt to modify either file by Write,
Edit, MultiEdit or Bash, while leaving them readable and runnable. Verified
against 23 payloads — 13 that must be denied, 10 that must be allowed.

**Caveat, recorded honestly:** Claude Code snapshots its hooks at session start,
so a hook added mid-session is not live until the next session. During the
session that created it the freeze was honoured by hand — neither file was
touched after item 3 — and it bites mechanically from the next session on.

## Next action

Items 5-7: write `stage0/stage0.asm` to the spec's layout, one commit per item,
serial before video. Then item 8, HANDOVER close-out and the manual test 4.
