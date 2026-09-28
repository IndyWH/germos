# Ring 8t — trial two · implementation plan

**For the plan gate.** Written by CC on **Opus 5.5 at high effort** (spec
decision 11, recorded at item 0), in plan mode, 28 September 2026. It
implements `trials/spec-trial2.md`: approved 27 September 2026 at `beef2da`,
with all twelve decisions as recommended, and **Amendment 1** of 28
September 2026 (Enter starts sittings 2 to 4, the `saved` line, the boot's
due line). Nothing below is built until the owner approves after Cowork's
review. At item 0 this file is copied verbatim to `trials/plan-8t.md`.

**Read for this plan:** CLAUDE.md; HANDOVER.md (Where we are, ring 8a's
test 5 and closure, Next action); `trials/spec-trial2.md` whole;
`stage7/TRIALS.md`, `stage7/spec-7d.md`, `stage7/plan-7d.md`; GLASS.md's 7d
section; `stage8/spec.md` with the ring 8t line; `stage8/PARTS.md`,
`stage8/SEED.md`, `stage8/seed-record.md`, `stage8/HP-8a.md`,
`stage8/plan-8a.md`; the shapes of `stage7/test-7d.sh`,
`stage7/checktrials.py`, `stage7/trials.py`, `stage8/test-8a.sh`,
`stage8/checkmolt.py`, `stage8/parts.py`; the trial code in
`stage8/stage8.asm` and the AHCI and molt paths in `stage8/loader.asm`
(read only); the HP charts in `history/`.

---

## Context

Ring 7d's trial chose A by a rule that Cowork's review found honest but
underpowered. Trial two asks one new question: **does the painted box
itself help this human?** It compares **layout G** (B's zones, labels and
targets, drawn as plain text with `|` separators) with **layout B** (the
boxes). The rule is R1 on a block score, trimmed mean plus 100 ms a miss,
over 16 pairs in four sittings of 8 blocks × 20 cues, with a 10-cue
warm-up. Times are hidden until the verdict. The verdict sets the
machine's default row: G or B, never A again.

It runs as **ring 8t**, between 8a (closed today) and 8b, on the generic
`i8042` driver throughout. Every human sitting is on the HP with its PS/2
mouse. The twin is the automated gate only. The guest code goes into
`stage8/stage8.asm`, which is unfrozen. `stage8/loader.asm` stays frozen
and untouched. The new binary is **seed 2** by SEED.md.

**The policy gate:** re-checked by Cowork on 28 September 2026. The help
centre article is unchanged since 16 June 2026, the change is still paused,
and `claude -p` draws from the subscription. Trial two's sittings need no
broker. This ring's gate talks to no broker, and the 8a gate inside its
test 4 talks only to mocks. No real Claude call is made by this session.

### The HP's disk now, and what a new seed does to it

The charts in `history/` say what the HP's notebook holds:
- ring 7c's two typed notes;
- trial one's 275 notes (three sittings, `trial verdict A`), so `S7: notebook 277 notes` at 7d's verdict boot;
- ring 8a's notes: 41 `molt` notes and 37 typed notes, ending with `molt i8042 demoted f0668b687c68cab0 unhealthy`, at **355 notes**.

Its home store holds the calculator and `part-i8042`. The current build of
`part-i8042` is `hang` (`f0668b687c68cab0`); the previous build is `good`
(`4fe6beefc4bc57d0`), because the install of `hang` replaced `good`.

**What a new seed does to an earlier seed's demoted part: nothing.**
PARTS.md keeps a slot's state in its `molt` notes alone, read at every boot
from the journal. It keeps the part in the home store. SEED.md's record
names builds of the seed, and no note, home entry, part header or germline
key (`molt i8042|abi3|<identity>`) names a seed. So seed 2 reads the same
notes as seed 1 and gets the same answer: `i8042 demoted f0668b687c68cab0
unhealthy`.
- **Step 1.** Every boot with a molt note runs the controller's minimal setup, finds and halts the TCO, and prints `S8: sha256 ok`.
- **Step 2.** The evidence bit is read and cleared.
- **Step 3.** The recovery decision finds no slot in shadow or live and the unhealthy run at 0, so it does nothing.
- **Steps 4 and 5.** No Esc window and no door, because nothing is in shadow or live.
- **Step 6.** No part loads, so there is no `molt boot` note and **the watchdog is never armed**.
- **Step 7.** The generic `mouse_init` runs with the seed's `i8042:` pair.

The demoted build stays in the home store. It can come back only by `! molt
undo`, which takes it to shadow, where it must earn the threshold again.
PARTS.md: "a build the watchdog demoted can never become live by undo
alone". **So `! trial 2` finds no part in the pointer's slot and opens
sitting 1.** Test 3 proves it on a twin of this disk (below, "Disk H").

### Environment

Read in this session, before planning:
- NASM 3.02, QEMU 11.1.1, Python 3.14.7, OVMF, mtools, OpenBSD netcat. The `claude` CLI version is read at item 0.
- **The trial machinery in `stage8.asm`:**
  - `bang_line` judges `trial` (3034) and jumps to `trial_start` (6003), whose refusals come in 7d's order;
  - `trial_ended` is the one-sitting-a-boot flag;
  - `line_is_reserved` is the six-byte `trial ` check (5980);
  - `trial_step` is called from `main_loop` and `part_loop`;
  - `choices_update` and `row_to_boxes` draw layout B (5616, 5809);
  - `note_verdict_check`, inside `notebook_replay`, reads `layout_default` at boot (6565);
  - `journal_scan` walks one note per sector read, at `! trial` and at `done` only;
  - `.mode_trial` in `strip_format` prints `'A' + layout`, so G needs its own branch.
- **Notes are written synchronously.** `notebook_append`, then `disk_rw` → `ahci_rw` → `ahci_cmd` (loader), which polls `PxCI` and returns only on success. `ahci_cmd` takes any ATA command in AL, so a FLUSH CACHE EXT (`0xEA`) can be issued from `stage8.asm` with `loader.asm` untouched.
- **Empty Enter today** journals nothing and draws a fresh prompt (`handle_key.enter`, 1055).
- **Every note is drawn at boot.** `notebook_replay` draws each note on the console (NOTEBOOK.md: "every note is drawn on the console on boot"). Trial-two notes carry ms and scores, so **the replay would show the times the spec hides**. Deviation 1 answers it.
- **The obs page:** `0x340`–`0x358` are zero and unused by ring 8a. `0x360` is `molt_overflows`, written only on a part-loaded boot.
- **The i8042 slot's state in guest code** is `ms_slots + SS_KIND`, which `molt_scan` fills at boot and the `! molt` words re-run.
- **No host writer for a home store exists.** Notes reach a disk from the host only as NOTEBOOK.md records after a blank boot (`checkmolt.Fates.new_disk`, `checknotes.expected_record`). `metal.parse_gpt`, `checkplans.parse_home` and `parts.home_of_disk` are the parsers.
- **The 8a gate's test 2** watches only `stage<N>/out/` and `germline/` (`checkmolt.outside_files`). So this ring's log under `trials/out/` may grow while `test-8a.sh` runs inside our test 4.
- **The bare `out/` line in `.gitignore`** already covers `trials/out/`. The spec asks for the explicit line anyway, at item 0.
- **The 8a gate** does not require the build to be the record's current seed. So guest changes keep it green without a new seed line until item 13.

---

## Decisions taken in this plan

### D1. The document: `trials/TRIALS2.md`

Frozen at item 9. It is TRIALS.md's twin in shape: the spec made exact,
with a Python block that `trials2.py` executes. **It supersedes these
sentences and nothing else:**
- **TRIALS.md, the reserved prefix.** A typed line whose first word is `trial`, or `trial` followed only by digits, is refused with `trial is reserved`. The first word is the bytes before the first space, or the whole line.
- **TRIALS.md and GLASS.md 7d, the default read at boot.** The **last verdict note of either family**, in journal order, sets `layout_default`: 0 A, 1 B, 2 G.
- **TRIALS.md, `trial_layout` and `layout_default`** gain the value 2, G.
- **NOTEBOOK.md, the replay.** A note beginning `trial2 ` is not drawn at boot (deviation 1). It is counted as ever: `S7: notebook N notes`, and `n` on the strip.
- **GLASS.md 6a, Enter.** While trial two is in progress on the notebook, Enter on an empty prompt line is `! trial 2` (D5).

**Layout G.** For *n* items on *C* columns, the zones are B's (`w = ⌊C/n⌋`,
the last zone takes the remainder):
- the label on row `R−2` at B's column, in normal colours (no bit 7);
- `|` (`0x7C`) at B's gap column on **both** rows, and no separator after the last zone;
- every other cell of both rows is a space;
- the targets are B's filled spans exactly, so a press on a `|` column does nothing but the count (a miss during a cue).

On the twin at C = 120:
- the four-item row: labels 12–16, 41–46, 71–77, 101–108; `|` at 29, 59, 89;
- the two-item prompt row: labels 27–31 and 87–92; `|` at 59;
- the HP's three-item prompt row (`? ask`, `! grow`, `! calculator`, w = 40): labels 17–21, 56–61, 94–105; `|` at 39 and 79.

These are the rule's numbers. **Item 8's probe reads them back from the
surface and the screendump.** The checker holds the run's values and test 1
asserts they equal the rule's; any difference stops item 8.

G is drawn during a G block and, outside a trial, when `layout_default` is
2, for every row state, exactly as B is for 1.

**The design** (spec §6, exact):
- **Cues and blocks:** 20 cues a block, 8 blocks, **block 0 the warm-up** of 10 cues.
- **Orders:** odd sittings `GBBG BGGB`, even sittings `BGGB GBBG`.
- **The warm-up's layouts:** cues 1–5 in the order's first letter and 6–10 in the other (odd: G then B; even: B then G).
- **The pause** is 500 ms after a hit.
- **The rest** is 5,000 ms after block 0 and after blocks 1–7. There is no rest after block 8.
- **The rest lines** are `warm-up done - rest` after block 0, and `block <b> of 8 - rest` after blocks 1–7.
- **The cue** is `click: <word>`, and the cue stamp is 7d's.

**The cue table.** Generated here under the spec's constraints and checked
by a script: each word exactly 5 times a row, none twice running, and each
word opens exactly two blocks. The warm-up row has each word at least twice,
none twice running, and all four words in each half. This goes into
TRIALS2.md verbatim for Cowork's review now:

```
block 0: ask app grow exit app grow ask app ask exit
block 1: app exit ask grow app grow exit app exit app ask grow exit app ask grow ask exit grow ask
block 2: app exit grow app exit ask grow ask grow app ask exit app ask grow exit ask exit app grow
block 3: grow ask exit ask exit grow exit grow exit app ask app grow app exit app ask app ask grow
block 4: ask exit ask exit ask grow exit grow app ask app grow exit app grow app exit app grow ask
block 5: exit grow ask app exit grow app grow ask grow app ask exit grow exit app ask app exit ask
block 6: grow ask app exit ask app grow ask exit app grow ask exit app exit grow ask exit grow app
block 7: ask exit ask exit app ask grow ask grow app ask grow exit grow app exit app grow app exit
block 8: exit ask grow app grow ask exit grow app ask app exit ask app ask exit grow app exit grow
```

**The score and the rule** (spec §4, in the guest's integers):
- **The block score:** the 20 hit ms sorted; the middle 16 (indices 2–17) summed; `sum / 16` by integer division; plus `100 × misses`.
- **A pair** is blocks (1,2), (3,4), (5,6) or (7,8) of one sitting, one G block and one B block. Its difference is `d = score(G) − score(B)`.
- **The trial** is the **first four sittings that end in `done`**, in sitting order: 16 pairs. Aborted sittings stand outside it.
- **The verdict (A1), decided on S, the sum of the 16 d:** **B if `S > 0`, G if `S <= 0`**. R1's "the mean of d above zero" is the sign of S, and decision 12 sends only an exact zero to G.
- **The number the note carries** is the mean, `S / 16` **truncated toward zero** (`idiv`). It is a record of the size and never enters the decision. So a near-tie reads `verdict B 0` or `verdict G 0` and is visible on the record as one.

**The notes**, all written by the machine, in NOTEBOOK.md's record:

```
trial2 sitting 1 GBBG BGGB        the sitting number, the order
trial2 1 0 G 3 1488               sitting, block (0 = warm-up), layout, cue, ms - a hit
trial2 1 0 G 4 miss               a miss; the cue stays
trial2 block 1 2 B 20 1 1561      sitting, block, layout, hits, misses, score (blocks 1-8 only)
trial2 sitting 1 done
trial2 sitting 1 aborted 3        the block in play; 0 in the warm-up; in a rest, the block that follows
trial2 prefer 1 b                 g, b, n - or skip for Esc at the question (deviation 2)
trial2 verdict B 57               the layout, then the mean (signed, no leading zero; 0 for a tie)
```

**The serial lines:**
- **Mirrors.** Each note goes to raw UART as it is journaled, with `trial2:` followed by the note from its seventh byte (`trial2: 1 0 G 3 1488`). These are never teed.
- **Boot lines** (Amendment 1(c), deviation 7). Two lines are raw and not notes: `trial2: due sitting <n>`, or `trial2: concluded verdict <L> default <L>`. No note's second word is `due` or `concluded`, so a reader never confuses them.

**A sitting's end, in order:**
1. Block 8's note, then `trial2 sitting <n> done`.
2. **The question** `easier? g, b or n` as a console line, before anything else is shown.
   - `g`, `b` or `n` (either case) journals `trial2 prefer <n> <key>`.
   - Esc journals `… skip`.
   - Other keys are counted and dropped. Presses count in `clicks` only. Esc here is a skip, not an abort.
3. The console lines `sitting <n> done` and `hits <h> misses <m>`, counted over blocks 1–8 (deviation 15). No score is shown.
4. **The verdict**, if this is the fourth `done` sitting:
   - the note `trial2 verdict <L> <mean>`, and `layout_default` set;
   - the console line `verdict <L> <mean>`;
   - the app panel cleared and holding **the four judged sittings' tables stacked**. Each table has 11 rows: `sitting n ORDER`, eight block rows `b L 20 m score`, `done`, and `prefer x`. Then the row `verdict L mean`. That is 45 rows in the panel's 63.
   - The row is then redrawn in the verdict's layout.
5. **ATA FLUSH CACHE EXT** through the loader's `ahci_cmd` (deviation 12, A4). The arguments are: AL = `0xEA`; EBX = 0; DL = 0 (no data flows); RDI = a scratch 512-byte buffer in `stage8.asm`'s BSS, which the command never fills. `ahci_cmd` returns only on success. If the disk answers with an error, the owner sees the loader's named `ERR:` line and a halt, with every note of the sitting already written and no `saved` line. Then the console line **`saved - power off when you like`**, then mode 0 and the prompt. Keys and presses made meanwhile are discarded, as after any answer.

**An abort** (Esc in any block or rest):
- the aborted note;
- `sitting <n> aborted <b>` and `hits <h> misses <m>`, with no score and no table;
- the flush;
- the same `saved` line (deviation 6), then the prompt.

**The strip.** Mode 5, and the mode word **`trial2 <L> <b>/8`**, with L the
current cue's layout (`trial2 G 0/8` in the warm-up). That is 12 characters,
padded to 18.

**The obs page.** The 7d words keep their meanings:
- `trial_layout` gains 2 for G;
- `trial_cue` runs 1–20, or 1–10 in the warm-up;
- `trial_block` is 0 during the warm-up.

**`0x340` `trial_number`**, written by the BSP, is 2 from a trial-two
sitting's start to the boot's end, and 0 on every other boot. Trial one
never writes it (deviation 10), so 7d's page rule holds on every 7d check.
`0x348`–`0x358` stay zero. `0x360` stays PARTS.md's `molt_overflows`,
unchanged.

**Worked examples**, each reproduced by `trials2.py --example`:
- **A.** One scripted sitting, with a warm-up miss and a miss in a G and a B block: every note in journal order, and the console lines at its end.
- **B.** Four sittings' block notes to verdict B, with the 16 d values and the mean.
- **C.** Three boundary trials (A1): S = 0 gives `verdict G 0` (the exact tie); S = 15 gives `verdict B 0`; S = −15 gives `verdict G 0`.
- **D.** An aborted sitting, then the first four done sittings to verdict G.
- **E.** A journal holding trial one's notes, molt notes and trial two's notes. The frozen `stage7/trials.py` prints trial one's tables and verdict A from it, unchanged.
- **F.** `--status` on a chart made from A's serial lines prints procedure facts only.

### D2. The tool: `trials/trials2.py`

It is `stage7/trials.py`'s shape. It execs TRIALS2.md's Python block
(frozen names supplied), and cross-checks the prose tables against the code.

| Mode | What it does |
|---|---|
| `--example` | Every worked example, byte for byte |
| `--disk IMG` | The notes partition, by the frozen parsers: every sitting's table, and the verdict or `no verdict: N done sitting(s), 4 needed`. Any block note that disagrees with its own hits, by the score rule, is a `DISAGREES` line and exit 1 (7d's A2) |
| `--serial LOG` | The same from a chart. `trial2:` is found anywhere in a line (ring 8a's finding 9), timestamps are ignored, and boot lines are not notes |
| `--status LOG` | **The blind read for Cowork** (below) |

**`--status LOG`** prints, per boot in the chart:
- the due or concluded line;
- `sitting <n> opened <ORDER>`;
- `sitting <n> done` or `aborted <b>`;
- `hits <h> misses <m>` (blocks 1–8), and `warm-up hits <h> misses <m>`;
- `preference saved`, without the letter (deviation 16);
- `question not answered` when a done sitting has no prefer note.

**It prints no ms and no score** while no `trial2: verdict` line is in the
chart. Once one exists it adds `verdict line present` and then the
`--serial` report.

### D3. The HP's history as a twin disk

A host builder in `checktrials2.py`, frozen with it.

**The notes** are built from the committed charts, each pinned by its
SHA-256 (a changed chart fails loudly):
- ring 7c's two notes as HANDOVER records them;
- trial one's notes from the three 7d sitting charts, each `trial:` line through TRIALS.md's `note_of_serial`;
- ring 8a's chart in order: each `molt:` line as `molt ` plus the line from its sixth byte, and the owner's typed notes where the chart's echo gives them. `!` and `?` lines are skipped and backspaces applied.

**The builder must reproduce every `S7: notebook N notes` checkpoint** on the
charts: 2, 93, 184, 277, 277, 278, 288, 296, 311, 316, 318, 323, 332, 339,
349, 352, 353, 354, and 355 after the demoted note. A typed note whose text
the echo cannot give is a stand-in in NOTEBOOK.md's format. **The text of
a typed note is not a criterion; nothing reads it.**

**The home store** is written by a new HOME.md writer (deviation 13) after
the disk's one blank boot (8a's `new_disk` way):
- `calculator`: the committed `stage6/echo.asm` fixture, assembled, stored under the HP's app's name;
- `part-i8042`: current build `stage8/fixtures/i8042-hang.bin`, previous build `i8042-good.bin`.

**It is read back before any boot**, and each must agree:
- `checkplans.parse_home`;
- `parts.py --disk`: `i8042 demoted f0668b687c68cab0 unhealthy`, 1 app and 1 part;
- the frozen `stage7/trials.py --disk`, whose output must equal `stage7/trials.py --serial` on the three 7d charts joined, byte for byte.

**The same writer makes test 2's small disks:** the part in shadow, the part
live, and the trial concluded.

### D4. The refusals, in the spec's order

`! trial 2` is a reserved body of the `!` line: exactly the seven bytes
`trial 2`, judged beside `trial`, before the home lookup and the broker. It
refuses in this order, each as a console line with one in `errors` and
nothing journaled:
1. `no mouse`
2. `an app is running`
3. `one sitting a boot` (shared with trial one: `trial_ended`)
4. `trial 2 concluded` (a `trial2 verdict` note exists)
5. **`a part is in the pointer's slot`**: the `i8042` slot's state, as its notes give it after the same rescan the `! molt` words make, is shadow or live (deviation 9: the notes' state, not only what this boot loaded, so an Esc recovery boot with a part live still refuses).

A demoted slot does not refuse. `! trial` (trial one) is unchanged.

### D5. Amendment 1 exactly

**Trial two is in progress** when the notebook holds a `trial2 sitting`
note and no `trial2 verdict` note. The scan is made at boot inside the
replay's walk, which already reads every note, and again at the moment of
need.

- **(a) The offer.** On a boot where trial two is in progress, after the replay, the conversation panel gets one console line: `trial 2 sitting <N>: press Enter to start`. N is the next sitting number.
  - While trial two is in progress, **Enter on an empty prompt line is `! trial 2`**, with the same refusals in the same order (deviation 8).
  - Otherwise, Enter on an empty line is today's.
  - With no trial-two note there is no offer and nothing changes.
- **(b) The `saved` line**, after the flush, as in D1.
- **(c) The boot line.** On a boot whose notebook holds any `trial2 ` note, one raw serial line straight after the replay and before the first prompt: `trial2: due sitting <N>` while in progress, or `trial2: concluded verdict <L> default <L>` once concluded. There is no line on any other disk.

### D6. The acceptance tests (spec §11, the kickoff's a–e, Amendment 1)

Written before the code and frozen at item 9. They are mock-free: no broker
is started by this ring's checker. Every run is appended to
`trials/out/gate-8t.log`, with one summary line per test, `8t test <n>:
PASS|FAIL <what>`, and a final `8t gate: PASS` or `8t gate: FAIL`. Scratch
lives under `trials/out/t8/`. The build is `stage8/mkimage.sh` then
`stage8/mkstick.py`, and every boot is the 7c shape through
`checkmetal.qemu_argv` with the stage8 stick copied into `trials/out/t8/`.

**Test 1 — the documents** (`checktrials2.py --document`), host only:
- PE32+, and the stick as 7c (`checkmetal.check_stick` with stage8's paths);
- TRIALS2.md parsed cold, with the cue table's constraints, the formats, the score and the rule;
- `trials2.py --example`: A to F byte for byte, the tie going to G;
- `--status` on example F's chart contains **none of its ms or score values as a token**;
- the history builder's checkpoints and SHA pins (D3);
- the G row's run values equal the rule's (D1).

**Test 2 — the rows and the refusals** (`--rows`):
- **R1, a blank disk** (19 lines):
  - no `trial2:` line and no offer;
  - `! trial 2` opens `trial2: sitting 1 GBBG BGGB`, with the mode word `trial2 G 0/8` on the strip;
  - the warm-up's G row to the pixel (surface bytes and a screendump), then its B row as 7d's `check_layout_b`, and the cue line in the conversation panel;
  - obs `trial_number` 2, `trial_block` 0;
  - Esc in block 2 journals `aborted 2`, followed by the `saved` line;
  - then `! trial 2` and an empty Enter each refuse `one sitting a boot`;
  - `trial2 x`, `trial` and `trial3 y` are refused `trial is reserved`, and `trials are fun` is journaled.
- **C, trial two concluded** (host-written, example B's notes):
  - `trial2: concluded verdict B default B`, with no offer;
  - `layout_default` 1 and the row in B;
  - `! trial 2` refuses `trial 2 concluded`; an empty Enter is a plain prompt with `errors` unchanged.
- **S, good in shadow** (host-written: a trial-two sitting done, `molt i8042 shadow <good> 3 1000 5000`, `part-i8042` = good, and the calculator):
  - `S8: part i8042 shadow`, the watchdog line, the offer;
  - `! calculator` launches from disk; Tab; `! trial 2`, then an empty Enter, each give `an app is running`;
  - Esc closes the app; `! trial 2`, then an empty Enter, each give **`a part is in the pointer's slot`**.
- **L, good live** (S's notes plus `molt i8042 live <good>`):
  - the part's `part:` pair;
  - `! trial 2` and an empty Enter each give the part refusal.
- `no mouse` is proven by the probe (deviation 11), as in 7d.

**Test 3 — sittings predicted** (`--sittings`), with the synthetic human:
scripted delays and misses, a fixed pointer model, and the monitor's
`mouse_move`/`mouse_button` paced 1 ms or more.

**Around every boot:** the notes before it are unchanged byte for byte
after it, the stick copy's tables are unchanged, and there is one `S7:
alive` per boot.

**Disk V, a blank disk, four sittings played to a scripted verdict B:**
- **V1.** `! trial 2` is typed; the whole sitting is played, with a miss each in the warm-up, a G block and a B block.
- **Every sitting is checked for:**
  - the notes equal to `notes_of(script)` by rule: hits' ms within the run's per-hit window; each block score recomputed from its own hits exactly, and within ±30 ms of the script's (7d's A3 number, never widened); misses exact;
  - serial equal to the notes;
  - obs at each block boundary;
  - **the times hidden (A2)**: no cell of the strip, the conversation panel or the app panel holds any recorded ms or score as a token, during or after the sitting. The same check runs on every boot that shows the offer, and it holds until a `trial2 verdict` note exists;
  - **the save rule**: at the question, the host reads the disk file and finds the done note but no prefer note, and there is no `saved` line; after the key, the `saved` line appears only once the host read finds every note of the sitting, the prefer note included.
- **V2–V4.** Each boot shows:
  - `trial2: due sitting <n>`;
  - the offer line;
  - **no `trial2` text drawn by the replay**, and A2's hidden-times check on the strip and both panels straight after ready.

  **An empty Enter starts the sitting.** It is played, and preferences `n`, `g`, `b` are answered.
- **V4's done**, being the fourth: the verdict note `trial2 verdict B <mean>` with the mean equal to `trials2.py`'s recomputation from the recorded block notes, and within slack of the script's. The four tables and the verdict row are in the app panel; `layout_default` is 1.
- **V5.**
  - `trial2: concluded verdict B default B`, with no offer;
  - the row at the prompt in B, `layout_default` 1;
  - an empty Enter is a plain prompt, and `! trial 2` is `trial 2 concluded`;
  - `trials2.py --disk` equals the panel's tables;
  - **`--status` on V1–V3's captures has no ms or score token**.

**Disk H, the HP's history (D3, the kickoff's a), then on to verdict G:**
- **H1.**
  - The boot: the 18 lines with `S7: notebook 355 notes` and `S7: home 1 apps`; `S8: sha256 ok` and **no other `S8:` line**, no `molt: boot`, no `hold Esc`, and **no watchdog armed** (no `S8: watchdog` line, and no reset through the whole sitting); the seed's `i8042:` pair.
  - No `trial2:` line and no offer; `layout_default` 0, and the three-item row in A to the pixel.
  - `! molt` shows `i8042 demoted f0668b687c68cab0 unhealthy`; `! trial` answers `trial concluded`.
  - `! trial 2` opens **sitting 1**, which is played to done with preference `g`.
- **After H1:**
  - the frozen `stage7/trials.py --disk` prints the same bytes as before H1 and as `--serial` on the 7d charts;
  - `parts.py --disk` is unchanged.
- **The host appends sittings 2 and 3** (G-favouring, from `notes_of`), and the disk is now **W**.
- **W1.** `due sitting 4` and the offer, with A2's check straight after ready (H's earlier trial-two notes are on the disk). An empty Enter starts sitting 4; Esc in block 3 journals `aborted 3` and gives the `saved` line. Then an empty Enter refuses `one sitting a boot`.
- **W2.** `due sitting 5`, A2's check straight after ready, and an empty Enter starts it. The sitting is played; the verdict is **G** over sittings 1, 2, 3 and 5, and the panel shows those four tables.
- **W3, a full trial on the disk (about 1,250 notes):**
  - `trial2: concluded verdict G default G` within the probe's boot window;
  - `layout_default` **2** and the HP's three-item row in G to the pixel;
  - a click on the `! grow` zone types `!`; a click on a `|` column does nothing but the count;
  - the frozen `stage7/trials.py --disk` output is still unchanged, verdict A included;
  - `parts.py --disk` is unchanged.

**Test 4 — nothing earlier disturbed:**
- **(a)** The harness's strings: every QEMU line uses the stick, with no `esp.img`; the scratch and the log are under `trials/out/`.
- **(b)** `check_argv_7c` on the checker's own argv.
- **(c)** `payloads.py` as a subprocess, 0 wrong, with the four new paths denied to Write, Edit, `sed -i`, `>` and a heredoc, and allowed to read and run; spot checks held as data.
- **(d)** Host only: the frozen `stage7/trials.py` on a disk holding trial one's HP notes and example A's trial-two notes prints trial one's output unchanged.
- **(e)** `./stage8/test-8a.sh`, exit 0. It runs 8a's tests 1–4, with 7d's checks on this binary through the seams in its test 2 (`! trial` is still trial one), and 7d's gate with 7c, 7b and 7a in its test 4.

**Test 5 — the owner's, on the HP** (`trials/HP-8t.md`): four sittings, one
a boot; the verdict at the fourth `done`; one more boot showing the
default. His word on each sitting and on the verdict closes the ring.

### What only a run can give, and what a rule fixes

**By rule** (TRIALS2.md, computed by `trials2.py`, never typed):
- the cue sequence, the layouts, the orders;
- every note's text but the ms;
- the scores and the verdict from recorded notes;
- the counts of notes a script leaves;
- the G and B columns by rule;
- the ±30 ms score slack.

**From item 8's run, each a named constant in `checktrials2.py` with its
date, and in HANDOVER:**
- the G row's columns read from the surface and a screendump (asserted equal to the rule's in test 1);
- `trial_number`'s offset as read from the page;
- `OFFSET_MS` and the per-hit window;
- the ready window on a blank disk, on H (355 notes) and on W3 (**the boot time with a full trial**);
- the settle;
- each boot's timeout;
- a sitting's wall time;
- `S7: notebook N notes` after each sitting, asserted equal to the rule's count.

The checker refuses to run while any is unset (7d's `UNSET`). A `--set
NAME=VALUE` override is for the probe only (8a's rule).

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- **Tests green before every commit that should pass them.** Each item names the tests that are red by design.
- **Commit messages** that mention frozen names or the bodyguard's words go in by `-F` from a file written with the Write tool.
- **The whole gate, `./trials/test-trial2.sh`,** runs the 8a gate inside its test 4 (about 43 min). The whole gate runs at items 9, 11, 12 and 13: the freeze, the items that change guest code, and the handover. At item 7 the binary is seed 1, unchanged since ring 8a closed, so test 4 runs without (e) there (A5). Every whole run is made **alone and never beside another gate** (the memory "gates run alone"). Item 8's probe binary is not the repository's, so only this ring's checker modes run on it.
- **Stages 0–6's gates** run on their own binaries before item 13's commit, one at a time.
- **Logs.** Every gate run and every direct checker run appends to `trials/out/gate-8t.log`. The chat carries the `8t test` lines and the log's path. Cowork reads the log; the owner never pastes output.
- **HANDOVER** is updated at every item.
- **A gotcha** goes into CLAUDE.md only at a second correction.
- **Probes** live under `trials/out/probe8t/`, are never committed, and are never undone with `git checkout --`: copy aside and restore from the copy.
- **The scope guard:** two honest attempts at any obstacle, each with a real diagnosis. Then stop, record the state in HANDOVER, commit, and wait. A frozen file that must change is never edited: the diff is written unapplied under `trials/out/`, and the owner's hand applies it. **No freeze opening is planned.**
- **Everything runs in QEMU:** the 7c shape, TCG, the caged e1000e, raw disks under `trials/out/` and `stage8/out/` only.
- **What CC never does:** spell a `/dev` path, run `dd`, flash, run `nmcli` or `sudo`, or push.

---

# Part 1 — the documents and the acceptance machinery, before the code

## Item 0 — the plan committed; ring 8t opened

- Copy this file verbatim to `trials/plan-8t.md`, and run `mkdir -p trials/out`.
- `.gitignore` gains `trials/out/`.
- **HANDOVER, the Where-we-are rows:**
  - **Stage:** 8, ring 8t, trial two, opened 28 September 2026, inserted after 8a and before 8b.
  - **Status:** no ring 8t test yet; every earlier gate green as 8a closed.
  - **Toolchain:** with the `claude --version` read now.
  - **Model:** **CC on Opus 5.5 at high effort**, spec decision 11.
- **The policy line:** Cowork's re-check of 28 September 2026 as above; the sittings need no broker; the gate talks only to mocks.
- **Next action:** the plan at the gate, then item 1.
- **A "Ring 8t — trial two" section** with this plan's shape and an empty test table.
- **The owner's decision of 28 September 2026 (A3)**, recorded in HANDOVER. It closes the question ring 8a's closure carried. **No new hardware.** The owner does the physical steps when asked, and the procedures keep them to a minimum:
  - the chart runs as a user service that Cowork writes;
  - Cowork reads every chart from its log;
  - one physical action per step, and no timed waits;
  - held keys and mouse sweeps in place of typing, where they do the job;
  - the machine states its own state on serial at boot.

  These carry to every molt ring from 8b on.
- **Cowork's two uncommitted edits** go in with it: the ring 8t line in `stage8/spec.md`, and Amendment 1 in `trials/spec-trial2.md`.
- One commit. *Expected at commit:* no ring 8t test exists; nothing else changed.

## Item 1 — the environment measured, on seed 1 and private copies

These go into HANDOVER's environment table. No source changes.
1. **The host reads the notes partition while QEMU runs** (the save rule's check). Boot seed 1 on a scratch disk, type a note, and read the file mid-boot.
2. **FLUSH CACHE EXT on the twin.** Make a private copy of `stage8.asm` under `trials/out/probe8t/` that calls `ahci_cmd` with `0xEA` after a note, and show the command completes with no `ERR:`.
3. **The walks' cost.** On a scratch disk carrying about 1,250 host-written notes on seed 1, time from `S7: alive` to `ready` and to the replay's end.
4. **The hook.** QEMU `-drive file=trials/out/…` and `rm -rf trials/out/t8` are allowed; `trials/` paths are judged as `stage` ones.
5. **The history builder's first pass**, in a scratch script: the checkpoints of D3 met from the charts, and how many typed notes are stand-ins.

*Expected at commit:* HANDOVER only.

## Item 2 — `trials/TRIALS2.md`

D1 in one text, written with the Write tool: the supersessions, layout G,
the design, the cue table above, the score, the rule, the notes, the serial
and boot lines, the end of a sitting, the abort, the offer and Enter, the
refusals, the strip, the obs page, the table, examples A to F, and "Parsing
it cold, in Python".

*Expected at commit:* no ring 8t test yet.

## Item 3 — `trials/trials2.py`

D2, proven on the host with no boot:
- `--example` reproduces A to F;
- a document with one cue row broken is refused, naming the constraint;
- example A with one block score changed by one is refused, naming the block;
- `--disk` on a formatted blank disk prints `no sittings`;
- `--serial` equals `--disk` on the notes the same lines make;
- `--status` on example F prints no ms or score token.

*Expected at commit:* no ring 8t test yet.

## Item 4 — `trials/test-trial2.sh`, the log, the build and test 1; `checktrials2.py --document`

- **The harness:** the log header `=== ring 8t gate <iso> commit <rev>[+uncommitted] ===`, the `tee`, the port refusals (9999, 9998, 9997), the build, and the summary lines.
- **The checker:** its `--document` mode, the history builder and the HOME.md writer (D3), and the G columns as `UNSET` constants.

*Expected at commit:* **test 1 red** only on the unset G constants, named; every other part of test 1 passes, quoted from the log.

## Item 5 — `checktrials2.py --rows` (test 2)

- `drive_8t`: 7d's `drive_7d` skeleton with `trials/out/t8/` paths, through `checkmetal.qemu_argv`, `twin.Driver` and `Pointer`;
- the G row check;
- the host-written disks C, S and L;
- test 2 in the harness.

*Expected at commit:* test 2 red, because on seed 1 `! trial 2` goes to the broker and no broker is up: `no answer from the broker`. Quoted.

## Item 6 — `checktrials2.py --sittings` (test 3), the synthetic human

`Human2`, 7d's `Human` transcribed for `trial2:` lines, the warm-up, the
question and the `saved` line. The scripts for V, H and W (V: B faster by
about 150 ms a cue; H and W: G faster). The host reads for the save rule.
The frozen `stage7/trials.py` and `parts.py` comparisons. The timing
constants `UNSET`, marked to be written at item 8.

*Expected at commit:* tests 1–3 red (the unset constants), named.

## Item 7 — `checktrials2.py --cage` and test 4

(a) to (e) of D6; `FROZEN_8T` and the spot checks as data.

*Expected at commit:* test 4 **red on (c) alone**, since nothing is frozen
yet; (a), (b) and (d) are green. **(e) is not run here** (A5): the binary
is seed 1, unchanged since ring 8a closed. (e)'s first run is item 9's.

## Item 8 — THE PROBE: the guest drafted privately; every number read from a run

- **The draft.** All of items 11 and 12, drafted on `trials/out/probe8t/stage8.asm` in a copy of the tree, built there, with its stick.
- **The runs.** `checktrials2.py --rows` and `--sittings` against it, with the unset constants supplied by `--set` for this run only.
- **Read from the log**, and written into `checktrials2.py` as named constants with the date, and into HANDOVER:
  - the G columns from the surface and the screendump;
  - `trial_number` at `0x340`;
  - `OFFSET_MS` and the per-hit window;
  - the ready windows on blank, on H and on W3 (**the boot time with a full trial**);
  - the settle and the timeouts;
  - a sitting's wall time;
  - the note counts after each sitting.
- **The `no mouse` probe:** a second copy with the reset answer forced; `! trial 2` answers `no mouse`, and the journal is unchanged.
- The probe then leaves the checker's path: `stage8/out/` is rebuilt from the repository's source.

*Expected at commit:* `git diff --stat` shows `trials/checktrials2.py` and
`HANDOVER.md` only. Test 1 is green; tests 2 and 3 are red on the missing
`trial2:` line (not on a placeholder); test 4 is red on (c).

## Item 9 — THE FREEZE — test 4 green

- `PROTECTED` gains `trials/TRIALS2.md`, `trials/trials2.py`, `trials/checktrials2.py` and `trials/test-trial2.sh`.
- `payloads.py` gains `FROZEN_8T`: `freeze_cases`, plus hand cases for the ring's scratch. QEMU on `trials/out/t8/…`, `rm -rf trials/out/t8` and `qemu-img` under `trials/out/` are allowed; `rm -rf trials`, and a glob over the four files, are denied.
- **Before the freeze, run the checker against the next planned state too** (8a's candidate gotcha): a seed record with a seed 2 line appended in a scratch copy, and a binary of a different size, must not trip test 1.
- The table re-run, with the count taken from the run and 0 wrong. One denied call shown live.
- Then the gate whole, with the commit message by `-F`.

*Expected at commit:* tests 1 and 4 green; 2 and 3 red by design.

## Item 10 — `trials/glass-8t-section.md` — then stop for the owner's hand

**A "Ring 8t — trial two" section for GLASS.md** in the 7d section's
manner. It states that everything above stands byte for byte, and then
covers:
- layout G's cells and click rule;
- `layout_default` 2;
- `! trial 2` and its five refusals;
- the widened reserved prefix;
- the mode word `trial2 <L> <b>/8`;
- `trial_number` at `0x340`;
- the replay rule for `trial2 ` notes;
- Enter while trial two is in progress;
- everything else by pointer to `trials/TRIALS2.md`.

The section is committed alone. **The session stops** and tells the owner:
`cat trials/glass-8t-section.md >> stage6/GLASS.md` from his terminal, and
commit it by his hand. Nothing is touched until he says it is in.

---

# Part 2 — the implementation, in `stage8/stage8.asm`

## Item 11 — the sitting: `! trial 2`, the warm-up, G and B, the scores, the end

From the probe:
- **The start:**
  - `bang_line`'s `trial 2` body and `trial2_start` with D4's five refusals (the slot state from `ms_slots` after `molt_scan`);
  - the widened prefix in `line_is_reserved`;
  - mode 5 for trial two, with `trial_number` and the mode word's `trial2` branch.
- **The blocks:**
  - the cue table, the warm-up and its two layouts, 20-cue blocks and 5 s rests;
  - layout G in `choices_update` (`row_to_grouped`: labels, `|`, B's spans as targets), for trial blocks and for `layout_default` 2;
  - `trial2_press`, and the block score (`trial2_score`: sort, middle 16, `+100×m`).
- **The notes:** the notes and their `trial2:` mirrors.
- **The end:**
  - the question and the prefer note;
  - the counts;
  - the verdict (`trial2_verdict`: 16 pairs over the first four done sittings; B if S > 0, else G; the note's mean `S / 16` by `idiv`) with the stacked tables;
  - the abort;
  - the flush through `ahci_cmd` `0xEA` and the `saved` line.
- **At boot:** `note_verdict_check` reads either family into `layout_default` 0, 1 or 2.

The replay rule, the boot line, the offer and Enter are left for item 12.

*Green at commit:* tests 1 and 4 (so **the 8a gate whole on this binary**,
7d's checks on it through its test 2), **test 2**. Test 3 is red only on
V2–V4 and W's due lines, offers, Enter and replay checks, said from the
log. Probed first on a private copy at `-smp 2`, `4` and `8`.

## Item 12 — Amendment 1 and the replay rule — TESTS 2 AND 3 GREEN

- **The replay:** `notebook_replay` skips drawing `trial2 ` notes and gathers the in-progress facts in the same walk.
- **The boot line:** `trial2: due …` or `concluded …`, raw, after the replay.
- **The offer:** its console line.
- **Enter:** an empty prompt line is `trial2_start` while trial two is in progress.

*Green at commit:* **all four tests, the whole gate**, with the `8t test`
lines in the commit message and the gate's wall time recorded. **This is
the commit seed 2 names.**

## Item 13 — the seed record, HANDOVER, CLAUDE.md, README

- **The seed record.** `parts.py --seed` rebuilds; **seed 2**'s line, naming item 12's commit, is written by `parts.seed_line` from the rebuild (never typed), as SEED.md's rule 5 requires: a later commit than the build's, after its gates were green on it. Then `parts.py --seed` exits 0.
- **HANDOVER:** green pending the oracle; the numbers (the binary's size, seed 2's hash, the boot time with a full trial, the gate's time); the carried items.
- **CLAUDE.md's build block** gains `./trials/test-trial2.sh`, `python3 trials/trials2.py …` and `--status`.
- **README**'s Stage 8 paragraph gains ring 8t.
- **The runs:** the payload table re-run; the whole gate; Stages 0–6 on their own binaries.

*Green at commit:* all four; the earlier gates.

## Item 14 — `trials/HP-8t.md`, the owner's day — then stop: GREEN PENDING THE ORACLE

A short document in HP-8a.md's shape, to Cowork's design. It names no
serial port, no device path and no flash command of CC's.
- **Before sitting 1**, Cowork's (not written by CC):
  - the user service running `broker/chart.py` for the whole trial, appending to `trials/out/hp-8t.log`;
  - the flash script from METAL.md steps 1–3, run once with seed 2's `stage8/out/stick.img` (its `sha256sum` beginning seed 2's prefix);
  - the Ethernet stays in the switch, because the boot waits for the link. There is no broker, relay, second address or firewall rule.
- **What the first boot shows:** `S7: notebook 355 notes`, `S8: sha256 ok` and no other `S8:` line, no `hold Esc`, and no `trial2:` line.
- **Each sitting is three steps with the owner's hands only** (keys, the mouse, the power button):
  1. Power on.
  2. Start the sitting: type `! trial 2` for sitting 1, or press Enter at `trial 2 sitting N: press Enter to start` for sittings 2–4. Click to the end and answer `easier? g, b or n`, all unbroken.
  3. Power off when the panel says `saved - power off when you like`.
- **After sitting 4, one boot** to show the default: the row at the prompt in the verdict's layout, and `trial2: concluded …` on the chart.
- **Cowork reads the chart after each step** with `trials2.py --status`. No step waits a set time, and none asks the owner to report inside a sitting.
- **What an abort means:** Esc ends the sitting; power off at `saved`; the next boot offers the next number; the trial is the first four done sittings.
- **A debugging table** for Cowork: no offer, an unexpected refusal, no `saved`, the chart's lines. **It has a row for the flush (A4):** an `ERR:` line and a halt after the question, with no `saved` line, means the disk refused FLUSH CACHE EXT. Every note of the sitting is already written; the owner powers off, and Cowork reads the chart before the next boot.

HANDOVER's Next action points to it. **The session stops**: green pending
the oracle, the ring's third stop.

---

## Test 5 — Wajira's

By `trials/HP-8t.md`: one flash (Cowork's script), four sittings, one a
boot, the verdict at the fourth `done`, and the verdict boot. His word on
each sitting and on the verdict closes the ring. Sittings may be added only
by a dated amendment to the spec before the next sitting.

## Verification

- `./trials/test-trial2.sh` from the repo root: it refuses to start if 9999, 9998 or 9997 is busy, and appends everything to `trials/out/gate-8t.log`. Four `8t test` lines and `8t gate: PASS`, with the 8a gate (and 7d, 7c, 7b, 7a) green inside test 4. About 75 min, measured at item 9.
- `python3 .claude/hooks/payloads.py`: 0 wrong.
- `python3 trials/trials2.py --example`; `python3 stage8/parts.py --seed` exits 0 with seed 2 current.
- Stages 0–6's gates on their own binaries at item 13.

## Safety

- QEMU only, with the cage.
- Disks are raw files under `trials/out/` and `stage8/out/`.
- No broker is started by this ring's checker; the 8a gate's mocks bind `127.0.0.1`.
- No `/dev` path, `dd`, flash, `nmcli`, `sudo` or push by CC.
- The HP's disk is never written by mlrig.
- `stage7/TRIALS.md` and `stage8/loader.asm` are untouched, and **no freeze opening is planned**.

## Risks, and what absorbs them

- **The FLUSH on the Q77's AHCI or the HP's disk.** It is mandatory for LBA48 drives, and item 1 proves the twin. If the HP answers it with an error, the owner sees the loader's named `ERR:` line and a halt, with every note already written and no `saved` line. He powers off, and Cowork reads the chart before the next boot (A4; HP-8t.md's debugging table).
- **The widened prefix or Enter disturbing an earlier gate.** Only disks with `trial2` notes change, and the 8a gate runs whole at every guest item.
- **Boot time with about 1,250 notes on the HP's disk:** three walks of one sector read per note. Item 1 measures it on the twin, and HP-8t.md says what the owner will see.
- **The history builder's typed notes:** stand-ins where the echo fails. Only the counts are criteria.
- **The gate's length** (about 75 min) is absorbed by the run-alone rule and the five named whole runs.

## Deviations from the spec and the kickoff, for approval

1. **The replay does not draw `trial2 ` notes** (NOTEBOOK.md's sentence superseded for that prefix). Otherwise every boot would show the hidden times (decision 7).
2. **Esc at the question journals `trial2 prefer <n> skip`**, so "the preference saved" is a fact on the record either way.
3. **The warm-up has no block note** (its layouts are mixed). Its rest line is `warm-up done - rest`, and an abort in it is `aborted 0`.
4. **Withdrawn by A1.** The verdict is decided on the sign of S; the truncated mean is the note's number only.
5. **The question, the counts and `saved` are conversation-panel lines.** The app panel is used only for the verdict's four tables.
6. **The `saved` line also follows an abort**, after the flush, so the owner's rule is one rule.
7. **The boot lines' form:** `trial2: due sitting <n>` and `trial2: concluded verdict <L> default <L>`. They are not notes.
8. **Enter's trigger** is "trial two in progress on the notebook", so every refusal fires through Enter as through `! trial 2`. The offer is drawn at boot under the amendment's conditions.
9. **The part refusal reads the slot's state from its notes** (shadow or live), not only this boot's load.
10. **`trial_number` is written only by trial two**, so the 7d checks on this binary see the reserved words zero.
11. **`no mouse` is proven by probe**, as in 7d (q35 cannot drop the PS/2 mouse).
12. **ATA FLUSH CACHE EXT** before `saved`, through the loader's `ahci_cmd` with `loader.asm` untouched, so "on the disk" is true on a disk with a write cache.
13. **The HP's disk in the twin is host-built:** the notes from the pinned charts, and the home store by a new HOME.md writer in the frozen checker. The calculator is a stand-in (`echo.asm`) under that name.
14. **Disk W continues disk H:** two trial-two sittings are host-written between guest-played ones. The guest plays sittings 1, 4 (aborted) and 5; disk V plays all four.
15. **The counts shown are over blocks 1–8** (`hits 160`); the warm-up is reported separately by `--status` only.
16. **`--status` prints `preference saved` without the letter.**
17. **The mode word's letter is the current cue's layout**, so the warm-up shows both.
18. **The log's summary format:** `8t test <n>: PASS|FAIL`, and `8t gate: PASS|FAIL`.
19. **The explicit `trials/out/` line in `.gitignore`**, though the bare `out/` already covers it.

## Amendments — Cowork's review, folded in before approval (28 September 2026)

Cowork found the plan sound and accepted all nineteen deviations, deviation 1
especially, and checked the cue table. Its five amendments are in the text above:

- **A1, required: the verdict on the sign of S.** B if S > 0, G if S <= 0. The note carries `S / 16` truncated toward zero, so a near-tie reads `verdict B 0` or `verdict G 0`. Worked example C: S = 0 gives `verdict G 0`, S = 15 gives `verdict B 0`, S = −15 gives `verdict G 0`. Deviation 4 is withdrawn. (D1, example C, item 11.)
- **A2, required: the times hidden everywhere the owner can look.** Test 3's check covers the strip as well as both panels, on every sitting boot and on every boot that shows the offer, until a verdict note exists. (D6, test 3: V, W1, W2.)
- **A3, required: the owner's decision of 28 September 2026 in HANDOVER at item 0.** No new hardware; the physical steps are kept to a minimum; this carries to every molt ring from 8b on. (Item 0.)
- **A4: the flush's arguments and its failure.** AL `0xEA`, EBX 0, DL 0, RDI a scratch 512-byte buffer. On an error the owner sees the loader's named `ERR:` line and a halt, with every note already written and no `saved` line. HP-8t.md's debugging table gets that row. (D1 step 5, the risks, item 14.)
- **A5: test 4 (e) at item 9 only.** At item 7 the binary is seed 1, unchanged, so test 4 runs without (e). This saves about 43 minutes. (The conventions, item 7.)
