# Stage 6, ring 6c — the pointer · implementation plan

**To be committed verbatim as `stage6/plan-6c.md`. Produced in plan mode, per
the foundation's build loop. Nothing below is implemented until Wajira
approves this document by writing the approval marker from his own terminal;
the ExitPlanMode hook holds the gate until then. Plan mode allows this
session to write only this one file and forbids commits, so — exactly as
rings 6a and 6b did — the copy to `stage6/plan-6c.md` and its commit are the
first act after the gate opens, item 0 below, before any other file is
touched. Cowork's amendments while the gate holds are adopted here as
numbered amendments (A1, A2, …) at the end of the document.**

## Context

Rings 6a (the glass) and 6b (the store of plans) are closed: on 3 September
2026 the calculator was installed from its plan by the real backend,
rehearsed against the plan's five tests, kept on the home image and launched
after a reboot with no broker. This is **ring 6c, the pointer** — the last
ring of Stage 6. The spec's reason for it: the choices row has targets on an
edge, Fitts's law is about pointing at targets, and the N-of-1 trials the
owner wants are pointing tasks; so the design demands a pointer at this ring
and not earlier. The done-when: **a click on a choices-row target does what
its key does, and pointer input-to-photon is a number on the obs strip.**
Test 5 is Wajira's: he clicks his way through the choices row and into the
calculator with the real broker, and his word closes the ring and the stage.

What this ring builds, from `stage6/spec.md` and the kickoff: the PS/2 mouse
on the i8042's auxiliary port, IRQ12, three-byte packets, interrupt-driven
into a ring of its own — the first time the i8042 is configured rather than
inherited (the controller command byte written to enable the auxiliary port
and its interrupt, the cascade IRQ2 and IRQ12 unmasked, every other line
masked, EOI to both chips, the mouse reset, identified and told to report);
`S6: mouse ready` on serial; the cursor — a one-cell arrow — drawn by the
glass core as the last thing in every frame from a position the interrupt
handler keeps in the obs page, the cell under it repainted from its surface
when the cursor leaves; pointer input-to-photon on the strip, stamped at the
interrupt and measured at the end of the frame copy that painted the cursor's
new cell; a click on a choices-row target doing what its key does (`? ask`
and `! grow` at the prompt, an installed app's `! <name>`, an app's declared
choices, `Esc exit`, `Tab prompt`, `Tab app`; a click on the gaps doing
nothing); a click in the app panel calling a new ABI 2 callback
`point(row, col, button)`, the ABI version staying 2 with the callback table
one entry longer, every existing app (the calculator on the home image
included) clicked on harmlessly; `stage6/GLASS.md` extended by a new frozen
section appended by the owner's own hand, its 6a and 6b text byte for byte
as it is; a new fixture, a new broker module `broker/pointer.py` that
imports and subclasses without editing; acceptance tests 1–4 written red
before any code and frozen with the payload table at 0 wrong. **The owner's
decisions, already made:** this ring is implemented on **Fable 5.1 at high
effort** (recorded in `HANDOVER.md` at item 0); the windowed run stays
1920x1080 and the 6c gate and twin run at 1920x1080 with two disks, exactly
ring 6b's shape; ring 6a's frozen gate (1440x1440, one disk) and ring 6b's
frozen gate must still pass on the same binary; GLASS.md's new section goes
in by the owner's hand.

The standing orders: the automated gate talks only to the mock, spends no
token and needs no internet; the real `claude -p` backend is exercised only
by the owner at test 5; **the cage, the storage bodyguard and every frozen
file stand** — every path in `PROTECTED` and every earlier stage's files
stay byte for byte, and `./stage6/test.sh`, `./stage6/test-6b.sh` and
Stages 0–5 must pass at the end of the ring. If a frozen file needs to
change, the session stops at the scope guard, writes the diff unapplied under
`stage6/out/`, records it in `HANDOVER.md` and says so. New broker code goes
in `broker/pointer.py`, importing `glass.py`, `twin.py` and `plans.py`
without editing them, subclassing `Installer`, passing what it needs through
the seams that exist (`twin.VGA_ARGS`, `extra_args`, `lines`, `after`); a
missing seam is a scope-guard stop. One commit per numbered item; tests red
before the code they judge; tests green before every commit that should pass
them; `HANDOVER.md` updated as we go; the second correction of a mistake goes
into CLAUDE.md's gotchas; **every number in a frozen test is written from a
run in this session, never from arithmetic** (ring 6b item 10b).

The plan is **evaluation-first**. Items 1–7 write the GLASS.md section, the
fixture, the broker module and the acceptance machinery so that tests 1–4
exist and fail before a single new instruction of `stage6.asm` is written.
Item 8 freezes them. Items 9–12 grow the guest and the gate closes at item
12: test 1 goes green at item 9, test 2 at item 10, test 4 at item 11 and
test 3 at item 12 (A1). Item 13 is the handover. Test 5 is Wajira's.

### Environment, measured in this session before planning

No new packages: NASM 3.01, QEMU 10.2.1, Python 3.14, OVMF, mtools, OpenBSD
netcat, the `claude` CLI — verified on the rebuilt mlrig; nothing installed.
Every probe booted a **private copy** under `stage6/out/probe6c/`
(gitignored, removed at item 0); no Claude call was made; nothing frozen was
touched; the working tree was clean at `ab7b331` throughout.

| Fact | Measured how |
|---|---|
| **QEMU offers no honest way to keep the keyboard and lose the auxiliary device.** `-device i8042,help` lists `kbd-irq` (default 1), `mouse-irq` (default 12), `kbd-throttle`, `extended-state` and the two child devices `ps2kbd` and `ps2mouse` — no property removes the mouse. `-machine q35,help` has only `i8042=<bool>`, which removes the whole controller, keyboard included, so `sendkey` — every gate's typing path — would die with it. The other pointing devices (`usb-mouse`, `usb-tablet`, `virtio-mouse-pci`, `vmmouse`) are not the PS/2 path and are not used by design | `qemu-system-x86_64 -device i8042,help`, `-machine q35,help`, `-device help` |
| **One monitor `mouse_move` is one three-byte packet while both deltas fit in a signed byte, and splits above 127 counts per axis, both axes drained together:** `mouse_move 10 20` → `28 0a ec`; `mouse_move -5 -7` → `18 fb 07`; `mouse_move 200 0` → `08 7f 00` then `08 49 00` (127 + 73); `mouse_move 0 300` → three packets, `28 00 81` twice then `28 00 d2` (−127, −127, −46); `mouse_move 130 -130` → `08 7f 7f` then `08 03 03`; `mouse_move 127 127` → one packet `28 7f 81`; `mouse_move 128 0` → `08 7f 00` then `08 01 00`. **`dy` arrives negated:** the monitor's positive `dy` (down the screen) is a negative PS/2 `dy` (bit 5 of byte 0 set, the byte two's complement) — PS/2 counts up as positive. Byte 0 always has bit 3 set; bits 4 and 5 are the sign bits and agree with the bytes; QEMU never sets the overflow bits | a 512-byte BIOS boot-sector probe (`stage6/out/probe6c/mouse.img`) that configures the i8042, resets and enables the mouse and prints every byte from port 0x60 with the status byte over COM1; `mouse_move` and `mouse_button` fed through the monitor; the same run traced with `-trace ps2_mouse_send_packet`, whose lines (`x 10 y -20 bs 0x28`, `x 127 y 0`, `x 73 y 0`, …) agree byte for byte with what the guest read |
| **A `mouse_button` change with no move sends one packet:** `mouse_button 1` → `09 00 00`; `mouse_button 0` → `08 00 00`; `mouse_button 2` → `0a 00 00`; `mouse_button 4` → `0c 00 00`; `mouse_button 7` → `0f 00 00`. The monitor's mask is `1` left, `2` right, `4` middle, and lands in bits 0–2 of byte 0 in that order (PS/2's left, right, middle). A move with a button held carries the button: `mouse_button 1` then `mouse_move 3 4` → `29 03 fc` | the same probe |
| **No unsolicited packet follows the enable, and no fake event exists on this path:** between `P: watching` (after the `F4` ACK) and the first `mouse_move` nothing arrived; twenty `mouse_move 1 0` commands 20 ms apart gave exactly twenty `08 01 00` packets; the `ps2_mouse_fake_event` trace never fired in either run | the probe's serial capture and the trace |
| **The reset and identify sequence:** `FF` → `FA AA 00` (ACK, self-test passed, ID 0 — a standard three-byte mouse); `F6` → `FA`; `F2` → `FA 00`; `F4` → `FA`. Every response arrived with status bit 5 set | the probe (`P: mouse cmd ff: Mfa Maa M00`, …) |
| **Status bit 5 tells the two devices apart:** every mouse byte came with status `0x3d` (bit 5 set), every keyboard byte with `0x1d` (bit 5 clear). With the auxiliary port and both interrupts enabled in the command byte, `sendkey a` still arrived as set-1 `1e` then `9e` — the keyboard's translation is untouched by enabling the mouse | the probe |
| **The command byte is firmware's, and OVMF's leaves the auxiliary port disabled:** SeaBIOS left `0x61` (translate, keyboard interrupt, aux port disabled); the probe's read-modify-write (set bits 0 and 1, clear bits 4 and 5, keep the rest) gave `0x43` and was read back so. **Under OVMF, on the current ring 6b image,** the firmware wrote `0xAD 0xA7 0xAA` then `0x60` with data **`0x67`** — translate on (`ps2_keyboard_set_translation mode 1`), system flag, keyboard interrupt, **aux interrupt enabled, aux port disabled (bit 5 set)** — and **never wrote a byte to the mouse** (no `ps2_write_mouse`; the keyboard got `F4`, `AB`, `FF`, `F0 02`, `F4`, `ED 00`). So today's guest, which masks the slave PIC entirely, never sees a packet, and a `mouse_move` on today's image queues nothing: `mouse_move 10 20`, `mouse_move 200 0`, `mouse_button 1`, `mouse_button 0` produced no `ps2_mouse_send_packet` line, the seventeen `S6:` lines stood, and `sendkey h`, `sendkey i` echoed `hi` exactly | the probe under SeaBIOS; the committed ring 6b image booted under OVMF with `-trace pckbd_kbd_write_command -trace pckbd_kbd_write_data -trace ps2_write_mouse -trace ps2_keyboard_set_translation -trace ps2_mouse_send_packet -trace ps2_mouse_fake_event` at 1920x1080 with two disks, driven through the monitor |
| **No blob that exists carries the proposed magic `POINTER2` at offset 16:** `stage6/app.bin` (608 bytes, offsets 16/252/369/418, bytes 16–27 `53 55 41 54 41 55 41 56 …` — `push rbx` and friends), `echo.bin` (121), `liar.bin` (129), `hog.bin` (104), `escapee.bin` (214); the gate's germline entries `bf5abcfb7651cc3b` and `d5c58d1ae943e1e6`; the machine's own `germline/` entries `0bf1f6c9165145ea` (the calculator, 617 bytes), `b14054b365ac9158`, `b754543ef4c77f4d`, `dc94314e1c4c5e95` (the clock); `stage5/component.bin`; and every current and previous build parsed out of `stage6/out/home.oracle.img`, `home.img` and `home.after-a.img` (echo 121 and 4096, calculator 617). Every blob's byte 16 begins code; none begins `P` `O` `I` `N` `T` `E` `R` `2` | a read-only scan with HOME.md's `parse_home` and `blob_of` |
| **What the frozen checks read on the strip, the choices row and the conversation** — quoted under deviation 4 below: `check_strip` reads rows 0 and 1 of the strip region whole (`read_cells(shot, geometry, strip, 0).rstrip()`) and compares row 1 to `strip_rows()` exactly and row 0 field by field; `check_choices` reads row 0 of the choices region against the row text and **row 1 against `""`** (blank across every column); `check_mode_field` reads strip row 1 columns 0–17; `check_surfaces` compares the choices, conversation and app regions cell for cell with their surfaces; `check_region_rows` reads the conversation rows around the expected block and scans every conversation row from column 0 for a repeat of the text; the twin's seventh criterion compares the conversation and choices regions cell for cell with their surfaces on screendump B and its eighth looks for one row on screendump C | read, `stage6/checkglass.py` lines 869–902 and 1155–1205, `stage6/checkplans.py` (`check_strip`, `check_surfaces` and `check_choices` imported and called at screens A, C, D, P, L, U, E and I), `broker/twin.py` `surface_mismatch` and `judge` |
| **No frozen check asserts the obs page is zero beyond `0x240`:** the twin reads `OBS_PAGE_BYTES = 0x240` (`xp /72xg`) and `parse_obs` unpacks named offsets only; both checkers read the page through `drv.read_obs`, the same 0x240 bytes; no `any(page[0x240:])` or the like exists anywhere | `grep -n "0x240\|read_obs" stage6/checkglass.py stage6/checkplans.py broker/twin.py broker/plans.py` |
| **The geometry this ring's tests will run at:** 1920x1080 is 120x67 cells; the conversation panel is rows 2–64, columns 0–59; the app panel rows 2–64, columns 60–119; the choices row is screen row 65 (pixels 1040–1055), its second row 66; the strip rows 0–1 hold 87 of 120 columns, leaving **33 spare columns, 87–119**; at 1440x1440 (90x90) the same rows leave three. A frame slot is 16.67 ms; two are 33.3 ms. The screen's centre pixel (960, 540) is cell row 33, column 60 — the app panel's first column | `regions()` from the frozen `glass.py`; arithmetic on the mode, confirmed by ring 6b's serial logs (`console 120x67`) |
| **The current guest's shape around the work** — `pic_init` masks everything but IRQ1 (`0xFD` master, `0xFF` slave); gates exist only at `0x21` (IRQ1) and `0x27` (spurious); `irq1_handler` reads 0x60 without looking at the status byte, stamps the TSC beside the scancode and keeps `keys_hw`; the main loop's wake test is `kbd_tail != kbd_head` before `sti; hlt`, and its key handling is inline from `.have` to a dozen `jmp main_loop`s; `finish_line` discards the keyboard ring after an answer; the serial tee draws every echoed byte into the conversation once the console is ready, so a line printed with `serial_puts` after `keyboard ready` would land in the conversation panel; `choices_update` builds the row text in `choices_line` from the same items the hit test needs; `svc_table` is 40 bytes in `.data`; the glass core's frame is `surf_render` ×4 then `strip_format`, with `echo_pending` snapshotted before the copies and measured after; `draw_cell` takes a cell byte and paints one 16x16 cell from the 8x8 font doubled, with `block_glyph` for `0x01` | read, `stage6/stage6.asm` |
| **The bodyguard and the freeze allow every planned command and deny the one that must be denied:** the 6c gate's QEMU line (three drives under `stage6/out/`, the 1080p device, MAC `52:54:00:a1:06:03`), `python3 stage6/checkpointer.py --point 2 / --serial 8`, `./stage6/test-6c.sh`, `python3 broker/pointer.py --mock …` and bare, `python3 broker/pointer.py --rehearse-app stage6/pointer.bin 'point app'`, `python3 broker/twin.py stage6/pointer.bin 'point app'`, `nasm -f bin stage6/pointer.asm -o stage6/pointer.bin` (until item 8 freezes it; `-o stage6/out/pointer.check.bin` after), `Write` on `stage6/out/glass-6c-section.md`, `stage6/pointer.asm`, `broker/pointer.py`, `stage6/checkpointer.py`, `stage6/test-6c.sh` and `stage6/plan-6c.md`; the read-only proofs of GLASS.md's old text — `head -n 777 stage6/GLASS.md \| sha256sum`, `git show HEAD:stage6/GLASS.md \| sha256sum`, `git diff --stat stage6/GLASS.md`, the `cmp` of the two — and `git add stage6/GLASS.md`; the probe's `rm -rf stage6/out/probe6c`; **denied:** `Write` on `stage6/GLASS.md` and `cat stage6/out/glass-6c-section.md >> stage6/GLASS.md` — the append is the owner's, by his own hand | the hook run directly on each payload (34 cases) |
| The ring 6b checker's driver, boot patterns, home parser, install checks and one-cell panel check, and the ring 6a checker's picture, record, germline and notebook helpers, are importable (`main` guarded in both); their `drive` step vocabularies are fixed and hold no mouse step, so the new checker spells its own `drive` with `mouse_move` and `mouse_button` steps and imports the rest | read |

---

## Deviations from the spec and the kickoff, for approval

Each argued from a measured fact or a frozen file. Everything else is the
spec as written. Deviations 1, 4 and 5 touch the two frozen gates'
expectations only in the sense of fitting around them; nothing frozen is
edited by any of them.

1. **`S6: mouse ready` is printed when the mouse first speaks, not at boot
   (trap 1).** The frozen `stage6/test.sh` demands *exactly* sixteen `S6:`
   lines with `keyboard ready` last; the frozen `stage6/test-6b.sh` exactly
   seventeen; the frozen `broker/glass.py` (`LINES = 16`) and
   `broker/plans.py` (`LINES = 17`) tell the frozen twin how many lines a
   boot has, and the frozen `checkglass.py` and `checkplans.py` count them
   again. Ring 6b kept 6a green with an honest hardware fact (a home line
   only when a second disk exists); no such fact exists here — measured
   above, QEMU cannot lose the auxiliary device without losing the
   keyboard, and the 6c gate is 6b's shape by the owner's decision. The
   options, with their costs:
   - **(a) the line at boot:** both frozen gates break, and so do both
     frozen brokers' twins (every 6b install would fail `the twin did not
     boot` at seventeen lines) and both frozen checkers — six frozen files
     (`stage6/test.sh`, `stage6/test-6b.sh`, `stage6/checkglass.py`,
     `stage6/checkplans.py`, `broker/glass.py`, `broker/plans.py`) amended
     by the owner's hand before the ring's code, each re-verified by Cowork,
     and the 6a and 6b gates would no longer prove "the same binary with one
     disk is ring 6a's, line for line". Rejected as the most expensive
     opening of the freeze in the project's history for one boot line.
   - **(b) the line when the mouse first speaks (recommended):** the boot
     processor prints `S6: mouse ready` exactly once, on serial only (a
     serial-only write, never the tee — the conversation is the human's),
     the first time its main loop sees the interrupt path's `packets`
     counter above zero. The frozen gates and the frozen twin never move the
     mouse, so they see exactly their sixteen or seventeen lines and an
     untouched echo after `keyboard ready`; the 6c gate's test 2 reads its
     lines after one `mouse_move` and demands eighteen with `mouse ready`
     eighteenth, and its echo checks allow that one line inside the stream.
     What the guest knows at boot — the mouse answered its reset with `FA
     AA 00` — is not lost: it is recorded in the obs page (`mouse_id`, 1 for
     a standard mouse, 0 when none answered) the moment it is known, and
     test 2 asserts it through `xp` before any packet. Honest in both
     directions: the page says the device was found at boot; the line says
     the device has spoken.
   - **(c) anything better:** none found. A line under another prefix
     (`S6c:`) would slip past the counts by trick, not by fact; a boot line
     conditional on a QEMU device the 6c gate adds would not be the PS/2
     path the spec chose; disabling the i8042 removes `sendkey`.
   **Recommendation: (b).** A caveat carried: a mouse that never moves
   never prints the line, so on Stage 7 metal the obs page is where to look
   for whether the mouse was found.
2. **The fifth callback is announced inside the blob, not in the frame or
   the home entry (trap 2).** The frozen `blob_offsets` reads four `u32`
   offsets and nothing more; the frozen wire rule requires byte 7 and bytes
   45–47 of the header zero; HOME.md's frozen parser requires the entry's
   padding zero; a home launch synthesises a kind 2 header. So the blob is
   self-describing: bytes 0–15 the four offsets as before; **bytes 16–23 the
   eight ASCII bytes `POINTER2`; bytes 24–27 a `u32` `point` offset.** The
   guest calls `point` only when `L ≥ 28`, the magic is present and the
   offset is below `L`; a blob with the magic and an offset at or beyond `L`
   (or below 28) is `bad component frame` — the same rule the four offsets
   obey — and `broker/pointer.py` refuses such a candidate before the twin.
   Measured above: no existing blob carries the magic, so every app that
   exists today is a four-callback app and is clicked on harmlessly. The
   frozen `parse_response` and the frozen twin accept the extended header
   unchanged (it is bytes of the blob to them).
3. **The spec's test 3 clicks in `test app`'s panel; the test app cannot
   have `point` (trap 6).** `stage6/app.asm`, `app.bin` and `glass.py`'s
   canned table are frozen. A new fixture, `stage6/pointer.asm` and
   `pointer.bin`, served by `broker/pointer.py`'s mock under the canned name
   **`point app`**, draws its starting state at `init` (ring 6b's A1 rule)
   and on `point` draws the button's digit at the cell it was given. Test 3
   clicks in `point app`'s panel and proves `point`; it also clicks in the
   frozen `test app`'s panel and proves harmlessness.
4. **The pointer's strip fields sit in the spare columns from column 88,
   and appear only once the mouse has spoken (trap 3).** The frozen
   `check_strip` reads each strip row whole and right-strips it:
   ```
   got0 = read_cells(shot, geometry, strip, 0).rstrip()
   got1 = read_cells(shot, geometry, strip, 1).rstrip()
   want1a, want1b = strip_rows(obs1, obs1["now"])
   ...
   if got1 != want1b.rstrip(): problems.append(...)
   m = STRIP0.fullmatch(got0)
   ```
   (`stage6/checkglass.py` 1163–1174) — so any glyph anywhere on either
   strip row beyond column 86 fails it, at 1440x1440 in ring 6a's `--truth`
   (screens A and D) and at 1920x1080 in ring 6b's `--store` (screen D).
   Those checks run on machines whose mouse never moves. Therefore: the
   pointer's fields — `pt LL.L/WW.W pk NNNN cl NNN` (pointer input-to-photon
   last/worst in ms, packets, clicks; 27 characters) — are written into
   strip row 0 from column 88 **only while `packets` in the obs page is
   above zero**, and the cursor is drawn only under the same condition. Until
   the mouse speaks the strip and the screen are ring 6a's to the pixel, which
   is exactly what the frozen gates require and what this ring's own test 4
   proves first (the frozen `check_strip` and `check_surfaces` are run,
   unchanged, on a screendump before the first packet). At 1440x1440 the
   field is cut at the right edge as GLASS.md already says of the strip; on
   the owner's 1920x1080 it is whole. The same gate protects the twin: its
   seventh criterion compares conversation and choices cells with their
   surfaces on screendump B, and no rehearsal ever moves the mouse (a hook
   that did would also put `S6: mouse ready` into the echo the eighth
   criterion demands byte-exact), so no cursor is ever drawn in the twin.
   In this ring's own checker the cursor's cell is excluded from every
   surface comparison and checked against the arrow instead.
5. **The obs page's "rest is zero" is superseded from `0x240` (trap 4).**
   GLASS.md's 6a section says the rest of the page is zero after the four
   surface descriptors; measured above, no frozen check asserts it. The new
   section defines the pointer's fields from `0x240` to `0x2BF` (decision 3)
   and states that it supersedes that sentence from this ring; the 6a text
   stands unedited, as the owner requires.
6. **The choices row's click targets are the items' text spans; button 1
   clicks the row.** "A click on a choices-row target does what its key would
   do" is made exact: a **left-button press** whose cell lies on screen row
   `R−2` within an item's text (from its first character to its last) acts as
   below; the three-space gaps, the blank tail, and rows other than `R−2` do
   nothing; the right and middle buttons do nothing on the row (all three
   reach `point`). What each item does: `? ask` and `! grow` type their
   marker byte into the prompt exactly as the key would (echoed on serial by
   the tee, drawn in the conversation, the line buffer extended) — whatever
   the line already holds; `! <name>` for an installed app types `! <name>`
   and Enter — the launch, with nothing on the wire — **only when the prompt
   line is empty (A3)**: with text already typed on the line the press counts
   in `clicks`, not in `hits`, and types nothing, so a click can never send
   a half-typed line to the wire or the journal; an app's declared choice
   `<k> <label>` delivers `<k>` to the
   app's `key` callback (the row shows those items only while the app has
   the keys); `Esc exit` is Esc (closes the app); `Tab prompt` and `Tab app`
   are Tab (the focus moves). The synthetic keys take the identical path a
   typed key takes (decision 7), so a click is a key to every consumer
   downstream — the tee, the journal, the parse, the app.
7. **`point` is delivered on a button press only, and focus does not move
   on a click.** `point(row, col, button)`: `RDI` the row and `RSI` the
   column relative to the app panel, `RDX` the button — 1 left, 2 right, 3
   middle; called once per press (a button's bit going from clear to set in
   a packet), for a press whose cell lies inside the app panel while an app
   runs; releases and moves are not delivered this ring; the app's focus is
   unchanged by a click in its panel (Tab and the row's `Tab app` move it —
   "no hidden modes": every focus change stays a visible act on the row). A
   press outside every target — the conversation, the strip, the empty app
   panel, the gaps — counts one in `clicks` and does nothing else.
8. **The pointer's ring holds packets, and the handler keeps the position;
   the ring is otherwise exactly the keyboard's.** The spec says the
   interrupt handler keeps the position in the obs page and the glass draws
   from it. If the position were updated by a consumer on the boot processor
   the cursor would freeze whenever the boot processor waits on the wire (a
   72-second install) or sits inside an app's `step` — the human's device
   frozen by the machine's work, against the constitution. So the shared
   i8042 handler assembles the three bytes (resynchronising on bit 3), adds
   the deltas to the position, stores the cell word, counts the packet and
   stamps it, and pushes **one entry per packet** — stamp, cell, buttons,
   the buttons newly pressed — into a ring of its own with a head the
   handler writes and a tail the consumer writes, a high-water mark in the
   obs page, and drop-on-full, exactly the keyboard's discipline. The boot
   processor's consumer acts on presses (deviation 6, 7) and nothing else;
   `finish_line` discards it as it discards the keyboard ring.
9. **Pointer input-to-photon is stamped at the first byte's interrupt and
   the budget is two frame slots.** `pt` is the time from the interrupt that
   delivered a packet's first byte to the end of the frame copy that drew the
   cursor after that packet — the glass core snapshots `ptr_pending` before
   its copies and measures after, as `ph` does; a packet that moves the
   cursor to no new cell is still measured to the next frame's end (GLASS.md's
   rule for a key that draws nothing). The budget test 4 holds `pointer_worst`
   under is **two frame slots, 33.3 ms**: a packet can land just after a
   frame's snapshot, wait one slot, and be painted at the end of the next
   frame. Ring 6a measured `ph` at one slot worst; the number is the design's,
   not a count.
10. **`keys` does not count clicks.** The obs page's `keys` is "keys
    delivered by the keyboard consumer"; a click's synthetic keys are the
    pointer consumer's and are counted in `clicks` (every press) and `hits`
    (presses that landed on a target); `ph` still measures a click's echo
    because the click's stamp is handed to the key path as the key stamp.
11. **The mouse is reset even though OVMF never touched it.** Measured: the
    firmware left the mouse at its power-on state and the aux port disabled
    with its interrupt bit set. The guest assumes nothing: it disables both
    ports, drains, reads the command byte and writes it back with bits 0 and
    1 set and bits 4 and 5 clear (translation kept as found — the keyboard
    map is set 1 and the probe showed the flag survives), enables the aux
    port, resets the mouse (`FF` → `FA AA <id>`), sets defaults (`F6`),
    enables reporting (`F4`), drains again — each response polled with a
    bounded PIT wait so a missing mouse costs a moment of boot and
    `mouse_id` 0, never a hang. The command byte as read and as written is
    recorded in the obs page.

---

## Decisions taken in this plan

1. **The serial lines.** The seventeen of ring 6b unchanged, in order, with
   `S6: keyboard ready` seventeenth (twelfth `S6: home <N> apps` only with a
   second disk, as HOME.md says). **`S6: mouse ready`** is printed once,
   serial only, the first time the main loop finds `packets ≥ 1` (deviation
   1). Without a mouse it never prints. The 6c gate's display is 1920x1080,
   console 120x67; nothing is baked in, the tests read the geometry from the
   guest's own log as ever.
2. **The i8042 and the two interrupts** (`stage6.asm`, item 9), in the
   keyboard block after `pic_init` and the gates, before the ready line,
   interrupts off:
   - `pic_init`: master `OCW1` becomes **`0xF9`** (IRQ1 and the cascade IRQ2
     open), slave **`0xEF`** (IRQ12 open); the remap is as before. Gates at
     `0x21` (IRQ1) and **`0x2C`** (IRQ12) point at two entries of one
     handler body; `0x27` keeps `irq7_spurious`; **`0x2F`** gets
     `irq15_spurious`, which sends EOI to the master only (the cascade was
     real, the slave has nothing in service).
   - `i8042_config` (deviation 11): `AD`, `A7` to 0x64; drain 0x60; `20` →
     read the command byte; set bits 0 and 1, clear bits 4 and 5, keep
     bit 6 and the rest; `60` then the byte; read it back; `A8`; then
     `mouse_cmd FF` expecting `FA AA` and the ID byte, `F6` expecting `FA`,
     `F4` expecting `FA`; every wait bounded (PIT, about 500 ms per
     response); on any timeout `mouse_id` stays 0 and boot goes on; `F2` is
     not sent (the ID rides on the reset). Responses are polled with the
     status byte read first and routed by bit 5 even here, so a keyboard
     byte queued meanwhile goes to the keyboard ring, not into the mouse's
     answer. The command byte read and written land in the obs page
     (`i8042_cmd`, read in bits 0–7, written in bits 8–15).
   - **`i8042_irq`** — one body, two entries: `irq1_entry` pushes, calls the
     body, sends EOI to the master, `iretq`; `irq12_entry` the same with EOI
     to the slave (`0xA0`) then the master. The body: read 0x64; **while
     bit 0 (output buffer full) is set:** read 0x60; if **bit 5** was set,
     `mouse_byte`; else the keyboard path as today (the scancode and its
     stamp into `kbd_ring`/`kbd_stamps`, `keys_hw`); read 0x64 again. A
     handler that finds the buffer empty (its byte was already taken by the
     other entry's drain) does nothing but EOI. So a byte never lands in the
     wrong ring, and three back-to-back packet bytes cost one to three
     interrupts, never a lost byte.
   - **`mouse_byte`** (the packet state machine, in the handler): counts
     `mouse_bytes`; phase 0 requires bit 3 set — a byte without it is
     dropped and counted in `resyncs`; phase 0 also records the TSC as the
     packet's stamp; phase 2 completes the packet: `dx` = byte 1 as a signed
     byte, `dy` = byte 2 as a signed byte (the sign bits of byte 0 agree on
     this machine and are not consulted; overflow bits ignored — QEMU clamps
     at 127); `ptr_x += dx`, `ptr_y −= dy`, each clamped to
     `[0, W−1]` / `[0, H−1]`; **`ptr_cell = (y >> 4) << 16 | (x >> 4)`
     stored as one `u64` after `ptr_x` and `ptr_y`**, so the glass never
     reads a torn cell; `buttons` = byte 0 bits 0–2, `pressed` = the bits
     newly set; `packets += 1`; if `ptr_pending` is 0: `ptr_stamp` = the
     packet's stamp, `ptr_pending = 1` (the older stamp kept, the worst case
     measured); the entry `(stamp, cell, buttons, pressed)` — 16 bytes —
     pushed into **`mse_ring`** (64 entries) unless full, `mouse_hw` kept.
   - The main loop's wake test becomes "the keyboard ring or the mouse ring
     is non-empty" before `sti; hlt`, and the announce check (decision 1)
     runs at the top of every pass.
3. **The obs page from `0x240`** (GLASS.md's new section; every field a
   `u64`, one writer each):

   | Offset | Field | Written by | Meaning |
   |---|---|---|---|
   | `0x240` | `ptr_x` | IRQ (i8042 handler) | the pointer's x in pixels, `0 … W−1`; `W/2` at boot |
   | `0x248` | `ptr_y` | IRQ | y in pixels, `0 … H−1`; `H/2` at boot |
   | `0x250` | `ptr_cell` | IRQ | `row << 16 \| col`, the cell holding the pointer, stored after the two above |
   | `0x258` | `packets` | IRQ | complete three-byte packets received |
   | `0x260` | `buttons` | IRQ | the buttons held after the last packet, bits 0–2 left, right, middle |
   | `0x268` | `mouse_hw` | IRQ | the packet ring's high-water occupancy |
   | `0x270` | `ptr_stamp` | IRQ | the TSC at the first byte of the packet awaiting its frame |
   | `0x278` | `ptr_pending` | IRQ sets, glass clears | |
   | `0x280` | `pointer_last` | glass | pointer input-to-photon, ticks |
   | `0x288` | `pointer_worst` | glass | the worst |
   | `0x290` | `clicks` | BSP | button presses the consumer saw |
   | `0x298` | `hits` | BSP | presses that landed on a choices-row target or reached `point` |
   | `0x2A0` | `mouse_bytes` | IRQ | bytes routed to the mouse by status bit 5 |
   | `0x2A8` | `resyncs` | IRQ | bytes dropped while waiting for a packet's first byte |
   | `0x2B0` | `mouse_id` | boot | 0 no mouse answered the reset; else 1 + the ID byte (1 for a standard mouse) |
   | `0x2B8` | `i8042_cmd` | boot | the command byte as read, and as written `<< 8` |

   `0x2C0` onward is zero this ring. The 6c section states plainly that it
   supersedes "the rest of the page is zero" from `0x240`.
4. **The cursor and the pointer's photon** (item 10), in the glass core's
   frame: step 1 also snapshots `ptr_pending`; after the strip (step 3) a
   new **step 3b**: if `packets` is non-zero, read `ptr_cell`; if it differs
   from the cell the arrow was last drawn at, repaint that old cell from its
   surface (`cell_repaint(row, col)`: the owning surface is the first of the
   four descriptors in the obs page — strip, choices, conversation, app —
   whose `row0`, `col0`, `rows`, `cols` contain the cell, never arithmetic
   on `C` and `R` (nit); the cell byte through `draw_cell`, the
   conversation's block cursor overlaid when it sits there); then draw the **arrow** at the
   new cell and remember it. The arrow is drawn every frame (a dirty row may
   have repainted its cell) and is the last thing painted, so nothing ever
   paints over it inside a frame. Step 4 gains: if `ptr_pending` was 1 at
   step 1, `pointer_last = rdtsc − ptr_stamp`, `pointer_worst = max`,
   `ptr_pending = 0`. **The arrow** is an 8x8 glyph doubled to the cell like
   every font glyph (bit 0 the leftmost pixel, as FONT.md): `01 03 07 0F 1F
   0D 19 30` — a tip at the cell's top left, a tail to the lower right; drawn
   through the same painter as `block_glyph`, never through a surface cell
   byte (a cell byte of `0x02` stays background, as GLASS.md says). Two
   colours only. The pointer starts at the screen's centre pixel, hidden
   until the first packet.
5. **The strip's row 0 extension** (item 10), from column 88, only while
   `packets ≥ 1`: **`pt LL.L/WW.W pk NNNN cl NNN`** — `pointer_last` /
   `pointer_worst` as ms to one decimal in GLASS.md's `%02d.%d`, saturating
   at 99.9; `packets` four digits; `clicks` three; every rule of the 6a strip
   (fixed width, zero padded, saturating). Cut at the right edge on a
   narrower screen as the strip already is. `strip_rows_6c(obs, now)` in the
   6c section renders both rows exactly as the glass does — `strip_rows()`
   from GLASS.md's Python, plus the field when `packets > 0`.
6. **The click consumer** (item 11): `mouse_next` pops one entry from
   `mse_ring` (the consumer writes `mse_tail`); for an entry with `pressed`
   non-zero, `clicks += 1` per pressed bit (one bit per packet on this
   machine; each bit is a press) and `click_dispatch(row, col, button)`:
   - row `R−2`, button 1: the **hit table** — up to five entries of (first
     column, last column, kind, argument), rebuilt by `choices_update` every
     time it writes the row (it knows every item: the two markers, the home
     entries by index, the app's declared keys, the Esc and Tab items) —
     is searched; a hit counts in `hits` and yields synthetic keys: kind
     *marker* → the byte (`?` or `!`); kind *launch* → **only if `line_len`
     is 0 (A3)** — `!`, space, the entry's name bytes, then `13`; with text
     on the line the press is a click and not a hit, and nothing is typed;
     kind *key* → the byte (`Esc` `0x1B`, `Tab` `9`, or the app's key). The
     click's stamp becomes `key_stamp` and each synthetic byte goes through
     **`handle_key`** (decision 7).
   - the app panel (rows `2 … R−3`, columns `⌊C/2⌋ … C−1`) while an app runs,
     any button: if the blob announces `point` (decision 8), `hits += 1` and
     `app_point(row − 2, col − ⌊C/2⌋, button)` with button 1, 2, 3 for bits
     0, 1, 2; a four-callback app: nothing.
   - anything else: nothing.
   `finish_line`'s discard (`kbd_tail = kbd_head`) also sets `mse_tail =
   mse_head`: presses made while the machine was busy are dropped like the
   keys typed then; the position stands.
7. **`handle_key`** (item 11): the main loop's key handling from `.have`'s
   `movzx ebx, al` to its `jmp main_loop`s is lifted into one routine —
   `EBX` = the translated key — that returns; the main loop calls it for a
   keyboard key, `click_dispatch` calls it for each synthetic byte. Its body
   is the same instructions in the same order (Esc, Tab, focus, the prompt's
   printable, Enter, Backspace paths); the only change is `ret` where `jmp
   main_loop` was. The 6a and 6b gates are the regression.
8. **`point` and the fifth entry** (item 12): `app_valid` gains the rule of
   deviation 2 (`L ≥ 28`, `POINTER2` at 16, the `u32` at 24 below `L` and
   `≥ 28`, else `bad component frame`), and `run_app` records
   `app_has_point`. `app_point(row, col, button)` = `app_call` with the
   blob's `u32` at 24, `RDI`, `RSI`, `RDX` as the contract says — the same
   `saved_rsp` discipline, interrupts enabled, the app may clobber every
   register but `RSP`. A home launch reads the blob from disk and finds the
   magic there too — the calculator has none and is clicked on harmlessly.
   The service table stays 40 bytes; the ABI version stays 2.
9. **The fixture** (`stage6/pointer.asm`, item 2): under 1 KB, `bits 64`,
   `default rel`, the 28-byte header (`init`, `step`, `key`, `exit`,
   `POINTER2`, `point`). `init` draws **`point app`** at panel row 0, column
   0 (the starting state — A1) and keeps the service table; `step` and `exit`
   return; `key` with `c` clears the panel with `fill` and redraws the title
   (its one declared choice, **`c clear`**), any other key is ignored;
   `point(row, col, button)` draws the digit `'0' + button` at `(row, col)`
   through `draw_text` — one glyph, the button number, at the cell it was
   given. Choices carried by the frame: `[(ord('c'), b'clear')]`, so the row
   while it has the keys is `c clear   Esc exit   Tab prompt`.
   `.gitignore` gains `!stage6/pointer.bin`.
10. **The broker module — `broker/pointer.py`** (item 3, frozen at item 8),
    standard library only, importing the frozen `broker`/`germline`
    (`serve`, `mock_answer`, `log`, `DEFAULT_PORT`), `glass` (`app_frame`,
    `parse_response`, `blob_offsets`, `parse_obs`, `strip_rows`, `regions`,
    `fmt_ms`, `fmt_n`, the constants), `twin` (`VGA_ARGS`, `DEFAULT_PORT`,
    `qemu_argv`) and `plans` (`Installer`, `mock_install`, `rehearse_plan`,
    `twin_extra_args`, `DISPLAY`, `TWIN_HOME`, `DEFAULT_WORKDIR`, `LINES`)
    — **editing none of them**. Importing `plans` sets `twin.VGA_ARGS` to
    1920x1080, so every rehearsal this module runs is 6b's twin: the home
    drive, seventeen lines, the machine's display.
    - **The 6c section's Python, verbatim:** `OBS_6C` (the offsets of
      decision 3), `OBS_PAGE_BYTES_6C = 0x2C0`, `parse_obs_6c(page)`
      (GLASS.md's `parse_obs` plus the new fields), `POINT_MAGIC =
      b"POINTER2"`, `POINT_HEADER = 28`, `point_offset(blob)` (None for a
      four-callback blob; the offset for a valid five-callback blob; a
      `ValueError` for the magic with a bad offset), `ARROW = bytes([0x01,
      0x03, 0x07, 0x0F, 0x1F, 0x0D, 0x19, 0x30])` — the eight arrow bytes
      of decision 4 —
      `POINTER_FIELD_COL = 88`, `pointer_fields(obs)` and `strip_rows_6c(obs,
      now)`, `pointer_cell(x, y)`, `MOUSE_LINE = "S6: mouse ready"`,
      `POINTER_BUDGET_MS = 2 × 1000 / 60`, the hit-table function
      `choice_targets(row_text)` (the items' column spans from the row's
      text, split on three spaces), and `click_action(row_text, col)`.
    - **`Pointer(Installer)`**: constructed with a generate callable that
      wraps the frozen mock — `mock_point(body, failure, plan=None)`: with
      no plan and body `point app`, `("app", the bytes of
      stage6/pointer.bin, b"point app", POINT_CHOICES)`; else
      `mock_install(body, failure, plan)` (GLASS.md's table and PLANS.md's,
      unchanged) — and with a rehearse callable **`rehearse_point`** that
      first checks the candidate's header (`point_offset`; a `ValueError`
      is a failed rehearsal with the phrase `the point offset lies beyond
      the blob`, no twin boot) and then calls the frozen `rehearse_plan` —
      the 1920x1080 twin, the home drive, seventeen lines, no hook for a
      plain request. Everything else is inherited: installs, the germline,
      the record (`Glazier`'s fields, `Installer`'s for an install).
    - **`main`**: `plans.py`'s flags, plus `--rehearse-app BLOB NAME` — a
      hand run of one blob under one name through `rehearse_point`, the
      log printed — for item 2's and item 12's real twin runs. Real mode
      imports `claude_backend` only there, as before.
    - **The mock's canned table for requests, ring 6c** (the section's
      table): `point app` → `stage6/pointer.bin`, name `point app`, choices
      `c clear`; everything else GLASS.md's and PLANS.md's tables. One
      generation call per lookup.
11. **The real backend** (`broker/claude_backend.py`, unfrozen): the ABI 2
    brief gains one paragraph lifted from the 6c section — the optional
    fifth callback, its header (`POINTER2` at 16, the offset at 24), its
    contract (a press, panel-relative row and column, button 1, 2, 3), that
    an app without it is clicked on harmlessly, and that the service table
    is unchanged. Never run by the gate.
12. **The harness — `stage6/test-6c.sh`** (ring 6b's shape; frozen at item
    8): refuses to run while 9999 or 9998 is held; the cage with
    **`mac=52:54:00:a1:06:03`**; the display spelled once
    (`-vga none -device VGA,edid=on,xres=1920,yres=1080`); wipes
    `stage6/out/germline/` and `stage6/out/rehearsal/`; builds with the
    unfrozen `stage6/mkimage.sh`; test 1 (the artefact, 6a's criteria);
    test 2 (`checkpointer.py --serial 8` and `--serial 2`); test 3
    (`--point 2` and `--point 8`); test 4 (the cage and display
    self-assertions, then `--truth`). **`stage6/checkpointer.py`**: its own
    `qemu_argv` (three drives under `stage6/out/`, the 1080p device, the
    6c MAC) and its own `drive` with checkplans's steps plus **`("mouse",
    dx, dy)`** → `mouse_move dx dy`, **`("button", mask)`** → `mouse_button
    mask`, **`("obs6c", label)`** → `xp /88xg` parsed by `parse_obs_6c`, and
    **`("surfaces6c", label)`**; a **pointer model** — the checker keeps the
    position it expects (the centre at boot, every `mouse` step applied with
    the measured sign rule) and emits only moves with `|dx|, |dy| ≤ 127`, so
    packets sent equals `mouse` steps plus `button` steps by measurement,
    never by a splitting model; helpers imported from `checkglass`
    (`open_shot`, `read_cells`, `check_region_rows`, `check_choices`,
    `check_mode_field`, `check_app_panel`, `check_app_panel_blank`,
    `check_strip`, `check_surfaces`, `check_colour_discipline`,
    `check_grow_entry`, `check_question_entry`, `check_germline_entry`,
    `germline_entries`, `check_image`, `read_record`, `record_count`,
    `port_state`, `report`, `say`, `PROMPT`, `cursor_cell`, `blank_cell`)
    and `checkplans` (`BOOT_PATTERNS`, `check_boot_lines`, `check_home`,
    `check_one_cell_panel`, `check_install_entry`, `check_install_germline`,
    `parse_home`, `CHOICES_PROMPT_ECHO`, `ECHO_TESTS_OK`), the twin's
    `Driver` and `keyname`, plans's `plan_keyname`, and `pointer`'s section
    Python; its own **`check_surfaces_except(shot, reads, cell)`** (every
    region equal to its surface bar the cursor's cell, which must be the
    arrow), **`check_arrow_at(shot, geometry, row, col)`**, **`check_no_arrow`**
    (no cell of the screen renders as the arrow), **`check_strip_6c`**
    (`check_strip`'s logic over `strip_rows_6c`, the `pt`, `pk`, `cl` fields
    parsed and compared: `pk` and `cl` equal in both page reads and on the
    screen, `pt` worst between the two reads and under budget), and
    **`check_panel_cells(shot, geometry, {(row, col): ch})`** (exactly those
    panel cells hold those glyphs, every other panel cell blank). The mock
    is `broker/pointer.py --mock` with the gate's germline and the 6b twin
    workdir. The line count: `check_boot_lines` from checkplans for the
    seventeen; the checker's own **`check_mouse_line`** — exactly eighteen
    `S6:` lines, the eighteenth `S6: mouse ready`, and the echo after
    `keyboard ready` equal to the typed lines with one `S6: mouse ready\r\n`
    inserted where the first packet fell. **No count in the checker is a
    hand-written literal (A2):** the step list is data, and one helper,
    `expected_counts(steps)`, derives every count from it — `packets` = the
    number of `mouse` and `button` steps so far, `clicks` = the `button`
    steps with a non-zero mask, `mouse_bytes` = 3 × `packets`, `keys` = the
    bytes of the `type` steps, and `hits` = the `button` steps carrying the
    flag **`hit=True`** — a per-step flag set by hand when the step is
    written, the one human judgement, made next to the step it describes
    (`("button", 1, "hit")` for a press on a target, `("button", 1)` for one
    on a gap, a panel with no `point`, a launch item with text on the line).
    Every obs read is checked against the counts derived from the steps
    before it; the values quoted below are what the derivation gives and
    are written into the checker by the helper, never typed in.
    - **Test 1** (`test-6c.sh`): the artefact, 6a's criteria.
    - **`--serial <smp>`** (test 2, at 8 and 2, two fresh disks): boot;
      `obs6c` **R0** right after ready; **`surfaces6c` S0**, screendump
      **S0**, `obs6c` **R0b**; **`mouse 1 0`**; sleep 0.5; `obs6c` **R1**;
      `surfaces6c` **S1**, screendump **S1**, `obs6c` **R1b**; quit. Assert:
      before the move — exactly **seventeen** `S6:` lines (6b's, `home 0
      apps` twelfth, the 6c MAC), no `mouse ready`; R0: `packets 0`,
      `mouse_id 1`, every counter from `expected_counts` of the empty step
      list so far (zero), `i8042_cmd` with bit 1 set, bits 4 and 5 clear and bit 6
      set in both its halves (the exact bytes are the firmware's and are
      printed, not asserted: `0x67` read and `0x47` written are what the
      measurement predicts), `ptr_x`/`ptr_y` the centre of the mode from the
      log, `ptr_cell` its cell, `pointer_last 0`, `clicks 0`; **S0 judged by
      the frozen `check_strip(S0, R0, R0b)` and `check_surfaces` unchanged**
      — before the first packet the machine is ring 6a's to the pixel; and
      `check_no_arrow`. After the move — **eighteen** lines with `S6: mouse
      ready` eighteenth, the echo after `keyboard ready` exactly `S6: mouse
      ready\r\n`; R1: `packets` and `mouse_bytes` from the steps (1 and 3),
      `resyncs 0`, `ptr_x` the
      centre plus one, `ptr_cell` its cell, `pointer_last` between 0 and the
      budget, `pointer_worst` the same, `mouse_hw 1`; S1: the arrow at
      `ptr_cell`, every region equal to its surface bar that cell, the strip
      by `check_strip_6c(S1, R1, R1b)` — `pk 0001 cl 000`, `pt` well formed;
      two colours everywhere.
    - **`--point <smp>`** (test 3): mock up, germline wiped, fresh notes and
      home; boot; `before` ⏎; `mouse 1 0` (the cursor appears); the model
      moves the pointer to the centre of the cell (65, 2) — inside `? ask` —
      in ≤127 steps; `button 1`, `button 0`; sleep 1; **screendump A**;
      type ` ping` ⏎; `wait_record` 1; settle; `! point app` ⏎;
      `wait_record` 2 (150 s); sleep 3; `obs6c` **P**; move to the centre of
      panel cell (5, 7) — screen (7, 67); `button 1`, `button 0`; move to
      panel (9, 12); `button 2`, `button 0`; move to panel (12, 3); `button
      4`, `button 0`; move to conversation cell (60, 59) — the panel's last
      row, last column, where no frozen check looks; sleep 1; **screendump
      B**, `obs6c` **B**; move to (65, 1) — `c clear`; `button 1`, `button
      0`; move to (60, 59); sleep 1; **screendump C**; move to the `Tab
      prompt` item's middle column (from the row text `c clear   Esc exit
      Tab prompt`: columns 20–29 → 24); `button 1`, `button 0`; sleep 1;
      `obs6c` **F0**; type `mid` ⏎; move to `Tab app`'s middle (the prompt
      row `? ask   ! grow   Tab app   Esc exit`: columns 17–23 → 20);
      `button 1`, `button 0`; sleep 1; `obs6c` **F1**; move to column 8 (the
      gap between `c clear` and `Esc exit`); `button 1`, `button 0`; sleep;
      `obs6c` **G**; move to `Esc exit`'s middle (columns 10–17 → 13);
      `button 1`, `button 0`; sleep 2; `obs6c` **X**; `! test app` ⏎;
      `wait_record` 3; sleep 3; move to screen (7, 67); `button 1`, `button
      0`; `button 2`, `button 0`; move to (60, 59); sleep 1; **screendump
      T**, `obs6c` **T**; Esc; sleep 2; `after` ⏎; settle; **screendump D**,
      `surfaces6c` **D**, `obs6c` **D2**; quit. Assert: the eighteen lines;
      the echo after ready exactly `before\r\nS6: mouse ready\r\n? ping\r\n!
      point app\r\nmid\r\n! test app\r\nafter\r\n` (the `?` is the click's
      echo, the rest typed); the record exactly three connections — `ping`
      answered `pong`; `point app` generated once, rehearsed once (`pass`),
      the frame `app_frame(pointer.bin, b"point app", POINT_CHOICES, 0)`;
      `test app` generated once (`pass`), GLASS.md's frame — and the
      germline exactly those two entries; the notebook `["before", "mid",
      "after"]`; **screen A**: the conversation rows `> before`, then a row
      `> ?` with the block cursor at column 3 (the click typed the marker:
      the checker's own row check), the choices row `? ask   ! grow`, no
      arrow in the conversation's text rows; **P**: `mode 3`, `name point
      app`, `focus 1`, `grows_generated 1`, `clicks` and `hits` from the
      steps so far (1 and 1); **screen
      B**: `check_panel_cells` with `point app` at row 0 and `1` at (5, 7),
      `2` at (9, 12), `3` at (12, 3), nothing else; the choices row `c clear
      Esc exit   Tab prompt`; `running point app` on the strip; obs B:
      `clicks` and `hits` from the steps so far (4 and 4); **screen C**: the
      panel holding only the title;
      **F0**: `focus 0`, the row `? ask   ! grow   Tab app   Esc exit`
      (checked on a screendump taken with the cursor parked — the checker
      moves it to (60, 59) before every screendump that reads the row, and
      the assertions say so); **F1**: `focus 1`; **G**: `clicks` one more
      than F1's, `hits` unchanged (the gap did nothing), `focus 1`; **X**:
      `mode 0`, `name ""`, the row `? ask   ! grow`, the panel blank;
      **screen T**: `check_app_panel(T, "-")` — the frozen test app's known
      picture untouched by two clicks in its panel — `running test app`,
      obs T `clicks` two more and `hits` unchanged, the conversation intact;
      **screen D**: mode `prompt`, the row `? ask   ! grow`, the panel blank,
      the conversation `> before`, `> ? ping`, `pong`, `> ! point app`, `>
      mid`, `> ! test app`, `> after`, the prompt; `check_surfaces_except(D,
      cell (60, 59))` with the arrow there; `check_strip_6c(D, D, D2)`;
      obs D: `keys` = the keys the checker typed (clicks not counted),
      `wire_conns 3`, `questions 1`, `requests 2`, `notes 3`, `errors 0`,
      `grows_generated 2`, `grows_served 0`, and `packets`, `clicks`,
      `mouse_bytes`, `keys` and `hits` from `expected_counts(steps)` (A2) —
      the derivation gives `hits` 8: the `?`, the three in the panel, `c
      clear`, `Tab prompt`, `Tab app` and `Esc exit` carry the flag; the gap
      click and the two clicks in the test app's panel do not; two colours
      everywhere.
    - **`--truth`** (test 4, `-smp 8`): the argv assertions — the checker's
      own QEMU line (the cage on 9999, the 1080p device, three drives under
      `stage6/out/`) and the twin's as `pointer.py` builds it
      (`twin.qemu_argv(..., extra_args=plans.twin_extra_args())` after
      `import pointer`: `twin.VGA_ARGS` the 1080p flags, the cage on 9998,
      three drives under `stage6/out/`); the fixture self-check
      (`stage6/pointer.asm` assembled to `stage6/out/pointer.check.bin`
      equals `stage6/pointer.bin`; its header parses: four offsets and
      `point_offset` below its length); `point_offset` is `None` for the
      five frozen fixtures and for every entry the gate's germline holds.
      Then **one boot** (mock up, germline wiped, fresh disks): `obs6c`
      **Z0**, `surfaces6c` **Z**, screendump **Z**, `obs6c` **Z0b** — before
      any packet: **the frozen `check_strip(Z, Z0, Z0b)` and the frozen
      `check_surfaces(Z, reads Z)` pass unchanged, `check_no_arrow`,
      `packets 0`** (the 6a and 6b gates' view of this binary, proven here
      too); then **the sweep**: from the centre, twelve `mouse 40 0`, then
      twelve `mouse 0 25`, then twelve `mouse -40 -25`, each followed by
      `sleep 0.06`, with a screendump and an `obs6c` read after moves 4, 8,
      12, 16, 20, 24, 28, 32 and 36 — at each: the arrow at the page's
      `ptr_cell`, the cell the previous screendump's arrow sat on equal to
      its surface again (a one-cell comparison against the surfaces read at
      Z, which no move changes), no other arrow anywhere, `packets` equal to
      the moves so far, `pointer_last` and `pointer_worst` under the budget;
      then the buttons on an empty spot (the app panel with no app: the
      pointer is there after the sweep): `button 1`, `button 0`, `button 2`,
      `button 0`, `button 4`, `button 0`; `obs6c` **K**: `clicks 3`, `hits
      0`, `buttons 0`, `packets` the moves plus six; then `! install echo` ⏎
      (`wait_record` 1, 150 s), sleep 3, Esc, sleep 1 — the row `? ask   !
      grow   ! echo`; **the empty-line rule (A3):** type `x` (no Enter);
      move to `! echo`'s middle (columns 16–21 → 18) on row 65; `button 1`
      (no flag), `button 0`; sleep 1; `obs6c` **L00**: `mode 0`, `clicks`
      one more, `hits` unchanged, the conversation's last row `> x` with the
      block cursor at column 3 (nothing typed by the click); type Backspace
      (the line empty again); `obs6c` **L0**; `button 1` (**hit**), `button
      0`; sleep 2; type `b`; sleep 1; move to (60, 59); **screendump L**,
      `obs6c` **L**: `check_one_cell_panel(L, "b")`, `running echo`, `mode
      3`, `name echo`, `wire_conns` equal to L0's (the launch by click put
      nothing on the wire), `hits` and `clicks` from the steps (1 and 5), the
      echo after ready carrying `! echo\r\n` typed by the click; Esc; `last`
      ⏎; sleep 1.5; `surfaces6c` **D**, **screendump D**, `obs6c` **D2**;
      quit. Assert at the end: eighteen lines; the echo exactly: the mouse
      line where the first sweep move fell, `! install echo\r\n`, `x`, the
      Backspace byte `\x08` (the tee echoes it), `! echo\r\n` (the click's
      line; the `b` went to the app, not the wire), `last\r\n`;
      the record: one install of echo (generated, `pass`, `installed` 1) and
      nothing else — the launch made no connection; the home image holding
      echo at sector 9; the notebook `["last"]`; **screen D**:
      `check_strip_6c(D, D, D2)` with `pk` and `cl` from
      `expected_counts(steps)` (every `mouse` and `button` step; the five
      presses), `pt` worst under 33.3 ms;
      `check_surfaces_except` with the arrow at (60, 59); the frozen
      `check_mode_field(D, "prompt")`, `check_choices(D, CHOICES_PROMPT_ECHO)`,
      `check_app_panel_blank(D)`, `check_region_rows(D, conv, ["> ! install
      echo", "installed echo", "> ! echo", "> last", PROMPT])` (the `x` was
      erased before Enter, so no `> x` row exists); obs D2: `packets`,
      `clicks`, `hits`, `mouse_bytes`, `keys` from `expected_counts(steps)`,
      `resyncs 0`, `mouse_hw ≤ 64`, `wire_conns 1`, `errors 0`; two colours. The gate's cost: five boots of its own (two in test 2,
      two in test 3, one in test 4) plus five rehearsals (`point app` and
      `test app` twice each, echo once), about eight minutes.
13. **The GLASS.md section** (item 1): appended after the last line of the
    frozen file (line 777, the closing fence of "Parsing it cold"), headed
    `## Ring 6c — the pointer`, and stating first that everything above it
    stands byte for byte and what it supersedes (deviation 5). Its parts:
    the device (the i8042 command byte, the two interrupts, the routing by
    status bit 5, the packet, the sign rule, the resync rule, the measured
    facts as facts); `S6: mouse ready` when the mouse first speaks, serial
    only; the obs page from `0x240` (decision 3's table); the cursor (the
    arrow's eight bytes, drawn last, hidden until the first packet, the cell
    repainted from its surface, the pointer's start at the centre); pointer
    input-to-photon (`pt`) and the strip's row 0 extension from column 88
    with its rendering rule; the click on the choices row (deviation 6's
    table of items and what each does; the hit is the item's text span;
    button 1; a launch item acts only on an empty prompt line, A3); the fifth callback (the 28-byte header, the magic, the
    contract, `bad component frame` for a bad offset, the service table
    unchanged, existing apps unchanged); the rehearsal (unchanged nine
    criteria; a five-callback candidate with a bad offset refused before the
    twin as `the point offset lies beyond the blob`; no mouse in the twin);
    the mock's canned table for ring 6c; worked examples (a packet `28 0a
    ec` and what it does to the position; the strip's row 0 with the field;
    the fixture's header bytes); and "Parsing it cold, in Python" — the code
    of decision 10 verbatim. Written to `stage6/out/glass-6c-section.md`
    with the Write tool, **its first line blank** so the new heading is not
    glued to the closing fence at line 777 (nit); the owner appends it with
    one command at the repo root, verbatim:
    ```
    cat stage6/out/glass-6c-section.md >> stage6/GLASS.md
    ```
    Then the item proves the old text is byte-identical — `cmp <(head -n 777
    stage6/GLASS.md) <(git show HEAD:stage6/GLASS.md)` silent, `git diff
    stage6/GLASS.md | grep -c '^-[^-]'` zero (no line removed), the diff's
    additions all after line 777 — and commits GLASS.md.
14. **The freeze boundary** (item 8): `stage6/pointer.asm`,
    `stage6/pointer.bin`, `broker/pointer.py`, `stage6/test-6c.sh`,
    `stage6/checkpointer.py` — five paths (GLASS.md is frozen already). Not
    frozen: `stage6/mkimage.sh`, `stage6/stage6.asm`,
    `broker/claude_backend.py`, `stage6/plan-6c.md`, the draft under
    `stage6/out/`. Everything frozen before stands untouched.
15. **The two commands for the oracle** (test 5), from the repo root:
    `python3 broker/pointer.py` and
    ```
    truncate -s 16M stage6/out/home.img
    qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
      -vga none -device VGA,edid=on,xres=1920,yres=1080 \
      -drive format=raw,file=stage6/out/esp.img \
      -drive format=raw,file=stage6/out/notes.img,if=virtio \
      -drive format=raw,file=stage6/out/home.img,if=virtio \
      -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
      -device virtio-net-pci,netdev=n0 -serial stdio
    ```
    (the `truncate` only if he wants a blank home; his oracle image
    `stage6/out/home.oracle.img` holds the calculator and is never touched
    by the harness). He clicks in the QEMU window to grab the mouse (QEMU's
    relative mode; Ctrl+Alt+G releases it), moves it — the arrow appears,
    `S6: mouse ready` on serial, `pt` and `pk` on the strip — clicks `! grow`
    and types a request, or clicks `! calculator` on the row and the
    calculator launches from disk; clicks into the calculator's panel
    (nothing happens — a four-callback app); clicks `= result`, `c clear`,
    `Tab prompt`, `Tab app`, `Esc exit` and each does what its key does.
    His word closes the ring and the stage.
16. **The prose the hook will dislike.** The new frozen basenames
    (`pointer.asm`, `pointer.bin`, `pointer.py`, `test-6c.sh`,
    `checkpointer.py`) join the prose rule; commit messages go in by `-F`
    from a file written with the Write tool. `GLASS.md` near `>>`, `cat`
    with a redirect, `cp`, `mv` or `tee` is denied in any Bash command from
    this session — the append is the owner's; the item's verification uses
    only `head`, `cmp`, `git show`, `git diff` and `sha256sum`.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are expected green at its commit**. Items
  0–8 commit with every ring 6c test failing **by design**. From item 9 the
  stated tests must be green before the commit.
- **`./stage0/test.sh` … `./stage5/test.sh`, ring 6a's `./stage6/test.sh`
  and ring 6b's `./stage6/test-6b.sh` stay green throughout** — run as
  regressions before every commit from item 9 (Stage 4's, 5's and both
  ring gates need 9999 free, 5's and the ring gates 9998 too; no two gates
  at once). The 6a gate is the same binary with one disk at 1440x1440 and
  the 6b gate the same binary with two at 1920x1080, neither moving the
  mouse: they are this ring's proof that nothing 6a or 6b built has moved.
- `HANDOVER.md` is updated as we go, with a final pass at item 13; the
  model-and-effort record (Fable 5.1 at high effort) goes in at item 0.
- Every new fault class earns a CLAUDE.md gotcha line; the second time a
  mistake is corrected its line goes in.
- Temporary probes are never committed and never undone with `git checkout
  --`: copy aside, restore from the copy. Every probe boots a private copy
  under its own `stage6/out/probe6c/` (QEMU's image lock).
- **The scope guard** governs items 9–13: two honest attempts at any one
  obstacle — a real diagnosis from the serial log, the rehearsal log, the
  obs page or a screendump, not a re-run — then stop, record the exact state
  in `HANDOVER.md`, commit that, and wait for Wajira. A frozen file that
  needs to change is never edited: the diff is written unapplied under
  `stage6/out/`, recorded, and the owner applies it. A seam missing from a
  frozen broker file is the same stop.
- **Everything runs inside QEMU with the caged network and the VGA
  device.** The only disks are raw files under `stage6/out/` (the gate's
  three; the twin's copies under `stage6/out/rehearsal/twin/` and its home
  at `stage6/out/rehearsal/home.img`; the probe's under
  `stage6/out/probe6c/`), created fresh by the harness or the broker. Both
  brokers bind only `127.0.0.1`. Nothing outside the repo is written, bar
  scratch files in the session temp directory. **No real Claude call is
  made by this session**: the mock is the only broker the gate ever talks
  to, `claude_backend.grow` is never run here, and test 5 is Wajira's.
- If the owner says the session budget is nearly spent: finish the current
  item, commit, record the exact state in `HANDOVER.md`, stop.

---

# Part 1 — the document, the fixture, the broker module and the acceptance machinery, written before the code

## Item 0 — this plan, committed; ring 6c opened in HANDOVER

Copy this file verbatim to `stage6/plan-6c.md` and commit it. The first act
after the gate opens. In the same act, remove the probe artefacts under
`stage6/out/probe6c/` (the mouse probe, the traced boot's copies and
captures) and `stage6/out/plan-6c.review.md` (Cowork's review copy, never
committed), and record in `HANDOVER.md` that ring 6c opened on 4 September
2026, implemented on **Fable 5.1 at high effort** (the owner's decision),
Cowork reviewing to the same standard as every ring; the "Where we are"
table's stage and status rows say so.

*Expected at commit:* no ring 6c tests exist yet. Stages 0–5, ring 6a and
ring 6b green (unchanged).

## Item 1 — GLASS.md's ring 6c section, appended by the owner's hand

Decision 13's section written to **`stage6/out/glass-6c-section.md`** with
the Write tool, byte-exact and complete: the measured facts as facts, the
obs page table, the arrow bytes, the strip extension, the click table, the
fifth callback's contract, the mock table, the worked examples, the Python.
Then the session **stops and says so**: the owner appends it at the repo
root with

```
cat stage6/out/glass-6c-section.md >> stage6/GLASS.md
```

When he says it is done, the item proves the old part is byte-identical
(decision 13's three read-only checks, their output quoted in the commit
message), proves the section's Python imports and runs (`python3 -c` over
the section's code block against `stage6/app.bin` — `point_offset` None —
and against a hand-made 28-byte header — the offset back), and commits
`stage6/GLASS.md`.

*Expected at commit:* no ring 6c tests yet. Everything green as before
(GLASS.md's 6a Python is unchanged, so `glass.py`'s import of it is not
affected — it carries its own copy in any case).

## Item 2 — the fixture: `stage6/pointer.asm` and `pointer.bin`

Decision 9's fixture, its source and binary committed, `.gitignore` gaining
`!stage6/pointer.bin`, the binary's size and SHA-256 in the commit message
and in the section's worked example (the section is already committed; the
example quotes the header's 28 bytes, which are fixed by the offsets and the
magic, not by the size — the size and hash go into HANDOVER). Proven on the
host alone with a scratch script: the five offsets are inside the blob and
above 27, `parse_response(app_frame(blob, b"point app", POINT_CHOICES))`
round-trips, `point_offset(blob)` returns the fifth, and
`blob_offsets(blob)` (the frozen four-offset reader) accepts it. **Then one
real twin run, no token, before anything is frozen (A1's rule from ring
6b):** `python3 broker/twin.py stage6/pointer.bin 'point app'` — the frozen
twin at 1440x1440 with one disk on the committed ring 6b image — **must
pass all nine criteria** (sixteen lines; `init` draws the title, so screen
B is not blank). The log is quoted in the commit message. Never freeze a
fixture that has not run in the twin.

*Expected at commit:* no ring 6c tests yet.

## Item 3 — `broker/pointer.py`, and the backend's `point` paragraph

Decisions 10 and 11 in code. Proven on the host alone, no guest, no Claude
call, against `--mock` on a throwaway port with `--image` pointing at a file
that does not exist: `ping` → `pong`; `x` → `mock: no canned component for:
x` (the inherited path); `install nothing` → `no plan named nothing` with
the call counter unchanged (the inherited install path); `point app` → the
pipeline into the twin, which fails `the twin did not boot` twice (no
image), the record carrying `name point app` and two generation calls; a
`Pointer` given a stub rehearse that always passes delivers
`app_frame(pointer.bin, b"point app", POINT_CHOICES, 0)` byte for byte; a
candidate whose header carries `POINTER2` with an offset beyond its length
is refused `rehearsal failed: the point offset lies beyond the blob` with
no twin boot (the rehearse callable returns before `rehearse_plan`);
`twin.VGA_ARGS` reads 1920x1080 after `import pointer` while
`checkglass.DISPLAY_EDID` still reads 1440x1440; `strip_rows_6c` with
`packets 0` equals GLASS.md's `strip_rows`, and with `packets 1` appends the
field at column 88; `choice_targets("? ask   ! grow   ! echo")` gives the
three spans `(0, 4)`, `(8, 13)`, `(16, 21)` and `click_action(..., 6)` is
None.

**Then one real twin run through this module, no token, before anything is
frozen:** `python3 broker/pointer.py --rehearse-app stage6/pointer.bin
'point app'` — the frozen twin at 1920x1080 with the home drive on the
committed ring 6b image, seventeen lines — **must pass all nine criteria**;
the log quoted in the commit message. (The fixture's `point` is not
exercised in the twin — no mouse in the twin, deviation 4 — it is proven by
the gate's guest at item 12 and again by hand there.)

*Expected at commit:* no ring 6c tests yet. No Claude call.

## Item 4 — `stage6/test-6c.sh` and acceptance test 1

Decision 12's harness with test 1. The three-drive QEMU line, the 1080p
display spelled once, the 6c MAC, the port refusals, the wipes, the summary
with decision 15's two commands.

*Expected at commit:* every ring 6c test fails (the binary has no mouse
line, no cursor, no `pt`). The non-zero exit quoted in the commit message.

## Item 5 — `stage6/checkpointer.py --serial` (test 2)

Decision 12's checker skeleton — its `qemu_argv`, its `drive` with the
mouse steps and the pointer model, `check_mouse_line`, `check_arrow_at`,
`check_no_arrow`, `check_surfaces_except`, `check_strip_6c` — and the
`--serial <smp>` mode. `test-6c.sh` gains test 2 at `-smp 8` and `-smp 2`.

*Expected at commit:* tests 1–2 fail (test 2 finds seventeen lines after the
move, no `mouse ready`, no arrow, `packets` absent — the page's `0x258` is
zero).

## Item 6 — `checkpointer.py --point` (test 3)

Decision 12's third mode: the mock lifecycle with `broker/pointer.py`, the
screens A, B, C, T, D and the obs reads P, F0, F1, G, X, T, D; every count
derived from the step list by `expected_counts`, the `hit` flag set beside
each press that lands on a target (A2). `test-6c.sh` gains test 3 at `-smp
2` and `-smp 8`.

*Expected at commit:* tests 1–3 fail.

## Item 7 — `checkpointer.py --truth` (test 4)

Decision 12's fourth mode: the argv assertions on the checker's and the
module's twin command, the fixture and magic self-checks, the pre-packet
proof with the frozen `check_strip` and `check_surfaces`, the sweep with
its nine screendumps, the buttons on an empty spot, the install, the launch
item clicked with text on the line and then on an empty line (A3), screen
D; every count from `expected_counts` (A2). `test-6c.sh` gains test 4.

*Expected at commit:* tests 1–4 fail.

## Item 8 — freeze the ring 6c acceptance machinery

`PROTECTED` grows the five paths of decision 14, the hook's comment says why
each is a criterion and why `mkimage.sh`, `stage6.asm`, `claude_backend.py`,
`plan-6c.md` and the draft under `out/` are not. `payloads.py` gains the ring
6c group: `freeze_cases` on each new path, the `-o` side door on
`stage6/pointer.bin`, the allowances measured above (the 6c gate, oracle and
checker lines with the 6c MAC, `python3 broker/pointer.py --mock …`, bare
and `--rehearse-app`, `./stage6/test-6c.sh`, the three checker modes,
`nasm … -o stage6/out/pointer.check.bin`, the read-only GLASS.md proofs and
`git add stage6/GLASS.md`, `Write` on the draft under `out/`, `rm -rf
stage6/out/probe6c`, every operation on the unfrozen four, `write("stage7/GLASS.md")`
as the "later stage's document" case moving on) and the denials (`Write` on
each new path, `nasm -o` over `stage6/pointer.bin`, `cat … >>
stage6/GLASS.md`, a heredoc writing `broker/pointer.py`). Re-run whole, 0
wrong; immediacy demonstrated live with one denied call.

*Expected at commit:* tests 1–4 still fail; the payload table 0 wrong.

---

*Everything above is written before any implementation code exists.
Everything below is the code.*

---

# Part 2 — the implementation, in the spec's order

## Item 9 — the i8042 configured, IRQ12, the packet ring, the position, the line

Decisions 1, 2 and 3 in `stage6/stage6.asm`: `pic_init`'s two masks, the
gates at `0x2C` and `0x2F`, `i8042_config` with its bounded waits and the
obs fields it writes, the shared `i8042_irq` body with its two entries and
the routing by bit 5, `mouse_byte`'s state machine and `mse_ring` with its
stamps and high-water, `ptr_x`/`ptr_y`/`ptr_cell` kept by the handler, the
main loop's wake test and announce check, `serial_only_puts` and `S6: mouse
ready`, `finish_line`'s second discard. The BSS gains `mse_ring`,
`mse_head`, `mse_tail`, `mse_phase`, `mse_pkt`, `mse_stamp0`, `mse_prev`,
`mouse_announced`. Verified with a **temporary, uncommitted probe** (a copy
of the image under `stage6/out/probe6c/`, the monitor): seventeen lines on
a two-disk boot and the obs page's `mouse_id 1`, `i8042_cmd` read `0x67`
written `0x47` (or whatever OVMF gave — recorded); `mouse_move 10 20` →
`packets 1`, `ptr_x` +10, `ptr_y` +20, `ptr_cell` right, `S6: mouse ready`
once; twenty `mouse_move 1 0` → `packets 21`, `resyncs 0`, `mouse_bytes
63`; `sendkey a` still echoes `a` with the aux interrupt live; `mouse_move
200 0` → two more packets; the one-disk boot sixteen lines.

*Green at commit:* **test 1.** Tests 2–4 red — test 2's after-move
assertions (the arrow at `ptr_cell`, `check_strip_6c`, `pointer_last`
within budget) are item 10's work (A1). Stages 0–5, ring 6a and ring 6b
green.

## Item 10 — the cursor drawn last, the pointer's photon, the strip's field

Decisions 4 and 5: `cell_repaint`, `draw_arrow` (the glyph painter with
`arrow_glyph`), step 3b and the pointer photon in `glass_main`'s frame,
`strip_format`'s row 0 extension gated on `packets`. Verified by hand
(probe copy, monitor): the arrow appears on the first `mouse_move` at the
page's cell and nowhere else; it follows a sweep, the old cell restored (a
screendump compared against the surfaces read through `xp`); `pt` and `pk`
on the strip equal to `strip_rows_6c` of the page; `pointer_worst` under
33.3 ms across fifty moves; before any move the strip is `strip_rows` of
the page exactly (the frozen `check_strip` run by hand on that screendump).

*Green at commit:* **tests 1 and 2** (A1). Tests 3–4 red (the clicks are
items 11 and 12). Stages 0–5, 6a and 6b green.

## Item 11 — the choices-row hit test, `handle_key`, the click consumer

Decisions 6 and 7: the hit table built in `choices_update`'s three paths,
`handle_key` lifted out of the main loop, `mouse_next`, `click_dispatch`
with the synthetic keys and the click stamp as the key stamp, the launch
item's empty-line rule (A3), `clicks` and `hits`. `app_point` is not yet called (item 12): a press in the app panel
counts a click and does nothing. Verified by hand first: a click on `? ask`
types `?`; on `! echo` (after an install) launches with `wire_conns`
unchanged; on `Esc exit`, `Tab prompt`, `Tab app` and an app's declared key
does what the key does; on a gap nothing; then the gate.

*Green at commit:* **tests 1, 2 and 4.** Test 3 red (its `point` clicks).
Stages 0–5, 6a and 6b green (the `handle_key` lift is the regression risk;
both ring gates type through it).

## Item 12 — `point` and the fifth entry

Decision 8: `app_valid`'s rule for the magic and the offset, `app_has_point`
set by `run_app` (a delivered frame and a home launch alike), `app_point`
from `click_dispatch`, `bad component frame` for a bad offset. Verified by
hand: `! point app` against `pointer.py --mock`, three buttons in its panel
drawing `1`, `2`, `3` where clicked; `! test app` clicked on harmlessly; then
`python3 broker/pointer.py --rehearse-app stage6/pointer.bin 'point app'` on
**this** image (the nine criteria still pass — the log quoted); then the
gate. A count the derived expectation gets wrong is a defect in the guest
or in a `hit` flag; the flag is frozen with the step it describes, so a
wrong flag is a freeze opening, not an edit — the scope guard.

*Green at commit:* **all four automated tests** at `-smp 2` and `-smp 8`.
Full `./stage6/test-6c.sh` output in the commit message. `./stage6/test.sh`,
`./stage6/test-6b.sh` and Stages 0–5 green.

## Item 13 — HANDOVER, gotchas, README, the payload table, the two commands

`HANDOVER.md` to the green-pending-oracle state (what was built, the numbers
on this build — the command byte, `pt` typical and worst, the packet count
of a gate run — tests 1–4 green with output, test 5 pending with decision
15's commands, the caveats: a mouse that never moves never announces itself;
no acceleration; button presses only, no drags or releases; the row's
targets are text spans; the twin never sees a mouse; the strip's field is
cut at 1440x1440; one app at a time and no watchdog still); `CLAUDE.md`'s
build block gains `./stage6/test-6c.sh` and the gotchas gain what bit twice
(candidates from the measurements, entered only if they bite: the sign of
`dy`; the command byte's bit 5 meaning *disable*; reading 0x60 without the
status byte with two devices live; a line printed with the tee after
`keyboard ready` landing in the conversation); `README.md`'s running section
gains ring 6c (the arrow, the click, the grab hint) and the story table its
row; `python3 .claude/hooks/payloads.py` re-run, 0 wrong; the two commands
printed for Wajira; stop.

*Green at commit:* all four automated tests, ring 6a's and 6b's gates,
Stages 0–5.

---

## Verification

- **Automated:** `./stage6/test-6c.sh` from the repo root — refuses to start
  if anything listens on 9999 or 9998; builds; tests 1–4 (two serial boots
  with one move each; the pointer at `-smp 2` and `-smp 8` against the mock,
  each with two rehearsals; the truth run with the sweep, the buttons, the
  install and the launch by click). About eight minutes. Exit 0 only if all
  pass. Run before every commit from item 9 on.
- **Regression:** `./stage6/test.sh` (ring 6a: one disk, 1440x1440, no
  mouse) and `./stage6/test-6b.sh` (ring 6b: two disks, 1920x1080, no mouse)
  and Stages 0–5's gates green before every commit from item 9. The two ring
  gates are the proof of deviations 1 and 4: on a machine whose mouse never
  moves this binary is theirs to the line and to the pixel.
- **The hook:** `python3 .claude/hooks/payloads.py` at items 8 and 13 — every
  case from every stage, 0 wrong; immediacy demonstrated live.
- **The probes:** items 2 and 3 (host-only, then the twin), 9, 10, 11 and
  12 each state their expected output.
- **Manual (test 5):** Wajira, decision 15's commands and clicks. His word
  closes the ring and the stage.

## Safety

Everything runs inside QEMU. Firmware, the VGA device, and exactly three
drives per guest — raw files under `stage6/out/` (the twin's copies under
`stage6/out/rehearsal/twin/`, its home beside them; the probe's under
`stage6/out/probe6c/`) — created by the harness, the broker or the probe;
the bodyguard is unchanged and was run on every planned command before this
plan was written. The network is slirp with `restrict=on` and one `guestfwd`
in every QEMU line, the twin's included; the brokers bind `127.0.0.1` only;
test 4's launch by click proves a click puts nothing on the wire. The
automated gate talks only to the mock, never to Claude, and refuses to run if
anything else holds either port. An app runs at ring 0 with the whole machine
in reach and now has a fifth entry point; the rehearsal is unchanged as the
mitigation, and a candidate whose fifth offset lies outside its blob is
refused before the twin and again by the guest. The i8042 is written for the
first time — inside QEMU only, and only the command byte, `A8`, `AD`, `A7`
and `D4`; on this machine every write was measured first. This session makes
no Claude call and never runs `claude_backend.grow`. Every existing frozen
file is untouched — `git diff --stat ab7b331 -- <every PROTECTED path>` is
empty at every commit, with one exception the owner makes by hand:
`stage6/GLASS.md` grows by appended lines only, its first 777 lines
byte-identical, proven at item 1 — and `./stage6/test.sh` and
`./stage6/test-6b.sh` are green at the end of the ring.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| The `S6: mouse ready` line breaks a frozen count | deviation 1: it prints only after the first packet, and no frozen gate or twin ever moves the mouse; the 6a and 6b gates run before every commit |
| The cursor or the `pt` field lands on a cell a frozen check reads | deviation 4: nothing pointer-related is drawn until `packets > 0`; test 4 proves the pre-packet screen with the frozen `check_strip` and `check_surfaces` themselves; the 6c checker excludes the cursor's cell and parks the cursor where no frozen helper looks |
| Enabling the aux port breaks the keyboard | measured: with the command byte at `0x43` the keyboard still arrives set-1 translated; the guest keeps bit 6 as found; `sendkey` is every gate's typing path and would fail loudly |
| A mouse byte lands in the keyboard ring, or a scancode in the mouse's | one handler body reads the status byte first and routes by bit 5 for every byte; a handler finding the buffer empty only EOIs; `resyncs` counts any byte dropped waiting for bit 3 |
| The three bytes of a packet arrive across two interrupts | the state machine lives in the handler and keeps its phase across interrupts; the packet is complete only at its third byte |
| The cursor freezes while the boot processor waits on the wire | deviation 8: the handler keeps the position; the glass core draws it; neither waits on anything |
| A torn position | `ptr_cell` is one `u64` stored last; the glass reads only it |
| The old cursor cell keeps a ghost arrow | `cell_repaint` from the owning surface every time the cell changes, and test 4 compares that cell with the surface at every screendump of the sweep |
| Frozen `blob_offsets` or `parse_response` rejects the 28-byte header | measured: they read four offsets and require each below `L`; the magic and the fifth offset are blob bytes to them; item 2 proves the round-trip on the host and in the twin |
| An existing app is called at a bogus fifth entry | deviation 2: no existing blob carries the magic (measured across every fixture, germline entry and home image); the guest requires the magic and a valid offset |
| A click's synthetic keys diverge from typed keys | decision 7: one `handle_key` for both; the 6a and 6b gates type through it |
| The `handle_key` lift regresses the prompt | both ring gates and Stages 4–5 type every path (notes, questions, requests, Tab, Esc, Backspace); run before the item 11 commit |
| A count in the frozen 6c checker is wrong (ring 6b item 10b again) | A2: no count is a literal — `expected_counts(steps)` derives packets, clicks, bytes and keys from the step list itself, and the only hand-made judgement is the `hit` flag written beside the press it describes; every move fits one packet by construction, so no splitting model exists to be wrong |
| The pointer's photon exceeds its budget on a busy frame | the budget is two slots by design; the sweep's screendumps also demand the cursor at the page's cell, so a lag would show as a position, not only as a number |
| The twin's echo criterion sees a mouse line | no rehearsal ever moves the mouse; `pointer.py`'s hand run and the mock's rehearsals use the plain path |
| A frozen file needs to change | the scope guard: stop, the diff unapplied under `stage6/out/`, the owner's hand |
| The gate spends a token | the double port refusal; the mock's tables; `claude_backend` imported only outside `--mock`; the call counts demanded by the record checks |
| Hick's five | the row is unchanged; the hit table is built from the row's items |
| A fixture that has never run in the twin is frozen wrong | items 2 and 3 rehearse `point app` for real in both twins before item 8 freezes it, and quote the logs |

---

## Amendments — Cowork's review, adopted before approval

Cowork approved the plan with three amendments and three nits, and
accepted all eleven deviations.

**A1 — Blocking: where test 2 goes green.** Item 9's expected-green line
claimed tests 1 and 2, but test 2's after-move assertions — the arrow at
`ptr_cell`, `check_strip_6c`, `pointer_last` within budget — are item 10's
work. Item 9 is green on test 1 only; item 10 on tests 1 and 2; the Context
sentence names where each test goes green: test 1 at item 9, test 2 at item
10, test 4 at item 11, test 3 at item 12. (Context, items 9 and 10 updated.)

**A2 — Blocking: no count in the frozen checker is a hand-written
literal.** The drive step list is data. One helper, `expected_counts(steps)`,
derives `packets` as the number of `mouse` and `button` steps, `clicks` as
the `button` steps with a non-zero mask, `mouse_bytes` as 3 × `packets`,
`keys` from the bytes of the `type` steps, and `hits` from a per-step `hit`
flag set by hand when the step is written — the one human judgement, made
next to the step it describes. Applied to `--serial`, `--point` and
`--truth`; the sentence about a dry count confirmed at item 12 is replaced
by this rule, and the risk table's row about a wrong count says so.
(Decision 12, items 6, 7 and 12, the risk table updated.)

**A3 — A click on an installed app's `! <name>` acts only when the prompt
line is empty.** With text already on the line the press counts in `clicks`,
not `hits`, and types nothing; the marker items `? ask` and `! grow` keep
typing their byte regardless. Test 4 exercises the empty-line case at the
cost of one click and no extra boot: `x` typed, the launch item clicked (a
click, no hit, nothing typed), Backspace, the launch item clicked again (the
launch). (Deviation 6, decision 6, the GLASS.md section's click table in
decision 13, decision 12's `--truth`, items 7 and 11 updated.)

**Nits.** The GLASS.md draft begins with a blank line so the new heading is
not glued to the closing fence at line 777 (decision 13, item 1).
`cell_repaint` takes its region bounds from the four surface descriptors in
the obs page, not from arithmetic on `C` and `R` (decision 4). Item 0 also
removes `stage6/out/plan-6c.review.md` (item 0).
