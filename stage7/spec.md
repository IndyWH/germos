# Stage 7 — Metal · spec

**Approved by the owner, 9 September 2026**, all recommendations taken, decision 5 amended (the switch, not a cable). Implementation: Fable 5.1 at high effort for rings 7a and 7b, medium for ring 7c (decided at the gate). The N-of-1 trials ring comes after the metal. Patient one is the **HP Compaq Elite 8300 SFF** (not the Lenovo HANDOVER names); patient two, later, the ThinkStation P330.

**Goal (foundation §7):** a sacrificial machine, boot from USB, every prior stage re-proven on real hardware. **Proves it was never just a simulation.**

**The policy gate, re-checked 9 September 2026:** Anthropic's help centre (article last updated 16 June 2026) still says the June 2026 change is paused — "nothing has changed: Claude Agent SDK, `claude -p`, and third-party app usage still draw from your subscription's usage limits." The broker keeps shelling out to `claude -p`, no API keys anywhere. Re-check at the Stage 8 gate.

## The patient, and what it demands

| The HP has | GermOS drives it today with | Stage 7 needs | QEMU twin device |
|---|---|---|---|
| Q77 SATA controller, AHCI; no drive fitted yet | virtio-blk (does not exist on metal) | **an AHCI driver** — notes and home on one SATA disk | `ich9-ahci`, q35's own SATA controller — `esp.img` already boots from it |
| Intel 82579LM gigabit, MAC 6C:3B:E5:3B:86:45 | virtio-net (does not exist on metal) | **an e1000e-family driver** | `e1000e` (emulates the 82574L: same MAC register family, a different PHY) |
| PS/2 keyboard and PS/2 mouse sockets | the i8042, configured since ring 6c | the same, plus a cold init that assumes nothing | the i8042, unchanged |
| COM A, 9-pin, on the rear panel | COM1 at 0x3F8, 115200 8N1 | the same — the observation chart survives | `-serial stdio`, unchanged |
| Intel HD graphics, VGA and DisplayPort | GOP, mode by the display's EDID read from QEMU's VGA BAR | GOP as before; **the EDID read guarded** (below) | `VGA,edid=on` as before |
| UEFI (AMI Aptio, HP K01 v03.08), Secure Boot off, Legacy off, USB first in the boot order | OVMF loads `BOOTX64.EFI` from a FAT image on SATA | OVMF loads the same file **from a USB stick** | `qemu-xhci` + `usb-storage` carrying the stick image — the firmware does the USB reading, GermOS never does |
| 4 cores, no HT; 8 GB | the MADT, INIT-SIPI-SIPI, `-smp 2` and `8` | the same; the gate adds `-smp 4` | `-smp 4 -cpu IvyBridge` (decision 4) |

Two things the inventory settles. **No USB driver this stage:** keyboard and mouse are PS/2 and the stick is read by the firmware, so XHCI stays in the "later, or never" column. **The serial question does not arise:** COM A is real; the USB-to-serial adapter plugs into mlrig, a null-modem cable joins the two DTE ports.

**What cannot be rehearsed, said plainly.** The twin's `e1000e` is an 82574L; the HP's 82579LM is the same register family behind the PCH with its own PHY, so link-up on the metal is the one thing the twin cannot prove. AMI's GOP, the HP's i8042 timing and its AHCI spin-up are likewise real silicon the twin only approximates. That is why ring 7c's boot is ordered so each device reports before the next is touched.

## Why three rings

| Ring | Name | What it proves | Done when |
|---|---|---|---|
| 7a | **The disk** | The machine keeps what it grows on a real controller | Stages 3 and 6b re-proven on an AHCI disk in the twin: a note survives a reboot, `! install echo` lands on the home partition, `! echo` launches with no broker |
| 7b | **The wire** | The umbilical works on a real NIC, and the cage becomes the home switch | Stages 4 to 6 re-proven on `e1000e` in the twin through the relay that will sit on mlrig's LAN port |
| 7c | **The metal** | It was never just a simulation | The HP boots GermOS from the stick: `S7:` lines on mlrig's serial terminal, the glass on the monitor, a note kept across a power cycle, a question answered over the LAN, an app installed from a plan and launched with the broker off, a click |

Each ring is a fresh CC session with its own plan gate and its own frozen tests. Rings 7a and 7b are drivers (high effort); 7c is procedure and a guard (medium). The Stage 6 binary and gates stay untouched: Stage 7 is `stage7/stage7.asm`, copied from `stage6.asm` at ring 7a item 1, drivers swapped, and Stages 0 to 6 stay green forever on their own binaries.

## Ring 7a — the disk

**One SATA disk, two partitions.** The guest owns the disk whole. On first boot it finds no GPT and writes one: a protective MBR, a GPT header, two partitions with GermOS's own type GUIDs — **notes**, 16 MB, and **home**, 16 MB — each holding its frozen format unchanged, so `stage3/NOTEBOOK.md` and `stage6/HOME.md` stand byte for byte; the partition is the raw image, moved. On later boots it reads the GPT and finds them by type GUID. `S7: disk <sectors> notes <lba> home <lba>` joins the serial lines, and `S7: gpt written` on the boot that formats. (Decision 2.)

**The driver.** AHCI per the 1.3 spec: the controller found by PCI class 0x0106 subclass 01, ABAR mapped uncached, one port with a SATA disk (signature 0x0101), the port stopped and its command list and FIS receive area given from BSS, `IDENTIFY DEVICE` for the sector count, then `READ DMA EXT` and `WRITE DMA EXT` one command slot at a time, polled, interrupts off — the same shape as the virtio-blk driver it replaces. Bus mastering set before any address is handed over (the standing gotcha). `blk_rw` keeps its signature; the two virtio devices become two partition descriptors over one AHCI port.

**The twin.** `stage7/out/disk.img`, a 64 MB raw file, on q35's SATA: `-drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1`, beside `esp.img` on `ide.0`. No `if=virtio` anywhere in a Stage 7 command. The gate parses the GPT and both partitions from the host with a Python GPT reader shared with the checker.

**Acceptance tests, ring 7a** (written first, frozen, mock only, no token):

| # | Test |
|---|---|
| 1 | **Artefact** — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image (standing). |
| 2 | **Serial** — ring 6c's lines as `S7:`, plus `S7: disk …` and, on a blank disk, `S7: gpt written`; found = woken = smp at `-smp 2`, `4` and `8`. |
| 3 | **The notebook on SATA** — Stage 3's persistence test on the notes partition: two notes, a reboot, both back; the partition parsed from the host agrees with the screen. |
| 4 | **The store on SATA** — ring 6b's test 4 on the home partition: `! install echo` through the mock, reboot with no broker, `S7: home 1 apps`, `! echo` runs from disk, the liar refused, the undo hash-checked from the host. |
| 5 | **Owner, windowed** — one note, one reboot, `! calculator` from a home partition the real broker installed. His word closes the ring. |

## Ring 7b — the wire

**The cage becomes a switch.** On metal the guest keeps its frozen addressing — 10.0.2.15/24, the broker at 10.0.2.4:9999, no gateway and no route: the guest ARPs for 10.0.2.4 directly (`stage4/UMBILICAL.md` and the stack, untouched). mlrig's LAN port carries 10.0.2.4/24 as a second address and answers that ARP across the switch (decision 5). A new unfrozen file, `broker/relay.py`, listens on 10.0.2.4:9999 and forwards each connection to the frozen broker on 127.0.0.1:9999 — the broker's bind stays frozen. In the twin the same relay is what slirp's `guestfwd` points at, so the gate exercises it. The link is plaintext on the home LAN, by the owner's choice; TLS stays in the broker this stage (decision 1).

**The driver.** e1000e per Intel's 82574 datasheet, the register set the 82579LM shares: the device found by vendor 0x8086 and a short class-0x0200 table, BAR0 mapped uncached, a reset, the MAC read from RAL/RAH (the EEPROM the firmware has already loaded), one receive ring and one transmit ring of legacy descriptors in BSS, polled, interrupts masked, link status from `STATUS.LU`. `S7: nic <mac>` reports what the registers say; `S7: link up` waits for the link with a timeout that ends in a named `ERR:` rather than a hang. The TCP stack above it is untouched.

**The twin.** `-netdev user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9998 -device e1000e,netdev=n0,mac=6c:3b:e5:3b:86:45`, with `relay.py` on 9998 relaying to the mock on 9999 — the guest's MAC is the HP's, so the serial line is the one the metal must print.

**Acceptance tests, ring 7b:**

| # | Test |
|---|---|
| 1 | **Artefact** (standing). |
| 2 | **Serial** — ring 7a's lines plus `S7: nic 6c:3b:e5:3b:86:45` and `S7: link up`. |
| 3 | **The question on e1000e** — Stage 4's round-trip through the relay and the mock at `-smp 2`, `4` and `8`; the wire counters on the strip agree with the relay's log. |
| 4 | **The cage holds** — `restrict=on` asserted; a mock-down run ends in a console message, not a hang; the relay refuses to start unless bound to 10.0.2.4 or 127.0.0.1; Stage 5's grow and ring 6b's install go through the relay unchanged. |
| 5 | **Owner, windowed** — `? ping` and `! make me a clock` with the real broker behind the relay. His word closes the ring. |

## Ring 7c — the metal

**The EDID guard.** The EDID is read from BAR2 only when the display device is QEMU's VGA (vendor 0x1234, device 0x1111). On any other display GermOS says `S7: edid none` and takes the highest GOP mode, which on Intel's GOP is the monitor's native mode. The Intel HD's BAR2 is its graphics aperture; parsed as an EDID it would name a mode that does not exist. (Decision 3.)

**The i8042 cold init.** Before the command byte is written: flush the output buffer, self-test (0xAA → 0x55), enable both ports, reset the mouse (0xFF → ACK, 0xAA, 0x00) with a bounded wait, enable reporting (0xF4). Every wait ends in a named `ERR:` instead of a spin. Retires Stage 2's debt.

**The stick.** `stage7/mkstick.py` (unfrozen builder) writes `stage7/out/stick.img`: protective MBR, GPT, one EFI System Partition of 64 MB holding `EFI/BOOT/BOOTX64.EFI` — written with mtools at the partition's offset, no loop device, no `/dev`, nothing outside `out/`. The twin boots that exact file over USB: `-device qemu-xhci -drive if=none,id=stick,format=raw,file=stage7/out/stick.img -device usb-storage,drive=stick`, no `esp.img` on SATA at all — so the gate proves the stick as the firmware will see it.

**The twin of the HP, one command** (the gate's, and the owner's windowed run):

```
qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -device qemu-xhci -drive if=none,id=stick,format=raw,file=stage7/out/stick.img -device usb-storage,drive=stick \
  -drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9998' \
  -device e1000e,netdev=n0,mac=6c:3b:e5:3b:86:45 -serial stdio
```

**The flash — the owner's hand, never CC's.** The storage bodyguard denies CC every `/dev` path, and that stays. The procedure lives in `stage7/METAL.md` as ordered steps, and it is Wajira who runs them at the repo root:

1. Plug the stick into mlrig. `lsblk -o NAME,SIZE,MODEL,TRAN` — the stick is the one line with `usb` under TRAN. Every other line is mlrig; none of them is ever a target.
2. `ls -l /dev/disk/by-id/ | grep usb` — take the stick's `usb-…` name. The by-id path is the only path used; never `sdX`.
3. `sudo dd if=stage7/out/stick.img of=/dev/disk/by-id/usb-<name> bs=4M conv=fsync status=progress` then `sync`, then unplug.
4. Fit the SATA drive in the HP (any size over 64 MB; it will be wiped by the first boot). Connect the null-modem cable COM A ↔ the USB-to-serial adapter on mlrig, the HP's Ethernet into the home switch, the PS/2 keyboard and mouse, the monitor on VGA or DisplayPort.
5. On mlrig: 10.0.2.4/24 added by hand as a second address on the LAN port (`nmcli con mod <name> +ipv4.addresses 10.0.2.4/24` then the connection brought up again); your user in the `dialout` group once, for the serial port; `python3 broker/pointer.py` and `python3 broker/relay.py` in two terminals; `python3 broker/chart.py /dev/ttyUSB0 stage7/out/metal.log` in a third — an unfrozen reader that tees the serial line to a file the review reads later.
6. Power the HP on, F9 for the boot menu if the stick is not first, choose the UEFI USB entry.

**The order of the first boot is the debugging strategy.** `S7: serial` is the first act, before video: a black screen with no serial line means the code died before it ran; with the line, the next device is the bug. Then GOP and `S7: edid none`, the mode line, the cores, the i8042, the disk, the NIC, `link up`, `ready`. Each line is a checkpoint on the chart, and the twin has printed the same lines in the same order.

**Acceptance tests, ring 7c:**

| # | Test |
|---|---|
| 1 | **Artefact** — the standing checks, plus `stick.img` parsed from the host: protective MBR, a valid GPT, an ESP with `EFI/BOOT/BOOTX64.EFI` byte-identical to the build. |
| 2 | **Serial, the metal configuration** — the twin boots the stick over USB with the SATA disk and e1000e: the full `S7:` line list, `edid 1920x1080` under QEMU's VGA and `edid none` (highest mode) when the harness boots with a display that is not QEMU's; the i8042 self-test and mouse reset lines. At `-smp 2`, `4` and `8`. |
| 3 | **Every stage re-proven in the twin of the HP** — Stage 2's typing, Stage 3's note across a reboot, Stage 4's question, Stage 5's grow, ring 6a's app in its panel, ring 6b's install and no-broker launch, ring 6c's click — one scripted run, the checkers reused through their seams. |
| 4 | **The bodyguard, extended** — the payload table gains the stick and the flash: `dd`, `of=`, `by-id`, `ttyUSB`, `nmcli` and every `/dev` spelling denied in CC's Bash, prose included; `mkstick.py` and `relay.py` allowed. 0 wrong. |
| 5 | **Oracle — Wajira, on the metal** — the HP boots the stick; the `S7:` lines arrive on mlrig's terminal in the twin's order; the glass on the monitor at the native mode; he types a note; power off, on, the note is back; `? ping` answered over the LAN; `! install calculator` built by the real broker over the LAN and, after a reboot with the broker off, `! calculator` launched from the SATA disk; a click on the choices row. **His word closes the ring and the stage.** The serial log goes into `history/` beside a photograph of the screen. |

## Decisions for the owner

1. **TLS on the LAN.** Recommend deferring: the link is on a home network the owner controls, the broker still speaks TLS to Claude, and the owner has said plainly that extra caution is not wanted here. The frozen TLS blob joins the guest at the ring where its traffic first crosses a network he does not own, or at Stage 8. The alternative is a TLS ring now, before any metal.
2. **The disk layout.** Recommend a GPT the guest writes itself, two partitions by type GUID, the frozen formats moved inside unchanged. The alternative — the two images at fixed LBA offsets with no partition table — is fewer lines but leaves a disk every other tool reads as blank, and the live USB is a useful witness.
3. **The EDID guard.** Recommend the vendor check: EDID from BAR2 only on QEMU's VGA, `edid none` and the highest GOP mode everywhere else. The alternative — drop the EDID path — would change ring 6a's frozen expectations.
4. **The twin's CPU.** Recommend `-cpu IvyBridge` in every Stage 7 command so CPUID in the twin says what the i5-3570 says; grown code is fitted to the processor it finds, and the twin should find the same one.
5. **The network.** Recommended a direct cable; **decided at approval: the HP plugs into the home switch** beside mlrig, and mlrig's ordinary LAN port carries 10.0.2.4/24 as a second address. The guest ARPs for 10.0.2.4 and mlrig answers across the switch; the OPNsense router routes nothing and needs no change. The relay binds 10.0.2.4 only. The cage's strict promise (the guest can reach nothing else) is given up knowingly on a home LAN the owner controls; the guest still has no route and listens for nothing.
6. **Who writes the stick.** Recommend the owner's hand by the by-id path, as above, with CC mechanically denied — the same rule as a freeze opening. The alternative, a hook that allows `dd` to a by-id USB path, is one allowed case in the table that guards mlrig's disks; not worth it for a step taken once per build.
7. **The ring split and effort.** Three rings, disk → wire → metal, high, high, medium. The alternative merges 7a and 7b into one driver ring; it saves a plan gate and puts two drivers behind one freeze.

## Risks, with likelihood

**Certain — the first metal boot goes black at some line.** Mitigation: serial first, the boot ordered device by device, the twin's log as the reference, commits minutes apart.

**High — the 82579LM's PHY.** The twin's 82574L has no PCH PHY; link-up on the HP may need a PHY reset through MDIC that the twin never exercised. Mitigation: `link up` is the last line before `ready`, its timeout is a named error, and the fix is one ring's item with the datasheet open.

**Medium — AMI's GOP.** A mode list in a different order, a `PixelsPerScanLine` that differs from the width, a framebuffer above 4 GB. Mitigation: the standing rules (stride from the mode, the BAR read and mapped, never assumed), and `S7: mode` printed before a pixel is drawn.

**Medium — the i8042 on real silicon.** Slower than QEMU's, and the mouse reset has real latency. Mitigation: the cold init's bounded waits with named errors.

**Low — the stick does not boot.** Mitigation: GPT with a proper ESP, rehearsed over `usb-storage` in the twin; a whole-disk FAT is the fallback.

**Low but fatal — the wrong disk.** Mitigation: by-id paths only, CC denied every `/dev`, the HP holds one sacrificial drive and nothing else, mlrig's disks never in the blast radius.

## Carried and deferred

Everything Stage 6 carried stands, less two debts paid: the i8042 is now initialised cold, and "one machine, one firmware" becomes two machines, two firmwares. Still unproven: the x2APIC path and the trampoline fallback (the HP's firmware may exercise either — test 2 will say). By design this stage: no USB driver, no NVMe (patient two), no ACPI interpreter (the machine is powered off by its button), no TLS, no timer interrupt, one SATA port, polled drivers, plaintext on the home LAN. The automated gate speaks only to the mock and spends no token. Nothing outside the repository is written by CC — the stick and the HP are written by the owner's hand.
