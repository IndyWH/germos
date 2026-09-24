# Stage 7 ring 7d — the trials · spec

**Approved by the owner, 22 September 2026.** Decisions 1–3 as recommended (the choices row, text against drawn boxes; ten cues a block, `ABBA BAAB` / `BAAB ABBA`, three sittings, the ten-of-twelve sign-test rule with misses not worse; the cue is the label word only). Decision 4: the verdict lives on the notebook, read at boot, so it holds with the broker off. Decisions 5–7 as recommended: sitting 1 in the windowed twin, sittings 2–3 on the HP; the model and the effort for CC decided at the kickoff and recorded at item 0; the GLASS.md section by the owner's hand. Written in a fresh Cowork session on Omarchy (mlrig, dual boot on the Crucial P2), after the regression of every stage on the new machine: the Stage 0 gate, the 7c gate and the payload table green on the item 21 binary, 40,960 bytes (commit `ebf5794`, the sixth freeze opening: twin.py's xp parser against QEMU 11's eight-digit addresses).

**Amended by the owner, 24 September 2026, before the first sitting — decision 5:** the trial is **three sittings on the HP's notebook**; the windowed twin's sitting is the protocol rehearsal and is not trial data. The sitting number counts from each disk's own notebook, so a twin sitting plus two HP sittings would leave no notebook with three: no verdict in the guest, no default following it, and the HP's first sitting repeating `ABBA BAAB`. Decided before any data existed; the rehearsal ran the same day. Test 5 below reads accordingly.

**The policy gate, re-checked 22 September 2026:** the help centre article "Use the Claude Agent SDK with your Claude plan" still carries its 15 June note — the change is paused, "nothing has changed: Claude Agent SDK, `claude -p`, and third-party app usage still draw from your subscription's usage limits." The CLI on Omarchy is logged in through claude.ai, first-party, no API key in the environment. The broker keeps shelling out to `claude -p`. Re-check at the next stage gate.

**Why this ring and not Stage 8:** the Stage 7 spec, approved 9 September, says "the N-of-1 trials ring comes after the metal"; HANDOVER's "Next action" of 18 September says the same. The owner confirmed the order on 22 September 2026: the trials first, the molt after. The foundation's stage list is unchanged; this is the last ring of Stage 7's order, numbered 7d so the record reads in sequence. (Sound and the full screen, raised on 15 September, stay on the list for a later gate.)

## The owner's ask, in his words

From the Stage 6 spec (1 September): "the N-of-1 trials the owner wants — layout A against B, measured in speed and errors — are pointing tasks." From the foundation (§5): "the DE may run N-of-1 trials — layout A against layout B, measured in speed and errors for this specific human — and fit the interface to its person the way the kernel fits the silicon." And the metric rule: "the DE optimises time-to-done and error rate, never engagement."

## Goal

GermOS runs a trial on its own human. Two layouts of the same control, a pre-registered crossover design, the machine as the timer and the case-report form, the analysis frozen before the first click. **Done when:** three sittings are on the notebook, the frozen analysis gives its verdict, and the DE's default follows the verdict. **Proves the interface is evidence-based, not asserted.**

## What is trialled

The **choices row** — the one control on an edge, the one the pointer clicks, the one Hick and Fitts both speak to. Since ring 6c it is text: items on row R−2 separated by three spaces, row R−1 a blank click margin. That is **layout A**, exactly as it is today, to the pixel.

**Layout B** draws the same items as **targets**: the two bottom rows split into equal boxes, one per item, each box ⌊C / n⌋ cells wide (the last box takes the remainder), filled in the strip's inverse colours, the label centred on row R−2, a one-cell gap between boxes. A click anywhere inside a box is that item. Nothing else on the screen moves: the strip, the panels and the conversation are unchanged in both layouts.

Fitts says a bigger target closer to the edge is hit faster and missed less. Layout B makes the targets bigger and keeps them on the edge. Whether that holds for this human on this machine is the question the trial answers; the spec does not presume it.

## The task

A **cue** names one item of the row; the human clicks it. The row shows the four items of GLASS.md's state-3 row, `? ask   ! grow   Tab app   Esc exit`, in both layouts, so the trial measures pointing at a row the human already knows, with no new words.

- The cue is one line in the conversation panel: `click: grow` (the label word only). The glass core stamps the end of the frame that painted it — the cue stamp, the same rule as input-to-photon.
- A click on the cued item is a **hit**: the time from the cue stamp to the click's interrupt stamp is the cue-to-hit time, in ticks, converted with `tsc_per_ms`. The next cue follows after a fixed pause of 500 ms with the row unchanged.
- A click anywhere else, including another item, is a **miss**: counted, the cue stays.
- In trial mode a click on the row does **not** do what its key does. Keys are ignored, counted in `keys` as ever, except Esc, which aborts the sitting: the current block is discarded, the completed blocks stand.

The mode word on the strip says `trial A 3/8` (the layout, the block, of how many) — the trial is a visible mode, never a hidden one (the constitution).

## The design

An N-of-1 crossover, pre-registered here, deterministic so the twin can check it:

- A **block** is ten cues on one layout. The cue sequence within a block is fixed by block number from a table in TRIALS.md (each item at least twice per block, no item cued twice running).
- A **sitting** is eight blocks, four pairs, counterbalanced: odd sittings `ABBA BAAB`, even sittings `BAAB ABBA`. Blocks are separated by a two-second pause with the row blank and the panel saying `block 4 of 8 - rest`.
- The **trial** is three sittings, on three separate days or at least separate boots, one sitting per sitting (the owner's rule). Sitting number = the number of `trial sitting` lines already on the notebook, plus one.
- **The measure:** per block, the median cue-to-hit in ms and the miss count. Per pair, the A block's median minus the B block's.
- **The pre-registered rule:** over the twelve pairs, B becomes the default if its median is lower in at least ten pairs (a sign test at p ≈ 0.02) and its total misses are not greater than A's; otherwise A stays. Nothing else is looked at before the verdict.

## What is recorded, and where

The notebook is the case-report form. Every event is one note, prefixed `trial `, journaled as any note (NOTEBOOK.md's format, unchanged, so `S7: notebook N notes` counts them and the boot replay shows them — the machine shows what it remembers):

```
trial sitting 1 ABBA BAAB
trial 1 1 A 3 412          (sitting, block, layout, cue index, ms - a hit)
trial 1 1 A 4 miss
trial block 1 1 A 10 1 431 (sitting, block, layout, hits, misses, median ms)
trial sitting 1 done
trial sitting 1 aborted 5  (the block that was discarded)
```

The same lines go to serial, raw UART after `keyboard ready` (the tee gotcha), prefixed `trial:` — so the chart on the HP carries the sitting without a flash to read the disk.

At `trial sitting N done` the app panel shows the sitting's table: eight rows, block, layout, hits, misses, median. After the third sitting the panel shows the verdict, computed in the guest by the same rule TRIALS.md states, and the strip's mode word returns to `prompt`. The host tool `stage7/trials.py` reads the notes partition of a disk image (checknotes.py's parser) and prints the same table and the same verdict; on the HP the same numbers are on the chart and on the screen.

**The obs page, from `0x2C0`** (a new GLASS.md section, by the owner's hand, superseding "the rest of the page is zero" to hold from `0x340`): `trial_sitting`, `trial_block`, `trial_layout` (0 A, 1 B), `trial_cue` (index within the block), `trial_target` (the item cued), `cue_stamp`, `cue_pending`, `trial_hits`, `trial_misses`, `hit_last` (ticks), `hit_worst`, `layout_default` (0 A, 1 B — what the row shows outside a trial), and four words reserved. `mode` gains the value 5, `trial`.

## How the ring enters

`! trial` at the prompt is a reserved word the guest answers itself, before the home lookup and before the broker, like the install word — one sentence of supersession in the new GLASS.md section. No new marker (Hick). It refuses with `no mouse` if `mouse_id` is 0, and with `an app is running` in mode 3.

After the verdict, `layout_default` is set from it and journaled as `trial verdict B` (or `A`); on later boots the guest reads the last verdict line from the notebook and the row takes that layout. Until a verdict exists the default is A — every earlier gate stays green on the same binary to the pixel.

## The twin

The 7c shape unchanged: q35, IvyBridge, the stick copy over qemu-xhci, the 64 MB SATA disk, the e1000e on the cage to the relay, the VGA at 1920x1080 — and the mouse driven through the monitor as ring 6c does. The **synthetic human** in the checker reads the obs page for the cue, waits a scripted delay, moves and clicks: a table of delays and deliberate misses per cue, fixed in the checker, so every recorded number is predicted before the run. The trial needs nothing from the wire: the mock broker is up only because the boot expects a link, and no request is sent.

## Acceptance tests

Tests 1–4 are written before the code, frozen once written, mock only, no token spent. Ring 7c's, 7b's and 7a's gates stay the regressions on the same binary.

1. **Artefact and the document.** PE32+ as before; the stick as before; `stage7/TRIALS.md` parses cold — the cue table, the block order per sitting parity, the note formats, the verdict rule — and `stage7/trials.py` reproduces the worked example's table and verdict from the worked example's notes, byte for byte.
2. **Serial and the row, both layouts.** Boot from the stick copy at -smp 4 on a blank disk: the twenty-two lines of 7c unchanged; `! trial` with `mouse_id` 0 (no mouse device) refuses `no mouse` and journals nothing. With the mouse: `! trial` prints `trial: sitting 1 ABBA BAAB`, the mode word reads `trial A 1/8`, the row on a layout-A block is ring 6c's row to the pixel, the row on a layout-B block is four boxes at TRIALS.md's cells with the labels centred, and the cue line is in the conversation panel. Screendumps checked as ring 6c checks them.
3. **A sitting, the numbers predicted.** The synthetic human plays sitting 1 to the end: eighty cues, the scripted delays, three scripted misses in named blocks, one block on layout B and one on A. Assert: the notebook holds exactly the lines TRIALS.md's formats give for that script — hits where hits were scripted, misses where misses were, each block's median within ±30 ms of the scripted delays' median (the pointer's own input-to-photon is the slack, measured from the run, never assumed); the serial `trial:` lines equal the notes; the obs fields at each block boundary; the app panel's table after `done`; `layout_default` still 0. Then a second boot on the same disk: `S7: notebook N notes` counts the sitting, the sitting number is 2 and the order is `BAAB ABBA`, Esc in block 3 journals `aborted 3` and blocks 1–2 stand. Then three sittings played to a scripted verdict of B: the panel shows the verdict, `trial verdict B` is on the notebook, and a further boot shows layout B's row at the prompt with no trial running, `layout_default` 1 — and ring 6c's click rule still holds on the boxes (a click on `! grow` types the launch line).
4. **The bodyguard, and the default unchanged.** The payload table with the four new frozen paths (`stage7/TRIALS.md`, `stage7/test-7d.sh`, `stage7/checktrials.py`, `stage7/trials.py`) added to `PROTECTED` and their cases 0 wrong; the argv checks as 7c; and the 7c, 7b and 7a gates green on the ring's binary — layout A at the prompt is byte-identical to the row those gates already assert.
5. **The oracle — Wajira's.** One sitting per session. A rehearsal in the twin, windowed, with mlrig's mouse grabbed in the QEMU window — not trial data (the amendment above). Sittings 1, 2 and 3 on the HP with the PS/2 mouse, by METAL.md's day (one flash of the ring's stick, then boots only). His word on each sitting; the verdict on the third closes the ring. He may add sittings before the verdict only by amending this spec first — the rule is pre-registered.

## Decisions for the owner

1. **The control trialled.** Recommend the choices row, text against drawn boxes, as above. The alternative the Stage 6 spec named — the conversation taking the whole width until an app appears — is a layout of the panels, not of a pointing target, and would need a different task; it can be trial two.
2. **The design.** Recommend ten cues a block, eight blocks a sitting in `ABBA BAAB` / `BAAB ABBA`, three sittings, the sign-test rule at ten of twelve with misses not worse. Your call on every number; a GP's N-of-1 instincts outrank mine here. If you would rather randomise pairs than counterbalance, the seed must be journaled so the twin can replay it.
3. **The cue.** Recommend the label word only (`click: grow`), no colour or arrow, so the trial measures pointing, not reading. Alternative: highlight the cued item — but a highlighted target is a different target, and both layouts would need it.
4. **Where the verdict lives.** Recommend the notebook (`trial verdict B`), read at boot, so the machine remembers its own evidence with the broker off. Alternative: the broker keeps it host-side — but that is the wrong machine remembering.
5. **The settings.** Recommend sitting 1 in the windowed twin (no flash, cheap to repeat if the protocol has a snag) and sittings 2–3 on the HP. A sitting in the twin measures QEMU's pointer path too; the serial line names where each sitting ran, and the analysis does not mix them into one verdict unless you say so. Alternative: all three on the HP.
6. **The model and the effort for CC** — your call at the gate, recorded at item 0. For comparison so far: Opus-high for Stages 0–1, Fable-high for 2–6a, 6c, 7a, 7b; Fable-medium for 6b and 7c.
7. **The GLASS.md section** goes in by your hand (`cat >>`), as ring 6c's did; the four new files are frozen at the plan's freeze item.

## What this ring does not do

No pointer acceleration; no timing of keyboard tasks (time-to-done is recorded for them, as since 6a, and a keyboard trial can be trial two); no second participant; no trial of anything but the row; no change to any frame, the wire, the rehearsal, the germline or the home image. The rehearsal's criteria are untouched: an app still cannot reach the row.

## Caveats carried

One machine, one firmware, plus the HP; the x2APIC and trampoline paths unproven; TIPG and the PHY speed reading from Stage 7's closure unchased; the trial's clock is the TSC, calibrated once at boot against the PIT — good to a few parts in a thousand, which is inside the ±30 ms slack and far inside a difference worth acting on.

## The windowed run (the oracle's sitting 1)

Three terminals at the repo root — the broker `python3 broker/wire.py`, the relay `python3 broker/relay.py --bind 127.0.0.1 --port 9997`, and the machine; click in the QEMU window to grab the mouse, Ctrl+Alt+G releases it; type `! trial` at the prompt:

```
./stage7/mkimage.sh && python3 stage7/mkstick.py
rm -f stage7/out/disk.img; truncate -s 64M stage7/out/disk.img
cp stage7/out/stick.img stage7/out/stick.twin.img
qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -device qemu-xhci -drive if=none,id=stick,format=raw,file=stage7/out/stick.twin.img -device usb-storage,drive=stick \
  -drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9997' \
  -device e1000e,netdev=n0,mac=6c:3b:e5:3b:86:45 -serial stdio
```

A sitting is eighty clicks and seven pauses: about four minutes.
