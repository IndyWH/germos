# HP-8a.md — the HP's day for ring 8a: good to live, Esc, hang and the reset

**Stage 8 ring 8a, plan item 17 (the plan's "Test 5"). The owner's
document — not frozen, not a criterion.** It is the procedure Wajira
carries out with his own hands, in this order, and what the review reads
afterwards. It is in `stage7/METAL.md`'s shape, and it leans on that
document for everything the metal already proved: the flash, the wiring,
the second address and the chart are METAL.md's steps as they stand.
Every command here is copied from the files as they stand at ring 8a item
17: `stage8/mkimage.sh`, `stage8/mkstick.py`, `broker/molt.py`,
`broker/relay.py`, `broker/chart.py`, `stage8/parts.py`. CC never runs the
flash, never names a device path in a command and never runs `nmcli`: the
storage bodyguard denies it all, and the flash is the owner's hand.

The patient is the one Stage 7 proved: the **HP Compaq Elite 8300 SFF**,
its disk holding GermOS's table, **277 notes** ending `trial verdict A`,
and the calculator. The stick now carries **seed 1**
(`stage8/seed-record.md`): the ring 8a binary, 57,344 bytes, SHA-256
`9e81c7b5d24ac363…`, from item 16b's commit `fc64a07`.

**What the day proves, from `stage8/spec.md` and the plan:** a part can
fail without taking the machine with it, on the metal.
- `good` earns its threshold in shadow on real typing and a real mouse, is taken, and runs live.
- Esc at power-on gives the machine back to the seed.
- `hang`, live, stops the HP. **The Q77's TCO watchdog resets it with nobody touching it**, and the next boot demotes `hang` and runs on the seed's own driver.

His word closes the ring.

**Two rules for the whole day.**
- **No stopping in the middle of a measured boot** (ring 7d's finding). Each boot's work runs to its health mark first, `S8: healthy <n>` on the chart. The chart and `! molt`'s table are read after that.
- **No timed coordination between the two machines.** The mock is changed only between boots, while the HP is powered off.

## 0. Once, before the day

- **The build the gate passed.** At the repo root, on item 17's commit,
  whose `./stage8/test-8a.sh` is green:

  ```
  ./stage8/mkimage.sh && python3 stage8/mkstick.py
  sha256sum stage8/out/BOOTX64.EFI
  ```

  `mkstick` prints `stick.img 69206016 bytes …`. The `sha256sum` must
  begin **`9e81c7b5d24ac363`**, seed 1's line in `stage8/seed-record.md`.
  Any other hash is not the seed the gate judged: stop there.
  `stage8/out/stick.img` is the file to flash, **the file as built**,
  never a copy the twin has booted.
- **The serial group.** On Omarchy it is `uucp` (ring 7d's day did it
  once: `sudo usermod -aG uucp $USER`, then a new login). `groups` lists
  it.
- **The HP's cables, all still in place:** the null-modem cable COM A ↔
  the USB-to-serial adapter on mlrig, the PS/2 keyboard and mouse in
  their own sockets, the monitor, and **the Ethernet in the home switch**
  (the boot waits for the link and halts without it, and two boots of
  the day fetch over it).
- **The second address.** mlrig moved to Omarchy on 22 September 2026,
  and its LAN port no longer carries `10.0.2.4/24`. Ring 7d's day needed
  no wire. On 27 September the port was `eno2` at `192.168.1.107/24`,
  under NetworkManager. **METAL.md step 5 adds it as written:** `nmcli
  device status` and `nmcli connection show` to find the connection, then
  `nmcli con mod <name> +ipv4.addresses 10.0.2.4/24` and `nmcli con up
  <name>`. The `ip addr add` fallback, if the port is unmanaged. Check
  with `ip -4 addr show eno2`: both addresses listed.

## 1. The flash — the owner's hand, once for the whole day

**METAL.md steps 1–3 as they stand**, with `stage8/out/stick.img` in
place of `stage7/out/stick.img`:
- `lsblk -o NAME,SIZE,MODEL,TRAN`: exactly one `usb` line, the stick's;
- the by-id path, never `sdX`;
- every partition of the stick unmounted with `udisksctl unmount`;
- `wipefs -a` on the partition, then on the stick;
- `dd … oflag=direct conv=fsync`, `sync`, `blockdev --flushbufs`;
- **`cmp -n 69206016 stage8/out/stick.img <the stick>` says nothing**;
- `lsblk` shows the partition as `vfat` with no MOUNTPOINTS;
- `udisksctl power-off`, then unplug.

**One flash for the day.** Nothing is changed on the stick between boots.
The HP's disk is never written by mlrig: every state change of the day
is a note the HP journals itself.

## 2. Three terminals at the repo root

In this order (METAL.md step 5's, with ring 8a's broker):

1. **The mock broker, serving `good`.** It calls nothing and spends no
   token; `! molt i8042` is answered with the committed fixture
   `stage8/fixtures/i8042-good.bin` in PARTS.md's part frame:

   ```
   python3 broker/molt.py --mock --part good
   ```

   It prints `listening on 127.0.0.1:9999`.

2. **The relay**, with no flags. Its defaults are the day's: it binds
   `10.0.2.4:9999` on the switch and forwards to the mock:

   ```
   python3 broker/relay.py
   ```

   It prints `relay listening on 10.0.2.4:9999 -> 127.0.0.1:9999`. A
   `cannot bind 10.0.2.4:9999` means step 0's second address is not on
   the port.

3. **The chart**, started **before the first power-on** and left running
   all day. It appends, so every boot of the day lands in one file:

   ```
   python3 broker/chart.py /dev/ttyUSB0 stage8/out/hp-8a.log
   ```

   As on every HP boot, the first line of each boot carries a few bytes
   of noise before `S7: alive`.

**On every boot that loads a part** (every boot from 2 on, except the
recovery boots), the console shows **`hold Esc for the seed`** for three
seconds before `S7: keyboard ready`. **Touch no key while it is showing,
except at step 6.** Other keys pressed then are dropped. Esc held there
is the owner's recovery, and it would spend that boot.

**On every boot that loads a part, wait for `S8: healthy <n>` on the
chart before powering off.** It comes 60 s after `S7: keyboard ready`. A
boot powered off before it is **unhealthy**. Two unhealthy boots in a row
demote the part in shadow (PARTS.md's recovery table), so a hurried day
could demote `good` for no fault of its own.

## 3. Boot 1 — no part, no change; the fetch

**Power on.** The chart shows **ring 7d's eighteen lines exactly**, as on
25 September. Among them are `S7: disk port 0 488397168 notes 2048 home
34816`, **`S7: notebook 277 notes`**, `S7: home 1 apps`, `S7: nic
6c:3b:e5:3b:86:45` and `S7: link up`, then the `i8042:` pair and `S7:
keyboard ready`. **There is no `S8:` line**, and no `hold Esc` on the
screen. This is the ring's first claim on the metal: with no `molt` note,
the seed is ring 7d's machine.

1. Type **`! molt`**. The app panel shows one row, **`i8042 generic`**.
2. Type **`! molt i8042`**. The strip says `growing` while the request goes over the switch. The relay logs one connection, and the mock's terminal logs `molt 'molt i8042 cpu … pci 8086:…:…': fixture i8042-good, 1152 bytes, threshold (3, 1000, 5000), key …`. **Copy that line into the record**: its identity is the HP naming itself, and ring 8b's germline keys on it. The console then says **`part i8042 shadow 4fe6beefc4bc57d0`**, and the chart shows `molt: i8042 shadow 4fe6beefc4bc57d0 3 1000 5000`.
3. Type **`! molt`** again: `i8042 shadow 4fe6beefc4bc57d0`, `boots 0/3 keys 0/1000 mouse 0/5000`, `disagreements 0 probation 0/3`.

Power off. (Boot 1 loaded no part, so it has no health mark to wait for.)

## 4. Boots 2, 3 and 4 — `good` in shadow

At each of the three boots:

1. **Power on; touch nothing** until `S7: keyboard ready`. The chart shows `S8: sha256 ok`; the console shows `hold Esc for the seed` for three seconds; then **`S8: part i8042 shadow 4fe6beefc4bc57d0`**, `molt: boot <n> i8042 shadow` (n = 1, 2, 3), **`S8: watchdog tco 30 s`**, then the seed's own `i8042:` pair (in shadow the generic serves) and `S7: keyboard ready`.
2. **Type about 200 keys of notes**: a few lines of plain lowercase words, Enter after each, **with a short pause after each Enter** (see below).
3. **Move the mouse steadily for about a minute**, with a few clicks in the conversation panel. **Not on the choices row**: a click there does what its key does, and `! calculator` would start an app.
4. **Wait for `S8: healthy <n>`** on the chart.
5. Type **`! molt`** and read the counts. They are summed over the shadow boots so far, and **`disagreements` must be 0**.
6. Power off.

**The rates, from D4 and PARTS.md's key-byte rule.** A plain key is two
keyboard bytes (make and break), and a shifted key four, so 200 keys a
boot is about 400 bytes, and 1,000 over three boots. The seed's init sends
the mouse `F6` (defaults) and never a sample rate, so it reports at the
PS/2 default of 100 packets a second, and only while it moves. So 5,000 packets over three boots is
about 17 s of steady movement a boot; a minute leaves a margin.

**Why plain lowercase and a pause after Enter.** PARTS.md states one
limit of the comparison. When a line is finished, the keys waiting behind
it are dropped (ring 7d's discard), and a Shift or an arrow's `E0` among
the dropped bytes can leave the part's decoder in a different state from
the generic's. The next key then counts as a disagreement, and one
disagreement blocks the take. The twin's synthetic human never meets
this. A human typing fast across an Enter could.

**After boot 4** the table should read **`boots 3/3`**, keys at least
**1000**, mouse at least **5000**, and `disagreements 0`. Then type
**`! molt take i8042`**. The console and the chart say **`molt i8042 live
4fe6beefc4bc57d0`**. The take journals this boot's counts first, so
typing after the health mark still counts.
- **If a count is short**, the take answers `below threshold: boots 3/3 keys …/1000 mouse …/5000` and changes nothing. Do one more shadow boot the same way, then the take again.
- **If `disagreements` is above 0**, see the debugging table.

## 5. Boot 5 — `good` live

Power on and touch nothing. The chart shows `S8: sha256 ok`, then **`S8:
part i8042 live 4fe6beefc4bc57d0`**, `molt: boot 4 i8042 live`, `S8:
watchdog tco 30 s`, and **the part's pair: `part: i8042 self-test ok`,
`part: i8042 mouse reset ok`**, with no `i8042:` line, then `S7: keyboard
ready`. The part initialised the HP's real controller, and every key and
packet from now on goes through it.
- Type a note: it echoes and journals.
- Move the mouse: the arrow follows it. Click in the conversation panel.
- Wait for **`S8: healthy 4`**.
- `! molt` shows `i8042 live 4fe6beefc4bc57d0` and `probation 1/3`.

Power off.

## 6. Boot 6 — Esc, the owner's way back

Deviation 11 and A3. **Power on without touching the keyboard.** Esc at
power-on opens the HP's own startup menu, so **press and hold Esc only
when `hold Esc for the seed` appears on the screen, never before.** The
window is 3 s. Keep holding until the console says **`S8: recovery
owner`**, then let go.

Expect:
- `S8: sha256 ok`, then `molt: recovery owner` and **`S8: recovery owner`**;
- **no `S8: part` line and no watchdog line**;
- the seed's own `i8042:` pair, and the keyboard working on the seed's driver. Type a note.

There is no health mark on this boot, because no part loaded. `! molt`
still shows `i8042 live 4fe6beefc4bc57d0`: Esc demotes nothing. Power
off.

If the HP's menu opened instead, Esc arrived before GermOS owned the
keyboard. Leave the menu with no change, power off, and do this step
again. The boot counts for nothing.

## 7. The mock changes, with the HP off

In terminal 1, Ctrl-C the mock, then:

```
python3 broker/molt.py --mock --part hang
```

`listening on 127.0.0.1:9999` again. The relay and the chart stay as
they are.

## 8. Boot 7 — `good` live again; `hang` fetched in its place

Power on and touch nothing. **`S8: part i8042 live 4fe6beefc4bc57d0`**
again, with the part's pair: Esc left nothing demoted.
- Type **`! molt i8042`**. The mock logs `fixture i8042-hang`; the console says **`part i8042 shadow f0668b687c68cab0`**. `hang` has replaced `good` as the slot's build, and from the next boot the slot is back on the generic, shadowing `hang`.
- Wait for **`S8: healthy 5`**. Power off.

## 9. Boot 8 — `hang` in shadow

Power on and touch nothing. **`S8: part i8042 shadow f0668b687c68cab0`**,
`molt: boot 6 i8042 shadow`, the watchdog line, and the seed's `i8042:`
pair. In shadow the part's `init` never runs, so it cannot hang.
- `hang`'s threshold is **1 boot, 100 keyboard bytes, 100 packets**. Type two lines of plain words, and move the mouse for ten seconds.
- Wait for **`S8: healthy 6`**.
- `! molt` shows `boots 1/1`, both counts over 100, and `disagreements 0`. Then **`! molt take i8042`** → **`molt i8042 live f0668b687c68cab0`**.

Power off.

## 10. Boot 9 — `hang` live, and the HP resets itself

Power on and touch nothing until `S7: keyboard ready`. Then **`S8: part
i8042 live f0668b687c68cab0`**, `molt: boot 7 i8042 live`, **`S8:
watchdog tco 30 s`**, and the part's pair.

**Leave the mouse alone** and type short numbered lines, Enter after
each: `hang 1`, `hang 2`, `hang 3`, … **Type line 8 straight after line
7's Enter, with no pause**, so that the hang comes as close to `hang 7`'s
stamp as the chart allows.

The part spins for ever on the 100th byte it is given after its own
`init`. Each of those lines is seven keys, so fourteen bytes, and by
PARTS.md's rule the HP stops during the **eighth line, at its first
key**. Mouse movement brings it sooner, three bytes a packet. The typed
letters stop appearing: the HP has stopped answering.

**Do nothing.** No key, no power button. The one exception is the HP's
own firmware screen asking for a key after the reset; the debugging
table says what to press. Within about half a minute **the
HP resets itself**. The monitor goes through the HP's own start, the
stick boots again, and the chart shows the next boot's noise and `S7:
alive`.

**What the next boot shows decides the rest:**

- **`molt: i8042 demoted f0668b687c68cab0 watchdog` and `S8: recovery i8042 watchdog`** (the twin's path, D1): the HP kept `SECOND_TO_STS` across its reset. The boot loads no part and shows no `hold Esc`. The seed's `i8042:` pair follows, and the keyboard works on the seed's driver. `! molt` shows **`i8042 demoted f0668b687c68cab0 watchdog`**.
- **No recovery line: the boot loads `hang` live again** (`S8: part i8042 live f0668b687c68cab0`, A4). The HP's firmware cleared the evidence, and with one unhealthy boot behind it the loader tries the part again. **Type `hang` lines again** until the HP stops and resets a second time. The boot after that shows **`molt: i8042 demoted f0668b687c68cab0 unhealthy` and `S8: recovery i8042 unhealthy`**, the keyboard on the seed's driver, and `! molt` showing `i8042 demoted f0668b687c68cab0 unhealthy`.
- **The chart said `S8: watchdog tco locked`, and the HP never resets** (decision 5's fallback): the HP's `NO_REBOOT` would not clear. Wait a full two minutes to be sure, then **use the power button**. The next boot finds no evidence and loads `hang` again. Type until it stops, and power off again. The boot after that is `S8: recovery i8042 unhealthy`. **This is the ring's finding, not a failure of the day.**
- **The chart said `S8: watchdog tco 30 s`, yet the HP has not reset a minute after it stopped** (Cowork, at the A6 review): the likely cause is that the firmware set `TCO_LOCK`. `TCO_EN` could then not be cleared, and the first expiry went to the firmware's SMM handler instead of counting on to the second. Wait the full two minutes, then take the power-button path above. **It is recorded as the ring's finding**, as decision 5's fallback says.

**Three things to read from the chart afterwards (A2, A4):**
1. **Whether the HP kept the evidence bit**: which of the first two paths it took.
2. **The HP's own deadline.** The chart stamps whole lines. Line 7's echo, `hang 7`, is the last line stamped before the hang, and the eighth line's first letter is its unfinished tail, which lands at the front of the next boot's first line. Take **the stamp of `hang 7` to the stamp of the next `S7: alive`**. That interval holds the deadline, **the pause between line 7's Enter and line 8's first key**, and the HP's own way from its reset to GermOS. The chart cannot split them. It is recorded beside the twin's 30.2 s (hang's trigger to OVMF's first byte) and the datasheet's 30 s.
3. **The recovery boot's lines** as above.

## 11. Afterwards

- Photograph the panel's last `! molt` table.
- Ctrl-C the chart, the relay and the mock.
- Then, on mlrig:

  ```
  python3 stage8/parts.py --serial stage8/out/hp-8a.log
  ```

  It reads the day's `molt:` lines back as notes and prints the same
  table the panel drew, then every `S8:` line of the day. It exits 0 when
  every molt line keeps PARTS.md's grammar.
- **Into `history/`:** the chart as `history/2026-MM-DD-ring8a-hp-serial.log`, the photographs as `history/2026-MM-DD-ring8a-<what>.jpg`, and the mock's terminal output (the HP's identity is in it).
- **The second address.** Leave it while more HP days are coming (ring 8b fetches over the same wire). METAL.md's section 9 says how to remove it.

His word closes the ring.

## The debugging table

| The chart or the screen shows | It means | Do |
|---|---|---|
| boot 1 has an `S8:` line | the notebook already holds a `molt` note | stop: the HP's disk is not the one this document expects |
| boot 1 stops before `S7: keyboard ready` | not ring 8a: the seed is ring 7d's here, line for line | METAL.md step 7's table, as on the metal's first day |
| `no answer from the broker` after `! molt i8042` | the fetch did not arrive | the relay's terminal: no connection means the ARP for `10.0.2.4` went unanswered (step 0's second address); a connection the mock refused means terminal 1 |
| `part refused: <why>` | the frame failed an install check | the mock's terminal names the fixture it sent; a mock started without `--mock` refuses every molt body |
| `unknown slot` | a typo in the slot's name | `! molt i8042`, exactly |
| `ERR: sha256 known answer` at a boot | the loader's own SHA-256 failed its test on this CPU | the boot is the seed's alone and loads no part; photograph it, it is a finding |
| `S8: part i8042 bad hash` or `bad header` | the door refused the stored part: a torn write or a changed disk | nothing is demoted and the generic serves; `! molt i8042` fetches it again |
| the take answers `disagreements <d>` | the part and the generic decoded some input differently, probably the discard limit (step 4) | the chart holds the `molt: i8042 disagree …` lines (the event pair each time). **`! molt i8042` fetches the same build again**, and an install restarts its shadow counts from 0: three more shadow boots, typed more gently |
| `S8: recovery i8042 unhealthy` during boots 2–4 | two part-loading boots in a row were powered off before `S8: healthy` | `good` is demoted. `! molt i8042` fetches it again (the mock must be serving `good`); the counts start from 0 |
| **`S8: recovery i8042 watchdog` on a boot where `good` was loaded** (boots 2 to 5, or 7) | the watchdog fired with `good` in shadow or live, which is not expected. The likeliest cause on the metal is the pet's outside check: a PS/2 timeout or parity error leaves bit 6 or 7 of the status byte set until the next byte arrives, and an idle human lets the deadline pass. The other causes are a ring overflow and a hang in the seed | keep the chart and photograph the screen. `good` is demoted: **stop the day there** and bring the chart to Cowork before going on. `! molt undo` returns `good` to shadow, with its counts starting again from 0 |
| **The HP stops at its own firmware screen after a reset**: a message about an unexpected restart, waiting for a key | the HP's firmware noticed the watchdog's reset and wants acknowledging | photograph it, then press the key the screen asks for to continue. **Never Esc or a menu key.** Let the stick boot. It is a finding; the next GermOS boot reads the evidence bit as usual |
| `S8: watchdog none` | no Intel LPC bridge at 00:1f.0, or PMBASE 0 | the boot goes on unguarded; a finding. Boot 9 then needs the power button, as the `tco locked` path |
| `S8: watchdog tco locked` | `NO_REBOOT` read back set: the firmware or the strap holds it | unguarded, decision 5's fallback; step 10's third path |
| `hold Esc` never appears on a part boot | no slot is in shadow or live, or a recovery ran first | the lines before it say which |
| `S8: recovery owner` on a boot where Esc was not meant | a key held through the window, or a stuck Esc | nothing is demoted; the next boot runs as before |
| boot 5 prints the `i8042:` pair, not the part's | the part did not load live | the line before it: `bad hash`, a recovery, or Esc |
| `ERR: exception <v> in part i8042 +0x…` | the part faulted: not expected from `good` or `hang` | wait: the watchdog resets it, and the next boot demotes it. Photograph the line |
| `ERR: exception <v> in seed` | the seed faulted with a part loaded | wait for the reset; the line and the chart are the finding |

## What the twin could not prove

Said plainly, so the day's first surprise is not a surprise:

- **The Q77's TCO.** The twin's ICH9 was measured at item 2: `NO_REBOOT` clear, `TCO_EN` sticking both ways, `TCO_LOCK` 0, the timer stopped until the guest reloads it, and the evidence surviving 14 resets. None of that is a promise about AMI's firmware on the HP. It may set `NO_REBOOT` by strap (`tco locked`), set `TCO_LOCK` (the SMM path), clear the evidence at POST (A4's path), or start the timer itself. Since the A6 review the loader halts the timer at every boot with a molt note, before its known answer, so a timer left running by an earlier boot cannot reset a boot that arms nothing. Every one of these is a line on the chart and a finding of the ring.
- **The deadline on silicon.** The datasheet says the clock is "approximately 0.6 seconds". The twin gave exactly 0.6 s. The HP's number is step 10's reading.
- **Esc on a real keyboard.** The twin's keyboard never repeats, its make arrives within 1 ms of the window's line, and it is translated set 1. The HP's keyboard repeats (repeats are makes, and the rule accepts them) and its timing is a human's. Its firmware opens a menu on Esc at power-on, which is why step 6 waits for the words on the screen.
- **`good`'s `init` on the HP's controller.** It is the seed's cold init packaged as a part: both ports off and drained around the self-test (ring 7c item 15), the command byte, the mouse reset. The seed's own copy has run on the HP since 18 September; the part's copy never has. Boot 5 is its first time.
- **Shadow on a human's input.** The synthetic human types at a fixed gap, with no Shift across an Enter, and moves the mouse at 5 ms a move. A human's typing can meet the discard limit (step 4). A real mouse's packets carry real sign and overflow bits. The generic and the part decode them with the same code, so a disagreement would be a finding.
- **The rates in human time.** The threshold of 1,000 bytes and 5,000 packets was sized against D4's twin rates. How long a human takes to earn it is the day's number.
- **The HP's identity in the request.** The twin sends `cpu 000306a9 pci 8086:2918:02`. The HP sends its own CPU and its Q77's LPC bridge, and the mock accepts any well-formed identity. Ring 8b's germline keys parts on it.
