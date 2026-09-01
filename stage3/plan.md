# Stage 3 — implementation plan

**To be committed as `stage3/plan.md`. Produced in plan mode, per the foundation's
build loop. Nothing below is implemented until Wajira approves this document.**

## Context

Stage 2 is closed: Wajira confirmed test 5 just after midnight on 1 September
2026. Stage 3 gives the machine *memory of its own*: a virtio-blk driver found
on the PCI bus and driven through the modern interface, a deliberately tiny
append-only notebook filesystem of our own design, and one visible behaviour —
every line entered at the prompt is written through to disk before the next
prompt appears, and the next boot replays it above the prompt. Type a note
tonight; tomorrow's boot shows it back. That is the foundation's done-when:
the OS keeps what it grows.

`stage3/spec.md` is approved and fixes the behavioural order, the new serial
lines, five acceptance tests, and the owner's three decisions: our own notebook
format per `stage3/NOTEBOOK.md`, every entered line persists automatically, and
the **overnight scope guard** — if virtio negotiation or anything else fights
back for more than two honest attempts, stop, record exactly where things stand
in `HANDOVER.md`, and leave the rest for the morning. No improvisation around
a storage device at 3 a.m.

This is an overnight, unattended run, so the plan is written as a recipe: the
facts it rests on were verified in this session before a line of it was
drafted, and every judgement call is listed up front so Wajira can overrule it
at approval rather than discover it in a diff.

The plan is **evaluation-first**, and it opens with the bodyguard: item 1 makes
the foundation's hard safety rule mechanical before any driver or filesystem
code exists. Items 2–6 write the format and the acceptance machinery so tests
1–4 exist and fail before a single instruction of `stage3.asm` is written. Item
7 freezes them. Items 8–12 grow the implementation on Stage 2's proven body,
and the gate closes at item 12. Test 5 is Wajira's eyeball and stays manual.

### Environment, verified in this session before planning

No new packages. The toolchain is Stage 2's: NASM 3.01, QEMU 10.2.1, Python
3.14, OVMF, mtools. Every probe below used a scratch image under
`stage3/out/` and nothing else.

| Fact | Verified how |
|---|---|
| `-drive format=raw,file=<img>,if=virtio` on q35 presents a **transitional** virtio-blk-pci: vendor `1af4`, device `1001`, subsystem `1af4:0002`, at bus 0 device 3 function 0; QEMU properties `disable-legacy=off`, `disable-modern=false` | `info pci` and `info qtree` over the monitor |
| Its BARs after OVMF has run: BAR0 I/O at `0x6000` (legacy), BAR1 32-bit MMIO at `0x810c5000` (MSI-X), **BAR4 64-bit prefetchable at `0xC000000000`**, 16 KB — the modern capability region | `info pci` taken after the guest printed `S2: keyboard ready` |
| So the modern registers sit at 768 GB — above the 4 GB identity map **and above the 512 GB that Stage 2's single PML4 entry covers**. The driver must map the BAR wherever the firmware put it | arithmetic on the address above; the paging code in `stage2/stage2.asm` `build_paging` |
| Stage 2's image still boots to `S2: keyboard ready` with the virtio drive attached as a second `-drive` after the boot image — OVMF finds no ESP on the blank disk and boots ours | the same probe run |
| PCI ECAM/MMCONFIG is **not** enabled by OVMF here (`xp` at `0xB0000000` reads "Cannot access memory") — PCI config space goes through ports `0xCF8`/`0xCFC`, which q35 always provides for bus 0 | monitor `xp` in the same run |
| The device reports 512-byte logical and physical blocks | `info qtree` |
| A 16 MB raw file created with `truncate` is read by QEMU as a 32768-sector disk of zeros | file size arithmetic; the first-boot format path depends on the blank sector 0 |
| Monitor-over-stdio driving, `sendkey`, screendumps and serial-to-file all still work together | `stage2/checktext.py` is green as of Stage 2's closure |

One thing learned and worth carrying into the code: OVMF's own virtio-blk
driver binds the device during boot (that is how it looked for a boot loader on
it) and resets it at ExitBootServices. Our driver resets it again regardless —
we assume nothing about the state the firmware left.

---

## Decisions taken in this plan

Judgement calls inside the approved spec. Flagged here so Wajira can overrule
any of them at approval.

1. **The eleven serial lines, exactly.** Each CRLF, decimal numbers, no
   padding:
   `S3: alive` · `S3: gop <W>x<H> fb 0x<16 lowercase hex>` · `S3: boot services
   exited` · `S3: gdt and paging ours` · `S3: idt ready` · `S3: cores found <N>`
   · `S3: cores woken <N>` · `S3: console <COLS>x<ROWS>` · **`S3: disk <N>
   sectors`** · **`S3: notebook formatted`** *or* **`S3: notebook <N> notes`**
   (exactly one of the two, `notes` never pluralised differently — `1 notes`
   is the spec's own text) · `S3: keyboard ready`. The two new lines sit
   between console and keyboard so that `keyboard ready` stays the last line
   before `sti` and the serial contract after it stays exactly Stage 2's: the
   raw echo and nothing else. Disk work therefore runs with interrupts off,
   polled, which is the simplest honest driver. `ERR:` remains the failure
   voice, now also for the disk (`ERR: no virtio-blk device on PCI bus 0`,
   `ERR: disk request timed out`, and so on — each one named).
2. **The notes are console-only.** A replayed note is drawn on the screen and
   never sent to serial — like the prompt, and for the same reason: after
   `keyboard ready` the wire carries only the echo. The persistence test's
   second run asserts the bytes after `keyboard ready` CRLF are **empty**,
   which is how a leak of notes onto the wire would be caught.
3. **Screen order on the second boot:** the eleven boot lines, then each note
   on its own line from column 0 (text only, no prefix), then the `> ` prompt
   and cursor. The notes are drawn after `S3: keyboard ready` is on the wire
   and before the prompt, so they sit immediately above it, as the spec says.
4. **The notebook format** (in full in `stage3/NOTEBOOK.md`, item 2), the
   smallest honest thing that proves persistence. Sector 0 is the header:
   magic `NOTEBOOK` (8 ASCII bytes), u32 version 1, u32 sector size 512, u64
   first journal sector 1, u64 journal sector count (capacity − 1), zeros to
   the end. The journal is **one note per 512-byte sector** from sector 1:
   `NOTE` (4 ASCII bytes), u32 sequence number (1-based, equal to the note's
   number and to its sector index), u16 length 1–500, u16 reserved zero, the
   text from offset 12, zeros to the end of the sector. All integers little
   endian. The journal ends at the first sector that is not a valid record;
   formatting writes the header **and zeroes sector 1**, so a reused disk
   cannot resurrect stale notes. One note per sector means every append is a
   single sector write with no read-modify-write, and the checker can parse
   the image cold with `struct` and nothing else.
5. **The header holds no note count.** An append-only journal recovers its
   count by scanning; a counter in the header would need a second write per
   note — a second window for a torn state. The boot scan reads N+1 sectors
   for N notes; at 32767 sectors the worst case is still under a second.
6. **What is a note.** The bytes typed between a prompt and Enter, after
   backspaces are applied — and the buffer follows the screen: a Backspace is
   recorded only when the console accepted it (Stage 2's rule: never past the
   prompt, never back up a wrapped row). **An empty line is not a note** —
   Enter on an empty line gives a new prompt and writes nothing (a blank
   greeting line would prove nothing and would clutter the morning). A line is
   capped at **500 bytes**, the record's capacity: the 501st printable key on
   a line is ignored — not echoed, not drawn — so that what is on screen is
   exactly what will be on disk. Neither limit is reachable by the tests.
7. **Write-through, then prompt.** On Enter the main loop echoes CRLF (Stage
   2's contract), then builds the record, issues the write, and **waits for
   the device to complete it and report status OK** before `console_prompt`
   draws the new prompt. The spec's power-cut guarantee follows: a prompt on
   screen means the note is on the disk.
8. **A full notebook drops the line, silently, and keeps running.** Halting
   the machine over a full diary is worse than losing one line; 32767 notes
   on the test image makes this unreachable, and it is recorded here as a
   known edge rather than an accident.
9. **The driver speaks the modern interface only.** VIRTIO_F_VERSION_1 is
   required; a device that does not offer it is an `ERR:`, not a fallback to
   the legacy I/O BAR. Exactly one feature is accepted — VERSION_1 — nothing
   else (no indirect descriptors, no event index, no packed ring): the device
   must confirm FEATURES_OK or we stop with a message. The transitional
   device QEMU presents carries the modern capabilities, and Stage 7's NVMe
   or a modern-only virtio device will not have a legacy BAR at all.
10. **The BAR is mapped wherever the firmware put it.** A generic
    `map_mmio_2m(phys)` routine installs a present, writable, **uncached**
    (PWT|PCD) 2 MB page for any physical address — creating the PML4 and PDPT
    entries if absent, from a small pool of spare 4 KB page-table pages in
    BSS (8 pages; exhaustion is an `ERR:`). The address is read from the BAR
    at runtime, never assumed; on this machine it will land at
    `0xC000000000` (verified above), which exercises the new-PML4-entry path
    on the first run. The physical address width from CPUID `0x80000008` is
    checked first so a BAR beyond it is a message rather than a reserved-bit
    fault.
11. **PCI is enumerated the plain way.** Bus 0 only, devices 0–31, functions
    0–7 when the header type byte says multi-function, through `0xCF8`/`0xCFC`.
    A match is vendor `0x1AF4` with device `0x1001` (transitional block) or
    `0x1042` (modern block); the first match wins. Capabilities are walked
    from the pointer at config offset `0x34`, taking vendor-specific (ID 9)
    entries of type 1 (common), 2 (notify, with its multiplier), 3 (ISR) and 4
    (device); each address is BAR base + offset, computed from the BAR the
    capability names. The command register gets MEMORY, BUS MASTER and
    **INTX_DISABLE**: DMA does not happen without bus mastering, and we poll,
    so the device's line interrupt must never be asserted into a PIC that has
    only IRQ1 unmasked.
12. **Accesses to the common configuration are exactly the field's width**,
    and the 64-bit fields (queue addresses, capacity) are written and read as
    two 32-bit halves — the spec says so and QEMU enforces it. One byte for
    status, 16 bits for queue fields, 32 for features, two 32s for the rest.
    This is the kind of detail that costs an hour at 3 a.m., so it is a plan
    line.
13. **One queue, one request at a time, polled.** Queue 0, its size read from
    the device (an `ERR:` if above 256, our static ring capacity, or not a
    power of two); descriptor table, available ring and used ring in BSS,
    4 KB-aligned, addresses handed over as guest-physical (the identity map
    makes them equal to what `lea` gives). A request is a three-descriptor
    chain — 16-byte header (type, reserved, sector), the 512-byte data
    buffer (device-writable for a read), a one-byte status (device-writable,
    preset to `0xFF`) — placed in the available ring, `mfence`, index
    bumped, `mfence`, then a 16-bit write of the queue number to the notify
    address (notify base + `queue_notify_off` × multiplier). Completion is
    the used index changing, polled with `pit_wait` between looks and bounded
    at about five seconds, after which `ERR: disk request timed out`. Status
    must be 0 (`VIRTIO_BLK_S_OK`) or `ERR: disk request failed`. The
    available ring's `NO_INTERRUPT` flag is set as well, belt and braces.
14. **One driver, three assertions.** `stage3/checknotes.py` owns the whole
    two-boot run exactly as `checktext.py` owns Stage 2's run. Mode
    `--persist <smp>` (test 3): create a fresh 16 MB image, boot, wait for
    `S3: keyboard ready`, type `r e m e m b e r spc m e ret` one key at a time
    with ≥ 150 ms gaps, settle, quit, reap; **parse the image from the host**
    and demand exactly one record, byte-exact per NOTEBOOK.md, reading
    `remember me`; boot the **same** image in a fresh QEMU, wait for ready,
    settle, quit; demand the eleven lines with `S3: notebook 1 notes`, an
    empty channel after `keyboard ready`, and the image **byte-identical** to
    what run one left (replay never writes). Mode `--pixels` (test 4): the
    same at `-smp 8` plus a screendump at the end of run two: `remember me`
    rendered from `stage2/font8x8.bin` appears exactly once, the prompt and
    cursor sit on the row directly below it, nothing but the two console
    colours anywhere. The font stays Stage 2's frozen file — one font, used
    three times now.
15. **The bodyguard's shape** (item 1). A new arm of the Bash check that runs
    on **every** Bash call, before and independently of the frozen-file
    check, and denies: any mention of `/dev/sd`, `/dev/nvme`, `/dev/disk`,
    `/dev/mapper` (the spec's four) and, in the same spirit, `/dev/hd`,
    `/dev/vd`, `/dev/loop`, `/dev/mmcblk`, `/dev/md`, `/dev/dm-`, `/dev/block`;
    the words `mount`, `umount`, `losetup`, `mkfs` (which covers `mkfs.ext4`),
    and the partitioning and wiping tools `fdisk`, `sfdisk`, `gdisk`, `parted`,
    `wipefs`, `blkdiscard`; `sudo`; a QEMU `-drive` whose `file=` is not a
    literal path inside a repo `out/` directory (relative like
    `stage3/out/notes.img`, or absolute under the repo — no `..`, no shell
    variable, since the hook cannot resolve one and must not guess); the QEMU
    shorthands `-hda`..`-hdd`, `-cdrom`, `-fda`, `-fdb`, `-blockdev`,
    `-pflash`, `-mtdblock`, `-sd`; and `qemu-img` with any path argument
    outside `out/`. Allowed as sources: `/dev/zero`, `/dev/urandom`,
    `/dev/random`, `/dev/null`, `/dev/stdin`, `/dev/stdout`, `/dev/stderr`,
    `/dev/fd/`, `/dev/tty`. Prose matches deliberately, as the freeze does:
    a commit message that says "no loop mount" is denied and goes in through
    `git commit -F` from a file written with the Write tool. A false deny
    costs a reworded command; a false allow costs a real disk.
16. **The payload table is committed this time**, as
    `.claude/hooks/payloads.py`: the Stage 0, 1 and 2 cases reconstructed from
    their commit records (the earlier tables lived in scratch), plus the
    Stage 3 storage cases and, at item 7, the Stage 3 freeze cases. Running
    it is `python3 .claude/hooks/payloads.py` — a command that mentions
    nothing the hook dislikes — and it exits non-zero if a single payload is
    judged wrongly. Cowork's review can re-run it, which is the point.

---

## Conventions for every item

- One commit per numbered item.
- Each item states **which tests are expected green at its commit**. Items
  1–7 commit with every Stage 3 test failing **by design** — there is no
  `stage3.asm` yet. That failure is the evidence the gate is real.
- From item 8 on, the stated tests must be green before the commit is made.
- **`./stage0/test.sh`, `./stage1/test.sh` and `./stage2/test.sh` stay green
  throughout** — run as regressions before every commit.
- `HANDOVER.md` is updated as we go, with a final pass at item 13.
- `/clear` between numbered items.
- Every new fault class earns a CLAUDE.md gotcha line and a regression check.
- Temporary probes are never committed, and never undone with
  `git checkout --`: copy aside, restore from the copy.
- **The scope guard** governs items 9–12: two honest attempts at any one
  obstacle, then stop, record the exact state in `HANDOVER.md` (what was
  tried, what the serial log said, which item is open), commit that, and
  leave the rest for the morning. "Honest" means a real diagnosis from the
  serial log, not a re-run.
- **Everything runs inside QEMU.** The only disks in existence are files
  under `stage3/out/`, created fresh by the harness. Nothing outside the repo
  is written, bar scratch files in the session temp directory.

---

# Part 1 — the bodyguard and the acceptance machinery, written before the code

## Item 1 — the storage bodyguard

The hard safety rule becomes a hook before any storage code exists.
`.claude/hooks/protect-tests.py` grows the storage arm of decision 15 — a
`STORAGE` table of (pattern, reason) pairs and an `out/`-path judge for QEMU
drive files, run on every Bash call ahead of the frozen-file check — with a
denial message that quotes the rule from the foundation. `.claude/hooks/
payloads.py` is written (decision 16) with three groups: the earlier stages'
freeze cases re-run, the storage denials (each `/dev` prefix; each verb; a
`-drive file=/tmp/x.img`; `-drive file=$IMG`; `-hda`; `qemu-img create
/tmp/x.img`; `sudo ls`; `dd of=/dev/sda`; a commit message mentioning a loop
mount), and the storage allowances (`dd if=/dev/zero of=stage3/out/x.img`,
`truncate -s 16M stage3/out/notes.img`, `head -c 16 /dev/urandom`, the
Stage 2 and Stage 3 QEMU commands with `-drive file=` under `out/`, `-bios
/usr/share/ovmf/OVMF.fd`, `qemu-img info stage3/out/notes.img`, `cat /dev/null`,
`./stage2/test.sh`, and the words `amount` and `mountpoint`, which must not
match). Per amendment A4 the edit bites at once, and that is **demonstrated,
not assumed**: after the edit, one harmless Bash call that the new rule covers
(`ls -l /dev/sda`) is attempted and must be denied by the live hook, and one
control (`head -c 8 /dev/urandom | xxd`) must be allowed.

*Expected at commit:* no Stage 3 tests exist yet. Stage 0, 1 and 2 green. The
payload table 0 wrong.

## Item 2 — `stage3/NOTEBOOK.md`: the on-disk format

The format of decision 4, byte-exact: a header table (offset, size, type,
value), a record table, the little-endian rule, the end-of-journal rule, the
format-on-first-boot rule (header + zeroed sector 1), the one-note-per-sector
rule and the 500-byte cap, the empty-line rule, the fullness rule, and a
worked example — the exact 512 bytes of sector 0 and of a `remember me`
record as an `xxd` listing, so a reader can check the checker. It is frozen at
item 7: the assembler implements it and the checker parses by it, so an
editable format would be an editable criterion.

*Expected at commit:* no Stage 3 tests yet. Stages 0–2 green.

## Item 3 — `stage3/mkimage.sh`, the `stage3/test.sh` harness, acceptance test 1

**`stage3/mkimage.sh`** (not frozen — the recipe): Stage 2's builder
retargeted: `nasm -f bin stage3/stage3.asm -o stage3/out/BOOTX64.EFI` from the
repo root (the font incbin path is repo-relative), packed with mtools into
`stage3/out/esp.img`. A missing `stage3.asm` is a reported build failure.

**`stage3/test.sh`** (frozen from item 7): Stage 2's harness shape — `set -u`,
repo-root resolution, numbered PASS/FAIL, summary, exit 0 only if all pass —
plus one helper, `fresh_disk <path>`: remove, then `truncate -s 16M`. Every
QEMU invocation in this stage carries the boot image first and the notebook
second: `-drive format=raw,file=<esp.img>` then
`-drive format=raw,file=<notes.img>,if=virtio`.

**Test 1 — Artefact.** Identical criteria to Stage 2's, on Stage 3's files:
MZ/PE magics, machine 0x8664, RELOCS_STRIPPED + EXECUTABLE, PE32+ magic 0x20B,
subsystem 10, and `esp.img` containing a byte-identical `BOOTX64.EFI` at the
removable-media path.

*Expected at commit:* every Stage 3 test fails — there is no `stage3.asm`.
The non-zero exit quoted in the commit message.

## Item 4 — acceptance test 2 (serial, first boot: the eleven lines)

`serial_check <smp>` on a **fresh** disk at `-smp 8` under `timeout -k 5 60`;
exit 124 expected. Stage 2's scan-extraction of `S3: ` runs, then **exactly
eleven** messages matching, in order, the lines of decision 1 with line ten
required to be `S3: notebook formatted` (a fresh disk); plus `W, H > 0`,
`fb != 0`, found = woken = 8, `COLS == W/16`, `ROWS == H/16`, `COLS >= 40`,
`ROWS >= 14` (eleven boot lines, a note, a prompt), and **`S3: disk <N>
sectors` with `N` equal to the image's byte size divided by 512** — the
harness made the disk, so it knows. Whole capture printed on failure.

*Expected at commit:* tests 1–2 fail.

## Item 5 — `stage3/checknotes.py`: the notebook parser and the persistence test (test 3)

The driver of decision 14 and the parser of decision 4: `parse_notebook(path)`
returns the list of note texts or raises with the offset and the field that
was wrong (bad magic, wrong version, sequence out of step, length out of
range, non-printable text, non-zero padding). Mode `--persist <smp>` runs the
two boots and asserts: run one's eleven boot lines with `notebook formatted`
and the echo exactly `remember me\r\n`; the parsed image exactly
`["remember me"]` with every byte of sector 0 and sector 1 as NOTEBOOK.md's
worked example and sector 2 not a record; run two's eleven lines with
`notebook 1 notes`, the channel after `keyboard ready` empty, and the image
byte-identical to run one's. Every QEMU is killed on timeout so none is left
behind. On failure the capture is printed with control bytes visible and the
first 64 bytes of the offending sector as hex.

`test.sh` gains **Test 3**: `--persist 2` and `--persist 8`, both must pass.

*Expected at commit:* tests 1–3 fail.

## Item 6 — checknotes.py `--pixels` (test 4)

The same two-boot run at `-smp 8`, plus a screendump after run two settles.
The checker parses `W`, `H`, `COLS`, `ROWS` from that run's own log, asserts
the PPM is exactly `W`x`H`, renders `remember me` from `stage2/font8x8.bin`
(after Stage 2's non-blank/mutually-distinct self-check on the glyphs it
uses), demands the strip appears **exactly once** at column 0, that the row
below it holds `>`, space, and the solid block cursor, and that every pixel
on screen is within ±4 of one of the two console colours. Per-cell census on
failure, as Stage 2.

`test.sh` gains **Test 4**. All four exist and all fail; the output goes in
the commit message.

*Expected at commit:* tests 1–4 fail.

## Item 7 — freeze the Stage 3 acceptance machinery

`PROTECTED` grows `stage3/test.sh`, `stage3/checknotes.py`,
`stage3/NOTEBOOK.md`. `stage3/mkimage.sh` stays unfrozen. `payloads.py` gains
the Stage 3 freeze cases (Write/Edit/Bash mutations on each new path; the
allowances — running the tests, `cat stage3/NOTEBOOK.md`, `python3
stage3/checknotes.py --persist 8`, every operation on `stage3/mkimage.sh`) and
is re-run whole: every earlier case must still be judged as before. Immediacy
demonstrated again with one live denied call.

*Expected at commit:* tests 1–4 still fail; the payload table 0 wrong.

---

*Everything above is written before any implementation code exists. Everything
below is the code.*

---

# Part 2 — the implementation, in the spec's order

## Item 8 — `stage3/stage3.asm`: Stage 2's proven body, `S2` becomes `S3`

Start from `stage2/stage2.asm` — the whole working organism, nothing removed:
PE32+ headers, serial-first entry, GOP, memory map, trampoline, ExitBootServices
with the retry, GDT and paging, IDT, MADT, INIT-SIPI-SIPI, the console, the
PIC, the keyboard, the main loop with the sti-shadow idiom. Every `S2:` becomes
`S3:`; the header comment is rewritten for Stage 3; the font incbin path stays
`stage2/font8x8.bin`.

*Green at commit:* **test 1.** Test 2 fails (nine lines, not eleven); tests 3
and 4 fail (no disk). Stages 0–2 green — the copy broke nothing behind it.

## Item 9 — the PCI bus and the map

Decisions 10 and 11: `pci_cfg_read32`/`pci_cfg_write32` on `0xCF8`/`0xCFC`
(and 8/16-bit wrappers); `pci_find_virtio_blk` scanning bus 0; the BAR reader
(64-bit BARs assembled from two dwords, the low four bits masked); the
capability walk filling `vio_common`, `vio_notify`, `vio_notify_mult`,
`vio_isr`, `vio_device` with linear addresses; `map_mmio_2m` with its spare
page pool, called for the first and last byte of each capability region; the
command register set. All of it runs after `S3: console` and before the
keyboard, with interrupts off. Failure paths are `ERR:` lines, each named.

Verified with a **temporary, uncommitted probe** that prints the BDF, the BAR
address, the four capability addresses and the multiplier over serial: the BAR
must read `0xC000000000` and the region must be readable through the new
mapping (a read of `num_queues` from the common config returning 1, not a
fault) — then the probe is removed, copy-aside.

*Green at commit:* test 1. Tests 2–4 still red. Stages 0–2 green.

## Item 10 — modern negotiation, and `S3: disk <N> sectors`

Decisions 9 and 12: reset (status ← 0, read back until 0), ACKNOWLEDGE,
DRIVER; device features read as two selected halves, VERSION_1 required;
driver features written as VERSION_1 alone; FEATURES_OK set and read back;
the capacity read as two 32-bit halves from the device config, the high half
required to be zero (a disk of 2 TB or more is an `ERR:` naming the limit);
then the line — **line nine**. DRIVER_OK is set at the end of item 11, once
the queue exists.

*Green at commit:* test 1. Ten of eleven lines; tests 2–4 still red.

## Item 11 — the virtqueue: sector read and sector write

Decision 13 in full: `vq_init` (select queue 0, read and check the size,
write the three ring addresses as 32-bit halves, `queue_enable ← 1`, read
`queue_notify_off`, compute the doorbell address, set DRIVER_OK) and
`disk_rw` (EAX = 0 read / 1 write, RBX = sector, RDI = 512-byte buffer): build
the chain, publish, notify, poll with the bounded `pit_wait`, check the used
id and the status byte. A sector at or beyond the capacity is refused with an
`ERR:` before it reaches the device.

Verified with a **temporary, uncommitted probe** against a scratch image under
`stage3/out/`: read sector 0 of a fresh image and print its first 8 bytes
(zeros); write a recognisable 512-byte pattern to sector 1; read it back and
print the first 8 bytes; quit; `xxd -s 512 -l 64 stage3/out/probe.img` on the
host must show the pattern — the round trip proven from outside the guest
before the notebook depends on it. Then the probe is removed, copy-aside.

*Green at commit:* test 1. Tests 2–4 still red (no notebook line yet).

## Item 12 — the notebook, and the gate closes

Decisions 3–8: `notebook_init` — read sector 0; on the magic and version,
scan the journal counting valid records (sequence, length, text bytes,
padding checked as the checker checks them) and print `S3: notebook <N>
notes`; otherwise write the header and a zeroed sector 1 and print
`S3: notebook formatted` — **line ten**. After `S3: keyboard ready`,
`notebook_replay` re-reads each record and draws its text through
`console_putc` followed by LF, console-only; then the prompt; then `sti`. The
main loop grows the line buffer of decision 6 (a printable appends if under
the cap, an accepted Backspace removes one) and, on Enter, the write-through
of decision 7 before `console_prompt`.

*Green at commit:* **all four automated tests** — tests 2, 3 and 4 close
here, at `-smp 2` and `-smp 8`. Full `./stage3/test.sh` output in the commit
message. Stages 0–2 still green.

## Item 13 — HANDOVER, gotchas, and the owner's command

- `HANDOVER.md` to the morning state: what was built, the BAR address and the
  mapping path taken on this machine, tests 1–4 green with output, test 5
  pending Wajira, caveats carried forward (everything Stage 2 carried; the
  legacy virtio interface untouched; NVMe deferred to a later ring; one
  outstanding request at a time; the notebook's 500-byte and full-disk edges;
  the spare page pool sized for one BAR).
- `CLAUDE.md` gotchas grown with whatever actually bit — candidates already
  visible: *a 64-bit BAR can land above the identity map, and above the first
  PML4 entry — map what the firmware assigned, never assume*; *virtio common
  config fields are accessed at their own width, 64-bit ones as two 32-bit
  halves*; *no DMA without PCI bus mastering*; *disable INTx when polling a
  device behind a PIC that has not unmasked its line*; *a note on the console
  is not a byte on the wire — replay through the console, not the tee*.
- Print the windowed command for Wajira's test 5, and the one-line
  good-morning summary.

*Green at commit:* all four automated tests, plus Stages 0–2.

---

## Verification

- **Automated:** `./stage3/test.sh` from the repo root — builds, packs, runs
  tests 1–4 (serial on a fresh disk at `-smp 8`; persistence at `-smp 2` and
  `-smp 8`, two boots each; pixels at `-smp 8`, two boots). About three
  minutes. Exit 0 only if all pass. Run before every commit from item 8 on.
- **Regression:** `./stage0/test.sh`, `./stage1/test.sh`, `./stage2/test.sh`
  green before every commit, throughout.
- **The hook:** `python3 .claude/hooks/payloads.py` at items 1 and 7 — every
  case from every stage, 0 wrong; immediacy demonstrated live at both.
- **The probes:** items 9 and 11 each carry a temporary serial probe whose
  expected output is stated in the item; item 11's is confirmed from the host
  with `xxd`.
- **Manual (test 5):** Wajira runs, from the repo root:

```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage3/out/esp.img \
  -drive format=raw,file=stage3/out/notes.img,if=virtio -serial stdio
```

`stage3/out/notes.img` will be the image the pixel test left behind, holding
`remember me` — the note the harness typed the night before. He reads it,
types a note of his own, closes QEMU, runs the same command again, and sees
both. His word closes the stage.

## Safety

Restated because this is the stage it was written for. Everything runs inside
QEMU. Firmware plus exactly two drives: the raw FAT boot image and the raw
16 MB notebook image, both under `stage3/out/`, both created by the harness.
OVMF is mapped read-only by `-bios`. No block device, no loop mount, no
`mkfs`, no `sudo`, and from item 1 onward the hook denies each of those
mechanically before the shell sees them. Nothing is written outside
`/home/indy/Projects/ai-os` bar scratch files in the session temp directory.
No network touch at all this stage.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| The modern BAR sits above the identity map | verified in advance (`0xC000000000`); the generic mapper of decision 10, exercised on the first run |
| Negotiation stalls — FEATURES_OK not confirmed, `queue_enable` refused | each step an `ERR:` line naming the step; the scope guard after two honest attempts |
| The request never completes — wrong doorbell, bus mastering off, a 64-bit field written as one qword | decisions 11–13 name each of these; the poll is bounded and reports a timeout instead of hanging the gate; item 11's probe proves the round trip from the host before the notebook exists |
| A write lands after the prompt, or not at all | decision 7's order; test 3 parses the image after run one and diffs it after run two |
| Notes leak onto the wire | decision 2; test 3 demands an empty channel after `keyboard ready` on the second boot |
| A stale record survives a format | the format zeroes sector 1; the scan stops at the first invalid record; the checker asserts sector 2 is not a record |
| The checker and the assembler disagree about the format | one document, `NOTEBOOK.md`, frozen, with a worked example in bytes that both are checked against |
| The bodyguard blocks the harness itself | the payload table's allowances include the exact QEMU commands the harness runs and `dd if=/dev/zero`; the harness scripts are files, not Bash commands, so the hook never sees their insides |
| A 3 a.m. improvisation around storage | the scope guard, in the conventions above, and item 1 making the safety rule mechanical before any storage code exists |
