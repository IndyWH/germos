# Stage 6, ring 6a — the glass · implementation plan

**To be committed verbatim as `stage6/plan-6a.md`. Produced in plan mode, per
the foundation's build loop. Nothing below is implemented until Wajira
approves this document by writing the approval marker from his own terminal;
the ExitPlanMode hook holds the gate until then. Plan mode allows this
session to write only this one file and forbids commits, so — exactly as
Stages 4 and 5 did — the copy to `stage6/plan-6a.md` and its commit are the
first act after the gate opens, item 0 below, before any other file is
touched. Cowork's amendments while the gate holds are adopted here as
numbered amendments (A1, A2, …) at the end of the document.**

## Context

Stage 5 is closed: on 1 September 2026 `! make me a clock` produced a
running clock, grown by Claude, rehearsed in the twin, cached in the
germline. Stage 6 — growth — is three rings, each with its own plan gate,
frozen tests and session (spec decision 1). This is **ring 6a, the glass**:
the screen gets one owner, the machine starts telling the truth about
itself, and the conversation stays alive while an app runs. The done-when:
**`! make me a clock` ticks in its own panel while you type a note beside
it, and the obs strip shows real numbers.**

`stage6/spec.md` is approved with all eight recommendations taken. What
this ring builds, from the spec: a dedicated **glass core** — the first
application processor — that alone writes pixels after it starts; four
fixed regions on the console's 16x16 grid (obs strip top, choices row
bottom, the conversation left, the app panel right), every size measured
from the mode; **surfaces** in RAM with dirty tracking, composited at a
fixed cadence; an **obs page** every counter is written into by the thing
doing the work and an **obs strip** drawn from it; **ABI 2** — an app is
four callbacks (`init`, `step`, `key`, `exit`) with a 50 ms step budget and
four services (`draw_text` into its own panel, `panel_size`, `ticks_ms`,
`fill`); the **kind `0x02` frame** in one new frozen document
`stage6/GLASS.md`; the **mode policy** of decision 8 (the display's
EDID-preferred mode if it states one, else the highest, the EDID read from
the standard VGA device's own memory); new broker files `broker/glass.py`
and `broker/twin.py` importing the frozen framing; a mock table of `test
app`, `big`, `fault`, `hog`, `escapee`; nine rehearsal criteria; and
acceptance tests 1–4 written red before any code and frozen.

The kickoff's standing orders: the automated gate talks only to the mock,
spends no token and needs no internet; the real `claude -p` backend is
exercised only by the owner at test 5; **the cage, the storage bodyguard
and every existing frozen file stand** — `stage5/GERMLINE.md`,
`broker/germline.py`, `broker/rehearse.py` and every Stage 5 file stay byte
for byte as they are, and `./stage5/test.sh` must still pass at the end of
the ring. If a frozen file needs to change, the session stops at the scope
guard, writes the diff unapplied under `stage6/out/`, records it in
`HANDOVER.md` and says so, as at Stage 5 item 8b.

The plan is **evaluation-first**, as every stage has been. Items 1–7 write
the wire document, the fixtures, the broker's ABI 2 pipeline and twin, and
the acceptance machinery so that tests 1–4 exist and fail before a single
instruction of `stage6.asm` is written. Item 8 freezes them. Items 9–13 grow
the implementation on Stage 5's proven body and the gate closes at item 13.
Item 14 is the handover. Test 5 is Wajira's, with the real broker.

### Environment, verified in this session before planning

No new packages: NASM 3.01, QEMU 10.2.1 (accelerators tcg, mshv, kvm; the
gate uses the default, TCG), Python 3.14, OVMF, mtools, OpenBSD netcat, the
`claude` CLI. The probes below ran on the committed Stage 5 image and on a
patched **scratch copy** of `stage5.asm` built and booted under
`stage5/out/probe/` (never committed, gitignored, removed after this plan
is committed); no Claude call was made.

| Fact | Verified how |
|---|---|
| **The standard VGA device sits at PCI bus 0 device 2, `1234:1111`, class `0300`, with `-vga none -device VGA,edid=on,xres=1440,yres=1440`.** BAR0 is the 16 MB prefetchable framebuffer at `0x80000000` (the GOP framebuffer, as before); **BAR2 is a 4 KB 32-bit MMIO region at `0x81082000` whose first 128 bytes are the EDID** (`00 ff ff ff ff ff ff 00`, vendor `49 14` = QEMU, monitor name `QEMU Monitor`). With those flags the virtio-net NIC moved to device 1 and the disk stayed at device 3; Stage 5's scan finds both by vendor and device id, unchanged | the monitor's `info pci` and `xp /128xb 0x81082000` on the Stage 5 image |
| **The first detailed timing descriptor names 1440x1440.** Bytes 54–55 = `dc 54` (pixel clock, non-zero), 56 = `a0`, 58 = `51` → horizontal active `0x5a0` = 1440; 59 = `a0`, 61 = `50` → vertical active `0x5a0` = 1440 | parsed by hand from the `xp` dump, then by the probe from inside the guest |
| **The guest can read the EDID itself:** a scan of bus 0 for class `0x0300`, BAR2 (register `0x18`) masked to its base, 128 **byte** reads, the header checked, the descriptor parsed: `P: edid 1440x1440 bar2 0x0000000081082000`, before ExitBootServices | the probe's own line |
| **OVMF puts the EDID's preferred mode first: mode 0 of 31 is 1440x1440**; the rest are the fixed list (640x480 … 2560x1600, 2048x2048 at 28). The probe's rule — the EDID's mode if it is in the list, else the highest — chose mode 0: `S5: gop 1440x1440 fb 0x0000000080000000`, `S5: console 90x90`, and a 1440x1440 screendump | `P: mode N WxH` for every mode, `P: chosen 0` |
| **Without an EDID (`-device VGA,edid=off`)** BAR2 still exists but holds no EDID header: `P: edid none`; the list has 30 modes, none 1440x1440, and the highest-area rule takes **2048x2048 (mode 27)**, console 128x128 — Stage 5's mode | the probe at `-smp 8` |
| **QEMU's default VGA (`-vga std`, what Stages 1–5 booted with) carries an EDID of its own naming 1280x800** — `edid=on` is the device's default — and OVMF lists 1280x800 first. Under the new rule that run becomes 80x50 cells. So the flags on every QEMU command are load-bearing, and BAR2's address differs between device sets (`0x81083000` there): the BAR is read at runtime, never assumed | `qemu-system-x86_64 -device VGA,help`; the probe with no `-vga` flag |
| **An AP woken by Stage 1's trampoline runs a painter while the BSP services the keyboard.** AP index 1 built a shifting-stripe band in a RAM buffer (32 scanlines) and copied it to the framebuffer for ever; the BSP echoed `abc` and `d` through its interrupt-driven loop meanwhile. Frames: 8382 at the first Enter, 16623 at the second; the screendump's top 32 rows are half foreground, half background; the console rows below hold the prompt. The same at `-smp 2` (8377 → 17118). At `-smp 1` there is no AP: frames stay 0 | `P: frames …` on each Enter; the screendump census |
| **A full-frame copy to the uncached framebuffer costs 3 ms at 1440x1440 and 5 ms at 2048x2048** (`rep movsd` from RAM, TCG). One 32-scanline band, built pixel by pixel then copied, is about 250 µs. A 60 Hz frame slot is 16.7 ms: a compositor that copies only dirty rows has room to spare, and even a whole-screen repaint fits | `copy_ms` and `band_us` on the probe's line |
| **The monitor's `xp` reads guest memory by an address the guest printed** — `xp /16xb 0x40e060` (the probe's `log_buf`) gave `53 35 3a 20 61 6c 69 76 65 0d 0a` = `S5: alive\r\n`; `xp` on the framebuffer showed the console's two colours; on the component region, zeros; and on the EDID BAR (MMIO), the EDID. This is how the harness and the twin will read the obs page and the surfaces | run 1 and run 3 |
| **Two QEMUs run side by side when the twin boots a copy:** the Stage 5 image on `stage5/out/esp.img` and a byte-identical copy under `stage5/out/probe/twin/`, both with the VGA device, both to thirteen lines. A third QEMU on the *same* file was refused (`Failed to get "write" lock`) — the Stage 5 gotcha, reconfirmed; it also bit this session when four probes were launched on one image at once | run 2; the failed parallel launch |
| **The bodyguard allows every planned command:** the gate's and the twin's QEMU lines with `-vga none -device VGA,edid=on,xres=1440,yres=1440` (and `edid=off`), drives under `stage6/out/` and `stage6/out/rehearsal/`, `python3 broker/glass.py --mock …`, `./stage6/test.sh`, `python3 stage6/checkglass.py --glass 2`, `cp stage6/out/esp.img stage6/out/rehearsal/esp.img`, `nasm -f bin stage6/app.asm -o stage6/app.bin` (allowed until item 8 freezes the binary), the monitor over stdio | the hook run directly on each payload, exit 0 |
| The Stage 5 image's shape, as this ring carries it forward: `absolute` BSS, the BSP stack 16 KB, `console_putc` → `draw_cell` direct to the framebuffer with a text `shadow`, `draw_cursor`/`erase_cursor` painting pixels, `console_redraw` from the shadow, `kbd_next` the one keyboard consumer, `irq1_handler` buffering only, `umbilical_ask` with `rx_dst`/`rx_max`/`rx_deadline`, `grow_request` → `component_valid` → `run_component`, the service table filled with RIP-relative `lea`s, `ap_entry` parking every AP after `lock inc [checkin]`, `tsc_calibrate`/`ticks_ms`, `comp_region` of `0x100040` received from +28 | read, `stage5/stage5.asm` |
| `broker/germline.py` exports the Stage 5 wire, `germline_lookup`/`germline_write` (which write `abi: 1`), `Grower` (whose `grow` imports `rehearse.rehearse` by name), `record_grow`, `handle` (dispatching on `is_grow` to `grower.grow(body)`) and `serve`; `broker/rehearse.py` exports `Listener`, `qemu_argv`, `cage_netdev`, `read_ppm`, `load_font`, `render_cell`, `cell_matches`, `row_on_screen`, `pure_background`, `parse_notebook`. All importable, none editable | read |

---

## Deviations from the spec, for approval

Each argued from a measured fact or from the kickoff's orders. Everything
else is the spec as written.

1. **The ABI 2 frame header is 96 bytes with the kind and ABI as single
   bytes, and one reserved byte becomes `source`.** The spec's fields (kind,
   ABI, blob length, a 32-byte name, `installed`, four choices of key plus a
   12-byte label, reserved zeros) do not fit 96 bytes with 4-byte kind and
   ABI fields (1+3+4+4+32+4+52 = 100). Laid out as kind `u8`, ABI `u8`,
   `source u8`, zero, `u32 L`, name, `installed u8`, three zeros, the four
   choices, the header is exactly 96. `source` (0 = generated, 1 = served
   from the germline) exists because the strip must show "grows generated
   and grows served from the germline" and only the broker knows which; the
   guest counts what the header says.
2. **The component region grows by 64 bytes to `0x100080`, and line 13
   reports region + 128.** Received at +28 as Stage 5 does, a kind `0x02`
   frame's blob begins at +128 (4-byte prefix, 96-byte header), 64-aligned,
   and the largest legal frame (4 + 96 + 1,048,576) ends at +`0x100080`.
   Line 13 keeps Stage 5's shape, `S6: component region 0x<16 hex> 1048576
   bytes`, with the address ≡ 128 mod 4096 — the ABI 2 blob's first byte.
3. **Focus moves between the app and the prompt with Tab.** The spec says a
   running app has the keys except Esc, *and* that you can type a note
   while the clock ticks (test 3 does both), without naming the switch. Tab
   toggles focus while an app runs; the choices row always says where the
   keys go (`Tab prompt` / `Tab app`), so the mode is never hidden. Focus is
   on the app at launch. Tab does nothing at the prompt with no app.
4. **The mock table gains `hold`:** the mock waits 8 s, then refuses with
   `mock: held`, with no candidate and no rehearsal. Test 4 needs "the mock
   told to hold its answer" to screendump the `growing` mode word; a table
   entry keeps it frozen with the rest of the mock.
5. **"The app drew outside its panel" is judged against the surfaces, not
   by a pixel diff over time.** An escapee that paints once at `init` never
   changes anything *while* the twin watches. The twin reads the
   conversation and choices surfaces through `xp` (their addresses are in
   the obs page), renders the pixels they say the screen holds, and
   compares with the screendump: any cell outside the app panel whose
   pixels are not what its surface says fires the phrase. The same
   machinery is test 4's "nothing outside the app panel changes while `test
   app` runs" and "the obs page agrees with the strip".
6. **The sixteen serial lines put `S6: edid …` second**, before the gop
   line — the mode choice depends on it — and `S6: obs page …`, `S6: glass
   core …` after the component region, before `keyboard ready` (decision 1).
7. **`step` is not called while the BSP waits on the wire, and a `!`
   request while an app runs closes the app first.** With no timer
   interrupt (a spec omission) the BSP is inside `umbilical_ask` for the
   whole wait, so a running clock pauses during `? question` and resumes
   after; one app at a time means a new request replaces the old one (Esc
   is implied; undo is `! make me a clock` again, served from the germline
   at once). Both are recorded caveats.

---

## Decisions taken in this plan

Judgement calls inside the approved spec, flagged so Wajira can overrule any
of them at approval rather than find them in a diff.

1. **The sixteen serial lines, exactly**, in order: `S6: alive`; **`S6:
   edid <W>x<H>`** or **`S6: edid none`**; `S6: gop <W>x<H> fb 0x<16 hex>`;
   `S6: boot services exited`; `S6: gdt and paging ours`; `S6: idt ready`;
   `S6: cores found <N>`; `S6: cores woken <N>`; `S6: console <C>x<R>`;
   `S6: disk <N> sectors`; `S6: notebook formatted` | `S6: notebook <N>
   notes`; `S6: nic <mac>`; `S6: component region 0x<16 hex> 1048576
   bytes` (deviation 2: ≡ 128 mod 4096); **`S6: obs page 0x<16 hex>`**
   (page-aligned, non-zero, below 4 GB); **`S6: glass core <id>`** (the
   glass core's APIC id, decimal); `S6: keyboard ready` — last, so the
   echo contract after it stays exactly Stage 2's. At `-smp 1` the log
   ends after line 14 with `ERR: the glass needs a second core - boot with
   -smp 2 or more` and a halt: no glass, no keyboard — and, before the
   halt, the BSP renders the conversation surface to the framebuffer once,
   so the `ERR:` row is on the screen as well as on serial (A3; no glass
   exists on that path, and the BSP halts immediately after).
2. **The mode policy** (spec decision 8, GLASS.md "The screen"), in
   `efi_main` before the mode loop, boot services still up: scan PCI bus
   0 (functions 0–7 of every device, as `pci_scan` does) for class code
   `0x0300`; take BAR2 (register `0x18`), require a memory BAR, mask to
   the base; read **128 bytes with byte reads** (the region's natural
   width); require the header `00 ff ff ff ff ff ff 00`; require a
   non-zero pixel clock in the first detailed timing descriptor (bytes
   54–55); width = byte 56 | (byte 58 >> 4) << 8, height = byte 59 |
   (byte 61 >> 4) << 8. Any step failing → `S6: edid none`. The mode loop
   (Stage 1's, unchanged in what it measures) remembers the first mode
   whose width and height equal the EDID's; after the loop, that mode
   wins if one was found, else Stage 1's highest-area choice stands. The
   framebuffer base, stride and size are read back from the protocol as
   ever. Nothing baked in: with `edid=off` the same binary picks 2048x2048
   (measured).
3. **The four regions** (spec decision 2), all in cells of the console's
   16x16 grid, from `C` = width/16 and `R` = height/16: the **obs strip**
   rows 0–1, columns 0–C-1; the **choices row** rows R-2–R-1, columns
   0–C-1; the **conversation panel** rows 2–R-3, columns 0–⌊C/2⌋-1; the
   **app panel** rows 2–R-3, columns ⌊C/2⌋–C-1. On this machine: 90x90
   cells; strip rows 0–1; choices rows 88–89; conversation 86 rows x 45
   columns at (2, 0); app panel 86 x 45 at (2, 45). A mode with R < 8 or
   C < 8 is `ERR: mode too small for the glass`, rendered once to the
   framebuffer by the BSP before the halt, as the `-smp 1` path is (A3).
   The conversation panel is
   Stage 5's console in every behaviour — wrap at its right edge (45
   columns here: long boot lines wrap), scroll within its rows, the
   prompt, the block cursor — just narrower and lower.
4. **Cells and surfaces** (GLASS.md "Surfaces"). A cell is one byte:
   `0x20`–`0x7E` a glyph from the shared font; **`0x01` a solid
   foreground block** (the cursor's shape, and `fill` colour 1); anything
   else the background. Two colours only, so every pixel test stays as
   before. A **surface** is a cell buffer of `rows x cols` bytes plus a
   **dirty byte per row**. Producer protocol: write the cells, then store
   the row's dirty byte = 1. Consumer protocol (the glass core): for each
   row, if the byte is set, `xchg` it to 0, **then** render the row. x86
   stores are seen in order and there is no compiler, so a cell stored
   before the flag is visible to a render that saw the flag; a cell stored
   after the `xchg` sets the flag again and is rendered next frame. A torn
   row lasts one frame. The conversation surface also carries the
   **cursor** as one packed dword — `on << 31 | row << 16 | col` — written
   atomically; the glass core paints a `0x01` block over that cell when
   rendering its row (the BSP marks the old and the new cursor rows dirty
   when the cursor moves). No lock anywhere. Each surface's descriptor
   (cells address, dirty-bytes address, row0, col0, rows, cols, cursor)
   lives in the obs page (decision 6), so the twin and the harness can
   read every surface through `xp` by one printed address.
5. **The glass core** (spec decision 3). `ap_entry` gives index 1 — the
   first AP to check in — to `glass_main` instead of parking; every other
   AP parks as before. `glass_main` records its APIC id (the xAPIC ID
   register, or the x2APIC MSR when `apic_x2` is set) in the obs page,
   sets `glass_ready`, and spins on `glass_go`. The BSP, after the obs
   page line and with every surface initialised, sets `glass_go`, waits up
   to 1 s for `glass_ready` (an `ERR:` otherwise), prints line 15, and
   **from that instruction never writes a pixel again**: `draw_cell`,
   `draw_cursor`, `erase_cursor` and `fb_clear` are called only from
   `glass_main` — with one exception (A3): on the two error paths that
   halt before any glass exists (`-smp 1`, a mode too small) the BSP calls
   `surface_render` on the conversation surface once and then halts, so
   the `ERR:` line is on screen; the one-owner rule holds because no
   second owner ever runs. Before the glass starts nothing else paints —
   the boot log accumulates in the conversation surface and appears whole
   on the first frame; a black screen with serial lines but no `glass
   core` line means the glass never started (a new line in the debugging
   strategy).
   The loop, for ever with interrupts off: `t0 = rdtsc`; for each surface,
   for each dirty row, render it (`draw_cell` per cell, the cursor
   overlaid); then format the strip from the obs page into the strip
   surface and render it; `frames += 1`; `frame_last = rdtsc - t0`,
   `frame_worst = max`; if a photon measurement was pending before the
   copy began, `photon_last = rdtsc - echo_stamp`, `photon_worst = max`,
   pending cleared (decision 6); then `pause` until `t0 + frame_ticks`
   where `frame_ticks = tsc_per_ms * 1000 / 60` — 60 frames a second, no
   timer interrupt, nothing else to do. At `-smp 1` there is no index 1:
   the BSP's wait fails and it halts with the named `ERR:` (decision 1).
6. **The obs page** (GLASS.md "The obs page"): one page-aligned 4 KB BSS
   page, `u64` fields at fixed offsets, every field written by exactly one
   writer and read by anyone; times are TSC ticks and the reader converts
   with `tsc_per_ms` from the page itself. Offsets: `0x00` magic
   `OBSPAGE2`; `0x08 tsc_per_ms`; `0x10 tsc_boot`; `0x18 mode` (0 prompt,
   1 asking, 2 growing, 3 running, 4 installing — 6b); `0x20 glass_apic`;
   `0x28 frames`; `0x30 frame_last`; `0x38 frame_worst`; `0x40
   photon_last`; `0x48 photon_worst`; `0x50 keys` (every key `kbd_next`
   delivered to the loop or an app); `0x58 keys_hw` (the ring's high-water
   occupancy, written by the interrupt handler); `0x60 errors` (every
   console error line: `nothing to ask`, `nothing to grow`, `bad component
   frame`, `no answer from the broker`, every refusal); `0x68 questions`
   (sent); `0x70 requests` (sent); `0x78 notes` (on disk, `nb_count`);
   `0x80 disk_reqs`; `0x88 disk_wait` (ticks polling completions); `0x90
   wire_conns` (`tcp_connect` calls); `0x98 bytes_in`; `0xA0 bytes_out`
   (Ethernet bytes through the NIC, ARP included); `0xA8 wire_wait` (ticks
   inside `umbilical_ask`); `0xB0 grows_generated`; `0xB8 grows_served`
   (from the header's `source`); `0xC0 steps`; `0xC8 step_last`; `0xD0
   step_worst`; `0xD8 tt_last`; `0xE0 tt_worst` (time-to-done: Enter to
   the prompt back, every line — spec decision 5, recorded not shown);
   `0xE8 focus` (0 prompt, 1 app); `0xF0 cols`; `0xF8 rows`; `0x100` the
   running app's name, 32 bytes; `0x120 echo_stamp`; `0x128 echo_pending`;
   `0x140`, `0x180`, `0x1C0`, `0x200` the strip, choices, conversation and
   app surface descriptors, 64 bytes each: cells, dirty, row0, col0, rows,
   cols, cursor, reserved. The rest zero. **Input-to-photon:** `irq1_handler`
   stores `rdtsc` in a stamp ring beside the scancode ring; `kbd_next`
   returns the stamp of the byte it translated in `key_stamp`; the BSP,
   when it has finished acting on a key (the echo drawn, or the app's `key`
   returned), sets `echo_stamp = key_stamp` and `echo_pending = 1` unless
   one is already pending (the older stamp is kept: worst case measured);
   the glass core snapshots `echo_pending` **before** a frame's copy and
   measures after it, so the frame credited is one that painted the echo.
7. **The obs strip** (GLASS.md "The obs strip"): two rows, redrawn from the
   obs page every frame by the glass core, drawn from column 0, cut at the
   right edge on a narrower screen. Every number is fixed width, zero
   padded, saturating at all nines; times are ms to one decimal, computed
   as `ticks * 10 / tsc_per_ms`, cap `99.9`. Row 0 (87 columns):
   `up 000012 core 01 fr 000000 00.0/00.0 ph 00.0/00.0 k 0000 hw 000 err 000 step 00.0/00.0`
   — uptime seconds; the glass core's APIC id; frames, then the last and
   worst frame time; `ph` last/worst — defined precisely in GLASS.md
   (A4): **the time from the keyboard interrupt stamping a key to the end
   of the frame copy that painted its echo into the framebuffer, not
   literally a photon**; keys; ring high-water; errors shown; step
   last/worst. Row 1 (87 columns):
   `prompt            q 000 n 000 g 000/000 disk 0000 000000 w 000 000000 io 000000/000000`
   — the **mode word** in an 18-column field (`prompt`, `asking`,
   `growing`, `running <name>` with the name cut to 10 characters,
   `installing` at 6b), questions sent, notes on disk, grows
   generated/served, disk requests and wait ms, wire connections and
   broker wait ms, bytes in/out. GLASS.md states plainly (A4) that **grows
   served is the one strip number the guest takes from the broker's
   `source` byte rather than measures itself; everything else on the strip
   is counted by the guest.** The harness renders both rows from the obs
   page it read and compares cell by cell.
8. **The choices row** (Hick, Fitts): row R-2 from column 0, items
   separated by three spaces; row R-1 blank this ring. At the prompt with
   no app: **`? ask   ! grow`**. An app running with focus on the app: **the
   first three declared choices at most** (A1 — the header keeps four
   slots; GLASS.md says the row shows the first three), each as `<key>
   <label>` (the label's padding trimmed), then **`Esc exit   Tab
   prompt`**. An app running with focus on the prompt: **`? ask   ! grow
   Tab app   Esc exit`**. Never more than five items, so Hick's law holds
   by construction. Written by the BSP whenever the mode or focus changes.
9. **ABI 2 — the blob** (GLASS.md "An app is four callbacks"): the blob's
   first 16 bytes are four `u32` offsets from the blob's first byte —
   `init`, `step`, `key`, `exit` — each below `L`; code and data follow,
   position-independent as at Stage 5. The guest `call`s `blob + offset`
   in 64-bit long mode, ring 0, interrupts enabled, `DF` clear, `RSP + 8`
   16-aligned, on the BSP's stack (under 4 KB); a callback returns with
   `ret`, `RSP` as found, may clobber every other register (the loader
   keeps its own state in memory), `RAX` ignored. `init` gets `RDI` = the
   service table; `key` gets `RDI` = the key byte (`0x20`–`0x7E`, `13`,
   `8`, `9` Tab is never delivered, `0x1B` never delivered); `step` and
   `exit` get nothing. **The service table, ABI 2:** `u32` version `2`;
   `u32` size `40`; `+8 draw_text(row, col, ptr, len)` — panel-relative,
   clipped at the panel's right edge, a row outside the panel draws
   nothing, bytes outside `0x20`–`0x7E` draw as spaces, cells only (the
   glass core paints); `+16 panel_size()` — `RAX = cols | rows << 32` of
   the app panel (45 | 86 << 32 here); `+24 ticks_ms()`; `+32 fill(row,
   col, rows, cols, colour)` — `RDI, RSI, RDX, RCX, R8`; colour 0 the
   background, 1 the foreground block, anything else the background;
   clipped to the panel. Calling rules as Stage 5's (arguments `RDI, RSI,
   RDX, RCX, R8`; the service preserves `RBX, RBP, RSP, R12–R15`). An app
   touches nothing else — no ports but its own request's, no framebuffer,
   no keyboard ports, no interrupts, no page tables. There is no
   `poll_key`: keys arrive by callback.
10. **The kind `0x02` frame** (deviation 1; GLASS.md "The wire"): the grow
    request is Stage 5's byte for byte (`0x01` then the body). The
    response is a refusal (kind `0x00`, as Stage 5) or an **app**: `0`
    kind `0x02`; `1` ABI `2`; `2` source (0 generated, 1 germline); `3`
    zero; `4–7 u32 L` (1 to 1,048,576); `8–39` the name (1–32 bytes
    `0x20`–`0x7E`, NUL-padded); `40` installed (0 this ring); `41–43`
    zero; `44–95` four choices of 13 bytes — key (`0x20`–`0x7E`, or 0 for
    an empty slot) and a 12-byte label (`0x20`–`0x7E`, NUL-padded) — empty
    slots all zero; then the blob. `N = 96 + L`. A frame failing any of
    that, **or kind `0x01`** (ABI 1 has no callbacks), draws `bad component
    frame` and counts an error. The 600 s deadline stands. The stream is
    received at region + 28; the blob at +128.
11. **What the screen does around an app** (GLASS.md "Running an app"). On
    a valid app frame: the name and choices are copied out of the header,
    the app panel surface is cleared, `mode = running`, `focus = app`, the
    choices row rewritten, the strip's name set, and `init` is called with
    the table; `grows_generated` or `grows_served` counts by `source`. The
    main loop while an app runs **never sleeps**: each pass drains the
    ring — a key with focus on the app goes to `key` (Esc and Tab
    excepted), with focus on the prompt takes Stage 5's path (a note, `?`,
    `!`); **Esc** (either focus) calls `exit`, clears the app panel,
    restores mode `prompt`, the choices row and focus, and a fresh prompt
    only if the cursor is mid-line — the conversation is untouched;
    **Tab** toggles focus and rewrites the choices row; then, if at least
    10 ms have passed since the previous `step` began, `step` is called
    and timed (`steps`, `step_last`, `step_worst`); then `pause`. A `?`
    with focus on the prompt asks as before (mode `asking`; `step` pauses
    for the wait — deviation 7); a `!` closes the running app (`exit`, the
    panel cleared) and then requests as before (mode `growing`). With no
    app, the loop is Stage 5's `sti; hlt` idiom. Every console error line
    increments `errors`; every Enter stamps `tt_last`/`tt_worst` when the
    prompt returns.
12. **The rehearsal, nine criteria** (`broker/twin.py`; GLASS.md "The
    rehearsal"), judged in this order, the first that fires naming the
    failure: **`the twin did not boot`** — no `S6: keyboard ready` within
    60 s, or not exactly sixteen `S6:` lines; **`the app was not
    delivered`** — the listener never saw the request or could not send;
    **`the twin reported an error`** — any `ERR:` in the serial capture
    (the `fault` blob dies here: `ud2` in `init` → `ERR: exception 6`);
    **`the app did not run`** — the obs page read through `xp` after
    delivery does not say `mode = running`, the delivered name, and
    `steps ≥ 1`; **`the app drew nothing`** — the app panel's region of
    screendump B is pure background; **`the app missed its budget`** —
    `step_worst` in the obs page exceeds 50 ms (`hog` dies here);
    **`the app drew outside its panel`** — the conversation and choices
    surfaces read through `xp` do not match their regions of screendump B
    pixel for pixel, cursor included (`escapee` dies here; deviation 5);
    **`no live prompt after esc`** — the row `> ! rehearsal` is not on the
    conversation panel in screendump C, or the obs page does not say `mode
    = prompt`, or the notebook does not parse to exactly `["after"]`, or
    the echo after ready is not exactly `! rehearsal\r\nafter\r\n`;
    **`the twin timed out`** — over 90 s. **Composable before it freezes
    (A2):** `twin.rehearse(blob, name, choices, image, workdir, port,
    extra_args=(), lines=16, after=None)` — `extra_args` are QEMU
    arguments appended to its command line (ring 6b adds the home image
    drive), `lines` is the number of `S6:` lines the first criterion
    demands (16 now, 17 at 6b, 18 at 6c), and `after`, when given, is a
    callable `after(driver, xp)` receiving the monitor driver (type,
    screendump, tell) and the `xp` reader, run **after the nine criteria
    have all passed** and returning a list of failure phrases (6b runs the
    plan's tests through it; an empty list passes). The nine criteria and
    their order stay exactly as above; with the defaults the behaviour is
    byte-identical to this plan. The twin: a one-shot listener on 9998, a
    headless `-smp 2` boot of a **private copy** of the image with
    a fresh notebook, **the VGA device with the EDID**, the cage with the
    guestfwd to 9998, monitor on stdio, serial to a file, all under
    `stage6/out/rehearsal/`; wait for ready; type `! rehearsal`; the
    listener answers with the candidate's app frame (name and choices from
    the caller) and closes; wait for delivery (30 s), 3 s more; `xp` the
    obs page and the conversation and choices surfaces (`xp /512xg` and
    `xp /<n>xb`, parsed from the monitor's echo); screendump B; Esc; 2 s;
    `after` Enter; 2 s; `xp` the obs page; screendump C; quit. The log
    holds the verdicts, the sixteen lines, any `ERR:`, the obs numbers and
    the timing; `stage6/out/rehearsal/` is scratch, wiped per run.
13. **The germline**: the key is the first 16 hex digits of SHA-256 over
    `<normalised>|abi2|qemu-q35-ovmf` — so nothing cached at Stage 5 is
    ever served to a Stage 6 guest; the directory holds `component.bin`,
    `provenance.json` (Stage 5's fields with `abi: 2`, plus `name` and
    `choices`) and `rehearsal.log`. `glass.py` reuses
    `germline.germline_lookup` (the hash check) and writes its own
    provenance (`germline_write` is Stage 5's and writes `abi: 1`).
    Serving from the germline delivers with `source = 1`.
14. **The mock's table** (`glass.py --mock`, frozen): `test app` → the
    bytes of `stage6/app.bin`, name `test app`, choices `a alpha`, `b
    beta`; `big` → the same padded with zeros to exactly 1,048,576 bytes,
    name `big`, the same choices; `fault` → the 18 bytes of a header whose
    four offsets are all 16, then `0f 0b` (`ud2` in `init`), name `fault`;
    `hog` → `stage6/hog.bin`, name `hog`; `escapee` → `stage6/escapee.bin`,
    name `escapee`; `hold` → 8 s, then the refusal `mock: held` (deviation
    4); anything else → `mock: no canned component for: <body>`. Every
    table lookup is one generation call; `hold` and the unknown body count
    too.
15. **The fixtures**, hand-written NASM, ABI 2, each under 1 KB, source and
    binary both committed and frozen at item 8 (the `.bin` gitignore
    exceptions as the font's), the checker assembling each source to
    `stage6/out/` and demanding the committed bytes. **`stage6/app.asm`**
    (`test app`): `init` keeps the table, draws at panel row 1 column 2
    `glass test app`, row 3 column 2 `panel <cols>x<rows>` from
    `panel_size`, row 7 column 2 `key: -`, row 9 column 2 `esc exits  tab
    prompt`, and `fill(11, 2, 1, 5, 1)` — five foreground blocks; `step`
    on its first call draws row 5 column 2 `ticks ok` if `ticks_ms` has
    advanced since `init` (`ticks stuck` otherwise), then nothing; `key`
    redraws row 7 as `key: <ch>` for a printable; `exit` returns. The known
    picture test 3 demands. **`stage6/hog.asm`**: `init` draws `hog` at row
    1 column 2; `step` spins on `ticks_ms` for 200 ms and returns. **
    `stage6/escapee.asm`**: `init` draws `escapee` at row 1 column 2, then
    finds the framebuffer the way a grown app could — a PCI scan for class
    `0x0300`, BAR0 — takes the screen width as twice the panel's columns
    times 16 (the stride equals the width on this device) and paints one
    16x16 foreground block at screen row 7, column 3 — inside the
    conversation panel; `step` returns.
16. **The broker** — `broker/glass.py`, item 3, frozen at item 8: standard
    library only; imports `HOST`, `DEFAULT_PORT`, `read_frame`, `frame`,
    `to_wire`, `mock_answer`, `RecordingSocket`, `Recorder`, `log` from the
    frozen `broker.py`, and `is_grow`, `refusal_frame`, `normalise`,
    `germline_lookup`, `record_grow`, `handle`, `serve` from the frozen
    `germline.py`; adds GLASS.md's Python verbatim (`app_frame`,
    `parse_response` for kinds 0 and 2, `germline_key` with `abi2`, the
    obs-page parser and the strip/choices renderers), its own `Glazier`
    (the pipeline of Stage 5's `Grower` — generate, rehearse, cache,
    deliver, `--tries 2` with the failure and the twin's `ERR:` fed back,
    the running call counter — and the record's fields with `name`, `abi:
    2`), **built to be subclassed, not forked (A2):** the constructor takes
    the rehearse callable as an argument defaulting to `twin.rehearse`,
    and its record writer and provenance writer (`glass.germline_write`)
    each accept a dictionary of extra fields merged into the JSON, so
    6b's install pipeline subclasses `Glazier` and passes its own
    rehearsal and fields; the mock table, and `main` (`--mock`,
    `--port`, `--record`, `--timeout`, `--germline`, `--image` default
    `stage6/out/esp.img`, `--workdir` default `stage6/out/rehearsal`,
    `--rehearsal-port` 9998, `--tries`, `--model`). Questions ride
    Stage 4's path unchanged. `broker/twin.py`, frozen: decision 12 whole,
    reusing `rehearse.Listener` (subclassed to reply with the app frame),
    `rehearse.cage_netdev`, and the picture and notebook helpers; its own
    `qemu_argv` with the VGA flags; an `xp` reader that sends the command
    to the monitor and parses the hex lines that follow.
17. **The real backend** — `claude_backend.grow()` gains an ABI 2 mode
    (`abi=2`, the default from `glass.py`), **not frozen**: the brief lifts
    GLASS.md's "An app is four callbacks" and "The service table" sections
    verbatim and asks for NASM source for a flat binary whose first 16
    bytes are the four offsets; the name delivered is the request body
    cut to 32 bytes; an optional `; choice <key> <label>` comment line in
    the returned source (up to four) declares choices; assembly rounds and
    the refusal path as Stage 5's. Never run by the gate.
18. **The freeze boundary** (item 8): `stage6/test.sh`,
    `stage6/checkglass.py`, `stage6/GLASS.md`, `stage6/app.asm`,
    `stage6/app.bin`, `stage6/hog.asm`, `stage6/hog.bin`,
    `stage6/escapee.asm`, `stage6/escapee.bin`, `broker/glass.py`,
    `broker/twin.py`. Not frozen: `stage6/mkimage.sh`, `stage6/stage6.asm`,
    `broker/claude_backend.py`, `stage6/plan-6a.md`. Everything frozen
    before stands untouched.
19. **The harness** — `stage6/test.sh` (Stage 5's shape): refuses to run
    while anything listens on 9999 or 9998; the cage with
    **`mac=52:54:00:a1:06:01`**; **the display spelled once:** `-vga none
    -device VGA,edid=on,xres=1440,yres=1440` (and the `edid=off` variant
    for test 2); wipes `stage6/out/germline/` and `stage6/out/rehearsal/`;
    builds; test 1; test 2 (three boots); test 3 (`checkglass.py --glass 2`
    and `--glass 8`); test 4 (`--truth`); the cage and display
    self-assertions. **`stage6/checkglass.py`** on `checkgermline.py`'s
    driver (mock lifecycle, `drive` with steps, record waits, the font
    renderer, `check_screen` restricted to a region, the notebook parser),
    plus GLASS.md's parsers, an **`xp` step** that reads the obs page and
    named surfaces through the monitor mid-run, a cell reader (each cell
    matched against the 95 glyphs and the block) for the strip's numbers,
    key names for Tab (`tab`) and Esc, and the fixtures' self-check.
    - **Test 2** (`test.sh`): at `-smp 8` with the EDID: sixteen lines in
      order, `edid 1440x1440` and the gop line's `WxH` equal to it, console
      = W/16 x H/16, line 13's address ≡ 128 mod 4096, line 14 page-aligned,
      found = woken = 8, exit 124; at `-smp 8` with `edid=off`: sixteen
      lines, `edid none`, the gop area ≥ the EDID run's area; at `-smp 1`
      (`checkglass.py --one-core`, the monitor on stdio, 30 s): an `ERR:
      the glass needs a second core` line, exactly fourteen `S6:` lines,
      no `glass core`, no `keyboard ready`, **and a screendump taken after
      the `ERR:` line holds that row rendered from the shared font** (A3)
      in the conversation panel's columns, two colours only.
    - **`--glass <smp>`** (test 3): mock up, germline wiped; fresh disk;
      boot; `before` ⏎; `! test app` ⏎, wait for the grow record (150 s —
      it rehearses), settle 3 s; `k`; settle; **screendump A**; Tab; `mid`
      ⏎; settle; Tab; `j`; settle; **screendump B**; Esc; settle 2 s; `? ping`
      ⏎, wait for the record; `after` ⏎; settle; **screendump C**; quit.
      Assert: the sixteen boot lines with the MAC; the echo after ready
      exactly `before\r\n! test app\r\nmid\r\n? ping\r\nafter\r\n` (`k`,
      Tab, `j`, Esc never reach the wire); the record: one grow whose raw
      bytes are GLASS.md's request frame, `source generated`,
      `generation_calls 1`, `rehearsals ["pass"]`, `answer_kind app`,
      `answer_sha256` = the checker's `app_frame(app.bin, "test app",
      choices, 0)`, then `ping` → `pong`; the germline: one entry, `abi 2`,
      the blob byte-identical, the provenance fields, a `rehearsal.log`
      with sixteen `S6:` lines and no `ERR:`; the notebook exactly
      `["before", "mid", "after"]`; **screen A**: the app panel holds the
      fixture's picture with `key: k` and `ticks ok` and the five blocks,
      every other app-panel cell blank; the choices row exactly `a alpha
      b beta   Esc exit   Tab prompt` (three spaces between items); the
      strip's mode field `running test app`; the conversation panel rows
      `> before`, `> ! test app`, then the prompt with the cursor; **screen
      B**: `key: j` in the panel, `> mid` and the prompt under `> ! test
      app`, the choices row the same as A; **screen C**: the app panel
      pure background, the choices row `? ask   ! grow`, mode `prompt`,
      the conversation `> before`, `> ! test app`, `> mid`, `> ? ping`,
      `pong`, `> after`, the prompt; two colours everywhere.
    - **`--truth`** (test 4, `-smp 8`): the argv assertions (the checker's
      own QEMU command and the twin's: the cage with the right port, the
      VGA flags, every drive under `stage6/out/`); mock up, germline
      wiped; boot; `! fault` ⏎ (wait, 240 s); `! hog` ⏎ (wait, 240 s); `!
      escapee` ⏎ (wait, 240 s); `! test app` ⏎ (wait, 150 s), settle 3 s;
      `k`, `e`, `y`; **`xp` obs page + all four surfaces, screendump A,
      `xp` obs page again**; sleep 1 s; **`xp` obs page (frames must have
      grown strictly), screendump A2**; Esc; `! test app` ⏎ (wait, 20 s —
      germline); Esc; `! big` ⏎ (wait, 150 s), settle 3 s, **screendump
      B**, Esc; `! hold` ⏎, sleep 3 s, **`xp` obs page, screendump H**
      (mode `growing`, the spinner cell), wait for the record (20 s); `?`
      ⏎; `?x` ⏎ (wait); `!` ⏎; `!x` ⏎ (wait); `last` ⏎; settle; **`xp` obs
      page + surfaces, screendump D, `xp` obs page**; quit. Assert: the
      boot lines; the echo exactly the twelve typed lines (`k e y`, the
      Escs never on the wire); the record in order: `fault` refused after
      `["fail: the twin reported an error"] * 2` (calls 2), `hog` refused
      `["fail: the app missed its budget"] * 2` (calls 4), `escapee`
      refused `["fail: the app drew outside its panel"] * 2` (calls 6),
      `test app` generated (7, `["pass"]`), `test app` germline (still 7,
      `[]`, `source` byte 1 in the frame hash), `big` generated (8, a frame
      of exactly 4 + 96 + 1,048,576 bytes), `hold` refused `mock: held`
      (9, `[]`), question `x`, `x` refused (10); the germline exactly two
      entries with provenance; the notebook `["last"]`; **screen A**: the
      fixture's picture with `key: y` (the last key) in the app panel; the
      strip rendered from the obs page read just before and just after the
      screendump agrees cell by cell — static fields equal, `up` and `fr`
      and the times between the two readings; the obs page's `keys`,
      `questions`, `errors`, `notes`, `grows`, `wire_conns` equal the
      counts the checker knows at that moment; every region outside the
      app panel matches its surface pixel for pixel; **A2**: `frames`
      strictly greater, the strip's `fr` field greater, the conversation
      panel unchanged; **B**: the 1 MB app's picture with `key: -`;
      **H**: mode `growing`, the choices row `? ask   ! grow`; **D**: mode
      `prompt`, the strip: `k` = every key the checker sent (including
      Enters, Escs, Tabs and the three app keys), `q 001`, `n 001`, `g
      002/001`, `err 007` (`nothing to ask`, `nothing to grow`, five
      refusals), the obs page agreeing; the conversation panel `> !
      fault`, `rehearsal failed: the twin reported an error`, `> ! hog`,
      `rehearsal failed: the app missed its budget`, `> ! escapee`,
      `rehearsal failed: the app drew outside its panel`, `> ! test app`,
      `> ! test app`, `> ! big`, `> ! hold`, `mock: held`, `> ?`, `nothing
      to ask`, `> ?x`, `mock: no canned answer for: x`, `> !`, `nothing to
      grow`, `> !x`, `mock: no canned component for: x`, `> last`, the
      prompt (wrapped rows judged as wrapped at the panel's width);
      two colours everywhere.
    The gate's cost: five boots of its own (three in test 2, one per test
    3 mode, one in test 4) plus ten rehearsal boots (two in test 3; in
    test 4 `fault` x2, `hog` x2, `escapee` x2, `test app`, `big`), about
    twelve minutes. Rehearsals run beside the gate's guest — two QEMUs, two
    ports, two `out/` directories, two images.
20. **The two commands for the oracle** (test 5), from the repo root:
    `python3 broker/glass.py` and
    ```
    qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
      -vga none -device VGA,edid=on,xres=1440,yres=1440 \
      -drive format=raw,file=stage6/out/esp.img \
      -drive format=raw,file=stage6/out/notes.img,if=virtio \
      -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
      -device virtio-net-pci,netdev=n0 -serial stdio
    ```
    He types `! make me a clock`; the strip says `growing` while Claude
    writes and the twin rehearses; the clock ticks in the app panel with
    `running make me a` on the strip; Tab; he types a note beside it and
    it journals; the strip's numbers move; Esc. His word closes the ring.
    The Stage 5 clock in `germline/` is an `abi1` entry: the `abi2` key
    differs, so the first request regenerates.
21. **The prose the hook will dislike.** The new frozen basenames
    (`GLASS.md`, `glass.py`, `twin.py`, `app.asm`, `app.bin`, `hog.asm`,
    `hog.bin`, `escapee.asm`, `escapee.bin`, `checkglass.py`) join the
    prose rule; commit messages go in by `-F` from a file written with the
    Write tool, as before.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are expected green at its commit**. Items
  0–8 commit with every ring 6a test failing **by design** — there is no
  `stage6.asm` yet. From item 9 the stated tests must be green before the
  commit.
- **`./stage0/test.sh` … `./stage5/test.sh` stay green throughout** — run
  as regressions before every commit (Stage 4's and Stage 5's need 9999
  free, Stage 5's 9998 too; no two gates run at once).
- `HANDOVER.md` is updated as we go, with a final pass at item 14.
- Every new fault class earns a CLAUDE.md gotcha line and a regression
  check; the second time a mistake is corrected its line goes in.
- Temporary probes are never committed, and never undone with `git checkout
  --`: copy aside, restore from the copy.
- **The scope guard** governs items 10–14: two honest attempts at any one
  obstacle — a real diagnosis from the serial log, the rehearsal log or the
  obs page, not a re-run — then stop, record the exact state in
  `HANDOVER.md`, commit that, and wait for Wajira. A frozen file that needs
  to change is never edited: the diff is written unapplied under
  `stage6/out/`, recorded, and the owner applies it.
- **Everything runs inside QEMU with the caged network and the VGA device.**
  The only disks are files under `stage6/out/` (the gate's, and the twin's
  under `stage6/out/rehearsal/`), created fresh by the harness or the
  broker. Both brokers bind only `127.0.0.1`. Nothing outside the repo is
  written, bar scratch files in the session temp directory. **No real
  Claude call is made by this session:** the mock is the only broker the
  gate ever talks to, `claude_backend.grow` is never run here, and test 5 is
  Wajira's.

---

# Part 1 — the wire, the fixtures, the broker and the twin, and the acceptance machinery, written before the code

## Item 0 — this plan, committed

Copy this file verbatim to `stage6/plan-6a.md` and commit it. The first act
after the gate opens, before any other file changes. In the same act,
delete `stage6/plan-6a.review.md` — Cowork's review copy, never to be
committed — and the probe artefacts under `stage5/out/probe/`.

*Expected at commit:* no ring 6a tests exist yet. Stages 0–5 green.

## Item 1 — `stage6/GLASS.md`: the glass, byte-exact

Decisions 2–14 as one document, the GERMLINE.md precedent: implemented by
the assembler and the fixtures, parsed by the broker, the twin and the
checker. Sections: what it adds to GERMLINE.md and UMBILICAL.md and what it
leaves alone (both frozen, referenced not restated); the screen — the mode
policy, the EDID read, the four regions and their formulas, the sixteen
lines; surfaces — cells, dirty rows, the protocol, the cursor; the glass
core — the loop, the cadence, the frame and photon measurements; the obs
page — the offset table; the obs strip — both rows to the character, the
number formats, and the two honesty lines of A4 (what `ph` measures; that
grows served comes from the broker's `source` byte, everything else is the
guest's own count); the choices row — the three texts, the first three
declared choices at most (A1); an app is four callbacks
— the blob header, the calling rules, the focus rule, Esc and Tab, the step
budget and pacing; the service table; the wire — the kind `0x02` frame,
offsets and ranges in a table, `bad component frame` for kind `0x01`, the
region and line 13; running an app — what the screen does; the console's
lines and the errors counter; the rehearsal — the twin's script and the
nine phrases; the germline with `abi2`; the mock's table with `hold`; the
record's fields; worked-example bytes (the request for `! test app`, an app
frame for the four-byte blob with a 16-byte header — `N = 96 + 20`, the
largest legal frame ending at region + `0x100080`, the strip rows for a
given obs page); and **"Parsing it cold, in Python"** — `app_frame(blob,
name, choices, source)`, `parse_response(content)` (kind 0 → `("refusal",
text)`, kind 2 → `("app", blob, name, choices, source)`, kind 1 →
`ValueError("ABI 1 has no callbacks")`), `normalise`, `germline_key`
(`abi2`), `regions(cols, rows)`, `parse_obs(page)`, `strip_rows(obs)`,
`choices_row(mode, focus, choices)`, `fmt_ms(ticks, tsc_per_ms)` — the
exact functions the three Python readers import.

*Expected at commit:* no ring 6a tests yet. Stages 0–5 green.

## Item 2 — the fixtures: `stage6/app.asm`, `stage6/hog.asm`, `stage6/escapee.asm` and their binaries

Decision 15: three hand-written ABI 2 blobs, `bits 64`, `default rel`, the
16-byte offset header first, the table kept in a data qword inside the
blob (the region is RAM), a `put_dec` for `panel <cols>x<rows>`. Assembled
with `nasm -f bin stage6/<name>.asm -o stage6/<name>.bin`; `.gitignore`
gains the three `!stage6/<name>.bin` exceptions; each binary's SHA-256 and
size go into the commit message and into GLASS.md's worked examples.

Proven on the host alone: a scratch script under the session temp
directory checks each blob's four offsets are below its length, that
`app.bin` contains its five strings, and that
`parse_response(app_frame(blob, name, choices, 0))` round-trips for each.
(The blobs first *run* at item 13, in the guest; that is the point of
writing them now.)

*Expected at commit:* no ring 6a tests yet. Stages 0–5 green.

## Item 3 — `broker/glass.py`, `broker/twin.py`, and `claude_backend.grow`'s ABI 2 mode

Decisions 12, 13, 14, 16 and 17 in code. `glass.py`: the imports from the
two frozen brokers; GLASS.md's Python; `Glazier` (the pipeline; the
rehearse callable a constructor argument defaulting to `twin.rehearse`;
the record and provenance writers taking extra fields — A2); the mock
table (the fixtures read at call time, `hold`'s sleep); the record fields;
`main`. `twin.py`: `rehearse(blob, name, choices, image, workdir, port,
extra_args=(), lines=16, after=None)` (A2), the VGA flags in `qemu_argv`
with `extra_args` appended, the `lines`-line ready wait, the app-frame
`Listener`, the monitor driver with the `xp` reader, the two screendumps,
the nine criteria in order, then `after` if given, the log. `claude_backend.py`
gains the ABI 2 brief and the `; choice` parse beside the untouched Stage
5 path.

Proven on the host alone, no guest, no Claude call, with a scratch client
under the session temp directory against `--mock` on a throwaway port and
`--image` pointing at a file that does not exist yet: `ping` answers `pong`
through the imported frame code; `x` is refused `mock: no canned component
for: x` with `generation_calls 1`; `test app` runs the pipeline into the
twin, which fails with `the twin did not boot` (no image), twice, and the
guest-side answer is `rehearsal failed: the twin did not boot`; a
`Glazier` built with a stub rehearse callable that always passes, and
extra record and provenance fields, delivers the frame and writes the
fields (A2's seams exercised without a guest); `hold`
takes 8 s and refuses `mock: held`; a kind-0x01 frame fed to
`parse_response` raises; the germline directory stays empty; `strip_rows`
on a hand-built obs page gives the two documented rows.

*Expected at commit:* no ring 6a tests yet. Stages 0–5 green. No Claude
call.

## Item 4 — `stage6/mkimage.sh`, the `stage6/test.sh` harness, acceptance test 1

`mkimage.sh` (not frozen): Stage 5's, retargeted. `test.sh` (frozen from
item 8): decision 19's shape — the port refusals, the cage with the new
MAC, the display flags spelled once, the wipes, the self-assertions on the
cage and the display. **Test 1** — the artefact, Stage 5's criteria on
Stage 6's files.

*Expected at commit:* every ring 6a test fails — there is no `stage6.asm`.
The non-zero exit quoted in the commit message.

## Item 5 — acceptance test 2 (serial: sixteen lines, the EDID, the highest, one core)

Decision 19's test 2: two `serial_check` runs in `test.sh` — `8 on`, `8
off` — each under `timeout -k 5 60`, exit 124 expected; the sixteen `S6:`
messages in order with the EDID and geometry cross-checks, line 13's
alignment, line 14's page alignment, line 15's decimal id; the `edid none`
run's area rule. The `-smp 1` run is `stage6/checkglass.py --one-core`,
created here with the driver it needs: the monitor on stdio, a 30 s wait
for the `ERR:` line, a screendump, the fourteen-line and no-glass checks,
and the `ERR:` row rendered from the shared font found in the conversation
panel's columns of the screendump (A3). Whole capture printed on failure.

*Expected at commit:* tests 1–2 fail.

## Item 6 — `stage6/checkglass.py --glass` (test 3)

Decision 19's first mode, beside item 5's `--one-core`:
`checkgermline.py`'s driver carried over with the
sixteen-line pattern table, GLASS.md's parsers, the fixtures' self-check,
`check_region` (a `check_screen` bounded to a region's rows and columns),
`check_app_panel` (the fixture's picture and every other panel cell
blank), the choices-row and mode-field checks, Tab's key name, the three
screendumps and the assertions of decision 19. `test.sh` gains **Test 3**:
`--glass 2` and `--glass 8`, both must pass.

*Expected at commit:* tests 1–3 fail.

## Item 7 — `checkglass.py --truth` (test 4)

Decision 19's second mode: the argv assertions for the checker's and the
twin's QEMU lines (cage, port, display, drives); the `xp` step and the obs
and surface parsers; the strip check — the two rows rendered from the obs
page read before and after a screendump, static fields exact, moving
fields bracketed; the cell reader; the surface-versus-screen check; the
long scripted run; the record judged entry by entry with the call sequence
2 / 4 / 6 / 7 / 7 / 8 / 9 / 10; the germline's two entries; the notebook;
the screens. `test.sh` gains **Test 4**. All four exist and all fail; the
output goes in the commit message.

*Expected at commit:* tests 1–4 fail.

## Item 8 — freeze the ring 6a acceptance machinery

`PROTECTED` grows the eleven paths of decision 18, and the hook's own
comment says why each is a criterion and why `mkimage.sh`, `stage6.asm`,
`claude_backend.py` and `plan-6a.md` are not. `payloads.py` gains the
Stage 6 group: the mutation battery on each new path (`freeze_cases`), the
`-o` side door on each new binary, the allowances — running the gate and
the checker, `python3 broker/glass.py --mock …`, `python3 broker/glass.py`,
`python3 broker/twin.py stage6/app.bin`, the gate's and the twin's QEMU
lines with the VGA flags and drives under `stage6/out/` and
`stage6/out/rehearsal/`, `cat stage6/GLASS.md`, `nasm -f bin stage6/app.asm
-o stage6/out/app.check.bin`, every operation on `stage6/mkimage.sh`,
`stage6/stage6.asm` and `broker/claude_backend.py`, `rm -rf
stage6/out/germline stage6/out/rehearsal`, `write("stage7/test.sh")` (the
"later stage" case moves on) — and is re-run whole: every earlier case
judged as before, 0 wrong. Immediacy demonstrated live with one denied
call.

*Expected at commit:* tests 1–4 still fail; the payload table 0 wrong.

---

*Everything above is written before any implementation code exists.
Everything below is the code.*

---

# Part 2 — the implementation, in the spec's order

## Item 9 — `stage6/stage6.asm`: Stage 5's proven body, `S5` becomes `S6`

Start from `stage5/stage5.asm` whole — nothing removed. Every `S5:` becomes
`S6:`; the header comment is rewritten; the font path stays
`stage2/font8x8.bin`. `stage5/stage5.asm` is untouched.

*Green at commit:* **test 1.** Tests 2–4 red. Stages 0–5 green.

## Item 10 — the EDID and the mode policy, the region, the stamps, Tab

Decisions 2, 10 (the region) and 6 (the stamp ring): `edid_read` before
the mode loop and line 2; the preferred mode remembered in the loop and
taken after it; `COMP_REGION_SIZE 0x100080`, `COMP_HDR 96`, `COMP_BLOB_OFF
128`, line 13 at +128; `kbd_stamps` beside `kbd_ring`, the handler stamping
`rdtsc`, `kbd_next` leaving `key_stamp`; scancode `0x0F` → `9` in both
tables, ignored at the prompt. The old loader keeps running kind `0x01`
frames this item only (it dies at item 13).

Verified with a **temporary, uncommitted probe** listing every mode and the
chosen one with the EDID on and off — then removed, copy-aside. Test 2
stays red (sixteen lines are not there yet), but the `edid` line and the
`gop` line must already agree.

*Green at commit:* test 1. Tests 2–4 red.

## Item 11 — the obs page and the counters, line 14

Decision 6 in the guest: `obs_page` in page-aligned BSS, filled at boot
(magic, `tsc_per_ms`, `tsc_boot`, cols, rows, the four descriptors);
`keys`, `keys_hw`, `errors`, `questions`, `requests`, `notes`, `disk_reqs`,
`disk_wait`, `wire_conns`, `bytes_in`, `bytes_out`, `wire_wait`, `tt_last`,
`tt_worst` incremented by `kbd_next`'s callers, `irq1_handler`, the console
error paths, `ask_question`, `grow_request`, `notebook_init`/`append`,
`disk_rw`, `tcp_connect`, `net_send`, `net_poll`, `umbilical_ask` and
`main_loop`'s Enter; line 14.

Verified with a **temporary, uncommitted probe**: `xp /512xg` on the printed
address after typing a known sequence shows the magic, `keys` equal to the
keys typed, `notes` equal to the notes journaled, `disk_reqs` at least the
notebook's reads and writes — then removed.

*Green at commit:* test 1. Tests 2–4 red.

## Item 12 — the surfaces, the glass core, the four regions, line 15

Decisions 3, 4, 5, 7 and 8: the four surfaces (cells and dirty rows in
BSS, 64 KB each, the descriptors in the obs page); the console re-targeted
— `console_init` measures the conversation panel from the regions,
`console_putc` writes cells and dirty rows only, `console_scroll` moves the
cells and dirties every row, `draw_cursor`/`erase_cursor` become the packed
cursor word and row dirties, `console_redraw` dirties every row, `fb_clear`
is not called by the BSP; `glass_main` on index 1 (the id, `glass_ready`,
the compositor, the strip formatter, the cadence, the frame and photon
timing); the BSP's start (`glass_go`, the 1 s wait, line 15, the `-smp 1`
`ERR:` and the mode-too-small `ERR:`, each preceded by one
`surface_render` of the conversation surface by the BSP — A3); the strip's
initial state; the choices row `? ask   ! grow`; the
mode word `prompt`, `asking`, `growing`. `draw_cell` now takes a screen
cell from a surface cell (glyph, `0x01` block, or background).

Verified with a **temporary, uncommitted probe** and by hand: at the
prompt the strip shows `up` counting and `fr` climbing, the choices row,
the boot log wrapped in the conversation panel, typed keys echoing there
with the cursor, `? ping` against the mock showing `asking` then `pong`;
`xp` on the obs page agrees with the strip; `-smp 1` halts with the named
line on serial and on the screen.

*Green at commit:* **tests 1 and 2** — sixteen lines with the EDID, the
highest without, the `-smp 1` error on serial and on screen. Tests 3–4 red.

## Item 13 — ABI 2: the frame, the loader, the services, focus

Decisions 9, 10, 11 and 14 in the guest: `app_valid` (the 96-byte header
checks, kind `0x01` → `bad component frame`); `run_app` (name, choices,
source counted, the panel cleared, mode and focus and the choices row,
`init`); the main loop with an app (the pass, the pacing, `key`, Esc →
`exit` and the restore, Tab, `!` closing first, `?` as before); the four
services (`svc_draw_text` panel-relative and clipped, `svc_panel_size`,
`ticks_ms`, `svc_fill`); `steps`/`step_last`/`step_worst`; the app name on
the strip; `grows_generated`/`grows_served`. Stage 5's `run_component`,
`svc_console_size`, `svc_poll_key` go, along with kind `0x01`.

Verified first by hand, `glass.py --mock` by hand: `! test app` rehearses,
passes, is cached, runs in its panel with `running test app` on the strip
and the choices row; `k` shows; Tab, a note journals beside it; Tab, `j`
shows; Esc restores the choices row and the conversation; a second `! test
app` comes from the germline with `g 001/001`; `! fault`, `! hog` and `!
escapee` are refused with their phrases and the twin's obs numbers in the
rehearsal log; `! big` streams the full `4 + 96 + 1,048,576` byte frame to
region + `0x100080` and runs; `! hold` shows `growing` for 8 s.

*Green at commit:* **all four automated tests** — tests 3 and 4 close here,
at `-smp 2` and `-smp 8`. Full `./stage6/test.sh` output in the commit
message. Stages 0–5 green.

## Item 14 — HANDOVER, gotchas, README, the two commands

- `HANDOVER.md` to the green-pending-oracle state: what was built, the
  regions and addresses on this build, tests 1–4 green with output, test
  5 pending Wajira, the two commands with the VGA flags, the note that the
  Stage 5 clock in `germline/` is an `abi1` entry regenerated for `abi2`
  on the first request, caveats carried forward (everything Stage 5
  carried; one app at a time; cooperative stepping with a budget but no
  preemption and no watchdog; `step` paused during a wire wait; a torn cell
  may last one frame; no timer interrupt; the choices row is text; the
  trials recorded for, not run; the glass core is the first AP, not chosen
  by topology until Stage 7).
- `CLAUDE.md` gotchas grown with whatever actually bit — candidates already
  measured: *QEMU's default VGA carries an EDID naming 1280x800, and OVMF
  puts the EDID's preferred mode first: the display flags on every QEMU
  command are load-bearing, and the EDID BAR's address moves with the
  device set — read it*; *two QEMUs on one image, again: every probe boots
  its own copy*.
- `README.md`'s running section gains ring 6a's two commands.
- `python3 .claude/hooks/payloads.py` re-run, 0 wrong.
- Print the two commands for Wajira.

*Green at commit:* all four automated tests, plus Stages 0–5.

---

## Verification

- **Automated:** `./stage6/test.sh` from the repo root — refuses to start
  if anything listens on 9999 or 9998; builds; tests 1–4 (serial at `-smp
  8` with and without the EDID and at `-smp 1`; the glass at `-smp 2` and
  `-smp 8` against the mock, each with one rehearsal; the truth run at
  `-smp 8` with eight rehearsals, the obs page read through the monitor,
  the strip rendered from it, every region checked against its surface).
  About twelve minutes. Exit 0 only if all pass. Run before every commit
  from item 9 on.
- **Regression:** Stages 0–5's `test.sh` green before every commit —
  `stage5/test.sh` in particular, since its files are untouched and its
  image is unaffected by the display flags this ring adds only to Stage 6's
  commands.
- **The hook:** `python3 .claude/hooks/payloads.py` at item 8 and item 14 —
  every case from every stage, 0 wrong; immediacy demonstrated live.
- **The probes:** items 3 (host-only), 10, 11, 12 and 13 each state their
  expected output; item 13's rehearsal verdicts are confirmed from the
  record file and the rehearsal logs on the host.
- **Manual (test 5):** Wajira, in two terminals at the repo root, the two
  commands of decision 20. He types `! make me a clock`; the strip says
  `growing` while Claude writes and the twin rehearses; the clock ticks in
  its panel; Tab; he types a note beside it; the strip's numbers move; Esc.
  His word closes the ring.

## Safety

Everything runs inside QEMU. Firmware, the standard VGA device, and exactly
two drives per guest, raw files under `stage6/out/` (the twin's under
`stage6/out/rehearsal/`), created by the harness or the broker; the
bodyguard is unchanged and still denies every other kind of disk before
the shell sees it. The network is slirp with `restrict=on` and one
`guestfwd` in every QEMU line, the twin's included; the brokers bind
`127.0.0.1` only. The automated gate talks only to the mock, never to
Claude, and refuses to run if anything else holds either port. A grown app
runs at ring 0 with the whole machine in reach — that is the thesis, and
the rehearsal in the twin is the mitigation the foundation prescribes; it
proves *safe* (boots, runs, keeps its budget, stays in its panel, faults
nothing, exits, the prompt lives), not *correct*. This session makes no
Claude call and never runs `claude_backend.grow`. Every existing frozen
file is untouched: `git diff --stat` against `5716576` on the `PROTECTED`
paths of Stages 0–5 is empty at every commit, and `./stage5/test.sh` is
green at the end of the ring.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| The EDID is not where the guest looks, or OVMF does not list its mode | measured before planning: BAR2 at runtime, the header checked, mode 0 is 1440x1440; `edid none` and the highest mode are the fallback, also measured |
| The glass core and the BSP race on a surface | one writer per cell buffer, one writer per dirty byte direction, `xchg` on the consumer side, the cursor a single dword; a torn row lasts one frame by design |
| The compositor cannot keep 60 Hz | a full-frame copy measured at 3 ms; dirty rows only; the strip reports the worst frame honestly, so a slow frame is a number, not a mystery |
| The BSP paints after the glass starts | `draw_cell`, `draw_cursor`, `erase_cursor`, `fb_clear` are reachable only from `glass_main`; test 4's surface-versus-screen check would see a stray pixel |
| An app hangs in `step` on the real machine | the rehearsal's 50 ms budget from the obs page, and the 90 s bound; the no-watchdog case is a recorded caveat |
| The twin is bent to pass | `twin.py` frozen; `fault`, `hog` and `escapee` must each fail with their fixed phrase; the checker reads the rehearsal logs |
| The gate spends a token or reaches Claude | the double port refusal; the mock's table; `grow()` imported only outside `--mock`; the mock counts calls and the checker demands the counts |
| Two QEMUs collide | different ports, `out/` directories, MACs and images (the twin's private copy); the harness checks both ports free first |
| The strip's text is too wide for a smaller mode | drawn from column 0 and cut at the edge; the checker compares the first `cols` cells |
| The 1 MB frame overruns the region | `COMP_RX_MAX = 4 + 96 + 1 MB` ends exactly at +`0x100080`; test 4's `big` streams a frame of exactly the cap into the guest and runs it |
| A frozen Stage 5 file turns out to need a change | the scope guard: stop, write the diff unapplied under `stage6/out/`, record it, wait for the owner's hand |
| Ring 6b or 6c needs the frozen twin or broker to behave differently | A2: `twin.rehearse` takes extra QEMU arguments, the expected line count and a post-delivery hook; `Glazier` takes its rehearse callable and extra record and provenance fields — later rings subclass and pass, never edit |

---

## Amendments — Cowork's review, adopted before approval

**A1 — Hick, five items at most.** Decision 8 promised never more than
five items on the choices row, but four declared choices plus `Esc exit`
plus `Tab prompt` is six. While an app runs the row shows **at most the
first three declared choices**, then `Esc exit` and `Tab prompt`. The
frame header keeps its four slots; GLASS.md says the row shows the first
three. The test app declares two, so test 3's expected row is unchanged.
(Decision 8 and item 1 updated.)

**A2 — `broker/twin.py` and `Glazier` composable before they freeze**, so
rings 6b and 6c reuse them without editing a frozen file. `twin.rehearse`
takes, with ring 6a defaults: `extra_args` — QEMU arguments appended to
its command line (6b adds the home image drive); `lines` — the number of
`S6:` lines expected (16 now, 17 at 6b, 18 at 6c); and `after` — an
optional post-delivery hook, a callable receiving the monitor driver and
the `xp` reader and returning a list of failure phrases, run after the
nine criteria (6b runs the plan's tests through it). The nine criteria and
their order stay exactly as decision 12 says; the defaults give
byte-identical behaviour to the plan as written. `Glazier` takes the
rehearse callable as a constructor argument defaulting to `twin.rehearse`,
and its record and provenance writers accept extra fields, so 6b's install
pipeline subclasses instead of forking. (Decisions 12 and 16, item 3 and
the risk table updated.)

**A3 — the error paths show their line.** At the `-smp 1` error path and
the mode-too-small error path, before halting, the BSP renders the
conversation surface to the framebuffer once, so the `ERR:` line is on
screen as well as on serial. The one-owner rule holds: no glass exists on
those paths and the BSP halts immediately after. Test 2's `-smp 1` run
adds one assertion: the screendump holds the `ERR:` row rendered from the
shared font — which puts that run under the checker (`--one-core`, created
at item 5) so it has a monitor to screendump with. (Decisions 1, 3, 5 and
19, items 5, 6 and 12 updated.)

**A4 — two honesty lines in GLASS.md.** The `ph` field is defined
precisely: the time from the keyboard interrupt stamping a key to the end
of the frame copy that painted its echo into the framebuffer, not
literally a photon. And GLASS.md states that grows served is the one strip
number the guest takes from the broker's `source` byte rather than
measures itself; everything else on the strip is counted by the guest.
(Decision 7 and item 1 updated.)

**Also, at item 0:** `stage6/plan-6a.review.md` — Cowork's review copy —
is deleted alongside the probe artefacts and never committed.
