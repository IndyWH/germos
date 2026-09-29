
## Ring 8t — trial two

**Ring 8t, plan item 10. Appended by the owner's own hand; frozen with the
rest of this file.** Everything above this heading stands **byte for
byte**: the 6a document, the 6c section, the 7d section, and what
`stage7/DISK.md` and `stage8/PARTS.md` added to the page. This section adds
**trial two**: an N-of-1 crossover of the choices row, layout G (B's zones,
labels and targets as plain text with `|` separators) against layout B (the
boxes), run by the machine on its own human.

The design, the cue table, the score, the verdict rule, the notes, the
serial and boot lines, the refusals, the offer and six worked examples are
in **`trials/TRIALS2.md`**. That is the frozen text the assembler implements
and `trials/trials2.py` and `trials/checktrials2.py` parse by. This section
holds what changes on the page, on the strip, in the cells, in the click
rule and at the prompt.

It **supersedes five sentences**, exactly as TRIALS2.md states them:
1. **The 7d section's reserved prefix** ("a typed line whose first six bytes are `trial `") widens to a first word of `trial`, or `trial` followed only by digits.
2. **The 7d section's default read at boot** is the last verdict note of either family, `trial verdict …` or `trial2 verdict …`.
3. **`trial_layout` and `layout_default`** gain the value 2, G.
4. **NOTEBOOK.md's replay** does not draw a note beginning `trial2 `, though it is counted.
5. **Enter on an empty prompt line** is `! trial 2` while trial two is in progress.

If it is wrong, that is a spec question for the owner, not an edit.

### The obs page, at `0x340`

One word of the 7d section's four reserved words is taken:

| Offset | Field | Written by | Meaning |
|---|---|---|---|
| `0x340` | `trial_number` | BSP | 2 from a trial-two sitting's start to the boot's end; 0 on every other boot. Trial one never writes it |

The words from `0x348` to `0x358` stay zero. `0x360` is PARTS.md's
`molt_overflows`, unchanged.

The 7d section's words keep their meanings, with these additions:
- `trial_layout` and `layout_default` gain 2, G;
- `trial_block` is 0 during the warm-up and the rest after it;
- `trial_cue` runs 1–20, or 1–10 in the warm-up.

### The mode

`mode` 5 is the 7d section's `trial`. **During a trial-two sitting the mode
word is `trial2 <L> <b>/8`** — `trial2 G 3/8`, and `trial2 B 0/8` in the
warm-up's second half. L is `trial_layout`, the current cue's layout, and b
is `trial_block`. The word is twelve characters, space-padded to the field's
18. No field of the strip shows a trial time.

### Layout G, and the click on it

**Outside a sitting the row is layout G when `layout_default` is 2.**
During a trial-two sitting it is layout G in a G block, or on a G cue of
the warm-up. For a row of *n* items on *C* columns:
- **The zones are the 7d section's boxes:** `w = ⌊C / n⌋`; zone *i* spans `i·w … (i+1)·w − 1`, and the last zone `(n−1)·w … C−1`.
- **The label**, the item's text exactly as layout A spells it, sits on row `R−2` at the 7d section's label column, in normal cells.
- **The gap column** of every zone but the last holds `|` on both rows, in normal cells.
- **Every other cell** is a space. No cell of layout G carries bit 7.

**The click rule** of the 6c section holds with the boxes' filled spans as
the targets. A button-1 press on any cell of a zone's filled span, on
either row, is that item, with the kind and argument the item has in
layout A. A press on a `|` column does nothing but the count. The items are
the row's items for the state, never more than five. During a rest both
rows are blank.

**During a block of a trial-two sitting** the row shows the four items of
the state-3 row, `? ask   ! grow   Tab app   Esc exit`, in the cue's layout,
and nothing on the row acts. The 7d section's hit, miss, pause and count
rules hold unchanged. Keys are counted and dropped, and Esc aborts the
sitting. At the question after the last block, one key answers it: `g`,
`b` or `n` (either case). Esc there skips the question instead of aborting.

### `! trial 2`, the prefix, Enter and the replay

**A `!` line whose body is the seven bytes `trial 2`** is answered by the
machine before the home lookup and before the broker, as `trial` is. It
refuses, in this order:
1. `no mouse`, unless a part is live in the `i8042` slot this boot;
2. `an app is running`;
3. `one sitting a boot`, shared with trial one;
4. `trial 2 concluded`;
5. `a part is in the pointer's slot`, when the slot's state by its `molt` notes is shadow or live.

**A typed line whose first word is `trial`, or `trial` followed only by
digits,** is never a note: `trial is reserved`, one in `errors`, nothing
journaled.

**While trial two is in progress** — a `trial2 sitting` note on the
notebook and no `trial2 verdict` note:
- the conversation panel shows, after the boot's replay, `trial 2 sitting <N>: press Enter to start`;
- Enter on an empty prompt line is `! trial 2`, its refusals included.

**The boot's replay does not draw a note beginning `trial2 `**, so no trial
time or score is on the screen before the verdict.

### The rest of trial two

Everything else is `trials/TRIALS2.md`'s, with its six worked examples and
its Python:
- the warm-up, the cue table, the orders `GBBG BGGB` / `BGGB GBBG`, the 500 ms pause and the 5000 ms rest;
- the block score, and the verdict on the sign of S over the first four done sittings;
- the notes and their raw serial lines (`trial2: …`, after `keyboard ready`, never the tee), and the boot's raw line (`trial2: due sitting <N>`, or `trial2: concluded verdict <L> default <L>`);
- the question, the counts, the four tables in the app panel at the verdict, the flush and `saved - power off when you like`.

The rehearsal's criteria are untouched: an app still cannot reach the row,
and the twin never runs a trial.
