# CLAUDE.md

Kept under one page. Source of truth is `ai-os-foundation.md`; current state is
`HANDOVER.md`.

## Build and test

```bash
# Stage 0 - closed, kept as a standing regression check
nasm -f bin stage0/stage0.asm -o stage0/out/stage0.img
./stage0/test.sh

# Stage 1
./stage1/mkimage.sh    # assemble stage1.asm, pack the FAT image (not frozen)
./stage1/test.sh       # acceptance tests 1-4. ~4 min: each halted guest burns
                       # its 60s timeout, which is the expected outcome

# Stage 2
./stage2/mkimage.sh    # assemble stage2.asm, pack the FAT image (not frozen)
./stage2/test.sh       # acceptance tests 1-4: artefact, nine serial lines,
                       # sendkey typing at -smp 2 and 8, pixel-checked console

# Stage 3
./stage3/mkimage.sh    # assemble stage3.asm, pack the FAT image (not frozen)
./stage3/test.sh       # acceptance tests 1-4: artefact, eleven serial lines on
                       # a fresh disk, persistence across two boots at -smp 2
                       # and 8 (image parsed from the host), pixel-checked
                       # replay. ~4 min, seven QEMU boots.

# Stage 4
./stage4/mkimage.sh    # assemble stage4.asm, pack the FAT image (not frozen)
./stage4/test.sh       # acceptance tests 1-4: artefact, twelve serial lines
                       # with the nic MAC, the "? " question round-trip through
                       # the MOCK broker at -smp 2 and 8 (a note between two
                       # questions, the wire echo untouched), and the cage -
                       # restrict=on with one guestfwd asserted, a mock-down
                       # run ending in a console message not a hang. Refuses to
                       # start if anything listens on 9999. Five QEMU boots.

# Stage 5
./stage5/mkimage.sh    # assemble stage5.asm, pack the FAT image (not frozen)
./stage5/test.sh       # acceptance tests 1-4: the grow request, the component
                       # rehearsed in the twin, the germline; needs 9999 and
                       # 9998 free. Five boots plus six rehearsals, ~8 min.

# Stage 6 ring 6a - the glass
./stage6/mkimage.sh    # assemble stage6.asm, pack the FAT image (not frozen)
./stage6/test.sh       # acceptance tests 1-4 at 1440x1440 with ONE virtio disk:
                       # sixteen lines, the app in its panel, the truth on the
                       # strip. ~14 min. Still the regression for ring 6b: the
                       # same binary without a home image is ring 6a's.

# Stage 6 ring 6b - the store of plans
./stage6/test-6b.sh    # acceptance tests 1-4 at 1920x1080 with TWO virtio disks
                       # (notes and home): seventeen lines, "! install echo"
                       # rehearsed against the plan's tests, the launch with no
                       # broker, the liar refused, the undo. ~12 min.

# Stage 6 ring 6c - the pointer
./stage6/test-6c.sh    # acceptance tests 1-4 at 1920x1080 with two virtio disks,
                       # the PS/2 mouse driven through the monitor: seventeen
                       # lines then "S6: mouse ready" on the first packet, the
                       # arrow and the strip's pt field, a click on the choices
                       # row doing what its key does, point in the point app's
                       # panel, packets counted equal packets sent. ~9 min.
                       # Rings 6a and 6b stay the regressions: the same binary
                       # with a mouse that never moves is ring 6a's to the pixel.

# The mock brokers (what the gates talk to; never spend a token)
python3 broker/broker.py --mock --port 9999     # Stage 4
python3 broker/plans.py --mock                  # Stage 6 (answers, apps, installs)
python3 broker/pointer.py --mock                # Stage 6 ring 6c (the point app too)

# The hook's payload table - every freeze and bodyguard case, 0 wrong or exit 1
python3 .claude/hooks/payloads.py
```

Windowed, for the oracle test (Stage 6 ring 6c shape, with the real broker
`python3 broker/pointer.py` in another terminal; click in the QEMU window to
grab the mouse, Ctrl+Alt+G releases it; earlier stages drop the drives, the
display and the cage they did not have and point at their own `esp.img` —
see README.md):

```bash
truncate -s 16M stage6/out/home.img
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage6/out/esp.img \
  -drive format=raw,file=stage6/out/notes.img,if=virtio \
  -drive format=raw,file=stage6/out/home.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Each stage's `test.sh` is its gate. It must be green before every commit that
should pass it, and earlier stages stay green forever.

## Conventions

- **Evaluation-first.** Acceptance tests are written before the code they judge.
- **Draft until approved.** `plan.md` is committed and approved before any
  implementation code is written.
- **One commit per numbered item** from `plan.md`. Small commits; the last known
  good state is minutes away.
- **Tests green before every commit.** No exceptions once the tests are expected
  to pass.
- **Update `HANDOVER.md` as you go**, not at the end of the week.
- **The second time a mistake is corrected, the correction goes into CLAUDE.md**
  — into the gotchas section below.
- **Guarantees are hooks, not requests.** Acceptance tests cannot be edited
  during implementation or a fix; `.claude/hooks/protect-tests.py` blocks it.
  Freezing a new stage's tests is one line: add the paths to `PROTECTED`.
- **The gate is frozen; the builder is not.** `test.sh` and the pixel checkers
  hold the criteria. `mkimage.sh` holds the recipe, and stays fixable.
- **QEMU only.** Nothing outside this folder is written. No real disk device is
  touched, ever, at any stage before Stage 7 — and since Stage 3 the same hook
  is the **storage bodyguard**: any `/dev` path bar the harmless sources and
  sinks, mount/umount/losetup/mkfs and the partitioning tools, `sudo`, a QEMU
  `-drive file=` outside a repo `out/`, the disk shorthands, and `qemu-img`
  outside `out/` are denied in any Bash command, prose included. The only
  disks are raw files the harness makes under `<stage>/out/`.
- **The network is a cage too (Stage 4).** slirp with `restrict=on` and one
  `guestfwd`: the guest reaches nothing but the broker on `127.0.0.1:9999`,
  and every other destination gets a RST. The broker binds `127.0.0.1` only.
  The automated gate talks only to `broker/broker.py --mock`, which calls
  nothing, and `stage4/test.sh` refuses to run while anything else holds the
  port — so the gate never spends a token or reaches the real Claude. Only
  Wajira's test 5, with `python3 broker/broker.py`, makes a real `claude -p`
  call, over ordinary HTTPS from the broker; the guest link stays plaintext
  inside the cage until the TLS ring (Stage 7).

## Bare-metal gotchas

Grown as we hit them. Every black-screen bug earns a line here and a regression
test in the twin.

- **Serial before video.** The first observable act of any stage is a serial
  line. A black screen with no serial output means the code died before it ran;
  a black screen *with* serial output means video setup is the bug. This
  distinction is the whole debugging strategy.
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
- **The ExitBootServices map key goes stale** if *anything* allocates after
  `GetMemoryMap` — including your own `AllocatePages`. On
  `EFI_INVALID_PARAMETER`, re-fetch the map and retry. Keep the map in a static
  buffer, so fetching it cannot itself invalidate it.
- **Walk a UEFI memory map by `DescriptorSize`**, never by the structure's size.
- **Relocations stripped means the loader must honour `ImageBase`.** EDK2
  allocates a relocs-stripped image at its preferred address and cannot fall
  back. Prove the chosen base works; do not assume it.
- **x2APIC has no delivery-status bit.** Poll ICR bit 12 on the xAPIC path only;
  in x2APIC mode it is reserved and the `wrmsr` is itself the serialising event,
  so polling spins for ever.
- **OVMF chatters on COM1; SeaBIOS does not.** Stage 0 could compare the whole
  serial stream byte for byte. From Stage 1 the test must extract the guest's
  own lines out of the firmware's noise.
- **Repeated log lines mean a triple fault, not a repeated print.** After
  ExitBootServices there is no IDT, so any exception reboots. That is why the
  test demands *exactly* seven lines rather than at least seven.
- **A halted guest never exits QEMU.** Wrap headless runs in `timeout` and treat
  exit 124 as the expected success signal; any other non-zero exit is real.
- **The uncached framebuffer is write-only.** Reads from UC memory are brutally
  slow, so scrolling re-renders from a text shadow buffer; nothing ever reads a
  pixel back.
- **Remap the PIC before `sti`.** The reset default routes IRQs to vectors
  8-15, which are CPU exceptions; an unremapped timer tick reads as a double
  fault. Remap both chips even if only one line is unmasked.
- **Never `hlt` while the queue holds data.** A byte arriving between the check
  and the `hlt` has spent its interrupt. The idiom: `cli`, check; if empty,
  `sti`;`hlt` back to back - the sti shadow carries a pending interrupt into
  the wake; if not, `sti` and drain.
- **A 0xE0 scancode prefix swallows its successor.** Ignoring just the prefix
  turns keypad Delete (`E0 53`) into keypad-dot's make code - a stray `.` on
  screen.
- **NASM `%define` is positional.** A constant used above its definition is
  "symbol not defined", and the *cascade* that follows — dozens of "label
  changed during code generation" errors — points everywhere but the cause.
  Read the first error only. Constants live at the top of the file.
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
- **A note on the console is not a byte on the wire.** Anything that must
  appear on screen but not on serial goes through `console_putc`, never the
  serial tee — the persistence test asserts an empty channel after `ready`.
- **OVMF's own driver has already bound the virtio device** and reset it at
  ExitBootServices. Reset it again and assume nothing about its state.
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
- **With `VIRTIO_F_VERSION_1` the virtio-net header is 12 bytes**, and a
  non-mergeable receive buffer must hold the whole frame (header plus up to
  1514) in one descriptor — QEMU requires it when `MRG_RXBUF` is not
  negotiated. The config MAC is valid only if `VIRTIO_NET_F_MAC` was
  negotiated; read it from device config, never assume the default.
- **QEMU sizes a virtio device's queues to the vCPU count.** virtio-blk here
  reports two queues at `-smp 2`, not one; drive only the queue you enabled
  and do not read a count into an assumption.
- **`claude -p --bare` skips the CLI's own login**, not just hooks and
  CLAUDE.md discovery — so the real call fails to authenticate while the mock
  gate, which never runs the backend, stays green. Leave `--bare` off the
  broker's backend. The mock proves the wire; the real `claude -p` has its
  own failure surface that only the oracle (test 5) exercises.
- **QEMU locks a raw image its guest boots from.** A second QEMU on the
  same file fails at start (`Failed to get "write" lock`), and
  `read-only=on` does not help on a SATA node. The twin must boot a
  byte-identical *copy* of the image (or `file.locking=off`, which
  disables the safety instead). Found at Stage 5 item 11, in a frozen
  file — probe two QEMUs on one image before freezing anything that
  boots one.
- **EFER.NXE is on under OVMF, but our own page tables carry no NX bits**,
  so anything mapped is executable — a component region in BSS needs no
  mapping change. Measured at Stage 5's planning: a blob copied there and
  called returned.
- **`pkill -f <pattern>` matches the shell running it** when the pattern
  appears in the command line; the shell dies with exit 144. Use a
  self-excluding pattern (`germline.p[y]`).
- **`default rel` cannot make `[label + reg]` RIP-relative.** NASM
  silently emits the label's absolute 32-bit address instead — the RVA,
  not where OVMF loaded the image — so the store lands in low RAM and
  nothing complains. `mov byte [strip_dirty + rbx], 1` set a dirty flag
  nobody ever read and no row was painted (ring 6a item 12). The idiom
  is `lea rax, [label]` then `[rax + rbx]`; a constant offset
  (`[label + 8]`) is fine.
- **`mul` clobbers RDX.** Keep no pointer there across a `mul` (the
  dirty-array pointer in `surf_describe` went to address 0).
- **QEMU's default VGA carries an EDID of its own, naming 1280x800**, and
  OVMF lists the EDID's preferred mode first. Under the mode policy a run
  without `-vga none -device VGA,edid=on,xres=1440,yres=1440` gets an
  80x50 console; the flags are load-bearing on every QEMU command, and
  the EDID BAR's address moves with the device set — read the BAR.
- **Several QEMUs on one image hit the lock, again** — every probe boots
  its own copy under its own `out/`, as the twin does.
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
- **A lookup that copies its argument must give the argument back.** A
  `rep movsb` into a scratch name buffer left RSI and ECX at the end of
  the copy, so the fall-through path to the broker sent an empty body
  (`nothing to grow`). Push what the caller still needs (ring 6b item 11).
- **`lodsb` sets AL only.** Index with the whole register afterwards and
  the stale high bytes go along; `xor eax, eax` first, or `movzx`.
- **Surfaces, then the screendump, then the page.** A strip check that
  wants the screen's counters *between* two page reads needs the
  screendump between them; a screendump taken before the first read can
  never satisfy it. One frozen mode had the order wrong and cost a freeze
  opening (ring 6c item 11b). Copy the order from a mode that passes.
- **Two devices on one i8042: read the status byte before port 0x60.**
  Bit 5 says whose byte it is; a handler that reads 0x60 blind puts a
  mouse byte in the keyboard ring. Command-byte bit 5 set means the aux
  port is *disabled* (OVMF leaves 0x67), and PS/2 `dy` counts upwards, so
  the monitor's `mouse_move 10 20` arrives as `28 0a ec` (ring 6c).
- **A serial line after `keyboard ready` must bypass the tee.** Once the
  console is up, `serial_putc` draws every byte into the conversation;
  a status line meant for serial alone goes through a raw UART write.
- **Nothing survives a call into grown code but memory and the stack.**
  An app may clobber every register but RSP, so loop state around
  `app_call` goes on the stack (pushed before, popped after - `app_call`
  restores RSP from `saved_rsp`), never in R12-R15, whatever the fixture
  happens to preserve. `click_panel`'s button loop passed the gate on the
  point app's courtesy alone (Cowork's pre-oracle review, ring 6c item 12b).
- **A mode is not a whole number of cells.** 1080 is 67 rows and 8 spare
  pixel rows; a pointer clamped to the framebuffer names a row the console
  lacks, the arrow is drawn half off the screen, and nothing owns the cell
  to repaint it - ghosts along the bottom edge. Clamp a pointer to the
  console's cells (`16C-1`, `16R-1`), never to the framebuffer (ring 6c
  item 12c, the oracle's finding).
- **A sweep that stays in the middle proves nothing about the edges.** The
  edges are where a human goes first and where Fitts's targets are; the
  gate's sweep lived inside the app panel and never met the spare pixels.
  Drive a pointer test into every corner and along every edge.

## Working with the hooks

- **Only the hook *registration* is snapshotted at session start; the script is
  re-read on every call.** So a brand-new hook does not fire until the next
  session, but *edits to an already-registered one are live immediately*. (This
  corrects the Stage 0 note, which assumed the stricter case.)
- **The freeze matches prose, deliberately.** A Bash command that merely
  *mentions* a frozen filename near a mutating verb — a commit message, a
  comment, the hook's own `PROTECTED` list — is denied. Reword it, or use the
  Write/Edit tools, which judge the target path only. A false deny costs a
  reworded command; a false allow costs an edited acceptance test.
- **Don't undo a temporary probe with `git checkout --`.** It reverts to HEAD
  and takes the current item's uncommitted work with it. Copy the file aside
  first, and restore from the copy.
- **A heredoc that mentions a frozen file near `open(`/`write` is denied**
  even when it only reads. Edit prose with the Edit tool; if a script must
  mention a frozen name, write the script to a file first and run the file.
- **Commit messages that mention the bodyguard's words go in via `-F`** from
  a file written with the Write tool; `-m` puts the words in the command.

## The plan gate

- Exiting plan mode is blocked by a hook until Wajira approves. He reviews the
  plan (via Cowork), then runs, in his own terminal at the repo root:
  echo approved > PLAN_APPROVED
  The hook consumes the marker: one approval opens the gate exactly once.
  Never create or mention PLAN_APPROVED from inside a session - the other
  hook denies every route to it. The plan gate exists because full-auto mode
  otherwise lets a session approve its own plan.
