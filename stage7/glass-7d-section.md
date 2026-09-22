
## Ring 7d — the trials

**Stage 7 ring 7d, plan item 9. Appended by the owner's own hand; frozen
with the rest of this file.** Everything above this heading stands **byte
for byte** — the 6a document, the 6c section, and what `stage7/DISK.md`
added to the page at `0x2C0`–`0x2D0`. This section adds **the trial**: an
N-of-1 crossover of the choices row, layout A (the row as the 6c section
draws it) against layout B (the same items as boxes), run by the machine
on its own human. The design, the cue table, the notes, the serial lines,
the verdict rule and two worked examples are in **`stage7/TRIALS.md`**,
the frozen text the assembler implements and `stage7/trials.py` and
`stage7/checktrials.py` parse by; this section holds what changes on the
page, on the strip, in the cells and in the click rule. It **supersedes
one sentence** of the 6c text and one of DISK.md: "The rest of the page,
from `0x2C0`, is zero" and "`0x2D8` onward is zero" hold from **`0x360`**
from this ring on. It supersedes one sentence of HOME.md: a `!` line whose
body is the five bytes `trial` is answered by the machine before the home
lookup and before the broker, as `undo install` is. And it supersedes one
sentence of NOTEBOOK.md: a typed line whose first six bytes are `trial `
is never a note — it is refused with `trial is reserved`, one in `errors`,
nothing journaled — because the journal's `trial ` prefix belongs to the
machine alone. If it is wrong, that is a spec question for the owner, not
an edit.

### The obs page, from `0x2E0`

Sixteen `u64` words, one writer each. `0x2D8` is zero.

| Offset | Field | Written by | Meaning |
|---|---|---|---|
| `0x2E0` | `trial_sitting` | BSP | the sitting number while a sitting runs, and the last sitting's after it; 0 before any |
| `0x2E8` | `trial_block` | BSP | the block, 1–8, while a sitting runs; 0 outside one (it advances at a rest's end) |
| `0x2F0` | `trial_layout` | BSP | the current block's layout, 0 A, 1 B |
| `0x2F8` | `trial_cue` | BSP | the cue's index in its block, 1–10; 0 while no cue shows |
| `0x300` | `trial_target` | BSP | the item cued: 0 `ask`, 1 `grow`, 2 `app`, 3 `exit` |
| `0x308` | `cue_stamp` | glass | the TSC at the end of the frame copy that painted the cue |
| `0x310` | `cue_pending` | BSP sets, glass clears | |
| `0x318` | `trial_hits` | BSP | hits in the current block |
| `0x320` | `trial_misses` | BSP | misses in the current block |
| `0x328` | `hit_last` | BSP | the last hit's cue-to-hit, ticks |
| `0x330` | `hit_worst` | BSP | the worst this boot |
| `0x338` | `layout_default` | boot, BSP at a verdict | what the row shows outside a trial: 0 A, 1 B — the last `trial verdict` note on the notebook, read at boot |
| `0x340`–`0x358` | reserved | — | four words, zero |

The rest of the page, from `0x360`, is zero.

**The cue's stamp** is the mirror of `echo_pending`: the boot processor
writes the cue line `click: <word>` into the conversation surface, sets
`trial_target` and `trial_cue`, then sets `cue_pending`; the glass core's
frame snapshots `cue_pending` before its copies and, at the end of the
copy, writes `cue_stamp` = `rdtsc` and clears it — every frame, whatever
else is pending. A cue is showing from that frame's end until its hit.

### The mode

**`mode` gains the value 5, `trial`.** The strip's mode word for it is
`trial <L> <b>/8` — `trial A 3/8`: the block's layout, the block, of
eight — eleven characters, space-padded to the field's 18 as every mode
word is. The trial is a visible mode, never a hidden one. The main loop
does not `hlt` while a sitting runs, as it does not while an app runs: it
watches the TSC for the pause's end and the rest's end.

### The inverse cell

**A surface cell byte with bit 7 set is drawn inverse:** `0x80 | ch` for
`ch` in `0x20`–`0x7E` is the glyph of `ch` in the background colour on the
foreground colour; **`0xA0`** is the solid foreground cell. `draw_cell`
swaps the two colours for such a byte and paints the glyph of `ch & 0x7F`.
No cell of layout A, of the strip, of the conversation or of an app ever
carries bit 7; the twin never sees one (its disk holds no verdict and it
never types `! trial`), so the 6a text's cell rules stand for everything
but layout B's two rows. Two colours, as everything.

### Layout B, and the click on the boxes

Outside a trial the row is layout B when `layout_default` is 1; during a
trial it is layout B in a B block. For a row of *n* items on *C* columns:
`w = ⌊C / n⌋`; box *i* spans columns `i·w … (i+1)·w − 1`, the last box
`(n−1)·w … C−1`; the last column of every box but the last is a gap,
background on both rows; every other cell of the box on rows `R−2` and
`R−1` is filled (`0xA0`), the label — the item's text, exactly as layout A
spells it — on row `R−2` from `first + ⌊(filled − len) / 2⌋`, inverse. The
items are the row's items for the state, as the 6a table and HOME.md's
extension give them, never more than five. **The click rule** of the 6c
section holds with the boxes as the targets: a button-1 press on any
filled cell of a box, either row, is that item, with the kind and the
argument the item has in layout A — `? ask` types `?`, `! grow` types `!`,
an installed app's item types its launch line on an empty prompt line,
`Esc exit` is Esc, `Tab …` is Tab; a press on a gap cell does nothing but
the count. The hit table is the boxes' filled spans, one entry each.

**During a block of a trial** the row shows the four items of the
state-3 row, `? ask   ! grow   Tab app   Esc exit`, in the block's layout,
and **nothing on the row acts**: a button-1 press on the cued item's
target while a cue shows is a hit, on anything else a miss, while no cue
shows (the pause after a hit, the rest between blocks, the frame before
the cue's paint) nothing but the count in `clicks`; buttons 2 and 3 are
counted and nothing more; `hits` (the 6c counter of presses that acted) is
not incremented in mode 5. Keys in mode 5 are counted in `keys` and
dropped, but Esc aborts the sitting. During a rest both rows are blank.

### The rest of the trial

Everything else — `! trial` and its four refusals (`no mouse`, `an app is
running`, `one sitting a boot`, `trial concluded`), the cue table, the
orders `ABBA BAAB` / `BAAB ABBA`, the 500 ms pause and the 2000 ms rest,
the median rule, the notes and their raw serial lines (`trial: …`, after
`keyboard ready`, never the tee), the table in the app panel, the verdict
over the first three `done` sittings at ten of twelve with misses not
worse, the sitting number — is `stage7/TRIALS.md`'s, with its two worked
examples and its Python. The rehearsal's criteria are untouched: an app
still cannot reach the row, and the twin never runs a trial.
