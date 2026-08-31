# Stage 0 spec — First pixel

**spec.md for Stage 0 · Cowork, 31 August 2026 · status: APPROVED by Wajira, 31 August 2026**

## What we are building

One 512-byte boot sector, written in NASM, run in QEMU. It says hello over serial, switches to a graphics mode, and paints Spectrum loading stripes. It proves the toolchain, the twin, and the build loop work end to end. Everything below runs only inside QEMU. No real disk is in reach at any point.

## Boot environment

QEMU's BIOS (SeaBIOS) loads the sector to address 0x7C00 and jumps to it in 16-bit real mode. No UEFI, no partition table — Stage 0 takes the romantic BIOS path, as the foundation document says.

## Layout of the 512 bytes

Only the last two bytes are fixed by the PC standard. The section sizes are budgets to guide the plan, not law. Total budget is comfortable: roughly 200 of 510 bytes used.

| Order | Size (approx) | Content |
|---|---|---|
| 1 | 12 B | Entry: interrupts off, DS/ES/SS zeroed, stack at 0x7C00, interrupts on |
| 2 | 30 B | Serial init, COM1 at port 0x3F8: interrupts off (IER=0), DLAB on, divisor 1 (115200, 8N1), FIFO on |
| 3 | 20 B | `serial_print` routine: poll LSR bit 5 until the transmit holding register is empty, write one byte, repeat until NUL |
| 4 | — | Log line 1 over serial — the first observable act, before any video, per the foundation's serial-log-from-byte-one rule |
| 5 | 8 B | BIOS int 10h, AX=0x0013: VGA mode 13h — 320x200, 256 colours, framebuffer at segment 0xA000 |
| 6 | 45 B | Stripe fill (rule below) |
| 7 | — | Log line 2 over serial |
| 8 | 5 B | Halt loop: cli, hlt, jump back |
| 9 | ~80 B | The two message strings, NUL-terminated, then zero padding |
| 10 | 2 B | Bytes 510–511: the boot signature, 0x55 0xAA |

## The stripes

Homage to the Spectrum loading border: pilot tone on top, data below. For each of the 200 rows, fill all 320 pixels with one VGA palette colour:

- Rows 0–99: red (colour 4) and cyan (colour 3), swapping every 4 rows — the slow pilot bands.
- Rows 100–199: blue (colour 1) and yellow (colour 14), swapping every 2 rows — the fast data bands.

## The serial lines

Exact bytes, each line ending CRLF:

```
S0: alive
S0: stripes drawn, hello from the boot sector
```

## Build and run

```
nasm -f bin stage0.asm -o stage0.img
qemu-system-x86_64 -drive format=raw,file=stage0.img -serial stdio
```

## Acceptance tests

Written now, before any code exists. They live in `test.sh`; all must pass before every commit, and CC is blocked from editing them during a fix.

1. **Artefact.** `stage0.img` is exactly 512 bytes and its last two bytes are 0x55 0xAA.
2. **Serial.** A headless run (`-display none -serial stdio`, 10-second timeout) captures both serial lines, byte-exact and in order.
3. **Pixels.** A scripted run takes a QEMU `screendump` a few seconds after boot. The script confirms all four stripe colours are present (RGB within tolerance), with red/cyan only in the top half and blue/yellow only in the bottom half.
4. **Oracle.** Wajira runs the windowed command and confirms it looks like a Spectrum loading. His word is the gate for the stage.

## Decisions recorded at approval (owner, 31 August 2026)

1. **Environment.** Native Ubuntu 26.04 on mlrig — WSL2 is retired and removed from the project documents. Repo lives at /home/indy/Projects/ai-os.
2. **Repo name.** Neutral placeholder `ai-os` until the owner names the project.
3. **Stripe pattern.** The two-band pilot-and-data pattern as specced, not the plainer single pattern.
