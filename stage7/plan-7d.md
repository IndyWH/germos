# Stage 7, ring 7d — the trials · implementation plan

**To be committed verbatim as `stage7/plan-7d.md`. Produced in plan mode,
per the foundation's build loop. Nothing below is implemented until Wajira
approves this document by writing the approval marker from his own
terminal; the ExitPlanMode hook holds the gate until then. Plan mode allows
this session to write only this one file and forbids commits and boots, so
— as every ring since 6a, and exactly as `stage7/plan-7c.md`'s header says
— the copy to `stage7/plan-7d.md` and its commit are the first act after
the gate opens, item 0 below, before any other file is touched. Cowork's
amendments while the gate holds are adopted here as numbered amendments
(A1, A2, …) at the end of the document.**

**The model note, for the record:** this ring is implemented on **Fable 5.1
at medium effort**, the owner's decision at the kickoff on 22 September
2026. Recorded here and in `HANDOVER.md` at item 0.

## Context

Ring 7c closed on 18 September 2026 and with it Stage 7. `stage7/spec-7d.md`
(approved by the owner, 22 September 2026, decisions 1–7 recorded at its
top) opens **ring 7d, the trials**: GermOS runs an N-of-1 crossover on its
own human — the choices row as it is today (**layout A**, text) against the
same items drawn as boxes (**layout B**), a cue names an item, the human
clicks it, the machine is the timer and the case-report form, the analysis
is frozen before the first click. **Done when:** three sittings are on the
notebook, the frozen analysis gives its verdict, and the row's default
follows it. **Proves the interface is evidence-based, not asserted.** Test 5
is Wajira's — sitting 1 in the windowed twin, sittings 2 and 3 on the HP —
and his word on the third sitting closes the ring.

What this ring builds, from the spec and the kickoff:

- **`stage7/TRIALS.md`** — the one text: the cue table per block, the block
  order per sitting parity, layout B's geometry in cells, the note formats,
  the serial line formats, the obs fields, mode value 5, the verdict rule,
  the refusals, and two worked examples. The assembler implements it; the
  checker and `stage7/trials.py` parse by it. Frozen at item 8.
- **`stage7/trials.py`** — the host tool: parses TRIALS.md cold, reads the
  notes partition of a disk image (DISK.md's table, NOTEBOOK.md's parser)
  or the `trial:` lines of a serial log, prints the sitting tables and the
  verdict; the pure functions the checker imports. Frozen at item 8.
- **`stage7/test-7d.sh` and `stage7/checktrials.py`** — acceptance tests
  1–4, written red before any guest code; the synthetic human in the
  checker; every gate run appended to `stage7/out/gate-7d.log`. Frozen at
  item 8.
- **The guest** (`stage7/stage7.asm`, unfrozen): the reserved word
  `! trial` answered before the home lookup and the broker; mode 5; the obs
  fields; the cue, the hit, the miss, the pauses, Esc; the notes and the
  raw serial lines; the table and the verdict in the app panel; layout B —
  inverse cells, the boxes, their hit table; `layout_default` read from the
  notebook at boot. Layout A untouched to the pixel and to the byte.
- **`stage7/glass-7d-section.md`** — the GLASS.md section for this ring,
  appended by the owner's hand (`cat >>`), never by CC.
- **The freeze** (item 8): the four paths into `PROTECTED`, their cases in
  the payload table, 0 wrong.
- **`HANDOVER.md`** as we go; `CLAUDE.md`'s build block and the windowed
  run; `README.md`'s ring 7d.

**The owner's decisions, already made, not reopened here:** (1) the
choices row, text against boxes; (2) ten cues a block, eight blocks
`ABBA BAAB` / `BAAB ABBA`, three sittings, the sign test at ten of twelve
with misses not worse; (3) the cue is the label word only; (4) the verdict
lives on the notebook; (5) sitting 1 in the twin, sittings 2–3 on the HP;
(6) Fable 5.1 at medium effort; (7) the GLASS.md section by the owner's
hand, the four files frozen at the plan's freeze item.

The standing orders: the automated gate talks only to the mock, spends no
token and needs no internet; **the trial needs nothing from the wire** —
the mock and the relay are up for one boot only (test 2's mode-3 refusal
needs an app running, and the only way to an app is a grow through the
mock); every other boot of this ring asks nothing and runs with nothing
listening, as 7c's test 2 boots do. The cage, the storage bodyguard and
every frozen file stand; `./stage7/test.sh`, `./stage7/test-7b.sh`,
`./stage7/test-7c.sh`, the three ring 6 gates and every earlier gate must
pass at the end of the ring. **The scope guard:** if a frozen file turns
out to be wrong, stop at the commit boundary, write the diff unapplied
under `stage7/out/`, say so in `HANDOVER.md`, and wait; the owner applies
it by his own hand. Never create or mention the approval marker from inside
a session. One commit per numbered item; `/clear` between items; tests red
before the code they judge; tests green before every commit that should
pass them; **every number in a frozen test is written from a run or
derived by a frozen document's rule, never from arithmetic** (ring 6b item
10b, ring 6c item 11b, ring 7b item 10b — three freeze openings of one
class). Two honest attempts per obstacle.

The plan is **evaluation-first**. Items 1–6 write the document, the tool
and the four tests so that test 1 is green and tests 2–4 are red before a
single instruction of guest code exists in the repository; item 7 plays the
synthetic human against a **private** binary and reads every number the
checker needs from that run; item 8 freezes the four files; item 9 writes
the GLASS.md section and stops for the owner's hand; items 10–11 are the
guest code, item 12 the handover. **Test 1 goes green at item 4; test 4 at
item 8 (the freeze); tests 2 and 3 at item 11.** Test 5 is Wajira's.

### Environment, measured in this session before planning

Read-only: no file was written but this one, no guest was booted, nothing
frozen was touched, no Claude call was made; the working tree is clean at
`e010fbb`.

| Fact | Measured how |
|---|---|
| **The toolchain on mlrig under Omarchy:** NASM 3.02, QEMU 11.1.1, Python 3.14.7, OVMF at `/usr/share/ovmf/OVMF.fd`, mtools, OpenBSD netcat, xxd; every `out/` exists; the Stage 0 gate, the 7c gate and the payload table green today on the item 21 binary (40,960 bytes) — the kickoff's word, not re-run here | the kickoff |
| **QEMU cannot boot the twin with a keyboard and no mouse.** `-machine q35,help` lists `i8042=<bool>` — the whole controller, keyboard included — and no property for the auxiliary port alone; `-device help` offers `usb-mouse`, `virtio-mouse`, `vmmouse` to *add* a pointer, nothing to remove the PS/2 one. The guest's keyboard is the i8042's, so `i8042=off` leaves nothing to type `! trial` with. **`mouse_id` is 1 on every twin boot** (7c's `i8042: mouse reset ok` on every boot) — the `no mouse` refusal cannot be reached from the gate's QEMU line (deviation 3) | `qemu-system-x86_64 -machine q35,help`, `-device help`; `stage7/checkmetal.py` `I8042_LINES` |
| **The obs page's tail is not free from `0x2C0`.** DISK.md (frozen, ring 7a) holds `ahci_cap` `0x2C0`, `ahci_pi` `0x2C8`, `ahci_port` `0x2D0` and says "`0x2D8` onward is zero this ring"; `stage7.asm` defines `OBS_AHCI_CAP 0x2C0` … `OBS_AHCI_PORT 0x2D0`. The spec's "from `0x2C0`" would overwrite them — deviation 1 puts the trial's sixteen words at **`0x2E0`–`0x358`** and the zero rule from **`0x360`**. No frozen checker asserts zeros beyond `0x2D8` (grep on every checker and broker module: none reads past `0x2D8` but `parse_obs_6c`, which stops at `0x2C0`) | `stage7/DISK.md` 207–216; `stage7.asm` 477–479; grep |
| **The mode word field.** `mode_words` is five words padded to 11 bytes each, copied into an 18-column field; `strip_format` writes `?` for a mode above 4 (`cmp rax, 4; ja .mode_unknown`). The frozen `glass.mode_word` returns `"?"` for mode 5, so `strip_rows_6c` and `check_strip_6c` cannot judge a strip in mode 5 — the trial checker renders the mode word by TRIALS.md's own Python and checks the mode field by the frozen `check_mode_field(shot, geometry, word)`, which takes any word. `trial A 3/8` is eleven characters, the same width as `installing ` | `stage7.asm` 9286–9310, 9768; `broker/glass.py` 242–246; `stage6/checkglass.py` 897 |
| **The renderer has no inverse cell.** `draw_cell` paints every cell foreground-on-background: a byte `0x20`–`0x7E` is its glyph, `CELL_BLOCK` (`0x01`) is the solid block, anything else is background; `fg_pix`/`bg_pix` are the only two colours. GLASS.md has no word "inverse" — the strip is drawn like every other surface, so the spec's "the strip's inverse colours" reads as *the inverse of the strip's colours*: background-coloured glyphs on foreground fill (decision 3). The frozen twin's `cell_pixels` renders a byte at or above `0x80` as background, and its criterion 7 compares the choices region with its surface — so an inverse cell must never reach a rehearsal: it cannot, because the twin's SATA disk is formatted fresh per rehearsal (no verdict, layout A) and the twin never types `! trial` | `stage7.asm` 8400–8435; `broker/twin.py` 216–221; grep `inverse` in stage6/*.md |
| **The click path today.** `click_dispatch` counts every pressed bit in `clicks`, then a button-1 press on row `R−2` or `R−1` goes through `choices_hit` (the `hit_table`, `HIT_MAX` 5 entries of first/last column, kind, argument, filled by `hit_add` from `choices_update`), a hit counts in `hits` and takes `handle_key`'s path; anything else goes to `click_panel`. The four-item row `? ask   ! grow   Tab app   Esc exit` has targets at columns **0–4, 8–13, 17–23, 27–34** (GLASS.md's worked example, `choice_targets(True, 0, [])`). Layout B fills the same `hit_table` with box spans, so the click machinery is reused, not duplicated | `stage7.asm` 1548–1721, 7256–7330; GLASS.md 1080–1085 |
| **The main loop sleeps in `hlt`** unless an app runs (`.app_turn` polls with `pause`); IRQ0 is masked (`OCW1 0xF9`), so a timed pause needs the loop to poll the TSC as it does for an app — a trial in progress keeps the loop awake the way an app does (decision 4) | `stage7.asm` 1395–1437; GLASS.md 824–826 |
| **The frame's stamp discipline** to mirror for the cue: `echo_pending` is snapshotted before the copies (`R14`), and after the copy's end `photon_last = rdtsc − echo_stamp`, `echo_pending = 0` — the cue takes the same shape with the roles reversed: the BSP sets `cue_pending`, the glass core writes `cue_stamp` = the copy's end and clears it (decision 4) | `stage7.asm` 9010–9043 |
| **The notes path.** `notebook_append` writes `line_buf`/`line_len` as the next record and empties the buffer; `notebook_replay` reads every note sector by sector at boot after `keyboard ready` and draws it console-only; `nb_count`, `nb_next`, `disk_sectors` are the journal's state; the notes partition is a NOTEBOOK.md disk at LBA 2048 (DISK.md). A trial note is built in a scratch buffer, copied into `line_buf`, and appended by the same routine — the prompt line is empty during a trial. The verdict and the sitting count are found by scanning the journal from disk at the moment of need, never from a table in memory (decision 5) | `stage7.asm` 7788–7850; DISK.md 166–178 |
| **The serial rule.** `serial_raw_puts` writes to the UART alone (the `S7: mouse ready` path); the tee draws every byte into the conversation once the console is up — the `trial:` lines take the raw path. The frozen `check_echo(capture, want)` demands the wire after `ready` equal to the typed text: the trial checker strips the `trial:` lines and the mouse line before that check and judges them separately | `stage7.asm` 2461–2470; `checkmetal.strip_mouse_line` |
| **`keys` is counted in the keyboard consumer** (`kbd_next`, before `handle_key`), so a key ignored in mode 5 is still counted, as the spec says | `stage7.asm` 1743–1800 |
| **The 7c checker's seams reused as they are** (module-level, importable): `qemu_argv` (the very command — test 4's argv check then holds by construction), `fresh_disk`, `fresh_stick`, `check_boot_lines`, `check_i8042_lines`, `strip_mouse_line`, `check_stick_tables_unchanged`, `start_relay`, `start_mock`, `geometry_of`, `PATTERNS_BLANK`/`PATTERNS_AGAIN`, `MOUSE_LINE`, `READY`, `RELAY_PORT`, `BROKER_PORT`, `DISK`, `METAL_OUT`; plus `checkglass.check_region_rows`, `check_mode_field`, `check_choices`, `check_counts`, `read_record`, `check_grow_entry`, `report`, `say`, `dump_capture`, `open_shot`, `cell_matches`, `render_cell`, `blank_cell`, `PROMPT`, `SETTLE`; `checkpointer.Pointer`, `target_col`, `park_cell`, `check_arrow_at`, `check_i8042`, `check_panel_cells`; `pointer.choice_targets`, `parse_obs_6c`; `glass.regions`, `app_frame`, `grow_request`, `TEST_CHOICES`; `checkdisk.parse_notebook`, `read_image`; `metal.parse_gpt`, `partition_bytes`; `twin.Driver`, `keyname`; `plans.plan_keyname`; `rehearse.KEY_GAP`. **Bound to a form and transcribed:** `checkmetal.drive` — its step loop cannot host a timed human, so `checktrials.drive_7d` copies its skeleton (the boot, the ready wait, the geometry, the model, the steps) and adds one step, `("play", script)`, the synthetic human | read |
| **The hook today** on this ring's names: `stage7/TRIALS.md`, `stage7/trials.py`, `stage7/checktrials.py`, `stage7/test-7d.sh` end in no frozen basename (`CANDIDATE` matches a token *ending* in one of `BASENAMES`; `trials.py` is not `metal.py`, `test-7d.sh` is not `test.sh`), so all four are writable today and test 4 is red by design until item 8; `stage7/out/gate-7d.log` is under `out/`, gitignored (`*.log` too) | `.claude/hooks/protect-tests.py` 273–278; `.gitignore` |
| **The plan gate:** `.claude/hooks/require-plan-approval.py` denies `ExitPlanMode` until `PLAN_APPROVED` exists at the repo root and consumes it once; the other hook denies every route to that name from a session | read |
| **A candidate cue table** satisfying the spec's rule (each of the four items at least twice per block, no item cued twice running) was checked mechanically: eight rows of ten, every row passing both constraints — decision 1 carries it | a ten-line Python check over the rows below |

**To be measured at item 1, before any test is written** (plan mode forbids
a boot), on the closed binary and private copies under
`stage7/out/probe7d/` (gitignored), nothing frozen touched, no probe
committed:

1. **The monitor's clocks under QEMU 11.1.1:** the wall time of one
   `xp /108xg` (a `0x360`-byte page) through `twin.Driver.xp`; the latency
   from a guest serial line to its bytes in the `-serial file:` capture
   (the ready line's arrival against the host clock while polling the
   file at 5 ms); the latency of `mouse_button 1` to the packet's arrival
   (`packets` on the page read straight after). These size the synthetic
   human's poll interval and are the terms of the offset item 7 measures.
2. **The pointer's own input-to-photon on this host:** `pointer_last` and
   `pointer_worst` on the page after twenty monitor moves on the closed
   binary — the spec's "the pointer's own input-to-photon is the slack",
   read before any trial code exists.
3. **The boot replay's cost:** the time from `S7: keyboard ready` to the
   prompt on screen on a disk carrying 300 short notes (written from the
   host by NOTEBOOK.md's format into a copy of a formatted disk) — three
   sittings leave about that many; the checker's settle after ready is
   written from this number.
4. **The frozen seams' behaviour on mode 5 and inverse cells**, confirmed
   by running them, not by reading: `mode_word(5, "")`, `cell_pixels(font,
   0xA0)`, `check_mode_field` with an eleven-character word.
5. **The hook's verdicts** on every command shape this ring will run
   (the four names with `Write`, `python3 stage7/trials.py --disk …`,
   `./stage7/test-7d.sh`, `python3 stage7/checktrials.py --sitting`, the
   log redirection, `cp` of the probe's stick over `stage7/out/stick.img`,
   `rm -rf stage7/out/probe7d stage7/out/trials`), fed through a scratch
   payload script written with the Write tool.

Recorded in `HANDOVER.md`'s environment table at item 1; `git diff` shows
only `HANDOVER.md`.

---

## Decisions taken in this plan

1. **The design, as TRIALS.md states it** (item 2). The four items and
   their label words: `? ask` → `ask`, `! grow` → `grow`, `Tab app` → `app`,
   `Esc exit` → `exit`; their indices 0–3 in that order (`trial_target`).
   **The cue table**, one row per block, fixed by block number, each item at
   least twice, none twice running (checked mechanically before this plan):
   ```
   block 1: grow ask exit app grow exit ask app exit ask
   block 2: app exit grow ask app grow exit ask grow exit
   block 3: exit app ask grow exit ask app grow ask grow
   block 4: ask grow app exit ask app grow exit app exit
   block 5: grow exit ask app grow ask exit app ask app
   block 6: app ask grow exit app exit ask grow exit grow
   block 7: exit grow app ask exit app grow ask grow ask
   block 8: ask app exit grow ask exit app grow exit app
   ```
   **The block order:** odd sittings `ABBA BAAB` (blocks 1–8 = A B B A B A A B),
   even sittings `BAAB ABBA`; block *b*'s layout is the order's *b*-th
   letter with the space removed. **The pairs:** blocks (1,2), (3,4),
   (5,6), (7,8) of each sitting — one A and one B in each by construction.
   **The sitting number** is one more than the number of notes of the form
   `trial sitting <n> <order>` already on the notebook (an aborted sitting
   counts: it was started). **The cue** is the line `click: <word>` in the
   conversation panel; the cue stamp is the end of the frame that painted
   it. **A hit** is a button-1 press on the cued item's target (layout A:
   the item's text on row `R−2`, or the same columns on row `R−1`; layout B:
   any filled cell of its box on either row); its cue-to-hit is
   `(press stamp − cue stamp) / tsc_per_ms`, integer division. **A miss** is
   any other button-1 press anywhere on the screen while a cue is showing;
   the cue stays. A press while no cue is showing (the 500 ms pause, the
   rest between blocks, the frame before the cue is painted) is neither:
   counted in `clicks` and nothing more; buttons 2 and 3 are counted and
   nothing more. In mode 5 `hits` (ring 6c's counter) is not incremented —
   nothing on the row acts. **The pause:** 500 ms after a hit with the row
   unchanged, then the next cue; **the rest:** 2000 ms between blocks with
   the row blank (both rows background, in either layout) and the panel
   line `block <b> of 8 - rest` (the block just finished; the next block's
   first cue follows the rest). **The measure:** per block, `hits` (always
   10 for a completed block), `misses`, and the **median** of the ten
   cue-to-hit values in ms — the ten sorted, the mean of the fifth and
   sixth rounded down. **The verdict rule, pre-registered:** over the
   twelve pairs of the **first three sittings that ended in `done`**, in
   sitting order, count the pairs in which the B block's median is
   strictly lower than the A block's; B becomes the default if that count
   is at least ten **and** the total misses of the twelve B blocks are not
   greater than those of the twelve A blocks; otherwise A. Nothing else is
   looked at. An aborted sitting's completed blocks stand on the record
   and in its table but are outside the verdict — the verdict needs twelve
   pairs, and a pair is two blocks of one sitting. **Esc** aborts: the
   current block's hit notes already journaled stand on disk (append-only)
   but no `trial block` line is written for it, so no table shows it; the
   completed blocks' lines stand; `trial sitting <n> aborted <b>` closes
   the sitting. **One sitting a boot:** a second `! trial` after a sitting
   ended in this boot refuses `one sitting a boot`. After a verdict exists,
   `! trial` refuses `trial concluded` (trial two is a later ring; the
   pre-registered rule is three sittings).
2. **The notes and the serial lines.** Every event is one note, NOTEBOOK.md's
   format unchanged, printable ASCII, single spaces:
   ```
   trial sitting 1 ABBA BAAB
   trial 1 1 A 3 412            sitting, block, layout, cue index (1-10), ms
   trial 1 1 A 4 miss
   trial block 1 1 A 10 1 431   sitting, block, layout, hits, misses, median
   trial sitting 1 done
   trial sitting 1 aborted 5    the block that was discarded
   trial verdict B              after the third done sitting; A or B
   ```
   Each note goes to serial at the moment it is journaled, **raw UART**,
   as the note with its first word replaced: `trial: sitting 1 ABBA BAAB`,
   `trial: 1 1 A 3 412`, `trial: block 1 1 A 10 1 431` — the rule is one
   line: the serial line is `trial:` followed by the note from its sixth
   byte. So `S7: notebook N notes` counts them and the boot replay shows
   them; and the chart on the HP carries the sitting. **The refusals** are
   console lines, counted in `errors`, journaling nothing: `no mouse`
   (`mouse_id` 0), `an app is running` (mode 3), `one sitting a boot`,
   `trial concluded`, and **`trial is reserved`** — a typed line whose
   first six bytes are `trial ` is never a note (A1): the journal's
   `trial ` prefix belongs to the machine alone, so the scans of decision
   5 read only what the machine wrote.
3. **Layout B** (TRIALS.md, "The boxes"). For a row of *n* items on a
   console *C* cells wide: `w = ⌊C / n⌋`; box *i* (0-based) spans columns
   `i·w … (i+1)·w − 1`, the last box `(n−1)·w … C−1`; **the last column of
   every box but the last is the gap**, background on both rows; every
   other cell of the box on rows `R−2` and `R−1` is filled — **the inverse
   of the strip's colours: background-coloured glyphs on foreground fill**;
   the label sits on row `R−2` from column `first + ⌊(filled − len) / 2⌋`
   where `filled = w − 1` (the last box: `C − (n−1)·w`). A press on any
   filled cell of a box is that item; a press on a gap cell is a gap. The
   hit table is the boxes' filled spans, one entry each — the same table
   `choices_hit` reads today. **The cell byte:** a byte with bit 7 set,
   `0x80 | ch` for `ch` in `0x20`–`0x7E`, is drawn inverse — `draw_cell`
   swaps the two colours for it; `0xA0` is the solid foreground cell. No
   cell of layout A, of the strip, of the conversation or of an app ever
   carries bit 7, so nothing outside layout B changes by a pixel. On the
   twin (C = 120): four boxes at columns 0–28, 30–58, 60–88, 90–119 with
   gaps at 29, 59, 89; the labels at 12–16, 41–46, 71–77, 100–107; at the
   prompt with no app installed, two boxes 0–58 and 60–119, labels at
   27–31 and 87–92. The choices row shows layout B **during a B block of a
   trial and, outside a trial, when `layout_default` is 1**; the items
   shown are the row's items for the state, exactly as today (GLASS.md's
   table, HOME.md's extension), never more than five. The row's state
   changes (`choices_update`) redraw it in whichever layout is current.
   **During any block of a trial the row shows the four items of the
   state-3 row**, `? ask   ! grow   Tab app   Esc exit`, in both layouts.
4. **The guest, mode 5** (items 10–11). `bang_line` gains one compare
   before the undo check: a body equal to the seven bytes `trial` (exact,
   nothing after it) goes to `trial_start`, before `home_lookup_name` and
   before the broker, as `undo install` already does. `trial_start`:
   `mouse_id` 0 → `no mouse`; `app_running` → `an app is running`; a sitting
   ended in this boot → `one sitting a boot`; the journal holds a
   `trial verdict` note (decision 5's scan) → `trial concluded`; each a
   console line, `errors + 1`, `finish_line`. Otherwise: the sitting number
   from the scan, the order by parity, the note and the serial line, mode
   5, `trial_sitting`/`trial_block 1`/`trial_layout`, the row set to the
   four items in the block's layout, and the first cue. **The loop:** while
   `trial_active`, the main loop does not `hlt` (the `.app_turn` idiom: a
   `trial_step` call each turn that watches the TSC for the pause's end
   and the rest's end); keys in mode 5 are counted and dropped in
   `handle_key` before `.prompt_key`, except Esc → `trial_abort`; presses
   in mode 5 go from `click_dispatch` to `trial_press` before the row
   logic — the pressed bits are counted in `clicks` first, as ever. **The
   cue:** the BSP writes `click: <word>` into the conversation surface
   (console-only, `console_puts`; the panel scrolls as it always has),
   sets `trial_target`, `trial_cue`, then `cue_pending = 1`; the glass core
   snapshots `cue_pending` before its copies and, after the copy's end,
   writes `cue_stamp = rdtsc` and clears it — the mirror of
   `echo_pending`. **A press:** `cue_pending` 1 or no cue showing → return;
   button 1 on the cued target (`choices_hit` for row `R−2`/`R−1`, judged
   by the current layout's hit table, kind and argument against
   `trial_target`) → `hit_last = press stamp − cue_stamp`, `hit_worst`,
   `trial_hits + 1`, the ms into the block's ten-slot array, the hit note
   and its line, then the pause (`pause_until = press stamp + 500 ×
   tsc_per_ms`); any other button-1 press → `trial_misses + 1`, the miss
   note and its line, the cue stays. **The pause's end:** cue 10 done →
   the block note (hits 10, misses, the median from the array), the line,
   `trial_cue = 0`, the row blank, the panel's rest line, `rest_until =
   now + 2000 × tsc_per_ms`; block 8 done → `trial_sitting_done`; else the
   next cue. **The rest's end:** `trial_block + 1`, `trial_layout` by the
   order, `trial_hits`/`trial_misses` 0, the row in the new layout, the
   first cue. **`trial_sitting_done`:** the `done` note and line; the
   table in the app panel — row 0 `sitting <n> <order>`, rows 1–8 the
   block notes from their block number on (`1 A 10 1 431`); then the
   verdict scan (decision 5): if this sitting is the third `done`, the
   verdict by the rule, journaled as `trial verdict <L>`, its line,
   `layout_default = 0/1`, row 9 of the panel `verdict <L>`, the row
   redrawn in that layout; mode 0 and `finish_line` (its prompt; the keys
   and presses made meanwhile discarded as ever). **`trial_abort`:** the
   `aborted <b>` note and line, the panel's table of the completed blocks
   with `aborted <b>` as its last row, mode 0, `finish_line`. The obs
   fields, all `u64`, one writer each (the section, decision 7):

   | Offset | Field | Written by | Meaning |
   |---|---|---|---|
   | `0x2E0` | `trial_sitting` | BSP | the sitting number while a sitting runs; the last sitting's after it; 0 before any |
   | `0x2E8` | `trial_block` | BSP | the block, 1–8; 0 outside a sitting |
   | `0x2F0` | `trial_layout` | BSP | the current block's layout, 0 A, 1 B |
   | `0x2F8` | `trial_cue` | BSP | the cue's index in its block, 1–10; 0 while no cue shows |
   | `0x300` | `trial_target` | BSP | the item cued: 0 ask, 1 grow, 2 app, 3 exit |
   | `0x308` | `cue_stamp` | glass | the TSC at the end of the frame copy that painted the cue |
   | `0x310` | `cue_pending` | BSP sets, glass clears | |
   | `0x318` | `trial_hits` | BSP | hits in the current block |
   | `0x320` | `trial_misses` | BSP | misses in the current block |
   | `0x328` | `hit_last` | BSP | the last hit's cue-to-hit, ticks |
   | `0x330` | `hit_worst` | BSP | the worst this boot |
   | `0x338` | `layout_default` | boot, BSP at a verdict | what the row shows outside a trial: 0 A, 1 B |
   | `0x340`–`0x358` | reserved | — | four words, zero |

   **`mode` gains the value 5, `trial`**, and the strip's mode word for it
   is `trial <L> <b>/8` (`trial A 3/8`), eleven characters, space-padded
   to the field's 18 as every mode word is. The rest of the page from
   `0x360` is zero.
5. **The journal is the memory** (decision 4 of the spec). Three scans,
   each a walk of the journal from sector 1 to `nb_count` reading each
   record into `sector_buf` (as `notebook_replay` does), at the moment of
   need and never cached across a boot: **at boot** (from
   `notebook_replay`'s walk, one pass), the last `trial verdict <L>` note
   sets `layout_default`; **at `! trial`**, the count of `trial sitting <n>
   <order>` notes gives the sitting number, and the presence of a verdict
   note refuses; **at `done`**, the block notes of every sitting that has a
   `done` note, the first three such sittings in order, give the twelve
   pairs. The parsers are byte compares on fixed positions and decimal
   reads; a note that does not parse is not a trial note and is skipped.
6. **The synthetic human** (`stage7/checktrials.py`, item 5; its numbers
   from item 7). It plays a **script**: per block, ten scripted delays in
   ms and the set of cue indices to miss first. It knows the cue sequence
   (TRIALS.md's table) and the layout (the order), so **during the 500 ms
   pause it moves the pointer onto the next cued target** — layout A: the
   middle column of the item's text on row `R−2` (`target_col` over
   `choice_targets(True, 0, [])`); layout B: the box's middle filled cell
   on row `R−1` (the margin row, so the arrow never sits on a label) —
   then, at *h + 500 ms + d* by the host clock, where *h* is the host time
   the previous hit's `trial:` line reached the serial file (polled at 5
   ms) and *d* the scripted delay, it presses and releases button 1. The
   first cue of the sitting is anchored on the sitting line, the first cue
   of a later block on the block line plus 2000 ms. **A scripted miss**
   presses at the scheduled time on a gap column (layout A: column 6;
   layout B: the first gap cell) — the guest journals the miss — then the
   human moves onto the target and presses after *d* again. Its hand is
   already over the target when the cue appears, so the cue-to-hit the
   guest records is `d + OFFSET`, where `OFFSET` is the sum of the serial
   file's latency and the click's latency, minus the frame wait before the
   cue's paint — **a small number, possibly negative, measured at item 7
   as the median over a sitting of (recorded ms − scripted d)**. Every
   count and every line the checker expects is the script expanded by
   TRIALS.md's rules through `trials.py`'s functions (`notes_of(script)`,
   `serial_of(note)`, `table_of(notes)`, `verdict_of(notes)`), with each
   hit's ms judged as a window and each block's median as **the median of
   the scripted delays plus `OFFSET`, ± `SLACK_MS = 30`** (the spec's
   rule). At each block boundary (during the rest) it reads the obs page
   once; at `done` it reads the page, the surfaces and takes a screendump
   with the arrow parked. The scripts: **`SCRIPT_1`** for test 3's first
   sitting — delays drawn from `120 … 400` ms in tens, A blocks with
   medians near 310 and B blocks near 210, no two blocks the same list,
   **three misses**: block 2 (B) cue 4, block 5 (A) cue 7, block 7 (A) cue
   2 (so B's misses are not worse); **`SCRIPT_ABORT`** for the second
   sitting — blocks 1–2 complete, Esc after cue 3 of block 3; **`SCRIPT_3`,
   `SCRIPT_4`** — B faster in every pair, no misses, so the twelve pairs of
   sittings 1, 3 and 4 give **B** by the rule (the verdict is the rule's
   output over the scripts, computed by `trials.py`, never typed).
7. **`stage7/glass-7d-section.md`** (item 9): the section for GLASS.md in
   the 6c section's shape — the heading `## Ring 7d — the trials`, the
   standing sentence (everything above stands byte for byte; DISK.md's
   three words stand), **the supersession:** "the rest of the page is
   zero" holds from `0x360` from this ring on (the 6c text said `0x2C0`,
   DISK.md `0x2D8`); the table of decision 4 with offset, writer, meaning;
   `mode` value 5 and its word; the inverse cell byte; the reserved word
   `! trial` answered before the home lookup and the broker (one sentence
   of supersession of HOME.md's "What a ! line does now"); the reserved
   prefix `trial ` (one sentence of supersession of NOTEBOOK.md's "any
   typed line is a note", A1); the click rule
   on the boxes; the pause's press rule; and a pointer to TRIALS.md for
   the design, the formats and the verdict. Written with the Write tool,
   committed as its own item, **then the session stops and waits**: the
   owner appends it with `cat >> stage6/GLASS.md` from his own terminal
   and says it is in before the next commit. CC never touches GLASS.md.
8. **The harness** (items 4–6, frozen at item 8), 7c's shape; the scratch
   **`stage7/out/trials/`** (disks, stick copies, captures, screens,
   records, relay logs); the log **`stage7/out/gate-7d.log`**: the first
   thing `test-7d.sh` does is `exec > >(tee -a "$LOG") 2>&1` after printing
   a header `=== ring 7d gate <ISO-8601 local time> commit <short hash> ===`,
   so every gate run — its own tests and the three earlier gates it calls —
   lands in the log whole, appended; the checker's every line goes through
   the same descriptors. Every boot `timeout -k 5 <T>`, exit 124 the
   expected outcome; `T` per boot from item 7's timings.
   - **Test 1** (`test-7d.sh`, then `checkmetal.py --stick` — frozen,
     reused as it is — then `checktrials.py --document`): the PE32+
     checks and the stick as 7c; then **TRIALS.md parsed cold** by
     `trials.py` — the cue table (eight rows of ten, the two constraints
     re-checked by the parser, not assumed), the two orders, the box
     geometry's rule, the note formats, the serial rule, the obs table
     (offsets, names), mode 5, the verdict rule — and **the two worked
     examples reproduced byte for byte**: example A, one scripted
     sitting's exact notes (93 lines) and the table `trials.py` prints
     from them; example B, three sittings written as their `sitting`,
     `block` and `done` lines only (27 lines) and the verdict line. Green
     at item 4.
   - **Test 2** (`checktrials.py --row`), one boot at `-smp 4`, a fresh
     disk, a fresh stick copy, the relay and the mock up for the one grow:
     the boot lines as the frozen 7c checker judges them
     (`check_boot_lines` blank, the `i8042:` pair — the count is the
     pattern list's length; the spec's "twenty-two" is nineteen `S7:`
     lines, the `i8042:` pair and `S7: mouse ready`); `! test app` ⏎
     (`wait_record` 1, 150 s), Tab (the prompt has the keys: the four-item
     row), `! trial` ⏎ → the conversation's last lines `! trial`,
     `an app is running`; obs: `mode 3`, `errors 1`, `trial_sitting 0`; the
     notes partition holding nothing of the trial; Esc; then `! trial` ⏎
     → serial `trial: sitting 1 ABBA BAAB`; a screendump with the arrow
     parked: `check_mode_field` `trial A 1/8`, `check_choices` with the
     four-item text (row `R−1` blank — ring 6c's row to the pixel), the
     conversation's last lines `! trial`, `click: grow`; obs: `mode 5`,
     `trial_block 1`, `trial_layout 0`, `trial_cue 1`, `trial_target 1`,
     `cue_pending 0`, `cue_stamp` non-zero; then block 1 played by the
     human (ten cues, no misses); during block 2 (B): the mode field
     `trial B 2/8`, **the choices surface's bytes equal to TRIALS.md's
     box cells for C = 120** (`read_surface` on the descriptor) **and the
     screendump's two rows equal to their inverse rendering** — the
     checker's `inverse_cell(font, ch)` is `render_cell` with the two
     colours swapped, `0xA0` the solid cell — with the arrow parked;
     `trial_layout 1`; quit. The disk is this test's own; nothing more is
     asserted of it. The `no mouse` refusal is deviation 3's probe.
   - **Test 3** (`checktrials.py --sitting`), five boots at `-smp 4` from
     one stick copy on one fresh disk, nothing listening on any port
     (asserted). **Boot 1:** `! trial` ⏎, `SCRIPT_1` to `done`. Judged: the
     notes partition holds **exactly** `notes_of(SCRIPT_1)` — every
     non-hit line byte for byte, every hit line's five fixed fields and
     its ms inside `[d + OFFSET − 60, d + OFFSET + 60]` (a per-hit sanity
     window, twice the median's), every block line's median inside the
     spec's window; the `trial:` lines on serial, in order, equal to
     `serial_of` of those notes with the same windows; the wire after
     `ready` with those lines and the mouse line stripped equal to
     `! trial\r\n`; the obs page at each of the seven rests (`trial_block`
     = the block just finished, `trial_cue 0`, `trial_hits 10`,
     `trial_misses` the script's, `mode 5`, `trial_layout` the order's)
     and at `done` (`mode 0`, `trial_sitting 1`, `layout_default 0`,
     `notes` = the count of notes, `clicks` and `packets` = the model's,
     `hits 0`); the app panel's cells equal to `table_of(notes)` (row 0
     the sitting line, rows 1–8, the rest blank — `check_panel_cells`);
     the mode field `prompt`; the row layout A. **Boot 2**, the same disk:
     `S7: notebook N notes` with N = the count of boot 1's notes (from the
     list, not typed); `! trial` → `trial: sitting 2 BAAB ABBA`;
     `SCRIPT_ABORT`: blocks 1–2, three cues of block 3, Esc → the notes
     grow by exactly `notes_of(SCRIPT_ABORT)` (the sitting line, blocks
     1–2's lines, block 3's three hit lines, `trial sitting 2 aborted 3`);
     the panel's table: the sitting line, two block rows, `aborted 3`;
     `mode 0`. **Boots 3 and 4**: `SCRIPT_3` then `SCRIPT_4`, sittings 3
     and 4 to `done`; after boot 4 the notes end `trial sitting 4 done`,
     `trial verdict B`; the panel's row 9 `verdict B`; serial
     `trial: verdict B`; obs `layout_default 1`; the row **layout B** with
     two boxes at the prompt. **Boot 5**, the same disk, no trial: the
     lines, the row layout B to the pixel and to the surface byte, `mode
     0`, `layout_default 1`; **`trial verdict A` typed and Enter** (A1):
     the conversation's last lines `trial verdict A`, `trial is reserved`,
     the notes partition the same list as after boot 4, `errors` one more,
     `layout_default` still 1, the row still layout B; every `done`
     sitting's block lines pass `check_blocks` (A2); then the arrow, a
     click on the `! grow` box's
     middle cell → the serial echo `!` (GLASS.md's rule: `! grow` types
     `!`; the spec's parenthesis says "the launch line" — see deviation 6);
     `hits 1`, `clicks 1`; Esc typed does nothing; and **`trials.py --disk`
     on the image prints the three done sittings' tables and `verdict B`
     equal to what the panels showed**. The time: four sittings of ten
     cues × 8 blocks at ~0.8 s a cue plus seven rests each, about six
     minutes of play and five boots — measured at item 7 and written from
     that run.
   - **Test 4** (`test-7d.sh`'s self-assertions, then `checktrials.py
     --cage`, then the three earlier gates): **(a)** the harness's own
     strings as 7c's (the cage to 9997, the machine, the display, the
     stick and disk helpers, no `esp.img` on any QEMU line, the log
     path under `stage7/out/`); **(b)** the checker's command is
     `checkmetal.qemu_argv` itself, passed through the frozen
     `check_argv_7c`; `twin.DEFAULT_PORT == 9998`, `wire.RELAY_PORT ==
     9997`; **(c)** the payload table as a subprocess, exit 0 and `0
     wrong`, plus the spot checks held as data: the four new paths'
     freeze cases (`Write`, `Edit`, `sed -i`, `>`, a heredoc) denied,
     running them allowed; **(d)** `./stage7/test-7c.sh`, `./stage7/test-7b.sh`
     and `./stage7/test.sh` run in turn from `test-7d.sh`, each exit 0
     required, their output in the log — the same source assembled by the
     same builder, so the same binary: layout A at the prompt byte-identical
     to the row those gates assert. Their cost, from `CLAUDE.md`: about
     two, five and eight minutes. Green at item 8.
   Test 5 is Wajira's, the spec's own: sitting 1 in the windowed twin,
   sittings 2 and 3 on the HP by METAL.md's day (one flash of the ring's
   stick, then boots only); his word on each; the verdict on the third
   closes the ring.
9. **`stage7/trials.py`** (item 3, frozen at item 8), standard library
   only, imports `metal` and `checkdisk` for the disk: `parse_trials_md(text)`
   → the document's data (the cue table, the orders, the box rule's
   constants, the formats, the obs table, the verdict rule's numbers —
   each read from the document's own tables and code fences, the parser
   failing loudly on any shape it does not know); `cue_sequence(block)`,
   `order(sitting)`, `layout(sitting, block)`; `boxes(C, items)` → the
   spans, the gaps and the label columns; `box_cells(C, items)` → the two
   rows' bytes; `notes_of(script)`, `serial_of(note)`, `parse_note(text)`,
   `table_of(notes)` (per sitting: the rows the panel shows),
   `check_blocks(notes)` (A2: every block line's median recomputed from
   its ten hit notes by the rule and compared exactly; a disagreement
   names the sitting, the block and both numbers, and `--disk`,
   `--serial` and test 3 fail on it),
   `verdict_of(notes)` (the rule; `None` before twelve pairs); `median(ms)`;
   `mode_word_7d(obs)`; `parse_obs_7d(page)` (the 6c parser plus decision
   4's fields, `OBS_PAGE_BYTES_7D = 0x360`); the modes `--example` (both
   worked examples reproduced, exit 1 on a byte's difference), `--disk
   <img>` (DISK.md's table, the notes partition, the tables and the
   verdict), `--serial <log>` (the `trial:` lines back into notes, then
   the same — the HP's chart). Every constant in it is read from TRIALS.md
   at import, so the document and the tool cannot drift.
10. **The probe method** (item 7, the kickoff's C). The implementation of
    decisions 3, 4 and 5 is **drafted on a private copy of the source**,
    `stage7/out/probe7d/stage7.asm`, assembled and packed there by a copy
    of the builder pointed at that directory, its stick copied over
    `stage7/out/stick.img` (scratch, gitignored, rebuilt by every gate);
    then `checktrials.py --row` and `--sitting` are run against it
    directly, their output into `gate-7d.log`. From that run the checker
    receives: `OFFSET` (decision 6), the ready window, the settle after
    `ready` on a full notebook, each boot's `timeout`, the sitting's wall
    time, the serial file's latency — each as a named constant with the
    run's date in its comment. A second private copy with the mouse's
    reset answer forced to "none" proves the `no mouse` refusal and its
    empty journal (deviation 3), quoted in `HANDOVER.md`. **Nothing of the
    probe is committed** but the checker's constants and the handover
    record; `stage7/stage7.asm` is untouched at item 7's commit (`git
    diff --stat` shows the checker and `HANDOVER.md`). Items 10 and 11
    then bring the same code into `stage7/stage7.asm` in two reviewed
    commits, the regressions green at each.
11. **The freeze boundary** (item 8): `stage7/TRIALS.md`, `stage7/test-7d.sh`,
    `stage7/checktrials.py`, `stage7/trials.py` into `PROTECTED`, with the
    hook's comment saying why each is a criterion or a criterion's parser.
    Not frozen: `stage7/glass-7d-section.md` (the owner appends it to a
    frozen file; the copy is paperwork), `stage7/stage7.asm`,
    `stage7/mkimage.sh`, `stage7/mkstick.py`, `stage7/plan-7d.md`. No broker
    module is new: the one mock this ring starts is `broker/wire.py --mock`,
    frozen at ring 7b. `payloads.py` gains `FROZEN_7D` with `freeze_cases`
    on the four paths, the `write`/heredoc/`sed -i` denials, and the
    allowances measured at item 1 (running the gate, the checker's four
    modes, `trials.py`'s three modes, the log redirection, `Write` on the
    asm, the builder, the section file and the plan, `stage8/TRIALS.md`,
    the scratch wipe, `git add` of the four paths and the hooks, the
    ring's words in prose). 0 wrong or exit 1; immediacy shown live with
    one denied call on the checker.
12. **The prose the hook will dislike.** From item 8 `TRIALS.md`,
    `trials.py`, `checktrials.py` and `test-7d.sh` are frozen basenames in
    the prose rule; commit messages by `-F` from a file written with the
    Write tool; edits to the section file, `HANDOVER.md`, `CLAUDE.md` and
    `README.md` by the Write and Edit tools.
13. **The windowed run** (test 5's sitting 1; `CLAUDE.md`'s build block,
    `HANDOVER.md`'s Next action) is the spec's own — the 7c shape, three
    terminals, the stick copy over USB, the relay on 9997 — with one
    sentence added: type `! trial` at the prompt; a sitting is eighty
    clicks and seven rests; Esc abandons it. On the HP, `python3
    stage7/trials.py --serial stage7/out/metal.log` prints the sitting
    from the chart.
14. **Carried:** everything Stage 7 carried (the PHY speed after a reset,
    TIPG, WIRE.md's halting sentence, the nineteen-line first boot never
    watched on the metal, the x2APIC and trampoline paths); the trial's
    clock is the TSC calibrated once against the PIT; no acceleration; a
    sitting in the twin measures QEMU's pointer path too — the sitting line
    does not say where it ran (deviation 7).

## What only a run can give, and what the spec fixes by rule

**By rule (TRIALS.md's, computed by `trials.py`, never typed):** the cue
sequence per block; the layout per block; the note text of every event
but a hit's ms; the serial line of every note; the count of notes a script
leaves (the length of `notes_of`); `S7: notebook N notes` on the next boot
(that length); each block's expected median (the scripted delays through
`median`, plus `OFFSET`); the verdict (the rule over the scripts); the
table's rows; the box cells for C = 120; the mode word; the sitting number
and the order; `clicks`/`packets` (the model's events, `expected_counts`);
`SLACK_MS = 30` (the spec's number).

**From a run, at item 7, never from arithmetic:** `OFFSET` (the median of
recorded ms minus scripted d over a sitting — the pointer's own path on
this host); the per-hit sanity window's width (CC's own, set from the
run's spread, its value and reason in the constant's comment — A3; the
median's ±30 ms is the spec's and is never widened: a spread it cannot
hold stops the item and goes to the owner); the ready window; the settle after `ready`
with a full notebook; every boot's `timeout`; the poll interval; the
sitting's wall time. Each is a named constant with its date; the run's
numbers are quoted in `HANDOVER.md`'s environment table at item 7.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are expected green at its commit and
  which are red by design**. Items 0–3 have no ring 7d test; items 4–7
  commit with test 1 green and tests 2–4 red by design; item 8 turns test
  4 green (the freeze; the three earlier gates already green on the
  unchanged binary); item 9 changes no test; item 10 keeps tests 2–3 red;
  **item 11 turns tests 2 and 3 green**; from item 11 all four must be
  green before the commit.
- **Which items run which earlier gates** (the kickoff's F): the three
  Stage 7 gates (`./stage7/test-7c.sh`, `./stage7/test-7b.sh`,
  `./stage7/test.sh`) run **once** before the item 8, 10, 11 and 12
  commits — at items 8, 11 and 12 inside `test-7d.sh`'s test 4 only, at
  item 10 on their own because tests 2 and 3 are red by design there (A4);
  the three ring 6 gates and Stages 0–5 on
  their own binaries before the item 12 commit. Items 7's probe binaries
  are never the repository's, so no gate runs on them but this ring's
  checker modes. Each gate needs 9999, 9998 and 9997 free; no two at once.
- Every gate run, and every direct run of the checker, writes to
  `stage7/out/gate-7d.log` (the kickoff's I); the chat carries **one line
  per test** — the `PASS`/`FAIL` line — and the log's path.
- `HANDOVER.md` is updated as we go, with a final pass at item 12; the
  model-and-effort record goes in at item 0.
- Every new fault class earns a CLAUDE.md gotcha line the second time it
  is corrected.
- Temporary probes are never committed and never undone with `git checkout
  --`: copy aside, restore from the copy. Every probe boots a private copy
  under `stage7/out/probe7d/`.
- **The scope guard** governs items 7–12: two honest attempts at any one
  obstacle — a real diagnosis from the serial log, the obs page, a
  screendump or the notes on disk, not a re-run — then stop, record the
  exact state in `HANDOVER.md`, commit that, and wait for Wajira. A frozen
  file that needs to change is never edited: the diff is written unapplied
  under `stage7/out/`, recorded, and the owner applies it.
- **Everything runs inside QEMU with the caged network, the VGA device at
  1920x1080, the IvyBridge CPU, the stick over `qemu-xhci`, the SATA disk
  on `ide.1`, the PS/2 mouse driven through the monitor.** The only disks
  are raw files under `stage7/out/` (the gate's under `stage7/out/trials/`,
  the probe's under `stage7/out/probe7d/`, the one mock's twin under
  `stage7/out/trials/rehearsal/twin/`). The mock and the relay bind
  `127.0.0.1` only. CC never spells a `/dev` path, never runs `dd`, never
  flashes anything. Nothing outside the repo is written, bar scratch files
  in the session temp directory. **No real Claude call is made by this
  session**; test 5 is Wajira's.
- If the owner says the session budget is nearly spent: finish the current
  item, commit, record the exact state in `HANDOVER.md`, stop.

---

# Part 1 — the document, the tool and the acceptance machinery, written before the code

## Item 0 — this plan committed; ring 7d opened in HANDOVER

Copy this file verbatim to `stage7/plan-7d.md`. The first act after the
gate opens. In `HANDOVER.md`: the "Where we are" table's **Stage** (7d, the
trials, opened 22 September 2026; the spec approved with all seven
decisions), **Status** (no ring 7d test yet; every earlier gate green on
this machine today on the item 21 binary), **Repo** (`/home/indy/Work/germos`),
**Machine** (mlrig, Omarchy — Arch Linux, kernel 7.2.5), **Toolchain**
(NASM 3.02, QEMU 11.1.1, Python 3.14.7, OVMF, mtools, OpenBSD netcat, xxd,
the `claude` CLI 2.1.278) and **Model** (**Fable 5.1 at medium effort**,
the owner's decision at the kickoff, 22 September 2026) rows; the "Next
action" section gains the ring's opening — ring 7d opened 22 September
2026, the spec approved with all seven decisions, Fable 5.1 at medium
effort, the plan at the gate; a "Ring 7d — the trials" section in the
shape of ring 7c's, with the shape from this plan, an empty test table and
the carried caveats. One commit, the plan and `HANDOVER.md` together.

*Expected at commit:* no ring 7d tests exist yet. Every earlier gate green
(unchanged binary).

## Item 1 — the environment measured: the monitor's clocks, the pointer's photon, the replay's cost, the seams, the hook

The five measurements under "To be measured at item 1", on the closed
binary and private copies under `stage7/out/probe7d/`; the values into
`HANDOVER.md`'s environment table; the poll interval and the first
estimate of the ready window written down before item 4 writes a string.
No source changed; `git diff` shows only `HANDOVER.md`.

*Expected at commit:* no ring 7d tests yet.

## Item 2 — `stage7/TRIALS.md`

Decisions 1–5 and 7's obs table in one text, in GLASS.md's and DISK.md's
manner: the design, the cue table, the orders, the pairs, the sitting
number, the cue, the hit, the miss, the pause and the rest, the measure,
the verdict rule, Esc, the refusals (the reserved prefix `trial ` among
them, A1), **the two corrections of the spec stated plainly** — the obs
fields from `0x2E0` and the zero rule from `0x360` (deviation 1), a click
on `! grow` typing `!` (deviation 6) — the boxes with the twin's example
columns, the inverse cell byte, the note formats, the serial rule, the obs
fields from `0x2E0` and mode 5, the strip's mode word, the app panel's
table, and **two worked examples** — A: the exact 93 notes of one scripted
sitting (a sitting of decision 6's shape with round numbers, computed by
hand from the rules and cross-checked by the item 3 tool before commit)
and the table they give; B: three sittings' `sitting`/`block`/`done` lines
and the verdict they give (B, by ten of twelve with misses 2 against 3);
then "Parsing it cold, in Python" — the functions `trials.py` will hold,
verbatim. Written with the Write tool.

*Expected at commit:* no ring 7d tests yet.

## Item 3 — `stage7/trials.py`

Decision 9 in code, its Python the document's. Proven on the host, no
boot: `--example` reproduces both worked examples byte for byte; a
document with one cue row edited to repeat an item is refused with the
constraint named; the worked example with one block line's median altered
by one is refused with the block named (A2); `--disk` on a formatted 7c disk prints "no sittings";
`--serial` on a scratch log of `trial:` lines prints the same table as
`--disk` on the notes the same lines make.

*Expected at commit:* no ring 7d tests yet.

## Item 4 — `stage7/test-7d.sh` with test 1, the log, and test 2

Decision 8's harness: the log header and `tee`, the port refusals, the
build (`mkimage.sh` then `mkstick.py`), the strings, test 1 (the PE checks,
the frozen `checkmetal.py --stick`, `checktrials.py --document`), test 2
calling `checktrials.py --row` — the checker's first two modes:
`drive_7d` (7c's skeleton with the `play` step), the relay and the mock
lifecycle bound to `stage7/out/trials/` (a transcription of 7c's
`start_relay`/`start_mock` with the paths changed — or the frozen ones
called with their own scratch, whichever item 1's reading of their path
binding allows), the box renderer, the surface check, the row's judgement.

*Expected at commit:* **test 1 green**; **test 2 red** — `! trial` on the
closed binary goes to the mock as a grow (the mock refuses an unknown body)
and no `trial:` line appears; the non-zero exit quoted in the commit
message from the log.

## Item 5 — `checktrials.py --sitting` (test 3), the synthetic human

Decision 6's human and scripts; decision 8's five boots and their
judgements through `trials.py` and the frozen seams; `OFFSET` and the
timing constants as named placeholders **marked to be written at item 7**
(the checker refuses to run while any is unset, so the placeholder can
never pass a boot); `test-7d.sh` gains test 3.

*Expected at commit:* test 1 green; tests 2–3 red (the checker stops at
its unset constants, naming them). The output quoted from the log.

## Item 6 — `checktrials.py --cage` and test 4

Decision 8's (a)–(d): the harness's strings, the argv check through the
frozen `check_argv_7c` on `checkmetal.qemu_argv`, the payload table as a
subprocess plus the spot checks as data, the three earlier gates run in
turn from `test-7d.sh`; `test-7d.sh` gains test 4.

*Expected at commit:* test 1 green; tests 2–3 red; **test 4 red** on (c)
alone — the four paths are not in `PROTECTED` yet (`Write` on them is
allowed today), while (a), (b) and (d) pass.

## Item 7 — the probe: the synthetic human played against a private binary; the numbers read from the run

Decision 10. The trial drafted on `stage7/out/probe7d/stage7.asm` (decisions
3, 4, 5 in full), built there, its stick over `stage7/out/stick.img`;
`checktrials.py --row` and `--sitting` run against it with the unset
constants supplied on the command line for this run only; from the log:
`OFFSET`, the per-hit spread, the ready window, the settle, the timeouts,
the sitting's wall time — **written into `checktrials.py` as its named
constants, each with the run's date**; the run's numbers into
`HANDOVER.md`'s environment table. The `no mouse` probe (deviation 3): the
second copy with the reset answer forced, `! trial` → `no mouse`, the
journal empty, quoted. The probe removed from the checker's path
(`stage7/out/stick.img` rebuilt by `mkimage.sh` and `mkstick.py` from the
repository's source before the commit's gate run). Two honest attempts if
the probe misbehaves; the scope guard.

*Expected at commit:* test 1 green; tests 2–4 red on the repository's
binary (the probe is not it) — the checker's constants are now set, so
tests 2 and 3 fail on the missing `trial:` line, not on a placeholder;
`git diff --stat` shows `stage7/checktrials.py` and `HANDOVER.md` only.

## Item 8 — freeze the ring 7d acceptance machinery — TEST 4 GREEN

Decision 11: `PROTECTED` grows the four paths; `payloads.py` gains
`FROZEN_7D`; the table re-run whole, 0 wrong; immediacy shown live with
one denied call. Then test 4 whole — the payload table green, the three
Stage 7 gates green on the unchanged binary through `test-7d.sh` — from
the log. Commit message by `-F`.

*Expected at commit:* test 1 green; **test 4 green**; tests 2–3 red by
design; the payload table 0 wrong.

## Item 9 — `stage7/glass-7d-section.md` — then stop for the owner's hand

Decision 7, written with the Write tool, committed alone. **The session
then stops**: it tells the owner the section is at
`stage7/glass-7d-section.md`, to append it with `cat
stage7/glass-7d-section.md >> stage6/GLASS.md` from his own terminal and to
commit that by his own hand, and waits until he says it is in before the
next commit. Nothing else is touched meanwhile.

*Expected at commit:* as item 8.

---

*Everything above is written before any guest code exists in the
repository. Everything below is the code and the documents.*

---

# Part 2 — the implementation

## Item 10 — the guest: the reserved word, mode 5, the sitting on layout A

Decisions 4 and 5 into `stage7/stage7.asm` from the probe: the compare in
`bang_line`, `trial_start` and the four refusals, the reserved prefix's
refusal `trial is reserved` in the Enter path beside it (A1), mode 5 and its strip
word, the obs fields, `cue_pending`/`cue_stamp` in the glass core's frame,
`trial_step` in the main loop, keys dropped and Esc in `handle_key`,
`trial_press` in `click_dispatch`, the notes through `notebook_append`, the
raw serial lines, the pause and the rest, the block's median, the table in
the app panel, `done`, the abort, the verdict scan and its note, the
sitting-count scan, the verdict read at boot into `layout_default` (the
row itself still drawn as A — layout B is item 11). Probed on a private
copy first: a sitting to `done` at `-smp 2`, `4` and `8`, the notes read
by `trials.py --disk`; then **`./stage7/test-7c.sh`, `./stage7/test-7b.sh`,
`./stage7/test.sh` green on this binary, run on their own** (A4: tests 2
and 3 are red here, so test 4's run is not taken) — nothing they see has changed:
no `S7:` line, the row, the strip in modes 0–4, the page to `0x2D8`.

*Green at commit:* tests 1 and 4; **tests 2 and 3 red** on layout B's
pixels and surface bytes alone (block 2's row, boot 5's row) — said in the
commit message from the log. The three Stage 7 gates green.

## Item 11 — layout B, and the default from the notebook — TESTS 2 AND 3 GREEN

Decision 3: the inverse cell in `draw_cell`, `choices_update`'s box path
(the spans, the gaps, the labels, the hit table) taken during a B block
and, outside a trial, when `layout_default` is 1; the row blank during a
rest. Probed on a private copy (a B block's row read back through the
surface and a screendump; a verdict written to a disk from the host by
NOTEBOOK.md's format and the row taking layout B on the next boot); then
the gate whole — its test 4 is the one run of the three Stage 7 gates for
this commit (A4).

*Green at commit:* **all four automated tests.** The full `./stage7/test-7d.sh`
output in the log, its `PASS` lines in the commit message; **the whole
gate's wall time recorded here and written into `CLAUDE.md`'s build block**
(A4). The three Stage 7 gates green inside it.

## Item 12 — HANDOVER, CLAUDE.md, README, the windowed run

`HANDOVER.md` to the green-pending-oracle state (what was built, the
numbers on this build — `OFFSET`, the sitting's time, the binary's size,
the gate's time — tests 1–4 green from the log, test 5 pending with the
windowed run and the HP's day, decision 14's caveats); `CLAUDE.md`'s build
block gains `./stage7/test-7d.sh` and `python3 stage7/trials.py`, the
windowed run gains its one sentence, the gotchas gain what bit twice (none
is owed yet; candidates from the probe are recorded in HANDOVER and
promoted only at a second correction); `README.md`'s Stage 7 paragraph and
running section gain ring 7d; `python3 .claude/hooks/payloads.py` re-run,
0 wrong; the gate whole (its test 4 the one run of the three Stage 7
gates, A4); the three ring 6 gates and Stages 0–5 on their own binaries;
the commands for the owner's sitting 1 printed; stop.

*Green at commit:* all four automated tests (the three Stage 7 gates
inside test 4), the three ring 6 gates, Stages 0–5.

## Test 5 — Wajira's

The spec's: sitting 1 in the windowed twin with mlrig's mouse grabbed;
sittings 2 and 3 on the HP with the PS/2 mouse by METAL.md's day, one flash
of the ring's stick; his word on each sitting; the verdict on the third
closes the ring. He may add sittings before the verdict only by amending
the spec first.

---

## Verification

- **Automated:** `./stage7/test-7d.sh` from the repo root — refuses to
  start if anything listens on 9999, 9998 or 9997; appends everything to
  `stage7/out/gate-7d.log` under a dated header; builds the image and the
  stick; tests 1–4 (the document and the tool; one boot for the refusal and
  both layouts' rows; five boots for the sittings, the abort, the verdict
  and the default; the strings, the argv check, the payload table, the
  three earlier gates). Exit 0 only if all pass. Run before every commit
  from item 11 on; its time recorded from the item 11 run.
- **Regression:** the three Stage 7 gates once before the item 8, 10, 11
  and 12 commits — inside test 4 at 8, 11 and 12, on their own at 10 (A4);
  the three ring 6 gates and Stages 0–5 before the item 12 commit.
- **The hook:** `python3 .claude/hooks/payloads.py` at items 8 and 12 —
  every case from every stage, 0 wrong; immediacy demonstrated live.
- **The probes:** items 1, 7, 10 and 11 each state their expected output
  and quote it in the commit message from the log.
- **Manual (test 5):** Wajira, one sitting a session; the verdict on the
  third closes the ring.

## Safety

Everything CC runs is inside QEMU or on the host's loopback. Firmware, the
IvyBridge CPU model, the VGA device, the stick as a raw file over
`qemu-xhci`, exactly two drives per guest of the gate's own — a copy of
`stick.img` and a raw 64 MB disk on q35's AHCI, both under
`stage7/out/trials/` (the probe's under `stage7/out/probe7d/`, the one
mock's twin under `stage7/out/trials/rehearsal/twin/`) — created by the
harness, the mock or the probe. The storage bodyguard is untouched this
ring (no new word, no new spelling): every planned command was read
against its rules before this plan. CC never touches `/dev`, never runs
`dd`, never flashes; the flash for sittings 2–3 is the owner's hand by
METAL.md. The network is a cage in every QEMU line, landing on `127.0.0.1`
— the relay on 9997 for one boot, nothing at all for the rest; the mock
binds `127.0.0.1` only, frozen. The gate refuses to run if anything else
holds any of the three ports. The guest's changes touch no driver, no
frame, no wire, no rehearsal, no germline, no home image: a compare in
`bang_line`, a mode, sixteen page words, a stamp in the frame, a poll in
the loop, notes through the existing append, lines through the existing
raw write, one branch in `draw_cell`, one path in `choices_update`. This
session makes no Claude call. Every existing frozen file is untouched —
`git diff --stat e010fbb -- <every PROTECTED path>` is empty at every
commit — and every earlier gate is green at the end of the ring.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| A count or a median in the frozen checker is wrong (the three freeze openings' class) | every count is a list's length or a rule's output through `trials.py`; the medians are the scripted delays through the document's `median` plus one measured constant; the only literals from a run are named, dated, and taken at item 7 before the freeze |
| The monitor's latency or the host's scheduling blows the ±30 ms window | the human's hand is on the target before the cue (decision 6), so the recorded time is the scripted delay plus a small constant; the median is robust to a few slow hits; item 1 measures the clocks and item 7 the spread before anything is frozen; **the window is the spec's and CC never widens it** — a spread it cannot hold stops item 7 at the commit boundary, the spread goes into `HANDOVER.md`, and the owner decides (A3) |
| A guest median off by one passes the ±30 ms window | `check_blocks` recomputes every block's median from its ten hit notes and demands equality with the block line (A2) |
| A typed note forges a trial line | the prefix `trial ` is refused at the prompt, journaled nothing (A1), proven in boot 5 |
| The obs page read through `xp` takes longer than a rest | the page is read once per rest (2 s) and item 1 times one read; the read is issued the moment the block line lands |
| The boot replay of a full notebook delays the prompt past the checker's settle | item 1 measures 300 notes' replay; the settle is written from it; the checker waits for the prompt's row, not a fixed sleep, where the frozen helpers allow |
| A press lands before the cue's frame is painted | `cue_pending` 1 is "no cue": counted and nothing more (decision 1); the human's earliest press is 500 ms + 120 ms after the hit |
| The serial `trial:` line lands inside a typed echo | no line is typed during a sitting (keys are dropped); `! trial`'s echo is complete before the sitting line; the checker strips the lines by their prefix as it strips the mouse line |
| A frozen gate goes red on this binary | no `S7:` line changes; the row, the strip in modes 0–4 and the page to `0x2D8` are untouched; layout B needs a verdict on the disk or a B block, and no earlier gate has either; the three gates run before every guest commit |
| The frozen twin sees an inverse cell | its disk is formatted fresh per rehearsal (no verdict) and it never types `! trial`; `cell_pixels` on a byte at or above `0x80` is read at item 1 to know what would happen if it did |
| `hit_table` overflows | `HIT_MAX` is 5 and the row never shows more than five items (Hick); the boxes are one entry each |
| The `no mouse` refusal cannot be reached in the twin | deviation 3: proven on a probe copy at item 7 and quoted; the code path is three instructions beside the mode-3 refusal the gate does prove |
| The verdict rule meets an aborted sitting | decision 1: the first three `done` sittings; test 3 plays exactly that shape |
| A frozen file needs to change | the scope guard: stop, the diff unapplied under `stage7/out/`, the owner's hand |
| The gate spends a token | the triple port refusal; `wire.py --mock` for one grow; the trial itself sends nothing; the record check demands the mock's one call |

---

## Deviations from the spec and the kickoff, for approval

Each argued from a measured fact or a frozen file. Everything else is the
spec as written.

1. **The obs fields start at `0x2E0`, not `0x2C0`, and the zero rule holds
   from `0x360`, not `0x340`.** DISK.md (frozen) already holds
   `ahci_cap`, `ahci_pi`, `ahci_port` at `0x2C0`–`0x2D0` and the guest
   writes them; `0x2D8` stays zero for alignment. Sixteen words, as the
   spec counts them.
2. **The sitting number counts sitting-start notes only** (`trial sitting
   <n> <order>`), not every note beginning `trial sitting` — `done` and
   `aborted` begin the same way and would count a sitting three times.
3. **The `no mouse` refusal is proven by a probe, not by the frozen gate.**
   QEMU's q35 has no way to remove the PS/2 mouse and keep the keyboard
   (`i8042=<bool>` removes both; measured). Test 2 proves the mode-3
   refusal (`an app is running`), the guest's refusal path shared by both;
   the `no mouse` branch is exercised on a private copy with the reset
   answer forced at item 7 and quoted in `HANDOVER.md`; the code is three
   instructions.
4. **The verdict is over the first three sittings that ended in `done`;
   an aborted sitting's blocks stand on the record but outside the
   verdict; one sitting a boot is enforced; after a verdict `! trial`
   refuses.** The spec's "twelve pairs" needs three complete sittings and
   says "the completed blocks stand" of an abort; this is the reading that
   keeps n = 12 and the sign test's p where the spec put it. Said in
   TRIALS.md so the rule is pre-registered.
5. **"The strip's inverse colours" is read as the inverse of the strip's
   colours** — background-coloured glyphs on foreground fill — because
   the strip is drawn foreground-on-background like every surface (no
   inverse exists in the renderer or in GLASS.md). One new cell byte
   (bit 7) carries it, confined to layout B.
6. **Boot 5's click on `! grow` asserts what GLASS.md's rule gives** — the
   press types `!` (the serial echo `!`, the prompt line holding `!`) —
   not "the launch line": `! grow` is a key item, and only an installed
   app's item types a launch line; test 3's disk has no installed app
   (nothing was grown on it). The ring 7c gotcha says to read the ring's
   own rule before writing the expectation, and this is it.
7. **The sitting line does not name where the sitting ran.** The spec's
   decision 5 says the serial line names it; the note format the spec
   fixes (`trial sitting 1 ABBA BAAB`) has no field for it, and NOTEBOOK.md
   is unchanged. The owner's record (HANDOVER, his word at test 5) says
   which sittings were in the twin; the analysis does not mix them unless
   he says so — that is a decision he makes reading the record, not a byte
   the guest writes. If he wants the byte, it is a spec amendment before
   item 2.
8. **Test 3 is five boots, not the spec's implied three** — one sitting a
   boot (deviation 4) makes sitting 1, the abort, sittings 3 and 4 and
   the no-trial boot five; sitting 1's script already favours B so that
   the three `done` sittings are 1, 3 and 4.
9. **Test 4 runs the three earlier gates from `test-7d.sh`** (about fifteen
   minutes) rather than asserting their greenness by hash: the spec says
   "green on the ring's binary", and running them is the only honest
   meaning. The gate's whole cost is measured at item 11 and written into
   `CLAUDE.md`.
10. **The synthetic human pre-positions during the pause** (decision 6),
    so the recorded time is the scripted delay plus a measured constant;
    the spec's "reads the obs page for the cue, waits a scripted delay,
    moves and clicks" would put the monitor's page-read latency (hundreds
    of milliseconds, variable) and a distance-dependent move inside every
    recorded number, and the ±30 ms window could not hold. The page is
    read at every rest and at `done`, as the spec's assertions need; the
    per-cue trigger is the guest's own `trial:` line on serial.
11. **The mock and the relay are up for one boot** (test 2's grow of `test
    app` for the mode-3 refusal), nothing listening for every other boot.
    The kickoff's G says the mock is up because the boot expects a link;
    the link is the e1000e's PHY, which needs nothing on the host (7c's
    test 2 boots prove it), so the honest shape is: up only where a
    request is made, and asserted down everywhere else.
12. **The probe binary at item 7 is the draft of the implementation**,
    kept in `stage7/out/probe7d/` and never committed, so that every
    number is from a run and the four files freeze before any guest code
    enters the repository (the kickoff's B and C together); items 10 and
    11 commit that code in two reviewed pieces with the regressions green
    at each. Said plainly: the code exists on disk before the freeze, in
    a gitignored directory, and the freeze protects the criteria from it.
13. **The GLASS.md section item (9) comes after the freeze and before the
    guest code**, so the owner's append precedes the first guest commit
    and the document the assembler implements is complete in the frozen
    file before the code lands; the session stops there as the kickoff's
    E requires.
14. **`stage7/checkmetal.py --stick` is reused for test 1's stick half**
    (a frozen checker run as it is) rather than transcribed, and the
    checker's QEMU command is `checkmetal.qemu_argv` itself, so 7c's argv
    check holds by construction.

---

## Amendments — Cowork's review, adopted before approval

Cowork reviewed the plan on 22 September 2026 and approved it with four
amendments, A1 blocking; all four are adopted here. All fourteen deviations
are accepted as argued; **deviations 1 and 6 correct the spec, and
TRIALS.md states both plainly at item 2.** Where an amendment contradicts a
decision, a deviation or an item above, **the amendment governs**; the
body of the plan is left as written so the review can be read against it.

**A1 (blocking) — the prefix `trial ` is reserved on the notebook**
(decisions 1, 2, 4, 5, 7; items 2, 9, 10; test 3). A typed line whose
first six bytes are `trial ` is refused at the prompt with the console
line `trial is reserved`, counted in `errors`, and journaled nothing,
exactly as the reserved-word refusals are — the check sits in
`handle_key`'s Enter path beside `parse_marker`, before the note path,
implemented at item 10 beside `trial_start`. Reason: decision 5's scans
cannot tell a typed note from a trial note, so a typed `trial verdict B`
would set `layout_default` at the next boot and a typed `trial sitting 1
ABBA BAAB` would miscount the sitting number. The rule is stated in
TRIALS.md at item 2 (the refusals' list gains it) and in the GLASS section
at item 9 as one sentence of supersession of NOTEBOOK.md's "any typed line
is a note". **Proven in test 3's boot 5:** type `trial verdict A` and
Enter; assert `trial verdict A` then `trial is reserved` as the
conversation's last lines, the notes partition unchanged (the same list as
after boot 4, its length the journal count), `errors` one more, obs
`layout_default` still 1, and the row still layout B to the pixel — before
the click on `! grow`.

**A2 — `trials.py` recomputes every block's median from its ten hit
notes** (decision 9; items 3 and 5; test 3). `table_of(notes)` (or a
`check_blocks(notes)` beside it) recomputes each block's median from that
block's ten hit notes by TRIALS.md's rule and compares it **exactly** with
the median field of the block line; a block line that disagrees with its
own hits is reported by `--disk` and `--serial` (the sitting, the block,
both numbers) and fails test 3's judgement of every `done` sitting. Item
3's proofs add the worked example with one block line's median altered by
one, refused with the block named. This is a rule-derived exact check, not
a run number, and it is the only thing that catches a guest median off by
one — the ±30 ms window cannot.

**A3 — the ±30 ms window is the spec's number and CC never widens it**
(decision 6, "What only a run can give", item 7, the risks table). If the
item 7 run shows a spread the window cannot hold, stop at the commit
boundary, record the measured spread in `HANDOVER.md`, and wait for the
owner: it is a spec question. The per-hit sanity window (±60 ms in decision
8) is CC's own and may be set from the run at item 7, its value and its
reason in the constant's comment. The sentence in "What only a run can
give" that allowed the sanity window to be "widened only if the run shows
the spread is larger" applies to that window alone, never to the median's.

**A4 — the three Stage 7 gates run once per commit, not twice**
(conventions, items 10–12, verification). At items 11 and 12 they run
inside `test-7d.sh`'s test 4 only; the convention "before the item 8, 10,
11 and 12 commits" is satisfied by that run. At item 10 they run on their
own, since tests 2 and 3 are red by design there. At item 8 test 4 runs
them. **The whole gate's wall time, measured at item 11, goes into
`CLAUDE.md`'s build block** beside the boot count.
