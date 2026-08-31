# CLAUDE.md

Kept under one page. Source of truth is `ai-os-foundation.md`; current state is
`HANDOVER.md`.

## Build and test

```bash
# Stage 0 - closed, kept as a standing regression check
nasm -f bin stage0/stage0.asm -o stage0/out/stage0.img
./stage0/test.sh

# Stage 1
./stage1/mkimage.sh    # assemble stage1.asm, pack the FAT image (not frozen)
./stage1/test.sh       # acceptance tests 1-4. ~4 min: each halted guest burns
                       # its 60s timeout, which is the expected outcome
```

Windowed, for the oracle test:

```bash
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage1/out/esp.img -serial stdio
```

Each stage's `test.sh` is its gate. It must be green before every commit that
should pass it, and earlier stages stay green forever.

## Conventions

- **Evaluation-first.** Acceptance tests are written before the code they judge.
- **Draft until approved.** `plan.md` is committed and approved before any
  implementation code is written.
- **One commit per numbered item** from `plan.md`. Small commits; the last known
  good state is minutes away.
- **Tests green before every commit.** No exceptions once the tests are expected
  to pass.
- **Update `HANDOVER.md` as you go**, not at the end of the week.
- **The second time a mistake is corrected, the correction goes into CLAUDE.md**
  — into the gotchas section below.
- **Guarantees are hooks, not requests.** Acceptance tests cannot be edited
  during implementation or a fix; `.claude/hooks/protect-tests.py` blocks it.
  Freezing a new stage's tests is one line: add the paths to `PROTECTED`.
- **The gate is frozen; the builder is not.** `test.sh` and the pixel checkers
  hold the criteria. `mkimage.sh` holds the recipe, and stays fixable.
- **QEMU only.** Nothing outside this folder is written. No real disk device is
  touched, ever, at any stage before Stage 7.

## Bare-metal gotchas

Grown as we hit them. Every black-screen bug earns a line here and a regression
test in the twin.

- **Serial before video.** The first observable act of any stage is a serial
  line. A black screen with no serial output means the code died before it ran;
  a black screen *with* serial output means video setup is the bug. This
  distinction is the whole debugging strategy.
- **Real mode segments.** At entry only `CS:IP` is trustworthy. Zero `DS`, `ES`
  and `SS` explicitly, set the stack, and do it with interrupts off.
- **NASM `-f bin` is literal.** No sections, no relocation. `org 0x7C00` must be
  declared or every label is wrong by 0x7C00.
- **`times 510-($-$$) db 0` fails loudly** if the code overruns 510 bytes. That
  error message is a feature, not a build break to work around.
- **`resb` is zero-*filled* by `-f bin`, not reserved.** Everything is one
  progbits blob, so a BSS declared with `resb` lands in the output file. Declare
  it with `absolute` instead and let the PE loader zero-fill `VirtualSize`
  minus `SizeOfRawData`. Caught when a 12 KB artefact quietly became 45 KB.
- **A label is not a scalar.** `(label + n) & mask` is rejected; subtract `$$`
  first.
- **Mode 13h clears the framebuffer.** Set the mode *before* writing pixels, or
  the stripes are wiped by the mode switch.
- **A0000h is a segment, not an address.** In real mode write pixels via
  `ES = 0xA000` and a 16-bit offset; the offset wraps at 64 KB.
- **QEMU line-doubles mode 13h**, but *not* a linear GOP framebuffer. A 320x200
  guest screendumps at 640x400; a 2048x2048 GOP mode screendumps 1:1. Never
  hard-code a resolution in a pixel check — read it from the guest's own log.
- **Stride is `PixelsPerScanLine`, never the width.** They are allowed to
  differ, and assuming otherwise skews every row down the screen.
- **Map the framebuffer uncached** (`PWT|PCD`). Left writeback, pixels can sit
  in a cache line and never reach the screen — a black screen with a serial log
  claiming success.
- **The ExitBootServices map key goes stale** if *anything* allocates after
  `GetMemoryMap` — including your own `AllocatePages`. On
  `EFI_INVALID_PARAMETER`, re-fetch the map and retry. Keep the map in a static
  buffer, so fetching it cannot itself invalidate it.
- **Walk a UEFI memory map by `DescriptorSize`**, never by the structure's size.
- **Relocations stripped means the loader must honour `ImageBase`.** EDK2
  allocates a relocs-stripped image at its preferred address and cannot fall
  back. Prove the chosen base works; do not assume it.
- **x2APIC has no delivery-status bit.** Poll ICR bit 12 on the xAPIC path only;
  in x2APIC mode it is reserved and the `wrmsr` is itself the serialising event,
  so polling spins for ever.
- **OVMF chatters on COM1; SeaBIOS does not.** Stage 0 could compare the whole
  serial stream byte for byte. From Stage 1 the test must extract the guest's
  own lines out of the firmware's noise.
- **Repeated log lines mean a triple fault, not a repeated print.** After
  ExitBootServices there is no IDT, so any exception reboots. That is why the
  test demands *exactly* seven lines rather than at least seven.
- **A halted guest never exits QEMU.** Wrap headless runs in `timeout` and treat
  exit 124 as the expected success signal; any other non-zero exit is real.

## Working with the hooks

- **Only the hook *registration* is snapshotted at session start; the script is
  re-read on every call.** So a brand-new hook does not fire until the next
  session, but *edits to an already-registered one are live immediately*. (This
  corrects the Stage 0 note, which assumed the stricter case.)
- **The freeze matches prose, deliberately.** A Bash command that merely
  *mentions* a frozen filename near a mutating verb — a commit message, a
  comment, the hook's own `PROTECTED` list — is denied. Reword it, or use the
  Write/Edit tools, which judge the target path only. A false deny costs a
  reworded command; a false allow costs an edited acceptance test.
- **Don't undo a temporary probe with `git checkout --`.** It reverts to HEAD
  and takes the current item's uncommitted work with it. Copy the file aside
  first, and restore from the copy.
