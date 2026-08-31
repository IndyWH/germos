# Stage 2 — implementation plan

**To be committed as `stage2/plan.md`. Produced in plan mode, per the foundation's
build loop. Nothing below is implemented until Wajira approves this document.**

## Context

Stage 1 is closed: Wajira confirmed test 5 and the `-smp 32` mirror run on
31 August 2026. Stage 2 makes the machine interactive — *senses*: an IDT so CPU
exceptions become readable serial messages instead of silent reboots, a text
console on the GOP framebuffer, and an interrupt-driven PS/2 keyboard. The bands
retire; the console is the picture. You type, and the machine answers.

`stage2/spec.md` is approved and fixes the behavioural order, the nine serial
lines, and five acceptance tests, plus the owner's three decisions:
interrupt-driven keyboard via the remapped PIC, font8x8 scaled 2x,
unshifted-only. This plan turns that spec into numbered items.

The plan is **evaluation-first**: items 1–5 commit the font and build the
acceptance machinery so tests 1–4 exist and fail before a single instruction of
`stage2.asm` is written. Item 6 locks them behind the hook. Items 7–10 grow the
implementation on Stage 1's proven body, and the gate closes at item 10. Test 5
is Wajira's eyeball and stays manual, forever.

### Environment, verified in this session before planning

No new packages are needed; the toolchain is Stage 1's.

| Fact | Verified how |
|---|---|
| `font8x8_basic.h` is reachable from the dhepper/font8x8 repo, 9596 bytes, sha256 `49d8df366296b203ca3211bc0672cf2a762135bf12710735b6292756b19dffd5` | fetched it (HTTP 200) |
| The glyph layout is **one byte per row, top to bottom, bit 0 = leftmost pixel** | converted all 128 glyphs and rendered 'A', '>', 'h' as ASCII art — all correct |
| The converted 1024-byte binary hashes to sha256 `66bba26c3b351634ed4dd3ad7561f6cc892e1727d4887204bd4d1d3883a18b37` | conversion run in the session scratchpad |
| **QEMU monitor `sendkey` keystrokes reach the guest's keyboard** | with no drive attached, `sendkey down` / `sendkey ret` navigated OVMF's own boot menu and setup UI over serial — the whole external-typing path works before any Stage 2 code exists |
| Monitor-over-stdio driving, screendumps, and serial-to-file all work together | Stage 1's `checkbands.py` does exactly this and is green |

One observation from the probe, recorded for the checker's design: OVMF's serial
UI output interleaves ANSI escapes mid-phrase, so the checker must key on *our*
lines (written contiguously by our code), exactly as Stage 1's extraction
already does.

---

## Decisions taken in this plan

Judgement calls inside the approved spec. Flagged here so Wajira can overrule
any of them at approval rather than discover them in the diff.

1. **The nine serial lines, exactly** (the spec gives placeholders). Each CRLF:
   `S2: alive` · `S2: gop <W>x<H> fb 0x<16 lowercase hex>` · `S2: boot services
   exited` · `S2: gdt and paging ours` · `S2: idt ready` · `S2: cores found <N>`
   · `S2: cores woken <N>` · `S2: console <COLS>x<ROWS>` · `S2: keyboard ready`.
   Decimal, no padding. There is **no** `S2: done`: after line nine the channel
   carries only the raw echo, per the spec. `ERR:` remains the failure voice.
2. **Console geometry.** Cells are 16x16 pixels (the 8x8 font scaled 2x);
   `COLS = W/16`, `ROWS = H/16`, integer division, glyphs drawn from the
   top-left. Test 2 asserts `COLS` and `ROWS` equal exactly that arithmetic on
   the same log's `W`x`H` (128x128 on this machine's 2048x2048 mode — measured,
   never baked in).
3. **Colours, pixel-exact** (they are baked into the frozen checker):
   background RGB(16,16,24) — dark, faintly blue; foreground RGB(224,224,224).
   Comparison tolerance ±4 per channel, as Stage 1.
4. **The font file is a raw binary, and it is frozen.** `stage2/font8x8.bin`:
   1024 bytes, glyphs 0x00–0x7F, 8 bytes per glyph, one byte per row top to
   bottom, bit 0 = leftmost pixel — converted mechanically from the
   public-domain `font8x8_basic.h` (dhepper/font8x8). Provenance — source URL,
   both sha256 hashes, the licence note, the conversion recipe, and a rendered
   glyph as evidence — goes in `stage2/FONT.md`. The `.bin` joins the freeze at
   item 6: the pixel test renders its expected text from this file, so an
   editable font is an editable criterion (an all-blank font would pass a blank
   screen). Belt and braces, the checker also asserts the glyphs it uses are
   non-blank and mutually distinct.
5. **Cursor: a static solid block** — the whole cell filled with the foreground
   colour. No blinking (nothing else on this machine moves without cause). The
   checker asserts it: after typing `hello` + Enter the screen's final text row
   is `> ` with the cursor block in column 2, one row below the `> hello` line.
6. **Echo bytes.** A printable echoes as itself; Enter echoes CR LF; Backspace
   echoes BS (0x08). On the console, Backspace erases only within the current
   line's typed text — never the prompt. Break codes (bit 7) are ignored; a
   0xE0 prefix swallows the byte after it (otherwise `E0 53`, keypad Delete,
   would print a `.`). Everything not in the map is ignored, silently.
7. **The screen keeps one owner.** The IRQ1 handler does nothing but read port
   0x60 and store the scancode into a 256-byte ring buffer (single producer —
   the interrupt, single consumer — the main loop; head and tail each written
   by one side only, so no lock). All translation, serial echo, and drawing
   happen in the BSP's main loop: `sti`, then `hlt`; each wake drains the ring.
   `sti` happens only after `S2: keyboard ready` is on the wire.
8. **PIC discipline.** Master remapped to 0x20–0x27, slave to 0x28–0x2F (both
   remapped even though only the master is used — a spurious slave vector must
   not land on an exception). Every line masked except IRQ1. EOI to the master
   only. Vector 0x27 (spurious IRQ7) gets a handler that `iretq`s without EOI.
   The timer stays masked; nothing in this stage wants it.
9. **The IDT: 256 gates, exceptions 0–31 through per-vector stubs.** Each stub
   pushes its vector number (and a dummy error code for the vectors the CPU
   does not push one, so the frame is uniform), then a common handler prints
   `ERR: exception <vector> at 0x<rip>` — vector decimal, RIP as 16 hex digits
   — and halts. Loaded on the BSP straight after paging (so the MADT walk and
   the wake are already covered), and by each AP before it parks: a fault on a
   parked core then becomes a message rather than a machine-wide triple-fault
   reboot. That dying core writes serial in violation of one-owner — accepted
   deliberately as the failure voice of a machine that is already lost, and
   flagged here so it is a decision, not an accident.
10. **Boot-log mirroring is a byte tee.** Every byte written to serial also goes
    through a mirror layer: before the console exists it lands in an 8 KB RAM
    log buffer; console init clears the screen, replays the buffer, and from
    then on the tee writes the console live. The mirrored log is byte-for-byte
    what serial saw. The `> ` prompt and cursor are console-only — the serial
    contract after line nine is the raw echo and nothing else.
11. **The i8042 is not reconfigured this stage.** QEMU's controller default —
    translation on, set-1 make codes — is what the spec's "scancode set 1"
    means here. We drain the output buffer (status bit 0) before unmasking
    IRQ1, and touch nothing else. Recorded honestly: controller init from cold
    is a Stage 7 problem, on real metal, where it belongs.
12. **The map: set 1, US, unshifted.** The 47 printable character keys plus
    space — letters, digits, `` ` - = [ ] ; ' \ , . / `` — plus Enter (0x1C)
    and Backspace (0x0E). Tab, Esc, modifiers, function keys, keypad: ignored.
    Keypad Enter arrives as `E0 1C` and is swallowed by decision 6.
13. **Scrolling never reads the framebuffer.** The console keeps a text shadow
    buffer (ROWS×COLS bytes); scroll shifts the shadow and re-renders the
    screen from it. The framebuffer is mapped uncached, and reads from UC
    memory are brutally slow — the framebuffer is write-only, always.
14. **One driver, two assertions.** `stage2/checktext.py` owns the whole
    interactive run, exactly as `checkbands.py` owns Stage 1's: boot headless
    with `-monitor stdio` and `-serial file:`, wait for `S2: keyboard ready` in
    the serial file, then `sendkey` one key at a time — h, e, l, l, o, ret —
    with generous (≥150 ms) gaps, settle, screendump, quit, reap. Mode
    `--type <smp>` asserts the serial capture after the `S2: keyboard ready`
    CRLF is **exactly** `hello` CR LF (the same run's boot lines are also
    checked, so a reboot loop cannot slip through); mode `--pixels` (at
    `-smp 8`) additionally takes the screendump and asserts the picture. Test 3
    runs `--type 2` and `--type 8`; test 4 runs `--pixels`.

---

## Conventions for every item

- One commit per numbered item.
- Each item states **which tests are expected green at its commit**. Items 1–6
  commit with every Stage 2 test failing **by design** — there is no
  `stage2.asm` yet. That failure is the evidence the gate is real.
- From item 7 on, the stated tests must be green before the commit is made.
- **`./stage0/test.sh` and `./stage1/test.sh` stay green throughout** — run as
  regressions before every commit.
- `HANDOVER.md` is updated as we go, with a final pass at item 11.
- `/clear` between numbered items if context grows long.
- Every new fault class earns a CLAUDE.md gotcha line and a regression check.
- Temporary probes are never committed, and never undone with `git checkout --`
  (the CLAUDE.md gotcha): copy aside, restore from the copy.

---

# Part 1 — the acceptance machinery, written before the code

## Item 1 — the font, with its provenance

`stage2/font8x8.bin` — fetched from dhepper/font8x8, converted exactly as the
session probe did, and verified against the hashes recorded above before
committing. `stage2/FONT.md` records: the source URL and upstream sha256, the
`.bin` sha256, the public-domain licence note, the byte/bit layout (8 bytes per
glyph, row per byte, LSB leftmost), the conversion recipe as a runnable Python
one-liner, and one rendered glyph as ASCII art. One font, used twice: the
assembly `incbin`s this file, and the checker renders its expected text from it.

*Expected at commit:* no Stage 2 tests exist yet. Stage 0 and Stage 1 green.

## Item 2 — `stage2/mkimage.sh`, `stage2/test.sh` harness, acceptance test 1

**`stage2/mkimage.sh`** (not frozen — the recipe, not a criterion): Stage 1's
builder retargeted: `nasm -f bin stage2/stage2.asm -o stage2/out/BOOTX64.EFI`,
then the same mtools packing into `stage2/out/esp.img` at
`EFI/BOOT/BOOTX64.EFI`. A missing `stage2.asm` is a reported build failure —
a test failure, not a crash. Everything lands in `stage2/out/` (gitignored).

**`stage2/test.sh`** (frozen from item 6): Stage 1's harness shape — `set -u`,
repo-root resolution, numbered PASS/FAIL, summary, exit 0 only if all pass.

**Test 1 — Artefact.** Identical criteria to Stage 1, on Stage 2's files:
MZ/PE magics, machine 0x8664, RELOCS_STRIPPED + EXECUTABLE, PE32+ magic 0x20B,
subsystem 10, and `esp.img` containing a byte-identical `BOOTX64.EFI` at the
removable-media path.

*Expected at commit:* every Stage 2 test fails — there is no `stage2.asm`.
`./stage2/test.sh` non-zero exit quoted in the commit message.

## Item 3 — acceptance test 2 (serial: the nine lines, in order)

A headless run at `-smp 8` under `timeout -k 5 60`; exit 124 expected (the
guest waits for keystrokes forever). Stage 1's scan-extraction of `S2: ` runs,
then **exactly nine** messages matching, in order:

```
S2: alive
S2: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})
S2: boot services exited
S2: gdt and paging ours
S2: idt ready
S2: cores found (\d+)
S2: cores woken (\d+)
S2: console (\d+)x(\d+)
S2: keyboard ready
```

plus: `W, H > 0`, `fb != 0`, found = woken = 8, `COLS == W/16` and
`ROWS == H/16` (integer division — decision 2), `COLS >= 40`, `ROWS >= 12`
(room for the boot log and the typing without wrap). Exactly nine catches a
triple-fault reboot loop, which from this stage on should instead appear as an
`ERR: exception` line — either way, a failed test with a readable cause.
Implemented as `serial_check <smp>` for reuse. Whole capture printed on failure.

*Expected at commit:* tests 1–2 fail.

## Item 4 — `stage2/checktext.py`: the driver and the type test (test 3)

The driver of decision 14, and mode `--type <smp>`: boot, wait for
`S2: keyboard ready` (60 s ceiling), send h e l l o ret one at a time with
≥150 ms gaps, settle ~1 s, quit, reap — killing on timeout so no QEMU is left
behind. Assert the nine boot lines (reusing the same expectations as test 2, on
this run's capture) and that the bytes after `S2: keyboard ready` + CRLF are
exactly `hello\r\n`. On failure, print the capture with control bytes visible.

`test.sh` gains **Test 3**: `--type 2` and `--type 8`, both must pass — the
echo must follow the machine, not the core count.

*Expected at commit:* tests 1–3 fail.

## Item 5 — checktext.py `--pixels` mode (test 4)

The same driver at `-smp 8`, plus screendump after the typing settles. The
checker then:

1. Parses `W`, `H`, `COLS`, `ROWS` from this run's own serial lines; asserts
   the PPM is exactly `W`x`H` (Stage 0's line-doubling diagnosis kept in the
   failure message).
2. Renders `> hello` from `stage2/font8x8.bin` itself — 16x16 cells, each font
   bit a 2x2 block, foreground/background per decision 3 — after asserting
   those glyphs are non-blank and mutually distinct (decision 4).
3. Scans the cell grid for that rendered strip: it must appear **exactly once**,
   pixel-correct within ±4 per channel.
4. Asserts the final prompt: one row below the `> hello` row, columns 0–2 are
   `>`, space, cursor block (decision 5).
5. Asserts colour discipline: every pixel on screen is within ±4 of either the
   background or the foreground — nothing else is allowed on this picture, so
   leftover bands, garbage, or a firmware splash all fail.
6. On failure, prints a per-cell census of the offending rows so a wrong glyph,
   wrong scale, wrong colour, or wrong stride is diagnosed from the output
   alone.

`test.sh` gains **Test 4**. All four tests now exist and all fail;
`./stage2/test.sh` output goes in the commit message as evidence the gate is
real before the code exists.

*Expected at commit:* tests 1–4 fail.

## Item 6 — extend the hook to freeze the Stage 2 acceptance machinery

`PROTECTED` in `.claude/hooks/protect-tests.py` grows three lines:
`stage2/test.sh`, `stage2/checktext.py`, `stage2/font8x8.bin` (decision 4).
`stage2/mkimage.sh` and `stage2/FONT.md` stay unfrozen — recipe and paperwork.

**Payload verification, as Stage 1:** a table of JSON payloads fed straight
into the hook — denied: Write/Edit to each new path, `sed -i`, `tee`, `>`,
`mv`, `cp`, `rm`, `chmod`, `git checkout`, a writing Python heredoc; allowed:
`cat`, running the tests, `python3 stage2/checktext.py --type 8`, redirecting
test *output*, every operation on `stage2/mkimage.sh` and `stage2/FONT.md`.
All Stage 0 and Stage 1 cases re-run alongside, proving the freeze loosened
nothing. Per amendment A4 (confirmed last session, now in CLAUDE.md), the
edited script **bites immediately** — verified as part of this item, not
assumed.

*Expected at commit:* tests 1–4 still fail; the hook demonstrably denies and
allows the right payloads.

---

*Everything above is written before any implementation code exists. Everything
below is the code.*

---

# Part 2 — the implementation, in the spec's order

## Item 7 — `stage2/stage2.asm`: Stage 1's proven body, bands retired

Start from `stage1/stage1.asm` — the whole working organism: PE32+ headers,
serial-first entry, GOP highest 32-bit mode, static-buffer memory map,
trampoline claim with fallback, ExitBootServices with the stale-key retry, own
GDT + 4 GB identity map with the uncached framebuffer, MADT walk, both APIC
paths, PIT delays, INIT-SIPI-SIPI, bounded check-in wait. Changes:

- every `S1:` becomes `S2:`; `S1: done` is deleted (decision 1);
- `paint_band`, the colour table, and both call sites go — **the APs now take
  their index, check in, and park** (`cli`/`hlt`); the BSP just waits for
  check-ins;
- the serial layer grows the mirror tee of decision 10 (buffer-only for now —
  there is no console yet to replay into).

Six of the nine lines: alive, gop, exited, gdt/paging, found, woken.

*Green at commit:* **test 1.** Tests 2–4 fail (six lines, no console, no
keyboard). Stage 0 and Stage 1 green — proving the copy broke nothing behind it.

## Item 8 — the IDT

Decision 9 in full: the 256-gate table in BSS, 32 exception stubs (error-code
vectors left as pushed, the rest push a dummy, all push their vector), the
common printer for `ERR: exception <vector> at 0x<rip>`, halt. `lidt` on the
BSP immediately after `mov cr3` — `S2: idt ready` is line five, before the MADT
walk, so the wake sequence runs covered. The AP entry gains its own `lidt`
before parking.

Verified with a temporary, uncommitted `ud2` probe: the log must show
`ERR: exception 6 at 0x<plausible rip>` and a clean halt — then the probe is
removed (copy-aside, never `git checkout --`).

*Green at commit:* test 1. Seven of nine lines; tests 2–4 still red.

## Item 9 — the console

The framebuffer becomes a text screen (decision 2, 3, 13):

- `incbin "stage2/font8x8.bin"` in `.data`; COLS/ROWS computed from the GOP
  mode at runtime, never assumed;
- clear to background; `console_putc`: glyph row bytes expanded 2x2 into the
  cell, cursor advance, wrap at COLS, LF = new line, BS = erase within the
  typed region; scroll by shifting the text shadow buffer and re-rendering —
  the framebuffer is never read;
- console init replays the mirror buffer (decision 10) — the boot log appears,
  byte-for-byte what serial carried; the tee goes live to the screen;
- `S2: console <COLS>x<ROWS>` — line eight — then the `> ` prompt and the
  cursor block, console-only.

*Green at commit:* test 1. Eight of nine lines; the screen now shows the boot
log and a prompt, but tests 2–4 stay red — nothing can type yet.

## Item 10 — the keyboard, and the gate closes

Decisions 6, 7, 8, 11, 12:

- PIC remap to 0x20/0x28, all masked but IRQ1; IDT gate 0x21 → the buffering
  handler (read 0x60, store to the ring, EOI master); gate 0x27 → the spurious
  handler;
- drain the i8042 output buffer; `S2: keyboard ready` — line nine — then the
  prompt, then `sti`;
- the main loop: `hlt`, drain the ring, translate (set 1, unshifted, E0-swallow,
  break-ignore), echo — serial byte per decision 6, console glyph via
  `console_putc`, Enter = CRLF + new prompt, Backspace bounded at the prompt.

*Green at commit:* **all four automated tests** — tests 2, 3, 4 close here, at
`-smp 2` and `-smp 8`. Full `./stage2/test.sh` output goes in the commit
message. Stage 0 and Stage 1 still green.

## Item 11 — HANDOVER, gotchas, and the owner's command

- `HANDOVER.md` to final Stage 2 state: what was built, the console geometry
  measured on this machine, tests 1–4 green with output, test 5 pending
  Wajira, caveats carried forward (x2APIC and trampoline-fallback paths still
  unproven; the i8042 not reconfigured — a Stage 7 debt; shift handling a
  later ring).
- `CLAUDE.md` gotchas grown with whatever actually bit — candidates already
  visible: *never read the uncached framebuffer back — scroll from a shadow
  buffer*; *remap the PIC before `sti` or IRQ0 lands on the double-fault
  vector*; *a 0xE0 scancode prefix must swallow its successor*; *`sendkey`
  needs real gaps — a monitor can outrun a guest*.
- Print the windowed command for Wajira's test 5.

*Green at commit:* all four automated tests, plus Stage 0 and Stage 1.

---

## Verification

- **Automated:** `./stage2/test.sh` from the repo root — builds, packs, runs
  tests 1–4 (serial at `-smp 8`; typing at `-smp 2` and `-smp 8`; pixels at
  `-smp 8`). Exit 0 only if all pass. Run before every commit from item 7 on.
- **Regression:** `./stage0/test.sh` and `./stage1/test.sh` green before every
  commit, throughout.
- **The hook:** the item 6 payload table, with all Stage 0 and Stage 1 cases
  re-run; immediacy of the freeze verified per A4.
- **Manual (test 5):** Wajira runs, from the repo root:

```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage2/out/esp.img -serial stdio
```

types whatever he likes, and watches his own keystrokes land. His word closes
the stage.

## Safety

Unchanged from Stage 1, and restated because it is load-bearing: everything
runs inside QEMU; firmware plus exactly one drive, a raw FAT image under
`stage2/out/`; OVMF mapped read-only by `-bios`; no block device, no loop
mount, no `sudo`; nothing written outside `/home/indy/Projects/ai-os` bar
scratch files in the session temp directory. The only network touch in the
whole stage is item 1's one-time fetch of a public-domain font file, verified
against the hash recorded in this plan.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| `sendkey` races the guest | keys sent only after the guest itself says `S2: keyboard ready`, one key at a time with ≥150 ms gaps, settle before asserting |
| IRQ1 never fires — silent deafness | the drain-then-unmask order; test 3 fails in seconds with the boot lines present and the echo absent, which localises it to the keyboard path |
| Exception stubs mis-read RIP on error-code vectors | uniform frames via dummy pushes; the `ud2` probe at item 8 checks a real RIP before anything depends on it |
| Console too slow on uncached memory | write-only framebuffer discipline; shadow-buffer scroll (decision 13) |
| Wrong font bits make the pixel test self-confirming | the font is converted once, hash-pinned in this plan, eyeballed at item 1, then frozen at item 6; the checker refuses blank or duplicate glyphs |
| A stray scancode (E0 pairs, break codes) prints garbage | decision 6's swallow rules; the oracle test types freely, which is what test 5 is for |
| The nine-line contract drifts between test 2, test 3, and the code | one `serial_check` implementation reused; the line list lives in this plan, verbatim |
