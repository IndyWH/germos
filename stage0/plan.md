# Stage 0 — implementation plan

**To be committed as `stage0/plan.md`. Produced in plan mode, per the foundation's build loop.**

## Context

Stage 0 of the AI OS project proves the toolchain, the twin (QEMU) and the build
loop work end to end, by growing one 512-byte boot sector from nothing. It says
hello over serial *before* it touches video, switches to VGA mode 13h, and paints
Spectrum loading stripes. Everything runs inside QEMU only; no real disk device
is in reach at any point.

`stage0/spec.md` is approved and fixes the layout, the stripe rule, the two exact
serial lines and four acceptance tests. This plan turns that spec into numbered
implementation items.

The plan is **evaluation-first**: items 1–3 build `stage0/test.sh` implementing
acceptance tests 1–3, so the tests exist and fail before a single byte of boot
sector code is written. Item 4 locks them behind a hook. Only then does items 5–7
write the assembly. Test 4 is Wajira's eyeball and stays manual, forever.

Toolchain confirmed present on mlrig: NASM 3.01, QEMU 10.2.1, Python 3.

## Conventions for every item

- One commit per numbered item.
- Each item below states **which tests are expected green at its commit.** Items
  1–4 commit with tests failing *by design* (there is no code yet) — that is the
  evaluation-first gate, and the failure is the evidence the tests are real.
- From item 5 on, the stated tests must be green before the commit is made.
- `HANDOVER.md` is updated as we go, with a final pass at item 8.

---

## Item 1 — `stage0/test.sh` harness + acceptance test 1 (artefact)

Create the single entry point for the gate.

- `stage0/test.sh`, bash, `set -u`, run from anywhere (resolves its own repo root).
- Builds first, exactly the spec's command, into a gitignored output directory:
  `nasm -f bin stage0/stage0.asm -o stage0/out/stage0.img`.
  A missing `stage0.asm` or a NASM error is a **test failure**, reported as such,
  not a crash.
- Test-runner scaffolding: numbered `PASS`/`FAIL` lines, a failure counter, a
  summary, exit 0 only if every test passed.
- **Test 1 — Artefact.** `stage0/out/stage0.img` is exactly 512 bytes
  (`stat -c%s`) and its last two bytes are `0x55 0xAA`
  (`xxd -p -s 510 -l 2` equals `55aa`).

*Expected at commit:* all tests fail — there is no `stage0.asm` yet. Verified by
running `./stage0/test.sh` and showing it exits non-zero.

## Item 2 — acceptance test 2 (serial, byte-exact)

- Headless run, exactly as the spec words it:
  `timeout -k 2 10 qemu-system-x86_64 -drive format=raw,file=stage0/out/stage0.img -display none -serial stdio </dev/null >stage0/out/serial.txt 2>stage0/out/qemu.err`
- The boot sector halts forever by design, so `timeout`'s exit code 124 is the
  **expected** outcome; any other non-zero exit is a QEMU failure and fails the
  test with `qemu.err` shown.
- **Byte-exact comparison.** Build the expected capture in the script as exactly:
  `S0: alive\r\nS0: stripes drawn, hello from the boot sector\r\n`
  and compare the *whole* capture against it with `cmp`. Not a grep, not a
  substring — equality of the full byte stream, which enforces both lines,
  their exact text, their CRLF endings, and their order, with nothing else.
- On failure, print a hexdump of what was actually captured. (This is the
  observations chart; when the screen is black the serial log is all we have.)

*Expected at commit:* tests 1 and 2 both fail — still no code.

## Item 3 — acceptance test 3 (pixels, screendump colour check)

Two files:

- `stage0/checkpixels.py` — pure Python 3, no third-party imports (PIL is present
  on mlrig but a dependency-free checker is one less thing to break):
  1. Launch QEMU with `-display none -monitor stdio` via `subprocess`, pipes on
     stdin/stdout. No graphical window, no serial needed for this run.
  2. Wait ~3 seconds for the guest to finish painting, write
     `screendump stage0/out/screen.ppm` to the monitor, wait for the file to
     appear and stop growing, then write `quit` and reap the process (kill on
     timeout so no QEMU is ever left running).
  3. Parse the PPM (`P6`, 320x200, maxval 255) by hand — header then raw RGB.
  4. Assert, per the spec: the four VGA palette colours are present within
     tolerance — red (170,0,0), cyan (0,170,170), blue (0,0,170),
     yellow (255,255,85), tolerance ±24 per channel; **red and cyan appear only
     in rows 0–99, blue and yellow only in rows 100–199**, and no pixel is
     anything else.
  5. On failure print a per-row colour census, so a wrong band width or a wrong
     colour index is diagnosed from the test output alone.
  6. Exit 0 on pass, 1 on any failure, with a clear message on every path.
- `stage0/test.sh` gains **Test 3**, which runs `checkpixels.py` and reports it.

*Expected at commit:* all three tests fail. `./stage0/test.sh` output pasted into
the commit message as the evidence that the gate is real before the code exists.

## Item 4 — the hook that freezes the acceptance tests

The foundation's rule: *guarantees we care about become hooks, not requests.*

- `.claude/hooks/protect-tests.sh` — a `PreToolUse` hook. Reads the tool call
  JSON on stdin and **denies** (exit 2, reason on stderr) any attempt to modify
  the frozen acceptance machinery:
  - `stage0/test.sh` and `stage0/checkpixels.py`
  - by any route: `Write`, `Edit`, `MultiEdit`, **and `Bash`** — the Bash arm
    matters most, since this session does its file edits through Bash, so the
    hook inspects the command string for the protected paths together with a
    mutating verb (`>`, `>>`, `sed -i`, `tee`, `mv`, `cp`, `rm`, `truncate`,
    `patch`, `git checkout/restore`).
  - Read-only use (`cat`, `bash stage0/test.sh`, `./stage0/test.sh`) stays allowed
    — the tests must still be *runnable*.
- `.claude/settings.json` registers it as a `PreToolUse` hook on
  `Write|Edit|MultiEdit|Bash`.
- Verified by attempting an edit of `stage0/test.sh` and showing the block, then
  showing `./stage0/test.sh` still runs.

From this commit on, the acceptance tests are out of the implementer's reach. If
a test turns out to be genuinely wrong, that is a **spec question for Wajira**,
not something to be quietly edited away. That is the entire point of the hook.

*Expected at commit:* the three tests still fail; the hook demonstrably blocks.

---

*Everything above is written before any implementation code exists. Everything
below is the code.*

---

## Item 5 — `stage0/stage0.asm`: entry, halt, signature

The skeleton, in spec layout order (spec rows 1, 8, 9, 10).

```
bits 16 / org 0x7C00
cli / xor ax,ax / mov ds,ax / mov es,ax / mov ss,ax / mov sp,0x7C00 / cld / sti
hang: cli / hlt / jmp hang
times 510-($-$$) db 0
dw 0xAA55
```

Notes: at entry only `CS:IP` is trustworthy, so `DS`/`ES`/`SS` are zeroed
explicitly with interrupts off. `cld` is set once here — `lodsb` and `stosb`
later both depend on the direction flag, and the BIOS is not required to leave it
clear. `times 510-($-$$)` fails the build loudly if the code ever overruns.

*Green at commit:* **test 1**. Tests 2 and 3 fail (no serial, black screen) —
stated in the commit message.

## Item 6 — serial init, `serial_print`, and log line 1

Spec rows 2, 3, 4 — the serial channel and the first observable act, **before any
video**, per the foundation's serial-log-from-byte-one rule.

- COM1 at 0x3F8: `IER(0x3F9)=0x00`, `LCR(0x3FB)=0x80` (DLAB), divisor
  `DLL=0x01, DLM=0x00` (115200), `LCR=0x03` (8N1, DLAB off), `FCR(0x3FA)=0xC7`
  (FIFO on, cleared), `MCR(0x3FC)=0x03` (DTR/RTS — the conventional init).
- `serial_print`: `SI` → NUL-terminated string. `lodsb`; on NUL return; else poll
  `LSR(0x3FD)` bit 5 (transmit holding register empty) until set, then `out` the
  byte to 0x3F8; loop. Preserves `AX` across the poll.
- `msg1: db "S0: alive", 13, 10, 0` — printed immediately after serial init.

*Green at commit:* **test 1**. Test 2 now captures the first line only and
therefore still fails the byte-exact comparison — correct, and the commit message
records the captured bytes. Test 3 fails.

## Item 7 — mode 13h, the stripes, and log line 2

Spec rows 5, 6, 7 — completes the boot sector.

- `mov ax,0x0013 / int 0x10` — VGA 320x200x256, framebuffer at segment 0xA000.
  Set the mode *before* writing pixels; the mode switch clears the framebuffer.
- Stripe fill, exactly the spec's rule. `ES=0xA000`, `DI=0`, `BX` = row 0..199;
  per row select the colour, `mov cx,320 / rep stosb`:
  - rows 0–99: `bx>>2` — even → red (4), odd → cyan (3). Red first, swapping
    every 4 rows: the slow pilot bands.
  - rows 100–199: `bx>>1` — even → blue (1), odd → yellow (14). Blue first,
    swapping every 2 rows: the fast data bands.
  - 200 × 320 = 64000 bytes, so `DI` never wraps the 64 KB segment. Mode 13h
    just fits, which is why this is the mode the spec chose.
- `msg2: db "S0: stripes drawn, hello from the boot sector", 13, 10, 0`, printed
  after the fill, then fall into the halt loop from item 5.
- Size check: roughly 170 of the 510 available bytes, inside the spec's ~200 budget.

*Green at commit:* **all of test 1, 2 and 3.** This is the commit that closes the
automated gate. `./stage0/test.sh` output goes in the commit message.

## Item 8 — HANDOVER.md, and hand the oracle his command

- `HANDOVER.md` updated to final Stage 0 state: what was built, the byte size
  actually used, tests 1–3 green with their output, test 4 pending Wajira, and
  the first entries earned for the CLAUDE.md gotchas section (anything that bit
  us during items 5–7 — every black-screen bug earns a line).
- Print the exact windowed command for **test 4**, run from the repo root:

  ```
  qemu-system-x86_64 -drive format=raw,file=stage0/out/stage0.img -serial stdio
  ```

*Green at commit:* all of tests 1–3. Test 4 is Wajira's, and his word is the gate
for the stage.

---

## Verification

- **Automated:** `./stage0/test.sh` from the repo root — builds the image and runs
  acceptance tests 1–3, exit 0 only if all three pass. Run before every commit
  from item 5 onward.
- **The hook:** attempt to edit `stage0/test.sh` and confirm the denial; confirm
  the tests still run.
- **Manual (test 4):** the windowed QEMU command above. Wajira confirms it looks
  like a Spectrum loading. That is the stage gate.

## Safety

Nothing is written outside `/home/indy/Projects/ai-os`. QEMU is given exactly one
drive, a 512-byte raw file inside this folder. No block device, no loop mount, no
`dd` to anything but a file in `stage0/out/`. The foundation's Stage 3 rule is
already in force here.
