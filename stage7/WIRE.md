# WIRE.md — the NIC the metal has, and the relay in front of the broker

**Stage 7 ring 7b, plan item 2. Frozen behind the hook from item 8.** The
assembler prints the lines this document names, the relay keeps the contract
it states, and the acceptance checker parses by both; one text, three
readers. If it is wrong, that is a spec question for the owner, not an edit.

`stage4/UMBILICAL.md` stands: the frame, the conversation, the no-answer
rule, the cage inside the twin and the broker's bind are unchanged. This
document supersedes exactly two of its sentences for Stage 7 — "Guest MAC:
read from the virtio-net device configuration" (below, the MAC is read from
whichever NIC the machine chose) and "every QEMU command in this stage
carries these two arguments" (below, the twin's NIC is an e1000e, and the
twin may carry two cages).

## The NIC

The patient's NIC is an Intel 82579LM (PCI `8086:1502`); the twin's is
QEMU's `e1000e`, an 82574L (`8086:10d3`). Both are found by **vendor
`0x8086` and class `0x0200`** with the device id in a table of three:
`0x10D3`, `0x1502`, `0x1503`. The virtio-net driver stays in the binary
beside the e1000e driver; **when both devices are present the e1000e is
chosen**, by kind, whatever their slot order. Neither device found is a
named error before the keyboard.

The driver, per the 82574 datasheet — the register set the 82579LM shares:
the function owned (memory, bus mastering, INTx off) **before** BAR0 is
read; BAR0 — a 128 KB memory region, wherever the firmware put it — mapped
uncached; interrupts masked (`IMC`), a software reset (`CTRL.RST`) awaited,
interrupts masked again and `ICR` read once, so nothing left by a firmware
driver is trusted; the MAC read from `RAL0`/`RAH0` with `RAH0.AV` required;
`CTRL.SLU` set with the forced speed and duplex, `ILOS` and `PHY_RST`
cleared, and **`STATUS.LU` awaited for at most ten seconds**; sixteen legacy
receive descriptors over 2048-byte buffers (`RCTL.BSIZE` 2048, `LPE` clear,
`BAM` set, `SECRC` set, no promiscuity; `RFCTL.EXSTEN` clear and `MRQC` 0:
legacy descriptors, one queue) and eight legacy transmit descriptors (`RS`
set on every frame, `IFCS` so the device appends the CRC), each ring in its
own page; polled, never interrupting. A received descriptor whose **errors
byte is non-zero is recycled, counted as taken, and never dispatched**. The
`MDIC` and the EEPROM are not touched. Frames are what they were on
virtio-net: an Ethernet frame without its CRC, at most 1514 bytes, no VLAN,
no offloads; the guest computes its own checksums.

## The serial lines

Ring 7a's lines, with one more after the nic line on the e1000e path:

```
S7: nic 6c:3b:e5:3b:86:45
S7: link up
```

`S7: nic <mac>` prints the six bytes of `RAL0`/`RAH0` (device configuration
on the virtio-net path), lowercase hex, colon separated. **`S7: link up`
follows only on the e1000e path**; the virtio-net path prints no link
line, so ring 7a's frozen gate keeps its eighteen and seventeen lines on
the same binary. A boot that formats a blank disk prints **nineteen**
`S7:` lines on the e1000e; a boot that recognises the disk prints
**eighteen**: alive, edid, gop, boot services exited, gdt and paging ours,
idt ready, cores found, cores woken, console, [gpt written], disk,
notebook, home, **nic, link up**, component region, obs page, glass core,
keyboard ready.

The named errors, every one halting the machine before `keyboard ready`:

| Line | When |
|---|---|
| `ERR: no network device on PCI bus 0 (e1000e or virtio-net)` | neither NIC found by the scan |
| `ERR: nic BAR0 is not a memory BAR` | BAR0's low bit set |
| `ERR: nic did not complete its reset` | `CTRL.RST` still set after one second |
| `ERR: nic has no address in RAL/RAH` | `RAH0.AV` clear after the reset |
| `ERR: nic link did not come up within 10 s` | `STATUS.LU` clear after the ten-second wait |
| `ERR: nic transmit timed out` | a transmit descriptor's `DD` not set within five seconds |

A link that drops after `keyboard ready` is not watched: the next question
fails by UMBILICAL.md's no-answer rule, never a halt.

## The relay

On the metal the guest keeps its frozen addressing — `10.0.2.15/24`, the
broker at `10.0.2.4:9999`, no gateway, no route — and ARPs for `10.0.2.4`
on the LAN; mlrig's LAN port carries `10.0.2.4/24` as a second address and
answers. **`broker/relay.py`** (not frozen: a tool, held to this contract
by the checker) is what listens there:

- It binds **exactly `10.0.2.4` or `127.0.0.1`** and nothing else. Any
  other `--bind` is refused **before any socket exists**, with
  `relay: refusing to bind <addr> - only 10.0.2.4 (the switch) or
  127.0.0.1 (the twin)` on stderr and exit status 2. Its defaults are
  `10.0.2.4` and port 9999 (the HP's day: `python3 broker/relay.py` with
  no flags). In the twin it is `python3 broker/relay.py --bind 127.0.0.1
  --port 9997`.
- It sets `SO_REUSEADDR` before its bind, as the broker does, so a port in
  TIME_WAIT between two runs of the gate does not refuse it. A bind the
  host refuses is a loud exit, never a shared port.
- Once bound it prints `relay listening on <addr>:<port> ->
  127.0.0.1:<broker-port>` on stdout, the line a harness waits for.
- **Each accepted connection is forwarded to the frozen broker on
  `127.0.0.1:<broker-port>`** (default 9999), one connection at a time,
  bytes copied both ways unchanged: the guest's close reaches the broker
  as end-of-file, the broker's close reaches the guest as a FIN — what
  `nc -N` alone did inside the twin. When the broker refuses the
  connection, the guest's side is closed at once; **whether the guest then
  sees a RST or a FIN depends on whether its request had been read, and
  both are "no answer from the broker"** by UMBILICAL.md's rule. Nothing
  here may be tightened into a criterion.
- Every `shutdown` and `close` on a socket whose peer has gone is
  swallowed: the teardown never raises, and the log line is always
  written.
- With `--log <path>` it appends **one JSON line per connection, written
  and flushed the moment the connection ends**:

| Field | Value |
|---|---|
| `t` | seconds since the epoch when the connection was accepted (number) |
| `peer` | the accepting side's peer, `"<addr>:<port>"` |
| `up` | bytes copied from the guest's side to the broker (number) |
| `down` | bytes copied from the broker to the guest's side (number) |
| `error` | `null`, or a short reason — `"broker refused: <reason>"` when the broker could not be reached |

A checker reads the log by these fields and nothing else: for a question
`up` is the request frame's length and `down` the response frame's; the
guest's own byte counters on the obs page count Ethernet bytes and are
therefore never less than these.

## The twin

The gate's own machine carries one cage with the e1000e:

```
-netdev user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9997
-device e1000e,netdev=n0,mac=6c:3b:e5:3b:86:45
```

with the relay on `127.0.0.1:9997` forwarding to the broker on 9999. The
rehearsal twin keeps the frozen `broker/twin.py` command — the virtio-net
on `n0`, its `guestfwd` to the twin's listener on 9998 — and gains, through
the frozen `extra_args` seam, a second cage of the same shape and the
e1000e on it:

```
-netdev user,id=n1,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9998
-device e1000e,netdev=n1,mac=6c:3b:e5:3b:86:45
```

Both cages are `restrict=on` with exactly one `guestfwd` landing on
`127.0.0.1`; the guest chooses the e1000e and reaches the listener through
it. The ports: **9999** the broker, **9998** the rehearsal listener, **9997**
the relay. The gate refuses to run while any of the three is held (a
connect probe, so a port in TIME_WAIT is free). The guest's MAC in the
twin is the HP's, so the nic line the twin prints is the one the metal
must print.
