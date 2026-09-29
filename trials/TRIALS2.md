# TRIALS2.md — trial two: the choices row, G against B

**Ring 8t, plan item 2. Frozen behind the hook from item 9.** The
assembler implements this document; `trials/trials2.py` and
`trials/checktrials2.py` parse by it. One text, three readers. If it is
wrong, that is a spec question for the owner, not an edit.

The trial's pre-registration is `trials/spec-trial2.md`, approved by the
owner on 27 September 2026, with its **Amendment 1** of 28 September 2026.
The plan is `trials/plan-8t.md`, with Cowork's amendments A1–A5. This
document is the spec made exact. Where the spec left a format to the plan,
the plan's decision is written here as the rule.

`stage7/TRIALS.md` is **untouched** and still holds trial one: its notes
(`trial `), its word (`! trial`), its refusals, its tables and its verdict.
Everything GLASS.md (with its 6c and 7d sections), NOTEBOOK.md, HOME.md,
DISK.md, TRIALS.md and PARTS.md say still stands, except the sentences
below.

## What this document supersedes

It supersedes **five sentences**, and nothing else:

1. **TRIALS.md, the reserved prefix** ("a typed line whose first six bytes are `trial ` is never a note"). From this ring on, a typed line whose **first word** is `trial`, or `trial` followed only by digits (`trial2`, `trial3`), is never a note. The first word is the bytes before the first space, or the whole line when it holds no space. At Enter it is refused with the console line `trial is reserved`, one in `errors`, nothing journaled, and the prompt returns. `trials are fun` is a note, as ever.
2. **TRIALS.md and GLASS.md's 7d section, the default read at boot** ("the last `trial verdict` note"). At boot the machine takes **the last verdict note of either family**, in journal order, into `layout_default`: `trial verdict A` or `trial verdict B`, or this document's `trial2 verdict G <mean>` or `trial2 verdict B <mean>`.
3. **TRIALS.md, the values of `trial_layout` and `layout_default`** ("0 A, 1 B"). Both gain **2, G**.
4. **NOTEBOOK.md, the replay** ("on a recognised disk, every note is drawn on the console on boot, in order"). A note beginning `trial2 ` is **not drawn** at boot. It is still counted: `S7: notebook N notes` and `n` on the strip count it, and it is on the disk like any note. Trial two's times stay hidden until the verdict (the spec's decision 7), and a replay would show them.
5. **GLASS.md 6a, Enter on an empty prompt line** ("nothing is journaled; a fresh prompt"). **While trial two is in progress** (below), Enter on an empty prompt line is `! trial 2`.

## The row and the items

The control trialled is trial one's: the **choices row**, rows `R−2` and
`R−1` of the console. During every block of a sitting the row shows the
**four items of the state-3 row**, `? ask`, `! grow`, `Tab app`, `Esc
exit`, with trial one's label words (the cue) and indices (`trial_target`:
0 `ask`, 1 `grow`, 2 `app`, 3 `exit`).

**Layout B** is trial one's boxes, exactly (TRIALS.md, "Layout B — the
boxes").

**Layout G, the grouped text row**, is B's geometry drawn as plain text.
For a row of *n* items on a console *C* cells wide:

- **The zones are B's boxes:** `w = ⌊C / n⌋`; zone *i* spans columns `i·w … (i+1)·w − 1`, and the last zone `(n−1)·w … C−1`.
- **The label** — the item's text, exactly as layout A spells it — sits on row `R−2` at B's column, `first + ⌊(filled − len) / 2⌋`, in **normal cells** (no bit 7).
- **The separator:** B's gap column of every zone but the last holds `|` (`0x7C`) in a normal cell, on **both** rows.
- **Every other cell** of both rows is a space.
- **The targets are B's filled spans, exactly.** A button-1 press on any cell of a zone's filled span, either row, is that item, with the kind and the argument the item has in layout A (GLASS.md 7d, "Layout B, and the click on the boxes"). A press on a `|` column does nothing but the count.

So G and B differ in one thing only: whether the box is painted.

**When the row is layout G:** during a G block of a trial-two sitting, or a
G cue of its warm-up; and outside a sitting when `layout_default` is 2, for
every row state, exactly as B is drawn when it is 1. The items shown are
the row's items for the state, as GLASS.md's table and HOME.md's extension
give them. During a rest both rows are blank.

**On the twin and the HP** (1920x1080, C = 120), G's labels and separators:

- the four-item row, `? ask   ! grow   Tab app   Esc exit`: labels at columns 12–16, 41–46, 71–77 and 101–108; `|` at 29, 59 and 89;
- the two-item prompt row with nothing installed, `? ask   ! grow`: labels at 27–31 and 87–92; `|` at 59;
- the three-item prompt row with one app, `? ask   ! grow   ! calculator`: labels at 17–21, 56–61 and 94–105; `|` at 39 and 79.

## The design

An N-of-1 crossover, pre-registered in the spec and made exact here,
deterministic so the twin can check it.

**A block** is twenty cues on one layout. **Block 0, the warm-up,** is ten
cues at the start of every sitting: cues 1–5 on the order's first letter's
layout and cues 6–10 on the other. So odd sittings warm up G then B, and
even sittings B then G. The warm-up is never trial data.

**The cue table** — the words of each block, fixed by block number. Each
block row holds each word five times and none twice running, and each
word opens two blocks. The warm-up row holds each word at least twice and
none twice running, and each half holds all four words:

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

**A sitting** is the warm-up and eight blocks. **The block order** is by the
sitting's parity: odd sittings `GBBG BGGB`, even sittings `BGGB GBBG`; block
*b*'s layout is the order's *b*-th letter with the space removed. **The
pairs** are blocks (1,2), (3,4), (5,6) and (7,8) of one sitting, one G and
one B in each by construction. Four pairs a sitting, and four sittings give
every block number both layouts exactly twice.

**The sitting number** is one more than the number of `trial2 sitting <n>
<order>` notes already on the notebook, in journal order. An aborted
sitting counts: it was started.

**The trial** is **the first four sittings that ended in `done`**, in
sitting order: sixteen pairs. **One sitting a boot**, shared with trial
one: after a sitting of either trial has ended in this boot (`done` or
`aborted`), the next one is refused.

## A sitting, step by step

**`! trial 2`** is a reserved word of the `!` line: a body equal to the
seven bytes `trial 2` and nothing else, after GERMLINE.md's marker parse
and trim. It is judged before the home lookup and before the broker, as
`trial` is. `! trial` stays trial one's. A `trial` body followed by
anything else is not reserved and takes its road as ever. `! trial 2`
refuses, with a console line, one in `errors`, nothing journaled, in this
order:

| Line | When |
|---|---|
| `no mouse` | `mouse_id` is 0 and no part is live in the `i8042` slot this boot. A live part resets the mouse itself, so the seed's `mouse_id` stays 0 on such a boot, and the part refusal below is the answer there |
| `an app is running` | `mode` is 3 |
| `one sitting a boot` | a sitting of either trial ended in this boot |
| `trial 2 concluded` | a `trial2 verdict` note is on the notebook |
| `a part is in the pointer's slot` | the `i8042` slot's state, as its `molt` notes give it (PARTS.md, "The states and the undo"), is shadow or live |

A demoted slot is not refused: its part is never loaded, and the generic
driver serves the pointer.

Otherwise the sitting begins:

1. The sitting number and the order, by the rules above.
2. The note `trial2 sitting <n> <order>` and its serial line.
3. The app panel cleared, and the console line `sitting <n> <order>`.
4. `mode` 5, `trial_number` 2, `trial_block` 0, and the obs fields.
5. The row set to the four items in the warm-up's first layout, and the first cue.

**The cue** is trial one's: the console line `click: <word>`, console-only,
with `cue_pending` and `cue_stamp` exactly as TRIALS.md says. A cue is
**showing** from the end of the frame that painted it until its hit.

**A press** is button 1's bit going from clear to set in a packet; every
pressed bit counts one in `clicks` first, as ever. `hits` (ring 6c's
counter) is not incremented in mode 5.

| The press | What happens |
|---|---|
| button 1 on the **cued item's target** while a cue is showing | a **hit**: `cue-to-hit = (press stamp − cue_stamp) / tsc_per_ms`, integer division; `hit_last` and `hit_worst` (ticks); `trial_hits + 1`; the note `trial2 <s> <b> <L> <c> <ms>` and its line; then **the pause** |
| button 1 **anywhere else** while a cue is showing — another item's target, a gap or `|` column, the strip, either panel | a **miss**: `trial_misses + 1`; the note `trial2 <s> <b> <L> <c> miss` and its line; **the cue stays** |
| button 1 while **no cue is showing** | nothing but the count in `clicks` |
| button 2 or 3 anywhere | nothing but the count |

`<L>` is the cue's layout: the block's, or in the warm-up the cue's own.

**The pause** is 500 ms after a hit, `pause_until = press stamp + 500 ×
tsc_per_ms`, with the row unchanged. Then comes the next cue, or the
block's end after its last cue.

**Keys** in mode 5 are counted in `keys` as ever and dropped, **except Esc,
which aborts** (below), and except the preference key at the question
(below).

**The block's end.**
- **After the warm-up's tenth hit and its pause:** no block note. Then `trial_cue` 0, the row blank, the console line `warm-up done - rest`, and the rest.
- **After a block's twentieth hit and its pause (blocks 1–8):** the block note `trial2 block <s> <b> <L> 20 <misses> <score>` and its line; then `trial_cue` 0 and the row blank. After blocks 1–7 comes the console line `block <b> of 8 - rest` and the rest.
- **The rest** is 5000 ms. At its end: `trial_block + 1`, `trial_layout` by the order, `trial_hits` and `trial_misses` 0, the row set in the new layout, and the first cue of the new block.
- **After block 8** there is no rest: the sitting's end follows.

**The block score**, in ms per cue: the twenty cue-to-hit values sorted
ascending; the fastest two and the slowest two dropped; the middle sixteen
summed and divided by sixteen, integer division; plus **100 for each miss**
in the block (the spec's miss charge of 2000 ms × misses / 20 cues):

```
score = (v3 + v4 + … + v18) / 16 + 100 × misses
```

**The sitting's end**, in this order:

1. The note `trial2 sitting <n> done` and its line.
2. **The verdict note**, if this is the fourth sitting that ended in `done`: `trial2 verdict <L> <mean>` by the rule below, and its line; `layout_default` set to it (1 B, 2 G). It is journaled here, before the question, so a machine powered off at the question still holds its verdict. Nothing of it is shown yet.
3. **The question:** the console line `easier? g, b or n`. One key answers:
   - `g`, `b` or `n` (either case) journals `trial2 prefer <n> <key>`, lowercase;
   - Esc journals `trial2 prefer <n> skip` — at the question Esc is a skip, not an abort;
   - every other key is counted and dropped, and presses count in `clicks` only.
4. The console lines `sitting <n> done` and `hits <h> misses <m>`, counted over blocks 1–8 (the warm-up is not in them). **No time and no score is shown.**
5. **At the verdict:** the console line `verdict <L> <mean>`, and the app panel cleared and holding **the four judged sittings' tables, stacked** from row 0, column 0, then the row `verdict <L> <mean>`. A sitting's table is:
   - `sitting <n> <order>`;
   - eight rows `<b> <L> 20 <misses> <score>`;
   - `done`;
   - `prefer <answer>`, when the sitting has a prefer note.
6. **The flush:** ATA FLUSH CACHE EXT (`0xEA`) through the loader's `ahci_cmd`, with AL `0xEA`, EBX 0, DL 0 and a 512-byte scratch buffer in RDI. `ahci_cmd` returns only on success. A failure is the loader's named `ERR:` line and a halt: every note is already written, and there is no `saved` line.
7. The console line **`saved - power off when you like`**.
8. `mode` 0 and the prompt, with the row in the layout `layout_default` gives. The keys and presses made meanwhile are discarded, as after any answer.

**Esc** at any moment of mode 5 before the question aborts the sitting:
1. The note `trial2 sitting <n> aborted <b>` and its line. *b* is the block in play: 0 in the warm-up, and during a rest the block that would have followed.
2. The hit and miss notes already journaled stand (the journal is append-only), but no block note is written for *b*, so it enters no score and no verdict.
3. The console lines `sitting <n> aborted <b>` and `hits <h> misses <m>`. No table and no score.
4. The flush, then `saved - power off when you like`.
5. `mode` 0 and the prompt.

## The verdict rule

Pre-registered (the spec's R1, decision 12, and the plan's amendment A1).
Over **the first four sittings that ended in `done`**, in sitting order,
take the sixteen pairs. In each pair, **`d = score(G) − score(B)`**: a
positive `d` favours B. **S** is the sum of the sixteen `d`.

**B becomes the default if S > 0. Otherwise G: S ≤ 0, the exact tie at 0
included.**

**The note carries the mean**, `S / 16` **truncated toward zero** — a
record of the size, which never enters the decision. So a near-tie reads
`verdict B 0` or `verdict G 0`, and is visible on the record as one. It is
written signed, with no leading zero: `-53`, `0`, `65`.

An aborted sitting's completed blocks stand on the record and are outside
the verdict. Nothing else is looked at.

**Where the verdict lives:** on the notebook, as `trial2 verdict <L>
<mean>`. At boot the machine takes the last verdict note of either family
into `layout_default` (superseded sentence 2). The row shows that layout at
the prompt from then on. Trial one's record is never touched: its notes,
its tables and its verdict A stand, and `stage7/trials.py` still prints
them.

## Amendment 1: the offer, Enter, the saved line, the boot line

**Trial two is in progress** when the notebook holds a `trial2 sitting
<n> <order>` note and no `trial2 verdict` note. The machine reads it at
boot, in the replay's walk, and again at the moment of need.

**The offer.** On a boot where trial two is in progress, after the replay,
the conversation panel gets one console line:

```
trial 2 sitting <N>: press Enter to start
```

N is the next sitting number. With no trial-two note on the disk there is
no offer.

**Enter.** While trial two is in progress, **Enter on an empty prompt line
is `! trial 2`**: the same start, and the same refusals in the same order.
So after a sitting has ended in this boot, an empty Enter answers `one
sitting a boot`; while an app runs with the keys at the prompt, `an app is
running`. When trial two is not in progress, Enter on an empty line is what
it has always been.

**The saved line** is the sitting's end's step 7 and the abort's step 4,
above. It follows the flush, so every note of the sitting is on the disk
when it shows.

**The boot line.** On a boot whose notebook holds any `trial2 ` note, the
machine writes **one raw serial line** straight after the replay and before
the first prompt. It names the next sitting due while the trial is in
progress, or the verdict and the default layout once concluded:

```
trial2: due sitting <N>
trial2: concluded verdict <L> default <L>
```

On a boot whose notebook holds no `trial2 ` note there is no such line. The
boot line is not a note: no note's second word is `due` or `concluded`.

## The notes

Every event is one note, NOTEBOOK.md's record unchanged, written by the
machine alone: printable ASCII, single spaces, decimal numbers without
leading zeros. `L` is the layout letter `G` or `B`:

```
trial2 sitting 1 GBBG BGGB        the sitting number, the order
trial2 1 0 G 3 1488               sitting, block (0 is the warm-up), layout, cue, ms - a hit
trial2 1 0 G 4 miss               sitting, block, layout, cue - a miss; the cue stays
trial2 block 1 2 B 20 1 1561      sitting, block (1-8), layout, hits, misses, score
trial2 sitting 1 done
trial2 sitting 1 aborted 3        the block in play; 0 in the warm-up
trial2 verdict B 57               the layout, then the mean; after the fourth done note
trial2 prefer 1 b                 g, b, n, or skip for Esc at the question
```

The notes of one cue are in journal order: its misses, then its hit. A
block note follows its twentieth hit. At the fourth `done` sitting the
verdict note follows the done note and precedes the prefer note.

## The serial lines

Each note goes to serial at the moment it is journaled, **raw UART** —
never the tee, so nothing lands in the conversation — as the note with its
first word replaced: `trial2:` followed by the note from its seventh byte.

```
trial2: sitting 1 GBBG BGGB
trial2: 1 0 G 3 1488
trial2: 1 0 G 4 miss
trial2: block 1 2 B 20 1 1561
trial2: sitting 1 done
trial2: sitting 1 aborted 3
trial2: verdict B 57
trial2: prefer 1 b
```

With the two boot lines above, these are the only `trial2:` lines. So the
chart on the HP carries each sitting without a flash to read the disk, and
`trials2.py --serial` and `--status` read it back.

## The strip

`mode` 5 is trial one's `trial`. During a trial-two sitting the mode word is
**`trial2 <L> <b>/8`** — `trial2 G 3/8`, and `trial2 B 0/8` in the warm-up's
second half. L is `trial_layout`, the current cue's layout; b is
`trial_block`. That is twelve characters, space-padded to the field's 18. No
field of the strip shows a trial time.

## The obs page

Trial one's sixteen words from `0x2E0` keep their meanings, with these
additions:
- `trial_layout` and `layout_default` gain 2, G;
- `trial_block` is 0 during the warm-up and the rest after it;
- `trial_cue` runs 1–20, or 1–10 in the warm-up.

One word of trial one's four reserved words is taken:

| Offset | Field | Written by | Meaning |
|---|---|---|---|
| `0x340` | `trial_number` | BSP | 2 from a trial-two sitting's start to the boot's end; 0 on every other boot. Trial one never writes it |

The three words from `0x348` to `0x358` stay zero. `0x360` is PARTS.md's
`molt_overflows`, unchanged.

## Worked example A — one scripted sitting

Sitting 1, `GBBG BGGB`: a miss in the warm-up (cue 4), a miss in block 1
(G, cue 7) and a miss in block 3 (B, cue 12), answered `b` at the question.
The 184 notes, in journal order — exactly what the notes partition holds
after the sitting; the serial lines are these with `trial2` → `trial2:`:

```
trial2 sitting 1 GBBG BGGB
trial2 1 0 G 1 1819
trial2 1 0 G 2 1882
trial2 1 0 G 3 1736
trial2 1 0 G 4 miss
trial2 1 0 G 4 1919
trial2 1 0 G 5 1879
trial2 1 0 B 6 1507
trial2 1 0 B 7 1826
trial2 1 0 B 8 1755
trial2 1 0 B 9 1481
trial2 1 0 B 10 1502
trial2 1 1 G 1 1441
trial2 1 1 G 2 1606
trial2 1 1 G 3 1745
trial2 1 1 G 4 1451
trial2 1 1 G 5 1441
trial2 1 1 G 6 1393
trial2 1 1 G 7 miss
trial2 1 1 G 7 1827
trial2 1 1 G 8 1810
trial2 1 1 G 9 1940
trial2 1 1 G 10 1475
trial2 1 1 G 11 1936
trial2 1 1 G 12 1803
trial2 1 1 G 13 1576
trial2 1 1 G 14 1392
trial2 1 1 G 15 1536
trial2 1 1 G 16 1911
trial2 1 1 G 17 1505
trial2 1 1 G 18 1591
trial2 1 1 G 19 1706
trial2 1 1 G 20 1547
trial2 block 1 1 G 20 1 1723
trial2 1 2 B 1 1456
trial2 1 2 B 2 1891
trial2 1 2 B 3 1781
trial2 1 2 B 4 1399
trial2 1 2 B 5 1353
trial2 1 2 B 6 1659
trial2 1 2 B 7 1853
trial2 1 2 B 8 1465
trial2 1 2 B 9 1713
trial2 1 2 B 10 1429
trial2 1 2 B 11 1309
trial2 1 2 B 12 1605
trial2 1 2 B 13 1678
trial2 1 2 B 14 1320
trial2 1 2 B 15 1722
trial2 1 2 B 16 1550
trial2 1 2 B 17 1496
trial2 1 2 B 18 1714
trial2 1 2 B 19 1765
trial2 1 2 B 20 1528
trial2 block 1 2 B 20 0 1582
trial2 1 3 B 1 1779
trial2 1 3 B 2 1887
trial2 1 3 B 3 1318
trial2 1 3 B 4 1563
trial2 1 3 B 5 1464
trial2 1 3 B 6 1397
trial2 1 3 B 7 1628
trial2 1 3 B 8 1447
trial2 1 3 B 9 1470
trial2 1 3 B 10 1557
trial2 1 3 B 11 1721
trial2 1 3 B 12 miss
trial2 1 3 B 12 1652
trial2 1 3 B 13 1830
trial2 1 3 B 14 1526
trial2 1 3 B 15 1425
trial2 1 3 B 16 1666
trial2 1 3 B 17 1709
trial2 1 3 B 18 1855
trial2 1 3 B 19 1345
trial2 1 3 B 20 1838
trial2 block 1 3 B 20 1 1704
trial2 1 4 G 1 1552
trial2 1 4 G 2 1656
trial2 1 4 G 3 1525
trial2 1 4 G 4 1467
trial2 1 4 G 5 1452
trial2 1 4 G 6 1921
trial2 1 4 G 7 1477
trial2 1 4 G 8 1645
trial2 1 4 G 9 1654
trial2 1 4 G 10 1373
trial2 1 4 G 11 1837
trial2 1 4 G 12 1649
trial2 1 4 G 13 1564
trial2 1 4 G 14 1881
trial2 1 4 G 15 1828
trial2 1 4 G 16 1602
trial2 1 4 G 17 1888
trial2 1 4 G 18 1560
trial2 1 4 G 19 1883
trial2 1 4 G 20 1834
trial2 block 1 4 G 20 0 1663
trial2 1 5 B 1 1641
trial2 1 5 B 2 1885
trial2 1 5 B 3 1335
trial2 1 5 B 4 1486
trial2 1 5 B 5 1856
trial2 1 5 B 6 1357
trial2 1 5 B 7 1878
trial2 1 5 B 8 1664
trial2 1 5 B 9 1588
trial2 1 5 B 10 1776
trial2 1 5 B 11 1493
trial2 1 5 B 12 1767
trial2 1 5 B 13 1458
trial2 1 5 B 14 1780
trial2 1 5 B 15 1870
trial2 1 5 B 16 1573
trial2 1 5 B 17 1776
trial2 1 5 B 18 1852
trial2 1 5 B 19 1605
trial2 1 5 B 20 1388
trial2 block 1 5 B 20 0 1660
trial2 1 6 G 1 1934
trial2 1 6 G 2 1847
trial2 1 6 G 3 1730
trial2 1 6 G 4 1948
trial2 1 6 G 5 1362
trial2 1 6 G 6 1400
trial2 1 6 G 7 1708
trial2 1 6 G 8 1361
trial2 1 6 G 9 1853
trial2 1 6 G 10 1536
trial2 1 6 G 11 1715
trial2 1 6 G 12 1398
trial2 1 6 G 13 1563
trial2 1 6 G 14 1718
trial2 1 6 G 15 1630
trial2 1 6 G 16 1585
trial2 1 6 G 17 1744
trial2 1 6 G 18 1397
trial2 1 6 G 19 1776
trial2 1 6 G 20 1563
trial2 block 1 6 G 20 0 1635
trial2 1 7 G 1 1360
trial2 1 7 G 2 1432
trial2 1 7 G 3 1812
trial2 1 7 G 4 1481
trial2 1 7 G 5 1440
trial2 1 7 G 6 1815
trial2 1 7 G 7 1712
trial2 1 7 G 8 1457
trial2 1 7 G 9 1737
trial2 1 7 G 10 1685
trial2 1 7 G 11 1616
trial2 1 7 G 12 1534
trial2 1 7 G 13 1896
trial2 1 7 G 14 1509
trial2 1 7 G 15 1513
trial2 1 7 G 16 1957
trial2 1 7 G 17 1606
trial2 1 7 G 18 1803
trial2 1 7 G 19 1506
trial2 1 7 G 20 1745
trial2 block 1 7 G 20 0 1623
trial2 1 8 B 1 1840
trial2 1 8 B 2 1447
trial2 1 8 B 3 1397
trial2 1 8 B 4 1768
trial2 1 8 B 5 1545
trial2 1 8 B 6 1323
trial2 1 8 B 7 1623
trial2 1 8 B 8 1662
trial2 1 8 B 9 1430
trial2 1 8 B 10 1553
trial2 1 8 B 11 1588
trial2 1 8 B 12 1820
trial2 1 8 B 13 1690
trial2 1 8 B 14 1552
trial2 1 8 B 15 1687
trial2 1 8 B 16 1656
trial2 1 8 B 17 1850
trial2 1 8 B 18 1774
trial2 1 8 B 19 1564
trial2 1 8 B 20 1710
trial2 block 1 8 B 20 0 1629
trial2 sitting 1 done
trial2 prefer 1 b
```

Block 1's score: its twenty hits sorted, the fastest two and slowest two
dropped, the middle sixteen summed and divided by sixteen, plus 100 for its
one miss. The conversation panel's lines at the sitting's end, after its
last note:

```
easier? g, b or n
sitting 1 done
hits 160 misses 2
saved - power off when you like
```

No score is shown. The sitting's table, which the app panel shows only at
the verdict and `trials2.py` prints:

```
sitting 1 GBBG BGGB
1 G 20 1 1723
2 B 20 0 1582
3 B 20 1 1704
4 G 20 0 1663
5 B 20 0 1660
6 G 20 0 1635
7 G 20 0 1623
8 B 20 0 1629
done
prefer b
```

No verdict: one `done` sitting is four pairs. The next boot's line is
`trial2: due sitting 2`, and its offer `trial 2 sitting 2: press Enter to
start`.

## Worked example B — four sittings, verdict B

Four sittings' `sitting`, `block`, `done`, `verdict` and `prefer` notes
(the hit and miss notes left out; a real journal holds them between):

```
trial2 sitting 1 GBBG BGGB
trial2 block 1 1 G 20 0 1715
trial2 block 1 2 B 20 1 1675
trial2 block 1 3 B 20 0 1540
trial2 block 1 4 G 20 0 1726
trial2 block 1 5 B 20 0 1666
trial2 block 1 6 G 20 0 1688
trial2 block 1 7 G 20 0 1665
trial2 block 1 8 B 20 0 1676
trial2 sitting 1 done
trial2 prefer 1 b
trial2 sitting 2 BGGB GBBG
trial2 block 2 1 B 20 0 1649
trial2 block 2 2 G 20 0 1694
trial2 block 2 3 G 20 0 1745
trial2 block 2 4 B 20 0 1592
trial2 block 2 5 G 20 1 1771
trial2 block 2 6 B 20 0 1675
trial2 block 2 7 B 20 0 1651
trial2 block 2 8 G 20 0 1688
trial2 sitting 2 done
trial2 prefer 2 n
trial2 sitting 3 GBBG BGGB
trial2 block 3 1 G 20 0 1687
trial2 block 3 2 B 20 0 1620
trial2 block 3 3 B 20 0 1591
trial2 block 3 4 G 20 0 1660
trial2 block 3 5 B 20 0 1536
trial2 block 3 6 G 20 0 1707
trial2 block 3 7 G 20 0 1732
trial2 block 3 8 B 20 0 1602
trial2 sitting 3 done
trial2 prefer 3 b
trial2 sitting 4 BGGB GBBG
trial2 block 4 1 B 20 0 1567
trial2 block 4 2 G 20 0 1668
trial2 block 4 3 G 20 0 1675
trial2 block 4 4 B 20 1 1739
trial2 block 4 5 G 20 0 1653
trial2 block 4 6 B 20 1 1717
trial2 block 4 7 B 20 0 1623
trial2 block 4 8 G 20 0 1696
trial2 sitting 4 done
trial2 verdict B 65
trial2 prefer 4 g
```

The sixteen `d = score(G) − score(B)`, in pair order, sittings 1 to 4:

```
40 186 22 -11 45 153 96 37 67 69 171 130 101 -64 -64 73
1051
65
```

The first line is the sixteen `d`, the second S, the third the mean.
**S > 0: verdict B**, and the note says so, with the mean. The app panel at
the verdict:

```
sitting 1 GBBG BGGB
1 G 20 0 1715
2 B 20 1 1675
3 B 20 0 1540
4 G 20 0 1726
5 B 20 0 1666
6 G 20 0 1688
7 G 20 0 1665
8 B 20 0 1676
done
prefer b
sitting 2 BGGB GBBG
1 B 20 0 1649
2 G 20 0 1694
3 G 20 0 1745
4 B 20 0 1592
5 G 20 1 1771
6 B 20 0 1675
7 B 20 0 1651
8 G 20 0 1688
done
prefer n
sitting 3 GBBG BGGB
1 G 20 0 1687
2 B 20 0 1620
3 B 20 0 1591
4 G 20 0 1660
5 B 20 0 1536
6 G 20 0 1707
7 G 20 0 1732
8 B 20 0 1602
done
prefer b
sitting 4 BGGB GBBG
1 B 20 0 1567
2 G 20 0 1668
3 G 20 0 1675
4 B 20 1 1739
5 G 20 0 1653
6 B 20 1 1717
7 B 20 0 1623
8 G 20 0 1696
done
prefer g
verdict B 65
```

The next boot's line is `trial2: concluded verdict B default B`, and
`layout_default` is 1.

## Worked example C — the boundary

Four sittings with every block scoring 1500 and no miss:

```
trial2 sitting 1 GBBG BGGB
trial2 block 1 1 G 20 0 1500
trial2 block 1 2 B 20 0 1500
trial2 block 1 3 B 20 0 1500
trial2 block 1 4 G 20 0 1500
trial2 block 1 5 B 20 0 1500
trial2 block 1 6 G 20 0 1500
trial2 block 1 7 G 20 0 1500
trial2 block 1 8 B 20 0 1500
trial2 sitting 1 done
trial2 sitting 2 BGGB GBBG
trial2 block 2 1 B 20 0 1500
trial2 block 2 2 G 20 0 1500
trial2 block 2 3 G 20 0 1500
trial2 block 2 4 B 20 0 1500
trial2 block 2 5 G 20 0 1500
trial2 block 2 6 B 20 0 1500
trial2 block 2 7 B 20 0 1500
trial2 block 2 8 G 20 0 1500
trial2 sitting 2 done
trial2 sitting 3 GBBG BGGB
trial2 block 3 1 G 20 0 1500
trial2 block 3 2 B 20 0 1500
trial2 block 3 3 B 20 0 1500
trial2 block 3 4 G 20 0 1500
trial2 block 3 5 B 20 0 1500
trial2 block 3 6 G 20 0 1500
trial2 block 3 7 G 20 0 1500
trial2 block 3 8 B 20 0 1500
trial2 sitting 3 done
trial2 sitting 4 BGGB GBBG
trial2 block 4 1 B 20 0 1500
trial2 block 4 2 G 20 0 1500
trial2 block 4 3 G 20 0 1500
trial2 block 4 4 B 20 0 1500
trial2 block 4 5 G 20 0 1500
trial2 block 4 6 B 20 0 1500
trial2 block 4 7 B 20 0 1500
trial2 block 4 8 G 20 0 1500
trial2 sitting 4 done
trial2 verdict G 0
```

Every `d` is 0, so **S = 0, the exact tie, gives `verdict G 0`**. Two
variants, each changing one block note:

- sitting 4's block 8 (a G block) scoring **1515**: S = 15 gives **`verdict B 0`**;
- sitting 4's block 7 (a B block) scoring **1515**: S = −15 gives **`verdict G 0`**.

The decision is on S; the mean only records the size.

## Worked example D — an abort, then verdict G

Five sittings' summary notes. Sitting 2 was aborted in block 3, after its
blocks 1 and 2, with no answer. Sitting 4 was powered off at the question,
so it has no prefer note. The first four `done` sittings are 1, 3, 4 and 5:

```
trial2 sitting 1 GBBG BGGB
trial2 block 1 1 G 20 0 1605
trial2 block 1 2 B 20 0 1635
trial2 block 1 3 B 20 0 1658
trial2 block 1 4 G 20 0 1560
trial2 block 1 5 B 20 0 1719
trial2 block 1 6 G 20 0 1676
trial2 block 1 7 G 20 0 1625
trial2 block 1 8 B 20 0 1662
trial2 sitting 1 done
trial2 prefer 1 g
trial2 sitting 2 BGGB GBBG
trial2 block 2 1 B 20 0 1678
trial2 block 2 2 G 20 0 1696
trial2 sitting 2 aborted 3
trial2 sitting 3 GBBG BGGB
trial2 block 3 1 G 20 0 1553
trial2 block 3 2 B 20 0 1637
trial2 block 3 3 B 20 0 1612
trial2 block 3 4 G 20 0 1566
trial2 block 3 5 B 20 0 1593
trial2 block 3 6 G 20 0 1580
trial2 block 3 7 G 20 1 1696
trial2 block 3 8 B 20 0 1649
trial2 sitting 3 done
trial2 prefer 3 n
trial2 sitting 4 BGGB GBBG
trial2 block 4 1 B 20 0 1627
trial2 block 4 2 G 20 0 1499
trial2 block 4 3 G 20 0 1651
trial2 block 4 4 B 20 0 1716
trial2 block 4 5 G 20 0 1587
trial2 block 4 6 B 20 0 1607
trial2 block 4 7 B 20 0 1684
trial2 block 4 8 G 20 0 1594
trial2 sitting 4 done
trial2 sitting 5 GBBG BGGB
trial2 block 5 1 G 20 1 1635
trial2 block 5 2 B 20 0 1642
trial2 block 5 3 B 20 0 1712
trial2 block 5 4 G 20 0 1575
trial2 block 5 5 B 20 0 1634
trial2 block 5 6 G 20 0 1624
trial2 block 5 7 G 20 0 1597
trial2 block 5 8 B 20 0 1699
trial2 sitting 5 done
trial2 verdict G -53
trial2 prefer 5 g
```

The sixteen `d`, then S, then the mean:

```
-30 -98 -43 -37 -84 -46 -13 47 -128 -65 -20 -90 -7 -137 -10 -102
-863
-53
```

**S ≤ 0: verdict G**, the mean truncated toward zero. The app panel at the
verdict:

```
sitting 1 GBBG BGGB
1 G 20 0 1605
2 B 20 0 1635
3 B 20 0 1658
4 G 20 0 1560
5 B 20 0 1719
6 G 20 0 1676
7 G 20 0 1625
8 B 20 0 1662
done
prefer g
sitting 3 GBBG BGGB
1 G 20 0 1553
2 B 20 0 1637
3 B 20 0 1612
4 G 20 0 1566
5 B 20 0 1593
6 G 20 0 1580
7 G 20 1 1696
8 B 20 0 1649
done
prefer n
sitting 4 BGGB GBBG
1 B 20 0 1627
2 G 20 0 1499
3 G 20 0 1651
4 B 20 0 1716
5 G 20 0 1587
6 B 20 0 1607
7 B 20 0 1684
8 G 20 0 1594
done
sitting 5 GBBG BGGB
1 G 20 1 1635
2 B 20 0 1642
3 B 20 0 1712
4 G 20 0 1575
5 B 20 0 1634
6 G 20 0 1624
7 G 20 0 1597
8 B 20 0 1699
done
prefer g
verdict G -53
```

The next boot's line is `trial2: concluded verdict G default G`, and
`layout_default` is 2.

## Worked example E — both families on one notebook

A journal made of **TRIALS.md's worked example B** (trial one: four
sittings, `trial verdict B`), then these molt notes, then **this
document's worked example A**:

```
molt i8042 shadow 4fe6beefc4bc57d0 3 1000 5000
molt boot 1 i8042 shadow
molt healthy 1
molt i8042 count 1 718 21199 0
molt i8042 demoted 4fe6beefc4bc57d0 unhealthy
```

`stage7/trials.py`, frozen, prints for it exactly what it prints for
TRIALS.md's worked example B alone. It reads only notes beginning `trial `,
and no `trial2 ` note begins that way. `layout_default` is 1 (the last
verdict note is trial one's). With this document's worked example D
appended, `stage7/trials.py` still prints the same, and `layout_default` is
2 (the last verdict note is trial two's G).

## Worked example F — the blind read

A chart of two boots: the first carries worked example A's serial lines,
and the second only its boot line.

```
S7: alive
S7: keyboard ready
trial2: sitting 1 GBBG BGGB
trial2: 1 0 G 1 1819
trial2: 1 0 G 2 1882
trial2: 1 0 G 3 1736
trial2: 1 0 G 4 miss
trial2: 1 0 G 4 1919
trial2: 1 0 G 5 1879
trial2: 1 0 B 6 1507
trial2: 1 0 B 7 1826
trial2: 1 0 B 8 1755
trial2: 1 0 B 9 1481
trial2: 1 0 B 10 1502
trial2: 1 1 G 1 1441
trial2: 1 1 G 2 1606
trial2: 1 1 G 3 1745
trial2: 1 1 G 4 1451
trial2: 1 1 G 5 1441
trial2: 1 1 G 6 1393
trial2: 1 1 G 7 miss
trial2: 1 1 G 7 1827
trial2: 1 1 G 8 1810
trial2: 1 1 G 9 1940
trial2: 1 1 G 10 1475
trial2: 1 1 G 11 1936
trial2: 1 1 G 12 1803
trial2: 1 1 G 13 1576
trial2: 1 1 G 14 1392
trial2: 1 1 G 15 1536
trial2: 1 1 G 16 1911
trial2: 1 1 G 17 1505
trial2: 1 1 G 18 1591
trial2: 1 1 G 19 1706
trial2: 1 1 G 20 1547
trial2: block 1 1 G 20 1 1723
trial2: 1 2 B 1 1456
trial2: 1 2 B 2 1891
trial2: 1 2 B 3 1781
trial2: 1 2 B 4 1399
trial2: 1 2 B 5 1353
trial2: 1 2 B 6 1659
trial2: 1 2 B 7 1853
trial2: 1 2 B 8 1465
trial2: 1 2 B 9 1713
trial2: 1 2 B 10 1429
trial2: 1 2 B 11 1309
trial2: 1 2 B 12 1605
trial2: 1 2 B 13 1678
trial2: 1 2 B 14 1320
trial2: 1 2 B 15 1722
trial2: 1 2 B 16 1550
trial2: 1 2 B 17 1496
trial2: 1 2 B 18 1714
trial2: 1 2 B 19 1765
trial2: 1 2 B 20 1528
trial2: block 1 2 B 20 0 1582
trial2: 1 3 B 1 1779
trial2: 1 3 B 2 1887
trial2: 1 3 B 3 1318
trial2: 1 3 B 4 1563
trial2: 1 3 B 5 1464
trial2: 1 3 B 6 1397
trial2: 1 3 B 7 1628
trial2: 1 3 B 8 1447
trial2: 1 3 B 9 1470
trial2: 1 3 B 10 1557
trial2: 1 3 B 11 1721
trial2: 1 3 B 12 miss
trial2: 1 3 B 12 1652
trial2: 1 3 B 13 1830
trial2: 1 3 B 14 1526
trial2: 1 3 B 15 1425
trial2: 1 3 B 16 1666
trial2: 1 3 B 17 1709
trial2: 1 3 B 18 1855
trial2: 1 3 B 19 1345
trial2: 1 3 B 20 1838
trial2: block 1 3 B 20 1 1704
trial2: 1 4 G 1 1552
trial2: 1 4 G 2 1656
trial2: 1 4 G 3 1525
trial2: 1 4 G 4 1467
trial2: 1 4 G 5 1452
trial2: 1 4 G 6 1921
trial2: 1 4 G 7 1477
trial2: 1 4 G 8 1645
trial2: 1 4 G 9 1654
trial2: 1 4 G 10 1373
trial2: 1 4 G 11 1837
trial2: 1 4 G 12 1649
trial2: 1 4 G 13 1564
trial2: 1 4 G 14 1881
trial2: 1 4 G 15 1828
trial2: 1 4 G 16 1602
trial2: 1 4 G 17 1888
trial2: 1 4 G 18 1560
trial2: 1 4 G 19 1883
trial2: 1 4 G 20 1834
trial2: block 1 4 G 20 0 1663
trial2: 1 5 B 1 1641
trial2: 1 5 B 2 1885
trial2: 1 5 B 3 1335
trial2: 1 5 B 4 1486
trial2: 1 5 B 5 1856
trial2: 1 5 B 6 1357
trial2: 1 5 B 7 1878
trial2: 1 5 B 8 1664
trial2: 1 5 B 9 1588
trial2: 1 5 B 10 1776
trial2: 1 5 B 11 1493
trial2: 1 5 B 12 1767
trial2: 1 5 B 13 1458
trial2: 1 5 B 14 1780
trial2: 1 5 B 15 1870
trial2: 1 5 B 16 1573
trial2: 1 5 B 17 1776
trial2: 1 5 B 18 1852
trial2: 1 5 B 19 1605
trial2: 1 5 B 20 1388
trial2: block 1 5 B 20 0 1660
trial2: 1 6 G 1 1934
trial2: 1 6 G 2 1847
trial2: 1 6 G 3 1730
trial2: 1 6 G 4 1948
trial2: 1 6 G 5 1362
trial2: 1 6 G 6 1400
trial2: 1 6 G 7 1708
trial2: 1 6 G 8 1361
trial2: 1 6 G 9 1853
trial2: 1 6 G 10 1536
trial2: 1 6 G 11 1715
trial2: 1 6 G 12 1398
trial2: 1 6 G 13 1563
trial2: 1 6 G 14 1718
trial2: 1 6 G 15 1630
trial2: 1 6 G 16 1585
trial2: 1 6 G 17 1744
trial2: 1 6 G 18 1397
trial2: 1 6 G 19 1776
trial2: 1 6 G 20 1563
trial2: block 1 6 G 20 0 1635
trial2: 1 7 G 1 1360
trial2: 1 7 G 2 1432
trial2: 1 7 G 3 1812
trial2: 1 7 G 4 1481
trial2: 1 7 G 5 1440
trial2: 1 7 G 6 1815
trial2: 1 7 G 7 1712
trial2: 1 7 G 8 1457
trial2: 1 7 G 9 1737
trial2: 1 7 G 10 1685
trial2: 1 7 G 11 1616
trial2: 1 7 G 12 1534
trial2: 1 7 G 13 1896
trial2: 1 7 G 14 1509
trial2: 1 7 G 15 1513
trial2: 1 7 G 16 1957
trial2: 1 7 G 17 1606
trial2: 1 7 G 18 1803
trial2: 1 7 G 19 1506
trial2: 1 7 G 20 1745
trial2: block 1 7 G 20 0 1623
trial2: 1 8 B 1 1840
trial2: 1 8 B 2 1447
trial2: 1 8 B 3 1397
trial2: 1 8 B 4 1768
trial2: 1 8 B 5 1545
trial2: 1 8 B 6 1323
trial2: 1 8 B 7 1623
trial2: 1 8 B 8 1662
trial2: 1 8 B 9 1430
trial2: 1 8 B 10 1553
trial2: 1 8 B 11 1588
trial2: 1 8 B 12 1820
trial2: 1 8 B 13 1690
trial2: 1 8 B 14 1552
trial2: 1 8 B 15 1687
trial2: 1 8 B 16 1656
trial2: 1 8 B 17 1850
trial2: 1 8 B 18 1774
trial2: 1 8 B 19 1564
trial2: 1 8 B 20 1710
trial2: block 1 8 B 20 0 1629
trial2: sitting 1 done
trial2: prefer 1 b
S7: alive
S7: keyboard ready
trial2: due sitting 2
```

`trials2.py --status` on it prints procedure facts only:

```
boot 1: no trial2 boot line
sitting 1 opened GBBG BGGB
warm-up hits 10 misses 1
sitting 1 done: hits 160 misses 2
preference saved
boot 2: trial2: due sitting 2
```

No ms and no score appears in it. After a `trial2: verdict` line, `--status`
adds `verdict line present` and then prints `--serial`'s report.

## Parsing it cold, in Python

`trials/trials2.py` executes this block as its own definitions, read from
this file at import, so the tool and the document cannot drift. The frozen
`parse_obs_7d` and `mode_word_7d` (TRIALS.md's) are supplied by name.
`checktrials2.py` uses the tool.

```python
import struct

ITEMS = ["ask", "grow", "app", "exit"]                    # trial_target 0-3, as trial one
ROW_ITEMS = ["? ask", "! grow", "Tab app", "Esc exit"]     # the row during a sitting, as trial one
WARMUP = "ask app grow exit app grow ask app ask exit"     # block 0
CUES = [
    "app exit ask grow app grow exit app exit app ask grow exit app ask grow ask exit grow ask",
    "app exit grow app exit ask grow ask grow app ask exit app ask grow exit ask exit app grow",
    "grow ask exit ask exit grow exit grow exit app ask app grow app exit app ask app ask grow",
    "ask exit ask exit ask grow exit grow app ask app grow exit app grow app exit app grow ask",
    "exit grow ask app exit grow app grow ask grow app ask exit grow exit app ask app exit ask",
    "grow ask app exit ask app grow ask exit app grow ask exit app exit grow ask exit grow app",
    "ask exit ask exit app ask grow ask grow app ask grow exit grow app exit app grow app exit",
    "exit ask grow app grow ask exit grow app ask app exit ask app ask exit grow app exit grow",
]
ORDERS = {1: "GBBG BGGB", 0: "BGGB GBBG"}                 # by the sitting's parity
LAYOUT_VALUE = {"A": 0, "B": 1, "G": 2}                   # trial_layout and layout_default
CUES_PER_BLOCK, WARMUP_CUES, BLOCKS, PAIRS_PER_SITTING = 20, 10, 8, 4
SITTINGS_NEEDED, PAIRS_NEEDED = 4, 16
TRIM, MISS_CHARGE_MS = 2, 100                             # dropped at each end; 2000 ms x misses / 20 cues
PAUSE_MS, REST_MS = 500, 5000
MODE_TRIAL, TRIAL_NUMBER = 5, 2
SEPARATOR = ord("|")
NOTE_PREFIX, SERIAL_PREFIX = "trial2 ", "trial2:"
WORD = "trial 2"                                          # the reserved body of the ! line
PREFERENCES = ("g", "b", "n", "skip")
REFUSALS = ["no mouse", "an app is running", "one sitting a boot", "trial 2 concluded",
            "a part is in the pointer's slot"]
RESERVED = "trial is reserved"
QUESTION = "easier? g, b or n"
SAVED = "saved - power off when you like"
OFFER = "trial 2 sitting %d: press Enter to start"
REST_LINES = {0: "warm-up done - rest"}                   # blocks 1-7: "block <b> of 8 - rest"
DUE_LINE = "trial2: due sitting %d"
CONCLUDED_LINE = "trial2: concluded verdict %s default %s"
OBS_8T = {"trial_number": 0x340}
OBS_ZERO_8T = (0x348, 0x360)                              # three words, zero
MODE_WORD_WIDTH = 18


def check_cue_table():
    """Every block row: twenty words, each item five times, none twice running.
    The warm-up: ten words, each item at least twice, none twice running,
    all four items in each half."""
    assert len(CUES) == BLOCKS
    for row in CUES:
        words = row.split()
        assert len(words) == CUES_PER_BLOCK and set(words) <= set(ITEMS), row
        assert all(words.count(w) == CUES_PER_BLOCK // len(ITEMS) for w in ITEMS), row
        assert all(a != b for a, b in zip(words, words[1:])), row
    assert sorted(r.split()[0] for r in CUES) == sorted(ITEMS * 2), "each item opens two blocks"
    words = WARMUP.split()
    assert len(words) == WARMUP_CUES and set(words) <= set(ITEMS)
    assert all(words.count(w) >= 2 for w in ITEMS)
    assert all(a != b for a, b in zip(words, words[1:]))
    half = WARMUP_CUES // 2
    assert set(words[:half]) == set(ITEMS) and set(words[half:]) == set(ITEMS)


def order(sitting):
    return ORDERS[sitting % 2]


def layout(sitting, block, cue=1):
    """The layout of a cue: block b's letter of the order; in the warm-up
    (block 0), the order's first letter for cues 1-5 and the other for 6-10."""
    letters = order(sitting).replace(" ", "")
    if block == 0:
        first = letters[0]
        return first if cue <= WARMUP_CUES // 2 else ("B" if first == "G" else "G")
    return letters[block - 1]


def cue_sequence(block):
    return (WARMUP if block == 0 else CUES[block - 1]).split()


def score(ms, misses):
    """The block score, ms per cue: the middle sixteen of the twenty hit
    times summed and divided by sixteen (integer division), plus 100 a miss."""
    v = sorted(ms)
    mid = v[TRIM:len(v) - TRIM]
    return sum(mid) // len(mid) + MISS_CHARGE_MS * misses


def mean_of(total):
    """S / 16 truncated toward zero - the number the verdict note carries."""
    q = abs(total) // PAIRS_NEEDED
    return q if total >= 0 else -q


def serial_of(note):
    return SERIAL_PREFIX + note[len(NOTE_PREFIX) - 1:]


def note_of_serial(line):
    return NOTE_PREFIX[:-1] + line[len(SERIAL_PREFIX):]


def zones(C, n):
    """B's boxes for n items on C columns: (first, last, filled_first, filled_last)."""
    w = C // n
    out = []
    for i in range(n):
        first = i * w
        last = (i + 1) * w - 1 if i < n - 1 else C - 1
        out.append((first, last, first, last - 1 if i < n - 1 else last))
    return out


def label_col(zone, label):
    first, last, ffirst, flast = zone
    return ffirst + (flast - ffirst + 1 - len(label)) // 2


def grouped_cells(C, labels):
    """The two rows of the choices surface in layout G, as bytes: each label
    at B's column in normal cells, '|' at B's gap column on both rows."""
    row0, row1 = bytearray(b" " * C), bytearray(b" " * C)
    zs = zones(C, len(labels))
    for i, (zone, label) in enumerate(zip(zs, labels)):
        lc = label_col(zone, label)
        for j, ch in enumerate(label):
            row0[lc + j] = ord(ch)
        if i < len(zs) - 1:
            row0[zone[1]] = row1[zone[1]] = SEPARATOR
    return bytes(row0), bytes(row1)


def grouped_targets(C, labels, kinds):
    """(first, last, kind, arg) per zone: B's filled spans, exactly."""
    return [(z[2], z[3], k, a) for z, (k, a) in zip(zones(C, len(labels)), kinds)]


def grouped_columns(C, labels):
    """(the labels' column spans, the separators' columns) - what the twin's rows are checked by."""
    zs = zones(C, len(labels))
    spans = [(label_col(z, l), label_col(z, l) + len(l) - 1) for z, l in zip(zs, labels)]
    return spans, [z[1] for z in zs[:-1]]


def parse_note(text):
    """A trial-two note's fields, or None for any other note."""
    w = text.split(" ")
    if not text.startswith(NOTE_PREFIX) or "" in w:
        return None
    try:
        if w[1] == "sitting" and len(w) == 5 and w[3] + " " + w[4] in ORDERS.values():
            return {"kind": "sitting", "sitting": int(w[2]), "order": w[3] + " " + w[4]}
        if w[1] == "sitting" and len(w) == 4 and w[3] == "done":
            return {"kind": "done", "sitting": int(w[2])}
        if w[1] == "sitting" and len(w) == 5 and w[3] == "aborted":
            return {"kind": "aborted", "sitting": int(w[2]), "block": int(w[4])}
        if w[1] == "block" and len(w) == 8 and w[4] in ("G", "B"):
            return {"kind": "block", "sitting": int(w[2]), "block": int(w[3]), "layout": w[4],
                    "hits": int(w[5]), "misses": int(w[6]), "score": int(w[7])}
        if w[1] == "prefer" and len(w) == 4 and w[3] in PREFERENCES:
            return {"kind": "prefer", "sitting": int(w[2]), "answer": w[3]}
        if w[1] == "verdict" and len(w) == 4 and w[2] in ("G", "B"):
            return {"kind": "verdict", "layout": w[2], "mean": int(w[3])}
        if len(w) == 6 and w[3] in ("G", "B"):
            if w[5] == "miss":
                return {"kind": "miss", "sitting": int(w[1]), "block": int(w[2]), "layout": w[3], "cue": int(w[4])}
            return {"kind": "hit", "sitting": int(w[1]), "block": int(w[2]), "layout": w[3], "cue": int(w[4]),
                    "ms": int(w[5])}
    except ValueError:
        return None
    return None


def notes_of(script):
    """The notes one scripted sitting leaves: script = {"sitting": n, "warmup": {"ms": [10 ints],
    "miss": [cues]}, "blocks": [{"ms": [20 ints], "miss": [cues]}, ...], "abort": None or
    (block, hits_before_esc), "prefer": one of PREFERENCES or None (the machine was powered off
    at the question)}. The warm-up is block 0; an aborted sitting's last played block holds the
    hits made before Esc. The verdict note is the trial's, not the sitting's (journal_of)."""
    n = script["sitting"]
    out = ["trial2 sitting %d %s" % (n, order(n))]
    abort = script.get("abort")
    played = [script["warmup"]] + list(script["blocks"])
    for b, blk in enumerate(played):
        stop = abort[1] if abort and abort[0] == b else None
        count = WARMUP_CUES if b == 0 else CUES_PER_BLOCK
        for c in range(1, (count if stop is None else stop) + 1):
            L = layout(n, b, c)
            if c in blk.get("miss", ()):
                out.append("trial2 %d %d %s %d miss" % (n, b, L, c))
            out.append("trial2 %d %d %s %d %d" % (n, b, L, c, blk["ms"][c - 1]))
        if stop is not None:
            out.append("trial2 sitting %d aborted %d" % (n, b))
            return out
        if b:
            out.append("trial2 block %d %d %s %d %d %d" % (n, b, layout(n, b), CUES_PER_BLOCK,
                                                           len(blk.get("miss", ())), score(blk["ms"], len(blk.get("miss", ())))))
    if abort:                                      # Esc in the rest before block abort[0]
        out.append("trial2 sitting %d aborted %d" % (n, abort[0]))
        return out
    out.append("trial2 sitting %d done" % n)
    if script.get("prefer"):
        out.append("trial2 prefer %d %s" % (n, script["prefer"]))
    return out


def sittings_of(notes):
    """The journal's trial-two notes grouped by sitting, in order."""
    out, cur = [], None
    for text in notes:
        p = parse_note(text)
        if p is None:
            continue
        if p["kind"] == "sitting":
            cur = {"sitting": p["sitting"], "order": p["order"], "blocks": {}, "hits": {}, "misses": {},
                   "end": None, "aborted": None, "prefer": None, "verdict": None}
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
        elif p["kind"] == "prefer":
            cur["prefer"] = p["answer"]
        elif p["kind"] == "verdict":
            cur["verdict"] = (p["layout"], p["mean"])
    return out


def counts(s):
    """(hits, misses) over blocks 1-8, and (hits, misses) of the warm-up: what the panel and --status show."""
    hits = sum(len(v) for b, v in s["hits"].items() if b)
    misses = sum(v for b, v in s["misses"].items() if b)
    return (hits, misses), (len(s["hits"].get(0, [])), s["misses"].get(0, 0))


def check_blocks(notes):
    """Every block note against its own hits: twenty hits, the misses counted, the score
    recomputed by the rule and equal, the layout by the order. Problems, empty when it agrees."""
    problems = []
    for s in sittings_of(notes):
        for b, p in sorted(s["blocks"].items()):
            hits = s["hits"].get(b, [])
            if len(hits) != CUES_PER_BLOCK or p["hits"] != CUES_PER_BLOCK:
                problems.append("sitting %d block %d: %d hit notes, the block note says %d hits" % (s["sitting"], b, len(hits), p["hits"]))
                continue
            if p["misses"] != s["misses"].get(b, 0):
                problems.append("sitting %d block %d: %d miss notes, the block note says %d" % (s["sitting"], b, s["misses"].get(b, 0), p["misses"]))
            if p["score"] != score(hits, p["misses"]):
                problems.append("sitting %d block %d: the score of its hits is %d, the block note says %d" % (s["sitting"], b, score(hits, p["misses"]), p["score"]))
            if p["layout"] != layout(s["sitting"], b):
                problems.append("sitting %d block %d: layout %s, the order gives %s" % (s["sitting"], b, p["layout"], layout(s["sitting"], b)))
    return problems


def table_of(notes):
    """Each sitting's table, as the app panel shows the judged four at the verdict."""
    out = []
    for s in sittings_of(notes):
        rows = ["sitting %d %s" % (s["sitting"], s["order"])]
        for b, p in sorted(s["blocks"].items()):
            rows.append("%d %s %d %d %d" % (b, p["layout"], p["hits"], p["misses"], p["score"]))
        if s["end"] == "done":
            rows.append("done")
        elif s["end"] == "aborted":
            rows.append("aborted %d" % s["aborted"])
        if s["prefer"]:
            rows.append("prefer %s" % s["prefer"])
        out.append((s["sitting"], rows))
    return out


def verdict_detail(notes):
    """(the sittings judged, the sixteen d = score(G) - score(B) in pair order, S, the mean),
    over the first four sittings that ended in done; None before there are four."""
    done = [s for s in sittings_of(notes) if s["end"] == "done"][:SITTINGS_NEEDED]
    if len(done) < SITTINGS_NEEDED:
        return None
    d = []
    for s in done:
        for p in range(PAIRS_PER_SITTING):
            b1, b2 = s["blocks"][2 * p + 1], s["blocks"][2 * p + 2]
            g, b = (b1, b2) if b1["layout"] == "G" else (b2, b1)
            d.append(g["score"] - b["score"])
    total = sum(d)
    return [s["sitting"] for s in done], d, total, mean_of(total)


def verdict_of(notes):
    """R1 on the sign of S: B if S > 0, G if S <= 0 (a tie goes to G)."""
    v = verdict_detail(notes)
    if v is None:
        return None
    return "B" if v[2] > 0 else "G"


def verdict_note(notes):
    v = verdict_detail(notes)
    return None if v is None else "trial2 verdict %s %d" % (verdict_of(notes), v[3])


def verdict_panel(notes):
    """The app panel at the verdict: the four judged sittings' tables, stacked, then the verdict row."""
    v = verdict_detail(notes)
    rows = []
    tables = dict(table_of(notes))
    for n in v[0]:
        rows += tables[n]
    return rows + ["verdict %s %d" % (verdict_of(notes), v[3])]


def journal_of(scripts):
    """The notes a run of scripted sittings leaves. The verdict note follows the fourth
    done sitting's done note at once, before the question is asked, so a machine powered
    off at the question still holds its verdict."""
    out = []
    for script in scripts:
        before = verdict_detail(out)
        notes = notes_of(script)
        out += notes
        if before is None and verdict_detail(out) is not None:
            at = out.index("trial2 sitting %d done" % script["sitting"]) + 1
            out.insert(at, verdict_note(out))
    return out


def sitting_number(notes):
    return sum(1 for t in notes if (parse_note(t) or {}).get("kind") == "sitting") + 1


def concluded(notes):
    return any((parse_note(t) or {}).get("kind") == "verdict" for t in notes)


def in_progress(notes):
    """A trial-two sitting note on the notebook and no trial-two verdict: the offer, and Enter."""
    return sitting_number(notes) > 1 and not concluded(notes)


def default_layout(notes):
    """The last verdict note of either family, in journal order: 0 A, 1 B, 2 G."""
    last = 0
    for t in notes:
        if t in ("trial verdict A", "trial verdict B"):
            last = LAYOUT_VALUE[t[-1]]
        p = parse_note(t)
        if p and p["kind"] == "verdict":
            last = LAYOUT_VALUE[p["layout"]]
    return last


def boot_line(notes):
    """The boot's raw serial line, or None on a notebook with no trial-two note."""
    if not any(t.startswith(NOTE_PREFIX) for t in notes):
        return None
    if in_progress(notes):
        return DUE_LINE % sitting_number(notes)
    v = [parse_note(t) for t in notes if (parse_note(t) or {}).get("kind") == "verdict"][-1]
    return CONCLUDED_LINE % (v["layout"], "ABG"[default_layout(notes)])


def offer(notes):
    return OFFER % sitting_number(notes) if in_progress(notes) else None


def is_reserved(line):
    """A typed line whose first word is 'trial', or 'trial' followed only by digits, is never a note."""
    first = line.split(" ", 1)[0]
    return first == "trial" or (first.startswith("trial") and first[5:].isdigit())


def end_lines(notes, sitting):
    """The conversation panel's lines at a sitting's end, after its last note is journaled,
    ending in the saved line: the question first (for a done sitting), then the counts, then
    the verdict line at the fourth done sitting."""
    s = [x for x in sittings_of(notes) if x["sitting"] == sitting][0]
    (h, m), _ = counts(s)
    if s["end"] == "aborted":
        return ["sitting %d aborted %d" % (sitting, s["aborted"]), "hits %d misses %d" % (h, m), SAVED]
    out = [QUESTION, "sitting %d done" % sitting, "hits %d misses %d" % (h, m)]
    if s["verdict"]:
        out.append("verdict %s %d" % s["verdict"])
    return out + [SAVED]


def status_of(chart):
    """The blind read: the chart's lines in order (strings, as the UART sent them), as
    procedure facts only - no ms and no score. Each boot begins at 'S7: alive'."""
    out, boot, head, cur = [], 0, None, None
    for raw in chart:
        if "S7: alive" in raw:
            boot += 1
            out.append("boot %d: no trial2 boot line" % boot)
            head = len(out) - 1
            continue
        i = raw.find(SERIAL_PREFIX)
        if i < 0:
            continue
        line = raw[i:]
        if line.startswith("trial2: due ") or line.startswith("trial2: concluded "):
            if head is not None:
                out[head] = "boot %d: %s" % (boot, line)
            continue
        p = parse_note(note_of_serial(line))
        if p is None:
            continue
        if p["kind"] == "sitting":
            cur = {"sitting": p["sitting"], "hits": {}, "misses": {}, "pending": None}
            out.append("sitting %d opened %s" % (p["sitting"], p["order"]))
        elif cur is None:
            continue
        elif p["kind"] == "hit":
            cur["hits"].setdefault(p["block"], []).append(0)
        elif p["kind"] == "miss":
            cur["misses"][p["block"]] = cur["misses"].get(p["block"], 0) + 1
        elif p["kind"] in ("done", "aborted"):
            (h, m), (wh, wm) = counts(cur)
            out.append("warm-up hits %d misses %d" % (wh, wm))
            if p["kind"] == "done":
                out.append("sitting %d done: hits %d misses %d" % (p["sitting"], h, m))
                out.append("question not answered")
                cur["pending"] = len(out) - 1
            else:
                out.append("sitting %d aborted %d: hits %d misses %d" % (p["sitting"], p["block"], h, m))
        elif p["kind"] == "prefer" and cur["pending"] is not None:
            out[cur["pending"]] = "preference saved"
            cur["pending"] = None
        elif p["kind"] == "verdict":
            out.append("verdict line present")
    return out


def mode_word_8t(obs):
    if obs["mode"] == MODE_TRIAL and obs["trial_number"] == TRIAL_NUMBER:
        return ("trial2 %s %d/%d" % ("ABG"[obs["trial_layout"]], obs["trial_block"], BLOCKS)).ljust(MODE_WORD_WIDTH)
    return mode_word_7d(obs)


def parse_obs_8t(page):
    obs = parse_obs_7d(page)
    for field, off in OBS_8T.items():
        obs[field], = struct.unpack_from("<Q", page, off)
    return obs
```
