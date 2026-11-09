# HP-8b.md: the HP's day for ring 8b, the first molt

**Stage 8 ring 8b, test 5. The owner's document, not frozen, not a criterion.**
CC never runs the flash, never names a device path in a command and never runs
the sudo block. Those are the owner's hand.

**What the day proves.** The part grown for the HP passes its threshold in
shadow on real typing and a real mouse, runs live after a reboot, and comes
through probation. **His word closes the ring.**

**Your hands on the HP:** one press of the power button, then the keys and the
mouse, as much or as little as you like. You read nothing on the HP. On mlrig
you start one program and type one word, `take`. Cowork reads
`stage8/out/hp-8b.log`. About 30 minutes, an estimate from ring 8a's day.

## Before the HP is touched

**1. The policy check and the grow.** Cowork re-checks the policy that day, and
CC then runs the grow on your word, on mlrig, with no API key. Its output is in
`stage8/out/grow-8b.log`.

- **If it ends `verdict: the generic stays`: no flash and no boots.** The finding is recorded, and you choose between amending the plan and another slot.
- **If it ends `verdict: beats`:** go on.

**2. The stick, once.** Plug the stick into mlrig, nothing else on USB storage,
and run this at the repo root. Give your sudo password and press `y` when it
names the stick. Move the stick to the HP when it says DONE.

```bash
./trials/hp-stick.sh
```

**3. The second address on mlrig, one block.**

```bash
sudo nmcli con mod ETH_UUID +ipv4.addresses 10.0.2.4/24
sudo nmcli con up ETH_UUID
sudo ufw status | grep -qw active && sudo ufw allow in on eno2 from 10.0.2.15 to 10.0.2.4 port 9999 proto tcp comment germos-hp
ip -4 addr show eno2
```

The `con up` drops mlrig's LAN for a moment. The last line must list both
`192.168.1.107/24` and `10.0.2.4/24`. If `eno2` turns out to be unmanaged, use
`sudo ip addr add 10.0.2.4/24 dev eno2` instead of the first two lines.

**4. The cables, all still in place from ring 8t:** the null-modem cable from
COM A to the USB-to-serial adapter on mlrig, the PS/2 keyboard and mouse, the
monitor and the Ethernet in the home switch. Boot 1 fetches over it.

## The day: one command, before the power button

Run this on mlrig, at the repo root:

```bash
python3 stage8/hp-day.py /dev/ttyUSB0
```

It checks the adapter, the second address, the free ports, the build against
the record's last seed, and that the germline holds the part. If anything is
wrong it says so in one plain line and starts nothing.

When it says **please press the HP's power button now**, press it once. Then use
the keys and mouse freely. The program sends every order and tells you in its
own terminal what is happening.

| Boot | Name | What the program waits for |
|---|---|---|
| 1 | fetch | The part installed in shadow, then a restart |
| 2 | shadow 1 | The health mark, about a minute, then a restart |
| 3 | shadow 2 | The same |
| 4 | shadow 3 | 1,000 key bytes and 5,000 mouse packets in all, and the health mark |
| 5 | live 1 | The health mark, at least one key and one mouse move, then a restart |
| 6 | live 2 | The same |
| 7 | live 3 | The health mark. The table says `probation 3/3` |

**The one word.** On boot 4 the program stops and asks. Stop typing on the HP,
and type `take` in its terminal and press Enter. The part goes live at the next
boot. The rest needs nothing from you but the keys.

Before each restart the HP's screen says `restarting in 3 s`, so a word
mid-typing is not a surprise.

## If something goes otherwise

The program does this itself, and says so in its terminal and in the log:

- **Esc held at power-on:** nothing is demoted. It restarts and carries on.
- **A disagreement, an `ERR:` line or any recovery but Esc:** it stops sending and leaves the services up. Tell Cowork, who reads the log, and you decide.
- **The restart does not take:** it asks you to press the power button, and carries on from the chart.
- **A hang or fault on a live boot:** the floor proven at ring 8a takes it, and the finding is recorded.

Ctrl-C ends the program and stops its services at any time.

## At the end

The program prints the table and stops the services. The ring's closing word is
yours. That day, the chart, the verdict and any photographs go into `history/`,
the record goes into HANDOVER, and the push is yours.
