# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 31 August 2026 — **Stage 0 closed.** Wajira ran test 4 and
confirmed the stripes and both serial lines. Stage 1 opens: spec approved,
plan being written.

---

## Where we are

| | |
|---|---|
| Stage | 1 — Owning the processor (opening) |
| Status | Stage 0 **CLOSED**. Stage 1 spec approved; `stage1/plan.md` in draft, awaiting Wajira's approval before any code. |
| Repo | `/home/indy/Projects/ai-os` (branch `main`) |
| Machine | mlrig, native Ubuntu 26.04, 32 logical CPUs |
| Toolchain | NASM 3.01, QEMU 10.2.1, Python 3, OVMF (`/usr/share/ovmf/OVMF.fd`), mtools |

## The project in three lines

An operating system grown on each machine rather than shipped to it. A small
frozen core boots the machine and connects it to Claude, which writes everything
else as machine code fitted to that exact hardware. Nothing touches real
hardware until it has survived a rehearsal in the twin (QEMU).

---

## Stage 0 — closed, 31 August 2026

**Done-when, met in full:** Spectrum loading stripes visible in QEMU, plus the
two serial lines, byte-exact:

```
S0: alive
S0: stripes drawn, hello from the boot sector
```

| # | Test | Status |
|---|---|---|
| 1 | Artefact — 512 bytes, signature `0x55 0xAA` | **PASS** |
| 2 | Serial — both lines, byte-exact, in order | **PASS** |
| 3 | Pixels — four colours, split top/bottom | **PASS** |
| 4 | **Oracle — Wajira's eyeball** | **PASS — confirmed 31 August 2026** |

Wajira ran the windowed command, saw the stripes and both serial lines, and
gave his word. That closed the stage. The gate stays runnable: `./stage0/test.sh`
is green as of the Stage 1 opening, and stays a standing regression check.

### What was built

`stage0/stage0.asm` — one 512-byte boot sector, **211 of 510 bytes used, 299
free**: entry and segment setup, COM1 serial init at 115200 8N1, `serial_print`,
serial line 1 **before any video**, `int 10h` mode 13h, 200 rows of `rep stosb`
stripes (rows 0–99 red/cyan every 4 rows, rows 100–199 blue/yellow every 2 rows),
serial line 2, halt loop, strings, padding, `0x55 0xAA`.

Independently confirmed against a screendump: 25 bands of 4 guest rows red/cyan,
then 50 bands of 2 guest rows blue/yellow — the spec's pattern, not merely the
right colours in the right halves.

Tests 1–3 were written and committed **red**, before any boot sector code
existed, and went green in the order the plan predicted: test 1 at item 5,
test 2 at item 7 (after showing only line 1 at item 6), test 3 at item 7.

### The freeze, and the caveat now discharged

The Stage 0 acceptance machinery is frozen by `.claude/hooks/protect-tests.py`,
a `PreToolUse` hook registered in `.claude/settings.json`. Verified against 23
payloads — 13 denied, 10 allowed.

Stage 0 recorded an honest caveat: Claude Code snapshots hooks at session start,
so the hook was **not** live during the session that wrote it, and the freeze was
honoured by hand instead.

**That caveat is now discharged.** In this session — the first since the hook was
created — a deliberate mode-change no-op against the frozen test script (harmless
had it been allowed, since the file is already executable) was **blocked** by the
hook, and reading and running the tests still work. The freeze is mechanical from
here on.

**One shortcoming found while doing it,** recorded honestly and carried into the
Stage 1 plan: the hook matches a mutating verb near a protected filename anywhere
in a Bash command string, so *prose that merely mentions* the frozen files
alongside such a verb — a commit message describing this very test — is denied
too. Nothing was worked around; the prose was reworded. The Stage 1 extension of
the hook inherits the issue and will be tested for it explicitly.

---

## Stage 1 — opening

**Goal (foundation §7):** the UEFI boot path — 64-bit long mode, paging, every
core woken and counted, the GOP framebuffer, pixels at native resolution. Proves
full control of the CPU.

`stage1/spec.md` is approved by Wajira, 31 August 2026. One hand-written PE32+
UEFI application, loaded by OVMF from a FAT image, that lights serial first,
takes the highest-resolution 32-bit GOP mode, exits boot services, stands up its
own GDT and identity-mapped page tables, counts cores from the ACPI MADT, wakes
every application processor with INIT-SIPI-SIPI, and has each core paint its own
horizontal band. The picture *is* the core count.

### Decisions recorded at Stage 1 approval (owner, 31 August 2026)

1. **The mirror run.** Automated tests at `-smp 2` and `-smp 8`; one manual
   `-smp 32` windowed run — the twin at full likeness of mlrig's 32 logical
   CPUs — before the stage closes.
2. **Resolution.** Highest-resolution 32-bit GOP mode: native in spirit.
3. **Timelines.** No cut line. The stage takes the sessions it takes; plan for
   correctness, not for tonight.

Carried from the foundation: Fable specs and Opus-at-high implements; no API
spend; the stage order; the name is reserved for the owner.

## Safety

Everything has run inside QEMU. Stage 0 gave QEMU exactly one drive: a 512-byte
raw file under `stage0/out/`. Stage 1 gives it exactly one drive: a FAT image
under `stage1/out/`, plus OVMF as firmware. No block device, no loop mount,
nothing written outside `/home/indy/Projects/ai-os`. No real disk device is
touched, ever, before Stage 7.

## Open questions for the owner

One: **approval of `stage1/plan.md`**, once written. No implementation code is
written before that approval.

## Next action

Write `stage1/plan.md` in plan mode, commit it, and stop for Wajira's approval.
