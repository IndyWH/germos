# Stage 7, ring 7a — the disk · implementation plan

**To be committed verbatim as `stage7/plan-7a.md`. Produced in plan mode, per
the foundation's build loop. Nothing below is implemented until Wajira
approves this document by writing the approval marker from his own terminal;
the ExitPlanMode hook holds the gate until then. Plan mode allows this
session to write only this one file and forbids commits, so — exactly as
every ring since 6a — the copy to `stage7/plan-7a.md` and its commit
(together with `stage7/spec.md`, approved today) are the first act after
the gate opens, item 0 below, before any other file is touched. Cowork's
amendments while the gate holds are adopted here as numbered amendments
(A1, A2, …) at the end of the document.**

## Context

Stage 6 is closed (5 September 2026). `stage7/spec.md` was approved by the
owner today, 9 September 2026, all recommendations taken, decision 5
amended: Stage 7 is three rings — the disk, the wire, the metal — and
**this is ring 7a, the disk.** Its reason: the patient, an HP Compaq Elite
8300 SFF, keeps its storage on a Q77 AHCI SATA controller, and virtio-blk
does not exist on metal. The done-when, from the spec: **Stages 3 and 6b
re-proven on an AHCI disk in the twin — a note survives a reboot,
`! install echo` lands on the home partition, `! echo` launches with no
broker.** Test 5 is Wajira's, windowed, with the real broker: one note, one
reboot, `! calculator` from a home partition the real broker installed.
His word closes the ring.

What this ring builds, from `stage7/spec.md` and the kickoff:

- **`stage7/`**, a new folder. `stage7/stage7.asm` starts as a copy of
  `stage6/stage6.asm` with the serial prefix `S7:`; `stage7/mkimage.sh`
  packs it. The Stage 6 binary, its three gates and every frozen file are
  untouched; Stages 0–6 stay green forever on their own binaries.
- **The AHCI driver**, per AHCI 1.3: the controller by PCI class (base
  `0x01`, subclass `0x06`, interface `0x01`), ABAR mapped uncached, the
  first port whose signature is a SATA disk (`0x00000101`), the port
  stopped, given a command list and a FIS receive area from BSS, started;
  `IDENTIFY DEVICE` for the sector count; `READ DMA EXT` and `WRITE DMA
  EXT` one command slot at a time, polled, interrupts off, INTx disabled,
  bus mastering set before any address is handed to the controller.
  `blk_rw` keeps its signature; the two virtio devices become two
  **partition descriptors** over one AHCI port. **No virtio-blk code runs
  in the Stage 7 binary.**
- **The disk layout**: the guest owns the disk whole. On a disk with no
  GPT it writes a protective MBR, a GPT header, its backup, and two
  partitions with GermOS's own type GUIDs — **notes** (16 MB) and **home**
  (16 MB) — and prints `S7: gpt written`. On later boots it reads the GPT
  and finds both by type GUID. Inside each partition the frozen format is
  unchanged: `stage3/NOTEBOOK.md` and `stage6/HOME.md` stand byte for byte;
  the partition is the raw image moved to an LBA offset. New line: `S7:
  disk <sectors> notes <lba> home <lba>`. The GUIDs, the offsets, the
  worked-example bytes and the Python GPT reader the checker shares live
  in a new frozen document, **`stage7/DISK.md`**.
- **The twin**: `stage7/out/disk.img`, a 64 MB raw file on q35's own SATA
  controller — `-drive if=none,id=d0,format=raw,file=stage7/out/disk.img
  -device ide-hd,drive=d0,bus=ide.1` — beside `esp.img` on `ide.0`. Every
  Stage 7 QEMU command adds **`-cpu IvyBridge`**; the gate runs at `-smp
  2`, `4` and `8`. No `if=virtio` in a Stage 7 command (one deliberate
  exception, deviation 2). The frozen `broker/twin.py` keeps its virtio
  notes disk: the SATA disk goes through `extra_args`, and the Stage 7
  guest ignores a device it has no driver for. A new module
  **`broker/metal.py`** subclasses the Stage 6 modules as `pointer.py`
  did, never editing a frozen file; its `--mock` serves the same canned
  table.
- **Acceptance tests 1–4**, written red before any driver code, in
  `stage7/test.sh` and `stage7/checkdisk.py`; then **the freeze**:
  `stage7/test.sh`, `stage7/checkdisk.py`, `stage7/DISK.md` and
  `broker/metal.py` into `PROTECTED`, the payload table extended, 0 wrong.
- **`HANDOVER.md`** updated as we go; `CLAUDE.md`'s build block gains the
  Stage 7 commands; every AHCI or GPT mistake corrected twice becomes a
  gotcha. **The owner's decisions, already made:** ring 7a is implemented
  on **Fable 5.1 at high effort** (recorded in `HANDOVER.md` at item 0),
  the policy gate was re-checked in the spec today, the N-of-1 trials come
  after the metal.

The standing orders: the automated gate talks only to the mock, spends no
token and needs no internet; the real `claude -p` backend is exercised only
by the owner at test 5. **The cage, the storage bodyguard and every frozen
file stand**: every path in `PROTECTED` stays byte for byte, and
`./stage6/test.sh`, `./stage6/test-6b.sh`, `./stage6/test-6c.sh` and every
earlier gate must pass at the end of the ring. The storage bodyguard
stands: the only disks are raw files under `stage7/out/` (the twin's under
`stage7/out/rehearsal/`). **The scope guard:** if a frozen file turns out
to be wrong, stop at the commit boundary, write the diff unapplied under
`stage7/out/`, say so in `HANDOVER.md`, and wait; the owner applies it by
his own hand. Never create or mention the approval marker from inside a
session. One commit per numbered item; tests red before the code they
judge; tests green before every commit that should pass them; **every
number in a frozen test is written from a run or derived from the test's
own data, never from arithmetic** (ring 6b item 10b, ring 6c A2).

The plan is **evaluation-first**. Items 1–7 make the folder, the document,
the broker module and the acceptance machinery so that tests 1–4 exist and
tests 2–4 fail before a single instruction of driver code is written. Item
8 freezes them. Items 9–10 grow the guest: **test 1 is green from item 4**
(the artefact of item 1 is a packed PE32+ from the day it is copied — said
plainly, deviation 10); **tests 2, 3 and 4 go green together at item 10**,
when the guest can write the table a blank disk lacks — nothing in the
guest separates them once the table is there (item 9 has the driver and
the reader, and every test starts from a blank disk). Item 11 is the
handover. Test 5 is Wajira's.

### Environment, measured in this session before planning

Read-only: no file was written, no guest was booted, nothing frozen was
touched; the working tree is clean at `b4b098a` but for the untracked
`paper/` (not this ring's) and `stage7/spec.md`. No Claude call was made.

| Fact | Measured how |
|---|---|
| **The toolchain is unchanged:** NASM 3.01, QEMU 10.2.1, Python 3.14.4, OVMF at `/usr/share/ovmf/OVMF.fd`, mtools, OpenBSD netcat. No new package is needed: q35's `ich9-ahci` is built in (`-machine q35,help` lists `sata=<bool>`, default on; `-device ich9-ahci,help` answers), `ide-hd` takes `drive=` and the generic `bus=`, and **`-cpu IvyBridge`** is offered (`Intel Xeon E3-12xx v2`, an alias configured by machine type) | `nasm -v`, `qemu-system-x86_64 --version`, `-device ich9-ahci,help`, `-device ide-hd,help`, `-cpu help`, `-machine q35,help` |
| **Two independent GPT witnesses exist on the host** and neither is a word the bodyguard denies: `/usr/sbin/blkid` (`blkid -p` probes an image file's partition-table type) and `/usr/bin/partx` (`partx -s` lists an image file's partitions with their start and size). Neither touches a device; both read a regular file. The partitioning *tools* the bodyguard names stay unused and unmentioned | `which blkid partx` |
| **Python's `zlib.crc32` is the GPT's CRC-32:** the check value over `123456789` is `0xCBF43926`, the reflected polynomial `0xEDB88320`'s — the UEFI specification's CRC. The guest's routine is proven against the same value | `python3 -c "import zlib; print(hex(zlib.crc32(b'123456789')))"` |
| **The frozen twin cannot read a Stage 7 guest.** `broker/twin.py` holds three things no seam reaches: `re.search(r"S6: obs page 0x…")` (line 332 — without it no obs page, criterion 4 "the app did not run"), `re.findall(r"S6: [^\n]*")` (line 378 — the line count, criterion 1), and `parse_notebook(open(disk))` on the **virtio** notes image it created (line 385 — criterion 8, the note `after` must be on the notebook). `READY` is a module global read at call time (seamable as `VGA_ARGS` is), `lines`, `extra_args` and `after` are seams; the three above are not. `broker/plans.py`'s `tests_hook` searches `rb"S6: obs page"` the same way (line 299). So a Stage 7 guest printing `S7:` fails every rehearsal in the frozen twin — the plan's deviation 1 | read, `broker/twin.py`, `broker/plans.py` |
| **What else in the frozen checkers is bound to `S6:` or to a 16 MB image:** `checkglass.READY`, `check_echo` (splits on `S6: keyboard ready`), `check_germline_entry` and `checkplans.check_install_germline` (count `^S6: ` lines in the rehearsal log against `LINES`), `checkplans.BOOT_PATTERNS`/`check_boot_lines`/`drive` (S6 patterns, the S6 obs-page regex); `check_cage_argv` demands **exactly two `-device`s** (a NIC and the VGA — an `ide-hd` is a third) and every drive under `stage6/out/`; `check_image` and `check_home` open a **path** and demand exactly `DISK_BYTES` (16 MB). Prefix-free and reusable as they are: `read_record`, `record_count`, `check_install_entry`, `check_grow_entry`, `check_question_entry`, `germline_entries`, `fixture_self_check`, `check_region_rows`, `check_choices`, `check_mode_field`, `check_app_panel_blank`, `check_one_cell_panel`, `check_strip`, `check_surfaces`, `check_colour_discipline`, `check_counts`, `port_state`, `report`, `say`, `dump_capture`, `PROMPT`, `parse_home`, `blob_of`, `stop_mock`, the twin's `Driver` and `keyname`, `plans.plan_keyname`, `parse_plan`, `install_key`, `PAD_BIG`, `stage3/checknotes.py`'s `parse_notebook`, `expected_header`, `expected_record` (`main` guarded in all of them) | `grep -n "S6" stage6/checkglass.py stage6/checkplans.py`, read |
| **The current guest's shape around the work** (`stage6/stage6.asm`, 8270 lines): twenty `'S6: '` string literals and four comments; the boot order in `efi_main` is console → `disk_find`/`disk_negotiate` → **line ten `S6: disk <N> sectors`** → `disk_queue_init` → `notebook_init` (line eleven) → `home_find`/`home_negotiate`/`home_queue_init`/`home_init` (line twelve, only with `home_present`) → the NIC; `pci_scan` records the first virtio-blk into `disk_dev`, the second into `home_dev`, the first virtio-net into `nic_dev` by vendor/device id; `vio_attach` sets `PCI_CMD_MEMORY \| MASTER \| INTX_OFF` before touching a BAR and maps every region with `map_mmio_2m`; **`map_mmio_2m` (RAX = a physical address) installs an uncached 2 MB identity mapping and, below 4 GB, overwrites the existing identity entry with an uncached one** — the seam an ABAR needs; `blk_rw` takes EAX = `VBLK_T_IN`/`VBLK_T_OUT`, EBX = the sector, RDI = a 512-byte buffer, RBP = the device block, checks `EBX < [RBP + VIO_SECTORS]`, polls with `PIT_200US` breaths `VQ_POLL_TRIES` (25000, about five seconds) times, counts `OBS_DISK_REQS` and `OBS_DISK_WAIT`, and every failure is a named `ERR:`; `notebook_init` takes the journal length from `disk_sectors`, `home_init`'s format takes the capacity from `[home_dev + VIO_SECTORS]`; the `home_present` flag gates `home_init`, `home_install` (`no home image: <name> not kept`), the lookups and `choices_update`; the NIC uses `vio_attach`, `vio_negotiate`, `vq_init`, `vio_driver_ok` and must keep them | read |
| **NOTEBOOK.md and HOME.md hold inside a partition unchanged.** Both parsers take *bytes* and check the header's capacity against `len(data) // 512` — so a 16 MB partition's bytes, cut from the disk by the GPT reader, parse exactly as a 16 MB image did, and the guest computes the journal length and the capacity from the **partition's** sector count | read, the two frozen documents |
| **The hook's shape for the new group:** `payloads.py` carries a `FROZEN_6C` list and one group per ring; `freeze_cases(paths)` gives the mutation battery per path; the "creating the next stage's test file" case is `write("stage7/test.sh")` → ALLOW and moves on a stage each time a stage freezes its test (the comment at line 225 says so). The bodyguard's `DRIVE_ARG` regex reads `file=` out of any `-drive` argument, quoted or bare, so `-drive if=none,id=d0,format=raw,file=stage7/out/disk.img` is judged by its `file=` under `out/` like every drive before it; `-device ide-hd,…` is not a shorthand it denies; `-cpu IvyBridge` is inert to it; the words this ring needs — *partition*, *table*, *GPT*, *sector*, *AHCI*, *SATA*, *blkid*, *partx* — are none of the denied words | read, `.claude/hooks/protect-tests.py`, `.claude/hooks/payloads.py` |
| **The 6c gate's MAC is `52:54:00:a1:06:03`**; each ring's gate carries its own so the NIC line is checked against a value the assembler cannot know. Ring 7a's is **`52:54:00:a1:07:01`** | read, `stage6/test-6c.sh` |
| **The fresh GUIDs for DISK.md**, generated once here and fixed from now on (decision 3, deviation 5): notes type `50845557-ee34-4731-8b83-d1d6f14fd8c5`, home type `456d4007-d803-41a0-a661-ca736ddcf96b`, the disk `2b74a505-e246-469d-8d73-3bfdc52a8df0`, the notes partition `6e5d297e-0ecb-48c5-92c8-4a93f4e98d44`, the home partition `82bc9169-ce31-4fd9-bf05-63c7521726eb` | `python3 -c "import uuid; print(uuid.uuid4())"` five times |

**To be measured at item 1, before any test is written** (plan mode forbids
a boot): the Stage 7 copy booted in the twin's shape (`-cpu IvyBridge`, the
SATA disk on `ide.1`, the frozen twin's virtio notes disk, `-smp 2`, `4`
and `8`) — that it reaches `S7: keyboard ready` with sixteen lines, that
OVMF boots `esp.img` from `ide.0` with a blank disk on `ide.1` beside it
(the boot order), and — through a temporary, uncommitted probe line — what
the firmware left: the AHCI function's class dword, BAR5 (the ABAR), `CAP`,
`PI`, the port's `PxSSTS`, `PxSIG`, `PxCMD` and `PxCLB` as OVMF's own
driver left them. Recorded in `HANDOVER.md`'s environment table at item 1;
the probe code removed before the commit.

---

## Deviations from the spec and the kickoff, for approval

Each argued from a measured fact or a frozen file. Everything else is the
spec as written.

1. **The frozen twin cannot rehearse a Stage 7 guest; `broker/metal.py`
   carries its own `rehearse_metal`, judged by the frozen `twin.judge`.**
   Measured above: `twin.rehearse` finds its lines and its obs page by
   `S6:` literals and reads the note from the virtio image it made; none
   of the three is a seam. With `S7:` on serial (the spec's choice, the
   kickoff's instruction, the line the metal must print) every rehearsal
   fails "the twin did not boot" — and test 4's `! install echo` is a
   rehearsal. The options:
   - **(a) the owner opens the freeze** on `broker/twin.py` and
     `broker/plans.py` to make the prefix and the notebook's source seams
     (three lines and one), before any ring 7a code. Two frozen files
     amended for one ring, and every later ring reads `S7:` through the
     same seams. Rejected as the more expensive route: a freeze opening is
     for a file that is *wrong*, and the twin is not wrong about Stage 6.
   - **(b) `metal.py` re-spells `twin.rehearse` as `rehearse_metal`
     (recommended):** the same nine criteria, the same `Driver`, the same
     `AppListener`, the same picture helpers and the frozen `judge`
     imported — only the three literals differ: `S7:` for the lines and
     the obs page, and the note read from the **SATA disk's notes
     partition** through DISK.md's reader. `plans.tests_hook`'s closure is
     re-spelled the same way as `tests_hook_metal` (one regex), its
     helpers (`Glyphs`, `panel_rows`, `region_pixels`, `test_line`,
     `plan_keyname`, `SETTLE`) imported. `metal.py` is frozen at item 8,
     so the copy is a criterion exactly as the original is. The cost: some
     hundred and fifty lines of transcription, and a copy that must be
     proven before it is frozen (item 3 runs it for real on the Stage 7
     copy of the binary — seven criteria pass, the eighth fails for the
     reason the ring exists — and item 9 runs it again on a working guest).
   **Recommendation: (b).** Ring 7b's module subclasses `metal.py` the same
   way and inherits the S7 twin.
2. **The twin's command keeps its virtio notes disk, and one boot of test
   2 carries one too.** The kickoff says leave the frozen `qemu_argv`, pass
   the SATA disk through `extra_args`, and let the guest ignore the virtio
   device — so the twin's command is the frozen one plus `-cpu IvyBridge`,
   the SATA drive and the `ide-hd` device (`metal.twin_extra_args`), and
   its virtio `notes.img` is never formatted. That is a fact the gate must
   prove, not assume: test 2's fourth boot (`-smp 2`) adds a blank virtio
   disk to the Stage 7 command — the one `if=virtio` in any Stage 7
   command, deliberately — and demands the same lines as without it, the
   SATA disk formatted, **the virtio image all zero afterwards**; test 4
   demands the same of the twin's `notes.img` after the install's
   rehearsal. "No `if=virtio` anywhere in a Stage 7 command" holds
   everywhere else: the gate's own boots, the checker's, the oracle's.
3. **`S7: gpt written` precedes the disk line.** The disk line reports the
   two partitions' LBAs, which are known only once the table has been read
   or written; so on a blank disk the order is *gpt written*, then *disk*.
   A blank disk prints **eighteen** `S7:` lines, a recognised one
   **seventeen**: alive, edid, gop, boot services exited, gdt and paging
   ours, idt ready, cores found, cores woken, console, [gpt written], disk,
   notebook, home, nic, component region, obs page, glass core, keyboard
   ready. The twin always boots a fresh disk, so `metal.LINES` is eighteen.
   No checker holds either number as a literal: each derives it from the
   length of its own pattern list (decision 7).
4. **Anything that is not GermOS's table is formatted, and a fresh table
   formats both stores.** The spec says "on a disk with no GPT". A drive
   pulled from a cupboard for the HP will most likely carry someone's old
   table; the spec also says it will be wiped by the first boot and the
   guest owns the disk whole. So the recognition rule is NOTEBOOK.md's:
   **recognised** = a primary GPT header at LBA 1 that is valid (signature,
   revision, size, its own CRC, the entries' CRC, `MyLBA` 1, 128 entries of
   128 bytes at LBA 2) *and* holds one entry of each GermOS type GUID;
   **anything else** — a blank disk, an MBR-only disk, a foreign GPT, a
   torn one — is formatted: the whole table written and **sector 0 of both
   partitions zeroed**, so the notebook and the home are formatted on the
   same boot and a stale header at the same LBA from an earlier GermOS life
   can never be read back. The backup header is written on format and read
   never this ring (a damaged primary is a format, not a recovery —
   carried). The safety is unchanged: the guest runs only inside QEMU on
   raw files under `out/` until ring 7c, and on the HP's one sacrificial
   drive after; mlrig's disks are never in its reach.
5. **Every GUID is fixed.** The two type GUIDs are GermOS's own by
   definition; the disk GUID and the two partition GUIDs are fixed too
   (the environment table's five), so the table the guest writes is a pure
   function of the sector count and the checker compares it **byte for
   byte** with what DISK.md's Python builds — the NOTEBOOK.md discipline.
   The alternative, unique GUIDs from `RDRAND` (IvyBridge has it), gives a
   table the checker can only check for shape; uniqueness across disks is
   not a need this stage has (one patient, one disk) and is carried.
6. **The partitions sit at 1 MiB alignment: notes at LBA 2048, home at LBA
   34816; the header's first usable LBA is 34 and its last is `N − 34`.**
   The convention every tool and firmware expects, so the live-USB witness
   the spec wants reads the disk as ordinary. The smallest disk the guest
   accepts is the one whose last usable LBA holds the home partition's last
   sector — a constant DISK.md's Python computes and prints, quoted from
   that run, never typed (67617 sectors by the rule; the run says).
7. **The home is always there.** HOME.md's "with one virtio-blk the machine
   is ring 6a's" and the `no home image: <name> not kept` branch have no
   Stage 7 case: both partitions exist or the boot is a named `ERR:`. The
   guest sets `home_present` unconditionally and the branch stays as dead
   code rather than being cut (the smaller diff; DISK.md says which HOME.md
   sentence it supersedes, as GLASS.md's 6c section did for 6a's).
8. **`-smp` coverage:** test 2 at 8, 4 (the recognised disk), 2 (blank) and
   2 again (with the virtio disk); test 3 at 2 and 8, as Stage 3's was;
   test 4 at **4**, the patient's count. Every value the kickoff names
   appears; the spec's "the gate adds `-smp 4`" is met in tests 2 and 4.
9. **The oracle's windowed command runs at `-smp 4`**, the HP's four
   cores, as ring 7c's command in the spec does; the owner may use 8.
10. **The Stage 7 copy is made at item 1, before the tests.** It is the
    Stage 6 binary renamed, not driver code, and item 1's probe of the
    firmware's AHCI state needs a Stage 7 image to boot; so test 1 (the
    artefact) is green from the moment `stage7/test.sh` exists at item 4,
    and tests 2–4 are red on that copy until item 10 (the copy needs a
    virtio disk the gate never gives it: `ERR: no virtio-blk device`).
11. **`broker/metal.py` is frozen at item 8 with the other three**, as the
    kickoff says, although its twin cannot pass a full rehearsal until the
    guest works (item 9). The mitigation is item 3's real run: every part
    of `rehearse_metal` that differs from the frozen original is exercised
    there (the S7 lines counted, the obs page found, the screens, the
    listener, the SATA disk created and parsed) and only criterion 8 fails,
    for the note landing on the virtio disk the copy still drives. The
    residual risk is the scope guard's.

---

## Decisions taken in this plan

1. **The serial lines** — deviation 3's list; every line of Stage 6's
   keeps its text under `S7:` bar one: **line ten becomes `S7: disk
   <sectors> notes <lba> home <lba>`** (`<sectors>` the whole disk's from
   `IDENTIFY DEVICE`, the two LBAs the partitions' first sectors from the
   table), preceded on a formatting boot by **`S7: gpt written`**. `S7:
   notebook formatted | <N> notes` and `S7: home <N> apps` keep their
   text and follow as before. `S7: mouse ready` is ring 6c's, serial only,
   on the first packet. The display is 1920x1080 in the gate, the twin and
   the oracle's run; nothing is baked in — the checkers read the geometry
   from the guest's own log.
2. **The AHCI driver** (`stage7/stage7.asm`, item 9), replacing
   `disk_find`/`disk_negotiate`/`disk_queue_init`, `home_find`/
   `home_negotiate`/`home_queue_init`, `blk_rw`, `disk_dev`, `home_dev`
   and the two disks' rings; `vio_attach`, `vio_negotiate`, `vq_init`,
   `vio_driver_ok` and `pci_scan` stay for the NIC, `pci_scan` losing its
   virtio-blk branch and gaining a class match (`0x010601` in bits 31:8 of
   register `0x08`) that records the AHCI function's BDF into `ahci_bdf`.
   With interrupts off, polled, one command in flight, BSP only:
   - **`ahci_attach`**: command register `MEMORY | MASTER | INTX_OFF`
     written **before** any BAR is read (the standing gotcha); BAR5
     (register `0x24`) a 32-bit memory BAR, low four bits masked, mapped
     with `map_mmio_2m` (first and last byte of the `0x1100`-byte region;
     the address is read, never assumed — the environment table at item 1
     says where OVMF put it); `GHC.AE` set, `GHC.IE` clear; `CAP` and `PI`
     read into the obs page's spare words for the record (`ahci_cap`,
     `ahci_pi`, `ahci_port` — three `u64` at `0x2C0`, `0x2C8`, `0x2D0`,
     written once at boot; DISK.md says so and supersedes "zero from
     `0x2C0`"); every implemented port polled for `PxSSTS.DET = 3` and
     `IPM = 1` with a bounded wait (up to one second across the ports — the
     spec's spin-up concern, cheap to bound now) and `PxSIG = 0x00000101`;
     the first such port wins, else `ERR: no SATA disk on any AHCI port`
     (no controller at all: `ERR: no AHCI controller on PCI bus 0`).
   - **The port stopped and given ours:** `PxCMD.ST` cleared, `PxCMD.CR`
     awaited clear; `PxCMD.FRE` cleared, `PxCMD.FR` awaited clear (each
     bounded, 500 ms, `ERR: AHCI port would not stop`); `PxCLB`/`PxCLBU`
     = `ahci_clb` (1 KB, 1 KB-aligned BSS, zeroed), `PxFB`/`PxFBU` =
     `ahci_fb` (256 bytes, 256-aligned, zeroed) — both below 4 GB, checked,
     the upper halves written zero; `PxSERR` written all-ones, `PxIS`
     written all-ones, `PxIE` zero; `PxCMD.FRE` set, `PxTFD.BSY|DRQ`
     awaited clear, `PxCMD.ST` set. OVMF's driver bound the device before
     ExitBootServices; nothing about its state is assumed.
   - **One command slot, slot 0:** the command header's `CFL` 5 (a
     20-byte H2D FIS), `W` for a write, `PRDTL` 1, `CTBA` = `ahci_ct`
     (256 bytes, 128-aligned: the FIS at 0, `ACMD` at 64, one PRD at 128).
     The FIS: type `0x27`, `C` set, the command, `device` `0x40` (LBA), the
     48-bit LBA in bytes 4–6 and 8–10, count 1 in bytes 12–13. The PRD: the
     buffer's address (word-aligned, below 4 GB), byte count − 1 = 511, no
     interrupt bit. Issue: `PxTFD.BSY|DRQ` clear (bounded), `PxCI = 1`;
     completion is `PxCI` bit 0 clear, polled with `PIT_200US` breaths
     `VQ_POLL_TRIES` times (`ERR: disk request timed out`, as before);
     then `PxIS.TFES` or `PxTFD.ERR` set is `ERR: disk request failed -
     task file error`, with `PxSERR` and `PxIS` cleared for the record.
     Counted and timed into `OBS_DISK_REQS` / `OBS_DISK_WAIT` exactly as
     `blk_rw` did.
   - **`ahci_identify`** (`0xEC`, 512 bytes into `ahci_ident`): the sector
     count from words 100–103 when word 83 bit 10 (LBA48) is set, else
     words 60–61; a count of 2^32 or more is `ERR: disk has 2^32 sectors
     or more - beyond this stage` (the old message, kept); word 106 bit 12
     set with words 117–118 not 256 is `ERR: disk sector is not 512
     bytes`. The count goes to `ahci_sectors`, and to `S7: disk`.
   - **`ahci_rw`**: EAX = `VBLK_T_IN` (0, `READ DMA EXT 0x25`) or
     `VBLK_T_OUT` (1, `WRITE DMA EXT 0x35`), EBX = the absolute LBA, RDI =
     a 512-byte buffer; `EBX < ahci_sectors` or `ERR: disk request beyond
     the capacity`. Preserves everything, as `blk_rw` did.
   - Interrupts: `PxIE` zero, `GHC.IE` zero, INTx disabled at the function;
     ring 6c's PIC masks (IRQ1, the cascade, IRQ12) stand.
3. **The GPT the guest writes and reads** (DISK.md, item 2; the guest,
   items 9–10). All integers little-endian; GUIDs in GPT's mixed order
   (`uuid.UUID(...).bytes_le`). `N` is the disk's sector count.
   - **LBA 0, the protective MBR:** 446 zero bytes; one partition entry —
     boot indicator `0x00`, starting CHS `00 02 00`, type `0xEE`, ending
     CHS `FF FF FF`, starting LBA 1, size `min(N − 1, 0xFFFFFFFF)`; three
     zero entries; `55 AA`.
   - **LBA 1, the header:** `EFI PART`, revision `0x00010000`, size 92,
     its CRC-32 (computed with the field zero), reserved 0, `MyLBA` 1,
     `AlternateLBA` `N − 1`, `FirstUsableLBA` 34, `LastUsableLBA` `N − 34`,
     the disk GUID, `PartitionEntryLBA` 2, 128 entries of 128 bytes, the
     entries' CRC-32; zero to the end of the sector.
   - **LBAs 2–33, the entries:** entry 0 the notes partition (type, unique
     GUID, first LBA 2048, last LBA 34815, attributes 0, name `GermOS
     notes` in UTF-16LE), entry 1 the home partition (34816 … 67583,
     `GermOS home`), entries 2–127 zero.
   - **LBAs `N − 33` … `N − 2`, the backup entries** (identical), **LBA
     `N − 1`, the backup header** (`MyLBA` and `AlternateLBA` swapped,
     `PartitionEntryLBA` `N − 33`, its own CRC).
   - **The guest's reader** (`gpt_init`): LBA 1 read; recognised by
     deviation 4's rule with the header CRC and the entries' CRC computed
     by `crc32` (bitwise, reflected, `0xEDB88320`, proven against
     `0xCBF43926` on the host at item 9 by a scratch run of the same
     routine's Python twin); the 32 entry sectors read into `gpt_entries`
     (16 KB BSS); the first entry of each type GUID gives its descriptor —
     `base = FirstLBA`, `sectors = LastLBA − FirstLBA + 1` — with the high
     halves required zero and the extent inside `[34, N − 34]`; both found
     or the disk is formatted. Not recognised → **`gpt_write`**: the
     thirty-six sectors above written one at a time through `ahci_rw`,
     sector 0 of each partition written as zeros, `S7: gpt written`; a
     disk with fewer than the minimum sectors is `ERR: disk too small for
     the two partitions` before anything is written. Then the disk line.
     The CRC-32 routine and the table builder live in the guest once; the
     backup header differs from the primary in three fields and is built
     from the same buffer.
4. **The partition descriptors and `blk_rw`.** Two eight-byte descriptors
   in BSS, `part_notes` and `part_home`: `PART_BASE` (u32) and
   `PART_SECTORS` (u32). **`blk_rw`** keeps its signature — EAX the type,
   EBX the sector, RDI the buffer, **RBP the descriptor** — checks `EBX <
   [RBP + PART_SECTORS]` (`ERR: disk request beyond the capacity`), adds
   the base and calls `ahci_rw`. `disk_rw` and `home_rw` are `blk_rw` on
   their descriptor, exactly as they were on their device block. Every
   `VIO_SECTORS` the notebook and home code read becomes the descriptor's
   `PART_SECTORS`: `notebook_init`'s journal length is `part_notes` sectors
   − 1 (32767 for a 16 MB partition — NOTEBOOK.md's worked example, byte
   for byte), `home_init`'s capacity is `part_home`'s sectors (32768 —
   HOME.md's). `disk_sectors` keeps its name and means the notes
   partition's count; `ahci_sectors` is the disk's.
5. **`stage7/DISK.md`** (item 2, frozen at item 8), in NOTEBOOK.md's and
   HOME.md's voice — "the assembler implements this document and the
   checker parses by it; one text, two readers": the disk (one AHCI port,
   512-byte sectors, `N`), the recognition rule (deviation 4), the table
   (decision 3, field by field), the two type GUIDs and the three fixed
   GUIDs with their mixed-order byte dumps, the offsets and the minimum
   size, what "the partition is the raw image, moved" means for the two
   frozen formats (their capacity fields are the partition's), the sentence
   of HOME.md it supersedes (deviation 7), the serial lines (`gpt written`,
   `disk … notes … home …`), the obs page's three AHCI words at `0x2C0`
   (decision 2) superseding the 6c section's "zero from `0x2C0`", the
   errors, the worked example (**every byte quoted from running the
   document's own Python on `N = 131072`** — the MBR, the header, entry 0
   and 1, the backup header — never typed by hand), and "Parsing it cold,
   in Python": `SECTOR`, the GUIDs, `NOTES_FIRST`, `PART_SECTORS`,
   `HOME_FIRST`, `ENTRIES`, `ENTRY`, `min_sectors()`, `guid_bytes(u)`,
   `crc32(data)` (`zlib.crc32`), `protective_mbr(n)`, `gpt_header(n, my,
   alt, entries_lba, entries_crc)`, `partition_entries()`,
   **`build_gpt(n)`** → `{lba: bytes}` for the thirty-six sectors,
   **`parse_gpt(data)`** → `{"sectors", "disk_guid", "entries": [...],
   "notes": (first, sectors), "home": (first, sectors)}` raising
   `ValueError` on anything the document forbids (the MBR, both headers,
   both CRCs, the backup's consistency with the primary), and
   **`partition_bytes(data, part)`** → the partition's bytes for
   `parse_notebook` and `parse_home`. `broker/metal.py` and
   `stage7/checkdisk.py` carry this code verbatim (`metal.py` is the
   importable copy; the checker imports `metal`).
6. **`broker/metal.py`** (item 3, frozen at item 8), standard library
   only, importing the frozen `broker`/`germline` (`serve`, `mock_answer`,
   `log`, `DEFAULT_PORT`), `glass` (`app_frame`, `parse_obs`, `regions`,
   `is_grow`, `CELL_BLOCK`, `STEP_BUDGET_MS`), `twin` (`Driver`,
   `AppListener`, `judge`, `qemu_argv`, `surface_mismatch`,
   `region_background`, `REQUEST`, `NOTE`, `ROW`, `PHRASES`, `SMP`,
   `BUDGET`, `DEFAULT_PORT`), `rehearse` (`load_font`, `row_on_screen`,
   `parse_notebook`, `OVMF`, `DISK_BYTES`, `KEY_GAP`), `plans`
   (`Installer`, `mock_install`, `Glyphs`, `panel_rows`, `region_pixels`,
   `test_line`, `plan_keyname`, `SETTLE`, `DISPLAY`, `PLANS_DIR`,
   `parse_plan`) and `pointer` (`Pointer`, `mock_point`, `point_offset`,
   `POINT_NAME`, `POINT_CHOICES`) — **editing none of them**; importing
   `plans` sets `twin.VGA_ARGS` to 1920x1080.
   - **DISK.md's Python, verbatim** (decision 5), plus `DISK_BYTES_7 =
     64 MB`, `LINES = 18` (deviation 3), `READY = b"S7: keyboard ready"`,
     `LINE_RE`, `OBS_RE`, `MAC_ORACLE`.
   - **`twin_extra_args(workdir)`** → `["-cpu", "IvyBridge", "-drive",
     "if=none,id=d0,format=raw,file=<workdir>/disk.img", "-device",
     "ide-hd,drive=d0,bus=ide.1"]` — the one place the twin's SATA disk is
     spelled; test 4 inspects the command it lands in.
   - **`rehearse_metal(blob, name, choices, image, workdir, port,
     extra_args=(), lines=LINES, after=None)`**: `twin.rehearse`
     transcribed, with exactly these differences — `disk.img` (64 MB,
     blank) created in the workdir beside the frozen shape's `notes.img`
     and `esp.img` copy; the command `twin.qemu_argv(twin_copy, notes,
     serial, port, twin_extra_args(workdir) + extra_args)`; `READY`,
     `LINE_RE` and `OBS_RE` the `S7:` ones; `ev["notes"]` from
     `parse_notebook(partition_bytes(disk, parse_gpt(disk)["notes"]))`;
     the log additionally says whether the virtio `notes.img` stayed all
     zero. Everything else — the listener, the typing, the reads through
     `xp`, the two screendumps, the `after` hook, the quit, the judge — is
     the frozen code's, line for line.
   - **`tests_hook_metal(tests, verdicts)`**: `plans.tests_hook` with
     `OBS_RE`.
   - **`rehearse_metal_plan(...)`**: `pointer.point_offset` first (the
     6c refusal before any boot), then `rehearse_metal` with
     `tests_hook_metal` for an install, no hook for a plain request.
   - **`Metal(Pointer)`**: `self.rehearse = rehearse_metal_plan`; its
     `install` swaps `plans.rehearse_plan` for `rehearse_metal_plan` for
     the duration of the frozen `Installer.install` (called directly, not
     through `Pointer.install`, whose swap is 6c's) and restores it. The
     germline, the record, the dispatch, the mock table (`mock_point`:
     GLASS.md's, PLANS.md's and the 6c row) are all inherited.
   - **`main`**: `pointer.py`'s flags with Stage 7 defaults — `--image
     stage7/out/esp.img`, `--workdir stage7/out/rehearsal/twin`, the
     machine's `germline/` — plus `--rehearse-app BLOB NAME` and
     `--rehearse BLOB PLAN` hand runs through this module's twin. Real mode
     imports `claude_backend` only there. The log line says "the twin boots
     … at 1920x1080 with a 64 MB SATA disk".
7. **The harness — `stage7/test.sh` and `stage7/checkdisk.py`** (items
   4–7, frozen at item 8), ring 6b's shape. `test.sh`: refuses to run while
   9999 or 9998 is held; the cage with **`mac=52:54:00:a1:07:01`**; the
   display spelled once; **the Stage 7 machine spelled once** — `-machine
   q35 -cpu IvyBridge -m 256M -bios OVMF`, `-drive
   format=raw,file=stage7/out/esp.img`, `-drive
   if=none,id=d0,format=raw,file=<disk> -device ide-hd,drive=d0,bus=ide.1`;
   `fresh_disk` makes a **64 MB** zero file; wipes `stage7/out/germline/`
   and `stage7/out/rehearsal/`; builds with the unfrozen
   `stage7/mkimage.sh`. `checkdisk.py`: its own `qemu_argv` (the same
   shape), its own `drive` (checkplans's step vocabulary — `type`, `sleep`,
   `wait_record`, `shot`, `obs`, `surfaces` — with `READY` and the obs
   regex `S7:`), its own `BOOT_PATTERNS` in two lists (`BLANK` with `gpt
   written`, `AGAIN` without) and `check_boot_lines(capture, smp, blank,
   notebook_want, home_want, sectors)` whose expected count is
   `len(patterns)` and whose disk line must carry the sector count of the
   image the harness made (its size ÷ 512) and DISK.md's two LBAs; its own
   `check_echo`, `check_install_germline` (the log holds `len(BLANK)`
   `S7:` lines) and `check_argv_7` (the cage as `check_cage_argv` states it
   but with the `ide-hd` counted as the third device, `-cpu IvyBridge`
   present, exactly two `-drive`s both under `stage7/out/`, none with
   `if=virtio`, one `ide-hd` on `ide.1`); `extract_partition(image, which)`
   writing the partition's 16 MB to `stage7/out/<which>.part.img` so the
   **frozen** `check_image` and `check_home` judge it unchanged; DISK.md's
   Python through `import metal`; everything else imported from
   `checkglass`, `checkplans`, `checknotes`, `twin`, `plans`, `pointer`.
   - **Test 1** (`test.sh`): the artefact, 6a's criteria on
     `stage7/out/BOOTX64.EFI` and `esp.img`.
   - **Test 2** (`test.sh`'s `serial_check`, then `checkdisk.py
     --formatted <image> <sectors> <notes> <home>` for the host's view),
     four boots: **`blank` at `-smp 8`** on a fresh 64 MB disk — eighteen
     lines in order, `S7: gpt written` tenth, the disk line's sectors equal
     to the image's, its LBAs handed to the checker, `notebook formatted`,
     `home 0 apps`, `nic` with the harness's MAC, found = woken = 8; then
     the image from the host: the thirty-six table sectors **byte-identical
     to `build_gpt(131072)`**, the notes partition a formatted empty
     notebook (`parse_notebook` gives `[]`, sector 0 equal to
     `expected_header(16 MB)`), the home partition a formatted empty home
     (`parse_home`: sixteen empty entries), **every other sector of the disk
     zero**; `blkid -p` and `partx -s`, when present, agree on the table
     type and the two partitions' starts and sizes (printed as witnesses,
     asserted when the tools answer). **`again` at `-smp 4`** on the same
     disk — seventeen lines, no `gpt written`, the same disk line, the
     image **byte-identical** afterwards (recognised, nothing written).
     **`fresh` at `-smp 2`** on a new blank disk — eighteen lines. **`virtio`
     at `-smp 2`** (deviation 2): a new blank SATA disk plus a blank 16 MB
     virtio disk — eighteen lines, the SATA image formatted as `blank`'s,
     the virtio image all zero afterwards. Each boot wrapped in `timeout
     60`, exit 124 the expected outcome.
   - **Test 3** (`checkdisk.py --persist <smp>` at 2 and 8): Stage 3's two
     boots on the notes partition. **Run one**, a blank disk: eighteen
     lines; `remember me` ⏎ and `on sata` ⏎ typed through the monitor
     (`plan_keyname`); the echo after ready exactly the two lines; quit;
     the image from the host — the table byte-exact, the notes partition
     holding exactly `["remember me", "on sata"]` with sectors 0–2 equal to
     `expected_header` and `expected_record(1, …)`, `expected_record(2,
     …)` byte for byte and sector 3 not a record; the home partition empty
     and formatted. **Run two**, the same image: seventeen lines with `S7:
     notebook 2 notes` and `home 0 apps`; the echo after ready empty; a
     screendump — the conversation panel's rows `remember me`, `on sata`,
     then `PROMPT` (`check_region_rows`), two colours only; the image
     byte-identical to run one's.
   - **Test 4** (`test.sh`'s cage and machine self-assertions on its own
     strings, then `checkdisk.py --store`, `-smp 4`): **the argv
     assertions** — the checker's command through `check_argv_7`, and the
     twin's as `metal.py` builds it (`twin.qemu_argv(…,
     extra_args=metal.twin_extra_args(workdir))`: the cage on 9998, the
     1080p display, `-cpu IvyBridge`, the `ide-hd` on `ide.1`, its disk
     under `stage7/out/rehearsal/twin/`, and — deviation 2 — the frozen
     virtio notes drive, exactly one); the two fixtures reproduced
     (`fixture_self_check`); the three plans parse; then **boot A** (the
     mock `broker/metal.py --mock` with the gate's germline wiped, a blank
     disk): `! install echo` ⏎, `wait_record` 1 (150 s), Esc — eighteen
     lines, the echo exact, the record one connection judged by
     `check_install_entry` (generated, one call, `["pass"]`, the frame with
     `installed` 1, the plan's five verdicts), the germline entry with an
     **eighteen-line `S7:` rehearsal log** and the hook's "found nothing",
     the home partition holding echo at `DATA_FIRST` hash-checked
     (`check_home`), the twin's SATA disk parsed from
     `stage7/out/rehearsal/twin/disk.img` — a table, a notebook holding
     `["after"]` — and **the twin's virtio `notes.img` all zero**; the disk
     copied aside. **Boot B**, no broker (9999 asserted closed), the same
     disk: seventeen lines with `home 1 apps`; screen P the choices row
     `? ask   ! grow   ! echo`; `! echo` ⏎, `b`, screen L
     (`check_one_cell_panel` `b`, `running echo`, the running row), obs L
     against obs R (`mode 3`, `name echo`, `wire_conns 0`, `bytes_in/out`
     unchanged); Esc; `! undo install echo` ⏎, screen U (`echo has no
     previous build`, `errors 1`, the panel blank); the disk **byte-identical
     to after A**. **Boot C**, the mock with the germline kept: `! install
     liar` (refused `rehearsal failed: expect "a"` after two rehearsals),
     `! install echo, but big` (generated, the padded build), `! install
     echo` (from the germline), `! undo install echo`, `! echo` + `c`
     (screen E), Esc, `last` ⏎, surfaces D, screen D, obs D2 — the record's
     three entries with **the counts ring 6b's frozen, passing `run_store`
     holds** (calls 2, 3, 3; the sources refused, generated, germline), the
     germline exactly two entries, the home partition with the padded build
     current at `DATA_FIRST + 1` and echo previous at `DATA_FIRST + 9`,
     `next_free` `DATA_FIRST + 10`, both extents hash-checked; the notes
     partition `["last"]`; screen D judged by the **frozen** `check_strip`
     and `check_surfaces`, `check_mode_field` `prompt`, `check_choices`,
     `check_app_panel_blank`, `check_region_rows` with the conversation
     from the liar's refusal to the restored build; `check_counts` with
     `keys` derived from the step list and the rest as ring 6b's run gave
     them (`requests 3`, `notes 1`, `errors 1`, `grows 1/1`, `wire_conns
     3`). The step lists are ring 6b's `run_store`'s, in order.
   The gate's cost: nine boots of its own (four in test 2, four in test 3,
   three in test 4 — the numbers are the step lists', not a promise) plus
   four rehearsals (echo, the liar twice, echo but big); the time is
   measured at item 10 and written into `HANDOVER.md` and the CLAUDE.md
   build block from that run.
8. **The freeze boundary** (item 8): `stage7/test.sh`,
   `stage7/checkdisk.py`, `stage7/DISK.md`, `broker/metal.py` — four
   paths. Not frozen: `stage7/mkimage.sh`, `stage7/stage7.asm`,
   `broker/claude_backend.py`, `stage7/plan-7a.md`, `stage7/spec.md`.
   Everything frozen before stands untouched. The "next stage's test file"
   case in the payload table moves on to `stage8/test.sh`.
9. **The two commands for the oracle** (test 5), from the repo root:
   `python3 broker/metal.py` and
   ```
   truncate -s 64M stage7/out/disk.img
   qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd \
     -vga none -device VGA,edid=on,xres=1920,yres=1080 \
     -drive format=raw,file=stage7/out/esp.img \
     -drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 \
     -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
     -device virtio-net-pci,netdev=n0 -serial stdio
   ```
   (the `truncate` only for a blank disk; `./stage7/test.sh` overwrites
   `stage7/out/disk.img`, so an image worth keeping is copied to
   `stage7/out/disk.oracle.img`, a name the harness never touches). He
   types a note, `! install calculator` (the real backend builds it, the
   twin rehearses it on a SATA disk of its own), does a sum, Esc; quits
   QEMU, stops the broker, boots the same command again: `S7: disk 131072
   notes 2048 home 34816`, `S7: notebook 1 notes`, `S7: home 1 apps`, the
   note on screen, `! calculator` on the row and launched from the home
   partition. His word closes the ring.
10. **The prose the hook will dislike.** The new frozen basenames
    (`test.sh` is already one; `checkdisk.py`, `DISK.md`, `metal.py` join)
    enter the prose rule at item 8; commit messages go in by `-F` from a
    file written with the Write tool. The bodyguard's words stay out of
    every command and commit message: the partitioning tools by name,
    *mount*, `/dev`; the table is parsed with DISK.md's Python, `blkid`
    and `partx` only.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are expected green at its commit**. Items
  0–3 have no ring 7a test; items 4–9 commit with test 1 green and tests
  2–4 failing **by design**; from item 10 all four must be green before
  the commit.
- **`./stage0/test.sh` … `./stage5/test.sh`, `./stage6/test.sh`,
  `./stage6/test-6b.sh` and `./stage6/test-6c.sh` stay green throughout**
  — run as regressions before the item 10 and item 11 commits (Stage 4's,
  5's and the three ring gates need 9999 free, 5's and the ring gates 9998
  too; no two gates at once). Nothing this ring writes is read by any of
  them; they are the proof that nothing was.
- `HANDOVER.md` is updated as we go, with a final pass at item 11; the
  model-and-effort record (Fable 5.1 at high effort, the owner's decision,
  9 September 2026) goes in at item 0.
- Every new fault class earns a CLAUDE.md gotcha line; the second time a
  mistake is corrected its line goes in.
- Temporary probes are never committed and never undone with `git checkout
  --`: copy aside, restore from the copy. Every probe boots a private copy
  under `stage7/out/probe7a/` (QEMU's image lock).
- **The scope guard** governs items 9–11: two honest attempts at any one
  obstacle — a real diagnosis from the serial log, the rehearsal log, the
  obs page, a screendump or a hexdump of the disk, not a re-run — then
  stop, record the exact state in `HANDOVER.md`, commit that, and wait for
  Wajira. A frozen file that needs to change is never edited: the diff is
  written unapplied under `stage7/out/`, recorded, and the owner applies
  it. A seam missing from a frozen broker file is the same stop.
- **Everything runs inside QEMU with the caged network, the VGA device and
  the IvyBridge CPU.** The only disks are raw files under `stage7/out/`
  (the gate's `disk.img` and its copies, the twin's under
  `stage7/out/rehearsal/twin/`, the probe's under `stage7/out/probe7a/`),
  created fresh by the harness, the broker or the probe. Both brokers bind
  only `127.0.0.1`. Nothing outside the repo is written, bar scratch files
  in the session temp directory. **No real Claude call is made by this
  session**: the mock is the only broker the gate ever talks to,
  `claude_backend.grow` is never run here, and test 5 is Wajira's.
- If the owner says the session budget is nearly spent: finish the current
  item, commit, record the exact state in `HANDOVER.md`, stop.

---

# Part 1 — the folder, the document, the broker module and the acceptance machinery, written before the code

## Item 0 — this plan and the spec, committed; ring 7a opened in HANDOVER

Copy this file verbatim to `stage7/plan-7a.md` and commit it together with
`stage7/spec.md`. The first act after the gate opens. Record in
`HANDOVER.md` that **Stage 7 — Metal — opened on 9 September 2026** with
the spec's three rings, the patient named, the policy re-check recorded in
the spec, and that **ring 7a opened the same day on Fable 5.1 at high
effort, the owner's decision**; the "Where we are" table's stage, status
and model rows say so; a "Ring 7a — the disk" section in the shape of ring
6c's, with the shape from the plan and an empty test table.

*Expected at commit:* no ring 7a tests exist yet. Stages 0–6 green
(unchanged).

## Item 1 — `stage7/`: the Stage 7 copy, `S7:`, the builder, the firmware's AHCI state measured

`stage7/stage7.asm` copied from `stage6/stage6.asm` with every `'S6: '`
literal and comment made `S7:` and the header comment naming the stage;
`stage7/mkimage.sh` as `stage6/mkimage.sh` with its paths (everything
under `stage7/out/`); `.gitignore` needs nothing (`out/` is covered, no new
binary). Proven: `./stage7/mkimage.sh` builds; the image booted in the
twin's shape under `stage7/out/probe7a/` — `-cpu IvyBridge`, a blank 64 MB
disk on `ide.1`, a blank virtio notes disk, `-smp 2`, `4` and `8` — prints
sixteen `S7:` lines to `S7: keyboard ready` (the copy still drives virtio;
one virtio disk, no home line) and OVMF boots `esp.img` from `ide.0` with
the blank SATA disk beside it. Then **a temporary probe** in the copy (a
few serial lines after the console, never committed) prints the AHCI
function's BDF and class dword, BAR5, `GHC`, `CAP`, `PI`, and for each
implemented port `PxSSTS`, `PxSIG`, `PxCMD`, `PxCLB` as the firmware left
them; the values go into `HANDOVER.md`'s environment table for the ring
(where the ABAR is, whether it lies under the 4 GB map, which port holds
the disk, what state OVMF's driver left the port in). The probe is removed
before the commit; `git diff` shows only the rename and the builder.

*Expected at commit:* no ring 7a tests yet. Everything green as before.

## Item 2 — `stage7/DISK.md`, byte-exact, with the reader the checker shares

Decision 5's document. Its Python is written first and run: `build_gpt`
→ `parse_gpt` round-trips for `N = 131072` and for the minimum `N`;
`min_sectors()` printed and quoted in the prose; a 64 MB image built on
the host from `build_gpt` (a scratch script under `stage7/out/`)
parses with `parse_gpt`, and `blkid -p` and `partx -s` on that image name
a GPT and the two partitions at the document's starts and sizes (the
witnesses quoted); `partition_bytes` of each partition is 16 MB of zeros.
The worked example's byte dumps are the output of the document's own
functions, pasted, never typed. The CRC check value `0xCBF43926` is in
the text as the routine's proof.

*Expected at commit:* no ring 7a tests yet.

## Item 3 — `broker/metal.py`

Decision 6 in code. Proven on the host alone, no guest, no Claude call,
against `--mock` on a throwaway port with `--image` pointing at a file
that does not exist: `ping` → `pong`; `x` → `mock: no canned component
for: x`; `install nothing` → `no plan named nothing` with the call counter
unchanged; `install echo` → the pipeline into the metal twin, which fails
`the twin did not boot` twice (no image), the record carrying the plan's
fields and two calls; `point app` refused before any boot when its header
carries `POINTER2` with a bad offset (the inherited 6c check);
`twin_extra_args("w")` is the six strings of decision 6;
`twin.qemu_argv(…, extra_args=twin_extra_args(w))` carries the cage, the
1080p display, one virtio drive, `-cpu IvyBridge` and the `ide-hd`; the
section's Python agrees with DISK.md's byte for byte (a `diff` of the two
code blocks). **Then one real run through this module's twin on the item
1 image**, no token: `python3 broker/metal.py --rehearse-app
stage6/app.bin 'test app'` — the S7 lines counted (sixteen: the copy with
one virtio disk; `--lines 16` for this run), the obs page found by the S7
regex, the app delivered and run, the two screendumps judged — **seven of
nine criteria pass and the eighth fails with the notebook holding `None`:
the note went to the virtio disk the copy still drives and the SATA disk
has no table** — the log quoted in the commit message. That failure is
the ring's reason, and item 9 turns it green.

*Expected at commit:* no ring 7a tests yet. No Claude call.

## Item 4 — `stage7/test.sh` and acceptance test 1

Decision 7's harness with test 1: the Stage 7 machine spelled once, the
64 MB `fresh_disk`, the cage with the 7a MAC, the display, the port
refusals, the wipes, the build, the summary with decision 9's two commands.

*Expected at commit:* **test 1 green** (deviation 10). Tests 2–4 do not
exist yet.

## Item 5 — `stage7/checkdisk.py --formatted`, and acceptance test 2

The checker's skeleton — DISK.md's Python through `import metal`, the two
pattern lists, `check_boot_lines`, `check_echo`, `extract_partition`,
`--formatted <image> <sectors> <notes> <home>` — and `test.sh`'s
`serial_check` with its four boots.

*Expected at commit:* test 1 green; **test 2 red** — the copy prints `ERR:
no virtio-blk device on PCI bus 0` in the gate's virtio-free machine, and
in the `virtio` boot it prints sixteen lines and a disk line of the old
shape; the non-zero exit quoted in the commit message.

## Item 6 — `checkdisk.py --persist` (test 3)

The checker's `qemu_argv`, `drive`, and the two-boot persistence run on
the notes partition. `test.sh` gains test 3 at `-smp 2` and `-smp 8`.

*Expected at commit:* test 1 green; tests 2–3 red.

## Item 7 — `checkdisk.py --store` (test 4)

`check_argv_7`, `check_install_germline` for the S7 log, the mock
lifecycle with `broker/metal.py`, boots A, B and C with ring 6b's step
lists and their counts, the twin's disk and virtio image inspected.
`test.sh` gains test 4 with its self-assertions.

*Expected at commit:* test 1 green; tests 2–4 red.

## Item 8 — freeze the ring 7a acceptance machinery

`PROTECTED` grows the four paths of decision 8; the hook's comment says
why each is a criterion (DISK.md for the NOTEBOOK.md reason; `metal.py`
because its twin's verdicts and its mock table are what test 4 judges by;
the gate itself) and why `stage7/mkimage.sh`, `stage7/stage7.asm`,
`claude_backend.py`, `plan-7a.md` and `spec.md` are not. `payloads.py`
gains the ring 7a group: `FROZEN_7A`, `freeze_cases` on each path, the
`write` denials, a heredoc writing `metal.py` denied, `sed -i` on the
checker denied; the allowances measured before the plan — `./stage7/test.sh`,
the three checker modes, `python3 broker/metal.py --mock …` with the
gate's germline, bare, `--rehearse-app` and `--rehearse`, `truncate -s 64M
stage7/out/disk.img`, `cp stage7/out/disk.img stage7/out/disk.oracle.img`,
the gate's, the checker's, the twin's and the oracle's Stage 7 QEMU lines
(`-cpu IvyBridge`, the `ide-hd`, the disk under `out/`), the `virtio` boot's
line, `blkid -p stage7/out/disk.img`, `partx -s stage7/out/disk.img`,
`Write` on the unfrozen five, `write("stage8/test.sh")` as the "next
stage's test file" case moving on, `rm -rf stage7/out/probe7a` — and the
denials: a SATA drive whose `file=` is outside `out/`, `-hda` with the
disk, the prose case. Re-run whole, 0 wrong; immediacy demonstrated live
with one denied call.

*Expected at commit:* test 1 green; tests 2–4 still red; the payload table
0 wrong.

---

*Everything above is written before any driver code exists. Everything
below is the code.*

---

# Part 2 — the implementation, in the spec's order

## Item 9 — the AHCI driver, the table read, the two partitions; virtio-blk gone

Decisions 2, 3 (the reader), and 4 in `stage7/stage7.asm`: `pci_scan`'s
class match, `ahci_attach`, `ahci_identify`, `ahci_rw`, `crc32`,
`gpt_init` (recognise, or fall to `gpt_write` — **a stub this item that
prints the error `ERR: disk has no GermOS table` and halts**), the two
descriptors, `blk_rw` over them, `disk_rw`/`home_rw`, `notebook_init` and
`home_init` on the partition sizes, `home_present` set unconditionally,
the disk line; the virtio-blk driver, the two device blocks and their
rings deleted, the NIC's virtio plumbing kept. The BSS gains `ahci_bdf`,
`ahci_abar`, `ahci_port_base`, `ahci_sectors`, `ahci_clb` (1 KB), `ahci_fb`
(256), `ahci_ct` (256), `ahci_ident` (512), `gpt_entries` (16 KB),
`part_notes`, `part_home`. Verified with a **temporary, uncommitted probe**
(a private copy under `stage7/out/probe7a/`, a disk **partitioned on the
host** by DISK.md's `build_gpt` through a scratch script, the monitor):
seventeen lines with `S7: disk 131072 notes 2048 home 34816`, `notebook
formatted`, `home 0 apps`; a note typed and read back from the host at
partition sector 1 (LBA 2049) byte-exact; a reboot replaying it; `!
install echo` against `metal.py --mock` landing at home partition sector 9
(LBA 34825) with its hash; the twin's own `--rehearse-app stage6/app.bin
'test app'` on this image — **nine of nine**, the note found on the SATA
partition, the virtio image zero — the log quoted; `-smp 2`, `4` and `8`
alike; the CRC routine's value for `123456789` printed once by the probe
and equal to `0xCBF43926`.

*Green at commit:* **test 1.** Tests 2–4 red on the writer alone — every
one starts from a blank disk and this binary refuses one with a named
error (the gate's captures quoted). Stages 0–6 green (nothing they read
has changed).

## Item 10 — the table written, the errors — ALL FOUR TESTS GREEN

Decision 3's writer: `gpt_write` — the MBR, the header, the thirty-two
entry sectors, the backup entries, the backup header, sector 0 of both
partitions zeroed, `S7: gpt written` — with `ERR: disk too small for the
two partitions` before any write; deviation 4's rule end to end (a foreign
table formatted, a torn header formatted). Verified by hand first on the
probe copy: a blank disk formatted and byte-identical to `build_gpt` from
the host; a disk carrying a foreign table (a scratch-built GPT with another
type GUID) formatted; a 32 MB disk refused by name; then the gate whole at
`-smp 2`, `4` and `8`, and the regression chain.

*Green at commit:* **all four automated tests.** Full `./stage7/test.sh`
output in the commit message. Stages 0–5 and the three ring 6 gates green.

## Item 11 — HANDOVER, gotchas, README, CLAUDE.md's build block, the payload table, the two commands

`HANDOVER.md` to the green-pending-oracle state (what was built, the
numbers on this build — the ABAR and the port, the binary's size, the
gate's time, `dk` on the strip for a boot — tests 1–4 green with output,
test 5 pending with decision 9's commands, the caveats: the backup header
is written and never read; GUIDs fixed; one port, one slot, polled; the
partitions' sizes fixed at 16 MB; no TRIM, no cache flush command (a
write completes when the device says so, as virtio's did); the twin's
virtio disk; the twin transcribed in `metal.py`; the `home_present` dead
branch); `CLAUDE.md`'s build block gains `./stage7/mkimage.sh`,
`./stage7/test.sh` and `python3 broker/metal.py --mock`, the windowed
command its Stage 7 shape, and the gotchas gain what bit twice (candidates:
the port must be stopped before `PxCLB` is written; `PxSERR` is
write-1-to-clear; a GUID's first three fields are little-endian on disk;
the header CRC is computed with its own field zero); `README.md`'s story
table gains Stage 7's opening row and its running section the Stage 7
ring 7a commands; `python3 .claude/hooks/payloads.py` re-run, 0 wrong; the
two commands printed for Wajira; stop.

*Green at commit:* all four automated tests, the three ring 6 gates,
Stages 0–5.

---

## Verification

- **Automated:** `./stage7/test.sh` from the repo root — refuses to start
  if anything listens on 9999 or 9998; builds; tests 1–4 (four serial
  boots, the persistence pair at `-smp 2` and `-smp 8`, the store at `-smp
  4` with its rehearsals). Exit 0 only if all pass. Run before every commit
  from item 10 on; its time recorded from the item 10 run.
- **Regression:** `./stage6/test.sh`, `./stage6/test-6b.sh`,
  `./stage6/test-6c.sh` and Stages 0–5's gates green before the item 10
  and item 11 commits. They boot their own binaries from their own
  folders; the Stage 7 files are invisible to them.
- **The hook:** `python3 .claude/hooks/payloads.py` at items 8 and 11 —
  every case from every stage, 0 wrong; immediacy demonstrated live.
- **The probes:** items 1, 2, 3, 9 and 10 each state their expected
  output and quote it in the commit message.
- **Manual (test 5):** Wajira, decision 9's commands. His word closes the
  ring.

## Safety

Everything runs inside QEMU. Firmware, the IvyBridge CPU model, the VGA
device, and exactly two drives per guest — a raw FAT boot image and a raw
64 MB disk on q35's own AHCI, both under `stage7/out/` (the twin's copies
under `stage7/out/rehearsal/twin/`, plus the frozen twin's 16 MB virtio
notes file that the guest never touches; the probe's under
`stage7/out/probe7a/`) — created by the harness, the broker or the probe.
The storage bodyguard is unchanged: every planned command was read against
its rules before this plan was written, and the partitioning tools it
names are neither run nor mentioned — the table is read with DISK.md's
Python and witnessed with `blkid` and `partx` on image files. The network
is slirp with `restrict=on` and one `guestfwd` in every QEMU line, the
twin's included; the brokers bind `127.0.0.1` only. The automated gate
talks only to the mock, never to Claude, and refuses to run if anything
else holds either port. The AHCI controller is written for the first time —
inside QEMU only: `GHC`, one port's `CMD`, `CLB`, `FB`, `SERR`, `IS`, `IE`
and `CI`, and the two ATA commands the spec names plus `IDENTIFY`. This
session makes no Claude call and never runs `claude_backend.grow`. Every
existing frozen file is untouched — `git diff --stat b4b098a -- <every
PROTECTED path>` is empty at every commit — and the three ring 6 gates and
Stages 0–5 are green at the end of the ring. `paper/` is not this ring's
and is not touched.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| The frozen twin cannot read `S7:` | deviation 1: `rehearse_metal` in the frozen-to-be `metal.py`, proven at item 3 (seven criteria on the copy) and item 9 (nine on the guest) before the gate depends on it |
| A defect in the transcribed twin found after its freeze | item 3's real run exercises every changed line but the SATA notebook read, which item 2 proves on host-built images; what remains is the scope guard's |
| The ABAR lies above the 4 GB map or the physical limit | `map_mmio_2m` creates entries as needed and names `ERR: BAR lies beyond the physical address width`; item 1 measures where it is before a line of driver code |
| OVMF's driver left the port running | the port is stopped (`ST`, then `FRE`, each awaited) before `CLB`/`FB` are written; a port that will not stop is a named error |
| DMA to a ring the controller cannot see | bus mastering set before any address is handed over; `CLB`, `FB` and every buffer checked below 4 GB; the upper halves written zero |
| A stale interrupt line | `PxIE` 0, `GHC.IE` 0, INTx disabled; the PIC masks unchanged |
| A wrong CRC in the table | one routine, proven against the standard's check value on the host and printed once by the item 9 probe; the checker recomputes both CRCs and compares the table byte for byte |
| The GUID byte order | `bytes_le` in the Python, the mixed-order dumps in DISK.md's worked example, the byte-exact comparison |
| A foreign or torn table on the sacrificial drive | deviation 4: formatted, both partitions zeroed at sector 0; inside QEMU on raw files under `out/` until ring 7c |
| The partitions' frozen formats break inside a partition | measured: both parsers take bytes and check capacity against their own length; the guest computes both from the partition's sector count; test 2 parses both cut from the disk |
| A count in the frozen checker is wrong (ring 6b item 10b again) | the line counts are the pattern lists' lengths; the LBAs are DISK.md's constants; the store's counts are ring 6b's frozen, passing checker's, replayed step for step; `keys` derived from the steps |
| The Stage 7 copy behaves differently under `-cpu IvyBridge` or `-smp 4` | item 1 boots it at 2, 4 and 8 before any test is written |
| A blank `ide.1` disk changes OVMF's boot order | item 1 measures it; the fallback is `bootindex=0` on the ESP's drive as a `-device` (a builder change, not a criterion) |
| The twin's virtio disk is silently driven by leftover code | the virtio-blk code is deleted, not bypassed; test 2's `virtio` boot and test 4's twin check demand an all-zero image |
| A frozen file needs to change | the scope guard: stop, the diff unapplied under `stage7/out/`, the owner's hand |
| The gate spends a token | the double port refusal; the mock's tables; `claude_backend` imported only outside `--mock`; the call counts demanded by the record checks |
| The bodyguard denies a needed command | every planned command shape was read against the hook's patterns; `blkid`/`partx` chosen over the denied tools; commit messages by `-F` |

---

## Amendments — Cowork's review, adopted before approval

Cowork reviewed the plan on 9 September 2026 and returned four amendments,
adopted here verbatim in substance. Where an amendment contradicts a
decision, a deviation or an item above, **the amendment governs**; the
body of the plan is left as written so the review can be read against it.

**A1 — Blocking: port selection, and no disk is ever formatted over.**
The twin always has two SATA disks — `esp.img` on `ide.0` (port 0) and
`disk.img` on `ide.1` — and the rehearsal twin can never change that,
because the frozen `qemu_argv` puts the boot image on SATA. Decision 2's
rule (the first port with a SATA disk wins) together with deviation 4
(anything that is not a GermOS table is formatted) would write a partition
table over `esp.img` on the first boot. Both are replaced by this rule:

- **Every implemented port with a SATA disk is identified** (`IDENTIFY
  DEVICE` on each; the port's signature, `PxSSTS`, and its sector count
  recorded).
- **The chosen port is the one holding a recognised GermOS table** (the
  primary header valid by deviation 4's validity test, both type GUIDs
  present).
- **If none, the chosen port is the one whose disk has sectors 0 and 1
  entirely zero**, and that disk is formatted (`S7: gpt written`).
- **If none, `ERR: no GermOS disk and no blank disk`**, naming each port
  and what it holds (a GermOS table, a foreign table, an MBR, a boot
  sector, a torn GermOS table, or a blank), and halt.
- **A foreign table, an MBR, a boot sector, a torn GermOS table: refused,
  never formatted.** Deviation 4 is **withdrawn**; its "sector 0 of both
  partitions zeroed on format" stands only for the blank-disk format,
  where it is a no-op stated for the record.

`stage7/DISK.md` states the recognition rule *and* the selection rule. The
disk line gains the port: **`S7: disk port <p> <sectors> notes <lba> home
<lba>`** (decision 1 and decision 3's line, `checkdisk.py`'s patterns and
`--formatted`'s arguments updated accordingly). **Test 2 gains, for every
boot, `esp.img` byte-identical before and after**, and **one more boot on
a disk carrying a foreign table** (built on the host by DISK.md's Python
with another type GUID, under `stage7/out/`) that ends in the named error
with the image untouched — five serial boots. **Item 10's foreign-table
check becomes a refusal**, and the 32 MB disk stays a refusal (`ERR: disk
too small for the two partitions` on the blank disk it would otherwise
format). Item 9's stub error becomes the selection rule's own (`no GermOS
disk and no blank disk` on a blank disk, since item 9 has no writer). For
the HP, `METAL.md` at ring 7c will tell the owner to zero the drive's first
sectors from the live USB before the first boot.

**A2 — The twin's SATA read never raises.** In `rehearse_metal`, the SATA
disk read (`parse_gpt`, `partition_bytes`, `parse_notebook`) is wrapped so
that any `ValueError` or a short read yields `ev["notes"] = None` and a
line in the log saying why (`notebook: <reason>`), never an exception out
of the rehearsal — the frozen `judge` then gives criterion 8's phrase.
**Item 3's real run must exercise exactly that path** (the Stage 7 copy
leaves the SATA disk without a table, so `parse_gpt` raises) **and quote
the verdict line** in the commit message.

**A3 — `broker/metal.py` is not frozen at item 8.** It joins `PROTECTED`
**at item 10**, after the gate has passed nine of nine through it, with its
own payload cases (the `write` denial, the heredoc denial, `freeze_cases`
on the path, the allowances for its modes) added then and the table re-run
at 0 wrong. `stage7/test.sh`, `stage7/checkdisk.py` and `stage7/DISK.md`
freeze at item 8 as planned; decision 8's boundary reads three paths at
item 8 and four from item 10. **Deviation 11 is withdrawn.** Reason: four
of the project's five freeze openings were in frozen Python that could not
be exercised before it froze.

**A4 — A record, not a change.** `-cpu IvyBridge` advertises x2APIC. At
item 1, the probe also prints, and `HANDOVER.md`'s environment table
records, whether OVMF left the BSP in xAPIC or x2APIC mode (`IA32_APIC_BASE`
bit 10) at `-smp 2`, `4` and `8`. If x2APIC, `HANDOVER.md` says that Stage
1's unproven x2APIC path was exercised for the first time at ring 7a, and
notes that the i5-3570 carries the same flag.
