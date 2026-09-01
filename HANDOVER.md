# HANDOVER

Rolling state of the AI OS project. Read this first, then `ai-os-foundation.md`
(the single source of truth), then the current stage's `spec.md` and `plan.md`.

**Last updated:** 1 September 2026 — **Stage 4 opens.** Stage 3 closed on
the morning of 1 September: Wajira booted the machine windowed and it
remembered his note — *"It remembers!"* `stage4/spec.md` — The umbilical — is
approved, with the foundation's Stage 4 policy gate already cleared and
recorded in it. Two owner decisions taken at the opening: **Fable 5 at high
effort implements this stage**, and the **subscription policy re-check
passed** (`claude -p` still draws from the Max subscription; the June 2026
credit-pool change is paused; re-check again at Stage 5). Next is
`stage4/plan.md`, drafted in plan mode and committed for his approval before
any code — and this is the first stage where the plan gate is a hook, not a
convention: exiting plan mode is blocked until he writes the approval marker
from his own terminal.

---

## Where we are

| | |
|---|---|
| Stage | 4 — The umbilical |
| Status | Spec **APPROVED** (1 September 2026). Plan pending approval at the plan gate. |
| Repo | `/home/indy/Projects/ai-os` (branch `main`) |
| Machine | mlrig, native Ubuntu 26.04, 32 logical CPUs |
| Toolchain | NASM 3.01, QEMU 10.2.1, Python 3, OVMF, mtools — Stage 4 needs no new packages (the broker is standard-library Python and shells out to `claude`) |
| Model | **Fable 5, high effort** — the owner's decision for Stage 4 (see below) |

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
`stage2/font8x8.bin`, `stage3/test.sh`, `stage3/checknotes.py` and
`stage3/NOTEBOOK.md` are frozen by `.claude/hooks/protect-tests.py`. The
format document is frozen for the reason the font is: the assembler
implements it and the checker parses by it, so an editable format would be an
editable criterion. The builders (`stage1/mkimage.sh`, `stage2/mkimage.sh`,
`stage3/mkimage.sh`) and `stage2/FONT.md` are deliberately **not** frozen:
recipe and paperwork, judged by their product.

The same hook is the **storage bodyguard** from Stage 3 item 1 (see the Stage
3 section). From Stage 3 the payload table is committed as
`.claude/hooks/payloads.py` — the Stage 0–2 freeze cases reconstructed from
their commit records, the storage cases, and the Stage 3 freeze cases: 300
payloads, 203 denied, 97 allowed, 0 wrong. Run it with
`python3 .claude/hooks/payloads.py`; it exits non-zero on a single wrong
verdict. Every freeze and the bodyguard bit immediately (per Stage 1's
amendment A4), demonstrated live each time.

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

## Stage 4 — The umbilical · opened 1 September 2026

**Goal (foundation §7):** network driver, minimal TCP/IP, and a broker on
mlrig that relays to Claude. Done when the booted OS asks Claude a question
and prints the answer. Proves the OS has a brain. `stage4/spec.md` is
approved (Cowork, 1 September 2026).

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

## Next action

`stage4/plan.md`, drafted in plan mode and committed for Wajira's approval,
evaluation-first: `stage4/UMBILICAL.md` (the wire protocol, byte-exact — the
NOTEBOOK.md precedent), `broker/broker.py` with its `--mock` mode,
`stage4/test.sh` and its checker for acceptance tests 1–4 committed red, then
the implementation grown on `stage3/stage3.asm`: the PCI scan generalised to
two virtio devices, modern virtio-net with receive and transmit queues, ARP,
IPv4, client-only TCP, and the `? ` question path drawn console-only. After
the gate opens: one commit per numbered item, `./stage4/test.sh` green before
each commit that should pass it, Stages 0–3 green throughout.

Cowork's review of Stage 3 (per `REVIEW.md`: bugs first, a disassembly-level
read of `disk_rw`, `map_mmio_2m` and `record_valid`; `python3
.claude/hooks/payloads.py` re-run rather than trusted) still stands as the
reviewer's task and does not block Stage 4's plan.

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
