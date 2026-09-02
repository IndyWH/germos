# GLASS.md — the glass: the screen's one owner, the obs page, and ABI 2

**Stage 6 ring 6a, plan item 1. Frozen behind the hook from item 8.** The
assembler and the three fixtures implement this document; the broker, the
twin and the acceptance checker parse by it. One text, six readers. If it
is wrong, that is a spec question for the owner, not an edit.

`stage4/UMBILICAL.md` and `stage5/GERMLINE.md` are frozen and untouched.
Everything they define stands as written: the cage, the addressing, the
frame (a `u32` little-endian length, then that many bytes), the connection,
the timers, the no-answer rule, the working indicator, the mock's canned
answers to questions, the record; the forgiving marker parse (`?` asks,
`!` requests, with or without a space), **the grow request** (a request
frame whose first byte is `0x01`, then the body), the refusal frame (kind
`0x00`), the 600 s grow deadline, the germline's directory shape and
normalisation, the record's grow fields. A **question** and a **note** ride
exactly as before. This document adds **the screen** (the mode policy, the
four regions, surfaces and the glass core), **the obs page** and **the obs
strip**, **the choices row**, **ABI 2** (an app is four callbacks with four
services), **the kind `0x02` frame** that carries one, **the rehearsal's
nine criteria**, and what changes in the germline key and the mock's table.
Everything a reader needs to check it with `xxd`, `struct` and the QEMU
monitor's `xp` is here.

## The screen

**The mode.** The display's preferred mode if it states one, else the
highest (spec decision 8). Before the GOP mode loop, boot services still
up, the guest scans PCI bus 0 (every function of every device) for a
device of class code `0x0300` — display controller, VGA-compatible — and
reads its **BAR2** (configuration register `0x18`): a memory BAR, masked
to its base. The first **128 bytes** of that region, read **one byte at a
time**, are the display's EDID. The guest requires the header `00 ff ff ff
ff ff ff 00`, then reads the **first detailed timing descriptor** at bytes
54–71: bytes 54–55 (the pixel clock) must be non-zero; the preferred
width is `byte 56 | (byte 58 >> 4) << 8`; the preferred height is `byte
59 | (byte 61 >> 4) << 8`. Any step failing — no such device, an I/O BAR,
no header, a zero clock — means the display states no preference. The
mode loop is Stage 1's (every mode with a 32-bit linear framebuffer
measured, the largest area remembered, the wider on a tie) and also
remembers the first mode whose width and height equal the EDID's; after
the loop that mode wins if one was found, otherwise the highest. The
framebuffer base, stride and size are read back from the protocol after
`SetMode`, as ever. Nothing is baked in: on the twin with `-vga none
-device VGA,edid=on,xres=1440,yres=1440` the EDID names 1440x1440, OVMF
lists it first, and the console is 90x90 cells; with `edid=off` the same
binary reports `edid none` and takes 2048x2048. (QEMU's default VGA
carries an EDID of its own naming 1280x800: every QEMU command in this
ring — the gate's, the twin's, the oracle's — carries the flags above.)

**The regions.** With `C` = width / 16 and `R` = height / 16 cells (the
console's 16x16-pixel grid from the shared font), four regions, in cells,
as (first row, first column, rows, columns):

| Region | Where | On this machine (90x90) |
|---|---|---|
| the **obs strip** | (0, 0, 2, C) | rows 0–1 |
| the **choices row** | (R−2, 0, 2, C) | rows 88–89 |
| the **conversation panel** | (2, 0, R−4, ⌊C/2⌋) | rows 2–87, columns 0–44 |
| the **app panel** | (2, ⌊C/2⌋, R−4, C−⌊C/2⌋) | rows 2–87, columns 45–89 |

A mode with fewer than 8 rows or 8 columns is `ERR: mode too small for the
glass`. The conversation panel is Stage 5's console in every behaviour —
the boot log replayed into it, wrap at its right edge, scroll within its
rows, the prompt `> `, the block cursor, notes, questions, requests and
their lines — only narrower and lower. With no app running the app panel
is background.

**The sixteen serial lines**, in order, `S6: keyboard ready` last so the
echo contract after it stays exactly Stage 2's:

```
S6: alive
S6: edid <W>x<H>                      | S6: edid none
S6: gop <W>x<H> fb 0x<16 hex digits>
S6: boot services exited
S6: gdt and paging ours
S6: idt ready
S6: cores found <N>
S6: cores woken <N>
S6: console <C>x<R>
S6: disk <N> sectors
S6: notebook formatted                | S6: notebook <N> notes
S6: nic <mac>
S6: component region 0x<16 hex digits> 1048576 bytes
S6: obs page 0x<16 hex digits>
S6: glass core <id>
S6: keyboard ready
```

Line 2 states the EDID's preferred mode, or `none`; when it is stated, line
3's mode equals it. Line 13's address is where an ABI 2 blob's first byte
will live: non-zero, below `0x100000000`, ≡ 128 mod 4096 (see "The wire").
Line 14 is the obs page: page-aligned, non-zero, below `0x100000000`. Line
15 is the glass core's local APIC id, decimal.

At `-smp 1` no core is free to own the screen: after line 14 the guest
prints `ERR: the glass needs a second core - boot with -smp 2 or more`,
renders the conversation surface to the framebuffer once so the line is
on screen too, and halts. The mode-too-small error takes the same path.
On those two paths, and only there, the boot processor paints.

## Surfaces and the glass core

**One owner.** After the glass core starts (line 15) the boot processor
never writes a pixel. Every region is a **surface**: a buffer of one byte
per cell, `rows × cols`, row-major, and a **dirty byte per row**. A cell
byte is `0x20`–`0x7E`, a glyph from the shared font in the two console
colours; **`0x01`, a solid foreground block**; anything else, background.
Two colours only, as every pixel test before this one assumes.

**The protocol**, without a lock: the producer stores the cells, then
stores the row's dirty byte as 1. The consumer — the glass core — for
each row, if the dirty byte is set, exchanges it to 0 (`xchg`), **then**
renders the row. x86 stores are seen in program order and there is no
compiler to reorder them, so a cell stored before the flag is visible to a
render that saw the flag; a cell stored after the exchange sets the flag
again and is rendered next frame. A torn row lasts one frame. The
conversation surface also has a **cursor**: one `u64`, `on << 31 | row <<
16 | col` (row and column relative to the surface), stored atomically;
when the glass core renders that row it paints a block over that cell.
The producer marks the old and the new cursor rows dirty when it moves.

**The glass core** is the first application processor to check in after
the boot processor (index 1 of Stage 1's wake). It records its APIC id in
the obs page, signals ready, waits to be started, and then loops for ever
with interrupts off:

1. `t0 = rdtsc`, stored in the obs page as `now`.
2. For each surface — strip, choices, conversation, app — for each dirty
   row: exchange the flag to 0, render the row's cells to the uncached
   framebuffer at the region's place, the cursor overlaid on its cell.
3. Format the obs strip from the obs page into the strip surface, render
   the two rows (they are always dirty).
4. `frames += 1`; `frame_last = rdtsc − t0`; `frame_worst = max`. If
   `echo_pending` was 1 when step 2 began: `photon_last = rdtsc −
   echo_stamp`, `photon_worst = max`, `echo_pending = 0`.
5. `pause` until `t0 + tsc_per_ms × 1000 / 60`: **60 frames a second**.
   No timer interrupt: the glass core has nothing else to do.

Nothing paints before it starts; the boot log accumulates in the
conversation surface and appears whole on the first frame. A black screen
with serial lines but no `S6: glass core` line means the glass never
started.

## The obs page

One 4 KB page, page-aligned, its address on line 14. Every field is a
`u64` at a fixed offset, written by exactly one writer — the thing doing
the work — and read by anyone: the glass core, the twin and the harness
(through the monitor: `xp /512xg <address>`). Times are **TSC ticks**; a
reader converts with `tsc_per_ms` from the page itself.

| Offset | Field | Written by | Meaning |
|---|---|---|---|
| `0x00` | magic | boot | the eight bytes `OBSPAGE2` |
| `0x08` | `tsc_per_ms` | boot | TSC ticks per millisecond, calibrated against the PIT |
| `0x10` | `tsc_boot` | boot | the TSC at calibration |
| `0x18` | `mode` | BSP | 0 prompt, 1 asking, 2 growing, 3 running, 4 installing (ring 6b) |
| `0x20` | `glass_apic` | glass | the glass core's local APIC id |
| `0x28` | `frames` | glass | frames drawn |
| `0x30` | `frame_last` | glass | the last frame's steps 2–4 |
| `0x38` | `frame_worst` | glass | the worst |
| `0x40` | `photon_last` | glass | see "Input-to-photon" |
| `0x48` | `photon_worst` | glass | the worst |
| `0x50` | `keys` | BSP | keys delivered by the keyboard consumer — to the prompt or to an app — printables, Enter, Backspace, Tab and Esc alike |
| `0x58` | `keys_hw` | IRQ1 | the scancode ring's high-water occupancy |
| `0x60` | `errors` | BSP | error lines shown on the console: `nothing to ask`, `nothing to grow`, `bad component frame`, `no answer from the broker`, every refusal |
| `0x68` | `questions` | BSP | questions sent to the broker |
| `0x70` | `requests` | BSP | grow requests sent |
| `0x78` | `notes` | BSP | notes on the disk (the notebook's count, this and earlier boots) |
| `0x80` | `disk_reqs` | BSP | virtio-blk requests |
| `0x88` | `disk_wait` | BSP | ticks spent polling for their completion |
| `0x90` | `wire_conns` | BSP | TCP connections opened |
| `0x98` | `bytes_in` | BSP | Ethernet bytes received from the NIC (the virtio header excluded) |
| `0xA0` | `bytes_out` | BSP | Ethernet bytes sent |
| `0xA8` | `wire_wait` | BSP | ticks inside a question's or request's whole exchange |
| `0xB0` | `grows_generated` | BSP | app frames received whose `source` byte is 0 |
| `0xB8` | `grows_served` | BSP | app frames received whose `source` byte is 1 |
| `0xC0` | `steps` | BSP | `step` calls completed |
| `0xC8` | `step_last` | BSP | the last `step`'s duration |
| `0xD0` | `step_worst` | BSP | the worst |
| `0xD8` | `tt_last` | BSP | time-to-done: the last Enter's stamp to its prompt coming back |
| `0xE0` | `tt_worst` | BSP | the worst |
| `0xE8` | `focus` | BSP | 0 the prompt has the keys, 1 the app has them |
| `0xF0` | `cols` | boot | `C` |
| `0xF8` | `rows` | boot | `R` |
| `0x100` | `name` | BSP | the running app's name, 32 bytes, NUL-padded; empty when none |
| `0x120` | `echo_stamp` | BSP | see "Input-to-photon" |
| `0x128` | `echo_pending` | BSP sets, glass clears | |
| `0x130` | `now` | glass | the TSC at the start of the last frame drawn — what the strip's `up` was computed from, so a reader can render the strip exactly as that frame did |
| `0x140` | strip surface | boot | a descriptor, below |
| `0x180` | choices surface | boot | |
| `0x1C0` | conversation surface | boot (cursor: BSP) | |
| `0x200` | app surface | boot | |

A **surface descriptor** is 64 bytes of `u64`s: `+0` the cells' address,
`+8` the dirty bytes' address, `+16` first row, `+24` first column, `+32`
rows, `+40` columns, `+48` the cursor word (the conversation's; 0
elsewhere), `+56` reserved. The rest of the page is zero.

**Input-to-photon.** The keyboard interrupt stores `rdtsc` in a stamp ring
beside the scancode ring. The keyboard consumer hands the stamp of the
byte it translated to the boot processor, which — once it has finished
acting on that key (the echo drawn into the conversation surface, or the
app's `key` returned) — stores it as `echo_stamp` and sets `echo_pending`
to 1 unless one is already pending (the older stamp is kept, so the worst
case is measured). The glass core reads `echo_pending` **before** a
frame's rendering and measures **after** it, so the frame credited is one
that painted the echo. **`ph` is therefore the time from the keyboard
interrupt stamping a key to the end of the frame copy that painted its
echo into the framebuffer — not literally a photon.** A key that draws
nothing (an app that ignores it, a Backspace at the prompt's start) is
still measured, from its stamp to the next frame's end.

## The obs strip

Redrawn by the glass core from the obs page every frame, drawn from column
0 of rows 0 and 1, cut at the right edge on a narrower screen. Every number
is fixed width, zero padded, saturating at all nines. A time is
milliseconds to one decimal: `tenths = ticks × 10 / tsc_per_ms`, integer
division, capped at 999, shown `%02d.%d`. Two rows of 87 characters:

```
up 000012 core 01 fr 000000 00.0/00.0 ph 00.0/00.0 k 0000 hw 000 err 000 step 00.0/00.0
prompt            q 000 n 000 g 000/000 disk 0000 000000 w 000 000000 io 000000/000000
```

| Field | Width | From |
|---|---|---|
| `up` | 6 | `(now − tsc_boot) / tsc_per_ms / 1000`, seconds, `now` the frame's own stamp |
| `core` | 2 | `glass_apic` |
| `fr` | 6, then `last/worst` | `frames`, `frame_last`, `frame_worst` |
| `ph` | `last/worst` | `photon_last`, `photon_worst` |
| `k` | 4 | `keys` |
| `hw` | 3 | `keys_hw` |
| `err` | 3 | `errors` |
| `step` | `last/worst` | `step_last`, `step_worst` |
| the mode word | 18 | `prompt`, `asking`, `growing`, `running <name>` with the name cut to 10 characters, `installing`; space-padded |
| `q` | 3 | `questions` |
| `n` | 3 | `notes` |
| `g` | 3/3 | `grows_generated`/`grows_served` |
| `disk` | 4, 6 | `disk_reqs`, `disk_wait / tsc_per_ms` (ms) |
| `w` | 3, 6 | `wire_conns`, `wire_wait / tsc_per_ms` (ms) |
| `io` | 6/6 | `bytes_in`/`bytes_out` |

**Every number on the strip is counted or stamped by the guest itself,
with one exception, stated plainly: grows served is taken from the
broker's `source` byte in the frame it delivered** — the guest cannot know
by itself whether a frame came from the germline. Nothing on the strip is
estimated.

## The choices row

Row R−2, from column 0, items separated by three spaces; row R−1 blank
this ring. Written by the boot processor whenever the app or the focus
changes:

| State | The row |
|---|---|
| no app running | `? ask   ! grow` |
| an app running, the app has the keys | the **first three** declared choices at most, each `<key> <label>` (the label's padding trimmed), then `Esc exit   Tab prompt` |
| an app running, the prompt has the keys | `? ask   ! grow   Tab app   Esc exit` |

Never more than five items (Hick). The frame carries up to four choices;
the row shows the first three.

## An app is four callbacks

Stage 5's component took the whole screen and the whole processor until
Esc. An **app** takes a panel and a turn. Its blob begins with a **16-byte
header of four `u32` offsets** from the blob's first byte — `init`,
`step`, `key`, `exit` — each below the blob's length; code and data
follow. The guest `call`s `blob + offset`:

- in 64-bit long mode, ring 0, on the guest's identity map; interrupts
  **enabled**; the direction flag clear; `RSP + 8` 16-byte aligned at
  entry, on the boot processor's stack (an app should use under 4 KB);
- **`init`**: `RDI` = the address of the service table. Called once, when
  the app is launched.
- **`step`**: no arguments. Called once per pass of the main loop while
  the app runs; consecutive calls begin at least **10 ms** apart, and a
  `step` is expected back within **50 ms** — the budget the rehearsal
  judges from the obs page.
- **`key`**: `RDI` = the key as one ASCII byte — a printable `0x20`–`0x7E`
  with Shift applied, `13` Enter, `8` Backspace. Called for each key while
  the app has the keys. Tab (`9`) and Esc (`0x1B`) are never delivered.
- **`exit`**: no arguments. Called once, when the app closes.

Each callback returns with `ret`, `RSP` as it found it; it may clobber
every other register (the loader keeps its state in memory); `RAX` on
return is ignored. The blob is position-independent (`bits 64`, `default
rel`, no absolute address of its own), may keep writable data inside
itself, may use port I/O its request needs (a clock reads the CMOS RTC at
`0x70`/`0x71`), and touches **nothing else the guest owns**: no serial
port, no framebuffer, no keyboard ports, no PIC, no notebook, no network,
no interrupt table, no page tables. It draws only through the services,
into its own panel.

**The service table**, `RDI` at `init`:

| Offset | Size | Value |
|---|---|---|
| 0 | 4 | `u32` ABI version, `2` |
| 4 | 4 | `u32` table size in bytes, `40` |
| 8 | 8 | address of `draw_text` |
| 16 | 8 | address of `panel_size` |
| 24 | 8 | address of `ticks_ms` |
| 32 | 8 | address of `fill` |

**Calling a service:** arguments in `RDI`, `RSI`, `RDX`, `RCX`, `R8` in
that order; the result in `RAX`. A service preserves `RBX`, `RBP`, `RSP`
and `R12`–`R15` and may clobber `RAX`, `RCX`, `RDX`, `RSI`, `RDI` and
`R8`–`R11`. No stack alignment is required. `DF` is clear on entry and on
return.

- **`draw_text(row, col, ptr, len)`** — `RDI` = row, `RSI` = column,
  **relative to the app panel**, `RDX` = the bytes, `RCX` = how many. Each
  byte into the next cell along the row, stopping at the panel's right
  edge; a row or column outside the panel draws nothing; a byte outside
  `0x20`–`0x7E` draws as a space. Cells only: the glass core paints them.
  No result.
- **`panel_size()`** — `RAX` = `cols | (rows << 32)` of the app panel
  (`45 | 86 << 32` on this machine).
- **`ticks_ms()`** — `RAX` = milliseconds since boot, `u64`, monotonic.
- **`fill(row, col, rows, cols, colour)`** — `RDI`, `RSI`, `RDX`, `RCX`,
  `R8`: the rectangle, panel-relative, clipped to the panel; colour `0`
  the background, `1` the foreground block, anything else the background.
  No result.

Exactly these four. There is no `poll_key`: keys arrive by callback.

## Running an app

On a valid app frame the guest: stops the working indicator; copies the
name and the choices out of the header; counts `grows_generated` or
`grows_served` by the `source` byte; clears the app panel; sets `mode =
running`, `focus = app`, the strip's name and the choices row; and calls
`init`. The conversation is not touched.

While an app runs the main loop never sleeps. Each pass: every key
waiting is taken (`keys` counts each) — with the app in focus a key goes to
`key`, except **Esc**, which closes the app, and **Tab**, which gives the
keys to the prompt; with the prompt in focus a key takes Stage 5's path
(a note, `?`, `!`), except Esc, which still closes the app, and Tab, which
gives the keys back to the app. Then, if at least 10 ms have passed since
the previous `step` began, `step` is called and timed (`steps`,
`step_last`, `step_worst`). Then `pause`. With no app running the loop is
Stage 5's: wait for a key with `hlt`.

**Closing:** Esc calls `exit`, clears the app panel, sets `mode = prompt`,
`focus = prompt`, the name empty, and the choices row for no app; if the
cursor is not at column 0 a fresh line is started and a prompt drawn; the
conversation comes back exactly as it was. A **`!` request while an app
runs closes it first** (as Esc would), then proceeds (`mode = growing`). A
**`?` question while an app runs** asks as before (`mode = asking`) and
the app's `step` is not called until the answer is drawn; the mode word
returns to `running <name>`.

The console lines for a request are Stage 5's, with one change:

| Line | When |
|---|---|
| `nothing to grow` | the body was empty (`nothing to ask` for `?`) |
| `no answer from the broker` | UMBILICAL.md's rule, the 600 s deadline included |
| `bad component frame` | a frame that fails the checks below — **kind `0x01` included: ABI 1 has no callbacks** |
| the refusal text | a refusal frame, drawn as an answer |

Each of them, and each refusal, counts one in `errors`.

## The wire

The grow request is GERMLINE.md's, byte for byte: a request frame whose
first byte is `0x01`, then the body. The response is exactly one frame per
connection: a **refusal**, kind `0x00`, as GERMLINE.md; or an **app**,
kind `0x02`:

| Offset | Size | Value |
|---|---|---|
| 0 | 4 | `u32 N` = 96 + `L` |
| 4 | 1 | `0x02` — the kind |
| 5 | 1 | the ABI version, **`2`** |
| 6 | 1 | `source`: `0` generated by the backend, `1` served from the germline |
| 7 | 1 | zero |
| 8 | 4 | `u32 L`, the blob length, **16 to 1,048,576** |
| 12 | 32 | the **name**: 1 to 32 bytes `0x20`–`0x7E`, NUL-padded |
| 44 | 1 | `installed`: `0` this ring (`1` at ring 6b) |
| 45 | 3 | zero |
| 48 | 52 | four **choice** slots of 13 bytes: a key `0x20`–`0x7E` and a 12-byte label of 1 to 12 printable bytes, NUL-padded; slots used from the first; an unused slot all zero |
| 100 | `L` | the blob, its 16-byte offset header first |

The kind byte and the 95 after it are the **96-byte header**: the blob
begins at byte 96 of the frame's content, byte 100 of the frame. A frame
that says otherwise — kind `0x01` or unknown, ABI not 2, `source` above 1,
byte 7 or bytes 45–47 not zero, `L` below 16 or above the cap, `N ≠ 96 +
L`, a name empty or not printable, a malformed choice, or a callback
offset at or beyond `L` — is not run: `bad component frame`. A response
whose `N` is above **`96 + 1,048,576`** is invalid: the no-answer rule.

**The region and line 13.** The guest keeps a fixed component region of
**`0x100080`** bytes, page-aligned. A response is received straight into
it from **region + 28**: the 4-byte length prefix at +28..+31, the 96-byte
header at +32..+127, and the blob at **region + 128**, 64-byte aligned.
The largest legal frame (4 + 96 + 1,048,576 bytes) ends exactly at region
+ `0x100080`. Line 13 prints region + 128 — the address the blob's first
byte will have — so the address ends in `080`. A blob never assumes it.

## The rehearsal

Every candidate blob boots in the twin before it reaches the guest: a
headless, scripted boot of a private byte-identical copy of the guest
image, with the display flags, fed through the same wire. The twin:

1. starts a one-shot listener on a private port (**9998** by default);
2. boots the copy at `-smp 2` with a fresh 16 MB notebook image, `-vga
   none -device VGA,edid=on,xres=1440,yres=1440`, UMBILICAL.md's cage
   with its `guestfwd` delivering to that port, any extra QEMU arguments
   the caller gives (a later ring's second disk), the monitor on stdio,
   serial to a file, all under `stage6/out/rehearsal/`;
3. waits for `S6: keyboard ready` (60 s), types **`! rehearsal`** and
   Enter through the monitor; the listener answers with the candidate's
   app frame — the name and choices the caller gives, `source` 0 — and
   closes;
4. waits for the listener to report the delivery (30 s), then 3 s more;
   reads the obs page and the conversation and choices surfaces through
   the monitor's `xp`; takes a screendump (**B**: the app running);
5. sends Esc, waits 2 s, types **`after`** and Enter, waits 2 s, reads the
   obs page again, takes a screendump (**C**: the prompt back), and quits.

The criteria, judged in this order; the first that fires names the
failure:

| Phrase | Fires when |
|---|---|
| `the twin did not boot` | no ready line within 60 s, or not exactly the expected number of `S6:` lines (sixteen this ring) |
| `the app was not delivered` | the listener never saw the request, or could not send the frame |
| `the twin reported an error` | any `ERR:` in the serial capture |
| `the app did not run` | after delivery the obs page does not say `mode` 3, the delivered name, and `steps` ≥ 1 |
| `the app drew nothing` | the app panel's region of B is pure background |
| `the app missed its budget` | `step_worst` in the obs page exceeds 50 ms |
| `the app drew outside its panel` | a cell of the conversation panel or the choices row in B is not what its surface, read through `xp`, says — the cursor overlaid on its cell |
| `no live prompt after esc` | the row `> ! rehearsal` is not on the conversation panel in C, or the obs page does not say `mode` 0, or the notebook image does not parse to exactly `["after"]`, or the serial echo after ready is not exactly `! rehearsal\r\nafter\r\n` |
| `the twin timed out` | the whole run took more than 90 s |

The rehearsal **passes** only if none fires — and, when the caller gives a
post-delivery hook (a later ring's plan tests), only if the hook, run
after these nine, returns no phrase. These prove *safe* — boots, loads,
runs, keeps its budget, stays in its panel, faults nothing, exits, the
prompt lives — not *correct*. The rehearsal log is the criteria's
verdicts, the twin's `S6:` lines, any `ERR:` line, the obs numbers read,
and the timing. A rehearsal never touches the germline;
`stage6/out/rehearsal/` is scratch, wiped per run.

## The germline

GERMLINE.md's directory, with the key over `<normalised>|abi2|<machine>`
— so nothing cached at Stage 5 is ever served to a Stage 6 guest — and
`provenance.json` carrying `abi` **2**, plus `name` (the delivered name)
and `choices` (a list of `[key, label]` pairs), beside GERMLINE.md's
fields. Serving from the germline delivers the frame with `source` 1. The
machine string this ring is still `qemu-q35-ovmf`.

## The mock's canned table for requests

`python3 broker/glass.py --mock` generates from this table and calls
nothing outside the repository; questions it answers from UMBILICAL.md's
table. Every lookup counts as one generation call. The rehearsal still
runs, for real, because it is what the acceptance tests judge.

| Body (exact bytes) | Candidate |
|---|---|
| `test app` | the bytes of `stage6/app.bin`; name `test app`; choices `a` `alpha`, `b` `beta` |
| `big` | the same padded with zeros to exactly 1,048,576 bytes — the cap; name `big`; the same choices; the padding sits after the code and never executes |
| `fault` | the 18 bytes `10 00 00 00 10 00 00 00 10 00 00 00 10 00 00 00 0f 0b` — every callback at offset 16, which is `ud2`: an invalid-opcode exception the moment `init` runs; name `fault` |
| `hog` | the bytes of `stage6/hog.bin` — `init` draws `hog`, `step` spins for 200 ms; name `hog` |
| `escapee` | the bytes of `stage6/escapee.bin` — `init` draws `escapee` in its panel, then finds the framebuffer by itself and paints one cell in the conversation panel; name `escapee` |
| `hold` | no candidate: after 8 seconds, the refusal `mock: held` |
| anything else | no candidate: the refusal `mock: no canned component for: ` followed by the body |

`fault`, `hog` and `escapee` must be refused, each with its phrase.

## The broker's record for a request

GERMLINE.md's fields, plus `abi` (`2`) and `name` (the delivered name, or
`null`). `answer_sha256` is over the whole response frame sent, prefix
included — so it differs between a generated delivery (`source` 0) and
the same blob served from the germline (`source` 1); a checker rebuilds
each frame it expects.

## Worked examples

**The request** `! test app`. The body is `test app`, 8 bytes; the frame
is 13 bytes:

```
00000000: 0900 0000 0174 6573 7420 6170 70         .....test app
```

**An app** named `tiny` for the 20-byte blob whose four offsets are all 16
and whose code is `8d 47 01 c3` (`lea eax, [rdi+1]`; `ret` — every
callback is the same four bytes): `L` = 20, `N` = 116; the frame is 120
bytes, the blob at byte 100:

```
00000000: 7400 0000 0202 0000 1400 0000 7469 6e79  t...........tiny
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000040: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000060: 0000 0000 1000 0000 1000 0000 1000 0000  ................
00000070: 1000 0000 8d47 01c3                      .....G..
```

**The same blob as `test app`, served from the germline** — the header
only (bytes 4–99 of the frame): `source` 1, the two choices packed from
the first slot:

```
00000000: 0202 0100 1400 0000 7465 7374 2061 7070  ........test app
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000 0000 6161 6c70  ............aalp
00000030: 6861 0000 0000 0000 0062 6265 7461 0000  ha.......bbeta..
00000040: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

**The largest legal app**, `L` = 1,048,576: `N` = `0x100060`, the frame
`0x100064` bytes; received at region + 28 it ends exactly at region +
`0x100080`.

**The germline key** for `make me a clock` on this ring's machine:
`sha256("make me a clock|abi2|qemu-q35-ovmf")`, its first 16 hex digits:
`dc94314e1c4c5e95`. `Make  me a CLOCK ` normalises to the same string and
the same key. `test app` is `bf5abcfb7651cc3b`.

**The strip** for an obs page with `tsc_per_ms` 3,000,000, `mode` 3, name
`test app`, `glass_apic` 1, `frames` 1234, `frame_last` 300,000 ticks
(0.1 ms), `frame_worst` 24,600,000 (8.2 ms), `photon_last` 9,000,000,
`photon_worst` 48,300,000, `keys` 27, `keys_hw` 3, `errors` 2,
`questions` 1, `notes` 2, `grows_generated` 2, `grows_served` 1,
`disk_reqs` 5, `disk_wait` 6,300,000, `wire_conns` 4, `wire_wait`
123,456,789,000, `bytes_in` 2345, `bytes_out` 987, `step_last` 600,000,
`step_worst` 3,300,000, read 754 seconds after boot:

```
up 000754 core 01 fr 001234 00.1/08.2 ph 03.0/16.1 k 0027 hw 003 err 002 step 00.2/01.1
running test app   q 001 n 002 g 002/001 disk 0005 000002 w 004 041152 io 002345/000987
```

**The choices row** while `test app` has the keys: `a alpha   b beta   Esc
exit   Tab prompt`; with four declared choices `a`–`d`: `a alpha   b beta
c gamma   Esc exit   Tab prompt`; with none: `Esc exit   Tab prompt`.

## Parsing it cold, in Python

The broker, the twin and the checker use this, and nothing more:

```python
import hashlib
import struct

ABI = 2
GROW_MARKER = 0x01
KIND_REFUSAL, KIND_COMPONENT, KIND_APP = 0x00, 0x01, 0x02
HEADER = 96                      # the kind byte and the 95 bytes after it
BLOB_MAX = 1048576
BLOB_HEADER = 16                 # four u32 offsets: init, step, key, exit
NAME_MAX = 32
CHOICES = 4
LABEL_MAX = 12
CHOICES_SHOWN = 3
REFUSAL_MAX = 4096
BODY_MAX = 497
MACHINE = "qemu-q35-ovmf"
STEP_BUDGET_MS = 50
FRAME_HZ = 60
LINES = 16

OBS_MAGIC = b"OBSPAGE2"
OBS = {                          # u64 fields at these byte offsets
    "magic": 0x00, "tsc_per_ms": 0x08, "tsc_boot": 0x10, "mode": 0x18,
    "glass_apic": 0x20, "frames": 0x28, "frame_last": 0x30, "frame_worst": 0x38,
    "photon_last": 0x40, "photon_worst": 0x48, "keys": 0x50, "keys_hw": 0x58,
    "errors": 0x60, "questions": 0x68, "requests": 0x70, "notes": 0x78,
    "disk_reqs": 0x80, "disk_wait": 0x88, "wire_conns": 0x90, "bytes_in": 0x98,
    "bytes_out": 0xA0, "wire_wait": 0xA8, "grows_generated": 0xB0,
    "grows_served": 0xB8, "steps": 0xC0, "step_last": 0xC8, "step_worst": 0xD0,
    "tt_last": 0xD8, "tt_worst": 0xE0, "focus": 0xE8, "cols": 0xF0, "rows": 0xF8,
    "name": 0x100, "echo_stamp": 0x120, "echo_pending": 0x128, "now": 0x130,
}
SURFACES = {"strip": 0x140, "choices": 0x180, "conversation": 0x1C0, "app": 0x200}
SURFACE = {"cells": 0, "dirty": 8, "row0": 16, "col0": 24, "rows": 32, "cols": 40, "cursor": 48}
MODES = {0: "prompt", 1: "asking", 2: "growing", 3: "running", 4: "installing"}
CELL_BLOCK = 0x01


def printable(data):
    return all(0x20 <= b <= 0x7E for b in data)


def is_grow(request):
    return (2 <= len(request) <= 1 + BODY_MAX and request[0] == GROW_MARKER
            and printable(request[1:]))


def grow_request(body):
    return struct.pack("<I", 1 + len(body)) + bytes([GROW_MARKER]) + body


def refusal_frame(text):
    return struct.pack("<I", 1 + len(text)) + bytes([KIND_REFUSAL]) + text


def app_header(length, name, choices, source=0, installed=0):
    if not 1 <= len(name) <= NAME_MAX or not printable(name):
        raise ValueError("name must be 1..32 printable bytes")
    if len(choices) > CHOICES:
        raise ValueError("at most four choices")
    slots = b""
    for key, label in choices:
        if not (0x20 <= key <= 0x7E) or not 1 <= len(label) <= LABEL_MAX or not printable(label):
            raise ValueError("a choice is a printable key and a 1..12 byte printable label")
        slots += bytes([key]) + label.ljust(LABEL_MAX, b"\0")
    slots = slots.ljust(CHOICES * (1 + LABEL_MAX), b"\0")
    return (bytes([KIND_APP, ABI, source, 0]) + struct.pack("<I", length)
            + name.ljust(NAME_MAX, b"\0") + bytes([installed, 0, 0, 0]) + slots)


def app_frame(blob, name, choices=(), source=0, installed=0):
    body = app_header(len(blob), name, choices, source, installed) + blob
    return struct.pack("<I", len(body)) + body


def blob_offsets(blob):
    """The four callback offsets, or a ValueError naming what is wrong."""
    if len(blob) < BLOB_HEADER:
        raise ValueError("blob shorter than its 16-byte header")
    offs = struct.unpack_from("<IIII", blob, 0)
    if any(o >= len(blob) for o in offs):
        raise ValueError("a callback offset lies beyond the blob")
    return offs


def parse_response(content):
    """The bytes after the length prefix. Returns ("refusal", text) or
    ("app", blob, name, choices, source, installed); raises ValueError."""
    if not content:
        raise ValueError("empty response")
    kind = content[0]
    if kind == KIND_REFUSAL:
        text = content[1:]
        if len(text) > REFUSAL_MAX or not all(0x20 <= b <= 0x7E or b == 0x0A for b in text):
            raise ValueError("refusal text is not printable ASCII or LF within 4096 bytes")
        return "refusal", text
    if kind == KIND_COMPONENT:
        raise ValueError("kind 0x01 is a Stage 5 component - ABI 1 has no callbacks")
    if kind != KIND_APP:
        raise ValueError("unknown response kind 0x%02x" % kind)
    if len(content) < HEADER:
        raise ValueError("app frame shorter than its header")
    if content[1] != ABI:
        raise ValueError("ABI version %d, want %d" % (content[1], ABI))
    source = content[2]
    if source not in (0, 1) or content[3] != 0:
        raise ValueError("source byte or byte 3 is not what the document says")
    length, = struct.unpack_from("<I", content, 4)
    if not 1 <= length <= BLOB_MAX:
        raise ValueError("blob length %d is outside 1..%d" % (length, BLOB_MAX))
    raw = content[8:8 + NAME_MAX]
    name = raw.split(b"\0", 1)[0]
    if not name or not printable(name) or any(raw[len(name):]):
        raise ValueError("name is not 1..32 printable bytes, NUL-padded")
    installed = content[40]
    if installed not in (0, 1) or any(content[41:44]):
        raise ValueError("installed byte or bytes 41-43 are not what the document says")
    choices = []
    for i in range(CHOICES):
        slot = content[44 + i * 13:44 + (i + 1) * 13]
        if slot[0] == 0:
            if any(slot):
                raise ValueError("an empty choice slot is not all zero")
            continue
        if choices and len(choices) < i:
            raise ValueError("choice slots are not packed from the first")
        label = slot[1:].split(b"\0", 1)[0]
        if not (0x20 <= slot[0] <= 0x7E) or not label or not printable(label) or any(slot[1 + len(label):]):
            raise ValueError("a choice is a printable key and a 1..12 byte printable label")
        choices.append((slot[0], label))
    if len(content) != HEADER + length:
        raise ValueError("frame carries %d bytes, header says %d" % (len(content) - HEADER, length))
    blob = content[HEADER:]
    blob_offsets(blob)
    return "app", blob, name, choices, source, installed


def normalise(body):
    return " ".join(body.lower().split())


def germline_key(body, machine=MACHINE):
    s = "%s|abi%d|%s" % (normalise(body), ABI, machine)
    return hashlib.sha256(s.encode("ascii")).hexdigest()[:16]


def regions(cols, rows):
    """The four regions as (row0, col0, rows, cols); None if too small."""
    if cols < 8 or rows < 8:
        return None
    half = cols // 2
    return {"strip": (0, 0, 2, cols), "choices": (rows - 2, 0, 2, cols),
            "conversation": (2, 0, rows - 4, half), "app": (2, half, rows - 4, cols - half)}


def parse_obs(page):
    """The obs page's bytes (at least 0x240). Returns a dict of the fields,
    the name as a string, and each surface as a dict."""
    if page[0:8] != OBS_MAGIC:
        raise ValueError("no obs page magic")
    obs = {}
    for field, off in OBS.items():
        if field == "magic":
            continue
        if field == "name":
            obs[field] = page[off:off + NAME_MAX].split(b"\0", 1)[0].decode("ascii", "replace")
        else:
            obs[field], = struct.unpack_from("<Q", page, off)
    for name, base in SURFACES.items():
        obs[name] = {k: struct.unpack_from("<Q", page, base + o)[0] for k, o in SURFACE.items()}
    return obs


def fmt_n(value, width):
    return "%0*d" % (width, min(value, 10 ** width - 1))


def fmt_ms(ticks, tsc_per_ms):
    tenths = min(ticks * 10 // max(tsc_per_ms, 1), 999)
    return "%02d.%d" % (tenths // 10, tenths % 10)


def mode_word(mode, name):
    word = MODES.get(mode, "?")
    if mode == 3:
        word = "running " + name[:10]
    return word.ljust(18)


def strip_rows(obs, now_ticks):
    """The two strip rows, exactly as the glass core draws them."""
    t = max(obs["tsc_per_ms"], 1)
    up = (now_ticks - obs["tsc_boot"]) // t // 1000
    row0 = "up %s core %s fr %s %s/%s ph %s/%s k %s hw %s err %s step %s/%s" % (
        fmt_n(up, 6), fmt_n(obs["glass_apic"], 2), fmt_n(obs["frames"], 6),
        fmt_ms(obs["frame_last"], t), fmt_ms(obs["frame_worst"], t),
        fmt_ms(obs["photon_last"], t), fmt_ms(obs["photon_worst"], t),
        fmt_n(obs["keys"], 4), fmt_n(obs["keys_hw"], 3), fmt_n(obs["errors"], 3),
        fmt_ms(obs["step_last"], t), fmt_ms(obs["step_worst"], t))
    row1 = "%s q %s n %s g %s/%s disk %s %s w %s %s io %s/%s" % (
        mode_word(obs["mode"], obs["name"]),
        fmt_n(obs["questions"], 3), fmt_n(obs["notes"], 3),
        fmt_n(obs["grows_generated"], 3), fmt_n(obs["grows_served"], 3),
        fmt_n(obs["disk_reqs"], 4), fmt_n(obs["disk_wait"] // t, 6),
        fmt_n(obs["wire_conns"], 3), fmt_n(obs["wire_wait"] // t, 6),
        fmt_n(obs["bytes_in"], 6), fmt_n(obs["bytes_out"], 6))
    return row0, row1


def choices_row(app_running, focus, choices):
    """Row R-2 of the choices region, from column 0."""
    if not app_running:
        return "? ask   ! grow"
    if focus == 0:
        return "? ask   ! grow   Tab app   Esc exit"
    items = ["%s %s" % (chr(k), label.decode("ascii")) for k, label in choices[:CHOICES_SHOWN]]
    return "   ".join(items + ["Esc exit", "Tab prompt"])
```
