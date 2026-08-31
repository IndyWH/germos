# Stage 2 spec — Senses

**spec.md for Stage 2 · Cowork, 31 August 2026 · status: draft, awaiting owner approval**

## What we are building

The machine learns to listen and to answer in writing. Stage 2 grows on Stage 1's body — same UEFI boot, same GOP framebuffer, same own GDT and paging, cores still woken — and adds three organs: a proper IDT so CPU exceptions become readable serial messages instead of silent reboots, a PS/2 keyboard driver fed by interrupts, and a text console drawn on the framebuffer. Done-when, from the foundation: the machine is interactive — you type, and the machine answers. The serial channel becomes permanent equipment.

## The work, in behavioural order

1. Everything Stage 1 proved, kept: serial first, GOP at highest mode, ExitBootServices, our GDT and paging, cores found and woken (the APs now just park — the bands retire, the console is the picture).
2. **The IDT.** Handlers for every CPU exception that print `ERR: exception <vector> at 0x<rip>` over serial and halt. From this stage on, a fault is a diagnosis, not a black screen. Log `S2: idt ready`.
3. **The console.** The framebuffer becomes a text screen: dark background, light glyphs, a fixed bitmap font from a font file in the repo, glyphs scaled 2x for legibility at 2048x2048. The boot log is mirrored to it, then a `> ` prompt. Cursor, line wrap, backspace, and scrolling when the bottom is reached. Log `S2: console <COLS>x<ROWS>`.
4. **The keyboard.** The legacy PIC remapped to vectors 0x20+, IRQ1 unmasked, the i8042 read on interrupt. Scancode set 1, US layout, unshifted printable characters plus Enter and Backspace; everything else ignored. Log `S2: keyboard ready`, then `sti`.
5. **The echo.** Every accepted printable character appears at the cursor and is sent verbatim over serial; Enter echoes CRLF and a new prompt. The interrupt handler only buffers the scancode; the main loop does the drawing — the screen keeps its single owner.

## The serial lines

Boot lines, exact, in order, CRLF: `S2: alive` · `S2: gop <W>x<H> fb 0x<16 hex>` · `S2: boot services exited` · `S2: gdt and paging ours` · `S2: idt ready` · `S2: cores found <N>` · `S2: cores woken <N>` · `S2: console <COLS>x<ROWS>` · `S2: keyboard ready`. After that, the channel carries the raw echo of what is typed, and nothing else. `ERR:` lines remain the failure voice.

## Build and run

As Stage 1, from stage2/: `mkimage.sh` packs `stage2/out/esp.img`; run with the same QEMU command pointing at it. No new packages.

## Acceptance tests

Written before the code, frozen behind the hook. Test 4's checker renders its expected text with the same font file the assembly includes — one font, used twice.

1. **Artefact.** PE32+ checks as Stage 1, on stage2's binary and image.
2. **Serial boot.** Headless run: the nine `S2:` lines, in order, found = woken = the `-smp` value, sane width, height, columns, rows.
3. **The type test.** Via the QEMU monitor, `sendkey` types `hello` then Enter. The serial capture after `S2: keyboard ready` is exactly `hello` and CRLF. Runs at `-smp 2` and `-smp 8`.
4. **Pixels.** After the typing, a screendump: the checker locates the prompt line and asserts the glyphs for `> hello` are pixel-correct per the font file, on the dark background.
5. **Oracle.** You run it windowed and type whatever you like. Seeing your own keystrokes land is the done-when. Your word closes the stage.

## Rules carried forward

QEMU only; nothing outside the repo; serial before video; only the BSP touches serial and screen; every new fault class earns a CLAUDE.md gotcha and a regression check.

## Judgement calls flagged for the owner

1. **Keyboard route.** Interrupt-driven via the remapped PIC (my recommendation — real interactivity, and the IDT pays for itself in debugging forever) versus polling the i8042 (simpler, no IDT yet). The IDT arrives this stage either way.
2. **The font.** Embed the public-domain 8x8 classic (font8x8), scaled 2x (my recommendation — zero licensing questions, retro-correct), versus hand-drawing our own.
3. **Shift and symbols.** Unshifted-only this stage (my recommendation — small rings) versus full shift handling now.
