# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 15 September 2026 — **Stage 7 ring 7c, the metal, is OPEN.** `stage7/plan-7c.md` was approved at the plan gate on 15 September 2026 with Cowork's seven amendments, A1–A3 required and A4–A7 adopted as cheap (A1 `chart.py` opens the port non-blocking, sets termios with `CLOCAL`, then clears the flag — a three-wire null-modem cable never asserts DCD; A2 under `CAP.SSS` a port's `DET 0` right after `SUD` is given a second to leave 0 before it is passed, then ten seconds to reach 3 or a named halt; A3 the flash procedure checks for exactly one USB line by SIZE and MODEL, unmounts the stick's partitions with `udisksctl` before the write and powers it off after `sync`; A4 the bodyguard's widened `/dev` mention stops at a word boundary so `/devel` and `/devices` stay allowed; A5 the mode-loop bound mirrors every mode-only limit `surf_describe` enforces, `SURF_ROWS_MAX` included; A6 the `i8042:` pair is asserted on all three of test 2's boots; A7 METAL.md says what `nmcli` does to the connection and how to undo it) and all eleven deviations accepted. **The model for this ring: Fable 5.1 at medium effort, the owner's decision in the spec.** Item 0 (this record, the plan's commit) is done; the items follow one commit each, exactly as the plan says — the builder and the acceptance machinery first (the stick, the three boots over USB, every stage re-proven in the twin of the HP in one scripted run, the bodyguard extended), the freeze, then the EDID guard, the i8042 cold init, `PxCMD.SUD`, the relay's grace close, `chart.py`, `METAL.md`. Test 5 is Wajira's, on the HP; his word closes the ring and the stage. Earlier — **Stage 7 ring 7b, the wire, is CLOSED.** Wajira ran test 5 on 15 September 2026 with the real broker behind the relay on `127.0.0.1:9997`: a blank 64 MB disk; nineteen `S7:` lines in order with `S7: nic 6c:3b:e5:3b:86:45` then `S7: link up`; `? ping` answered over the e1000e through the relay ("pong. I hear you, GermOS. The link is up and I am ready for your next line."); `! make me a clock` written by the real backend, rehearsed in the wire twin, and running in its panel with its own choices row (`h 12/24 hour`, `d date on/off`, `Esc exit`, `Tab prompt`). The strip: `w 002 002941`, `g 000/001`, `err 000`, `io 002040/000676`. *"Save the screenshot and test 5 is passed."* — the owner's words. The screenshot is `history/2026-09-15-ring7b-clock-e1000e.png`. Cowork's pre-oracle review of the driver and the relay found zero defects. **The model note, for the owner's comparison:** ring 7b was implemented on **Fable 5.1 at high effort**, one session, thirteen commits plus 10b, one per item; at the plan gate Cowork needed no blocking amendment (A1–A5 adopted); one freeze opening, in the frozen checker, of ring 6b item 10b's class (a count written from arithmetic, not from a run); zero review defects; zero oracle defects. Next: **ring 7c, the metal**, a fresh session for Cowork and for CC, medium effort by the spec. Earlier — **ring 7b was green pending the oracle.** All four automated tests pass on `./stage7/test-7b.sh` (314 s, ten boots plus two rehearsals, mock only): nineteen `S7:` lines on an e1000e carrying the HP's MAC with `S7: link up`, eighteen on the same disk, the e1000e preferred beside a virtio-net, the link taken down through the monitor ending in `ERR: nic link did not come up within 10 s` and a halt; `? ping`, a note and `? hello` through `broker/relay.py` on 9997 to the mock at `-smp 2`, `4` and `8` with the relay's log agreeing with the record and the strip's wire counters; the cage — both argv checks, the relay's bind rule on the host, a mock-down run ending in a console message, `! test app` and `! install echo` through the relay with nineteen-line rehearsal logs in the twin, the launch with nothing on the wire. Ring 7a's gate on the same binary and the three ring 6 gates and Stages 0–5 on their own: all green. **One session, twelve commits plus one (item 10b, the project's fifth freeze opening, by the owner's hand: a count in the frozen checker written from arithmetic — ring 6b item 10b's class again); tests red before code; the driver worked on the first probe.** Test 5 is Wajira's, the three commands under "Next action". **The model note, for the owner's comparison:** ring 7b was implemented on **Fable 5.1 at high effort**; at the plan gate Cowork needed no blocking amendment (A1–A5 adopted). Earlier — **Stage 7 ring 7b opened.** `stage7/plan-7b.md` was approved at the plan gate on 15 September 2026 with Cowork's five amendments, none blocking (A1 the relay sets `SO_REUSEADDR` and flushes each log line as the connection ends; A2 its teardown never raises, and a RST or a FIN on a refused broker are both "no answer" by UMBILICAL.md; A3 the relay's bind battery is three fixed addresses, no hostname lookup; A4 `e1k_poll` honours a received descriptor's errors byte; A5 the ports as this ring settled them carried to ring 7c — the relay on 9997 in the twin, `python3 broker/relay.py` with no flags on the HP's day, the spec's 7c command corrected at the 7c gate) and all eleven deviations accepted. **The model for this ring: Fable 5.1 at high effort, the owner's decision in the spec.** Item 0 (this record, the plan's commit) is done; the items follow one commit each, exactly as the plan says. Earlier — **Stage 7 ring 7a, the disk, is CLOSED.** Wajira ran test 5 with the real broker on 9 September 2026: `S7: gpt written` then `S7: disk port 1 131072 notes 2048 home 34816` on a 64 MB SATA disk; `? Hi there.` answered over the wire (`w 001 005531`); `! install calculator` built by the real backend and rehearsed in the twin on a SATA disk of its own; a sum; then a reboot with no broker — `S7: home 2 apps` (echo from the gate's disk beside it), `! calculator` launched from the home partition with `w 000` and `io 000000/000000`. *Everything ran as expected.* The screenshots are `history/2026-09-09-ring7a-hi-there-sata.png` and `history/2026-09-09-ring7a-calculator-from-sata.png`. One trap found at the oracle, not a defect: `truncate -s 64M` on a file already 64 MB changes nothing, so the run started on the gate's disk (its note `last`, its echo) — remove the file first for a blank disk; the command below says so. Cowork's pre-oracle review of the AHCI driver, the selection rule and the GPT code found zero defects. **The model note, for the owner's comparison:** ring 7a was implemented on **Fable 5.1 at high effort**, one session, twelve commits, one per item; at the plan gate Cowork needed one blocking amendment (A1, the port selection rule — the twin's boot image sits on AHCI port 0 and the plan would have formatted it) and three others; no freeze opening; zero review defects; zero oracle defects. Next: **ring 7b, the wire** (e1000e, the relay), a fresh session for Cowork and for CC. Earlier — **Stage 7 — Metal — is OPEN, and ring
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
| Stage | **7 — Metal — OPEN since 9 September 2026**: ring 7a (the disk) **closed 9 September**; ring 7b (the wire) **closed 15 September**; **ring 7c (the metal) OPEN since 15 September 2026** — `stage7/plan-7c.md` approved with Cowork's seven amendments, medium effort by the spec. Stages 0–6 closed (Stage 6 on 5 September 2026) |
| Status | Ring 7c: **item 0 done** (the plan committed, this record); items 1–14 follow, one commit each; no ring 7c test exists yet. Ring 7b: **all five tests PASS** (test 5 confirmed by Wajira, 15 September 2026). Ring 7a: **all five tests PASS** (test 5 confirmed by Wajira, 9 September 2026). Stages 0–5 and the three ring 6 gates green on their own binaries; both Stage 7 gates green on the 7b binary. |
| Repo | `/home/indy/Projects/ai-os` (branch `main`) — **public since 1 September 2026 at `github.com/IndyWH/germos`, MIT licence** (commit `beef02e`) |
| Machine | mlrig, native Ubuntu 26.04, 32 logical CPUs |
| Toolchain | NASM 3.01, QEMU 10.2.1, Python 3.14, OVMF, mtools, OpenBSD netcat, the `claude` CLI 2.1.261 — ring 6a needs no new packages (QEMU's standard VGA device with `edid=on` is built in) |
| Model | **Ring 7c: Fable 5.1 at medium effort** — the owner's decision in the spec, recorded at item 0 (the spec sets high for 7a and 7b, medium for 7c, decided at each gate); to be compared with ring 6b, the earlier medium-effort ring. Ring 7b was Fable 5.1 at high effort — one session, thirteen commits plus 10b, one freeze opening of ring 6b item 10b's class, zero review defects, zero oracle defects. Ring 7a was Fable 5.1 at high effort. Ring 6c was Fable 5.1 at high; ring 6b Fable 5.1 at medium, the owner's experiment, to be compared with Opus at high (Stages 0 and 1) and Fable at high (Stages 2 to 6a, 6c); Cowork reviews to the same standard as every ring |

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

## Stage 7 — Metal · opened 9 September 2026

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
project's fifth freeze opening**, after Stage 5 item 8b, ring 6a item
12b, ring 6b item 10b and ring 6c item 11b, and its class is ring 6b
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


## Ring 7c — the metal · opened 15 September 2026

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
| 1 | Artefact — the standing PE32+ checks, plus `stick.img` parsed from the host: protective MBR, a valid GPT, one ESP of the type GUID, `EFI/BOOT/BOOTX64.EFI` byte-identical to the build | not yet written |
| 2 | Serial, the metal configuration — the stick over USB with the SATA disk and the e1000e: nineteen lines at `-smp 8`, eighteen at 4, `edid none` and the highest mode on a display that is not QEMU's at 2; the `i8042:` pair on every boot | not yet written |
| 3 | Every stage re-proven in the twin of the HP — one scripted run, two boots, `-smp 4` | not yet written |
| 4 | The bodyguard, extended — the payload table 0 wrong, the harness's strings, the argv checks, the bind rule | not yet written |
| 5 | **Oracle — Wajira, on the HP** — the stick, the lines on the chart, the glass at native, a note across a power cycle, `? ping` over the LAN, `! install calculator` and its launch with the broker off, a click | pending |

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

## Next action

**Ring 7c is open at item 1.** Next: item 2, `stage7/mkstick.py` from the
probe's shape, then items 3–14 as `stage7/plan-7c.md` says. The HP's day: three
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
