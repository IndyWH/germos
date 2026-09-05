# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 4 September 2026 — **Stage 6 ring 6c, the pointer, is
OPEN** at item 0: `stage6/plan-6c.md` approved with Cowork's three
amendments and three nits (A1 where test 2 goes green; A2 no count in the
frozen checker is a literal — every one is derived from the step list;
A3 a launch item clicked with text on the prompt line does nothing), all
eleven deviations accepted. **The model note:** ring 6c is implemented on
**Fable 5.1 at high effort**, the owner's decision, Cowork reviewing to the
same standard as every ring. The ring's section is below the ring 6b
build. Earlier — **Stage 6 ring 6b, the store of
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
| Stage | 6 — Growth: ring 6a closed 2 September 2026; ring 6b closed 3 September 2026 (Stages 0–5 closed); **ring 6c — the pointer — OPEN**, 4 September 2026, the last ring of the stage |
| Status | Ring 6c: `stage6/plan-6c.md` **approved** 4 September 2026 (Cowork's A1–A3 and nits adopted, eleven deviations accepted); items 0–5 done (the GLASS.md section appended by the owner, the fixture and `broker/pointer.py` rehearsed in both twins, the gate and the checker with tests 1–4, tests 2–4 red on the ring 6b binary, the freeze at 1206 payloads 0 wrong); items 9–11 done (the i8042, IRQ12, the packet ring, the line, the cursor, `pt`, the click on the row; tests 1, 2 and 4 green, every earlier gate green); the freeze opened once at item 11b by the owner's hand for one misordered read in the checker; item 12 next, one commit per item. Ring 6b: all five tests PASS (test 5 confirmed 3 September 2026). |
| Repo | `/home/indy/Projects/ai-os` (branch `main`) — **public since 1 September 2026 at `github.com/IndyWH/germos`, MIT licence** (commit `beef02e`) |
| Machine | mlrig, native Ubuntu 26.04, 32 logical CPUs |
| Toolchain | NASM 3.01, QEMU 10.2.1, Python 3.14, OVMF, mtools, OpenBSD netcat, the `claude` CLI 2.1.252 — ring 6a needs no new packages (QEMU's standard VGA device with `edid=on` is built in) |
| Model | **Ring 6c: Fable 5.1 at high effort** — the owner's decision for this ring, recorded at item 0. Stage 6's standing rule is Fable 5.1 at high (6a); ring 6b was Fable 5.1 at medium, the owner's experiment, to be compared with Opus at high (Stages 0 and 1) and Fable at high (Stages 2 to 6a, 6c); Cowork reviews to the same standard as every ring |

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

## Next action

**Ring 6c is at item 11b; item 12 (`point`) follows on a full green gate.** Next: item 1 — GLASS.md's ring 6c section
written to `stage6/out/glass-6c-section.md`, appended by the owner's own
hand with one `cat … >>` command at the repo root (spelled in the plan's
decision 13), the first 777 lines proven byte-identical, committed. Then
items 2–8 (the fixture, `broker/pointer.py`, `stage6/test-6c.sh` and
`stage6/checkpointer.py` with tests 1–4 red, the freeze), then the guest
code in items 9–12, the handover at item 13, and test 5 — the owner clicks
his way through the choices row and into the calculator with
`python3 broker/pointer.py`.

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
