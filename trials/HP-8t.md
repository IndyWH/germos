# HP-8t.md — the HP's days for trial two: four sittings and the verdict boot

**Ring 8t, plan item 14 (the plan's "Test 5"). The owner's document — not
frozen, not a criterion.** It is the procedure Wajira carries out with his
own hands, in `stage8/HP-8a.md`'s shape and to Cowork's design, and what
Cowork reads afterwards.

**His hands do only three things on the HP:** the keys, the mouse and the
power button. Everything else is Cowork's:
- the flash;
- the chart;
- reading the chart after each step with `python3 trials/trials2.py --status trials/out/hp-8t.log`.

No step waits a set time, and no step asks him to report inside a sitting.

The patient is the **HP Compaq Elite 8300 SFF**. Its disk holds GermOS's
table and **355 notes**:
- ring 7c's two notes;
- trial one's three sittings, ending `trial verdict A`;
- ring 8a's molt notes, ending `molt i8042 demoted f0668b687c68cab0 unhealthy`.

Its home store holds the calculator and the demoted `part-i8042`. The stick
carries **seed 2** (`stage8/seed-record.md`): ring 8t's binary, 61,440 bytes,
SHA-256 `c221feca2508f7b6…`, from item 12's commit `93d5f85`.

**What the days prove** (`trials/spec-trial2.md`, test 5): four sittings of
trial two on the HP's own PS/2 mouse, one a boot, and the verdict computed
in the guest at the fourth `done`. Then one more boot shows the machine
drawing its choices row in the verdict's layout. His word on each sitting
and on the verdict closes the ring.

## 0. Before sitting 1 — Cowork's, not the owner's

- **The flash, once for the whole trial:** Cowork's `trials/hp-stick.sh`, which is `stage7/METAL.md` steps 1–3 as one checked script, run once at the repo root on mlrig. It rebuilds the stick and checks the build is the seed in the record. **`BOOTX64.EFI`'s SHA-256 must begin `c221feca2508f7b6`**, seed 2's line; any other hash is not the seed the gate judged. It writes, compares and powers the stick off. Nothing is changed on the stick between sittings.
- **The chart, for the whole trial:** Cowork's `trials/hp-chart.service`, a user service installed once, runs `broker/chart.py` and appends every boot to `trials/out/hp-8t.log`. It is running before the first power-on and until the verdict boot.
- **The Ethernet stays in the home switch.** The boot waits for the link and halts without it. **No broker, no relay, no second address and no firewall rule are needed**: a trial sends nothing over the wire.

## 1. What every boot shows before a sitting

The chart shows ring 8a's pattern:
- the eighteen `S7:` lines, with `S7: notebook <N> notes` and `S7: home 1 apps`;
- then **`S8: sha256 ok` and no other `S8:` line**: the demoted part is never loaded, and no watchdog is armed;
- the seed's own `i8042:` pair, and `S7: keyboard ready`.

There is **no `hold Esc for the seed`** on the screen, because there is no part to load.

The **first** boot reads `S7: notebook 355 notes` and has no `trial2:` line.
From the second boot on, the chart carries one line straight after the
ready line, `trial2: due sitting <N>`. The conversation panel's last line
before the prompt offers **`trial 2 sitting <N>: press Enter to start`**.

Nothing about trial two's times is ever on the screen before the verdict.
The boot's replay does not draw trial two's notes.

## 2. Each sitting — three steps

1. **Power on.** Wait for the prompt.
2. **Start the sitting, click to its end, and answer — all unbroken.**
   - Start it. **Sitting 1:** type `! trial 2` and press Enter. **Sittings 2, 3 and 4:** press Enter at the offer; nothing need be typed.
   - The strip says `trial2 G 0/8` or `trial2 B 0/8`: the warm-up, ten cues, never trial data.
   - Then eight blocks of twenty cues with a five-second rest between them. Each cue is a line `click: <word>`; click that item on the choices row at your normal pace.
   - At the end the panel asks **`easier? g, b or n`** — press `g`, `b` or `n` (n for no difference). Esc skips the question.
   - About seven minutes in all.
3. **Power off when the panel says `saved - power off when you like`.**

**Keys do nothing during a sitting except Esc, which ends it** (below). A
click anywhere but the cued item is a miss, and the cue stays.

After each step Cowork reads the chart with `--status`. It shows only
procedure facts:
- `sitting <n> opened <ORDER>`;
- `warm-up hits … misses …`;
- `sitting <n> done: hits 160 misses <m>`;
- `preference saved`;
- the boot's `trial2:` line.

**It shows no time and no score until the verdict.**

## 3. After sitting 4 — the verdict, then one boot

- **At sitting 4's end**, after the preference key, the conversation panel says `verdict G <mean>` or `verdict B <mean>`. The app panel shows the four sittings' tables and the verdict row. Then comes `saved - power off when you like`: **photograph the app panel**, then power off.
- **One more boot**, with nothing typed. The chart's line after ready is `trial2: concluded verdict <L> default <L>`, and there is no offer. **The choices row at the prompt is drawn in the verdict's layout:**
  - **G** is the items as text with `|` between their zones;
  - **B** is the boxes.

  Photograph it, and power off.

## 4. If something goes other than planned

- **Esc during a sitting** ends it. The panel says `sitting <n> aborted <b>`, then `saved - power off when you like`. Power off. The next boot offers the next sitting number. An aborted sitting is outside the trial, which is **the first four sittings that end in `done`**.
- **Powered off at the question**, before a key: the sitting is `done` and counts, with no preference saved. At sitting 4 the verdict note is already on the disk, since it is written before the question. The panel's tables are then never drawn, but the next boot is the verdict boot, and the chart and `trials2.py --serial` hold the verdict.
- **Adding sittings** needs a dated amendment to `trials/spec-trial2.md` before the next sitting, never after looking at numbers.

## The debugging table — Cowork's

| What the chart or the screen shows | What it means | What to do |
|---|---|---|
| no `trial2: due sitting …` line after sitting 1, and no offer | the sitting's notes did not reach the disk, or the boot read another disk | stop; read the chart's `S7: notebook` line against the last boot's; ask CC |
| an `ERR:` line and a halt after the preference key, and no `saved` line | the disk refused ATA FLUSH CACHE EXT. **Every note of the sitting is already written** | the owner powers off; Cowork reads the chart before the next boot, and the next boot's `S7: notebook` count shows the notes are there |
| `no mouse` at `! trial 2` | the PS/2 mouse did not answer its reset at boot | power off, check the mouse's plug, power on |
| `a part is in the pointer's slot` | a `molt` note left `i8042` in shadow or live | never expected on this disk (the part is demoted); stop and ask CC |
| `one sitting a boot` | a sitting already ended in this boot | power off; the next boot offers the next sitting |
| `trial 2 concluded` | the verdict note is on the disk | the trial is over; only the verdict boot remains |
| an `S8: part …` or `S8: watchdog …` line | a part loaded | stop: the trial runs on the seed's own driver only; ask CC |
| `hold Esc for the seed` on the screen | a part is about to load | touch nothing, let the boot finish, then stop and ask CC |

## What the twin could not prove

- **The HP's disk and FLUSH CACHE EXT.** The twin's AHCI completes the command; the HP's disk and the Q77's controller are proven at sitting 1's `saved`.
- **A human's pace.** The synthetic human's cues took 230–400 ms; the owner's take about 1.6 s, so a sitting is about seven minutes rather than three.
- **The rebuilt history.** The twin's copy of the HP's disk was rebuilt from the charts, and it met every `S7: notebook` checkpoint. Its typed notes are the charts' echoes; the calculator is a stand-in, but it carries the HP's name. The HP's own disk is the real one.
