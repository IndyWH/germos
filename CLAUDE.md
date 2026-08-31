# CLAUDE.md

Kept under one page. Source of truth is `ai-os-foundation.md`; current state is
`HANDOVER.md`.

## Build and test

```bash
nasm -f bin stage0/stage0.asm -o stage0/out/stage0.img   # build
./stage0/test.sh                                          # acceptance tests 1-3
qemu-system-x86_64 -drive format=raw,file=stage0/out/stage0.img -serial stdio   # test 4, windowed
```

`test.sh` is the gate. It must be green before every commit that should pass it.

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
  during implementation or a fix; the hook blocks it.
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
- **Mode 13h clears the framebuffer.** Set the mode *before* writing pixels, or
  the stripes are wiped by the mode switch.
- **A0000h is a segment, not an address.** In real mode write pixels via
  `ES = 0xA000` and a 16-bit offset; the offset wraps at 64 KB (320x200 = 64000
  bytes, so mode 13h just fits in one segment).
