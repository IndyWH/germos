# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 31 August 2026 — Stage 0 built, automated tests green, awaiting
Wajira's eyeball (test 4).

---

## Where we are

| | |
|---|---|
| Stage | 0 — First pixel |
| Status | **Built. Acceptance tests 1–3 green. Test 4 — Wajira's eyeball — pending.** |
| Repo | `/home/indy/Projects/ai-os` (branch `main`) |
| Machine | mlrig, native Ubuntu 26.04 |
| Toolchain | NASM 3.01, QEMU 10.2.1, Python 3 |

## The project in three lines

An operating system grown on each machine rather than shipped to it. A small
frozen core boots the machine and connects it to Claude, which writes everything
else as machine code fitted to that exact hardware. Nothing touches real
hardware until it has survived a rehearsal in the twin (QEMU).

## Stage 0 done-when

**Spectrum loading stripes visible in QEMU, plus the two serial lines**, byte-exact:

```
S0: alive
S0: stripes drawn, hello from the boot sector
```

## What was built

`stage0/stage0.asm` — one 512-byte boot sector, **211 of 510 bytes used, 299
free**, in the spec's layout order:

1. Entry: interrupts off, DS/ES/SS zeroed, stack at 0x7C00, `cld`, interrupts on.
2. Serial init, COM1 at 0x3F8: IER=0, divisor 1 (115200, 8N1), FIFO on, DTR/RTS.
3. `serial_print` — poll LSR bit 5, write a byte, repeat to NUL.
4. **Serial line 1, before any video** — the foundation's serial-log-from-byte-one rule.
5. `int 10h`, AX=0x0013 — VGA mode 13h, 320x200x256 at segment 0xA000.
6. Stripes: 200 rows of `rep stosb`, 320 bytes each. Rows 0–99 red (4) / cyan (3)
   every 4 rows; rows 100–199 blue (1) / yellow (14) every 2 rows.
7. Serial line 2.
8. Halt loop, then the strings, padding, and `0x55 0xAA`.

Independently confirmed against a screendump that the bands are the spec's
pattern and not merely the right colours in the right halves: 25 bands of 4 guest
rows red/cyan, then 50 bands of 2 guest rows blue/yellow.

## Test status

| # | Test | Status |
|---|---|---|
| 1 | Artefact — 512 bytes, signature `0x55 0xAA` | **PASS** |
| 2 | Serial — both lines, byte-exact, in order | **PASS** |
| 3 | Pixels — four colours, split top/bottom | **PASS** |
| 4 | **Oracle — Wajira's eyeball** | **pending — his word is the gate** |

Run tests 1–3 with `./stage0/test.sh` (exit 0 only if all three pass).
Test 4, windowed, from the repo root:

```
qemu-system-x86_64 -drive format=raw,file=stage0/out/stage0.img -serial stdio
```

Tests 1–3 were written and committed **red**, before any boot sector code
existed (items 1–3), and went green in the order the plan predicted: test 1 at
item 5, test 2 at item 7 (after showing only line 1 at item 6), test 3 at item 7.

## The frozen acceptance machinery

`stage0/test.sh` and `stage0/checkpixels.py` are the gate, and they are frozen.
`.claude/hooks/protect-tests.py` is a `PreToolUse` hook, registered in
`.claude/settings.json`, that denies any attempt to modify either file by Write,
Edit, MultiEdit or Bash, while leaving them readable and runnable. Verified
against 23 payloads — 13 that must be denied, 10 that must be allowed.

**Caveat, recorded honestly:** Claude Code snapshots its hooks at session start,
so a hook added mid-session is not live until the next session — confirmed with a
deliberate no-op that was *not* blocked. During the session that created it the
freeze was honoured by hand: neither file was touched after item 3. It bites
mechanically from the next session on.

## Decisions recorded (Stage 0 spec, approved by Wajira 31 August 2026)

1. **Environment.** Native Ubuntu 26.04 on mlrig. WSL2 is retired and removed
   from the project documents. Repo lives at `/home/indy/Projects/ai-os`.
2. **Repo name.** Neutral placeholder `ai-os` until the owner names the project.
3. **Stripe pattern.** The two-band pilot-and-data pattern as specced, not the
   plainer single pattern.
4. **Boot path.** BIOS (SeaBIOS), 16-bit real mode, load address 0x7C00. Stage 0
   only; from Stage 1 the project takes the UEFI road.

Carried from the foundation: Fable specs and Opus-at-high implements; no API
spend; the stage order; the name is reserved for the owner.

## Safety

Everything ran inside QEMU. QEMU was given exactly one drive: a 512-byte raw file
under `stage0/out/`. No block device, no loop mount, nothing written outside
`/home/indy/Projects/ai-os` (bar scratch files in the session temp directory).

## Open questions for the owner

None. One thing needs him: **test 4.**

## Next action

Wajira runs the windowed command above and confirms it looks like a Spectrum
loading. If yes, Stage 0 is closed and Stage 1 (UEFI, long mode, GOP) can be
specced. If no, the fix is in `stage0.asm` — the tests do not move.
