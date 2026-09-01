# UMBILICAL.md — the wire between GermOS and its broker

**Stage 4, plan item 1. Frozen behind the hook from item 7.** The assembler
implements this document; the acceptance checker and the broker parse by it.
One text, three readers. If it is wrong, that is a spec question for the
owner, not an edit.

The umbilical is the smallest honest link that lets a booted machine ask a
question and print the answer: one TCP connection per question inside a
caged virtual network, carrying one length-prefixed request and one
length-prefixed response. Everything a reader needs to check it with `xxd`
and `struct` is here.

## The cage

QEMU's user-mode network (slirp) with the guest isolated, and exactly one
door. Every QEMU command in this stage carries these two arguments and no
other network option:

```
-netdev user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999
-device virtio-net-pci,netdev=n0
```

(The `-netdev` value contains a space; in a shell it is quoted whole. The
harness may add `mac=<address>` to the `-device` so it knows what the guest
must report.)

- `restrict=on`: the guest cannot reach the host, the LAN or the internet.
  A SYN to any address and port other than the door below is answered by
  slirp with a RST. Measured before this document was written.
- The door is guest address **`10.0.2.4`, TCP port `9999`**. It is `.4`
  because libslirp refuses a forward on its own virtual host `10.0.2.2` and
  DNS `10.0.2.3`; `10.0.2.4` is slirp's own default for a guest forward, on
  the guest's own subnet, and slirp answers ARP for it.
- Each guest connection to the door makes slirp run `nc -N 127.0.0.1 9999`
  and splice the connection to that process: a fresh loopback connection to
  the broker per question, the guest's close delivered to the broker as
  EOF (`-N`), the broker's close delivered to the guest as a FIN. If the
  broker is not listening, the guest's handshake completes and is followed
  at once by a RST. (The `-tcp:host:port` form of `guestfwd` is not used:
  it is one character device opened when QEMU starts, shared by every guest
  connection, and QEMU refuses to start when nothing is listening.)
- The broker listens on **`127.0.0.1:9999`** only.

## Addressing

| | |
|---|---|
| Guest IPv4 address | `10.0.2.15`, mask `/24` — slirp's fixed first address; no DHCP |
| Guest MAC | read from the virtio-net device configuration |
| The broker, as the guest sees it | `10.0.2.4:9999`, on-link |
| Gateway, DNS, routes | none used. The guest's whole world is one on-link peer; there is no route table and no default gateway |
| Broker MAC | learned by ARP at the first question, cached for the boot |

## The frame

Every message in either direction is a **frame**: a length, then that many
bytes. All integers are **little endian**, as in the notebook.

| Offset | Size | Type | Value |
|---|---|---|---|
| 0 | 4 | u32 | `N`, the number of bytes that follow |
| 4 | `N` | bytes | the text |

**Request** (guest → broker): exactly one per connection. `N` is **1 to 498**
inclusive. Every byte is printable ASCII, **0x20 to 0x7E** inclusive. The
text is the question exactly as typed after the marker (below).

**Response** (broker → guest): exactly one per connection. `N` is **0 to
4096** inclusive. Every byte is **0x20 to 0x7E** inclusive or **0x0A** (LF,
a line break). No CR, no tab, no byte above 0x7E: the broker folds or drops
anything else before it reaches the wire.

A reader that receives a length outside the range for that direction treats
the frame as invalid: the broker closes the connection; the guest reports no
answer (below).

## The conversation

1. The guest resolves `10.0.2.4` by ARP if it has not already (a broadcast
   request; up to three tries a second apart). No reply is a failed
   question, not a halt.
2. The guest opens a TCP connection from `10.0.2.15:<port>` to
   `10.0.2.4:9999`. `<port>` starts at **49152** at boot and increases by one
   per question; the initial sequence number is the low 32 bits of the
   time-stamp counter at connect. The SYN carries one option, MSS 1460, and
   advertises a 4096-byte window. The SYN is retransmitted after 1 s, five
   tries in all.
3. The guest sends the request frame in one segment, retransmitted after 1 s
   if unacknowledged, five tries in all.
4. The broker reads the request (it allows 10 s for it to arrive whole),
   answers with the response frame, and closes.
5. The guest assembles the response by its length prefix, and when the whole
   frame has arrived it closes (FIN). It does not wait for the broker's FIN
   to know the answer is complete. Either side may close first; the guest
   acknowledges whatever arrives and honours a RST from any state.
6. The guest allows **150 s** from the request being acknowledged for the
   whole response to arrive. The broker's own limit on a real answer is
   120 s, after which it responds with a short text saying so, so in normal
   life a frame always arrives inside the guest's deadline.

The guest's TCP is client-only, one connection at a time, one segment in
flight, in-order only: a segment that does not begin at the next expected
byte is dropped and the current acknowledgement repeated, and the peer
retransmits. An IPv4 or TCP segment with a bad checksum is dropped without
comment, in both directions — slirp does the same to the guest, so a wrong
checksum looks like silence.

## No answer

If any of these happens — no ARP reply, no SYN-ACK within the retries, a
RST, a FIN before the response frame is complete, a response length above
4096, or the 150 s deadline — the guest draws, on the console only, exactly:

```
no answer from the broker
```

on its own line, then a fresh prompt. Never a hang, never a halt.

## What is a question

A line typed at the prompt whose first two bytes are `?` and a space
(`0x3F 0x20`). The question is every byte after those two, verbatim, as the
line stood when Enter was pressed (backspaces applied). A line is capped at
500 bytes as in Stage 3, so a question is at most 498.

- `?` alone, or `?` followed by anything but a space, is a **note** and is
  journaled exactly as in Stage 3.
- A question of zero bytes (`? ` and nothing else) sends nothing and gives a
  fresh prompt.
- A question is **never** written to the notebook. Notes are unchanged.

The serial echo contract is Stage 2's: after `keyboard ready` the wire
carries the typed bytes and the CRLF that Enter echoes, and nothing else. No
indicator, no answer, no error text ever reaches serial.

## What the screen shows

After Enter on a question, on the console only:

1. A **working indicator** while waiting: one cell at column 0 of the fresh
   line, cycling through `-`, `\`, `|`, `/` about four times a second. It is
   erased before anything else is drawn.
2. The answer, from column 0: bytes 0x20–0x7E drawn in order, LF starting a
   new line at column 0, lines longer than the console wrapping at its right
   edge. An empty answer draws nothing. Then the prompt on the next line.
3. Or, on failure, the no-answer line above, then the prompt.

Keys pressed while the indicator is turning are discarded when it stops.

## The mock's canned table

`python3 broker/broker.py --mock` answers from this table and makes no other
call of any kind. The acceptance tests use only the mock.

| Question (exact bytes) | Answer (exact bytes; `\n` is 0x0A) |
|---|---|
| `ping` | `pong` |
| `hello` | `hello from the mock broker\nask me something true at test 5` |
| anything else | `mock: no canned answer for: ` followed by the question |

## The broker's record

With `--record <path>`, the broker appends one JSON object per accepted
connection, one per line, written when that connection ends:

| Field | Value |
|---|---|
| `t` | seconds since the epoch when the connection was accepted (number) |
| `request` | every byte read from the connection, as lowercase hex — the 4-byte length and then the text, or whatever arrived before the failure |
| `question` | the request text as a string, if the frame was valid; otherwise `null` |
| `answer` | the response text sent, if any; otherwise `null` |
| `error` | `null`, or a short reason the connection was closed without an answer |

A checker judges `request` by this document's own frame rule, not by the
`question` field.

## Worked example

The harness types `? ping` and Enter. The guest connects and sends this
request frame — 8 bytes:

```
00000000: 0400 0000 7069 6e67                      ....ping
```

The mock answers with this response frame — 8 bytes — and closes:

```
00000000: 0400 0000 706f 6e67                      ....pong
```

For `? hello` the request is 9 bytes, `0500 0000 6865 6c6c 6f`, and the
response is 4 + 58 bytes:

```
00000000: 3a00 0000 6865 6c6c 6f20 6672 6f6d 2074  :...hello from t
00000010: 6865 206d 6f63 6b20 6272 6f6b 6572 0a61  he mock broker.a
00000020: 736b 206d 6520 736f 6d65 7468 696e 6720  sk me something 
00000030: 7472 7565 2061 7420 7465 7374 2035       true at test 5
```

The record after both, with the timestamps elided:

```
{"t": ..., "request": "0400000070696e67", "question": "ping", "answer": "pong", "error": null}
{"t": ..., "request": "0500000068656c6c6f", "question": "hello", "answer": "hello from the mock broker\nask me something true at test 5", "error": null}
```

## Parsing it cold, in Python

The broker's reader and the checker's judge are this, and nothing more:

```python
import struct

REQUEST_MAX, RESPONSE_MAX = 498, 4096

def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ValueError("connection closed after %d of %d bytes" % (len(data), n))
        data += chunk
    return data

def read_frame(sock, limit):
    n, = struct.unpack("<I", recv_exact(sock, 4))
    if n > limit:
        raise ValueError("frame of %d bytes exceeds %d" % (n, limit))
    return recv_exact(sock, n)

def valid_request(text):
    return 1 <= len(text) <= REQUEST_MAX and all(0x20 <= b <= 0x7E for b in text)

def valid_response(text):
    return len(text) <= RESPONSE_MAX and all(0x20 <= b <= 0x7E or b == 0x0A for b in text)

def frame(text):
    return struct.pack("<I", len(text)) + text
```
