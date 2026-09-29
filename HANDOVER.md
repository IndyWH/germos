# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 28 September 2026 — **Ring 8t, trial two, OPENED** (inserted after ring 8a and before ring 8b, by the owner's decision at trial two's kickoff; the line is under `stage8/spec.md`'s ring table). `trials/plan-8t.md` was approved at the plan gate with Cowork's five amendments (A1 the verdict on the sign of S, the sum of the sixteen pair differences — B if S > 0, G if S <= 0 — with the note carrying S/16 truncated toward zero; A2 the times hidden on the strip as well as both panels, on every sitting boot and every boot that shows the offer, until a verdict note exists; A3 the owner's decision on how the HP's days are run, recorded below; A4 the flush's arguments and its failure named; A5 the 8a gate inside test 4 run at item 9, not item 7) and all nineteen deviations accepted bar deviation 4, which A1 withdraws. The spec is `trials/spec-trial2.md` (approved 27 September 2026 at `beef2da`) with its **Amendment 1** of 28 September 2026 (Enter starts sittings 2 to 4 at an offer; the panel says `saved` when every note is on the disk; the boot names what is due). **The model note:** CC on **Opus 5.5 at high effort** (spec decision 11). **The policy gate,** re-checked by Cowork on 28 September 2026: the help centre article is unchanged since 16 June 2026, the change is still paused, and `claude -p` draws from the subscription; trial two's sittings need no broker, and the gate talks only to mocks. **The owner's decision of 28 September 2026 (A3)** closes the question ring 8a's closure carried: **no new hardware.** The owner does the physical steps when asked, and the procedures keep them to a minimum — the chart as a user service Cowork writes, Cowork reading every chart from its log, one physical action per step, no timed waits, held keys and mouse sweeps in place of typing where they do the job, and the machine stating its own state on serial at boot. These carry to every molt ring from 8b on. Item 0 is this record. Earlier the same day — **Ring 8a, the floor, is CLOSED, by the owner's word after test 5 on the HP.** One flash of seed 1, fourteen boots: `good` fetched over the home switch, three shadow boots on the owner's typing and mouse with 0 disagreements, the take, `good` live on the HP's own i8042, Esc back to the seed, then `hang` fetched, taken and live, and the HP stopped and was reset by the Q77's TCO watchdog four times with nobody touching it. The HP does not keep `SECOND_TO_STS`, so `hang` was demoted by the unhealthy path: `S8: recovery i8042 unhealthy`, the seed's driver back. The HP's hang-to-reset-to-POST under 27.4 s; its identity `cpu 000306a9 pci 8086:1e47:04`; no guest defect on the metal. The record is under ring 8a's closure section. Next: ring 8t, trial two. Earlier, 27 September 2026 — **Ring 8a, the floor, is GREEN PENDING THE ORACLE** (item 17): all four automated tests on `./stage8/test-8a.sh` in 43.0 min, with the earlier gates green; seed 1 in the record; the tenth freeze opening by the owner's hand (`503b4e5`); test 5 is the owner's day on the HP by `stage8/HP-8a.md`, which Cowork reviews first. Earlier, 25 September 2026 — **Stage 8, the molt, is OPEN: ring 8a, the floor, opened today.** `stage8/spec.md` was approved by the owner with all fourteen decisions settled (the first slot `i8042`; the GPS rewrite postponed). The policy gate was re-checked by Cowork this morning: the help centre article is unchanged since 16 June 2026, the change is still paused, and `claude -p` still draws from the subscription. The owner applied the TRIALS.md label-width sentence by his own hand as a planned freeze opening, the project's **ninth** (`076d74b`); 7d's test 1 ran once straight after, green (`stage8/out/trials-sentence-test1.log`). `stage8/plan-8a.md` was approved at the plan gate with Cowork's six amendments (A1 the pet at every breath of a long wait; A2 `TCO_TMR` by the PCH datasheet's rule; A3 Esc's own port setup, both scancode sets, W = 3 s; A4 the no-evidence path on the HP; A5 one expectation per twin event; A6 Cowork's review of `loader.asm` before its freeze at item 16b) and all seventeen deviations accepted. **The model note:** CC on **Opus 5.5 at high effort** (spec decision 11). Item 0 is this record. Earlier — **Stage 7 ring 7d, the trials, is CLOSED, by the owner's word on the verdict — and with it every ring of Stage 7's order.** GermOS ran an N-of-1 crossover on its own human and kept the result on its own disk: three sittings on the HP Compaq Elite 8300's notebook, 240 cues, the choices row as text (A) against drawn boxes (B), the verdict computed in the guest by the rule pre-registered before the first click — **A stays** (B's median lower in 8 of 12 pairs, ten needed; misses A 4, B 0). One flash for the whole trial; no guest defect on the metal. The ring: 22 commits before the closure, four plan amendments, four pre-oracle defects fixed in the unfrozen guest (item 13), one freeze opening (item 13b, the project's eighth). **The model note:** CC on Fable 5.1 at medium effort for every item; Cowork on Fable 5.1 at medium for the spec, the plan review and the pre-oracle review, on Opus 5.5 at high effort for the rehearsal, the three sittings and the closure. README says closed. Next: Stage 8, the molt — fresh sessions for Cowork and CC, CC on Opus 5.5 from that kickoff. Earlier — **Stage 7 ring 7d: HP sitting 3 of the trial ran on the HP and PASSED, by the owner's word, and the trial's verdict is A.** A later boot of the same evening; no flash; one terminal, the chart only (`stage7/out/hp-sitting3.log`), no broker, no relay, no second address. The boot read `S7: notebook 184 notes`; `! trial` opened `trial: sitting 3 ABBA BAAB`; eighty cues to `trial: sitting 3 done` with two misses, then `trial: verdict A`. The table — `1 A 10 0 1564`, `2 B 10 0 1340`, `3 B 10 0 1403`, `4 A 10 1 1842`, `5 B 10 0 1542`, `6 A 10 0 1301`, `7 A 10 1 1278`, `8 B 10 0 1533`, `done`, `verdict A` — the same on the HP's panel, on the chart and from `trials.py --serial`. By the pre-registered rule over the three sittings: B's median lower in 8 of 12 pairs, ten needed; misses A 4, B 0; **A stays.** The guest, `trials.py --serial` on the three charts joined, and Cowork's count by hand agree. The verdict boot (25 September 2026, 00:16): `S7: notebook 277 notes`, the row at the prompt in layout A, `! trial` answered `trial concluded`. The arrow on the metal as in sittings 1 and 2. The owner's word on the verdict: passed. Next: the ring's closure — README, the closure record, the owner's push. Earlier — **Stage 7 ring 7d: HP sitting 2 of the trial ran on the HP and PASSED, by the owner's word.** A later boot of the same evening; no flash (the stick as sitting 1 left it); one terminal, the chart only (`stage7/out/hp-sitting2.log`), no broker, no relay, no second address. The boot read `S7: notebook 93 notes` (the owner's two and sitting 1's 91) and `S7: home 1 apps`; `! trial` opened `trial: sitting 2 BAAB ABBA`; eighty cues to `trial: sitting 2 done` with one miss. The table — `1 B 10 0 1784`, `2 A 10 0 1700`, `3 A 10 1 1632`, `4 B 10 0 1610`, `5 A 10 0 1614`, `6 B 10 0 1555`, `7 B 10 0 1432`, `8 A 10 0 1514` — the same on the HP's panel, on the chart and from `trials.py --serial`. Block 1's first cue took 2627 ms: the step ran straight from `! trial` into the clicking, and sitting 1's procedure finding did not recur. The arrow on the metal as in sitting 1. Next: HP sitting 3, by "Next action"; its `done` gives the verdict. Earlier — **Stage 7 ring 7d: HP sitting 1 of the trial ran on the HP Compaq Elite 8300 and PASSED, by the owner's word.** The ring's stick (`stage7/out/stick.img` as built, `BOOTX64.EFI` 45,056 bytes) flashed once by the owner's hand by `stage7/METAL.md` steps 1–3 (`cmp` silent, the partition `vfat`); one terminal, the chart only (`stage7/out/hp-sitting1.log`), no broker, no relay, no second address. The boot read `S7: notebook 2 notes` (the owner's `hello metal` and `Tell me about this machine`, both typed on the 7c days, no `trial` note) and `S7: home 1 apps`; `! trial` opened `trial: sitting 1 ABBA BAAB` with `trial A 1/8` on the strip; eighty cues to `trial: sitting 1 done` with one miss. The table — `1 A 10 0 2390`, `2 B 10 0 1777`, `3 B 10 0 1514`, `4 A 10 0 1780`, `5 B 10 0 1800`, `6 A 10 1 1579`, `7 A 10 0 1535`, `8 B 10 0 1529` — the same on the HP's panel, on the chart and from `trials.py --serial` (`no verdict: 1 done sitting(s), 3 needed`). The arrow on the metal: white on a black cell over a box, the box solid again behind it. One procedure finding, recorded and not fixed: block 1's first cue waited 196.5 s while the owner reported to Cowork after `! trial`; it does not decide pair 1. Next: HP sittings 2 and 3, one a session, by "Next action". Earlier — **Stage 7 ring 7d: test 5's rehearsal ran in the windowed twin, and the owner decided which record is the trial.** Before any click, the owner pre-registered that **the trial is three sittings on the HP's notebook**; the twin's sitting is the protocol rehearsal and is not trial data (spec-7d decision 5, amended the same day: the sitting number counts from each disk's own notebook, so a twin sitting plus two HP sittings would leave no notebook with three, no verdict in the guest and the block orders repeated). The rehearsal, on the item 13 binary (45,056 bytes, the stick rebuilt from the item 14 tree), one terminal, no broker, no relay: nineteen `S7:` lines on a blank disk, `! trial`, eighty cues, `trial: sitting 1 done`, the panel's table equal to `trials.py --disk`; the arrow drawn plain over the boxes (a black cell, the arrow white) and the box refilled solid behind it (the one check the gate cannot make: item 13's fix (1) passes). Its finding is the host's, not the guest's: the QEMU window on Hyprland showed only the left 80 of the 120 columns, so the right third — layout B's `Esc exit` box, columns 90–119 — was off screen; block 8 cue 9 took three misses and 104.7 s. The HP draws to a real 1920x1080 monitor and cannot show it; for later windowed runs, `-display gtk,zoom-to-fit=on`. The owner's words on the layouts: *clicking the blocked squares was a lot easier; in the text row I thought `Tab` and `app` were two separate items, and the same with `Esc` and `exit`.* Next: the three HP sittings, one a session, by "Next action". Earlier — **Stage 7 ring 7d, the trials, OPENED.** The machine moved to Omarchy (mlrig, dual boot) and every stage was regressed on it first: the Stage 0 gate, the 7c gate and the payload table green on the item 21 binary at commit `ebf5794` (the seventh freeze opening, `twin.py`'s xp parser against QEMU 11's eight-digit addresses, by the owner's hand). `stage7/spec-7d.md` was approved by the owner on 22 September 2026 with all seven decisions (the choices row, text against boxes; ten cues a block, eight blocks `ABBA BAAB` / `BAAB ABBA`, three sittings, ten of twelve with misses not worse; the cue is the label word; the verdict on the notebook; sitting 1 in the twin, 2–3 on the HP; Fable 5.1 at medium effort, decided at the kickoff; the GLASS.md section by the owner's hand). `stage7/plan-7d.md` was approved at the plan gate the same day with Cowork's four amendments (A1 blocking: the prefix `trial ` reserved on the notebook, refused at the prompt; A2 `trials.py` recomputes every block's median from its hits and demands equality; A3 the ±30 ms window is the spec's and CC never widens it; A4 the three Stage 7 gates once per commit) and all fourteen deviations accepted — among them the obs fields from `0x2E0` (DISK.md owns `0x2C0`–`0x2D0`), the `no mouse` refusal proven by a probe (q35 cannot drop the PS/2 mouse and keep the keyboard), the verdict over the first three `done` sittings with one sitting a boot. **The model for this ring: Fable 5.1 at medium effort.** Item 0 (this record, the plan's commit) is done; the items follow one commit each, exactly as the plan says: the document, the tool and the four tests red (items 1–6), the synthetic human played against a private binary and every number read from that run (item 7), the freeze of the four files (item 8), the GLASS.md section for the owner's hand (item 9, the session stops there), the guest code (items 10–11), the handover (item 12). Test 5 is Wajira's: one sitting a session, the verdict on the third closes the ring. Earlier — **Stage 7 ring 7c, the metal, is CLOSED, and with it STAGE 7 — METAL — IS CLOSED: Wajira ran test 5 on the HP Compaq Elite 8300 on 18 September 2026, all eight steps, and his word closes the ring and the stage.** With the item 21 binary (40,960 bytes) flashed by his hand: the eighth watched boot — eighteen lines to `S7: keyboard ready` in 0.634 s from `S7: alive` by the probe's stamps, then `? ping` answered over the home switch through the relay (*pong. I hear you, GermOS — the link is up and I'm ready when you are.*, `w 001`), `! install calculator` (`installed calculator`, `g 000/001`, `w 002`); the ninth, with the broker and the relay stopped — `S7: home 1 apps`, the arrow under the mouse with `pt` on the strip, and a click on `! calculator` launching it from the SATA disk with nothing on the wire: 4096, `w 000`, `io 000000/000000`. The disk carried GermOS's table from a blind boot on 15 September (a straight serial cable, nothing read), so every watched boot was the eighteen-line pattern with `S7: notebook N notes`, never the nineteen; the format path is proven by the table the 15th left. **Nine watched boots and seven flashes by the record**; two defects the twin could not show, both in the 82579LM (the read after `CTRL.RST`, item 16; TCTL's `MULR`, item 21), the second found through item 20's serial monitor in one boot. The five photographs of the 18th with their 1600-pixel copies, the serial log with the whole monitor dialogue, the sixth boot's chart, the HP's `lspci` and the 15th's serial test are in `history/`; `stage7/METAL.md` holds the flash block as it was run and the null-modem finding; CLAUDE.md the automounter gotcha; README says closed. The three Stage 7 gates green at the closure on the same binary. **The model note:** CC ran every item of ring 7c on Fable 5.1 at medium effort; Cowork was Fable 5.1 except for a stretch during the item 19 diagnosis (a fall-back to Opus 4.8, then Opus 5 at high effort briefly, then Fable 5.1 again — the DRV_LOAD misstep and its retraction in that stretch, the PCIM2PCI finding under Opus 5, confirmed under Fable); the item 21 diagnosis was CC on Fable 5.1 at medium effort through the monitor in one boot. **Next: the N-of-1 trials ring, per `stage7/spec.md`'s order, a fresh session for Cowork and for CC.** Earlier — **the cause of the transmit timeout is found and fixed (item 21). The HP's seventh watched boot, with the item 20 binary, stopped in the serial monitor after `? ping`, and a CC session drove it through `broker/probe.py`'s socket on `127.0.0.1:9995` in that one boot, no flash between the sixth boot and the fix (`stage7/out/metal.log` lines 128 to 3314; twenty-two resets, `q` never typed). Receive DMA was proven by three ARPs from mlrig (`RDH` 0 to 3); the descriptor and the frame in memory were as `e1k_send` wrote them; every cheap poke, the reset with `PHY_RST`, and seven fresh-reset variables changed nothing. The narrowing: on `t` the transmit FIFO's tail takes 16 bytes and freezes; a descriptor without `EOP` is fetched whole, every descriptor with `EOP` stalls at the hand-off to the transmitter. The cause: the 82579LM's TCTL resets to `0x3003f0f8` and `e1k_attach`'s absolute write of `0x0003f0fa` cleared `MULR` (bit 28) — bit 29 alone stalls, bit 28 alone sends, and TCTL `0x3003f0fa` with TARC1 `0x45000403` read `mon: t tdh 2 tdt 2 sta 0x01`, `TPT` 2, the HP's MAC in mlrig's neighbour table. Item 21: TCTL is written read-modify-write (the `CT` and `COLD` fields masked, `EN`, `PSP`, `CT`, `COLD` and `MULR` ORed in, every other bit at its reset default, as Linux's `e1000_configure_tx`), and TARC1 bit 28 is cleared, Linux's rule with `MULR` set. The twin cannot show the defect — QEMU's 82574L transmits with `MULR` clear (its TCTL reads `0x00000000` before the write and `0x1003f0fa` after, one private probe); the three gates green on the binary (40,960 bytes still); the payload table 1566 cases, 0 wrong; the stick rebuilt, to be flashed once; CLAUDE.md has the gotcha. Next: the owner powers the HP off, flashes, and runs the day again from `stage7/METAL.md` step 5 with probe.py in place of the chart, expecting `pong`.** Earlier — **the HP's sixth watched boot, with the item 19 binary, read `e1k: tdh 0 tdt 1 status 0x00080483 … fwsm 0x6001c04c sta 0x00 tdlen 128 tdbal 0x004ce000 tdbah 0x00000000 expect 0x00000000004ce000` — the ring is configured in the device exactly as written, item 19's read-back passed every register first time, and the lost-write branch is closed: every register we can name reads right and the 82579LM will not fetch one descriptor. Items 16 to 19 each cost the owner a flash and a boot for one question; item 20 ends that loop with the serial monitor: on the transmit timeout, after the `e1k:` line and the named error, the guest no longer halts but answers commands read from COM1 (`r`, `w`, `d`, `t`, `m`, `q`; every answer one `mon:` line), and `broker/probe.py` on mlrig does what the chart does and also listens on `127.0.0.1:9995` for one client, so a CC session asks the questions over the wire, many per boot, no flash between them. One reading the sixth boot's line already gives, for the monitor to check first: `status` bit 10 (PHYRA, PHY reset asserted) is set and bit 9 (LAN_INIT_DONE) clear — the twin's is the reverse — the PHY reset Linux issues and completes on this chip, in the list of what its reset and init do that we do not. No green run reaches the monitor: no `S7:` line changes, every frozen counter holds, `WIRE.md` untouched. Proven in the twin through probe.py's socket; the three gates green on the binary (40,960 bytes still); the payload table 1566 cases, 0 wrong; the stick rebuilt, to be flashed once more. Next: the owner flashes, boots with probe.py in place of the chart, types `? ping`; the monitor answers `mon: ready`; from then on a CC session drives the investigation over the socket with no flash until the fix is known.** Earlier — **Stage 7 ring 7c: the HP's fifth watched boot, with the item 18 binary, read `e1k: tdh 0 tdt 1 … txdctl 0x00400000 tarc0 0x0d800403 … fwsm 0x6001c04c sta 0x00` — item 18's bits are in (the 82579LM reads them back where QEMU's model masks them) and the descriptor is still never fetched. That is upstream of the MAC and the wire; only the descriptor engine's own registers can do it, and TDLEN, TDBAL and TDBAH had never been read back — a TDLEN of 0 in the device gives exactly this line. Linux waits on the ME for this chip exactly (`FLAG2_PCIM2PCI_ARBITER_WA`: the 82579 with FWSM `FW_VALID` set — every register write spins on FWSM bit 24 first, and TDT is read back). Item 19 does both: the `e1k:` line gains `tdlen`, `tdbal`, `tdbah` read from the device beside `expect` (the address we wrote), and every register write goes through `e1k_write` (the bounded wait) with the six ring registers read back and rewritten by `e1k_verify`, a named `ERR:` if one will not hold. QEMU has no ME, so the twin cannot show the defect; three private probes show the read-back, the wait's clear path (`waits 0`), the widened line and the named error; the three gates green on the binary (40,960 bytes still); the stick rebuilt and to be reflashed; the CLAUDE.md gotcha waits for the sixth boot.** Earlier — **the HP's fourth watched boot, with the item 17 binary, read `e1k: tdh 0 tdt 1 … txdctl 0x00000000 tarc0 0x00000403 … fwsm 0x6001c04c sta 0x00` before `ERR: nic transmit timed out` — the 82579LM never fetched the descriptor; item 18 sets the hardware bits Linux's `e1000_initialize_hw_bits_ich8lan` sets before this family transmits (CTRL_EXT 22, TXDCTL0/1 22, TARC0 26 on every e1000e; TARC0 23/24/27 and TARC1 24/26/28/30 on the PCH parts only, reserved on the 82574), in `e1k_attach` after the reset and before TCTL; the twin cannot show the defect, the read-back probe shows the writes land, the three gates are green on the binary (40,960 bytes still), the stick is rebuilt and is to be reflashed; the ME (FWSM FW_VALID) is the next candidate; the CLAUDE.md gotcha waits for the fifth boot.** Earlier — **the HP's second and third watched boots went all the way to the glass; test 5 steps 1 to 4 passed; step 5, `? ping`, stopped at `ERR: nic transmit timed out`; item 17 makes the timeout name the 82579LM's state.** With item 16 the chart (`stage7/out/metal.log`, 19:00:45 and 19:06:58) shows eighteen `S7:` lines in the twin's order on the disk the 15th formatted, `S7: nic 6c:3b:e5:3b:86:45`, `S7: link up`, `S7: glass core 2`, the `i8042:` pair, `S7: keyboard ready` — the glass at 1920x1080 on the monitor, a note (`hello metal`) kept across a power cycle (`S7: notebook 1 notes`); the photographs are `history/2026-09-17-ring7c-hello-metal.jpg` and `history/2026-09-17-ring7c-first-glass-on-metal.jpg`. Then `? ping` at 19:08:43 and, five seconds later, `ERR: nic transmit timed out`: the first frame, the ARP for `10.0.2.4`, sat in its legacy descriptor with `DD` never set — the rings page-aligned and below 4 GB, bus mastering set, the link up. Ring 7b's caveat, exactly: the twin's 82574L cannot show what the PCH's integrated LAN does with a descriptor. **Item 17 is one thing, no fix:** on the timeout path, before the halt, one `e1k:` line naming TDH, TDT, STATUS, CTRL, TCTL, TXDCTL0, TARC0, CTRL_EXT, FWSM, the descriptor's status byte and the ring's address, so the next boot says which half the defect is in (the reading is under item 17 and in `METAL.md` step 7); the numbers choose the fix, one item, next. The binary is 40,960 bytes (the section stepped up one page), the three Stage 7 gates green on it, the stick rebuilt. Earlier — **the HP's first watched boot stopped inside the e1000e's reset; item 16 fixes it, the stick is to be reflashed.** The chart (`stage7/out/metal.log`) showed twelve lines, `S7: alive` through `S7: home 0 apps` — AMI's GOP at 1920x1080 with `edid none`, four cores woken, the AHCI at port 0 on a 250 GB disk formatted with GermOS's table — then nothing: no `ERR:`, no exception, no repeat, the monitor black (expected before the glass core's first frame). Live Ubuntu on the same machine (`stage7/out/hp-lspci.log`) reads the MAC from the 82579LM and brings the link up at 1000 Mbps, so the NIC is healthy and the processor stopped in `e1k_attach` before the nic line. The defect: `CTRL.RST` written and `CTRL` read back in the next instruction; on the PCH's integrated LAN that read hangs the hardware with no fault (Intel's `ich8lan.c` says so and sleeps 20 ms). The twin's 82574L tolerates the read, so no gate could show it and none is written red; the fix is one `pit_wait` of 25 ms after the reset write, the binary 36,864 bytes still, the three Stage 7 gates green on it (item 16). Test 5 stays pending: flash the stick built at item 16 and run the day again by `stage7/METAL.md`. Earlier — **Stage 7 ring 7c, the metal, is GREEN PENDING THE ORACLE.** All four automated tests pass on `./stage7/test-7c.sh` (104 s, five boots plus two rehearsals, mock only): the stick parsed from the host — a protective MBR, both GPT headers and arrays, one EFI System Partition, `BOOTX64.EFI` read back byte for byte; the same binary booted from a copy of the stick over `qemu-xhci` + `usb-storage` with no `esp.img` on SATA at `-smp 8`, `4` and `2` — nineteen and eighteen lines, `S7: disk port 1`, `S7: edid none` with the highest mode on virtio-vga, the `i8042:` pair on every boot, the stick copy's tables unchanged; every stage re-proven in one run of two boots — typing, the note across the reboot, `? ping`, `! test app`, `! install echo` in `wire.py`'s twin, then with nothing on the wire the note back and a click on `! echo` launching it from the home partition; the argv checks, the relay's bind rule, the payload table (1563 cases, 0 wrong) and the flash's words and every device spelling denied to CC. Rings 7a and 7b on the same binary, the three ring 6 gates and Stages 0–5 on their own: all green. **One session, fifteen commits (items 0–14), one per item; tests red before code; no freeze opening; every probe on private copies, none committed.** The guest's changes: the EDID guard and the mode bound, the i8042 cold init, `PxCMD.SUD` under `CAP.SSS`; the tools: `stage7/mkstick.py`, the relay's grace close, `broker/chart.py`; the documents: `stage7/METAL.md`, this one, CLAUDE.md, README. Test 5 is Wajira's, on the HP, by `stage7/METAL.md` — the three commands under "Next action"; his word closes the ring and Stage 7. **The model note, for the owner's comparison:** ring 7c was implemented on **Fable 5.1 at medium effort**, the owner's decision in the spec; at the plan gate Cowork needed three required amendments (A1–A3) and four cheap ones (A4–A7), all adopted; one expectation corrected once during Part 1 (a click on a launch item types the launch line — ring 6c's own rule, now a gotcha); zero freeze openings; the pre-oracle review pending. Earlier — **Stage 7 ring 7c, the metal, opened.** `stage7/plan-7c.md` was approved at the plan gate on 15 September 2026 with Cowork's seven amendments, A1–A3 required and A4–A7 adopted as cheap (A1 `chart.py` opens the port non-blocking, sets termios with `CLOCAL`, then clears the flag — a three-wire null-modem cable never asserts DCD; A2 under `CAP.SSS` a port's `DET 0` right after `SUD` is given a second to leave 0 before it is passed, then ten seconds to reach 3 or a named halt; A3 the flash procedure checks for exactly one USB line by SIZE and MODEL, unmounts the stick's partitions with `udisksctl` before the write and powers it off after `sync`; A4 the bodyguard's widened `/dev` mention stops at a word boundary so `/devel` and `/devices` stay allowed; A5 the mode-loop bound mirrors every mode-only limit `surf_describe` enforces, `SURF_ROWS_MAX` included; A6 the `i8042:` pair is asserted on all three of test 2's boots; A7 METAL.md says what `nmcli` does to the connection and how to undo it) and all eleven deviations accepted. **The model for this ring: Fable 5.1 at medium effort, the owner's decision in the spec.** Item 0 (this record, the plan's commit) is done; the items follow one commit each, exactly as the plan says — the builder and the acceptance machinery first (the stick, the three boots over USB, every stage re-proven in the twin of the HP in one scripted run, the bodyguard extended), the freeze, then the EDID guard, the i8042 cold init, `PxCMD.SUD`, the relay's grace close, `chart.py`, `METAL.md`. Test 5 is Wajira's, on the HP; his word closes the ring and the stage. Earlier — **Stage 7 ring 7b, the wire, is CLOSED.** Wajira ran test 5 on 15 September 2026 with the real broker behind the relay on `127.0.0.1:9997`: a blank 64 MB disk; nineteen `S7:` lines in order with `S7: nic 6c:3b:e5:3b:86:45` then `S7: link up`; `? ping` answered over the e1000e through the relay ("pong. I hear you, GermOS. The link is up and I am ready for your next line."); `! make me a clock` written by the real backend, rehearsed in the wire twin, and running in its panel with its own choices row (`h 12/24 hour`, `d date on/off`, `Esc exit`, `Tab prompt`). The strip: `w 002 002941`, `g 000/001`, `err 000`, `io 002040/000676`. *"Save the screenshot and test 5 is passed."* — the owner's words. The screenshot is `history/2026-09-15-ring7b-clock-e1000e.png`. Cowork's pre-oracle review of the driver and the relay found zero defects. **The model note, for the owner's comparison:** ring 7b was implemented on **Fable 5.1 at high effort**, one session, thirteen commits plus 10b, one per item; at the plan gate Cowork needed no blocking amendment (A1–A5 adopted); one freeze opening, in the frozen checker, of ring 6b item 10b's class (a count written from arithmetic, not from a run); zero review defects; zero oracle defects. Next: **ring 7c, the metal**, a fresh session for Cowork and for CC, medium effort by the spec. Earlier — **ring 7b was green pending the oracle.** All four automated tests pass on `./stage7/test-7b.sh` (314 s, ten boots plus two rehearsals, mock only): nineteen `S7:` lines on an e1000e carrying the HP's MAC with `S7: link up`, eighteen on the same disk, the e1000e preferred beside a virtio-net, the link taken down through the monitor ending in `ERR: nic link did not come up within 10 s` and a halt; `? ping`, a note and `? hello` through `broker/relay.py` on 9997 to the mock at `-smp 2`, `4` and `8` with the relay's log agreeing with the record and the strip's wire counters; the cage — both argv checks, the relay's bind rule on the host, a mock-down run ending in a console message, `! test app` and `! install echo` through the relay with nineteen-line rehearsal logs in the twin, the launch with nothing on the wire. Ring 7a's gate on the same binary and the three ring 6 gates and Stages 0–5 on their own: all green. **One session, twelve commits plus one (item 10b, the project's sixth freeze opening, by the owner's hand: a count in the frozen checker written from arithmetic — ring 6b item 10b's class again); tests red before code; the driver worked on the first probe.** Test 5 is Wajira's, the three commands under "Next action". **The model note, for the owner's comparison:** ring 7b was implemented on **Fable 5.1 at high effort**; at the plan gate Cowork needed no blocking amendment (A1–A5 adopted). Earlier — **Stage 7 ring 7b opened.** `stage7/plan-7b.md` was approved at the plan gate on 15 September 2026 with Cowork's five amendments, none blocking (A1 the relay sets `SO_REUSEADDR` and flushes each log line as the connection ends; A2 its teardown never raises, and a RST or a FIN on a refused broker are both "no answer" by UMBILICAL.md; A3 the relay's bind battery is three fixed addresses, no hostname lookup; A4 `e1k_poll` honours a received descriptor's errors byte; A5 the ports as this ring settled them carried to ring 7c — the relay on 9997 in the twin, `python3 broker/relay.py` with no flags on the HP's day, the spec's 7c command corrected at the 7c gate) and all eleven deviations accepted. **The model for this ring: Fable 5.1 at high effort, the owner's decision in the spec.** Item 0 (this record, the plan's commit) is done; the items follow one commit each, exactly as the plan says. Earlier — **Stage 7 ring 7a, the disk, is CLOSED.** Wajira ran test 5 with the real broker on 9 September 2026: `S7: gpt written` then `S7: disk port 1 131072 notes 2048 home 34816` on a 64 MB SATA disk; `? Hi there.` answered over the wire (`w 001 005531`); `! install calculator` built by the real backend and rehearsed in the twin on a SATA disk of its own; a sum; then a reboot with no broker — `S7: home 2 apps` (echo from the gate's disk beside it), `! calculator` launched from the home partition with `w 000` and `io 000000/000000`. *Everything ran as expected.* The screenshots are `history/2026-09-09-ring7a-hi-there-sata.png` and `history/2026-09-09-ring7a-calculator-from-sata.png`. One trap found at the oracle, not a defect: `truncate -s 64M` on a file already 64 MB changes nothing, so the run started on the gate's disk (its note `last`, its echo) — remove the file first for a blank disk; the command below says so. Cowork's pre-oracle review of the AHCI driver, the selection rule and the GPT code found zero defects. **The model note, for the owner's comparison:** ring 7a was implemented on **Fable 5.1 at high effort**, one session, twelve commits, one per item; at the plan gate Cowork needed one blocking amendment (A1, the port selection rule — the twin's boot image sits on AHCI port 0 and the plan would have formatted it) and three others; no freeze opening; zero review defects; zero oracle defects. Next: **ring 7b, the wire** (e1000e, the relay), a fresh session for Cowork and for CC. Earlier — **Stage 7 — Metal — is OPEN, and ring
7a, the disk, opened today.** `stage7/spec.md` was approved by the owner
on 9 September 2026 (all recommendations taken, decision 5 amended: the
HP plugs into the home switch; the policy gate re-checked the same day —
`claude -p` still draws from the subscription, no API keys). Patient one
is the **HP Compaq Elite 8300 SFF** (Q77 AHCI SATA, Intel 82579LM, PS/2
keyboard and mouse, COM A, four cores), not the Lenovo the earlier notes
named. Three rings: **7a the disk** (AHCI, one SATA disk with a GPT the
guest writes, notes and home as two partitions, the frozen formats moved
inside unchanged), **7b the wire** (e1000e, the cage becoming the home
switch through a relay), **7c the metal** (the stick, the flash by the
owner's hand, every stage re-proven on the HP). Ring 7a's plan,
`stage7/plan-7a.md`, was approved at the plan gate with Cowork's four
amendments (A1 the port-selection rule — a GermOS table wins, else a blank
disk is formatted, else a named error and nothing is ever formatted over;
A2 the twin's SATA read never raises; A3 `broker/metal.py` freezes at item
10, after nine of nine through it; A4 the BSP's APIC mode recorded at item
1) and all eleven deviations accepted bar the two the amendments withdraw.
**The model for this ring: Fable 5.1 at high effort, the owner's decision.**
**Ring 7a is green pending the oracle**: all four automated tests pass at
`-smp 2`, `4` and `8` (item 10, the same day) — a blank SATA disk
partitioned by the guest with the table byte-identical to DISK.md's, two
notes across a reboot on the notes partition, ring 6b's whole store test
on the home partition with the twin formatting a SATA disk of its own; the
foreign table refused by name and never written; Stages 0–5 and the three
ring 6 gates green on their own binaries. One session, one commit per
item, tests red before code, no freeze opening; two defects of the first
driver draft fixed before any probe passed (an address table in data, a
clobbered loop register); the plan's A1 wording of "esp.img byte-identical"
replaced by what the guest must never do to it, once OVMF's NvVars write
was measured at item 1. Test 5 is Wajira's, the two commands under "Next
action". Earlier — **Stage 6 ring 6c, the pointer, is
CLOSED — and with it STAGE 6.** Wajira ran test 5 twice with the real
broker. The first run, on the morning of 5 September: the arrow appeared
on the first move, `! calculator` launched from disk by a click, clicks
in its panel did nothing, `= result`, `c clear`, `Tab prompt`, `Tab app`
and `Esc exit` did what their keys do — and he found the defect the gate
had missed: the arrow left fragments along the bottom edge at 1080
(fixed as item 12c, below). The second run, after the fix: every edge and
corner swept clean, `! calculator` launched by a click at the very bottom
of the window, the sums done, the arrow parked in the bottom-right
corner. *All above steps were functional as expected.* The screenshots
are `history/2026-09-05-ring6c-hello-cursor.png` (the first run — "Hello
cursor. This GUI is unfamiliar. :-)") and
`history/2026-09-05-ring6c-corner-calculator.png` (the second — the arrow
in the corner, `pk 9999` saturated, "Hello intuitive GUI!"). All four
automated tests pass at `-smp 2` and `-smp 8`: the PS/2 mouse on the i8042 —
configured for the first time — speaks in three-byte packets into a ring of
its own; the glass core draws a one-cell arrow last in every frame from the
position the interrupt handler keeps in the obs page; pointer input-to-photon
is `pt` on the strip, beside the packets and the clicks, from the first
packet on (3–16 ms measured, one frame slot at worst); a click on a
choices-row item does what its key does — `? ask` types the marker, `!
echo` launches from disk on an empty line, an app's key reaches it, Esc and
Tab move as the keys do; the point app's `point(row, col, button)` draws the
cell it was given, and every four-callback app is clicked on harmlessly.
Stages 0–5, ring 6a and ring 6b stay green on the same binary: a mouse that
never moves leaves the machine ring 6a's to the line and to the pixel.
**Test 5 was Wajira's, and his word closed the ring and the stage on
5 September 2026.** **The model note, for the owner's comparison:** ring 6c was
implemented on **Fable 5.1 at high effort**, one session, one commit per
item, tests red before code; at the plan gate Cowork needed no blocking
change to the design (A1 an expected-green line, A2 no count a literal, A3
the empty-line rule), and the freeze was opened once for a misordered read
in the checker's own screen D (item 11b); Cowork's pre-oracle review found one defect — loop state in R12–R15 across a call into grown code — fixed as item 12b; the oracle's first run found the arrow leaving ghosts along the bottom edge (a mode is not a whole number of cells) — fixed as item 12c with the pointer clamped to the console's cells and row R−1 made the choices row's margin, the fifth freeze opening by the owner's hand. The ring's section is below the
ring 6b build. Earlier — **Stage 6 ring 6b, the store of
plans, is CLOSED.** Wajira ran test 5 with the real broker:
`! install calculator` was built by the real backend from
`plans/calculator.md` and rehearsed against the plan's five tests in one
72-second exchange (`w 001 071881` on the strip); `installed calculator`
with the plan's choices `= result` and `c clear` on the row; a sum done.
Then a reboot with no broker: `S6: home 2 apps` (the gate's echo fixture
shares `stage6/out/home.img` with the oracle), `! calculator` on the
choices row, and the launch from disk with `wire_conns` 0 and `io
000000/000000`. *It worked as expected.* The screenshots are
`history/2026-09-03-ring6b-calculator-installed.png` and
`history/2026-09-03-ring6b-calculator-offline-launch.png`. All four
automated tests pass at `-smp 2` and `-smp 8`: an app is a plan file,
grown at install time, rehearsed in the twin against the plan's own
five-verb tests on top of the nine safety criteria, kept on a second
disk with its SHA-256, launched after a reboot with no broker and
nothing on the wire, undone one step. **The model note, for the owner's
comparison:** ring 6b was implemented on **Fable 5.1 at medium effort**
and passed its oracle first time; at the plan gate Cowork needed one
blocking amendment (fixtures must draw at `init` or the frozen twin's
criterion 5 fails them), and the freeze was opened once for a miscount
in the plan's own test arithmetic (item 10b). One session, one commit per
item, tests red before code. Ring 6b's section is below the ring 6a
build. Earlier — **Stage 6 ring 6a, the glass, is CLOSED.** Wajira ran test 5 with the real broker: `! make me a clock`
was grown by Claude against the ABI 2 contract, rehearsed in the twin,
and ticked in its own panel while he typed a note beside it and the
strip's numbers moved — with two choices Claude declared unasked on the
choices row. *He is happy.* The screenshot is
`history/2026-09-02-ring6a-clock-in-panel.png`. All four automated tests
pass at `-smp 2` and `-smp 8`: the screen has one owner (a glass core on the first AP
compositing four surfaces at sixty frames a second), the machine tells
the truth about itself (an obs page every counter is written into by the
thing doing the work, and an obs strip the harness reads back cell by
cell against that page), and the conversation stays alive while an app
runs (ABI 2: four callbacks stepped by the main loop, Tab moving the keys
between the app and the prompt). Built in one session on Fable 5.1 at
high effort from the plan approved with Cowork's four amendments, one
commit per item, tests red before code; the one stop (a two-line defect
in the frozen twin, found at the first app rehearsal) was fixed by the
owner's own hand as item 12b. Test 5 is Wajira's: `! make me a clock` in
its own panel, a note typed beside it, the strip moving, Esc. The spec
was approved on 1 September with all eight recommendations taken
(Fable 5.1 at high effort implements; the screen mode is the display's
EDID-preferred one, 1440x1440 in the twin); the policy gate was
re-checked then: `claude -p` still draws from the subscription, no API
keys, next re-check at Stage 7. Earlier — **Stage 5 CLOSED.** Wajira ran test 5
with the real broker: he typed `! make me a clock` at the GermOS prompt;
Claude wrote NASM for a flat binary against GERMLINE.md's ABI; the broker
assembled it, **rehearsed it in a headless boot of the same image**, cached
it in the germline and delivered it — and a clock ticked on the machine's
own screen, with the date and a `GermOS clock - Esc to exit` line nobody
asked for. *"Yay!"* — the done-when, in the owner's word. The loop the
project exists for is closed: English in, machine code back, verified in
the twin, then run. Both oracle screenshots are in `history/`. Cowork's
Stage 5 review preceded the run — the full guest diff, the two frozen
broker files and the unfrozen backend — and found zero defects. Built on
Fable 5 at high effort, one commit per numbered item, the plan gate
holding until the owner approved; the automated gate spoke only to the
mock and spent no token; the one stop on the way (QEMU's image lock in
the frozen rehearsal) was fixed by the owner's own hand as item 8b.
Earlier the same day: Stage 4 closed at its test 5, and the project was
named **GermOS** and **published** (`github.com/IndyWH/germos`, MIT). Six
stage closures in two days from an empty folder. Next: the Stage 6 spec.

---

## Where we are

| | |
|---|---|
| Stage | **8 — The molt — ring 8t, trial two, opened 28 September 2026**, inserted after ring 8a and before ring 8b (`trials/spec-trial2.md`, approved 27 September 2026 at `beef2da`, with Amendment 1 of 28 September 2026; `trials/plan-8t.md` approved at the plan gate with Cowork's five amendments A1–A5). Earlier — **ring 8a, the floor, opened 25 September 2026, CLOSED 28 September 2026.** `stage8/spec.md` approved by the owner with all fourteen decisions settled (rings 8a–8g; the first slot `i8042`); `stage8/plan-8a.md` approved at the plan gate with Cowork's six amendments (A1–A6) and all seventeen deviations accepted. Stage 7 closed with ring 7d on 25 September 2026 (rings 7a–7d closed 9, 15, 18 and 25 September); Stages 0–6 closed |
| Status | **Ring 8t: items 0–11 done** (29 September 2026). The GLASS.md section is in by the owner's hand (`877fd53`). Item 11 put the sitting into `stage8/stage8.asm` (61,440 bytes): tests 1 and 4 green, the 8a gate with 7d, 7c, 7b and 7a green inside test 4; tests 2 and 3 red only on part B's checks — the offer, an empty Enter, the boot line, the replay rule, a trial-two verdict read at boot (52.7 min, the run of 08:57). Earlier: the acceptance machinery FROZEN at item 9. **Tests 1 and 4 green** (test 4 with ring 8a's whole gate inside it, 7d, 7c, 7b and 7a within that); **tests 2 and 3 red by design on seed 1's missing `trial2:` lines** (green on item 8's private draft). The gate whole: 45.8 min (`trials/out/gate-8t.log`, the run of 01:05). Item 9 froze the four files. Item 8 was the probe. Item 7 wrote `checktrials2.py --cage` and test 4. Item 6 wrote `checktrials2.py --sittings` (test 3). Item 5 wrote `checktrials2.py --rows` (test 2). Item 4 wrote `trials/test-trial2.sh` and `trials/checktrials2.py --document`; item 3 `trials/trials2.py`; item 2 `trials/TRIALS2.md`. Item 1 measured the host's read mid-boot, FLUSH CACHE EXT on the twin, the walks at 0, 355 and 1,250 notes, the hook on `trials/out/`, and the HP's history as notes with every chart checkpoint met (section below). Every earlier gate green on its own binary as ring 8a closed; **Next: item 12, Amendment 1 and the replay rule — tests 2 and 3 green.** Earlier: **Ring 8a: CLOSED 28 September 2026, by the owner's word — test 5 on the HP passed** (the day and its findings under ring 8a's closure section). **Next: ring 8t, trial two, by `trials/spec-trial2.md`.** Earlier: **Ring 8a: GREEN PENDING THE ORACLE — items 0–17 done (27 September 2026).** Item 17: seed 1 recorded (`fc64a07`, 57,344 bytes, `9e81c7b5d24ac363…`; `parts.py --seed` exit 0), `stage8/HP-8a.md` written, `CLAUDE.md` and `README.md` brought up to ring 8a; the gate whole ALL FOUR TESTS GREEN (43.0 min, alone, on `503b4e5` with seed 1 in the record); the tenth freeze opening by the owner's hand (`503b4e5`, `parts.py`'s `current_seed` check); Stages 0–5 and the three ring 6 gates green on their own binaries. **Next: test 5, the owner's day on the HP by `stage8/HP-8a.md`; his word closes the ring.** Earlier: **item 16b (27 September 2026): `stage8/loader.asm` FROZEN, and the ring's gate ALL FOUR TESTS GREEN on it** (`./stage8/test-8a.sh`, 42.9 min; the payload table 2064 cases, 0 wrong; ring 7d's gate with 7c, 7b and 7a green inside test 4). Before it, Cowork's A6 review of the loader: no defects; one change by the owner's decision at the review (the TCO found and halted before the known answer), as a further item 16 commit with the gate re-run. Earlier: item 16 (27 September 2026): the watchdog, the pet, the health mark, the recovery rules, Esc and the blame line**, with Cowork's four points from its review of the draft and item 15 built in (RCBA off → `tco locked`; the owner's decision: the timer halted at step 2 on every boot with a molt note; `F0 01` not an Esc make; `dma_pages` refused before the sum). 57,344 bytes. The gate whole: **tests 1–3 PASS** (test 3 in 851.9 s), test 4 red on its nine `loader.asm` refusals alone with the stage7 gates green inside it; ten private probes ok, among them hang and fault at `-smp 2` and `8`. The question item 16 left open (a boot whose known answer fails never reached step 2's halt) was answered at the A6 review. Earlier: **item 15 (27 September 2026): the slot, ABI 3, the part frame, the home names, the notes, the words and shadow**, the draft rebased onto item 14's layout with Cowork's three placement points; 57,344 bytes. The private probe: good shadowed to its threshold with 0 disagreements, taken, live at `-smp 2`, `4` and `8`, `parts.py --disk` agreeing (218.4 s). The gate whole: tests 1 and 2 PASS (test 2 in 425.8 s); test 3 red by design at G2's awaited health mark, L already green; test 4 red on its nine `loader.asm` refusals alone, the stage7 gates green inside it. Earlier: **item 14 (27 September 2026): the loader moved into `stage8/loader.asm`, `.text` read-only with CR0.WP on every core**; a write into `.text` from the main loop and from the glass core each faults at its own store; `checkmolt.py --document` exit 0 and test 2 green on this binary (425.7 s). Earlier: **items 0–13 done; the acceptance machinery FROZEN at item 13 (27 September 2026)**, after the owner's amendment to PARTS.md on Cowork's review of item 12 (`c4a6111`). Tests 1 and 2 PASS; test 3 red by design until item 16 (green on the private draft, 851.8 s); test 4 red on its nine `loader.asm` refusals alone until 16b, the payload table 2046 cases, 0 wrong. Earlier: **tests 1 and 2 PASS** (item 9, 27 September 2026: `stage8/test-8a.sh` with the log, `checkmolt.py --document` and `--seven`; test 2 on ring 7d's binary through D3's seams, 426 s, no `S8:`, `part:` or `molt:` line in twelve captures; tests 3 and 4 not yet written; items 0 to 8: the plan's commit; Stage 8 opened on ring 7d's source, the build byte-identical to ring 7d's, and D3's seams proven by a run - every 7c and 7d entry point returns 0 on the stage8 build with nothing escaping to `stage7/out/`; item 2: D1 measured - the ICH9 TCO resets the twin at 2 × `TCO_TMR` × 0.6 s as the 7-series datasheet says, `TCO_TMR` 25 for 30 s, `SECOND_TO_STS` survives the reset, so the one twin path is the watchdog's; item 3: D2 - `-icount shift=0` repeats exactly at `-smp 4`, not quite at 2, `auto` never; D4 - `qemu_argv` passes `check_argv_7c` unchanged, Esc arrives as `0x01`/`0x81` with no repeats and the checker's hold is 5,000 ms, keys match the byte rule, packets equal moves at any pace from 1 ms, the identity `cpu 000306a9 pci 8086:2918:02`; the hook allows every ring 8a shape, and allows removing a whole directory of frozen files, a finding for the owner, whose decision of 25 September 2026 adds a directory rule at item 13; item 4: `stage8/PARTS.md` written, its worked examples reproduced from its own Python block, 0 wrong, then Cowork's amendment on what ABI 3's services refuse; item 5: the five fixtures, each header valid by PARTS.md, and their byte entries matching the generic event for event on the host; item 6: `stage8/SEED.md` and `stage8/seed-record.md`, seed 0 `bbf80635…b28cd5` from a clean rebuild of `bd613b3`, the worked example reproduced from SEED.md's own block, 0 wrong; item 7: `stage8/parts.py`, both documents' blocks exec'd and checked against their prose, PARTS.md's fixtures section filled from the `.bin`s, `--example` green and 27 one-change copies of the documents refused, `--disk` and `--serial` printing the same table, `--seed` rebuilding seed 0 and naming the build seed 0; item 8: `broker/molt.py`, unfrozen, serving each fixture's frame as `parts.fixture_frame` byte for byte, refusing other slots and malformed bodies, `wire.Wire`'s answers to everything else, and the record carrying the identity, `parts.molt_key` and the frame, 73 checks with no boot). Every earlier gate green on its own binary, as ring 7d closed. **Nine freeze openings on the record** (by the owner's count of 28 September 2026) — the ninth the TRIALS.md label-width sentence, by the owner's hand, 25 September 2026 (`076d74b`), 7d's test 1 green once after it. Earlier — **Ring 7d: all four automated tests PASS** (`./stage7/test-7d.sh`, 21 min, the log's item 11 run; items 0–13 committed, one per item, item 13 the four fixes of Cowork's pre-oracle review, the section appended by the owner's hand at item 9) — **test 5: the rehearsal ran in the windowed twin on 24 September 2026 (not trial data, by the owner's pre-registration); the trial is three sittings on the HP's notebook, one a session, the verdict on the third closes the ring. HP sittings 1, 2 and 3 PASSED on 24 September 2026 (the owner's word on each; one, one and two misses); the verdict A — B's median lower in 8 of 12 pairs, ten needed; misses A 4, B 0 — the owner's word on it 25 September 2026; the verdict boot answered `trial concluded`. Ring 7d CLOSED 25 September 2026, by the owner's word.** Ring 7c: all five tests PASS (18 September). Rings 7b and 7a: all five PASS. Stages 0–5 and the three ring 6 gates green on their own binaries |
| Repo | `/home/indy/Work/germos` (branch `main`) on Omarchy since 22 September 2026 (`/home/indy/Projects/ai-os` was the Ubuntu path) — **public since 1 September 2026 at `github.com/IndyWH/germos`, MIT licence** (commit `beef02e`) |
| Machine | mlrig, **Omarchy (Arch Linux, kernel 7.2.5-3-omarchy), dual boot on the Crucial P2** since 22 September 2026 (native Ubuntu 26.04 before), 32 logical CPUs |
| Toolchain | NASM 3.02, QEMU 11.1.1, Python 3.14.7, OVMF at `/usr/share/ovmf/OVMF.fd`, mtools, OpenBSD netcat, xxd, the `claude` CLI **2.1.283** (`claude --version` at ring 8t's item 0; 2.1.282 at ring 8a's planning) — ring 8t needs no new package; every `stage0..8/out/` and `trials/out/` exists (the fresh-clone gotcha; the ring 8a gate makes its own) |
| Model | **Ring 8t: CC on Opus 5.5 at high effort** — spec decision 11 of `trials/spec-trial2.md`, recorded at item 0 (28 September 2026); Cowork on Opus 5.5 at high effort for the spec, Amendment 1 and the plan review. Earlier — **Ring 8a: Opus 5.5 at high effort** — the owner's decision, spec decision 11 (25 September 2026), recorded at item 0; Cowork on Opus 5.5 at high effort for the spec, the plan review, the reviews, test 5 on the HP and the closure. Earlier — **Ring 7d: Fable 5.1 at medium effort** — the owner's decision at the kickoff, 22 September 2026, recorded at item 0; Cowork on Fable 5.1 at medium effort for the spec, the plan review and the pre-oracle review; **Cowork on Opus 5.5 at high effort for the oracle sittings and the closure** (from 24 September 2026, the owner's choice; CC's implementer moves to Opus 5.5 from the next ring's kickoff, not mid-ring). For comparison: ring 7c Fable 5.1 at medium (three required amendments at its gate, zero freeze openings, two metal-only defects found on the HP); ring 7b Fable 5.1 at high (one freeze opening); ring 7a Fable 5.1 at high; ring 6c Fable at high; ring 6b Fable at medium; Stages 2–6a Fable at high; Stages 0–1 Opus at high |

## The project in three lines

An operating system grown on each machine rather than shipped to it. A small
frozen core boots the machine and connects it to Claude, which writes everything
else as machine code fitted to that exact hardware. Nothing touches real
hardware until it has survived a rehearsal in the twin (QEMU).

---

## Stages closed

### Stage 0 — First pixel · closed 31 August 2026

Spectrum loading stripes and two byte-exact serial lines from a 512-byte BIOS
boot sector, 211 of 510 bytes used. `./stage0/test.sh` is a standing regression
check and is still green.

### Stage 1 — Owning the processor · closed 31 August 2026

One hand-written PE32+ UEFI application: serial first, GOP at the highest 32-bit
mode, ExitBootServices, our own GDT and 4 GB identity map, the ACPI MADT read for
the core count, every core woken with INIT-SIPI-SIPI off a sub-1MB trampoline,
and each core painting its own band. **The picture is the core count.**

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed at `EFI/BOOT/BOOTX64.EFI` | **PASS** |
| 2 | Serial — seven `S1:` lines in order, found = woken = 8 | **PASS** |
| 3 | Scaling — the same at `-smp 2` and `-smp 8` | **PASS** |
| 4 | Pixels — 8 equal solid bands at the resolution the log claimed | **PASS** |
| 5 | **Oracle — Wajira's eyeball** | **PASS — confirmed 31 August 2026** |
| — | **`-smp 32` mirror run** | **PASS — confirmed 31 August 2026** |

On this machine the chosen mode is **2048x2048 at 0x80000000** — measured, never
baked in; the pixel test reads the resolution out of the guest's own log from the
same run. Tests 1–4 were committed **red** before any of `stage1.asm` existed and
went green exactly where the plan predicted: test 1 at item 6, tests 2 and 3 at
item 12, test 4 at item 13.

Run the gate with `./stage1/test.sh` (about four minutes — each halted guest
burns its 60-second timeout, which is the expected outcome, not a fault).

**Caveats carried forward, still true:**

- **The x2APIC path is unproven.** OVMF leaves the BSP in xAPIC mode here
  (`apic_x2 = 0`, MMIO at `0xFEE00000`), so nothing has ever executed it.
- **The trampoline fallback is unproven.** The preferred address `0x8000` is
  granted every time, so the below-1MB memory-map scan has never been taken.
- **One machine, one firmware.** QEMU q35 with OVMF. No claim about real
  hardware; that is Stage 7.

---

## Stage 2 — Senses · closed 1 September 2026

**Goal (foundation §7):** keyboard input and a text console on the framebuffer;
the serial debug channel becomes permanent. Proves the machine is interactive.

Built on Stage 1's body, per the approved spec and plan (both committed, plus
plan amendment A1 — the sti-shadow hlt idiom): an IDT whose 32 exception stubs
print `ERR: exception <vector> at 0x<rip>` and halt (proven byte-precise with a
ud2 probe against the nasm listing); a text console — font8x8 scaled 2x into
16x16 cells, dark rgb(16,16,24) ground, light rgb(224,224,224) glyphs, the boot
log replayed from a serial mirror buffer, static block cursor, wrap, backspace,
shadow-buffer scrolling, the framebuffer never read; and an interrupt-driven
PS/2 keyboard — PIC remapped to 0x20/0x28 with only IRQ1 unmasked, a
scancode ring between the handler and the main loop, set-1 unshifted US
translation, E0 pairs and break codes swallowed. The screen has one owner: the
handler only buffers; the BSP main loop draws. On this machine the console is
**128x128 cells** on the 2048x2048 mode — measured, never baked in.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial — nine `S2:` lines in order, found = woken = smp, console = W/16 x H/16 | **PASS** |
| 3 | Typing — monitor `sendkey` hello+Enter; echo exactly `hello` CRLF, at `-smp 2` and `-smp 8` | **PASS** |
| 4 | Pixels — `> hello` pixel-correct per the shared font, prompt+cursor below, only the two console colours on screen | **PASS** |
| 5 | **Oracle — Wajira's eyeball** | **PASS — confirmed 1 September 2026, just after midnight: typed at the prompt, echo and picture both confirmed** |

Tests 1–4 were committed **red** before any of `stage2.asm` existed and went
green exactly where the plan predicted: test 1 at item 7, tests 2–4 at item 10.
The shared font is `stage2/font8x8.bin` (public-domain font8x8, provenance and
hashes in `stage2/FONT.md` and pinned in `plan.md`), frozen alongside the tests
because the checker renders its expectations from it.

**The owner's model experiment, recorded for the record.** Stage 2 was
implemented on Fable 5 at high effort rather than on Opus, as an experiment by
the owner. Cowork's review found zero defects — the same result as Opus's
Stages 0 and 1. The standing rule from the foundation remains Opus at high
effort for implementation; Fable is to be considered for Stages 4 and 8, and
that is an owner-reserved decision. This Stage 3 session also runs on Fable 5,
by the owner's choice at launch.

**Caveats carried forward:**

- **Stage 1's stand:** the x2APIC path and the trampoline fallback remain
  unproven; one machine, one firmware (QEMU q35 + OVMF).
- **The i8042 is not reconfigured** — QEMU's controller as OVMF leaves it
  delivers set-1 codes and interrupts (proven by the echo working). Cold
  controller init is a Stage 7 debt.
- **Unshifted only.** Shift, symbols-over-digits, and capitals are a later ring.
- **A parked AP that faults prints over serial** — a deliberate one-owner
  breach for a machine that is already lost (plan decision 9).

---

## Stage 3 — Memory of its own · closed 1 September 2026

**Goal (foundation §7):** block storage (virtio first) and a simple filesystem.
Proves the OS keeps what it grows. **Hard safety rule:** storage code touches
only QEMU disk images until Stage 7, never any disk holding real data.

Built on Stage 2's body, per the approved spec and plan (thirteen items, one
commit each, no amendments needed). What grew:

- **The storage bodyguard** (item 1, before any storage code): the hook denies
  every Bash call that mentions a `/dev` path other than the harmless sources
  and sinks, the words mount/umount/losetup/mkfs and the partitioning and
  wiping tools, `sudo`, a QEMU `-drive file=` outside a repo `out/` directory,
  the disk shorthands (`-hda`, `-cdrom`, `-blockdev`, `-pflash`, …), and
  `qemu-img` on any path outside `out/`. The payload table is committed
  (`.claude/hooks/payloads.py`, 300 payloads, 0 wrong) so a reviewer can re-run
  it. It bit at once — proven with a harmless `ls` of a SATA device node that
  the hook refused — and it also bit *me* once on a false deny (a heredoc that
  mentioned a frozen filename near a write call), costing a reworded command,
  as designed.
- **The disk** (items 9–11): PCI bus 0 enumerated through `0xCF8`/`0xCFC`
  (OVMF leaves ECAM off); the virtio-blk device found at bus 0 device 3
  (`1af4:1001`, transitional, with modern capabilities); its capability region
  read from the BAR the capability names and **mapped wherever the firmware
  put it** — on this machine `0xC000000000`, above the 4 GB identity map *and*
  above the first PML4 entry — by a generic uncached 2 MB mapper drawing on a
  spare page pool (two pages used: a new PDPT and PD under a fresh PML4[1]);
  command register set to MEMORY | BUS MASTER | INTX_DISABLE; modern
  negotiation with VERSION_1 required and alone accepted, FEATURES_OK read
  back; capacity read as two 32-bit halves; one virtqueue, three-descriptor
  chains, polled completion bounded at five seconds. `S3: disk 32768 sectors`
  on the harness's 16 MB image. Every failure path is a named `ERR:` line.
- **The notebook** (item 12): `stage3/NOTEBOOK.md` in code — header at sector
  0, one note per sector from sector 1, the journal ending at the first
  invalid record; a blank disk formatted (header plus a zeroed sector 1); a
  recognised one scanned and counted, its notes drawn console-only above the
  first prompt; every non-empty line written through on Enter before the new
  prompt appears.

The eleven serial lines: Stage 2's nine as `S3:` with `S3: disk <N> sectors`
and `S3: notebook formatted` / `S3: notebook <N> notes` between console and
keyboard, so `keyboard ready` stays the last line before `sti` and the echo
contract after it stays exactly Stage 2's.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial, first boot — eleven `S3:` lines on a fresh disk, found = woken = 8, sector count = image size / 512, notebook formatted | **PASS** |
| 3 | Persistence — type `remember me`, quit; image parsed from the host holds exactly that note byte-exact; same image rebooted logs `notebook 1 notes`, nothing on the wire after ready, image unchanged; at `-smp 2` and `-smp 8` | **PASS** |
| 4 | Pixels — after the second boot, `remember me` pixel-correct from the shared font, `> ` and cursor on the row below, only the two console colours | **PASS** |
| 5 | **Oracle — Wajira's eyeball** | **PASS — confirmed 1 September 2026: "It remembers!"** |

The oracle's own evidence is still on the disk. `stage3/out/notes.img` now
parses as two notes — `remember me`, typed by the harness overnight, and
`i am an ai-os.`, typed by Wajira at the prompt on the morning of the 1st.
The machine wrote a human's sentence to a disk it formatted itself, and gave
it back after a reboot. That is the stage's done-when, in his own words.

Tests 1–4 were committed **red** before any of `stage3.asm` existed and went
green exactly where the plan predicted: test 1 at item 8, tests 2–4 at item 12
— on the first run of the gate at that item. The gate takes about four minutes
(seven QEMU boots).

**Verified in the plan, before any code:** the device identity, the BAR
address, and the absence of ECAM were all read out of a running QEMU with the
monitor before `plan.md` was drafted; the driver was then written to those
facts and the item 9 probe confirmed them from inside the guest.

**One thing that bit, now a gotcha:** NASM `%define` is positional. The
virtqueue constants were first used in `efi_main`, above their definition,
and the cascade of "label changed during code generation" errors that
followed pointed everywhere but the cause.

**Caveats carried forward:**

- **Stage 1's and Stage 2's stand:** the x2APIC path and the trampoline
  fallback remain unproven; the i8042 is not reconfigured; unshifted keys
  only; a parked AP that faults prints over serial; one machine, one firmware.
- **Modern interface only.** The legacy virtio I/O BAR is never touched; a
  legacy-only device is an `ERR:`, not a fallback. NVMe is the foundation's
  "second" and is deferred to a later ring.
- **One request in flight at a time, polled.** Interrupt-driven completion
  and multiple outstanding requests are a later ring's concern.
- **The notebook's edges are by design, not by test:** a line is capped at
  500 bytes (keys beyond it are ignored); an empty line is not a note; a full
  journal drops the line silently. None is reachable by the acceptance tests.
- **32-bit sector arithmetic.** A disk of 2^32 sectors (2 TB) or more is an
  `ERR:` naming the limit.
- **The spare page pool holds eight pages** — room for four MMIO regions
  beyond the identity map. Exhaustion is a named `ERR:`.
- **OVMF's own virtio driver binds the device during boot** and resets it at
  ExitBootServices; ours resets it again and assumes nothing.

---

## The frozen acceptance machinery

`stage0/test.sh`, `stage0/checkpixels.py`, `stage1/test.sh`,
`stage1/checkbands.py`, `stage2/test.sh`, `stage2/checktext.py`,
`stage2/font8x8.bin`, `stage3/test.sh`, `stage3/checknotes.py`,
`stage3/NOTEBOOK.md`, `stage4/test.sh`, `stage4/checkumbilical.py`,
`stage4/UMBILICAL.md`, **`broker/broker.py`**, and from Stage 5
`stage5/test.sh`, `stage5/checkgermline.py`, `stage5/GERMLINE.md`,
`stage5/component.asm`, `stage5/component.bin`, **`broker/germline.py`**
and **`broker/rehearse.py`** are frozen by `.claude/hooks/protect-tests.py`.
Stage 5 also closed a side door: a tool's `-o` aimed at a frozen path is
now a mutation the hook knows (with the binary frozen, `nasm ... -o
stage5/component.bin` had been allowed). The Stage 5 table is **569
payloads, 383 denied, 186 allowed, 0 wrong**. And it recorded the first
deliberate opening of a freeze: `broker/rehearse.py` was fixed by the
owner's own hand (item 8b) after the session stopped at the scope guard
and wrote the diff out unapplied — by decision, not by drift. The format and protocol documents are
frozen for the reason the font is: the assembler implements them and the
checker parses by them, so an editable criterion would be no criterion. The
broker is frozen because the mock's framing, record and canned table are what
test 3 judges the guest by — but `broker/claude_backend.py` (the one
`claude -p` function the automated gate never runs) is **not** frozen, split
at the trust boundary. The builders (`stage<N>/mkimage.sh`) and `stage2/FONT.md`
are deliberately not frozen: recipe and paperwork, judged by their product.

The same hook is the **storage bodyguard** from Stage 3 item 1 (see the Stage
3 section). The committed payload table `.claude/hooks/payloads.py` covers
the Stage 0–2 freeze cases (reconstructed from their commit records), the
storage cases, and the Stage 3 and Stage 4 freeze cases — including the cage
in real commands and the `nc`/`restrict`/`guestfwd` words in prose: **400
payloads, 267 denied, 133 allowed, 0 wrong**. Run it with
`python3 .claude/hooks/payloads.py`; it exits non-zero on a single wrong
verdict. Every freeze and the bodyguard bit immediately (per Stage 1's
amendment A4), demonstrated live each time — the Stage 4 freeze denied a
redirect into `stage4/UMBILICAL.md` the moment it was armed.

Two things learned about the hook, both now in CLAUDE.md:

- Only the hook **registration** is snapshotted at session start; the script is
  re-read on every call. A new hook waits for the next session, but edits to an
  already-registered one are live at once.
- It matches **prose** deliberately. A Bash command that merely mentions a frozen
  filename near a mutating verb is denied. Reword it, or use the Write/Edit
  tools, which judge the target path only.

`Stage 1 item 0` was an unplanned commit: the Stage 0 hook matched the bare
basename `test.sh` and so denied the *creation* of `stage1/test.sh`. Protecting a
file we have not written is a wall, not a freeze. Recorded as amendment A3 in
`stage1/plan.md`.

**The freeze openings, each by the owner's hand** (the owner's count of
28 September 2026; each ring's section has the detail):
1. `dffcb56`, Stage 5 item 8b: `broker/rehearse.py`, the twin boots a private copy.
2. `483c7b5`, ring 6a item 12b: the twin reads its own evidence.
3. `c000982`, ring 6b item 10b: the checker counts what a fresh mock records.
4. `7465153`, ring 6c item 11b: `stage6/checkpointer.py`, the screendump's order.
5. `0a5fd87`, ring 6c item 12c: `stage6/GLASS.md` and `stage6/checkpointer.py`, the pointer clamped to the console's cells (the oracle's finding).
6. `2a011d3`, ring 7b item 10b: `stage7/checkwire.py`, `grows_served` 0.
7. `ebf5794`: `broker/twin.py`'s `xp` parser, for QEMU 11.
8. `1020754`, ring 7d item 13b: `stage7/checktrials.py`, a failed monitor read.
9. `076d74b`: TRIALS.md's label-width sentence.
10. **`503b4e5`, ring 8a item 17 (27 September 2026)**: `stage8/parts.py` alone, one line.

**The count, settled by the owner on 28 September 2026:** `0a5fd87`
counts, as its own message and the paper's evidence audit of 5 September
say, so `503b4e5` is the tenth. This file had counted without it. The
commit messages of `2a011d3`, `ebf5794`, `1020754` and `503b4e5` carry
the old numbers, one lower, and are left as they are; so do `7481e4b`,
`204fb5d` and `422f7a7`, which record them.

About the tenth: SEED.md's worked example says that with seed 0's line
alone in the record, `current_seed` is seed 0. The frozen check applied
that claim to the live record, so it failed the moment item 17 added seed
1, as SEED.md and the plan require. It now asks the question of the
example's one-line record. The diff was CC's, written unapplied to
`stage8/out/item17-current-seed.diff` and proved on a private copy
(`stage8/out/probe8a/i17/`). Its class is ring 6b item 10b's and ring 7b
item 10b's: **an expectation written for the state at the freeze, not
for the state the plan says comes next.**

## Safety

Everything has run inside QEMU. Stages 1 and 2 give QEMU firmware plus exactly
one drive: a raw FAT image under the stage's `out/`. Stage 3 adds exactly one
more: a raw 16 MB notebook image under `stage3/out/`, created fresh by the
harness with `truncate`. OVMF is mapped read-only by `-bios`. No block device,
no loop mount, no `mkfs`, no `sudo` — and from Stage 3 item 1 the hook denies
each of those mechanically before the shell sees them. Nothing written outside
`/home/indy/Projects/ai-os` (bar scratch files in the session temp directory).
Stage 2's single network touch was the one-time fetch of the public-domain font,
verified against the sha256 pins recorded in `stage2/plan.md`; Stage 3 touched
the network not at all.

Stage 4 adds a network, but a caged one: slirp with `restrict=on` and a single
`guestfwd`, so the guest reaches nothing but the broker on `127.0.0.1:9999`
and every other destination gets a RST (measured before any guest code
existed, by injecting raw frames into slirp from the host). The broker binds
`127.0.0.1` only. The automated gate talks only to `broker/broker.py --mock`,
which makes no outward call of any kind, and `stage4/test.sh` refuses to run
while anything else holds the port — so **this session made no real Claude
call and spent no token.** The only outward connection in the whole design is
`claude -p`'s own HTTPS from the real broker, and that happens only in
Wajira's hands at test 5.

Stage 5 adds a second guest per grow — the rehearsal's twin — booted by
the broker from a private byte-identical copy of the image under
`stage5/out/rehearsal/`, with its own fresh notebook image, inside the
same cage with its `guestfwd` delivering to a private listener on
`127.0.0.1:9998`. Every drive is still a raw file under an `out/`; the
gate refuses to run while anything listens on 9999 or 9998. A grown
component runs at ring 0 with the whole (virtual) machine in reach — that
is the thesis — and the rehearsal in the twin is the mitigation the
foundation prescribes. This session made no Claude call:
`claude_backend.grow()` has never been run.

## Stage 4 — The umbilical · closed 1 September 2026

**Goal (foundation §7):** network driver, minimal TCP/IP, and a broker on
mlrig that relays to Claude. Done when the booted OS asks Claude a question
and prints the answer. Proves the OS has a brain. `stage4/spec.md` and
`stage4/plan.md` are approved (the plan through the plan-gate hook, its
first live use).

**What grew, on Stage 3's proven body:**

- **The wire, one document** — `stage4/UMBILICAL.md`, frozen: the cage, the
  addressing, the length-prefixed frame (a `u32` little-endian length then
  the bytes; requests 1–498 printable ASCII, responses 0–4096 printable or
  LF), the timers, the no-answer rule, the `? ` question rule, the mock's
  canned table, the record format, worked-example bytes, and the Python
  parser the checker and the broker share.
- **The broker** — `broker/broker.py` (frozen: framing, listener, record,
  the mock's canned table are criteria) binds `127.0.0.1` only, one
  connection at a time; `--mock` answers from the table and calls nothing;
  `--record` logs the raw bytes as hex so the checker judges by the document.
  `broker/claude_backend.py` (**not** frozen) is the one swappable function:
  `claude -p --output-format text --tools "" --no-session-persistence` with a
  two-line brief, its output folded to the wire's ASCII. (`--bare` was in the
  plan and was dropped at test 5 — see below.)
- **Two virtio devices** — Stage 3's globals became a per-device block; one
  PCI pass records both BDFs; `vio_attach`/`vio_negotiate`/`vq_init` are
  generic. On this machine the NIC is at bus 0 device 2 (`1af4:1000`, BAR4
  `0xC000000000`), the disk moved to device 3 (`0xC000004000`) — same 2 MB
  page, and `disk_rw` is unchanged, so the notebook still persists.
- **virtio-net** — `VIRTIO_NET_F_MAC | VERSION_1` only; queue 0 receives
  (sixteen 2048-byte buffers, whole-frame, no merge), queue 1 transmits, both
  polled with INTx off; the MAC read from device config. `S4: nic <mac>` is
  line eleven.
- **The stack** — Ethernet, ARP (reply for `10.0.2.15`, resolve `10.0.2.4`),
  IPv4 with the checksum verified on receive, client-only TCP (one connection
  and one segment at a time, in-order only, MSS 1460, a 4096-byte window, the
  guest the active closer, RST honoured). No gateway, no route — the guest's
  world is one on-link peer.
- **The question** — a line typed `? ...` goes to the broker as one frame;
  the answer is drawn console-only with a spinning working indicator while it
  waits, wrapped, above a fresh prompt; keys pressed during the wait are
  discarded. A note (no marker) still takes Stage 3's path. The serial echo
  contract is unchanged — the wire carries only the typed line and its CRLF.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial — twelve `S4:` lines, `S4: nic <mac>` in its slot carrying the harness's chosen MAC, found = woken = 8 | **PASS** |
| 3 | The question — mock up, `? ping` and `? hello` round-trip (broker receives exactly those frames per UMBILICAL.md; the canned answers are on the screen pixel-correct; a note typed between them is the only thing journaled; the wire echo untouched), at `-smp 2` and `-smp 8` | **PASS** |
| 4 | The cage — `restrict=on` with the single guestfwd asserted in both harnesses; a mock-down run ends in `no answer from the broker`, not a hang | **PASS** |
| 5 | **Oracle — Wajira's eyeball, with the real broker** | **PASS — confirmed 1 September 2026: the machine asked Claude and printed the answer** |

Tests 1–4 were committed **red** before any of `stage4.asm` existed and went
green where the plan predicted: test 1 at item 8, test 2 at item 10, tests 3
and 4 at item 14. The gate is five QEMU boots and refuses to run while
anything holds port 9999.

**The three deviations from the spec, approved with the plan** (each forced
by a measured fact): the broker's guest-side address is `10.0.2.4`, not
`10.0.2.2` (libslirp rejects a forward on its own host); the guestfwd's host
side is `cmd:nc -N 127.0.0.1 9999`, not a bare `-tcp:` target (which is one
chardev opened at QEMU start, shared, and refuses to boot with the broker
down); and test 3 types a note between the two questions to prove notes still
persist on Stage 4's own binary. The `nc` in the cage line is a real
dependency (OpenBSD netcat, stock Ubuntu).

**One bug caught and fixed during item 12, now a gotcha:** the first
`tcp_send` left `snd_nxt` unadvanced, so the peer's ACK of the data fell
outside the accepted window and the guest gave up while holding an answered
request. Advancing `snd_nxt` at send time fixed it.

**One thing test 5 surfaced, now a gotcha:** the backend's `--bare` flag
skips the CLI's own login (OAuth and keychain) along with the hooks and
CLAUDE.md discovery, so the real `claude -p` returned an auth failure while
the mock gate — which never runs the backend — stayed green. Dropped at
test 5 (commit `5b9e8fa`). The lesson: the frozen mock proves the wire, but
the real backend has its own failure surface that only the oracle exercises,
and Stage 5 will lean on `claude -p` far harder.

**One more thing test 5 surfaced — a usability finding, not a bug in the
code:** the first user typed `?` without the trailing space, and the line
went silently to the notebook as a note instead of to Claude. That is
exactly what Stage 4's plan decision 3 specified (the marker explicit and
exact: `?` alone or `?x` is a note), and the gate proved it — but a rule the
first user trips over on the first line is a design error, per the
foundation's human-factors constitution, not a user error. The Stage 5 spec
fixes it with a **forgiving marker parse**: the marker character alone, or
with any spacing, is recognised, and a marker line that cannot reach the
broker says so on the console instead of silently doing nothing. Stage 4's
frozen machinery is untouched by that fix — it lands in Stage 5's binary
and Stage 5's own tests (test 4's marker-parse cases).

**Caveats carried forward:**

- **Everything Stage 3 carried**, minus "unshifted only" — the shifted US
  layout now exists (`? ` is typeable). The x2APIC path and the trampoline
  fallback remain unproven; the i8042 is not reconfigured; one machine, one
  firmware.
- **The stack's omissions are by design:** no DHCP, DNS, UDP, IPv6, ICMP,
  congestion control, IP options or fragments, out-of-order reassembly, TCP
  options beyond MSS, window scaling, or keepalives. One connection at a
  time, polled, no NIC interrupts.
- **Plaintext inside the cage this ring.** TLS lives in the broker; the
  pre-built TLS blob joins the guest at the ring where its traffic first
  touches a real wire (Stage 7). Cryptography is never improvised.
- **The broker's `claude -p` backend is exercised only at test 5.** Its
  flags are its own to get right there; the file is unfrozen for that reason,
  and the automated gate never runs it. Proven at test 5 after `--bare` was
  dropped (above).

**The two gate questions, settled by the owner at the opening:**

- **The model.** The foundation's standing rule is Opus at high effort for
  implementation; Fable was the experiment for Stages 2 and 3 (zero defects
  in Cowork's review both times), and Stages 4 and 8 were flagged for a
  decision. Wajira's decision: **Fable 5 at high effort implements Stage 4.**
  This session runs on it.
- **The subscription policy.** Re-checked here as the foundation requires,
  and recorded in the spec: Anthropic announced, then paused, a June 2026
  change moving Agent SDK and `claude -p` usage to a separate credit pool.
  The current official position is that nothing changed — **`claude -p`
  still draws from Max subscription limits.** So the broker shells out to
  `claude -p`, no API keys anywhere, and its Claude backend is one small
  swappable function. **Re-check again at Stage 5.**

**The shape, from the spec:** the twin's network is a cage with one door —
QEMU's user-mode NIC with `restrict=on`, so the guest can reach nothing at all
except one `guestfwd` socket landing on the broker at `127.0.0.1:9999` on
mlrig. Inside the cage the guest↔broker link is plaintext this ring (owner
decision 1: TLS lives in the broker, and the pre-built TLS blob joins the
guest at the ring where its traffic first touches a real wire); `? ` is the
question marker (decision 2); DHCP, DNS, UDP, IPv6 and congestion control are
out, each a recorded omission (decision 3). The acceptance tests use only a
`--mock` broker, so the automated gate never spends a token or needs the
internet; the real backend is exercised by Wajira at test 5.

**The plan gate is live for the first time.** `.claude/hooks/
require-plan-approval.py` (Cowork-authored, owner-installed, commit
`770c941`) blocks ExitPlanMode until Wajira writes the approval marker from
his own terminal; the other hook denies this session every route to that
file. The correct behaviour on drafting the plan is: commit it, say it is
ready, and wait.

## Stage 5 — The conversation · opened 1 September 2026

**Goal (foundation §7):** the prompt itself: English in, machine code back,
verified in the twin, then run. The germline starts as a local cache of
proven components. **Done when "make me a clock" produces a running clock.**
Proves the loop closes — the Spectrum prompt is back. `stage5/spec.md` is
approved by the owner.

**The policy gate, re-checked 1 September 2026 as the foundation requires:**
the June 2026 credit-pool change is **still paused** per Anthropic's help
centre — Agent SDK, `claude -p` and third-party app usage still draw from
subscription limits, there is no separate credit pool, and any future
change is to be announced before it takes effect. So **`claude -p` still
draws from the Max subscription, no API keys anywhere**, and the broker's
backend stays one swappable unfrozen function. **Next re-check at the
following stage gate** (Stage 6). The germline cache this stage builds is
itself the mitigation if the policy ever tightens: a proven component is
never generated twice.

**The model:** the spec's decision 4 recommended Fable 5 at high effort
(Stages 2, 3 and 4 shipped on it with zero review defects); the owner
launched this session on Fable 5 at high effort, so that is the decision.

**The shape, from the spec:** a third kind of line — `! make me a clock` —
asks Claude to grow something; both markers get the forgiving parse; the
guest gains a loader (a fixed component region, a binary frame over the
wire, a jump into the blob with one register at a small service table, Esc
back to the prompt); one new frozen document, `stage5/GERMLINE.md`, carries
the whole new wire — `stage4/UMBILICAL.md` is frozen and not touched; the
broker grows the pipeline generate → rehearse (a headless boot of the same
guest image) → cache (`germline/`, gitignored) → deliver, with a repeat
request served from the cache and no generation call. The automated gate
speaks only to the mock and spends no token; the cage, the bodyguard and
every existing frozen file stand.

**What grew, on Stage 4's proven body** (items 9–12, `stage5/stage5.asm`):

- **The wire, one new document** — `stage5/GERMLINE.md`, frozen:
  the forgiving marker parse; the grow request (a request frame whose
  first byte is `0x01`, deliberately not printable, then the body); the
  grow response — a refusal (kind `0x00`, drawn like an answer) or a
  component (kind `0x01`, a 32-byte header, the blob at byte 32 of the
  content, the 1 MB cap); the 600 s deadline; the component region and
  line twelve; the entry contract; the four-entry service table; what the
  screen does around a component; the fixed console lines and refusal
  phrases; the rehearsal's seven criteria; the germline's key,
  normalisation, machine string and provenance; the mock's grow table;
  the record's grow fields; worked-example bytes; the shared Python.
  `stage4/UMBILICAL.md` is untouched.
- **The component region** — `0x100040` bytes of page-aligned BSS; a grow
  response is received straight into it from +28, the blob at +64. On this
  build `S5: component region 0x00000000004b4040 1048576 bytes` (line
  twelve). Code there executes: EFER.NXE is on under OVMF but our tables
  carry no NX bits — measured before planning.
- **The clock** — the TSC calibrated once at boot against one PIT 10 ms
  wait (`tsc_per_ms` 2,999,478 here); `ticks_ms` divides by it.
- **The keyboard** — `kbd_next` factored out of the main loop as the
  ring's one consumer; Esc (`0x1B`) in both tables, ignored at the prompt.
- **The marker parse and the third kind of line** — `parse_marker`
  (leading spaces skipped, `?` asks, `!` requests, the body trimmed and
  capped, a marker line never a note, an empty body drawing `nothing to
  ask` / `nothing to grow`); `grow_request` (the `0x01` frame; the refusal
  drawn; the component frame checked by `component_valid` and run; `bad
  component frame` otherwise); `umbilical_ask` generalised with `rx_dst`,
  `rx_max` and `rx_deadline`.
- **The loader and the services** — `run_component` (`fb_clear`, the
  `call` into region + 64 with `RDI` = the table and `RSP` 16-aligned,
  `console_redraw` from the shadow after, the ring discarded, the
  prompt); `svc_draw_text` (pixels only), `svc_console_size`,
  `svc_poll_key`, `ticks_ms`; the table filled at boot RIP-relative.

**The broker grew** (item 3): `broker/germline.py`, frozen, imports the
frozen Stage 4 framing from `broker/broker.py` (byte-identical) and adds
the marker-byte dispatch and the pipeline — generate, rehearse, cache,
deliver — with a running generation-call counter, `--tries 2` with the
failure fed back, the germline lookup (hash-verified) and write
(`component.bin`, `provenance.json`, `rehearsal.log`), the mock's grow
table (`test component`, `big` = the same padded to the cap, `fault` =
`ud2`). `broker/rehearse.py`, frozen: the twin driver — a one-shot
listener on 9998, a headless `-smp 2` boot of **a private byte-identical
copy** of the guest image under `stage5/out/rehearsal/` (item 8b), `!
rehearsal` typed through the monitor, two screendumps, Esc, a note, the
seven criteria in the document's order. `broker/claude_backend.py`
(unfrozen) gained `grow()`: `claude -p` with a brief that lifts the entry
contract and service table verbatim from `GERMLINE.md`, NASM source back,
assembled on the host, up to three assembly rounds; never run by the gate.

**The test component** (item 2): `stage5/component.asm` and its 448-byte
binary, both frozen; five strips through the table, `key: <ch>` for each
key, Esc to return. The checker assembles the source to `stage5/out/` and
demands the committed binary byte for byte.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial — thirteen `S5:` lines inside the cage with the harness's MAC, line twelve the region by shape (non-zero, below 4 GB, ≡ 64 mod 4096, the 1048576-byte cap), found = woken = 8 | **PASS** |
| 3 | The growth, mocked — `before`, `? ping`, `! test component` rehearsed in the twin, cached, delivered as the exact frame, run; `k` shown; Esc; `after`; the record, the germline entry, the notebook, both screens, at `-smp 2` and `-smp 8` | **PASS** |
| 4 | The rehearsal and the germline — both cages asserted; `! fault` refused after two failed rehearsals (`the twin reported an error`); `! test component` generated then served from the germline with no generation call; `! big` streamed as a `4 + 32 + 1,048,576` byte frame and run; `?`, `?x`, `!`, `!x` routed; the record's call sequence 2 / 3 / 3 / 4 / 5; two germline entries with provenance | **PASS** |
| 5 | **Oracle — Wajira, real broker** — `! make me a clock` | **PENDING** |

Tests 1–4 were committed **red** before any of `stage5.asm` existed and
went green where the plan predicted: test 1 at item 9, test 2 at item 10,
tests 3 and 4 at item 12. The gate is five boots of its own plus six
rehearsal boots, about eight minutes, and refuses to run while anything
listens on 9999 or 9998.

**One thing bit, hard, and is now a gotcha:** QEMU locks the raw image a
running guest boots from, so the rehearsal — which booted the very
`stage5/out/esp.img` the guest runs from — could never boot the twin
beside a guest. Found at item 11's probe, after the freeze. The session
stopped at the scope guard (commit `f22eea3`), measured the alternatives,
wrote the fix out as a patch under `stage5/out/` and did not apply it;
Cowork verified the diff, the owner applied it by his own hand, and item
8b committed it with the payload table re-run (569, 0 wrong). The freeze
was opened for exactly that change and nothing else. Lesson: probe two
QEMUs on one image before freezing anything that boots one.

**Smaller things that bit:** `%define` is positional (again — `CHAR_SPACE`
below `svc_draw_text`; the first error was the only one that mattered);
`pkill -f` matches its own shell; a probe's first expected screen row must
not be a prefix of another row (`> ?` matched `> ?x`).

**Caveats carried forward:**

- **Everything Stage 4 carried.** The x2APIC path and the trampoline
  fallback remain unproven; the i8042 is not reconfigured; one machine,
  one firmware; the stack's omission list; plaintext inside the cage.
- **One component at a time, cooperatively run, no watchdog.** A component
  that never returns hangs the real machine; the rehearsal's 90 s budget
  catches it in the twin first. Esc is a convention the component honours.
- **The rehearsal proves safe, not correct.** Whether the thing on the
  screen is what was asked for is the oracle's judgement this ring.
- **The machine string is the twin's** (`qemu-q35-ovmf`): the machine the
  user faces and the twin are the same image this ring. At Stage 7 it
  becomes the scanned hardware.
- **The generation brief's quality is the backend's own affair.** The gate
  proves the pipeline with the mock; `claude_backend.grow()` has never been
  run and is exercised only at test 5 (Stage 4's `--bare` lesson applies:
  it is unfrozen for exactly that reason).
- **No persistence of components in the notebook**; the germline lives
  broker-side, per machine, gitignored. A 600 s grow deadline in the guest.
- **A component runs at ring 0 with the whole machine in reach** — the
  thesis, and the rehearsal is the mitigation the foundation prescribes.

## Stage 6 — Growth · opened 1 September 2026

**Goal (foundation §7):** a simple compositor and GUI, more devices, and
the store-of-plans prototype: install an application from a plan file.
The compositor ships with the machine's obs chart from day one — border
stripes reborn as truthful, live telemetry — and the DE takes its shape
from the human-factors constitution (foundation §5), not from existing
desktops. **Proves the machine can grow a face and a store.**
`stage6/spec.md` is approved by the owner, 1 September 2026.

**The policy gate, re-checked 1 September 2026 as the foundation
requires:** Anthropic's help centre says the June 2026 credit-pool change
is **still paused** — Agent SDK, `claude -p` and third-party app usage
still draw from subscription limits, there is no separate credit pool,
and any change is to be announced before it takes effect. So the broker
keeps shelling out to `claude -p` with **no API keys anywhere**, and the
backend (`broker/claude_backend.py`) stays one swappable unfrozen
function. The germline remains the mitigation if the policy ever
tightens. **Next re-check at the Stage 7 gate.**

**The owner's decisions at approval — all eight recommendations taken:**

1. **Three rings**, glass → plans → pointer, one plan gate, one set of
   frozen tests and one fresh session each; the pointer may slip to the
   end of the stage without weakening it.
2. **Fixed regions this ring:** obs strip top, choices row bottom, the
   conversation left, the app panel right, every size measured from the
   mode at boot.
3. **The glass core and ABI 2 now:** a dedicated core owns the screen
   (the concurrency doctrine's one absolute law); an app is four
   callbacks — `init`, `step`, `key`, `exit` — with a 50 ms step budget
   the rehearsal judges. No watchdog this ring.
4. **Installed apps live on a second image**, `home.img`, with its own
   frozen format (ring 6b); the notebook is untouched.
5. **N-of-1 trials are measured for now and run later:** every request's
   time-to-done, every error shown and every input-to-photon is recorded
   in the obs page from ring 6a.
6. **The calculator is the first plan** and ring 6b's oracle.
7. **Fable 5.1 at high effort implements Stage 6**; Cowork specs and
   reviews on the same. (This session runs on it.)
8. **The screen mode is the EDID route at 1440x1440:** the display's
   preferred mode if it states one, else the highest. The guest reads the
   EDID from the standard VGA device's own memory (a PCI lookup of the
   display class, the EDID BAR, 128 bytes, the first detailed timing
   descriptor); every QEMU command — gate, twin and the oracle's windowed
   run — gains `-vga none -device VGA,edid=on,xres=1440,yres=1440`. The
   console becomes 90x90 cells here; nothing is baked in, the tests keep
   reading the resolution from the guest's own log. The `yres` number is
   the owner's to adjust.

**The three rings:**

| Ring | Name | Done when | State |
|---|---|---|---|
| 6a | **The glass** | `! make me a clock` ticks in its own panel while you type a note beside it, and the obs strip shows real numbers | **CLOSED 2 September 2026** — test 5 confirmed by Wajira |
| 6b | **The store of plans** | `! install calculator` from `plans/calculator.md` gives a working calculator; reboot with no broker; `! calculator` still runs it | **CLOSED 3 September 2026** — test 5 confirmed by Wajira |
| 6c | **The pointer** | click a choice on the choices row and it happens; pointer input-to-photon is a number on the obs strip | not started — its own session; allowed to slip |

**Ring 6a's shape, from the spec** (the plan fixes the details): the
glass core compositor on the first AP, four regions on the console's
16x16 grid (obs strip, choices row, conversation panel, app panel), the
obs page and obs strip, ABI 2 (`init`, `step`, `key`, `exit`; `draw_text`
into the panel, `panel_size`, `ticks_ms`, `fill`), the kind `0x02` frame
in a new frozen `stage6/GLASS.md`, the mode policy of decision 8, new
broker files `broker/glass.py` and `broker/twin.py` importing the frozen
framing, the mock table (`test app`, `big`, `fault`, `hog`, `escapee`),
nine rehearsal criteria, and acceptance tests 1–4 written red before any
code and frozen. Stage 5's files stay byte for byte as they are and
`stage5/test.sh` must still pass at the end of the ring. The automated
gate speaks only to the mock and spends no token.

### Ring 6a — the build, item by item

`stage6/plan-6a.md` was approved on 2 September 2026 with Cowork's four
amendments (A1 at most three declared choices on the choices row; A2
the twin and the pipeline composable before they freeze; A3 the error
paths render their line to the screen; A4 two honesty lines in the wire
document). Part 1 — everything written before any code — is done and
frozen: `stage6/GLASS.md` (item 1), the three fixtures `stage6/app.asm`,
`hog.asm`, `escapee.asm` with their binaries (item 2), `broker/glass.py`
and `broker/twin.py` beside the untouched Stage 5 brokers and the
backend's ABI 2 mode (item 3), `stage6/mkimage.sh` and `stage6/test.sh`
with test 1 (item 4), test 2 with `stage6/checkglass.py --one-core`
(item 5), `--glass` (item 6), `--truth` (item 7), and the freeze of
eleven paths with the payload table at **814 payloads, 0 wrong** (item
8). Part 2 so far: item 9 (Stage 5's body as `stage6.asm`, test 1
green), item 10 (the EDID and the mode policy — `S6: edid 1440x1440`
then `S6: gop 1440x1440`, `edid none` then 2048x2048 without; the region
at `0x100080` with line thirteen at +128; the keyboard stamp ring; Tab),
item 11 (the obs page and every counter, line fourteen), item 12 (the
surfaces, the glass core on the first AP, the four regions, the strip
formatted from the page, the choices row, line fifteen, the one-core
error rendered to the screen — **test 2 green**).

Then item 12b (the owner's fix to the frozen twin, below), and item 13
(ABI 2: the kind `0x02` validator field by field, the loader with
`init`/`step`/`key`/`exit` and RSP kept in memory across every callback,
the four services into the app panel, the app-aware main loop — Esc
closes whoever has the keys, Tab moves them, the step every 10 ms timed
into the page — the choices row's three states, a `!` closing the running
app first) — **all four automated tests green at `-smp 2` and `-smp 8`.**
Item 14 is this handover. **Item 14b — Cowork's pre-oracle review, fix
first:** the one defect, input-to-photon on the Enter path — `photon_mark`
ran after `notebook_append`, `ask_question` or `grow_request` returned,
so `ph` measured the whole broker wait and one real grow would have
pinned its worst at 99.9 for the session; it is now marked once, right
after the CRLF echo (the new line is Enter's echo), and the wire's wait
stays in `w`. Two nits taken: `draw_cursor` stores the new cursor word
before dirtying the old row, so the glass core can never leave a ghost
block; the backend's ABI 2 brief puts the `; choice` lines immediately
after `default rel`, where `extract_source` keeps them.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial — sixteen `S6:` lines with the EDID (`edid 1440x1440`, the mode 1440x1440, console 90x90, region `0x…4c8080`, obs page `0x…4c7000`, `glass core 1`), `edid none` and 2048x2048 without, found = woken = 8; at `-smp 1` the named error after fourteen lines, on serial and rendered on the screen | **PASS** |
| 3 | The glass, mocked — `! test app` rehearsed in the twin, cached, delivered, run in its panel with its choices on the row and `running test app` on the strip; `k` to the app; Tab, a note beside it journaled; Tab, `j`; Esc restores the prompt's row; `? ping` answers; at `-smp 2` and `-smp 8` | **PASS** |
| 4 | The truth on the strip — `fault`, `hog` and `escapee` each refused with their phrase after two rehearsals and never on the screen; the test app's keys counted; the strip on screen equal to the obs page read before and after it, frames strictly increasing; every region equal to its surface; the same app served from the germline (source 1, calls unchanged); `big` streamed as a `4 + 96 + 1,048,576` byte frame and run; `hold` showing `growing`; the markers; at the end `k 0080 q 001 n 001 g 002/001 err 007` on the strip and in the page | **PASS** |
| 5 | **Oracle — Wajira, real broker** — `! make me a clock`; a note beside it; the strip moves; Esc | **PASS — confirmed 2 September 2026** |

**What the oracle showed** (`history/2026-09-02-ring6a-clock-in-panel.png`):
two requests, `make a clock` and `make me a clock`, both grown by the
real backend against GLASS.md's callback contract and both rehearsed in
the twin — `g 002/000` on the strip; the clock ticking in the app panel
while a note was typed and journaled beside it in the conversation; the
strip honest about the human path against the wire — **`ph 13.2/15.5`
ms** against **`w` 167,339 ms** for the two exchanges; and **two choices
Claude declared unasked**, `h` (12/24 hour) and `d` (date on/off), on the
choices row. The clock came with switches nobody asked for, as the Stage
5 clock came with a date.

**The owner's decision at the oracle: windowed runs use
`xres=1920,yres=1080`.** A 1440-tall window overflows a 1440 monitor
under QEMU's title and menu bars, and 1080p is what cheap monitors state
— what Stage 7's metal will most likely say. The mode policy does the
rest: the same binary reads the EDID and takes 1920x1080, console
120x67. **The caveat that follows:** the frozen gate and the frozen twin
keep 1440x1440, so the twin now rehearses an app on a 45x86 panel while
the machine runs it on 60x63. Apps adapt through `panel_size` — the
grown clock did — but a rehearsal is no longer on the machine's exact
geometry. Ring 6b's broker module is to set `twin.VGA_ARGS` to match the
machine's display before calling `twin.rehearse`, which the frozen file
allows without being touched.

Tests 1–4 were committed **red** before any of `stage6.asm` existed and
went green where the plan predicted: test 1 at item 9, test 2 at item
12, tests 3 and 4 at item 13. The gate is five boots of its own plus ten
rehearsal boots, about fourteen minutes, and refuses to run while
anything listens on 9999 or 9998.

**On this build:** the glass core is the first AP (APIC id 1); a frame
that paints nothing costs about 0.06 ms and the worst seen in the gate
is a few ms (a whole-panel repaint); input-to-photon is typically 1–4 ms
with a worst of one frame slot (16.7 ms); the test app's `step` is under
0.1 ms.

**Caveats carried forward:**

- **Everything Stage 5 carried.** The x2APIC path and the trampoline
  fallback remain unproven; the i8042 is not reconfigured; one machine,
  one firmware; the stack's omissions; plaintext inside the cage; a
  component runs at ring 0 with the whole machine in reach.
- **One app at a time, cooperatively stepped, no preemption and no
  watchdog.** A `step` that never returns hangs the real machine; the
  twin's 50 ms budget and 90 s bound catch it first. `step` is not called
  while the BSP waits on the wire (a `?` question pauses a running clock
  for the wait; deviation 7). A `!` request closes the running app first.
- **The glass core is the first AP to check in**, not chosen by
  topology until Stage 7. A torn cell may last one frame. No timer
  interrupt: the glass paces on the TSC, the BSP spins while an app runs.
- **The choices row is text**, not drawn targets (ring 6c). The strip is
  87 columns wide and is cut at the right edge on a narrower screen.
- **The trials are recorded for, not run**: time-to-done and every error
  are in the obs page; no N-of-1 trial exists yet.
- **`ph` is not literally a photon** (GLASS.md's honesty line), and
  **grows served is the one strip number taken from the broker**.
- **The real backend's ABI 2 brief is exercised only at test 5**, as
  Stage 4's `--bare` lesson prescribes; `claude_backend.grow(abi=2)` has
  never been run.
- **A GLASS.md wording defect stands** (below): the frozen checker's
  expectation is the operative criterion.

**The stop, and the freeze opened once — item 12b.** A defect in the
frozen `broker/twin.py`, found at item 13's first probe: `judge` reads
the conversation surface under the key `conversation`; `rehearse` stored
it as `conv`. Every rehearsal that reached the seventh criterion died
with a `KeyError` instead of a verdict and the broker's connection closed
without an answer. Two lines. The session stopped at the scope guard
(commit `4e59ffe`), wrote the diff unapplied at
`stage6/out/twin.fix.patch` (gitignored, so its text is also here) and
verified it on a scratch copy of the twin against all four candidates
above. **Cowork verified the diff against the frozen file — the two
renamed keys match the one read at the judge, no criterion is weakened,
the nine phrases stand — and the owner applied it by his own hand with
`git apply` at the repo root, 2 September 2026.** Item 12b commits it
with the payload table re-run (814, 0 wrong). The freeze was opened for
exactly that change and nothing else — the second such opening in the
project's history, the first being Stage 5 item 8b. The diff, for the
record:

```
--- a/broker/twin.py
+++ b/broker/twin.py
@@ -304,7 +304,7 @@
     ev = {"ready": False, "lines": [], "errs": [], "echo": None, "delivered": False,
           "b": False, "c": False, "notes": None, "listener_error": None,
-          "obs_b": None, "obs_c": None, "conv": None, "choices": None,
+          "obs_b": None, "obs_c": None, "conversation": None, "choices": None,
           "name": name, "after": None, "lines_want": lines}
@@ -349,7 +349,7 @@
                         ev["obs_b"] = drv.read_obs(obs_addr)
-                        ev["conv"] = drv.read_surface(ev["obs_b"]["conversation"])
+                        ev["conversation"] = drv.read_surface(ev["obs_b"]["conversation"])
                         ev["choices"] = drv.read_surface(ev["obs_b"]["choices"])
```

**One wording defect in the frozen `stage6/GLASS.md`, for the owner's
judgement, no code depends on it:** under "Running an app", the closing
sentence says "if the cursor is not at column 0 a fresh line is started
and a prompt drawn". The prompt is already live while an app runs (that
is the point of the ring), so on Esc the cursor is always past column 0,
and the frozen checker's screen C expects **no** extra prompt line between
`> mid` and `> ? ping`. The guest does what the checker and the sentence's
last clause say — the conversation comes back exactly as it was — and
the sentence should lose its middle clause when the owner next opens
that file.

**Things that bit this ring, now in CLAUDE.md's gotchas:** NASM
under `default rel` cannot make `[label + reg]` RIP-relative and silently
emits the label's absolute 32-bit address — the RVA, not the loaded
address — so a dirty flag went to low RAM and nothing painted (the Stage
5 idiom, `lea` then index, is the rule); `mul` clobbers RDX; a patch that
appended a block after itself left the live copy of `kbd_next` without
its counter; QEMU's default VGA carries an EDID naming 1280x800; four
probes on one image hit the lock again.

## Ring 6b — the store of plans · opened 3 September 2026

`stage6/plan-6b.md` was approved on 3 September 2026 with Cowork's four
amendments (A1 every app draws its starting state in `init`, and the
fixtures run in the twin before they freeze; A2 the owner's two changes to
the calculator's intent; A3 the no-broker launch compares two obs reads;
A4 `install` with no plan name is refused before any call) and all ten
deviations accepted. **The owner's experiment for this ring: Fable 5.1 at
medium effort implements**, to be compared with Opus at high (Stages 0 and
1) and Fable at high (Stages 2 to 6a); Cowork reviews to the same standard
as every ring. Item 0 (this record and the plan's commit) is done; the
items follow one commit each, exactly as the plan says.

**The one edit to `stage6/spec.md` (item 2, amendment A2):** the owner
approved, at the 6b plan gate, two changes to the calculator's intent in
the appendix — the line shows `0` before anything is typed and after `c`
clears; dividing by zero shows `error` until the next key, which clears
it, and numbers over nine digits show `error` the same way. The appendix
was edited to say so and `plans/calculator.md` copied from it byte for
byte; the choices and the five tests are exactly as the spec first wrote
them.

### Ring 6b — the build, item by item

**What grew, on ring 6a's body** (`stage6/stage6.asm`, items 9–11):

- **The second disk** — `pci_scan` records the first virtio-blk as the
  notebook's disk and the second, by drive order (PCI device order,
  measured), as the home image; `blk_rw` drives either by its device
  block; the home has its own rings. Without a second disk the machine
  is ring 6a's line for line — ring 6a's frozen gate boots the same
  binary with one disk and stays green.
- **The home image** (`stage6/HOME.md`, frozen) — `GERMHOME` header,
  sixteen 256-byte entries (name, the current build's size, extent and
  SHA-256, the previous build the same, the frame's choice slots), the
  builds from sector 9; formatted on first boot, scanned on every boot
  (validity by the document's rule, the next free sector recovered by
  scanning, no count in the header); line twelve `S6: home <N> apps`.
- **The install** — an app frame with `installed` 1 is written to the
  home image before it runs: the blob's sectors first, then the entry's
  table sector (replace keeps the previous build); the SHA-256 is the
  guest's own (`sha256` in the guest, verified on the host against
  `sha256sum` for nine inputs before it ran there); `installed <name>`
  on the console; full or absent home says so, counts an error, and the
  app runs anyway. `installing` on the strip while an `install` request
  waits.
- **The launch** — `! <name>` for a valid entry reads the build from
  disk, hashes it, checks the entry (a mismatch refuses, loudly),
  synthesises the header and runs it exactly as a delivered app — with
  nothing on the wire and neither grows counter moved. `! undo install
  <name>` swaps the two builds. The choices row at the prompt names up
  to three installed apps as `! <name>`.

**The broker** (`broker/plans.py`, frozen; item 3) subclasses the frozen
`Glazier` and drives the frozen twin through amendment A2's seams
(`extra_args` for the home drive at `stage6/out/rehearsal/home.img`,
`lines=17`, `after=` the plan's tests), sets `twin.VGA_ARGS` to
1920x1080 so the twin is the machine again, reads `plans/<name>.md`
(`stage6/PLANS.md`, frozen: the name alphabet, Intent, Choices, the five
verbs with their exact grammar and how the twin runs each), keys the
germline by the plan's hash and any amendment at the door (`! install
echo, but big`), delivers with `installed` 1 (from the germline too), and
refuses a failed test in the plan's own words: `rehearsal failed: expect
"a"`. `install` with no plan name is refused before any call (A4). The
unfrozen backend gained the plan brief. **The two fixtures ran for real
in the twin before the freeze (A1):** `echo.bin` passed all nine
criteria and its five verbs, `liar.bin` failed at `expect "a"`.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial — seventeen `S6:` lines with `S6: home 0 apps` twelfth on two fresh disks at 1920x1080 (console 120x67); the home image parsed from the host as formatted and empty; the same image booted again byte-identical; one disk gives ring 6a's sixteen | **PASS** |
| 3 | The install, mocked — `! install echo` rehearsed against the plan's tests in the twin (seventeen lines, the hook's verdicts in the log), `installing` on the strip meanwhile, the frame with `installed` 1, `installed echo` in the conversation, the app in its panel, the home image holding exactly that build with the guest's hash equal to hashlib's, the germline's provenance naming the plan and its hash, `! echo` on the choices row at the prompt; at `-smp 2` and `-smp 8` | **PASS** |
| 4 | The store keeps its word — a reboot with **no broker**: `S6: home 1 apps`, `! echo` on the row, `! echo` run from disk with `wire_conns` 0 and the byte counters unchanged between a read after ready and a read after the launch (A3), an undo with nothing to undo refused; then `! install liar` refused `rehearsal failed: expect "a"` after two rehearsals, `! install echo, but big` replacing (4096 bytes), `! install echo` served from the germline with `source` 1 and `installed` 1 replacing again, `! undo install echo` swapping the previous build back, `! echo` running it — both extents hash-checked from the host, the strip against the page (`err 001`, `g 001/001`) | **PASS** |
| 5 | **Oracle — Wajira, real broker** — `! install calculator`; a sum; reboot with the broker off; `! calculator`; the sum again | **PASS — confirmed 3 September 2026** |

**What the oracle showed** (`history/2026-09-03-ring6b-calculator-installed.png`,
`history/2026-09-03-ring6b-calculator-offline-launch.png`): the real
backend built the calculator from `plans/calculator.md`'s intent and the
twin rehearsed it against the plan's five tests in one exchange of 72
seconds — `w 001 071881` on the strip; `installed calculator`, the
plan's choices `= result` and `c clear` on the choices row, a sum done.
Then the reboot with no broker: `S6: home 2 apps` — the gate's echo
fixture shares `stage6/out/home.img` with the oracle — `! calculator` on
the choices row, and the launch from disk with `wire_conns` 0 and `io
000000/000000`: nothing on the wire, as HOME.md promises.

**The oracle's own evidence is still on the disk:** `stage6/out/home.img`
was set aside as `stage6/out/home.oracle.img` (gitignored, as Stage 3 did
with its notes) so the next gate run, which rewrites `home.img`, does not
erase the first calculator installed from a plan. The harness never
touches that name.

Tests 1–4 were committed **red** before any of the ring's guest code and
went green where the plan predicted: tests 1 and 2 at item 9, tests 3
and 4 at item 11. The gate is eight boots of its own plus six rehearsals,
about twelve minutes, and refuses to run while anything listens on 9999
or 9998.

**On this build:** region `0x4ce080`, obs page `0x4cd000`; echo's first
build lands at sector 9, the padded one at 10–17, a re-install at 18;
an install of a 121-byte build is two disk writes and a launch two reads.

**Caveats carried forward:**

- **Everything ring 6a carried.** One app at a time, no watchdog, the
  glass core the first AP, the trials recorded for, not run.
- **Space behind an abandoned build is not reclaimed**; sixteen entries;
  a name matches exactly, byte for byte.
- **Drive order is the contract** for which disk is the notebook and
  which the home; a foreign image on the second slot is formatted.
- **A home launch counts in neither `g` field** (the obs page is
  frozen); the mode word and the conversation record it.
- **The twin rehearses installs with `installed` 0** (the frozen
  listener); the write to the home image is proven by the gate's guest.
- **`press` cannot press `` ` `` or `~`** (they do not arrive through
  the monitor); `expect` matches anywhere on the panel, so a plan's
  intent should say what else is drawn.
- **The real backend's plan brief is exercised only at test 5.**

**Things that bit this ring, now in CLAUDE.md's gotchas:** a counter
lives in the process that holds it (the freeze opening below); a lookup
that copies its argument must give it back (RSI/ECX after `rep movsb`);
`lodsb` sets AL only.

### Ring 6b — the record of the build

Part 1 is done and frozen: `stage6/PLANS.md` and `stage6/HOME.md` (item
1), the three plans and the echo and liar fixtures (item 2 — the
calculator copied from the spec's appendix after the owner's A2 edit),
`broker/plans.py` and the backend's plan brief (item 3 — both fixtures
rehearsed for real in the twin before the freeze, echo passing all nine
criteria and five verbs, liar failing at `expect "a"`), `stage6/test-6b.sh`
and `stage6/checkplans.py` with tests 1–4 written red (items 4–7), the
freeze of twelve paths with the payload table at **1072 payloads, 0
wrong** (item 8). Part 2: item 9 (the second disk by drive order,
`blk_rw` on a device block, HOME.md's format-or-scan, line twelve —
tests 1 and 2 green, ring 6a's gate and Stages 0–5 green); item 10
(SHA-256 verified on the host against `sha256sum` for nine inputs before
it ran in the guest, the install write, `installing` on the strip — tests
1 and 2 green, test 3 green but for the choices row, ring 6a and Stages
0–5 green).

**Item 11 stopped at the scope guard, 3 September 2026, before its
commit.** The `!` dispatch (`undo install
<name>`, a launch from the home image with the hash checked and a
synthesised header, else the broker), the choices row with up to three
installed apps, `run_app` leaving the grows counters alone on a launch.
With it, `./stage6/checkplans.py --install 2` passes whole, and
`--store` passes **every check but three numbers**: boot C's record
expects `generation_calls` 3, 4, 4 for the liar, the amended re-install
and the germline re-install, but the checker itself stops the mock after
boot A and starts a fresh one for boot C, so the counter restarts and
the broker truthfully records 2, 3, 3. The frozen checker is wrong by my
own hand (the plan's decision 12 counted across boots as if one broker
served them); the guest is right. Per the plan's scope guard the frozen
file is not edited: the fix is written unapplied at
**`stage6/out/checkplans.fix.patch`** (three counts and one message
line; `git apply --check` passes), and a scratch copy of the checker with
that patch applied was run against the guest: **`the store: kept its
word`** — every other assertion of test 4 (the no-broker launch with
the wire counters unchanged, the liar refused `rehearsal failed: expect
"a"`, the amended re-install, the germline re-install, the undo
hash-checked from the host, the strip against the page) passes as
written. Item 11's guest diff is in the working tree and copied to
`stage6/out/item11.diff` (312 lines). One defect was found and fixed on
the way: `home_lookup_name` clobbered RSI and ECX, so an unknown `!`
body reached the broker as an empty one (`nothing to grow`) — fixed by
preserving both.

**The freeze opened once — item 10b, 3 September 2026.** Cowork
verified the diff against the frozen checker: the counts 2, 3, 3 are
what a fresh mock truthfully records for boot C, and no criterion is
weakened. **The owner applied it by his own hand with `git apply` at the
repo root**, and item 10b commits it with the payload table re-run
(1072, 0 wrong). The freeze was opened for exactly that change and
nothing else — the third such opening in the project's history, after
Stage 5 item 8b and ring 6a item 12b. The diff, for the record: the
three `generation_calls` expectations in `run_store`'s boot C (3 → 2,
4 → 3, 4 → 3) and the message line that reports them. **Item 11 then
committed with all four tests green** at both `-smp` values, ring 6a's
gate and Stages 0–5 green; item 12 is this handover, README's ring 6b
section, CLAUDE.md's build block (Stages 5, 6a and 6b) and three
gotchas, the payload table re-run (1072, 0 wrong).

## Ring 6c — the pointer · opened 4 September 2026

`stage6/plan-6c.md` was approved on 4 September 2026 with Cowork's three
amendments and three nits (A1 test 1 goes green at item 9, test 2 at item
10, test 4 at item 11, test 3 at item 12; A2 no count in the frozen checker
is a hand-written literal — `expected_counts(steps)` derives packets, clicks,
mouse bytes and keys from the step list and `hits` from a per-step flag
written beside the press it describes; A3 a click on an installed app's
`! <name>` acts only on an empty prompt line, else it is a click and not a
hit and types nothing; the GLASS.md draft opens with a blank line;
`cell_repaint` reads its bounds from the four surface descriptors; item 0
removes the review copy) and all eleven deviations accepted. **The model for
this ring: Fable 5.1 at high effort**, the owner's decision; Cowork reviews
to the same standard as every ring. Item 0 (this record and the plan's
commit) is done; the items follow one commit each, exactly as the plan says.

**The shape, from the plan** (its environment table holds the measurements
behind every choice): `S6: mouse ready` is printed once, serial only, when
the mouse first speaks — no honest hardware fact can hide a PS/2 mouse from a
QEMU guest that keeps its keyboard, and the frozen gates count lines exactly
— while the boot-time identification lives in the obs page (`mouse_id`);
the fifth callback is announced inside the blob (`POINTER2` at offset 16, a
`u32` `point` offset at 24; no existing blob carries the magic); the cursor
and the strip's `pt`/`pk`/`cl` field at column 88 appear only once a packet
has arrived, so a machine whose mouse never moves is ring 6a's to the pixel;
the obs page's pointer fields run from `0x240` to `0x2BF`; the i8042 handler
keeps the position and rings whole packets; a click's synthetic keys take
the typed key's path through one `handle_key`; a new fixture `point app`
(`stage6/pointer.asm`) and a new module `broker/pointer.py` subclassing the
frozen `Installer`; the 6c gate at 1920x1080 with two disks, `-smp 2` and
`-smp 8`, about eight minutes, mock only.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial — seventeen `S6:` lines and the frozen 6a strip and surface checks passing before any packet, `mouse_id` 1 and the i8042 command byte (`0x77` read, `0x47` written) in the page; one `mouse_move`, then eighteen lines with `S6: mouse ready` eighteenth and nothing else after `keyboard ready`, the arrow at the page's cell, every other cell its surface's, `pt` within budget, the strip's third field equal to the page; at `-smp 8` and `-smp 2` | **PASS** |
| 3 | The pointer, driven by the monitor — a click on `? ask` types the marker; `! point app` rehearsed and run; three buttons in its panel draw `1`, `2`, `3` where they landed; `c clear`, `Tab prompt`, `Tab app`, a gap and `Esc exit` clicked; the frozen test app clicked on twice harmlessly; the record three connections (a click puts nothing on the wire); every count derived from the events (47 keys, 11 clicks, 8 hits; `pk 0107 cl 011` on the strip); at `-smp 2` and `-smp 8` | **PASS** |
| 4 | The truth about the pointer — the checker's and the twin's commands inspected; the six fixtures reproduced and only the point app carrying `POINTER2`; the pre-packet screen judged by the **frozen** 6a `check_strip` and `check_surfaces`; a 36-move sweep with the arrow at the page's cell, exactly one arrow, the cell it left restored and `pt` under two frame slots at nine screendumps; three presses on an empty spot (3 clicks, 0 hits); `! install echo`; `! echo` clicked with `x` on the line (a click, nothing typed), Backspace, clicked again (the launch from disk, the wire counters unchanged); the strip's field the page | **PASS** |
| 5 | **Oracle — Wajira, real broker** — clicks his way through the choices row and into the calculator, along every edge and into the corners | **PASS — confirmed 5 September 2026** (first run found the edge defect, fixed as item 12c; second run clean) |

**On this build** (5 September 2026, `-smp 8`, 1920x1080): the binary is
36,864 bytes; the i8042 command byte OVMF leaves is `0x67` (read as `0x77`
after the guest's own two port-disables), written `0x47`; the mouse
answers `FA AA 00`; `pt` after a single move 3.4 ms at `-smp 8` and 14.4 ms
at `-smp 2`, worst across a 36-move sweep 16.2 ms — one frame slot; every
`mouse_move` within 127 counts is one packet, `mouse_button` one packet;
`mouse_hw` never above 2 in the gate. The gate is five boots of its own
plus five rehearsals, about nine minutes.

**Caveats carried forward:**

- **Everything ring 6b carried.** One app at a time, no watchdog, the glass
  core the first AP, the trials recorded for, not run.
- **A mouse that never moves never announces itself**: `S6: mouse ready` is
  printed on the first packet, serial only; the boot-time identification is
  the obs page's `mouse_id`. On Stage 7 metal the page is where to look.
- **Button presses only**: no drags, no releases and no moves are delivered
  to `point`; there is no acceleration; the overflow bits are ignored.
- **The choices row's targets are text spans**, not drawn targets; button 1
  clicks the row; a launch item acts only on an empty prompt line.
- **The strip's third field is cut at 1440x1440** (`pt` alone fits in the
  three spare columns), as the strip was always cut at a narrow screen.
- **The twin never sees a mouse**: `point` is proven on the machine by the
  gate, and a rehearsal that moved the mouse would put the eighteenth line
  into the echo the eighth criterion demands byte-exact.
- **Presses made while the machine is busy are dropped** with the keys typed
  then (`finish_line`'s discard); the position stands and the cursor is live
  throughout, because the handler keeps it.
- **The real backend's `point` paragraph is exercised only at test 5**, as
  every ring's brief has been.

**Things that bit this ring, now in CLAUDE.md's gotchas:** the order of
the three reads around a screendump (surfaces, screendump, page) is itself a
criterion — the freeze opening; two devices on one i8042 need the status
byte read before port 0x60, and command-byte bit 5 set means *disabled*;
a serial line after `keyboard ready` must bypass the tee.

### Ring 6c — the build, item by item

Part 1 so far: **item 1** — GLASS.md's ring 6c section (416 lines) written
to `stage6/out/glass-6c-section.md` and appended by the owner's own hand;
the first 777 lines proven byte-identical (`cmp` against `HEAD`, the same
SHA-256 `f5f9f092…`, zero lines removed, one hunk of additions from line
775); the section's Python run from the appended file against the frozen
6a code. Running it caught two slips in the plan's prose (an item after two
gaps starts at column 17, not 16; the 6a example row ends `.1`), corrected
in `stage6/plan-6c.md`. **Item 2** — the fixture `stage6/pointer.asm` and
`pointer.bin` (186 bytes, SHA-256 `abbcd0a1c99424fd…`; offsets 28, 47, 48,
98, `POINTER2`, `point` at 99), `.gitignore`'s exception; the frame
round-trips through the frozen `parse_response`; **rehearsed for real in
the frozen twin** at 1440x1440 with one disk on the committed ring 6b
image: all nine criteria pass in 14 s (`steps 325`, `step_worst 0.0 ms`,
`frame_worst 3.1 ms`). **Item 3** — `broker/pointer.py`: `Pointer(Installer)`
with the section's Python verbatim, the one new canned request `point app`,
`rehearse_point` refusing a five-callback blob whose offset lies outside
`[28, L)` before any twin boot (`rehearsal failed: the point offset lies
beyond the blob`), `--rehearse-app`; the backend's ABI 2 brief gains
`POINT_RULE` and the section's "five callbacks" text lifted from GLASS.md.
Proven on the host with no guest and no call (the display seam, the
helpers, a stub rehearsal delivering GLASS.md's frame and the germline
serving it with `source` 1, the bad offset refused with no boot, the mock
over the wire on a throwaway port: `ping`/`pong`, `x` refused, `install
nothing` refused with no call, `point app` twice into a twin with no image),
then **rehearsed for real through this module's twin** — 1920x1080, the
home drive, seventeen lines, the committed ring 6b image — all nine
criteria in 14.3 s. The twin never moves the mouse. **Item 4** —
`stage6/test-6c.sh` with test 1 (the 6c MAC `52:54:00:a1:06:03`, the
display, the port refusals, the summary with the two commands and the grab
hint). **Item 5** — `stage6/checkpointer.py`: the driver with `mouse`,
`button`, `moveto` and `serial` steps and a pointer model (the centre at
boot, every move within one packet), `expected_counts(events)` (A2: every
count derived from the emitted events, `hits` from the per-step flag),
`check_boot_lines` with this ring's MAC, `strip_mouse_line`,
`check_arrow_at`, `check_no_arrow`, `check_surfaces_except`,
`check_cell_restored`, `check_strip_6c`, `check_i8042`, and `--serial`
(test 2). Red on the ring 6b binary as it must be: before the move the
frozen `check_strip` and `check_surfaces` pass and the page's `mouse_id` is
0 (want 1); after one `mouse_move` the lines are still seventeen, no mouse
line, `packets 0`, no arrow, the strip without its field. **Item 6** —
`--point` (test 3): the click on `? ask` typing the marker, `! point app`
rehearsed and run, three buttons in its panel drawing their digits, `c
clear`, `Tab prompt`, `Tab app`, a gap and `Esc exit` clicked, the frozen
test app clicked on harmlessly, the record with three connections and the
germline with two entries, screen D with the strip's field; every target
column from the section's `choice_targets`, every count from
`expected_counts`. Red on the ring 6b binary: no mouse line, the `?` never
typed (the line became the note ` ping`), no digits, the counters zero.
**Item 7** — `--truth` (test 4): the argv assertions on the checker's and
the twin's commands; the six fixtures reproduce their binaries and only the
point app carries the magic; the pre-packet screen judged by the **frozen**
`check_strip` and `check_surfaces` (they pass on the ring 6b binary, as
deviation 4 predicted); a 36-move sweep through the empty app panel with
nine screendumps — the arrow at the page's cell, exactly one arrow, the cell
it left restored, `pt` under budget; three buttons on an empty spot; `!
install echo`; the launch item clicked with `x` on the line (a click, no
hit, nothing typed — A3), Backspace, clicked again (the launch, the wire
counters unchanged); screen D with the strip's field against the page. The
6c checker's own germline check for a plain grow expects the twin's
seventeen lines (the frozen 6a helper expects sixteen). Red on the ring 6b
binary as it must be. `stage6/test-6c.sh` now runs all four tests.
**Item 8** — the freeze: `PROTECTED` grows `stage6/pointer.asm`,
`stage6/pointer.bin`, `broker/pointer.py`, `stage6/test-6c.sh` and
`stage6/checkpointer.py` (GLASS.md was frozen at 6a; its 6c section went in
by the owner's hand); `payloads.py` gains the ring 6c group — the battery on
each path, the `-o` side door, the owner's append denied, the measured
allowances — **1206 payloads, 839 denied, 367 allowed, 0 wrong**; the
freeze demonstrated live with one denied append. Part 1 is done: tests 1–4
exist, tests 2–4 are red on the ring 6b binary, and every criterion is
frozen. Part 2, the guest code, begins at item 9.

**Part 2 so far — item 9** (`stage6/stage6.asm`): the i8042 configured for
the first time — both ports off, the command byte read (`0x77` after the
two disables; OVMF's `0x67` with them clear) and written **`0x47`** (both
interrupts on, both ports enabled, translation kept), `A8`, the mouse reset
(`FA AA 00`, `mouse_id` 1), defaults, reporting on, drained, all bounded by
the PIT; the PIC's masks `0xF9`/`0xEF`; one handler body with two entries
(IRQ1, IRQ12) reading the status byte first and routing by bit 5, plus the
slave's spurious vector; `mouse_byte`'s three-byte machine in the handler —
resync on bit 3, the stamp at the first byte, the deltas applied and
clamped, the cell word stored last, the presses, one ring entry per packet
(64, drop-on-full, high-water); the pointer at the screen's centre from
boot; `mouse_next` and the main loop's second wake test; `finish_line`
dropping the mouse ring too; **`S6: mouse ready` once, serial only, through
a raw UART write** the first time the main loop sees a packet. Probed by
hand on a private copy: seventeen lines then eighteen; `mouse_move 10 20`
→ (970, 560), `200 0` → two packets, a button → one packet with `buttons`
1, `sendkey a` echoing `a` with the aux port live. Test 2 red only on item
10's assertions (the arrow, the field, the pending stamp). **The regression
chain on this binary: Stages 0–5, ring 6a (383 s) and ring 6b (395 s) all
PASS** — a mouse that never moves leaves the machine ring 6a's to the line.
**Item 10** — the cursor and the pointer's photon: `cursor_draw` as the
frame's last act (nothing until the first packet; the old cell repainted by
`cell_repaint` from the surface whose descriptor bounds contain it, the
conversation's block cursor overlaid; the arrow — `01 03 07 0F 1F 0D 19
30` through `draw_glyph`, `draw_cell`'s painter with the bytes given — every
frame); `ptr_pending` snapshotted before the copies and `pointer_last` /
`pointer_worst` measured after them; the strip's third field ` pt LL.L/WW.W
pk NNNN cl NNN` from column 87 once `packets` is non-zero, `strip_put_row`
taking the row's length. **Test 2 green at `-smp 8` and `-smp 2`**: after
one move the arrow at the page's cell, every other cell its surface's, `pt`
3.4 ms and 14.4 ms, the field equal to the page. Test 4's sweep, run for
information: 36 moves, 36 packets, the arrow at the page's cell and the
cell it left restored at all nine screendumps, `pt` worst 16.2 ms — one
frame slot; only the clicks (items 11–12) fail. **Item 11** — the click:
`handle_key` lifted out of the main loop (the same instructions, `ret` for
`jmp main_loop`), so a click's synthetic keys take a typed key's path;
`click_dispatch` counting every press in `clicks`, a left press on row `R−2`
searched in the **hit table** (`hit_table`, up to five entries of first
column, last column, kind, argument, rebuilt by `choices_update` beside the
row it writes — the markers, the home entries as launches, the app's keys,
Esc and the Tab items), the press's stamp as the key's stamp, a hit counted
and its key handled; a launch item typing `! <name>` and Enter **only on an
empty prompt line** (A3), else a click and no hit; the gaps, the other
buttons and the other rows nothing; `click_panel` a stub for item 12.
**Test 4 GREEN**: the frozen 6a checks on the pre-packet screen, the
36-move sweep, three presses on an empty spot (3 clicks, 0 hits), `! echo`
clicked with `x` on the line (a click, nothing typed), Backspace, clicked
again (the launch from disk, the wire counters unchanged), the strip's field
against the page. Test 3 red on `point` alone — and on one defect of the
frozen checker's own, below.

**The stop at item 11, 5 September 2026 — a defect in the frozen
`stage6/checkpointer.py`, my own hand.** `--point`'s final steps read
`("shot", D), ("surfaces", "d"), ("obs", "d2")`: the screendump is taken
*before* the first page read, so `check_strip_6c`'s rule that the strip's
`up` and `frames` lie between the two reads can never hold (the screen
showed `up 000069`, `fr 004192` against reads of `000070`/`004220` and
`004235`). `--serial` and `--truth` have the order the frozen 6a and 6b
checkers use — surfaces, then the screendump, then the page — and pass.
Per the scope guard the frozen file is not edited: the one-line reorder was
written unapplied at **`stage6/out/checkpointer.fix.patch`** (`git apply
--check` passed) and its text is below for the record; a scratch copy of
the checker with the patch applied proved item 12 meanwhile. No criterion is
weakened: the same three reads, in the order every frozen checker takes
them. **The owner applied it by his own hand with `git apply` at the repo
root, 5 September 2026; item 11b commits it with the payload table re-run
(1206, 0 wrong)** — the fourth opening of the freeze in the project's
history, after Stage 5 item 8b, ring 6a item 12b and ring 6b item 10b, each
for exactly one change.

```
-            ("shot", shots["d"]), ("surfaces", "d"), ("obs", "d2"),
+            ("surfaces", "d"), ("shot", shots["d"]), ("obs", "d2"),
```

**Item 12** — `point` and the fifth entry: `app_valid`'s rule for the magic
and the offset (`bad component frame` outside `[28, L)`), `run_app`
recording `app_has_point` from the blob in the region (a delivery and a
home launch alike), `app_call` keeping the callback's three arguments (its
scratch pointer moved to R11), `click_panel` calling `point(row, col,
button)` once per button newly pressed inside the panel of an app that
announces it, one hit each; a four-callback app clicked on without effect.
**All four automated tests green at `-smp 2` and `-smp 8`** — test 3: the
click on `? ask` typing the marker, `! point app` rehearsed and run, three
buttons drawing `1`, `2`, `3` at the clicked cells, `c clear`, `Tab prompt`,
`Tab app`, a gap and `Esc exit` clicked, the frozen test app clicked on
harmlessly, screen D with `pk 0107 cl 011`, 47 keys, 11 clicks, 8 hits, every
count derived from the events; the point app rehearsed by hand through
`broker/pointer.py` on this image, nine criteria in 14.0 s; Stages 0–5, ring
6a and ring 6b green on the same binary. The binary is 36,864 bytes.

**Item 12b — Cowork's pre-oracle review, one defect, fixed before the
oracle.** `click_panel` kept its loop state — the panel row, the column,
the pressed bits, the button number — in R12–R15 across `call app_call`;
`app_call` preserves nothing but RSP and GLASS.md lets an app clobber every
other register, so after `point` returned the loop could run again on
garbage. It passed the gate only because `pointer.asm` preserves R12 and
RBX, which the contract does not require of a grown app. The fix: the four
registers pushed before the call and popped after (`app_call` restores RSP
from `saved_rsp`, so the pushes are still there). Two nits taken:
`mouse_init` reads the command byte back with `20` after writing it, as the
section says, a confirmation only (`i8042_cmd`'s meaning unchanged); the
README's oracle paragraph says `! point app` is the mock's request. A gotcha
in CLAUDE.md: nothing survives a call into grown code but memory and the
stack. Verified by hand on a private copy with the mock — five clicks in
the point app drew `1`, `2`, `3`, `1`, `2` where they landed (5 hits), three
in the test app left its known picture — then the gate whole and every
earlier gate, all green (`stage6/out/regress.item12b`).

**Item 12c — the oracle's finding, fixed before the oracle again; the fifth
freeze opening.** Wajira moved the mouse along the bottom edge of the
1920x1080 window and fragments of the arrow stayed behind under the choices
row. Cowork confirmed the cause in the code: 1080 is not a multiple of 16,
so the console has 67 rows over 1072 pixels and 8 spare rows below;
`mouse_byte` clamped `ptr_y` to the mode (1079), the cell word named row 67,
`cursor_draw` painted the arrow half past the screen and `cell_repaint`
found no surface owning row 67 to repaint. The gate never saw it: its sweep
stayed inside the app panel. Reproduced on a private copy through the
monitor: 600 down from the centre gave `ptr_cell` row 67 and 40 foreground
pixels in rows 1072–1079; a sweep along the edge and back left 200 (five
ghosts). **The owner's two decisions:** the pointer is clamped to the
console's cells, `0 … 16C−1` and `0 … 16R−1`, never to the mode; and row
`R−1`, the blank row under the choices row, is the row's margin — a button-1
press there is judged by its column exactly as one on row `R−2` (Fitts: a
slam to the bottom edge hits the target, not a dead row). Both change frozen
text: **the two patches were written unapplied — `stage6/out/glass-6c-edge.patch`
(three hunks in the ring 6c section: the clamp sentence, the two obs rows,
the click table's row for `R−1`; the section's Python is column-based and
needed no change) and `stage6/out/checkpointer.edge.patch` (the model's
clamp; in `--truth` eight clamped moves to the corner, the arrow at
`(R−1, C−1)` and nowhere else, the position the console's last pixel, every
region its surface's; the two launch clicks moved along the bottom edge to
row `R−1`) — checked with `git apply --check` and applied by the owner's own
hand at the repo root, 5 September 2026;** the applied diffs were verified
equal to the patches line for line. The guest: `mouse_byte` clamps to
`scr_cols·16−1` and `scr_rows·16−1`; `click_dispatch` takes a button-1 press
on `scr_rows−1` as one on `scr_rows−2` for the hit test. After the fix, on
the probe: 600 down gives row 66, zero pixels below the console, zero after
the edge sweep; a bottom-edge click over `? ask` types the marker and one
over `! echo` launches it (`mode 3`, `name echo`). Then the gate whole (the
corner: the pointer at (1919, 1071) in cell (66, 119), the arrow whole there
and nowhere else), every earlier gate and the payload table, all green
(`stage6/out/regress.item12c`).

## Stage 7 — Metal · opened 9 September 2026 · closed 18 September 2026

`stage7/spec.md`, approved by the owner on 9 September 2026 with every
recommendation taken and decision 5 amended (the HP plugs into the home
switch beside mlrig; mlrig's LAN port carries 10.0.2.4/24 as a second
address and answers the guest's ARP across the switch). The policy gate
re-checked the same day: `claude -p` still draws from the subscription, no
API keys anywhere; next re-check at the Stage 8 gate. **The patient: the
HP Compaq Elite 8300 SFF** — Q77 AHCI SATA (no drive fitted yet), Intel
82579LM (`6C:3B:E5:3B:86:45`), PS/2 keyboard and mouse, COM A on the rear
panel, Intel HD graphics, AMI Aptio UEFI with Secure Boot off and USB
first, four cores, 8 GB. Patient two, later, the ThinkStation P330. Three
rings, each a fresh session with its own plan gate and its own frozen
tests: **7a the disk** (an AHCI driver; notes and home on one SATA disk
under a GPT the guest writes), **7b the wire** (an e1000e driver; the cage
becomes the home switch through `broker/relay.py`), **7c the metal** (the
EDID guard, the i8042 cold init, the stick, the flash by the owner's hand,
every stage re-proven on the HP). The N-of-1 trials ring comes after the
metal. The Stage 6 binary and gates are untouched: Stage 7 is
`stage7/stage7.asm`, copied from `stage6.asm` at ring 7a item 1 with the
prefix `S7:`, drivers swapped, and Stages 0–6 stay green forever on their
own binaries.

## Ring 7a — the disk · opened 9 September 2026

`stage7/plan-7a.md` was approved on 9 September 2026 with Cowork's four
amendments (A1 the port-selection rule: every SATA port identified, the
port holding a recognised GermOS table chosen, else the port whose first
two sectors are all zero and that disk formatted, else `ERR: no GermOS
disk and no blank disk` naming each port — a foreign table, an MBR, a boot
sector or a torn table is refused, never formatted; the disk line gains
the port; test 2 checks `esp.img` byte-identical around every boot and
adds a foreign-table refusal boot; A2 the twin's SATA read yields `notes
None` and a log line on any error, never an exception; A3 `broker/metal.py`
joins `PROTECTED` at item 10 after nine of nine through it, the other
three paths at item 8; A4 the BSP's xAPIC/x2APIC mode recorded at item 1)
and every deviation accepted bar the two the amendments withdraw. **The
model for this ring: Fable 5.1 at high effort**, the owner's decision;
Cowork reviews to the same standard as every ring. Item 0 (this record,
the plan's and the spec's commit) is done; the items follow one commit
each, exactly as the plan says.

**The shape, from the plan** (its environment table holds the measured
facts behind every choice): the AHCI driver per 1.3 — the controller by
class, the ABAR mapped uncached, every port with a SATA disk identified,
one command slot, `IDENTIFY DEVICE`, `READ DMA EXT` and `WRITE DMA EXT`,
polled, interrupts off, bus mastering before any address; `blk_rw` over
two partition descriptors; a GPT with GermOS's own type GUIDs and fixed
disk and partition GUIDs, so the table is a function of the sector count
and the checker compares it byte for byte with what `stage7/DISK.md`'s own
Python builds; notes at LBA 2048 and home at 34816, 16 MB each, the two
frozen formats inside unchanged; `S7: gpt written` then `S7: disk port <p>
<sectors> notes <lba> home <lba>` — eighteen lines on a blank disk,
seventeen on a recognised one, no count a literal; the frozen twin cannot
read an `S7:` guest (three literals, no seam), so `broker/metal.py` carries
`rehearse_metal`, the frozen twin transcribed and judged by the frozen
`judge`, the SATA disk through `extra_args` beside the frozen virtio notes
disk the guest ignores (proven by one deliberate `if=virtio` boot in test
2 and by the twin's image after every rehearsal); the gate at 1920x1080,
`-cpu IvyBridge`, `-smp 2`, `4` and `8`, mock only. Test 1 is green from
item 4; tests 2, 3 and 4 go green together at item 10.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial — eighteen `S7:` lines on a blank disk with `gpt written` and the disk line, the table byte-identical to DISK.md's from the host and both stores freshly formatted; seventeen on the same disk, byte-identical afterwards; the twin's shape with a virtio disk beside the SATA disk, the virtio image all zero; a foreign table refused by name and never written; the boot image untouched around every boot; at `-smp 8`, `4`, `2`, `2` and `2` | **PASS** |
| 3 | The notebook on SATA — `remember me` and `on sata` typed on a blank disk, the notes partition holding exactly them byte-exact per NOTEBOOK.md, a reboot with `S7: notebook 2 notes`, nothing on the wire, both above the prompt on screen, the disk untouched; at `-smp 2` and `-smp 8` | **PASS** |
| 4 | The store on SATA — `! install echo` through the mock and a twin that formats its own SATA disk (its virtio image all zero), echo at LBA 34825 hash-checked; a reboot with no broker, `S7: home 1 apps`, `! echo` from the partition with the wire counters unchanged, the undo with nothing to undo refused; the liar refused, two re-installs, the undo swapping the builds back, both extents hash-checked from the host; screen D the truth; at `-smp 4` | **PASS** |
| 5 | **Oracle — Wajira, real broker** — one note, one reboot, `! calculator` from a home partition the real broker installed | **PASS — confirmed 9 September 2026** |

**On this build** (9 September 2026): the binary is 36,864 bytes, Stage
6's size; the AHCI function is `00:1f.2` (`8086:2922`), its ABAR at
`0x81080000` below 4 GB, the disk on port 1 beside the boot image on port
0; a blank 64 MB disk formats in one boot with thirty-eight sector writes
(the table's thirty-six and the two partitions' first sectors) and both
stores' own; the gate is twelve boots plus four rehearsals, about eight
minutes; the twin's rehearsal 14 s for the test app, 17 s for echo against
its plan; the BSP in xAPIC mode under `-cpu IvyBridge`; the payload table
1324 cases, 0 wrong.

**Caveats carried forward:**

- **Everything Stage 6 carried.** One app at a time, no watchdog, the
  glass core the first AP, the trials recorded for, not run.
- **One port, one slot, one sector a command, polled**; no NCQ, no TRIM,
  no FLUSH CACHE (a write completes when the device says so, as virtio's
  did); interrupts never enabled on the controller.
- **The backup header is written and never read**: a damaged primary is
  `torn`, refused, not recovered. **Every GUID is fixed**: the table is a
  function of the sector count alone, so two GermOS disks in one machine
  would share a disk GUID.
- **The partitions are 16 MB each at fixed LBAs**; the guest reads whatever
  a recognised table names but writes only DISK.md's layout.
- **Nothing that is not blank is ever formatted** (A1): a drive from
  another life must have its first two sectors zeroed by the owner's hand
  before the first boot — ring 7c's `METAL.md` will say so.
- **OVMF writes `NvVars` into the ESP on every boot**, so "the boot image
  untouched" means what the guest must never do to it: sector 0
  identical, no table over it, `BOOTX64.EFI` identical.
- **The frozen twin's virtio notes disk stays in every rehearsal**,
  ignored by the guest and asserted all zero; `rehearse_metal` is the
  frozen twin transcribed (plan deviation 1), judged by the frozen
  `judge`, whose log line says "S6: lines" whatever the prefix.
- **The `home_present` branch is dead code**: always 1 on a GermOS disk.
- **The real backend is unchanged** this ring and exercised only at test 5.

**Things that bit this ring, now in CLAUDE.md's gotchas:** a table of
addresses in data is a table of RVAs (the stripped-relocations trap, its
other form); OVMF writes to the ESP on every boot; the twin always has two
SATA disks, so a driver chooses by what a disk holds and never writes one
that is not blank.

### Ring 7a — the build, item by item

**Item 0** — this record; `stage7/plan-7a.md` and `stage7/spec.md`
committed. **Item 1** — `stage7/stage7.asm` (the ring 6c source with every
`S6:` made `S7:`, twenty-five literals and comments, and a Stage 7 header
above Stage 6's own), `stage7/mkimage.sh` (the recipe retargeted; 36,864
bytes, the same size as Stage 6's). The environment, measured on private
copies under `stage7/out/probe7a/` with a temporary probe injected into a
copy of the source (never into `stage7/stage7.asm`, never committed):

| Fact | Measured how |
|---|---|
| **The copy boots in the twin's shape** — `-cpu IvyBridge`, `esp.img` on `ide.0`, a blank 64 MB disk on `ide.1`, the frozen twin's blank virtio notes disk, the cage, 1920x1080 — to `S7: keyboard ready` with **sixteen** `S7:` lines at `-smp 2`, `4` and `8` (one virtio disk, no home line), found = woken = smp, `console 120x67`; OVMF boots `esp.img` from `ide.0` with the blank disk beside it; the SATA disk's sectors 0–1 stay zero (no driver touches it) and the virtio notes disk is formatted by the copy, as it must be | `stage7/out/probe7a/boot.sh`, six boots |
| **The BSP is in xAPIC mode** under `-cpu IvyBridge` at `-smp 2`, `4` and `8`: `IA32_APIC_BASE` = `0xfee00900` (BSP, enabled, bit 10 clear). Stage 1's x2APIC path is **not** exercised by this CPU model (A4); the i5-3570 carries the same flag and its firmware decides | the probe's `rdmsr 0x1B` |
| **The AHCI function is `00:1f.2`**, vendor:device `8086:2922` (ICH9 AHCI), class dword `0x01060102` (class 01, subclass 06, interface 01, revision 02); command register `0x0007` — memory, I/O **and bus mastering already on**, left so by OVMF's driver — status `0x0010`; **BAR5 = `0x81080000`**, a 32-bit memory BAR below 4 GB, inside the identity map (`map_mmio_2m` remaps its 2 MB page uncached) | the probe's PCI scan by class |
| **The HBA:** `CAP` `0xc0141f05` — S64A, NCQ, **32 command slots**, 6 ports, Gen 2; `GHC` `0x80000000` — **AE already set, IE clear**; `PI` `0x3f`; `VS` 1.0 | the probe, ABAR mapped uncached |
| **Ports 0 and 1 hold the two disks, ports 2–5 are empty.** Ports 0 and 1: `PxSSTS` `0x113` (DET 3 device present and Phy up, SPD Gen 1, IPM 1 active), `PxSIG` **`0x00000101`** (a SATA disk), **`PxCMD` `0x0006` — SUD and POD set, ST, FRE, CR and FR all clear: OVMF's driver stopped its ports before handing over**; `PxCLB` one list shared by every port (`0x0ea63000`, `0x0ea53000`, `0x0e833000` — moves with the boot), `PxFB` `CLB + 0x1000 + port·0x100`; `PxTFD` `0x50` (DRDY, DSC); `PxSERR` 0; `PxIS` `0x1` (a stale D2H-register bit to clear); `PxIE` 0. Ports 2–5: `PxSSTS` 0, `PxSIG` `0xffff0101`, `PxCMD` `0x4014`. **`ide.1` is port 1; `esp.img` is port 0** — exactly A1's case | the probe, every implemented port |
| **OVMF writes to `esp.img` on every boot, whether the guest touches the disk or not**: with `-bios OVMF.fd` and no separate variable store the firmware keeps its non-volatile variables in a file, **`NvVars`** (3,031 bytes), on the first FAT volume — 1,711 bytes differ between the image before and after a boot (FSInfo's free-cluster hints at sector 1, the FAT at sectors 32 and 788, the root directory at 1544, four data sectors), and no two boots leave the same bytes. **So A1's "`esp.img` byte-identical before and after" cannot be a criterion as worded**; what the guest must never do is write a table over it, and that is what test 2 will check: sector 0 (the FAT boot sector) byte-identical, `classify(esp)` still `other` (no protective MBR, no `EFI PART` at sector 1), `BOOTX64.EFI` extracted byte-identical to the build, and the refusal boot's error line naming port 0 as `other`. Recorded here for the owner and Cowork before item 5 writes the test | `md5sum` before and after each boot; `cmp -l`; `mdir` on the booted copy |
| **`blkid -p` and `partx -s` read a table built by DISK.md's Python** (a 64 MB image on the host): `PTTYPE="gpt"`, `PTUUID` the disk GUID, partition 1 `GermOS notes` 2048–34815 and partition 2 `GermOS home` 34816–67583, each 16M, with their GUIDs — the host's two witnesses agree with the document before the guest exists (item 2's evidence, measured at item 1) | `blkid -p`, `partx -s` on `stage7/out/probe7a/host-gpt.img` |

**Item 2** — `stage7/DISK.md` (505 lines): the controller and the port,
A1's selection rule in the guest's five words (`germos`, `blank`, `gpt`,
`torn`, `other`), the recognition rule, the table field by field with the
five fixed GUIDs and their on-disk order, the partitions at 2048 and
34816 (32,768 sectors each; the smallest disk 67,617 sectors), the frozen
formats inside and the HOME.md paragraph superseded, the lines (eighteen
on a formatting boot, seventeen recognising; `S7: disk port <p> <N> notes
<lba> home <lba>`), the obs words at `0x2C0`, the errors by name, the
worked example with every byte from the document's own Python, and the
Python (`build_gpt`, `parse_gpt`, `classify`, `partition_bytes`,
`check_table`). Proven on the host: the code block byte-identical to the
tested module; the CRC check value; the round trip at 131,072 sectors and
at the minimum; `classify` on the built image, zeros, `esp.img`, a foreign
type GUID and a flipped bit; the built image the one the two host
witnesses read at item 1.
**Item 3** — `broker/metal.py` (not frozen until item 10, A3): DISK.md's
Python verbatim (its three imports included, so the block matches the
document byte for byte); `twin_extra_args(workdir)` — `-cpu IvyBridge`
and a 64 MB SATA disk on `ide.1` under the twin's scratch directory;
`read_sata_notes` (A2: a missing file, a short file, a blank disk, a table
without a notebook — each a `notebook: …` log line and `None`, never an
exception); `rehearse_metal`, the frozen `twin.rehearse` transcribed with
the `S7:` ready line, line regex and obs-page regex, the SATA disk created
blank beside the frozen shape's virtio `notes.img`, the note read from the
SATA notes partition, and a log line saying whether the virtio image
stayed all zero — judged by the frozen `twin.judge`; `tests_hook_metal`
(`plans.tests_hook` with the `S7:` regex); `rehearse_metal_plan` behind
ring 6c's point-offset check; `Metal(Pointer)` swapping
`plans.rehearse_plan` for this twin around the frozen `Installer.install`;
`--rehearse-app` and `--rehearse` hand runs; Stage 7 defaults. Proven on
the host with no guest and no call: the twin's command as built (three
drives — the ESP, the frozen virtio notes disk, the SATA disk — the cage
on 9998, the 1080p device, the `ide-hd`, `-cpu IvyBridge`); a bad point
offset refused with no boot; the four A2 paths; a stub twin delivering
GLASS.md's `point app` frame and the install swap reaching the stub with
the plan and eighteen lines, `plans.rehearse_plan` restored after; the
mock over the wire on a throwaway port with a twin pointed at a file that
does not exist — `ping`/`pong`, `x` refused, `install nothing` refused at
no cost, `install echo` refused `rehearsal failed: the twin did not boot`
with two rehearsals recorded and the running call total 3 (ring 6b's
gotcha: the count is the process's). **Then the twin for real on the item
1 image** (`--rehearse-app stage6/app.bin 'test app' --lines 16`): sixteen
`S7:` lines found, the obs page found, the app delivered and run (`mode 3`,
`steps 324`, `frame_worst 3.1 ms`), both screens judged — **seven of nine
criteria pass and the eighth fails on exactly A2's path**: `notebook: no
EFI PART signature (the SATA disk holds blank)`, `virtio notes.img: WRITTEN
- 24 non-zero bytes`, `fail: no live prompt after esc (the notebook holds
None, want ['after'])`, 14 s. That failure is the ring's reason; item 9
turns it green.
**Item 4** — `stage7/test.sh` with test 1: the machine spelled once
(`-machine q35 -cpu IvyBridge -m 256M -bios OVMF`), the display, the cage
with the 7a MAC `52:54:00:a1:07:01`, `sata_drive` (the `if=none` drive
and the `ide-hd` on `ide.1`, spelled once), `fresh_disk` at 64 MB, the
port refusals, the wipes, the build, the summary with the two commands at
`-smp 4`. **Test 1 green** (deviation 10: the item 1 copy is a packed
PE32+). Tests 2–4 do not exist yet.
**Item 5** — `stage7/checkdisk.py`'s host side and test 2. The checker:
DISK.md's Python through `import metal`; the two pattern lists (eighteen
with `gpt written`, seventeen without — the expected count is the list's
length), `check_boot_lines` (the disk line's sector count the image's, its
LBAs the document's), `check_echo` under `S7:`, `extract_partition`,
`check_notes_partition` (NOTEBOOK.md's worked-example bytes),
`check_home_partition`, `check_formatted` (the table byte-exact, both
stores freshly formatted, every other sector zero), `check_recognised`,
`write_foreign` (a valid table with another type GUID, `classify` `gpt`),
`check_esp` (sector 0 identical, still `other`, `BOOTX64.EFI` extracted
identical, the size unchanged — A1's intent, given OVMF's NvVars write).
Proven on synthetic images built by the same Python: a formatted image
passes, a table without stores fails on both, a stray sector at 50000
is named, wrong LBAs are named, the foreign image is `gpt`, the item 1
boot's ESP passes `--esp` and a table written over it fails on all four
counts. `test.sh`'s `serial_check` in three modes (`blank`, `again`,
`foreign`, an optional virtio disk) with `--esp` around every boot, and
test 2's five boots: `blank` at 8 then `--formatted`, `again` at 4 on the
same disk byte-identical, `fresh` at 2, `virtio` at 2 (the SATA disk
formatted, the virtio image all zero), `foreign` at 2 (the named refusal,
the image byte-identical). **Red on the item 1 copy as it must be**: nine
lines then `ERR: no virtio-blk device on PCI bus 0` in the four
virtio-free boots; sixteen lines with `S7: disk 32768 sectors` tenth in
the virtio boot; the wrong `ERR:` on the foreign disk; the boot image
passed its check in every boot and the foreign disk stayed byte-identical.
Test 1 green.
**Item 6** — `checkdisk.py --persist` (test 3): the checker's own
`qemu_argv` (the Stage 7 machine, two drives, the cage, `-cpu
IvyBridge`), `drive` (ring 6b's step vocabulary under `S7:`; a guest that
never reaches ready has its `ERR:` line quoted), and `run_persist` — run
one on a blank disk types `remember me` and `on sata`, the echo exact, the
disk parsed from the host (the table byte-exact, the notes partition
exactly those two notes per NOTEBOOK.md's worked example, the home
partition empty); run two on the same disk demands seventeen lines with
`S7: notebook 2 notes`, nothing on the wire, both notes above the prompt in
the conversation panel through the frozen `check_region_rows`, and the
disk byte-identical. `test.sh` gains test 3 at `-smp 2` and `-smp 8`.
**Red on the item 1 copy**: run one never reaches ready — `ERR: no
virtio-blk device on PCI bus 0` quoted.
**Item 7** — `checkdisk.py --store` (test 4, `-smp 4`): `check_argv_7` (the
cage, `-cpu IvyBridge`, the display, one `ide-hd` on `ide.1` and no other
device, every drive under `stage7/out/`, no virtio drive — or exactly one
for the twin's frozen shape), applied to the checker's own command and to
the twin's as `metal.py` builds it; `start_mock` on `broker/metal.py`;
`check_install_germline_7` (an eighteen-line `S7:` rehearsal log that also
says the twin's virtio disk stayed all zero); `check_partitions` (both
stores cut from the disk and judged by the frozen `check_image` and
`check_home`); boots A, B and C with ring 6b's step lists and counts
replayed on SATA, plus this ring's own: the table byte-exact after A and
C, the twin's disk holding `after` on its notes partition with its virtio
image all zero, the whole disk byte-identical across B. `test.sh` gains
test 4 with its self-assertions on the cage, the machine, the display and
the disk strings. Proven on the host: the two argv checks pass on the
real commands and name a stray virtio drive. **Red on the item 1 copy**:
both argv checks pass, the fixtures and plans pass, the mock comes up,
boot A never reaches ready — `ERR: no virtio-blk device on PCI bus 0`.
**Item 8** — the freeze: `PROTECTED` grows `stage7/DISK.md`,
`stage7/test.sh` and `stage7/checkdisk.py` (A3: `broker/metal.py` joins at
item 10); the hook's comment says why; `payloads.py` gains the ring 7a
group — the battery on each path, the `write` denials, a heredoc and a
`sed -i` denied, the allowances (the gate, the checker's modes, the mock
and the real broker, the hand rehearsals, the Stage 7 QEMU lines of the
oracle, the checker, the gate's virtio boot and the twin, the disk and its
copies under `out/`, the two host witnesses, the probe) and the denials (a
SATA drive outside `out/`, a shorthand); the "next stage's test file" case
moved on to `stage8/test.sh`. **1302 payloads, 892 denied, 410 allowed, 0
wrong**; the freeze demonstrated live with one denied append to DISK.md.
The gate whole on the item 1 copy, for the record: test 1 PASS, tests 2,
3 and 4 FAIL, exit 1. Part 1 is done: tests 1–4 exist, 2–4 are red, and
every criterion but the twin's module is frozen. Part 2, the guest, begins
at item 9.

**Part 2 so far — item 9** (`stage7/stage7.asm`): the AHCI driver —
`pci_scan` matching class `0x010601` into `ahci_bdf` (its virtio-blk
branch gone), `ahci_find` (the command register owned before BAR5 is read,
the ABAR mapped uncached, `AE` set and `IE` clear, `CAP` and `PI` into the
obs page at `0x2C0`), `ahci_port_stop`/`ahci_port_open` (ST then FRE
awaited clear, the list, the FIS area and the table zeroed, `SERR` and `IS`
cleared, `IE` masked, FRE then ST once the task file is idle), `ahci_cmd`
(slot 0, a 20-byte H2D FIS, one PRD of 512 bytes, `PxCI` polled with PIT
breaths and bounded, `TFES` and `ERR` named), `ahci_identify` (LBA48 from
words 100–103, the sector size checked), `ahci_rw` (`READ`/`WRITE DMA
EXT`); DISK.md's selection rule in `disk_select` — every implemented port
with `DET` 3 and `IPM` 1 (a Phy still coming up given a bounded wait, an
empty port passed at once) and the SATA signature opened, identified,
classified by `disk_classify` (two sectors read; blank, other, or
`gpt_validate`'s germos/gpt/torn by the recognition rule — the header's
fields and CRC, the array read and its CRC, every entry zero or inside the
usable range, the first entry of each type into the descriptors) and
stopped again; the first germos port chosen, else the first blank (item
10's writer; at item 9 the stub falls to the refusal), else `ERR: no
GermOS disk and no blank disk - port 0: other, port 1: blank` naming each
port through `word_string` (RIP-relative leas — a first draft's table of
`dq` addresses in data printed nothing, relocations being stripped: the
standing gotcha, met again); `crc32_update` bit by bit; the two partition
descriptors, `blk_rw` over them with Stage 3's signature, `disk_rw` and
`home_rw` unchanged for their callers; the disk line; the virtio-blk
driver, its two device blocks, their rings and the request header gone,
the NIC's virtio plumbing kept. The binary is 36,864 bytes still. **Probed
by hand on private copies:** a host-partitioned disk (DISK.md's `build_gpt`
on the host) at `-smp 4`, `2` and `8` — seventeen lines with `S7: disk port
1 131072 notes 2048 home 34816`, the table recognised (the guest's CRC
agreeing with zlib's on the header and the 16 KB array), `notebook
formatted`, `home 0 apps`; `remember me` typed, the notes partition
holding it byte-exact per NOTEBOOK.md at LBA 2049, the home partition
formatted, the table untouched; the same disk again — `notebook 1 notes`,
the note above the prompt on the screen through the frozen
`check_region_rows`, the disk byte-identical across the reboot; a blank
disk refused `port 0: other, port 1: blank` and left all zero; the foreign
disk refused `port 0: other, port 1: gpt` and left byte-identical; the
twin's shape (a blank virtio disk beside the host-partitioned SATA disk) —
seventeen lines, the SATA stores formatted, the virtio image all zero; the
twin through `metal.py` on this image — its blank disk refused by name,
`virtio notes.img: untouched, all zero`, `the twin did not boot` (nine of
nine is item 10's, once the guest can write the table). A second defect of
the first draft, for the record: `gpt_validate`'s entry loop used R12,
the port loop's index — port 1 was never recorded; the validator now saves
it. The frozen `judge`'s log line says "S6: lines" whatever the prefix; the
count it reports is this twin's. **The gate on this binary: test 1 PASS;
tests 2, 3 and 4 FAIL on the writer alone** — every one starts from a
blank disk and this binary refuses one by name; test 2's foreign boot
already passes its own check (the refusal, the disk byte-identical, the
boot image untouched).
**Item 10** — the writer: `gpt_write` (a blank disk of fewer than 67,617
sectors named `disk too small for the two partitions` before any write;
the protective MBR built in a buffer, the entry array from the document's
256 bytes and zeros with its CRC, the primary header by `gpt_build_header`
— every field, the disk GUID, the CRC over the 92 bytes with its field
zero — LBA 0, 1, 2–33, `N−33` … `N−2` and the backup header at `N−1`
written one command each, sector 0 of both partitions written as zeros,
`S7: gpt written`); the selection rule's second case takes the blank
port's count for the writer and then re-opens and re-reads the disk
(`gpt_read`: a table just written that does not read back as GermOS is a
named error). **Probed by hand first** on private copies: a blank disk at
`-smp 4` — eighteen lines, `check_boot_lines` clean, the thirty-six
table sectors **byte-identical to `build_gpt`**, `remember me` on the
notes partition byte-exact, the home formatted and empty, every other
sector of the disk zero; the same disk at `-smp 2` — seventeen lines,
`notebook 1 notes`, byte-identical across the reboot; a 32 MB disk —
`ERR: disk too small for the two partitions`, the disk still all zero;
**the twin through `metal.py` — nine of nine** in 14.1 s, `notebook:
['after'] on the notes partition at LBA 2048`, `virtio notes.img:
untouched, all zero`; the echo build against its plan's five tests in the
same twin — all five `ok`, the hook found nothing, 17.2 s. Then
`broker/metal.py` frozen (A3): `PROTECTED` gains it, `payloads.py` its
battery, the `write` denial, a heredoc and a `sed -i` denied, `git add` at
its freeze allowed, `stage8/metal.py` allowed — **1324 payloads, 910
denied, 414 allowed, 0 wrong**, the freeze demonstrated live with one
denied append. **The gate whole: ALL FOUR AUTOMATED TESTS GREEN** — test
2's five boots (the table byte-exact on the blank disk, the recognised
disk untouched, the virtio image beside the SATA disk all zero, the
foreign table refused by name), test 3 at `-smp 2` and `-smp 8`, test 4
at `-smp 4` (echo installed at LBA 34825 through a twin whose own disk
held its note on SATA with its virtio image all zero; the launch with no
broker from the partition; the liar refused; both extents of the undo
hash-checked from the host; screen D the truth). **The regression chain
on their own binaries: Stages 0–5, ring 6a, 6b and 6c all PASS** (14, 182,
77, 92, 102, 230, 383, 395 and 207 s).
**Item 11** — this handover to the green-pending-oracle state; CLAUDE.md's
build block gains `./stage7/mkimage.sh`, `./stage7/test.sh` and
`python3 broker/metal.py --mock`, the windowed command its Stage 7 shape,
and three gotchas; README's Stage 7 paragraph and its ring 7a running
section; the payload table re-run, 1324 cases, 0 wrong; the two commands
above for Wajira. The probe artefacts stay under `stage7/out/probe7a/`
(gitignored) for the review; nothing frozen touched.

## Ring 7b — the wire · opened 15 September 2026

`stage7/plan-7b.md` was approved on 15 September 2026 with Cowork's five
amendments (A1 the relay's `SO_REUSEADDR` and flushed log lines; A2 its
teardown never raises, RST or FIN both "no answer"; A3 the bind battery's
three fixed addresses; A4 the errors byte honoured in `e1k_poll`; A5 the
ports carried to ring 7c) and every deviation accepted. **The model for
this ring: Fable 5.1 at high effort**, the owner's decision in the spec;
Cowork reviews to the same standard as every ring. Item 0 (this record,
the plan's commit) is done; the items follow one commit each, exactly as
the plan says.

**The shape, from the plan** (its environment table holds the measured
facts behind every choice): an e1000e-family driver per the 82574
datasheet beside the virtio-net driver, the e1000e preferred by kind —
found by vendor `0x8086`, class `0x0200` and a table of three ids
(`0x10D3` the twin's 82574L, `0x1502` the HP's 82579LM, `0x1503`), BAR0
mapped uncached, `IMC`/`RST`/`IMC`/`ICR` before anything is trusted, the
MAC from `RAL0`/`RAH0`, `SLU` set and `STATUS.LU` awaited for ten seconds
or `ERR: nic link did not come up within 10 s`, sixteen legacy receive
descriptors over the virtio driver's buffers offset by its twelve-byte
header and eight legacy transmit descriptors, polled, interrupts masked,
INTx off; `S7: nic 6c:3b:e5:3b:86:45` then `S7: link up` — **nineteen
lines on a blank disk, eighteen on a recognised one**, `link up` on the
e1000e path only so ring 7a's frozen gate stays green on the same binary;
the TCP stack above `net_send` and `net_poll` untouched. `broker/relay.py`
(unfrozen, the spec's word) listens on `10.0.2.4` or `127.0.0.1` and
nothing else, forwards each connection to the frozen broker on
`127.0.0.1:9999`, and logs one JSON line per connection; **in the twin it
sits on 9997** (9998 is the frozen twin's own listener), the gate's
`guestfwd` names it, and every gate boot that reaches the broker goes
through it. `broker/wire.py` subclasses `metal.py` — the e1000e on a
second restricted netdev `n1` through `rehearse_metal`'s `extra_args` and
`lines` seams, nineteen lines, the rehearsal's listener reached direct on
9998 — and `metal.py` is not edited. A short frozen `stage7/WIRE.md`
carries the lines, the relay's contract and its log line. The gate
`stage7/test-7b.sh` and `stage7/checkwire.py` at 1920x1080 on IvyBridge
with the SATA disk: ten boots and two rehearsals, mock only. Test 1 is
green from item 5 (the artefact is 7a's until item 9); test 2 goes green
at item 9, tests 3 and 4 at item 10, when `broker/wire.py` freezes after
nine of nine through it.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image | **PASS** |
| 2 | Serial — nineteen `S7:` lines on a blank disk with `nic 6c:3b:e5:3b:86:45` and `link up`, the table byte-exact from the host; eighteen on the same disk, byte-identical afterwards; the e1000e preferred beside a virtio-net carrying its own MAC; the link taken down through the monitor before the guest runs — fourteen lines to the nic line, then `ERR: nic link did not come up within 10 s` at 11.5 s, no link line, no keyboard, one `S7: alive`; at `-smp 8`, `4`, `2` and `2` | **PASS** |
| 3 | The question on e1000e — `? ping`, `keep this`, `? hello` through the relay on 9997 and the mock on 9999 at `-smp 2`, `4` and `8`: nineteen lines, the echo exact, the record's two frames, the relay's log `up 8/9 down 8/62` agreeing with it, the note alone on the notes partition, the conversation on screen, the strip the obs page, `wire_conns` the relay's count, the byte counters never below the relay's | **PASS** |
| 4 | The cage holds — both cage strings and both argv checks (one restricted cage to the relay with the e1000e on n0; the twin's two cages to 9998 with the frozen virtio-net on n0 and the e1000e on n1); the relay refusing `0.0.0.0`, `10.0.2.2` and `192.0.2.1` before any socket exists and listening on `127.0.0.1`; the mock-down run at `-smp 8` — `no answer from the broker`, the note journaled, one refused connection in the relay's log; `! test app` and `! install echo` through the relay at `-smp 4` — the record (calls 1 and 2), the relay's log `up 13/17 down 708/221`, two germline entries with nineteen-line rehearsal logs carrying `link up` and the virtio disk untouched, echo at partition sector 9, the twin's disk with `after` on SATA, screen A, `grows_generated 2 grows_served 0`; the reboot with 9999 and 9997 closed — eighteen lines, `home 1 apps`, echo launched showing `b` with `wire_conns 0` and the byte counters unchanged, the disk untouched | **PASS** (after item 10b) |
| 5 | **Oracle — Wajira, real broker behind the relay** — `? ping` and `! make me a clock` | **PASS — confirmed 15 September 2026** |

**On this build** (15 September 2026): the binary is 36,864 bytes, ring
7a's size; the e1000e is `00:03.0` in the twin's order and `00:02.0`
alone (`8086:10d3`, BAR0 `0x810a0000`, 128 KB, below 4 GB); the reset
self-clears at once and `STATUS.LU` is set at once in the twin, so the
ten-second wait costs nothing when the link is up and exactly ten seconds
when it is not; a question over the e1000e through the relay to the mock
lands in `w 001` with 5–11 ms of wire wait; the gate is ten boots plus
two rehearsals, 314 s; the twin's rehearsal 14.3 s for the
test app and 17.4 s for echo against its plan; the payload table 1444
cases, 0 wrong.

**Caveats carried forward:**

- **Everything ring 7a carried.**
- **The twin's 82574L is not the HP's 82579LM.** Link-up on the metal is
  the one thing the twin cannot prove; the MDIC and the EEPROM are not
  touched; `SLU` set, the forced speed and duplex cleared, the PHY left to
  autonegotiate. `link up` is the last line before `ready`, its timeout a
  named error, and the fix is a ring 7c item with the datasheet open.
- **Legacy descriptors on one queue, sixteen receive and eight transmit,
  polled; no MSI, no offloads, no VLAN, no multicast (`MTA` zeroed, `BAM`
  set), no link-change handling after boot** — a cable pulled after
  `ready` is a failed question by UMBILICAL.md's rule, never a halt.
- **The receive buffers are the virtio driver's, offset by twelve bytes;
  safe because `LPE` is clear** (frames over 1522 bytes are discarded by
  the device). The virtio-net driver stays in the binary and is the path
  ring 7a's gate exercises.
- **The relay serves one connection at a time**, speaks plaintext on the
  home LAN by the owner's choice, and logs bytes per connection; whether a
  refused broker gives the guest a RST or a FIN is a race and both are "no
  answer" (A2). TLS at Stage 8 or the ring where traffic first crosses a
  network the owner does not own.
- **`grows_served` counts app frames whose `source` byte is 1** (GLASS.md);
  a fresh germline makes it 0 after any number of generated frames — the
  number item 10b corrected.
- **For ring 7c:** the HP's firmware may leave `CAP.SSS` set, so a port
  may need `PxCMD.SUD` before its disk appears — no code this ring.
- **The ports, as this ring settled them (A5):** in the twin the relay is
  `python3 broker/relay.py --bind 127.0.0.1 --port 9997` and every 7c QEMU
  line's `guestfwd` names 9997, not the spec's 9998; on the HP's day the
  relay is `python3 broker/relay.py` with no flags (its defaults are
  `10.0.2.4` and 9999) beside the broker on `127.0.0.1:9999`, and
  `METAL.md` step 5 will say so; the spec's ring 7c twin command is
  corrected at the 7c gate.
- **The 82579LM's PHY** may need MDIC work the twin never exercises; `link
  up` is the last line before `ready`, its timeout a named error.

### Ring 7b — the build, item by item

**Item 0** — this record; `stage7/plan-7b.md` committed verbatim.
**Item 1** — the environment, measured on private copies under
`stage7/out/probe7b/` (gitignored) with a temporary probe spliced into a
copy of the source (never into `stage7/stage7.asm`, never committed); no
source changed, nothing frozen touched:

| Fact | Measured how |
|---|---|
| **Ring 7a's binary boots in this ring's twin shape** — `-cpu IvyBridge`, the SATA disk on `ide.1`, the frozen virtio notes disk, the frozen `virtio-net-pci` on `n0` and **the e1000e on a second restricted cage `n1`** (mac `6c:3b:e5:3b:86:45`), 1920x1080 — to `S7: keyboard ready` with **eighteen** lines at `-smp 2`, `4` and `8`, the nic line the virtio device's `52:54:00:12:34:56`, the e1000e ignored, `console 120x67`, the disk formatted as ring 7a's. **`S7: alive` at 1.25–1.30 s and ready at 1.45–1.55 s from QEMU's start with iPXE's option ROM present; 1.10 s and 1.20 s with `rombar=0`** — the ROM costs about 0.15 s and changes no line and no boot order, so the gate keeps it (the faithful twin: the HP's firmware carries an Intel driver of its own) | `stage7/out/probe7b/boot.py`, four boots |
| **The e1000e is `00:03.0`** (BDF `0x1800`), device id **`0x10d3`**, command register **`0x0007` — memory, I/O and bus mastering already on**, left so by the firmware; **BAR0 = `0x810a0000`**, a 32-bit memory BAR below 4 GB (inside the identity map; `map_mmio_2m` remaps its 2 MB pages uncached), the write-ones probe answering `0xfffe0000`: **a 128 KB region** | the probe's PCI scan by vendor and class |
| **What the firmware and iPXE's ROM left in the registers:** `CTRL` `0x00140261` (FD, ASDE, SLU, speed 1000), **`STATUS` `0x00080283` — `LU` already set**, FD, speed 1000; `CTRL_EXT` 0; **`IMS` 0, `RCTL` 0, `TCTL` 0, every ring register 0** — nothing initialised the device for traffic, or it was torn down cleanly; `TIPG` `0x00602008` (the reset default, the value the plan writes); `RXDCTL` `0x00010000`, `TXDCTL` 0; `RXCSUM` `0x0300`; **`RFCTL` 0 (legacy descriptors) and `MRQC` 0 (one queue)** as the plan assumes; **`RAL0` `0x3be53b6c`, `RAH0` `0x80004586` — `AV` set, the six bytes the harness's MAC** `6c:3b:e5:3b:86:45` | the probe, BAR0 mapped uncached |
| **The reset:** `CTRL.RST` self-clears within the first read (**0 breaths**); `ICR` reads 0 after; `CTRL` after reset `0x00140241` (ASDE cleared, **SLU still set** — QEMU's reset default), `STATUS` **`0x00080283` — `LU` set at once, 0 breaths after the reset alone and 0 after SLU is written**; `RAL0`/`RAH0` unchanged by the reset (`AV` still set, the MAC intact) — the reset-then-read order the plan chose is safe | the probe: `IMC`, `RST` awaited, `IMC`, `ICR`, then `STATUS.LU` polled |
| **`set_link e1000e.0 off` before `cont` holds the link down for good:** `STATUS` `0x00080681` at handover and `0x00080281` after the reset — **`LU` clear** — and both link polls ran to their bound: **`0xc350` = 50000 breaths each**, `LU` still clear after; the two ten-second waits took the guest from 1.30 s to ready at 21.69 s, so **50000 breaths of `PIT_200US` is ten seconds on this host**, the bound the plan wrote | the probe booted paused, the link taken down through the monitor, then `cont` |
| The probe's guestfwd used a throwaway port (9996); the gate's ports were never touched; no packet left the cage | `boot.py` |

**Items 2–8** — `stage7/WIRE.md` (item 2); `broker/relay.py` proven on
the host with `stage7/out/probe7b/relay_proof.py` (item 3: the bind rule,
a ping through it, the port clash a loud exit, a refused broker a RST and
a logged error, a restart in TIME_WAIT); `broker/wire.py` (item 4: the
twin's command with two cages and four devices, the mock with no image,
and the real rehearsal of the test app on ring 7a's binary failing "the
twin did not boot (ready True, 18 S6: lines, want 19)" in 14.3 s — the
ring's reason); `stage7/test-7b.sh` with test 1 green and test 2 red
(item 5); `stage7/checkwire.py --down` and `--question`, test 3 (item 6);
`--cage`, test 4 (item 7) — the gate whole on ring 7a's binary: test 1
PASS, tests 2–4 FAIL on the missing driver; the freeze (item 8): three
paths into `PROTECTED`, **1421 payloads, 964 denied, 457 allowed, 0
wrong**, one append into WIRE.md denied live.

**Part 2 so far — item 9** (`stage7/stage7.asm`): the e1000e attached —
`pci_scan` matching vendor `0x8086`, class `0x020000` and the three-id
table into `e1k_bdf` (the virtio-net and AHCI branches kept); `nic_find`
choosing by kind into `nic_kind`; `e1k_attach` — the command register
owned before BAR0 is read, BAR0 (32- or 64-bit) mapped uncached, `IMC`,
`CTRL.RST` awaited, `IMC`, `ICR`, the MAC from `RAL0`/`RAH0` with `AV`
required, `SLU` set with the forced bits cleared, `STATUS.LU` awaited
50000 breaths, the MTA zeroed, sixteen legacy receive descriptors over
the virtio buffers offset by twelve, `RDBAL`/`RDLEN`/`RDH`/`RDT`,
`RFCTL.EXSTEN` clear, `MRQC` 0, `RCTL` EN|BAM|SECRC, the tail to 15,
eight transmit descriptors, `TDBAL`/`TDLEN`/`TDH`/`TDT`, `TIPG`, `TCTL`;
`net_send` and `net_poll` dispatching on `nic_kind` (the send a named
stub this item); the strings and the BSS. The binary is 36,864 bytes
still. **Probed by hand on private copies:** nineteen lines with `S7: nic
6c:3b:e5:3b:86:45` and `S7: link up` at `-smp 2`, `4` and `8` on the
e1000e alone (ready at 1.30–1.40 s), the same with the virtio-net beside
it in the twin's order, the link-down boot ending in `ERR: nic link did
not come up within 10 s` at 11.5 s and halting. **The gate: tests 1 and 2
PASS** (the four boots, the down boot's error at 11.5 s inside the 45 s
clock); **tests 3 and 4 FAIL on the stub alone** — `ERR: e1000e send not
yet written` at the first question. **Ring 7a's gate on this binary: all
four PASS** (the virtio path, eighteen lines).

**Item 10 — STOPPED at the commit boundary, one wrong number in the
frozen checker; the diff unapplied for the owner's hand.** The guest is
complete: `e1k_send` (one legacy descriptor, EOP|IFCS|RS, the tail moved,
`DD` awaited five seconds or `ERR: nic transmit timed out`) and
`e1k_poll` (the head descriptor's `DD`, the errors byte honoured — A4 —
EOP and the length required, the frame dispatched by EtherType from the
shared buffers, the descriptor cleared and handed back through `RDT`, the
head advanced; R12–R14 preserved) replace the item 9 stubs; the block
moved below the wire section's defines (the positional-`%define` gotcha,
met once). The binary is 36,864 bytes still. **Probed by hand on private
copies** (`stage7/out/probe7b/ask.py`): `? ping`, a note, `? hello` over
the e1000e through `relay.py` on 9997 to the mock on 9999 at `-smp 4` —
nineteen lines, no `ERR:`, both answered, the relay's log `up 8 down 8`
and `up 9 down 62` agreeing with the record, the obs page `questions 2
notes 1 wire_conns 2 wire_wait 11 ms bytes_in 782 bytes_out 665`; the
mock stopped — two refused connections in the relay's log, `errors 2`,
the note journaled between them; **the twin through `broker/wire.py` —
nine of nine** for the test app (14.3 s, `'after'` on the notes
partition, the virtio image all zero) and for echo against its plan's
five tests (17.4 s, the hook found nothing). Then `broker/wire.py`
frozen (deviation 10): `PROTECTED` gains it, `payloads.py` its five
cases — **1444 payloads, 982 denied, 462 allowed, 0 wrong**, one append
into the module denied live.

**The gate chain on this binary** (`stage7/out/wire.chain10.log`):
`./stage7/test-7b.sh` **tests 1, 2 and 3 PASS**; **test 4 FAIL on one
number** — every assertion of (a) to (f) passed (the argv checks, the
bind rule, the mock-down run with its refused connection logged, the grow
and the install through the relay with the record, the relay's log `up
13/17 down 708/221`, the two nineteen-line rehearsal logs with `link up`,
the home partition, the twin's disk, screen A, the launch with nothing
on the wire) except `after the install: the obs page's grows_served is 0,
want 2`. By GLASS.md `grows_served` counts app frames whose `source`
byte is 1; both frames came generated from a fresh germline, so the
guest's `grows_generated 2, grows_served 0` is the truth and the frozen
checker's `2` was written from arithmetic, not from a run — ring 6b item
10b's class, again. **The one-line diff is at
`stage7/out/checkwire.item10b.diff`, unapplied**; the owner applies it,
then `./stage7/test-7b.sh` whole. 313 s for the gate as it ran. **The
regression chain, all green on their own binaries and this one:**
`./stage7/test.sh` (458 s, the virtio path), `./stage6/test.sh` (383),
`test-6b.sh` (395), `test-6c.sh` (207), Stages 5–0 (230, 102, 92, 76,
183, 13 s).

**Item 10b — the freeze opening, by the owner's hand.** Wajira applied
`stage7/out/checkwire.item10b.diff` exactly, at the repo root:
`stage7/checkwire.py`'s one wrong number, `grows_served` 2, became 0 —
the count GLASS.md's rule gives after two generated frames — and ran
`./stage7/test-7b.sh` whole: **all four automated tests PASS.** The
payload table re-run, 1444 cases, 0 wrong, no path changed. **This is the
project's sixth freeze opening** (by the owner's count of 28 September 2026), after Stage 5 item 8b, ring 6a item
12b, ring 6b item 10b, ring 6c item 11b and ring 6c item 12c, and its class is ring 6b
item 10b's again: a count in a frozen test written from arithmetic, not
from a run. The gotcha already stands in CLAUDE.md ("write the
expectation from a run, never from arithmetic"); this ring adds its
second form at item 11 — a counter whose rule lives in a frozen document
is looked up there before the number is typed, and a number no run can
give before the freeze is written as the rule, not as a guess.

**Item 11** — this handover to the green-pending-oracle state; `CLAUDE.md`'s
build block gains `./stage7/test-7b.sh`, `python3 broker/wire.py --mock`
and `python3 broker/relay.py --bind 127.0.0.1 --port 9997`, the windowed
command its ring 7b shape (three terminals), and two gotchas (a counter's
rule lives in its frozen document — the item 10b class; NASM's positional
`%define` in its other form — a block moved above its constants); README's
Stage 7 paragraph and its running section gain ring 7b; the gate re-run
whole on the applied checker (314 s, all four PASS); the payload
table re-run, 1444 cases, 0 wrong; the three commands below for Wajira. The
probe artefacts stay under `stage7/out/probe7b/` (gitignored) for the
review; nothing frozen touched.


## Ring 7d — the trials · opened 22 September 2026 · closed 25 September 2026

`stage7/plan-7d.md` was approved on 22 September 2026 with Cowork's four
amendments (A1 the prefix `trial ` reserved on the notebook and refused at
the prompt; A2 every block line's median recomputed from its ten hits by
`trials.py` and compared exactly; A3 the ±30 ms window on the median is
the spec's and is never widened by CC — a spread it cannot hold is a spec
question; A4 the three Stage 7 gates once per commit, inside test 4 where
the gate is expected green) and every deviation accepted. **The model for
this ring: Fable 5.1 at medium effort**, the owner's decision at the
kickoff. Item 0 (this record, the plan's commit) is done; the items follow
one commit each, exactly as the plan says.

**The shape, from the plan:** GermOS runs an N-of-1 crossover on its own
human — the choices row as text (layout A, today's row to the pixel)
against the same items as boxes (layout B: `⌊C/n⌋`-cell boxes with a gap
column, the inverse of the strip's colours, the label centred); a cue
`click: <word>` in the conversation panel, the click on the cued item a
hit timed from the frame that painted the cue to the press's interrupt,
any other press a miss; ten cues a block from a fixed table, eight blocks
`ABBA BAAB` / `BAAB ABBA`, one sitting a boot, three `done` sittings to a
verdict by a sign test at ten of twelve with misses not worse; every event
a note (`trial …`, NOTEBOOK.md unchanged) and a raw serial line
(`trial: …`); the verdict on the notebook and `layout_default` read from
it at boot; `! trial` a reserved word answered before the home lookup and
the broker, refusing `no mouse`, `an app is running`, `one sitting a
boot`, `trial concluded`; mode 5 `trial A 3/8` on the strip; sixteen obs
words from `0x2E0`. The four new files — `stage7/TRIALS.md`,
`stage7/trials.py`, `stage7/test-7d.sh`, `stage7/checktrials.py` — are
frozen at item 8; the GLASS.md section (`stage7/glass-7d-section.md`) goes
in by the owner's hand at item 9. Every gate run appends to
`stage7/out/gate-7d.log`.

| Test | State |
|---|---|
| 1 — the artefact, the stick, TRIALS.md parsed cold, the worked examples | **PASS** (item 4 on) |
| 2 — the refusal, both layouts' rows, the cue | **PASS** (item 11) |
| 3 — a sitting predicted, the abort, three sittings to a verdict, the default, the reserved prefix, a click on a box | **PASS** (item 11) |
| 4 — the freeze, the argv check, the payload table, the three Stage 7 gates | **PASS** (item 8 on) |
| 5 — Wajira's: three sittings on the HP's notebook (the owner's pre-registration, 24 September 2026); the twin's sitting a rehearsal | **rehearsal done 24 September 2026** (the twin, `done`, not trial data); **HP sittings 1, 2 and 3 PASSED 24 September 2026** (the owner's word on each); **verdict A** (B 8 of 12, ten needed; misses A 4, B 0; the owner's word 25 September 2026; the verdict boot: `trial concluded`) — **PASS**; the ring CLOSED 25 September 2026 |

**Carried into this ring:** everything Stage 7 carried (the PHY speed
after a reset, TIPG, WIRE.md's halting sentence, the nineteen-line first
boot never watched on the metal, the x2APIC and trampoline paths); the
trial's clock is the TSC calibrated once against the PIT; the sitting line
does not say where a sitting ran (deviation 7 — the owner's record does).

### Ring 7d — the build, item by item

**Item 0** — this record; `stage7/plan-7d.md` committed verbatim; the
"Where we are" rows for Omarchy and this ring.
**Item 1** — the environment, measured on the closed binary (item 21,
40,960 bytes) booted from a stick copy with a blank SATA disk under
`stage7/out/probe7d/` (gitignored), nothing listening, `-smp 4`; no source
changed, nothing frozen touched, no Claude call:

| Fact | Measured how |
|---|---|
| **The monitor's clocks under QEMU 11.1.1:** one `xp` of the whole `0x360`-byte page takes **50 ms** (the first 101 ms), one `xp` of a single qword **50 ms** too — `Driver.xp`'s drain sets the floor, not the size; a key's round trip `sendkey` → its echo byte in the `-serial file:` capture, polled at 5 ms, is **5 to 20 ms**; a `mouse_button 1` is seen in `packets` within **100 ms** (two qword reads). So the synthetic human's per-cue trigger cannot be a page read (50 ms a poll, 500 ms pause) and is the guest's own `trial:` line in the serial file at a 5 ms poll, as the plan's decision 6 says; the page is read once per rest and at `done` | `stage7/out/probe7d/probe1.py` |
| **The pointer's own input-to-photon on this host:** after twenty monitor moves `pointer_last` **2.04 ms**, `pointer_worst` **16.16 ms** — one frame slot at worst, the term the ±30 ms window absorbs | the obs page through `xp` |
| **`S7: keyboard ready` at 1.4 s** from QEMU's start on the stick copy (7c's number holds); the page's words at `0x2C0`–`0x2D0` read `0xc0141f05`, `0x3f`, `0x1` (DISK.md's `ahci_cap`, `ahci_pi`, `ahci_port` — the trial's fields must start above them, deviation 1) and **`0x2D8`–`0x360` is all zero** on the closed binary | the same |
| **A full notebook's replay is cheap:** 300 notes written from the host by NOTEBOOK.md's format into the notes partition (LBA 2048 + *n*), the next boot says `S7: notebook 300 notes` and the conversation's cursor word settles at `0x803e0002` (row 62, column 2 — the prompt) **within 0.3 s of ready** (an upper bound: three 50 ms reads agreeing). Three sittings leave about 280 notes; the checker's settle after ready stays 7c's one second | `checkdisk.parse_notebook` on the image; `xp` of the descriptor's cursor word |
| **The frozen seams on mode 5 and inverse cells, run not read:** `glass.mode_word(5, "")` returns `'?'` padded to 18 — so `strip_rows_6c` and `check_strip_6c` cannot judge a strip in mode 5, and `trials.py` renders the mode word itself; `twin.cell_pixels(font, 0xA0)` renders **background** (16 rows of `BG`) — an inverse cell would fail the twin's criterion 7, and never reaches it: the twin's SATA disk is formatted fresh per rehearsal (`wire.py`'s `twin_extra_args`) and the twin never types `! trial`; `checkglass.check_mode_field` takes any word and pads to 18 | `probe1.py` |
| **The hook today** on every command shape this ring will run, fed as payloads by `stage7/out/probe7d/verdicts.py`: `Write` on the four new names and on `stage7/glass-7d-section.md` **allowed**; running `trials.py` (`--disk`, `--example`, `--serial`), `test-7d.sh` (bare and piped), the checker's four modes and `checkmetal.py --stick` allowed; the probe's stick copied over `stage7/out/stick.img`, the scratch wipe, the log's `>>` and `tail`, `git add` of the four paths with the hooks, `git commit -F`, `nasm` on the probe copy, the ring's words in prose: all allowed; **`sed -i` on `checktrials.py` and `echo x > stage7/TRIALS.md` allowed today — test 4 is red by design until item 8**; `cat stage7/glass-7d-section.md >> stage6/GLASS.md` **denied** (GLASS.md is frozen; the append is the owner's hand, item 9) | `verdicts.py` |

**Item 2** — `stage7/TRIALS.md`: the one text (the design, the sitting
step by step, the verdict rule, layout B, the notes, the serial lines,
mode 5, the obs page from `0x2E0`, the panel's table, two worked examples,
the Python). The spec corrected in two places, stated in the document:
the obs fields from `0x2E0` (DISK.md owns `0x2C0`–`0x2D0`) and a click on
the `! grow` box typing `!`. Cross-checked by the item 3 tool before its
commit: both examples reproduced.
**Item 3** — `stage7/trials.py`: executes the document's Python as its
own definitions and compares them with the document's tables (the cue
table, the orders, the obs rows, the zero rule), so the two cannot drift;
`--example` reproduces both worked examples (A's 93 notes, table and
serial lines; B's verdict B by 10 of 12 with misses 2 against 2 over
sittings 1, 3, 4; a block median altered by one refused with the block
named); a document with one cue row edited to repeat an item is refused
at import; `--disk` on the 7c gate's disk prints `no sittings`; `--serial`
on a scratch log of the `trial:` lines prints example A's table.
**Item 4** — `stage7/test-7d.sh` with test 1, the log and test 2;
`stage7/checktrials.py` with `--document` and `--row`: the log
(`stage7/out/gate-7d.log`, a dated header per run, `tee` on every line),
the port refusals, the build, test 1 (the PE checks, the frozen
`checkmetal.py --stick` run as it is, `--document`), test 2 (`--row`, one
boot: the mode-3 refusal through the mock's `test app`, the sitting's
start with layout A's row to the pixel and the cue, block 1 played by the
synthetic human, block 2's row as TRIALS.md's boxes in the surface's
bytes and on the screen). The checker's driver is 7c's skeleton with the
`play` step; the synthetic human (`Human`) anchors every press on the
guest's own `trial:` line in the serial file at a 5 ms poll and parks its
hand on the next target during the pause (plan decision 6); its four
timing constants are `None` until the item 7 run and it refuses to play
while any is unset. One number in TRIALS.md corrected before the freeze
while writing the checker: the last box is thirty cells wide, so `Esc
exit` sits at 101–108, not 100–107 (the rule was right, the example's
arithmetic was not — the checker computes the columns by the rule).
**Test 1 green; test 2 red by design** (the constants unset; on the closed
binary `! trial` would go to the mock as a grow and no `trial:` line
would appear).
**Item 5** — `checktrials.py --sitting` (test 3): the four scripts
(`SCRIPT_1` three misses, `SCRIPT_ABORT` Esc after three cues of block 3,
`SCRIPT_3`, `SCRIPT_4`; A blocks' delays with median 300, B blocks' 200),
five boots on one disk, every expectation the script expanded by
`trials.py` (`notes_of` on the expected ms — `d`, or `2d` for a cue
missed first, plus `OFFSET_MS`), every hit inside the per-hit window,
every block median inside the spec's ±30 ms of the rule over the expected
ms, `check_blocks` on every record (A2), the serial `trial:` lines equal
to the notes, the page at every rest, the tables in the app panel, the
verdict B by the rule over sittings 1, 3 and 4, layout B at the prompt,
the reserved prefix refused with the notebook unchanged (A1), the click on
the `! grow` box typing `!`, `trials.py --disk` agreeing with the panels.
One correction of the plan's text while writing the script: the plan
named the second miss in "block 5 (A)", but block 5 of `ABBA BAAB` is B;
the miss sits in block 4 (A), so B's misses (1) are not worse than A's (2)
and the scripted verdict is B. **Tests 2 and 3 red by design** (the
constants unset until item 7).
**Item 6** — `checktrials.py --cage` and test 4: the harness's own
strings (7c's, with the log's path under `stage7/out/`), the checker's
command — `checkmetal.qemu_argv` itself — through the frozen
`check_argv_7c`, the frozen modules' ports and display, the payload table
as a subprocess with `0 wrong` required, the spot checks as data (every
mutation of this ring's four files denied, running the gate, the checker
and the tool allowed), then the three earlier Stage 7 gates run in turn
from `test-7d.sh` on the same source. Run whole once on the closed binary
(the log's second run): **test 1 green; tests 2 and 3 red by design; test
4 red on (c) alone** — the four files are writable today — while (a), (b)
and (d) pass: the 7c, 7b and 7a gates green inside test 4 (this is the
one run of the three gates before this commit, A4). TRIALS.md gained one
clause while the probe was drafted: no rest and no rest line after block
8 (the sitting's end follows the block note directly).
**Item 7** — the probe: the trial drafted on a private copy of the source
(`stage7/out/probe7d/stage7.asm`, spliced by `splice.py` there in two
groups — the machinery and layout B — assembled to 45,056 bytes, packed
into its own stick), the synthetic human played against it, every number
the checker needs read from the run, nothing of the guest committed (`git
diff --stat`: the checker and this file). **Measured:** a sitting of
eighty cues plays in **85.5 s**; the recorded ms minus the scripted delay,
per cue, over sitting 1's script — **a cue after a pause +31 to +49, median
39** (the hit's note is journaled, a disk write, before its serial line
anchors the next press: the guest's clock leads the human's by that
write); **the first cue of a block −16 to −1, median −8** (anchored on the
block line and the rest, no write between); a cue missed first carries a
second interval of the same shape; the residuals against that rule within
20 ms. So `OFFSET_MS = 39`, `OFFSET_FIRST_MS = -8`, `HIT_WINDOW_MS = 60`
(CC's own, A3), `READY_LIMIT_S = 60`, `SETTLE_S = 1.0`, each dated in the
checker; **the ±30 ms window on the median is the spec's and holds:** every
block median of every sitting inside it. The whole `--sitting` run (five
boots, four sittings) took **5 min 45 s**; `--row` about 2.5 min with the
mock's grow. **Three probe runs, three defects found and fixed in the
draft, none in a frozen file:** the cue's stamp sat inside the pointer's
conditional in the glass core's frame, so it fired only on frames with a
mouse packet (the second cue was never stamped); the table's last row
shared the buffer row 0 overwrote; the box builder read the labels from a
line buffer the four-item row never filled (`choices_set` takes its text
from a constant), so it reads row 0 of the choices surface, copied aside
before the fills. Three checker corrections from the same runs, before
the freeze: the echo rule is ring 7a's (`S7:`), not Stage 6's; a typed
line shows as `> …` and a cue line repeats on screen, so the conversation
checks name unique rows and read the cue lines from the surface; the
human types `! trial` itself with no gap after the Enter, so the sitting
line is timed from the key (the first cue read +195 ms with the gap
after it). **The `no mouse` refusal (deviation 3):** a second private copy
with the reset answer forced to none boots with `i8042: mouse reset ok`
and `mouse_id` 0, `! trial` prints `no mouse`, `errors` 1, `notes` 0, no
`trial:` line on serial, the journal empty (`stage7/out/probe7d/nomouse/`).
**On the probe binary: `--row` and `--sitting` both green** (the log's third
probe run); on the repository's binary tests 2 and 3 stay red by design.
**Item 8** — the freeze: `PROTECTED` grows `stage7/TRIALS.md`,
`stage7/test-7d.sh`, `stage7/checktrials.py`, `stage7/trials.py`, the
hook's comment saying why each is a criterion or a criterion's parser and
why the section file, the guest, the builders and the plan are not;
`payloads.py` gains the ring 7d group (the freeze battery on the four
paths, `Write`/`Edit`/heredoc/`sed -i`/`>>` denied, the owner's append to
GLASS.md denied to CC, the gate, the checker's four modes, the tool's
three, the log, the probe under `out/` and the ring's words allowed, a
trial disk outside `out/` denied): **1678 payloads, 1117 denied, 561
allowed, 0 wrong**; immediacy shown live — `echo x > stage7/checktrials.py`
denied by the hook the moment the paths were in. The gate whole (the log's
run at this commit): **test 1 green, test 4 green** — the payload table,
the argv check, and the 7c, 7b and 7a gates green inside test 4 on the
unchanged binary (the one run of the three gates before this commit, A4)
— **tests 2 and 3 red by design** (the repository's binary has no trial
yet).
**Item 9** — `stage7/glass-7d-section.md`: the GLASS.md section for this
ring in the 6c section's shape — the standing sentence, the three
supersessions (the page's zero rule from `0x360`; `! trial` answered
before the home lookup and the broker; the `trial ` prefix never a note,
A1), the obs table from `0x2E0` with writer and meaning, the cue's stamp,
mode 5 and its word, the inverse cell byte, layout B's boxes and the click
rule on them, the trial's press rule, and a pointer to TRIALS.md for the
rest. **The session stops here: the owner appends the file to
`stage6/GLASS.md` by his own hand** (the shell's append of the section
file onto the document, then his commit) and says it is in before the
next commit; the hook denies CC that append.
The owner appended it and committed (`6beb717`, 22 September 2026).
**Item 10** — the guest, the machinery on layout A: the probe's splice
(group 1) into `stage7/stage7.asm` — the sixteen obs defines and mode 5;
the five-byte `trial` compare in `bang_line` before the undo and the home
lookup; `trial_start` with the four refusals in order; keys dropped in
mode 5 but Esc in `handle_key`, and the reserved prefix refused at Enter
before the note path (A1); the press routed to `trial_press` from
`click_dispatch`; `trial_step` from the main loop, which no longer sleeps
while a sitting runs; the cue's stamp in the glass core's frame beside
the pointer's, every frame; `trial A 3/8` in `strip_format`; the last
verdict note read into `layout_default` in `notebook_replay`'s walk; the
four-item row during a sitting from `choices_update`; the trial section
itself — the cue, the hit and its median, the miss, the pause and the
rest, the block note, the sitting's end with the table in the app panel
and the verdict scan, the abort, the journal walk, the decimal helpers,
`note_emit` (the journal through `notebook_append`, the raw line through
`serial_raw_puts`). The binary is **45,056 bytes** (the section stepped up
one page from 40,960). The row is still layout A everywhere: layout B is
item 11. **The three Stage 7 gates run on their own on this binary** (A4:
tests 2 and 3 of this ring are red by design here) — the log's item 10
run.
**Item 11** — layout B, and the default from the notebook: the probe's
splice (group 2) — `draw_cell` swaps the two colours for a byte with bit 7
set (`0xA0` the solid cell); `choices_update`'s `.layout` tail calls
`row_to_boxes` in a B block of a sitting and, outside one, when
`layout_default` is 1 — the row just built (row 0 of the choices surface
copied aside, the hit table) redrawn as TRIALS.md's boxes with the gap
columns blank and the labels centred inverse, the hit table's spans the
filled spans; `notebook_replay` redraws the row after the walk when the
verdict said B. **All four automated tests green** on `./stage7/test-7d.sh`
(the log's item 11 run): TRIALS.md parsed cold and both worked examples;
the mode-3 refusal, the sitting's start, layout A's row to the pixel,
block 1 played, block 2's boxes in the surface and on the screen; sitting
1 predicted to the note with the three misses and every median inside the
spec's window, the abort with blocks 1–2 standing, sittings 3 and 4 to
`trial verdict B` by 12 of 12 with misses A 2 B 1, layout B at the prompt
before any packet on the next boot, `trial verdict A` typed and refused
with the notebook unchanged, the click on the `! grow` box typing `!`,
`trials.py --disk` agreeing with the panels; the freeze, the argv check,
the payload table 0 wrong, and the 7c, 7b and 7a gates green inside test
4 (A4: the one run of the three gates for this commit). **The whole gate's
wall time: 21 min (1250 s)** — into CLAUDE.md's build block at item 12. The binary
stays 45,056 bytes.
**Item 12** — this file to the green-pending-oracle state, CLAUDE.md's
build block and the windowed run's sentence, README's ring 7d, the payload
table re-run (1678, 0 wrong), the three ring 6 gates and Stages 0–5 green
on their own binaries.
**Item 13** — Cowork's pre-oracle review (23 September 2026): **fix first,
four defects, all in the unfrozen guest**, fixed in one commit. (1)
`draw_glyph` jumped into `draw_cell` past the `cell_inverse` reset but
before the colour swap, so the arrow was drawn inverse whenever the last
cell painted before it carried bit 7 — `cursor_draw` repaints the old
cell first, so an arrow leaving a box would have been inverted; the reset
now precedes the jump. **The gate cannot show this one:** its block 2
screendump has the arrow parked in the conversation panel, so **the
oracle's eye is the check** — the arrow over a box, and after leaving it,
must be the plain arrow. (2) `row_to_boxes` with a label wider than its
box's filled span computed a negative width, shifted it huge, and stored
the label far outside the surface (a narrow screen); now such a label is
cut to its first `filled` characters from the box's first column, the
target the filled span as ever — **the rule, one sentence:** *a label
wider than its box is cut to the box's filled width, from the box's first
column.* TRIALS.md is frozen and does not say it; the sentence is written
unapplied for the owner at `stage7/out/trials-md-label-rule.txt`. (3)
`trial_press` subtracted the cue's stamp from the packet's without a
compare: a packet stamped at its first byte before the cue's frame end,
consumed after it, would wrap to a huge hit; a press stamped below
`cue_stamp` is now "no cue showing" — counted in `clicks`, nothing more.
(4) `note_verdict_check` now compares bytes 4–5 against `l ` as
`journal_scan` does, so both readers of the verdict note judge the same
bytes. The binary stays 45,056 bytes. **All four automated tests green on
the fixed binary** (the log's item 13 run, 21 min (1248 s)), the three Stage 7 gates
inside test 4 (A4).
**Item 13b** (`1020754`, the owner's hand, 23 September 2026) — **the
project's eighth freeze opening** (by the owner's count of 28 September 2026), from Cowork's pre-oracle review: the
frozen `stage7/checktrials.py` now records a failed monitor read after
boots 1 to 4 of `--sitting` as a problem instead of skipping it, and keeps
the missing-verdict message. **Item 14** — the gate run whole on the
patched checker: all four automated tests green, 21 min (1249 s) (the log's item 14
run).

**Test 5 — the rehearsal in the twin (24 September 2026, Cowork on Opus 5.5
at high effort).** *The record first:* before the run the owner decided
that **the trial is three sittings on the HP's notebook** and this sitting
is the protocol rehearsal, not trial data. The reason: `trials.py` and the
guest count the sitting number from the disk's own notebook, so the twin's
disk and the HP's are two notebooks — a twin sitting plus two HP sittings
would leave neither with three, the guest would never reach a verdict,
`layout_default` would never follow it, and the HP's first sitting would
repeat `ABBA BAAB`. Decided before any data existed; spec-7d decision 5
amended the same day. *The run:* the stick rebuilt from the item 14 tree
(`mkimage.sh`, `mkstick.py`; `BOOTX64.EFI` 45,056 bytes), the 7c twin
command with a blank disk, **one terminal — no broker, no relay** (the
trial sends nothing; the cage refuses cleanly with nothing on 9997), the
serial through a `stdio` chardev with a `logfile`. Nineteen `S7:` lines to
`S7: keyboard ready` and `S7: mouse ready`; `! trial`; eighty cues, seven
rests; `trial: sitting 1 done`; the panel's table and `python3
stage7/trials.py --disk stage7/out/disk.img` agree (`no verdict: 1 done
sitting(s), 3 needed`). The table: `1 A 10 1 3120`, `2 B 10 0 2117`, `3 B
10 0 1529`, `4 A 10 1 1928`, `5 B 10 0 1860`, `6 A 10 1 1833`, `7 A 10 1
1619`, `8 B 10 4 1929`. **The arrow stayed a visible arrow over the boxes
and after leaving them** — the owner's eye on item 13's fix (1), the one
check the gate cannot make. **Checked again by the owner the same evening
in a second windowed boot, looking only at the arrow on the boxes:** the
cell under the arrow goes black with the arrow white on it — the arrow
drawn plain, as a whole cell, never inverse — and when the arrow moves on
the cell turns solid again, no trail. **Item 13's fix (1) passes.** The evidence:
`history/2026-09-24-ring7d-rehearsal-twin-table.png` (the screen at the
end) and `history/2026-09-24-ring7d-rehearsal-twin-serial.log` (the whole
serial stream, the terminal's escape codes stripped; the disk copied to
`stage7/out/disk.rehearsal.img`).

*What the rehearsal found — in the host, not the guest:* the QEMU window
under Hyprland showed only the left 80 of the 120 columns (the screenshot
is 1276 pixels of a 1920-pixel mode, 1:1), so the right third of the
screen was off the window. The owner made QEMU full screen to get the
pointer to behave, and still at the end the arrow would not go right; the
cue was block 8's ninth, `exit`, whose box in layout B is columns 90–119:
three misses, then a hit at 104,726 ms. The block's median (1929) is not
moved by one outlier. **The HP draws to a real 1920x1080 monitor, so this
cannot happen there.** For any later windowed run on this desktop:
`-display gtk,zoom-to-fit=on` on the QEMU line, so the whole mode is
scaled into the window. Also on the record: the first block was the
slowest (3.1 s, against 1.5–1.9 s after it) — the warm-up the ABBA/BAAB
order exists to absorb; the strip counted ten keys (the full-screen
toggles), dropped by the trial's rule; a stray `f` typed and erased at the
prompt after `done`.

*The owner's words on the two layouts, recorded as said and not part of
the pre-registered rule:* **clicking the blocked squares was a lot easier;
in the text row he read `Tab` and `app` as two separate items, and the same
with `Esc` and `exit`.** In layout A an item's words are one space apart
and the items three, and that gap did not group them for him — a proximity
finding about layout A's text, whatever the trial's numbers say. The
threat it carries, said once: the trial is not blinded (it cannot be — the
human sees the layout), and the owner now has a stated preference; the
pre-registered rule on medians and misses is what decides, not the
preference.

**Test 5 — HP sitting 1 (24 September 2026, Cowork on Opus 5.5 at high
effort). The owner's word: passed.** *The setup:* the owner already in
`uucp` on Omarchy; `udisksctl` present; the ring's stick flashed once, by
METAL.md steps 1–3 as they stand — one `usb` line in `lsblk` (7.4 GB, its
old 64 MB ESP not mounted), the by-id path
`usb-USB_Mass_Storage_Device_812320090519-0:0` (`sdc`), `wipefs` on the
partition then the stick, `dd` of 69,206,016 bytes, `cmp -n 69206016`
silent, `sdc1` `vfat` with no mount point, `power-off`. The file flashed
was `stick.img` as built from the item 14 tree at the rehearsal
(`BOOTX64.EFI` 45,056 bytes), never the twin's copy. The wiring as ring 7c
left it. One terminal: `python3 broker/chart.py /dev/ttyUSB0
stage7/out/hp-sitting1.log` (the CP2102), started before power-on; no
broker, no relay, no second address.

*The boot (22:34:27 by the chart):* the first line is noise bytes where
`S7: alive` stands — the UART settling at power-on, not the guest; then
`S7: edid none`, `S7: gop 1920x1080`, four cores found and woken, `S7:
console 120x67`, `S7: disk port 0 488397168 notes 2048 home 34816`, **`S7:
notebook 2 notes`**, `S7: home 1 apps`, the nic and `S7: link up`, `S7:
glass core 2`, the `i8042:` pair, `S7: keyboard ready`, and `S7: mouse
ready` at the first move. The second note was not in the record, whose
last charted boot (18 September, 10:07) read one: the owner read both on
the screen before the sitting — `hello metal` and `Tell me about this
machine`, both typed by him on the 7c days (the second with no `?`, so a
note). Neither begins `trial`, and this ring's binary had never run on the
HP, so the sitting number was 1, as pre-registered.

*The sitting:* `! trial` at 22:37:08 — `trial: sitting 1 ABBA BAAB`, the
strip `trial A 1/8`; `trial: sitting 1 done` at 22:43:46. The table,
identical on the HP's panel, on the chart and from `python3
stage7/trials.py --serial stage7/out/hp-sitting1.log` (`no verdict: 1 done
sitting(s), 3 needed`): `1 A 10 0 2390`, `2 B 10 0 1777`, `3 B 10 0 1514`,
`4 A 10 0 1780`, `5 B 10 0 1800`, `6 A 10 1 1579`, `7 A 10 0 1535`, `8 B
10 0 1529`. The strip at the end: `cl 081` (80 hits and the one miss), `n
093` (the two notes and the sitting's 91), `k 0008` (`! trial` and Enter),
`err 000`; the prompt row in layout A, no verdict yet. **The arrow on the
metal:** white on a black cell over a box, and the box solid again when it
moved on — item 13's fix (1) holds on the HP as in the twin.

*What the sitting found — in the procedure, not the guest (recorded, not
fixed):* Cowork's step had the owner stop after `! trial` and report
before the first click, so block 1's first cue stayed on the screen
through the exchange: `trial: 1 1 A 1 196498` (196.5 s). By the
pre-registered rule the hit stands. It does not decide pair 1: at any
value of that cue, block 1's median is at least 2203 (its other nine hits
run 1706 to 2795), above block 2's 1777.

The evidence: `history/2026-09-24-ring7d-hp-sitting1-table.jpg` (the
monitor at `done`) with its 1600-pixel copy, and
`history/2026-09-24-ring7d-hp-sitting1-serial.log` (the chart as recorded,
the first line's noise kept).

**Test 5 — HP sitting 2 (24 September 2026, Cowork on Opus 5.5 at high
effort). The owner's word: passed.** *The setup:* no flash — the stick as
sitting 1 left it, nothing changed on it; the wiring unchanged. A later
boot of the same evening, as the design allows (separate days or at least
separate boots). One terminal: `python3 broker/chart.py /dev/ttyUSB0
stage7/out/hp-sitting2.log`, started before power-on; no broker, no relay,
no second address.

*The boot (23:03:46 by the chart):* the first line again noise bytes where
`S7: alive` stands; then the same lines as sitting 1's boot, with **`S7:
notebook 93 notes`** — the owner's two and sitting 1's 91 (its start, 80
hits, one miss, eight block notes, `done`) — and `S7: home 1 apps`; `S7:
mouse ready` at 23:03:47. The boot replay drew sitting 1's notes to `trial
sitting 1 done`; the strip `n 093`, `err 000`; the prompt row in layout A
(`? ask   ! grow   ! calculator`), no verdict.

*The sitting:* `! trial` at 23:06:11 — `trial: sitting 2 BAAB ABBA`;
`trial: sitting 2 done` at 23:09:29. The table, identical on the HP's
panel, on the chart and from `python3 stage7/trials.py --serial
stage7/out/hp-sitting2.log` (`no verdict: 1 done sitting(s), 3 needed` —
the count is of the one log it read): `1 B 10 0 1784`, `2 A 10 0 1700`, `3
A 10 1 1632`, `4 B 10 0 1610`, `5 A 10 0 1614`, `6 B 10 0 1555`, `7 B 10 0
1432`, `8 A 10 0 1514`. The one miss: block 3, cue 9 (`trial: 2 3 A 9
miss`, then its hit at 4717 ms). Eighty hit lines and one miss line on the
chart. The strip at the end: `cl 081` (80 hits and the one miss), `n 184`
(93 and the sitting's 91), `k 0008`, `err 000`; the prompt row in layout
A, no verdict yet. Block 1's first cue took 2627 ms: Cowork's step ran
straight from `! trial` into the eighty clicks and ended at `done`, so
sitting 1's procedure finding (the 196.5 s cue) did not recur. **The arrow
on the metal, the owner's words:** the arrow white, the cell black, and it
turns white when the mouse moves — the box solid again behind it, as in
sitting 1. No pair was compared: nothing is looked at before the verdict.

The evidence: `history/2026-09-24-ring7d-hp-sitting2-table.jpg` (the
monitor at `done`; the photograph's EXIF block removed and a C2PA content
credential added by Cowork's file delivery, the image data unchanged)
with its 1600-pixel copy, and
`history/2026-09-24-ring7d-hp-sitting2-serial.log` (the chart as recorded,
the first line's noise kept).

**Test 5 — HP sitting 3 and the verdict (24–25 September 2026, Cowork on
Opus 5.5 at high effort). The owner's word: passed, on the sitting and on
the verdict.** *The setup:* no flash — the stick as sittings 1 and 2 left
it; the wiring unchanged. A later boot of the same evening. One terminal:
`python3 broker/chart.py /dev/ttyUSB0 stage7/out/hp-sitting3.log`,
started before power-on; no broker, no relay, no second address. Before
the boot the owner pushed 2309407 and 9bee3e2 (origin at 9bee3e2).

*The boot (23:31:42 by the chart):* the first line again noise bytes where
`S7: alive` stands; then the same lines as sittings 1 and 2, with **`S7:
notebook 184 notes`** — what sitting 2 left — and `S7: home 1 apps`; `S7:
mouse ready` at 23:31:44.

*The sitting:* `! trial` at 23:56:02 (the chart's echo `hp`, two erases,
`! trial`) — `trial: sitting 3 ABBA BAAB`; `trial: sitting 3 done` at
23:59:09 and `trial: verdict A` 59 ms after it. The table, identical on
the HP's panel, on the chart and from `python3 stage7/trials.py --serial
stage7/out/hp-sitting3.log` (`stage7/out/hp-sitting3.trials.txt`): `1 A
10 0 1564`, `2 B 10 0 1340`, `3 B 10 0 1403`, `4 A 10 1 1842`, `5 B 10 0
1542`, `6 A 10 0 1301`, `7 A 10 1 1278`, `8 B 10 0 1533`, `done`,
`verdict A`. The two misses: block 4 cue 2 (then its hit at 2968 ms) and
block 7 cue 10 (then its hit at 3100 ms). Eighty hit lines and two miss
lines on the chart. Block 1's first cue took 3753 ms. The strip at the
end: `cl 082` (80 hits and the two misses), `n 277` (184, the sitting's
92 and the verdict note), `k 0013`, `err 000`; the prompt row in layout
A. Twelve of the thirteen keys are on the chart's echo (`h`, `p`, two
erases, `! trial`, Enter); the thirteenth has no echo — a key pressed
inside the sitting, where a key is ignored and counted by the rule, or a
key that prints nothing; it decides nothing. **The arrow on
the metal, the owner's words:** same as before, no bugs.

*The verdict, by TRIALS.md's pre-registered rule over the first three
`done` sittings* — in each pair a win for B when B's median is strictly
lower. Sitting 1: A 2390 B 1777 (B), B 1514 A 1780 (B), B 1800 A 1579
(A), A 1535 B 1529 (B). Sitting 2: B 1784 A 1700 (A), A 1632 B 1610 (B),
A 1614 B 1555 (B), B 1432 A 1514 (B). Sitting 3: A 1564 B 1340 (B), B
1403 A 1842 (B), B 1542 A 1301 (A), A 1278 B 1533 (A). **Wins for B: 8
of 12; ten needed.** Misses: the twelve A blocks 4 (one in each of
sittings 1 and 2, two in sitting 3), the twelve B blocks 0, so B's are
not greater. The first condition fails: **A stays.** The guest wrote
`trial verdict A` to the notebook at the end of sitting 3. The host
agrees: the three charts joined in order (`stage7/out/hp-sittings-all.log`)
and read by `python3 stage7/trials.py --serial` give `verdict A: sittings
[1, 2, 3], wins for B 8 of 12 (10 needed), misses A 4 B 0`
(`stage7/out/hp-sittings-all.trials.txt`). Cowork's count by hand from
the three tables gives the same. Nothing else was looked at. The owner's
words at the rehearsal (the boxes felt easier) are on the record above;
they are not part of the rule, and the rule gave A.

*After the sitting — one slip, recorded:* the owner typed a command meant
for mlrig's terminal on the HP's keyboard. None of it is on the chart,
and the next boot's `S7: notebook 277 notes` shows nothing was journaled.

*The verdict boot (25 September 2026, 00:16:26 by the chart
`stage7/out/hp-verdict-boot.log`):* a new boot, no flash; the same lines
with **`S7: notebook 277 notes`** (no `S7: mouse ready` — the mouse was
not moved). The row at the prompt is layout A (`? ask   ! grow   !
calculator`). `! trial` (its echo on the chart at 00:16:53) answered
**`trial concluded`** on the console: nothing journaled, one in `errors`
(`err 001` on the strip), `k 0008`, `n 277`. What this boot shows and
what it cannot: `trial concluded` shows the verdict note found on the
notebook. The row is the verdict's layout, but A is also the layout
before any verdict, so the row alone cannot show `layout_default` taken
from the note at boot; that read is proven in the twin by test 3 (the
default read at boot after a scripted verdict B).

The evidence: `history/2026-09-24-ring7d-hp-sitting3-table.jpg` (the
monitor at `done` with `verdict A`) and
`history/2026-09-25-ring7d-hp-verdict-boot-concluded.jpg` (the monitor at
`trial concluded`), each with its 1600-pixel copy — the photographs' EXIF
block removed (the GPS with it) and a C2PA content credential added by
Cowork's file delivery, the image data unchanged, as for sitting 2 — and
`history/2026-09-24-ring7d-hp-sitting3-serial.log` and
`history/2026-09-25-ring7d-hp-verdict-boot-serial.log` (the charts as
recorded, the first line's noise kept).

**Ring 7d — CLOSED 25 September 2026, by the owner's word on the
verdict.** The spec's Done-when asks for three sittings on the notebook,
the frozen analysis's verdict, and the DE's default following the
verdict. On the HP: three `done` sittings on its notebook (24 September
2026); `trial verdict A` journaled by the guest at the third `done` and
read back by `trials.py` from the three charts joined; and at the next
boot `! trial` answered `trial concluded`. The default is A, the layout
the row already had. The read of the verdict into `layout_default` at
boot is proven in the twin (test 3, a scripted verdict B); on the metal
it shows only as far as the row being A.

*The trial in numbers:* 240 cues on the HP in three sittings of eight
blocks. Block medians 1278 to 2390 ms on A and 1340 to 1800 ms on B.
B's median lower in 8 of the 12 pairs, ten needed. Misses 4, all on A.
**A stays.** One flash of the ring's stick (45,056 bytes) before sitting
1 and none after; no guest defect found on the metal.

*The ring's record:* 22 commits before this closure (`7272636` …
`d0e49f5`): items 0–14 one per item with 13b, the owner's GLASS.md
append (`6beb717`), the rehearsal, the three sittings, the plain
photographs. At the plan gate four Cowork amendments (A1 blocking: the
reserved prefix) and fourteen deviations accepted. The freeze at item 8,
the payload table at 1678 cases, 0 wrong. Cowork's pre-oracle review:
four defects in the unfrozen guest, fixed at item 13; one weakness in the
frozen checker, fixed by the owner's hand at item 13b — the project's
eighth freeze opening. All four automated tests green at item 14 (21
min). Test 5: the rehearsal in the windowed twin (not trial data, by the
owner's pre-registration), HP sittings 1 to 3, the verdict boot. Two
findings, both recorded and not fixed: the host's (the QEMU window under
Hyprland showed 80 of the 120 columns; for windowed runs,
`-display gtk,zoom-to-fit=on`), and the procedure's (sitting 1's first
cue waited 196.5 s while the owner reported to Cowork; it does not
decide pair 1, and the step was changed for sittings 2 and 3).

*The model note, for the owner's comparison:* CC ran every item of ring
7d on **Fable 5.1 at medium effort**. Cowork ran the spec, the plan review
and the pre-oracle review on Fable 5.1 at medium effort, and the
rehearsal, the three sittings and this closure on **Opus 5.5 at high
effort**. Ring 7d on Fable 5.1 medium: one blocking amendment of four,
one freeze opening, four pre-oracle defects, no metal defect. Ring 7c on
Fable 5.1 medium: three required amendments, no freeze opening, two
metal-only defects.

*Carried out of ring 7d:*
(1) The label-width sentence for TRIALS.md's "Layout B - the boxes",
written at item 13 and unapplied because the document is frozen and test
1 parses it cold. Its text, since `stage7/out/` is not in the
repository: *If the label is wider than the box's filled width (a narrow
screen), only its first `filled` characters are drawn, from the box's
first column; the box's target is the filled span as ever.* It waits for
a freeze opening with a parser check.
(2) The photographs committed before `9bee3e2` carry GPS in the
repository's history. The files are plain from `9bee3e2` on; removing
the old versions needs a history rewrite and a force push, which change
the hashes this file cites — the owner's decision, not taken.
(3) Windowed runs on Hyprland: `-display gtk,zoom-to-fit=on` on the QEMU
line.
(4) Stage 7's caveats, unchanged: the PHY speed after a reset, TIPG,
WIRE.md's halting sentence, the nineteen-line first boot never watched on
the metal, the x2APIC and trampoline paths.
(5) The HP's disk holds GermOS's table, 277 notes (the owner's two and
the trial's 275, the last `trial verdict A`) and the calculator; the
stick is as flashed for the trial.

The evidence of ring 7d in `history/`: the rehearsal's screenshot and
serial log; for each HP sitting the photograph of the table (with its
1600-pixel copy) and the chart; the verdict boot's photograph and chart.

## Ring 7c — the metal · opened 15 September 2026 · closed 18 September 2026

`stage7/plan-7c.md` was approved on 15 September 2026 with Cowork's seven
amendments (A1 `chart.py`'s non-blocking open before termios, DCD never
asserted on a three-wire cable; A2 under `CAP.SSS` a second for `DET` to
leave 0 after `SUD`, then ten seconds to `DET 3` or a named halt; A3 the
flash procedure's single-USB-line check, the `udisksctl` unmount before the
write and the power-off after `sync`; A4 the `/dev` mention bounded by `\b`;
A5 the mode-loop bound mirroring `surf_describe`'s mode-only limits; A6 the
`i8042:` pair on all three test 2 boots; A7 what `nmcli` does and how it is
undone) and every deviation accepted. **The model for this ring: Fable 5.1
at medium effort**, the owner's decision in the spec; Cowork reviews to the
same standard as every ring. Item 0 (this record, the plan's commit) is
done; the items follow one commit each, exactly as the plan says.

**The shape, from the plan** (its environment table holds the measured facts
behind every choice): **procedure and a guard, no new driver.** The EDID
guard — BAR2 read as an EDID only when the display is QEMU's VGA
(`1234:1111`), `S7: edid none` and the highest mode by area on any other,
plus a bound in the mode loop mirroring the console's fixed limits (A5); the
i8042 cold init — the controller self-test before the command byte is
written, `i8042: self-test ok` and `i8042: mouse reset ok` (or `i8042:
mouse none`, a line not an error) before `keyboard ready`, `ERR: i8042 …`
and a halt only for the controller, **no new `S7:` line** so every frozen
counter (18/17, 19/18) holds; `PxCMD.SUD` under `CAP.SSS` in the AHCI probe
(A2), unexercisable in the twin whose `CAP` is `0xc0141f05` with bit 27
clear; `stage7/mkstick.py` (unfrozen) writing `stage7/out/stick.img` — a
protective MBR, a GPT, one 64 MB ESP with `EFI/BOOT/BOOTX64.EFI` through
mtools' `image@@offset` form, no loop device, no `/dev`; the gate booting a
**copy** of it over `qemu-xhci` + `usb-storage` with no `esp.img` on SATA
(OVMF writes `NvVars` to the stick's FAT, so the file as built is the thing
test 1 parses and the owner flashes); the relay's grace close (the guest
side closed two seconds after the broker has finished, `WIRE.md` untouched);
`broker/chart.py` (the serial port at 115200 8N1 through `termios`, teed to
a file with timestamps, proven on a pty pair); the bodyguard extended
(`dd`, `of=`, `by-id`, `ttyUSB`, `nmcli` and every `/dev` spelling denied in
Bash, prose included; `/dev/tty*` narrowed to `/dev/tty`; one Stage 3
allowance flipped); `stage7/METAL.md`, the owner's document, unfrozen, in
the spec's step order with Cowork's A3 and A7. **The ports:** the relay on
**9997** in the twin (`python3 broker/relay.py --bind 127.0.0.1 --port
9997`), not the spec's 9998 — 9998 is the frozen twin's own listener; on
the HP's day `python3 broker/relay.py` with no flags (`10.0.2.4:9999 →
127.0.0.1:9999`) beside `python3 broker/wire.py` (not the spec's
`pointer.py`: `wire.py`'s twin rehearses on SATA over an e1000e). The gate
`stage7/test-7c.sh` and `stage7/checkmetal.py`, frozen at item 6: test 1
the stick parsed from the host; test 2 three boots over USB (`blank` at
`-smp 8`, `again` at 4, `novga` at 2 on `virtio-vga` for `edid none`); test
3 every stage re-proven in one scripted run of two boots at `-smp 4`
(Stage 2's typing, Stage 3's note across the reboot, Stage 4's `? ping`,
ring 6a's `! test app`, ring 6b's `! install echo` in `wire.py`'s twin, and
in the no-broker boot ring 6c's click on `! echo` doing ring 6b's launch);
test 4 the strings, the argv checks, the frozen bind battery and the
payload table. Test 1 is green from item 3; test 2 whole and test 3 from
item 8; test 4 from item 13.

| # | Test | Status |
|---|---|---|
| 1 | Artefact — the standing PE32+ checks, plus `stick.img` parsed from the host: protective MBR, both GPT headers and arrays with their CRCs, exactly one ESP-type entry at 2048..133119, `classify` `gpt`, every table sector as the builder spells it, `EFI/BOOT/BOOTX64.EFI` read back at the offset byte-identical to the build | **PASS** |
| 2 | Serial, the metal configuration — a copy of the stick over `qemu-xhci` + `usb-storage`, no `esp.img` on SATA, the SATA disk and the e1000e: nineteen lines at `-smp 8` with `S7: disk port 1` and the disk byte-exact from the host, eighteen at 4 with the disk byte-identical, `S7: edid none` and the gop line 1920x1080 on virtio-vga at 2; the `i8042:` pair once each in order between the glass core's line and the keyboard's on every boot, on serial and on the glass; every stick copy's tables unchanged | **PASS** |
| 3 | Every stage re-proven in the twin of the HP — one scripted run of two boots at `-smp 4`: `first note`, `? ping`, `! test app` with `k` and screen A, `! install echo` rehearsed in `wire.py`'s twin — the record's three entries, the relay's three, the germline's two with nineteen-line logs, the notes and home partitions, the twin's disk, obs E (`grows_served 0` by GLASS.md's rule); then with 9999 and 9997 closed — the note back above the prompt and `! echo` on the row, the arrow on the first move, a click on `! echo` launching it from the home partition with the echo exactly `! echo`, `b` to it, the strip's pointer field, the arrow parked, the disk and the stick copy untouched | **PASS** |
| 4 | The bodyguard, extended — the harness's strings (no QEMU line names `esp.img`), `check_argv_7c` on the checker's command and the frozen `check_argv_7b` on the twin's, the frozen bind battery, the payload table as a subprocess (1563 cases, 0 wrong), twenty-four spellings and words denied and twenty-three harmless sources, sinks and tools allowed | **PASS** |
| 5 | **Oracle — Wajira, on the HP** — the stick, the lines on the chart, the glass at native, a note across a power cycle, `? ping` over the LAN, `! install calculator` and its launch with the broker off, a click | **PASS — confirmed by Wajira on the HP, 18 September 2026, all eight steps; his word closes ring 7c and Stage 7.** (1) the lines on the chart in the twin's order — eighteen, never nineteen: the disk carried GermOS's table from the blind boot of 15 September, so every watched boot read `S7: disk port 0 488397168 notes 2048 home 34816` with `S7: notebook N notes` and no `S7: gpt written`; the format path is proven by the table the 15th left, which every boot since has accepted; (2) the glass at 1920x1080 (`history/2026-09-17-ring7c-first-glass-on-metal.jpg`); (3) and (4) `hello metal` typed and back after the power button (`history/2026-09-17-ring7c-hello-metal.jpg`); (5) `? ping` — *pong. I hear you, GermOS — the link is up and I'm ready when you are.*, `w 001 002675` (`history/2026-09-18-ring7c-pong-on-metal.jpg`, the eighth watched boot, the item 21 binary); (6) `! install calculator` — `installed calculator`, `g 000/001`, `w 002`, `! calculator` on the choices row (`-installed-calculator.jpg`); (7) power off, the broker and the relay stopped, power on — `S7: home 1 apps`, `w 000` (`-home-1-apps-broker-off.jpg`, the ninth watched boot); (8) the mouse moved — `S7: mouse ready`, the arrow, `pt` on the strip (`-mouse-arrow.jpg`) — and a click on `! calculator` launched it from the SATA disk with nothing on the wire: `running calculator`, 4096, `w 000 000000`, `io 000000/000000` (`-calculator-from-disk-4096.jpg`); each photograph has a 1600-pixel web copy beside it. The serial log of every boot in `stage7/out/metal.log` and the whole monitor dialogue is `history/2026-09-18-ring7c-serial.log`; the sixth boot's chart, which was read into another file, is `history/2026-09-17-ring7c-serial-sixth-boot.log`. The history of the row, kept: **steps 1 to 4 passed on 17 September 2026** (the second and third watched boots: eighteen lines in the twin's order, the glass at 1920x1080, `hello metal` kept across a power cycle — the photographs in `history/`); **step 5 stopped at `ERR: nic transmit timed out`** (the first frame's `DD` never set on the 82579LM; item 17 names the device's state before that halt; **the fourth boot's line read `tdh 0`, `txdctl 0`, `tarc0 0x403`, FWSM FW_VALID — the descriptor never fetched; item 18 sets the ich8lan hardware bits; the fifth boot's line read `tdh 0` still with `txdctl 0x00400000` and `tarc0 0x0d800403` — the bits in and not enough; item 19 waits on the ME's window before every register write, reads the ring registers back and widens the line with the device's TDLEN/TDBAL/TDBAH; **the sixth boot's line read `tdh 0` with `tdlen 128 tdbal 0x004ce000 tdbah 0x00000000 expect 0x00000000004ce000` — the ring configured in the device exactly as written, the lost-write branch closed; item 20 is the serial monitor and `broker/probe.py`, so the questions from here are asked over the wire, many per boot, no flash between them**). **the seventh boot (18 September 2026) stopped in the monitor and a CC session found the cause over the socket: TCTL's reset default `0x3003f0f8` carries `MULR` (bit 28), the driver's absolute write cleared it, and the 82579LM then never commits a packet with `EOP` — bit 28 alone sends, and TCTL `0x3003f0fa` with TARC1 `0x45000403` read `tdh 2 tdt 2 sta 0x01`; item 21 is that fix**. The first watched boot stopped after `S7: home 0 apps` before the nic line (item 16). Flash the stick built at item 21 once, boot with probe.py in place of the chart, type `? ping`, expecting `pong`; the monitor is there if the `e1k:` line comes again (`stage7/METAL.md`, "The monitor") |

**On this build** (15 September 2026; the sizes as of item 21, 18
September): the binary is 40,960 bytes (36,864 through item 16, ring 7b's
size; the section stepped up one page at item 17, and item 18's twenty
instructions, item 19's three routines, six read-backs and twenty-nine
call sites, item 20's monitor — five routines, twelve defines, ten
strings and the register table — and item 21's three instructions fit in
its padding); the stick 69,206,016 bytes (135,168
sectors), the ESP at LBA 2048 for 131,072; a boot from the stick over USB reaches `S7: alive` at
1.2–1.3 s and ready at 1.4–1.5 s, the SATA path's numbers; OVMF's GOP
lists 30 modes on QEMU's VGA and 23 on virtio-vga, 1920x1080 the highest
on the latter; the twin's `CAP` is `0xc0141f05` (`SSS` clear) and its
firmware sets `SUD` itself; the i8042 answers every command on the first
poll; the gate is five boots plus two rehearsals, 104 s; the payload table
1566 cases, 0 wrong.

**Caveats carried forward:**

- **Everything ring 7b carried** — the 82579LM's PHY, legacy descriptors on
  one queue with no link-change handling, plaintext on the home LAN, TLS at
  Stage 8 or the ring where traffic first crosses a network the owner does
  not own.
- **`CAP.SSS`:** written to the AHCI spec with A2's two-stage wait; the
  twin cannot exercise it (`SSS` clear); the HP's first `S7: disk` line is
  its test.
- **The i8042's real timing, AMI's GOP's mode list, the x2APIC path and the
  trampoline:** the twin approximates or never reaches them; test 2 on the
  HP will say.
- **The relay's grace close** is a tool's behaviour recorded here and in
  `METAL.md`, not a frozen criterion (deviation 7).

### Ring 7c — the build, item by item

**Item 0** — this record; `stage7/plan-7c.md` committed verbatim.
**Item 1** — the environment, measured on private copies under
`stage7/out/probe7c/` (gitignored) with a temporary probe spliced into a
copy of the source (never into `stage7/stage7.asm`, never committed); no
source changed, nothing frozen touched, no Claude call, no `/dev` path in
any command:

| Fact | Measured how |
|---|---|
| **mtools' `image@@offset` form works on this host:** a hand-built 66 MiB stick (`STICK_SECTORS` 135168; protective MBR with one `0xEE` entry; GPT at LBA 1 and its backup at the last LBA; one entry of the ESP type GUID, first LBA **2048**, last **133119**, 131072 sectors, the spec's 64 MB) formatted with `mformat -i stick.img@@1048576 -F -T 131072 -v GERMOS ::`, `mmd`, `mcopy` at the offset; `mdir` at the offset lists `BOOTX64 EFI 36864`; `mtype` at the offset extracts it **byte-identical** to the build; the host's `blkid -p` says `PTTYPE="gpt"`, `partx -s` lists `1 2048 133119 131072 64M EFI System`; DISK.md's `classify` says **`gpt`** and `parse_gpt` raises "a valid table without both GermOS partitions (found [])" — the AHCI driver would refuse it, which is right | `stage7/out/probe7c/mkstick_probe.py`; `blkid`, `partx`, `broker/metal.py` |
| **Ring 7b's closed binary boots from a copy of the stick over `qemu-xhci` + `usb-storage` with no `esp.img` on SATA**, the blank SATA disk on `ide.1` and the e1000e cage to a throwaway port (9996), at `-smp 2`, `4` and `8`: **nineteen lines**, `S7: disk port 1 131072 notes 2048 home 34816` (only port 1 holds a disk now), `S7: nic 6c:3b:e5:3b:86:45`, `S7: link up`, `console 120x67`; **`S7: alive` at 1.20–1.30 s and ready at 1.40–1.50 s from QEMU's start — the SATA path's numbers; OVMF's USB enumeration costs nothing measurable.** The gate keeps `timeout 60` and the 60 s ready window | `stage7/out/probe7c/boot.py`, eight boots |
| **OVMF did not write `NvVars` into the stick copy**: the copy is **byte-identical** to the built stick after every one of the eight boots (0 sectors differ), and no `NvVars` string lands on the SATA disk either — unlike ring 7a's `esp.img` on SATA, which changed on every boot. The plan's criterion (the stick copy's MBR, GPT header, entry array and backup unchanged after a boot) stands as written and is not tightened to byte-identity: OVMF's behaviour is the firmware's to change, and the owner's HP has its own | `boot.py`, `cmp`, `grep -c` |
| **The display that is not QEMU's VGA.** QEMU's VGA is `1234:1111` with BAR2 `0x810c5000`, a memory BAR (the EDID), and OVMF's GOP lists **30 modes** for it, all `PixelFormat` 1 (BGR), from 640x480 to **2560x1600**, 2048x2048 and 2000x2000 among them (mode 0 is the EDID's 1920x1080). **`virtio-vga` is `1af4:1050`**, class `0x0300`, and **its BAR2 reads `0x0000000c` — an I/O BAR**, so today's `edid_read` skips it by the existing `test al, 1` and prints **`S7: edid none`** already; OVMF's GOP lists **23 modes** for it, 640x480 to **1920x1080** (mode 22), all format 1, and the mode loop takes **1920x1080 — the highest by area** (1600x1200 is smaller); `console 120x67`; the glass draws. **`cirrus-vga` is `1013:00b8`**, BAR2 zero, **two modes**, 640x480 and 800x600; `edid none`, `800x600`, `console 50x37`. **So no QEMU display puts a valid EDID behind a memory BAR2 under a foreign vendor: the twin cannot exercise the guard's refusal directly.** The `novga` boot (virtio-vga, `edid none`, the gop line **1920x1080** — the literal from this run) is the spec's observable; **the guard's own proof is item 7's probe: the constant changed in a copy, QEMU's VGA with its valid EDID at BAR2 must then print `edid none`** | the probe's `P: display id` and `P: mode` lines on three displays |
| **`CAP` through the monitor on the stick boot: `0xc0141f05`, `PI` `0x3f`** — bit 27 (`SSS`) **clear**, as ring 7a recorded. **Port 1's `PxCMD` after the selection is `0xc017`** — `ST`, **`SUD` and `POD` already set by the firmware**, `FRE`, `FR`, `CR` — and `PxSSTS` `0x113` (`DET` 3, Gen 1, `IPM` 1). With `SSS` clear the `SUD` path of decision 4 and A2 is not taken in the twin; the code is written to the spec | `xp` on `obs + 0x2C0`; the probe's `P: pxcmd` line |
| **The i8042 as the twin answers it**, after `0xAD`, `0xA7` and the drain: **`0xAA` answered `0x55` on the first poll**; the command byte then reads **`0x77`** (translation on, both interrupts off, both ports disabled — bit 4 set by our own `0xAD`; ring 6c's `0x67` was read before any disable); the mouse's **`FA`, `AA`, `00` each on the first poll** (`polls-left 50` of `I8042_WAIT_TRIES` 50). QEMU's controller has no latency to measure; **deviation 9 is decided by the PS/2 specification alone: `I8042_WAIT_TRIES` becomes 100** (one second per answer, the mouse's post-reset self-test being specified at up to 500 ms), a change the twin cannot feel | the probe's `P: i8042` and `P: mouse` lines, three boots |
| **The console's limits for A5:** `SHADOW_SIZE` `0x10000` cells (its comment says "128x128 cells, this machine's 2048x2048 mode exactly, with room over" — 64 KB holds 65536 cells, so every mode OVMF lists here fits: 2560x1600 is 16000 cells); `surf_describe` checks `PANEL_CELLS` (`0x10000`) per panel and **`SURF_ROWS_MAX` 256 rows** at `.too_small` (`stage7.asm` 7256–7282); item 7 mirrors the mode-only ones | read |
| **The pty pair accepts the serial settings:** `os.open(name, O_RDWR\|O_NOCTTY\|O_NONBLOCK)`, `tcsetattr` with `B115200` in and out, `CS8\|CREAD\|CLOCAL`, `PARENB`/`CSTOPB`/`ICANON` clear, `VMIN` 1, then `O_NONBLOCK` cleared with `fcntl` — every setting reads back as set and bytes written to the master arrive (A1's order, inside one Python script; the slave's name never appears in a command) | a Python script on `pty.openpty()` |
| **The hook's verdicts today on the spelling table** (fed as payloads by `stage7/out/probe7c/spellings.py`, the spellings held as data): **denied** — `/dev/sda`, `//dev/sda`, `/dev//sda`, `/dev/./sda`, `/dev/disk/by-id/…`, `/dev/serial/by-id/…`, `"/dev/sda"`, `'/dev/'sda`, `$'/dev/sda'`, `/dev/`; **allowed today, to be denied at item 13** — `"/dev"/sda`, `/de\v/sda`, `\/dev\/sda`, bare `/dev`, `/dev/ttyUSB0`, `/dev/ttyS0`, `/dev/ttyACM0`, and the words `dd`, `of=`, `by-id`, `ttyUSB`, `nmcli`; **allowed and staying so** — `/dev/null`, `/dev/zero`, `/dev/urandom`, `/dev/random`, `/dev/stdin`, `/dev/stdout`, `/dev/stderr`, `/dev/fd/0`, `/dev/tty`, `/dev/pts/3`, `</dev/null`, `"/dev/null"`, `/devel/x`, `stage7/out/devices.txt` (A4), `add odd dd-x`, `lsblk`, `python3 stage7/mkstick.py`, `python3 broker/chart.py` | `spellings.py`, 40 payloads |
| The probe's guestfwd used a throwaway port (9996); the gate's ports were never touched; no packet left the cage; the probe's stick copies and disks are under `stage7/out/probe7c/` | `boot.py` |

**Decided at item 1, before any test is written:** the ready window stays
60 s and the gate's `timeout` 60; the `novga` display is `virtio-vga,edid=on`
and its gop literal `1920x1080`; the stick's constants are the probe's
(135168 sectors, the ESP at 2048 for 131072); `I8042_WAIT_TRIES` 100
(deviation 9); the guard is proven by item 7's constant-changed probe, not
by the `novga` boot, which is green on its EDID criterion already on ring
7b's binary (its red at item 3 is the missing `i8042:` pair alone).

**Item 2** — `stage7/mkstick.py` (unfrozen, the builder): the probe's
shape as decision 8 — `STICK_SECTORS` 135168, the ESP at LBA 2048 for
131072 sectors (64 MB), the protective MBR, both headers and both entry
arrays with their CRCs, `build_table()` returning every table sector for
the checker to compare a booted copy against; `mformat -F -T 131072`,
`mmd`, `mcopy` at `@@1048576`; exit 0 only if `mdir` at the offset lists
the file. Proven on the host: `classify` says `gpt`; `mtype` at the offset
extracts the build byte-identical; a second run overwrites cleanly; with
`BOOTX64.EFI` absent it exits 1 with a message and writes nothing.

**Item 3** — `stage7/test-7c.sh` with test 1 and test 2, and
`stage7/checkmetal.py`'s first two modes: `--stick` (the built stick parsed
from the host — the protective MBR, both headers and both arrays with their
CRCs, exactly one ESP-type entry at 2048..133119, `classify` `gpt`, every
table sector as `mkstick.build_table` spells it, `mdir` and `mtype` at the
offset); `--serial blank|again|novga SMP` (the checker's `qemu_argv` — the
stick copy over xhci + usb-storage, the SATA disk, the e1000e cage, no
`esp.img`; its `drive` with ring 6c's mouse steps; ring 7b's pattern lists
with the EDID line in either form; `check_i8042_lines` — the pair once, in
order, between the glass core's line and the keyboard's; the stick copy's
tables compared to the built file after the boot; the screen's last log
rows above the prompt). **The gate on ring 7b's binary: test 1 PASS; test 2
FAIL on exactly one thing in all three boots — the `i8042:` lines are `[]`
on serial and absent from the glass.** The `novga` boot passes its EDID and
mode criteria already (item 1's finding); the `again` boot's disk is
byte-identical; every stick copy's tables unchanged. `stage7/out/gate7c.item3.log`.

**Item 4** — `checkmetal.py --stages` (test 3, deviation 6) and test 3 in
`test-7c.sh`: the relay and mock lifecycles bound to `stage7/out/metal/`;
boot A — `first note`, `? ping`, `! test app` with `k` and screen A, `!
install echo`, obs E — judged by the frozen `check_question_entry`,
`check_grow_entry` (call 1), `check_install_entry` (call 2), the relay's
three entries by `question_bytes` and the frame lengths, the two `_7b`
germline transcriptions, the notes partition `["first note"]`, echo on the
home partition, the twin's disk, screen A, obs E with `grows_served 0` by
GLASS.md's rule and the i8042 command byte by `check_i8042`; boot B with
9999 and 9997 closed — screen N (`first note` above the prompt, `! echo`
on the row), the arrow, a click on `! echo` at the column
`pointer.choice_targets` gives, `b`, the arrow parked, obs L, screen L,
obs L2, Esc — judged by `strip_mouse_line`, eighteen lines with `notebook
1 notes` and `home 1 apps`, the echo exactly `! echo` (the line the click types, as ring 6c made it), `check_one_cell_panel`,
`check_mode_field`, `check_choices`, the obs counters (`wire_conns 0`,
the bytes unchanged, the packets, one click, one hit), `check_arrow_at`,
`check_strip_6c`, the disk and the stick copy untouched. **On ring 7b's
binary (`stage7/out/stages.item4.log`): every check passes except the two
serial-log checks, each on the `i8042:` pair alone** — the ring adds two
lines and takes nothing away.

**Item 5** — `checkmetal.py --cage` (test 4) and test 4's self-assertions
in `test-7c.sh`: (a) the harness's strings — the cage, the MAC, both
displays, the machine, the SATA disk and the stick helper under
`stage7/out/metal/`, and no QEMU line of its own naming `esp.img`; (b)
`check_argv_7c` on the checker's command (one cage to 9997, five devices —
the display, the xhci, the usb-storage on the drive named `stick`, the
`ide-hd` on `ide.1`, the e1000e on `n0` with the MAC; two raw drives under
`stage7/out/`, neither virtio, neither `esp.img`, neither `stick.img`
itself) and the frozen `check_argv_7b` on the twin's as `wire.py` builds
it, unchanged; (c) the frozen bind battery; (d) the payload table as a
subprocess, exit 0 and `0 wrong` required, plus the spot checks held as
data — the flash's words and every `/dev` spelling of decision 7 and A4
denied, the harmless sources and sinks and this ring's tools allowed.
**On today's hook (`stage7/out/cage.item5.log`): (a), (b) and (c) pass,
the table is 1444 cases 0 wrong, and (d) names exactly the fourteen
spellings and words the hook allows today** — item 13's flips.

**Item 6** — the freeze: `PROTECTED` grows `stage7/test-7c.sh` and
`stage7/checkmetal.py`, the hook's comment saying why and why `METAL.md`,
`mkstick.py`, `relay.py`, `chart.py`, `mkimage.sh`, `stage7.asm`,
`claude_backend.py` and `plan-7c.md` are not; `payloads.py` gains the ring
7c freeze group — the battery on both paths, the heredoc and `sed -i`
denials, the allowances measured before the plan and at item 1 (the gate,
the checker's modes, the builder and the tools writable, the mtools lines
at the offset, the stick boot, the `novga` boot, the twin's line under the
metal scratch, the oracle's line, the probe's line, the host witnesses, the
scratch wipe, `git add`) and the denials (a stick or a disk outside `out/`,
a shorthand). **1524 payloads, 1020 denied, 504 allowed, 0 wrong**; one
append into the checker denied live. The gate whole on ring 7b's binary
(`stage7/out/gate7c.item5.log`): test 1 PASS, tests 2–4 FAIL by design on
the `i8042:` pair and today's hook.

**Part 2 — item 7** (`stage7/stage7.asm`): **the EDID guard and the mode
bound.** `edid_read` keeps register 0's device:vendor word in `R10D` and,
after the class matches, compares it with `EDID_QEMU_VGA` (`0x11111234`) —
any other display goes to `.none` and prints `S7: edid none` without BAR2
ever being read. The mode loop, before a mode is a candidate, mirrors the
console's fixed limits (A5) — at least 8 cells each way, at most
`STRIP_CELLS/2` columns, the panels' rows (rows − 4) at most
`SURF_ROWS_MAX`, the cells in all at most `SHADOW_SIZE` — and skips a mode
that fails one; `PANEL_CELLS` is judged as before. The binary is 36,864
bytes still. **Probed on private copies of the source (never committed),
each booted from its own stick copy:** (a) the guard's constant changed —
QEMU's VGA, with its valid EDID at BAR2, prints **`S7: edid none`** and
takes the highest by area, **2048x2048**, `console 128x128`; (b) the cell
bound lowered to 8000 with the guard off — 1920x1080 (8040 cells) skipped
for **1600x1200** (7500 cells, the next by area); (c) the rows bound
lowered to 60 with the guard off — 1920x1080 (67 rows) skipped for
**1600x900**. The real binary: `S7: edid 1920x1080` on QEMU's VGA, `S7:
edid none` and 1920x1080 on virtio-vga, as before. **`./stage7/test.sh`
and `./stage7/test-7b.sh` on this binary: all four PASS each**
(`stage7/out/gate7a.item7.log`, `gate7b.item7.log`).

**Item 8** (`stage7/stage7.asm`): **the i8042 cold init** — after the two
disables and the drain, the controller's self-test `0xAA` must answer
`0x55` within the bound (a timeout or another byte: `ERR: i8042 self-test
failed`, a halt), then **`i8042: self-test ok`**; the command byte read
*after* the self-test (a controller that passed and then falls silent:
`ERR: i8042 command byte not answered`), the read-modify-write, the
read-back and `0xA8` as ring 6c wrote them; the mouse's reset, defaults
and reporting with every failure going to **`i8042: mouse none`** and
`mouse_id` 0 — a line, never an error — and success printing **`i8042:
mouse reset ok`**; `i8042_wait_ibf`'s exhaustion `ERR: i8042 input buffer
never emptied`. `I8042_WAIT_TRIES` 100 (deviation 9, decided at item 1).
The binary is 36,864 bytes still. **Probed on private copies:** the
expected self-test byte changed to `0x56` — eighteen lines, the named
error, no keyboard, one `S7: alive` (a halt); the expected reset byte
changed to `0xAB` — `self-test ok`, `mouse none`, nineteen lines, the
keyboard ready. **The gate: tests 1, 2 and 3 PASS** (the pair on every
boot on serial and on the glass; every stage re-proven in one run with
the arrow and the click); test 4 red on the hook alone. **`./stage7/test.sh`
and `./stage7/test-7b.sh`: all four PASS each** (`stage7/out/gate7c.item8.log`,
`gate7a.item8.log`, `gate7b.item8.log`).

**Item 9** (`stage7/stage7.asm`): **`PxCMD.SUD` under `CAP.SSS`** (decision
4, A2) in `disk_select`'s probe loop — with `SSS` set, `SUD` on each
implemented port before its `PxSSTS` is looked at; a second for `DET` to
leave 0 (stays 0: an empty port, passed); ten seconds
(`AHCI_SPINUP_TRIES`) for a device that appeared to reach `DET 3, IPM 1`,
or **`ERR: ahci port N did not come up after spin-up`** and a halt. With
`SSS` clear the path is ring 7a's, byte for byte. The binary is 36,864
bytes still. **Unexercisable in the twin** (`SSS` clear, the firmware
already sets `SUD`); **probed with the `SSS` test forced true on private
copies:** the five empty ports passed after a second each, the disk found
on port 1, ready at 6.5 s; the spin-up's target made unreachable — the
named halt naming port 1 after ten seconds, one `S7: alive`. The HP's
first `S7: disk` line is the real test. **The gate: tests 1–3 PASS;
`./stage7/test.sh` and `./stage7/test-7b.sh` all four PASS each**
(`stage7/out/gate7c.item9.log`, `gate7a.item9.log`, `gate7b.item9.log`).

**Item 10** (`broker/relay.py`, unfrozen): **the grace close** (decision 5)
— once the broker has finished, the guest side is given `GRACE` 2.0 s to
close; if it has not, the relay shuts and closes it and serves the next
connection; the log line's bytes as counted, `error` null, a stderr note.
WIRE.md untouched. **Proven on the host** (`stage7/out/probe7c/relay_grace.py`):
a client holding its socket after reading `pong` whole; the next client
served **2.00 s** after the first's answer; three log lines, every error
null, `up 8 down 8`; a closing client logged at once; ring 7b's relay
proof re-run, every assertion held. `./stage7/test-7b.sh` all four PASS;
the 7c gate tests 1–3 PASS (`stage7/out/gate7b.item10.log`,
`gate7c.item10.log`).

**Item 11** (`broker/chart.py`, unfrozen): **the serial reader** (decision
6, A1) — the port opened `O_RDWR | O_NOCTTY | O_NONBLOCK`, termios set raw
at `B115200`, `CS8 | CREAD | CLOCAL`, no parity, one stop bit, `VMIN` 1,
then `O_NONBLOCK` cleared (a three-wire null-modem cable never asserts DCD;
without this order the open would hang and the HP would be wrongly
suspected); every line to stdout as it arrives and to the log file with
a millisecond timestamp, flushed per line; a partial line kept at Ctrl-C;
a port that cannot be opened a loud exit 2. **Proven on a pty pair**
(`stage7/out/probe7c/chart_proof.py`, the slave's name computed inside the
script): five lines in — one with a stray `\r`, one with a non-UTF-8 byte,
one partial at SIGINT — five out on stdout and in the log with the
timestamp's shape, exit 0; a path under `out/` that does not exist, exit
2 with the reason. The usage text names the adapter's usual path once,
inside the file.

**Item 12** — `stage7/METAL.md`, the owner's document (decision 10, A3,
A7), unfrozen: step 0 once before the day (the `dialout` group, the build
the gate passed, the network thought through); step 1 `lsblk` with
exactly one `usb` line by SIZE and MODEL; step 2 the by-id path and the
`udisksctl unmount -b` of every mounted partition, and why; step 3 the
flash by the owner's hand with `conv=fsync`, `sync`, `udisksctl power-off
-b`; step 4 the wiring; step 5 the LAN port's second address by `nmcli`
(the bounce, the persistence) with the `ip addr add` fallback (gone at
reboot), then the three terminals — `python3 broker/wire.py`, `python3
broker/relay.py` with no flags, `python3 broker/chart.py` on the adapter's
port started before power-on; step 6 power on; step 7 the debugging
table, line by line from `nothing at all` to `keyboard ready and no
prompt`; step 8 test 5 in order; step 9 the chart and the photograph into
`history/` and the second address's removal; a closing section on what
the twin could not prove. Written with the Write tool; every command
copied from the files as they stand.

**Item 13** — **the bodyguard extended** (decision 7, A4) —
`.claude/hooks/protect-tests.py`: the command normalised for the
bodyguard's eyes before the device rule (quotes and backslashes deleted,
runs of slashes and dot segments collapsed), a bare `/dev` a mention at a
word boundary (`/devel`, `/devices` stay ordinary), `/dev/tty` itself the
only terminal allowed (the named serial ports denied), and `METAL_WORDS`
— `dd` as a word on its own, `of=`, `by-id`, `ttyUSB`, `nmcli` — denied
wherever they appear, prose included. `payloads.py`: the ring 7c
bodyguard group (twenty-five denials, fourteen allowances) and the Stage
3 allowance of `dd` into `out/` flipped to a denial with its label saying
why. **1563 payloads, 1046 denied, 517 allowed, 0 wrong**; one word in
prose denied live. **`./stage7/test-7c.sh`: ALL FOUR AUTOMATED TESTS
PASS** (`stage7/out/gate7c.item13.log`). **The regression chain on this
tree, every gate green:** `./stage7/test.sh`, `./stage7/test-7b.sh`,
`./stage6/test.sh`, `./stage6/test-6b.sh`, `./stage6/test-6c.sh`, Stages
5–0 (`stage7/out/gate7a.item13.log`, `gate7b.item13.log`,
`chain13.*.log`).

**Item 14** — this handover to the green-pending-oracle state; `CLAUDE.md`'s
build block gains `python3 stage7/mkstick.py` and `./stage7/test-7c.sh`,
the windowed command its ring 7c shape (the stick over USB as a copy,
9997), and four gotchas (no QEMU display stands in for a foreign display
with an EDID at BAR2; a prose rule against a path must see through the
shell's quoting; a click on a launch item types the launch line; OVMF's
`NvVars` on a stick copy — assert what the guest must never do, never
byte-identity); `README.md`'s Stage 7 paragraph and running section gain
ring 7c; the gate re-run whole and timed (104 s, all four PASS,
`stage7/out/gate7c.item14.log`); the payload table re-run, 1563 cases, 0
wrong. The probe artefacts stay under `stage7/out/probe7c/` (gitignored)
for the review; nothing frozen touched.

**Item 15** — from Cowork's pre-oracle review: **the ports re-disabled
after the self-test.** In `mouse_init`, once `0xAA` has answered `0x55` and
before `i8042: self-test ok` is printed, `0xAD` and `0xA7` go through
`i8042_cmd` again and the output buffer is drained. On some real
controllers the self-test resets the controller and re-enables both ports,
and a device's power-on byte (the keyboard's `0xAA`, the mouse's `0xAA
0x00`) can then sit in the output buffer ahead of the command byte — the
`0x20` read would take a device byte as the command byte, clear
translation and write it back: a dead keyboard on the HP. The twin cannot
show the difference; the rule stands in the comment and as a CLAUDE.md
gotcha. The binary is 36,864 bytes still. `./stage7/test-7c.sh`,
`./stage7/test.sh` and `./stage7/test-7b.sh`: all four PASS each
(`stage7/out/gate7c.item15.log`, `gate7a.item15.log`, `gate7b.item15.log`);
the payload table 1563 cases, 0 wrong.

**Item 16** — from the HP's first watched boot, 17 September 2026: **the
e1000e reset on the metal.** The chart (`stage7/out/metal.log`) showed
twelve lines — `S7: alive`, `S7: edid none`, `S7: gop 1920x1080 fb
0xe0000000`, boot services exited, gdt and paging ours, idt ready, `cores
found 4`, `cores woken 4`, `console 120x67`, `S7: disk port 0 488397168
notes 2048 home 34816`, `notebook 0 notes`, `home 0 apps` — then nothing:
no `ERR:`, no exception line, no repeat, the monitor black, which is
expected before the glass core's first frame. So the x2APIC path, the
trampoline, AMI's GOP and the AHCI with `SUD` all passed on real silicon
on the first boot, and the processor stopped inside `e1k_attach` before
`msg_nic`. The HP's own view from live Ubuntu (`stage7/out/hp-lspci.log`):
the 82579LM (`8086:1502`, `00:19.0`, BAR0 `f7c00000` 128 KB, subsystem
`103c:3397`, MSI on, FLR capable) is healthy — Linux's e1000e reads
`6c:3b:e5:3b:86:45` from it (`MAC: 10, PHY: 11`) and the link comes up at
1000 Mbps full duplex. **The defect** (`stage7.asm` 5204–5207): `CTRL.RST`
written and `CTRL` read back in the very next instruction. On the PCH's
integrated LAN an MMIO access straight after the reset write hangs the
hardware — no fault, no timeout; Intel's own driver
(`drivers/net/ethernet/intel/e1000e/ich8lan.c`, `e1000_reset_hw_ich8lan`)
writes `CTRL.RST`, says in a comment that a flush cannot be issued there
because it hangs the hardware, and sleeps 20 ms before its next register
access. **The fix:** one `pit_wait` of `PIT_25MS` (an existing constant)
between the reset write and the first read of `CTRL`; the bounded poll and
`ERR: nic did not complete its reset` unchanged; no new `S7:` line, no
frozen counter changed, `WIRE.md` untouched (it says the reset is
awaited, and now it is from the first read). Nine bytes of code, 25 ms on
every boot; the binary is **36,864 bytes still** (the section's padding
absorbs it). **Tests red before code — said plainly: the twin cannot see
this defect.** QEMU's 82574L answers the immediate read, so no test was
written red for it and no expectation was invented. What the twin can say
was recorded on a private copy first (`stage7/out/probe7c/probe16.asm`,
never committed, packed into a private stick and booted with the item 1
harness at `-smp 4` on the throwaway port): nineteen lines, `S7: nic
6c:3b:e5:3b:86:45`, `S7: link up`, alive 1.30 s and ready 1.50 s — item
1's numbers — the stick copy's tables unchanged, 0 sectors differing; the
binary built from the source afterwards is byte-identical to the probe's.
**The two neighbours, raised at the plan gate and left alone by its
decision:** (a) Linux takes the `EXTCNF_CTRL.SWFLAG` semaphore around this
reset because on a vPro board the ME shares the LAN; even Linux resets
anyway when the acquire times out. Not taken here — the hang matches the
immediate read exactly, and one variable per boot is the debugging
strategy. It becomes the next candidate if the next chart shows the nic
line with a wrong MAC, `ERR: nic has no address in RAL/RAH`, or a link
that never comes: about fifteen lines, a bounded set-and-verify of bit 5
at `0x0F00` before the reset and a clear after the `ICR` read, no new
line. (b) The ten-second link wait is the next thing the twin could not
prove; the next boot decides it by itself — `S7: link up`, or `ERR: nic
link did not come up within 10 s`, the named error that names the next
item (the PCH PHY through `MDIC`, `CTRL.PHY_RST`, `ich8lan.c`'s post-reset
workarounds). `CLAUDE.md` gains the gotcha; `stage7/METAL.md` step 7 gains
the row for `S7: home N apps` then nothing, the sentence that the monitor
is black until `S7: glass core`, and the reset timing under what the twin
could not prove. **`./stage7/test-7c.sh` (103 s), `./stage7/test.sh` (459 s)
and `./stage7/test-7b.sh` (335 s) on the same binary: all four tests PASS
each** (`stage7/out/gate7c.item16.log`, `gate7a.item16.log`,
`gate7b.item16.log`); the payload table 1563 cases, 1046 denied, 517
allowed, 0 wrong. The stick rebuilt: `stage7/out/stick.img`, 69,206,016
bytes, the ESP at LBA 2048..133119 holding the 36,864-byte binary. No
flash, no `/dev` path, nothing outside the repository; the owner's broker
and relay from the first day were stopped so the gates could hold their
ports.

**Item 17** — from the HP's second and third watched boots, 17 September
2026: **the transmit timeout names the 82579LM's state.** With item 16 the
boot goes all the way (`stage7/out/metal.log`, the boots at 19:00:45 and
19:06:58): eighteen `S7:` lines in the twin's order on the disk the 15th
formatted (`S7: disk port 0 488397168 notes 2048 home 34816`), `S7: nic
6c:3b:e5:3b:86:45` 38 ms after `home`, `S7: link up` in the same
millisecond, `S7: component region`, `S7: obs page`, `S7: glass core 2`,
`i8042: self-test ok`, `i8042: mouse reset ok` 415 ms later, `S7: keyboard
ready`; the glass at 1920x1080 on the monitor; `hello metal` typed at
19:03:58 and back above the prompt after a power cycle (`S7: notebook 1
notes` at 19:06:58). **Test 5 steps 1 to 4 passed**; the photographs are
`history/2026-09-17-ring7c-first-glass-on-metal.jpg` and
`history/2026-09-17-ring7c-hello-metal.jpg` (the owner's files, committed
with this item at his request, A1). **Step 5:** `? ping` at 19:08:43.197,
then `ERR: nic transmit timed out` at 19:08:48.403 and the halt — the
first frame, the ARP for `10.0.2.4`, sat in its legacy descriptor for
`VQ_POLL_TRIES` (five seconds) with `DD` never set. What is known: both
rings are page-aligned and below 4 GB (`ERR: nic ring sits above 4GB` was
not printed), bus mastering is set in the same `pci_cfg_write32` the AHCI
uses, the link is up, the MAC is right. This is ring 7b's caveat exactly —
the twin's 82574L cannot show what the PCH's integrated LAN does with a
descriptor — and item 16's class again: a difference between the 82574L
and the 82579LM that no gate can see. **The item is one thing, no fix**
(`stage7/stage7.asm`): on the timeout path in `e1k_send`, before
`serial_err` halts, `e1k_tx_state` prints one line through the tee (so it
is on the chart and on the glass):

```
e1k: tdh N tdt N status 0x… ctrl 0x… tctl 0x… txdctl 0x… tarc0 0x… ctrlext 0x… fwsm 0x… sta 0x… ring 0x…
```

— TDH (`0x3810`) and TDT (`0x3818`) in decimal; STATUS (`0x0008`), CTRL
(`0x0000`), TCTL (`0x0400`), TXDCTL0 (`0x3828`), TARC0 (`0x3840`), CTRL_EXT
(`0x0018`) and FWSM (`0x5B54`) as eight hex digits; the descriptor's status
byte as two; the transmit ring's physical address as sixteen (identity
mapped: the label's address is the bus address the device was given).
Four defines, one helper (`serial_puthex32`), one routine, eleven strings;
the numbers choose the fix, one item, next. **How to read it:** `tdh`
still **0** — the descriptor was never fetched, which points at the PCH
LAN's descriptor-fetch setup, the `TXDCTL` and `TARC` bits Linux sets in
`e1000_initialize_hw_bits_ich8lan` before it transmits; `tdh` at **1** —
the frame went out and only the `DD` write-back is missing; `status` **bit
4** (`TXOFF`) set — transmit is paused by flow control; `fwsm` says whether
the ME holds the interface; `ctrlext` for completeness. **No new `S7:`
line:** the `e1k:` line is on a failure path no green run takes, so every
frozen counter (18/17, 19/18) holds; `WIRE.md` untouched (the named error
is unchanged and still halts). **Proven on a private copy with the path
forced** (`stage7/out/probe7c/probe17.py`, never committed: the poll's
`DD` test replaced by a test that never passes, the copy assembled into a
private stick copy and booted at `-smp 4` on the throwaway port, `? ping`
typed through the monitor): the line printed once, formatted as specified
to the regex, `ERR: nic transmit timed out` the very next line five
seconds after the echo, nothing after it and one `S7: alive` — the halt
followed. **The twin's reading, the reference beside the HP's future
line:** `e1k: tdh 1 tdt 1 status 0x00080283 ctrl 0x00140241 tctl
0x0003f0fa txdctl 0x00000000 tarc0 0x00000403 ctrlext 0x00000000 fwsm
0x00000000 sta 0x01 ring 0x00000000004ce000` — the 82574L fetched the
descriptor, sent the frame and wrote `DD` back (`sta 0x01`); only the
forced test ignored it. **The binary is 40,960 bytes** (from 36,864: the
section stepped up one 4 KB page; test 1 judges the PE fields, not the
size); the stick rebuilt, 69,206,016 bytes, the ESP at LBA 2048..133119
holding it. **`./stage7/test-7c.sh` (104 s), `./stage7/test.sh`
(459 s) and `./stage7/test-7b.sh` (314 s) on the same binary:
all four tests PASS each** (`stage7/out/gate7c.item17.log`,
`gate7a.item17.log`, `gate7b.item17.log`); no `e1k:` line in any gate's
serial capture; the payload table 1563 cases, 1046 denied, 517 allowed, 0
wrong. `stage7/METAL.md` step 7 gains the row for the timeout and its
reading. No flash, no `/dev` path, nothing outside the repository; the
stick is the owner's hand. No CLAUDE.md gotcha yet: the fix item earns it.

**Item 18** — from the HP's fourth watched boot, 17 September 2026: **the
transmit descriptor fetch on the 82579LM — the ich8lan hardware bits.**
With item 17 the boot went to `S7: keyboard ready` as before
(`stage7/out/metal.log`, 19:50:15, eighteen lines on the same disk); `?
ping` at 19:50:48.998 ended at 19:50:54.218 in the item 17 line and the
halt:

```
e1k: tdh 0 tdt 1 status 0x00080483 ctrl 0x00100240 tctl 0x0003f0fa txdctl 0x00000000 tarc0 0x00000403 ctrlext 0x01481000 fwsm 0x6001c04c sta 0x00 ring 0x00000000004ce000
ERR: nic transmit timed out
```

**Read field by field:** `tdh 0` after `tdt 1`, `sta 0x00` — the
descriptor was never fetched, the `tdh 0` half of item 17's rule; `status`
bit 1 (LU) set, bits 7:6 = 10 (1000 Mb/s), bit 0 (FD) set, bit 19 (GIO
master enabled) set, **bit 4 (TXOFF) clear** — the link is up at 1000 full
and transmit is not paused by flow control; `ctrl` SLU (bit 6) and bit 20;
`tctl` exactly what `e1k_attach` wrote (EN, PSP, CT 0xF, COLD 0x3F; MULR,
bit 28, clear); `txdctl 0x00000000` — no prefetch, host or write-back
threshold, GRAN 0; `tarc0 0x00000403` — COUNT 3, ENABLE (bit 10) and
nothing above it; `ctrlext 0x01481000` — bits 12, 19, 20, **22** and 24
already set by the firmware; `fwsm 0x6001c04c` — **FW_VALID (bit 15) set:
the ME is present and shares the LAN**; `ring 0x4ce000`, page-aligned and
below 4 GB. Beside it the twin's reference line (`tdh 1 tdt 1 … txdctl
0x00000000 tarc0 0x00000403 … sta 0x01`): the 82574L fetches a descriptor
with the same zero TXDCTL and the same TARC0; the PCH's LAN does not.
**What Linux does before this family transmits:**
`e1000_initialize_hw_bits_ich8lan` in
`drivers/net/ethernet/intel/e1000e/ich8lan.c`, called from
`e1000_init_hw_ich8lan` on every init before `setup_link` (the current
source, fetched and read this session), sets read-modify-write: CTRL_EXT
bit 22 (plus PHYPDEN, bit 20, on pchlan and later — already set on the
HP); TXDCTL(0) bit 22; TXDCTL(1) bit 22; TARC(0) bits 23, 24, 26, 27 (28
and 29 only on ich8lan); TARC(1) bits 24, 26, 30, and bit 28 when
TCTL.MULR is clear. **The item is one fix** (`stage7/stage7.asm`): in
`e1k_attach`, right after the reset's second `IMC` write and the `ICR`
read and before the MAC is read — Linux's place, before the link is set
up, and so before TCTL is enabled — those bits, read-modify-write each
register, with `e1k_idx` (the index into `e1k_ids`, stored at the PCI
scan's hit: 0 the 82574L, 1 and 2 the PCH parts) choosing the split.
**The split, from the 82574 datasheet (rev 3.3, read this session) and
Linux's own 82574 path (`e1000_initialize_hw_bits_82571`) — the answer
the plan gate asked for:** CTRL_EXT bit 22 is a *defined* bit on the 82574
("Tx LS Flow"); TXDCTL bit 22 and TARC0 bit 26 are *reserved* on the
82574 by its datasheet, yet Linux sets both on the 82574 too, so those
three go to every e1000e and the twin exercises every register and every
helper the item touches; TARC0 bits 23, 24, 27 and TARC1 bits 24, 26,
28, 30 are reserved on the 82574 ("should be written to 0") and Linux
never writes them there (it clears TARC0 27 on the 82574), so they go to
the PCH parts only, gated by id — bit 28 of TARC1 because our TCTL never
sets MULR. Five new defines, two register offsets, one BSS dword, one
store in the scan, twenty-two instructions, **one write per register as
Linux does it** — the first draft wrote TARC0 twice on the PCH path
(the common bit, then the PCH bits by a second read-modify-write), and a
device that reads a reserved bit as 0 would have lost bit 26 on the
second write; caught reading the diff while the first gate run was
under way, the mask folded into one write, the probe and all three
gates rerun on the corrected binary. `e1k_send`, `e1k_tx_state`,
`e1k_poll` and the strings untouched. **No new `S7:` line**, no frozen
counter moved; `WIRE.md` untouched — its init description names no
TXDCTL or TARC field and nothing in it becomes false. **Tests red before
code — said plainly: the twin cannot see this defect either.** QEMU's
82574L fetches without the bits, so no test was written red and no
expectation invented. **What the twin can say, on private copies**
(`stage7/out/probe7c/probe18.py`, never committed): two builds, each with
one splice after the hardware bits printing `p18: ctrlext … txdctl0 …
txdctl1 … tarc0 … tarc1 …` read back from the device, packed into a
private stick copy and booted over `qemu-xhci` + `usb-storage` at `-smp
4` on a fresh 64 MB disk on the throwaway port. **A, the source as
written:** `p18: ctrlext 0x00400000 txdctl0 0x00400000 txdctl1
0x00400000 tarc0 0x00000403 tarc1 0x00000403`. **B, the gate forced
(`e1k_idx` set to 1, the twin standing in for the 82579LM):** `p18:
ctrlext 0x00400000 txdctl0 0x00400000 txdctl1 0x00400000 tarc0 0x08000403
tarc1 0x50000403`. Both: nineteen `S7:` lines, `S7: nic
6c:3b:e5:3b:86:45`, `S7: link up`, `S7: keyboard ready`, one `S7: alive`,
no `ERR:`, the stick copy's tables unchanged. **One thing the probe
taught, recorded not assumed:** QEMU's `e1000e_get_tarc`
(`hw/net/e1000e_core.c`) reads TARC through a mask of bits 10:0 and
27..30 — the datasheet's "reads as 0" for 26:11 — so TARC0 bits 23, 24
and 26 and TARC1 bits 24 and 26 are stored by the model (`e1000e_putreg`,
verbatim) but never read back, and the probe's first expectation
(`tarc0 0x04000403`, then `0x0d800403`/`0x55000403`) was wrong by
exactly those bits; the second run's expectation is the model's mask.
CTRL_EXT (only ASDCHK and EE_RST masked), TXDCTL0, TXDCTL1, TARC0 27 and
TARC1 28 and 30 read back set: the write path is proven for every bit
the model shows, and the 82579LM's own TARC reads are for the fifth boot
to show through the `e1k:` line, if it prints again. **The binary is
40,960 bytes still**; the stick rebuilt, 69,206,016 bytes, the ESP at LBA
2048..133119 holding it. **`./stage7/test-7c.sh` (104 s), `./stage7/test.sh`
(458 s) and `./stage7/test-7b.sh` (313 s) on the same binary: all four
tests PASS each** (`stage7/out/gate7c.item18.log`, `gate7a.item18.log`,
`gate7b.item18.log`); no `e1k:` or `p18:` line in any gate's serial
capture; the payload table 1563 cases, 1046 denied, 517 allowed, 0
wrong. **The next candidates, in
order, if the fifth boot's line still says `tdh 0`:** (1) **the ME** —
`fwsm 0x6001c04c` has FW_VALID set, so the Management Engine shares this
LAN; item 16's neighbour (a), the `EXTCNF_CTRL.SWFLAG` semaphore at
`0x0F00` — a bounded set-and-verify of bit 5 before the reset and a clear
after the `ICR` read, about fifteen lines, no new line; with `ich8lan.c`'s
`e1000_acquire_swflag_ich8lan` open; (2) **the transmit descriptor
write-back policy** Linux applies later in `e1000_init_hw_ich8lan`
(TXDCTL GRAN with WTHRESH 1 and PTHRESH 31, `E1000_TXDCTL_FULL_TX_DESC_WB`
and `MAX_TX_DESC_PREFETCH`) and `CTRL_EXT.RO_DIS` (bit 17); (3) `tdh 1`
on the line instead — the write-back item, as item 17 said. **No
CLAUDE.md gotcha this item, deliberately:** the gotcha is written at the
closure, when the fifth boot proves or refutes the fix — a rule typed
before its boot would be a guess of ring 6b item 10b's class.
`stage7/METAL.md` step 7's transmit row gains this reading. No flash, no
`/dev` path, nothing outside the repository; the stick is the owner's
hand.

**Item 19** — from the HP's fifth watched boot, 17 September 2026: **the
82579LM with the ME alive — lost register writes.** With item 18 the boot
went to `S7: keyboard ready` as before (`stage7/out/metal.log`, 20:53:21,
eighteen lines on the same disk); `? ping` at 20:53:33.041 ended at
20:53:38.259 in the item 17 line and the halt:

```
e1k: tdh 0 tdt 1 status 0x00080483 ctrl 0x00100240 tctl 0x0003f0fa txdctl 0x00400000 tarc0 0x0d800403 ctrlext 0x01481000 fwsm 0x6001c04c sta 0x00 ring 0x00000000004ce000
ERR: nic transmit timed out
```

**Read field by field:** `txdctl 0x00400000` and `tarc0 0x0d800403` —
item 18 landed, and the 82579LM reads bits 23, 24, 26 and 27 back where
QEMU's model masks them; `tdh 0` after `tdt 1`, `sta 0x00` — the
descriptor is still never fetched; `status`, `ctrl`, `tctl`, `ctrlext`
and `fwsm` byte for byte the fourth boot's. Item 18's bits were not the
fix. **What the line rules out:** `tdh 0` is upstream of the MAC and the
wire — the PHY, the link (up at 1000 full), flow control (`TXOFF` clear)
and the ME's own use of the network cannot keep the head at 0; only the
descriptor engine's registers can: TCTL.EN, TDBAL, TDBAH, TDLEN, TDH, TDT.
`tctl` and `tdt` read back correct on the line. **TDLEN, TDBAL and TDBAH
have never been read back** — the line's `ring` field was our label's
address, not the device's register — and a TDLEN of 0 in the device is
the one configuration that gives exactly this line: nothing to fetch, the
head never leaves 0, the tail accepts any value. **Why a write could be
lost on this chip:** Linux's `drivers/net/ethernet/intel/e1000e/ich8lan.c`
sets `FLAG2_PCIM2PCI_ARBITER_WA` for one case, under the comment "Enable
workaround for 82579 w/ ME enabled": `mac.type == e1000_pch2lan` and
`FWSM & E1000_ICH_FWSM_FW_VALID` (bit 15, `0x00008000`) — this HP exactly
(`fwsm 0x6001c04c`). Under it every register write goes through `__ew32`
(`netdev.c`), whose `__ew32_prepare` spins while FWSM bit 24
(`E1000_ICH_FWSM_PCIM2PCI`, `0x01000000`, "ME PCIm-to-PCI active") is set,
at most `E1000_ICH_FWSM_PCIM2PCI_COUNT` (2000) `udelay(50)`; and
`e1000e_update_tdt_wa` writes TDT, reads it back, and on a mismatch clears
`TCTL.EN` with "ME firmware caused invalid TDT - resetting"
(`e1000e_update_rdt_wa` the same for RDT; both are also called from
`e1000_configure_tx`/`_rx` at init) — all read verbatim from the current
source this session. QEMU has no ME, so the twin cannot show any of it.
The same line on three boots fits a deterministic window: our ring
registers are written milliseconds after `CTRL.RST`, the event the ME
reacts to. **The item is two parts in one commit** (`stage7/stage7.asm`),
both from that finding. **Part one, the diagnostic:** the `e1k:` line
gains `tdlen` (decimal), `tdbal` and `tdbah` (eight hex digits) read from
the device after `sta`, and its `ring` field becomes `expect` — the label
address printed as before, so the line shows what the device holds beside
what we wrote:

```
e1k: tdh N tdt N status 0x… ctrl 0x… tctl 0x… txdctl 0x… tarc0 0x… ctrlext 0x… fwsm 0x… sta 0x… tdlen N tdbal 0x… tdbah 0x… expect 0x…
```

**Part two, the protection, on every e1000e so the twin walks the same
code:** `e1k_write` (RDI the BAR, ECX the offset, EAX the value) waits for
FWSM bit 24 to clear — `E1K_PCIM2PCI_TRIES` 2000 polls of `PIT_50US` (60
ticks, 50.3 us), Linux's bound, and writes anyway when it runs out, as
Linux does — then writes, preserving every register; every register write
in `e1k_attach` goes through it (IMC, the reset's CTRL — the wait is before
the write, so item 16's 25 ms of no access after it is kept — IMC, the
five item 18 registers, CTRL for the link, the 128 MTA dwords with the
offset walked in ECX, RDBAL/RDBAH/RDLEN/RDH/RDT, RFCTL, MRQC, RCTL, RDT,
TDBAL/TDBAH/TDLEN/TDH/TDT, TIPG, TCTL), and so does TDT in `e1k_send`;
`e1k_verify` (the same three registers in) reads the register back and
rewrites it through the wait on a mismatch, `E1K_HOLD_TRIES` (8) times,
then `e1k_hold_err` prints one line through the tee and halts:

```
ERR: nic register 0x00003808 wrote 0x00000080 read 0x00000000 - it will not hold its value
```

— the offset, the value written, the value the device holds. The six ring
registers (RDBAL, RDBAH, RDLEN, TDBAL, TDBAH, TDLEN) are verified right
after each is written; the heads and tails are not (the device moves the
heads, the driver the tails, and the line shows both). Three defines, one
PIT constant, three routines, twenty-nine call sites, eight strings, one
renamed; `e1k_tx_state`'s other reads untouched, the virtio-net driver
untouched. **Two choices beyond the brief, said at the gate:** (1) the
RDT write in `e1k_poll` goes through the wait too — Linux routes every
write and a lost RDT starves receive in silence; RDI is dead there and
the virtio poll path already clobbers it, so no caller relied on it; one
FWSM read per frame received; (2) `E1K_HOLD_TRIES` 8 is a bound no run
can give — Linux does not retry, it resets the adapter — written as a
define and named a guess. **A deviation, recorded:** `WIRE.md`'s table of
named errors lacks the new `ERR: nic register …` line, as it lacks item
17's `e1k:` line; the document is frozen and untouched — the row that
would change is one more line in "The named errors" (a ring register
that did not read back after eight rewrites), a freeze opening only if
the owner wants the document to say it. **No new `S7:` line**, no frozen
counter moved; nothing frozen parses the `e1k:` line (every checker, gate
and broker grepped: no hit). **Tests red before code — said plainly: the
twin cannot see this defect either.** QEMU's 82574L has no Management
Engine, its FWSM reads 0, and no gate was written red. **What the twin
can say, on private copies** (`stage7/out/probe7c/probe19.py`, never
committed; three builds, each spliced into a copy of the source, packed
into a private stick copy and booted over `qemu-xhci` + `usb-storage` at
`-smp 4` on a fresh 64 MB disk on the throwaway port): **A, the read-back
and the wait path** — a counter in the wait loop and a private line after
TCTL: `p19: tdbal 0x004ce000 tdbah 0x00000000 tdlen 128 rdbal 0x004cd000
rdbah 0x00000000 rdlen 256 waits 0` — the six registers read back as
written and every FWSM read took the clear path on the first read;
nineteen `S7:` lines to `keyboard ready`, no `ERR:`. **B, the widened
line** — item 17's forcing (the `DD` test never passes), `? ping` typed
through the monitor: `e1k: tdh 1 tdt 1 status 0x00080283 ctrl 0x00140241
tctl 0x0003f0fa txdctl 0x00400000 tarc0 0x00000403 ctrlext 0x00400000
fwsm 0x00000000 sta 0x01 tdlen 128 tdbal 0x004ce000 tdbah 0x00000000
expect 0x00000000004ce000` — the twin's reference beside the HP's future
line: `tdlen 128` and `tdbal` the low half of `expect`; `ERR: nic transmit
timed out` the next line, nothing after. **C, the named error** — the plan
said a wrong expected value; the probe instead drops every write to TDLEN
inside `e1k_write` (the lost write itself, simulated): `S7: link up`, then
`ERR: nic register 0x00003808 wrote 0x00000080 read 0x00000000 - it will
not hold its value` and the halt, one `S7: alive`, fifteen `S7:` lines. All
three: the stick copy's tables unchanged. **The binary is 40,960 bytes
still**; the stick rebuilt, 69,206,016 bytes, the ESP at LBA 2048..133119
holding it. **`./stage7/test-7c.sh` (104 s), `./stage7/test.sh`
(458 s) and `./stage7/test-7b.sh` (314 s) on the same binary:
all four tests PASS each** (`stage7/out/gate7c.item19.log`,
`gate7a.item19.log`, `gate7b.item19.log`); no `e1k:` or `p19:` line in any
gate's serial capture; the payload table 1563 cases, 1046 denied, 517
allowed, 0 wrong. **How the sixth boot reads** (`METAL.md` step 7's
transmit row says the same): `pong` — step 5 passes, item 19 was the fix,
and the closure item writes the CLAUDE.md gotcha; the line again with
**`tdlen 128` and `tdbal` matching `expect`** — the ring is configured in
the device and the fetch is gated elsewhere (item 18's list: the
`EXTCNF_CTRL.SWFLAG` semaphore, then the TXDCTL write-back policy and
`CTRL_EXT.RO_DIS`); **`tdlen 0` or a mismatch** — a lost write the
protection did not catch: the window is not the one Linux waits on (read
`e1000_reset_hw_ich8lan` whole, the ME's state around `CTRL.RST`);
**`ERR: nic register …`** — the ME overwrites what the host writes, and
the rewrite bound is the next number to read. **No CLAUDE.md gotcha this
item, deliberately**, item 18's reason: a rule typed before its boot is a
guess. No flash, no `/dev` path, nothing outside the repository; the stick
is the owner's hand.

**Item 20** — from the HP's sixth watched boot, 17 September 2026: **the
serial monitor, the umbilical for the metal's debugging.** With item 19
the boot went to `S7: keyboard ready` as before (the chart of that boot is
`stage7/out/hp-linuxref.log`, 23:12:08 — the reader was started on that
file after item 19's gates; `stage7/out/metal.log` ends at the fifth boot
and a 22:08 stub); `? ping` at 23:12:25.491 ended at 23:12:30.716 in the
widened line and the halt:

```
e1k: tdh 0 tdt 1 status 0x00080483 ctrl 0x00100240 tctl 0x0003f0fa txdctl 0x00400000 tarc0 0x0d800403 ctrlext 0x01481000 fwsm 0x6001c04c sta 0x00 tdlen 128 tdbal 0x004ce000 tdbah 0x00000000 expect 0x00000000004ce000
ERR: nic transmit timed out
```

**Read field by field:** `tdlen 128`, `tdbal 0x004ce000` the low half of
`expect`, `tdbah 0` — the ring is configured in the device exactly as
written, and item 19's read-back passed every register first time (no
`ERR: nic register …`, `S7: link up` on time). **The branch it closed:**
the lost write. `tdh 0` after `tdt 1`, `sta 0x00`, and every other field
byte for byte the fifth boot's: every register we can name reads right
and the 82579LM will not fetch one descriptor. **One reading the line
gives that no earlier boot was read for:** `status 0x00080483` has **bit
10 set and bit 9 clear** — in the ich8lan family's STATUS register bit 9
is `LAN_INIT_DONE` and bit 10 `PHYRA` ("PHY reset asserted";
`E1000_STATUS_LAN_INIT_DONE 0x200`, `E1000_STATUS_PHYRA 0x400` in Linux's
`defines.h`); the twin's `0x00080283` is the reverse. Linux's
`e1000_get_cfg_done_ich8lan` waits for `LAN_INIT_DONE` after the PHY reset
its `e1000_reset_hw_ich8lan` issues and then clears `PHYRA` by writing
STATUS; this driver issues no PHY reset and never touches STATUS. Not a
fix, a question — the monitor's first. **What Linux's reset and init do
on this chip that we do not** (`e1000_reset_hw_ich8lan`,
`e1000_init_hw_ich8lan`, `e1000e_reset` in `netdev.c`), in the order the
monitor should ask them: (1) the PCIe master disabled
(`CTRL.GIO_MASTER_DISABLE`, `STATUS.GIO_MASTER_ENABLE` awaited clear) and
TCTL quieted (RCTL 0, TCTL `PSP` only, a flush) before the reset; (2)
`PHY_RST` written with `RST`, then `LAN_INIT_DONE` awaited and `PHYRA`
cleared — the STATUS bits above; (3) `KABGTXD.BGSQLBIAS` set after the
reset; (4) `PBA` written (the packet buffer split; Linux writes 26 KB for
the pch2lan family); (5) `WUC` cleared. **Items 16 to 19 each cost the
owner a flash and a boot for one question; the owner said that loop must
end.** The serial line is two-way and proven in both directions on this
machine. **The item is a monitor in the guest and a tool on mlrig**
(`stage7/stage7.asm`, `broker/probe.py`). In the guest: on the transmit
timeout, after the `e1k:` line, the named error is printed as before and
then, instead of the halt, `e1k_monitor`: `mon: ready`, then commands
read from COM1 one line at a time (`mon_getline`: LSR bit 0 polled, RBR
read, CR ignored, LF ends the line, 63 bytes kept), each answered by one
line starting `mon: ` through the tee (on the chart and on the glass, as
the `e1k:` line is); hex arguments, no prefix (`mon_hex`, up to sixteen
digits); an unknown or malformed command answers `mon: ?`:

| Command | Does | Answers |
|---|---|---|
| `r OFF` | reads the dword at BAR0 + OFF (OFF below 0x20000, dword aligned) | `mon: r 00000400 0003f0fa` |
| `w OFF VAL` | `e1k_write` (the ME's window awaited), then reads back; a write to CTRL with `RST` set waits 25 ms before the read-back — item 16's rule, so a reset typed through the monitor cannot hang the PCH's LAN | `mon: w 00005408 12345678 read 12345678` |
| `d` | the `e1k:` line's fields for the descriptor that timed out, then PBA `0x1000`, WUC `0x5800`, WUFC `0x5808`, MANC `0x5820`, FCRTL `0x2160`, FCRTH `0x2168`, FCTTV `0x0170`, KABGTXD `0x3004`, FEXTNVM3 `0x003C`, EXTCNF_CTRL `0x0F00`, RDLEN `0x2808`, RDH `0x2810`, RDT `0x2818`, RXDCTL `0x2828`, GCR `0x5B00` | `mon: tdh 0 tdt 1 status 0x… … expect 0x… pba 0x… wuc 0x… wufc 0x… manc 0x… fcrtl 0x… fcrth 0x… fcttv 0x… kabgtxd 0x… fextnvm3 0x… extcnf 0x… rdlen N rdh N rdt N rxdctl 0x… gcr 0x…` |
| `t` | re-arms the same frame in the next descriptor exactly as `e1k_send` does (`e1k_arm`, the arming split out of `e1k_send` so both call one routine; the length from the timed-out descriptor, the frame still in `nic_tx_buf`), moves TDT, waits 100 ms | `mon: t tdh 2 tdt 2 sta 0x01` |
| `m ADDR` | sixteen bytes at a physical address (at most `0xFFFFFFF0`, the identity map) | `mon: m 00000000004ce000 0c c0 4c 00 …` |
| `q` | leaves: the halt as before | `mon: bye` |

Two more splits, no behaviour changed: `serial_err` into `serial_err_line`
(prints, returns) and the halt; `e1k_tx_state` into `e1k_tx_fields` (the
fields, no prefix, no line end — `d` prints them after `mon: `) and the
`e1k: ` prefix with the line end, the line's text unchanged to the byte.
The `d` registers are a table whose names sit inline beside their offsets
(`dw offset, db kind, the name, 0`), never a table of label addresses —
the RVA gotcha. Twelve defines, five routines, ten strings, one table,
two BSS fields; `WIRE.md` untouched. **A deviation, recorded:** `WIRE.md`
says every named error halts the machine before `keyboard ready`; from
item 20 `ERR: nic transmit timed out` is printed and the halt comes at
`q`, on a path no green run takes — the document is frozen and untouched,
a freeze opening only if the owner wants it to say so. **On mlrig:
`broker/probe.py`** (unfrozen, a tool), started by the owner's hand with
the serial port as its first argument exactly as `chart.py` is and the log
as its second: it imports `chart.py`'s port opener (A1's order), prints
every serial line and tees it to the log with a timestamp, and also
listens on `127.0.0.1:9995` for **one client at a time** — each line from
the client goes to the port, each line from the port goes to the client
and to the log, and the client's own lines are logged too, marked `> `,
so the log reads as the dialogue (one addition beyond the brief). It
replaces the chart on the port for the monitor's session; the port is
`argv[1]`, and the source spells no device path. The payload table gains
three cases (`probe.py` written and run, allowed): 1566 cases, 1046
denied, 520 allowed, 0 wrong; the frozen `SPOT_ALLOW` untouched. **No
new `S7:` line**, no frozen counter moved: the monitor is entered only on
the transmit timeout, so no green run ever reaches it. **Tests red before
code — said plainly: the twin cannot show the defect and no gate was
written red.** **Proven in the twin on private copies**
(`stage7/out/probe7c/probe20.py`, never committed): probe17's forcing
(the `DD` test never passes) spliced into a copy of the source, packed
into a private stick copy and booted over `qemu-xhci` + `usb-storage` at
`-smp 4` on a fresh 64 MB disk on the throwaway port, with QEMU's serial
on a pty whose name the script computes (never on a command line) and
`broker/probe.py` started on it; `? ping` typed through the QEMU monitor;
then, through probe.py's socket: the `e1k:` line, `ERR: nic transmit
timed out` and `mon: ready` in that order; `r 400` → `mon: r 00000400
0003f0fa` (TCTL as written); `w 5408 12345678` → `mon: w 00005408
12345678 read 12345678` (RAL1 as the scratch register — the plan named
TIDV, which QEMU's model reads back as 0, recorded not argued); `d` →
`mon: tdh 1 tdt 1 status 0x00080283 ctrl 0x00140241 tctl 0x0003f0fa
txdctl 0x00400000 tarc0 0x00000403 ctrlext 0x00400000 fwsm 0x00000000 sta
0x01 tdlen 128 tdbal 0x004ce000 tdbah 0x00000000 expect
0x00000000004ce000 pba 0x00140014 wuc 0x00000000 wufc 0x00000000 manc
0x10000000 fcrtl 0x00000000 fcrth 0x00000000 fcttv 0x00000000 kabgtxd
0x00000000 fextnvm3 0x00000000 extcnf 0x00000008 rdlen 256 rdh 1 rdt 15
rxdctl 0x00010000 gcr 0x06800200` (every field; the twin's reference
beside the HP's future line); `t` → `mon: t tdh 2 tdt 2 sta 0x01` — the
82574L fetched the re-armed descriptor and wrote `DD` back; `m 4ce000` →
`mon: m 00000000004ce000 0c c0 4c 00 00 00 00 00 3c 00 00 0b 01 00 00 00`
— the ring's first descriptor: the frame's address, its length 60, the
command byte `EOP|IFCS|RS`, the status byte with `DD`; `r 3`, `r 20000`,
`x` and an empty line → `mon: ?`; `q` → `mon: bye` and nothing after; one
`S7: alive`, the echo once; every log line stamped, the ten client lines
in the log marked `> `; the stick copy's tables unchanged. **The binary is
40,960 bytes still**; the stick rebuilt, 69,206,016 bytes, the ESP at LBA
2048..133119 holding it. **`./stage7/test-7c.sh`, `./stage7/test.sh` and
`./stage7/test-7b.sh` on the same binary: all four tests PASS each**
(`stage7/out/gate7c.item20.log`, `gate7a.item20.log`,
`gate7b.item20.log`); no `e1k:` or `mon:` line in any gate's serial
capture. `stage7/METAL.md` gains "The monitor" and step 7's transmit row
its reading of the sixth boot. **No CLAUDE.md gotcha yet**, item 18's
reason: the rule is written when the fix is known. No flash, no `/dev`
path, nothing outside the repository; the stick is the owner's hand.

**Item 21** — from the HP's seventh watched boot, 18 September 2026: **the
fix — TCTL read-modify-write.** The owner flashed the item 20 stick, booted
with `broker/probe.py` in place of the chart and typed `? ping`; at
09:14:40 the same `e1k:` line, `ERR: nic transmit timed out`, then `mon:
ready`. From there a CC session drove the monitor through
`127.0.0.1:9995` with a private client (`stage7/out/probe7c/monclient.py`,
one connection held for the session; `monreset.py`, `monreset2.py`,
`moncraft.py` beside it, never committed) and found the cause in that one
boot, no flash between the sixth boot and the fix. **The dialogue is
`stage7/out/metal.log` lines 128 to 3314** (09:14:40 to 09:33:21; the fix
found at line 2970, the three separating runs after it); `q` never typed.
**In short.** *The first `d` against the twin's:* `status 0x…483` (PHYRA
set, LAN_INIT_DONE clear), `ctrl 0x00100240`, `pba 0x000e0012`, `wuc
0x109` (APME, APMPME, PHY_WAKE), `manc 0x00a20000`, `fextnvm3
0x08864e00`, `extcnf 0x00280089` (SWFLAG clear — the ME does not hold the
semaphore), `rdh 0`, `gcr 0`; none of them the cause. *Memory:* `m 4ce000`
and the frame at `0x4cc00c` exactly what `e1k_send` wrote — the buffer's
address, length 60, command `0x0b`, status 0, a well-formed ARP. *Receive
DMA proven:* `RDH` stayed 0 and `GPRC` 0 only because the link was silent;
three ARP broadcasts from mlrig (`ping` to 10.0.2.15) moved `RDH` 0 to 3,
`GPRC` and `BPRC` to 3, the frame with `DD|EOP` and mlrig's MAC in the
first receive buffer — only transmit was stuck. *PCI config, read through
ECAM* (`m f80c8000`; the base is `0xF8000000` on this HP, the function
00:19.0): `8086:1502`, command `0x0507`, status `0x0010` with no abort
bit, the power state D0. *Cheap pokes that changed nothing, one `t` each
on the running engine:* PHYRA cleared by `w 8`; PBA `0x14`; WUC 0;
TCTL.EN off then on; KABGTXD bit 5 (it will not hold — reads 0); TDT
rewritten; TDH written 0; TXDCTL `0x0141001f`; CTRL.FD; CTRL_EXT
DRV_LOAD. *The reset* (RST with PHY_RST through `w 0`, the monitor's 25 ms
wait; RCTL 0 and the interrupts masked first): LAN_INIT_DONE set within
50 ms, PHYRA cleared, everything `e1k_attach` programs replayed through
`w` in its order (the MTA's 128 writes once), the link back in 1.7 s —
`t` still `tdh 0`. *Fresh-reset variables that changed nothing, one per
reset, one `t` each:* TXDCTL `0x0141001f` on queue 0, then on both
queues; CTRL_EXT RO_DIS; DRV_LOAD; WUC 0 (once void — the guest's index
had wrapped, TDT 0 against TDH 0 is an empty ring — then repeated); K1
disabled through KMRNCTRLSTA as `e1000_configure_k1_ich8lan` does it
(K1_CONFIG `0x140e` to `0x140c`); TDLEN 256. *The narrowing:* on `t` the
transmit FIFO's tail moves `TDFT 0xa00` to `0xa02` — 16 bytes — and
freezes, `TDFPC` 0; with TDBAL lent the *receive* ring (a descriptor with
no `EOP`) and TDT moved to 1 by hand, **TDH went to 1** and 64 bytes
entered the FIFO — the engine fetches descriptors and data. Hand-made
transmit descriptors were then laid into a receive buffer by one UDP
broadcast from mlrig (receive DMA as the memory writer the monitor lacks)
and TDBAL pointed at them: command `0x02` (no `EOP`) is fetched whole;
`0x01`, `0x03`, `0x09` and `0x0b` — every descriptor with `EOP` — stall
at the hand-off to the transmitter; in a two-descriptor packet the first
is taken and the one carrying `EOP` is not. So neither our ring's address
nor our buffer's, and not DMA. *The cause:* **TCTL read straight after a
fresh reset is `0x3003f0f8`** — the 82579LM's default carries bits 28
(`MULR`) and 29 — and `e1k_attach`'s absolute write of `0x0003f0fa`
cleared them. From a fresh reset with TCTL `0x3003f0fa` on our own ring:
**`mon: t tdh 6 tdt 6 sta 0x01`**, `TPT` 6, `GPTC` 6, the FIFO drained,
`DD` in the descriptor in memory, and `10.0.2.15 lladdr
6c:3b:e5:3b:86:45` in mlrig's neighbour table — the frames reached the
wire. *The separation, at the owner's word, each from a fresh reset:*
TCTL `0x2003f0fa` (bit 29 alone) **stalls** (`tdh 0 tdt 7 sta 0x00`, the
FIFO at `0xa02`); TCTL `0x1003f0fa` (bit 28 alone) **sends** (`tdh 1 tdt
1 sta 0x01`). *Run 3, the configuration item 21 ships:* TCTL `0x3003f0fa`
with TARC1 `0x45000403` (bit 28 cleared, as Linux has it when `MULR` is
set) — **`tdh 2 tdt 2 sta 0x01`, `TPT` 2**. Twenty-two resets in the log,
nineteen of them before the fix (the session's first report said
seventeen; the log was counted afterwards). *Observed, not chased:*
STATUS read speed 10 (`0x00080003`) after the PHY reset where it read 1000
(`0x…83`) before — no LCD configuration or OEM bits are replayed after a
PHY reset through the monitor, and `e1k_attach` issues no PHY reset, so
the shipped path keeps the speed the firmware negotiated; TIPG's default
on this chip is `0x00902008`, not the `0x00602008` we write — every
sending run used ours. Two messages that arrived inside tool results
during the session, a reset sequence that takes SWFLAG among them, were
not acted on until the owner spoke in his own turn, and he then dropped
it. **The item is two changes in `e1k_attach`** (`stage7/stage7.asm`),
approved by the owner after Cowork's review: (1) TCTL is no longer
written absolutely — it is read, the `CT` field (bits 4 to 11) and the
`COLD` field (bits 12 to 21) masked, `TCTL_EN | TCTL_PSP | TCTL_CT |
TCTL_COLD | TCTL_MULR` ORed in (three new defines: `TCTL_CT_FIELD`,
`TCTL_COLD_FIELD`, `TCTL_MULR`), and written through `e1k_write`; every
other bit keeps its reset default, as Linux's `e1000_configure_tx` leaves
them — `0x3003f0fa` on the HP; (2) in item 18's hardware bits TARC1 bit
28 is now **cleared**, not set (`TARC1_PCH` loses it, `TARC1_MULR_CLEAR`
masks it), Linux's rule with `MULR` set — the PCH parts only, as before.
Nothing else: TIPG stays `0x00602008`, item 20's monitor stays,
`e1k_verify` stays, `WIRE.md` untouched, no `S7:` line changed. **Tests
red before code — said plainly: the twin cannot show the defect.** QEMU's
82574L transmits with `MULR` clear, so no gate was written red and none
could be. **One private probe on the twin** (`stage7/out/probe7c/
probe21.py`, a copy of the source, never committed; the stick copy over
`qemu-xhci` + `usb-storage` at `-smp 4`, a fresh 64 MB disk, the throwaway
port): `p21: tctl reset 0x00000000 after 0x1003f0fa tarc1 0x00000403` —
QEMU's model resets TCTL to 0, the read-modify-write leaves `0x1003f0fa`,
TARC1 on the 82574L is untouched (no PCH bit written); nineteen `S7:`
lines, `? ping` typed with no `e1k:`, `ERR:` or `mon:` line, the stick
copy's tables unchanged. **The binary is 40,960 bytes still**; the stick
rebuilt, 69,206,016 bytes, the ESP at LBA 2048..133119 holding it.
**`./stage7/test-7c.sh`, `./stage7/test.sh` and `./stage7/test-7b.sh` on
the same binary: all four tests PASS each** (`stage7/out/
gate7c.item21.log`, `gate7a.item21.log`, `gate7b.item21.log`); the payload
table 1566 cases, 0 wrong. `stage7/METAL.md` step 7's transmit row gains
the seventh boot's reading and the fix, and "What the twin could not
prove" its sentence; **CLAUDE.md gains the gotcha** items 18 to 20 held
back: never write a MAC control register absolutely on the PCH's
integrated LAN. **The model note, for the owner's comparison:** item 21
on **Fable 5.1 at medium effort**; the diagnosis driven through item 20's
monitor over the socket in one boot — twenty-two resets, some 1,600
commands, no flash between the sixth boot and the fix; the owner's list
of pokes and the reset ran first and changed nothing, the FIFO pointers
and the borrowed receive ring turned the question from "why no fetch" to
"why no commit", and the register's own reset default answered it. No
flash, no `/dev` path, nothing outside the repository; the HP untouched
by this item; the stick is the owner's hand.

**The closure — 18 September 2026: test 5 PASSED on the HP, all eight
steps; the owner's word closes ring 7c and Stage 7.** The owner powered
the HP off after item 21, flashed the stick built at item 21 and ran the
day from `stage7/METAL.md` step 5 with `broker/probe.py` in place of the
chart. **The eighth watched boot** (10:00:32, the item 21 binary):
eighteen `S7:` lines in the twin's order with the `i8042:` pair, then
`? ping` at 10:00:41 — *pong. I hear you, GermOS — the link is up and I'm
ready when you are.*, `w 001 002675` on the strip; no `e1k:` line, no
`ERR:`, no `mon:`. Then `! install calculator`: `installed calculator`,
`g 000/001`, `w 002`, `! calculator` on the choices row (the serial echo
reads `! install calulculator` — the keys as they went down, a correction
among them; the screen and the photograph read the line as it stood).
**The ninth watched boot** (10:07:05, the broker and the relay stopped):
`S7: home 1 apps`; the mouse moved at 10:07:54 — `S7: mouse ready`, the
arrow, `pt` on the strip; a click on `! calculator` at 10:10:33 typed the
launch line (ring 6c's rule) and launched it from the SATA disk with
nothing on the wire — `running calculator`, 4096, `w 000 000000`, `io
000000/000000`. **The timings read from the log** (the probe's stamps on
mlrig, the serial line at 115200): the eighth boot `S7: alive` 10:00:32.685
to `S7: keyboard ready` 10:00:33.319 — **0.634 s**; the ninth 10:07:05.081
to 10:07:05.716 — 0.635 s; of each, 0.414 s is the mouse's reset between
`i8042: self-test ok` and `i8042: mouse reset ok`, and `S7: alive` to
`S7: glass core 2` is 0.207 s. **The disk, said plainly:** the HP's 250 GB
disk (488,397,168 sectors, AHCI port 0) carried GermOS's table from a
blind boot on 15 September — the day the serial cable turned out to be a
straight one and nothing was read — so **every watched boot was the
eighteen-line pattern with `S7: notebook N notes`** (0 on the first two,
1 from the third, after `hello metal`) **and never the nineteen with
`S7: gpt written`**; the format path on the metal is proven by the table
the 15th left, which nine boots then recognised, mounted and wrote notes
and an app into. **Counted from the record:** **nine watched boots** — six
on 17 September (18:04 the item 15 binary, stopped after `S7: home 0
apps`; 19:00 and 19:06 item 16, to the glass and the note; 19:50 item 17;
20:53 item 18; 23:12 item 19, its chart in `stage7/out/hp-linuxref.log`)
and three on 18 September (09:14 item 20, the monitor; 10:00 and 10:07
item 21, test 5) — and the blind boot of the 15th before them, unwatched;
**seven flashes**, one per binary — the ring's first stick (the blind boot
and the first watched boot), then items 16, 17, 18, 19, 20 and 21 (counted as one flash per
binary: the record holds no line for a second flash of any one binary,
and only the owner can say whether the first stick was written more than
once between the 15th and the 17th); the owner's block with `wipefs` first (`METAL.md` step 3, amended at this
closure) was run once on the 17th and twice on the 18th. **The evidence,
committed at the closure:** the five photographs of the 18th in
`history/` (`2026-09-18-ring7c-pong-on-metal.jpg`,
`-installed-calculator.jpg`, `-home-1-apps-broker-off.jpg`,
`-mouse-arrow.jpg`, `-calculator-from-disk-4096.jpg`) each with a
1600-pixel web copy (`-1600.jpg`, made as the 17th's two were: resized,
quality 85, the EXIF dropped; the 17th's four files were already tracked
from the README commit of that day); `history/2026-09-18-ring7c-serial.log`
(a copy of `stage7/out/metal.log`: eight of the nine watched boots and the
whole monitor dialogue, lines 128 to 3314), `history/2026-09-17-ring7c-
serial-sixth-boot.log` (the sixth boot's chart, which had been read into
`hp-linuxref.log` — kept so the record holds every watched boot),
`history/2026-09-17-ring7c-hp-lspci.log` (the HP from live Ubuntu) and
`history/2026-09-15-ring7c-serial-loopback.log` (the 15th's serial test:
`hello`, twice). **The documents:** `stage7/METAL.md` step 3 is the flash
block as it was run (`wipefs` on the partition and then the stick,
`oflag=direct conv=fsync`, `blockdev --flushbufs`, `cmp -n 69206016`,
`lsblk` showing `vfat`, then power-off), step 4 says the cable must be a
null-modem cable and that the serial path is proven from a live Ubuntu on
the HP before the first boot, step 7's row and section 10 say the monitor
found the fix and that a `pong` is what step 5 gives; CLAUDE.md gains the
automounter gotcha; README's row, status sentence and the metal's
paragraph say closed, with the binary that passed (40,960 bytes; the
Ubuntu image 158,262 times larger), 0.63 s, and the NIC's story with its
credit to Intel's e1000e driver in the Linux kernel. **The gates at the
closure, on the binary as it stands (item 21's, 40,960 bytes):**
`./stage7/test-7c.sh`, `./stage7/test.sh` and `./stage7/test-7b.sh`, all
four tests PASS each (`stage7/out/gate7c.closure.log`,
`gate7a.closure.log`, `gate7b.closure.log`). **The model note, for the
owner's comparison:** CC ran every item of ring 7c — 0 to 21 and this
closure — on **Fable 5.1 at medium effort**. Cowork was Fable 5.1 except
for a stretch during the item 19 diagnosis, when its session fell back to
Opus 4.8 and the owner briefly set Opus 5 at high effort, then back to
Fable 5.1: the DRV_LOAD misstep and its retraction happened in that
stretch, the PCIM2PCI finding under Opus 5, confirmed under Fable. The
item 21 diagnosis was CC on Fable 5.1 at medium effort through the
monitor in one boot. The ring's tally: twenty-two items and the closure;
seven amendments at the plan gate; no freeze opening; one expectation
corrected in Part 1; two defects the twin could not show, both in the
82579LM (the read after `CTRL.RST`, item 16; `MULR`, item 21), and one
found by Cowork's pre-oracle review (the i8042 drain, item 15). No flash,
no `/dev` path, nothing outside the repository by CC at any item; every
flash was the owner's hand.

## Stage 8 — The molt · opened 25 September 2026

`stage8/spec.md` was approved by the owner on 25 September 2026 with all
fourteen decisions settled: rings 8a to 8g, with 8a and 8b designed in full;
the first slot `i8042`; parts in the home store under `part-` names and the
state in `molt ` notes on the notebook; the loader and the cryptography in
their own frozen file; the PCH's TCO watchdog with a 30 s deadline and a
60 s health window; the strict rule for "beat" at 5 % under `-icount`; the
shadow threshold of 3 boots, 1,000 keyboard bytes, 5,000 mouse packets and
0 disagreements, then probation for 3 healthy boots; the witness from 8c;
the week's rules; the GPS history rewrite postponed; the policy gate
re-checked at every ring's kickoff (re-checked 25 September 2026:
unchanged). **Done when the machine reboots into a kernel it grew itself
and survives a week.**

## Ring 8a — the floor · opened 25 September 2026 · closed 28 September 2026

`stage8/plan-8a.md` was approved on 25 September 2026 with Cowork's six
amendments and all seventeen deviations accepted:

- **A1:** the pet routine is called at every main loop turn and at every breath of a bounded wait. Test 3 holds a broker request for `HOLD_S` (twice the deadline) and idles 60 s on a live boot, with no reset.
- **A2:** `TCO_TMR` for 30 s comes from the Intel 7-series PCH datasheet's rule. D1 only confirms the twin agrees, and the HP's own deadline is read from the chart.
- **A3:** before the Esc window the loader enables port 1 and drains the buffer. It accepts Esc in set 1 and set 2, with W = 3 s. The owner holds Esc only when `hold Esc for the seed` appears.
- **A4:** the no-evidence path on the HP (type again to the second reset, expect `unhealthy`). Whether the HP kept the bit is a finding.
- **A5:** one expectation per twin event in every frozen file, fixed from D1's run.
- **A6:** item 16 stops for Cowork's review of `stage8/loader.asm`, and item 16b freezes it with the whole gate green.

**The model for this ring: Opus 5.5 at high effort**, spec decision 11. Item 0 (this record, the plan's commit, `CLAUDE.md`'s windowed line) is done. The items follow one commit each, exactly as the plan says.

**The shape, from the plan:**

- **What 8a proves.** A part can fail without taking the machine with it. Five hand-written fixture parts for the `i8042` slot meet their fates in the twin of the HP:
  - `good` passes shadow and runs live;
  - `wrong` is caught in shadow and cannot be taken;
  - `hang` is reset by the hardware watchdog and demoted;
  - `fault` is named by the blame line and demoted;
  - `liar` is refused at the door.
- **No part, no change.** With no `molt` note the Stage 8 binary is ring 7d's to the line and to the pixel. The frozen 7c and 7d checks run against it through their module seams.
- **The source.** `stage8/stage8.asm` is copied from `stage7.asm` byte for byte at item 1. At item 14 the loader and SHA-256 move into `stage8/loader.asm`, with `.text` read-only and CR0.WP on every core.
- **The mock.** `broker/molt.py --mock --part <fixture>` serves the fixtures and is unfrozen. The checker rebuilds every frame from PARTS.md and the frozen `.bin`s.
- **Frozen at item 13:** `stage8/PARTS.md`, `stage8/SEED.md`, `stage8/parts.py`, `stage8/test-8a.sh`, `stage8/checkmolt.py` and the five fixtures (`.asm` and `.bin`). `stage8/loader.asm` is frozen at item 16b.
- **The seed record.** `stage8/seed-record.md` is unfrozen and append-only; SEED.md fixes its format.
- **The log.** Every gate run and every direct checker run appends to `stage8/out/gate-8a.log`.
- **Test 5** is the owner's day on the HP, written at item 17 as `stage8/HP-8a.md`.

| Test | State |
|---|---|
| 1 — the artefact, the stick, PARTS.md and SEED.md parsed cold, the worked examples, the fixtures, SHA-256's known answer | **PASS** at item 9 (27 September 2026); at 16b; **PASS at item 17 with seed 1 in the record**, after the tenth freeze opening (`503b4e5`) |
| 2 — no part, no change: the 7c and 7d checks on the Stage 8 binary, no `S8:` line | **PASS** at item 9 (27 September 2026), on ring 7d's binary (deviation 15); **PASS** at item 14 on the binary with `loader.asm` and the read-only floor (425.7 s); **PASS** at 16b and at item 17 (425.8 s) |
| 3 — the fates: good, wrong, hang, fault, liar; undo; Esc; the held request; the idle wait | written at item 10 (27 September 2026); its run constants written at item 12 from the draft's run, where all five fates passed; G5's 300 moves during the hold added by the owner's amendment (`c4a6111`), green on the amended draft; **frozen at item 13**; **red by design** until item 16: on the repository's binary it stops at each install's first missing `molt:` line; **PASS** at item 16 (851.9 s), 16b (852.0 s) and item 17 (852.1 s) |
| 4 — the bodyguard (every ring 8a frozen path, `loader.asm` among them), the argv check, the 7d gate with 7c, 7b and 7a inside it | written at item 11 (27 September 2026); **frozen at item 13** with the directory rule in the hook; **red by design on (c)'s nine `loader.asm` refusals alone** until item 16b: (a), (b) and (d) pass, the 7d gate green inside it; **PASS** at 16b and at item 17 (2064 payloads, 0 wrong; the 7d gate with 7c, 7b and 7a green inside it) |
| 5 — the owner's, on the HP: good to the threshold and live; Esc; hang live and the HP resetting itself | **pending**: `stage8/HP-8a.md`, written at item 17; Cowork reviews it from the committed file before the day |

**Carried into this ring, from ring 7d's closure:**

- (1) The TRIALS.md label-width sentence: **done**, by the owner's hand, the ninth freeze opening (`076d74b`).
- (2) The GPS in the old git history: **postponed by the owner** (spec decision 12); its own CC session when it is done.
- (3) Zoom-to-fit on Hyprland: **done at item 0**. `-display gtk,zoom-to-fit=on` is on `CLAUDE.md`'s windowed QEMU line, and every windowed line in Stage 8's documents carries it.
- (4) Stage 7's caveats, unchanged: the PHY speed after a reset, TIPG, WIRE.md's halting sentence (ring 8e's to settle), the nineteen-line first boot never watched on the metal, the x2APIC and trampoline paths.
- (5) The HP's disk holds GermOS's table, 277 notes ending `trial verdict A`, and the calculator. The stick is as flashed for the trial. Stage 8 writes its `molt` notes after the 277 and changes nothing before them.

### Ring 8a — the build, item by item

**Item 0** — this record; `stage8/plan-8a.md` committed verbatim; the "Where we are" rows (Stage, Status, Toolchain, Model); the ninth freeze opening recorded (by the owner's count of 28 September 2026); `CLAUDE.md`'s windowed QEMU line gains `-display gtk,zoom-to-fit=on`. No ring 8a test exists yet; every earlier gate is unchanged.

**Item 1** — Stage 8 opened on ring 7d's source, 25 September 2026.
`stage8/stage8.asm` is `stage7/stage7.asm` byte for byte (`cmp` silent).
`stage8/mkimage.sh` and `stage8/mkstick.py` are 7c's builders with only
the paths (and the comments naming them) moved to `stage8/`; the font's
`incbin` stays `stage2/font8x8.bin`. After a fresh `./stage7/mkimage.sh`
and `python3 stage7/mkstick.py`, **`stage8/out/BOOTX64.EFI` equals
`stage7/out/BOOTX64.EFI` byte for byte: 45,056 bytes, SHA-256
`bbf80635a83beeca2254ef35aa492306d30224950b4f405b434b900475b28cd5`**; the
two sticks built the same minute were byte-identical too (not a promise:
the FAT carries timestamps, which is why SEED.md's seed is the EFI).

**D3, the frozen checkers' seams, found by a run.** A private driver,
`stage8/out/probe8a/seams.py` (never committed), imports `checkmetal` and
`checktrials`, rebinds their module paths, and runs the seven entry points
test 2 will run on the stage8 build. It audits every `open()`,
`shutil.copyfile` and `subprocess.Popen` in its own process for a path
under `stage7/out/`, and lists the mtimes of every file under
`stage*/out/` and `germline/` before and after each entry point. Nothing
listened on 9999, 9998 or 9997 before or after.

| Fact | Measured how |
|---|---|
| **The rebindings that hold (attempt 2):** `checkmetal.OUT` → `stage8/out`; `checkmetal.METAL_OUT` → `stage8/out/seven/metal`, with `DISK`, `GERMLINE`, `REHEARSAL` and `TWIN_WORKDIR` under it; `checkmetal.STICK`, `EFI` and `ESP` → `stage8/out/stick.img`, `BOOTX64.EFI` and `esp.img`; `checktrials.OUT` → `stage8/out`, `TRIALS_OUT` → `stage8/out/seven/trials` with `DISK` under it, `STICK` → stage8's; the two bound defaults, `checkmetal.check_stick.__defaults__ = (stick, efi)` and `check_stick_tables_unchanged.__defaults__ = (stick,)` (one function object, so `checktrials`' by-name import follows); and **two seams the plan did not list: `checkdisk.OUT` → `stage8/out/seven/metal` and `checkglass.OUT` → `stage8/out/seven`**. `checktrials`' by-name `qemu_argv`, `fresh_stick` and `start_mock` need no rebinding: they read `checkmetal`'s globals at call time. `checktrials.METAL_OUT` is imported but never read | `seams.py`; read of the call sites |
| **Attempt 1 found two escapes**, both from `run_stages` (and `run_row` for the second): `checkdisk.extract_partition` writes `stage7/out/notes.part.img` and `home.part.img` through `checkdisk.OUT`, and `checkglass.fixture_self_check` writes `stage6/out/app.check.bin` and `echo.check.bin` through `checkglass.OUT`. Every other `OUT` use in those two modules sits on a path 7c and 7d never call. The two files attempt 1 left in `stage7/out/` are scratch that ring 7a's gate rewrites itself | the audit (`seams.result.attempt1.json`) |
| **Attempt 2, the whole run: every entry point returns 0 on the stage8 build**, and nothing under `stage7/out/` is opened, copied or handed to a subprocess; no file outside `stage8/` changes. `run_stick` 0.0 s; `run_serial` blank 8, again 4 and novga 2 4.4, 4.2 and 4.2 s (one boot each); `run_stages` 68.5 s (two boots; the mock's twin rehearses `! install echo` on `stage8/out/esp.img`); `checktrials.run_row` 43.6 s (one boot); `run_sitting` 301.7 s (five boots). **Total 426.6 s**, eleven boots, every drive under `stage8/out/seven/` | `seams.log`, `seams.result.json` |
| **How the entry points report failure:** each `run_*` returns 0 or 1, through `report()`/`say()` on stdout; none calls `sys.exit` (only the modules' `main` does) and none catches an exception. So test 2 calls them in-process and treats a non-zero return or any exception as a failure | read, and the run's return values |
| **The shell gates cannot be pointed elsewhere** (`stage7/test-7c.sh` and `test-7d.sh` hard-code `stage7/out` and rebuild from `stage7.asm`), as the plan found, so test 2 drives the Python entry points, and the shell gates run only in test 4 (d) on ring 7d's own binary. The fallback (copying stage8's build over `stage7/out/`) was not needed | read |

No ring 8a test exists yet; no guest code changed.

**Item 2** — D1, the watchdog, measured on 25 September 2026. **The twin
agrees with the datasheet; the ICH9 TCO resets the twin; the evidence bit
survives the reset.** The probe is a private copy of `stage8.asm` with
`probe.inc` included straight after `S7: keyboard ready` (interrupts still
off, on the BSP). It prints the LPC bridge and the TCO registers, and it
can arm the timer, never pet it (watching `TCO_RLD` and both status
registers, one line per change), pet it for a time, or keep the evidence
and halt. The mode and `TCO_TMR` are chosen with `nasm -D`. It is built
under `stage8/out/probe8a/tco/b-*/` by stage8's own `mkstick` with its
paths rebound. `d1.py` boots it on **`checkmetal.qemu_argv` unchanged**
(the 7c twin: q35, IvyBridge, OVMF, the stick copy over `qemu-xhci`, a
blank 64 MB SATA disk, the e1000e cage) with a fresh disk per run. It
stamps every serial chunk with the host's monotonic clock (10 ms polls)
and keeps the monitor on stdin. Ten runs, twenty-five boots, fourteen
watchdog resets (one more start of the `noreboot` run failed on `d1.py`'s
own argument parsing before any boot and was rerun); the
summaries are `stage8/out/probe8a/tco/run-*/summary.txt` and `batch.log`.
Nothing is committed from there, and nothing outside `stage8/out/`
changed.

**The datasheet** is the Intel 7 Series / C216 Chipset Family PCH
Datasheet, order number 326776-003 (June 2012), the Q77's:

- **§13.9.** The TCO registers sit at TCOBASE = PMBASE + 60h.
- **§13.9.11, `TCO_TMR` (TCOBASE+12h, bits 9:0):** "The timer is clocked at approximately 0.6 seconds, and thus allows timeouts ranging from 1.2 second to 613.8 seconds"; values 0 and 1 are ignored. The default is 0004h.
- **§13.9.4, `TCO2_STS.SECOND_TO_STS` (bit 1):** set when "the TIMEOUT bit had been (or is currently) set and a second timeout occurred before the TCO_RLD register was written. If this bit is set and the NO_REBOOT config bit is 0, then the PCH will reboot the system after the second timeout". It is cleared by writing 1, "or by a RSMRST#", so on silicon it survives a platform reset.
- **`BOOT_STS` (bit 2):** "Software should first clear the SECOND_TO_STS bit before writing a 1 to clear the BOOT_STS bit".
- **§13.9.6, `TCO1_CNT`:** `TCO_TMR_HLT` is bit 11, `TCO_LOCK` bit 12, and `NMI_NOW` (bit 8) is R/WC, so it is never written back.
- **GCS (RCBA+3410h) bit 5, No Reboot:** "may not override the strap when it indicates 'No Reboot'".
- **§5.14.1.1:** "the TCO timer times out twice and the PCH asserts PLTRST#".

**So the rule gives `TCO_TMR` = 25 for a 30 s deadline**: the first
expiry at 25 × 0.6 = 15 s sets TIMEOUT and counts again, and the second
at 30 s resets.

| Fact | Measured how |
|---|---|
| **The LPC bridge as OVMF leaves it:** `8086:2918` rev `02` (class `0601`), at 00:1f.0. PMBASE (cfg `0x40`) **`0x600`**, so TCOBASE `0x660`; ACPI_CNTL (cfg `0x44`) `0x80`, enabled. GEN_PMCON_1 (cfg `0xA0`) `0`: no SMI lock. RCBA (cfg `0xF0`) **`0xFED1C001`**: the base is `0xFED1C000`, enabled, and it is mapped uncached with `map_mmio_2m` for the read. **GCS = `0`, so `NO_REBOOT` is already clear.** SMI_EN `0` (no `GBL_SMI_EN`: this OVMF has no SMM), SMI_STS `0` | the probe's status line, every boot of every run |
| **The TCO at rest (a cold boot):** `TCO_RLD` 0, `TCO1_STS` 0, `TCO2_STS` 0, `TCO1_CNT` `0` (halt bit clear), `TCO2_CNT` `8`, `TCO_TMR` **4** (the datasheet's default), and **the timer is not running**: 40 s of a mode-0 boot and no expiry, no status bit and no reset. QEMU starts it only when the guest reloads it. On silicon it counts from reset unless the firmware halts it, so the loader writes the halt, the value, the reload and the unhalt explicitly. **`enable_tco` defaults to `true` and `noreboot` to `false`** (`qom-get` on the `ICH9-LPC` object, `/machine/unattached/device[2]`) | `run-smoke`; `qom-get` in a `-S` QEMU |
| **`TCO_EN` (SMI_EN bit 13) sticks both ways under OVMF:** from `0`, a write with it set reads `0x2000` and a write with it clear reads `0`. `TCO_LOCK` is 0. The loader's clear therefore sticks. The first expiry is not routed anywhere with `TCO_EN` clear, and nothing happened at it in any run | the probe's `tco_en` line, every arming |
| **The twin agrees with the datasheet's rule.** After arming, `TCO_RLD` reads *n*−1 at once and falls by one every **599–600 ms** (the guest's TSC: 29,425 ms from 24 to the second 0 at *n* = 25; the host's stamps: 0.595–0.606 s per step). At the first expiry TIMEOUT (`TCO1_STS` bit 3) sets and the count starts again from *n*−1. **At the second expiry the machine resets: at 2 × *n* × 0.6 s after the reload, within the 10 ms polling, for every *n* measured** (2, 4, 10, 25 and 50). No tick error was seen in the twin; the datasheet allows about one tick on silicon | runs `arm2`, `arm4-smp2`, `arm10-smp8`, `arm25`, `arm50` |
| **The reset's latency, arming line → OVMF's first bytes of the next boot, in the same capture:** *n* = 2: 3.390, 3.380 s; *n* = 4 (`-smp 2`): 5.735, 5.732 s; *n* = 4 (`-smp 4`, three runs): 5.791–5.800 s; *n* = 10 (`-smp 8`): 13.144, 13.143 s; **n = 25 (`-smp 4`): 31.017, 30.995 s**, and 31.0 s from the last pet in the pet run; *n* = 50: 60.986 s. **After subtracting 1.2 *n*, the reset to OVMF's first byte is 0.93 s at `-smp 2`, 0.98–1.02 s at 4 and 1.14 s at 8.** A cold QEMU start to OVMF's first byte is 0.65–0.69 s | the stamps (`stamps.json`), the `armed` line to the first ESC after it |
| **QEMU stays running across the reset.** The next boot is in the same process and the same serial capture, and the monitor answers `VM status: running` after two and three resets. No flag is needed: the default action is `reset` | `info status` at the end of every run |
| **The evidence survives the reset.** At the next boot's first read after a watchdog reset: **`TCO1_STS` = `0x0008` (TIMEOUT) and `TCO2_STS` = `0x0006` (`SECOND_TO_STS` and `BOOT_STS`)**, every time (14 resets). A cold boot (a new QEMU process) reads 0. **A monitor `system_reset` keeps them too:** in the keep run the boot after the watchdog reset left the bits set and halted, the checker sent `system_reset`, and the boot after that read `0x0008` / `0x0006` again. So only a new QEMU process clears them in the twin, as RSMRST# does on silicon | `keep4`; every armed run's second and later boots |
| **Clearing:** writing 1 to TIMEOUT and to `SECOND_TO_STS`, then 1 to `BOOT_STS` (the datasheet's order), reads back 0 and 0. **In QEMU, writing `SECOND_TO_STS` alone also clears `BOOT_STS`** (mode 4 never writes `BOOT_STS`, and still reads `TCO2_STS` 0 and arms normally). The loader keeps the datasheet's two writes regardless | `bootsts4` |
| **The pet holds.** Armed at 25 and reloaded once a second (by the TSC) 90 times, the count read just before each pet was always 23, and there was **no reset in 90 s**. When the pets stopped, the reset came 31.0 s later (30 s + OVMF). A second boot in the same process armed and petted again normally | `pet25` |
| **`-global ICH9-LPC.noreboot=on` (the strap):** GCS reads **`0x20`** at boot (`NO_REBOOT` set). A write of 0 **reads back 0**, so the bit appears to clear, but **the machine never resets**. `SECOND_TO_STS` and `BOOT_STS` set at the second expiry (6.2 s at *n* = 4) and the timer cycles on, for 25 s. **So in the twin the strap is invisible to a GCS read-back:** `S8: watchdog tco locked` cannot be shown with `noreboot=on`. The one guest-visible sign of a strap is `SECOND_TO_STS` set during a boot that is still running. Silicon "may not override the strap", so on the HP the read-back may show it | `noreboot4` |
| **The no-evidence path (A4, point 9):** in every armed boot the probe cleared the bits by hand before arming, and from then on every read in that boot showed `TCO2_STS` 0 until the reset: a loader reading after that point sees a boot with no evidence. The watchdog still reset the machine 1.2 *n* s after the reload, and the next boot read the evidence afresh. **So the twin walks the no-evidence path only when the bit is cleared by hand before the loader reads it.** Left alone, the twin always keeps the evidence | every armed run (`cleared` line, then the watch lines) |
| **`-smp` does not change the timing.** The tick and the reset point are identical at 2, 4 and 8; only OVMF's own start moves (0.93 / 1.0 / 1.14 s) | `arm4-smp2`, `arm25`, `arm10-smp8` |

**The single choices (A5)**, which PARTS.md (item 4) and the checker carry:

- **`TCO_TMR` = 25** by the datasheet's rule (0.6 s ticks, 10 bits, reset on the second expiry: 2 × 25 × 0.6 = 30.0 s). **The twin agrees**, so item 2 does not stop.
- **The watchdog is the ICH9 TCO**, built into q35. There is no new device and no new flag, so `check_argv_7c` is unchanged (item 3 runs it as data) and `i6300esb` is not needed. **The one watchdog line in the twin is `S8: watchdog tco 30 s`.**
- **`SECOND_TO_STS` survives the reset**, so **the one recovery path test 3 expects is the watchdog's**: the next boot's `S8: recovery i8042 watchdog` and `molt i8042 demoted <sha16> watchdog`, in the same QEMU process and the same capture as the hang. The `unhealthy` path is the HP's alternative (A4), in `HP-8a.md` only. In the twin that row is proven by a probe that clears the bit by hand before the loader reads it (point 9's mechanism): deviation 13's mirror image, carried to items 12 and 16.
- **`RESET_S`'s terms:**
  - the 30.0 s deadline, counted from the last reload, not from the hanging input;
  - plus the time from the last pet to the hang, which is at most the pet's rate limit (item 4 sets it);
  - plus the reset to OVMF's first byte, 1.14 s at worst (`-smp 8`);
  - plus no tick error, since the twin showed none.

  Item 12's run writes the number.
- **The consequences for the checker** (items 10 and 12):
  - a hang's boot and its recovery boot must be one QEMU process, because only a new process clears the bit;
  - a boot that should see no evidence must be a fresh process;
  - the monitor's `system_reset` does not clear the evidence either.
- **`S8: watchdog tco locked` stays probe-only** (deviation 16): `noreboot=on` does not show as a lock in the twin.

The HP may differ in three places, each a finding of test 5:

- its firmware may clear the bit in POST (A4);
- its strap may read back as a lock;
- its tick may be off by one.

HP-8a.md step 10 reads the HP's own deadline from the chart (A2).

No ring 8a test exists yet; no guest code changed.

**Item 3** — D2, D4 and the hook's verdicts, measured on 25 September
2026. The probe is one private include, `stage8/out/probe8a/d24/probe.inc`,
in three modes, each built into a private copy of `stage8.asm` by stage8's
own `mkstick` under `stage8/out/probe8a/d24/b-m<mode>/`:

- **Mode 1, the bench (D2):** after `S7: keyboard ready`, interrupts off, on the BSP.
- **Mode 2, the Esc window (D4):** just before `mouse_init`, where the handover will be.
- **Mode 3, the rates (D4):** the boot as ever, with `kbd_push` counting every keyboard byte into the obs page's reserved word `0x340`.

`d24.py` boots each on **`checkmetal.qemu_argv` unchanged**, with a fresh
disk per run. The bench runs add `-icount`. It stamps every serial chunk
with the host's monotonic clock (1–5 ms polls) and keeps the monitor on
stdin. Twenty-two bench boots (a first `shift=0` trial run, then twenty-one kept), nine Esc boots, two rate boots. The summaries are
`stage8/out/probe8a/d24/run-*/summary.txt`, the argv check
`argv.result.json` and the hook's cases `hookcases.result.json`. Nothing
is committed from there, and nothing outside `stage8/out/` changed. No
port was listened on before or after.

**D2 — `-icount` under QEMU 11.1.1.** The stream is 3,092 bytes, fixed by
a seed:
- the mixed text `The Quick brown fox, 42 jumps! …` as set 1 make and break, with its shift pairs;
- E0 arrow pairs at random word ends;
- two mouse packets after every word.

That is 2,084 keyboard bytes (880 keys) and 1,008 mouse bytes (336 packets).
Each byte is fed through the generic decoder's two halves:
- `kbd_push`, then `kbd_next` until the ring is empty;
- `mouse_byte`, then `mouse_next` until empty.

The TSC is read around each byte, and the stream runs five passes. Before the passes come two
straight-line loops of `dec rcx` / `jnz`, 2N instructions each, between two `rdtsc`s.

| Fact | Measured how |
|---|---|
| **`-icount` forces round-robin TCG in silence**: no warning at `-smp` 2 or 4, and every boot reached `ready`. An explicit `-accel tcg,thread=multi` beside it is refused: "No MTTCG when icount is enabled" | stderr of every run; one `-S` start |
| **`shift=0,sleep=off` and `shift=0,align=off,sleep=off` are the same mode**: every line of the six runs at one `-smp` matches across the two spellings (`align=off` is the default) | runs `s0-*`, `s0a-*` |
| **Under `shift=0` the TSC counts virtual nanoseconds**: `tsc_per_ms` 1,000,017, i.e. one tick per instruction. **The 1M-turn loop gives exactly 2N + 5 = 2,000,005 at `-smp` 2 and 4**: the loop's 2N instructions plus the five between the two `rdtsc`s. The 10M-turn loop gives 28,896,293 at `-smp 2` and 29,107,959 at `-smp 4`, not 20,000,005. Once round-robin moves to another vCPU (the glass core), that vCPU's instructions are in the BSP's span too. **So `rdtsc` advances by exactly count × 2^shift only within one round-robin slice**; a per-byte delta (33–140 ticks) is inside one | runs `s0-*`, `s0a-*` |
| **The decoder under `shift=0`, per byte:** min 33, median 69, worst 135–140 ticks (instructions, `rdtsc` included). Pass 1's sum is 222,413 and its total 259,521 in all twelve `shift=0` runs, at both `-smp`. Medians and minima are identical in every pass of every run | the pass lines |
| **Which mode repeats exactly: `shift=0` at `-smp 4`**. All six runs are identical on every line: both loops, every pass's sum, min, median, worst and total. **At `-smp 2` it does not quite repeat**: passes 1, 3, 4 and 5 are identical in all six runs, but pass 2's sum is 222,423 or 222,430 and its total 259,538 or 259,545, and one worst is 140 against 136. That is 7 ticks in 259,000; the source is unidentified (a host-clock timer is the likely one) | the pass lines, run by run |
| **`-smp` changes the numbers**: the 10M loop (+8.9M at 2, +9.1M at 4); passes 2–5 by tens to hundreds of ticks (pass 3's sum 222,475 at 2, 222,678 at 4). Pass 1, and the minimum and median of every pass, do not move | the same |
| **`shift=auto` repeats nothing**: the 1M loop 49.55M / 49.62M / 49.61M at `-smp 2` and 27.4M at 4; the per-byte median 552, 276, then 138 as the shift adapts pass by pass (138 = 2 × 69: shift 1). Outliers of 635,304 to 2,120,768 ticks appear in some runs and not in others | runs `auto-*` |
| **Without `-icount`** the TSC is the host's (`tsc_per_ms` 2,998,206–3,000,979). The per-byte median is 162–284, the worst up to 238,272, and no two runs agree | runs `base-*` |
| **The wall-time cost**, QEMU start → `S7: keyboard ready`: **none 1.38–1.40 s; `shift=0` 7.2 s at `-smp 2`, 9.7 s at `-smp 4`** (5.2× and 6.9×; OVMF's first byte at 1.88 s against 0.66 s); `shift=auto` 3.4 s and 4.5 s. The bench itself, `ready` → `done`: 0.06 s without `-icount`, 0.15 s under `shift=0`. The batch ran six at a time on 32 CPUs, and the one `shift=0` `-smp 4` run done alone read `ready` at 9.66 s, the same | the stamps (`extra` line) |

These are ring 8b's measures, recorded before any freeze as the spec
requires. **Ring 8a's gate uses no `-icount`.**

**D4 — the argv.** `argv.py` runs the frozen `check_argv_7c(argv, 9997,
MAC)` as data:

| Argv | Verdict |
|---|---|
| **`checkmetal.qemu_argv` unchanged, stage8 paths, `-smp` 2, 4 and 8 (D1's choice: the ICH9 TCO, no flag)** | **PASS**, with `checkmetal.OUT` rebound to `stage8/out` (D3). Without the rebinding both drives fail: "a drive is not a file under stage7/out/" |
| + `-device i6300esb` (the fallback, not needed) | FAIL: "expected exactly five devices", six found |
| + `-icount shift=0,sleep=off`; + `-global ICH9-LPC.noreboot=on`; + `-action watchdog=reset` | PASS, because **`check_argv_7c` inspects none of the three**. If the ring 8a argv must be free of them, test 4 (item 11) has to say so itself |

**D4 — Esc at power-on through the monitor.** In mode 2, the loader's
minimal setup (A3) runs first:
- wait for the input buffer to empty, write `0xAE`, let the controller settle, and drain the output buffer, one line per byte drained;
- read the command byte with `0x20`;
- the marker `PROBE: window ms <t>`, then 14 s of polling `0x64`/`0x60`, one line per byte with its TSC ms.

The checker sent `sendkey esc <hold>` on the monitor as soon as the marker
reached the capture (1 ms polls).

| Fact | Measured how |
|---|---|
| **The setup takes 3 ms** (setup line at 65 ms, window at 68 ms). **The command byte after `0xAE` reads `0x67`**, OVMF's value: translation on, port 1 enabled, aux disabled. The status byte on each key byte is `0x1D` (bit 5 clear: the keyboard's) | every run |
| **The make arrives as translated set 1 `0x01` and the break as `0x81`**, at every hold and every `-smp` | runs `esc-w*` |
| **The break lands at t0 + hold**: guest intervals of 99, 998, 2,997 and 9,991 ms for holds of 100, 1,000, 3,000 and 10,000 at `-smp 4`, and 2,997 and 2,996 at `-smp 2` and 8. By the host's stamps the break arrives 0.096, 0.997, 2.999, 9.998, 2.996 and 2.996 s after the make. The guest's ms runs about 0.07 % slow against the host, from the TSC's calibration on one 10 ms PIT wait | the byte lines and their stamps |
| **No typematic repeats**: exactly two bytes (make, break) in the window for every hold, 10 s included. QEMU's PS/2 keyboard does not repeat; a real keyboard's repeats are makes, which the held rule accepts | `n 2` on every `window end` line |
| **The drift, marker in the capture → make in the guest: 0–1 ms of guest time** (the make's ms minus the window's ms, sent the same poll the marker landed in), at `-smp` 2, 4 and 8 | runs `esc-w*` |
| **An Esc sent before ExitBootServices** (on `S7: alive`) **loses its make to OVMF**, which still owns the keyboard then. With a 100 ms hold the break `0x81` was already waiting and the loader's drain took it (`drained st 1d b 81`); the window saw nothing. With a 3,000 ms hold the break arrived inside the window at 2,831 ms with no make before it. Either way the held rule (a make, then no break before the window ends) counts it as **not held**. A key held from power-on is therefore not a hold; the owner's instruction (hold only when `hold Esc for the seed` appears, A3) is the only way | runs `esc-alive100`, `esc-alive3000` |
| **With no key sent, the window sees no byte** in 14 s | run `esc-none` |

**The checker's hold (A3), the single choice:** `sendkey esc 5000`, sent
when the line before the window lands, **W + 2,000 ms**. The make lands
within 1 ms and the break within 10 ms of the hold, so the margin covers
the setup's 3 ms, the capture's poll and the gap between the line and the
window by about two orders of magnitude. A break after the window is only
a break code in the seed's ring, and `kbd_next` ignores those. W stays
PARTS.md's human 3 s, not measured.

**D4 — the rates.** Mode 3, at `-smp 4`, idle after `ready` + 1 s, the
obs page read through the monitor before and after:

| Fact | Measured how |
|---|---|
| **Keys at `rehearse.KEY_GAP` (0.2 s):** the mixed text `The Quick brown fox, 42 jumps! Over? the lazy dog` and four arrows, 53 `sendkey`s. The rule predicts **124 keyboard bytes** (a plain key 2, a shifted one 4 — shift make, make, break, shift break — an E0 key 4). **124 were counted**, and `OBS_KEYS` rose by 49 (the 49 printables; shift and the arrows translate to nothing). **11.7 bytes/s**, 5 keys/s. The rule holds as PARTS.md will state it | `rates-smp4` |
| **Faster gaps lose nothing:** the same 53 keys at 50 ms and at 20 ms: 124 bytes and 49 keys each time, the ring's high-water 2 | `rates2-smp4` |
| **The mouse, 1,000 `mouse_move`s alternating ±1:** in a **tight loop (no pause) QEMU coalesces them: 31 packets**. The moves arrive faster than the guest drains the PS/2 queue, and QEMU sums the deltas, which here cancel. At a **1, 2, 3, 5 and 20 ms pace, packets = moves = 1,000** and mouse bytes 3,000, at 851, 457, 315, 193 and 49.5 packets/s. **`OBS_RESYNCS` 0 in every case**, the tight loop included, and the ring's high-water 1–2 at a paced rate (10 after the tight loop) | `rates-smp4`, `rates2-smp4` |

**What this sizes (good's threshold, 1,000 keyboard bytes and 5,000
packets over three boots):** typing at `KEY_GAP` gives 1,000 bytes in
about 86 s of mixed text, about 29 s a boot. 5,000 packets take about
101 s at checkmetal's 20 ms mouse pace, 26 s at 5 ms and 6 s at 1 ms.
**`("wiggle", n)` must pace its moves** (any pace from 1 ms up gave
packets = moves); a tight loop never makes one packet a move. Item 12
chooses the paces from these.

**D4 — the identity.** **CPUID leaf 1 EAX under `-cpu IvyBridge` is
`0x000306A9`** (family 6, model 0x3A, stepping 9), the same at `-smp` 2
and 4. EBX carries the logical count (`0x00020800` at 2, `0x00040800` at
4), which is why the identity takes EAX alone. The LPC bridge is `8086:2918`
rev `02` (D1). **So the twin's molt request body is `molt i8042 cpu
000306a9 pci 8086:2918:02`** by decision 3's format.

**The hook's verdicts** (`hookcases.py`, 87 cases through
`protect-tests.py` as the harness feeds it):
- **Every new ring 8a path is writable today** with Write and Edit, relative and absolute: PARTS.md, SEED.md, `parts.py`, `test-8a.sh`, `checkmolt.py`, `loader.asm`, `seed-record.md`, HP-8a.md, `broker/molt.py`, and the ten fixture files.
- **Every command shape the ring will run is allowed:**
  - `parts.py` in all four modes; the gate; the checker's four modes;
  - `nasm -f bin` of a fixture to its `.bin` and to a check copy under `stage8/out/molt/`;
  - `cp` of a disk and of the stick under `stage8/out/`; `truncate`; `mkdir -p` and `rm -rf` of the scratch;
  - the builders; `molt.py --mock` with `--part` and `--hold-s`; the relay;
  - the twin's QEMU line with drives under `stage8/out/molt/`;
  - the payload table; a `git commit -F`; the 7d gate; `trials.py` on a stage8 disk.
- **The controls stay denied:** a Write to `stage7/checkmetal.py` or `checktrials.py`, a `cp` over a frozen checker, and a drive outside `out/`.

**One finding, for the owner (not ring 8a's, and not fixed here):**
**the freeze does not catch a command that names only a directory
holding frozen files.** All of these are ALLOWED:
- `rm -rf stage7` and `rm -r stage7/`;
- `mv stage7 old7`;
- `git rm -r stage7`;
- `rm -rf stage6`, `rm -rf broker`, `rm -rf stage8/fixtures`.

The hook judges named frozen paths, as it has since Stage 0, so every frozen stage has had
this gap. It is carried to item 13, which freezes `stage8/fixtures/`, as
a question: whether the owner wants a directory rule in the hook first.
The hook is the owner's guarantee, so CC does not edit it unasked.

No ring 8a test exists yet; no guest code changed.

**The owner's decision on item 3's finding, 25 September 2026: yes, a
directory rule in the freeze, added at item 13.** At item 13, alongside
`PROTECTED`, the hook will deny `rm`, `rmdir`, `mv`, `git rm` and `git mv`
when any argument is:
- the repo root;
- a directory that holds a frozen file;
- a glob that covers one.

Examples to deny: `rm -rf stage7`, `mv stage7 old7`, `git rm -r stage8/fixtures`.
**These stay allowed:** moving or removing an ordinary file beside frozen
files, and wiping `stage8/out`. Every shape, denials and allowances alike,
goes into the payload table as data, with 0 wrong. The hook's comment
says plainly that a rule which reads the command cannot catch every
route: a script that removes a folder, for example, still gets past it.
The item 13 record will list the shapes as the table holds them.

**Item 4** — `stage8/PARTS.md`, 25 September 2026: 1,366 lines, written
with the Write tool. It covers decisions 2–9 and 11 in the manner of TRIALS.md, with D1's and
D4's single choices in it:
- `TCO_TMR` 25 by the datasheet's rule, and the twin's agreement;
- `S8: watchdog tco 30 s`, and `S8: recovery i8042 watchdog` as the one twin path;
- W = 3 s, set 1 and set 2, and the checker's hold of 5,000 ms named as the checker's own;
- the key-byte rule;
- the identity `cpu 000306a9 pci 8086:2918:02`;
- `HOLD_S` = 60 s and `RESET_S`'s three terms;
- the corpus reserved for ring 8b.

**Its "Parsing it cold" block** is the Python `parts.py` will execute. A
scratch self-check (not committed) exec'd the block from the document
itself and reproduced every worked example: 53 checks, 0 wrong. Those are:
- the request frame's `xxd`, the key, and the made-up part's header, build and frame;
- the liar's rule on it;
- the tables along disk G's history, and the undo cases;
- every recovery row, the Esc byte sequences, the 124 keyboard bytes, `TCO_TMR`, the known answer and the round constants.

The fixtures' frames and the liar's bytes are marked "completed at item 7",
as the plan says. A grep for a twin expectation offering two lines (A5)
finds none.

**Details the plan left open, fixed here** (for Cowork's review; none
changes a decision):
- **The install note carries the threshold:** `molt <slot> shadow <sha16> <boots> <keys> <packets>`. HOME.md's entry has no field for it, and its choice slots must stay valid for HOME.md's frozen parser.
- **Every molt note is mirrored to serial**, raw, as `molt:` and the note from its fifth byte (the ring 7d `trial:` pattern), so `parts.py --serial` can rebuild the table from the HP's chart.
- **The part's shape:**
  - a 96-byte header, then the body; 65,536 bytes at most;
  - a part region per slot in BSS, never the component region;
  - the service table passed to `byte` and `health` as well, since shadow never calls `init`;
  - in shadow a table whose hardware services do nothing.
- **The state:**
  - every state change takes effect at the next boot;
  - the shadow counts and probation both count from the build's last entry into shadow (an install, or an undo from `demoted`); an undo from `live` keeps them, which is what gives G7 probation 2;
  - an undo from shadow returns to the state before the build's install only if the home entry's previous build is that build; otherwise it goes to `generic`;
  - the unhealthy run restarts at a `healthy`, `demoted` or `recovery` note.
- **The comparison:** events are written `k<hex>`, `m<dx>,<dy>,<b>` and `-`. At each count point the raw ring is drained into the part first, and a side left ahead then counts its extra events as disagreements.
- **The boot:** the `S8:` block sits after `S7: glass core <n>` and before the `i8042:` or `part:` pair, in eight numbered steps.
- **The `part-` supersession** also covers `undo install part-…` and an app frame named `part-…`.
- **Smaller fixes:**
  - the blame line is `+0x` and 8 hex digits, after `exc_common`'s own line;
  - the liar's torn write flips bit 0 of the part's byte 96;
  - the pet's rate limit is 1,000 ms.

No ring 8a test exists yet; no guest code changed.

**Cowork's review of PARTS.md at `30bb0bb`, 26 September 2026:** the five
details above are accepted as written. **One amendment, applied while
PARTS.md is still open, as its own commit before item 5.** ABI 3's
services now refuse, each refusal answering 0, a refused `pci_write32`
writing nothing:
- **`map_mmio` refuses a range whose 2 MB pages overlap RAM** as the kept UEFI memory map records it: every descriptor but types 11 and 12. The test is on the 2 MB pages because those are what the service maps. So a part can never get the seed's image back as a writable page, nor undo the image page's read-only 4 KB split.
- **`pci_write32` refuses every register of the LPC bridge at 00:1f.0.**
- **`map_mmio` refuses the 2 MB pages that overlap the RCBA window** (RCBA to RCBA + 16 KB, where GCS and `NO_REBOOT` sit).
- **The PMBASE range is I/O space**, which no ABI 3 service reaches. That is how the review's "PMBASE range" clause is met: with no service for it, rather than a check in one.

`pci_write32` now answers 1 when it writes. **One sentence states the
honest limit:** a part runs in ring 0, so the refusals guard the floor
against a part's mistakes, not against a part that means harm. The check
on grown code is ring 8b's pipeline. Neither the worked examples nor the
Python block touch these services, so neither changed; the self-check
still reads 0 wrong. **This is for item 15's implementation:** RCBA's 2 MB
page, `0xFEC00000`–`0xFEDFFFFF` in the twin, also holds the I/O APIC and
the HPET, so no part can map those either. No `i8042` part needs any
MMIO.

**Item 5** — the five fixtures, 26 September 2026:
`stage8/fixtures/i8042-{good,wrong,hang,fault,liar}.{asm,bin}`, and
`.gitignore` gains the five `!stage8/fixtures/i8042-*.bin` lines.
- **`good`** is transcribed from the seed's i8042 code:
  - `init` is `mouse_init`'s work, including ring 7c item 15's second ports-off-and-drain, with its two lines through `serial_line` and its waits through `pit_wait`;
  - `byte` is `kbd_next`'s decode and `mouse_byte`'s packet machine;
  - `health` answers init's failure code, 0 when init succeeded;
  - its state (24 bytes, zero as stored) and its own copies of `scan1_map` and `scan1_shift_map` live inside the body.
- **Each of the other four** is generated from `good`'s source, with its one change marked `FIXTURE CHANGE` and a banner stating its fate:
  - `wrong`: make code `0x10` decoded as `0x11`'s key in both maps;
  - `hang`: once `init` has run, the 100th `byte` call spins;
  - `fault`: once `init` has run, the first mouse byte executes `ud2`;
  - `liar`: only the name field.
- **NASM cannot compute SHA-256**, so each `.asm` carries its body's hash as a literal line. It was written from a first assembly and checked on the second.

| Fixture | Bytes | Body | `init` / `byte` / `health` | Build (first 16) |
|---|---|---|---|---|
| `good` | 1,152 | 1,056 | +96 / +382 / +611 | `4fe6beefc4bc57d0` |
| `wrong` | 1,152 | 1,056 | +96 / +382 / +611 | `b41ddccde138ea23` |
| `hang` | 1,176 | 1,080 | +96 / +382 / +637 | `f0668b687c68cab0` |
| `fault` | 1,160 | 1,064 | +96 / +382 / +622 | `99e9f923a568309e`, `ud2` at `+0x1fb` |
| `liar` | 1,152 | 1,056 | +96 / +382 / +611 | `f15e77a8966e95e3` |

**Proven on the host, no boot**, by the plan's two checks and one more:
- **Each assembles byte for byte twice.**
- **Each header passes PARTS.md's own `check_part`**, exec'd from the document. `fault` has exactly one `0F 0B` pair, and no other fixture has one.
- **The extra check, beyond the plan's two:** a scratch C harness loaded each `.bin` into executable memory and called its `byte` entry (which uses no privileged instruction) through a register-saving trampoline, with C upcalls recording each event. A Python model of `kbd_next` and `mouse_byte`, with the maps read from `stage8.asm`, gave the reference. **`good`, `hang`, `fault` and `liar` matched the model event for event, stamps included**, on three streams:
  - item 3's 3,092-byte bench stream (1,216 events);
  - 20,000 random bytes (4,431 events);
  - every make and break code plain, shifted and after `E0` (104 events).

  **`wrong` differed only where `q` became `w` or `Q` became `W`** (8, 49 and 2 events). With `init`'s flag set by hand, **`hang` spun on exactly its 100th byte, and `fault` trapped at `+0x1fb` on the stream's first mouse byte**, while `good` ran on. The first run of the check was red everywhere, and the fault was the model's: its map parser cut `';'` at the quoted semicolon. Fixed in the model; the fixtures were not touched.

**For item 15:** a live part cannot write the obs page. So the seed must:
- centre the pointer before `init`, as `mouse_init` does;
- keep `OBS_MOUSE_ID` and `OBS_I8042_CMD` truthful itself. `! trial` refuses with `no mouse` when `mouse_id` is 0, so a live part must not leave it at 0.

No ring 8a test exists yet; no guest code changed.

**Item 6** — `stage8/SEED.md` and `stage8/seed-record.md`, 26 September
2026. SEED.md, written with the Write tool, holds:
- **the seed:** `stage8/out/BOOTX64.EFI` as `stage8/mkimage.sh` builds it from one commit with a named NASM. The stick and `esp.img` carry it but are not it (FAT timestamps, `NvVars`);
- **what may change:** the loader and SHA-256 frozen for good from item 16b, the rest ring by ring, each seed version one record line. A build no line names is not a seed;
- **the rebuild:** an empty `stage8/out/seed/<n>/`, `git archive <commit> | tar -x` into it, that tree's own `mkimage.sh`, the NASM version checked first (another version is refused, never compared), and SHA-256 and length of the EFI;
- **the record:** one bare ``` fence, seed lines only inside it, `seed <n> <sha256> <bytes> <commit> <yyyy-mm-dd> nasm <version>`. The date is the named commit's committer date (`%cs`), a fact of the commit. The commit must be an ancestor of the commit that adds the line. Rules: append-only (checked against the file's git history), numbered from 0 by one, no repeat of the previous hash, dates never backwards, the witness uses the last line, and a line only for a build its gate judged;
- **three SHA-256 known answers** (FIPS 180-2's `abc` and two-block message, and the empty message). The `abc` answer must agree with PARTS.md's;
- **the worked example:** seed 0's rebuild, its line and parse, five refused records with their messages, and one refused history;
- **"Parsing it cold, in Python":** the block `parts.py` will exec, with `seed_kat`, `build_id`, `nasm_version`, `parse_seed_line`, `record_lines`, `parse_seed_record`, `current_seed`, `seed_named`, `append_only`, `seed_line` and `rebuild_script`. The git plumbing is `parts.py`'s (item 7).

**Seed 0, from the build, never typed.** `rebuild_script("bd613b3",
"stage8/out/seed/0")`, run at the repo root, gave 45,056 bytes,
`bbf80635a83beeca2254ef35aa492306d30224950b4f405b434b900475b28cd5`: ring
7d's binary's, and HEAD's build's. A scratch script exec'd SEED.md's own
block, rebuilt, and wrote the record with `seed_line`:
`seed 0 bbf80635…b28cd5 45056 bd613b3 2026-09-25 nasm 3.02`.

**Proven on the host, no boot:** a second scratch script exec'd the block
from SEED.md cold and checked 21 claims, 0 wrong:
- the record parses; `current_seed` is 0; `seed_named` names both the rebuild and HEAD's build `0`, and the build with one byte appended `None`;
- the line, its dict, the rebuild line and the `sha256sum` line appear in SEED.md as the functions give them;
- each refusal message is in SEED.md's table, and the history message too;
- `abc` agrees with PARTS.md's `KAT_ABC`; `bd613b3` resolves and is an ancestor of HEAD; `nasm -v` gives `3.02`.

The first run found one wrong: the history's message wrapped across two
lines of prose. The sentence was reworded; the block was not touched.

No ring 8a test exists yet; no guest code changed.

**Item 7** — `stage8/parts.py`, and PARTS.md's fixtures example filled,
26 September 2026. Standard library only; it imports `metal`, `checkdisk`
and HOME.md's parser (`checkplans`) only when a disk is read.
- **At import** it execs PARTS.md's and SEED.md's Python blocks into one namespace (no name defined by both), then checks each block against its document's prose. It fails loudly if any of these disagree:
  - the header, service and frame tables' offsets;
  - the six install `<why>`s in order;
  - the deadline, the tick, `TCO_TMR` 25, the pet's 1,000 ms, `HOLD_S`, the health window, W, the Esc codes, the floor, probation and the sixteen disagree notes;
  - the fixture table's names and thresholds, and the hang point;
  - SEED.md's field table and its known answers, whose `abc` must be PARTS.md's.
- **What it adds to the blocks:**
  - `parse_parts_md` and `parse_seed_md`;
  - `fixture`, `fixture_frame` (the frame the mock must serve), `install_note`;
  - `sha_k_in` (where the 64 round constants lie in a build: once, at `0x964c` in seed 0);
  - `render_fixture`, `door_of` (PARTS.md's step 5), `xxd` (checked against the real `xxd` on 52 lengths);
  - the git plumbing: `resolve_commit`, `commit_date`, `is_ancestor`, `record_versions`, and `rebuild`, which runs `rebuild_script` and nothing else.
- **The modes:**
  - `--example`, with `--parts DOC` and `--seeddoc DOC` to read another copy;
  - `--disk IMG`: the table, the next boot number, the unhealthy run, DISK.md's partitions, the home's apps and parts, the entry and the door;
  - `--serial LOG`: the `molt:` lines as notes, the same table, and the chart's `S8:` lines;
  - `--seed`: the record against git, every line rebuilt, and the current build named.

**PARTS.md's "The fixtures' frames and the liar"** replaces its "completed
at item 7" paragraph (145 lines). There is one subsection per fixture:
its length and entries, its build and `<sha16>`, its install note, its
96-byte header, and its frame's first 40 bytes. `fault` adds `ud2` at
byte 507 and its blame line, `… +0x000001fb`. `liar` adds that its body is
`good`'s byte for byte, and the torn write `48` → `49` with both hashes
(`f15e77a8…` kept by the entry, `2ae3a89f…` stored). **The text is
`render_fixture`'s output**, and `--example` demands it: the fences
exactly, the prose with its whitespace collapsed. Cross-checked by hand
against item 5's table (sizes, entries, builds, `ud2`), plus one frame
decoded by hand: `N` 0x4a0 = 1,184, `L` 0x480 = 1,152, and the thresholds
3, 0x3e8 and 0x1388.

**Proven on the host, no boot** (scratch scripts, not committed; scratch
under `stage8/out/probe8a/parts/`):
- **`--example`** exits 0. **27 one-change copies of the documents** are each refused, each by the check aimed at it: a byte in good's frame, the made-up frame and the request; a table row, a recovery row, an Esc row, the key total, `HOLD_S` in the block, a fixture threshold, the blame offset, the liar's hash and byte, the key's ABI, the frame table's last offset, an install why, W, a round constant, a name field, a boot number and a refusal; in SEED.md a refusal message, the seed line's date, the dict, the build size, a known answer and the commit's date.
- **`--disk`** on `stage7/out/disk.after-first-boot.img` and on `disk.img` (15 notes) prints `i8042 generic` and loads nothing, exit 0.
- **`--serial` and `--disk` agree.** A copy of the formatted disk was given disk G's history with good's real `<sha16>` among typed notes, and good's part as `part-i8042` in the home store. The same notes went to a log as `molt:` lines among firmware noise. Both modes print `i8042 live 4fe6beefc4bc57d0`, `boots 3/3 keys 1020/1000 mouse 5100/5000` and `disagreements 0 probation 2/3`, which is `table_of`'s answer. The door says `S8: part i8042 live 4fe6beefc4bc57d0`.
- **The liar on a disk:** the door says `shadow f15e77a8966e95e3`, then `bad hash` after the host flips the part's byte 96 on the image. A note `molt i8042 shadow nothex 1 1 1` is named `DISAGREES`, exit 1.
- **`--seed`** rebuilt `bd613b3` into `stage8/out/seed/0` under NASM 3.02: `bbf80635…b28cd5`, 45,056 bytes, agrees. It says `stage8/out/BOOTX64.EFI … is seed 0`, exit 0. Its logic, fed altered records, refused each case by its own rule:
  - a changed line against the history (`a seed line was changed or removed`);
  - with no history: a hash and a size (the rebuild disagrees), a commit that is not one, a wrong date, another NASM (`no rebuild`);
  - a line naming the commit that adds it (`not an ancestor`);
  - a second line whose build no rebuild gives.

The first `--example` run was red on eight checks. All were the tool's
faults: backticks paired across code fences, and the bullet indices one
off. Both were fixed in the tool; the documents' examples were not
touched.

No ring 8a test exists yet; no guest code changed.

**Item 8** — `broker/molt.py`, 27 September 2026. Unfrozen (decision 14,
deviation 5). Standard library only; it imports `stage8/parts.py`, so the
frame, the request and the key are PARTS.md's own Python and never
spelled in the broker.
- **`Molt(wire.Wire)`**: `grow()` claims a body that is `molt` or begins `molt `; everything else goes to `wire.Wire.grow`, so `! test app`, `! install echo` and the relay behave as at ring 7c.
- **The request** must be `parts.request_body(slot, ident)` byte for byte, with the identity `cpu <8 hex> pci <4>:<4>:<2>`, lowercase. Anything else is refused: `molt request malformed: …`.
- **`--mock --part good|wrong|hang|fault|liar`** (default `good`): `molt i8042 <any identity>` gets `part_frame(fixture, FIXTURES[fate], 0)`. Before listening, the fixture's frame is parsed back through `parts.parse_frame` and must give the same part, threshold, source 0 and name field. The mock serves any identity, since the HP's differs from the twin's.
- **A slot other than `i8042`** gets `no part for slot <s>: ring 8a's slot table holds i8042 alone`. **Without `--mock`**, a molt body gets `no part for slot <s>: the molt pipeline is ring 8b's`: the real grow path is ring 8b's.
- **The record** (GERMLINE.md's grow line) adds `slot`, `identity`, `fixture`, `threshold`, `build` (the part's SHA-256) and `frame` (the answer's hex). `key` is `parts.molt_key`, the plain string `molt <slot>|abi3|<identity>`; `source` is `fixture` or `refused`. A malformed body is recorded with no slot and no key.
- **`--hold-s S`** (A1) holds the answer to `? hold` for S seconds, then answers `hold: the mock held this answer for <S> s`. Every other question is `wire.py`'s answer, unheld.
- **Defaults:** `--image stage8/out/esp.img`, `--workdir stage8/out/molt/rehearsal/twin`. The checker passes its own paths, as `checkmetal` does for `wire.py`.

**Proven on the host, no boot** (a scratch client, not committed; scratch
under `stage8/out/probe8a/molt/`). The gate's germline
(`stage7/out/metal/germline`, which holds `test app` and `install echo`)
was copied twice, so both brokers served from a cache and no twin booted:
- **Each of the five fixtures** on 127.0.0.1:9999: the answer to the twin's request equals `part_frame(fixture, threshold)` and `parts.fixture_frame(fate)` (1,188, 1,188, 1,212, 1,196 and 1,188 bytes). Another machine's identity gets the same frame. The record's request, text, slot, identity, key, frame, `answer_sha256`, fixture, threshold and build are each right.
- **Refused**, each as a refusal frame by `parts.parse_frame`: `molt x86 …`, `molt disk …`, `molt i8042`, bare `molt`, an uppercase short CPU, a double space, a trailing word. `molt x86` is recorded with its identity and its key.
- **`test app` and `install echo`** get molt.py's answer equal to `wire.py --mock`'s on 9995, byte for byte (708 and 221 bytes, kind 2). The record shows wire.Wire's path (`source` germline). `? ping`, `? hello` and an uncanned question match too.
- **`--hold-s 3`**: `? hold` is answered after 3.0 s with the text above; `? ping` is not held.
- **Real mode**, in process: a molt body is refused with no generation call.
- No twin workdir was created.

The first run failed one check: the record's second line was missing,
because the script stopped the broker before the broker wrote the record
after closing the connection. That was the scratch script's race; it now
waits for the record's lines. The broker was not changed.

No ring 8a test exists yet; no guest code changed.

**Item 9** — `stage8/test-8a.sh` and `stage8/checkmolt.py` with
`--document` and `--seven`, 27 September 2026. **Tests 1 and 2 PASS**
(deviation 15: the binary is still ring 7d's, so "no part, no change" is
honestly green before any change).

- **The harness** is ring 7d's shape:
  - its first act is `=== ring 8a gate <date -Is> commit <short> ===` into `stage8/out/gate-8a.log`, then `exec > >(tee -a …) 2>&1`;
  - it exports `GATE_8A=1`, refuses to start while 9999, 9998 or 9997 answers, and runs `mkdir -p` on `stage8/out/`, `molt/` and `seven/`;
  - it builds with `stage8/mkimage.sh` and `python3 stage8/mkstick.py`;
  - it spells the cage, the machine, the display and the two drive shapes once (test 4 (a) will judge them).
- **The log.** `checkmolt.py` run directly writes `=== checkmolt.py <mode> <date> commit <short> ===` and tees its own descriptors 1 and 2 (children included) into the log through `tee -a`. Under `GATE_8A=1` it does neither.
- **Test 1**, the shell's PE32+ checks, then `--document`:
  - `checkmetal.check_stick(stage8/out/stick.img, stage8/out/BOOTX64.EFI)`, the arguments explicit;
  - `parts.py --example` as a subprocess, which reproduces every worked example of both documents, seed 0's line among them;
  - each fixture reassembled into `stage8/out/i8042-<fate>.check.bin`. It must be byte-identical to the committed `.bin`, and its banner must give its own `nasm -f bin …` line. Its header must pass `check_part` for `i8042` with its fate as its name, and its frame must parse back to its part, its threshold and source 0;
  - `sha256_kat()` and `seed_kat()`, and **the 64 round constants lying exactly once in the build** (`0x964c` in seed 0's);
  - the seed record parsed, and append-only against its git history.
- **Test 2**, `--seven`:
  - it wipes `stage8/out/seven/` and points the frozen checkers at stage8's build with D3's attempt-2 rebindings (the two bound defaults and `checkdisk.OUT`/`checkglass.OUT` among them);
  - it calls, in-process, `run_serial` blank 8, again 4 and novga 2, `run_stages`, `checktrials.run_row` and `run_sitting`. Each must return 0 (an exception is a failure) and leave at least one fresh serial capture. The ports must be free after each;
  - **nothing outside `stage8/out/` may change**: every file under `stage0..7/out/` and `germline/`, by mtime and size;
  - **no capture under `stage8/out/seven/` may hold an `S8: `, `part: ` or `molt: `**, anywhere it begins a word, with the firmware's escape sequences read as line breaks.
  - The plan named `S8:` and `part:`; `molt:` is added, since PARTS.md mirrors every molt note to serial under it.

| Run | Result |
|---|---|
| **The gate, whole** (the log from line 144, commit `562c4b5` plus these two files) | **test 1 PASS, test 2 PASS**, exit 0, 7.1 min (10:36:38 to 10:43:44) |
| Test 2's entry points | blank 8 4.2 s, again 4 4.2 s, novga 2 4.2 s, stages 68.4 s, row 43.5 s, sittings 301.4 s; 425.7 s in all, twelve captures (the stages' and the row's twin rehearsals among them), none with a ring 8a line |
| The first gate run (the log from line 9) | green too. The line detector was then tightened from "at a line's start" to "anywhere it begins a word, escapes as breaks", after a probe showed that `\x1b[0mpart: …` slipped past. Run 2 is the committed code's |

**The checks' teeth, proven on the host by two scratch probes** (not
committed; scratch under `stage8/out/probe8a/item9/`). Each case was refused
by the check aimed at it, 0 wrong:
- `--document`, 8 cases:
  - the baselines are accepted;
  - a byte of `i8042-wrong.bin` altered (does not reproduce);
  - hang's banner line altered;
  - liar replaced by good (the name field);
  - one round constant altered in the build (0 places);
  - the constants appended twice (2 places).
- `--seven`, 6 cases with fake entry points and no boot:
  - an entry that is well gets 0;
  - one returning 1, one raising, one leaving no capture, one whose capture holds `\x1b[0mS8: …`, and one writing a file under `stage7/out/` each get 1. The stray file was removed.

The first `--document` probe was refused for the wrong reason: the scratch
copy's path did not match the banner line. The probe was fixed to demand
each case's own message; the checker was not changed.

No guest code changed. Tests 3 and 4 are not yet written.

**Item 10** — `checkmolt.py --fates` (test 3), the synthetic human, and
Cowork's review of item 9, 27 September 2026. **Tests 1 and 2 PASS; test
3 FAILS by design**, stopping on its ten unset run constants and naming
them.

**Cowork's review of item 9, folded in here.** Both log headers named
HEAD, so a gate run made before its item's commit was logged under the
previous item's hash (both of item 9's runs say `commit 562c4b5`). Now
both headers, the gate's and `checkmolt.py`'s own, append `+uncommitted`
to the short hash when `git diff --quiet HEAD` returns non-zero, for
example `commit 7368b2e+uncommitted`.
- The command is read-only: `git --no-optional-locks -C <repo> diff --quiet HEAD`. The flag stops git's opportunistic index refresh, so nothing writes the index. `.git/index`'s mtime and size were unchanged across both headers.
- Checked in a scratch clone: tracked edits give `+uncommitted`; a clean tree gives the bare hash; an untracked file alone gives the bare hash (only tracked files count); no HEAD gives `none`, as before.
- Nothing else from item 9 changed.

**The run constants** are ten named placeholders, each `None` until item
12 writes it from its run: `READY_S`, `SETTLE_S`, `WORD_S`, `ANSWER_S`,
`HEALTH_SLACK_S`, `HOLD_SLACK_S`, `RESET_S`, `RECOVER_S`,
`WIGGLE_PACE_S` and `BOOT_T_S` (each boot runs under `timeout -k 5
<BOOT_T_S>`, decision 15). While any is `None`, `--fates` names them all
and exits 1. For item 12's run only, `--fates --set NAME=VALUE` gives
one. It is refused for a name that is not a run constant, and for a
constant already written, so once item 12 writes them no override is
possible.

**By rule, never typed.** These come from PARTS.md through `parts.py`:
- `HOLD_S`, `HEALTH_S`, `HANG_BYTE`, the thresholds, the key-byte rule, every note and table, the take and undo answers, the recovery notes and line, the blame line with `ud2_offset`, the door and the liar's stored bytes;
- the twin's identity, read from PARTS.md's worked example;
- the checker's Esc hold, `sendkey esc 5000`, read from PARTS.md's Esc section;
- the part's pair, built from `checkmetal.I8042_LINES` with `part: i8042 ` in place of `i8042: `.

**The disks and boots** (all at `-smp 4`, scratch under
`stage8/out/molt/`):
- **Every disk** starts as a fresh 64 MB file booted blank (the frozen 19-line check). The host then writes 40 notes by NOTEBOOK.md's format (`checknotes.expected_record`): 12 typed notes, ring 7d's aborted sitting as TRIALS.md expands it (27 notes), and `trial verdict A` last.
- **G1:** `! molt` draws `i8042 generic`; `molt x` is refused; `! molt i8042` goes through the relay to `molt.py --mock --part good`; `! part-i8042` is refused; the take is refused below threshold. `errors` is 3, and the mock's record matches the rule.
- **G2–G4:** shadow boots, each typed to a third of good's threshold and wiggled, then a click and the health mark. G4 takes the part.
- **G5:** live. It idles to the health mark, then takes a note and a click through the part, the held `? hold`, `! molt undo` and `! molt take i8042`.
- **G6:** Esc held. The disk is then copied as H.
- **G7:** live again, probation 2.
- **W1–W2:** `wrong` installed; one shadow boot whose first note has a `q`; the take is refused with `disagreements 1`.
- **H1–H3:** `hang` installed on a boot where good is live (boot 5); one shadow boot and the take; then the live boot. There, 50 plain keys make the 100th byte, and OVMF's first byte must come within `RESET_S`. Then `S8: recovery i8042 watchdog` within `RECOVER_S`, in the same process.
- **F1–F3:** the same with `fault`. The first `mouse_move` gives exc_common's line and then the blame line.
- **L1–L2:** `liar` installed. The host checks that the stored build is `i8042-liar.bin`, flips bit 0 of the part's byte 96 on the image, and demands the stored bytes be `liar_stored(bin)` and the door `bad hash`. Then comes the boot.
- **Around every boot:** the three ports are free before; the mock and the relay run only for a boot that asks; the ports are free after; the stick copy's tables are unchanged (the copy is then removed, 64 MB a boot); the notebook's sectors up to the last note before the boot are byte-identical.
- **Each boot is judged** against a model of it (`Book`): every note and every ring 8a line in order. The frozen `check_boot_lines` and the echo are checked; the conversation's tail after each word is checked (checktrials' `check_conv_tail`); the app panel's table must equal `table_of`; the notebook must be exactly the notes before plus the model's; and the mock's frame must equal `parts.fixture_frame(fate)`.

**Choices the plan did not spell, for Cowork's review before the freeze:**
1. **`drive_7d` is not called; its loop is re-spelled as `Human8a`,** with 7d's own helpers imported (`Driver`, `Pointer`, `expected_counts`, `target_col`, `parse_obs_7d`, `KEY_GAP`, `conv_rows`). `drive_7d` waits for one ready line and then runs its steps, so it cannot host a step before the ready line (the Esc hold at `S8: sha256 ok`) or a reset inside one process (the hang's boot and its recovery must be one process, D1). The plan said "imported from `checktrials`"; this is the nearest honest form.
2. **A word's count note carries the keyboard bytes up to its Enter's make, not its break.** `sendkey` holds a key 100 ms, and the word runs long before the break arrives. So the model's count at a word is the bytes before it plus the line's bytes, less one. The health mark's count note carries every byte. Item 12's run will confirm or refute this.
3. **G5 idles first, then asks.** The plan listed the held request before the idle wait. The health mark falls 60 s after `ready`, so a 60 s held request run first would span it and leave no idle stretch. Both waits still exceed the deadline.
4. **Order within a recovery and an Esc:** the note(s) are journaled (their `molt:` mirror) before the `S8:` line. PARTS.md says "journals its notes and prints its line" and "Esc held: `molt recovery owner`, `S8: recovery owner`". One order, per A5.
5. **"A click working" is a click on `! grow` followed by typing ` molt` and Enter.** The row holds only `? ask` and `! grow` with no apps. The click's `!` is judged in the serial echo, and the table must land in the app panel. On a boot that loaded a part this is a molt word, so its count note is in the model.
6. **The part's pair on a live boot** is checked by the frozen `check_boot_lines` with the two `part:` lines standing in for the generic's `i8042:` pair (positions and all), after demanding that no `i8042:` line is present.
7. **OVMF's first byte after a reset** is the first escape byte after the ready line. The guest writes none after `ready`, as every capture shows.
8. **The held answer's text is never typed.** It lands when the conversation's tail is `> ? hold`, an answer and the prompt; afterwards it must equal the mock's recorded answer to `hold`.

**Proven on the host** (scratch not committed; the dry run lives in the
session's scratchpad):
- **Unset constants:** `--fates` names all ten and exits 1. `--set FOO=2` is refused.
- **A smoke run on the current binary** (still ring 7d's) with trial constants given by `--set`, 100.2 s:
  - the four blank boots pass the frozen 19-line check;
  - the host-written notebook reads back and boots as `S7: notebook 40 notes`;
  - the relay and `molt.py` start and stop around each asking boot, and the ports are free after;
  - each install fails as it must on a binary with no molt words. The 7d guest sends `! molt` to the broker as a grow, so G1 recorded two requests and `molt x` became a note.
- **A dry run of the scenario logic** with QEMU faked (a perfect guest by construction) runs every path of G, W, H and F with no exception, and prints each boot's model:
  - W2's disagreement is `molt i8042 disagree 1 3 k71 k77` (the `q` of "a quiet …" is event 3);
  - G4's take is `molt i8042 live 4fe6beefc4bc57d0` at `boots 3/3 keys 1131/1000 mouse 5025/5000`;
  - G5's undo is `molt i8042 undo shadow 4fe6beefc4bc57d0`, and the take again passes on the same three shadow boots;
  - G7 is probation 2/3;
  - H3 and F3 end `i8042 demoted <sha16> watchdog`.

  Disk L's host-side flip needs a stored part, so it is exercised first at item 12. Two faults in the checker surfaced and were fixed: a boot whose step failed went on to judge marks that were never taken (now it is judged by its error and the capture alone); and each stick copy was left behind.

| Run | Result |
|---|---|
| **The gate, whole** (`stage8/out/gate-8a.log` from line 454, headed `commit beef2da+uncommitted`: the owner's trial-two commit had landed during the session, and the header shows these three files uncommitted on top of it) | **test 1 PASS, test 2 PASS, test 3 FAIL by design**, exit 1 |
| Test 2's entry points | blank 8 4.5 s, again 4 4.2 s, novga 2 4.2 s, stages 68.5 s, row 43.6 s, sittings 301.5 s; 426.4 s in all, twelve captures, none with a ring 8a line |
| Test 3, quoted | `the run constants READY_S, SETTLE_S, WORD_S, ANSWER_S, HEALTH_SLACK_S, HOLD_SLACK_S, RESET_S, RECOVER_S, WIGGLE_PACE_S, BOOT_T_S are not set - they are written from item 12's run (plan item 10), never guessed` |

No guest code changed. Test 4 is not yet written.

**Item 11** — `checkmolt.py --cage` and test 4, 27 September 2026. **Tests
1 and 2 PASS; test 3 FAILS by design** (its ten unset run constants, as at
item 10); **test 4 FAILS by design on (c) alone.** (a), (b) and (d) pass.

- **(a), in `test-8a.sh`**, 7d's self-checks on the harness's own strings:
  - the netdev: slirp, `restrict=on`, one guestfwd to `10.0.2.4:9999` via `nc -N 127.0.0.1 9997`, no hostfwd;
  - the ports 9999, 9998 and 9997, the e1000e with the HP's MAC, the machine, the display;
  - `sata_drive` and `stick_drive` spelled on `stage8/out/molt/`;
  - `OUT` is `stage8/out`, with the scratch (`molt/`, `seven/`) and the log under it; no QEMU line of the harness names `esp.img`.
- **(b), `checkmolt.py --cage`.** The fates' two commands are now each spelled in one function, `boot_argv` and `molt_argv`, which the fates call and (b) inspects. Nothing else in `--fates` changed.
  - A boot's command begins `timeout -k 5 <T>` exactly once, and the rest is `checkmetal.qemu_argv` itself. That rest goes through the frozen `check_argv_7c`, with `checkmetal.OUT` pointed at `stage8/out` as the fates point it. `-smp` is 4, and the three files are under `stage8/out/molt/`.
  - **D4's gap, closed here:** `-icount`, `-global`, `-action`, `-watchdog`, `-watchdog-action`, `-no-reboot`, `-accel` and `-enable-kvm` are refused, and so is any argument naming `noreboot` or `i6300esb` (D1 chose the ICH9 TCO with no flag).
  - With `BOOT_T_S` unset, the prefix is judged by its shape and the line says so. Once item 12 writes it, `BOOT_T_S` must be a positive whole number of seconds.
  - The mock: `broker/molt.py --mock`, `--port 9999`, `--rehearsal-port 9998`, its record, germline, image and workdir under `stage8/out/`, the repository's plans, and no `--model`.
  - The ports as the frozen modules hold them: `checkmetal`'s three, `twin.DEFAULT_PORT` 9998, `wire.RELAY_PORT` 9997, and `twin.VGA_ARGS` is 7c's display.
- **(c), `checkmolt.py --cage`.** First the payload table as a subprocess: exit 0 and 0 wrong, **1678 payloads, 1117 denied, 561 allowed, 0 wrong** today. Then the spot checks, held as data:
  - **the 16 frozen paths** (the 15 of item 13 and `stage8/loader.asm`): `Write` and `Edit` denied on each, relative and absolute, and `Read` allowed;
  - **80 shell spellings denied:** `>`, `sed -i`, `cp` over, `rm -f` and a heredoc's `open(…,'w')` on each path;
  - **5 `nasm … -o` over a fixture's `.bin`, denied;**
  - **the owner's directory rule, in his own examples** (item 3's decision): `rm -rf stage7`, `mv stage7 old7`, `git rm -r stage8/fixtures`, `rm -rf stage8/fixtures`, `rm -rf stage8`;
  - **Write allowed** on the builder, the mock and the records (`stage8.asm`, `mkimage.sh`, `mkstick.py`, `broker/molt.py`, `seed-record.md`, `HP-8a.md`, `plan-8a.md`, `HANDOVER.md`);
  - **26 shapes allowed:**
    - the gate, and the checker's four modes;
    - `parts.py`'s four modes;
    - reads (`cat`, `grep`, `xxd`), and `nasm` of a fixture to a check copy under `stage8/out/`;
    - the log's `tail` and `>>`;
    - the builders and `molt.py --mock`;
    - the scratch wipes, `rm -rf stage8/out` among them, and an ordinary file removed or moved beside frozen ones;
    - `git add` of the paths, `git commit -F`, and the 7d gate.
- **(d), in `test-8a.sh`:** `./stage7/test-7d.sh`, whose output lands in both logs. As in 7d, (b) to (d) run only when (a) holds.

| Run | Result |
|---|---|
| **The gate, whole** (`stage8/out/gate-8a.log` from line 751, headed `commit 41621e4+uncommitted`, 11:50:21 to 12:18:43, 28.4 min) | **test 1 PASS, test 2 PASS, test 3 FAIL by design, test 4 FAIL by design on (c) alone**, exit 1 |
| Test 4 (a) | the harness's strings held |
| Test 4 (b) | the fates' command and the mock's held; `timeout -k 5 <BOOT_T_S, item 12's>` |
| Test 4 (c) | the payload table `1678 payloads: 1117 must be denied, 561 must be allowed, 0 wrong`; **154 refusals, every one an expected "allows"**: 64 Write/Edit on the 16 paths, 80 spellings, 5 `nasm -o`, 5 directory shapes. Nothing allowed was denied |
| Test 4 (d) | `./stage7/test-7d.sh` **green**: 7d's tests 1–4, and inside its test 4 the 7c, 7b and 7a gates, all four tests each, on ring 7d's own binary. This is the earlier gates' one run at this commit (plan conventions) |

**(b) has teeth, shown on the host** by two scratch probes (in the
session's scratchpad, not committed; no boot, no port).
- **Probe 1, 22 cases, 0 wrong.** It bends the fates' own builders:
  - each of D4's three flags, `-no-reboot`, `-enable-kvm` and an `i6300esb` inserted;
  - no timeout, and the timeout twice;
  - `-smp 2`;
  - the relay port 9999;
  - a drive under `stage7/out/`, a drive under `stage8/out/seven/`, and `esp.img` on SATA;
  - the mock without `--mock`, on 9997, with its twin on 9999, with the germline in the repository, or with `--model`;
  - `BOOT_T_S` set to 0 or to 2.5.

  Each is refused; the baseline and `BOOT_T_S` 900 are accepted.
- **Probe 2, 9 cases, 0 wrong.** It bends `checkmetal.qemu_argv` itself, so the equality check agrees and the flag checks must refuse alone. Each of the eight flags and `-smp 2` is refused by its own message.

**One choice for Cowork's review before the freeze:** (c) holds the
owner's directory rule as five spot denials. The rule's code comes at item
13, so from then on (c) holds the hook to the owner's own examples.

No guest code changed.

**Item 12** — the probe, 27 September 2026 (plan item 12, the ring 7d
method). **Test 3's ten run constants are written from a run; the
implementation, drafted privately in full, passes all five fates.**
Nothing of the draft is committed; `git diff --stat` shows
`stage8/checkmolt.py` and `HANDOVER.md` alone.

**Cowork's review of item 11, folded in here, while `checkmolt.py` is still
open.** Test 4 (c) held the owner's directory rule of 25 September 2026
through only five examples, so a hook that caught only a plain directory
name would have passed at item 13. `SPOT_DENY_8A` now covers every category
of the decision recorded under item 3, each as data:
- the repo root: `rm -rf .` and `rm -rf` with the repo's absolute path;
- a glob that covers a frozen file: `rm -rf stage*`, `rm stage8/fixtures/*`, `rm -f stage8/*.md`, `mv stage8/fixtures/* /tmp`;
- `rmdir stage8/fixtures`; `git mv stage7 old7` and `git mv stage8/fixtures old`;
- a directory by a trailing slash and by its absolute path: `rm -r stage7/` and `rm -rf` with the absolute path of `stage8/fixtures`;
- `rm -r broker`, since `broker/` holds frozen files.

`SPOT_ALLOW_8A` gains the allowed side of the same decision: `rm -f
stage8/HP-8a.md`, `git mv stage8/HP-8a.md stage8/HP-8a.old.md`, `mv
broker/molt.py /tmp/molt.py.bak` (an ordinary file beside frozen files,
removed or moved), and `rm -rf stage8/out/*` (stage8/out wiped by a glob).
Today's hook, fed each shape as data: **all 17 directory shapes ALLOWED**
(the five and the twelve new) and **all 30 allowances ALLOWED**, so (c)
stays red on them until item 13 brings the rule, as the five did. At item
13 the same shapes go into the payload table, 0 wrong. The module docstring
says so.

**The draft** lives in `stage8/out/probe8a/draft/`: a `patch.py` that makes
its `stage8.asm` from the repository's by 19 hooks (each asserted to apply
exactly once), and the new code in six includes: `defs.inc`, `bss.inc`,
`data.inc`, `loader.asm` (1,881 lines: the scan, the known answer, the
watchdog and the pet, recovery, Esc, the door, `part_call`, the blame
line), `molt.asm` (1,831 lines: ABI 3's services and upcalls, the raw
ring's stubs, the polled main loop, shadow's comparison, the health mark,
the four words, the part's home install) and `split.asm` (the read-only
floor). `build.sh` assembles it and packs a stick with stage8's own
`mkstick` rebound. **Decisions 2–10 are all in it; it assembled first
time: 57,344 bytes**, SHA-256 `1d5f495b8d4bf567…`. Its stick was copied
over `stage8/out/stick.img` for the runs and is rebuilt from the
repository's source at the end.

**How the draft is built, for Cowork's review before items 14–16** (each a
choice PARTS.md left to the implementation, or a place the draft had to
decide):
1. **The notes are the state.** `molt_scan` re-reads the notebook at boot and at every word, one forward pass equal to `parts.py`'s `history`, `counts_of`, `probation_of`, `arrival` and `unhealthy_run`. There is no second copy of the state to drift.
2. **No part, no change, literally.** Only when a part loads are IRQ1's and IRQ12's gates pointed at the part stubs (`irq1_part`, `irq12_part`), and only then does the boot enter the polled loop (`part_loop`) instead of `main_loop`. The shared code gained: a `molt_breath` call in `net_breathe` and in the AHCI poll (the heartbeat, and a pet only once armed); `molt_finish` in `finish_line` (returns unless a part is live); the `molt`/`part-` checks in `bang_line`; the `molt ` note refusal; `part-` filtered from `home_recount`'s count and the choices row; the `part-` app-frame refusal; the blame hook in `exc_common`; the `.text` split and CR0.WP.
3. **Shadow compares keys and packets as two channels.** The generic's keys leave in the main loop (`kbd_next`) but its packets leave in IRQ context (`mouse_byte`), so one merged sequence would make a correct part disagree whenever a packet completed while a key waited in the ring. Each event carries the raw sequence number of the byte that completed it. At a count point an event one side has beyond the other counts only once both sides have taken its byte (its tag below both frontiers), so input still in flight is never counted. `<k>` is the event's position in the part's arrival-ordered sequence: W2 gives `k71 k77` at 3, PARTS.md's.
4. **The Esc window's minimal setup** (A3: `0xAE`, the settle, the drain) runs just before `S8: sha256 ok` is printed, not just before the window. The checker sends its hold when that line lands, and a drain after it could eat the make. The window itself still opens after steps 2 and 3.
5. **Machine notes are written from their own buffer** (`nb_write`), never through the line buffer, so a `disagree` note journaled mid-line cannot take the user's typing.
6. **A live part's keys** go through a queue to the main loop, which counts `OBS_KEYS` and calls `handle_key`; **its packets** go to `mouse_sink`, the second half of `mouse_byte` in main-loop context. With a part live, `finish_line` first feeds the raw ring to the part (its decoder keeps its state), then drops the keys it gave, as ring 7d drops the generic's.
7. **For item 15 (item 5's note):** with a part live the seed centres the pointer itself before `init`, and sets `OBS_MOUSE_ID` to 1 at the part's first packet (the seed cannot ask the mouse while the part owns the controller). `OBS_I8042_CMD` stays 0 with a part live.
8. **Pet condition 5, the rings:** an overflow of the keyboard ring, the mouse ring, the raw ring or the live key queue since the last pet blocks the pet. Only a pet clears the flag, so an overflow stops the pets for the boot and the watchdog resets. That is the literal reading of "no ring has overflowed". The raw ring's 256 entries fill after about 128 keys typed during one long wait. Open for the review.
9. **The shadow table's `pci_read32` is real**, so a part can find the seed's `.text` through the table's addresses. The stray-write probe below does exactly that.
10. **Known limits of the comparison**, by PARTS.md's letter and never met by the gate: keys the generic discards after a request (`finish_line`) are still decoded by the part, so they count as disagreements; and the generic's `kbd_e0` reset at that discard is invisible to the part.

**Two faults in the checker, found by the run and fixed before the freeze**
(both in `checkmolt.py`, neither in the guest):
- **`shadow_boot`'s expected echo** was `echo_of(notes)`: the note texts without the Enter each was typed with. Every other boot uses `echo_of([t + "\n"])`. The capture's `\r\n` after each note was right. Now `echo_of([t + "\n" for t in notes])`.
- **`judge` collected the ring 8a lines after swapping the part's `part:` pair for the generic's `i8042:` pair** (the swap lets the frozen 7c line check run on a live boot). So a live boot's `part:` lines, which `Book.loaded` expects, were never found. Now they are collected from the segment before the swap.

Both surfaced on the first run of disk G, at G2 and at G5. The draft was
not changed for either.

**The runs**, every one against the draft's stick:
- **Disk by disk first** (a private runner, `steps.py`, that calls the checker's own `Fates` methods with trial constants): G and H, then W, F and L. After the two checker fixes, all five were green.
- **The run the constants are read from:** `python3 stage8/checkmolt.py --fates --set READY_S=90 --set SETTLE_S=1.0 --set WORD_S=3.0 --set ANSWER_S=40 --set HEALTH_SLACK_S=30 --set HOLD_SLACK_S=30 --set RESET_S=45 --set RECOVER_S=90 --set WIGGLE_PACE_S=0.005 --set BOOT_T_S=900`, in `stage8/out/gate-8a.log` under its own header: **`the fates: G ok, W ok, H ok, F ok, L ok in 875.1 s`**, 21 boots.
- **A timing probe for the waits the fates' captures carry no stamp for:** the fetch's install note and every word's note (`! molt`, the take, the undo) came **within one key gap (0.2 s, the probe's resolution) of their Enter**.
- **The confirmation, with the constants written and no `--set`:** `python3 stage8/checkmolt.py --fates`, the log again: **`the fates: G ok, W ok, H ok, F ok, L ok in 852.5 s`**.

| Fact | Measured how |
|---|---|
| **QEMU's start to `S7: keyboard ready`:** 1.4–1.5 s with no part to load; 4.4–4.5 s with one (the 3 s Esc window); **0.8 s from a reset's first OVMF byte** (the recovery boot loads nothing, so no window) | the run's stamps, every boot |
| **The health mark 60.0–60.2 s after the ready line**, on all eight boots that awaited it (G2–G5, G7, W2, H2, F2) | the same |
| **The held request (A1):** `? hold` answered **60.9 s after its Enter** (HOLD_S 60), `S7: alive` once, no OVMF byte in between; G5's idle wait to the health mark with a part live, no reset | G5 |
| **The reset (RESET_S's terms):** **30.3 s** from the hang's last key to OVMF's first byte (H3), **31.0 s** from the fault's packet (F3). PARTS.md's three terms sum to 32.14 s | H3, F3 |
| **The recovery line 0.8 s after OVMF's first byte**, both times: **the one path D1 chose, walked** (`S8: recovery i8042 watchdog`, `molt i8042 demoted <sha16> watchdog`, in the same process and capture as the hang) | H3, F3 |
| **The wiggle at 5 ms a move:** every shadow boot's packets equal to the model's (1,677 at G2–G4, 109 at W2, H2, F2), the counts journaled equal to the checker's own | G2–G4, W2, H2, F2 |
| **The longest boot:** G5, 151.6 s (the idle mark, the held request, two words); **the whole fates run 875.1 s** (14.6 min) | the run |

**The constants, written into `checkmolt.py` with the run's date** (a bound
each, with its margin over the measure):

| Constant | Value | From |
|---|---|---|
| `READY_S` | 30.0 | worst 4.5 s |
| `SETTLE_S` | 1.0 | ring 7d's `checktrials.SETTLE_S`; no key lost in the run |
| `WORD_S` | 2.0 | within 0.2 s |
| `ANSWER_S` | 10.0 | within 0.2 s, through the relay and the mock |
| `HEALTH_SLACK_S` | 10.0 | 60.0–60.2 s after the ready line |
| `HOLD_SLACK_S` | 10.0 | 60.9 s, 0.9 s beyond `HOLD_S` |
| `RESET_S` | 35.0 | 30.3 s and 31.0 s; PARTS.md's terms 32.14 s |
| `RECOVER_S` | 10.0 | 0.8 s |
| `WIGGLE_PACE_S` | 0.005 | packets equal to moves (D4: from 1 ms) |
| `BOOT_T_S` | 600 | the longest boot 151.6 s |

`--set` now refuses every name, since all ten are written.

**The rules the gate cannot reach, probed and quoted** (`probes.py`, each
on a build of its own under `stage8/out/probe8a/draft/p-*/`, booted through
the checker's own `Fates.boot`: the ports, the mock and the relay only when
asked, the stick copy's tables, the notes unchanged; notes appended from the
host by NOTEBOOK.md's record where a history is needed). Every boot's step
list completed with no problem from the checker's own checks.

- **`S8: watchdog tco locked`.** D1 showed that `noreboot=on` does not lock in the twin: GCS reads back 0 and the machine simply never resets. So the path is shown on a copy whose read-back ORs in bit 5, as silicon may (`-DPROBE_LOCK`). Good's shadow boot then printed:
  ```
  S8: sha256 ok
  S8: part i8042 shadow 4fe6beefc4bc57d0
  molt: boot 1 i8042 shadow
  S8: watchdog tco locked
  S7: keyboard ready
  molt: healthy 1
  molt: i8042 count 1 54 0 0
  S8: healthy 1
  ```
  The boot went on unguarded to its health mark (decision 5's fallback).
- **The known answer failing** (`-DPROBE_KAT`: one byte of the `abc` digest altered), on a notebook with good's install note: `ERR: sha256 known answer`, then `S7: keyboard ready`. There is no `S8:` line at all, no window, no part, no note, and the generic's pair.
- **`another part is on probation`** (`-DSLOT_N=2`: `disk` stubbed as a second slot; notes `molt disk shadow aaaaaaaaaaaaaaaa 1 1 1`, `molt disk live aaaaaaaaaaaaaaaa`, `molt i8042 shadow bbbbbbbbbbbbbbbb 1 1 1`). The boot printed `S8: part i8042 bad hash` and `S8: part disk bad hash` (neither has a home entry). `! molt` drew both slots' rows, `disk live aaaaaaaaaaaaaaaa` at `probation 0/3`. **`! molt take i8042` → `another part is on probation`; `! molt i8042` → `another part is on probation`, with `requests` 0: nothing was sent.** `errors` was 2.
- **`molt recovery all`.** Hang was fetched through the mock, then the host appended its history to past probation (`live`, then boots 2–4 each `healthy`: `parts.recovery_of(notes, True)` gives `('recovery', 'watchdog', [('i8042', 'f0668b687c68cab0')], True)`). Live at boot 5, fifty keys: the reset 30.2 s after the last key, then:
  ```
  S8: sha256 ok
  molt: i8042 demoted f0668b687c68cab0 watchdog
  molt: recovery all
  S8: recovery all
  ```
  0.8 s after OVMF's first byte.
- **A part's stray write into `.text`.** Good's `byte` entry was rewritten on the host to `mov rax, [rcx + 8]` (the table's `pci_read32`, an address in the seed's `.text`), `mov byte [rax], 0xCC`, `ret`. Its header hash was made anew and it was put in place of good's stored build, with the entry's hash and a live history for it (build `94803b17eb0cb352…`). The first key after its `init`:
  ```
  ERR: exception 14 at 0x00000000005dd182
  ERR: exception 14 in part i8042 +0x00000182
  ```
  `+0x182` is the write's offset, and `0x5dd000` is the part region. The reset came 31.0 s after the key, then `molt i8042 demoted 94803b17eb0cb352 watchdog` and `S8: recovery i8042 watchdog`. **So the read-only floor holds from a part: the write faults instead of changing the seed.**
- **The unhealthy path (A4, D1 point 9; deviation 13's mirror), in the twin.** A copy clears `SECOND_TO_STS` by hand before the loader reads it (`-DPROBE_NO_EVIDENCE`). Hang live at boot 2; the reset 30.2 s after the last key. Boot 3 found no evidence and an unhealthy run of 1, so it **loaded the part live again** (`molt: boot 3 i8042 live`, `S8: watchdog tco 30 s`, the part's pair). Fifty keys, and the reset 30.2 s later. At boot 4 the run was 2: `molt i8042 demoted f0668b687c68cab0 unhealthy`, `S8: recovery i8042 unhealthy`, 0.8 s after OVMF's first byte. All of it was one QEMU process.

**Test 2 on the draft, for items 14 and 15** (not a plan requirement):
`python3 stage8/checkmolt.py --seven` with the draft's stick is **green in
425.9 s**. The 7c serial boots, the stages, the row and the three
sittings all return 0; nothing outside `stage8/out/` changed; and not one
`S8:`, `part:` or `molt:` line appears in the twelve captures. So every
shared hook and the read-only floor (the `.text` split, CR0.WP on every
core) leave a machine with no molt note ring 7d's.

**Cleanup.** `stage8/out/stick.img` and `BOOTX64.EFI` are rebuilt from the
repository's source (`./stage8/mkimage.sh`, `python3 stage8/mkstick.py`):
45,056 bytes, `bbf80635…b28cd5`, seed 0's. **The draft stays in
`stage8/out/probe8a/draft/`, which is the source items 14–16 bring in by
their three commits**: it is gitignored scratch, so nothing may wipe
`stage8/out/probe8a/` before item 16. `python3
stage8/out/probe8a/draft/patch.py` remakes its `stage8.asm` from the
repository's, and `stage8/out/probe8a/draft/build.sh --install` builds it
and puts its stick in place.

| Run | Result |
|---|---|
| **The gate, whole, on the repository's binary** (`stage8/out/gate-8a.log` from line 1672, headed `commit a6f1a6b+uncommitted`, 13:58:51 to 14:28:35, 29.7 min) | **test 1 PASS, test 2 PASS, test 3 FAIL by design, test 4 FAIL by design on (c) alone**, exit 1 |
| Test 3, quoted | `G1: no 'molt: i8042 shadow [0-9a-f]{16} ' within 10 s of the step`, and the same at W1, F1 and L1 (disk H not made): **the first missing ring 8a line, not a placeholder**. `the fates: G FAILED, W FAILED, H FAILED, F FAILED, L FAILED in 81.8 s` |
| Test 4 (a), (b) | held; the command now `timeout -k 5 600` before `checkmetal.qemu_argv` itself |
| Test 4 (c) | the payload table `1678 payloads: 1117 must be denied, 561 must be allowed, 0 wrong`; **166 refusals, every one an expected "allows"**: 64 Write/Edit on the 16 paths, 80 spellings, 5 `nasm -o`, **17 directory shapes**. Nothing allowed was denied |
| Test 4 (d) | ring 7d's gate **green**: 7d's tests 1–4, and inside its test 4 the 7c, 7b and 7a gates, all four tests each |

No guest code changed in the repository.

**Cowork's review of item 12, with the owner's approval, 27 September
2026: one amendment to `stage8/PARTS.md` while it is still open**, as its
own commit before the freeze, as `51fdbf6` was. The owner's decisions on
the ten choices, in four points:
1. **The pet and overflows (choice 8).** An overflow of any ring while the boot processor is inside a bounded wait (the wire's TCP poll, the disk's command wait) is counted in the obs page but never blocks the pet. Only an overflow between two main loop turns blocks it. In shadow, a raw-ring overflow ends that boot's comparison at the overflow: no later byte is fed or counted, no later disagreement is noted, and the boot's count notes carry the counts up to it. Live, an overflow loses input as the generic's drop-on-full does.
2. **The discard after a request (choice 10).** When `finish_line` drops the generic's waiting keys, the seed first feeds the raw ring to the part, then drops both sides' uncompared key events up to that point with no disagreement counted, so the sides start level. The generic's `kbd_e0` reset there stays a stated limit.
3. **Shadow as two channels (choice 3).** PARTS.md's shadow section states keys and packets, each compared in order, with the frontier rule and the meaning of `<k>` as the draft has them.
4. **The Esc setup (choice 4).** PARTS.md's Esc section and its boot steps state that the controller setup runs just before `S8: sha256 ok` is printed.

**What PARTS.md now says** (no worked example and no line of its Python
changed; `parts.py --example` exit 0, every example reproduced):
- **A new subsection, "Overflows"**, under "Never in interrupt context": the four rings (keyboard, mouse, raw, the live key queue), every overflow counted, and the three consequences above. **A wait runs from its first breath to the main loop's next turn**, so the input a wait held back, handed to a live part when the wait ends, is inside it too.
- **Where the obs page counts them:** one word, **`molt_overflows` at `0x360`**, written by the boot processor on a boot that loaded a part. The obs page had no overflow counter, so point 1 needed one. That makes it **the sixth sentence PARTS.md supersedes**: TRIALS.md's "the rest of the page, from `0x360`, is zero". With no part loaded the word is never written, so no ring 7d check can see it; the 7c and 7d readers stop at `0x360`.
- **The pet's condition 5** reads "no ring has overflowed between two main loop turns", and names the live key queue.
- **Shadow:** sequence numbers and tags, the two channels, the frontiers (the part's last byte fed; the generic's last popped key byte; for packets, the last byte the stub read), in-flight events neither counted nor dropped, and `<k>`: the part's event's place in its own upcalls, keys and packets together, or the place its next upcall would take. W2's `3 k71 k77` is the example.
- **The discard.** The point is the next raw sequence number, taken inside ring 7d's own `cli` with the drop. **One reading of point 2, for the owner:** every line's Enter reaches `finish_line` before the next turn compares it. Dropping every uncompared key literally would therefore never compare an Enter, and a part that decoded Enter wrongly would pass shadow. So the discard first compares the key pairs both sides already hold, as a turn does (the Enter is among them). It then drops what is left uncompared below the point, with no disagreement. **The stated limit, one clause wider than the decision:** the generic's shift state has the same limit as `kbd_e0`. A shift make or break among the dropped bytes reaches the part's decoder but never the generic's.
- **The boot's step 1** is now "the controller's minimal setup, then SHA-256's known answer", on every boot with a molt note. Esc's step 1 says where it runs and why (the checker's hold lands with the `sha256 ok` line).

**The checker (test 3, `checkmolt.py`, still open):** during G5's held
request the synthetic human sends **`HOLD_WIGGLES` = 300 paced moves**. The
raw ring's size is read from PARTS.md ("a **raw ring** of 256 entries").
The Enter's break takes one entry, since sendkey holds a key 100 ms and the
first move comes a key gap later. So the part is given (256 − 1) / 3 = **85
packets**, and the other 215 are lost: nothing drains the ring during the
wait. The model's packet count drops by 215, and the pointer model moves for
the first 85 only. **There must be no reset:** the existing check (no OVMF
byte during the hold, `S7: alive` once) now names the moves, and a run that
did not send them fails.

**The draft follows** (`stage8/out/probe8a/draft/`, gitignored scratch).
It has `note_overflow` at all five overflow sites, and `in_wait` (set by
`molt_breath` at a wait's breath, cleared by a new `molt_turn` at
`part_loop`'s turn). It gains `cmp_ended`/`cmp_end` (the stub stops filling
the raw ring, and the generic's events past the end are not queued) and
`molt_discard_point` (a twentieth hook, a `call` inside `finish_line`'s
`cli` that returns at once unless a part is in shadow). `molt_finish`
gains a shadow branch. **The raw ring now holds all 256 entries**: its
head and tail run free, where the old ring was full at 255. The draft
assembled first time: 57,344 bytes, SHA-256 `4349269805b43808…`.

| Run | Result |
|---|---|
| **Disk G alone, the new clause, on the unamended draft** (`1d5f495b…`; `stage8/out/probe8a/draft/run-G-before-amend.txt`) | **red, as it should be:** G1–G4 green; at G5 the 300 moves overflowed the raw ring during the hold, the pet stopped, and the watchdog reset the machine at +77.3 s. The next boot printed `molt: i8042 demoted 4fe6beefc4bc57d0 watchdog` and `S8: recovery i8042 watchdog`: `the held answer never landed in the conversation within 70 s` |
| **`checkmolt.py --fates` on the amended draft** (`stage8/out/gate-8a.log` from line 2478, headed `commit 722216f+uncommitted`) | **`the fates: G ok, W ok, H ok, F ok, L ok in 851.8 s`**. G5: `'? hold' answered 60.4 s after its Enter (HOLD_S 60), 300 moves during it (85 packets kept), with no reset`, and the undo and the take after it are right, with their count notes by the model. W2 still gives `disagreements 1`; H3's reset 30.2 s and F3's 31.0 s after the trigger; the recovery 0.8 s after OVMF's first byte |

**Cleanup:** `stage8/out/stick.img` and `BOOTX64.EFI` are rebuilt from the
repository's source: 45,056 bytes, `bbf80635…`, seed 0's. The draft keeps
its amended sources, and `build.sh --install` builds them. The unamended
build is in `draft/b/` and the amended one in `draft/b2/`.

**The owner's word on the amendment's three readings, 27 September 2026,
before the freeze** (asked after `c4a6111`, since after item 13 a change
would be a freeze opening): **all three kept as committed.**
- The discard compares the key pairs both sides already hold first, so the line's Enter is compared.
- The limit names both `kbd_e0` and the shift state.
- `molt_overflows` sits at `0x360`, as PARTS.md's sixth superseded sentence.

**Item 13** — the ring 8a acceptance machinery frozen, 27 September 2026.
- **`PROTECTED` grows fifteen paths:** `stage8/PARTS.md`, `SEED.md`, `parts.py`, `test-8a.sh`, `checkmolt.py`, and the five fixtures' `.asm` and `.bin`. The hook's comment says why each is a criterion or a criterion's parser, and what stays unfrozen: the builders, `broker/molt.py`, the seed record, `HP-8a.md` and the plan. `stage8/loader.asm` joins at item 16b.
- **The owner's directory rule of 25 September 2026 is in the hook** (`dir_rule`). Each segment of the command (split at `; & | ( )` and newlines, quotes honoured, a redirection's target skipped) whose verb is `rm`, `rmdir`, `mv`, `git rm` or `git mv` (after `VAR=` assignments, `command`/`nohup`/`time`/`nice`/`exec`, or `git`'s own options) gives its non-option words. Each word is judged against every frozen path and every directory holding one:
  - a word of only `.` and `..` is the root;
  - an absolute path is judged from the root, and only inside the repo (the repo itself is the root);
  - a relative path is judged as a suffix, the freeze's bare-basename rule for directories: `fixtures` and `../stage7` are denied;
  - a glob is matched component by component with `fnmatch`, as the shell matches it.

  **The comment says the limit plainly:** a rule that reads the command cannot catch every route. A script that removes a folder, `find -delete`, `xargs` fed from a pipe, a `cd` whose target the rule cannot know, or a word with `$` or `~` gets past it.
- **`payloads.py` gains the ring 8a section:** `freeze_cases` on the fifteen, `nasm -o` over each fixture's binary, the targeted denials, and the allowances measured at item 3. `loader.asm`'s Write and Edit stay allowed until 16b. Then **34 directory-rule denials**: all 17 of test 4 (c)'s shapes, plus the rule's edges (a bracket glob, a `?` glob, `git -C . rm`, a dot segment, `../stage7`, a bare `fixtures`, the second segment of a chain, after a pipe, `/bin/rm`, an assignment first, after `--`, a file moved *into* a directory holding frozen files, since the owner said "any argument"). And **18 allowances**: all of (c)'s allowed side, plus scratch globs, `/tmp/stage7`, the words in prose and in a quoted message, `git rm` of an ordinary path. **The table: `2046 payloads: 1392 must be denied, 654 must be allowed, 0 wrong`.** Every earlier stage's allowance survives the rule.
- **The spot lists of test 4 (c), fed to the hook as data:** all 102 denials but `loader.asm`'s five are denied; all 30 allowances allowed; the builder's eight files writable. The five `loader.asm` mutations are the clause that stays red until 16b.
- **A5, the one-expectation grep:** PARTS.md's only "or"s near a line are the guest's general rules (the recovery table's two `<why>`s, the `demoted` state), not twin expectations. The checker awaits exactly `S8: watchdog tco 30 s` and `S8: recovery i8042 watchdog`, and no pattern alternates two lines.
- **Immediacy:** one `Edit` on PARTS.md (`W = 3,000 ms` → `5,000`) was **denied** by the live hook: "stage8/PARTS.md is frozen acceptance machinery … (a direct Edit)".
- **`git diff 076d74b` over the 63 earlier `PROTECTED` paths: empty.**
- `CLAUDE.md`: the payload count (2046 at ring 8a) and one bullet on the directory rule under "Working with the hooks".

| Run | Result |
|---|---|
| **The gate, whole, on the repository's binary** (`stage8/out/gate-8a.log` from line 2552, headed `commit c4a6111+uncommitted`, 15:11:28 to 15:41:34, 30.1 min) | **test 1 PASS, test 2 PASS, test 3 FAIL by design, test 4 FAIL by design on (c)'s loader clause alone**, exit 1: the expected state at this commit |
| Test 3, quoted | `G1: no 'molt: i8042 shadow [0-9a-f]{16} ' within 10 s of the step`, and the same at W1, F1 and L1: `the fates: G FAILED, W FAILED, H FAILED, F FAILED, L FAILED in 81.9 s`. The repository's binary has no molt words yet |
| Test 4 (a), (b) | held: the harness's strings; `timeout -k 5 600` before `checkmetal.qemu_argv` itself |
| Test 4 (c) | **`2046 payloads: 1392 must be denied, 654 must be allowed, 0 wrong`**; the only refusals are **the nine on `stage8/loader.asm`** (Write and Edit, relative and absolute; `>`, `sed -i`, `cp`, `rm -f`, a python heredoc), which item 16b freezes. Every directory shape is now denied |
| Test 4 (d) | ring 7d's gate **green**: 7d's tests 1–4, and inside its test 4 the 7c, 7b and 7a gates, all four tests each |

**Item 14** — the loader moved into `stage8/loader.asm`; the read-only
floor, 27 September 2026.

**The move.** `stage8.asm` does `%include "stage8/loader.asm"` at `.text`'s
start, below its constants. The move was made by a script over ring 7d's
source (fourteen spans and the constants, each moved verbatim), and a
comparison of every non-blank line before and after: nothing lost but the
four lines deliberately edited, nothing added but the new lines listed in
the commit. `loader.asm` (2,706 lines) holds, in reading order:
- **`efi_main` to the handover**: its last act is `call mouse_init`, then `jmp seed_main`. `seed_main` in `stage8.asm` is the rest of the old `efi_main`: the drain, `S7: keyboard ready`, the replay, the prompt and the main loop;
- serial with `serial_raw_puts`, and the firmware helpers `get_memory_map` and `alloc_tramp_page`;
- paging: `build_paging`, the new `text_split`, `cpu_phys_bits`, `alloc_spare_page`, `map_mmio_2m`;
- the IDT, `exc_common` and `halt_forever`;
- `pci_cfg_read32`/`write32` and `pit_wait`;
- the disk's read path: the whole AHCI driver with its one command routine `ahci_rw`, `disk_select` and DISK.md's words, `gpt_validate`, `gpt_read`, `crc32_update`, `disk_rw`/`home_rw`/`blk_rw`, `notebook_init` with `record_valid`, and `home_init`;
- SHA-256;
- **every constant those read, inside `.text`**: their strings and errors, the words and GUIDs, the GOP's GUID, `sha_k` and `sha_init`. A grep found no write to any of them;
- the `LOADER_STATE` macro, which the seed expands in its BSS.

**Choices for Cowork's review of the loader (A6):**
- **Routines that both read and format stay whole.** `disk_select`, `notebook_init` and `home_init` can format a blank disk, and they moved as they were. The seed keeps the writers `gpt_write`, `gpt_build_header`, `notebook_append` and `home_install`, which reach the disk through the loader's `disk_rw` and `home_rw`.
- **What the loader calls in the seed:** `edid_read`, the ACPI walk and the wake of the cores, `tsc_calibrate`, the glass and the console, `pci_scan` (it also records the NICs, so it stays the seed's), `gpt_write` on a blank disk, `home_recount` and `choices_update`, `nic_find`, `pic_init` and the interrupt entries, and `mouse_init`. The loader's banner lists them.
- **Kept in the seed's `.data`:** the GDT, `gdtr`, `idtr` and every variable (`svc_table`, `fb_*`, `gop_ptr`, …). PARTS.md leaves the descriptor tables writable this ring.

**The floor.**
- `build_paging` ends in a jump to `text_split`. That maps the image's 2 MB page as 512 pages of 4 KB in `image_pt`, a new BSS page beside `pd_tables`: `.text` present and read-only, the rest present and writable, with the 2 MB entry's cache bits. A `.text` across two 2 MB pages halts with a named error instead of staying writable.
- CR0.WP is set straight after the CR3 load, and in the trampoline (`0x80010001`, PG | WP | PE).
- **`LOADER_STATE`** is one page-aligned block holding `sha_state`, `sha_w`, `sha_tail` and `sha_digest`.
- `home_undo` sets its build aside in its own `undo_build` (`HB_BYTES`), no longer in `sha_tail`.
- The three `PCI_CMD_*` defines moved to the top of `stage8.asm`, since the loader's AHCI code now assembles above their old place.

**The build.** It assembled first time: **45,056 bytes** as before (`.text` still 0x401000–0x408FFF, `.data` 8 KB raw, the image to 0x5E3000, inside one 2 MB page), SHA-256 `7a1a5563605d6c0b…`.

| Run | Result |
|---|---|
| **A private copy writing into `.text` from the main loop** (`stage8/out/probe8a/item14/`, the 7b shape headless at `-smp 4`) | all nineteen lines to `S7: keyboard ready`, then **`ERR: exception 14 at 0x00000000004035b4`**: the listing puts the probe's `mov byte [rax], 0xCC` at RVA `0x35b4` |
| **The same from the glass core** (the first instruction of `glass_main`) | **`ERR: exception 14 at 0x0000000000408136`**, its store; then `the glass needs a second core`, as that core is gone. So CR0.WP holds on the application processors through the trampoline |
| **`checkmolt.py --document`** (test 1's checker; `gate-8a.log`, header 16:28:51) | exit 0; **the 64 round constants lie once in the build, at 0x3428, inside `.text`**. The PE fields test 1's shell reads (MZ, PE, `0x8664`, characteristics `0x22f`, PE32+, subsystem 10) read the same from the build |
| **`checkmolt.py --seven`** (test 2 on this binary; same header) | **green in 425.7 s**: the 7c serial boots, the stages, the row and the three sittings each return 0; nothing outside `stage8/out/` changed; not one `S8:`, `part:` or `molt:` line in the twelve captures |

**Not re-run at this commit:** test 3 (red by design: no `! molt`), test 4
(red on (c)'s loader clause until 16b), and the stage7 gates, whose binary
this item cannot touch (the plan's conventions for items 14 and 15). The
log also holds an earlier `--seven` header at 16:26:17 with no result: that
run was stopped by hand after a reorder of the loader's sections changed
the build under it. Its capture is superseded by the 16:28:51 run.

**For item 15:** the draft's `patch.py` no longer applies. Its hook 1, the
CR0.WP insertion, stops it: the code moved into `loader.asm`. It exits
before writing anything. The draft's `split.asm` and its three paging hooks
are now in the repository, and its other hooks (`mouse_init`'s call site,
`exc_common`'s blame line, the AHCI poll's breath) now point into
`loader.asm`. Item 15 rebases the draft's molt code onto this layout.

**Item 15** — the slot, ABI 3, the part frame, the home names, the notes,
the words and shadow, 27 September 2026. The draft's molt code, rebased
onto item 14's layout by two splice scripts (each anchor applied exactly
once), with Cowork's three points from the pre-read placed as asked.

**The loader's half (`stage8/loader.asm`):**
- **`molt_boot`**, called where `efi_main` called `mouse_init`. With no molt note it is `mouse_init` alone. With one: the known answer, the door for each slot in shadow or live, the boot note, `svc3_fill`, then a live part's `init` (the pointer centred first) or the generic's `mouse_init`, and the IRQ1 and IRQ12 gates pointed at the part stubs. **Steps 2–4 and the arming (the evidence, the recovery decision, Esc, the watchdog) are item 16's**, so the boot goes straight from `S8: sha256 ok` to the door;
- the notebook's molt scan (`molt_scan`, the tokenizer, `ms_apply` with every note kind, the accumulators, `slot_counts`, `slot_on_probation`), whole: probation is decision 7, and the table and the undo need the demoted state;
- `door`, `part_name`, `check_part` (the header rule, which the seed's install calls too), `part_call`, `s8_line`, `molt_ready` (only `after_ready` this item), and the hex and state putters;
- **Cowork's point 1:** `slot_words`, `kat_abc`/`kat_digest`, `hex_digits` (moved from the seed's `.data`), the thirteen note words, `S8: sha256 ok`, `sha256 known answer`, `molt `, `molt boot `, `S8: part `, `bad hash` and `bad header` are inside `.text`;
- **Cowork's point 2:** `LOADER_STATE` gains the scan's state (`ms_*`), the boot's (`part_loaded`, `part_state`, `boot_n`, `after_ready`, `part_saved_rsp`) and the loader's own buffers (`ldr_line`, `ldr_note`, `ldr_hex`, `ldr_kat`). The draft's `kat_ok` (written, never read) and `ls_sha_state` (unused) are gone. Item 16 adds the evidence, Esc's result, the watchdog's bases and verdict, the pet's state, the heartbeat and the exception flag to the same block.

**The seed's half (`stage8/stage8.asm`):** the molt's defines and
`SAVE_ALL`/`RESTORE_ALL` at the top; the notebook's machine writer
(`nb_write`, `molt_note`: the writers are the seed's, decision 10);
`pointer_centre`; ABI 3's tables, services and upcalls; `mouse_sink`; the
part stubs and `part_service`; `note_overflow` (the obs page's
`molt_overflows` at `0x360` only: blocking the pet is item 16's);
`part_loop` (no heartbeat, pet or health mark yet); shadow's comparison,
the count notes and `count_point`; the discard point and `molt_finish`;
the four words, the fetch and `home_install_part`; the nine hooks (the
ready line, `part_loop`'s entry, `molt ` refused, `bang_line`, the
`part-` app frame, the app count, the choices row, `finish_line`'s two).
**Cowork's point 3:** the service tables, the raw ring, `kbd_seq`, the
four comparison queues, the live key queue, the counts, the seed's line
buffers, the part region and the DMA pool are one block of the seed's BSS
placed before `obs_page`: not in `LOADER_STATE`, and not before
`image_pt`.

**Two changes from the draft:**
- **`svc_map_mmio`'s RCBA refusal reads RCBA from the LPC bridge at each call** (`lpc_rcba`: Intel at 00:1f.0, the enable bit, the 16 KB window). The draft read a `rcba` that `tco_find` sets, which is item 16's, so the refusal would have been off until then.
- `home_swap_part` sets its build aside in `undo_build`, as `home_undo` does since item 14, not in `sha_tail`.

The plan's item text says "the part region (1 MB + header)"; PARTS.md,
frozen, says 65,536 bytes, and the build follows PARTS.md, as the draft
did.

**The build.** It assembled first time: **57,344 bytes**, the draft's size
(`.text` 0x401000–0x40BFFF, inside the image's first 2 MB page; the image
to 0x60C000), SHA-256 `bac24a0853ab0910…`.

| Run | Result |
|---|---|
| **The probe** (`stage8/out/probe8a/i15/probe15.py`, private: the checker's own `Fates.boot`, `judge`, `conv`, `table`, `check_notes` and `check_fetch` on a private build, its `Book` less item 16's watchdog line, a `! molt` at each boot's end where the health mark will write the count note) | **ok in 218.4 s.** P1: `part i8042 shadow 4fe6beefc4bc57d0`, the frame `parts.fixture_frame('good')` byte for byte, the twin's request and key. P2–P4 at `-smp 4`: 363, 383 and 433 keyboard bytes and 1,668 packets each, **0 disagreements**, the table `boots 3/3 keys 1141/1000 mouse 5004/5000`, then the take `molt i8042 live 4fe6beefc4bc57d0`. **P5, P6, P7 live at `-smp 2`, `4` and `8`**: the part's `part:` pair and no `i8042:` line, the note typed through the part, 40 packets, the pointer at the centre before the first packet, `mouse_id` 0 then 1, `i8042_cmd` 0 |
| `parts.py --disk` on the probe's disk | exit 0: `i8042 live 4fe6beefc4bc57d0`, `boots 3/3 keys 1179/1000 mouse 5004/5000`, `disagreements 0 probation 0/3`, 15 molt notes, the door's `S8: part i8042 live 4fe6beefc4bc57d0`. Its `unhealthy run 6` is right for a build with no health mark yet |
| **The gate, whole, on this source** (`stage8/out/gate-8a.log` from line 3330, headed `commit 62f6be7+uncommitted`, 16:58:35 to 17:32:12, 33.6 min; its build byte-identical to the probe's) | **test 1 PASS, test 2 PASS, test 3 FAIL by design, test 4 FAIL by design on (c)'s loader clause alone**, exit 1: the expected state at this commit |
| Test 1 | green: the 64 round constants lie once in the build, at 0x43d0, inside `.text` |
| Test 2 | **green in 425.8 s**: ring 7c's three serial boots, its stages, ring 7d's row and sittings each return 0 on this build; nothing outside `stage8/out/` changed; not one `S8:`, `part:` or `molt:` line in the twelve captures |
| Test 3, quoted | G1 green: `'! molt' drew ['i8042 generic']; 'molt x' refused 'molt is reserved'; 'part i8042 shadow 4fe6beefc4bc57d0'; '! part-i8042' refused; the take refused 'below threshold: boots 0/3 keys 0/1000 mouse 0/5000'; errors 3`, the frame and the key the twin's. **G2, W2 and F2 red: `no 'S8: healthy 1\r\n' within 70 s of ready`**: the first shadow boot's awaited health mark. The plan expected the first red at G2's watchdog line, but the step loop's await of the mark fails before `judge` compares the lines, where the missing `S8: watchdog tco 30 s` would be named. Both are item 16's. W1 and F1 green (the installs). H not made (G did not reach G6). **L green**: `'S8: sha256 ok', 'S8: part i8042 bad hash', no watchdog, no boot note, the generic's pair; … nothing demoted`, as the liar's door boot loads no part. `the fates: G FAILED, W FAILED, H FAILED, F FAILED, L ok in 291.4 s` |
| Test 4 | (a), (b) held; (c) `2046 payloads: 1392 must be denied, 654 must be allowed, 0 wrong`, the only refusals **the nine on `stage8/loader.asm`**, which 16b freezes; (d) ring 7d's gate **green**, with the 7c, 7b and 7a gates inside it |

**Item 16** — the watchdog, the pet, the health mark, the recovery
rules, Esc and the blame line, 27 September 2026. The draft's item 16
code spliced by hand onto item 15's layout, with **Cowork's four points
from its review of the draft and item 15 built in**, and the owner's
decision on the timer's halt.

**The loader's half (`stage8/loader.asm`, 4,624 lines):**
- **`molt_boot` gains steps 1–4 and 6:** `esc_setup` before the known answer (A3; PARTS.md's step 1), then `tco_find`, `tco_evidence` and `tco_halt` (step 2), `recovery_apply` (step 3), `any_running` and `esc_window` with `molt recovery owner` (step 4); after the boot note, `tco_arm` (step 6). `molt_ready` stamps `ready_tsc`;
- `recovery_apply` and `demote_note` (the recovery table, the blamed part, `recovery all`); `esc_setup` and `esc_window`; `tco_find`, `tco_evidence`, `tco_halt`, `tco_arm`; `molt_breath`, `molt_turn` and `molt_pet`; `exc_blame`;
- **the two loader hooks:** `molt_breath` at every breath of `ahci_rw`'s `.poll`, and `exc_common`'s blame call with a part loaded (with none, ring 7d's `jmp halt_forever`);
- **`LOADER_STATE`** gains `evidence`, `esc_held`, `tco_base`, `pm_base`, `rcba`, `tco_armed` (the verdict), `exc_flag`, `overflow`, `in_wait`, `health_done`, `ready_tsc`, `heartbeat` and the pet's three `last_pet_*`; the fourteen strings go into `.text` beside item 15's;
- the banner names what item 16 added, the seed routines it now calls (`i8042_wait_ibf`, `console_puts`, `console_putc`), and says exactly which of `LOADER_STATE`'s flags the seed's own code writes: `health_done` (the health mark) and `overflow` (`note_overflow`, reached from the stubs, the live key upcall and `mouse_sink`). No address in the block is handed to a part. The draft's sentence ("nothing … its upcalls write is in it") was no longer true once `overflow` moved into the block, so it was rewritten.

**The seed's half (`stage8/stage8.asm`):** the TCO's registers and the
loader's times as defines beside the molt's (`TCO_TMR_VALUE` 25, `PET_MS`
1000, `HEALTH_MS` 60000, `ESC_W_MS` 3000); `molt_breath` at `net_breathe`;
`note_overflow` sets `overflow` outside a wait; `part_loop` calls
`molt_turn` and takes the health mark; `health_mark` beside `count_point`;
its two strings in `.data`. **The draft's `PROBE_LOCK` and
`PROBE_NO_EVIDENCE` switches are not in the repository's loader**: the
probes below patch private copies instead.

**Cowork's four points, built in before the review:**
1. **RCBA not enabled.** `tco_find` leaves `rcba` 0 when config `0xF0` bit 0 is clear, and `tco_arm` then goes to `S8: watchdog tco locked` and leaves the timer halted, unguarded. The draft went on to arm and printed `S8: watchdog tco 30 s` with `NO_REBOOT` never cleared or read back.
2. **The owner's decision at item 16: the timer halted at step 2.** With the evidence read and cleared, the loader sets `TCO_TMR_HLT` in `TCO1_CNT` (`NMI_NOW` masked out, never written back) on every boot with a molt note where a TCO was found. Step 6 unhalts it when it arms; `tco locked` leaves it halted. No new line. **The owner's reason:** a boot that arms nothing (a recovery boot, an Esc boot, a door refusal) must not depend on the firmware to stop a timer an earlier boot armed. The twin stops it at its own reset, but silicon may not.
3. **`esc_window`.** `0x01` counts as a make only when the previous byte was not `0xF0` (`F0 01` is F9's break in set 2), as `parts.esc_held` says. `F0 76` stays Esc's break.
4. **`svc_dma_pages`.** A count above `DMA_POOL_PAGES` is refused before it is added to `dma_used`. Before this, `dma_used + count` wrapped in 32 bits, so `dma_pages(0xFFFFFFFF)` after one page passed the pool check and `rep stosq` ran on.

**For Cowork's review, one question the owner's decision leaves open:** a
boot whose known answer fails stops at step 1 (PARTS.md: "arms nothing,
… no further `S8:` line"), so it never reaches step 2's halt. On silicon
that keeps an earlier boot's timer across the reset, such a boot would be
reset about 30 s later, and so would every later boot, because each one
fails the same way. The halt was placed at step 2 as decided; whether it
belongs before the known answer too is the owner's to say.

**The build.** It assembled first time: **57,344 bytes**, SHA-256
`4661fd8e7aab6759…` (`.text` still inside the image's first 2 MB page).

| Run | Result |
|---|---|
| **Points 3 and 4 on the host** (`stage8/out/probe8a/i16/units.py`, private: the exact lines of `esc_window`'s decision loop and of `svc_dma_pages` cut out of the source, wrapped in an x86-64 Linux harness, assembled with `nasm -f elf64` and run) | **Esc: 5,813 vectors against `parts.esc_held`, 0 wrong**: PARTS.md's six rows, seven for point 3 (`F0 01` no, `01 F0 01` yes, `76 F0 01` yes, `F0 01 81` no, `F0 76 01` yes, `01 F0 76` no, `F0 F0 01` no), every string of up to four over seven byte values, and 3,000 random. **The pool:** `dma_pages(1)` page 0; `0xFFFFFFFF` and `0x80000000` refused with `dma_used` 1; 16 refused; 15 pages 1–15; then 1 and 0 refused; the page after the pool untouched. **A/B:** the draft's `esc_window` gives 18 wrong (every `F0 01` a make); HEAD's `svc_dma_pages` runs `rep stosq` off the harness's memory on `0xFFFFFFFF` (SIGSEGV) |
| **Test 3 alone on this build** (`checkmolt.py --fates`, `gate-8a.log` headed 17:57:41) | **`the fates: G ok, W ok, H ok, F ok, L ok in 852.7 s`**. G2–G4: `S8: watchdog tco 30 s`, 0 disagreements, the mark 60.2 s after ready. G5: `'? hold' answered 60.4 s after its Enter (HOLD_S 60), 300 moves during it (85 packets kept), with no reset`, idle to `S8: healthy 4` with no reset (A1). G6: Esc held from `S8: sha256 ok`, `S8: recovery owner`, no part and no watchdog. H3: the reset 30.2 s after the hang's trigger. F3: `ERR: exception 6 in part i8042 +0x000001fb`, the reset 31.0 s later. Both are followed 0.8 s after OVMF's first byte by `S8: recovery i8042 watchdog`. L2: `bad hash`, no watchdog |
| **The probes** (`stage8/out/probe8a/i16/probe16.py`, private; each variant is a copy of both files under `i16/v-<name>/`, patched by exact replacement, and booted through the checker's own `Fates.boot`; `probe16.txt`) | **`results: smp2 ok, smp8 ok, lock ok, norcba ok, leftover ok, kat ok, probation ok, all ok, stray ok, unhealthy ok`** |
| Hang and fault live at **`-smp 2` and `-smp 8`** (fetched through the mock, made live by host notes, then the checker's own `trigger_boot`) | all four judged ok by the checker. Resets **30.1 s** (H2), **30.9 s** (F2), **30.4 s** (H8) and **31.2 s** (F8) after the trigger; the recovery 0.8 s after OVMF's byte each time; `molt i8042 demoted <sha16> watchdog` |
| `lock` (GCS read back with bit 5 set) | `S8: watchdog tco locked`, then on to `molt healthy 1`, the count note and `S8: healthy 1`, unguarded |
| **`norcba` (point 1: config `0xF0` bit 0 masked)** with hang live | `S8: part i8042 live …`, `molt boot 2 i8042 live`, **`S8: watchdog tco locked`**, no `tco 30 s`; the hang, then **one `S7: alive` in 70 s**: the timer stays halted and nothing resets |
| **`leftover` (point 2, A/B)**: a copy that, just before step 2's halt, leaves the timer running as an earlier boot would have (`TCO_EN` cleared, `TCO_TMR` 25, reloaded, unhalted) | **with the halt:** a door refusal (`S8: part i8042 bad hash`) and a recovery boot (`S8: recovery i8042 unhealthy`) each ran 70 s with **one `S7: alive`**. **Without it** (`leftover-nohalt`): the door refusal was **reset by the leftover timer, three `S7: alive` in 70 s** |
| `kat` (one byte of `abc`'s digest altered) | `ERR: sha256 known answer`; no `S8:` line, no window, the generic's pair |
| `probation` (`SLOT_N` 2) | both doors `bad hash`; `! molt take i8042` and `! molt i8042` → **`another part is on probation`**, `errors` 2, `requests` 0 |
| `all` (hang past probation by host notes, live at boot 5) | the reset 30.2 s after the trigger; `molt i8042 demoted f0668b687c68cab0 watchdog`, `molt recovery all`, `S8: recovery all` 0.8 s after OVMF's byte |
| `stray` (good's `byte` entry writing into the seed's `.text`) | `ERR: exception 14 at 0x…4da182`, then **`ERR: exception 14 in part i8042 +0x00000182`**; the reset 31.0 s later, `S8: recovery i8042 watchdog` |
| `unhealthy` (`SECOND_TO_STS` cleared before the read) | boot 2 and boot 3 live, each reset 30.2 s after its trigger; at boot 4 `molt i8042 demoted f0668b687c68cab0 unhealthy`, `S8: recovery i8042 unhealthy` |
| **The gate, whole, on this source** (`stage8/out/gate-8a.log` from line 4063, headed `commit c6b30c0+uncommitted`, 18:27:46 to 19:10:44, 43.0 min) | **test 1 PASS, test 2 PASS, test 3 PASS, test 4 FAIL by design on (c)'s loader clause alone**, exit 1: the state the plan expects at item 16 (A6) |
| Test 2 | green: with no part installed the build is ring 7d's to every frozen 7c and 7d check, and not one `S8:`, `part:` or `molt:` line |
| Test 3 | **green: `the fates: G ok, W ok, H ok, F ok, L ok in 851.9 s`** |
| Test 4 | (a), (b) held; (c) `2046 payloads: 1392 must be denied, 654 must be allowed, 0 wrong`, and **the only refusals are the nine on `stage8/loader.asm`**, which 16b freezes; (d) `./stage7/test-7d.sh` **green**: 7d's tests 1–4, with the 7c, 7b and 7a gates inside its test 4, all four tests each |

**Item 16, the A6 review** — Cowork's review of `stage8/loader.asm`,
27 September 2026: **no defects.** One change came out of it, by **the
owner's decision at the A6 review**, answering the question item 16 left
open. It was made while the file was still open, as a further item 16
commit:
- **In `molt_boot`, `tco_find` and `tco_halt` now run before the known answer**, just after `esc_setup`. So a boot whose SHA-256 known answer fails still halts a timer an earlier boot armed.
- **The evidence is still read and cleared at step 2**, after the known answer, as PARTS.md orders it. Step 2 is now `tco_evidence` alone.
- A failed known answer still loads nothing, journals nothing, arms nothing and prints no further `S8:` line. Halting reads no status bit and clears none.
- The comments at steps 1 and 2, the banner and `tco_arm`'s step 1 say so.

The build: 57,344 bytes, SHA-256 `9e81c7b5d24ac363…`.

| Run | Result |
|---|---|
| **The probes the change touches**, re-run on this build (`probe16.py katleft kat leftover norcba lock unhealthy`; `stage8/out/probe8a/i16/probe16b.txt`; item 16's outputs kept as `probe16.item16.txt`) | **`results: katleft ok, kat ok, leftover ok, norcba ok, lock ok, unhealthy ok`** |
| **`katleft`, the change's own case (A/B)**: a failed known answer with a timer an earlier boot left running | **with the halt before the known answer:** `ERR: sha256 known answer`, no `S8:` line, **one `S7: alive` in 70 s**. **Without it:** the same boot was reset by the leftover timer, **three `S7: alive` in 70 s**, each boot failing the same way: the reset loop the change prevents |
| `leftover` (the halt now at step 1) | a door refusal and a recovery boot each 70 s with one `S7: alive`; without the halt, the door refusal was reset. **The reset boot of that run printed `S8: recovery i8042 watchdog`, so `SECOND_TO_STS` survives the halt at step 1 and is read at step 2** |
| `kat`, `norcba`, `lock`, `unhealthy` | as at item 16: no `S8:` line; `tco locked` with no reset in 70 s after a live hang; `tco locked` then `S8: healthy 1`; boots 2 and 3 reset 30.2 s after their triggers, then `S8: recovery i8042 unhealthy` |
| **The gate, whole, on this build** (`stage8/out/gate-8a.log` from line 4646, headed `commit 01a34b1+uncommitted`, 20:27:50 to 21:10:46, 43.0 min) | **test 1 PASS, test 2 PASS, test 3 PASS** (`the fates: G ok, W ok, H ok, F ok, L ok in 852.0 s`), **test 4 FAIL by design on (c)'s loader clause alone**: `2046 payloads: … 0 wrong`, the nine `loader.asm` refusals the only ones, `./stage7/test-7d.sh` green inside it with 7c, 7b and 7a |

**Carried to item 17, for `stage8/HP-8a.md`** (Cowork, at the A6 review):
if the HP prints `S8: watchdog tco 30 s` but does not reset within about a
minute of the hang, the likely cause is the firmware having set
`TCO_LOCK`. `TCO_EN` then could not be cleared, and the first expiry went
to SMM. It is recorded as the ring's finding, as decision 5's fallback
says.

**Item 16b** — `stage8/loader.asm` frozen, 27 September 2026 (A6).
- **`PROTECTED` grows to sixteen ring 8a paths:** `stage8/loader.asm` joins, and the hook's comment says what the floor holds and that only the owner's hand opens it now.
- **`payloads.py` gains `FROZEN_8A_LOADER`**: `freeze_cases` on the loader, its 18 cases (15 mutations denied, `cat`, `grep` and `sha256sum` allowed). Item 13's two allowances, `Write` and `Edit` on `loader.asm`, become denials. **The table: `2064 payloads: 1409 must be denied, 655 must be allowed, 0 wrong`.**
- **Immediacy, shown live:** one `Edit` on `loader.asm` (a word in `tco_arm`'s step-1 comment) was **denied** by the running hook: "stage8/loader.asm is frozen acceptance machinery, and this call would modify it (a direct Edit)".
- **The loader frozen is `d01a013`'s**: item 16 with the A6 review's change. The build is 57,344 bytes, SHA-256 `9e81c7b5d24ac363…`.
- `CLAUDE.md`: the payload count (2064 at item 16b) and the ring 8a gate with its wall time in the build block.

| Run | Result |
|---|---|
| **The gate, whole, on the frozen loader** (`stage8/out/gate-8a.log` from line 5229, headed `commit d01a013+uncommitted`, 21:12:36 to 21:55:32, **42.9 min**) | **ALL FOUR TESTS PASS, exit 0**: "All automated tests passed." **The ring's gate passes for the first time, and on `loader.asm` frozen**, as A6 and the kickoff's F require |
| Test 1 | green: the artefact, the stick as 7c, PARTS.md and SEED.md read cold with every worked example, the five fixtures, the known answer, the seed record |
| Test 2 | green: with no part installed the build is ring 7d's to every frozen 7c and 7d check, and says nothing of ring 8a |
| Test 3 | green: `the fates: G ok, W ok, H ok, F ok, L ok in 852.0 s` |
| Test 4 | **green**: the harness's strings, the argv check, **every ring 8a path frozen, `loader.asm` with them**, `2064 payloads: 1409 must be denied, 655 must be allowed, 0 wrong`, with no refusal left; `./stage7/test-7d.sh` green inside it, 7d's tests 1–4 with the 7c, 7b and 7a gates inside its test 4, all four tests each |

**Item 17** — the paperwork and the owner's procedure, 27 September 2026.
No guest code changed. **One frozen file changed, by the owner's hand: the tenth freeze opening, `503b4e5`**, `stage8/parts.py`'s `current_seed` check ("The frozen acceptance machinery" has the list and the reason). The item stopped at it, and the owner applied CC's diff.
- **`stage8/seed-record.md` gains seed 1**, naming item 16b's commit `fc64a07`. The line came from a rebuild by SEED.md's recipe: `git archive fc64a07` into an emptied `stage8/out/seed/1/`, that tree's `stage8/mkimage.sh`, NASM 3.02. It was written by `parts.seed_line` from the build, never typed:
  `seed 1 9e81c7b5d24ac363d2d8711e31044a70b4946ff72f1173b429eec6c478fcff77 57344 fc64a07 2026-09-27 nasm 3.02`. **`python3 stage8/parts.py --seed`: exit 0.** Both seeds rebuild from their commits and agree; the witness's seed is seed 1, and `stage8/out/BOOTX64.EFI` is seed 1.
- **`stage8/HP-8a.md`**, the owner's day, in METAL.md's shape (the plan's "Test 5"). It has steps 0–11, a debugging table and "what the twin could not prove", and it carries Cowork's `TCO_LOCK` note from the A6 review at step 10. Four things were added beyond the plan's list, each from PARTS.md's rules:
  - **wait for `S8: healthy` on every boot that loads a part**, because two unhealthy boots in a row demote the part in shadow;
  - **type plain lowercase with a pause after Enter**, because of PARTS.md's stated discard limit: a Shift or an `E0` among the keys dropped after a line can make the next key disagree, and one disagreement blocks the take;
  - **boot 9's trigger predicted**: `hang N` lines are fourteen bytes each, so the HP stops at the eighth line's first key;
  - **the deadline read from the chart as an upper bound**: `chart.py` stamps whole lines and the HP's firmware writes nothing but noise to COM A, so the interval from `hang 7` to the next `S7: alive` holds the HP's reset path too.
  It also records that mlrig on Omarchy no longer carries `10.0.2.4/24` (checked 27 September: `eno2` at `192.168.1.107/24`, NetworkManager active), so METAL.md step 5 must be done again.
- **`CLAUDE.md`**: `./stage8/mkimage.sh`, `python3 stage8/mkstick.py`, the gate's boot count (32 QEMU runs and two rehearsals of its own, 21 of them in test 3, two carried through a watchdog reset), `python3 stage8/parts.py …` and `python3 broker/molt.py --mock --part <f>` in the build block; the windowed paragraph names `stage8/HP-8a.md` and ring 8a's twin. **The gotchas gain nothing**: nothing this ring was corrected a second time. The first-time candidates are below.
- **`README.md`**: Stage 8 and ring 8a in the story table and the prose, and ring 8a's twin under "Running it", with `-display gtk,zoom-to-fit=on`.

| Run | Result |
|---|---|
| **The payload table** (`python3 .claude/hooks/payloads.py`) | `2064 payloads: 1409 must be denied, 655 must be allowed, 0 wrong`, exit 0 |
| **A first gate run, void** (`stage8/out/gate-8a.log`, the header after line 5229's run) | **test 1 PASS; test 2 FAIL on its escape watch alone**: `test 2 changed 45 file(s) outside stage8/out/: stage0/out/nasm.err, …`. **CC's error, not the guest's:** Stages 0–3's gates had been started beside the gate, and test 2 watches every other stage's `out/` for writes. Every one of test 2's entry points had returned 0. CC stopped the run in test 3 by its process groups, checked that nothing held 9999, 9998 or 9997, and ran the gate again alone |
| **A second gate run, stopped** (the next header in the log, before `503b4e5`) | **test 1 FAIL: `FAIL: seed: current_seed`**, `parts.py --example` failing on the record with seed 1: the frozen-file defect above. **Test 2 PASS** (425.9 s, nothing outside `stage8/out/` changed). CC stopped, wrote the diff unapplied, and waited for the owner's hand; the run was stopped in test 3 once `503b4e5` landed |
| **`parts.py --example` and `--seed`** on `503b4e5` | both exit 0: every worked example reproduced; seeds 0 and 1 rebuilt and agreeing, the witness's seed 1, the build seed 1 |
| **The gate, whole** (`stage8/out/gate-8a.log` from line 6072, headed `commit 503b4e5+uncommitted`, 22:22:00 to 23:05:00, **43.0 min**, nothing else running) | **ALL FOUR TESTS PASS, exit 0**: test 1 green with seed 1 in the record (every worked example, the record append-only, the witness's seed 1); test 2 green in 425.8 s, nothing outside `stage8/out/` changed, not one `S8:`, `part:` or `molt:` line in 12 captures; test 3 `the fates: G ok, W ok, H ok, F ok, L ok in 852.1 s`; test 4 green, `2064 payloads: … 0 wrong` and `./stage7/test-7d.sh` green inside it with the 7c, 7b and 7a gates inside its test 4, all four tests each |
| **Stages 0–3** (each `mkimage.sh` or `nasm`, then `test.sh`, on their own binaries) | **all green**: "All automated tests passed" four times |
| **Stages 4 and 5, rings 6a, 6b and 6c** (each on its own binary, one at a time after the gate) | **all green, each alone after the gate**: Stage 4 (101 s), Stage 5 (230 s), ring 6a `./stage6/test.sh` (382 s), ring 6b `test-6b.sh` (394 s), ring 6c `test-6c.sh` (206 s), "All automated tests passed" each |

**Item 17, Cowork's review of `stage8/HP-8a.md`** (28 September 2026,
from `422f7a7`). Cowork found the document sound, having checked every
expected line against PARTS.md and the loader. Three additions went in,
all to the unfrozen document, with no gate run:
1. **A debugging row for the HP's own firmware screen after a reset** (an unexpected-restart message waiting for a key). Photograph it and press the key it asks for, never Esc or a menu key. It is a finding; the evidence bit is read by the next GermOS boot as usual. Step 10's "do nothing" points to that row.
2. **A debugging row for `S8: recovery i8042 watchdog` on a boot where `good` was loaded** (boots 2–5 or 7). That is unexpected. The likeliest metal cause is the pet's outside check: a PS/2 timeout or parity error leaves status bit 6 or 7 set until the next byte, and an idle human lets the deadline pass. The others are a ring overflow and a seed hang. The owner stops the day there and brings the chart to Cowork. `! molt undo` returns `good` to shadow with its counts from 0.
3. **Step 10: line 8 typed straight after line 7's Enter**, and the deadline's reading says the interval also holds that pause.

**The owner's decision on the openings' count**, at the same review:
`0a5fd87` counts, so `503b4e5` is the tenth. The list in "The frozen
acceptance machinery" and every ordinal in this file were corrected,
and so were the two in CLAUDE.md's gotchas (ring 7b item 10b, now the
sixth; `ebf5794`, now the seventh).

### Ring 8a — green pending the oracle (item 17, 27 September 2026)

**What was built.** Stage 8's first ring, on ring 7d's source (`stage8/stage8.asm`):
- **The loader** in `stage8/loader.asm`, frozen at item 16b. It covers everything from `efi_main` to the handover, the disk's read path, and SHA-256, whose `abc` known answer is checked at every boot with a molt note. `.text` is mapped read-only in 4 KB pages, with CR0.WP set on every core.
- **One slot, `i8042`**, with ABI 3's service table.
- **Parts** in the home store as `part-i8042`, and `! molt`, `! molt i8042`, `! molt take i8042`, `! molt undo`.
- **The state in `molt` notes**, each mirrored on serial as `molt:`.
- **Shadow**: two channels, keys and packets, compared in order.
- **The threshold and probation.**
- **The PCH's TCO watchdog** at 30 s. The pet is called at every main loop turn and at every breath of a bounded wait (A1). The health mark comes 60 s after ready, and the recovery table follows from it.
- **Esc at power-on** with a 3 s window.
- **The blame line**, naming the part and its offset.
- **The mock** `broker/molt.py`, and the host tool `stage8/parts.py`.
- **The five fixtures** and their fates in the twin: good, wrong, hang, fault and liar.

With no `molt` note the binary is ring 7d's to every frozen 7c and 7d check (test 2). **57,344 bytes, seed 1, SHA-256 `9e81c7b5d24ac363…`.**

**The numbers:**
- **D1, the twin's TCO:** a tick of 0.6 s (599–600 ms by the TSC), with the reset at 2 × *n* × 0.6 s for *n* = 2, 4, 10, 25 and 50. At *n* = 25 it came 31.0 s from the arming line to OVMF's first byte. The evidence survives every watchdog reset and a monitor `system_reset` (14 resets); only a new QEMU process clears it. The timer does not run until the guest reloads it. `-smp` changes nothing.
- **D2, `-icount shift=0,sleep=off`:** exact repetition at `-smp 4`, and 7 ticks in 259,000 apart at `-smp 2`. The decoder costs 33 / 69 / 135–140 instructions a byte (min / median / worst). The wall time is 5.2× to 6.9× longer.
- **D3, the seams:** attempt 2's rebindings let every 7c and 7d entry point run on stage8's build with nothing escaping `stage8/out/`.
- **D4:**
  - `checkmetal.qemu_argv` passes with `stage8/out` rebound;
  - Esc arrives as translated set 1 `0x01`/`0x81`, with the break at the hold's end and no repeats; an Esc before ExitBootServices is lost to OVMF;
  - the key-byte rule was measured exactly (124 of 124);
  - `mouse_move`s paced 1 ms or more give one packet each, and back to back they are coalesced;
  - the twin's identity is `cpu 000306a9 pci 8086:2918:02`.
- **Item 12's constants:** `READY_S` 30, `SETTLE_S` 1, `WORD_S` 2, `ANSWER_S` 10, `HEALTH_SLACK_S` 10, `HOLD_SLACK_S` 10, `RESET_S` 35, `RECOVER_S` 10, `WIGGLE_PACE_S` 0.005, `BOOT_T_S` 600. The measurements behind them: the health mark 60.0–60.2 s after ready; the held answer at 60.4–60.9 s; the reset 30.1–31.2 s after the trigger (hang and fault, `-smp` 2, 4 and 8); the recovery line 0.8 s after OVMF's first byte.
- **The gate:** 42.9 min at item 16b, 43.0 min at item 17; test 3 alone 852 s; the payload table 2064 cases.

**Tests 1–4 green** on the gate (item 16b's run, and item 17's above). **Test 5 pending**: the owner's day, `stage8/HP-8a.md`.

**The findings of the ring:**
1. **QEMU's `-global ICH9-LPC.noreboot=on` is invisible to a GCS read-back** (D1): GCS reads back 0 after the clear, and the machine simply never resets. So `S8: watchdog tco locked` can be shown in the twin only on a patched copy (items 12 and 16's `lock` probe).
2. **The twin's TCO timer waits for the guest's first reload; silicon counts from reset unless halted.** Hence the owner's decision at item 16: the timer is halted on every boot with a molt note. At the A6 review the halt moved before the known answer (`katleft`, A/B): without it, a failed known answer would be reset by an earlier boot's timer, and so would every boot after it.
3. **Input during a long wait can stop the pets** (item 12). On the unamended draft, G5's 300 moves during the held request overflowed the raw ring, the pet stopped, and the watchdog reset the machine 77 s in. By the owner's amendment (`c4a6111`) test 3 now sends those moves. An overflow inside a bounded wait is counted in `molt_overflows` and never blocks the pet.
4. **The freeze did not cover a command naming only a directory** (item 3). The owner's directory rule is in the hook since item 13, and in CLAUDE.md's hooks section.
5. **Cowork's four points at item 16:** RCBA disabled now means `tco locked`; the timer is halted; `F0 01` is not an Esc make; `dma_pages` is refused before the sum can wrap. **The A6 review: no defects.**
6. **Two checker faults, found by item 12's run and fixed before the freeze:** the expected echo left out each note's Enter, and live boots' `part:` lines were collected after the swap that removes them.
7. **One freeze opening, the project's tenth, at item 17** (`503b4e5`, the owner's hand): `parts.py` checked SEED.md's one-line example against the live record, so it failed as soon as the plan's seed 1 went in.

**Carried:**
- **The IDT, the GDT and the page tables stay writable** (PARTS.md, the read-only floor); a later ring's.
- **Rules proven only by probe, never by the gate:** `tco locked` (a patched GCS read-back), RCBA disabled (`norcba`), the leftover timer and `katleft` (the halt at step 1), the known answer failing (`kat`), `another part is on probation` (`probation`), `recovery all` (`all`), a part writing into the seed's `.text` and the blame line naming it (`stray`), and the no-evidence path to `recovery … unhealthy` (`unhealthy`). All of these are in `stage8/out/probe8a/i16/probe16.py`, with outputs `probe16.item16.txt` and `probe16b.txt`. Esc's decision loop and `svc_dma_pages` were proven on the host by `units.py` (5,813 vectors, 0 wrong). The `.text` write faults are item 14's probes.
- **PARTS.md's stated limit:** keys dropped after a line are still decoded by the part, so a Shift or an `E0` among them can make a later key disagree. The gate never meets it; HP-8a.md tells the owner how to avoid it.
- **Stage 7's caveats, unchanged:** the PHY speed after a reset, TIPG, WIRE.md's halting sentence (ring 8e's), the nineteen-line first boot never watched on the metal, and the x2APIC and trampoline paths.
- **The GPS in the old git history:** postponed by the owner (spec decision 12).
- `stage8/out/probe8a/` is kept: never wipe it.

**First-time candidates for CLAUDE.md's gotchas** (each goes in if it is corrected a second time):
- **A frozen check must hold for every state the plan says comes after the freeze, not only for the state at the freeze.** `parts.py` asked a question of the live record that SEED.md asks only of its one-line example, and item 17's planned seed 1 broke it (the tenth opening). Before freezing, run the checker against the next planned state too. This is near CLAUDE.md's "write the expectation from a run" gotcha, but not the same.
- **Run a gate alone.** Ring 8a's test 2 watches every other stage's `out/` and `germline/`, so any other gate running beside it fails it (item 17's void run). The regressions go after the gate, one at a time.
- **A byte-level match must look at the byte before.** In set 2, `F0 01` is F9's break, not Esc's make (item 16, point 3).
- **Bound a count before adding it.** `dma_used + count` wrapped in 32 bits and passed the pool check (item 16, point 4).
- **A boot that fails early must still stop what an earlier boot started.** The TCO halt moved before the known answer (the A6 review).
- **A refusal that reads state a later item sets is off until then.** The draft's RCBA refusal read `rcba` before `tco_find` existed (item 15).
- **Collect what a check needs before transforming the capture** (item 12's second checker fault).
- **QEMU coalesces back-to-back `mouse_move`s**; pace them 1 ms apart or more (D4).
- **`-icount` forces round-robin TCG without a word**, and `-accel tcg,thread=multi` beside it is refused (D2).

### Ring 8a — test 5 on the HP, and the closure (28 September 2026)

**Ring 8a is CLOSED, by the owner's word, 28 September 2026.** Test 5 ran on the HP Compaq Elite 8300 by `stage8/HP-8a.md`. The stick was flashed once, by the owner's hand, from seed 1 (`BOOTX64.EFI` 57,344 bytes, SHA-256 `9e81c7b5d24ac363…`, rebuilt at step 0 and matching `stage8/seed-record.md`; `cmp` silent). The mock `broker/molt.py --mock` sat behind the relay on `10.0.2.4:9999`. There were fourteen boots (boot 1 at 07:12, the rest from 21:53 to 22:40), one flash, and four watchdog resets with nobody touching the machine.

**The record in `history/`:**
- the chart, `2026-09-28-ring8a-hp-serial.log`;
- `parts.py --serial` on it, `2026-09-28-ring8a-hp-parts-serial.txt`: exit 0, `i8042 demoted f0668b687c68cab0 unhealthy`, 41 molt notes and 45 `S8:` lines;
- the mock's and the relay's output, `2026-09-28-ring8a-hp-mock.log` and `-relay.log` (the HP's identity is in the mock's);
- two photographs with their 1600-pixel copies: `2026-09-28-ring8a-hp-boot1-fetch.jpg` (the panel after the fetch of `good`) and `2026-09-28-ring8a-hp-hang-demoted.jpg` (the last `! molt`). EXIF stripped, pixels unchanged. The files carry the Anthropic content-credentials block (C2PA) that the upload adds; it holds no location.

| Boot | molt boot | What the chart shows |
|---|---|---|
| 1 | — | ring 7d's eighteen lines, `S7: notebook 277 notes`, no `S8:` line; `! molt` → `i8042 generic`; the first `! molt i8042` → `no answer from the broker` (the firewall, finding 8); after the owner's rule, `molt: i8042 shadow 4fe6beefc4bc57d0 3 1000 5000` |
| 2 | 1, `good` shadow | `S8: sha256 ok`, `S8: part i8042 shadow …`, `S8: watchdog tco 30 s`, the seed's `i8042:` pair; `S8: healthy 1`; the last count `718 21199 0` |
| 3 | 2, shadow | `S8: healthy 2`; `142 578 0` |
| 4 | 3, shadow | `S8: healthy 3`; the take journals `407 949 0`, then `molt: i8042 live 4fe6beefc4bc57d0` |
| 5 | 4, `good` live | **the part's pair**, `part: i8042 self-test ok` and `part: i8042 mouse reset ok`, and no `i8042:` line; a note and the arrow through the part; `S8: healthy 4` |
| 6 | — | Esc held at `hold Esc for the seed`: `molt: recovery owner`, `S8: recovery owner` 3.0 s after `S8: sha256 ok`; no part and no watchdog line; the seed's pair |
| 7 | 5, `good` live | Esc left nothing demoted; with the mock on `hang`, `! molt i8042` → `molt: i8042 shadow f0668b687c68cab0 1 100 100`; `S8: healthy 5` |
| 8 | 6, `hang` shadow | `S8: healthy 6`; the take → `molt: i8042 live f0668b687c68cab0` |
| 9 | 7, `hang` live | `hang 1` to `hang 6` typed; the HP stopped at `hang 7`'s `7` (a typo and a backspace in line 2 added 4 bytes, moving the part's 100th byte one line earlier than step 10 predicts); **reset by the watchdog** |
| 10 | 8, `hang` live | **no recovery line**: the evidence was gone. The health mark came 60 s after ready while the owner was idle (`S8: healthy 8`), so the boot counted healthy; the hang at line 8's first key; reset |
| 11 | 9, `hang` live | tried again, as the recovery table says with no evidence and no unhealthy run; `S8: healthy 9` while idle; powered off |
| 12 | 10, `hang` live | the A key held straight after the prompt; the hang before the health mark; reset |
| 13 | 11, `hang` live | the same; reset |
| 14 | — | **`molt: i8042 demoted f0668b687c68cab0 unhealthy`, `S8: recovery i8042 unhealthy`**, no part, the seed's `i8042:` pair; `! molt` → `i8042 demoted f0668b687c68cab0 unhealthy` |

**The ring's findings on the metal:**
1. **The Q77's TCO arms and resets the HP.** `S8: watchdog tco 30 s` on all eleven boots that loaded a part: `NO_REBOOT` cleared and read back clear. Never `tco locked`, never `none`, and no firmware screen after any of the four resets.
2. **The HP does not keep `SECOND_TO_STS` across the watchdog's reset** (A4's path). Four resets, and not one `recovery … watchdog` line. On this machine the recovery is the unhealthy path: two boots in a row that load a part and never reach the health mark. The twin keeps the bit (D1). The chart cannot say whether the HP's firmware or its reset clears it.
3. **The HP's deadline, as an upper bound (A2).** From `hang 7`'s stamp (22:30:00.657) to the next `S7: alive` (22:30:28.063): **27.4 s**. That interval holds the pause before line 8's `h`, the deadline, and the HP's whole way from its reset to GermOS's first line. So on the HP the hang, the reset and the POST together took less than 27.4 s, while the twin gives 30.2 s from the trigger to OVMF's first byte before any POST. The Q77 resets sooner than 2 × 25 × 0.6 s: either its tick is shorter than 0.6 s or its reset comes earlier in the count; the chart cannot tell which. The other readings: 30.9 s from `hang 6`'s stamp (it holds the typing of `hang 7`); 32.7 s and 35.1 s from `S7: keyboard ready` on the held-key boots (they hold the owner's reaction).
4. **The HP's identity:** `molt i8042 cpu 000306a9 pci 8086:1e47:04` (the i5-3570's Ivy Bridge signature; the Q77's LPC bridge, revision 04). Ring 8b's key: `molt i8042|abi3|cpu 000306a9 pci 8086:1e47:04`. The twin's is `8086:2918:02`.
5. **Shadow on a human:** 1,267 keyboard bytes (718, 142, 407) and 22,726 packets (21,199, 578, 949) over three shadow boots, **0 disagreements all day**, with capitals typed mid-line. About 19 minutes from boot 2's `ready` (21:53:48) to the take (22:13:02), the owner's chat with Cowork included. The discard limit was never met.
6. **`good`'s `init` on the HP's controller:** the part's pair on boots 5 and 7, and every key and packet through the part.
7. **Esc on a real keyboard**, held from the words on the screen, with its repeats: `S8: recovery owner`, and the HP's firmware menu never opened.
8. **Two procedure findings:**
   - **Omarchy's ufw drops the HP's connection to the relay.** The default is deny incoming. mlrig answered the ARP (`10.0.2.15 lladdr 6c:3b:e5:3b:86:45` in its neighbour table), but five 44-byte SYNs to 9999 were dropped and the guest said `no answer from the broker`. The owner added one rule, which stays for ring 8b: `sudo ufw allow in on eno2 from 10.0.2.15 to 10.0.2.4 port 9999 proto tcp comment germos-hp` (rule 5). HP-8a.md step 0 now has it.
   - **Step 10's second path needs the hang before the health mark.** A boot whose health mark comes while the human is idle is healthy even if it hangs later, and it ends the unhealthy run (boots 10 and 11). What worked: holding one key down straight after the prompt, whose repeats reach the part's 100th byte in about three seconds. HP-8a.md step 10 now says so.
9. **Cosmetic:** a raw `molt:` or `S8:` line can land inside an echoed line on the chart (`kakka poo molt: healthy 2`). `parts.py --serial` finds it anywhere in the line.

**The owner's word at the day, 28 September 2026:** hand-driven metal days do not scale. *"I am fed up of this testing while you or CC can do it with a link to HP … Can you imagine me doing this for every driver testing on GermOS on HP?"* He can power the HP on and type or move the mouse when asked, without new hardware, and wants the process easier. **Carried to the next gate, undecided:** keep the owner's hand for what only he can do (the trials, and the word that closes a ring). Cowork's options: without new hardware, procedures that read the chart for him and ask for one action at a time (held keys instead of typed lines); with cheap hardware, a smart plug, network boot from mlrig (no flash), a PS/2 emulator on a microcontroller, and a capture dongle, so a CC session can drive a whole day.

**The model note:** CC on Opus 5.5 at high effort for every item, 0 to 17 with 16b; Cowork on Opus 5.5 at high effort for the spec, the plan review, the reviews, test 5 and this closure. The ring: items 0 to 17 and 16b, one commit each; six plan amendments (A1–A6); Cowork's four points at item 16, built in before the review; the A6 review found no defects; one freeze opening, the project's tenth (`503b4e5`); **on the metal, no guest defect**.

## Ring 8t — trial two · opened 28 September 2026

**The ring.** Trial two, by `trials/spec-trial2.md` with its Amendment 1, and the plan `trials/plan-8t.md` (approved with Cowork's amendments A1–A5 and deviations 1–3 and 5–19; A1 withdraws deviation 4). The question is whether the painted box itself helps this human: layout **G** (B's zones, labels and targets drawn as plain text with `|` separators) against layout **B** (the boxes). The rule is R1 on a block score (the mean of the middle 16 of 20 cue-to-hit times plus 100 ms a miss), decided on the sign of S, the sum of the sixteen pair differences G − B: **B if S > 0, G if S <= 0** (A1); the verdict note carries S/16 truncated toward zero. Four sittings of a 10-cue warm-up and 8 blocks of 20 cues, one a boot; the times hidden until the verdict, on the strip and both panels (A2); the preference asked after each sitting. It runs on the generic `i8042` driver throughout. The guest code goes into `stage8/stage8.asm`; the loader stays frozen and untouched; the new binary becomes **seed 2** at item 13. Every human sitting is on the HP; the twin is the automated gate only.

**The HP's disk now, from the charts in `history/`:** 355 notes (ring 7c's 2; trial one's 275, ending `trial verdict A`; ring 8a's 41 `molt` notes and 37 typed notes, ending `molt i8042 demoted f0668b687c68cab0 unhealthy`). The home store holds the calculator and `part-i8042` (current `hang`, previous `good`). **A new seed changes nothing about the demoted part:** the state lives in the `molt` notes and the part in the home store, and neither names a seed, so seed 2 reads `demoted` as seed 1 did. It loads no part and never arms the watchdog; `S8: sha256 ok` is its one `S8:` line; `! trial 2` opens sitting 1.

**The shape:**
- items 0–7: the document (`trials/TRIALS2.md`), the tool (`trials/trials2.py`), the checker (`trials/checktrials2.py`) and the gate (`trials/test-trial2.sh`), red before the code;
- item 8: the probe (a private draft played by the synthetic human, every expected number read from the run);
- item 9: the freeze of the four files;
- item 10: the GLASS.md section, then a stop for the owner's `cat >>`;
- items 11–12: the guest;
- item 13: seed 2, this record, CLAUDE.md, README;
- item 14: `trials/HP-8t.md`, then a stop: green pending the oracle.

Every gate run is appended to `trials/out/gate-8t.log` (`8t test <n>: PASS|FAIL`, then `8t gate: PASS|FAIL`). The whole gate, with the 8a gate inside its test 4, runs at items 9, 11, 12 and 13, alone (A5: not at item 7, where the binary is still seed 1). No freeze opening is planned.

| Test | What | State |
|---|---|---|
| 1 | The documents: PE32+, the stick as 7c, TRIALS2.md cold, the worked examples, `--status` blind, the history builder | **green from item 8** |
| 2 | The rows and the refusals: G and B to the pixel, `! trial 2`'s five refusals, the widened prefix | written (item 5); red by design on the unset run constants until item 8, then on seed 1's missing `trial2:` lines until item 11 |
| 3 | Sittings predicted: disk V to verdict B, the HP's history (disk H, then W) to verdict G, the save rule, the times hidden, the offer, Enter, the boot line, the default read at boot | written (item 6); red by design on the unset run constants until item 8, then on seed 1's missing `trial2:` lines until item 12 |
| 4 | Nothing earlier disturbed: the strings, the argv, the payload table, the frozen `stage7/trials.py` unchanged, the 8a gate whole | **green from item 9** (the 8a gate green inside it on seed 1) |
| 5 | The owner's, on the HP, by `trials/HP-8t.md` | pending |

### Ring 8t — the build, item by item

**Item 0 (28 September 2026, `84321a2`):** the plan committed as `trials/plan-8t.md`; this section; the rows above; Cowork's two edits; `.gitignore` gains `trials/out/`.

**Item 1 (28 September 2026): the environment measured**, on seed 1 and one private copy, every file under `trials/out/probe8t/i1/` (`probe1.py`, `hook1.py`, `history1.py`, the log `probe1.txt`). No source changed.

| Measure | Reading |
|---|---|
| The host reads the notes partition while QEMU runs | A note typed on seed 1 was in the disk file, read by the frozen parsers, **0.016 s** after its Enter. So the save rule's check (the host read at the question and at `saved`) works. |
| FLUSH CACHE EXT through the loader's `ahci_cmd` | A private tree (`git archive HEAD`), with `stage8.asm` calling `ahci_cmd` with AL `0xEA`, EBX 0, DL 0 and a 512-byte buffer after each note's write. 57,344 bytes. Two notes typed: no `ERR:` line; both notes on the disk; the next boot `S7: notebook 2 notes`, no `ERR:`. `loader.asm` untouched. |
| The boot's walks on seed 1 (`-smp 4`, a 64 MB SATA disk formatted by its blank boot, notes written from the host) | 0 notes: `S7: alive` 1.19 s, the notebook line 1.38, ready 1.40, a key's echo 1.41 (the replay 0.01 s). **355 notes:** ready 1.55, echo 1.63 (replay 0.08 s). **1,250 notes:** notebook line 1.63, ready 1.92, echo 2.18 (replay 0.26 s). The walks cost about 0.4 ms a note in the twin. |
| The hook on `trials/out/` | Allowed: QEMU `-drive …file=trials/out/t8/…` (disk and stick), `qemu-img create` and `truncate` under `trials/out/`, `rm -rf trials/out/t8`. Denied: a `-drive` or `qemu-img` on `trials/` outside `out/`. `rm -rf trials` is still allowed, as nothing under `trials/` is frozen yet; item 9's payload cases pin it denied. |
| The HP's history as notes (the builder's first pass) | From the four ring 7d charts (`trial:` lines through `note_of_serial`) and the ring 8a chart: raw `molt:`, `S8:`, `part:`, `i8042:` and `S7: mouse ready` lines taken out of the echo stream wherever they land (one landed inside `kakka poo`, one inside `five in nu…`), backspaces applied, `!` and `?` lines skipped, a `molt:` note placed where its raw line starts and a typed note at its Enter. **Every checkpoint met:** 2, 93, 184, 277 (7d), then 277, 278, 288, 296, 311, 316, 318, 323, 332, 339, 349, 352, 353, 354 at the fourteen 8a boots, and **355 in all**, ending `molt i8042 demoted f0668b687c68cab0 unhealthy`: 2 ring 7c notes, 275 `trial` notes, 41 `molt` notes and **37 typed notes, every one recovered from its echo, no stand-in**. |

**Item 2 (28 September 2026): `trials/TRIALS2.md`**, 1,537 lines, in trial one's document's shape. It covers:
- the five sentences it supersedes (the reserved prefix widened to a first word `trial` or `trial` plus digits; the last verdict of either family as the default; the value 2 for G; the replay not drawing `trial2 ` notes; Enter on an empty line while trial two is in progress);
- layout G with the twin's columns;
- the design with the cue table (the plan's, verbatim) and the warm-up;
- a sitting step by step, the score, the verdict on the sign of S (A1), Amendment 1 (the offer, Enter, `saved` after the flush with A4's arguments, the boot line);
- the notes, the serial lines, the strip, and `trial_number` at `0x340`;
- worked examples A (184 notes of one scripted sitting), B (verdict B, S 1051, mean 65), C (S 0 gives G 0; 15 gives B 0; −15 gives G 0), D (an abort and a question left unanswered, verdict G, S −863, mean −53), E (both families on one notebook) and F (a chart and its blind read);
- the Python block.

**One decision taken in writing it:** the verdict note is journaled straight after the fourth `done` note, before the question, and shown only after the answer. So a machine powered off at the fourth sitting's question still holds its verdict. The examples were computed by the block itself, and example E was checked against the frozen `stage7/trials.py`: its report is identical with and without the trial-two and molt notes.

**Item 3 (28 September 2026): `trials/trials2.py`**, in `stage7/trials.py`'s shape. It execs the document's Python block, with the frozen `parse_obs_7d` and `mode_word_7d` loaded by path from `stage7/trials.py`. It compares the Python with the prose cue table, the orders sentence, the obs row and the twin's three G rows. Its modes are `--example [--doc PATH]`, `--disk`, `--serial` and `--status`.

**Proven on the host, no boot** (`trials/out/probe8t/i3/proof3.py`, 8 of 8):
- `--example` reproduces A to F, and a block score altered by one is refused with the block named;
- a document whose block 3 cue row has a word twice running, in both copies, is refused with the constraint named;
- the prose cue table changed alone is refused;
- a G separator column changed in the prose is refused with both columns shown;
- `--disk` on a formatted disk with two ordinary notes prints `no sittings`;
- `--disk` on example A's notes and `--serial` on its chart print the same report, with the table and `boot line: trial2: due sitting 2`;
- `--status` on example F's chart prints the blind read;
- after a `trial2: verdict` line, `--status` adds `verdict line present` and the report.

**Item 4 (28 September 2026): `trials/test-trial2.sh`, the log, the build and test 1; `trials/checktrials2.py --document`.**

**The gate** is 8a's skeleton: a header `=== ring 8t gate <iso> commit <rev>[+uncommitted] ===` in `trials/out/gate-8t.log`, the `tee`, the port refusals, the build (`stage8/mkimage.sh`, `stage8/mkstick.py`) and the PE32+ checks. At the end come one `8t test <n>: PASS|FAIL - …` line per test and the last line `8t gate: PASS|FAIL`; a busy port gives `8t gate: FAIL` with no test run.

**The checker's test 1:**
- the stick as 7c's frozen `check_stick` sees it, with stage8's paths;
- `trials2.py --example`;
- **the HP's history**: 355 notes from the five charts, each pinned by its SHA-256, meeting every `S7: notebook` checkpoint, with the counts (275, 41, 37, 2) and the last note from item 1's run, leaving `i8042` demoted by PARTS.md's own `state_of`;
- **the HP's disk**, formatted from the host by DISK.md (`metal.build_gpt`), NOTEBOOK.md and HOME.md and written by the new home writer (the calculator a stand-in, `stage6/echo.bin`; `part-i8042` with the committed `hang` current and `good` previous, each pinned by its SHA-256). It is read back:
  - the notes and HOME.md's parse;
  - `stage8/parts.py --disk`: `i8042 demoted f0668b687c68cab0 unhealthy`, 1 app and 1 part;
  - `stage7/trials.py --disk` byte for byte equal to its `--serial` on the 7d charts joined, `verdict A: sittings [1, 2, 3], wins for B 8 of 12 (10 needed), misses A 4 B 0`;
  - `trials2.py --disk`: `no sittings`, `boot line: none`;
- `G_ROWS_RUN` and `TRIAL_NUMBER_AT_RUN` equal to the rule. These two are `UNSET` until item 8, so test 1 is red on them alone, by design.

**Item 5 (28 September 2026): `checktrials2.py --rows`, test 2.**

**The twin session, `Boot`:** ring 7c's QEMU command through `checkmetal.qemu_argv` on a copy of stage8's stick under `trials/out/t8/`, the guest's ready line awaited, the monitor and the serial file, the PS/2 mouse through the monitor with ring 6c's pointer model. The page is read by TRIALS2.md's `parse_obs_8t` through `0x368`, with the three words it keeps zero.

**The synthetic human, `Boot.play`:** ring 7d's `Human` transcribed for `trial2:` lines, the warm-up, the rests, Esc, the question, the key and the `saved` line, with hooks at the start, before any cue, at a rest, at the question and at `saved`.

**The judgements:**
- `compare_notes`: 7d's, over scores;
- `check_layout_g`: the surface is `grouped_cells`, no bit 7, and the screen matches cell for cell by 7d's frozen `check_choices_bytes`;
- `g_columns_of`: the spans and separators read back from a surface;
- `hidden_times`: A2's token check over the strip and both panels, the rows of other notes' replay passed over. Every script's times and scores are kept between 100 and 999 ms (`check_script_range`), so no zero-padded counter of the strip can read as one.

**Test 2's four disks:**
- **R1**, blank: no boot line and no offer; the warm-up's G row and `trial2 G 0/8`; its B row at cue 6; block 1; Esc in block 2 and the `saved` line; `! trial 2` and an empty Enter each refused `one sitting a boot`; `trial2 x`, `trial` and `trial3 y` refused; `trials are fun` journaled; the echo.
- **C**, example D's notes, verdict G: the concluded line, no offer, no trial-two note replayed, `layout_default` 2 and the two-item prompt row in G; the refusal; an empty Enter plain; a click on `! grow` typing `!`; a click on `|` only counted.
- **S**, good in shadow, example A's sitting and the calculator: the `S8:` and `molt:` lines, the due line and the offer; `an app is running`, then the part refusal, each by `! trial 2` and by an empty Enter.
- **L**, good live: the part's pair and the part refusal both ways.

**Run once on seed 1**, with provisional values given by `--set` for that run only (READY_LIMIT_S 60, SETTLE_S 1, OFFSET_MS 40, OFFSET_FIRST_MS −8, HIT_WINDOW_MS 60, none of them kept). Red for the right reason: R1 `no 'trial2: sitting 1' line`; C, S and L `no answer from the broker` where the refusals belong, no boot line, no offer, `layout_default` 0 and the prompt row A. One checker fault was found and fixed before this commit: `check_boot_lines` wants `S7: notebook <n> notes`. **In the gate, test 2 is red on the unset constants**, named (`trials/out/gate-8t.log`).

**Item 6 (29 September 2026): `checktrials2.py --sittings`, test 3.**

**The scripts**, each a sitting's delays in ms, kept between 100 and 999 ms and asserted so:
- disk V: B faster by about 130 ms a cue;
- H and W: G faster by the same;
- a check that each script's predicted S clears 16 × the slack, so the verdict cannot turn on the pointer's own latency.

**Each sitting's boot** (`play_boot`) checks:
- the boot line and the offer (or their absence);
- A2 at the boot, at the rests after the warm-up and block 4, and at the question and at `saved` until a verdict exists;
- the page at every rest;
- **the save rule**, by reading the disk file from the host: at the question, the done note is there, no prefer note is, and no `saved` line shows; at `saved`, the prefer note is there;
- the notes against the script (`compare_notes`) and serial equal to the notes;
- one `S7: alive` per boot (no reset) and the wall time under `SITTING_S`;
- the end lines;
- the app panel empty before the verdict.

**The verdict** (`check_verdict`): the note equal to the rule's recomputation from the recorded notes, the layout the script's, the mean within the slack of the script's, the serial line, the four tables in the app panel, `layout_default` and mode 0.

**The boot after a verdict** (`boot_after`): the concluded line, no offer, the default read and drawn (B's boxes, or G's row), an empty Enter plain, `! trial 2` refused, a click on `! grow` typing `!`, a click on the gap only counted.

**The disks:**
- **Disk V:** four sittings (the first typed, then Enter at the offer), verdict B, V5. Then `trials2.py --disk` against the panel, and `--status` on V1–V3's charts showing no time or score, then on V1–V5 adding the report.
- **Disk H:** the HP's history and home from item 4's writer. H1's boot is 18 lines with 355 notes and one home app; `S8: sha256 ok` is the only `S8:`/`molt:` line; no boot line, no offer, no Esc window; `layout_default` 0 and the three-item row in A; `! molt` shows `i8042 demoted f0668b687c68cab0 unhealthy`; `! trial` answers `trial concluded`; then `! trial 2` and sitting 1. The frozen `stage7/trials.py --disk` and `stage8/parts.py --disk` print the same after it.
- **Disk W:** H with sittings 2 and 3 appended from the host. W1 is sitting 4, started by Enter and aborted in block 3, then an empty Enter giving `one sitting a boot`. W2 is sitting 5 to the verdict G over sittings 1, 2, 3 and 5. W3 has a full trial on the disk: G at the prompt with the three-item row, and the frozen tools unchanged again.

**Run once on seed 1** with provisional `--set` values, none kept. V1 and H1 failed as expected: `no 'trial2: sitting 1' line`. **Every check of H1's boot passed on seed 1**: the eighteen lines with `S7: notebook 355 notes`, `S8: sha256 ok` alone, no watchdog, trial one's A row with `! calculator`, `! molt` and `! trial` as above. So the twin disk behaves as the HP's does before any guest change. **In the gate, test 3 is red on the unset constants**, named.

**Item 7 (29 September 2026): `checktrials2.py --cage` and test 4.**
- **(a)**, in the harness: its own cage, machine, display, stick and disk strings (under `trials/out/t8/`), the scratch and the log under `trials/out/`, and no QEMU line naming `esp.img`.
- **(b):** the checker's own QEMU command, `checkmetal.qemu_argv` itself, through ring 7c's frozen `check_argv_7c`, with `checkmetal.OUT` and `STICK` pointed at this ring's for that call only. Eight flags that check does not inspect are refused. Plus `-smp 4`, the files under `trials/out/t8/`, and the frozen modules' ports and display.
- **(c):** `payloads.py` whole, 0 wrong, then the spot checks as data: the four frozen paths denied Write and Edit, relative and absolute, and five mutation spellings each, and readable; `trials/` under the owner's directory rule (nine spellings); the nine files that stay writable; twenty-two shapes of running and building allowed.
- **(d):** trial one's 277 notes from the HP's history and worked example A's trial-two sitting on one host-formatted disk. The frozen `stage7/trials.py --disk` prints its report on the 7d charts, byte for byte.
- **(e)**, in the harness: `./stage8/test-8a.sh`.

**`--cage` run at this commit:**
- (b) passes;
- (c)'s payload table passes: **2,064 cases, 1,409 denied, 655 allowed, 0 wrong**;
- (c)'s ring 8t spot checks fail, because nothing is frozen until item 9 — **red by design**;
- (d) passes: `verdict A: sittings [1, 2, 3], wins for B 8 of 12 (10 needed), misses A 4 B 0`.

The harness passes `bash -n`. **By A5, (e) — the 8a gate, about 43 min — is not run at this item:** the binary is seed 1, unchanged since ring 8a closed. Its first run is item 9's.

**Item 8 (29 September 2026): THE PROBE.**

**The draft.** The guest code of items 11 and 12 was written as `trials/out/probe8t/i8/patch8t.py`, a script of exact edits to `stage8.asm`:
- part A is the sitting;
- part B is Amendment 1 and the replay rule;
- the two new sections are `t2_sitting.asm` and `t2_boot.asm`.

It was applied to a `git archive HEAD` copy of the tree under `trials/out/probe8t/i8/tree/` and built there: **61,440 bytes**, `loader.asm` untouched. Its EFI and stick were copied into the scratch `stage8/out/` for the run. **At the commit `stage8/out/` holds seed 1 again** (`9e81c7b5d24ac363`, rebuilt from the repository's source), and item 11 applies the same script's part A to `stage8/stage8.asm`.

**Test 2 on the draft: green.** R1, C, S and L exactly as the checker asks; the echo; every refusal by `! trial 2` and by an empty Enter.

**Test 3 on the draft: green, 25.4 min.**
- Disk V: four sittings; the verdict **B 142** over sittings 1–4; V5 in B.
- Disk H: the HP's history, 355 notes; `S8: sha256 ok` alone; no part, no watchdog, no reset through a 195 s sitting; the frozen `stage7/trials.py` and `parts.py` unchanged.
- Disk W: sitting 4 aborted in block 3; sitting 5 to the verdict **G −134** over sittings 1, 2, 3 and 5.
- W3: a full trial on the disk, **1,141 notes, ready 1.89 s after QEMU's start**; the HP's three-item row in G; trial one's verdict A still printed by the frozen tool.

**Test 1 green** with the constants set.

**The `no mouse` probe** (`nomouse.py`): a second private build with the mouse's reset answer forced to nothing. `! trial 2` on a blank disk gives `no mouse`, `errors` 1, `mouse_id` 0, the journal empty, no `trial2:` line.

**The numbers, written into `checktrials2.py` with the date:**

| Constant | Value | From |
|---|---|---|
| `G_ROWS_RUN` | four items: labels 12–16, 41–46, 71–77, 101–108, `|` at 29, 59, 89; two: 27–31, 87–92, `|` 59; three: 17–21, 56–61, 94–105, `|` 39, 79 | read back from the choices surface at R1, C1 and W3; equal to the rule (test 1) |
| `TRIAL_NUMBER_AT_RUN` | `0x340` | R1's page read at the sitting's start: 2 there, `0x348`–`0x358` zero |
| `OFFSET_MS` | 39 | 1,048 cues timed from a hit's line: +31 to +49 |
| `OFFSET_FIRST_MS` | −12 | 58 cues timed from a sitting or block line |
| `HIT_WINDOW_MS` | 60 | CC's own; every hit's residual against the rule was within 15 ms, every block score within 3 ms of the script's (the slack is 30) |
| `READY_LIMIT_S` | 60 | ready 1.41–1.81 s, 4.50 s with a part's Esc window; 7c's window kept |
| `READY_FULL_S` | 20 | W3, 1,141 notes: 1.89 s |
| `SETTLE_S` | 1.0 | the replay's end 0.26 s at 1,250 notes (item 1) |
| `SITTING_S` | 300 | a sitting's boot 186.8–195.0 s |

**The note counts** (by rule, and read from the run): 184, 182, 181, 183 (+ the verdict note) on V; 182 at H1; 58 for W1's abort; 183 at W2.

**Findings of the probe, fixed before the freeze:**
1. **In the guest and the document — a live part owns the mouse.** With good live, the seed's `mouse_id` stays 0 until the part's first packet, so `! trial 2` answered `no mouse` and the part refusal never had its turn. `no mouse` now does not apply while a part is live in the slot this boot. TRIALS2.md's refusal row says so (its one change since item 2; `--example` green).
2. **The checker — the echo.** Stripping the `trial2:` lines collapsed an empty Enter's CRLF. The lines are now removed with their own CRLF, and nothing is collapsed.
3. **The checker — hooks inside a cue delay its press.** R1's cues at the warm-up's start and at cue 6 are untimed, and the cue-6 read waits until cue 6 shows.
4. **The checker — A2 was naive.** The mode word `trial2 …` looks like a note, and the strip's `n` counter (and the boot log's `S7: notebook 366 notes`) can read as a three-digit time. The strip is now checked against GLASS.md's template shape with a legal mode word, since no counter field can carry a time. The boot log's rows and the counts row are passed over in the conversation.
5. **The checker — the rest after the warm-up** starts at the last hit's pause end, and the hook now waits for it.
6. **The checker — the `mode` read at the `saved` instant** raced the close, and is dropped there. The boot after the verdict checks mode 0.
7. **The checker — `parts.py --disk` prints the note count.** It is compared with the count masked.
8. **The checker — block 1's first cue** is timed from the warm-up's last hit line, so it takes `OFFSET_MS`. Cues timed from a sitting or block line take `OFFSET_FIRST_MS`.

**Item 9 (29 September 2026): THE FREEZE.**
- **`PROTECTED`** gains `trials/TRIALS2.md`, `trials/trials2.py`, `trials/checktrials2.py` and `trials/test-trial2.sh`.
- **`payloads.py`** gains `FROZEN_8T`: `freeze_cases`, the document, tool, checker and gate each denied Write or Edit, `sed -i` on a run constant and on the slack denied, and python writing the tool denied. The owner's directory rule covers `trials/` (`rm -rf trials`, `mv trials`, a glob over `trials/*.py`, `git rm -r trials`). The guest, the owner's procedure, the section, the plan, the spec's amendments and the draft under `out/` stay writable; running the gate, the checker and the blind read is allowed. A trial-two boot under `trials/out/` is allowed, and a disk under `trials/` but outside `out/` denied. **The table: 2,164 cases, 1,482 denied, 682 allowed, 0 wrong.** Immediacy shown live: an Edit of `checktrials2.py`'s slack was denied.
- **Before the freeze, the next planned states:** no test of this ring reads the seed record or the build's size, and test 1 passed on the 61,440-byte draft at item 8. Ring 8a's test 1, which parses the record, meets seed 2 at item 13.

**The gate whole (01:05, 45.8 min, alone):**
- test 1 PASS;
- tests 2 and 3 FAIL by design, every problem seed 1's: no `trial2:` line, `no answer from the broker` where a refusal belongs, no boot line, no offer, no G row;
- **test 4 PASS**: (a), (b), (c) with 2,164 cases, and (d); and (e) `./stage8/test-8a.sh` green — its tests 1–4, 7d's checks on this binary through the seams, and 7d's gate with 7c, 7b and 7a inside it.

**Item 10 (29 September 2026): `trials/glass-8t-section.md`**, for the owner's `cat >>` onto `stage6/GLASS.md`, in the 7d section's manner. It states:
- that everything above it stands byte for byte;
- the five sentences TRIALS2.md supersedes;
- `trial_number` at `0x340`;
- the mode word `trial2 <L> <b>/8`;
- layout G's cells and its click rule;
- `! trial 2` and its five refusals, with `no mouse` as TRIALS2.md now words it (not while a part is live);
- the widened prefix, Enter while trial two is in progress, and the replay rule;
- everything else by pointer to `trials/TRIALS2.md`.

**The session stops here** until the owner says the section is in.

**Item 11 (29 September 2026): the sitting into `stage8/stage8.asm`.** Part A of item 8's `patch8t.py` was applied to the repository's source, exactly as the probe ran it. It holds:
- `! trial 2` and `trial2_start` with the five refusals (`no mouse` not while a part is live);
- the widened reserved prefix;
- `trial_kind` and `trial_number`, and the mode word's `trial2` branch;
- the warm-up and its two layouts, the 20-cue blocks, the 5 s rests and the score;
- layout G through `row_to_boxes`' style bytes, for trial blocks and for `layout_default` 2;
- the `trial2` notes and their `trial2:` lines;
- the question and the prefer note, the counts, the verdict on the sign of S with the four tables, the abort;
- the flush through `ahci_cmd` and the `saved` line;
- `journal_scan2`, which also reads the i8042 slot's state from its molt notes.

The build is 61,440 bytes, `loader.asm` untouched.

**Probed first** (`trials/out/probe8t/i11/smp.py`): R1's script (the warm-up, block 1, Esc in block 2) at `-smp 2` and `8`. Each gave 36 notes as the checker's `compare_notes` wants them, `aborted 2`, and the `saved` line.

**The gate whole, alone, 52.7 min:**
- tests 1 and 4 PASS; test 4 holds ring 8a's whole gate, green on this binary, with 7d's checks through the seams in its test 2 (`! trial` still trial one's) and 7d's gate with 7c, 7b and 7a inside its test 4;
- **R1, V1 and H1 pass** — the sitting, both rows, the notes, the save rule, A2, the HP's disk;
- tests 2 and 3 fail only on part B's ground: an empty Enter not yet `! trial 2`, no boot line, no offer, the replay drawing `trial2` notes, and the trial-two verdict not read at boot (disk C's `layout_default` 0).

The plan expected test 2 green here. It is not, because R1, S and L each press an empty Enter, which is part B's. That is said in the commit.

**Carried** from ring 8a's closure: the IDT, GDT and page tables writable; the rules proven only by probe; PARTS.md's stated limit; Stage 7's caveats; the GPS history postponed; `stage8/out/probe8a/` kept. On mlrig, the second address on `eno2` and ufw rule 5 stay for ring 8b; trial two needs neither.

## Next action

**Ring 8t, trial two, OPENED (28 September 2026).** The plan `trials/plan-8t.md` is approved with Cowork's five amendments. Items 1 to 11 are done (the ring 8t section); the GLASS.md section is in by the owner's hand. **Next: item 12**, part B of item 8's draft into `stage8/stage8.asm` (the offer, Enter, the boot line, the replay rule, the trial-two verdict at boot), with the gate whole: all four tests green. Then items 13–14 as the plan says, one commit each. The session stops at item 10 for the owner's `cat >>` of the GLASS.md section, and at item 14, green pending the oracle.

Earlier — **Ring 8a is CLOSED (28 September 2026), by the owner's word after test 5 on the HP** (the record is under ring 8a's closure section). **Next: ring 8t, trial two**, by `trials/spec-trial2.md` (approved by the owner on 27 September 2026, `beef2da`): the choices-row N-of-1 re-run, every human sitting on the HP with the PS/2 mouse and none in QEMU, in its own sessions for Cowork and CC; then ring 8b. **Before 8t's kickoff, the owner's question of 28 September:** how much of the HP's days can move off his hands (the options are in the closure section). **Left in place on mlrig for 8b:** the second address `10.0.2.4/24` on `eno2` and ufw rule 5 (`germos-hp`). The GPS history rewrite stays postponed.

Earlier — **Ring 8a was GREEN PENDING THE ORACLE (item 17, 27 September 2026).**
All four automated tests pass on `./stage8/test-8a.sh`, with the 7d, 7c,
7b and 7a gates green inside its test 4. Stages 0–5 and the three ring 6
gates are green on their own binaries. The seed is seed 1
(`stage8/seed-record.md`: `fc64a07`, 57,344 bytes, `9e81c7b5d24ac363…`).
Every item of the plan, 0 to 17, is done, one commit each. Item 17 took
the project's tenth freeze opening by the owner's hand (`503b4e5`,
`parts.py`'s `current_seed` check), with the gate re-run whole on it.

**Cowork has reviewed `stage8/HP-8a.md`** (28 September 2026, from
`422f7a7`): sound, and its three additions are in. **The document is
ready for the owner's day.**

**Test 5 is Wajira's: the HP's day, by `stage8/HP-8a.md`.** One flash,
three terminals, nine boots or so, each boot's work run to its health
mark before anything is read:
- boot 1: ring 7d's eighteen lines with no `S8:` line, then the fetch of `good`;
- boots 2–4: shadow on real typing and a real mouse, to 3 / 1,000 / 5,000 with 0 disagreements, then the take;
- boot 5: `good` live;
- boot 6: Esc at `hold Esc for the seed`, then `S8: recovery owner`;
- the mock changed to `hang` with the HP off;
- boot 7: the fetch of `hang`;
- boot 8: `hang` in shadow, then the take;
- boot 9: `hang` live. The HP stops, and resets itself about 30 s later.

**What the HP's day records as findings:**
- whether the HP kept the evidence bit (the recovery line says `watchdog` or `unhealthy`, A4);
- the HP's deadline, read from the chart's stamps (A2);
- any `tco locked`, `none`, or a `tco 30 s` with no reset (`TCO_LOCK`, Cowork's note);
- the HP's identity in the mock's log;
- how long a human takes to earn the threshold.

His word closes the ring. **At the closure:** the chart and the
photographs into `history/`, this record, README, and the owner's
`git push`.

**Before the day, on Omarchy:** mlrig's LAN port no longer carries
`10.0.2.4/24` (the OS changed on 22 September, and ring 7d needed no
wire), so METAL.md step 5 adds it again (HP-8a.md step 0). The serial
group is `uucp`.

**The criteria are frozen, the loader with them since 16b:** a frozen
file that turns out wrong is never edited. Stop, write the diff unapplied
under `stage8/out/`, and wait for the owner's hand. **Carried:** the
probes in `stage8/out/probe8a/i16/` and the draft in
`stage8/out/probe8a/draft/`. Never wipe `stage8/out/probe8a/`.

Earlier — **Ring 8a, item 17** was the paperwork and the owner's
procedure (the record is under ring 8a's item 17).

Earlier — **Ring 7d is CLOSED (25 September 2026), and with it every ring of Stage
7's order. Next: Stage 8 — the molt**, by the owner's order of 22
September 2026 (the trials first, the molt after; sound and the full
screen stay on the list for a later gate). A fresh session for Cowork
and a fresh session for CC, starting as every stage has: read
`ai-os-foundation.md` (Stage 8), this file and `stage7/spec.md`; re-check
the subscription policy at the gate; the spec and then the plan written
and approved at the plan gate before any code; the acceptance tests
before the code they judge. **CC's implementer moves to Opus 5.5 from
that kickoff** (the owner's decision of 23 September 2026, not
mid-ring). **What the next session inherits:** the ring 7d binary,
45,056 bytes (`stage7/out/BOOTX64.EFI`; the stick as flashed for the
trial); the HP's disk with GermOS's table, 277 notes ending in `trial
verdict A`, and the calculator; the items carried under ring 7d's
closure.

Earlier — **Ring 7d: the three trial sittings on the HP — one sitting a session.**
Pre-registered by the owner on 24 September 2026, before any data: the
trial is the HP's notebook alone; the twin's sitting of that day was the
rehearsal and enters nothing. The HP's disk holds GermOS's table, the note
`hello metal` and the calculator, and no `trial` note — so the HP's
sittings are numbered 1, 2 and 3 there, in the orders `ABBA BAAB`, `BAAB
ABBA`, `ABBA BAAB`, and the guest gives the verdict at the end of its third
`done` sitting. The binary is the ring's (45,056 bytes); the stick is
flashed **once**, before sitting 1, and not again until the ring closes.

**What the HP's day needs, and what it does not.** The trial sends nothing
over the wire, so there is **no broker, no relay and no second address on
mlrig** — but the HP's Ethernet stays in the home switch, because the boot
waits for the link and halts at `ERR: nic link did not come up within 10 s`
without it. The chart stays: `trial:` lines on serial are the record mlrig
keeps, since the HP's disk cannot be read from mlrig. **One terminal.**

**Sitting 1 (the first HP session) — DONE 24 September 2026, passed by the owner's word** (the record is under ring 7d's test 5).

1. **Once, on Omarchy:** the serial port's group is `uucp` on Arch, not
   Ubuntu's `dialout` (METAL.md step 0): `sudo usermod -aG uucp $USER`, then
   log out and in. Check the null-modem cable, the PS/2 keyboard and mouse,
   the monitor and the Ethernet are still on the HP.
2. **The flash**, by METAL.md steps 1–3 as they stand (`lsblk`, the by-id
   path, unmount, `wipefs`, `dd`, `cmp` saying nothing, `power-off`), of
   `stage7/out/stick.img` as built — never `stick.twin.img`.
3. **The chart**, started before power-on:
   `python3 broker/chart.py /dev/ttyUSB0 stage7/out/hp-sitting1.log`.
4. **Power on.** Eighteen lines with `S7: notebook 1 notes` and `S7: home 1
   apps`, the `i8042:` pair, `S7: keyboard ready`.
5. **`! trial`**; the strip says `trial A 1/8`; eighty clicks at a normal
   pace; no keys (Esc aborts). **Watch the arrow over and after a B box:
   the plain arrow, not a dark arrow on a light block.**
6. **Photograph the table** in the app panel; Ctrl-C the chart; then
   `python3 stage7/trials.py --serial stage7/out/hp-sitting1.log` prints the
   same table. Power off.

**Sitting 2 (the second HP session) — DONE 24 September 2026, passed by the owner's word** (the record is under ring 7d's test 5).

**Sitting 3 (the third HP session) — DONE 24 September 2026, passed by the owner's word; verdict A, the owner's word on it 25 September 2026; the verdict boot answered `trial concluded`** (the record is under ring 7d's test 5). **Next: the ring's closure — README, the closure record, the owner's push.**

**Sittings 2 and 3 (one session each, a later day or at least a later
boot):** steps 3 to 6 only — no flash — with the log named
`hp-sitting2.log`, `hp-sitting3.log`. Sitting 2 opens `trial: sitting 2
BAAB ABBA`, sitting 3 `ABBA BAAB`. At sitting 3's `done` the panel's last
row is `verdict A` or `verdict B`, and `trial: verdict …` is on the chart;
then **one more boot**: the row at the prompt is in the verdict's layout
with no trial running (the Done-when: the default follows the verdict), and
`! trial` answers `trial concluded`. The three charts together go to
`trials.py --serial` for the verdict from the host.

**The rules that stay pre-registered:** one sitting a boot; an aborted
sitting counts as started (the next number and its order move on) and its
blocks stand outside the verdict — the verdict is over the first three
`done` sittings, so an abort costs one more session, never a redo; nothing
is changed on the stick between sittings; the owner's word on each sitting,
the verdict on the third closes the ring. **At the closure:** the three
charts and photographs into `history/`, this record, README, and the
owner's `git push`.

Earlier — **Ring 7d, the trials, is GREEN PENDING THE ORACLE — 23 September 2026.**
All four automated tests pass on `./stage7/test-7d.sh` (21 min; every run in
`stage7/out/gate-7d.log`): the document parsed cold with its worked
examples; the refusal while an app runs, the sitting's start, layout A's
row to the pixel, the boxes in the surface and on the screen; the
synthetic human's three sittings to `trial verdict B` with every block
median inside the spec's ±30 ms, the abort, the default read at boot, the
reserved prefix refused, a click on a box; the freeze, the payload table
(1678 cases, 0 wrong) and the 7c, 7b and 7a gates green inside test 4 on
the same binary (45,056 bytes). Items 0–12, one commit each; the four
files frozen at item 8; the GLASS.md section by the owner's hand at item
9; one probe binary at item 7 with every timing number read from its run;
no freeze opening. **Test 5 is Wajira's: one sitting a session, three
sittings, his word on the third closes the ring.** Sitting 1 in the
windowed twin — three terminals at the repo root, the 7c shape below,
then `! trial` at the prompt with the mouse grabbed: eighty clicks and
seven rests, about four minutes; the table appears in the app panel at
the end, and `python3 stage7/trials.py --disk stage7/out/disk.img` prints
it from the disk. Sittings 2 and 3 on the HP by `stage7/METAL.md`'s day:
one flash of the ring's stick (`stage7/out/stick.img` as built at item
11), then boots only — the HP's disk already holds a note and the
calculator, and the sitting number counts from the notebook, so sitting
1 there would be sitting 1 of that disk's trial; **the twin's sitting and
the HP's are two notebooks, and the verdict on each is over its own three
sittings** — the owner decides which record is the trial (deviation 7:
the sitting line does not say where it ran). With the chart running,
`python3 stage7/trials.py --serial stage7/out/metal.log` prints a sitting
from the serial lines without reading the disk. Earlier — **Ring 7c and Stage 7 are CLOSED — 18 September 2026, by the owner's
word, after test 5 passed on the HP, all eight steps.** Nothing is owed
on Stage 7. **Next: the N-of-1 trials ring, per `stage7/spec.md`'s order
("The N-of-1 trials ring comes after the metal") — a fresh session for
Cowork and a fresh session for CC**, starting as every ring has: read
`ai-os-foundation.md`, this file and `stage7/spec.md`; the spec and then
the plan are written and approved at the plan gate before any code; the
acceptance tests before the code they judge; the model and the effort are
the owner's decision at that gate. Patient one stays the HP Compaq Elite
8300; patient two, later, is the ThinkStation P330 (the spec's words).
**What the next session inherits:** the binary that passed test 5 is item
21's, 40,960 bytes (`stage7/out/BOOTX64.EFI`, the stick
`stage7/out/stick.img` as flashed); the HP's disk holds GermOS's table,
one note (`hello metal`) and one app (calculator); `stage7/METAL.md` is
the HP's day as it was actually run, the flash block and the null-modem
finding included; `broker/probe.py` and item 20's monitor stay in the
binary for the next device that will not speak; mlrig's LAN port still
carries `10.0.2.4/24` (METAL.md's last section says how to remove it).
**Caveats carried out of Stage 7:** the nineteen-line first boot with
`S7: gpt written` was never *watched* on the metal (the 15th's blind boot
did it unread); after a PHY reset through the monitor STATUS read speed
10 where it read 1000 before — not chased, and `e1k_attach` issues no PHY
reset; TIPG is written as `0x00602008` where this chip's default is
`0x00902008` — it sends either way; `WIRE.md` still says every named
error halts, where since item 20 the transmit timeout enters the monitor
(a freeze opening only if the owner wants the document to say so). The
evidence is in `history/` (the closure's paragraph above lists it).

To click through the twin of the HP again at any time — three terminals
at the repo root: `python3 broker/wire.py`, `python3 broker/relay.py
--bind 127.0.0.1 --port 9997`, and the machine booted from a copy of the
stick (for a blank disk remove `stage7/out/disk.img` first):

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

OVMF says it is loading from the USB drive; nineteen lines with `S7: disk
port 1 …`, then `i8042: self-test ok`, `i8042: mouse reset ok`, `S7:
keyboard ready`. Earlier — **Ring 7b is closed.** Next: **ring 7c, the metal** The HP's day: three
terminals at the repo root, `python3 broker/wire.py`, `python3
broker/relay.py`, and the serial reader on the adapter's port, all written
out in `stage7/METAL.md` at item 12.

Earlier — **Ring 7b is closed.** Next: **ring 7c, the metal** — the EDID guard, the i8042 cold init, the stick, the flash by the owner's hand, every stage re-proven on the HP — per `stage7/spec.md`, a fresh Cowork session and a fresh CC session, **medium effort by the spec's decision**. Carry into 7c's handover:

- **`CAP.SSS` and `PxCMD.SUD`:** the HP's firmware may leave staggered spin-up set, so a port may need `PxCMD.SUD` before its disk appears (ring 7a's carried note; no code yet).
- **The ports as A5 settled them:** in the twin the relay is `python3 broker/relay.py --bind 127.0.0.1 --port 9997` and every 7c QEMU line's `guestfwd` names 9997, not the spec's 9998; on the HP's day the relay is `python3 broker/relay.py` with no flags (its defaults `10.0.2.4` and 9999) beside the broker on `127.0.0.1:9999`, and `METAL.md` step 5 says so; **the spec's ring 7c twin command is to be corrected at the 7c gate.**
- **One item for the unfrozen relay:** it serves one connection at a time, so a guest that dies mid-connection without closing holds it until that socket ends; a close of the guest side once the broker side has finished, after a short grace, frees it.

To click through ring 7b again at any time — three terminals at the repo root: the broker `python3 broker/wire.py`, the relay `python3 broker/relay.py --bind 127.0.0.1 --port 9997`, and the machine (for a blank disk remove `stage7/out/disk.img` first; a disk worth keeping is copied to `stage7/out/disk.oracle.img`, a name the harness never touches):

```
rm -f stage7/out/disk.img; truncate -s 64M stage7/out/disk.img
qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage7/out/esp.img \
  -drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9997' \
  -device e1000e,netdev=n0,mac=6c:3b:e5:3b:86:45 -serial stdio
```

`S7: nic 6c:3b:e5:3b:86:45` then `S7: link up`; `? ping` logs one connection in the relay's terminal and puts `w 001` on the strip; `! make me a clock` is written by the real backend, rehearsed in the wire twin, and ticks in its panel. Earlier — **Ring 7a is closed.** Next: **ring 7b, the wire** — the e1000e driver rehearsed on QEMU's `e1000e` with the HP's MAC, `broker/relay.py` in front of the frozen broker, the cage on the relay — per `stage7/spec.md`, a fresh Cowork session and a fresh CC session, Fable 5.1 at high effort by the spec's decision. Carry into 7b's handover: the HP's firmware may leave `CAP.SSS` set, so a port may need `PxCMD.SUD` before its disk appears (ring 7c). To click through ring 7a again at any time — two terminals at the repo root. The broker (it answers
questions, grows requests, installs plans; every candidate rehearsed in
the twin at 1920x1080 on IvyBridge with a 64 MB SATA disk of its own):

```
python3 broker/metal.py
```

and the machine, windowed, with one SATA disk — for a blank disk remove `stage7/out/disk.img` first, then the `truncate` (on a file already 64 MB it changes nothing) — the `truncate` only for a
blank disk (`./stage7/test.sh` overwrites `stage7/out/disk.img`; a disk
worth keeping is copied to `stage7/out/disk.oracle.img`, a name the
harness never touches):

```
truncate -s 64M stage7/out/disk.img
qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage7/out/esp.img \
  -drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

On a blank disk the serial log says `S7: gpt written` then `S7: disk port
1 131072 notes 2048 home 34816`, `S7: notebook formatted`, `S7: home 0
apps`. Type a note. Type **`! install calculator`**: the strip says
`installing` while Claude builds from `plans/calculator.md` and the twin
runs its five tests on a SATA disk of its own; then `installed calculator`
in its panel. Do a sum; Esc. Quit QEMU, stop the broker, run the same QEMU
command again (no `truncate`): `S7: disk port 1 131072 notes 2048 home
34816`, `S7: notebook 1 notes`, `S7: home 1 apps`; the note on screen;
**`! calculator`** on the choices row, launched from the home partition
with nothing on the wire. On the host, `blkid -p stage7/out/disk.img` and
`partx -s stage7/out/disk.img` read the table the machine wrote. His word
closes the ring; then ring 7b, the wire, in its own session with its own
plan gate.

Earlier — **Ring 6c is closed; Stage 6 is closed.** The Stage 7 spec was
written in a fresh Cowork session on 9 September 2026 with the policy
re-check the foundation requires at the gate, against the HP's inventory
(the Lenovo below was replaced by the HP). What the owner brought to it:

1. **The Lenovo** (the sacrificial desktop with the laptop board inside,
   decided 1 September), fetched from Baldock and fitted with a drive it
   will accept — SATA or NVMe, any size; it will be wiped. Nothing else on
   it matters; it must be a machine with no data anyone wants.
2. **Its hardware inventory**, taken from a Linux live USB before the spec
   is written: `lspci -nn` (the NIC, the disk controller — AHCI or NVMe —
   the display, the USB controller), `lsusb`, `dmidecode -t bios` (UEFI or
   legacy, and whether it boots a USB stick), and whether the keyboard
   and mouse reach it over PS/2 or USB. The spec is written against this
   list: virtio-blk and virtio-net do not exist on metal, so Stage 7's
   first work is the drivers the inventory names, each rehearsed first in
   the twin with QEMU's matching device (`e1000`, `ahci`, `nvme`,
   `qemu-xhci`) before anything touches the machine.
3. **A USB stick** to boot GermOS from, and a USB-to-serial adapter if the
   board has a COM header — the serial log is the observation chart; if
   there is no serial, the spec decides what replaces it (the screen, or
   a USB debug path).
4. **The policy re-check**: does `claude -p` still draw from the
   subscription with no API keys? Checked at every stage gate since
   Stage 4.
5. **The implementing model** for Stage 7, and whether the trials ring
   (N-of-1, layout A against B on the numbers the obs page has recorded
   since ring 6a) comes before or after the metal.

To click through again at any time — two terminals at the repo root. The broker (it answers questions, grows requests, installs
plans, serves the point app from its mock table only in `--mock`; every
candidate rehearsed in the twin at 1920x1080 with a home drive):

```
python3 broker/pointer.py
```

and the machine, windowed, with both disks (`stage6/out/home.oracle.img`
still holds the calculator installed at ring 6b's oracle and is never
touched by the harness; copy it over `stage6/out/home.img` to start with
the calculator installed, or `truncate -s 16M stage6/out/home.img` for a
blank home and `! install calculator` again):

```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage6/out/esp.img \
  -drive format=raw,file=stage6/out/notes.img,if=virtio \
  -drive format=raw,file=stage6/out/home.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Click in the QEMU window to grab the mouse (Ctrl+Alt+G releases it) and
move it: the arrow appears, `S6: mouse ready` goes out on serial, and `pt`,
`pk` and `cl` join the strip's first row. Click **`! calculator`** on the
choices row: the calculator launches from disk. Click into its panel:
nothing happens (a four-callback app). Click **`= result`** and **`c
clear`**, **`Tab prompt`** and **`Tab app`**, then **`Esc exit`**. Click
**`! grow`**, type a request, Enter — the strip says `growing` while Claude
writes and the twin rehearses. His word closed the ring and the stage on
5 September 2026.

Earlier — **ring 6b is closed.** Ring 6c's shape as the 6b handover put it, per
`stage6/spec.md`: the PS/2 mouse on the i8042's auxiliary port (IRQ12,
three-byte packets into a ring as the keyboard's), the i8042 configured
for the first time, `S6: mouse ready` as the eighteenth line, the cursor
drawn by the glass core last in every frame from a position the handler
keeps in the obs page, pointer input-to-photon on the strip, a click on
a choices-row target doing what its key does, a new ABI 2 callback
`point(row, col, button)` with the table one entry longer, GLASS.md
extended by a new frozen section rather than edited (the 6a section
stands byte for byte), and acceptance tests 1–4 written red before any
code. A fresh session, its own plan gate. The twin's `lines` becomes 18
through the frozen seam; ring 6b's gate (`./stage6/test-6b.sh`) and ring
6a's stay green as regressions on the same binary.

To install something from a plan again at any time — two terminals at
the repo root. The broker (it
answers questions, grows requests, and installs plans — every candidate
rehearsed in the twin at 1920x1080 with a home drive, an install against
its plan's own tests):

```
python3 broker/plans.py
```

and the machine, windowed, with both disks (the home image is a blank
16 MB file the guest formats on first boot; `stage6/out/` is gitignored
— `./stage6/mkimage.sh` rebuilds the boot image if it is gone):

```
truncate -s 16M stage6/out/home.img
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage6/out/esp.img \
  -drive format=raw,file=stage6/out/notes.img,if=virtio \
  -drive format=raw,file=stage6/out/home.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Type **`! install calculator`**. The strip says `installing` while
Claude builds from `plans/calculator.md`'s intent and the twin runs its
five tests (the broker's terminal narrates the verdicts; a failed test is
refused in the plan's words, `rehearsal failed: expect "5"`, and the
brief in `broker/claude_backend.py` — unfrozen — is the thing to adjust);
then `installed calculator` and the calculator in its panel with
`= result   c clear   Esc exit   Tab prompt` on the row. Do a sum. Esc.
Quit QEMU, stop the broker, run the same QEMU command again: `S6: home 1
apps`, `! calculator` on the choices row, **`! calculator`** runs it
from disk, and the sum works again. His word closes the ring; then ring
6c, the pointer, in its own session.

Earlier — before ring 6b opened — **ring 6a is closed.** Ring 6b's
shape, as the ring 6a handover put it, per
`stage6/spec.md`: `plans/<name>.md` in the format a new frozen
`stage6/PLANS.md` defines (intent, choices, the five-verb tests),
`! install <name>` rehearsed in the twin against the plan's own tests
through `twin.rehearse`'s post-delivery hook, the home image with its
frozen `stage6/HOME.md`, `S6: home <N> apps`, launch without the broker,
`! undo install`, the calculator as its oracle. A fresh session, its own
plan gate; it subclasses `Glazier` and calls `twin.rehearse` with the
machine's display in `twin.VGA_ARGS` and the extra drive in
`extra_args`, never editing a frozen file.

To grow something on the glass again at any time — two terminals at the
repo root. The broker (it answers questions and requests, rehearses
every candidate app in the twin, and caches what passes in `germline/`
under an `abi2` key):

```
python3 broker/glass.py
```

and the machine, windowed — the display flags are load-bearing (the
EDID is what picks the mode; 1920x1080 is the owner's choice for a
window on this monitor, and the gate keeps 1440x1440):

```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage6/out/esp.img \
  -drive format=raw,file=stage6/out/notes.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Type **`! make me a clock`**. The strip says `growing` while Claude
writes and the twin rehearses (the broker's terminal narrates each
step); the clock ticks in the app panel with `running make me a` on the
strip and `Esc exit   Tab prompt` on the choices row; **Tab** gives the
keys to the prompt — type a note beside the ticking clock, it journals —
**Tab** gives them back; the strip's numbers move; **Esc** closes the
app. `! make me a clock` again comes from `germline/` at once with
`g 001/001`. **The Stage 5 clock in `germline/` is an `abi1` entry**:
ring 6a keys its germline `abi2`, so the first request regenerates
against GLASS.md's callback contract — the brief in
`broker/claude_backend.py` (unfrozen) is the thing to adjust if a
candidate fails rehearsal twice; the screen says `rehearsal failed:
<phrase>` and the broker's terminal says which. `stage6/out/` is
gitignored: `./stage6/mkimage.sh` rebuilds the boot image and
`truncate -s 16M stage6/out/notes.img` makes a blank notebook. His word
closes the ring; then ring 6b, the store of plans, in its own session.

**Stage 5 is closed** — test 5 confirmed by Wajira on 1 September 2026:
the clock ran, right time, date and exit line included; the two oracle
screenshots are `history/2026-09-01-first-grown-clock.png` and
`history/2026-09-01-stage5-boot-log.png`. Cowork's review preceded the
run: zero defects.

To grow something again at any time — two terminals at the repo root.
The broker (it answers questions and requests, rehearses every candidate
in the twin, and caches what passes in `germline/`):

```
python3 broker/germline.py
```

and the machine, windowed:

```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage5/out/esp.img \
  -drive format=raw,file=stage5/out/notes.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Type **`! make me a clock`**. The indicator turns while Claude writes and
the twin rehearses (the broker's terminal narrates each step: the
generation call, the rehearsal's verdict and time, the germline write);
a clock with the right time ticks on GermOS's screen; **Esc** returns the
prompt; `! make me a clock` again comes from `germline/` at once. If a
candidate fails rehearsal twice, the screen says `rehearsal failed:
<phrase>` and the broker's terminal says which `ERR:` line the twin
printed — the brief in `broker/claude_backend.py` (unfrozen) is the thing
to adjust. `stage5/out/` is gitignored: `./stage5/mkimage.sh` rebuilds
the boot image and `truncate -s 16M stage5/out/notes.img` makes a blank
notebook.

To ask GermOS a question again at any time, in two terminals at the repo
root — the real broker, then the machine windowed:

```
python3 broker/broker.py
```
```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage4/out/esp.img \
  -drive format=raw,file=stage4/out/notes.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Type `? ` and a question; a note (no `?`) still persists across a reboot,
exactly as Stage 3. `stage4/out/` is gitignored — if the images are gone,
`./stage4/mkimage.sh` rebuilds the boot image and
`truncate -s 16M stage4/out/notes.img` makes a blank notebook.

To boot Stage 3 again at any time, from the repo root:

```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage3/out/esp.img \
  -drive format=raw,file=stage3/out/notes.img,if=virtio -serial stdio
```

`stage3/out/` is gitignored, so the notebook is not in the repository: if the
image is gone, `./stage3/mkimage.sh` rebuilds the boot image and
`truncate -s 16M stage3/out/notes.img` makes a blank disk, which the next boot
formats. Note that `./stage3/test.sh` overwrites `notes.img` — the two notes
from the oracle run are a keepsake, not a fixture, so a copy of that exact
image was set aside as `stage3/out/notes.oracle.img` (also gitignored; the
harness never touches that name).
