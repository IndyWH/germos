# GOTCHAS.md

Grown as we hit them. Every black-screen bug earns a line here and a regression
test in the twin.

## NASM and x86

- **Real mode segments.** At entry only `CS:IP` is trustworthy. Zero `DS`, `ES`
  and `SS` explicitly, set the stack, and do it with interrupts off.
- **NASM `-f bin` is literal.** No sections, no relocation. `org 0x7C00` must be
  declared or every label is wrong by 0x7C00.
- **`times 510-($-$$) db 0` fails loudly** if the code overruns 510 bytes. That
  error message is a feature, not a build break to work around.
- **`resb` is zero-*filled* by `-f bin`, not reserved.** Everything is one
  progbits blob, so a BSS declared with `resb` lands in the output file. Declare
  it with `absolute` instead and let the PE loader zero-fill `VirtualSize`
  minus `SizeOfRawData`. Caught when a 12 KB artefact quietly became 45 KB.
- **A label is not a scalar.** `(label + n) & mask` is rejected; subtract `$$`
  first.
- **NASM `%define` is positional.** A constant used above its definition is
  "symbol not defined", and the *cascade* that follows — dozens of "label
  changed during code generation" errors — points everywhere but the cause.
  Read the first error only. Constants live at the top of the file.
- **`default rel` cannot make `[label + reg]` RIP-relative.** NASM
  silently emits the label's absolute 32-bit address instead — the RVA,
  not where OVMF loaded the image — so the store lands in low RAM and
  nothing complains. `mov byte [strip_dirty + rbx], 1` set a dirty flag
  nobody ever read and no row was painted (ring 6a item 12). The idiom
  is `lea rax, [label]` then `[rax + rbx]`; a constant offset
  (`[label + 8]`) is fine.
- **`mul` clobbers RDX.** Keep no pointer there across a `mul` (the
  dirty-array pointer in `surf_describe` went to address 0).
- **A lookup that copies its argument must give the argument back.** A
  `rep movsb` into a scratch name buffer left RSI and ECX at the end of
  the copy, so the fall-through path to the broker sent an empty body
  (`nothing to grow`). Push what the caller still needs (ring 6b item 11).
- **`lodsb` sets AL only.** Index with the whole register afterwards and
  the stale high bytes go along; `xor eax, eax` first, or `movzx`.
- **A table of addresses in data is a table of RVAs.** `dq label` stores
  the label's offset in the file, not where OVMF loaded the image
  (relocations are stripped), so a lookup through it reads low memory and
  a string prints as nothing. The `[label + reg]` gotcha above, in its
  other form: choose with a compare chain of `lea`s (ring 7a item 9).
- **NASM `%define` is positional, in its other form:** a block of code
  moved above the section whose constants it uses assembles as "symbol not
  defined" followed by the cascade. The e1000e driver had to sit below the
  wire section's `TX_BASE` and `ETH_*` defines (ring 7b item 10). Read the
  first error only; move the code, not the defines.

## UEFI and OVMF

- **The ExitBootServices map key goes stale** if *anything* allocates after
  `GetMemoryMap` — including your own `AllocatePages`. On
  `EFI_INVALID_PARAMETER`, re-fetch the map and retry. Keep the map in a static
  buffer, so fetching it cannot itself invalidate it.
- **Walk a UEFI memory map by `DescriptorSize`**, never by the structure's size.
- **Relocations stripped means the loader must honour `ImageBase`.** EDK2
  allocates a relocs-stripped image at its preferred address and cannot fall
  back. Prove the chosen base works; do not assume it.
- **OVMF chatters on COM1; SeaBIOS does not.** Stage 0 could compare the whole
  serial stream byte for byte. From Stage 1 the test must extract the guest's
  own lines out of the firmware's noise.
- **Repeated log lines mean a triple fault, not a repeated print.** After
  ExitBootServices there is no IDT, so any exception reboots. That is why the
  test demands *exactly* seven lines rather than at least seven.
- **OVMF writes to the ESP on every boot.** With `-bios OVMF.fd` and no
  separate variable store the firmware keeps its variables in a file,
  `NvVars`, on the first FAT volume: FSInfo, the FAT, the root directory
  and a few data sectors change on every boot, and no two boots leave
  the same bytes. "The boot image is byte-identical before and after" can
  never be a criterion; what the guest must never do to it can (ring 7a
  item 1, amendment A1's test).
- **OVMF wrote no `NvVars` to a stick copy on `usb-storage` in eight
  boots**, though it writes them to an `esp.img` on SATA every boot (ring
  7a). Neither is a promise: assert what the guest must never do to a boot
  medium (its tables unchanged), never byte-identity and never a change.
- **FAT32 under OVMF wants an ESP of about 33 MB or more.** Measured for the
  bench's own image, which is 48 MB (ring 8b item 6).

## The framebuffer and the console

- **Mode 13h clears the framebuffer.** Set the mode *before* writing pixels, or
  the stripes are wiped by the mode switch.
- **A0000h is a segment, not an address.** In real mode write pixels via
  `ES = 0xA000` and a 16-bit offset; the offset wraps at 64 KB.
- **QEMU line-doubles mode 13h**, but *not* a linear GOP framebuffer. A 320x200
  guest screendumps at 640x400; a 2048x2048 GOP mode screendumps 1:1. Never
  hard-code a resolution in a pixel check — read it from the guest's own log.
- **Stride is `PixelsPerScanLine`, never the width.** They are allowed to
  differ, and assuming otherwise skews every row down the screen.
- **Map the framebuffer uncached** (`PWT|PCD`). Left writeback, pixels can sit
  in a cache line and never reach the screen — a black screen with a serial log
  claiming success.
- **The uncached framebuffer is write-only.** Reads from UC memory are brutally
  slow, so scrolling re-renders from a text shadow buffer; nothing ever reads a
  pixel back.
- **A note on the console is not a byte on the wire.** Anything that must
  appear on screen but not on serial goes through `console_putc`, never the
  serial tee — the persistence test asserts an empty channel after `ready`.
- **QEMU's default VGA carries an EDID of its own, naming 1280x800**, and
  OVMF lists the EDID's preferred mode first. Under the mode policy a run
  without `-vga none -device VGA,edid=on,xres=1440,yres=1440` gets an
  80x50 console; the flags are load-bearing on every QEMU command, and
  the EDID BAR's address moves with the device set — read the BAR.
- **A serial line after `keyboard ready` must bypass the tee.** Once the
  console is up, `serial_putc` draws every byte into the conversation;
  a status line meant for serial alone goes through a raw UART write.
- **A mode is not a whole number of cells.** 1080 is 67 rows and 8 spare
  pixel rows; a pointer clamped to the framebuffer names a row the console
  lacks, the arrow is drawn half off the screen, and nothing owns the cell
  to repaint it - ghosts along the bottom edge. Clamp a pointer to the
  console's cells (`16C-1`, `16R-1`), never to the framebuffer (ring 6c
  item 12c, the oracle's finding).
- **No QEMU display can stand in for a foreign display with an EDID at
  BAR2.** `virtio-vga` (`1af4:1050`) has an I/O BAR2 and `cirrus-vga` none;
  `bochs-display` and `secondary-vga` carry QEMU's own `1234:1111`. So a
  guard that reads BAR2 only for QEMU's VGA is invisible to a twin: the
  `novga` boot proves the "edid none, highest mode" rule, and the guard's
  refusal is proven by a probe with the vendor constant changed on QEMU's
  VGA (ring 7c item 1, item 7). Measure what the stand-in device's BARs
  hold before writing a test that assumes them.

## Interrupts and the i8042

- **x2APIC has no delivery-status bit.** Poll ICR bit 12 on the xAPIC path only;
  in x2APIC mode it is reserved and the `wrmsr` is itself the serialising event,
  so polling spins for ever.
- **Remap the PIC before `sti`.** The reset default routes IRQs to vectors
  8-15, which are CPU exceptions; an unremapped timer tick reads as a double
  fault. Remap both chips even if only one line is unmasked.
- **Never `hlt` while the queue holds data.** A byte arriving between the check
  and the `hlt` has spent its interrupt. The idiom: `cli`, check; if empty,
  `sti`;`hlt` back to back - the sti shadow carries a pending interrupt into
  the wake; if not, `sti` and drain.

## Virtio

- **A 64-bit BAR can land above the identity map — and above the first PML4
  entry.** OVMF puts virtio's modern region at `0xC000000000` here. Read the
  BAR at runtime and map what the firmware assigned, uncached, creating
  PML4/PDPT entries as needed; never assume the 4 GB map covers a device.
- **Virtio common-config fields are accessed at their own width**, the 64-bit
  ones (queue addresses, capacity) as two 32-bit halves. The spec requires it
  and QEMU implements only the natural widths; never rely on a qword access.
- **No DMA without PCI bus mastering.** Set COMMAND bit 2 before handing a
  device any ring address, or every request times out with a perfect-looking
  ring.
- **Disable INTx when polling a device behind a PIC that has not unmasked its
  line.** COMMAND bit 10, plus `NO_INTERRUPT` on the available ring.
- **OVMF's own driver has already bound the virtio device** and reset it at
  ExitBootServices. Reset it again and assume nothing about its state.
- **With `VIRTIO_F_VERSION_1` the virtio-net header is 12 bytes**, and a
  non-mergeable receive buffer must hold the whole frame (header plus up to
  1514) in one descriptor — QEMU requires it when `MRG_RXBUF` is not
  negotiated. The config MAC is valid only if `VIRTIO_NET_F_MAC` was
  negotiated; read it from device config, never assume the default.
- **QEMU sizes a virtio device's queues to the vCPU count.** virtio-blk here
  reports two queues at `-smp 2`, not one; drive only the queue you enabled
  and do not read a count into an assumption.

## The network and the broker

- **A `guestfwd` cannot sit on slirp's own addresses.** libslirp rejects a
  forward on the virtual host `10.0.2.2` or the DNS `10.0.2.3`
  (`Conflicting/invalid host:port`). Use another on-link address — `10.0.2.4`
  is slirp's own default for a guest forward, and it answers ARP for it.
- **A `-tcp:host:port` guestfwd target is one chardev opened at QEMU start**,
  shared by every guest connection, and QEMU refuses to boot when nothing
  listens. For a connection-per-request that also survives the listener being
  down (a prompt RST), use `guestfwd=...-cmd:nc -N 127.0.0.1 <port>` instead.
- **slirp drops a bad checksum in silence.** A segment with a wrong IPv4 or
  TCP checksum gets no reply at all — so when a well-formed-looking request
  gets nothing back, suspect the checksum before anything else. The twin
  enforces this both ways, which is exactly why the guest must compute them.
- **Advance `snd_nxt` when you send TCP data, not when it is acked.** Leave it
  and the send window `snd_nxt - snd_una` is zero, so the peer's legitimate
  ACK of the data falls outside the acceptable range and is discarded; the
  sender retransmits until it gives up while the receiver has the data. Send
  and retransmit from `snd_una`; move `snd_nxt` past the data at send time.
- **`claude -p --bare` skips the CLI's own login**, not just hooks and
  CLAUDE.md discovery — so the real call fails to authenticate while the mock
  gate, which never runs the backend, stays green. Leave `--bare` off the
  broker's backend. The mock proves the wire; the real `claude -p` has its
  own failure surface that only the oracle (test 5) exercises.

## QEMU and the twin

- **QEMU locks a raw image its guest boots from.** A second QEMU on the
  same file fails at start (`Failed to get "write" lock`), and
  `read-only=on` does not help on a SATA node. The twin must boot a
  byte-identical *copy* of the image (or `file.locking=off`, which
  disables the safety instead). Found at Stage 5 item 11, in a frozen
  file — probe two QEMUs on one image before freezing anything that
  boots one.
- **Several QEMUs on one image hit the lock, again** — every probe boots
  its own copy under its own `out/`, as the twin does.
- **The twin always has two SATA disks.** The frozen twin boots its ESP
  from q35's own controller, so a driver that takes "the first port with a
  disk" takes the boot image, and a rule that formats "anything not ours"
  formats it. Identify every port, choose by what the disk holds, and
  never write a disk that is not blank (ring 7a, amendment A1).
- **A fresh clone has no `out/` directories.** Every `<stage>/out/` is
  gitignored, and the frozen checkers assume they exist (test 3 of the 7c
  gate assembles `stage6/app.asm` into `stage6/out/app.check.bin` and fails
  "the app fixture is not what the repository says" when the directory is
  missing). Before the first gate on a new machine:
  `mkdir -p stage{0..8}/out trials/out stage7/out/metal` (Omarchy on mlrig,
  22 September 2026; the second correction on Ubuntu 26.10, 8 November
  2026, when the 8t gate's first run failed on `stage7/out/metal` alone).
- **QEMU 11 prints `xp` addresses as eight hex digits, QEMU 10 as sixteen.**
  The monitor parser `XP_LINE` in `broker/twin.py` demanded exactly sixteen,
  so under QEMU 11.1.1 every obs-page and surface read returned "xp read 0
  of N bytes", the rehearsal judged "the app did not run", and test 3 of the
  7c gate fell over from that one line while the guest booted perfectly. The
  project's seventh freeze opening, by the owner's hand: `{16}` became
  `{8,16}` (22 September 2026). A parser of the host's tools is a criterion's
  eye, not the criterion, and the tools move under it: pin nothing about a
  tool's output format that the tool does not document.
- **A QEMU socket chardev must be drained.** Orders to a guest over
  `-chardev socket,...,logfile=` need a thread reading the socket for the
  whole boot, or the guest's serial output backs up behind it (ring 8b, test
  3). The logfile is still the chart.

## Grown code

- **EFER.NXE is on under OVMF, but our own page tables carry no NX bits**,
  so anything mapped is executable — a component region in BSS needs no
  mapping change. Measured at Stage 5's planning: a blob copied there and
  called returned.
- **The current boot is counted in the take.** PARTS.md's rule: the first
  shadow boot's refusal says `boots 1/3`, not `0/3`. The expectation was typed
  from arithmetic and corrected from the document before the freeze (ring 8b
  item 12), the counter's-rule class again.
- **A loser on the bench never reaches the rehearsal.** The pipeline runs cheap
  steps first, so a part meant to fail a later step must first beat the
  measures: the frozen `hang` loses 19 to 17 and never rehearses. Test 2
  carries `fast` with a `jmp $` at `init` (ring 8b item 9).

## Checkers and counters

- **`pkill -f <pattern>` matches the shell running it** when the pattern
  appears in the command line; the shell dies with exit 144. Use a
  self-excluding pattern (`germline.p[y]`).
- **A latency counter is stamped at the echo, never after a wait that
  has its own counter.** Input-to-photon marked after `grow_request`
  returned measured the whole broker wait, and one real grow pinned
  `ph` worst at 99.9 for the session — the strip telling an untruth
  about the human path while `w` already held the wire's wait. Mark at
  the moment the key's echo lands in the surface (ring 6a item 14b).
- **A counter lives in the process that holds it.** The mock's
  `generation_calls` restarts when the checker restarts the mock between
  boots; a frozen test that expected the count to carry across boots
  cost a freeze opening (ring 6b item 10b). Count per process, and
  write the expectation from a run, never from arithmetic.
- **Surfaces, then the screendump, then the page.** A strip check that
  wants the screen's counters *between* two page reads needs the
  screendump between them; a screendump taken before the first read can
  never satisfy it. One frozen mode had the order wrong and cost a freeze
  opening (ring 6c item 11b). Copy the order from a mode that passes.
- **A sweep that stays in the middle proves nothing about the edges.** The
  edges are where a human goes first and where Fitts's targets are; the
  gate's sweep lived inside the app panel and never met the spare pixels.
  Drive a pointer test into every corner and along every edge.
- **A counter's rule lives in its frozen document; look it up before the
  number is typed.** `grows_served` counts app frames whose `source` byte
  is 1 (GLASS.md), so two frames generated from a fresh germline make it
  0, not 2; the checker's 2 was arithmetic and cost the project's sixth
  freeze opening (ring 7b item 10b) - the ring 6b item 10b class again.
  A number no run can give before the freeze is written as the document's
  rule, never as a guess.
- **A prose rule against a path must see through the shell's quoting.**
  `"/dev"/sda`, a backslash inside the word, an ANSI-C quoted string and a
  bare `/dev` all slipped past a regex that wanted the literal `/dev/`
  (ring 7c item 1). Normalise the command - delete quotes and backslashes,
  collapse slashes and dot segments - before the rule looks, and keep the
  spellings as data in the payload table, never on a command line: the
  hook denies the probe that spells them.
- **A click on a launch item types the launch line.** Ring 6c made a
  click do what its key does, and a `! echo` target types `! echo` and
  Enter - so the serial echo after the click is that line, not nothing
  (ring 7c item 4, one correction). Read the ring's own rule before
  writing the expectation.
- **A guest's serial line can start mid-line.** The echo of a half-typed word
  has no line end, so an answer lands after it: `the calculator liorder: count
  244 0 0`. Read a chart by searching for the marker, as `parts.py` does, never
  by the line's start. The twin proof of `hp-day.py` found it; on the HP the
  owner's first word would have stopped the day (ring 8b item 18).

## The metal

- **On the PCH's integrated LAN an MMIO read straight after `CTRL.RST`
  hangs the processor** - no fault, no timeout, no line: the HP's first
  watched boot ended after `S7: home 0 apps` with the 82579LM healthy
  under Linux (ring 7c item 16). Sleep 20 ms after the reset write before
  the first register access (`ich8lan.c` says a flush there hangs the
  hardware); `e1k_attach` waits 25 ms on the PIT. The discrete 82574L in
  the twin never shows it, so no gate can.
- **Never write a MAC control register absolutely on the PCH's integrated
  LAN.** TCTL's reset default on the 82579LM carries `MULR` (bit 28). An
  absolute write of `EN`, `PSP`, `CT` and `COLD` clears it, and with `MULR`
  clear the MAC fetches descriptors and takes 16 bytes into the transmit
  FIFO but never commits a packet with `EOP` to the transmitter: no error,
  no counter, TDH stays 0, and every register reads as written. QEMU's
  82574L transmits with `MULR` clear, so no gate could show it; it cost six
  flashes and one monitor session (item 21, 18 September 2026). Read, mask
  the fields you own, OR in your bits, write, as Linux does.
- **The desktop's automounter writes a stale superblock over a freshly
  flashed stick.** A stick whose old partition is mounted when the image
  goes over it gets the mount's writeback on top of the new bytes, and it
  boots the old world or none. Unmount before the write, `wipefs` the
  partition and then the stick first, compare the stick against the image
  afterwards, power the stick off before the plug comes out, and never
  trust a stick that was flashed while mounted (ring 7c, the owner's
  flashes of 17 and 18 September 2026; `stage7/METAL.md` step 3 is the
  block). The flash is the owner's hand; the hook denies CC every word of
  it.
