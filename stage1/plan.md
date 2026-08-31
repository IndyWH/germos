# Stage 1 — implementation plan

**To be committed as `stage1/plan.md`. Produced in plan mode, per the foundation's
build loop. Nothing below is implemented until Wajira approves this document.**

## Context

Stage 0 is closed: Wajira ran test 4 on 31 August 2026 and confirmed the stripes
and both serial lines. Stage 1 takes the practical UEFI road the foundation
flags, and proves **full control of the CPU**: one hand-written PE32+ UEFI
application, loaded by OVMF from a FAT image, that lights serial first, takes the
framebuffer at native resolution, throws the firmware's ladder away, wakes every
core, and has each core paint its own band. The picture *is* the core count.

`stage1/spec.md` is approved and fixes the behavioural order, the seven serial
lines, and five acceptance tests. This plan turns that spec into numbered items.

The plan is **evaluation-first**: items 1–4 build the acceptance machinery so the
tests exist and fail before a single instruction of `stage1.asm` is written. Item
5 locks them behind the hook. Only then, items 6–13 write the assembly, and the
gate closes in two steps — the serial tests at item 12, the pixel test at item
13. Test 5 is Wajira's eyeball and stays manual, forever.

### Environment, verified in this session before planning

Everything the stage needs is already on mlrig; **no new packages are required**
(the spec anticipated needing `ovmf` and `mtools`; both are installed).

| Fact | Verified how |
|---|---|
| `ovmf` present — `/usr/share/ovmf/OVMF.fd`, 4 MB | `ls` |
| `mtools` present — `mformat`, `mmd`, `mcopy`, `mdir`, `mtype` | `which` |
| NASM 3.01, QEMU 10.2.1, Python 3, 32 logical CPUs | `nasm -v`, `qemu … --version`, `nproc` |
| **A partitionless mtools FAT32 image boots under OVMF** | built a 48 MB image, put a known-good `grubx64.efi` at `EFI/BOOT/BOOTX64.EFI`, and OVMF logged `BdsDxe: starting Boot0002 "UEFI QEMU HARDDISK"` and ran it |
| **OVMF chatters heavily on COM1** — ANSI escapes, `BdsDxe:` lines | same run; this is exactly why the spec matches `S1:` lines, not the whole stream |
| **Framebuffer is at `0x80000000`, 16 MB** (stdvga BAR0), below 4 GB | `info pci` on the monitor |
| **A GOP-mode screendump is 1:1** — `P6 1280 800`, 3072016 bytes, no scaling | `screendump` on the monitor |
| **`od --endian=little` reads PE fields**; all header offsets confirmed | parsed a real UEFI PE32+: `e_lfanew` 128, machine `0x8664`, opt magic `0x20b`, subsystem 10 |
| **mtools round-trips byte-identically** (`mtype` output `cmp`-equal) | `cmp` against the source file |
| QEMU exits **124** on `timeout`, as in Stage 0 | headless probe run |

Stage 0's line-doubling gotcha does **not** apply here: it was a VGA property of
200-line modes. A linear GOP framebuffer screendumps at exact size, so test 4 can
demand exact equality with the resolution the serial log claimed.

---

## Decisions taken in this plan

Judgement calls inside the approved spec. Flagged here so Wajira can overrule any
of them at approval rather than discover them in the diff.

1. **The builder is split from the gate, and only the gate is frozen.**
   `stage1/mkimage.sh` (assemble + pack) is *not* frozen; `stage1/test.sh` and
   `stage1/checkbands.py` (the criteria) *are*. Reason: the spec's test 1 judges
   the **artefact** ("`BOOTX64.EFI` carries the MZ and PE magics…; `esp.img`
   contains…"), not the recipe. If the FAT packing needs adjusting we must be
   able to fix it without touching frozen files. The tests verify the *result*
   independently — `esp.img` is read back with `mdir`/`mtype` and byte-compared,
   and no packing trick can fake booting in QEMU.
2. **Serial line formats** (the spec gives placeholders). Exactly, each CRLF:
   `S1: alive` · `S1: gop <W>x<H> fb 0x<16 lowercase hex>` · `S1: boot services
   exited` · `S1: gdt and paging ours` · `S1: cores found <N>` · `S1: cores woken
   <N>` · `S1: done`. `W`, `H`, `N` decimal, no padding.
3. **Failure diagnostics use an `ERR:` prefix**, never `S1:`. A failure path can
   then say what happened without adding an eighth `S1:` line and muddying the
   test's contract. The tests print the whole capture on failure, so `ERR:` lines
   are seen.
4. **Colour table**, 8 entries, cycling: red, cyan, yellow, blue, green, magenta,
   orange, white. Neighbours differ strongly, *and so does the wrap* (white→red),
   which matters at the `-smp 32` mirror run.
5. **Band boundaries**: band *i* is rows `i*H/N` (inclusive) to `(i+1)*H/N`
   (exclusive), integer division. Covers every row exactly, bands differ by at
   most one row when `N` does not divide `H`. The checker uses the same formula,
   so "equal bands" means one rule, applied twice.
6. **Two PE sections, not one**: `.text` (read+execute) and `.data` (read+write,
   with the BSS as `VirtualSize > SizeOfRawData`). A single RWX section risks
   tripping OVMF's image-protection / W^X policy, which would fault on our first
   write to a variable. Two sections avoids the class entirely.
7. **Identity map: the first 4 GB, in 2 MB pages** (1 PML4 + 1 PDPT + 4 PDs =
   24 KB, all in `.data`). Covers low RAM, our image, the trampoline, and the
   framebuffer at `0x80000000`. 1 GB pages are *not* used — they need a CPUID
   check QEMU's default CPU may fail. The 2 MB pages covering the framebuffer are
   marked **PCD|PWT (uncached)**; the rest is writeback.
8. **Trampoline at `0x8000`**, claimed before ExitBootServices with
   `AllocatePages(AllocateAddress)`; on failure, fall back to the first free
   conventional page below 1 MB in the memory map. The trampoline is written
   position-independently (see item 12), so the fallback costs nothing.
9. **Both xAPIC and x2APIC are supported** for sending INIT-SIPI-SIPI, chosen at
   runtime from `IA32_APIC_BASE`. We cannot assume which mode OVMF leaves the
   BSP in, and guessing wrong is a silent hang.
10. **Core cap 64.** AP stacks are a fixed `.data` array of 64 × 8 KB. More than
    64 enabled processors in the MADT is an `ERR:` and a halt, not a buffer
    overrun. 64 comfortably covers mlrig's 32.
11. **Delays after ExitBootServices use PIT channel 2** (port 0x61 gate, poll
    OUT2). Boot services' `Stall()` is gone by then, and INIT-SIPI-SIPI needs a
    real 10 ms / 200 µs.
12. **The wait for check-ins is bounded** (~1 s), then the *actual* count is
    logged. A core that never arrives makes `S1: cores woken` disagree with
    `S1: cores found` and fails the test in one second, instead of hanging until
    the 60 s timeout with nothing to read.

---

## Conventions for every item

- One commit per numbered item.
- Each item states **which tests are expected green at its commit**. Items 1–5
  commit with every test failing **by design** — there is no `stage1.asm` yet.
  That failure is the evidence the gate is real.
- From item 6 on, the stated tests must be green before the commit is made.
- `HANDOVER.md` is updated as we go, with a final pass at item 14.
- `/clear` between numbered items if context grows long.
- Every black-screen (or now, triple-fault) bug earns a CLAUDE.md gotcha line.

---

# Part 1 — the acceptance machinery, written before the code

## Item 1 — `stage1/mkimage.sh`, `stage1/test.sh` harness, acceptance test 1

**`stage1/mkimage.sh`** (not frozen) — build and pack, the spec's commands:

```
nasm -f bin stage1/stage1.asm -o stage1/out/BOOTX64.EFI
dd if=/dev/zero of=stage1/out/esp.img bs=1M count=48
mformat -i stage1/out/esp.img -F -v ESP ::
mmd    -i stage1/out/esp.img ::/EFI ::/EFI/BOOT
mcopy  -i stage1/out/esp.img stage1/out/BOOTX64.EFI ::/EFI/BOOT/BOOTX64.EFI
```

A missing `stage1.asm` or a NASM error exits non-zero with the error shown — a
**test failure**, not a crash. Everything lands in `stage1/out/`, already
gitignored by the `out/` rule.

**`stage1/test.sh`** (frozen from item 5) — bash, `set -u`, resolves its own repo
root, numbered `PASS`/`FAIL` lines, failure counter, summary, exit 0 only if every
automated test passed. Calls `mkimage.sh` first and reports a build failure as a
test failure.

**Test 1 — Artefact.** Reading the built files back, independently of how they
were made:

- `BOOTX64.EFI` bytes 0–1 are `MZ`; `e_lfanew` = dword at 0x3C; bytes at
  `e_lfanew` are `PE\0\0`.
- Machine (`e_lfanew+4`) = `0x8664`.
- COFF Characteristics (`e_lfanew+22`) has `IMAGE_FILE_RELOCS_STRIPPED` (0x0001)
  and `IMAGE_FILE_EXECUTABLE_IMAGE` (0x0002) — the spec's "relocations stripped".
- Optional header magic (`e_lfanew+24`) = `0x20B` (PE32+).
- Subsystem (`e_lfanew+92`) = `10` (EFI application).
- `esp.img` lists `BOOTX64.EFI` under `::/EFI/BOOT` (`mdir`), and `mtype` of it
  is byte-identical to `stage1/out/BOOTX64.EFI` (`cmp`).

All offsets confirmed in this session against a real UEFI PE32+; fields are read
with `od --endian=little`.

*Expected at commit:* every test fails — there is no `stage1.asm`. Shown by
running `./stage1/test.sh` and pasting its non-zero exit into the commit message.

## Item 2 — acceptance test 2 (serial: the seven lines, in order)

A headless run at `-smp 8`, the spec's command with `-display none`, under
`timeout -k 5 60` (the spec's 60 s), redirected to `stage1/out/serial.8.txt`.
Exit 124 is the **expected** outcome (the guest halts forever); any other
non-zero exit is a QEMU failure, reported with `qemu.err`.

**Extraction.** OVMF's chatter is filtered by pulling every occurrence of
`S1: …` up to the next CR or LF out of the whole capture, in order — a scan, not
a line-start match, so a stray OVMF escape sequence sharing a line with our
output cannot break the test while the *content* stays strict.

**Assertions.** Exactly seven extracted messages, matching in order:

```
S1: alive
S1: gop (\d+)x(\d+) fb 0x([0-9a-f]{16})
S1: boot services exited
S1: gdt and paging ours
S1: cores found (\d+)
S1: cores woken (\d+)
S1: done
```

plus `W > 0`, `H > 0`, `fb != 0`, and **found = woken = 8**, the `-smp` value.
Requiring exactly seven also catches a triple-fault reboot loop, which would
repeat the whole sequence. On failure the entire capture is printed (`cat -v`).

Implemented as a shell function `serial_check <smp>` so item 3 can reuse it.

*Expected at commit:* tests 1 and 2 fail.

## Item 3 — acceptance test 3 (scaling at `-smp 2` and `-smp 8`)

The spec: *"Test 2's logic passes at `-smp 2` and `-smp 8` — the count must
follow the machine, not be baked in."* Test 3 runs `serial_check 2` **and**
`serial_check 8` as independent runs (there is no time pressure; independence is
worth twenty seconds). Passes only if both pass, with `found = woken = smp` in
each. A build that hard-codes 8 fails at `-smp 2`; one that hard-codes the MADT
count without waking anything fails `woken`.

*Expected at commit:* tests 1–3 fail.

## Item 4 — `stage1/checkbands.py` and acceptance test 4 (pixels)

`stage1/checkbands.py` — pure Python 3, no third-party imports (the Stage 0
precedent: a dependency-free checker is one less thing to break).

1. Launch QEMU at `-smp 8` with `-display none -monitor stdio` **and**
   `-serial file:stage1/out/serial.px.txt`, so the same run yields both the
   picture and the claim it must match.
2. Poll the serial file until `S1: done` appears (or time out), then write
   `screendump stage1/out/screen.ppm` to the monitor, wait for the file to
   appear and stop growing, `quit`, and reap — killing on timeout so no QEMU is
   ever left running.
3. Parse `W`, `H` from the run's own `S1: gop` line.
4. Parse the PPM by hand (`P6`, maxval 255) and assert:
   - **dimensions are exactly `W`×`H`** — the resolution the serial log claimed.
     If they are an exact integer multiple instead, say so explicitly and cite
     Stage 0's line-doubling gotcha, so the diagnosis is in the output.
   - **exactly 8 bands**, boundaries by decision 5 with `N = 8`.
   - each band is **solid**: every pixel within ±4 per channel of its expected
     colour from the table in decision 4, in order.
   - adjacent bands differ — a screen that is one flat colour cannot pass.
5. On failure, print a per-band census (row range, colour histogram) so a wrong
   band width, a wrong colour, or a wrong pixel format is diagnosed from the test
   output alone.
6. Exit 0 on pass, 1 on any failure, with a clear message on every path.

`test.sh` gains **Test 4**, which runs it and reports it.

*Expected at commit:* all four tests fail. `./stage1/test.sh` output goes in the
commit message as the evidence that the gate is real before the code exists.

## Item 5 — extend the hook to freeze the Stage 1 tests

Extend `.claude/hooks/protect-tests.py` (it already guards Stage 0) to also deny
modification of **`stage1/test.sh`** and **`stage1/checkbands.py`**, by Write,
Edit, MultiEdit, NotebookEdit and Bash. Reading and running stay allowed.
`stage1/mkimage.sh` is deliberately **not** frozen (decision 1).

The filename alternation grows a stage-aware form so `stage0/test.sh` and
`stage1/test.sh` are both caught, including by bare basename.

**Payload-verification discipline, as Stage 0.** The hook is exercised by feeding
JSON payloads straight into it and checking the exit code — a table of cases that
must be **denied** (Write/Edit to each new path; `sed -i`, `tee`, `>`, `mv`, `cp`,
`rm`, `chmod`, `git checkout`, a Python heredoc that opens one for writing) and
cases that must be **allowed** (`cat`, `./stage1/test.sh`,
`python3 stage1/checkbands.py`, redirecting test *output* elsewhere, and every
operation on `stage1/mkimage.sh`). The Stage 0 cases are re-run to prove no
regression.

**Two honest caveats, recorded rather than glossed:**

- **The extension only bites from the next session.** Claude Code snapshots hooks
  at session start. Stage 0 recorded this; this session *confirmed* it, since the
  Stage 0 hook — added last session — blocked a deliberate no-op today. So the
  Stage 1 extension is honoured **by hand** until the next session: after item 5,
  `stage1/test.sh` and `stage1/checkbands.py` are not touched again, and the
  commit says so.
- **The hook over-matches prose.** Its Bash arm looks for a mutating verb near a
  protected filename anywhere in the command string, so a commit message that
  merely *describes* editing a frozen file is denied too — this session's first
  attempt at the Stage 0 closure commit was refused for that reason. Item 5 adds
  a payload case documenting the behaviour. Narrowing it is *not* attempted: a
  false deny is cheap (reword the prose), a false allow is not.

*Expected at commit:* tests 1–4 still fail; the hook demonstrably denies and
allows the right payloads.

---

*Everything above is written before any implementation code exists. Everything
below is the code.*

---

# Part 2 — the implementation, in the spec's behavioural order

Common ground for every item below: **NASM `-f bin`, one flat image**, code
strictly **RIP-relative** (that is what earns the stripped relocations), and the
Microsoft x64 calling convention for every firmware call — `RCX, RDX, R8, R9`,
**32 bytes of shadow space**, 5th argument at `[rsp+32]`, `RSP` 16-byte aligned
at the `call`. `RSP` is aligned and given a 0x40 reservation once, at entry.

## Item 6 — the PE32+ headers and the entry stub

`stage1/stage1.asm`: a DOS stub (`MZ`, `e_lfanew` at 0x3C), `PE\0\0`, the COFF
header (machine `0x8664`, 2 sections, `SizeOfOptionalHeader` `0xF0`,
characteristics with relocs/symbols/lines/debug stripped + executable + large
address aware), the PE32+ optional header (magic `0x20B`, subsystem 10,
`DllCharacteristics` 0 — no NX_COMPAT, no dynamic base — 16 data directories, all
zero), and two section headers:

- `.text` — `0x60000020` (code, execute, read)
- `.data` — `0xC0000040` (initialised data, read, write), `VirtualSize` covering
  the BSS so the loader zero-fills it and the file stays small.

`SectionAlignment` = `FileAlignment` = `0x1000`, so **file offsets equal RVAs**
and `-f bin` output is laid out by construction. `SizeOfHeaders` `0x1000`,
`.text` at RVA `0x1000`. Entry point is `.text`'s first byte. Sizes and
`SizeOfImage` are computed from NASM labels, never hand-counted.

Body for this item: `cli` / `hlt` / `jmp $`.

*Green at commit:* **test 1**. Tests 2–4 fail (no serial, no picture).

*Load check without serial:* run it under OVMF headless and confirm the capture
shows `BdsDxe: starting Boot0002 …` and then **stops** — no load error, no fall
through to the boot manager or shell. That is as far as "did it load" can be
proven before item 7, and it is stated as such rather than assumed.

## Item 7 — serial init, the print helpers, and `S1: alive`

The spec's step 1 — the first observable act, before anything else.

- Entry saves `RCX` (ImageHandle) and `RDX` (SystemTable) to `.data`, caches
  `SystemTable->BootServices` (offset `0x60`), aligns `RSP` and reserves 0x40,
  `cld`.
- COM1 at 0x3F8, the Stage 0 sequence: `IER=0`, `LCR=0x80` (DLAB), divisor 1
  (115200), `LCR=0x03` (8N1), `FCR=0xC7`, `MCR=0x03`. OVMF has already touched
  COM1; we take it over, which is the point of the step.
- `serial_putc`, `serial_puts` (RSI, NUL-terminated), `serial_putdec` (EAX),
  `serial_puthex64` (RAX, 16 lowercase digits), `serial_err` (prints `ERR: …`
  and halts). All poll LSR bit 5 before each byte.
- Print `S1: alive`.

*Green at commit:* test 1. Test 2 now finds one `S1:` line of seven and fails —
correct, and the commit message records the captured bytes. **This is the commit
that proves the image loads and runs.**

## Item 8 — GOP: highest 32-bit mode, and `S1: gop …`

The spec's step 2, and the owner's resolution decision.

- `BootServices->LocateProtocol` (offset `0x140`) with the GOP GUID
  `9042a9de-23dc-4a38-96fb-7aded080516a`.
- Iterate `ModeNumber` 0 … `MaxMode-1`, `QueryMode` each (freeing the pool copy
  it returns). Accept only `PixelFormat` 0 (`RedGreenBlueReserved8Bit`) or 1
  (`BlueGreenRedReserved8Bit`) — the spec's "32-bit". `PixelBitMask` and
  `PixelBltOnly` are skipped. Score by `W*H`, tie-break larger `W`, then lower
  mode number. No candidate at all is an `ERR:`.
- `SetMode` the winner, then read the authoritative values back from
  `This->Mode` / `Mode->Info`: `FrameBufferBase` (+`0x18`), `FrameBufferSize`
  (+`0x20`), `HorizontalResolution`, `VerticalResolution`, `PixelFormat`,
  **`PixelsPerScanLine`**. Save all to `.data`.
- **Stride is `PixelsPerScanLine * 4`, never `W * 4`** — they are allowed to
  differ, and assuming otherwise skews every row.
- Assert `FrameBufferBase + FrameBufferSize <= 4 GB`, since item 10 maps exactly
  that much; a framebuffer above it is an `ERR:` rather than a black screen.
- Print `S1: gop <W>x<H> fb 0x<16 hex>`.

*Green at commit:* test 1. (On mlrig's OVMF this is expected to be 1920x1080 at
`0x80000000`, but nothing anywhere hard-codes it — the test reads it from the log.)

## Item 9 — memory map, ExitBootServices with the stale-key retry, our own stack

The spec's step 3.

- `GetMemoryMap` (offset `0x38`) into a **static 16 KB `.data` buffer**, not a
  pool allocation — allocating changes the very map whose key we are about to
  use, and a static buffer sidesteps the whole dance. A buffer-too-small return
  is an `ERR:` naming the size needed.
- Claim the trampoline page here, while boot services still exist:
  `AllocatePages(AllocateAddress, EfiLoaderData, 1, 0x8000)`; on failure, scan
  the map for a free conventional page below 1 MB (decision 8). Then re-fetch the
  map, because the allocation invalidated it.
- `ExitBootServices(ImageHandle, MapKey)` (offset `0xE8`). **On
  `EFI_INVALID_PARAMETER` the key is stale: re-`GetMemoryMap` and retry**, up to
  5 times, then `ERR:`. This is the spec's named retry and the classic UEFI trap.
- `cli` immediately — the firmware's timer interrupt would otherwise keep firing
  into code that no longer exists. No IDT is installed; from here any CPU
  exception is a triple fault and a reboot.
- Switch `RSP` to our own 16 KB stack in `.data`.
- Print `S1: boot services exited`.

*Green at commit:* test 1. Three of seven lines.

## Item 10 — our own GDT and identity-mapped page tables

The spec's step 4 — the machine stands on structures we built.

- GDT in `.data`, four descriptors: null, **0x08** 64-bit code
  (`0x00AF9A000000FFFF`), **0x10** flat data (`0x00CF92000000FFFF`), **0x18**
  32-bit code (`0x00CF9A000000FFFF`). The 32-bit descriptor exists only for the
  AP trampoline's middle step (item 12).
- `lgdt`, then reload `CS` via a far return (`push 0x08` / `lea rax,[rel .next]`
  / `push rax` / `o64 retf`), then `DS/ES/SS/FS/GS = 0x10`.
- Page tables in `.data`, 4 KB-aligned: 1 PML4 → 1 PDPT → 4 PDs, 2 MB pages,
  identity-mapping 0–4 GB (decision 7). Present+writable everywhere; the 2 MB
  pages overlapping `[FrameBufferBase, +FrameBufferSize)` additionally get
  **PCD|PWT**, so framebuffer writes are not parked in a writeback cache.
- `mov cr3, rax`. Safe because the new tables identity-map the code that is
  executing, its stack, and its data — all below 4 GB.
- Print `S1: gdt and paging ours`.

*Green at commit:* test 1. Four of seven lines.

## Item 11 — the MADT, and `S1: cores found <N>`

The spec's step 5.

- Walk `SystemTable->ConfigurationTable` (offset `0x70`, count at `0x68`,
  24-byte entries) for the ACPI 2.0 GUID `8868e871-e4f1-11d3-bc22-0080c73c8881`
  → RSDP. Valid after ExitBootServices: the system table is
  `EfiRuntimeServicesData` and ACPI tables are `EfiACPIReclaimMemory`, both
  preserved, and both inside our identity map.
- RSDP → `XsdtAddress` (offset 24). Walk the XSDT's 8-byte pointers (header is
  36 bytes) for signature `APIC` → the MADT.
- Walk MADT entries from offset 44 (`Type`, `Length`):
  - **type 0** Processor Local APIC — 1-byte APIC ID at +3, flags at +4;
  - **type 9** Processor Local x2APIC — 4-byte ID at +4, flags at +8.
  Count an entry if flags bit 0 (Enabled) **or** bit 1 (Online Capable) is set,
  and record its APIC ID. A zero `Length` is an `ERR:` rather than an infinite
  loop; more than 64 is an `ERR:` (decision 10).
- Read the BSP's own APIC ID so it can be excluded from the wake list.
- Print `S1: cores found <N>`.

*Green at commit:* test 1. Five of seven lines. `found` is already correct at
both `-smp 2` and `-smp 8` here, which is worth confirming in the commit message.

## Item 12 — the trampoline, INIT-SIPI-SIPI, and `S1: cores woken <N>`

The spec's step 6, minus the painting — so that the serial gate and the pixel
gate close on separate commits and a failure at either is unambiguous.

**PIT delay** (decision 11): channel 2, mode 0, gate via port 0x61 bit 0 with the
speaker bit kept clear, poll OUT2 (bit 5). 10 ms = 11932 ticks, 200 µs = 239.

**The trampoline**, assembled in `.text` and copied to the claimed page. APs
start in real mode at `CS = base>>4, IP = 0`, so it must not depend on where it
lands. It does not:

- 16-bit stage: `cli`, `cld`, `DS = CS`, and `EBX = base` computed from `CS`
  itself (`mov ax,cs` / `shl ebx,4`) — so every later reference is `EBX +
  constant`, with no absolute address anywhere in the trampoline's own code.
- `o32 lgdt [our GDT pointer]`, set `CR0.PE`, **indirect** far jump through a
  patched `offset32:selector` pair to the 32-bit stage (selector `0x18`).
- 32-bit stage: `CR4.PAE`, `CR3` = our PML4, `EFER.LME` via `wrmsr`, `CR0.PG`,
  then an indirect far jump through a second patched pair (selector `0x08`) to
  the shared 64-bit AP entry in our `.text`.
- The BSP patches four values into the page's data area before waking anyone: the
  GDT pseudo-descriptor, `CR3`, and the two far pointers. Nothing is patched at
  runtime by the APs, so there is no write race in the trampoline.
- The conventional **real → 32-bit protected → long** route is used deliberately,
  not the one-shot `PE|PG` trick: the shortcut runs briefly with a real-mode `CS`
  cache in long mode, which is not architecturally defined. Correctness over
  cleverness — this code has to survive Stage 7 on metal.
- The 64-bit AP entry's address must fit in 32 bits for the far pointer; asserted
  at runtime, `ERR:` if not.

**The wake.** For each recorded APIC ID that is not the BSP's: software-enable
the local APIC (SVR bit 8), then INIT (ICR `0x4500`), wait 10 ms, SIPI (ICR
`0x4600 | vector`, vector = page >> 12), wait 200 µs, SIPI again — polling ICR
delivery-status (bit 12) between writes. Via **MMIO at the `IA32_APIC_BASE`
address** (registers `0x300`/`0x310`) or **MSR `0x830`** when bit 10 says x2APIC
(decision 9).

**The AP entry**, 64-bit: load `0x10` into the segment registers, take an index
with `lock xadd [next_index], 1` (no stack needed for that), set `RSP` from the
per-core stack array, `lock inc [checkin]`, then `cli` / `hlt` / `jmp $`.

**The BSP**: sets `next_index = 1` and `checkin = 0` before the wake, takes band 0
by fiat, `lock inc [checkin]` for itself, then waits — bounded to ~1 s
(decision 12) — for `checkin == N`, and prints `S1: cores woken <count actually
seen>` followed by `S1: done`.

**Only the BSP touches COM1**, at any point, ever. The APs have no serial code
reachable from their entry at all — the concurrency doctrine's one-owner-per-
device rule, enforced by construction rather than by care.

*Green at commit:* **tests 1, 2 and 3.** The serial gate closes here, at `-smp 2`
and `-smp 8`. Test 4 still fails: nothing is painted yet.

## Item 13 — the bands

The spec's step 6 painting and the screen section.

- `paint_band(index)`, shared by every core: rows `i*H/N` to `(i+1)*H/N`
  (decision 5), `stride` bytes per row, colour `table[i mod 8]` (decision 4),
  encoded per the saved `PixelFormat` — `0x00RRGGBB` for format 1, byte-swapped
  for format 0.
- Each core writes only its own rows, so the bands need no lock; the only shared
  writes in the whole stage remain the two `lock`-prefixed counters.
- Called by each AP after it takes its index, and by the BSP for band 0 before it
  waits for check-ins — so painting overlaps AP startup.

*Green at commit:* **all four automated tests.** `./stage1/test.sh` output goes in
the commit message.

## Item 14 — HANDOVER, gotchas, and the owner's two commands

- `HANDOVER.md` to final Stage 1 state: what was built, the chosen GOP mode and
  framebuffer, tests 1–4 green with their output, test 5 pending Wajira, the
  `-smp 32` mirror run pending.
- `CLAUDE.md` gotchas grown with what actually bit us — candidates already
  visible: *repeated `S1:` lines in a capture mean a triple-fault reboot loop,
  not a duplicated print*; *stride is `PixelsPerScanLine`, not width*; *the
  ExitBootServices map key goes stale if anything allocates*; *OVMF chatters on
  COM1, unlike SeaBIOS, so Stage 0's byte-exact whole-stream comparison could not
  be carried forward*.
- Print the two windowed commands for Wajira: the `-smp 8` run (test 5) and the
  `-smp 32` mirror run.

*Green at commit:* all four automated tests.

---

## Verification

- **Automated:** `./stage1/test.sh` from the repo root — builds, packs, and runs
  acceptance tests 1–4 (serial at `-smp 2` and `-smp 8`, pixels at `-smp 8`).
  Exit 0 only if all four pass. Run before every commit from item 6 onward.
- **Regression:** `./stage0/test.sh` stays green throughout; Stage 0 is now a
  standing regression check, not a closed book.
- **The hook:** payload table fed straight into `protect-tests.py`, Stage 0 cases
  re-run alongside the new Stage 1 ones; then the honest note that the extension
  does not bite mechanically until the next session, and is honoured by hand
  until then.
- **Manual (test 5):** Wajira's eyeball on the windowed `-smp 8` run — his word
  closes the stage — plus the one `-smp 32` mirror run he asked for at approval,
  the twin at full likeness of mlrig's 32 logical CPUs.

## Safety

Nothing is written outside `/home/indy/Projects/ai-os` (bar scratch files in the
session temp directory). QEMU is given **firmware plus exactly one drive**: a
raw FAT image inside `stage1/out/`. `/usr/share/ovmf/OVMF.fd` is mapped read-only
by `-bios`. No block device, no loop mount, no `dd` to anything but a file under
`stage1/out/`, no `sudo`, no partition table on a real disk. The foundation's
Stage 3 rule is already in force, and Stage 7 is the first time real hardware
exists.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| Hand-written PE headers rejected by OVMF | Test 1 checks the fields; item 6's load check catches a rejection at the next item, with the headers as the only suspect |
| Image protection faults on our first write to a variable | Two sections, `.text` RX and `.data` RW (decision 6) |
| Triple fault after ExitBootServices — reboot, no message | Serial lines 1–4 bracket every step, and a reboot loop is *visible* as repeated `S1:` lines, which test 2 rejects |
| Stale memory-map key | The spec's retry, plus a static map buffer so we never allocate mid-dance |
| APs never arrive | Bounded wait, then log the real count — fails in a second with a readable number, not at the 60 s timeout |
| OVMF leaves the BSP in x2APIC mode | Both paths implemented (decision 9) |
| FAT packing needs changing after the freeze | The builder is not frozen; the criteria are (decision 1) |

---

## Amendments after approval

Recorded here rather than folded silently into the items, so the approved
document stays the thing the work is reviewed against.

**A1 — item 12, x2APIC has no delivery-status bit** (Cowork's plan review).
The ICR delivery-status poll (bit 12) applies to the **xAPIC path only**. In
x2APIC mode bit 12 is reserved and the `wrmsr` to `0x830` is itself the
serialising event, so the x2APIC path must send INIT-SIPI-SIPI **without**
polling for delivery status. Polling it there would read a reserved bit and
could spin forever. Item 12's two paths therefore differ by more than the
register they write, and the code says so at the branch.

**A2 — item 9, the buffer-too-small error names the number** (Cowork's plan
review). If the static 16 KB memory-map buffer is too small, `GetMemoryMap`
returns `EFI_BUFFER_TOO_SMALL` and writes the required size back. The `ERR:`
line must **print that size**, so that fixing it is changing one constant rather
than guessing at one. The plan already asked for this; it is restated because it
is the difference between a five-second fix and a bisect.

**A3 — item 0, an unplanned precondition: the freeze had to be made
path-precise before item 1 could start.** The Stage 0 hook matched the bare
basename anywhere in a path, so it denied the *creation* of `stage1/test.sh` by
every legitimate route. Protecting a file we have not written is a wall, not a
freeze. The fix resolves a candidate path before judging it: a path with a
directory part is protected only if it ends with a `PROTECTED` repo-relative
path; a bare basename stays conservatively protected, since it may be a command
run from inside `stage0/`. Verified with 30 payloads — all 16 Stage 0 denials
unchanged, Stage 0's gate still exits 0. Committed separately, before item 1.

**A4 — item 5's caveat is weaker than the plan assumed, in our favour.** Item 0
established that only the hook **registration** in `.claude/settings.json` is
snapshotted at session start; the hook **script** is re-read on every
invocation. Confirmed both ways in one session: the same command was denied by
the old script and allowed by the new one. So the Stage 1 freeze added at item 5
**bites immediately**, and the "honoured by hand until the next session" caveat
that Stage 0 carried does *not* apply to it. Item 5 verifies this rather than
assuming it, and `CLAUDE.md`'s gotcha is corrected at item 14.
