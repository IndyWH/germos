# Stage 1 spec — Owning the processor

**spec.md for Stage 1 · Cowork, 31 August 2026 · status: APPROVED by Wajira, 31 August 2026**

## What we are building

One UEFI application, hand-assembled in NASM as a PE32+ binary — no compiler, no C runtime, headers written byte by byte like everything else. OVMF (the UEFI firmware for QEMU) loads it from a FAT boot image. It lights the serial channel, takes the framebuffer at native resolution, throws the firmware's ladder away, wakes every core, and each core paints its own band on screen. Proves full control of the CPU. Everything runs only inside QEMU.

## Boot environment

QEMU q35 machine with OVMF (`-bios /usr/share/ovmf/OVMF.fd`). The firmware finds `EFI/BOOT/BOOTX64.EFI` on the FAT image and calls it in 64-bit long mode with boot services live. COM1 is still at 0x3F8. Stage 0's romantic BIOS path retires; from here on it is the practical UEFI road, as the foundation flags.

## The work, in behavioural order

1. Serial init, then log `S1: alive` — the first observable act, before anything else.
2. Query the Graphics Output Protocol, select the highest-resolution 32-bit mode, save the framebuffer address. Log `S1: gop <W>x<H> fb <addr>`.
3. Get the memory map and call ExitBootServices. Log `S1: boot services exited`.
4. Load our own GDT and our own identity-mapped page tables (2 MB pages covering low RAM and the framebuffer), then load CR3. The firmware's tables are gone; the machine now stands on structures we built. Log `S1: gdt and paging ours`.
5. Parse the ACPI MADT for the processor list. Log `S1: cores found <N>`.
6. Place a trampoline below 1 MB and wake every application processor with INIT-SIPI-SIPI. Each core atomically takes an index, paints its own band, and halts. **Only the BSP ever touches serial — one owner per device**, the concurrency doctrine's first appearance. The BSP paints band 0, waits for all check-ins, logs `S1: cores woken <N>`.
7. Log `S1: done`, halt everything.

## The screen

The screen splits into one equal horizontal band per core, at the GOP's native resolution, band i filled with colour i from a fixed cycling table with distinct neighbours. Eight cores, eight bands. The picture *is* the core count — visible proof that every core ran.

## Build and run

```
nasm -f bin stage1/stage1.asm -o stage1/out/BOOTX64.EFI
(mtools packs it into stage1/out/esp.img as EFI/BOOT/BOOTX64.EFI)
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd -drive format=raw,file=stage1/out/esp.img -serial stdio
```

New packages needed: `ovmf`, `mtools`.

## Acceptance tests

Written before the code, frozen behind the hook (extended to cover stage1's test files), all green before every commit.

1. **Artefact.** `BOOTX64.EFI` carries the MZ and PE magics, machine type x86-64 (0x8664), subsystem EFI application (10); `esp.img` contains `EFI/BOOT/BOOTX64.EFI` at the removable-media path.
2. **Serial.** A headless run (60-second timeout): the lines beginning `S1:` match the seven expected lines, in order, with found = woken = the `-smp` value. OVMF's own chatter is filtered out, which is why this test matches the `S1:` lines rather than the whole stream.
3. **Scaling.** Test 2's logic passes at `-smp 2` and `-smp 8` — the count must follow the machine, not be baked in.
4. **Pixels.** A screendump at `-smp 8` is the resolution the serial log claimed and shows exactly 8 equal solid bands in the expected colours.
5. **Oracle.** Wajira runs the windowed command. His word closes the stage.

## Rules carried forward

Serial before video. QEMU only; nothing written outside the repo; no real disk exists at any point. Every black-screen bug found on the way earns a CLAUDE.md line and a regression check.

## Decisions recorded at approval (owner, 31 August 2026)

1. **The mirror run.** Automated tests run at `-smp 2` and `-smp 8`; one manual `-smp 32` windowed run — the twin at full likeness of mlrig's 32 logical CPUs — happens before the stage closes.
2. **Resolution.** Highest-resolution 32-bit GOP mode: native in spirit.
3. **Timelines.** No cut line — the stage takes the sessions it takes. Owner's instruction: don't worry about the timelines.
