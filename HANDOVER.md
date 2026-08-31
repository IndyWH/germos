# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 1 September 2026 — **Stage 2 closed.** Wajira ran test 5
windowed, typed, and watched his keystrokes land; his word closes the stage.
The machine is interactive. Next: Stage 3 — Memory of its own (block storage,
virtio first, and a simple filesystem), which opens with a Cowork spec and
carries the foundation's hard safety rule: storage code touches only QEMU disk
images until Stage 7, never any disk holding real data.

---

## Where we are

| | |
|---|---|
| Stage | 3 — Memory of its own (not yet opened) |
| Status | Stage 2 **CLOSED**. No Stage 3 spec yet. |
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

## Stage 2 — Senses · closed 1 September 2026

**Goal (foundation §7):** keyboard input and a text console on the framebuffer;
the serial debug channel becomes permanent. Proves the machine is interactive.

Built on Stage 1's body, per the approved spec and plan (both committed, plus
plan amendment A1 — the sti-shadow hlt idiom): an IDT whose 32 exception stubs
print `ERR: exception <vector> at 0x<rip>` and halt (proven byte-precise with a
ud2 probe against the nasm listing); a text console — font8x8 scaled 2x into
16x16 cells, dark rgb(16,16,24) ground, light rgb(224,224,224) glyphs, the boot
log replayed from a serial mirror buffer, static block cursor, wrap, backspace,
shadow-buffer scrolling, the framebuffer never read; and an interrupt-driven
PS/2 keyboard — PIC remapped to 0x20/0x28 with only IRQ1 unmasked, a
scancode ring between the handler and the main loop, set-1 unshifted US
translation, E0 pairs and break codes swallowed. The screen has one owner: the
handler only buffers; the BSP main loop draws. On this machine the console is
**128x128 cells** on the 2048x2048 mode — measured, never baked in.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial — nine `S2:` lines in order, found = woken = smp, console = W/16 x H/16 | **PASS** |
| 3 | Typing — monitor `sendkey` hello+Enter; echo exactly `hello` CRLF, at `-smp 2` and `-smp 8` | **PASS** |
| 4 | Pixels — `> hello` pixel-correct per the shared font, prompt+cursor below, only the two console colours on screen | **PASS** |
| 5 | **Oracle — Wajira's eyeball** | **PASS — confirmed 1 September 2026** |

Tests 1–4 were committed **red** before any of `stage2.asm` existed and went
green exactly where the plan predicted: test 1 at item 7, tests 2–4 at item 10.
The shared font is `stage2/font8x8.bin` (public-domain font8x8, provenance and
hashes in `stage2/FONT.md` and pinned in `plan.md`), frozen alongside the tests
because the checker renders its expectations from it.

**Caveats carried forward:**

- **Stage 1's stand:** the x2APIC path and the trampoline fallback remain
  unproven; one machine, one firmware (QEMU q35 + OVMF).
- **The i8042 is not reconfigured** — QEMU's controller as OVMF leaves it
  delivers set-1 codes and interrupts (proven by the echo working). Cold
  controller init is a Stage 7 debt.
- **Unshifted only.** Shift, symbols-over-digits, and capitals are a later ring.
- **A parked AP that faults prints over serial** — a deliberate one-owner
  breach for a machine that is already lost (plan decision 9).

---

## The frozen acceptance machinery

`stage0/test.sh`, `stage0/checkpixels.py`, `stage1/test.sh`,
`stage1/checkbands.py`, `stage2/test.sh`, `stage2/checktext.py` and
`stage2/font8x8.bin` are frozen by `.claude/hooks/protect-tests.py`. The
builders (`stage1/mkimage.sh`, `stage2/mkimage.sh`) and `stage2/FONT.md` are
deliberately **not** frozen: recipe and paperwork, judged by their product.

The Stage 2 extension was verified with 55 payloads — 33 that must be denied,
22 that must be allowed — with Stage 0's and Stage 1's cases re-run alongside,
so freezing a new stage is shown not to have loosened an older one. The freeze
bit immediately (per Stage 1's amendment A4), demonstrated live: the first
attempt to run the payload table as a heredoc was itself denied, because the
payload text mentions frozen names near mutating verbs.

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

Everything has run inside QEMU. Stages 1 and 2 give QEMU firmware plus exactly
one drive: a raw FAT image under the stage's `out/`. OVMF is mapped read-only by
`-bios`. No block device, no loop mount, no `sudo`, nothing written outside
`/home/indy/Projects/ai-os` (bar scratch files in the session temp directory).
Stage 2's single network touch was the one-time fetch of the public-domain font,
verified against the sha256 pins recorded in `stage2/plan.md`.

## Next action

Cowork writes the Stage 3 spec — Memory of its own: block storage (virtio
first, NVMe second) and a simple filesystem, per foundation §7. The hard
safety rule is already standing and gets restated in the spec: **storage code
touches only QEMU disk images until Stage 7, and never any disk holding real
data.** Wajira approves the spec; then a fresh Claude Code session starts in
plan mode, commits `stage3/plan.md` for approval, and implements one commit
per numbered item — acceptance tests first and committed red, as ever. All
three closed stages' `test.sh` remain standing regression checks.
