# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 31 August 2026 — **Stage 1 closed.** Wajira ran test 5 and the
`-smp 32` mirror run and confirmed both. Stage 2 opens: spec drafted, three
judgement calls awaiting his answers.

---

## Where we are

| | |
|---|---|
| Stage | 2 — Senses (opening) |
| Status | Stage 1 **CLOSED**. `stage2/spec.md` is a **draft awaiting approval**; no plan yet, no code. |
| Repo | `/home/indy/Projects/ai-os` (branch `main`) |
| Machine | mlrig, native Ubuntu 26.04, 32 logical CPUs |
| Toolchain | NASM 3.01, QEMU 10.2.1, Python 3, OVMF, mtools — Stage 2 needs no new packages |

## The project in three lines

An operating system grown on each machine rather than shipped to it. A small
frozen core boots the machine and connects it to Claude, which writes everything
else as machine code fitted to that exact hardware. Nothing touches real
hardware until it has survived a rehearsal in the twin (QEMU).

---

## Stages closed

### Stage 0 — First pixel · closed 31 August 2026

Spectrum loading stripes and two byte-exact serial lines from a 512-byte BIOS
boot sector, 211 of 510 bytes used. `./stage0/test.sh` is a standing regression
check and is still green.

### Stage 1 — Owning the processor · closed 31 August 2026

One hand-written PE32+ UEFI application: serial first, GOP at the highest 32-bit
mode, ExitBootServices, our own GDT and 4 GB identity map, the ACPI MADT read for
the core count, every core woken with INIT-SIPI-SIPI off a sub-1MB trampoline,
and each core painting its own band. **The picture is the core count.**

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed at `EFI/BOOT/BOOTX64.EFI` | **PASS** |
| 2 | Serial — seven `S1:` lines in order, found = woken = 8 | **PASS** |
| 3 | Scaling — the same at `-smp 2` and `-smp 8` | **PASS** |
| 4 | Pixels — 8 equal solid bands at the resolution the log claimed | **PASS** |
| 5 | **Oracle — Wajira's eyeball** | **PASS — confirmed 31 August 2026** |
| — | **`-smp 32` mirror run** | **PASS — confirmed 31 August 2026** |

On this machine the chosen mode is **2048x2048 at 0x80000000** — measured, never
baked in; the pixel test reads the resolution out of the guest's own log from the
same run. Tests 1–4 were committed **red** before any of `stage1.asm` existed and
went green exactly where the plan predicted: test 1 at item 6, tests 2 and 3 at
item 12, test 4 at item 13.

Run the gate with `./stage1/test.sh` (about four minutes — each halted guest
burns its 60-second timeout, which is the expected outcome, not a fault).

**Caveats carried forward, still true:**

- **The x2APIC path is unproven.** OVMF leaves the BSP in xAPIC mode here
  (`apic_x2 = 0`, MMIO at `0xFEE00000`), so nothing has ever executed it.
- **The trampoline fallback is unproven.** The preferred address `0x8000` is
  granted every time, so the below-1MB memory-map scan has never been taken.
- **One machine, one firmware.** QEMU q35 with OVMF. No claim about real
  hardware; that is Stage 7.

---

## Stage 2 — Senses (opening)

**Goal (foundation §7):** keyboard input and a text console on the framebuffer;
the serial debug channel becomes permanent. Proves the machine is interactive.

`stage2/spec.md` is committed as a **draft**. It grows on Stage 1's body and adds
three organs: an IDT so CPU exceptions become readable serial messages instead of
silent reboots, an interrupt-driven PS/2 keyboard, and a text console on the
framebuffer. The bands retire; the console becomes the picture. Nine `S2:` boot
lines, then the channel carries the raw echo of what is typed.

### Open questions for the owner — these block the Stage 2 plan

The spec flags three judgement calls, with Cowork's recommendation first:

1. **Keyboard route.** Interrupt-driven via the remapped PIC *(recommended)*, or
   polling the i8042. The IDT arrives this stage either way.
2. **The font.** Embed the public-domain 8x8 `font8x8` scaled 2x *(recommended)*,
   or hand-draw our own.
3. **Shift and symbols.** Unshifted-only this stage *(recommended)*, or full
   shift handling now.

Nothing else is needed. No Stage 2 code exists and none should be written until
the spec is approved and a `stage2/plan.md` is committed and approved in turn.

---

## The frozen acceptance machinery

`stage0/test.sh`, `stage0/checkpixels.py`, `stage1/test.sh` and
`stage1/checkbands.py` are frozen by `.claude/hooks/protect-tests.py`. The
builders (`stage1/mkimage.sh`) are deliberately **not** frozen: they hold the
recipe, and the tests judge the artefact the recipe produces.

Verified with 91 payloads — 62 that must be denied, 29 that must be allowed —
with Stage 0's cases re-run alongside Stage 1's, so freezing a new stage is shown
not to have loosened an older one. **Freezing Stage 2's tests is a one-line
change**: add the paths to the `PROTECTED` tuple.

Two things learned about the hook, both now in CLAUDE.md:

- Only the hook **registration** is snapshotted at session start; the script is
  re-read on every call. A new hook waits for the next session, but edits to an
  already-registered one are live at once.
- It matches **prose** deliberately. A Bash command that merely mentions a frozen
  filename near a mutating verb is denied. Reword it, or use the Write/Edit
  tools, which judge the target path only.

`Stage 1 item 0` was an unplanned commit: the Stage 0 hook matched the bare
basename `test.sh` and so denied the *creation* of `stage1/test.sh`. Protecting a
file we have not written is a wall, not a freeze. Recorded as amendment A3 in
`stage1/plan.md`.

## Safety

Everything has run inside QEMU. Stage 1 gave QEMU firmware plus exactly one
drive: a raw FAT image under `stage1/out/`. OVMF is mapped read-only by `-bios`.
No block device, no loop mount, no `sudo`, nothing written outside
`/home/indy/Projects/ai-os` (bar scratch files in the session temp directory).

## Next action

Wajira answers the three Stage 2 judgement calls and approves `stage2/spec.md`.
Then a fresh Claude Code session starts in plan mode, commits `stage2/plan.md`
for approval, and implements one commit per numbered item — acceptance tests
first and committed red, as ever.
