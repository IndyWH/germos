# TRIALS.md — the N-of-1 trial of the choices row

**Stage 7 ring 7d, plan item 2. Frozen behind the hook from item 8.** The
assembler implements this document; `stage7/trials.py` and
`stage7/checktrials.py` parse by it. One text, three readers. If it is
wrong, that is a spec question for the owner, not an edit.

The ring's spec is `stage7/spec-7d.md`. This document is the spec made
exact, and it **corrects the spec in two places** (plan deviations 1 and 6,
accepted by the owner): the obs fields begin at `0x2E0`, not `0x2C0`,
because DISK.md already holds three words at `0x2C0`–`0x2D0`; and a click
on the `! grow` box outside a trial types `!`, as GLASS.md's click rule
gives, not a launch line. Everything GLASS.md, HOME.md, NOTEBOOK.md and
DISK.md say stands, except where a sentence below says it supersedes one.

The foundation's rule for this ring: the DE optimises time-to-done and
error rate, never engagement. The trial measures the first two for this
one human on this one machine, and nothing else is looked at before the
verdict.

## The row and the items

The control trialled is the **choices row**: rows `R−2` and `R−1` of the
console (GLASS.md, "The choices row"). **Layout A** is the row exactly as
ring 6c left it — items on row `R−2` separated by three spaces, row `R−1`
blank, a press on either row judged by its column. **Layout B** draws the
same items as boxes (below). Nothing else on the screen differs between
the layouts.

During every block of a trial the row shows the **four items of the
state-3 row**, `? ask   ! grow   Tab app   Esc exit`, in the block's
layout, whatever else the machine holds. The four items, their **label
words** (the cue) and their **indices** (`trial_target`):

| Index | Item | Word |
|---|---|---|
| 0 | `? ask` | `ask` |
| 1 | `! grow` | `grow` |
| 2 | `Tab app` | `app` |
| 3 | `Esc exit` | `exit` |

In layout A their targets are the columns GLASS.md's `choice_targets`
gives for that row: 0–4, 8–13, 17–23, 27–34, on row `R−2` and, by the
margin rule, on row `R−1`.

## The design

An N-of-1 crossover, pre-registered here, deterministic so the twin can
check it.

**A block** is ten cues on one layout. **The cue table** — the sequence of
words for each block, fixed by block number; each word at least twice,
none twice running:

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

**A sitting** is eight blocks. **The block order** is by the sitting's
parity: odd sittings `ABBA BAAB`, even sittings `BAAB ABBA`; block *b*'s
layout is the order's *b*-th letter with the space removed. **The pairs**
are blocks (1,2), (3,4), (5,6), (7,8) of one sitting — one A and one B in
each by construction; four pairs a sitting.

**The sitting number** is one more than the number of notes of the form
`trial sitting <n> <order>` already on the notebook, in journal order. An
aborted sitting counts: it was started. The `done` and `aborted` notes
begin with the same three words and are not counted.

**The trial** is three sittings that ended in `done`. **One sitting a
boot:** after a sitting has ended in this boot, `! trial` refuses.

## A sitting, step by step

**`! trial`** is a reserved word of the `!` line: a body equal to the five
bytes `trial` and nothing else, judged before the home lookup and before
the broker, as `undo install` is (this sentence supersedes HOME.md's
"anything unknown goes to the broker" for that one body). It refuses, with
a console line, one in `errors`, nothing journaled, in this order:

| Line | When |
|---|---|
| `no mouse` | `mouse_id` is 0 — no mouse answered its reset at boot |
| `an app is running` | `mode` is 3 |
| `one sitting a boot` | a sitting ended (`done` or `aborted`) in this boot |
| `trial concluded` | a `trial verdict` note is on the notebook |

Otherwise the sitting begins: the sitting number and the order by the
rules above; the note `trial sitting <n> <order>` and its serial line; the
console line `sitting <n> <order>` in the conversation panel; `mode` 5;
the obs fields; the row set to the four items in block 1's layout; and
the first cue.

**The cue** is one console line in the conversation panel, `click:
<word>`, console-only as every console line (never on serial). The boot
processor writes the line, sets `trial_target` and `trial_cue`, then sets
`cue_pending` to 1; the glass core snapshots `cue_pending` before its
copies and, at the end of the frame copy that painted the line, writes
`cue_stamp` = `rdtsc` and clears `cue_pending` — the mirror of
`echo_pending`. A cue is **showing** from that frame's end until its hit.

**A press** is button 1's bit going from clear to set in a packet (GLASS.md,
"The click on the choices row"); every pressed bit counts one in `clicks`
first, as ever. In mode 5:

| The press | What happens |
|---|---|
| button 1 on the **cued item's target**, while a cue is showing | a **hit**: `cue-to-hit = (press stamp − cue_stamp) / tsc_per_ms`, integer division; `hit_last` and `hit_worst` (ticks); `trial_hits + 1`; the note `trial <s> <b> <L> <c> <ms>` and its line; then **the pause** |
| button 1 **anywhere else** on the screen — another item, a gap, the margin's gap columns, the strip, either panel — while a cue is showing | a **miss**: `trial_misses + 1`; the note `trial <s> <b> <L> <c> miss` and its line; **the cue stays** and the next press is judged again |
| button 1 while **no cue is showing** — the pause, the rest, or the frame before the cue's paint (`cue_pending` 1) | nothing but the count in `clicks` |
| button 2 or 3 anywhere | nothing but the count |

`hits` (ring 6c's counter of presses that acted) is **not** incremented in
mode 5: nothing on the row acts during a trial. The target in layout A is
the item's text on row `R−2` or the same columns on row `R−1`; in layout
B any filled cell of its box on either row (below). The press's stamp is
the packet's first byte's interrupt stamp, as ring 6c stamps it.

**The pause:** 500 ms after a hit, `pause_until = press stamp + 500 ×
tsc_per_ms`, the row unchanged, `trial_cue` still the hit cue's index;
then the next cue, or the block's end after cue 10.

**Keys** in mode 5 are counted in `keys` as ever and dropped — printables,
Enter, Backspace, Tab — **except Esc, which aborts** (below).

**The block's end:** after cue 10's pause, the block's note `trial block
<s> <b> <L> <hits> <misses> <median>` and its line — `hits` is 10 for
every completed block — then `trial_cue` 0, the row blank (both rows
background, in either layout), the console line `block <b> of 8 - rest`
in the conversation panel, and **the rest**: 2000 ms (no rest and no rest line after block 8); then, for blocks
1–7, `trial_block + 1`, `trial_layout` by the order, `trial_hits` and
`trial_misses` 0, the row set in the new layout, the first cue of the new
block; after block 8, the sitting's end.

**The median** of a block: the ten cue-to-hit values in ms sorted
ascending, the mean of the fifth and the sixth rounded down — `(v5 + v6)
/ 2` by integer division.

**The sitting's end:** the note `trial sitting <n> done` and its line; the
console line `sitting <n> done`; the sitting's table in the app panel
(below); then **the verdict scan**: if this sitting is the third with a
`done` note, the verdict by the rule below, the note `trial verdict <L>`
and its line, `layout_default` set to it (0 A, 1 B), the console line
`verdict <L>`, the table's last row `verdict <L>`, and the row redrawn in
that layout for the prompt; `mode` 0 and the prompt, the keys and presses
made meanwhile discarded as after any answer.

**Esc** at any moment of mode 5 aborts the sitting: the note `trial
sitting <n> aborted <b>` and its line, where *b* is **the first block
with no block note** — the block in play, or, during a rest, the block
that would have followed; the hit and miss notes of that block already on
the journal stand (the journal is append-only) but no block note is
written for it, so no table shows it and it enters no verdict; the console
line `sitting <n> aborted <b>`; the table of the completed blocks in the
app panel with `aborted <b>` as its last row; `mode` 0 and the prompt.

**The reserved prefix.** A typed line whose first six bytes are `trial `
is never a note: at Enter it is refused with the console line `trial is
reserved`, one in `errors`, nothing journaled, and the prompt returns.
This sentence supersedes NOTEBOOK.md's "the bytes typed at the prompt
between one Enter and the next … every such line is appended" for lines
with that prefix: the journal's `trial ` prefix belongs to the machine
alone, so the scans below read only what the machine wrote.

## The verdict rule

Pre-registered. Over the **first three sittings that ended in `done`**, in
sitting order, take the twelve pairs. In each pair the A block's median
and the B block's median are compared: a pair is a **win for B** when B's
median is **strictly lower**. **B becomes the default if the wins are at
least ten and the total misses of the twelve B blocks are not greater
than the total misses of the twelve A blocks; otherwise A stays.** Ten of
twelve under the null hypothesis of no difference is a sign test at
*p* ≈ 0.02 (one-sided, 0.019). Nothing else is looked at.

An aborted sitting's completed blocks stand on the record and in its
table and are outside the verdict: a pair is two blocks of one sitting,
and twelve pairs are three complete sittings.

**Where the verdict lives:** on the notebook, as `trial verdict <L>`. At
boot the machine reads the journal and takes the **last** verdict note
into `layout_default`; the row shows that layout at the prompt from then
on. Until a verdict exists `layout_default` is 0 and every earlier gate
sees ring 6c's row to the pixel. The same three scans — the last verdict,
the count of sitting-start notes, the block notes of the `done` sittings —
are walks of the journal from sector 1 to its end, made at the moment of
need and never cached across a boot.

## Layout B — the boxes

For a row of *n* items on a console *C* cells wide:

- `w = ⌊C / n⌋`. Box *i* (0-based) spans columns `i·w … (i+1)·w − 1`; the
  last box spans `(n−1)·w … C−1`.
- **The gap:** the last column of every box but the last is background on
  both rows. Every other cell of the box, on rows `R−2` and `R−1`, is
  **filled**: the inverse of the strip's colours — a background-coloured
  glyph on foreground fill. The filled width is `w − 1`, or `C − (n−1)·w`
  for the last box.
- **The label** — the item's text, exactly as layout A spells it — sits on
  row `R−2` from column `first + ⌊(filled − len) / 2⌋`, inverse.
- **A press** on any filled cell of a box, either row, is that item, with
  the kind and the argument the item has in layout A (`? ask` types `?`,
  `! grow` types `!`, an installed app's item types its launch line on an
  empty prompt line, `Esc exit` is Esc, `Tab …` is Tab); a press on a gap
  cell does nothing but the count. The hit table is the boxes' filled
  spans, one entry each.

**The cell byte.** A surface cell byte with **bit 7 set** is drawn inverse:
`0x80 | ch` for `ch` in `0x20`–`0x7E` is the glyph of `ch` in the
background colour on the foreground colour; **`0xA0`** is the solid
foreground cell. No cell of layout A, of the strip, of the conversation or
of an app carries bit 7. Two colours, as everything.

**When the row is layout B:** during a B block of a trial; and outside a
trial when `layout_default` is 1. The items shown are the row's items for
the state, exactly as today — GLASS.md's table, HOME.md's extension, never
more than five. During a rest the row is blank in either layout.

**On the twin** (1920x1080, C = 120), the four-item row: `w = 30`; boxes
0–28, 30–58, 60–88, 90–119; gaps at 29, 59, 89; labels `? ask` at 12–16,
`! grow` at 41–46, `Tab app` at 71–77, `Esc exit` at 101–108 (the last box is thirty cells wide). The
two-item row at the prompt with nothing installed: `w = 60`; boxes 0–58
and 60–119; the gap at 59; labels at 27–31 and 87–92.

## The notes

Every event is one note, NOTEBOOK.md's record unchanged: printable ASCII,
single spaces, decimal numbers without leading zeros, `L` the layout
letter `A` or `B`:

```
trial sitting 1 ABBA BAAB     the sitting number, the order
trial 1 1 A 3 412             sitting, block, layout, cue index 1-10, ms - a hit
trial 1 1 A 4 miss            sitting, block, layout, cue index - a miss
trial block 1 1 A 10 1 431    sitting, block, layout, hits, misses, median ms
trial sitting 1 done
trial sitting 1 aborted 5     the first block with no block note
trial verdict B               A or B; the last such note is the default
```

The notes of one cue are in journal order: its misses, then its hit. A
block's note follows its tenth hit. `S7: notebook N notes` counts them, the
boot replay draws them, `n` on the strip counts them.

## The serial lines

Each note goes to serial at the moment it is journaled, **raw UART** —
never the tee, so nothing lands in the conversation — as the note with
its first word replaced: the serial line is `trial:` followed by the note
from its sixth byte:

```
trial: sitting 1 ABBA BAAB
trial: 1 1 A 3 412
trial: 1 1 A 4 miss
trial: block 1 1 A 10 1 431
trial: sitting 1 done
trial: sitting 1 aborted 5
trial: verdict B
```

So the chart on the HP carries the sitting without a flash to read the
disk, and `trials.py --serial` reads it back. No `S7:` line is added by
this ring.

## The strip

`mode` gains the value **5, `trial`**. The mode word for it is `trial <L>
<b>/8` — `trial A 3/8`: the block's layout, the block, of eight — eleven
characters, space-padded to the field's 18 as every mode word is. The
trial is a visible mode, never a hidden one. Every other field of the
strip is as GLASS.md and the 6c section draw it.

## The obs page, from `0x2E0`

Sixteen `u64` words, one writer each. DISK.md's three words at
`0x2C0`–`0x2D0` stand; `0x2D8` is zero. **The rest of the page, from
`0x360`, is zero** — this supersedes the 6c section's "from `0x2C0`" and
DISK.md's "`0x2D8` onward" from this ring on.

| Offset | Field | Written by | Meaning |
|---|---|---|---|
| `0x2E0` | `trial_sitting` | BSP | the sitting number while a sitting runs, and the last sitting's after it; 0 before any |
| `0x2E8` | `trial_block` | BSP | the block, 1–8, while a sitting runs; 0 outside one |
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

`trial_block` advances at a rest's end, so during a rest it names the
block just finished and `trial_cue` is 0.

## The app panel's table

At a sitting's end the app panel is cleared and holds the sitting's table,
one row per panel row from row 0, column 0:

```
sitting 1 ABBA BAAB
1 A 10 0 303
2 B 10 1 206
...
8 B 10 0 206
done
```

Row 0 is the sitting-start note from its second word; rows 1–8 are the
block notes from their block number on; the next row is `done` or
`aborted <b>` (after an abort only the completed blocks' rows appear);
and, at the third `done` sitting, one more row `verdict <L>`. The panel
keeps the table until something else clears it (a launch, a grow, the
next sitting). `trials.py` prints the same tables, one per sitting.

## Worked example A — one scripted sitting

Sitting 1, `ABBA BAAB`, three misses (block 2 cue 4, block 5 cue 7, block
7 cue 2). The 93 notes, in journal order — exactly what the notes
partition holds after the sitting, `S7: notebook 93 notes` on the next
boot; the serial lines are these with `trial` → `trial:`:

```
trial sitting 1 ABBA BAAB
trial 1 1 A 1 312
trial 1 1 A 2 298
trial 1 1 A 3 305
trial 1 1 A 4 330
trial 1 1 A 5 287
trial 1 1 A 6 301
trial 1 1 A 7 344
trial 1 1 A 8 279
trial 1 1 A 9 318
trial 1 1 A 10 296
trial block 1 1 A 10 0 303
trial 1 2 B 1 204
trial 1 2 B 2 215
trial 1 2 B 3 198
trial 1 2 B 4 miss
trial 1 2 B 4 240
trial 1 2 B 5 187
trial 1 2 B 6 209
trial 1 2 B 7 222
trial 1 2 B 8 193
trial 1 2 B 9 231
trial 1 2 B 10 201
trial block 1 2 B 10 1 206
trial 1 3 B 1 211
trial 1 3 B 2 196
trial 1 3 B 3 228
trial 1 3 B 4 203
trial 1 3 B 5 190
trial 1 3 B 6 219
trial 1 3 B 7 207
trial 1 3 B 8 235
trial 1 3 B 9 199
trial 1 3 B 10 214
trial block 1 3 B 10 0 209
trial 1 4 A 1 327
trial 1 4 A 2 291
trial 1 4 A 3 309
trial 1 4 A 4 316
trial 1 4 A 5 302
trial 1 4 A 6 288
trial 1 4 A 7 335
trial 1 4 A 8 297
trial 1 4 A 9 322
trial 1 4 A 10 306
trial block 1 4 A 10 0 307
trial 1 5 B 1 199
trial 1 5 B 2 226
trial 1 5 B 3 208
trial 1 5 B 4 183
trial 1 5 B 5 217
trial 1 5 B 6 202
trial 1 5 B 7 miss
trial 1 5 B 7 239
trial 1 5 B 8 195
trial 1 5 B 9 221
trial 1 5 B 10 210
trial block 1 5 B 10 1 209
trial 1 6 A 1 304
trial 1 6 A 2 319
trial 1 6 A 3 293
trial 1 6 A 4 338
trial 1 6 A 5 300
trial 1 6 A 6 311
trial 1 6 A 7 284
trial 1 6 A 8 326
trial 1 6 A 9 297
trial 1 6 A 10 315
trial block 1 6 A 10 0 307
trial 1 7 A 1 321
trial 1 7 A 2 miss
trial 1 7 A 2 289
trial 1 7 A 3 307
trial 1 7 A 4 296
trial 1 7 A 5 333
trial 1 7 A 6 302
trial 1 7 A 7 318
trial 1 7 A 8 285
trial 1 7 A 9 310
trial 1 7 A 10 299
trial block 1 7 A 10 1 304
trial 1 8 B 1 188
trial 1 8 B 2 223
trial 1 8 B 3 205
trial 1 8 B 4 197
trial 1 8 B 5 234
trial 1 8 B 6 201
trial 1 8 B 7 216
trial 1 8 B 8 192
trial 1 8 B 9 229
trial 1 8 B 10 207
trial block 1 8 B 10 0 206
trial sitting 1 done
```

Block 1's median: the ten values sorted are 279 287 296 298 301 305 312
318 330 344; the fifth and sixth are 301 and 305; `(301 + 305) / 2` = 303.
The table the app panel shows, and `trials.py --disk` prints:

```
sitting 1 ABBA BAAB
1 A 10 0 303
2 B 10 1 206
3 B 10 0 209
4 A 10 0 307
5 B 10 1 209
6 A 10 0 307
7 A 10 1 304
8 B 10 0 206
done
```

No verdict: one `done` sitting is four pairs.

## Worked example B — four sittings, one aborted, and the verdict

Four sittings' `sitting`, `block`, `done` and `aborted` notes (the hit and
miss notes left out here; a real journal holds them between). Sitting 2
was aborted in block 3, so its two block notes stand but it is outside
the verdict; the first three `done` sittings are 1, 3 and 4:

```
trial sitting 1 ABBA BAAB
trial block 1 1 A 10 0 310
trial block 1 2 B 10 1 204
trial block 1 3 B 10 0 209
trial block 1 4 A 10 0 309
trial block 1 5 B 10 0 204
trial block 1 6 A 10 0 307
trial block 1 7 A 10 1 304
trial block 1 8 B 10 0 203
trial sitting 1 done
trial sitting 2 BAAB ABBA
trial block 2 1 B 10 0 241
trial block 2 2 A 10 0 298
trial sitting 2 aborted 3
trial sitting 3 ABBA BAAB
trial block 3 1 A 10 0 301
trial block 3 2 B 10 0 214
trial block 3 3 B 10 1 220
trial block 3 4 A 10 0 296
trial block 3 5 B 10 0 199
trial block 3 6 A 10 1 312
trial block 3 7 A 10 0 288
trial block 3 8 B 10 0 231
trial sitting 3 done
trial sitting 4 BAAB ABBA
trial block 4 1 B 10 0 306
trial block 4 2 A 10 0 299
trial block 4 3 A 10 0 218
trial block 4 4 B 10 0 222
trial block 4 5 A 10 0 296
trial block 4 6 B 10 0 217
trial block 4 7 B 10 0 211
trial block 4 8 A 10 0 305
trial sitting 4 done
trial verdict B
```

The twelve pairs: sitting 1 — 310/204, 209/309, 204/307, 304/203 (A/B
medians in pair order: B lower in all four); sitting 3 — 301/214, 296/220,
312/199, 288/231 (four); sitting 4 — 299/306 (A lower), 218/222 (A
lower), 296/217, 305/211 (two). **Wins for B: 10 of 12.** Misses, per
block in block order: the A blocks 0+0+0+1 (sitting 1), 0+0+1+0 (sitting
3), 0+0+0+0 (sitting 4) = 2; the B blocks 1+0+0+0, 0+1+0+0, 0+0+0+0 = 2.
Not greater. **Verdict B**, and the
last note says so. The sitting numbers ran 1–4 because the aborted sitting
was started; the next `! trial` on this notebook is refused, `trial
concluded`.

## Parsing it cold, in Python

`stage7/trials.py` executes this block as its own definitions — read from
this file at import, so the tool and the document cannot drift — with the
frozen `parse_obs_6c` (the 6c section) and `mode_word` (the 6a section)
supplied by name. `checktrials.py` uses the tool.

```python
import struct

ITEMS = ["ask", "grow", "app", "exit"]                    # trial_target 0-3
ROW_ITEMS = ["? ask", "! grow", "Tab app", "Esc exit"]     # the row during a trial
CUES = [
    "grow ask exit app grow exit ask app exit ask",
    "app exit grow ask app grow exit ask grow exit",
    "exit app ask grow exit ask app grow ask grow",
    "ask grow app exit ask app grow exit app exit",
    "grow exit ask app grow ask exit app ask app",
    "app ask grow exit app exit ask grow exit grow",
    "exit grow app ask exit app grow ask grow ask",
    "ask app exit grow ask exit app grow exit app",
]
ORDERS = {1: "ABBA BAAB", 0: "BAAB ABBA"}                 # by the sitting's parity
CUES_PER_BLOCK, BLOCKS, PAIRS_PER_SITTING = 10, 8, 4
SITTINGS_NEEDED, PAIRS_NEEDED, WINS_NEEDED = 3, 12, 10
PAUSE_MS, REST_MS = 500, 2000
MODE_TRIAL = 5
INVERSE, SOLID = 0x80, 0xA0
NOTE_PREFIX, SERIAL_PREFIX = "trial ", "trial:"
REFUSALS = ["no mouse", "an app is running", "one sitting a boot", "trial concluded", "trial is reserved"]
OBS_7D = {
    "trial_sitting": 0x2E0, "trial_block": 0x2E8, "trial_layout": 0x2F0, "trial_cue": 0x2F8,
    "trial_target": 0x300, "cue_stamp": 0x308, "cue_pending": 0x310, "trial_hits": 0x318,
    "trial_misses": 0x320, "hit_last": 0x328, "hit_worst": 0x330, "layout_default": 0x338,
}
OBS_PAGE_BYTES_7D = 0x360        # the page's zero rule holds from here


def check_cue_table():
    """The two constraints on every row: each item at least twice, none twice running."""
    for row in CUES:
        words = row.split()
        assert len(words) == CUES_PER_BLOCK and set(words) <= set(ITEMS), row
        assert all(words.count(w) >= 2 for w in ITEMS), row
        assert all(a != b for a, b in zip(words, words[1:])), row


def order(sitting):
    return ORDERS[sitting % 2]


def layout(sitting, block):
    return order(sitting).replace(" ", "")[block - 1]


def cue_sequence(block):
    return CUES[block - 1].split()


def median(ms):
    v = sorted(ms)
    return (v[4] + v[5]) // 2


def serial_of(note):
    return SERIAL_PREFIX + note[5:]


def note_of_serial(line):
    return "trial" + line[len(SERIAL_PREFIX):]


def boxes(C, n):
    """Layout B for n items on C columns: (first, last, filled_first, filled_last) per box."""
    w = C // n
    out = []
    for i in range(n):
        first = i * w
        last = (i + 1) * w - 1 if i < n - 1 else C - 1
        out.append((first, last, first, last - 1 if i < n - 1 else last))
    return out


def label_col(box, label):
    first, last, ffirst, flast = box
    return ffirst + (flast - ffirst + 1 - len(label)) // 2


def box_cells(C, labels):
    """The two rows of the choices surface in layout B, as bytes."""
    row0, row1 = bytearray(b" " * C), bytearray(b" " * C)
    for box, label in zip(boxes(C, len(labels)), labels):
        first, last, ffirst, flast = box
        for c in range(ffirst, flast + 1):
            row0[c] = row1[c] = SOLID
        lc = label_col(box, label)
        for i, ch in enumerate(label):
            row0[lc + i] = INVERSE | ord(ch)
    return bytes(row0), bytes(row1)


def box_targets(C, labels, kinds):
    """(first, last, kind, arg) per box, over the filled span - choice_targets' shape."""
    return [(b[2], b[3], k, a) for b, (k, a) in zip(boxes(C, len(labels)), kinds)]


def parse_note(text):
    """A trial note's fields, or None for any other note."""
    w = text.split(" ")
    if not text.startswith(NOTE_PREFIX) or "" in w:      # single spaces, no leading or trailing
        return None
    try:
        if w[1] == "sitting" and len(w) == 5 and w[3] in ("ABBA", "BAAB"):
            return {"kind": "sitting", "sitting": int(w[2]), "order": w[3] + " " + w[4]}
        if w[1] == "sitting" and len(w) == 4 and w[3] == "done":
            return {"kind": "done", "sitting": int(w[2])}
        if w[1] == "sitting" and len(w) == 5 and w[3] == "aborted":
            return {"kind": "aborted", "sitting": int(w[2]), "block": int(w[4])}
        if w[1] == "block" and len(w) == 8:
            return {"kind": "block", "sitting": int(w[2]), "block": int(w[3]), "layout": w[4],
                    "hits": int(w[5]), "misses": int(w[6]), "median": int(w[7])}
        if w[1] == "verdict" and len(w) == 3 and w[2] in ("A", "B"):
            return {"kind": "verdict", "layout": w[2]}
        if len(w) == 6 and w[3] in ("A", "B"):
            if w[5] == "miss":
                return {"kind": "miss", "sitting": int(w[1]), "block": int(w[2]), "layout": w[3], "cue": int(w[4])}
            return {"kind": "hit", "sitting": int(w[1]), "block": int(w[2]), "layout": w[3], "cue": int(w[4]),
                    "ms": int(w[5])}
    except ValueError:
        return None
    return None


def notes_of(script):
    """The notes a scripted sitting leaves: script = {"sitting": n, "blocks": [{"ms": [10 ints],
    "miss": [cue indices]}, ...], "abort": None or (block, hits_before_esc)}; an aborted
    sitting's last entry holds the hits played before Esc."""
    n = script["sitting"]
    out = ["trial sitting %d %s" % (n, order(n))]
    for b, blk in enumerate(script["blocks"], 1):
        L = layout(n, b)
        abort = script.get("abort")
        if abort and abort[0] == b:
            for c in range(1, abort[1] + 1):
                if c in blk.get("miss", ()):
                    out.append("trial %d %d %s %d miss" % (n, b, L, c))
                out.append("trial %d %d %s %d %d" % (n, b, L, c, blk["ms"][c - 1]))
            out.append("trial sitting %d aborted %d" % (n, b))
            return out
        for c in range(1, CUES_PER_BLOCK + 1):
            if c in blk.get("miss", ()):
                out.append("trial %d %d %s %d miss" % (n, b, L, c))
            out.append("trial %d %d %s %d %d" % (n, b, L, c, blk["ms"][c - 1]))
        out.append("trial block %d %d %s %d %d %d" % (n, b, L, CUES_PER_BLOCK, len(blk.get("miss", ())), median(blk["ms"])))
    abort = script.get("abort")
    if abort:
        out.append("trial sitting %d aborted %d" % (n, abort[0]))
    else:
        out.append("trial sitting %d done" % n)
    return out


def sittings_of(notes):
    """The journal grouped by sitting, in order: [{"sitting", "order", "blocks": {b: block note},
    "hits": {b: [ms...]}, "misses": {b: n}, "end": "done"|"aborted"|None, "aborted": b, "verdict": L|None}]."""
    out, cur = [], None
    for text in notes:
        p = parse_note(text)
        if p is None:
            continue
        if p["kind"] == "sitting":
            cur = {"sitting": p["sitting"], "order": p["order"], "blocks": {}, "hits": {}, "misses": {},
                   "end": None, "aborted": None, "verdict": None}
            out.append(cur)
        elif cur is None:
            continue
        elif p["kind"] == "hit":
            cur["hits"].setdefault(p["block"], []).append(p["ms"])
        elif p["kind"] == "miss":
            cur["misses"][p["block"]] = cur["misses"].get(p["block"], 0) + 1
        elif p["kind"] == "block":
            cur["blocks"][p["block"]] = p
        elif p["kind"] == "done":
            cur["end"] = "done"
        elif p["kind"] == "aborted":
            cur["end"], cur["aborted"] = "aborted", p["block"]
        elif p["kind"] == "verdict":
            cur["verdict"] = p["layout"]
    return out


def check_blocks(notes):
    """Every block note against its own hits: ten hits, the misses counted, the median
    recomputed by the rule and equal. A list of problems, empty when the record agrees."""
    problems = []
    for s in sittings_of(notes):
        for b, p in sorted(s["blocks"].items()):
            hits = s["hits"].get(b, [])
            if len(hits) != CUES_PER_BLOCK or p["hits"] != CUES_PER_BLOCK:
                problems.append("sitting %d block %d: %d hit notes, the block note says %d hits" % (s["sitting"], b, len(hits), p["hits"]))
                continue
            if p["misses"] != s["misses"].get(b, 0):
                problems.append("sitting %d block %d: %d miss notes, the block note says %d" % (s["sitting"], b, s["misses"].get(b, 0), p["misses"]))
            if p["median"] != median(hits):
                problems.append("sitting %d block %d: the median of its hits is %d, the block note says %d" % (s["sitting"], b, median(hits), p["median"]))
            if p["layout"] != layout(s["sitting"], b):
                problems.append("sitting %d block %d: layout %s, the order gives %s" % (s["sitting"], b, p["layout"], layout(s["sitting"], b)))
    return problems


def table_of(notes):
    """The app panel's table per sitting: [(sitting number, [rows])]."""
    out = []
    for s in sittings_of(notes):
        rows = ["sitting %d %s" % (s["sitting"], s["order"])]
        for b, p in sorted(s["blocks"].items()):
            rows.append("%d %s %d %d %d" % (b, p["layout"], p["hits"], p["misses"], p["median"]))
        if s["end"] == "done":
            rows.append("done")
        elif s["end"] == "aborted":
            rows.append("aborted %d" % s["aborted"])
        if s["verdict"]:
            rows.append("verdict %s" % s["verdict"])
        out.append((s["sitting"], rows))
    return out


def verdict_detail(notes):
    """(the sittings judged, wins for B, A misses, B misses) over the first three done sittings,
    or None before there are three."""
    done = [s for s in sittings_of(notes) if s["end"] == "done"][:SITTINGS_NEEDED]
    if len(done) < SITTINGS_NEEDED:
        return None
    wins = ma = mb = 0
    for s in done:
        for p in range(PAIRS_PER_SITTING):
            b1, b2 = s["blocks"][2 * p + 1], s["blocks"][2 * p + 2]
            a, b = (b1, b2) if b1["layout"] == "A" else (b2, b1)
            wins += b["median"] < a["median"]
            ma += a["misses"]
            mb += b["misses"]
    return [s["sitting"] for s in done], wins, ma, mb


def verdict_of(notes):
    d = verdict_detail(notes)
    if d is None:
        return None
    _, wins, ma, mb = d
    return "B" if wins >= WINS_NEEDED and mb <= ma else "A"


def sitting_number(notes):
    return sum(1 for t in notes if (parse_note(t) or {}).get("kind") == "sitting") + 1


def default_layout(notes):
    last = 0
    for t in notes:
        p = parse_note(t)
        if p and p["kind"] == "verdict":
            last = 1 if p["layout"] == "B" else 0
    return last


def is_reserved(line):
    return line.startswith(NOTE_PREFIX)


def mode_word_7d(obs):
    if obs["mode"] == MODE_TRIAL:
        return ("trial %s %d/%d" % ("AB"[obs["trial_layout"]], obs["trial_block"], BLOCKS)).ljust(18)
    return mode_word(obs["mode"], obs["name"])


def parse_obs_7d(page):
    obs = parse_obs_6c(page)
    for field, off in OBS_7D.items():
        obs[field], = struct.unpack_from("<Q", page, off)
    return obs
```
