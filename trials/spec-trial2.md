# Trial two — the choices row, again, with a rule built for the job · pre-registration

**Approved by the owner, 27 September 2026: all twelve decisions as recommended (section 13).** So: G against B; rule R1 on the block score; a miss charge of 2000 ms; 20 cues × 8 blocks × 4 sittings; the warm-up as block 0; the stated preference recorded; times hidden until the verdict; the `trial2 ` family and `! trial 2`; TRIALS.md untouched; ring 8t after ring 8a closes; CC on Opus 5.5 at high effort; a tie to G. From here, a change is a dated amendment at the top, made before the sitting it affects.

Written by Cowork on Opus 5.5 at high effort, in parallel with CC building ring 8a in its own session. Nothing is built, frozen or flashed by this document, and it touches nothing CC works on. It lives in a new folder, `trials/`, because `stage8/` is CC's while ring 8a is open.

**Read for this draft:** CLAUDE.md; ai-os-foundation.md section 5; stage7/spec-7d.md; stage7/TRIALS.md; the ring 7d sections of HANDOVER.md (the rehearsal, the three HP sittings, the closure); the four HP serial logs in `history/`; stage6/GLASS.md's 7d section and stage8/spec.md, for how trial two fits Stage 8.

---

## 1. The question

**Which choices row should this machine show its one human by default: the drawn boxes (B), or a text row with the items properly grouped (G)?**

This is a decision for one person on one machine. It is not a claim for a paper. The rule below is built for that job: a cheap, reversible choice between two harmless layouts.

## 2. Why there is a trial two

Ring 7d closed on 25 September 2026 with verdict A, by its pre-registered rule. That verdict stands and is not reopened. The facts that lead here:

- Over three HP sittings, B's block median was lower in 8 of 12 pairs. The rule needed 10.
- The median per click was A 1613 ms and B 1542 ms.
- Misses were A 4 and B 0. Three of the four were on the narrowest item, `? ask`.
- At the rehearsal the owner found the boxes clearly easier. He also read `Tab` and `app`, and `Esc` and `exit`, as separate items in the text row.

Cowork's review of trial one's rule, accepted by the owner, found it honest, correctly applied, and mistuned in three ways:

1. **Low power.** Nobody computed it before the freeze. The simulation in section 5 puts a number on it: if B's true advantage was the size trial one saw, trial one's rule would have chosen B only **18 times in 100**.
2. **The wrong bar.** A sign test at p ≈ 0.02 is a science-grade bar. It was used for a personal choice between two harmless layouts that the machine can switch back in one boot.
3. **Misses could only veto B, never count for it.** The foundation names two measures, time-to-done and error rate. Trial one used the second only as a brake.

**What trial one's data may and may not do here.** They are used only to estimate spread and effect sizes for planning (section 5). They are not trial two evidence. This document does not report what the new rules would have said about trial one's data, and no rule was chosen for how it would have judged them.

## 3. What is compared — decision 1

**Recommendation: G against B.**

**Layout G, the grouped text row.** The same items as B, in the same places, drawn as plain text:

- Each item gets the same zone as B's box: `w = ⌊C / n⌋` cells, the last zone taking the remainder.
- The label sits where B puts it, centred in its zone on row `R−2`, in normal colours (no bit 7).
- The column where B has its gap holds a `|` on both rows, as a separator.
- The target is B's filled span, exactly. A press on the `|` column is a miss, as a press on B's gap is.

On the twin and the HP (1920x1080, C = 120), the four-item row: labels at columns 12–16, 41–46, 71–77 and 101–108; separators at 29, 59 and 89. That is B's geometry to the column.

So G and B differ in one thing only: whether the box is painted. Target size and position are the same. This separates two questions that trial one mixed together. B's targets were 29–30 columns wide against A's 5–8, so any B advantage in trial one could be Fitts (bigger targets) or the look of a box. Fitts is settled evidence, and the foundation says to build on settled results rather than trial them. The owner's proximity finding is also settled evidence (items that sit apart read as separate things). G takes both settled results as given and asks the one open question: **does the painted box itself help this human?**

**The alternative: A against B again.** Its strengths: trial one's effect size applies directly, so power is easiest to predict (section 5, the moderate row), and no new drawing code is needed. Its weaknesses: A is the layout its own human misreads, so the trial would spend 640 clicks choosing between B and a layout already known to be flawed; and running the same comparison again after a verdict one did not like looks like rolling the dice twice, even with a better rule.

**Rejected in one line:** a compact grouped text row with A-sized targets (items joined, `|` between) would mostly re-test Fitts against B, which is settled. A three-arm trial (A, G and B) would need a new counterbalancing design, a third of the power per comparison, and more guest code, for little gain.

**What either choice does to trial one's verdict.** Trial one's verdict set the default to A. Trial two's verdict, whichever comparison is run, will set a new default. Trial one's record stands exactly as written: under its rule, A stayed. Trial two is a new question, pre-registered before any of its data exist, and its verdict supersedes the default, not trial one's record. With G against B, A leaves the default either way. The owner should see that plainly before approving.

## 4. The measure and the rule

### The measure: one score per block, time and misses together — decision 2

For each block, the **block score** in ms per cue:

1. Take the block's cue-to-hit times (a cue's time already includes any miss before its hit, because the cue stays until the hit).
2. Sort them. Drop the fastest tenth and the slowest tenth (with 20 cues, two at each end). Take the mean of the rest. This is the trimmed mean. It keeps most of the information in the times, unlike a median, and one stray long wait cannot swamp it, unlike a plain mean. (Sitting 1's first cue in trial one waited 196.5 s while the owner reported to Cowork. A trimmed mean drops it; a plain mean would have been ruined by it.)
3. Add a **miss charge** of M ms for each miss in the block, spread over its cues: `score = trimmed mean + M × misses / cues`.

The trimming usually drops the missed cue's slow hit, so the charge is what makes a miss count. That is deliberate: the charge is the price of an error, set in advance, rather than whatever time the miss happened to cost.

**The miss charge — decision 3. Recommendation: M = 2000 ms.** In trial one, a missed cue's hit came 1.2 to 3.1 s later than the block's median. In daily use a miss also acts: a click on the wrong item types the wrong marker, and `Esc exit` closes a running app. So 2 s is a floor for what a miss costs, not a ceiling. With 20 cues, one miss adds 100 ms to the block's score. (Alternatives: M = 0 counts time only, which is trial one's mistake in another form; M = 4000 weighs errors more heavily. Section 5 shows what M = 0 does to power.)

In integer arithmetic, as the guest will compute it: `score = (sum of the middle 16 times) / 16 + 100 × misses`, integer division.

**For each pair** (one G block and one B block, adjacent in one sitting): `d = score(G) − score(B)`. A positive `d` favours B.

### The rule — three candidates

Over the n pairs of the trial:

- **R1 — the point estimate. Recommended.** B becomes the default if the mean of `d` is above zero. Otherwise G. In words: take whichever layout did better overall, time and misses together.
- **R2 — Bayesian, threshold 0.8.** B becomes the default if the posterior probability that B's true score is lower is at least 0.8 (a normal model for `d` with a flat prior, which works out as `t ≥ 0.866` with 16 pairs). Otherwise G.
- **R3 — the sign test, re-tuned.** Count the pairs where B's score is lower. B becomes the default if that count reaches the smallest k whose one-sided p is at most 0.20 (8 of 12; 11 of 16). Otherwise G.

**Why R1.** The choice is cheap, harmless and reversible, and neither layout is today's default (A is). When the two options cost the same to adopt and the same to undo, the choice that loses least on average is simply the one that looked better. A higher bar (R2, R3) lowers the chance of switching to B when there is truly no difference. But when there is truly no difference, nothing is lost whichever layout is picked. The higher bar only helps when one option has a switching cost, and here neither does. What a higher bar does cost is missing a real small difference (section 5: with the recommended size, R1 finds a small B advantage 88 times in 100, R2 63, R3 38). R1 is also the simplest to compute in the guest (one signed sum) and the simplest to check by hand.

**R1's honest weak spot:** when the layouts are truly equal, it picks B half the time. That is not an error for this question, because either default is then as good. The verdict note carries the size of the difference (section 8), so a near-tie is visible on the record as a near-tie.

**A tie** (the mean of `d` exactly zero, integer ms) goes to G, the smaller change from a text row. Decision 12.

**Nothing else is looked at before the verdict.** The per-sitting times are not shown (section 7).

## 5. Power, checked before anything is frozen

The simulation below resamples trial one's HP clicks. It takes the spread of cue-to-hit times within a block (log sd 0.281), the extra spread between blocks (log sd 0.064), B's typical time (1605 ms), and the extra time trial one's missed cues took (1156, 1540, 1822 and 3085 ms). It then plays 4,000 whole trials per line under four scenarios, applies all three rules to each, and counts how often each rule picks B. The column T1 is trial one's own rule (B wins at least ten twelfths of the pairs on medians, misses not worse), for reference.

The scenarios, in how much slower the other layout is than B, per cue:

- **null:** no difference; both layouts miss 1.7 times in 100 (trial one's pooled rate).
- **small:** 40 ms, and B misses 1 in 100 against 2 in 100.
- **moderate:** 90 ms, and B misses 0.4 in 100 against 3.3 in 100 — about the size trial one saw between A and B.
- **reversed small:** the other layout is better, by the small scenario's amounts.

Chance of the verdict being B, with M = 2000 ms, 8 blocks a sitting:

| Cues a block × sittings | Scenario | R1 | R2 | R3 | T1 |
|---|---|---|---|---|---|
| 10 × 3 (trial one's size) | null | 0.50 | 0.21 | 0.19 | 0.02 |
| | small | 0.79 | 0.48 | 0.42 | 0.05 |
| | moderate | 0.97 | 0.86 | 0.75 | **0.18** |
| | reversed small | 0.22 | 0.05 | 0.06 | 0.00 |
| 20 × 3 | null | 0.50 | 0.21 | 0.19 | 0.01 |
| | small | 0.85 | 0.57 | 0.49 | 0.06 |
| | moderate | 0.99 | 0.95 | 0.88 | 0.25 |
| | reversed small | 0.16 | 0.03 | 0.05 | 0.00 |
| **20 × 4 (recommended)** | null | 0.49 | 0.19 | 0.10 | 0.01 |
| | small | **0.88** | 0.63 | 0.38 | 0.05 |
| | moderate | **1.00** | 0.98 | 0.86 | 0.25 |
| | reversed small | **0.11** | 0.02 | 0.01 | 0.00 |
| 30 × 4 | null | 0.50 | 0.19 | 0.10 | 0.01 |
| | small | 0.91 | 0.67 | 0.42 | 0.06 |
| | moderate | 1.00 | 0.99 | 0.91 | 0.30 |
| | reversed small | 0.09 | 0.02 | 0.01 | 0.00 |
| 20 × 6 | null | 0.51 | 0.20 | 0.16 | 0.00 |
| | small | 0.93 | 0.73 | 0.56 | 0.01 |
| | moderate | 1.00 | 1.00 | 0.97 | 0.12 |
| | reversed small | 0.07 | 0.01 | 0.01 | 0.00 |

**How to read it.** In the small and moderate rows, a high number is good: B is truly better and the rule finds it. In the reversed row, a low number is good: B is truly worse and the rule avoids it. In the null row, nothing is at stake. So at the recommended size, R1 picks the better layout 88 or 89 times in 100 for a small real difference, and every time for a difference the size of trial one's.

**Three things the table shows.**

1. Trial one's rule would have found an advantage of its own observed size only 18 times in 100. That is the power problem, put as a number.
2. Doubling the cues per block does more than a whole extra sitting of ten-cue blocks. Most of the noise is click-to-click, not block-to-block, so more clicks help wherever they go.
3. R3 gets worse from 12 to 16 pairs for the small effect, because the sign test's bar jumps from 8 of 12 (p 0.19) to 11 of 16 (p 0.11). A count bar is coarse; R1 is not.

**Counting misses matters.** The same simulation with M = 0 at the recommended size: R1 finds the small effect 84 times in 100 instead of 88, and R3 31 instead of 38.

**What G against B is likely to look like.** G and B share their targets, so the plausible difference between them is smaller than trial one's A against B: the small or null rows, not the moderate one. At the recommended size, R1 still picks the better one about 88 times in 100 when a small difference exists. When there is none, the record will show a near-zero difference, which is itself the answer: the paint does not matter for this human.

**The model's limits, said once.** Clicks are drawn independently from trial one's pooled spread; the layout effect is added as a fixed time per cue; the scenarios' miss rates are guesses anchored on trial one's 4 of 240. The G-against-B effect sizes are borrowed, because no G data exist. The numbers guide the size of the trial; they are not a promise.

**The code** is in the appendix, stdlib Python only, fixed seed. From the repo root it reruns in about a minute:

```
sed -n /^#SIM-BEGIN/,/^#SIM-END/p trials/spec-trial2.md > /tmp/sim2.py && python3 /tmp/sim2.py
```

## 6. The size of a sitting — decision 4

**Recommendation: 20 cues a block, 8 blocks a sitting, 4 sittings. 16 pairs, 640 scored cues.**

- **Blocks and order:** as trial one — odd sittings `GBBG BGGB`, even sittings `BGGB GBBG`. Four sittings give every block number both layouts exactly twice, so the fixed cue table is balanced across layouts. Three sittings cannot do that.
- **The cue table:** eight rows of 20 words, fixed by block number; each word five times a block; none twice running. Written into the trial document at the plan and frozen with it.
- **Timing:** a click takes about 1.6 s, plus the 500 ms pause. So 160 scored cues are about 5.6 minutes. Rests of 5 s between blocks (trial one used 2 s; 20-cue blocks earn a longer breath), plus the warm-up: **about 7 minutes a sitting.** Trial one's sittings were about 3.5 minutes.
- **The upper limit for fatigue:** 240 cues or 10 minutes of clicking a sitting, whichever comes first. Pointing speed starts to drift with tiredness and boredom well before a quarter of an hour of repetitive clicking. The 30 × 4 design sits at that limit and buys 3 more points of power for the small effect (0.91 against 0.88); not worth it.
- **Sittings:** one a boot, as trial one. Any spacing. At most two a day is a sensible habit, not a rule.
- **No early stopping and no extra sittings.** The trial is the first four sittings that end in `done`. Aborted sittings are outside the rule, as in trial one. Adding sittings needs an amendment to this document before the next sitting, never after looking at numbers.

## 7. What the owner sees during the trial — decision 7

**Recommendation: the times stay hidden until the verdict.** At a sitting's end the panel shows `sitting 2 done` and the counts (`hits 160 misses 1`), not the block scores. Trial one showed the medians after every sitting. With an unblinded human who already has a stated preference, seeing a running score invites trying harder on one layout, or easing off. The serial chart still carries every raw line, because it is the case-report form; the owner does not read it during the trial, and Cowork does not tally it. At the verdict, the panel shows all four sittings' tables and the verdict line.

## 8. The warm-up and the stated preference

### The warm-up — decision 5

**Recommendation: yes, 10 cues at the start of every sitting, never trial data.** Trial one's first cue after each rest was slow (median 2463 ms against 1529 for the rest), and its first block was the slowest of the sitting. A warm-up absorbs the settling-in. It is **block 0**: five cues in G then five in B on odd sittings, the reverse on even ones. Its notes carry block number 0, and the rule reads blocks 1 to 8 only. That is decided here, before any data. It runs on the HP like everything else. There is no separate practice mode: an aborted sitting simply falls outside the rule, so a snag on the first sitting costs a sitting number, nothing more.

### The stated preference — decision 6

**Recommendation: record it, worth a little.** After each sitting's last cue, before anything else is shown, the panel asks `easier? g, b or n` (n for no difference). One key answers; Esc skips. The answer is journaled and reported beside the verdict. It is not part of the rule.

What it is worth: the trial cannot be blinded, and the owner stated a preference (boxes easier) before trial two began, so the answer carries his prior. Its value is for later. If, over trials, what he says feels easier matches what he measures, future trials could be shorter; if it does not, that is worth knowing for a human-factors desktop too. It costs one key press a sitting. It must be asked before any numbers, which is also why the times stay hidden (section 7).

## 9. How trial two enters the machine — decisions 8 to 11

### Numbering and the notebook — decision 8

**Recommendation: a second family of notes, `trial2 `, beside trial one's `trial `.**

- **Trial one stays exactly as it is.** Its notes, its word `! trial` and its answer `trial concluded` on the HP are unchanged. The frozen `stage7/trials.py` reads only notes beginning `trial ` (with the space), so it will still print trial one's three tables and verdict A from the HP's disk after trial two, byte for byte. That becomes an acceptance test.
- **The word:** `! trial 2` opens a trial-two sitting, a reserved body judged before the home lookup and the broker, as `! trial` is. Keeping `! trial` as trial one's word keeps the 7d gate green on the new binary, which Stage 8 requires.
- **Its refusals**, in this order: `no mouse`; `an app is running`; `one sitting a boot` (shared by both trials); `trial 2 concluded`; and one new one, `a part is in the pointer's slot`, when Stage 8's `i8042` slot holds a part in shadow or live (decision 10).
- **The notes** (formats exact at the plan):

```
trial2 sitting 1 GBBG BGGB
trial2 1 0 G 3 1488          warm-up: block 0, never in the rule
trial2 1 2 B 7 1502          sitting, block, layout, cue, ms - a hit
trial2 1 2 B 8 miss
trial2 block 1 2 B 20 1 1561 sitting, block, layout, hits, misses, score
trial2 sitting 1 done
trial2 prefer 1 b
trial2 verdict B 57          the layout, and the mean of d in ms per cue (signed)
```

- **The reserved prefix widens.** A typed line whose first word is `trial` or `trial` followed only by digits (`trial2`, `trial3`) is refused, `trial is reserved`. This supersedes TRIALS.md's six-byte rule and covers any later trial.
- **The default:** at boot, the **last verdict note of either family**, in journal order, sets `layout_default`. It gains a third value: 0 A, 1 B, 2 G. On the HP that means trial two's verdict replaces trial one's A as the default, and — unlike trial one — the prompt row will show it, because both G and B look different from A.
- **The obs page:** trial two reuses trial one's cue fields at `0x2E0` onward with the same meanings, so the synthetic human needs no new eyes. It needs one more word, `trial_number`. Its offset is set at trial two's plan from whatever ring 8a leaves free (the four reserved words at `0x340`–`0x358`, if still zero). The mode word is `trial2 G 3/8`.
- **Capacity:** a trial-two sitting writes about 185 notes; four sittings about 750. The notebook holds 32,767. Every journal walk at boot grows with it; CC measures the boot time with a full trial on the disk.

### What supersedes what, and what is frozen — decision 9

**Recommendation:**

- **`stage7/TRIALS.md`: untouched.** No freeze opening. It stays trial one's frozen text. Trial two's document states the few sentences of it that it supersedes (the reserved prefix, the default read at boot, the values of `layout_default`) and supersedes nothing else.
- **`stage6/GLASS.md`: a new section, by the owner's hand** (`cat >>`), as for rings 6c and 7d: layout G, the third value of `layout_default`, `! trial 2`, the widened reserved prefix, the mode word, the new obs word.
- **Frozen at the plan's freeze item, after a probe run supplies every number** (the rule learned twice in Stage 6 and 7: write expectations from a run, never from arithmetic): `trials/TRIALS2.md` (the document, with its Python block, as TRIALS.md), `trials/trials2.py` (the host tool), `trials/checktrials2.py` (the checker), `trials/test-trial2.sh` (the gate). The guest code lives in `stage8/stage8.asm`, unfrozen.
- **`trials/`** becomes the machine's trial register: this pre-registration, trial two's frozen files, and any later trial's. `trials/out/` joins `.gitignore` at the plan's item 0.
- **This spec** is frozen by approval, as every spec is: changes after approval are dated amendments at the top, made before the sitting they affect.

### Where trial two sits in the ladder — decision 10

**Recommendation: ring 8t ("t" for trial), after ring 8a closes and before ring 8b's kickoff.**

- **Why there.** Ring 8b grows a part for the `i8042` slot, which is the mouse's driver, and runs it in shadow and then live on the HP. Trial two measures pointing through that driver. Running the trial on the generic driver throughout, before any grown part touches the pointer, keeps one thing changing at a time. The guest enforces it: `! trial 2` refuses while a part is in that slot (the refusal above). As ring 8a's test 5 is written, its oracle ends with `hang` demoted and the HP's slot back on the seed's driver, so the trial can start then. If 8a ends otherwise, `! molt undo` or the recovery rules clear the slot first.
- **Why not later.** After 8b the pointer's path is a grown part, and the trial would measure the part as much as the layout.
- **Why "8t" and not a renumbering.** The approved Stage 8 spec names 8b to 8g; a letter out of sequence leaves all of them as written. One line under the Stage 8 spec's ring table records the insertion, by the owner's hand at trial two's kickoff (not now: `stage8/` is CC's while 8a is open).
- **The Stage 8 synergy it gives up:** trial sittings make thousands of mouse packets, which ring 8b's shadow threshold needs (5,000). Counting them would mean running the trial with a part in shadow. Recommended against: the shadow part's answers are not used, but it runs on every byte, and the principle is worth more than the saved clicks.

### CC's model and effort — decision 11

**Recommendation: Opus 5.5 at high effort,** the owner's model plan for every ring from 8a on. Ring 7d on Fable 5.1 medium had four pre-oracle defects in the guest; trial two changes the same code. The effort is the owner's call at the kickoff, recorded at item 0.

## 10. Where the sittings run

- **Every human sitting runs on the HP Compaq Elite 8300 with its PS/2 mouse**, by `stage7/METAL.md`'s day: one flash of trial two's stick, then boots only; the chart (`broker/chart.py`) logging each boot to a file; no broker needed.
- **No human sitting in QEMU, not even a rehearsal.** The warm-up (block 0) is the only practice, on the HP, and it is not trial data.
- **The twin is CC's automated gate only**, with its synthetic human driving the mouse through the monitor, mock only, no token spent.
- **Ring 7d's procedure finding holds:** no step asks the owner to stop and report inside a sitting. He types `! trial 2`, runs the sitting to its end, answers the preference key, then reports.

## 11. The acceptance tests, in outline

Tests 1–4 written before the code, frozen at the plan's freeze item, mock only. The 7d gate, the 8a gate and the Stage 7 gates stay the regressions on the same binary.

1. **The documents.** `trials/TRIALS2.md` parsed cold: the cue table's constraints, the formats, the score and the rule; `trials2.py` reproduces the document's worked examples byte for byte, including a tie going to G.
2. **The rows.** Layout G's row on the twin at 1920x1080 to the pixel (labels and separators at the columns in section 3); B's as 7d's; the refusals of `! trial 2`, the part-in-slot one included.
3. **Sittings predicted.** The synthetic human plays a sitting with scripted times and misses: the warm-up's block-0 notes, twenty-cue blocks, the scores exactly as the rule computes them, the preference key journaled, the times hidden on the panel; an abort; then four sittings to a scripted verdict B and, on a second disk, to a scripted verdict G; the default read at boot (1 and 2) and the prompt row drawn in it.
4. **Nothing earlier disturbed.** The payload table with the four new frozen paths; the argv checks; the frozen `stage7/trials.py` on a disk holding both families prints trial one's tables and verdict A unchanged; the 7d gate green on the binary (`! trial` is still trial one); the 8a gate green.
5. **The owner's, on the HP.** Four sittings, one a boot; the verdict at the fourth `done`; the next boot shows the verdict's row at the prompt. His word on each sitting and on the verdict closes the ring.

## 12. Threats, said once

- **Designed after a result.** Trial two exists because trial one leaned towards B. The mitigations: every rule and number here is fixed before any trial-two data exist; trial one's data are not reused as evidence; the recommended comparison is a new one (G, not A); and the rule was not chosen for how it would judge trial one.
- **No blinding, and a stated prior.** The human sees the layout and has said which he finds easier. The rule on scores decides, not the preference; the times are hidden until the verdict.
- **Learning.** Speed improved across trial one's sittings (a median of 1715 ms in sitting 1's A blocks, 1464 in sitting 3's). The GBBG/BGGB order puts both layouts at every stage of learning equally.
- **The miss charge is a value judgment.** 2000 ms is argued above; the owner may set another before approval.
- **The clock** is the TSC calibrated once against the PIT: good to a few parts in a thousand, far inside any difference worth acting on.
- **One human, one machine.** That is the point, not a flaw: the result is this machine's default for this person.

## 13. Decisions for the owner

1. **What is compared.** Recommend **G against B** (section 3). Alternative: A against B again.
2. **The rule.** Recommend **R1, the point estimate on the block score**. Alternatives: R2 (posterior ≥ 0.8) or R3 (sign test, p ≤ 0.20).
3. **The miss charge.** Recommend **M = 2000 ms**.
4. **The size.** Recommend **20 cues × 8 blocks × 4 sittings**, 5 s rests; limit 240 cues or 10 minutes a sitting.
5. **The warm-up.** Recommend **yes**: 10 cues, block 0, never in the rule.
6. **The stated preference.** Recommend **record it** after each sitting, before any numbers; not in the rule.
7. **Times hidden until the verdict.** Recommend **yes**.
8. **Numbering and journaling.** Recommend the **`trial2 ` family**, `! trial 2`, the widened reserved prefix, the last verdict of either family as the default, `layout_default` 2 for G.
9. **Supersession and freezing.** Recommend **TRIALS.md untouched**; four new frozen files under `trials/`; a GLASS.md section by your hand.
10. **The ladder.** Recommend **ring 8t, after 8a closes, before 8b**, with the guest refusing while a part is in the `i8042` slot; one line under the Stage 8 spec's ring table by your hand at the kickoff.
11. **CC's model and effort.** Recommend **Opus 5.5 at high effort**.
12. **A tie.** Recommend **G** (the smaller change from a text row).

---

## Appendix — the simulation

Stdlib Python, fixed seed, reads trial one's three HP charts from `history/`. Run from the repo root with the command in section 5. It printed the table in section 5 on 27 September 2026 (about 70 seconds). Set `M_MISS = 0` to reproduce the M = 0 figures.

```python
#SIM-BEGIN
# Trial two power check. Stdlib only. Run from the repo root (see section 5).
# Trial one's HP data are used ONLY to estimate spread and effect sizes for planning.
import glob, math, random, statistics as st

LOGS = sorted(glob.glob("history/2026-09-24-ring7d-hp-sitting[123]-serial.log"))
REPS, SEED = 4000, 20260927
M_MISS = 2000          # ms charged per miss in the block score (decision 3)
DELTA_R1 = 0           # R1's minimum difference, ms per cue
POST_R2 = 0.80         # R2's posterior threshold
P_R3 = 0.20            # R3's one-sided sign-test bar
PROCEDURE_MS = 20000   # a hit slower than this is a procedure event, kept out of the spread

# 1. Trial one's hits, by block
hits, misses = {}, {}
for path in LOGS:
    for line in open(path, errors="replace"):
        w = line.split()
        if len(w) != 7 or w[1] != "trial:" or w[2] in ("sitting", "block", "verdict"):
            continue
        key = (int(w[2]), int(w[3]), w[4])
        if w[6] == "miss":
            misses[key] = misses.get(key, 0) + 1
        else:
            hits.setdefault(key, []).append(int(w[6]))
assert len(hits) == 24 and sum(map(len, hits.values())) == 240, "expected 24 blocks of 10 hits"

# 2. The spread: log residuals within blocks, and the extra spread between blocks
resid, means = [], {"A": [], "B": []}
for key, v in hits.items():
    lv = [math.log(x) for x in v if x < PROCEDURE_MS]
    m = st.mean(lv)
    resid += [x - m for x in lv]
    means[key[2]].append(m)
within = st.variance(resid) * len(resid) / (len(resid) - len(hits))
between = max(0.0, st.mean([st.variance(means["A"]), st.variance(means["B"])]) - within / 10)
SD_BLOCK = math.sqrt(between)
BASE = math.exp(st.mean(means["B"]))           # B's typical cue-to-hit, ms
EXTRA = []                                       # what a miss added to its cue's hit, ms
for key, n in misses.items():
    med = st.median(hits[key])
    EXTRA.append(max(hits[key]) - med)           # the slowest hit of the block is the missed cue's
print("trial one, for planning: B typical %d ms, within-block log sd %.3f, between-block log sd %.3f"
      % (BASE, math.sqrt(within), SD_BLOCK))
print("misses A %d of 120, B %d of 120; extra time on a missed cue %s ms"
      % (sum(n for k, n in misses.items() if k[2] == "A"), sum(n for k, n in misses.items() if k[2] == "B"),
         sorted(round(x) for x in EXTRA)))

# 3. The rules
def t_cdf(t, df):
    f = lambda x: (1 + x * x / df) ** (-(df + 1) / 2)
    c = math.gamma((df + 1) / 2) / (math.sqrt(df * math.pi) * math.gamma(df / 2))
    n = 2000
    h = t / n
    s = f(0) + f(t) + sum((4 if i % 2 else 2) * f(i * h) for i in range(1, n))
    return 0.5 + c * s * h / 3

def sign_k(n, p=P_R3):
    for k in range(n + 1):
        if sum(math.comb(n, j) for j in range(k, n + 1)) / 2 ** n <= p:
            return k

def t_crit(df, q=POST_R2):
    lo, hi = 0.0, 5.0
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_cdf(mid, df) < q else (lo, mid)
    return hi

def composite(times, nmiss):
    k = len(times)
    trim = k // 10
    v = sorted(times)[trim:k - trim]
    return st.mean(v) + M_MISS * nmiss / k

def rules(d, wins, n):
    mean = st.mean(d)
    sd = st.stdev(d)
    t = mean / (sd / math.sqrt(n)) if sd > 0 else math.copysign(99, mean)
    return {"R1": mean > DELTA_R1, "R2": t >= TCRIT[n], "R3": wins >= SIGNK[n]}

# 4. One simulated block and one simulated trial
def block(rng, cues, slow_ms, p_miss):
    u = rng.gauss(0, SD_BLOCK)
    times, nmiss = [], 0
    for _ in range(cues):
        t = BASE * math.exp(u + rng.choice(resid)) + slow_ms
        if rng.random() < p_miss:
            nmiss += 1
            t += rng.choice(EXTRA)
        times.append(t)
    return times, nmiss

def trial(rng, cues, pairs, sc):
    d, wins, old_w, old_ma, old_mb = [], 0, 0, 0, 0
    for _ in range(pairs):
        tb, mb = block(rng, cues, 0, sc["pB"])
        tc, mc = block(rng, cues, sc["delta"], sc["pC"])
        sb, sc_ = composite(tb, mb), composite(tc, mc)
        d.append(sc_ - sb)
        wins += sb < sc_
        old_w += st.median(tb) < st.median(tc)       # trial one's rule, for reference
        old_ma += mc
        old_mb += mb
    out = rules(d, wins, pairs)
    out["T1"] = old_w >= round(pairs * 10 / 12) and old_mb <= old_ma
    return out

SCENARIOS = [  # delta: how much slower the other layout is than B, ms per cue; pB, pC: miss rates
    ("null: no difference",          {"delta": 0,   "pB": 0.017, "pC": 0.017}),
    ("small: B 40 ms and 1 miss in 100 better", {"delta": 40,  "pB": 0.010, "pC": 0.020}),
    ("moderate: trial one's size",   {"delta": 90,  "pB": 0.004, "pC": 0.033}),
    ("reversed small: other better", {"delta": -40, "pB": 0.020, "pC": 0.010}),
]
DESIGNS = [(10, 3), (20, 3), (20, 4), (30, 4), (20, 6)]   # (cues a block, sittings); 8 blocks = 4 pairs a sitting
TCRIT = {4 * s: t_crit(4 * s - 1) for _, s in DESIGNS}
SIGNK = {4 * s: sign_k(4 * s) for _, s in DESIGNS}
print("R2 needs t >= %s; R3 needs wins >= %s" % ({n: round(c, 3) for n, c in TCRIT.items()}, SIGNK))

rng = random.Random(SEED)
print("\nP(verdict B) in %d simulated trials each. T1 = trial one's rule, for reference." % REPS)
print("%-9s %-40s %6s %6s %6s %6s" % ("design", "scenario", "R1", "R2", "R3", "T1"))
for cues, sittings in DESIGNS:
    pairs = 4 * sittings
    for name, sc in SCENARIOS:
        tally = {"R1": 0, "R2": 0, "R3": 0, "T1": 0}
        for _ in range(REPS):
            for r, b in trial(rng, cues, pairs, sc).items():
                tally[r] += b
        print("%2dx8x%d   %-40s %6.2f %6.2f %6.2f %6.2f" % (cues, sittings, name,
              *(tally[r] / REPS for r in ("R1", "R2", "R3", "T1"))))
#SIM-END
```

Its first three lines of output, the planning estimates from trial one:

```
trial one, for planning: B typical 1605 ms, within-block log sd 0.281, between-block log sd 0.064
misses A 4 of 120, B 0 of 120; extra time on a missed cue [1156, 1540, 1822, 3085] ms
R2 needs t >= {12: 0.876, 16: 0.866, 24: 0.858}; R3 needs wins >= {12: 8, 16: 11, 24: 15}
```
