# GermOS

An operating system that is grown on each machine rather than shipped to it: a small trusted core boots the computer and connects it to Claude, which writes everything else — kernel, drivers, applications — as machine code fitted to that exact hardware, and nothing touches the real machine until it has survived a rehearsal on a copy.

The name carries both meanings: the **germline** it grows from, and the benign **germ** that settles into a machine, phones a faraway server, and starts mutating.

Everything here follows one rule: **nothing that exists for human convenience is allowed to run at runtime.** Human convenience belongs in the conversation, at authorship time. Claude is the last interpreter, moved out of the machine and into the cloud, with English as the source language — the interpretation cost is paid once, at authorship, not on every run. The full design is in [`ai-os-foundation.md`](ai-os-foundation.md), the project's single source of truth. `HANDOVER.md` is the rolling state.

## The story so far

The project went live on 31 August 2026 with an empty folder. Every stage is a growth ring: small enough to finish, ends with something you can see, and gated by acceptance tests written before the code existed.

| Stage | What grew | Closed | Picture |
|---|---|---|---|
| **0 — First pixel** | A 512-byte BIOS boot sector: Spectrum loading stripes and a hello over serial. 211 of 510 bytes used. | 31 Aug 2026 — pixels by teatime | [the stripes](history/2026-08-31-stage0-stripes.png) |
| **1 — Owning the processor** | A hand-written PE32+ UEFI application: own GDT and paging, all cores woken with INIT-SIPI-SIPI, each painting its own band at native resolution. The picture *is* the core count. | 31 Aug 2026 | [eight bands, eight cores](history/2026-08-31-stage1-bands.png) |
| **2 — Senses** | Interrupt-driven PS/2 keyboard and a framebuffer text console. First words typed into the OS: *hello world. yay. thank you claude.* | 1 Sep 2026, midnight | [the first words](history/2026-09-01-stage2-first-words.png) |
| **3 — Memory of its own** | A virtio-blk driver and an append-only notebook filesystem, grown overnight in one unattended run. Typed lines survive a reboot: *"It remembers!"* | 1 Sep 2026 | [it remembers](history/2026-09-01-stage3-it-remembers.png) |
| **4 — The umbilical** | virtio-net, a minimal TCP/IP stack, and a caged network with one door to a broker that relays to Claude. The booted OS asked Claude its first question and printed the answer. | 1 Sep 2026 | [the first conversation](history/2026-09-01-first-conversation.png) |
| **5 — The conversation** | The loop closes. A line typed `! ...` goes to Claude and comes back as machine code, **rehearsed in a twin boot before it may run**, then cached in the germline. *"Make me a clock"* produced a running clock — with the date and an exit line nobody asked for. | 1 Sep 2026 | [the first grown clock](history/2026-09-01-first-grown-clock.png) · [the boot log](history/2026-09-01-stage5-boot-log.png) |
| **6a — The glass** | The screen gets one owner: a glass core composites four regions from surfaces in RAM at sixty frames a second; an obs strip of live counters the harness reads back against the machine's own obs page; an app is four callbacks stepped beside a live conversation. The grown clock ticked in its panel while a note was typed next to it — with two switches Claude added unasked. | 2 Sep 2026 | [the clock in its panel](history/2026-09-02-ring6a-clock-in-panel.png) |
| **6b — The store of plans** | An app is a plan file: intent in English plus five-verb tests. `! install calculator` was grown from `plans/calculator.md`, rehearsed in the twin against the plan's own tests, kept on a second disk with its SHA-256, and launched after a reboot with the broker gone. | 3 Sep 2026 | [the calculator installed](history/2026-09-03-ring6b-calculator-installed.png) · [launched offline](history/2026-09-03-ring6b-calculator-offline-launch.png) |
| **6c — The pointer** | The PS/2 mouse on the i8042, the first device configured rather than inherited: a one-cell arrow drawn last in every frame by the glass core, pointer input-to-photon on the strip, a click on the choices row doing what its key does, and an optional fifth callback `point(row, col, button)` for apps that want clicks. | 5 Sep 2026 | [hello cursor](history/2026-09-05-ring6c-hello-cursor.png) · [the corner and the calculator](history/2026-09-05-ring6c-corner-calculator.png) |

The pictures in `history/` are the machine's own screendumps, taken by each stage's acceptance harness (Stage 4's and Stage 5's are window captures from the oracle runs).

![The first grown component — asked for a clock at the GermOS prompt, Claude wrote one in machine code; it was rehearsed in the twin, then it ran](history/2026-09-01-first-grown-clock.png)

**Stage 6 — growth — is closed** (5 September 2026): the glass, the store of plans and the pointer, three rings in four days. The owner's first oracle run found a defect the gate had missed — the arrow left fragments along the bottom edge, because a 1080-pixel mode is not a whole number of 16-pixel cells — and the fix made the bottom row a click margin for the choices row, as Fitts's law asks of an edge.

**Stage 7 — metal — is open** (9 September 2026): the patient is an HP Compaq Elite 8300, and every driver the metal needs is rehearsed first in the twin. **Ring 7a, the disk** (closed 9 September 2026), replaces virtio-blk with an AHCI driver: one SATA disk, a GPT the machine writes itself on a blank drive, the notebook and the home as two partitions with their formats unchanged inside ([`stage7/DISK.md`](stage7/DISK.md)). The disk is chosen by what it holds — a GermOS table wins, a blank disk is formatted, anything else is refused by name and never written. **Ring 7b, the wire** (closed 15 September 2026), replaces virtio-net with an e1000e driver beside it — the NIC preferred by kind, the MAC from the device's own registers, the link awaited and its absence a named error — and puts a relay in front of the frozen broker ([`stage7/WIRE.md`](stage7/WIRE.md)): on the home switch the relay is what answers the guest's ARP for `10.0.2.4`, and in the twin every question, grow and install of the gate goes through it. **Ring 7c, the metal** (green pending the oracle, 15 September 2026), is procedure and a guard: the EDID is read from BAR2 only on QEMU's VGA and any other display gets `S7: edid none` and the highest mode the console can hold; the i8042 is initialised cold — the controller's self-test before its command byte, `i8042: self-test ok` and `i8042: mouse reset ok` (or `mouse none`, a line not an error), every controller failure named; staggered spin-up is honoured on the AHCI ports; `stage7/mkstick.py` writes a bootable stick image with mtools at the partition's offset and the gate boots a copy of it over USB with no boot image on SATA, re-proving every stage in one run; the storage bodyguard denies CC the flash's own words and every spelling of a device path; and `stage7/METAL.md` is the owner's day, step by step. Test 5 is the HP itself.

## Running it

Everything runs inside QEMU — that is a design rule, not a convenience: nothing touches real hardware until Stage 7, on a sacrificial machine. On Ubuntu:

```
sudo apt install nasm qemu-system-x86 ovmf mtools python3
```

Each stage keeps a frozen acceptance gate — `./stageN/test.sh` from the repo root builds it and proves it still works. To *see* each one:

**Stage 0** — stripes and a serial hello:

```
./stage0/test.sh
qemu-system-x86_64 -drive format=raw,file=stage0/out/stage0.img -serial stdio
```

**Stage 1** — one band per core (the machine's core count, painted):

```
./stage1/mkimage.sh
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage1/out/esp.img -serial stdio
```

**Stage 2** — type at the prompt:

```
./stage2/mkimage.sh
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage2/out/esp.img -serial stdio
```

**Stage 3** — type a line, quit, boot again: it remembers.

```
./stage3/mkimage.sh
truncate -s 16M stage3/out/notes.img
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage3/out/esp.img \
  -drive format=raw,file=stage3/out/notes.img,if=virtio -serial stdio
```

**Stage 4** — ask Claude a question from inside the OS. Two terminals; the broker shells out to the [Claude Code CLI](https://claude.com/claude-code) (`claude`), which must be installed and logged in:

```
python3 broker/broker.py
```

```
./stage4/mkimage.sh
truncate -s 16M stage4/out/notes.img
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage4/out/esp.img \
  -drive format=raw,file=stage4/out/notes.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Type `? ` and a question. A line without the marker is a note, and persists — exactly as Stage 3. The guest's network is a cage: `restrict=on` means it can reach nothing at all except that one forwarded socket to the broker on localhost.

**Stage 5** — ask the OS to grow something. The Stage 5 broker answers questions *and* requests; on a request it asks Claude for a flat binary against the ABI in [`stage5/GERMLINE.md`](stage5/GERMLINE.md), **rehearses it in a headless boot of the same image** (the twin) before it is allowed anywhere near your screen, caches what passed in `germline/` (per machine, gitignored), and delivers it. Two terminals:

```
python3 broker/germline.py
```

```
./stage5/mkimage.sh
truncate -s 16M stage5/out/notes.img
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage5/out/esp.img \
  -drive format=raw,file=stage5/out/notes.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Type `! make me a clock`. The indicator turns while Claude writes and the twin rehearses; a clock ticks; **Esc** brings the prompt back; ask again and it comes from the germline at once. `?` still asks (with or without the space now), and a plain line is still a note. The automated gate (`./stage5/test.sh`) uses only a mock broker with a canned test component, so it never spends a token.

**Stage 6, ring 6a — the glass.** The screen gets one owner: a dedicated core composites four regions — an obs strip of live counters on top, a choices row at the bottom, the conversation on the left, the app on the right — from surfaces in RAM, sixty frames a second. An app is four callbacks (`init`, `step`, `key`, `exit`, per [`stage6/GLASS.md`](stage6/GLASS.md)) stepped by the main loop, so the conversation stays alive beside it. The display's EDID picks the mode, so QEMU is given a display that states one. Two terminals:

```
python3 broker/glass.py
```

```
./stage6/mkimage.sh
truncate -s 16M stage6/out/notes.img
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage6/out/esp.img \
  -drive format=raw,file=stage6/out/notes.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Type `! make me a clock`: the strip says `growing` while Claude writes and the twin rehearses, then the clock ticks in the app panel with `running make me a` on the strip. **Tab** gives the keys to the prompt — type a note beside the running clock — and **Tab** gives them back; **Esc** closes the app. The choices row always says what the keys do. The Stage 5 clock in `germline/` is an ABI 1 entry: ring 6a keys its germline `abi2`, so the first request regenerates. The automated gate (`./stage6/test.sh`) speaks only to the mock and its canned apps, and spends no token.

**Stage 6, ring 6b — the store of plans.** An app is a file: [`plans/<name>.md`](plans/) — its name, an **Intent** in plain English, up to four **Choices** for the choices row, and **Tests** in five verbs (`press`, `wait`, `expect "…"`, `expect not "…"`, `expect changed`) that the twin runs against the build before it is delivered ([`stage6/PLANS.md`](stage6/PLANS.md)). `! install <name>` grows it from the intent, rehearses it against the plan's own tests on top of the safety criteria, and delivers it with the `installed` flag; the machine writes it to a second disk, the **home image** ([`stage6/HOME.md`](stage6/HOME.md): a header, a table of apps with each build's SHA-256 and the previous build kept for undo), and runs it. From then on `! <name>` launches it from disk with nothing on the wire — the choices row names the installed apps — and `! undo install <name>` swaps the previous build back. Windowed runs are 1920x1080; the twin is the same machine. Two terminals:

```
python3 broker/plans.py
```

```
./stage6/mkimage.sh
truncate -s 16M stage6/out/notes.img
truncate -s 16M stage6/out/home.img
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage6/out/esp.img \
  -drive format=raw,file=stage6/out/notes.img,if=virtio \
  -drive format=raw,file=stage6/out/home.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Type `! install calculator`: the strip says `installing` while Claude builds and the twin runs the plan's five tests; `installed calculator` and the calculator in its panel with `= result   c clear   Esc exit   Tab prompt` on the row. Do a sum; Esc. Quit QEMU, stop the broker, boot the same command again: `S6: home 1 apps`, `! calculator` on the choices row, and `! calculator` runs it from disk. An install may be amended at the door — `! install calculator, but big keys` — and a plan whose build fails its own tests is refused naming the test. The automated gate (`./stage6/test-6b.sh`) speaks only to the mock and its two canned plans, `echo` and the `liar`, and spends no token.

**Stage 6, ring 6c — the pointer.** The PS/2 mouse arrives because the constitution demands it: the choices row has targets on an edge, and Fitts's law is about pointing at them. The i8042 is configured for the first time (the auxiliary port and its interrupt, the mouse reset and told to report — the path Stage 7's metal will have, not a tablet); the glass core draws a one-cell arrow as the last thing in every frame from a position the interrupt handler keeps in the obs page; pointer input-to-photon joins the strip as `pt`, beside the packet and click counts, the moment the mouse first speaks — until then the machine is ring 6a's to the pixel. A click on a choices-row item does what its key does: `? ask` and `! grow` type their marker, `! calculator` launches from disk (on an empty prompt line), an app's declared choices reach the app, `Esc exit` and the Tab items move as the keys do. An app may announce a fifth callback in its blob — `POINTER2` at byte 16, then the offset of `point(row, col, button)` — and every earlier app, the calculator included, is clicked on harmlessly ([`stage6/GLASS.md`](stage6/GLASS.md), "Ring 6c — the pointer"). Two terminals:

```
python3 broker/pointer.py
```

```
./stage6/mkimage.sh
truncate -s 16M stage6/out/notes.img
truncate -s 16M stage6/out/home.img
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage6/out/esp.img \
  -drive format=raw,file=stage6/out/notes.img,if=virtio \
  -drive format=raw,file=stage6/out/home.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Click in the QEMU window to grab the mouse (Ctrl+Alt+G releases it) and move it: the arrow appears, `S6: mouse ready` goes out on serial, and `pt`, `pk` and `cl` join the strip. Click `! grow` and type a request, or `! install calculator` and then click `! calculator` on the row; click into the calculator's panel (nothing happens — it has no `point`), then `= result`, `c clear`, `Tab prompt`, `Tab app`, `Esc exit`. With the mock broker (`python3 broker/pointer.py --mock`) the request `! point app` serves the one committed app that takes clicks: each button draws its digit where you clicked. The automated gate (`./stage6/test-6c.sh`) drives QEMU's PS/2 mouse through the monitor, speaks only to the mock, and spends no token.

**Stage 7, ring 7a — the disk.** The same machine on q35's own SATA controller with the patient's CPU model: one 64 MB raw disk, blank, which the machine partitions on its first boot — a protective MBR, a GPT with GermOS's own type GUIDs, a 16 MB notes partition at LBA 2048 and a 16 MB home partition at 34816, the frozen formats byte for byte inside — and recognises on every boot after. `S7: gpt written` on the boot that formats, then `S7: disk port 1 131072 notes 2048 home 34816`. A disk holding anyone else's table, a boot sector or a torn table is refused by name (`ERR: no GermOS disk and no blank disk - port 0: other, port 1: gpt`) and never written; the twin's own boot image sits on port 0 and is never touched. Everything Stage 6 does runs unchanged on the partitions. Two terminals:

```
python3 broker/metal.py
```

```
./stage7/mkimage.sh
truncate -s 64M stage7/out/disk.img
qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage7/out/esp.img \
  -drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

Type a note; `! install calculator`; do a sum; quit, stop the broker, boot the same command again: the note is back, `S7: home 1 apps`, and `! calculator` runs from the home partition. On the host, `blkid -p stage7/out/disk.img` and `partx -s stage7/out/disk.img` read the table the machine wrote. The automated gate (`./stage7/test.sh`) drives five serial boots, the persistence pair and ring 6b's store test on the partitions, speaks only to the mock, and spends no token.

**Stage 7, ring 7b — the wire.** The same machine on the NIC the metal has: an e1000e — QEMU's 82574L standing in for the HP's 82579LM, the same register family — found by vendor, class and a table of three ids and preferred over a virtio-net whenever both are present, owned, reset with interrupts masked, its MAC read from `RAL0`/`RAH0`, its link awaited for ten seconds (`S7: nic 6c:3b:e5:3b:86:45` then `S7: link up`; a link that never comes is `ERR: nic link did not come up within 10 s`, never a hang), sixteen legacy receive descriptors and eight transmit descriptors, polled ([`stage7/WIRE.md`](stage7/WIRE.md)). The TCP stack above is untouched. On the metal the guest keeps its frozen addressing and ARPs for `10.0.2.4` on the home switch; `broker/relay.py` is what answers there — it binds exactly `10.0.2.4` or `127.0.0.1` and nothing else, forwards each connection to the frozen broker on `127.0.0.1:9999`, and logs one JSON line per connection. In the twin the relay sits on `127.0.0.1:9997` and the cage's `guestfwd` lands on it, so every question, grow and install of the gate goes through it. Three terminals:

```
python3 broker/wire.py
```

```
python3 broker/relay.py --bind 127.0.0.1 --port 9997
```

```
./stage7/mkimage.sh
rm -f stage7/out/disk.img; truncate -s 64M stage7/out/disk.img
qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -drive format=raw,file=stage7/out/esp.img \
  -drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9997' \
  -device e1000e,netdev=n0,mac=6c:3b:e5:3b:86:45 -serial stdio
```

The serial log says `S7: nic 6c:3b:e5:3b:86:45` then `S7: link up`. Type `? ping`: the relay's terminal logs one connection, `pong` appears, and the strip says `w 001`. Type `! make me a clock`: Claude writes it, the twin rehearses it on a SATA disk and an e1000e of its own, and the clock ticks in its panel. On the HP's day the relay runs with no flags (`10.0.2.4:9999`, the switch) beside the broker.

**Stage 7, ring 7c — the metal.** The twin of the HP: the same binary on a USB stick the firmware reads (`stage7/mkstick.py` writes `stage7/out/stick.img` — a protective MBR, a GPT, one 64 MB EFI System Partition holding `EFI/BOOT/BOOTX64.EFI`, formatted and filled with mtools at the partition's offset, no loop device), booted as a copy over `qemu-xhci` + `usb-storage` with no boot image on SATA, the SATA disk and the e1000e as before. The guest reads an EDID only from QEMU's VGA and takes the highest mode the console can hold on any other display (`S7: edid none`), initialises the i8042 cold (`i8042: self-test ok`, `i8042: mouse reset ok`), and honours staggered spin-up on the AHCI ports. The relay closes a guest that never closes; `broker/chart.py` reads the HP's serial port on the day; `stage7/METAL.md` is the owner's procedure — the flash by his own hand by the by-id path, the LAN port's second address, the three terminals, the first boot line by line. Three terminals, the same as ring 7b's with the stick in place of the boot image:

```
python3 broker/wire.py
```

```
python3 broker/relay.py --bind 127.0.0.1 --port 9997
```

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

OVMF says it is loading from the USB drive, then the nineteen lines with `S7: disk port 1 …` (the only disk on SATA now) and the `i8042:` pair before `S7: keyboard ready`. Everything the earlier rings did runs unchanged. The automated gate (`./stage7/test-7c.sh`) parses the stick from the host, boots it three times over USB, re-proves every stage in one scripted run, and checks the bodyguard's table — mock only, no token. The stick is a copy in the twin because QEMU locks what it boots; the file as built is what the owner flashes.

## The team of three

GermOS is built by a team of three, and the division of labour is the experiment as much as the OS is:

- **Wajira** ([@IndyWH](https://github.com/IndyWH)) — product owner and QA oracle. A UK GP and health-informatician who verifies every stage by eyeball; the medical model runs through the project's verification (the trial protocol precedes the treatment).
- **Claude Cowork** — design and specs. Writes each stage's one-page spec for approval, reviews every diff, flags the judgement calls.
- **Claude Code** — implementation. Writes all the assembly, one commit per numbered plan item, tests green before every commit — mechanically held to an approved plan by hooks it cannot edit.

The acceptance tests are written before the code and frozen by a hook; the human's word is the final gate of every stage. Every spec, plan, decision and mistake is in the git history and `HANDOVER.md` — the project's coordination channel is the audit trail.

## What this is not

Not a Linux replacement. Not a product. Not secure enough to trust with anything that matters — and never, under any circumstances, connected to clinical work or patient data. It is a laboratory for one thesis — that software can be grown rather than shipped — and the most fun available per kilobyte.

## Licence

[MIT](LICENSE).
