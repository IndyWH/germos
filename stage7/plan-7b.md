# Stage 7, ring 7b — the wire · implementation plan

**To be committed verbatim as `stage7/plan-7b.md`. Produced in plan mode, per
the foundation's build loop. Nothing below is implemented until Wajira
approves this document by writing the approval marker from his own terminal;
the ExitPlanMode hook holds the gate until then. Plan mode allows this
session to write only this one file and forbids commits, so — exactly as
every ring since 6a — the copy to `stage7/plan-7b.md` and its commit are the
first act after the gate opens, item 0 below, before any other file is
touched. Cowork's amendments while the gate holds are adopted here as
numbered amendments (A1, A2, …) at the end of the document.**

## Context

Ring 7a, the disk, closed on 9 September 2026 at Wajira's test 5.
`stage7/spec.md` (approved 9 September 2026) makes Stage 7 three rings, and
**this is ring 7b, the wire.** Its reason: the patient, an HP Compaq Elite
8300 SFF, reaches the world through an Intel 82579LM, and virtio-net does
not exist on metal. The done-when, from the spec: **Stages 4 to 6 re-proven
on `e1000e` in the twin through the relay that will sit on mlrig's LAN
port.** Test 5 is Wajira's, windowed, with the real broker behind the relay:
`? ping` and `! make me a clock`. His word closes the ring.

What this ring builds, from `stage7/spec.md` and the kickoff:

- **An e1000e-family driver** in `stage7/stage7.asm`, per Intel's 82574
  datasheet — the register set the 82579LM shares: the device found by
  vendor `0x8086` and a short class-`0x0200` device table; BAR0 mapped
  uncached; a reset; the MAC read from RAL/RAH (the EEPROM the firmware has
  already loaded); one receive ring and one transmit ring of legacy
  descriptors in BSS; polled, interrupts masked, INTx off, bus mastering
  set before any ring address is handed over; link status from
  `STATUS.LU`. Two serial lines: `S7: nic 6c:3b:e5:3b:86:45` and
  `S7: link up`, the link wait bounded and ending in a named `ERR:` line,
  never a hang. **The TCP stack above `net_send` and `net_poll` is
  untouched** (`stage4/UMBILICAL.md` and the stack stand). The virtio-net
  driver stays in the binary beside the e1000e, the e1000e preferred when
  both are present (kickoff fact B).
- **`broker/relay.py`, new and unfrozen**: listens on one address and port
  and forwards each connection to the frozen broker on `127.0.0.1:9999`;
  refuses to start unless bound to `10.0.2.4` or `127.0.0.1`; the broker's
  bind stays frozen. In the twin, slirp's `guestfwd` points at the relay,
  so the gate exercises it. TLS stays in the broker this stage.
- **`broker/wire.py`**, this ring's broker module, subclassing
  `broker/metal.py` the way `metal.py` subclassed `pointer.py`: the twin
  with an e1000e on a second netdev through the `extra_args` seam, nineteen
  lines expected, `metal.py` and `metal.twin_extra_args` untouched.
- **Acceptance tests 1–4**, written red before any driver code, in
  `stage7/test-7b.sh` and `stage7/checkwire.py`, with a short frozen
  `stage7/WIRE.md` (the lines, the relay's contract and its log line, the
  twin's second netdev); then **the freeze**.
- **`HANDOVER.md`** updated as we go; `CLAUDE.md`'s build block gains the
  ring's commands; every e1000e or relay mistake corrected twice becomes a
  gotcha. **The owner's decisions, already made:** ring 7b is implemented
  on **Fable 5.1 at high effort** (recorded in `HANDOVER.md` at item 0,
  per the spec); the policy gate was re-checked in the spec on 9 September;
  the N-of-1 trials come after the metal.

The standing orders: the automated gate talks only to the mock, spends no
token and needs no internet; the real `claude -p` backend is exercised only
by the owner at test 5. **The cage, the storage bodyguard and every frozen
file stand**: every path in `PROTECTED` stays byte for byte —
`stage7/test.sh`, `stage7/checkdisk.py`, `stage7/DISK.md` and
`broker/metal.py` included — and `./stage7/test.sh`, the three ring 6 gates
and every earlier gate must pass at the end of the ring. The storage
bodyguard stands: the only disks are raw files under `stage7/out/`. **The
scope guard:** if a frozen file turns out to be wrong, stop at the commit
boundary, write the diff unapplied under `stage7/out/`, say so in
`HANDOVER.md`, and wait; the owner applies it by his own hand. Never create
or mention the approval marker from inside a session. One commit per
numbered item; tests red before the code they judge; tests green before
every commit that should pass them; **every number in a frozen test is
written from a run or derived from the test's own data, never from
arithmetic** (ring 6b item 10b, ring 6c A2). Two honest attempts per
obstacle.

The plan is **evaluation-first**. Items 1–7 make the document, the relay,
the broker module and the acceptance machinery so that tests 1–4 exist and
tests 2–4 fail before a single instruction of driver code is written. Item
8 freezes them. Items 9–10 grow the guest: **test 1 is green from item 5**
(the artefact is ring 7a's closed binary until item 9, a packed PE32+ from
the first day — deviation 9); **test 2 goes green at item 9** (the device
attached, the MAC, the link, the two lines); **tests 3 and 4 go green at
item 10** (frames sent and received; `broker/wire.py` frozen then, after
nine of nine through it — A3's precedent). Item 11 is the handover. Test 5
is Wajira's.

### Environment, measured in this session before planning

Read-only: no file was written, no guest was booted, nothing frozen was
touched; the working tree is clean at `3baeee7` but for the untracked
`paper/` (not this ring's). No Claude call was made. The one QEMU started
here was paused at start (`-S`, no firmware executed, no drive attached)
so its monitor could list PCI devices and networks; it was quit from the
monitor.

| Fact | Measured how |
|---|---|
| **The toolchain is unchanged:** NASM 3.01, QEMU 10.2.1, Python 3.14.4, OVMF at `/usr/share/ovmf/OVMF.fd`, mtools, OpenBSD netcat 1.234. No new package is needed: **`-device e1000e` is built in — "Intel 82574L GbE Controller"** — with properties `mac`, `netdev`, `subsys` (default 0), `subsys_ven` (default `0x8086`), `rombar`/`romfile`, `disable_vnet_hdr` (the backend side, not guest-visible) and no property that changes its device id. `igb` (82576) and three `e1000` (8254x) models exist too; **none is an 82579** | `-device e1000e,help`, `-device help` |
| **The e1000e's PCI identity: vendor:device `8086:10d3`**, subsystem `8086:0000`, class Ethernet controller; **BAR0 a 32-bit memory BAR** (the register set), BAR1 32-bit memory (flash), BAR2 I/O, BAR3 32-bit memory (MSI-X). virtio-net is `1af4:1000`. **With the twin's device order — the frozen `virtio-net-pci` first, the e1000e appended through `extra_args` — the VGA is `00:01.0`, virtio-net `00:02.0`, the e1000e `00:03.0`**, the AHCI `00:1f.2` as ring 7a found it. The driver's table: `0x10D3` (82574L, the twin), `0x1502` (82579LM, the HP) and `0x1503` (82579V, its sibling) — the two PCH ids from Intel's published list, unmeasurable here | the paused instance's `info pci` with the twin's two devices |
| **libslirp accepts two user-mode netdevs, each `restrict=on` with a `guestfwd` of its own**, and `info network` shows both: `n0` behind `virtio-net-pci.0`, `n1` behind `e1000e.0`. So the twin's second NIC can carry a second cage, and the gate's `both` boot too (kickoff fact A) | the paused instance's `info network` |
| **`set_link e1000e.0 off` is accepted by the monitor** for an e1000e given no `id` — its default name is `e1000e.0` — so a boot can start paused, have its link taken down, and `cont`: the mechanism for the bounded link wait's test (decision 7's `down` boot) | `help set_link`, `set_link`, `info network` in the paused instance |
| **OVMF carries no e1000 driver of its own** (zero matches in the firmware image); **the device's option ROM is iPXE's `efi-e1000e.rom` (512 KB)**, loaded by QEMU unless `rombar=0`. Whether OVMF runs it and what it leaves in the registers is item 1's probe — as ring 7a measured the AHCI port's state | `strings OVMF.fd`, `ls /usr/share/qemu` |
| **This host has no `10.0.2.4`**: a bind there fails with errno 99, `127.0.0.1` binds; **the host's LAN address is `192.168.1.107` on `eno2`** — the relay must never listen there in the twin, which is exactly what its bind rule forbids. **9999, 9998 and 9997 are free** | a Python bind on each address, `ip -4 addr`, a connect on each port |
| **The frozen seams the twin needs, and their arguments.** `glass.Glazier.grow` calls `self.rehearse(blob, name, choices, image, workdir, port)`; `plans.Installer.install` calls `plans.rehearse_plan(blob, pname, choices, image, workdir, port, plan=…, verdicts=…)`; **neither passes `lines`**, so a module's rehearsal function carries its line count as its default (`pointer.rehearse_point` and `metal.rehearse_metal_plan` do). `metal.rehearse_metal` takes `extra_args` (appended after `metal.twin_extra_args(workdir)`) and `lines` — the two seams this ring uses; its `READY`, `LINE_RE` and `OBS_RE` are `S7:` and serve as they are. The mock's record field `generation_calls` is the process's running total (`self.calls`), so in one boot a grow followed by an install records 1 then 2 — a number the test's own step list fixes, not arithmetic about the guest | read, `broker/glass.py` 387–424, `broker/plans.py` 453–495, `broker/metal.py` |
| **What the frozen ring 7a gate demands of this ring's binary** (kickoff fact B): `stage7/test.sh` and `stage7/checkdisk.py` boot with `virtio-net-pci` only, MAC `52:54:00:a1:07:01`, and count **exactly eighteen** `S7:` lines on a blank disk and seventeen on a recognised one; `check_argv_7` demands exactly one `-netdev`, one `virtio-net-pci` and **exactly three `-device`s** on the checker's command and on `twin.qemu_argv(…, extra_args=metal.twin_extra_args(…))`; `check_install_germline_7` demands an eighteen-line rehearsal log. So: the virtio driver stays; `S7: link up` is printed only on the e1000e path; `metal.py` is not edited; the twin's e1000e lives in `wire.py`'s own extra arguments, checked by `wire`'s own argv check | read, `stage7/test.sh`, `stage7/checkdisk.py` |
| **The guest's shape around the NIC** (`stage7/stage7.asm`, 9103 lines): `pci_scan` records the first virtio-net (`1af4:1000`/`1041`) into `nic_dev` and the first AHCI function by class into `ahci_bdf`; `nic_find` → `vio_attach`; `nic_negotiate` (VERSION_1 \| MAC, the six bytes from device config into `nic_mac`); `nic_queue_init` (sixteen 2048-byte receive buffers posted, one transmit descriptor); **`net_send`** (ECX = the frame's length at `nic_tx_buf + TX_BASE`, pads to 60, counts `OBS_BYTES_OUT`, zeroes the 12-byte virtio header, one descriptor, polls the used ring `VQ_POLL_TRIES` × `PIT_200US` — five seconds — then `ERR: nic transmit timed out`); **`net_poll`** (pushes R12–R14, dispatches each frame by EtherType from `nic_rx_bufs + VNET_HDR_LEN + i·2048` to `arp_input`/`ip_input`, counts `OBS_BYTES_IN`, reposts, returns EAX = frames taken); the callers — `arp_resolve`, `ip_send`, `tcp_*` — reach the device **only** through `net_send` and `net_poll`; `OBS_WIRE_CONNS` is counted in `tcp_connect`; `map_mmio_2m` maps any physical address uncached, creating tables as needed; `vio_attach` reads a 64-bit BAR as two halves — the shape the e1000e's BAR read copies; the strings `msg_nic` and `err_no_vnet`; the boot order in `efi_main` is disk → notebook → home → NIC (line fourteen) → component region → obs page → glass core → keyboard | read |
| **The frozen checkers, prefix-free and reusable as they are:** `checkglass.check_question_entry` (with `CANNED` ping/hello), `check_grow_entry`, `check_app_panel` (the test app's picture), `check_one_cell_panel`, `check_strip`, `check_counts`, `check_region_rows`, `check_choices`, `check_mode_field`, `check_app_panel_blank`, `read_record`, `port_state`, `stop_mock`, `fixture_self_check`, `germline_entries`, `PROMPT`, `NO_ANSWER`, `SETTLE`; `checkplans.check_install_entry`, `ECHO_TESTS_OK`, `CHOICES_ECHO_RUNNING`, `DATA_FIRST`; `checkdisk.check_notes_partition`, `check_partitions`, `check_table`, `read_image`, `check_echo`, `fresh_disk`, the `--formatted` and `--esp` modes; `twin.Driver`, `keyname`; `plans.plan_keyname`; `glass.app_frame`, `grow_request`, `TEST_CHOICES`, `regions`. **Bound to a count or a device and transcribed instead:** `checkglass.check_germline_entry` (counts `^S6:` against 16), `checkdisk.check_install_germline_7` (eighteen), `checkdisk.qemu_argv`/`drive` (the virtio cage), `check_argv_7` (one netdev, three devices) | `grep -n "S6\|LINES\|virtio" stage6/checkglass.py stage6/checkplans.py stage7/checkdisk.py`, read |
| **The hook:** `PROTECTED` holds 53 paths, the ring 7a four included; the payload table is 1324 cases (`FROZEN_7A`, `QEMU7`, `SATA7`, `CAGE7`, the twin's line); the words this ring needs — *relay*, *e1000e*, *link*, *netdev*, *set_link*, *switch* — are none of the denied words; **`-S` is not a shorthand the bodyguard names** (`-sd` is; `\b` keeps them apart); a second `-netdev` is inert to it; `-device e1000e,…` is not a drive. The "next stage's test file" case stays `stage8/test.sh` | read, `.claude/hooks/protect-tests.py`, `.claude/hooks/payloads.py` |
| **The MACs.** Ring 7a's gate keeps `52:54:00:a1:07:01` on virtio-net, untouched (kickoff fact D). This ring's e1000e carries the HP's **`6c:3b:e5:3b:86:45`** in the gate, the twin and the oracle's command; the gate's one boot with both NICs gives the virtio device **`52:54:00:a1:07:02`**, a value that must *not* appear on the nic line | read, `stage7/test.sh`; the spec |

**To be measured at item 1, before any test is written** (plan mode
forbids a boot): ring 7a's closed binary booted in this ring's twin shape
(`-cpu IvyBridge`, the SATA disk, the frozen virtio notes disk, **the
e1000e on a second netdev beside the virtio-net**) at `-smp 2`, `4` and
`8` — that it still reaches `S7: keyboard ready` with eighteen lines on the
virtio path with the e1000e ignored, and how long OVMF takes to `S7: alive`
with the iPXE ROM present and with `rombar=0`; and, through a temporary,
uncommitted probe copy, what the firmware left: the e1000e's command
register, BAR0 and its size, `CTRL`, `STATUS` (whether `LU` is already
set), `RCTL`, `TCTL`, `IMS`, `RDBAL`/`RDT`, `TDBAL`, `RAL0`/`RAH0` (whether
`AV` is set and the MAC is the harness's), `RFCTL`, `MRQC`; then, after a
`CTRL.RST` from the probe, how many 200 µs breaths until `STATUS.LU`
returns (the twin's autonegotiation time) and whether `set_link e1000e.0
off` before `cont` leaves `LU` clear for good. Recorded in `HANDOVER.md`'s
environment table at item 1; the probe removed before the commit.

---

## Deviations from the spec and the kickoff, for approval

Each argued from a measured fact or a frozen file. Everything else is the
spec as written.

1. **The relay's port in the gate is 9997, not the spec's 9998.** The
   spec's twin line puts the relay on 9998; 9998 is the frozen twin's own
   rehearsal listener (`twin.DEFAULT_PORT`, kickoff fact C). So: the broker
   on 9999, the rehearsal listener on 9998, **the relay on 9997**; the gate
   refuses to run while any of the three is held; the oracle's command
   says 9997 too. On the HP's day the relay binds `10.0.2.4:9999` and no
   port of the twin's is involved.
2. **The twin's rehearsals go direct to 9998 on both netdevs, not through
   a relay of their own.** The relay forwards to the *broker* on 9999 by
   the spec; a rehearsal's far end is the frozen twin's one-shot listener,
   not a broker, so a relay in front of it would need a second forwarding
   target and a per-rehearsal process lifecycle inside a module that is
   to be frozen — for no criterion the spec names. The relay is exercised
   by every gate boot that reaches the broker (tests 3 and 4: the
   question, the mock-down run, the grow, the install). The twin's second
   netdev carries the same cage as the first — `restrict=on`, one
   `guestfwd` to `nc -N 127.0.0.1 9998` — and the guest, preferring the
   e1000e, reaches the listener through it; the rehearsal log's nineteen
   lines with `S7: link up` prove the driver was the one on the wire.
3. **Nineteen lines on a disk the guest formats, eighteen on a recognised
   one; `S7: link up` follows the nic line.** Ring 7a's eighteen and
   seventeen plus one: alive, edid, gop, boot services exited, gdt and
   paging ours, idt ready, cores found, cores woken, console, [gpt
   written], disk, notebook, home, **nic, link up**, component region,
   obs page, glass core, keyboard ready. `S7: link up` is printed only by
   the e1000e path, so the frozen 7a gate's virtio boots keep their
   counts (kickoff fact B). No checker holds either number as a literal:
   each derives it from the length of its own pattern list.
4. **"Stage 5's grow" is ring 6a's `! test app`.** Stage 5's `! test
   component` was ABI 1, retired at ring 6a item 13; the grow path on this
   binary is ABI 2, and its fixture with a known picture is
   `stage6/app.bin`. Test 4 sends `! test app` through the relay, then `!
   install echo`, in one boot; the mock's record counts the grow as its
   first generation call and the install as its second (measured: the
   counter is the process's running total).
5. **The twin's shape is proven from both slot orders.** The twin puts
   virtio-net at `00:02.0` and the e1000e at `00:03.0`; the gate's `both`
   boot puts the e1000e first and the virtio-net second. The driver
   prefers the e1000e by *kind*, not by slot — `pci_scan` records the
   first of each kind — and both orders are exercised (test 2's `both`
   boot, test 4's twin).
6. **The e1000e's receive buffers are the virtio driver's sixteen
   buffers, offset by the virtio header's twelve bytes.** Descriptor `i`
   names `nic_rx_bufs + i·2048 + 12`, so `net_poll`'s frame arithmetic and
   the dispatch are shared between the two paths and the transmit frame
   stays at `nic_tx_buf + TX_BASE`. Safe because `RCTL.LPE` is clear: the
   device discards any frame over 1522 bytes, and 12 + 1522 fits inside
   the 2048-byte slot. The rings themselves are new BSS (decision 2).
7. **The link wait is ten seconds.** Real autonegotiation takes two to
   three seconds on copper and the 82579's PCH PHY can take longer; the
   twin's is measured at item 1. Ten seconds is inside every gate boot's
   60 s window, and the `down` boot spends it once. The named error is
   `ERR: nic link did not come up within 10 s`.
8. **A short frozen `stage7/WIRE.md`, though the spec names none.** The
   relay's log line is parsed by the frozen checker and written by an
   unfrozen file; the two serial lines and the relay's contract (the bind
   rule, the forwarding, the log) are what ring 7c's `METAL.md` will point
   the owner at. In NOTEBOOK.md's voice, one page: the assembler prints the
   lines, the relay keeps the contract, the checker parses by both.
   `UMBILICAL.md` stands untouched; WIRE.md says which of its sentences
   ("Guest MAC read from the virtio-net device configuration"; "every QEMU
   command carries these two arguments") it supersedes for this ring.
9. **The artefact is ring 7a's closed binary until item 9**, so test 1 is
   green from the moment `stage7/test-7b.sh` exists at item 5 (as 7a's
   deviation 10), and tests 2–4 are red on it: `ERR: no virtio-net device
   on PCI bus 0` in every e1000e-only boot, eighteen lines with the virtio
   MAC in the `both` boot, `keyboard ready` instead of the named error in
   the `down` boot.
10. **`broker/wire.py` is frozen at item 10, not at item 8** — A3's
    precedent, for A3's reason: four of the project's five freeze
    openings were in frozen Python that could not be exercised before it
    froze. `broker/relay.py` is never frozen (the spec says so); its
    contract is a criterion through WIRE.md and the checker that parses
    its log, so a bent relay is a red gate, not a bent criterion.
11. **The oracle's run needs three terminals**: the real broker
    (`python3 broker/wire.py`), the relay (`python3 broker/relay.py --bind
    127.0.0.1 --port 9997`) and the machine. On mlrig today `10.0.2.4`
    does not exist (measured), so the twin's relay binds `127.0.0.1`; the
    `10.0.2.4` bind is the HP's day, ring 7c's `METAL.md` step 5.

---

## Decisions taken in this plan

1. **The serial lines** — deviation 3's list. `S7: nic <mac>` keeps its
   text and prints what RAL0/RAH0 hold on the e1000e path (device config
   on the virtio path, as before); **`S7: link up`** follows it on the
   e1000e path only. The named errors, all before `keyboard ready`, all
   halting as `serial_err` does: `ERR: no network device on PCI bus 0
   (e1000e or virtio-net)` (replacing `err_no_vnet`'s text; nothing frozen
   asserts the old one), `ERR: nic BAR0 is not a memory BAR`, `ERR: nic
   did not complete its reset`, `ERR: nic has no address in RAL/RAH`,
   `ERR: nic link did not come up within 10 s`; `ERR: nic transmit timed
   out` keeps its text. The display is 1920x1080 in the gate, the twin and
   the oracle's run; nothing is baked in.
2. **The e1000e driver** (`stage7/stage7.asm`, items 9–10), per the 82574
   datasheet's register map, offsets from BAR0: `CTRL` `0x0000` (FD 0, SLU
   6, ILOS 7, FRCSPD 11, FRCDPX 12, RST 26, PHY_RST 31), `STATUS` `0x0008`
   (LU bit 1), `ICR` `0x00C0`, `IMS` `0x00D0`, `IMC` `0x00D8`, `RCTL`
   `0x0100` (EN 1, BAM 15, BSIZE 17:16, BSEX 25, SECRC 26), `TCTL` `0x0400`
   (EN 1, PSP 3, CT 11:4, COLD 21:12), `TIPG` `0x0410`, `RDBAL`/`RDBAH`/
   `RDLEN`/`RDH`/`RDT` `0x2800`–`0x2818`, `TDBAL`/`TDBAH`/`TDLEN`/`TDH`/
   `TDT` `0x3800`–`0x3818`, `RFCTL` `0x5008` (EXSTEN 15), `MTA` `0x5200`
   (128 dwords), `RAL0` `0x5400`, `RAH0` `0x5404` (AV 31), `MRQC` `0x5818`.
   Legacy descriptors, sixteen bytes: receive — address u64, length u16,
   checksum u16, status u8 (DD 0, EOP 1), errors u8, special u16; transmit
   — address u64, length u16, CSO u8, command u8 (EOP 0, IFCS 1, RS 3),
   status u8 (DD 0), CSS u8, special u16. With interrupts off, polled, BSP
   only, every wait bounded by `PIT_200US` breaths:
   - **`pci_scan`** gains a branch: vendor `0x8086`, class `0x020000` in
     bits 31:8 of register 8, device id in a `dw` table of constants
     (`0x10D3`, `0x1502`, `0x1503` — constants, not addresses; the RVA
     trap is for labels), the first into `e1k_bdf`/`e1k_found`. The
     virtio-net and AHCI branches stay.
   - **`nic_find`** chooses by kind: e1000e found → `nic_kind` 2 and
     `e1k_attach` (which prints both lines); else virtio-net found →
     `nic_kind` 1 and the existing `vio_attach`, `nic_negotiate`,
     `nic_queue_init`, the nic line, no link line; else the named error.
   - **`e1k_attach`**: the command register `MEMORY | MASTER | INTX_OFF`
     written **before** BAR0 is read (the standing gotcha); BAR0 at `0x10`,
     a memory BAR, the 64-bit form read as two halves as `vio_attach` does,
     low bits masked; the 128 KB region's first and last page mapped
     uncached by `map_mmio_2m` (the address read, never assumed: item 1
     says where OVMF put it in the twin; the HP's firmware decides its
     own). Then, assuming nothing about what the firmware's or iPXE's
     driver left: `IMC` = all ones; `CTRL.RST` set and awaited clear
     (`E1K_RESET_TRIES`, one second) or `ERR: nic did not complete its
     reset`; `IMC` all ones again and `ICR` read once. **The MAC**: `RAL0`
     bytes 0–3, `RAH0` bits 15:0 bytes 4–5, `RAH0.AV` required set, into
     `nic_mac`; the nic line. **The link**: `CTRL` with FRCSPD, FRCDPX,
     ILOS and PHY_RST cleared and **SLU set** (Linux's copper link setup
     for the 82574 and the 82579 alike; the PHY autonegotiates; MDIC
     untouched this ring — carried, spec risk "the 82579LM's PHY"), then
     `STATUS.LU` polled `E1K_LINK_TRIES` (50000 breaths, ten seconds) or
     the named error; `S7: link up`. **Receive**: the 128 MTA dwords
     zeroed; the sixteen descriptors written (address `nic_rx_bufs + i·2048
     + VNET_HDR_LEN`, status 0); `RDBAL`/`RDBAH` = `e1k_rx_ring` (below
     4 GB, checked), `RDLEN` 256, `RDH` 0, `RDT` 0; `RFCTL.EXSTEN` clear
     and `MRQC` 0 (legacy descriptors, one queue); `RCTL` = EN | BAM | SECRC
     with BSIZE 00 and BSEX 0 (2048-byte buffers), LPE 0, no UPE/MPE, LBM
     0; then `RDT` = 15 — the hardware owns descriptors 0–14 and stops at
     the tail, the datasheet's convention; `e1k_rx_head` = 0. **Transmit**:
     the eight descriptors zeroed; `TDBAL`/`TDBAH` = `e1k_tx_ring`, `TDLEN`
     128 (the minimum), `TDH` 0, `TDT` 0; `TIPG` `0x00602008` (the copper
     values every driver writes); `TCTL` = EN | PSP | CT `0x0F` | COLD
     `0x3F`; `e1k_tx_idx` = 0. Interrupts stay masked, INTx off at the
     function, the PIC's masks unchanged.
   - **`e1k_send`** (ECX = the frame's length, already padded to 60 by
     `net_send`): descriptor `e1k_tx_idx` — address `nic_tx_buf + TX_BASE`,
     the length, command EOP | IFCS | RS, status 0; `sfence`; `TDT` =
     (idx + 1) & 7; the status's DD polled `VQ_POLL_TRIES` breaths or `ERR:
     nic transmit timed out`; the index advanced. `net_send` keeps its
     padding and its `OBS_BYTES_OUT` count and dispatches on `nic_kind` to
     `vnet_send` (the virtio body, renamed) or `e1k_send`.
   - **`e1k_poll`**: while descriptor `e1k_rx_head`'s status has DD —
     `lfence`; the length; with EOP set and length ≥ 14 the frame at
     `nic_rx_bufs + head·2048 + VNET_HDR_LEN` dispatched by EtherType
     exactly as the virtio body does, `OBS_BYTES_IN` counted; status
     written 0; `RDT` = head (the descriptor back to the hardware); head =
     (head + 1) & 15; counted. Returns EAX = frames taken and preserves
     R12–R14 as the virtio body does (the TCP input's assumption).
     `net_poll` dispatches on `nic_kind` to `vnet_poll` or `e1k_poll`.
   - **BSS**: `nic_kind`, `e1k_bdf`, `e1k_found`, `e1k_bar` (u64),
     `e1k_rx_head`, `e1k_tx_idx`; `e1k_rx_ring` (16 × 16 bytes) and
     `e1k_tx_ring` (8 × 16 bytes), each 4 KB aligned in its own page; the
     virtio blocks, rings and buffers stay. The binary's size is measured
     at item 9, not promised.
   - The frame-level contract is unchanged: no VLAN, no offloads (the
     guest computes its checksums; slirp drops a bad one in silence),
     CRC appended by the device on send (IFCS) and stripped on receive
     (SECRC), so lengths mean what they meant on virtio.
3. **`broker/relay.py`** (item 3, unfrozen by the spec), standard library
   only, ~120 lines:
   - `--bind ADDR` (default `10.0.2.4`), `--port` (default 9999),
     `--broker-port` (default 9999; the broker is always `127.0.0.1`),
     `--log PATH` (one JSON line per connection). **The bind rule, before
     any socket exists:** `ADDR` is exactly `10.0.2.4` or `127.0.0.1`, or
     the relay prints `relay: refusing to bind <addr> - only 10.0.2.4 (the
     switch) or 127.0.0.1 (the twin)` to stderr and exits 2. A bind that
     the host refuses (no such address, a port held) is a loud exit as the
     broker's is. Once bound it prints **`relay listening on
     <addr>:<port> -> 127.0.0.1:<broker-port>`** to stdout, the line a
     harness waits for.
   - Per connection: connect to the broker; on refusal the accepted
     connection is closed at once and the log line carries `"error":
     "broker refused: <reason>"`; otherwise two threads splice the two
     sockets, each doing `shutdown(SHUT_WR)` on the far side when its own
     side reads EOF, so the guest's close reaches the broker as EOF and
     the broker's close reaches the guest as a FIN, exactly as `nc -N`
     alone did; when both directions are done both sockets close and the
     line is written: `{"t": <accept time>, "peer": "<addr>:<port>",
     "up": <bytes guest→broker>, "down": <bytes broker→guest>, "error":
     null}`. One connection at a time is served (the broker's own
     discipline); Ctrl-C stops it.
   - **WIRE.md** carries this contract and the log line word for word.
4. **`broker/wire.py`** (item 4, frozen at item 10), importing `metal`
   (its `rehearse_metal`, `tests_hook_metal`, `Metal`, `twin_extra_args`,
   `twin_disk`, `READY`, `LINES` as `LINES_7A`), `twin`, `plans`,
   `pointer`, `broker`, `germline`, `glass` — editing none:
   - `LINES = 19` (deviation 3), `MAC = "6c:3b:e5:3b:86:45"`, `RELAY_PORT
     = 9997`, `NETDEV_ID = "n1"`.
   - **`e1000e_netdev(port)`** → `"user,id=n1,restrict=on,guestfwd=tcp:
     10.0.2.4:9999-cmd:nc -N 127.0.0.1 <port>"` and **`e1000e_device(mac
     = MAC)`** → `"e1000e,netdev=n1,mac=<mac>"`: the one place the twin's
     second NIC is spelled. **`wire_extra_args(port)`** → the two pairs;
     **`twin_extra_args(workdir, port)`** → `metal.twin_extra_args(workdir)
     + wire_extra_args(port)`, the whole of what the twin's command gains,
     which test 4 inspects.
   - **`rehearse_wire_plan(blob, name, choices, image, workdir,
     port=twin.DEFAULT_PORT, plan=None, verdicts=None, lines=LINES)`**:
     `pointer.point_offset` first (the 6c refusal, no boot), then
     `metal.rehearse_metal(…, extra_args=wire_extra_args(port),
     lines=lines, after=tests_hook_metal(...) or None)`. Nothing of the
     frozen twin or of `rehearse_metal` is transcribed again: the two seams
     carry everything this ring adds.
   - **`Wire(Metal)`**: `self.rehearse = rehearse_wire_plan`; `install`
     swaps `plans.rehearse_plan` for `rehearse_wire_plan` around the
     frozen `Installer.install` and restores it — `metal.py`'s own shape.
     The germline, the record, the dispatch and the mock table (GLASS.md's
     test app, PLANS.md's installs, the 6c point app) are inherited.
   - **`main`**: `metal.py`'s flags with this ring's defaults — `--workdir
     stage7/out/wire/rehearsal/twin`, `--lines` 19 for the hand runs,
     `--rehearse-app` and `--rehearse` through this module's twin; the
     log line says "the twin boots … with a 64 MB SATA disk and an e1000e
     on a second cage". Real mode imports `claude_backend` only there.
5. **`stage7/WIRE.md`** (item 2, frozen at item 8), one page in
   NOTEBOOK.md's voice: the NIC the metal has and the twin's stand-in; the
   two lines and where they fall (deviation 3's list); the driver's
   contract in one paragraph (found by vendor and class, BAR0 uncached,
   reset, the MAC from RAL/RAH, legacy rings, polled, masked, the link
   bounded); the errors by name; the relay — the bind rule, the
   forwarding, the listening line, the log line's fields; the twin's
   second netdev and device as `wire.py` spells them and the gate's own
   line; the ports (9999, 9998, 9997); the sentences of UMBILICAL.md it
   supersedes for this ring (the MAC's source; "every QEMU command carries
   these two arguments") and what it does not touch (the frame, the
   conversation, the cage's promise inside the twin).
6. **The harness — `stage7/test-7b.sh` and `stage7/checkwire.py`** (items
   5–7, frozen at item 8), ring 7a's shape; the gate's scratch under
   `stage7/out/wire/` (disks, captures, screens, records, relay logs, the
   twin under `stage7/out/wire/rehearsal/twin`, the germline under
   `stage7/out/wire/germline`) so ring 7a's own artefacts survive. `test-7b.sh`:
   refuses to run while 9999, 9998 or 9997 is held; **the cage with the
   e1000e** — `CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:
   9999-cmd:nc -N 127.0.0.1 9997"`, `CAGE_DEVICE="e1000e,netdev=n0,mac=
   6c:3b:e5:3b:86:45"`; the machine, the display and `sata_drive` spelled
   as 7a's; `fresh_disk` 64 MB; the build with the unfrozen
   `stage7/mkimage.sh`; the relay started and stopped by the gate (its
   listening line awaited, its log named per test). `checkwire.py`: its
   own `qemu_argv` (the e1000e cage, a `link_down` flag adding `-S`), its
   own `drive` (checkdisk's step vocabulary — `type`, `sleep`,
   `wait_record`, `shot`, `obs`, `surfaces` — the line it waits for a
   parameter as checkdisk's is, plus the paused start: `set_link e1000e.0
   off` then `cont` when asked), its own two pattern lists
   (`PATTERNS_BLANK` nineteen with `gpt written`, `PATTERNS_AGAIN` eighteen;
   the nic pattern checked against this ring's MAC, `S7: link up` after
   it) and `check_boot_lines` (the expected count `len(patterns)`), `start_relay`/
   `stop_relay`, `read_relay_log`, `check_relay_log(entries, want)` (one
   entry per connection, in order, `up` and `down` the frame lengths the
   test computes from its own request and the mock's answer, `error`
   null), `start_mock` on `broker/wire.py --mock`, `check_argv_7b(argv,
   port, want_mac, want_drives, virtio_allowed, netdevs)`,
   `check_germline_entry_7b` and `check_install_germline_7b` (nineteen `S7:`
   lines, `S7: link up` present, no `ERR:`, the virtio image untouched);
   everything else imported from the frozen checkers. Where the lines
   fall on the screen is judged by the frozen `check_region_rows`; the
   strip by the frozen `check_strip` with the screendump between the two
   page reads (the ring 6c gotcha).
   - **Test 1** (`test-7b.sh`): the artefact, 6a's criteria on
     `stage7/out/BOOTX64.EFI` and `esp.img` — the same artefact ring 7a's
     gate judges.
   - **Test 2** (`test-7b.sh`'s `serial_check`, then the frozen
     `checkdisk.py --formatted`/`--esp` for the host's view; the `down`
     boot in `checkwire.py --down 2`), four boots: **`blank` at `-smp 8`**
     on a fresh disk — nineteen lines in order, `S7: nic
     6c:3b:e5:3b:86:45` and `S7: link up` fourteenth and fifteenth, found =
     woken = 8, the disk line's numbers as 7a's, then the disk from the host
     byte-exact through the frozen `--formatted`. **`again` at `-smp 4`** on
     the same disk — eighteen lines, no `gpt written`, the image
     byte-identical. **`both` at `-smp 2`** (deviation 5) on a fresh disk
     with the e1000e on `n0` *and* a `virtio-net-pci` on a second cage `n1`
     carrying `52:54:00:a1:07:02` — nineteen lines, the nic line the
     e1000e's MAC, `link up`, `--formatted`. **`down` at `-smp 2`**: the
     e1000e's link taken down through the monitor before the guest runs —
     the lines to `S7: nic …` (fourteen on a blank disk), then exactly
     `ERR: nic link did not come up within 10 s` and no `S7: link up`, no
     `S7: keyboard ready`; the error must appear within the checker's
     45 s ready window (the bound, proven by a clock the test owns), and
     the guest must be halted, not rebooting (no repeated lines — the
     triple-fault gotcha). The boot image checked around every boot by
     the frozen `--esp`. Each boot wrapped in `timeout 60`, exit 124 the
     expected outcome.
   - **Test 3** (`checkwire.py --question <smp>` at 2, 4 and 8): the relay
     on 9997 logging to `relay.question.<smp>.jsonl`, the mock on 9999
     recording, a fresh disk; Stage 4's steps — `? ping` ⏎, `wait_record` 1,
     `keep this` ⏎, `? hello` ⏎, `wait_record` 2 — then **obs R1, the
     screendump, obs R2**. Judged: nineteen lines; the echo exactly the three
     typed lines; the record's two entries by the frozen
     `check_question_entry`; **the relay's log: two entries, in order, `up`
     = `len(frame(b"ping"))` and `len(frame(b"hello"))`, `down` =
     `len(frame(answer))` for the canned answers, `error` null, and as many
     entries as the record has**; the notes partition holding exactly
     `["keep this"]` (the frozen `check_notes_partition`) — neither question
     journaled; the screen: `> ? ping`, `pong`, `> keep this`, `> ? hello`,
     the two answer lines, `PROMPT` (frozen `check_region_rows`); **the
     strip the truth** (frozen `check_strip` against R1 and R2) and **the
     wire counters agreeing with the relay**: `wire_conns` equals the log's
     entry count, `questions` 2, `notes` 1, `errors` 0, `bytes_out` ≥ the
     log's `up` total and `bytes_in` ≥ its `down` total (frames wrap
     payloads; the guest counts Ethernet bytes, the relay payload bytes,
     so ≥ is the honest relation and equality would be a lie).
   - **Test 4** (`test-7b.sh`'s self-assertions, then `checkwire.py
     --cage`): **(a)** the harness's own strings — slirp user mode,
     `restrict=on`, exactly one `guestfwd` to `10.0.2.4:9999` via `nc -N
     127.0.0.1 9997`, no `hostfwd`; the device `e1000e,netdev=n0,mac=<HP>`;
     the machine, display and disk strings as 7a's. **(b)** the argv
     assertions — the checker's own command through `check_argv_7b` (one
     netdev to 9997; three devices: the VGA, the `ide-hd` on `ide.1`, the
     e1000e on `n0` with the MAC; two drives under `stage7/out/`, none
     virtio; `-cpu IvyBridge`); **the twin's as `wire.py` builds it**
     (`twin.qemu_argv(…, 9998, extra_args=wire.twin_extra_args(workdir,
     9998))`: **two netdevs**, each user mode, `restrict=on`, exactly one
     `guestfwd` to `nc -N 127.0.0.1 9998`, no `hostfwd`; **four devices**:
     the frozen `virtio-net-pci` on `n0`, the VGA, the `ide-hd`, the e1000e
     on `n1` with the MAC; three drives, exactly one `if=virtio` — the
     frozen notes disk, 7a's deviation 2); `wire.LINES == len(PATTERNS_BLANK)`,
     `metal.READY == READY`, `twin.DEFAULT_PORT == 9998`, `wire.RELAY_PORT
     == 9997`. **(c)** the relay's bind rule on the host, no guest:
     `--bind 0.0.0.0`, `--bind 10.0.2.2`, `--bind 192.0.2.1` and the host's
     own address (whatever `socket.gethostbyname(socket.gethostname())`
     says, when it is not loopback) each exit 2 with the refusal and leave
     nothing listening on the port; `--bind 127.0.0.1 --port 9997` prints
     the listening line and is stopped. (That `10.0.2.4` cannot be bound
     on mlrig today is an environment fact, recorded, not a criterion.)
     **(d) the mock-down run** at `-smp 8`: the relay up, 9999 asserted
     closed; `? ping` ⏎, six seconds, `still here` ⏎, a screendump —
     nineteen lines, the echo the two lines, the notes partition `["still
     here"]`, the screen `> ? ping`, `no answer from the broker`, `> still
     here`, `PROMPT`; the relay's log **one entry whose `error` is
     non-null** — its byte counts *not* asserted, since whether the
     request's eight bytes reach the relay before it closes is a race no
     test may decide. **(e) the grow and the install through the relay**
     at `-smp 4`: the relay up, the mock up with the wire germline wiped, a
     fresh disk; `! test app` ⏎, `wait_record` 1 (150 s), `k`, screen A,
     Esc, `! install echo` ⏎, `wait_record` 2 (150 s), Esc, obs E —
     nineteen lines; the echo the two typed lines; the record: entry 1 by
     the frozen `check_grow_entry` (`"test app"`, generated, calls 1,
     `["pass"]`, the app frame for `stage6/app.bin` with `TEST_CHOICES`),
     entry 2 by the frozen `check_install_entry` (`"install echo"`,
     generated, calls 2, `["pass"]`, the frame with `installed` 1, the
     plan's five verdicts); the germline exactly two entries, each judged
     by the `_7b` transcriptions (nineteen-line logs with `S7: link up`,
     the virtio image all zero); the home partition holding echo at
     `DATA_FIRST` hash-checked (the frozen `check_partitions`), the notes
     partition empty; the twin's SATA disk holding `["after"]` with its
     table byte-exact and its virtio image all zero; **the relay's log:
     two entries, `up` the lengths of GERMLINE.md's two request frames,
     `down` the lengths of the two answer frames the record hashes,
     `error` null; `wire_conns` on obs E equal to the log's count**;
     screen A by the frozen `check_app_panel` (`k`) and `check_mode_field`
     `running test app`. **(f) the reboot with nothing on the wire** — 9999
     and 9997 asserted closed, the same disk: eighteen lines with `S7:
     home 1 apps`; obs R; `! echo` ⏎, `b`, screen L, obs L; Esc — the
     frozen `check_one_cell_panel` `b`, `check_mode_field` `running echo`,
     `check_choices` with `CHOICES_ECHO_RUNNING`; obs L: `wire_conns` 0,
     `bytes_in`/`bytes_out` equal to obs R's; the disk byte-identical to
     after (e).
   The gate's cost: ten boots (four in test 2, three in test 3, three in
   test 4) plus two rehearsals (the test app, echo against its plan); the
   time is measured at item 10 and written into `HANDOVER.md` and the
   CLAUDE.md build block from that run.
7. **The freeze boundary** (item 8): `stage7/WIRE.md`, `stage7/test-7b.sh`,
   `stage7/checkwire.py`; **item 10**: `broker/wire.py`. Not frozen:
   `broker/relay.py` (the spec), `stage7/mkimage.sh`, `stage7/stage7.asm`,
   `broker/claude_backend.py`, `stage7/plan-7b.md`. Everything frozen
   before stands untouched. The "next stage's test file" case stays
   `stage8/test.sh`.
8. **The three commands for the oracle** (test 5), from the repo root, in
   three terminals: `python3 broker/wire.py`, `python3 broker/relay.py
   --bind 127.0.0.1 --port 9997`, and
   ```
   truncate -s 64M stage7/out/disk.img
   qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd \
     -vga none -device VGA,edid=on,xres=1920,yres=1080 \
     -drive format=raw,file=stage7/out/esp.img \
     -drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 \
     -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9997' \
     -device e1000e,netdev=n0,mac=6c:3b:e5:3b:86:45 -serial stdio
   ```
   (remove `stage7/out/disk.img` first for a blank disk — `truncate` on a
   file already 64 MB changes nothing, ring 7a's trap; the 7b gate never
   touches that path). The serial log says `S7: nic 6c:3b:e5:3b:86:45` then
   `S7: link up`; he types `? ping` (the relay's terminal logs one
   connection, `pong` on the screen, `w 001` on the strip), then `! make
   me a clock` — the real backend writes it, the twin rehearses it on a
   SATA disk of its own over an e1000e of its own, and the clock ticks in
   its panel. His word closes the ring.
9. **The prose the hook will dislike.** The new frozen basenames
   (`WIRE.md`, `test-7b.sh`, `checkwire.py`; `wire.py` from item 10) enter
   the prose rule at their freeze; commit messages go in by `-F` from a
   file written with the Write tool. The bodyguard's words stay out of
   every command: no `/dev`, no `sudo`; the down boot's `-S` is not a
   shorthand the hook names (measured); the twin's second `-netdev` is
   inert to it.
10. **Carried, for ring 7c and after** (HANDOVER's caveats): the HP's
    firmware may leave `CAP.SSS` set, so a port may need `PxCMD.SUD`
    before its disk appears (kickoff fact F, ring 7c; no code here); the
    82579LM's PHY may need MDIC work the twin never exercises (the spec's
    high risk: `link up` is the last line before `ready`, its timeout is a
    named error, and the fix is a 7c item with the datasheet open); the
    driver speaks legacy descriptors on one queue, no MSI, no offloads,
    no VLAN, no multicast, no link-change handling after boot (a cable
    pulled after `ready` is a failed question, not a halt); the relay
    serves one connection at a time and speaks plaintext on the home LAN
    by the owner's choice; TLS at Stage 8 or the ring where traffic
    first crosses a network he does not own.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are expected green at its commit**. Items
  0–4 have no ring 7b test; items 5–8 commit with test 1 green and tests
  2–4 failing **by design**; item 9 with tests 1–2 green and 3–4 red; from
  item 10 all four must be green before the commit.
- **`./stage7/test.sh` (ring 7a's gate) stays green on this ring's binary
  throughout** — the regression the kickoff names — and `./stage0/test.sh`
  … `./stage5/test.sh`, `./stage6/test.sh`, `./stage6/test-6b.sh`,
  `./stage6/test-6c.sh` stay green on their own binaries: all run before
  the item 10 and item 11 commits (each needs 9999 free, most 9998 too; no
  two gates at once). Nothing this ring writes is read by any of them.
- `HANDOVER.md` is updated as we go, with a final pass at item 11; the
  model-and-effort record (Fable 5.1 at high effort, the owner's decision
  in the spec, 9 September 2026) goes in at item 0.
- Every new fault class earns a CLAUDE.md gotcha line; the second time a
  mistake is corrected its line goes in.
- Temporary probes are never committed and never undone with `git checkout
  --`: copy aside, restore from the copy. Every probe boots a private copy
  under `stage7/out/probe7b/` (QEMU's image lock; several probes, several
  copies).
- **The scope guard** governs items 9–11: two honest attempts at any one
  obstacle — a real diagnosis from the serial log, the relay's log, the
  rehearsal log, the obs page, a screendump or a register dump, not a
  re-run — then stop, record the exact state in `HANDOVER.md`, commit
  that, and wait for Wajira. A frozen file that needs to change is never
  edited: the diff is written unapplied under `stage7/out/`, recorded, and
  the owner applies it. A seam missing from a frozen broker file is the
  same stop.
- **Everything runs inside QEMU with the caged network (one restricted
  slirp per NIC, one `guestfwd` each), the VGA device and the IvyBridge
  CPU.** The only disks are raw files under `stage7/out/` (the gate's under
  `stage7/out/wire/`, the twin's under `stage7/out/wire/rehearsal/twin/`,
  the probe's under `stage7/out/probe7b/`), created fresh by the harness,
  the broker or the probe. The broker and the twin's listener bind
  `127.0.0.1` only; the relay binds `127.0.0.1` in this ring and refuses
  every other address but the HP's `10.0.2.4`. Nothing outside the repo is
  written, bar scratch files in the session temp directory. **No real
  Claude call is made by this session**: the mock is the only broker the
  gate ever talks to, `claude_backend.grow` is never run here, and test 5
  is Wajira's.
- If the owner says the session budget is nearly spent: finish the current
  item, commit, record the exact state in `HANDOVER.md`, stop.

---

# Part 1 — the document, the relay, the broker module and the acceptance machinery, written before the code

## Item 0 — this plan committed; ring 7b opened in HANDOVER

Copy this file verbatim to `stage7/plan-7b.md` and commit it. The first act
after the gate opens. Record in `HANDOVER.md` that **ring 7b, the wire,
opened on Fable 5.1 at high effort, the owner's decision in the spec**; the
"Where we are" table's stage, status and model rows say so; a "Ring 7b —
the wire" section in the shape of ring 7a's, with the shape from the plan,
an empty test table, and the carried note from 7a's handover (`CAP.SSS`,
kickoff fact F) in its caveats.

*Expected at commit:* no ring 7b tests exist yet. Stages 0–7a green
(unchanged).

## Item 1 — the environment measured: the closed binary in this ring's twin shape, the e1000e as the firmware left it

No source is changed and committed. Ring 7a's binary is booted from a
private copy under `stage7/out/probe7b/` in this ring's twin shape — `-cpu
IvyBridge`, the SATA disk on `ide.1`, the frozen virtio notes disk, the
frozen `virtio-net-pci` on `n0` and the e1000e on `n1` (both cages, both
to a throwaway port), 1920x1080 — at `-smp 2`, `4` and `8`: it reaches
`S7: keyboard ready` with eighteen lines on the virtio path (the e1000e
ignored); the time from QEMU's start to `S7: alive` with the iPXE ROM
present and with `rombar=0` (if the ROM costs seconds or changes the boot
order, the gate's device string gains `rombar=0` — a decision for the plan's
record at this item, before item 5 writes the string). Then **a temporary
probe** in a copy of the source (a few serial lines after the console,
never committed) prints the e1000e's BDF, class dword, command register,
BAR0 and its size (the write-ones probe), and `CTRL`, `STATUS`, `RCTL`,
`TCTL`, `IMS`, `RDBAL`, `RDT`, `TDBAL`, `RAL0`/`RAH0`, `RFCTL`, `MRQC` as
OVMF and its option ROM left them; then, after `CTRL.RST`, the breaths
until `STATUS.LU` returns, and — booted paused with `set_link e1000e.0
off` then `cont` — that `LU` stays clear for as long as the probe watches.
The values go into `HANDOVER.md`'s environment table for the ring. The
probe is removed; `git diff` shows only `HANDOVER.md`.

*Expected at commit:* no ring 7b tests yet. Everything green as before.

## Item 2 — `stage7/WIRE.md`

Decision 5's document. Its lines are deviation 3's list; its relay
contract is decision 3's, the log line's fields named; its twin paragraph
quotes the `-netdev`/`-device` pair `wire.py` will spell and the gate's
own; its supersession paragraph names the two UMBILICAL.md sentences.
Nothing in it is a number a run must supply.

*Expected at commit:* no ring 7b tests yet.

## Item 3 — `broker/relay.py`

Decision 3 in code. Proven on the host alone, no guest, no Claude call:
`--bind 0.0.0.0`, `10.0.2.2`, `192.0.2.1` and the host's LAN address each
refused with exit 2 and the message, nothing listening after; `--bind
10.0.2.4` passes the rule and fails at the bind on this host (errno 99,
quoted — the HP's day is ring 7c's); `--bind 127.0.0.1 --port 9997` prints
the listening line; with `broker/broker.py --mock` on 9999 a `ping` frame
sent by a scratch Python client through 9997 comes back `pong`, the relay's
log holding `up` 8, `down` 8, `error` null; with the mock stopped the same
client gets a closed connection at once and the log an `error`; the
guest's-side close reaches the broker as EOF (the broker's own log says
so); `--port 9999` while the mock holds it is a loud exit.

*Expected at commit:* no ring 7b tests yet.

## Item 4 — `broker/wire.py`

Decision 4 in code. Proven on the host with no guest and no Claude call:
`twin_extra_args("w", 9998)` is `metal.twin_extra_args("w")` plus the
netdev and device pair; `twin.qemu_argv(…, extra_args=…)` carries two
cages, `-cpu IvyBridge`, the `ide-hd`, one virtio drive and the e1000e with
the HP's MAC; `--mock` on a throwaway port with `--image` pointing at a
file that does not exist: `ping` → `pong`, `x` refused, `install nothing`
refused at no cost, `install echo` refused `the twin did not boot` with two
rehearsals recorded and the call total 3 (the ring 6b gotcha again). **Then
one real run through this module's twin on ring 7a's binary**, no token:
`python3 broker/wire.py --rehearse-app stage6/app.bin 'test app'` — the
guest boots on the virtio path with the e1000e beside it, prints eighteen
lines, and the twin, wanting nineteen, fails **`the twin did not boot (…
18 S6: lines, want 19)`** — the frozen judge's phrase (its log line says
"S6:" whatever the prefix, ring 7a's record); the log quoted in the commit
message. That failure is the ring's reason, and item 9 turns it green.

*Expected at commit:* no ring 7b tests yet. No Claude call.

## Item 5 — `stage7/test-7b.sh` with test 1, and test 2's serial boots

Decision 6's harness: the three port refusals, the e1000e cage, the
machine, the display, the disk, the wipes under `stage7/out/wire/`, the
build, test 1 (green: the artefact is 7a's), `serial_check` in its three
modes (`blank`, `again`, `both`) with the frozen `--formatted` and `--esp`
around them, and the call into `checkwire.py --down 2`, which does not
exist yet (the gate reports the missing checker as test 2's failure).

*Expected at commit:* **test 1 green**; **test 2 red** — the two
e1000e-only boots end in `ERR: no virtio-net device on PCI bus 0` right
after the home line, the `both` boot prints eighteen lines with the virtio
MAC `52:54:00:a1:07:02`; the non-zero exit quoted in the commit message.

## Item 6 — `checkwire.py --down` and `--question` (tests 2 and 3)

The checker's skeleton — `qemu_argv`, `drive` with the paused start, the
two pattern lists, `check_boot_lines`, the relay lifecycle and its log's
reader, `start_mock` on `wire.py` — then `--down <smp>` and `--question
<smp>`; `test-7b.sh` gains test 3 at `-smp 2`, `4` and `8`.

*Expected at commit:* test 1 green; **tests 2–3 red** — the `down` boot
prints the virtio error, not the link error; the question boots never
reach ready.

## Item 7 — `checkwire.py --cage` (test 4)

`check_argv_7b`, the relay's bind battery, the mock-down run, the grow and
the install through the relay, the reboot with nothing on the wire, the
`_7b` germline transcriptions; `test-7b.sh` gains test 4 with its
self-assertions. Proven on the host: both argv checks pass on the real
commands and name a stray `hostfwd`, a third netdev, a missing MAC; the
bind battery passes (the relay exists since item 3).

*Expected at commit:* test 1 green; tests 2–4 red — (a), (b) and (c) pass,
(d) never reaches ready.

## Item 8 — freeze the ring 7b acceptance machinery

`PROTECTED` grows `stage7/WIRE.md`, `stage7/test-7b.sh` and
`stage7/checkwire.py`; the hook's comment says why each is a criterion and
why `broker/relay.py` (the spec: a tool, its contract judged through
WIRE.md and the checker), `stage7/stage7.asm`, `stage7/mkimage.sh`,
`claude_backend.py` and `plan-7b.md` are not, and that `broker/wire.py`
joins at item 10. `payloads.py` gains the ring 7b group: `FROZEN_7B`,
`freeze_cases` on the three paths, the `write` denials, a heredoc writing
the checker denied, `sed -i` on the gate denied, an append into WIRE.md
denied; the allowances measured before the plan — `./stage7/test-7b.sh`,
the checker's three modes, `python3 broker/wire.py --mock …` with the
wire germline, bare, `--rehearse-app`, `--rehearse`, `python3
broker/relay.py` with each of its flags (the refusal is the relay's, not
the hook's), the gate's e1000e QEMU line, the `both` boot's two-cage line,
the `down` boot's `-S -monitor stdio` line, the twin's four-device line as
`wire.py` builds it, the oracle's line, `Write` on `broker/relay.py` and
the unfrozen five, `write("stage8/wire.py")` and `write("stage8/WIRE.md")`
allowed, `rm -rf stage7/out/wire stage7/out/probe7b` — and the denials: a
SATA drive outside `out/` on an e1000e line, a shorthand. Re-run whole, 0
wrong; immediacy demonstrated live with one denied call.

*Expected at commit:* test 1 green; tests 2–4 still red; the payload table
0 wrong.

---

*Everything above is written before any driver code exists. Everything
below is the code.*

---

# Part 2 — the implementation, in the spec's order

## Item 9 — the e1000e attached: the device, the reset, the MAC, the link, the rings — TEST 2 GREEN

Decision 2 up to and including the rings' setup, in `stage7/stage7.asm`:
`pci_scan`'s table, `nic_kind`, `nic_find`'s preference, `e1k_attach`, the
two lines, the named errors, the BSS; `net_send`/`net_poll` dispatch to the
e1000e bodies as **stubs that print `ERR: e1000e send not yet written`**
(a question at item 9 is a named error, never a hang). Verified with
temporary, uncommitted probes on private copies under
`stage7/out/probe7b/`: nineteen lines with `S7: nic 6c:3b:e5:3b:86:45` and
`S7: link up` at `-smp 2`, `4` and `8` on the e1000e alone; the same with
the virtio-net beside it in both slot orders; eighteen lines with the
virtio MAC and no link line on the virtio-net alone; the link-down boot's
named error after ten seconds and a halt; the registers after attach
dumped once by the probe (`RCTL`, `TCTL`, `RDT`, `RAH0`) and quoted. Then
`./stage7/test.sh` — ring 7a's gate on this binary — green.

*Green at commit:* **tests 1 and 2**; tests 3–4 red on the stubs alone.
`./stage7/test.sh` green. Stages 0–6 green (nothing they read has changed).

## Item 10 — frames on the wire, `broker/wire.py` frozen — ALL FOUR TESTS GREEN

`e1k_send` and `e1k_poll` replacing the stubs. Probed by hand first on a
private copy: `? ping` through `relay.py` on 9997 to `broker/broker.py
--mock` — `pong` on the screen, the relay's log one line, `w 001` on the
strip; the mock stopped — `no answer from the broker`; **the twin through
`wire.py` on this image — nine of nine** (`--rehearse-app stage6/app.bin
'test app'`, nineteen lines with `link up` in its log, the note on SATA,
the virtio image zero); echo against its plan the same way. Then
`broker/wire.py` frozen (deviation 10): `PROTECTED` gains it,
`payloads.py` its battery, the `write` denial, a heredoc and a `sed -i`
denied, `git add` at its freeze allowed, `stage8/wire.py` allowed; the
table re-run, 0 wrong, the freeze demonstrated live. **Then the gate
whole** — tests 1–4 green at `-smp 2`, `4` and `8` — and the regression
chain: `./stage7/test.sh`, the three ring 6 gates, Stages 0–5.

*Green at commit:* **all four automated tests.** Full `./stage7/test-7b.sh`
output in the commit message. `./stage7/test.sh`, Stages 0–5 and the three
ring 6 gates green.

## Item 11 — HANDOVER, gotchas, README, CLAUDE.md's build block, the payload table, the three commands

`HANDOVER.md` to the green-pending-oracle state (what was built, the
numbers on this build — the e1000e's slot and BAR0, the binary's size, the
gate's time, the twin's autonegotiation time, `w` and `io` on the strip
for a question — tests 1–4 green with output, test 5 pending with decision
8's three commands, decision 10's caveats); `CLAUDE.md`'s build block gains
`./stage7/test-7b.sh`, `python3 broker/wire.py --mock`, `python3
broker/relay.py --bind 127.0.0.1 --port 9997` and the windowed command's
e1000e shape, and the gotchas gain what bit twice (candidates: the tail
descriptor is never the hardware's; `RDT` is written after `RCTL.EN`; the
option ROM's driver leaves rings pointing at freed memory, so reset before
anything; a legacy descriptor's status byte is cleared by software, not
the device); `README.md`'s Stage 7 paragraph and running section gain ring
7b; `python3 .claude/hooks/payloads.py` re-run, 0 wrong; the three
commands printed for Wajira; stop.

*Green at commit:* all four automated tests, `./stage7/test.sh`, the three
ring 6 gates, Stages 0–5.

---

## Verification

- **Automated:** `./stage7/test-7b.sh` from the repo root — refuses to
  start if anything listens on 9999, 9998 or 9997; builds; tests 1–4 (four
  serial boots, the question at `-smp 2`, `4` and `8`, the cage's three
  boots and two rehearsals). Exit 0 only if all pass. Run before every
  commit from item 10 on; its time recorded from the item 10 run.
- **Regression:** `./stage7/test.sh` on this ring's binary before the item
  9, 10 and 11 commits (the virtio path, eighteen lines, the 7a twin);
  `./stage6/test.sh`, `./stage6/test-6b.sh`, `./stage6/test-6c.sh` and
  Stages 0–5's gates before the item 10 and 11 commits. They boot their
  own binaries; this ring's files are invisible to them.
- **The hook:** `python3 .claude/hooks/payloads.py` at items 8, 10 and 11
  — every case from every stage, 0 wrong; immediacy demonstrated live.
- **The probes:** items 1, 3, 4, 9 and 10 each state their expected output
  and quote it in the commit message.
- **Manual (test 5):** Wajira, decision 8's three commands. His word closes
  the ring.

## Safety

Everything runs inside QEMU. Firmware, the IvyBridge CPU model, the VGA
device, exactly two drives per guest of the gate's own — a raw FAT boot
image and a raw 64 MB disk on q35's own AHCI, both under `stage7/out/wire/`
or `stage7/out/` (the twin's copies under `stage7/out/wire/rehearsal/twin/`
with the frozen twin's 16 MB virtio notes file the guest never touches; the
probe's under `stage7/out/probe7b/`) — created by the harness, the broker
or the probe. The storage bodyguard is unchanged: every planned command
was read against its rules before this plan was written. **The network is
a cage in every QEMU line, both netdevs of the twin included**: slirp with
`restrict=on` and one `guestfwd` per netdev, the guest reaching nothing but
`10.0.2.4:9999`, which lands on `127.0.0.1` — the relay on 9997, the
listener on 9998 — and never on the LAN; the relay binds `127.0.0.1` in
this ring and refuses `0.0.0.0` and every LAN address by rule, tested;
the broker binds `127.0.0.1` only, frozen. The automated gate talks only
to the mock, never to Claude, and refuses to run if anything else holds
any of the three ports. The e1000e is written for the first time — inside
QEMU only: `CTRL`, `IMC`, `ICR`, `RCTL`, `TCTL`, `TIPG`, the two rings'
base, length, head and tail registers, `RFCTL`, `MRQC`, `MTA`; `RAL`/`RAH`
are read, never written; `MDIC` and the EEPROM are not touched. This
session makes no Claude call and never runs `claude_backend.grow`. Every
existing frozen file is untouched — `git diff --stat 3baeee7 -- <every
PROTECTED path>` is empty at every commit — and `./stage7/test.sh`, the
three ring 6 gates and Stages 0–5 are green at the end of the ring.
`paper/` is not this ring's and is not touched.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| The twin's 82574L is not the HP's 82579LM: link-up on metal may need PHY work through MDIC | the spec's own answer — `link up` last before `ready`, a ten-second bound, a named error; decision 10 carries it to ring 7c with the datasheet |
| The option ROM's driver (iPXE) leaves the device running with rings in freed memory | `IMC`, `CTRL.RST`, `IMC`, `ICR` before anything else; the reset awaited; item 1 measures what was left and how long the reset takes |
| iPXE's ROM costs boot time or changes OVMF's boot order | item 1 measures `S7: alive` with and without `rombar=0`; the gate's device string decided before item 5 writes it |
| `STATUS.LU` never sets in the twin because autonegotiation needs something the driver did not do | item 1's probe measures the breaths from `RST` to `LU` on the twin before any test is written; `SLU` set, forced speed and duplex cleared, as every Intel driver does |
| BAR0 lies above the 4 GB map or the physical limit on the HP | `map_mmio_2m` creates entries as needed and names the error; the twin's BAR0 is read at item 1, not assumed |
| DMA to rings the device cannot see | bus mastering before any base register; both rings below 4 GB, checked; the high halves written zero |
| A receive buffer overrun into the next slot's twelve header bytes | `RCTL.LPE` clear (the device discards frames over 1522 bytes) and `BSIZE` 2048; deviation 6 says the arithmetic |
| The tail descriptor mistaken for a usable one, or `RDT` written before `RCTL.EN` | the datasheet's convention stated in decision 2 and probed at item 9: sixteen buffers, fifteen owned, one tail |
| The TCP stack touched by accident | `git diff` at items 9 and 10 shows no change between `arp_input` and the end of `tcp_*`; the frozen UMBILICAL.md and Stage 4's own gate on its own binary |
| The frozen 7a gate goes red on this binary | the virtio path kept and dispatched by `nic_kind`; `link up` on the e1000e path only; `./stage7/test.sh` run before every commit from item 9 |
| Two netdevs confuse the twin or the guest | measured: libslirp accepts them, each restricted with its own forward; the guest ARPs on the NIC it chose; test 2's `both` boot and test 4's twin prove both slot orders |
| The relay races the guest on a refused broker | test 4 (d) asserts the error and the count, never the bytes |
| A count in the frozen checker is wrong (ring 6b item 10b again) | the line counts are the pattern lists' lengths; the relay's byte counts are `len(frame(...))` of the test's own requests and the canned answers; the call counts follow the step list (1 then 2); `wire_conns` is compared to the relay's log, not to a literal |
| A defect in `wire.py` found after its freeze | frozen at item 10 after nine of nine and the whole gate through it (A3's precedent); what remains is the scope guard's |
| The bodyguard denies a needed command | every planned command shape was read against the hook's patterns; `-S` measured inert; commit messages by `-F` |
| A frozen file needs to change | the scope guard: stop, the diff unapplied under `stage7/out/`, the owner's hand |
| The gate spends a token | the triple port refusal; the mock's tables; `claude_backend` imported only outside `--mock`; the call counts demanded by the record checks |

---

## Amendments — Cowork's review, adopted before approval

Cowork reviewed the plan on 15 September 2026 and returned five
amendments, none blocking, adopted here verbatim in substance. Where an
amendment contradicts a decision, a deviation or an item above, **the
amendment governs**; the body of the plan is left as written so the review
can be read against it.

**A1 — The relay under a gate that restarts it.** `relay.py` sets
`SO_REUSEADDR` before its bind, as `broker.py` does: `test-7b.sh` starts
and stops the relay per test, 9997 sits in TIME_WAIT between two tests,
and without it the second bind fails while the checker waits for a
listening line that never comes. Each JSON log line is written and flushed
the moment the connection ends: the gate stops the relay by signal, and a
line still in Python's buffer is lost, which turns test 3's entry count red
for a reason that is not the guest's. The port-free refusal in
`test-7b.sh` is a connect probe, as 7a's is, so a port in TIME_WAIT is not
held. WIRE.md states both. (Decision 3 and item 3 gain these two
properties; item 3's host proof starts the relay twice on 9997 in
succession and reads the log after a signal.)

**A2 — The relay's teardown never raises.** Every `shutdown` and `close` on
a socket whose peer has already gone is wrapped and the `OSError`
swallowed, so the splice thread ends cleanly and the log line is still
written. On a broker refusal the guest-side socket may be closed with the
request bytes unread, and Linux then sends a RST rather than a FIN. Both
are `no answer from the broker` by UMBILICAL.md's rule, and the plan
already declines to assert the bytes in test 4 (d). WIRE.md says so, so
nobody later fixes the RST into a FIN and moves a criterion.

**A3 — Test 4 (c) drops the `gethostbyname(gethostname())` case.** On this
Ubuntu the name resolves to loopback and the case is skipped, a criterion
that silently never runs; on another host it is whatever DNS says that
day. The three fixed addresses (`0.0.0.0`, `10.0.2.2`, `192.0.2.1`) prove an
exact-match rule against two literals. The host's LAN address stays an
environment fact in HANDOVER, not a criterion. (Decision 6's test 4 (c)
and item 3's host proof read accordingly.)

**A4 — `e1k_poll` honours the errors byte.** A received descriptor whose
errors byte is non-zero (CE, SE, RXE) is recycled and counted as taken but
never dispatched. QEMU never sets it; the HP's silicon can. One compare,
and it is the datasheet's rule. (Decision 2's `e1k_poll` gains the compare
before the EtherType dispatch; WIRE.md's driver paragraph says so.)

**A5 — The carried list for ring 7c records the ports as this ring settled
them.** In the twin the relay is `python3 broker/relay.py --bind 127.0.0.1
--port 9997` and every 7c QEMU line's `guestfwd` names 9997, not the
spec's 9998; on the HP's day the relay is `python3 broker/relay.py` with no
flags (its defaults are `10.0.2.4` and 9999) beside the broker on
`127.0.0.1:9999`, and `METAL.md` step 5 will say so. The spec's ring 7c
twin command is to be corrected at the 7c gate, not now. (Decision 10 and
`HANDOVER.md`'s caveats at item 11 carry this.)
