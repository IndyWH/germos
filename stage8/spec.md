# Stage 8 — The molt · spec

**Approved by the owner, 25 September 2026**, all fourteen decisions settled the same day (below). Written in a fresh Cowork session on Opus 5.5 at high effort, on Omarchy (mlrig). CC's implementer is Opus 5.5 from this stage's kickoff (the owner's decision of 23 September 2026); the effort is decided at the kickoff (decision 11). The first part to molt is the owner's decision (decision 1).

**The owner's decisions, 25 September 2026:** decision 1, the first part to molt is `i8042`, as recommended; decision 11, CC implements ring 8a on Opus 5.5 at **high** effort; decision 12, the GPS rewrite is **postponed** and not done in the spec session; decisions 2 to 10, 13 and 14 **as recommended**. So: rings 8a to 8g, with 8c to 8g given short specs at their gates; parts in the home store under `part-` names and `molt ` notes on the notebook; the loader in its own frozen file; the PCH's TCO watchdog with a 30 s deadline, a 60 s health window and the recovery rules as written; the strict rule for beat at a 5 % margin under `-icount`; the `i8042` measures as written; shadow to 3 boots, 1,000 keyboard bytes, 5,000 mouse packets and zero disagreements, then probation for 3 healthy boots; the witness before every take from 8c on and at the week's start and end; the week's rules as written; the TRIALS.md sentence by the owner's hand at 8a's kickoff with 7d's test 1 run once; the policy gate re-checked at every ring's kickoff.

**Goal (foundation §7, Stage 8):** the OS replaces the generic core with parts it grew itself, one component at a time — drivers first, kernel proper last. Each brewed part must beat the generic one in the twin, then run in shadow beside it before it takes over. The old core is demoted to a recovery slot, never deleted, and a watchdog boots it if the brewed system fails its health checks. Every so often the system is re-derived from the frozen seed and compared with the brewed line. Two parts never molt: the loader and the cryptography. **Done when the machine reboots into a kernel it grew itself and survives a week. Proves the OS is self-hosting.**

**The policy gate, re-checked 25 September 2026:** the help centre article *Use the Claude Agent SDK with your Claude plan* (last updated 16 June 2026) still says the change is paused and nothing has changed: the Agent SDK, `claude -p` and third-party apps draw from the subscription's usage limits. The broker keeps shelling out to `claude -p`, no API key anywhere. Stage 8 makes more real grows than any stage before it (every part, every re-derivation), so the gate is re-checked at **every ring's kickoff** (decision 14), not only at Stage 9.

**What this stage inherits:** the ring 7d binary, 45,056 bytes, and its stick as flashed for the trial; the HP Compaq Elite 8300 with GermOS's table on its SATA disk, 277 notes ending in `trial verdict A`, and the calculator; the twin of the HP (the 7c shape); mlrig on Omarchy with NASM 3.02, QEMU 11.1.1, Python 3.14.7 and the `claude` CLI 2.1.280; the three Stage 7 gates, the 7d gate and the payload table (1678 cases) green; seven freeze openings on the record.

---

## The words this spec uses

| Word | Meaning in GermOS |
|---|---|
| **seed** | The Stage 8 binary as CC builds it: the loader, the cryptography, and the generic implementation of every slot. It lives on the stick. The guest never writes the stick. |
| **slot** | A named job the seed can hand to a part. Stage 8 has four: `i8042` (keyboard and mouse), `disk` (AHCI), `wire` (e1000e), `kernel` (the main loop and the glass core). There is no slot for the loader or the cryptography. |
| **part** | A grown blob that fills one slot, with a header naming its slot, its ABI and its SHA-256. |
| **generic** | The seed's own implementation of a slot, written by CC at build time. It is never deleted. |
| **grown** | Made by GermOS's own loop: the machine asks, Claude writes the part from a plan, the twin rehearses and measures it. |
| **brewed line** | The chain of live parts, each rehearsed in a twin of the machine as it was when that part was grown. |
| **shadow** | The part is on the machine and sees the machine's real traffic, but the generic does the work. Every disagreement is counted. |
| **live** | The part does the work. The generic waits in the seed. |
| **probation** | A live part's first boots, under the watchdog, before the next part may start. |
| **demoted** | Sent back from live or shadow to the generic, by the watchdog or by the owner. |

The foundation's analogy holds exactly: shadow is a registrar seeing patients while the consultant reviews every decision; `! molt take` is the sign-off; probation is the first weeks on their own, with the watchdog as the senior on call.

## The two parts that never molt

**The loader** is everything from `efi_main` to the moment the seed hands a slot to a part:

- the UEFI entry, the GOP mode, the memory map, ExitBootServices, the GDT, the paging and the IDT;
- serial — the observation chart — from its first line;
- its own read path to the disk: the seed's AHCI, the GPT, the notebook replay and the home table, used to find the parts and the molt state before any part runs;
- the checks at the door: each part's SHA-256 against its home entry, its header against PARTS.md;
- the recovery decision, the watchdog's arming and the pet routine (below);
- the exception handler's blame line.

**The cryptography** is the seed's SHA-256 (`sha256`, `sha256_block`, the round constants) and, when it joins the guest one day, the TLS blob.

Three things keep them out of reach. The loader and the cryptography move into their own source file, `stage8/loader.asm`, included by `stage8/stage8.asm`, and that file joins the hook's `PROTECTED` list at the ring 8a freeze. Only the owner's hand opens it, as with any frozen file. PARTS.md names no slot for either, so a part frame that names one is refused at the door. And after the handover the loader's pages are mapped read-only (CR0.WP set), so a stray write from a part faults with a clear blame instead of quietly corrupting the floor (decision 4). At every boot that loads a part, the loader runs SHA-256's known answer for `abc` before it trusts a hash.

The loader keeps its own copy of the disk read path even after the `disk` slot molts. A grown disk driver serves the machine after the handover; the loader never depends on it to find the parts. That is the price of a floor that cannot be pulled out from under itself.

## Where the parts live, and the recovery floor

**The recovery floor is the seed on the stick.** It holds a generic implementation of every slot, so a boot that loads no part is always a whole machine. The guest never writes the stick, and every Stage 8 gate asserts the stick copy's tables unchanged, as ring 7c did. That is the Spectrum's ROM in our terms: the brewed system can break itself, but it cannot touch the thing it falls back to.

**The parts live in the home store; the molt state lives on the notebook** (decision 3). No new partition and no new disk format:

- A part is a HOME.md entry under a reserved name, `part-<slot>` (`part-i8042`). The home store already gives a part everything it needs: a size up to 1 MB, its SHA-256, a previous build for undo, and a torn entry that is ignored. A name beginning `part-` is refused by `! <name>`, so a part can never be launched as an app.
- The state is journaled on the notebook as notes with the reserved prefix `molt `, as ring 7d reserved `trial `: `molt i8042 shadow`, `molt i8042 live`, `molt boot 41 parts i8042`, `molt healthy 41`, `molt i8042 demoted watchdog`, one note a disagreement (the first sixteen a boot), one summary a boot. A typed note beginning `molt ` is refused as reserved. The loader reads the last state of each slot from the notebook at boot, as the 7d verdict is read.

The alternative is a third GPT partition (decision 3). It would separate parts from apps cleanly, but it means rewriting the partition table on the HP's disk, which holds the trial's 277 notes. The home store and the notebook are frozen formats that have run on the metal since 18 and 24 September.

**With no `molt` note on the notebook, the Stage 8 binary is ring 7d's to the line and to the pixel.** No new serial line appears until a part is installed. So the 7c and 7d checks run against the Stage 8 binary through their seams, unchanged, as its regressions. How they are pointed at it is the plan's to find (a probe before the freeze), never an edit of a frozen file.

**What a part is given.** A part is position-independent code called by the seed, as components are (GERMLINE.md). Its service table (ABI 3, defined in a new frozen `stage8/PARTS.md`) gives it only what its slot needs: PCI configuration reads and writes, an uncached MMIO mapping, DMA pages below 4 GB from the seed's pool, `ticks_ms` and `pit_wait`, one raw serial line with the prefix `part:`, and its slot's upcalls (for `i8042`: a key event and a mouse packet). No notebook, no framebuffer, no network.

**How a part arrives.** The owner types `! molt <slot>` on the machine. It is a reserved word the guest answers before the home lookup, as `! trial` is. The guest sends the broker a molt request carrying the slot and **the machine's identity as the guest reads it**: the CPUID signature, and the PCI vendor, device and revision of the slot's device. The germline key is built from that identity, not from `qemu-q35-ovmf`, so a part is keyed to the HP (GERMLINE.md promised this at Stage 7 and it was not done). The broker grows, rehearses and measures the part in the twin of the HP, then delivers it in a new frame kind. The guest stores it in the home store in `shadow`. A later `! molt take <slot>` promotes it; `! molt undo` steps back one state; `! molt` alone shows the table. Four words, one reserved prefix (Hick).

## The watchdog: what it checks

**The hardware.** The watchdog is the PCH's own TCO timer — on the HP, the Q77's; in the twin, q35's ICH9 (decision 5). The loader arms it just before the first part runs. If nothing pets it before its deadline (30 s, pre-registered), the chipset resets the machine. Nothing in GermOS can be hung so badly that the reset does not come, because the timer is in the chipset, not in our code. Whether QEMU's ICH9 timer resets the twin, and whether the HP's firmware has locked the chip's no-reboot bit, are **measured before anything freezes**: the first by a probe in the twin, the second by the owner on the HP at ring 8a's oracle. If the twin's timer cannot reset, the twin uses QEMU's `i6300esb` watchdog device, and the HP's TCO is proven on the metal alone.

**The pet.** The pet routine belongs to the loader, and it decides for itself. The main loop calls it, and it pets the timer only when all of these hold since the last pet:

1. the main loop's heartbeat counter has moved;
2. the glass core's frame counter has moved;
3. no exception has been taken;
4. every live part's `health()` answers ok, and the seed's outside checks of that slot agree — for `i8042` the controller's status is sane and no queue has overflowed; for `disk` the last command completed without error; for `wire` the link is up and the transmit ring is not stuck.

When the kernel molts, the grown kernel must call the pet routine. That is part of its contract. If it stops calling, the machine resets.

**The health mark.** When a boot that loaded parts has stayed healthy for 60 s after `keyboard ready`, the guest journals `molt healthy <boot>`. A boot is unhealthy until it earns that note.

**The recovery rules** (decision 5), applied by the loader at the next boot:

| What the loader finds | What it does |
|---|---|
| The chipset's record that the last reset was the watchdog's (the TCO status bit that survives a reset, where the chip keeps one) | Recovery boot at once: no parts. The part on probation is demoted and journaled `molt <slot> demoted watchdog`. `S8: recovery <slot> watchdog` |
| One unhealthy boot with no evidence (the power was cut in the first minute, say) | Tries the parts again, and counts |
| Two unhealthy boots in a row | Recovery boot: the part on probation is demoted. `S8: recovery <slot> unhealthy` |
| A part whose SHA-256 does not match its home entry | That part is skipped and the generic serves its slot. `S8: part <slot> bad hash`. Nothing is demoted: a torn write is not a verdict |
| **Esc held at power-on**, polled by the loader before the handover | Recovery boot, nothing demoted. `S8: recovery owner`. The human is the highest-priority device, so the owner always has a way back that needs no command |

Only one part is on probation at a time, and no part enters shadow while another is on probation. So the blame is never ambiguous. If a failure comes after every live part has passed probation, the recovery boot demotes all of them, journals `molt recovery all`, and the owner decides which to promote again.

The exception handler, when a part is loaded, adds one line before it halts: `ERR: exception <vector> in part <slot> +<offset>`, or `in seed` when the address is not in a part. It writes nothing to the disk in exception context. The halt stops the pets, and the watchdog does the rest.

## How a grown part is shown to beat the generic one

Everything below is **pre-registered in the part's plan**, `plans/parts/<slot>.md`, committed before the grow. The plan carries the intent, the slot's contract, the test corpus, the measures, the margins and the shadow threshold. The git commit is the timestamp of the pre-registration. A plan amended after a failed verdict is a new pre-registration, not a second look at the same data. This is ring 7d's rule, carried over.

**Gates — every one must pass.** A part that fails any gate is not delivered.

1. **The safety criteria**, as GERMLINE.md's and GLASS.md's rehearsals judge an app: the twin boots, the part loads, no `ERR:`, no exception, `health()` answers.
2. **Differential correctness against the generic.** The corpus goes through both implementations, and the outputs must be identical, event for event. The generic is the reference because it has passed every oracle since Stage 2. For `i8042` the corpus is a fixed byte stream in PARTS.md: every make and break code, the `E0` and `E1` sequences, typematic runs, mouse packets with every sign and overflow bit, a lost byte in the middle of a packet, keyboard and mouse bytes interleaved.
3. **The frozen gates with the part live.** Every existing gate that exercises the slot runs in the twin with the part live, and must pass as it does on the generic. For `i8042` that is the typing, the note across a reboot, the click on the choices row, and the 7d gate's synthetic human playing a sitting through the part's decode.

**Measures — decide whether it beats.** Both implementations run on the same corpus, through the same slot interface, in one bench boot of the twin under QEMU's `-icount`. In that mode the twin's time counts instructions, so the numbers are **instruction counts, the same on every run**, not wall-clock noise. The bench alternates the two in blocks (generic, grown, grown, generic, and so on) so neither is always measured warm. Whether `-icount` behaves as documented under QEMU 11 is measured by the plan's probe before the freeze.

**The rule** (decision 6): the part **beats** the generic if every gate passes, **and** its primary measure is lower than the generic's by at least the plan's margin (5 % recommended), **and** no secondary measure is worse by more than its margin. Otherwise the generic stays. That is a finding, recorded in the germline's provenance and in HANDOVER, not a failure to hide. For `i8042` the recommended primary is the median instructions per byte, from the slot's entry to the event in its ring. That is the human's input path, where the constitution says the milliseconds are guarded. The secondaries are the worst case per byte and the part's size in bytes (decision 7).

**On the metal the same comparison is repeated in shadow**, in real cycles: the guest times both decoders with the TSC on every real byte and journals the medians with each boot's summary. These numbers are reported as confirmation. They do not decide, because the twin's rule is the one registered.

## Shadow: supervised practice before sign-off

In shadow the part sees what the machine really sees, and the generic's answer is the one used. For `i8042` this is exact. The seed's interrupt stub reads the status byte and port `0x60` once, as the gotcha requires. It hands the byte to the generic decoder, whose events go to the rings as ever, and to the part's decoder, whose events go to a shadow ring. The two are compared event by event. The part's `init` (the controller's cold init and the mouse reset) cannot be shadowed, because there is one controller. It is exercised in the twin's gates and at the takeover boot, under probation.

The other slots cannot be shadowed as exactly, and each of their ring specs decides how:

- for `disk`, every read is made twice, by each driver in turn, and the bytes compared; writes go through the generic only; and in probation every write the part makes is read back and checked;
- for `wire`, the frames and descriptors are built by both and compared byte for byte, and the generic's are sent;
- for `kernel`, two main loops cannot both run, so shadow becomes a long soak in the twin, then probation on the HP under the watchdog.

**The threshold** (decision 8), pre-registered in the part's plan. For `i8042` the recommendation is: at least 3 separate boots, at least 1,000 keyboard bytes (about 400 key presses) and at least 5,000 mouse packets, and **zero disagreements**. The guest refuses `! molt take` below the threshold and shows the counts. The owner's word is the sign-off. **Probation** lasts 3 healthy boots.

## The witness: re-derivation from the frozen seed

**Why.** After the first part, each new part is rehearsed in a twin of the machine as it is: the seed plus the parts already live. That is what "fitted to the machine" means. It is also how a fault could perpetuate itself: a subtle fault in part one shapes the rehearsal that passes part two.

**What.** `broker/witness.py` builds a second line that never touches the brewed one:

- a clean workspace with an **empty germline**;
- the seed rebuilt from its pinned commit and checked against the SHA-256 recorded in a new frozen `stage8/SEED.md`;
- a twin running **the seed alone**, with no brewed part;
- every live part grown again from its plan, by a fresh `claude -p` call, rehearsed, measured, and then run on the same corpus as the brewed part.

**The comparison is behaviour, not bytes.** Claude never writes the same bytes twice, so byte equality would fail every time. The witness demands identical outputs on the corpus, the same gates passed, and measures within the plan's margins. It prints `witness: agree` or `witness: diverge <slot> <what>`. A divergence sends the brewed part back to shadow until the owner has judged it.

**What the witness cannot do, said plainly.** It is independent of the brewed line's history, not of the model. A mistake Claude makes every time it writes a given driver will appear in both lines, and they will agree. The guard against that is the other independent witness Stage 8 keeps: the differential check against the generic, which was written by a different route (CC at build time, judged by every oracle since Stage 2).

**When** (decision 9): before every `! molt take` from ring 8c on, and at the start and end of the week.

**What changes in the seed.** Only the loader and the cryptography are frozen for good. The seed's other code — the slot plumbing each ring adds, the generic implementations — may still change ring by ring through the usual build loop. Each seed version is recorded in SEED.md with its SHA-256 and its commit, and the witness uses the current one. What makes the witness independent is that it never runs brewed code, not that the seed never changes.

---

## The rings

Stage 8 is large, and later rings depend on what the earlier ones teach. So this spec designs rings 8a and 8b fully and gives 8c to 8g their done-when and their shape. Each of those gets a short spec of its own at its gate, as ring 7d did (decision 2). One fresh CC session per ring, each with its own plan gate and its own frozen tests.

| Ring | Name | What it proves | Done when |
|---|---|---|---|
| **8a** | **The floor** | A part can fail without taking the machine with it | In the twin of the HP, five fixture parts meet their fates: `good` passes shadow with no disagreement and runs live after `! molt take`; `wrong` is caught in shadow and cannot be taken; `hang` is reset by the hardware watchdog and the next boot comes up on the seed's own driver with the part demoted; `fault` is named and recovered the same way; `liar` is refused at the door. With no part installed the machine is ring 7d's to the line. On the HP, by the owner's hand: `good` live, then `hang` live, and **the HP resets itself** and comes back in recovery |
| **8b** | **The first molt** | GermOS grows a driver for itself that beats the one it was given | The first part (the owner's choice), grown by the real backend from its plan and keyed to the HP's identity, beats the generic in the twin by the plan's pre-registered rule, passes its shadow threshold on the HP, and runs live after a reboot and through probation. By the owner's sign-off |
| **8c** | **The witness** | The brewed line can be checked by something it did not make | `broker/witness.py` re-derives the live part from the frozen seed and agrees with the brewed line, and a planted divergence (a fixture brewed part with one scancode decoded wrongly) is caught |
| **8d** | **The disk** | The machine keeps what it grows with code it grew | The AHCI part live on the HP through the 8b pipeline (read-compare shadow, write read-back in probation), witnessed |
| **8e** | **The wire** | The umbilical is carried by grown code | The e1000e part, fitted to the 82579LM, live on the HP: `? ping` answered and a part delivered through it, witnessed |
| **8f** | **The kernel** | The machine's time is scheduled by code it grew | The main loop and the glass core as one grown part. It beats the seed's on input-to-photon (`ph` and `pt`) while a hog burns every other core — the foundation's §5 budget test. It is live on the HP after a reboot, calls the pet routine, and is witnessed |
| **8g** | **The week** | The OS is self-hosting | 168 hours on the HP on the brewed system, by the rules below |

The alternative to 8d and 8e is a shorter path: after the first driver, go straight to the kernel and the week (decision 2). The foundation says drivers first, kernel last, but not that every driver must molt. The recommendation is all three, because a grown kernel on the seed's disk and wire is half a molt.

## Ring 8a — the floor

**What is built.**

- `stage8/stage8.asm`, copied from `stage7.asm` at item 1, with the loader and SHA-256 moved into `stage8/loader.asm`.
- The slot table: one pointer set per slot, the generic's by default.
- ABI 3 and the part frame; the `part-` names in the home store; the `molt ` notes; the four `! molt` words.
- The shadow ring and the comparison for `i8042`.
- The TCO watchdog, the pet routine, the health mark, the recovery rules, Esc at power-on, the blame line, the loader's pages read-only.
- `broker/molt.py`, the molt broker, subclassing the wire broker: `--mock` serves the fixtures and spends nothing.
- `stage8/PARTS.md` and `stage8/SEED.md`, frozen documents written from the design above.

**The fixtures.** Five hand-written parts for the `i8042` slot, committed and frozen as the ring 6 fixtures were:

| Fixture | What it is | Its fate |
|---|---|---|
| `good` | The seed's own decoder, packaged as a part | Shadow with 0 disagreements; taken; live; all gates green |
| `wrong` | `good` with one scancode decoded as another | Shadow counts the disagreement; `! molt take` refused |
| `hang` | `good` whose byte handler spins forever on its 100th byte | Live; the watchdog resets the twin; the next boot is recovery, the part demoted |
| `fault` | `good` with `ud2` on its first mouse byte | Live; the blame line names the part; reset; recovery, demoted |
| `liar` | `good` stored with a changed byte after its hash was written | Skipped at the door; the generic serves; nothing demoted |

**Acceptance tests, ring 8a** — written first, frozen, mock only, no token spent. Every run appends to `stage8/out/gate-8a.log`.

| # | Test |
|---|---|
| 1 | **Artefact and documents** — PE32+ as before; the stick as 7c; PARTS.md and SEED.md parsed cold and their worked examples reproduced; the part frame and the `molt` notes by their formats; SHA-256's known answer. |
| 2 | **No part, no change** — on a blank disk and on a disk holding a Stage 7 notebook: no `S8:` line, the 7c and 7d checks green on the Stage 8 binary; a disk carrying ring 7d's notes and a `trial verdict` boots in that verdict's layout. |
| 3 | **The fates** — in the twin of the HP with the synthetic human from ring 7d typing and clicking, each fixture in turn as its row above says: the serial lines, the notes as parsed from the host, the recovery within the pre-registered time, the seed's driver serving after recovery (typing and a click work), `! molt undo` one step back, Esc held at power-on, the stick copy's tables unchanged, and every note written before the run unchanged byte for byte. |
| 4 | **The bodyguard and the regressions** — the new frozen paths, `stage8/loader.asm` among them, in `PROTECTED` with their payload cases 0 wrong; the argv checks as 7c; the 7c, 7b, 7a and 7d gates green on their own binary. |
| 5 | **The owner, on the HP** — one flash of the ring's stick. With `broker/molt.py --mock` behind the relay: `! molt i8042` installs `good`; three boots of typing and mouse work to the threshold; `! molt take i8042`; a boot live. Then `hang` in its place: the HP freezes, **resets itself** within a minute, and comes back with `S8: recovery i8042 watchdog` and the keyboard working. Then Esc at power-on. His word closes the ring. If the HP's firmware has locked the TCO, that is the ring's finding, and decision 5's fallback applies |

## Ring 8b — the first molt

**What is built.**

- The plan format for parts, and the first plan, `plans/parts/<slot>.md`, committed before any grow.
- The real grow path in `broker/molt.py`: the brief carries the plan, the HP's identity, ABI 3 and the CLAUDE.md gotchas for that device, and says the part is for this machine only.
- The bench boot under `-icount`, and the verdict by the plan's rule.
- The shadow's TSC medians on the metal.

The broker's brief and the grow path stay unfrozen, as `claude_backend.py` always has. The plan, the corpus and the verdict rule are frozen at the ring's freeze, before the first real grow.

**Acceptance tests, ring 8b:**

| # | Test |
|---|---|
| 1 | **Artefact and documents** — as 8a, plus the plan parsed cold and its measures and threshold read back. |
| 2 | **The pipeline, mocked** — `! molt i8042` against `--mock` with a canned grown part that differs from the generic in code but not in output: rehearsed, benched, a verdict printed by the rule, delivered in shadow; a canned part that is slower gets `the generic stays` and nothing is delivered. |
| 3 | **Shadow to live, in the twin** — the synthetic human drives the canned part to its threshold; `take`; probation boots; the pet routine sees `health()`; the 7d gate's sitting played through the part. |
| 4 | **The bodyguard and the regressions** — as 8a, with 8a's gate added. |
| 5 | **The owner** — `! molt <slot>` on the HP with the real broker: Claude writes the part, the twin rehearses and benches it, the verdict comes back. If it beats: shadow over at least three sessions to the threshold, one session at a time; the sign-off; a reboot live; probation. If it does not beat: the finding is recorded, and the owner chooses to amend the plan (a new pre-registration) or to move to another slot. His word closes the ring |

## Rings 8c to 8g, in outline

Each gets a short spec at its gate. What each must settle:

- **8c the witness:** SEED.md's recorded seed and how it is rebuilt from its commit; the clean workspace; the planted divergence; how long a re-derivation may take in tokens and minutes.
- **8d the disk:** the shadow's read-compare and how two drivers take turns on one AHCI port; write read-back in probation. The trial's record is safe whatever happens, because every sitting's chart is in `history/`.
- **8e the wire:** the frame-building shadow; the part fitted to the 82579LM. This is where Stage 7's caveats about the wire are settled: TIPG at the chip's default, the PHY speed after a reset, and WIRE.md's halting sentence (a freeze opening, by the owner's hand, if he wants the document to say what the monitor does).
- **8f the kernel:** the kernel's service table (everything the main loop and the glass core call); its intent from foundation §5 (the interactive path reserved on its own core, homeostasis under load); the budget test with a hog as the primary measure; the soak in the twin in place of shadow; the pet contract.
- **8g the week:** below.

## The week — ring 8g, the survival test on the HP

**The start.** A cold boot into the brewed system with every molted part live and past probation, the kernel among them. The witness agrees, and the chart is started. The start time is the first `molt healthy` note of that boot.

**The record is the machine's own.** Every hour the guest journals `molt heartbeat <hour> <counters>`: uptime, the main loop's and the glass core's counters, the worst `ph` and `pt` in that hour, the parts' health counts. So the week is proven by 168 notes on its own notebook, whether or not mlrig kept the chart running. mlrig is the owner's daily machine and may reboot, or boot Ubuntu, during the week. `! molt week` shows the week's table on the panel, and a photograph of it closes the record.

**The daily ward round** (decision 10): once a day the owner moves the mouse, types a note `day <n>`, launches the calculator and does a sum. The point is to prove the human path still works each day, not to keep the machine busy. A missed round is a protocol deviation, recorded; it is not a failure.

**It fails** at any unplanned reset, any recovery boot, any `ERR:` or exception, any gap between heartbeats longer than 70 minutes, or any hour whose worst `ph` or `pt` breaks the budget ring 8f registers. **It is void, and restarts,** if the power is cut from outside (a power cut in the flat, or the plug pulled). **It passes** at 168 hours from the start, with no failure, the seven ward-round notes on the notebook, the witness agreeing again at the end, and the owner's word. That is the Stage 8 done-when, and it closes the stage.

## Carried into Stage 8

1. **The label-width sentence for TRIALS.md** (text in HANDOVER, ring 7d's closure): recommended to be applied by the owner's hand at ring 8a's kickoff, as a planned freeze opening, with the 7d gate's test 1 run once straight after. If test 1 goes red, the sentence comes out again and waits (decision 13).
2. **The GPS in old git history** (photographs committed before `9bee3e2`): the owner asked for this to be raised at this gate. The recommendation is to do it **before the ring 8a kickoff**, in its own CC session: `git filter-repo` replacing the old photograph blobs with the plain ones; a follow-up commit mapping the hashes HANDOVER cites; the force push by the owner's hand. Every Stage 8 commit made first is one more hash to rewrite (decision 12). **Postponed by the owner, 25 September 2026.** GitHub keeps unreachable commits reachable by their hash for a while after a force push; GitHub support can purge them if the owner wants that too.
3. **Zoom-to-fit on Hyprland:** every windowed QEMU line in Stage 8's documents carries `-display gtk,zoom-to-fit=on`, and CLAUDE.md's windowed block gains it at 8a's item 0. The gates are headless and are unaffected.
4. **Stage 7's caveats:** the wire's (TIPG, the PHY speed after a reset, WIRE.md's halting sentence) are ring 8e's to settle, as above. The nineteen-line first boot stays unwatched on the metal, because Stage 8 never reformats the HP's disk. The x2APIC and trampoline paths stay unproven. The watchdog will give the HP more cold resets than it has ever had, which is a test of the boot path in itself.
5. **The HP's disk:** Stage 8 writes its `molt` notes after the trial's 277 and changes nothing before them. Test 3 of every Stage 8 ring asserts that earlier notes are unchanged byte for byte.
6. **Ring 7d's procedure finding:** no step asks the owner to stop and report in the middle of a measured run. Shadow sessions and the week run to their end first, then he reports.

## Decisions for the owner

**All fourteen settled by the owner on 25 September 2026: 1, 11 and 12 as marked below; the rest as recommended.**

1. **The first part to molt — yours.** Recommend **`i8042`**, keyboard and mouse. It is the smallest driver (about 470 lines of the seed). Its shadow is exact, because both decoders see the same byte. It touches no stored data. The twin models it well. And its measure is the human's own input path, which the obs strip already watches. The alternatives: **`disk`**, where the bespoke gain is plausible but a wrong write could damage the notebook and its shadow is two drivers taking turns on one port; **`wire`**, where fitting to the 82579LM matters most (two defects the twin could not show), but the twin is least faithful there, no exact shadow exists, and a failure cuts the umbilical that delivers parts. **Decided 25 September 2026: `i8042`, as recommended.**
2. **The rings.** Recommend 8a to 8g as above, one CC session and one plan gate each, with 8a and 8b designed here and 8c to 8g given short specs at their gates. Alternative: the shorter path, 8a, 8b, 8c, then the kernel and the week, without molting the disk and the wire.
3. **Where parts and molt state live.** Recommend the home store under `part-` names, and `molt ` notes on the notebook. No format change on the HP's disk. Alternative: a third GPT partition, which is cleaner but means rewriting the table on a disk holding data.
4. **The loader boundary.** Recommend the list under "The two parts that never molt": its own file, hook-protected from 8a's freeze, its pages read-only after the handover, and its own disk read path forever.
5. **The watchdog and the recovery rules.** Recommend the PCH's TCO timer; a 30 s deadline; a 60 s health window; recovery at once on the watchdog's evidence, and after two unhealthy boots without it; Esc at power-on as the owner's way back; one part on probation at a time. Fallback if the HP's firmware has locked the TCO: the boot counter and the power button, with the week counting any hang as a failure either way.
6. **What "beat" means.** Recommend the strict rule: every gate passes, the primary measure lower by at least 5 %, no secondary worse beyond its margin, measured as instruction counts under `-icount`. A part that does not beat stays generic, and that is recorded as a finding. Alternative: non-inferiority, where a part that is no worse may molt. That is easier, but the foundation says *beat*.
7. **The first part's measures.** For `i8042`, recommend the primary as median instructions per byte from the slot's entry to the event in its ring; the secondaries as the worst case per byte and the size in bytes; the corpus as described under the gates.
8. **The shadow threshold and probation.** Recommend at least 3 boots, 1,000 keyboard bytes, 5,000 mouse packets and zero disagreements, then probation for 3 healthy boots. Your N-of-1 instincts outrank mine on every number.
9. **The witness's cadence.** Recommend before every `take` from 8c on, and at the week's start and end. Alternative: on the owner's request only. That is cheaper in tokens, but it is then a check, not a witness.
10. **The week's rules.** Recommend 168 hours, the hourly heartbeat on the notebook as the record, the daily ward round, and the fail and void lists above.
11. **CC's effort for ring 8a** (the model is Opus 5.5, decided). Recommend **high**: 8a draws the boundary that is frozen for good and builds the thing that resets the machine. The effort for later rings is decided at their kickoffs. **Decided 25 September 2026: Opus 5.5 at high effort for ring 8a.**
12. **The GPS rewrite.** Recommend now, before 8a's kickoff, in its own CC session, with the force push by your hand. Alternative: leave the history as it is. **Decided 25 September 2026: postponed** — not done in the spec session; when it is done, it is its own CC session.
13. **The TRIALS.md sentence.** Recommend applying it at 8a's kickoff by your hand with 7d's test 1 run once. Alternative: leave it until TRIALS.md is next opened for a second trial.
14. **The policy gate.** Recommend a re-check at every Stage 8 ring's kickoff, because this stage spends more real `claude -p` calls than any before it.

## Risks, with likelihood

**Certain — a grown part may not beat the generic.** The generic `i8042` code is small and has been fixed by seven rings of findings. Mitigation: the rule treats "the generic stays" as a result. The plan can be amended once as a new pre-registration, or another slot can go first.

**High — the HP's firmware has locked the TCO, or routes its first timeout to its own SMM code.** Mitigation: ring 8a's oracle tests it on the HP before anything depends on it. The fallback is written in decision 5. The week counts a hang as a failure whether or not the machine resets itself.

**Medium — the twin's watchdog or `-icount` behaves otherwise than documented under QEMU 11.** Mitigation: both are measured by a probe before the freeze (the lesson of the sixth freeze opening: pin nothing about a tool's behaviour that the tool does not document).

**Medium — correlated mistakes.** The witness cannot catch a mistake Claude makes every time. Mitigation: the differential check against the generic, and the frozen gates, are written by a different route.

**Medium — the kernel ring is far larger than the driver rings.** Mitigation: it gets its own spec, and it may split into rings of its own.

**Low but fatal — a grown part damages the HP's disk.** Mitigation: the `disk` slot is not recommended first; its shadow writes nothing; probation reads back every write; the trial's record is already in `history/`; the HP's drive is sacrificial. mlrig's disks stay outside the blast radius, and the bodyguard is unchanged.

**Low — token cost.** Each part is one grow with a retry, and each witness one more. Mitigation: the policy gate at every ring, and the germline serving repeats.

## What Stage 8 does not do

No new devices: sound and the full screen stay on the list for a later gate. No TLS in the guest; the rule reserves its place for the day it comes. No second machine: the P330 stays patient two, later. No shared germline across machines: Mycelium stays on the horizon. No USB driver and no timer interrupt, unless ring 8f's spec decides the grown kernel needs one. No part runs anywhere but the twin and the HP. The flash stays the owner's hand. The automated gates speak only to the mock and spend no token. The foundation stays at v1.9.
