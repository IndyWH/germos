# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 31 August 2026 — Stage 1 built, **all four automated tests
green**, awaiting Wajira's eyeball (test 5) and the `-smp 32` mirror run.

---

## Where we are

| | |
|---|---|
| Stage | 1 — Owning the processor |
| Status | **Built. Acceptance tests 1–4 green. Test 5 — Wajira's eyeball — pending.** |
| Repo | `/home/indy/Projects/ai-os` (branch `main`) |
| Machine | mlrig, native Ubuntu 26.04, 32 logical CPUs |
| Toolchain | NASM 3.01, QEMU 10.2.1, Python 3, OVMF, mtools — all already installed |

## The project in three lines

An operating system grown on each machine rather than shipped to it. A small
frozen core boots the machine and connects it to Claude, which writes everything
else as machine code fitted to that exact hardware. Nothing touches real
hardware until it has survived a rehearsal in the twin (QEMU).

---

## Stage 0 — closed, 31 August 2026

Spectrum loading stripes plus two byte-exact serial lines, from a 512-byte BIOS
boot sector. Wajira ran test 4 and gave his word. `./stage0/test.sh` is a
**standing regression check** and is still green.

---

## Stage 1 — built, awaiting the oracle

**Done-when:** the UEFI path — long mode, paging, every core woken and counted,
the GOP framebuffer, pixels at native resolution. Proves full control of the CPU.

### What was built

`stage1/stage1.asm` — one hand-written PE32+ UEFI application, in the spec's
behavioural order:

1. **Headers.** DOS stub, COFF and PE32+ optional header, two sections
   (`.text` RX, `.data` RW with the BSS as VirtualSize). Relocations stripped,
   every reference RIP-relative, `ImageBase 0x400000`.
2. **Serial first** — COM1 115200 8N1, then `S1: alive`, before anything else.
3. **GOP** — every mode queried, only 32-bit linear formats eligible, highest
   area wins. On this machine: **2048x2048 at 0x80000000**, measured not assumed.
4. **ExitBootServices** — static 16 KB map buffer, trampoline page claimed
   first, stale-key retry, then interrupts down and onto our own stack.
5. **Our own GDT and page tables** — four descriptors; 4 GB identity-mapped in
   2 MB pages (24 KB of tables); framebuffer pages marked uncached; `CR3` loaded.
6. **MADT** — RSDP from the EFI configuration table, XSDT, `APIC` table; type 0
   and type 9 processor entries counted and their APIC IDs recorded.
7. **The wake** — trampoline copied below 1 MB and patched, INIT-SIPI-SIPI to
   every core but the BSP, PIT-timed. Each core takes a band index with a locked
   `xadd`, paints its band, and checks in. **Only the BSP ever touches COM1.**

The seven serial lines, in order:

```
S1: alive
S1: gop 2048x2048 fb 0x0000000080000000
S1: boot services exited
S1: gdt and paging ours
S1: cores found 8
S1: cores woken 8
S1: done
```

### Test status

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed at `EFI/BOOT/BOOTX64.EFI` | **PASS** |
| 2 | Serial — seven `S1:` lines in order, found = woken = 8 | **PASS** |
| 3 | Scaling — the same at `-smp 2` and `-smp 8` | **PASS** |
| 4 | Pixels — 8 equal solid bands at the resolution the log claimed | **PASS** |
| 5 | **Oracle — Wajira's eyeball** | **pending — his word is the gate** |

`./stage1/test.sh` exits 0. It takes about four minutes: each halted guest burns
its 60-second timeout, which is the expected outcome, not a fault.

Tests 1–4 were written and committed **red**, before any of `stage1.asm`
existed, and went green in the order the plan predicted: test 1 at item 6,
tests 2 and 3 at item 12, test 4 at item 13.

### Verified beyond the automated gate

- **`-smp 32` dry run** — 32 found, 32 woken, and all 32 bands confirmed solid
  and in the right colours (64 rows each). Wajira's mirror run should hold no
  surprises.
- **Screendump geometry** — 2048x2048, 1:1, so test 4's exact-equality
  assertion is sound. Stage 0's line-doubling gotcha is a VGA property and does
  not apply to a linear framebuffer.
- **RIP-relative addressing** — checked from the instruction encodings, not
  assumed, because a page table loaded from a wrong address is a triple fault.

### Honest caveats

- **The x2APIC path is unproven.** OVMF leaves the BSP in xAPIC mode here
  (`apic_x2 = 0`, MMIO at `0xFEE00000`), so only the xAPIC path is exercised.
  The x2APIC path is written and reasoned about but nothing has run it.
- **The trampoline fallback is unproven.** The preferred address `0x8000` is
  granted every time, so the "scan the memory map for a page below 1 MB"
  fallback has never been taken.
- **One core count, one machine.** Everything here is QEMU q35 with OVMF. No
  claim is made about real hardware; that is Stage 7.

## The frozen acceptance machinery

`stage0/test.sh`, `stage0/checkpixels.py`, `stage1/test.sh` and
`stage1/checkbands.py` are frozen by `.claude/hooks/protect-tests.py`.
`stage1/mkimage.sh` is deliberately **not** frozen: it is the recipe, and the
tests judge the artefact it produces.

Verified with 91 payloads — 62 that must be denied, 29 that must be allowed —
with Stage 0's cases re-run alongside Stage 1's to show that freezing a new
stage did not loosen an older one.

**Stage 0's caveat is discharged and corrected.** Only the hook *registration*
is snapshotted at session start; the script is re-read on every call. So the
Stage 1 freeze bit immediately, in the same session that added it — proven with
a deliberate no-op that was blocked.

**One unplanned commit, `Stage 1 item 0`.** The Stage 0 hook matched the bare
basename `test.sh`, so it denied the *creation* of `stage1/test.sh` by every
legitimate route. Protecting a file we have not written is a wall, not a freeze.
The fix resolves a candidate path before judging it; all 16 Stage 0 denials are
unchanged. Recorded in `stage1/plan.md` as amendment A3.

## Decisions recorded (Stage 1 spec, approved by Wajira 31 August 2026)

1. **The mirror run.** Automated tests at `-smp 2` and `-smp 8`; one manual
   `-smp 32` windowed run before the stage closes.
2. **Resolution.** Highest-resolution 32-bit GOP mode.
3. **Timelines.** No cut line; plan for correctness.

Cowork's plan review added two amendments, both implemented: **A1** the ICR
delivery-status poll is xAPIC-only, and **A2** the map-buffer error names the
size needed.

## Safety

Everything ran inside QEMU. QEMU was given firmware plus exactly one drive: a
raw FAT image under `stage1/out/`. `/usr/share/ovmf/OVMF.fd` is mapped read-only
by `-bios`. No block device, no loop mount, no `sudo`, nothing written outside
`/home/indy/Projects/ai-os` (bar scratch files in the session temp directory).

## Open questions for the owner

None. Two things need him: **test 5**, and the **`-smp 32` mirror run**.

## Next action

Wajira runs the two windowed commands below. If the bands and the serial lines
are right, Stage 1 is closed and Stage 2 (keyboard, text console) can be specced.
If not, the fix is in `stage1.asm` — the tests do not move.

```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage1/out/esp.img -serial stdio

qemu-system-x86_64 -machine q35 -m 256M -smp 32 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage1/out/esp.img -serial stdio
```
