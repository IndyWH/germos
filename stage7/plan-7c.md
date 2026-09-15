# Stage 7, ring 7c — the metal · implementation plan

**To be committed verbatim as `stage7/plan-7c.md`. Produced in plan mode, per
the foundation's build loop. Nothing below is implemented until Wajira
approves this document by writing the approval marker from his own terminal;
the ExitPlanMode hook holds the gate until then. Plan mode allows this
session to write only this one file and forbids commits and boots, so — as
every ring since 6a — the copy to `stage7/plan-7c.md` and its commit are the
first act after the gate opens, item 0 below, before any other file is
touched. Cowork's amendments while the gate holds are adopted here as
numbered amendments (A1, A2, …) at the end of the document.**

## Context

Ring 7b, the wire, closed on 15 September 2026 at Wajira's test 5.
`stage7/spec.md` (approved 9 September 2026) makes Stage 7 three rings, and
**this is ring 7c, the metal**: it was never just a simulation. The done-when,
from the spec: **the HP Compaq Elite 8300 boots GermOS from a USB stick; the
`S7:` lines arrive on mlrig's serial terminal in the twin's order; the glass on
the monitor at the native mode; a note kept across a power cycle; `? ping`
answered over the LAN; `! install calculator` built by the real broker over
the LAN and, after a reboot with the broker off, `! calculator` launched from
the SATA disk; a click on the choices row.** Test 5 is Wajira's, on the HP.
His word closes the ring and the stage.

What this ring builds, from `stage7/spec.md` and the kickoff — procedure and
a guard, no new driver:

- **The EDID guard** in `edid_read`: BAR2 is read as an EDID only when the
  display device is QEMU's VGA (`1234:1111`); any other display prints
  `S7: edid none` and the mode loop keeps the highest mode by area, as Stage 1
  wrote it. On the HP, Intel's GOP lists the monitor's own modes and the
  highest is native. Plus one cheap bound in the mode loop: a mode whose cell
  count exceeds the console shadow is skipped (decision 2).
- **The i8042 cold init**: the controller self-test (`0xAA` → `0x55`) before
  the command byte is written, two `i8042:` serial lines (the self-test, the
  mouse reset), and named `ERR: i8042` lines in place of the silent
  `jc .done` on the controller path. Retires Stage 2's debt. No new `S7:` line.
- **The stick**: `stage7/mkstick.py` (unfrozen builder) writes
  `stage7/out/stick.img` — protective MBR, GPT, one ESP holding
  `EFI/BOOT/BOOTX64.EFI` — with mtools' `image@@offset` form, no loop
  device, no `/dev`, nothing outside `out/`. The gate boots a **copy** of it
  over `qemu-xhci` + `usb-storage` with no `esp.img` on SATA.
- **`PxCMD.SUD`** in the AHCI port bring-up when `CAP.SSS` is set — the item
  carried from ring 7a, the smallest shape the AHCI 1.3 spec gives; the
  twin's `CAP.SSS` is clear (measured), so the path is written to the spec
  and cannot be exercised here (decision 4, said plainly).
- **The relay's grace close** (`broker/relay.py`, unfrozen): once the broker
  side has finished, the guest side is closed after a short grace, so a guest
  that dies mid-connection never holds the relay. Proven on the host, no
  guest; WIRE.md stands untouched.
- **`broker/chart.py`**: the serial reader for the HP's day — the port at
  115200 8N1 through the standard library's `termios`, every line to the
  terminal and teed to a file with a timestamp. Proven on a pty pair inside a
  Python script, so no `/dev` path appears in any Bash command.
- **The bodyguard, extended**: `dd`, `of=`, `by-id`, `ttyUSB`, `nmcli` and
  every `/dev` spelling denied in Bash, prose included; `/dev/tty*` narrowed
  to `/dev/tty` itself; the payload table 0 wrong.
- **`stage7/METAL.md`**: the owner's document, unfrozen — the flash and the
  HP's day as ordered steps, the debugging table, what goes into `history/`.
- **Acceptance tests 1–4**, written red before any code, in
  `stage7/test-7c.sh` and `stage7/checkmetal.py` — test 3 re-proving every
  stage in the twin of the HP in one scripted run; then **the freeze**.
- **`HANDOVER.md`** as we go; `CLAUDE.md`'s build block and gotchas;
  `README.md`'s ring 7c; the three commands for the HP's day.

**The owner's decisions, already made, not reopened here:** (1) this ring is
implemented on **Fable 5.1 at medium effort**, per the spec — recorded in
`HANDOVER.md` at item 0; (2) the HP plugs into the home switch and mlrig's
LAN port carries `10.0.2.4/24` as a second address, the relay binding
`10.0.2.4` on the HP's day; (3) the stick is flashed by the owner's hand by
the by-id path, never by CC — CC never touches `/dev`; (4) TLS stays in the
broker, the N-of-1 trials ring comes after the metal, no policy re-check this
ring; (5) the Stage 6 binary and gates are untouched, and Stages 0–6, ring
7a's gate and ring 7b's gate stay green on the 7c binary or their own
throughout.

The standing orders: the automated gate talks only to the mock, spends no
token and needs no internet; the real backend is exercised only by the owner
at test 5. The cage, the storage bodyguard and every frozen file stand: every
path in `PROTECTED` stays byte for byte — the ring 7b four included — and
`./stage7/test.sh`, `./stage7/test-7b.sh`, the three ring 6 gates and every
earlier gate must pass at the end of the ring. **The scope guard:** if a
frozen file turns out to be wrong, stop at the commit boundary, write the
diff unapplied under `stage7/out/`, say so in `HANDOVER.md`, and wait; the
owner applies it by his own hand. Never create or mention the approval
marker from inside a session. One commit per numbered item; `/clear` between
items; tests red before the code they judge; tests green before every commit
that should pass them; **every number in a frozen test is written from a run
or derived from the test's own data, never from arithmetic, and a counter's
rule is looked up in its frozen document before the number is typed** (ring
6b item 10b, ring 7b item 10b). Two honest attempts per obstacle.

The plan is **evaluation-first**. Items 1–5 make the builder and the
acceptance machinery so that tests 1–4 exist and tests 2–4 fail before a
single instruction of guest code is written; item 6 freezes them. Items 7–14
are the code, the tools, the documents and the handover. **Test 1 goes green
at item 3** (the stick parsed from the host; the artefact is ring 7b's closed
binary until item 7). **Test 2's `novga` boot goes green at item 7** (the
guard) and **test 2 whole at item 8** (the i8042 lines); **test 3 at item 8**;
**test 4 at item 13** (the hook). Item 14 is the handover. Test 5 is Wajira's.

### Environment, measured in this session before planning

Read-only: no file was written but this one, no guest was booted, nothing
frozen was touched; the working tree is clean at `c964c3b` but for the
untracked `paper/` (not this ring's). No Claude call was made. The one hook
probe that spelled a `/dev` path was denied by the bodyguard, prose rule
included, before it ran — which is the rule working; the `/dev` spellings
below are therefore reasoned from the hook's regexes and go to item 1 as a
measurement through the payload table, never through a Bash command.

| Fact | Measured how |
|---|---|
| **The toolchain is unchanged:** NASM 3.01, QEMU 10.2.1, Python 3.14.4, OVMF at `/usr/share/ovmf/OVMF.fd`, **mtools 4.0.49**, OpenBSD netcat. No new package. **`qemu-xhci` (PCI) and `usb-storage` (usb-bus, `drive=<id>`, `removable`, `bootindex`) are built in.** Display devices present: `VGA`, `bochs-display`, `cirrus-vga`, `ramfb`, **`virtio-vga` (PCI, `edid=on` by default)**, `virtio-gpu-pci` | `-device help`, `-device virtio-vga,help`, `-device usb-storage,help` |
| **mtools' `image@@offset` form is documented on this host**: "you can also supply an offset within the image file by including @@offset into the file name", `mcopy -i my-image-file.bin@@1M …` | `man mtools`, "Sizes and offsets" |
| **The hook's verdicts today** on this ring's names and words: `echo x > stage7/METAL.md`, `cp x stage7/Metal.py`, `echo x > stage7/checkmetal.py`, `echo x > stage7/mkstick.py`, `echo x > broker/chart.py` all **allowed** — the freeze's `CANDIDATE` and `BASENAMES` are case-sensitive (`re.compile` with no `re.I`), and `checkmetal.py` resolves to nothing (`resolve` takes the whole token's basename, so the `metal.py` tail inside it is not a hit); **`by-id`, `nmcli`, `ttyUSB`, `of=`, `dd` are allowed words today** (`echo by-id nmcli ttyUSB of=x add odd dd` exits 0) — so test 4 is red by design until item 13; the stick's mtools lines (`mformat -i stage7/out/stick.img@@1048576 …`, `mcopy -i …@@…`), the stick's QEMU line (`-device qemu-xhci -drive if=none,id=stick,format=raw,file=stage7/out/metal/stick.img -device usb-storage,drive=stick`), `-device virtio-vga,edid=on` and `python3 broker/chart.py` are **allowed**. **The payload table: 1444 cases, 982 denied, 462 allowed, 0 wrong** | the hook fed each payload on stdin; `python3 .claude/hooks/payloads.py` |
| **The `/dev` rule today**, from `DEV_MENTION = /dev/[\w./+-]*` and `DEV_ALLOWED`: `/dev/sda`, `//dev/sda`, `/dev//sda`, `/dev/./sda`, `/dev/disk/by-id/…` are denied (each contains a `/dev/…` token not in the allow list); **`/dev/ttyUSB0` and `/dev/ttyS0` are allowed** (`tty\w*`); a quoted split (`"/dev"/sda`), a backslash inside the word (`/de\v/sda`) and a bare `/dev` with no slash are **not matched** — the three holes item 13 closes. **`dd` is already a freeze verb** in `MUTATIONS` (aimed at a frozen path) but not a bodyguard word. The payload table's Stage 3 allowance `dd if=/dev/zero of=stage3/out/x.img …` becomes a denial at item 13 (decision 7) | read, `.claude/hooks/protect-tests.py`, `payloads.py` |
| **The twin's `CAP` is `0xc0141f05`** (ring 7a's item 1): bit 27, `SSS`, is **clear**. The `SUD` path cannot be exercised in the twin; the code is written to the spec and left for the HP (decision 4). `CAP` is in the obs page at `0x2C0` (`OBS_AHCI_CAP`), so item 1 re-reads it through the monitor rather than trusting the record | `HANDOVER.md` ring 7a item 1; `stage7/DISK.md` |
| **The serial line rule this ring must not break:** `stage7/test.sh` greps `S7: .*` and demands 18/17; `stage7/checkwire.py` derives 19/18 from its pattern lists (`len(patterns)`) and greps `S7: [^\n]*`; `broker/metal.py` `LINES = 18`, `LINE_RE = r"S7: [^\n]*"`; `broker/wire.py` `LINES = 19`; the frozen `twin.judge` fails a rehearsal on any `ERR:` line and on a line count other than `lines_want`. **So an `i8042:` line is invisible to every frozen counter, and an `ERR:` line fails every rehearsal** — the two facts behind the line design (decision 1) | read |
| **`S7: edid none` already exists** (`msg_edid_none`, `stage7.asm` 8907) and replaces `S7: edid WxH` one for one — the count holds. `edid_read` reads register 0 (vendor, device) of every function, then the class at register 8 into the same `EAX`; the vendor/device word must be kept aside (`R10D`) before the class read for the guard's compare. The mode loop keeps the highest area, ties to the wider; a mode needing more than `SHADOW_SIZE = 0x10000` cells (128×128, 2048×2048 pixels) halts in `console_init` with `err_shadow` | read, `stage7.asm` 640–760, 2402–2507, 7473–7520 |
| **The i8042 cold init mostly exists** (`mouse_init`, 2253–2313): `0xAD`, `0xA7`, drain, the command byte read (`0x20`), bits 0–1 set and 4–5 cleared, written (`0x60`), read back, `0xA8`, the mouse reset `0xFF` → `FA`, `AA`, the ID (kept as read, `1 + ID` into `mouse_id`), `0xF6`, `0xF4`, drain. Every read bounded by `I8042_WAIT_TRIES = 50` × `PIT_10MS`; `i8042_wait_ibf` spins `0x10000` reads and **returns silently on exhaustion**; the controller path's failures are a silent `jc .done`. **Missing:** the self-test, the two lines, the named errors. `S7: mouse ready` (`msg_mouse`) goes out raw after `keyboard ready` on the first packet, as ring 6c's | read |
| **The AHCI probe** (`disk_select`, 3195–3236): a port with `DET` 0 is passed at once; `DET` non-zero waits `AHCI_PROBE_TRIES = 5000` × 200 µs = one second for `DET 3, IPM 1`; `ahci_find` reads `CAP` into the obs page. `PX_CMD` is `0x18`; `PXCMD_SUD` is bit 1 (not yet defined) | read |
| **The frozen seams the 7c checker reuses as they are:** `checkwire.check_argv_7b(argv, port, mac, drives, virtio_allowed, netdevs, nic_netdev)`, `start_relay`, `read_relay_log`, `check_relay_log`, `question_bytes`, `start_mock` (on `broker/wire.py --mock`; bound to `stage7/out/wire/`), `check_germline_entry_7b`, `check_install_germline_7b`, `PATTERNS_BLANK`/`PATTERNS_AGAIN`, `NIC_LINE`, `LINK_LINE`, `MAC`, `READY`; `checkdisk.check_notes_partition`, `check_partitions`, `check_table`, `read_image`, `check_echo`, `check_formatted`, `check_esp`; `checkglass.check_question_entry`, `check_grow_entry`, `check_app_panel`, `check_one_cell_panel`, `check_strip`, `check_counts`, `check_region_rows`, `check_choices`, `check_mode_field`, `read_record`, `port_state`, `stop_mock`, `fixture_self_check`, `germline_entries`, `say`, `report`, `dump_capture`, `PROMPT`, `NO_ANSWER`, `SETTLE`, `CANNED`; `checkplans.check_install_entry`, `ECHO_TESTS_OK`, `CHOICES_ECHO_RUNNING`, `DATA_FIRST`; `pointer.choice_targets(app_running, focus, choices, installed=())`, `point_offset`, `parse_obs_6c`, `OBS_PAGE_BYTES_6C`; `metal.parse_header`, `parse_gpt`, `classify`, `partition_bytes`, `crc32`, `SECTOR`; `twin.Driver`, `keyname`, `qemu_argv`, `DEFAULT_PORT`; `plans.plan_keyname`; `glass.app_frame`, `grow_request`, `regions`, `TEST_CHOICES`. **Bound to a device or a form and transcribed instead:** `checkwire.qemu_argv`/`drive` (the ESP on SATA, no mouse steps), `checkwire.check_boot_lines` (the `WxH` EDID form), `checkpointer.drive`/`Pointer`/`strip_mouse_line`/`target_col`/`park_cell` (two virtio disks, `S6:`); `checkdisk.qemu_argv`/`drive` | read |
| **The pointer is driven through the monitor** as ring 6c did: `mouse_move dx dy` within one packet, `mouse_button mask`, the checker's own `Pointer` model turning a cell into moves (`moveto`), the arrow parked at the conversation panel's last cell before a screendump, `S7: mouse ready` stripped from the capture before the echo check (`strip_mouse_line`'s idiom) | read, `stage6/checkpointer.py` 133–350, 416–434, 864–884 |
| **The 7a and 7b oracle artefacts stay out of the 7c gate's path:** `stage7/out/disk.img` is the owner's; the 7b gate's scratch is `stage7/out/wire/`, the 7a gate's `stage7/out/`. This ring's scratch is **`stage7/out/metal/`** (disks, stick copies, captures, screens, records, relay logs) and its probe `stage7/out/probe7c/`; `stage7/out/` is gitignored | read, `.gitignore`, `ls stage7/out` |
| **The relay** (`broker/relay.py`, 147 lines): `handle` joins both pump threads before closing either socket; the up pump ends only when the guest's side reads EOF — the hang the kickoff names. `Log.add` flushes per line (A1); every teardown is `quiet` (A2) | read |
| **The frozen 7b gate's shape to copy:** `test-7b.sh` refuses to run while 9999, 9998 or 9997 is held (a connect probe), builds with `mkimage.sh`, spells the cage, machine, display and `sata_drive` once, wraps each headless boot in `timeout -k 5 60` with exit 124 the expected outcome, checks the boot image around every boot with the frozen `checkdisk.py --esp`, and calls the checker's modes | read |
| **The spec's ring 7c twin command names 9998 for the relay; 9998 is the frozen twin's own listener** (`twin.DEFAULT_PORT`). Corrected to **9997** here (deviation 1, A5) | read |
| **Commit messages** go in by `-F` from a file written with the Write tool: this ring's words (`dd`, `of=`, `by-id`, `ttyUSB`, `nmcli`, any `/dev` spelling) will be denied in prose from item 13, and `mount` already is | read, the hook |

**To be measured at item 1, before any test is written** (plan mode forbids a
boot), on private copies under `stage7/out/probe7c/` (gitignored), a
temporary probe spliced into a copy of the source, never into
`stage7/stage7.asm`, never committed:

1. **The stick over USB.** A hand-built stick image (the item 1 script, the
   shape `mkstick.py` will take): that `mformat -i stick.img@@<offset>` with
   the partition's size and `mmd`/`mcopy` at that offset work on this host's
   mtools, and that `mdir -i stick.img@@<offset> ::/EFI/BOOT` lists the file;
   then ring 7b's closed binary booted from a **copy** of it over
   `-device qemu-xhci -drive if=none,id=stick,format=raw,file=… -device
   usb-storage,drive=stick` with **no `esp.img` on SATA**, the 64 MB SATA disk
   on `ide.1` and the e1000e cage to a throwaway port, at `-smp 2`, `4` and
   `8`: that it reaches `S7: keyboard ready` with nineteen lines, `S7: disk
   port 1 …` (the ESP is no longer on port 0), and **the seconds from QEMU's
   start to `S7: alive` and to ready** — OVMF's USB enumeration may cost more
   than the SATA path's 1.3 s, and the checker's ready window and the gate's
   `timeout` are sized from that number. Whether OVMF writes `NvVars` into
   the stick copy (expected: yes — the ring 7a gotcha; the copy's FAT
   changes, its GPT does not).
2. **The display that is not QEMU's VGA.** The same binary booted with
   `-vga none -device virtio-vga,edid=on` (the candidate: vendor `0x1af4`,
   device `0x1050`, class `0x0300`) and, as the fallback, `cirrus-vga`: the
   PCI vendor and device the probe reads at register 0, BAR2's value, whether
   OVMF's GOP drives it and **its full mode list** (`QueryMode` over
   `MaxMode`: `WxH`, `PixelFormat`, `PixelsPerScanLine`, printed by the probe
   before the mode is set), the highest mode by area, whether that mode fits
   the shadow (`(w/16)·(h/16) ≤ 65536`), and what today's `edid_read` prints
   on it (expected: it reads virtio-vga's BAR2 as a valid EDID and prints
   `S7: edid WxH` — the very thing the guard must refuse). **The highest
   mode's `WxH` measured here is the literal the `novga` boot asserts** (a
   number from a run, not arithmetic).
3. **`CAP` through the monitor** on the stick boot: `OBS_AHCI_CAP` read from
   the obs page, bit 27 confirmed clear; `PxCMD` of port 1 as the firmware
   left it (`SUD`, `POD`, `ICC`).
4. **The i8042 as the twin answers it:** the probe issues `0xAA` to port
   `0x64` after the two disables and prints the answer (expected `0x55`), then
   reads the command byte (expected `0x67`, ring 6c's measurement, or whatever
   the self-test left) and the mouse's reset answer bytes and their timing in
   `PIT_10MS` breaths — so the two lines' wording and `I8042_WAIT_TRIES` are
   written from a run.
5. **`broker/chart.py`'s pty pair**: that `termios` on a pty accepts
   `B115200`, `CS8`, `CREAD|CLOCAL`, no parity, one stop bit (the settings are
   accepted and `tcgetattr` reads them back), inside a Python script with
   `pty.openpty()` — no `/dev` path in the Bash command.
6. **The hook's spelling table**: every `/dev` spelling of decision 7 fed to
   the hook through a scratch payload script written with the Write tool
   (never a Bash command line that spells them), each verdict recorded as
   today's, so item 13's flips are written from a run.

Recorded in `HANDOVER.md`'s environment table at item 1; the probe removed;
`git diff` shows only `HANDOVER.md`.

---

## Deviations from the spec and the kickoff, for approval

Each argued from a measured fact or a frozen file. Everything else is the
spec as written.

1. **The relay's port in the twin is 9997, not the spec's 9998** (ring 7b's
   deviation 1, A5). 9998 is the frozen twin's own rehearsal listener. Every
   7c QEMU line's `guestfwd` names 9997 and the gate refuses to run while
   9999, 9998 or 9997 is held. On the HP's day the relay is `python3
   broker/relay.py` with no flags — its defaults are `10.0.2.4` and 9999 —
   beside the broker on `127.0.0.1:9999`; `METAL.md` step 5 says so, and
   `HANDOVER.md` carries the correction.
2. **The broker on the HP's day is `python3 broker/wire.py`, not the spec's
   `pointer.py`.** The spec's step 5 was written before rings 7a and 7b
   existed; `wire.py`'s twin is the one that rehearses on a SATA disk of its
   own over an e1000e of its own, as ring 7b's oracle did. `pointer.py`'s twin
   boots two virtio disks that the 7c binary would not find. `METAL.md` names
   `wire.py`.
3. **No `S7:` line is added; the i8042 speaks with its own prefix.** Fact A:
   every frozen counter on this binary demands an exact `S7:` count (18/17,
   19/18) and the frozen twin fails any `ERR:` line. So the spec's "i8042
   self-test and mouse reset lines" are `i8042: self-test ok` and `i8042:
   mouse reset ok` (or `i8042: mouse none` for a keyboard-only machine — a
   line, not an error, the boot continues); a controller that fails its
   self-test or never empties its input buffer is `ERR: i8042 …` and a halt.
   `S7: edid none` replaces `S7: edid WxH` one for one. The 7c checker counts
   19 and 18 `S7:` lines exactly as `checkwire` does and finds the two
   `i8042:` lines by their own pattern, in order, before `keyboard ready`.
4. **The cold init stays where `mouse_init` is called today** — after the
   glass core, just before `S7: keyboard ready` — not "before the disk" as
   the spec's prose orders the first boot. The `S7:` order is unchanged
   because the new lines are not `S7:` lines; moving the i8042 above the disk
   would reorder nothing observable and would put controller I/O before
   `pic_init` for no criterion.
5. **The stick is proven from the file `mkstick.py` wrote, before any boot,
   and every boot is of a copy.** OVMF writes `NvVars` to the first FAT
   volume on every boot (the ring 7a gotcha); with no `esp.img` on SATA that
   volume is the stick's ESP, so "`stick.img` byte-identical after a boot" can
   never be a criterion. Test 1 parses `stage7/out/stick.img` as built; the
   gate and the owner's windowed run boot copies under `stage7/out/metal/`
   (QEMU's image lock, and the owner flashes the file as built). What the
   guest must never do to the stick copy *is* asserted: its GPT header and
   entries are unchanged after every boot (the AHCI driver never sees a USB
   disk; a table written there would be a driver writing where it must not).
6. **Test 3 is one scripted run of two boots at `-smp 4`**, because "Stage 3's
   note across a reboot" needs a reboot and "ring 6b's no-broker launch"
   needs the broker off: boot A with the relay and the mock — Stage 2's
   typing and the note, Stage 4's `? ping`, ring 6a's `! test app` in its
   panel, ring 6b's `! install echo` rehearsed against the plan's tests in
   `wire.py`'s twin; boot B with 9999 and 9997 closed — the note back on
   screen (Stage 3), the arrow on the first move and **a click on `! echo`
   on the choices row launching it from the home partition** (ring 6c's
   click and ring 6b's launch in one act), a key to it, Esc. "Stage 5's grow"
   is ring 6a's `! test app`, as ring 7b's deviation 4 settled. The checkers
   are reused through their seams; only what is bound to a device is
   transcribed.
7. **Test 4's guest-free half is the payload table and the argv checks; the
   relay's grace close and `chart.py` are proven by their items' probes, not
   by the frozen gate.** The relay is unfrozen and held to `WIRE.md` by the
   frozen `checkwire`; the grace close changes no line of that contract and
   `WIRE.md` is not edited, so a criterion for it would have no frozen
   document — it is recorded in `METAL.md` and `HANDOVER.md` with its host
   proof quoted. `chart.py` reads a port the twin does not have.
8. **A short bound in the mode loop** (fact C's recommendation): a mode whose
   cell count exceeds `SHADOW_SIZE` is skipped before the area compare. One
   compare and the arithmetic to feed it. Insurance against a GOP that lists
   a mode the console cannot hold; measured harmless in the twin (no listed
   mode is over 2048×2048).
9. **`I8042_WAIT_TRIES` may rise from 50 to 100** (one second per answer, up
   from half) if item 1's timing or the spec's "real latency" risk argues for
   it: a PS/2 mouse's self-test after `0xFF` is specified at up to 500 ms,
   and half a second is the whole of today's bound. A missing mouse then costs
   at most three seconds at boot, once. Decided at item 8 from item 1's
   numbers, recorded in `HANDOVER.md`.
10. **The artefact is ring 7b's closed binary until item 7**, so test 1 (the
    stick) is green from item 3 and tests 2–3 are red on it: `S7: edid WxH`
    on virtio-vga instead of `edid none`, no `i8042:` lines. Test 4 is red on
    the hook as it stands (the words allowed today).
11. **`stage7/checkmetal.py` is the checker's name**; measured to collide
    with no frozen basename (`checkmetal.py` is not `metal.py` to the hook's
    resolver, and `METAL.md` is not either — case-sensitive). No new frozen
    document: the lines this ring adds are `i8042:` and `edid none`, and their
    text lives in the checker's patterns and in `METAL.md`, which the owner
    reviews and which is not a criterion.

---

## Decisions taken in this plan

1. **The serial lines and errors.** Before `S7: keyboard ready`, after
   `S7: glass core N`:
   ```
   i8042: self-test ok
   i8042: mouse reset ok        (or: i8042: mouse none)
   ```
   `S7: edid none` in place of `S7: edid WxH` on any display but QEMU's VGA.
   The named errors, halting as `serial_err` does: `ERR: i8042 self-test
   failed` (`0xAA` not answered by `0x55` within the bound, or not answered at
   all), `ERR: i8042 input buffer never emptied` (`i8042_wait_ibf`
   exhausted), `ERR: ahci port N did not come up after spin-up` (decision 4).
   `mouse none` covers every mouse-side failure: no `FA`, no `AA`, no ID —
   the boot continues with `mouse_id` 0, as GLASS.md's rule already says.
2. **The EDID guard and the mode bound** (`stage7/stage7.asm`, item 7).
   `edid_read`, at `.fn`: register 0's `EAX` (device in the high word,
   vendor in the low) is saved in `R10D` before the class read; after the
   class matches `0x0300`, `cmp r10d, 0x11111234` — equal, and BAR2 is read
   as today; not equal, `jmp .none`, which prints `S7: edid none` and leaves
   `edid_w`/`edid_h` 0 so the mode loop's preferred-mode compare never
   matches. Nothing else in `edid_read` changes; the 7a and 7b gates boot
   QEMU's VGA and keep seeing `WxH`. In `.mode_loop`, after the zero checks
   on `EAX` (width) and `ECX` (height): `mov edx, eax; shr edx, 4; mov r8d,
   ecx; shr r8d, 4; imul edx, r8d; cmp edx, SHADOW_SIZE; ja .free_and_next`
   — a mode the shadow cannot hold is never a candidate, so `err_shadow` can
   only fire on a firmware that lists no mode at all that fits, and
   `err_no_mode` names that case first.
3. **The i8042 cold init** (`mouse_init`, item 8). The sequence becomes:
   `0xAD`, `0xA7`, drain; **`0xAA` to `0x64`, `i8042_read`** — a timeout or
   any byte but `0x55` is `ERR: i8042 self-test failed`; **`i8042: self-test
   ok`** (`serial_puts` — before `keyboard ready` the tee is the log, and the
   line lands in the console's boot replay like every other); then the
   command byte read (`0x20`), bits 0–1 set, 4–5 cleared, written (`0x60`),
   read back, `0xA8` — exactly as today, now *after* the self-test so a reset
   of the command byte by the self-test cannot undo the write; **a timeout on
   the command byte read is `ERR: i8042 self-test failed`'s sibling: the
   controller answered `0x55` and then nothing — named, not `jc .done`**
   (`ERR: i8042 command byte not answered`); then the mouse: `0xFF`, `FA`,
   `AA`, the ID as read — every mouse-side `jc`/mismatch goes to a `.no_mouse`
   label that prints **`i8042: mouse none`** and continues; success prints
   **`i8042: mouse reset ok`** after the ID byte lands in `mouse_id`, then
   `0xF6`, `0xF4` (a failure of those two is `mouse none` too, `mouse_id`
   reset to 0 so the page tells the truth), drain. `i8042_wait_ibf` gains the
   named error on exhaustion: `ERR: i8042 input buffer never emptied`. The
   obs page's `i8042_cmd` keeps GLASS.md's meaning — as read (after the
   self-test), as written. Nothing in the interrupt path changes.
4. **`PxCMD.SUD` under `CAP.SSS`** (`disk_select`, item 9), the AHCI 1.3
   spec's own sentence (§10.1.2, staggered spin-up): if `CAP` bit 27 is set,
   for each implemented port, before its `PxSSTS` is looked at, set `PxCMD`
   bit 1 (`SUD`); then the probe loop as today, but under `SSS` the bound is
   `AHCI_SPINUP_TRIES` (50000 × 200 µs, ten seconds — a disk spinning up from
   rest, the spec's worst case) instead of one second, and **a port whose
   `DET` was non-zero after `SUD` and never reached `3` within the bound is
   `ERR: ahci port N did not come up after spin-up`** — a device present that
   will not talk is a named halt, never a silent skip; a port whose `DET`
   stays `0` is passed as today (nothing is plugged into it; the HP's five
   empty ports must not stall the boot). With `SSS` clear — the twin — the
   code path is the existing one, unchanged to the byte. `PXCMD_SUD` and
   `AHCI_SPINUP_TRIES` join the defines. **Said plainly: this path runs only
   on the HP, and the first boot's `S7: disk` line (or its absence) is its
   test.**
5. **The relay's grace close** (`broker/relay.py`, item 10). In `handle`:
   after `t_down.join()` (the broker has finished; its bytes are forwarded
   and the guest side has had `SHUT_WR`), `up_done.wait(GRACE)` with `GRACE
   = 2.0` s; if the up pump has not seen the guest's EOF by then, `quiet(conn.
   shutdown, SHUT_RDWR)` and `quiet(conn.close)` — the up pump's `recv` ends,
   the thread finishes, `t_up.join()` returns, the log line is written with
   the bytes as counted and `error` **null** (the exchange completed; the
   guest's silence after the answer is not an error), and a stderr note
   `closed the guest side after the grace`. Nothing in `WIRE.md`'s five
   fields or its listening line changes. Proven on the host at item 10 with
   `stage7/out/probe7c/relay_grace.py`: the mock on 9999, the relay on 9997;
   client one sends `ping`, reads `pong` whole and **holds the socket open
   without closing**; client two connects within the grace plus a second and
   is answered; the log's first line `up 8 down 8 error null`; a client that
   closes normally is logged at once, as before; the ring 7b proof's cases
   (the bind rule, a refused broker, the port clash, the restart in
   TIME_WAIT) re-run unchanged.
6. **`broker/chart.py`** (item 11), standard library only, ~80 lines:
   `python3 broker/chart.py <port> <logfile>`; opens the port `O_RDWR |
   O_NOCTTY`, `termios.tcsetattr` to raw — `B115200` in and out, `CS8`,
   `CREAD | CLOCAL`, `PARENB`, `CSTOPB`, `IXON/IXOFF`, `ICANON`, `ECHO`,
   `ICRNL`, `OPOST` all clear, `VMIN` 1, `VTIME` 0; reads bytes, splits on
   `\n`, strips `\r`, decodes with replacement, prints each line to stdout as
   it is and appends `<ISO-8601 local time, milliseconds> <line>` to the log
   file, flushed per line; a partial line at exit is written too; Ctrl-C
   ends it with the file closed; a port that cannot be opened is a loud exit
   2 with the reason. Its usage text names the adapter's usual path once,
   inside the file (written by the Write tool, so the hook never sees the
   word in a command). Proven at item 11 with `stage7/out/probe7c/chart_proof.py`:
   `pty.openpty()`, `chart.py` started on the slave's name as a subprocess,
   three lines written to the master (`S7: alive`, one with a stray `\r`, one
   with a non-UTF-8 byte), stdout and the log file compared line for line,
   the timestamp's shape checked by regex, SIGINT delivered and the file
   complete.
7. **The bodyguard, extended** (`.claude/hooks/protect-tests.py`,
   `payloads.py`, item 13). Three changes, each mechanical:
   - **`DEV_ALLOWED`** narrows `tty\w*` to `tty` — `/dev/tty` (the terminal)
     stays a harmless sink; `/dev/ttyUSB0`, `/dev/ttyS0` and every named
     terminal are denied. `pts(?:/\d+)?` stays.
   - **The `/dev` spellings.** Before `DEV_MENTION` runs, the command is
     normalised for the bodyguard's eyes only: every `'`, `"` and `\` deleted,
     `$'` removed, runs of `/` collapsed to one, `/./` collapsed to `/`; then
     every `/dev` token — `DEV_MENTION` becomes `/dev(?:/[\w./+-]*)?` so a
     bare `/dev` is a mention too — must match `DEV_ALLOWED`. The table's
     denials: `/dev/sda`, `//dev/sda`, `/dev//sda`, `/dev/./sda`,
     `/dev/disk/by-id/usb-x`, `/dev/serial/by-id/x`, `"/dev"/sda`,
     `"/dev/sda"`, `'/dev/'sda`, `/de\v/sda`, `\/dev\/sda`, `$'/dev/sda'`,
     bare `/dev`, `/dev/`, `/dev/ttyUSB0`, `/dev/ttyS0`, `/dev/ttyACM0`; the
     allowances: `/dev/null`, `/dev/zero`, `/dev/urandom`, `/dev/random`,
     `/dev/stdin`, `/dev/stdout`, `/dev/stderr`, `/dev/fd/0`, `/dev/tty`,
     `/dev/pts/3`, `</dev/null` and `2>/dev/null` as the gates write them,
     `"/dev/null"` quoted. (`/DEV` is not a Linux path and is not matched;
     said in the hook's comment.)
   - **The metal's words**, a new tuple `METAL_WORDS` judged like
     `STORAGE_VERBS`, prose included: `\bdd\b` ("the flash's verb"; `add`,
     `odd`, `dd-` inside a longer word stay allowed by the boundaries),
     `\bof=`, `\bby-id\b`, `\bttyUSB`, `\bnmcli\b`. **Consequence, stated:**
     the payload table's Stage 3 allowance `dd if=/dev/zero of=stage3/out/x.img
     …` flips to a denial with its label rewritten ("dd is the flash's verb
     from ring 7c; the builders run it inside their scripts, never at the
     prompt") — every `mkimage.sh` keeps its `dd`, unseen by the hook; a
     probe that needs bytes from an image uses Python or `xxd`/`cmp`, as the
     7a and 7b probes did. `lsblk` stays allowed (it writes nothing and the
     spec's step 1 is the owner's; CC has no reason to run it and the plan
     does not).
   - **The table gains** the ring 7c group: `freeze_cases` on
     `stage7/test-7c.sh` and `stage7/checkmetal.py` (item 6), the
     `write`/heredoc/`sed -i` denials on each, the spelling and word denials
     above, and the allowances measured before the plan and at item 1 —
     `Write` on `stage7/mkstick.py`, `broker/relay.py`, `broker/chart.py`,
     `stage7/METAL.md`, `stage7/stage7.asm`, `stage7/mkimage.sh`,
     `stage7/plan-7c.md`; `python3 stage7/mkstick.py`; `python3
     broker/chart.py` bare; `./stage7/test-7c.sh`; the checker's modes; the
     stick's mtools lines (`mformat`, `mmd`, `mcopy`, `mdir`, `mtype` with
     `@@`); `cp stage7/out/stick.img stage7/out/metal/stick.blank.img`; the
     gate's stick boot (`qemu-xhci`, `usb-storage`, `file=` under out/, no
     ESP drive, the SATA disk, the e1000e cage to 9997); the `novga` boot
     (`-device virtio-vga,edid=on`); the twin's four-device line as `wire.py`
     builds it, unchanged; the oracle's windowed line; `rm -rf stage7/out/metal
     stage7/out/probe7c`; `git add` of the two frozen paths and the hooks;
     `write("stage8/test-7c.sh")`, `write("stage8/checkmetal.py")`,
     `write("stage8/METAL.md")`; prose with `usb-storage`, `xhci`, `stick`,
     `mformat`, `@@offset` — and the denials: a stick drive whose `file=` lies
     outside `out/`, `-drive` with `file=stage7/out/stick.img` (the file as
     built, never booted — a plan rule, not a hook rule: allowed by the hook,
     listed in the table as allowed, forbidden by the gate's own strings),
     a shorthand. 0 wrong or exit 1, immediacy demonstrated live with one
     denied call.
8. **`stage7/mkstick.py`** (item 2, unfrozen — the builder), standard
   library plus mtools, ~120 lines: reads `stage7/out/BOOTX64.EFI` (built by
   `mkimage.sh`; refuses if absent), writes `stage7/out/stick.img`:
   `STICK_SECTORS = 135168` (66 MiB), the ESP at LBA `2048` for `131072`
   sectors (the spec's 64 MB), the protective MBR (one `0xEE` entry from LBA
   1 to the end, `0x55AA`), the GPT header at LBA 1 and its backup at the
   last LBA, the entry array (128 entries × 128 bytes, 32 sectors) at LBA 2
   and before the backup, one entry with the ESP type GUID
   `C12A7328-F81F-11D2-BA4B-00A0C93EC93B`, a fixed partition GUID, the name
   `EFI System`; CRC32 of the array and of the header with its own CRC field
   zeroed — `metal.crc32`, `guid_bytes`, `gpt_header`'s shape reused by
   import where the shape fits (the disk GUID and the entries differ, so the
   header is built here; DISK.md's Python is not edited). Then `mformat -i
   stick.img@@1048576 -F -T 131072 -v GERMOS ::` (the exact flags as item 1
   measured them), `mmd ::/EFI ::/EFI/BOOT`, `mcopy BOOTX64.EFI
   ::/EFI/BOOT/BOOTX64.EFI`, all at the offset, all under `out/`; prints the
   size and the partition's LBAs; exit 0 only if `mdir` at the offset lists
   the file. No loop device, no `/dev`, no root.
9. **The harness — `stage7/test-7c.sh` and `stage7/checkmetal.py`** (items
   3–5, frozen at item 6), ring 7b's shape; the scratch `stage7/out/metal/`.
   - **`test-7c.sh`**: refuses to run while 9999, 9998 or 9997 is held;
     wipes `stage7/out/metal/germline` and `rehearsal`; builds with
     `mkimage.sh` **then `mkstick.py`**; spells once — the machine and display
     as 7b's, `CAGE_NETDEV`/`CAGE_DEVICE` as 7b's (the relay on 9997),
     `sata_drive`, **`stick_drive() { -device qemu-xhci -drive
     if=none,id=stick,format=raw,file=<copy> -device usb-storage,drive=stick }`**,
     **`NOVGA="-vga none -device virtio-vga,edid=on"`**; `fresh_disk`;
     `fresh_stick <copy>` (a copy of `stage7/out/stick.img`); every boot
     `timeout -k 5 <T>` with `T` from item 1's measurement, exit 124 the
     expected outcome; **no `-drive format=raw,file=…esp.img` on any 7c
     line** (asserted in test 4's string checks).
   - **Test 1** (`test-7c.sh`, then `checkmetal.py --stick`): the standing
     PE32+ checks on `stage7/out/BOOTX64.EFI` (7b's, verbatim); then the
     stick parsed from the host, no boot: sector 0's signature and one `0xEE`
     protective entry starting at LBA 1; the primary and backup GPT headers
     by `metal.parse_header`'s rules (signature, revision, size, CRC, LBAs
     agreeing), the entry array's CRC; **exactly one used entry**, type
     `C12A7328-F81F-11D2-BA4B-00A0C93EC93B`, first LBA 2048, last LBA
     133119 (2048 + 131072 − 1, the spec's 64 MB, written as the constant
     the builder and the checker both name), the rest of the array zero;
     `metal.classify` on the image says `gpt` (a table that is not GermOS's —
     the AHCI driver would refuse it, which is right: the stick is never a
     data disk); `mdir -i stick.img@@1048576 ::/EFI/BOOT` lists `BOOTX64
     EFI`; `mtype` at the offset extracts it **byte-identical to
     `stage7/out/BOOTX64.EFI`**.
   - **Test 2** (`checkmetal.py --serial <mode> <smp>`): three boots, each
     from a fresh copy of the stick, the SATA disk on `ide.1`, the e1000e cage
     to 9997 (the relay not needed — nothing is asked), `-display none`.
     **`blank` at `-smp 8`** on a fresh disk: nineteen `S7:` lines in order
     (7b's `PATTERNS_BLANK` with the EDID pattern accepting `WxH` or `none`;
     under QEMU's VGA the `WxH` form is demanded and equal to the gop line, as
     7b), `S7: disk port 1 …`, found = woken = 8, the nic line the HP's MAC,
     `link up`; **the two `i8042:` lines** — `i8042: self-test ok` then
     `i8042: mouse reset ok` (the twin has a mouse), each exactly once, in
     that order, after `S7: glass core` and before `S7: keyboard ready`, and
     no `i8042:` line anywhere else; no `ERR:`; the disk from the host
     byte-exact by the frozen `checkdisk.check_formatted`; **the stick copy's
     GPT unchanged** (LBA 1 and the entry array and the backup compared to
     the built stick's) while its FAT may differ (OVMF's `NvVars`, deviation
     5). **`again` at `-smp 4`** on the same disk: eighteen lines, the disk
     byte-identical after. **`novga` at `-smp 2`** on a fresh disk with
     `NOVGA` in place of the VGA device: `S7: edid none` second, the gop line
     `WxH` **equal to the highest mode measured at item 1** (the one literal,
     from a run), the console line `W/16 x H/16`, the rest as `blank`; a
     screendump whose size is that mode (the frozen `check_region_rows` on the
     conversation panel showing the prompt, so the picture is drawn at that
     geometry). Each boot's ready window from item 1's measurement.
   - **Test 3** (`checkmetal.py --stages`, deviation 6), `-smp 4`, the relay
     on 9997 logging, the mock `broker/wire.py --mock` on 9999 with the metal
     germline wiped (a transcription of `checkwire.start_mock` bound to
     `stage7/out/metal/` — `GERMLINE`, `REHEARSAL`, the record), a fresh
     disk, a fresh stick copy, QEMU's VGA. **Boot A:** `first note` ⏎ (Stage
     2's typing: the echo on serial and the line in the conversation panel);
     `? ping` ⏎, `wait_record` 1 (Stage 4); `! test app` ⏎, `wait_record` 2
     (150 s), `k`, screen A, Esc (ring 6a); `! install echo` ⏎, `wait_record`
     3 (150 s), Esc (ring 6b); obs E. Judged: nineteen lines with the two
     `i8042:` lines; the echo the four typed lines; the record's three
     entries — `check_question_entry` (`ping`), `check_grow_entry` (`test
     app`, generated, calls 1, `["pass"]`), `check_install_entry` (`install
     echo`, generated, calls 2, `["pass"]`, the plan's verdicts) — the call
     numbers by the record's own rule (the mock's running total of
     *generation* calls: the question is not one); the relay's log three
     entries, `up`/`down` by `question_bytes("ping")` and the two frame
     lengths, `error` null, as many as the record; the germline exactly two
     entries by the frozen `_7b` transcriptions (nineteen-line rehearsal logs
     with `link up`, the virtio image untouched — the twin is `wire.py`'s,
     unchanged); the notes partition `["first note"]`; the home partition
     holding echo at `DATA_FIRST` hash-checked (`check_partitions`); screen A
     by `check_app_panel` (`k`) and `check_mode_field` `running test app`;
     obs E: `questions 1`, `notes 1`, `wire_conns` = the relay's count,
     `grows_generated 2`, **`grows_served 0`** (GLASS.md: frames whose
     `source` is 1; both came generated — ring 7b item 10b's rule, looked up,
     not computed), `errors 0`. **Boot B**, 9999 and 9997 asserted closed,
     the same disk and stick copy: obs R; the arrow — `("mouse", 1, 0)`, the
     `S7: mouse ready` line once after ready (the `strip_mouse_line` idiom);
     `("moveto", crow, target_col(choice_targets(False, 0, [], ["echo"]),
     "launch", "echo"))`, a click; 2 s; `b`; park; screen L; obs L; Esc.
     Judged: eighteen lines with `S7: notebook 1 notes`, `S7: home 1 apps`;
     the echo empty but the `b` (a click types nothing; the launch is the
     click's); the conversation panel showing `first note` above the prompt
     before the launch (a screendump before the click, `check_region_rows`
     with `["first note", PROMPT]` — Stage 3); `check_one_cell_panel` `b`,
     `check_mode_field` `running echo`, `check_choices` with
     `CHOICES_ECHO_RUNNING`; obs L: `mode 3`, `name echo`, `wire_conns 0`,
     `clicks 1`, `hits 1`, `packets` = the model's count, `bytes_in`/`out`
     equal to obs R's; the pointer field on the strip by
     `checkpointer.POINTER_FIELD`'s regex against the page; the disk
     byte-identical to after boot A; the stick copy's GPT unchanged. The
     obs page is parsed by the frozen `pointer.parse_obs_6c` (the 6c section's
     page, which DISK.md extended — `OBS_PAGE_BYTES` per DISK.md's table).
   - **Test 4** (`test-7c.sh`'s self-assertions, then `checkmetal.py
     --cage`): **(a)** the harness's own strings — the cage as 7b's (one
     `guestfwd` to `nc -N 127.0.0.1 9997`, `restrict=on`, no `hostfwd`, the
     e1000e with the HP's MAC), the machine, the display, the SATA disk, **the
     stick line** (`qemu-xhci`, `usb-storage,drive=stick`, the drive's file
     under `stage7/out/metal/` and not `stage7/out/stick.img` itself), **no
     `esp.img` in any 7c QEMU line**, the `NOVGA` string; **(b)** the argv
     checks — the checker's own command (a `check_argv_7c`: one netdev to
     9997, four devices: the display, the xhci, the usb-storage, the `ide-hd`
     on `ide.1`, the e1000e on `n0`; two drives, both under `stage7/out/`,
     neither virtio, neither `esp.img`; `-cpu IvyBridge`) and **the twin's as
     `wire.py` builds it through the frozen `checkwire.check_argv_7b`**,
     unchanged from 7b; `wire.LINES == len(PATTERNS_BLANK)`, `twin.DEFAULT_PORT
     == 9998`, `wire.RELAY_PORT == 9997`; **(c)** the relay's bind battery
     (`checkwire.check_bind_rule`, frozen, reused); **(d) the payload table:
     `python3 .claude/hooks/payloads.py` run as a subprocess, exit 0
     required, and its last line parsed for `0 wrong`; plus the checker's own
     spot checks fed to the hook from a list held as data** — the spellings
     and words of decision 7 (denied) and the harmless five (allowed) — so a
     hook that regresses is a red gate whatever the table says.
   The gate's cost: five boots (three in test 2, two in test 3) plus two
   rehearsals; measured at item 8 and written from that run.
10. **`stage7/METAL.md`** (item 12, unfrozen, the owner's document), in the
    spec's step order with the kickoff's additions, every command copied from
    the files as they exist:
    0. **Once, before the day:** `sudo usermod -aG dialout $USER`, log out
       and in; `python3 stage7/mkstick.py` after `./stage7/mkimage.sh` on
       the commit the gate passed; `./stage7/test-7c.sh` green.
    1. The stick into mlrig; `lsblk -o NAME,SIZE,MODEL,TRAN` — the one line
       with `usb` under TRAN; every other line is mlrig, never a target.
    2. `ls -l /dev/disk/by-id/ | grep usb` — the `usb-…` name; the by-id
       path is the only path used, never `sdX`.
    3. `sudo dd if=stage7/out/stick.img of=/dev/disk/by-id/usb-<name> bs=4M
       conv=fsync status=progress`, `sync`, unplug. (The file as built —
       never a copy the twin has booted, which carries OVMF's `NvVars`.)
    4. The SATA drive fitted (any size over 64 MB, wiped by the first boot);
       the null-modem cable COM A ↔ the adapter on mlrig; Ethernet into the
       home switch; PS/2 keyboard and mouse; the monitor on VGA or
       DisplayPort.
    5. On mlrig: `nmcli device status` and `nmcli connection show` to name
       the LAN port's connection; `nmcli con mod <name> +ipv4.addresses
       10.0.2.4/24 && nmcli con up <name>`; **the fallback** for a port
       NetworkManager does not manage: `sudo ip addr add 10.0.2.4/24 dev
       <port>`; `ip -4 addr show <port>` shows both addresses. Three
       terminals at the repo root: `python3 broker/wire.py`; `python3
       broker/relay.py` (no flags: `10.0.2.4:9999 → 127.0.0.1:9999`, its
       listening line quoted); `python3 broker/chart.py /dev/ttyUSB0
       stage7/out/metal.log` (started before the HP is powered on, so
       `S7: alive` is the first line in the file).
    6. Power on; F9 if the stick is not first; the UEFI USB entry.
    7. **The first boot, line by line — the debugging table:** no line at all
       → the code died before `serial_init` returned (the stick did not boot
       GermOS, or COM A is not COM1 at `0x3F8`: check the BIOS's serial
       setting and the cable); `S7: alive` then a black screen and nothing
       more → GOP or the mode (`S7: edid none` missing: `edid_read`; `S7: gop`
       missing: no 32-bit linear mode or the shadow bound); `S7: gop` then
       nothing → `ExitBootServices` or paging; through `S7: idt ready` then
       nothing → the APs (the x2APIC path or the trampoline, the spec's
       unproven pair); `S7: console` then nothing → the AHCI (`CAP.SSS`,
       decision 4; `ERR: ahci …` names the port); `S7: home` then `ERR: nic
       link did not come up within 10 s` → the 82579LM's PHY (the spec's high
       risk: the fix is a ring item with the datasheet); `S7: glass core` then
       `ERR: i8042 …` → the controller (the named line says which step);
       `i8042: mouse none` → no mouse answered; the boot continues; `S7:
       keyboard ready` and no prompt on the monitor → the glass core's
       framebuffer (uncached mapping, stride) — the serial log is complete and
       the screen is the bug.
    8. Test 5's steps in order: the lines in the twin's order; the glass at
       the native mode; a note; power off, on, the note back; `? ping`
       (the relay's terminal logs one connection); `! install calculator`
       (the real broker over the LAN, the twin rehearsing on mlrig); power
       off, broker and relay stopped, power on, `! calculator` from the SATA
       disk; a click on the choices row.
    9. Afterwards: the photograph of the screen and `stage7/out/metal.log`
       copied into `history/` as `2026-MM-DD-ring7c-<what>.png` and
       `2026-MM-DD-ring7c-serial.log`; the relay's terminal output kept.
    Plus one paragraph each on the relay's grace close and on what the twin
    could not prove (the PHY, the i8042's timing, AMI's GOP, `SSS`).
11. **The freeze boundary** (item 6): `stage7/test-7c.sh`,
    `stage7/checkmetal.py`. Not frozen: `stage7/METAL.md`, `stage7/mkstick.py`,
    `broker/relay.py`, `broker/chart.py`, `stage7/mkimage.sh`,
    `stage7/stage7.asm`, `broker/claude_backend.py`, `stage7/plan-7c.md`.
    No broker module is new this ring: the mock is `broker/wire.py --mock`,
    frozen at ring 7b. Everything frozen before stands. The "next stage's test
    file" case stays `stage8/test.sh`.
12. **The three commands for the HP's day** (test 5), from the repo root, in
    three terminals — `METAL.md` step 5, `HANDOVER.md`'s Next action:
    ```
    python3 broker/wire.py
    python3 broker/relay.py
    python3 broker/chart.py /dev/ttyUSB0 stage7/out/metal.log
    ```
    and **the windowed twin of the HP** (for `CLAUDE.md`'s build block, the
    stick over USB, the relay on 9997; the stick copied because QEMU writes
    OVMF's `NvVars` into whatever it boots and the owner flashes the file as
    built):
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
    with `python3 broker/wire.py` and `python3 broker/relay.py --bind
    127.0.0.1 --port 9997` beside it. The spec's 9998 is corrected to 9997
    (deviation 1).
13. **The prose the hook will dislike.** From item 6 the new frozen basenames
    (`test-7c.sh`, `checkmetal.py`) enter the prose rule; from item 13 the
    metal's words and every `/dev` spelling are denied in every Bash command,
    prose included. Commit messages by `-F` from a file written with the
    Write tool; `METAL.md` and `chart.py` written and edited with the Write
    and Edit tools only; a grep that needs one of the words is reworded
    (`grep -n "by-" …` is allowed; `by-id` is not).
14. **Carried, for the HP's day and after:** everything ring 7b carried (the
    82579LM's PHY; legacy descriptors, no link-change handling; plaintext on
    the home LAN; TLS at Stage 8); `SSS` written to the spec and unexercised;
    the i8042's real timing; AMI's GOP's mode list; the x2APIC path and the
    trampoline (test 2 on the HP will say); the N-of-1 trials ring after the
    metal.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are expected green at its commit and which
  are red by design**. Items 0–2 have no ring 7c test; items 3–6 commit with
  test 1 green and tests 2–4 red by design; item 7 adds test 2's `novga`
  boot; item 8 turns tests 2 and 3 green; items 9–12 keep them; item 13 turns
  test 4 green; from item 13 all four must be green before the commit.
- **`./stage7/test.sh` and `./stage7/test-7b.sh` stay green on this ring's
  binary throughout** — the regressions the kickoff names — and
  `./stage0/test.sh` … `./stage5/test.sh`, `./stage6/test.sh`,
  `./stage6/test-6b.sh`, `./stage6/test-6c.sh` stay green on their own
  binaries: the two Stage 7 gates before the item 7, 8, 9 commits, the whole
  chain before the item 13 and item 14 commits (each needs 9999 free, most
  9998 too; no two gates at once). Nothing this ring writes is read by any of
  them.
- `HANDOVER.md` is updated as we go, with a final pass at item 14; the
  model-and-effort record (**Fable 5.1 at medium effort**, the owner's
  decision in the spec) goes in at item 0.
- Every new fault class earns a CLAUDE.md gotcha line; the second time a
  mistake is corrected its line goes in.
- Temporary probes are never committed and never undone with `git checkout
  --`: copy aside, restore from the copy. Every probe boots a private copy
  under `stage7/out/probe7c/` (QEMU's image lock; several probes, several
  copies; the stick copies too).
- **The scope guard** governs items 7–14: two honest attempts at any one
  obstacle — a real diagnosis from the serial log, the relay's log, the
  rehearsal log, the obs page, a screendump or a register dump, not a re-run
  — then stop, record the exact state in `HANDOVER.md`, commit that, and
  wait for Wajira. A frozen file that needs to change is never edited: the
  diff is written unapplied under `stage7/out/`, recorded, and the owner
  applies it.
- **Everything runs inside QEMU with the caged network, the VGA device (or
  virtio-vga for the one `novga` boot), the IvyBridge CPU, and the stick
  over `qemu-xhci`.** The only disks are raw files under `stage7/out/` (the
  gate's under `stage7/out/metal/`, the twin's under
  `stage7/out/metal/rehearsal/twin/`, the probe's under `stage7/out/probe7c/`),
  created fresh by the harness, the broker or the probe. The broker and the
  twin's listener bind `127.0.0.1` only; the relay binds `127.0.0.1` in this
  ring's twin and refuses every other address but the HP's `10.0.2.4`. CC
  never spells a `/dev` path, never runs `dd`, never flashes anything: the
  stick is a file until the owner's hand. Nothing outside the repo is
  written, bar scratch files in the session temp directory. **No real Claude
  call is made by this session**; test 5 is Wajira's, on the HP.
- If the owner says the session budget is nearly spent: finish the current
  item, commit, record the exact state in `HANDOVER.md`, stop.

---

# Part 1 — the builder and the acceptance machinery, written before the code

## Item 0 — this plan committed; ring 7c opened in HANDOVER

Copy this file verbatim to `stage7/plan-7c.md` and commit it. The first act
after the gate opens. Record in `HANDOVER.md` that **ring 7c, the metal,
opened on Fable 5.1 at medium effort, the owner's decision in the spec**; the
"Where we are" table's stage, status and model rows say so; a "Ring 7c — the
metal" section in the shape of ring 7b's, with the shape from the plan, an
empty test table, the carried notes from 7b's handover (`CAP.SSS`, the ports
as A5 settled them with the spec's 9998 corrected to 9997 and why, the
relay's one item) in its caveats.

*Expected at commit:* no ring 7c tests exist yet. Stages 0–7b green
(unchanged).

## Item 1 — the environment measured: the stick over USB, the display that is not QEMU's VGA, `CAP`, the i8042's answers, the pty, the spellings

The six measurements listed under "To be measured at item 1", on private
copies under `stage7/out/probe7c/`: the hand-built stick and the closed
binary booted from a copy of it over USB at `-smp 2`, `4` and `8` with the
times to `alive` and `ready`; the virtio-vga (and cirrus) probe — vendor,
device, BAR2, OVMF's mode list, the highest mode and whether it fits the
shadow, what today's `edid_read` prints; `CAP` and port 1's `PxCMD` through
the monitor; the i8042's self-test answer, the command byte after it and the
mouse's reset timing; the pty's termios; the spelling table through a scratch
payload script. The values go into `HANDOVER.md`'s environment table; the
`novga` mode, the ready window and `I8042_WAIT_TRIES`'s fate are decided here
and written down before item 3 writes a string. The probe is removed; `git
diff` shows only `HANDOVER.md`.

*Expected at commit:* no ring 7c tests yet. Everything green as before.

## Item 2 — `stage7/mkstick.py`

Decision 8 in code, with item 1's mtools flags. Proven on the host, no boot:
`stage7/out/stick.img` written; `xxd` on sector 0 and LBA 1 quoted;
`metal.classify` says `gpt`; `mdir` at the offset lists `BOOTX64 EFI`;
`mtype` at the offset extracts the build byte for byte (`cmp`); a run with
`BOOTX64.EFI` absent exits 1 with a message and writes nothing; a second run
overwrites cleanly.

*Expected at commit:* no ring 7c tests yet.

## Item 3 — `stage7/test-7c.sh` with test 1, and test 2's three boots

Decision 9's harness: the port refusals, the build (`mkimage.sh` then
`mkstick.py`), the strings, the stick and disk helpers, test 1 (the PE checks
and `checkmetal.py --stick` — the checker's first mode, written here) —
green, since the stick is the build's; test 2 calling `checkmetal.py --serial
blank 8`, `again 4`, `novga 2` — the checker's `qemu_argv` (the stick copy
over xhci, the SATA disk, the e1000e cage, the display chosen by mode), its
`drive` (checkwire's shape plus checkpointer's mouse steps — `mouse`,
`moveto`, `button` — and a `serial` read), its pattern lists (7b's with the
EDID pattern widened, the `i8042:` pair found by their own regex), its
`check_boot_lines`, its stick-GPT-unchanged check; the frozen `--formatted`
around the `blank` boot.

*Expected at commit:* **test 1 green**; **test 2 red** — `blank` and `again`
lack the `i8042:` lines; `novga` prints `S7: edid WxH` from virtio-vga's own
EDID instead of `edid none`; the non-zero exit quoted in the commit message.

## Item 4 — `checkmetal.py --stages` (test 3)

Deviation 6's two boots: the relay and the mock lifecycle bound to
`stage7/out/metal/`, the steps, the judgements through the frozen seams, the
click on `! echo` from `choice_targets` with `installed=["echo"]`, the mouse
line stripped, the obs page by `parse_obs_6c`; `test-7c.sh` gains test 3.

*Expected at commit:* test 1 green; **tests 2–3 red** — boot A's line check
wants the `i8042:` pair; everything else in test 3 passes on ring 7b's binary
(the twin, the install, the click), which is the point: the ring adds two
lines and a guard and takes nothing away. The output quoted.

## Item 5 — `checkmetal.py --cage` and test 4's self-assertions

Decision 9's (a)–(d): the harness's own strings, `check_argv_7c` and the
frozen `check_argv_7b` on the twin's command, the frozen bind battery, the
payload table as a subprocess plus the spot checks held as data; `test-7c.sh`
gains test 4. Proven on the host: both argv checks pass on the real commands
and name a stray `esp.img` drive, a missing xhci, a third device; the spot
checks name today's allowances (`ttyUSB0`, `by-id`, `dd`) as the failures.

*Expected at commit:* test 1 green; tests 2–4 red — (a), (b), (c) pass, (d)
fails on the words the hook allows today.

## Item 6 — freeze the ring 7c acceptance machinery

`PROTECTED` grows `stage7/test-7c.sh` and `stage7/checkmetal.py`; the hook's
comment says why each is a criterion and why `stage7/METAL.md` (the owner's
procedure, reviewed, not a criterion), `stage7/mkstick.py` (the builder),
`broker/relay.py` and `broker/chart.py` (tools), `stage7/stage7.asm`,
`stage7/mkimage.sh`, `claude_backend.py` and `plan-7c.md` are not.
`payloads.py` gains the ring 7c freeze group: `FROZEN_7C`, `freeze_cases` on
the two paths, the `write` denials, a heredoc writing the checker denied,
`sed -i` on the gate denied, and the allowances measured before the plan and
at item 1 (decision 7's list, the stick lines, the `novga` line, the twin's
line, the oracle's line, the mtools lines, the scratch wipe, `git add`,
`stage8/…` of the same names). Re-run whole, 0 wrong; immediacy demonstrated
live with one denied call on the checker.

*Expected at commit:* test 1 green; tests 2–4 still red; the payload table
0 wrong.

---

*Everything above is written before any guest code exists. Everything below
is the code, the tools, the documents.*

---

# Part 2 — the implementation, in the kickoff's order

## Item 7 — the EDID guard and the mode bound — test 2's `novga` boot green

Decision 2 in `stage7/stage7.asm`: `R10D` around the class read, the
`0x11111234` compare, `jmp .none`; the cell-count bound in `.mode_loop`.
Probed on private copies: QEMU's VGA at 1920x1080 still `S7: edid
1920x1080`; virtio-vga now `S7: edid none` and the gop line item 1's highest
mode; a probe copy with `SHADOW_SIZE` temporarily halved proving the bound
skips the big mode and takes the next (a probe, never committed). Then
`./stage7/test.sh` and `./stage7/test-7b.sh` on this binary — green.

*Green at commit:* test 1; **test 2's `novga` boot passes its EDID and mode
checks** but test 2 stays red on the `i8042:` lines, tests 3–4 red. The two
Stage 7 gates green. Stages 0–6 green (nothing they read has changed).

## Item 8 — the i8042 cold init — TESTS 2 AND 3 GREEN

Decision 3 in `mouse_init` and `i8042_wait_ibf`; deviation 9's
`I8042_WAIT_TRIES` decided from item 1's numbers. Probed on private copies:
the two lines at `-smp 2`, `4` and `8`; the obs page's `i8042_cmd` and
`mouse_id` as GLASS.md says (`checkpointer.check_i8042`'s rule, read by
hand); the arrow still appears on the first packet (`S7: mouse ready` once);
a probe copy with the self-test's expected byte changed to `0x56` proving the
named error and the halt (never committed). Then the gate whole and the
regression pair: `./stage7/test.sh`, `./stage7/test-7b.sh`.

*Green at commit:* **tests 1, 2 and 3**; test 4 red on the hook alone. Both
Stage 7 gates green. Full `./stage7/test-7c.sh` output in the commit message;
the gate's time recorded.

## Item 9 — `PxCMD.SUD` under `CAP.SSS`

Decision 4: `PXCMD_SUD`, `AHCI_SPINUP_TRIES`, the `SSS` test in
`disk_select`'s probe loop, the named error. Unexercisable in the twin
(`SSS` clear, measured twice); the change is read against AHCI 1.3 §10.1.2
and §3.3.7 (`PxCMD.SUD`, `PxSSTS.DET`) in the commit message, and the twin's
path is proven unchanged: `./stage7/test.sh`, `./stage7/test-7b.sh`,
`./stage7/test-7c.sh` all green on the binary; the disk line and the obs
page's `ahci_port` identical to item 8's.

*Green at commit:* tests 1–3; test 4 red by design. The three Stage 7 gates
green.

## Item 10 — the relay's grace close

Decision 5 in `broker/relay.py`; the host proof `stage7/out/probe7c/relay_grace.py`
quoted in the commit message (the held socket freed after the grace, the
second client served, the first's log line `up 8 down 8 error null`, the
ring 7b proof's cases re-run). Then `./stage7/test-7b.sh` (the relay is in
every question of that gate) and `./stage7/test-7c.sh` green.

*Green at commit:* tests 1–3; test 4 red by design. The 7b and 7c gates green.

## Item 11 — `broker/chart.py`

Decision 6; the pty proof `stage7/out/probe7c/chart_proof.py` quoted (three
lines in, three lines out on stdout and in the log with timestamps, the
partial line at SIGINT, the loud exit on a path that cannot be opened —
the proof's bad path is a file under `stage7/out/probe7c/`, never a device).

*Green at commit:* tests 1–3; test 4 red by design.

## Item 12 — `stage7/METAL.md`

Decision 10, written after the machinery so it names the real files and
commands — every command in it copied from `test-7c.sh`, `mkstick.py`,
`relay.py`, `chart.py` and the spec as they now are, the debugging table from
the boot order the twin printed at item 8. Written with the Write tool. This
is what Cowork reviews with the guard (item 7), the cold init (item 8) and
`mkstick.py` (item 2) before the owner's flash.

*Green at commit:* tests 1–3; test 4 red by design.

## Item 13 — the bodyguard extended, the payload table — ALL FOUR TESTS GREEN

Decision 7 in `.claude/hooks/protect-tests.py` and `payloads.py`: the
narrowed `tty`, the normalised `/dev` rule, `METAL_WORDS`, the Stage 3
allowance flipped with its label, the ring 7c spelling and word group; the
table re-run whole, 0 wrong; immediacy demonstrated live (one denied `echo`
of a word, reworded). **Then the gate whole** (test 4's (d) green) and the
regression chain: `./stage7/test.sh`, `./stage7/test-7b.sh`, the three ring
6 gates, Stages 0–5.

*Green at commit:* **all four automated tests.** Full `./stage7/test-7c.sh`
output in the commit message. Every earlier gate green.

## Item 14 — HANDOVER, gotchas, README, CLAUDE.md's build block, the three commands

`HANDOVER.md` to the green-pending-oracle state (what was built, the numbers
on this build — the stick's size and LBAs, the ready time over USB, the
`novga` mode, the i8042's answers, the binary's size, the gate's time — tests
1–4 green with output, test 5 pending with decision 12's three commands,
decision 14's caveats, the ports as A5 settled them); `CLAUDE.md`'s build
block gains `./stage7/test-7c.sh` and `python3 stage7/mkstick.py`, the
windowed command its ring 7c shape (the stick over USB, 9997), and the
gotchas gain what bit twice (candidates: OVMF writes `NvVars` to the stick
too, so boot a copy; a self-test may reset the i8042's command byte, so
write it after; a display's BAR2 is an EDID only when the vendor says so;
the bodyguard's `/dev` rule must see through quotes); `README.md`'s Stage 7
paragraph and running section gain ring 7c; `python3 .claude/hooks/payloads.py`
re-run, 0 wrong; the three commands printed for Wajira; stop.

*Green at commit:* all four automated tests, `./stage7/test.sh`,
`./stage7/test-7b.sh`, the three ring 6 gates, Stages 0–5.

---

## Verification

- **Automated:** `./stage7/test-7c.sh` from the repo root — refuses to start
  if anything listens on 9999, 9998 or 9997; builds the image and the stick;
  tests 1–4 (the stick parsed; three boots over USB; the two-boot scripted
  run with two rehearsals; the strings, the argv checks, the bind rule, the
  payload table). Exit 0 only if all pass. Run before every commit from item
  8 on; its time recorded from the item 8 run.
- **Regression:** `./stage7/test.sh` and `./stage7/test-7b.sh` on this
  ring's binary before the item 7, 8, 9, 10, 13 and 14 commits;
  `./stage6/test.sh`, `./stage6/test-6b.sh`, `./stage6/test-6c.sh` and
  Stages 0–5's gates before the item 13 and 14 commits. They boot their own
  binaries or this one from `esp.img`; this ring's files are invisible to
  them.
- **The hook:** `python3 .claude/hooks/payloads.py` at items 6, 13 and 14 —
  every case from every stage, 0 wrong; immediacy demonstrated live.
- **The probes:** items 1, 2, 7, 8, 10 and 11 each state their expected
  output and quote it in the commit message.
- **Manual (test 5):** Wajira, on the HP, by `METAL.md`. His word closes the
  ring and the stage.

## Safety

Everything CC runs is inside QEMU or on the host's loopback. Firmware, the
IvyBridge CPU model, the VGA device (virtio-vga for one boot), the stick as a
raw file over `qemu-xhci`, exactly two drives per guest of the gate's own —
a copy of `stick.img` and a raw 64 MB disk on q35's AHCI, both under
`stage7/out/metal/` (the twin's copies under `stage7/out/metal/rehearsal/twin/`
with the frozen twin's virtio notes file the guest never touches; the probe's
under `stage7/out/probe7c/`) — created by the harness, the broker or the
probe. **The storage bodyguard is tightened, never loosened**: every planned
command was read against its rules before this plan was written, and from
item 13 the flash's own words are denied to CC in any command, prose
included. **CC never touches `/dev`, never runs `dd`, never sees the stick as
anything but a file**; the flash is the owner's hand by the by-id path
(`METAL.md` step 3), once per build. The network is a cage in every QEMU
line: slirp with `restrict=on` and one `guestfwd`, landing on `127.0.0.1` —
the relay on 9997, the listener on 9998 — never on the LAN; the relay binds
`127.0.0.1` in the twin and refuses every other address but `10.0.2.4`,
tested; the broker binds `127.0.0.1` only, frozen. The automated gate talks
only to the mock and refuses to run if anything else holds any of the three
ports. `chart.py` is proven on a pty pair and opens only the path it is
given; in this session that is never a device. The guest's changes are a
compare in `edid_read`, a compare in the mode loop, the i8042's self-test and
two lines, and a spin-up path that does not run in the twin. This session
makes no Claude call. Every existing frozen file is untouched — `git diff
--stat c964c3b -- <every PROTECTED path>` is empty at every commit — and every
earlier gate is green at the end of the ring. `paper/` is not this ring's and
is not touched.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| The stick does not boot on the HP (AMI's USB stack, the GPT, the FAT) | a proper ESP with the type GUID and a protective MBR, rehearsed over `usb-storage` in the twin as the firmware will see it; the fallback the spec names (a whole-disk FAT) is one `mkstick.py` change and no frozen file — but the frozen test 1 asserts the GPT, so that fallback is a freeze opening by the owner's hand, said here |
| OVMF's USB path is slow or its boot order skips the stick | item 1 measures `alive` and `ready` over USB at three `-smp` values before any window is written; `bootindex` on `usb-storage` is the lever if the order is wrong |
| Intel's GOP lists a mode the console cannot hold, or a `PixelsPerScanLine` that is not the width | the mode bound (decision 2); the stride read from the mode since Stage 1; `S7: gop` before any pixel |
| virtio-vga is not driven by OVMF's GOP, or has no linear mode | item 1 measures it first and cirrus-vga is the named fallback; the `novga` string is written after that measurement |
| The i8042 on the HP is slower than QEMU's, or the mouse's reset takes longer than the bound | every wait bounded and named; `I8042_WAIT_TRIES` decided from item 1 and the PS/2 specification (deviation 9); a mouse that never answers is a line, not a halt |
| The self-test resets the controller and undoes a disable | the command byte is written after the self-test (decision 3), and read back |
| `CAP.SSS` set on the HP and the disk never appears | `SUD` set and a ten-second bound with a named error (decision 4); the port's state is in the obs page and on the serial log |
| The 82579LM's PHY never links | ring 7b's answer stands: `link up` last before `ready`, ten seconds, a named error; the fix is an item with the datasheet open, after the first boot's log |
| The bodyguard's new rule denies a command the gate or a probe needs | every planned command shape was fed to the hook before this plan (the table above); `dd` leaves the prompt for the scripts; probes read images with Python; commit messages by `-F` |
| The bodyguard's new rule misses a spelling | the spellings are enumerated as data in the table and in the checker's spot checks (decision 9 (d)), and the normalisation is deliberately blunt: it deletes every quote and backslash before looking |
| A count in the frozen checker is wrong (ring 6b item 10b, ring 7b item 10b) | the line counts are the pattern lists' lengths; the `i8042:` pair is found by regex, not by index; the relay's bytes are `len(frame(...))`; the call numbers follow the record's own rule (generation calls only); `grows_served` is GLASS.md's rule, 0; the `novga` mode is item 1's run; the stick's LBAs are the builder's constants the checker imports |
| The frozen 7a or 7b gate goes red on this binary | the guard keeps QEMU's VGA on the EDID path; no `S7:` line is added; the i8042 lines carry their own prefix; both gates run before every guest commit |
| The frozen twin refuses a rehearsal on the new lines | `twin.judge` counts `S7:` lines and `ERR:` lines only — measured by reading it; `i8042:` is invisible to it |
| The click on `! echo` in boot B lands on the wrong cell | the target from the frozen `choice_targets` with `installed=["echo"]`, the column as `checkpointer.target_col` computes it from the section's own targets, the pointer model from the geometry the guest printed |
| The relay's grace closes a slow but honest guest | the grace starts only after the broker has finished and its bytes are forwarded; the guest has its whole answer; two seconds is the bound the ring 7b oracle's longest close never approached |
| A frozen file needs to change | the scope guard: stop, the diff unapplied under `stage7/out/`, the owner's hand |
| The gate spends a token | the triple port refusal; `wire.py --mock`; `claude_backend` imported only outside `--mock`; the record checks demand the mock's call counts |

---

## Amendments — Cowork's review, adopted before approval

Cowork reviewed the plan on 15 September 2026 and returned seven
amendments: A1 to A3 must be adopted; A4 to A7 are cheap and are adopted
too. All seven are adopted here verbatim in substance. Where an amendment
contradicts a decision, a deviation or an item above, **the amendment
governs**; the body of the plan is left as written so the review can be
read against it.

**A1 — `chart.py` opens the port non-blocking, then sets termios, then
clears the flag** (decision 6, item 11). `chart.py` opens the port with
`O_RDWR | O_NOCTTY | O_NONBLOCK`, sets termios (`CLOCAL` among the flags),
then clears `O_NONBLOCK` with `fcntl`. Reason: a serial open without
`O_NONBLOCK` blocks until DCD is asserted while `CLOCAL` is still clear in
the driver's default termios. A three-wire null-modem cable never asserts
DCD, so `chart.py` would hang at open and print nothing, and the first
suspect on the day would wrongly be the HP. The pty proof cannot show this
(a pty has no carrier), so the commit message states the rule and the order:
open non-blocking, set termios, clear the flag.

**A2 — Under `CAP.SSS`, `DET 0` right after `SUD` is not a pass** (decision
4, item 9). After `SUD` is set, wait up to `AHCI_PROBE_TRIES` (one second)
for `DET` to leave 0; if it stays 0 the port is empty and is passed; if it
becomes non-zero, wait up to `AHCI_SPINUP_TRIES` (ten seconds) for `DET 3`
or halt with the named error. Reason: with staggered spin-up the device is
not detected until the port has been told to spin it up, so `DET 0` in the
first microseconds means nothing; passing it at once would skip the HP's
only disk and end in the no-blank-disk error. With `SSS` clear, the twin's
path stays byte-identical.

**A3 — Three additions to the flash procedure** (decision 10, METAL.md steps
1 to 3). First, step 1 requires exactly one line with `usb` under TRAN, and
its SIZE and MODEL must match the stick; if there are two, unplug the other
before going on. Second, between steps 2 and 3: the desktop auto-mounts a
plugged-in stick, so before the write the owner unmounts every partition of
it by its by-id path with `udisksctl unmount -b`, and METAL.md says why (a
raw write onto a mounted stick races the mount's writeback and the kernel
refuses to re-read the new table). Third, after `sync` in step 3:
`udisksctl power-off -b` on the by-id path, then unplug. These commands are
the owner's; they appear only in METAL.md, written with the Write tool.

**A4 — The widened `DEV_MENTION` is `/dev\b(?:/[\w./+-]*)?`** (decision 7,
item 13), so a bare `/dev` is a mention only at a word boundary. Reason:
without the boundary, any repo path beginning `/devel`, `/device` or
`/devices` would be denied, a false-deny class the ring does not need. The
payload table gains `/devel/x` and `stage7/out/devices.txt` as allowances
and bare `/dev`, `/dev/` and `"/dev"/sda` as denials, all measured at item 1
through the scratch payload script.

**A5 — The mode-loop bound is the tightest of the console's fixed limits,
not `SHADOW_SIZE` alone** (decision 2, item 7): cells (`w/16 × h/16`) at
most `SHADOW_SIZE`, and rows (`h/16`) at most `SURF_ROWS_MAX` (256), which
the glass core already enforces at `surf_describe` with `.too_small`. Item 7
reads `surf_describe`'s checks and mirrors every one that depends on the
mode alone (`PANEL_CELLS` depends on the split, so it is judged as today).
The halved-constant probe at item 7 proves the bound on each limit it
mirrors.

**A6 — The `again` and `novga` boots assert the `i8042:` pair exactly as
the `blank` boot does** (decision 9, test 2): each line once, in order,
after `S7: glass core` and before `S7: keyboard ready`, and no `i8042:` line
elsewhere. The plan's text says this for `blank` only; the checker applies
it to all three.

**A7 — METAL.md says what `nmcli` does to the connection, and how to undo
it** (decision 10, METAL.md step 5). `nmcli con up <name>` bounces the LAN
connection for a few seconds, and `+ipv4.addresses` persists across
reboots. METAL.md says both, and its closing section gives the removal line,
`nmcli con mod <name> -ipv4.addresses 10.0.2.4/24` followed by `nmcli con up
<name>`, for after Stage 7 closes. The `ip addr add` fallback is gone at the
next reboot on its own; METAL.md says that too.
