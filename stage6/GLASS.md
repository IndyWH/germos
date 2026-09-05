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

## Ring 6c — the pointer

**Stage 6 ring 6c, plan item 1. Appended by the owner's own hand; frozen
with the rest of this file.** Everything above this heading — the 6a
document from its first line to the closing fence before this one — stands
**byte for byte**: the screen, the surfaces and the glass core, the obs page
to `0x23F`, the strip's two rows of 87 characters, the choices row, the four
callbacks and the four services, the wire, the rehearsal's nine criteria,
the germline, the mock's table, the Python. `stage6/HOME.md` and
`stage6/PLANS.md` stand too. This section adds **the pointer**: the PS/2
mouse and how the i8042 is configured for it, one serial line, the obs
page's pointer fields from `0x240`, the cursor, pointer input-to-photon and
the strip's third field, what a click does on the choices row, a **fifth
callback** an app may announce inside its blob, and what the mock serves. It
**supersedes one sentence** of the 6a text: "The rest of the page is zero"
holds from `0x2C0`, not from `0x240`, from this ring on. The assembler
implements this section; the broker module, the twin's caller and the
acceptance checker parse by it. One text, four readers. If it is wrong, that
is a spec question for the owner, not an edit.

### The device

**The PS/2 mouse on the i8042's auxiliary port.** Stage 2 inherited the
controller as the firmware left it. This ring configures it, once, in the
keyboard block, interrupts off, before `S6: keyboard ready`:

1. `AD` and `A7` to port `0x64` — both ports disabled; port `0x60` drained.
2. `20` to `0x64` — the **command byte** read from `0x60`. Bits 0 and 1 are
   set (the keyboard's and the auxiliary port's interrupts), bits 4 and 5
   are cleared (the two ports enabled; bit 5 set means the auxiliary port is
   *disabled*), every other bit is kept as found — bit 6, translation, in
   particular: the keyboard map is scancode set 1 and the firmware's
   translation must survive. `60` to `0x64`, then the byte to `0x60`; read
   back with `20`. On this machine OVMF leaves `0x67` and the guest writes
   `0x47`; the values are the firmware's and are recorded, not assumed.
3. `A8` to `0x64` — the auxiliary port enabled.
4. To the mouse, each byte as `D4` to `0x64` then the byte to `0x60`, each
   answer polled from `0x60` with the status byte read first and routed by
   its bit 5: **`FF`** (reset) → `FA`, `AA`, then the ID byte (`00`, a
   standard three-byte mouse); **`F6`** (defaults) → `FA`; **`F4`** (enable
   reporting) → `FA`. Every wait is bounded (the PIT, about half a second a
   response); a mouse that does not answer costs that and nothing more —
   `mouse_id` stays 0 and boot goes on.
5. Port `0x60` drained again.

The **PIC**: master `OCW1` **`0xF9`** (IRQ1 and the cascade IRQ2 open),
slave **`0xEF`** (IRQ12 open); every other line masked, as Stage 2 left
them. Gates at `0x21` (IRQ1) and **`0x2C`** (IRQ12) enter one handler body
with two exits: EOI to the master for IRQ1; EOI to the slave (`0xA0`) then
the master for IRQ12. A spurious IRQ15 (vector **`0x2F`**) gets EOI to the
master only; a spurious IRQ7 none, as before.

**The handler** reads the status byte at `0x64` first and, **while bit 0 is
set**, reads one byte from `0x60` and routes it by **status bit 5**: clear,
a keyboard byte — into the scancode ring with its stamp, exactly as ring 6a;
set, a mouse byte — into the packet state machine below. A handler that
finds the output buffer empty (the other vector's drain took its byte) does
nothing but EOI. A byte never lands in the wrong ring.

**The packet.** Three bytes: byte 0 has **bit 3 always set**, bits 0–2 the
buttons held (left, right, middle), bits 4 and 5 the signs of the deltas;
byte 1 `dx`, byte 2 `dy`, each a signed byte, **`dy` positive upwards**
(PS/2's convention, so a move down the screen arrives negative). The state
machine keeps its phase across interrupts; a byte arriving in phase 0
without bit 3 is dropped and counted in `resyncs`; phase 0 also records the
TSC as the packet's stamp; the third byte completes the packet:
`ptr_x += dx` and `ptr_y −= dy`, each clamped to the console's cells
(`0 … 16C−1`, `0 … 16R−1`) — not to the mode: a mode is not a whole number
of cells (1080 is 67 rows and 8 spare pixels), and a pointer clamped to
the framebuffer could name a row the console lacks, where nothing owns the
cell and the arrow leaves ghosts — then **`ptr_cell = (y >> 4) << 16 | (x >> 4)` stored as one
`u64` after the two positions** — the glass reads only the cell word, so it
never reads a torn position; `buttons` = byte 0 bits 0–2 and the bits newly
set are the **presses**; `packets += 1`; `ptr_stamp` and `ptr_pending`
below; and one **entry per packet** — the stamp, the cell word, the buttons,
the presses, 16 bytes — into **the mouse ring** (64 entries), head written
by the handler, tail by the boot processor's consumer, dropped when full,
`mouse_hw` its high-water occupancy: the keyboard ring's discipline, one
packet per entry instead of one scancode. The overflow bits are ignored;
there is no acceleration; the pointer starts at the screen's centre pixel
(`W/2`, `H/2`).

**Measured on this machine, and true of QEMU's i8042 whatever the
firmware:** one monitor `mouse_move` is one packet while both deltas fit in
a signed byte and splits above 127 counts per axis, both axes drained
together; a `mouse_button` change with no move sends one packet; no packet
follows the enable unasked; every keyboard byte keeps status bit 5 clear
with the auxiliary port live.

### The eighteenth line

**`S6: mouse ready`** is printed **once, on serial only** — a raw write to
the UART, never the tee, so it never lands in the conversation — the first
time the boot processor's main loop finds `packets` above zero. It is not a
boot line: a machine whose mouse never moves prints exactly the seventeen
lines of HOME.md (sixteen with one disk) and its echo after `S6: keyboard
ready` is exactly what was typed; the twin, whose mouse never moves, sees
the same. After the first packet the serial stream carries the eighteenth
line wherever that packet fell, between typed lines or inside one. What the
guest knows at boot — whether the mouse answered its reset — is in the obs
page from boot: `mouse_id`.

### The obs page, from `0x240`

Every field a `u64`, one writer each, read by anyone through `xp /88xg`.
"IRQ" is the i8042 handler on the boot processor.

| Offset | Field | Written by | Meaning |
|---|---|---|---|
| `0x240` | `ptr_x` | IRQ | the pointer's x in pixels, `0 … 16C−1` (the console's cells, not the mode); `W/2` at boot |
| `0x248` | `ptr_y` | IRQ | y in pixels, `0 … 16R−1`; `H/2` at boot |
| `0x250` | `ptr_cell` | IRQ | `row << 16 \| col`, the cell holding the pointer, stored after the two above |
| `0x258` | `packets` | IRQ | complete three-byte packets received |
| `0x260` | `buttons` | IRQ | the buttons held after the last packet: bit 0 left, 1 right, 2 middle |
| `0x268` | `mouse_hw` | IRQ | the mouse ring's high-water occupancy |
| `0x270` | `ptr_stamp` | IRQ | the TSC at the first byte of the packet awaiting its frame |
| `0x278` | `ptr_pending` | IRQ sets, glass clears | |
| `0x280` | `pointer_last` | glass | pointer input-to-photon, ticks |
| `0x288` | `pointer_worst` | glass | the worst |
| `0x290` | `clicks` | BSP | button presses the consumer saw |
| `0x298` | `hits` | BSP | presses that landed on a choices-row target or reached `point` |
| `0x2A0` | `mouse_bytes` | IRQ | bytes routed to the mouse by status bit 5 |
| `0x2A8` | `resyncs` | IRQ | bytes dropped while waiting for a packet's first byte |
| `0x2B0` | `mouse_id` | boot | 0 no mouse answered the reset; else 1 + the ID byte (1 for a standard mouse) |
| `0x2B8` | `i8042_cmd` | boot | the command byte as read (bits 0–7) and as written (bits 8–15) |

The rest of the page, from `0x2C0`, is zero.

### The cursor

**The arrow** is one cell: an 8x8 glyph doubled to 16x16 like every glyph of
the shared font (FONT.md: bit 0 of a row byte is the leftmost pixel), in the
foreground colour on the background — two colours, as everything:

```
01 03 07 0F 1F 0D 19 30

X.......
XX......
XXX.....
XXXX....
XXXXX...
X.XX....
X..XX...
....XX..
```

Its tip is the cell's top-left pixel; the cell is `ptr_cell`. It is painted
through the glyph painter directly, never through a surface cell byte (a
cell byte of `0x02` is still background, as the 6a text says).

**The glass core's frame** gains one step and one measurement. Step 1 also
snapshots `ptr_pending`. After step 3 (the strip), **step 3b:** if `packets`
is non-zero, read `ptr_cell`; if it differs from the cell the arrow was last
drawn at, **repaint that old cell from its surface** — the owning surface is
the first of the four descriptors in the obs page whose `row0`, `col0`,
`rows`, `cols` contain the cell, the cell byte painted as `surf_render`
would paint it, the conversation's block cursor overlaid when it sits there
— then paint the arrow at the new cell and remember it. The arrow is painted
**every frame**, after everything else (a dirty row may just have repainted
its cell), so nothing paints over it inside a frame. Step 4 gains: if
`ptr_pending` was 1 at step 1, `pointer_last = rdtsc − ptr_stamp`,
`pointer_worst = max`, `ptr_pending = 0`. **No cursor is drawn until the
first packet** — `packets` is 0 — so a machine whose mouse never moves
paints exactly what ring 6a painted.

### Pointer input-to-photon, and the strip's third field

The handler stamps a packet at its first byte's interrupt; when the packet
completes, if no stamp is pending, `ptr_stamp` takes it and `ptr_pending`
becomes 1 (an older pending stamp is kept — the worst case is measured). The
glass core reads `ptr_pending` **before** its copies and measures **after**
them, so the frame credited is one that painted the cursor where that
packet put it. **`pt` is the time from the interrupt that delivered a
packet's first byte to the end of the frame copy that drew the cursor after
it** — not literally a photon, as `ph` is not. A packet that moves the
cursor to no new cell is still measured, to the next frame's end.

**The strip's row 0**, from **column 88**, **only while `packets` is above
zero**: `pt LL.L/WW.W pk NNNN cl NNN` — `pointer_last` and `pointer_worst`
as milliseconds to one decimal in the 6a strip's `%02d.%d` (saturating at
`99.9`), `packets` four digits, `clicks` three, zero padded, saturating at
all nines. Columns 87 and beyond are blank until then, so before the mouse
speaks the strip is the 6a strip to the character; cut at the right edge on
a narrower screen, as the strip always was (a 90-column screen shows `pt`
and no more). Row 1 is unchanged.

### The click on the choices row

A **press** is a button's bit going from clear to set in a packet; the boot
processor's consumer pops the mouse ring, counts every press in `clicks`,
and acts on its cell:

| The press | What happens |
|---|---|
| **button 1 on screen row `R−2`, within an item's text** — from the item's first character to its last, the items being exactly those the row shows (6a's table, HOME.md's extension), separated by three spaces | one in `hits`, and the item acts **as its key would**, by the same path a typed key takes (the stamp of the press is the key's stamp, so `ph` measures the click's echo): **`? ask`** types `?`; **`! grow`** types `!` — whatever the prompt line already holds; **`! <name>`** (an installed app) types `!`, a space, the name and Enter — **only when the prompt line is empty**; with text on the line it is a click and not a hit, and types nothing; **`<k> <label>`** (an app's declared choice, shown while the app has the keys) delivers `<k>` to the app's `key`; **`Esc exit`** is Esc; **`Tab prompt`** and **`Tab app`** are Tab |
| **button 1 on row `R−1`** — the blank row under the choices row, its margin: a slam to the bottom edge must hit the target, not a dead row (Fitts) | judged by its column exactly as a press on row `R−2`: the same table, the same hit, the same act |
| button 1 on row `R−2` or `R−1` in a gap or on the blank tail; button 2 or 3 anywhere on either row | nothing but the count |
| any button inside the **app panel** while an app runs | `point(row, col, button)` if the app announces it (below), and one in `hits`; nothing for a four-callback app |
| anywhere else — the conversation, the strip, the app panel with no app | nothing but the count |

The synthetic keys are not counted in `keys` (the keyboard consumer's
count); they are the click's, counted in `clicks` and `hits`. A `!` line
typed by a click takes HOME.md's path: the launch, with nothing on the
wire. Focus never moves on a click in the app panel: Tab and the row's Tab
items move it, visibly. `finish_line`'s discard (the keys typed while the
machine was busy) also empties the mouse ring — presses made then are
dropped like those keys; the position stands, the cursor is live throughout,
because the handler keeps it.

### An app is five callbacks, when it says so

The blob's first 16 bytes are the four `u32` offsets of the 6a text. A blob
whose length is at least 28 and whose **bytes 16–23 are the eight ASCII
bytes `POINTER2`** announces a fifth: **bytes 24–27, a `u32` offset of
`point`**, which must be at least 28 and below the blob's length — a blob
with the magic and an offset outside that range is `bad component frame`,
as a bad offset among the four is. A blob without the magic is a
four-callback app and is clicked on without effect: every app that existed
before this ring is one (measured: none carries the magic by accident).

- **`point`**: `RDI` = the row, `RSI` = the column, **relative to the app
  panel**, of the cell the press landed on; `RDX` = the button, **1 left,
  2 right, 3 middle**. Called once per press inside the panel while the app
  runs, whoever has the keys; releases and moves are not delivered. The
  calling convention, the stack, the registers and the rules of the other
  four callbacks apply unchanged.

The **service table is unchanged**: ABI version `2`, size `40`, the four
services. The frame is unchanged: kind `0x02`, ABI `2`, the 96-byte header;
the home image's entry is unchanged; a launch from the home image reads the
blob from disk and finds the magic there or not. The frozen `blob_offsets`
and `parse_response` see the magic and the fifth offset as bytes of the
blob, which they are.

### The rehearsal

The nine criteria and the post-delivery hook stand. Two things are added
around them, neither inside the frozen twin: a candidate blob that carries
the magic with an offset outside `[28, L)` is refused **before the twin
boots**, with the phrase **`the point offset lies beyond the blob`**
(delivered to the guest as `rehearsal failed: the point offset lies beyond
the blob`); and **the twin never moves the mouse** — its seventh criterion
compares the conversation and choices regions with their surfaces on
screendump B, and its eighth demands the echo after ready byte-exact, so no
cursor and no eighteenth line may appear in a rehearsal. `point` is proven
on the machine, by the gate's guest.

### The mock's canned table for requests, ring 6c

`python3 broker/pointer.py --mock` answers questions from UMBILICAL.md's
table, installs from PLANS.md's table, plain requests from the 6a table —
and one more:

| Body (exact bytes) | Candidate |
|---|---|
| `point app` | the bytes of `stage6/pointer.bin`; name `point app`; one choice `c` `clear` |

Every lookup counts as one generation call. The rehearsal still runs, for
real, in the 6b twin (1920x1080, the home drive, seventeen lines).

**`point app`** (`stage6/pointer.asm`, frozen): `init` draws `point app` at
panel row 0, column 0; `key` with `c` clears the panel and redraws that
title, any other key does nothing; `step` and `exit` return; `point(row,
col, button)` draws the one glyph `'0' + button` — `1`, `2` or `3` — at the
cell it was given. The row while it has the keys: `c clear   Esc exit   Tab
prompt`.

### Worked examples

**A packet** `28 0a ec` on a 1920x1080 machine with the pointer at the
centre (960, 540): byte 0 `0x28` — bit 3 set, bit 5 set (dy negative), no
buttons; `dx` = `0x0a` = +10; `dy` = `0xec` = −20; the pointer moves to
(970, **560**) — down the screen — and `ptr_cell` is `35 << 16 | 60` =
`0x0023003c`, screen row 35, column 60. The monitor command that produced it
was `mouse_move 10 20`.

**A press**: `09 00 00` — button 1 held, no move — after `08 …` is a left
press at the current cell; `08 00 00` after it is the release. `0a 00 00` is
a right press; `0c 00 00` a middle press; `29 03 fc` a move of (+3, −4 →
down 4) with the left button held.

**The strip's row 0** with the 6a example's page and `pointer_last`
9,000,000 ticks, `pointer_worst` 48,300,000 (`tsc_per_ms` 3,000,000),
`packets` 27, `clicks` 3, on a 120-column screen, from column 85:

```
.1 pt 03.0/16.1 pk 0027 cl 003
```

— the field occupies columns 88–114; with `packets` 0 columns 87–119 are
blank and the row is the 6a row exactly.

**The fixture's header**, 28 bytes, for a blob whose `init` is at 28,
`step` at 40, `key` at 41, `exit` at 60 and `point` at 70:

```
00000000: 1c00 0000 2800 0000 2900 0000 3c00 0000  ....(...)...<...
00000010: 504f 494e 5445 5232 4600 0000            POINTER2F...
```

**The choices row's targets** for `? ask   ! grow   ! echo`: columns 0–4
(`?`), 8–13 (`!`), 17–22 (launch `echo`); a press at column 6 or 15 does
nothing; at column 19 with an empty prompt line it types `! echo` and Enter.
For `c clear   Esc exit   Tab prompt`: 0–6 (`c` to the app), 10–17 (Esc),
21–30 (Tab). For `? ask   ! grow   Tab app   Esc exit`: 0–4, 8–13, 17–23
(Tab), 27–34 (Esc).

### Parsing it cold, in Python

The broker module and the checker use this, with the 6a code above, and
nothing more:

```python
import struct

OBS_6C = {                       # u64 fields at these byte offsets
    "ptr_x": 0x240, "ptr_y": 0x248, "ptr_cell": 0x250, "packets": 0x258,
    "buttons": 0x260, "mouse_hw": 0x268, "ptr_stamp": 0x270, "ptr_pending": 0x278,
    "pointer_last": 0x280, "pointer_worst": 0x288, "clicks": 0x290, "hits": 0x298,
    "mouse_bytes": 0x2A0, "resyncs": 0x2A8, "mouse_id": 0x2B0, "i8042_cmd": 0x2B8,
}
OBS_PAGE_BYTES_6C = 0x2C0        # what parse_obs_6c needs
POINT_MAGIC = b"POINTER2"        # blob bytes 16-23 announce the fifth callback
POINT_HEADER = 28                # four offsets, the magic, the point offset
POINTER_FIELD_COL = 88           # the strip's third field, row 0
POINTER_BUDGET_MS = 2 * 1000 / 60   # two frame slots
MOUSE_LINE = "S6: mouse ready"
ARROW = bytes([0x01, 0x03, 0x07, 0x0F, 0x1F, 0x0D, 0x19, 0x30])   # bit 0 leftmost
BUTTON_OF_MASK = {1: 1, 2: 2, 4: 3}  # the monitor's mouse_button mask -> point's button
KEY_ESC, KEY_TAB, KEY_ENTER = 0x1B, 9, 13


def parse_obs_6c(page):
    """The obs page's bytes (at least 0x2C0): parse_obs plus the pointer's
    fields, and ptr_row / ptr_col from the cell word."""
    obs = parse_obs(page)
    for field, off in OBS_6C.items():
        obs[field], = struct.unpack_from("<Q", page, off)
    obs["ptr_row"], obs["ptr_col"] = obs["ptr_cell"] >> 16, obs["ptr_cell"] & 0xFFFF
    return obs


def point_offset(blob):
    """None for a four-callback blob; the fifth offset for one that announces
    point; a ValueError when the magic is there with an offset outside [28, L)."""
    if len(blob) < POINT_HEADER or blob[16:24] != POINT_MAGIC:
        return None
    off, = struct.unpack_from("<I", blob, 24)
    if off < POINT_HEADER or off >= len(blob):
        raise ValueError("the point offset lies beyond the blob")
    return off


def pointer_cell(x, y):
    return y // 16, x // 16


def pointer_field(obs):
    t = max(obs["tsc_per_ms"], 1)
    return "pt %s/%s pk %s cl %s" % (fmt_ms(obs["pointer_last"], t), fmt_ms(obs["pointer_worst"], t),
                                     fmt_n(obs["packets"], 4), fmt_n(obs["clicks"], 3))


def strip_rows_6c(obs, now_ticks):
    """The two strip rows exactly as the glass core draws them this ring."""
    row0, row1 = strip_rows(obs, now_ticks)
    if obs["packets"]:
        row0 = row0.ljust(POINTER_FIELD_COL) + pointer_field(obs)
    return row0, row1


def render_arrow():
    """The arrow's 16 pixel rows, as render_cell renders a glyph."""
    rows = []
    for b in ARROW:
        line = b"".join(bytes(FG) * 2 if b >> i & 1 else bytes(BG) * 2 for i in range(8))
        rows += [line, line]
    return rows


def choice_targets(app_running, focus, choices, installed=()):
    """The choices row's click targets for the state, (first column, last
    column, kind, argument): kind "key" with the byte a press types or
    delivers, or "launch" with the installed app's name. Built from the same
    items the row shows (6a's choices_row and HOME.md's extension)."""
    if not app_running:
        items = [("? ask", "key", ord("?")), ("! grow", "key", ord("!"))]
        items += [("! " + name, "launch", name) for name in list(installed)[:CHOICES_SHOWN]]
    elif focus == 0:
        items = [("? ask", "key", ord("?")), ("! grow", "key", ord("!")),
                 ("Tab app", "key", KEY_TAB), ("Esc exit", "key", KEY_ESC)]
    else:
        items = [("%s %s" % (chr(k), label.decode("ascii")), "key", k) for k, label in choices[:CHOICES_SHOWN]]
        items += [("Esc exit", "key", KEY_ESC), ("Tab prompt", "key", KEY_TAB)]
    out = []
    col = 0
    for text, kind, arg in items:
        out.append((col, col + len(text) - 1, kind, arg))
        col += len(text) + 3
    return out


def click_action(targets, col, line_empty=True):
    """What a left press at this column of row R-2 does: None for a gap or
    the tail (and for a launch item while the prompt line holds text);
    ("key", byte) or ("launch", name) otherwise."""
    for first, last, kind, arg in targets:
        if first <= col <= last:
            if kind == "launch" and not line_empty:
                return None
            return kind, arg
    return None


def launch_keys(name):
    """The bytes a launch item types: "! <name>" and Enter."""
    return b"! " + name.encode("ascii") + bytes([KEY_ENTER])
```
