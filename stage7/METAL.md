# METAL.md — the HP's day: the flash, the wiring, the boot, test 5

**Stage 7 ring 7c, plan item 12. The owner's document — not frozen, not a
criterion.** It is the procedure Wajira carries out with his own hands, in
this order, and what the review reads afterwards. Every command in it is
copied from the files as they stand at ring 7c: `stage7/mkimage.sh`,
`stage7/mkstick.py`, `broker/wire.py`, `broker/relay.py`,
`broker/chart.py`, `stage7/test-7c.sh`. CC never runs steps 1–3 or 5's
`nmcli`: the storage bodyguard denies it every `/dev` path, `dd`, `of=`,
`by-id`, `ttyUSB` and `nmcli` in any Bash command, prose included, from
item 13 — the flash is the owner's hand by the by-id path, the same rule
as a freeze opening (spec decision 6).

The patient: the **HP Compaq Elite 8300 SFF** — Q77 AHCI SATA, an Intel
82579LM at `6c:3b:e5:3b:86:45`, PS/2 keyboard and mouse, COM A on the
rear panel, Intel HD graphics, AMI Aptio UEFI with Secure Boot off and
USB first in the boot order, four cores. The done-when, from
`stage7/spec.md`: **the HP boots GermOS from the stick; the `S7:` lines
arrive on mlrig's terminal in the twin's order; the glass on the monitor
at the native mode; a note kept across a power cycle; `? ping` answered
over the LAN; `! install calculator` built by the real broker over the
LAN and, after a reboot with the broker off, `! calculator` launched from
the SATA disk; a click on the choices row.** His word closes the ring and
the stage.

## 0. Once, before the day

- **The serial port's group.** `sudo usermod -aG dialout $USER`, then log
  out and in again (a new login, not a new terminal). Without it
  `chart.py` cannot open the adapter's port.
- **The build the gate passed.** At the repo root, on the commit whose
  `./stage7/test-7c.sh` is green:

  ```
  ./stage7/mkimage.sh && python3 stage7/mkstick.py
  ./stage7/test-7c.sh
  ```

  `stage7/out/stick.img` is the file to flash — **the file as built,
  never a copy the twin has booted**: a booted copy may carry OVMF's own
  variable store in its FAT, and the twin proved the file, not the copy.
- **The network, thought through once.** The guest keeps its frozen
  addressing — `10.0.2.15/24`, the broker at `10.0.2.4:9999`, no gateway,
  no route — and ARPs for `10.0.2.4` on the home switch. mlrig answers
  because its LAN port carries `10.0.2.4/24` as a second address (step 5).
  The OPNsense router routes nothing and needs no change. The link is
  plaintext on the home LAN by the owner's choice (spec decision 1).

## 1. The stick into mlrig, and only the stick

Plug the stick in. Then:

```
lsblk -o NAME,SIZE,MODEL,TRAN
```

**Exactly one line must say `usb` under TRAN, and its SIZE and MODEL must
be the stick's** (A3). Every other line is mlrig — none of them is ever a
target. If two lines say `usb`, unplug the other device and run `lsblk`
again before going on. If none does, the stick was not seen; try another
port.

## 2. The by-id path, and nothing else

```
ls -l /dev/disk/by-id/ | grep usb
```

Take the stick's `usb-<vendor>_<model>_<serial>-0:0` name — the one with
no `-part` suffix; the `-part1` beside it is its ESP. **The by-id path is
the only path used; never `sdX`** — a letter is whatever the kernel handed
out this boot, and a wrong letter is one of mlrig's disks.

**Unmount it first** (A3). The desktop auto-mounts a stick's partitions
the moment it is plugged in; writing the image over a mounted stick races
the mount's writeback, and the kernel then refuses to re-read the new
table. For each mounted partition of the stick (the `-part1` name, and
any other `-partN` `lsblk` showed mounted):

```
udisksctl unmount -b /dev/disk/by-id/usb-<name>-part1
```

`lsblk` again: no MOUNTPOINTS on the stick's lines.

## 3. The flash — the owner's hand

```
sudo dd if=stage7/out/stick.img of=/dev/disk/by-id/usb-<name>-0:0 bs=4M conv=fsync status=progress
sync
udisksctl power-off -b /dev/disk/by-id/usb-<name>-0:0
```

Then unplug. `conv=fsync` makes `dd` flush before it returns; `sync` is
belt and braces; `power-off` (A3) spins the stick down cleanly and
detaches it from the kernel, so nothing is left half-written when the
plug comes out. The whole image is 66 MiB and takes seconds.

## 4. The wiring

- **The SATA drive** into the HP — any size over 64 MB; the first boot
  wipes it (a blank disk is formatted with GermOS's table; a disk holding
  anyone else's table is refused by name and never written — so a drive
  with a leftover table must be blanked first, on another machine, or the
  boot ends at `ERR: no GermOS disk and no blank disk`).
- **The null-modem cable** COM A ↔ the USB-to-serial adapter on mlrig. A
  three-wire cable (TX, RX, ground) is enough: `chart.py` opens the port
  in a way that does not wait for DCD (A1).
- **Ethernet** from the HP into the home switch, beside mlrig.
- **The PS/2 keyboard and mouse** into their own sockets — not USB: the
  metal has no USB driver.
- **The monitor** on VGA or DisplayPort.

## 5. mlrig: the second address, then three terminals

**The LAN port's second address.** Find the port and the connection
NetworkManager knows it by:

```
nmcli device status
nmcli connection show
```

The LAN port is the `ethernet` device that is `connected`; its CONNECTION
column names `<name>`. Then:

```
nmcli con mod <name> +ipv4.addresses 10.0.2.4/24
nmcli con up <name>
```

**`nmcli con up` bounces the connection for a few seconds** — an SSH
session over it drops and a download stalls; do it between things (A7).
**`+ipv4.addresses` persists across reboots** — mlrig will carry
`10.0.2.4/24` on that port until it is removed (the last section says
how). Check:

```
ip -4 addr show <port>
```

Both addresses are listed, the usual one and `10.0.2.4/24`.

**The fallback**, for a port NetworkManager does not manage (its device
status says `unmanaged`):

```
sudo ip addr add 10.0.2.4/24 dev <port>
```

This one is gone at the next reboot on its own; add it again on the next
day (A7).

**Three terminals at the repo root**, in this order:

1. The broker — the real backend, `claude -p` over the subscription; it
   answers questions, grows requests and installs plans, every candidate
   rehearsed in the twin (a 64 MB SATA disk of its own, an e1000e of its
   own) before it is delivered:

   ```
   python3 broker/wire.py
   ```

   It prints `listening on 127.0.0.1:9999`. (Not `pointer.py`: its twin
   boots two virtio disks the Stage 7 binary would not find.)

2. The relay — with no flags its defaults are the day's: it binds
   `10.0.2.4:9999` and forwards to the broker on `127.0.0.1:9999`:

   ```
   python3 broker/relay.py
   ```

   It prints `relay listening on 10.0.2.4:9999 -> 127.0.0.1:9999`. If it
   prints `cannot bind 10.0.2.4:9999` instead, step 5's address is not on
   the port yet. It serves one connection at a time, logs each to stderr,
   and closes the guest's side itself two seconds after the broker has
   finished — so a machine powered off mid-answer never holds it. (In the
   twin it is `python3 broker/relay.py --bind 127.0.0.1 --port 9997`;
   9998 is the frozen twin's own listener, which is why the spec's twin
   command was corrected.)

3. The chart — the serial reader, **started before the HP is powered on**
   so `S7: alive` is the first line in the file:

   ```
   python3 broker/chart.py /dev/ttyUSB0 stage7/out/metal.log
   ```

   It prints `chart: reading /dev/ttyUSB0 at 115200 8N1, teeing to
   stage7/out/metal.log (Ctrl-C ends it)` and then every line the HP
   sends, as it arrives; the file gets the same lines with a timestamp. If
   the adapter is not `ttyUSB0`, `ls -l /dev/serial/by-id/` names it. A
   `Permission denied` is step 0's group.

## 6. Power on

Power the HP on. If the stick is not first in the boot order, **F9** at
the HP logo for the boot menu and choose the **UEFI** USB entry (not the
legacy one: Legacy is off, and the file the firmware loads is
`EFI/BOOT/BOOTX64.EFI` from the stick's ESP).

## 7. The first boot, line by line — the debugging table

The order of the first boot is the debugging strategy (`stage7/spec.md`):
serial first, then each device before the next is touched. The twin has
printed the same lines in the same order — `stage7/out/metal/serial.blank.8.txt`
from the last green gate is the reference. Where the chart stops says
where the bug is. **The monitor stays black until the glass core's first
frame** — nothing is drawn before `S7: glass core N` — so a black screen
before that line is not a display finding; read the chart:

| The chart shows | It means | Look at |
|---|---|---|
| nothing at all, ever | the code died before `serial_init` returned — or the stick did not boot GermOS, or COM A is not COM1 at `0x3F8` at 115200 | the HP's BIOS: the serial port's setting (`3F8/IRQ4`), the boot entry chosen; the cable's TX/RX crossed; `chart.py` started before power-on |
| `S7: alive`, then nothing, black screen | GOP: no protocol, or no 32-bit linear mode inside the console's limits, or `SetMode` failed | the next line is `S7: edid none` on Intel's GOP — its absence is `edid_read` (should be impossible: the guard prints `none` for any non-QEMU vendor); `S7: gop` absent is `err_no_gop`, `err_no_mode` or `err_setmode` on the chart |
| `S7: edid none` (expected on the HP) | Intel's display is not QEMU's VGA: BAR2 was not read; the highest mode by area is taken | nothing — this is the guard working; `S7: gop WxH` is the monitor's native mode |
| `S7: gop WxH`, then nothing | `ExitBootServices` or the switch to our own paging | the map key gotcha (CLAUDE.md); the identity map's size against the framebuffer's address in the gop line |
| through `S7: idt ready`, then nothing or a repeat | the APs: the MADT, INIT-SIPI-SIPI, the x2APIC path or the trampoline — the spec's unproven pair on real silicon | `S7: cores found N` absent: the MADT walk; `found` without `woken`: the trampoline; a repeated `S7: alive`: a triple fault |
| `S7: console CxR`, then nothing | the AHCI: the controller by class, the ABAR, the ports under `CAP.SSS` | `ERR: ahci port N did not come up after spin-up` names the port (ten seconds); `ERR: no SATA disk on any AHCI port`: the drive is not seen (cable, power, the BIOS's SATA mode must be AHCI, not IDE/RAID); `ERR: no GermOS disk and no blank disk`: the drive holds another table — blank it |
| `S7: home N apps`, then nothing, black screen — no `ERR:`, no repeat | the e1000e's first touches before the nic line: the function owned, BAR0 mapped, `IMC`, the reset — a hang with no `ERR:` is an MMIO access the PCH's LAN would not take (the 82579LM hangs the processor on a read straight after `CTRL.RST`; the 25 ms wait of item 16 is the first such fix, found on the first watched boot, 17 September 2026) | `e1k_attach` up to `msg_nic`, with `ich8lan.c` open beside the datasheet; `hp-lspci.log` says what the NIC looks like healthy |
| `S7: home N apps`, then `ERR: nic link did not come up within 10 s` | the 82579LM's PHY — the one thing the twin could not prove (spec: high) | the cable and the switch's port light first; then a ring item with the datasheet open (MDIC, the PHY reset) |
| `S7: link up`, `S7: component region`, `S7: obs page`, `S7: glass core N` | the wire and the glass core are up | — |
| `ERR: i8042 self-test failed` / `command byte not answered` / `input buffer never emptied` | the controller | the named step; a controller that answers `0x55` late is the bound (`I8042_WAIT_TRIES`, a second) |
| `i8042: mouse none` | no mouse answered its reset — the boot goes on, keyboard only | the mouse's plug (the socket beside the keyboard's), then the bound |
| `i8042: self-test ok`, `i8042: mouse reset ok`, `S7: keyboard ready` | the machine is up | — |
| `S7: keyboard ready` and no prompt on the monitor | the framebuffer: the uncached mapping, the stride, the mode | the serial log is complete and the screen is the bug (CLAUDE.md's first gotcha, in its other half) |
| `? ping` echoed, then `e1k: tdh N tdt N status 0x… …` and `ERR: nic transmit timed out` | the first frame's descriptor was not completed by the 82579LM within five seconds (the second watched boot, 17 September 2026; item 17 added the `e1k:` line) — the line names the device's state | read it by item 17's rule: **`tdh 0`** — the descriptor was never fetched: the PCH LAN's descriptor-fetch setup, the `TXDCTL0` and `TARC0` bits Linux sets in `e1000_initialize_hw_bits_ich8lan` before it transmits; **`tdh 1`** — the frame went out and only the `DD` write-back is missing; **`status` bit 4** (`TXOFF`) set — transmit is paused by flow control; **`fwsm`** says whether the ME holds the interface; `sta` is the descriptor's own status byte and `ring` its physical address. The twin's line reads `tdh 1 tdt 1 … sta 0x01`. **The fourth watched boot (17 September 2026, 19:50) read** `e1k: tdh 0 tdt 1 status 0x00080483 ctrl 0x00100240 tctl 0x0003f0fa txdctl 0x00000000 tarc0 0x00000403 ctrlext 0x01481000 fwsm 0x6001c04c sta 0x00 ring 0x00000000004ce000` — never fetched, the link up at 1000 full, `TXOFF` clear, TXDCTL zero, TARC0 bare, FWSM with `FW_VALID` (the ME shares the LAN). **Item 18 sets the ich8lan hardware bits** (CTRL_EXT 22, TXDCTL0/1 22, TARC0 23/24/26/27, TARC1 24/26/28/30) in `e1k_attach` before TCTL. **The fifth watched boot (17 September 2026, 20:53) read** `e1k: tdh 0 tdt 1 status 0x00080483 ctrl 0x00100240 tctl 0x0003f0fa txdctl 0x00400000 tarc0 0x0d800403 ctrlext 0x01481000 fwsm 0x6001c04c sta 0x00 ring 0x00000000004ce000` — the bits are in (the 82579LM reads them back) and the descriptor is still never fetched. **Item 19** reads the ME's window: with `FW_VALID` set the Management Engine shares the MAC's registers and a host write can be lost while FWSM bit 24 is set (Linux's `FLAG2_PCIM2PCI_ARBITER_WA`, the 82579 with the ME enabled — this HP), and TDLEN, TDBAL and TDBAH had never been read back. From item 19 every register write waits for that bit (`e1k_write`), the six ring registers are read back and rewritten (`e1k_verify`), and the line gains three fields read from the device — `… sta 0x00 tdlen N tdbal 0x… tdbah 0x… expect 0x…` (`expect` is the old `ring`: the address we wrote). **How to read the sixth boot:** `pong` — step 5 passes. The line again with **`tdlen 128` and `tdbal` equal to the low half of `expect`** — the ring is configured in the device and the fetch is gated elsewhere: the `EXTCNF_CTRL.SWFLAG` semaphore, then the TXDCTL write-back policy and `CTRL_EXT.RO_DIS`. **`tdlen 0` or a `tdbal` that does not match** — a lost write the wait did not catch: the window is not the one Linux waits on. **`ERR: nic register 0x… wrote 0x… read 0x… - it will not hold its value`** — the ME overwrites what the host writes; the rewrite bound is the next number to read. The numbers choose the fix — one item, with `ich8lan.c` open |

Every `S7:` line after `keyboard ready` is the raw echo of what is typed;
`S7: mouse ready` goes out once, on the first packet, when the mouse first
moves.

## 8. Test 5, in order

1. **The lines** on the chart in the twin's order — nineteen `S7:` lines
   on the blank disk, `S7: edid none`, `S7: gop` the monitor's native
   mode, `S7: disk port P …` with `S7: gpt written` before it, `S7: nic
   6c:3b:e5:3b:86:45`, `S7: link up`, the `i8042:` pair, `S7: keyboard
   ready`.
2. **The glass** on the monitor at the native mode: the boot log above
   the prompt, the strip's two rows, the choices row.
3. **A note.** Type a line, Enter. It echoes on the chart and journals;
   the strip's `n` counts it.
4. **Power off, on** (the button; there is no ACPI). The chart shows
   eighteen lines with `S7: notebook 1 notes`; the note is back above the
   prompt.
5. **`? ping`** — the relay's terminal logs one connection, `pong` on the
   screen, `w 001` on the strip. (A `no answer from the broker` on the
   screen: the relay's terminal says whether the connection arrived — if
   nothing arrived, the ARP for `10.0.2.4` was not answered: step 5's
   address; if it arrived and the broker refused, terminal 1.)
6. **`! install calculator`** — the strip says `installing` while the
   real backend builds from `plans/calculator.md` and the twin on mlrig
   runs its five tests on a SATA disk of its own; then `installed
   calculator` in its panel with `= result` and `c clear` on the row. Do
   a sum. Esc.
7. **Power off; stop the broker and the relay (Ctrl-C in terminals 1 and
   2); power on.** `S7: home 1 apps`; `! calculator` on the choices row.
8. **A click.** Move the mouse — the arrow appears, `S7: mouse ready` on
   the chart, `pt` on the strip. Click `! calculator` on the choices
   row: it launches from the SATA disk with nothing on the wire (`w 000`,
   `io 000000/000000`). Do a sum. Esc.

His word closes the ring and Stage 7.

## 9. Afterwards

- Ctrl-C in terminal 3. Copy the chart and photograph the screen:
  `history/2026-MM-DD-ring7c-serial.log` (the file
  `stage7/out/metal.log`) and `history/2026-MM-DD-ring7c-<what>.png`.
  Keep the relay's terminal output too; the review reads all three.
- **Undo the second address** when Stage 7 is closed and the HP's days
  are over (A7):

  ```
  nmcli con mod <name> -ipv4.addresses 10.0.2.4/24
  nmcli con up <name>
  ```

  (The `ip addr add` fallback needs no undoing: it is gone at the next
  reboot.)

## What the twin could not prove

Said plainly, so the first surprise on the day is not a surprise:

- **The 82579LM's reset timing — found on the day.** The first watched
  boot (17 September 2026) hung on the read of `CTRL` straight after the
  `CTRL.RST` write: no fault, no line. The twin's 82574L answers that
  read, so no gate could show it; item 16 leaves the reset write alone for
  25 ms, as Intel's own driver does. The link came up on the second boot;
  **the transmit descriptor path is the next thing the twin could not
  prove, found on the same day:** the first frame's `DD` never set, `ERR:
  nic transmit timed out` after five seconds. From item 17 the `e1k:` line
  before that error names the device's state (step 7's last row); the
  twin's 82574L completes every descriptor, so only the HP can say. The
  fourth boot said `tdh 0` — never fetched — and item 18 sets the
  hardware bits Linux's `ich8lan.c` sets before this family transmits;
  the twin's 82574L fetches without them, so again only the fifth boot
  can say. The fifth boot said `tdh 0` with the bits in; item 19 waits
  for the ME's window before every register write and reads the ring
  registers back — QEMU has no Management Engine, so the twin's FWSM
  reads 0 and the wait never waits; only the sixth boot can say.
- **The 82579LM's PHY.** The twin's e1000e is an 82574L; the HP's NIC is
  the same register family behind the PCH with its own PHY. `SLU` is set,
  the forced speed and duplex cleared, the PHY left to autonegotiate;
  `MDIC` and the EEPROM are not touched. `link up` waits ten seconds and
  ends in a named error. The fix, if it is needed, is a ring item with
  the datasheet open.
- **`CAP.SSS`.** The twin's controller has staggered spin-up clear and
  its firmware sets `SUD` itself; the HP's may not. The guest sets `SUD`,
  gives each port a second to show a device and a device ten seconds to
  come up, and halts naming the port otherwise. Proven only with the
  path forced in a probe.
- **AMI's GOP.** The mode list's order and contents, the stride, the
  framebuffer's address: all read at boot, never assumed; the console's
  limits are judged before a mode is taken. `S7: gop` says what was
  chosen before a pixel is drawn.
- **The i8042's timing.** QEMU's controller answers on the first poll;
  the HP's has real latency. Every answer has a second.
- **The x2APIC path and the trampoline** on real silicon, and OVMF's
  variable store against AMI's: the first boot's chart will say.
