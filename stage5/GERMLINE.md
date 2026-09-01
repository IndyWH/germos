# GERMLINE.md — the grow wire, the loader, and the germline

**Stage 5, plan item 1. Frozen behind the hook from item 8.** The assembler
and the test component implement this document; the broker, the rehearsal
and the acceptance checker parse by it. One text, five readers. If it is
wrong, that is a spec question for the owner, not an edit.

`stage4/UMBILICAL.md` is frozen and untouched. Everything it defines — the
cage, the addressing, the frame (a `u32` little-endian length, then that
many bytes), the connection, the timers, the no-answer rule, the working
indicator, the mock's canned answers to questions, the record — stands as
written, and this document only adds to it. A **question** rides exactly
as before. This document adds the **request**: a line that asks Claude to
grow something, the binary **component frame** that comes back, the
**entry contract** and **service table** a component is born into, the
**rehearsal** every component survives first, and the **germline** that
remembers what passed. Everything a reader needs to check it with `xxd`
and `struct` is here.

## What is a question, what is a request

On Enter, the line as it stands (backspaces applied, at most 500 bytes) is
read like this:

1. Leading spaces are skipped.
2. If the first remaining byte is **`?`** (`0x3F`) the line is a
   **question**; if it is **`!`** (`0x21`) the line is a **request**;
   otherwise the line is a **note** and takes Stage 3's path unchanged (an
   empty line is not a note).
3. The **body** is every byte after the marker with leading and trailing
   spaces removed. So `? ping`, `?ping`, `?   ping  ` and ` ? ping` all ask
   `ping`; `! make me a clock` and `!make me a clock` both request `make
   me a clock`.
4. A body longer than the wire's maximum — 498 bytes for a question, 497
   for a request — is cut at the maximum.
5. An **empty body** sends nothing and draws, on the console only, exactly
   **`nothing to ask`** (for `?`) or **`nothing to grow`** (for `!`) on its
   own line, then a fresh prompt.

A marker line is **never** written to the notebook. A note that merely
contains `?` or `!` later in the line is still a note. This section
supersedes UMBILICAL.md's "What is a question" for Stage 5 binaries: the
`? ` form that document describes gives byte-identical wire traffic under
this rule, and its "note" cases (`?` alone, `?x`) become a question of
nothing and a question of `x`. The first user typed `?` without the space
and the line went silently to the notebook; that is why.

The serial echo contract is Stage 2's, still: after `keyboard ready` the
wire carries the typed bytes and the CRLF that Enter echoes, and nothing
else. No indicator, no answer, no refusal, no console line above ever
reaches serial — and, below, nothing a running component does either.

## The grow request

One TCP connection per request, exactly as for a question (UMBILICAL.md,
"The conversation"). The request frame is UMBILICAL.md's request frame —
`N` from 1 to 498, then `N` bytes — whose **first byte is `0x01`**,
followed by the body: 1 to 497 bytes, every one `0x20` to `0x7E`.

| Offset | Size | Value |
|---|---|---|
| 0 | 4 | `u32 N` = 1 + the body length |
| 4 | 1 | `0x01` — the grow marker |
| 5 | `N−1` | the body, printable ASCII |

The marker byte is deliberately **not printable**. A question's text may be
any printable bytes, so a printable marker (`!`, say) would make a question
beginning with it unaskable; `0x01` can never be typed and never collides.
A broker that knows only UMBILICAL.md rejects such a frame as not printable
— which is right: a Stage 4 broker cannot grow.

A frame whose first byte is not `0x01` is a question and is answered per
UMBILICAL.md.

## The grow response

Exactly one response frame per connection, then the broker closes. `N` is
the number of bytes that follow the prefix; the **first of them is the
kind**.

### A refusal — kind `0x00`

| Offset | Size | Value |
|---|---|---|
| 0 | 4 | `u32 N` = 1 + the text length |
| 4 | 1 | `0x00` |
| 5 | `N−1` | the text: 0 to 4096 bytes, each `0x20`–`0x7E` or `0x0A` |

Drawn exactly as a question's answer is drawn (UMBILICAL.md, "What the
screen shows"): from column 0, LF a new line, wrapping at the right edge,
then the prompt.

### A component — kind `0x01`

| Offset | Size | Value |
|---|---|---|
| 0 | 4 | `u32 N` = 32 + `L` |
| 4 | 1 | `0x01` |
| 5 | 3 | zero |
| 8 | 4 | `u32` ABI version, **`1`** |
| 12 | 4 | `u32 L`, the blob length, **1 to 1,048,576** |
| 16 | 20 | zero, reserved |
| 36 | `L` | the blob — the component's bytes, its first instruction first |

The kind byte and the 31 bytes after it are the **32-byte header**: the
blob begins at byte 32 of the frame's content, byte 36 of the frame. A
component frame that says otherwise — kind unknown, bytes 5–7 or 16–35 not
zero, ABI not 1, `L` zero or above the cap, or `N ≠ 32 + L` — is not run:
the guest draws **`bad component frame`** on its own line, then the
prompt.

### The limits, and the deadline

A response whose `N` is above **`32 + 1,048,576`** is invalid: the guest
reports no answer (UMBILICAL.md, "No answer"), as it does for a question
whose `N` is above 4096. The guest allows **600 s** from the request being
acknowledged for the whole response to arrive — not the 150 s of a
question — because a grow is a generation and a rehearsal, with one retry;
the working indicator turns throughout. The no-answer rule and its console
text are otherwise UMBILICAL.md's, unchanged.

## The component region, and line twelve

The guest keeps a fixed **component region** of `0x100040` bytes in its own
image, page-aligned. A grow response is received straight into it: the
stream begins at region + 28, so the 4-byte length prefix occupies bytes
+28 to +31, the kind byte and the header +32 to +63, and the blob begins
at **region + 64**, 64-byte aligned. The largest legal frame (4 + 32 +
1,048,576 bytes) ends exactly at **region + `0x100040`**, the region's last
byte.

The guest reports where a component will live as serial line twelve of
thirteen, between `S5: nic <mac>` and `S5: keyboard ready`:

```
S5: component region 0x<16 lowercase hex digits> 1048576 bytes
```

The address is region + 64 — the address the component's first
instruction will have — as exactly sixteen hex digits, so it is non-zero,
below `0x100000000`, and `≡ 64 mod 4096`; the number is the cap. The
address differs between builds; a component never assumes it.

## The entry contract

The guest **`call`s the blob's first byte**. At entry:

- 64-bit long mode, ring 0, on the guest's identity map; the whole machine
  is in reach, which is the point and the danger — the rehearsal below is
  what makes it affordable.
- **`RDI` = the address of the service table** (next section). No other
  register carries anything.
- The direction flag is clear; interrupts are **enabled** (the keyboard
  interrupt keeps buffering); `RSP` was 16-byte aligned before the
  `call`, so at entry `RSP + 8` is 16-byte aligned. The stack is the
  guest's own, 16 KB; a component should use under 4 KB of it.
- The framebuffer has just been cleared to the console background; nothing
  is on screen.

The component **returns with `ret`**, `RSP` as it found it. It may clobber
every other register; `RAX` on return is ignored. It:

- is **position-independent**: assembled `bits 64`, `default rel`, with no
  absolute address of its own (its load address is fixed per build and
  told only by line twelve);
- may keep writable data inside itself — the region is ordinary RAM;
- may use port I/O — a clock reads the CMOS RTC at `0x70`/`0x71` itself;
- touches **nothing else the guest owns**: no serial port, no framebuffer
  except through `draw_text`, no keyboard ports, no PIC, no notebook, no
  network, no interrupt table, no page tables;
- honours **Esc**: when `poll_key` returns `0x1B` it returns promptly. A
  component that never returns is a hang — the rehearsal exists to catch
  it in the twin first.

## The service table

`RDI` points at this, in the guest's own memory:

| Offset | Size | Value |
|---|---|---|
| 0 | 4 | `u32` ABI version, `1` |
| 4 | 4 | `u32` table size in bytes, `40` |
| 8 | 8 | address of `draw_text` |
| 16 | 8 | address of `console_size` |
| 24 | 8 | address of `poll_key` |
| 32 | 8 | address of `ticks_ms` |

**Calling a service:** arguments in `RDI`, `RSI`, `RDX`, `RCX` in that
order; the result in `RAX`. A service preserves `RBX`, `RBP`, `RSP` and
`R12`–`R15` and may clobber `RAX`, `RCX`, `RDX`, `RSI`, `RDI` and
`R8`–`R11`. No stack alignment is required. The direction flag is clear
on entry and on return.

- **`draw_text(row, col, ptr, len)`** — `RDI` = row, `RSI` = column,
  `RDX` = the bytes, `RCX` = how many. Draws each byte in the next cell
  along the row, from the shared font (`stage2/font8x8.bin`, 16x16 cells)
  in the two console colours, and stops at the right edge. A row or column
  outside the console draws nothing. A byte outside `0x20`–`0x7E` draws as
  a space. **Pixels only:** the console's text shadow is not touched. No
  result.
- **`console_size()`** — `RAX` = `cols | (rows << 32)`: the console's
  cells across and down.
- **`poll_key()`** — `RAX` = the next key as one ASCII byte, with Shift
  applied — the printables, `13` Enter, `8` Backspace, **`0x1B` Esc** — or
  `0` if no key is waiting. A key a component takes is not echoed to serial
  and never reaches the prompt.
- **`ticks_ms()`** — `RAX` = milliseconds since boot as a `u64`,
  monotonic, from the time-stamp counter calibrated once at boot against
  the PIT.

Exactly these four. A component that wants a clear screen draws spaces.

## What the screen does around a component

On a valid component frame, the guest: stops the working indicator, erases
the cursor, **clears the framebuffer** to the background (the text shadow
is kept), and calls the component. When it returns, the guest **re-renders
the whole console from the shadow** — the conversation comes back exactly
as it was — discards any keys still waiting, moves to a fresh line if the
cursor is not already at column 0, and draws the prompt. The screen has one
owner throughout: the component draws only through `draw_text`, on the
same processor, in the main loop's stead.

## The lines the console can show for a request

Console only, each on its own line, then the prompt:

| Line | When |
|---|---|
| `nothing to grow` | the body was empty (`nothing to ask` for `?`) |
| `no answer from the broker` | UMBILICAL.md's rule, the 600 s deadline included |
| `bad component frame` | a component frame that fails the checks above |
| the refusal text | a refusal frame, drawn as an answer |

The broker's refusal texts are fixed phrases, so a checker can render them:

| Refusal text | When |
|---|---|
| `rehearsal failed: <phrase>` | every candidate failed rehearsal; the phrase is the last try's, from the table below |
| `mock: no canned component for: <body>` | `--mock`, and the body is not in the canned table |
| anything else | a real backend's own refusal (an assembly error, say) — printable, at most 4096 bytes |

## The rehearsal

Every candidate blob boots in the twin before it reaches the guest — a
headless, scripted boot of the **same guest image**, fed through the same
wire. The rehearsal:

1. starts a one-shot listener on a private port (**9998** by default);
2. boots the image at `-smp 2` with a fresh 16 MB notebook image and
   UMBILICAL.md's cage, its `guestfwd` delivering to that port, the monitor
   on stdio, serial to a file, all of it under `stage5/out/rehearsal/`;
3. waits for `S5: keyboard ready` (60 s), types **`! rehearsal`** and
   Enter through the monitor; the listener answers the request with the
   candidate's component frame and closes;
4. waits for the listener to report the delivery (30 s), then 3 s more,
   and takes a screendump (**B**: the component running);
5. sends Esc, waits 2 s, types **`after`** and Enter, waits 2 s, takes a
   screendump (**C**: the prompt back), and quits.

The criteria, judged in this order; the first that fires names the
failure:

| Phrase | Fires when |
|---|---|
| `the twin did not boot` | no ready line within 60 s, or not exactly thirteen `S5:` lines |
| `the component was not delivered` | the listener never saw the request, or could not send the frame |
| `the twin reported an error` | any `ERR:` in the serial capture |
| `the component did not run` | the row `> ! rehearsal`, rendered from the shared font, is still on screen in B — the loader never cleared the console and took over |
| `the component drew nothing` | B is pure background |
| `no live prompt after esc` | the row `> ! rehearsal` is not back on screen in C, the notebook image does not parse to exactly `["after"]`, or the serial echo after ready is not exactly `! rehearsal\r\nafter\r\n` |
| `the twin timed out` | the whole run took more than 90 s |

The rehearsal **passes** only if none fires. These prove *safe* — boots,
loads, runs, faults nothing, returns, the prompt lives — not *correct*;
whether the thing on the screen is the thing that was asked for is the
oracle's judgement this ring. The rehearsal log is the criteria's verdicts,
the twin's `S5:` lines, any `ERR:` line, and the timing. A rehearsal never
touches the germline; `stage5/out/rehearsal/` is scratch, wiped per run.

## The germline

A directory per proven component under the cache root (`germline/` at the
repository root by default — the machine's own cache, never repository
content; `--germline <dir>` names another).

- **The key** is the first 16 hex digits of SHA-256 over the ASCII string
  `<normalised>|abi1|<machine>`, where the **normalised** request is the
  body lowercased, every run of whitespace collapsed to one space, and
  stripped; and the **machine** this ring is the string **`qemu-q35-ovmf`**
  — the twin's identity, because the machine the user faces and the twin
  are the same guest image. At Stage 7 the string becomes the scanned
  hardware.
- The directory `<root>/<key>/` holds **`component.bin`** (the blob),
  **`provenance.json`** and **`rehearsal.log`**.
- `provenance.json` is one JSON object: `request` (the body as sent),
  `normalised`, `key`, `abi` (`1`), `machine`, `date` (ISO-8601, UTC, when
  the entry was written), `model` (the backend's name: `mock`, or
  `claude -p <cli version>` plus the `--model` if one was given), `sha256`
  (of the blob, lowercase hex), `size` (the blob length), `tries` (how many
  candidates the backend produced for this entry), and `rehearsal` — an
  object with `passed` (`true`), `phrases` (the empty list), `seconds`.

**Serving:** a request whose key has a directory is answered from
`component.bin` — after its SHA-256 is checked against the record; a
mismatch is a miss — and the generation backend is not invoked. Otherwise
the pipeline runs: generate, rehearse (retrying once with the failure
named, `--tries 2` by default), cache, deliver. A candidate that fails
every try is a `rehearsal failed:` refusal and nothing is cached.

## The mock's canned table for requests

`python3 broker/germline.py --mock` generates from this table and calls
nothing outside the repository; questions it answers from UMBILICAL.md's
table. Every lookup counts as one generation call. The rehearsal still runs,
for real, because it is what the acceptance tests judge.

| Body (exact bytes) | Candidate |
|---|---|
| `test component` | the bytes of `stage5/component.bin` |
| `big` | the bytes of `stage5/component.bin` padded with zeros to exactly 1,048,576 bytes — the cap; the padding sits after the code and never executes |
| `fault` | the two bytes `0f 0b` (`ud2`) — an invalid-opcode exception the moment it runs |
| anything else | no candidate: the refusal `mock: no canned component for: ` followed by the body |

## The broker's record for a request

With `--record <path>`, one JSON object per connection, one per line,
written when that connection ends. For a question the object is
UMBILICAL.md's. For a request:

| Field | Value |
|---|---|
| `t` | seconds since the epoch when the connection was accepted |
| `kind` | `"grow"` |
| `request` | every byte read from the connection, as lowercase hex — the prefix, the marker, the body |
| `text` | the body as a string, if the frame was valid; otherwise `null` |
| `key` | the germline key, or `null` |
| `source` | `"germline"`, `"generated"` or `"refused"` |
| `generation_calls` | the backend's running call count for this broker process, after this connection |
| `rehearsals` | a list, in order, of `"pass"` or `"fail: <phrase>"` for each candidate rehearsed on this connection |
| `answer_kind` | `"component"` or `"refusal"`, or `null` if none was sent |
| `answer_sha256` | SHA-256 of the whole response frame sent, prefix included, lowercase hex, or `null` |
| `answer` | the refusal text as a string, or `null` |
| `error` | `null`, or a short reason the connection was closed without an answer |

A checker judges `request` by this document's frame rule and `answer_sha256`
by rebuilding the frame it expects, not by the `text` and `answer` fields.

## Worked examples

**The request** `! test component`. The body is `test component`, 14
bytes; the frame is 19 bytes:

```
00000000: 0f00 0000 0174 6573 7420 636f 6d70 6f6e  .....test compon
00000010: 656e 74                                  ent
```

**A refusal**, `rehearsal failed: the twin reported an error` (44 bytes);
the frame is 49 bytes:

```
00000000: 2d00 0000 0072 6568 6561 7273 616c 2066  -....rehearsal f
00000010: 6169 6c65 643a 2074 6865 2074 7769 6e20  ailed: the twin
00000020: 7265 706f 7274 6564 2061 6e20 6572 726f  reported an erro
00000030: 72                                       r
```

**A component**, for the four-byte blob `8d 47 01 c3` (`lea eax, [rdi+1]`;
`ret`): `L` = 4, `N` = 36; the frame is 40 bytes, the blob at byte 36:

```
00000000: 2400 0000 0100 0000 0100 0000 0400 0000  $...............
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 8d47 01c3                      .....G..
```

**The largest legal component**, `L` = 1,048,576: `N` = `0x100020`, the
frame `0x100024` bytes; received at region + 28 it ends exactly at region
+ `0x100040`.

**The germline key** for `make me a clock` on this ring's machine:
`sha256("make me a clock|abi1|qemu-q35-ovmf")`, its first 16 hex digits.
`Make  me a CLOCK ` normalises to the same string and the same key.

## Parsing it cold, in Python

The broker, the rehearsal and the checker use this, and nothing more:

```python
import hashlib
import struct

ABI = 1
GROW_MARKER = 0x01
KIND_REFUSAL, KIND_COMPONENT = 0x00, 0x01
HEADER = 32                      # the kind byte and the 31 bytes after it
BLOB_MAX = 1048576
REFUSAL_MAX = 4096
BODY_MAX = 497
MACHINE = "qemu-q35-ovmf"

def is_grow(request):
    """True if a valid request frame's text is a grow request."""
    return (2 <= len(request) <= 1 + BODY_MAX and request[0] == GROW_MARKER
            and all(0x20 <= b <= 0x7E for b in request[1:]))

def grow_request(body):
    return struct.pack("<I", 1 + len(body)) + bytes([GROW_MARKER]) + body

def refusal_frame(text):
    return struct.pack("<I", 1 + len(text)) + bytes([KIND_REFUSAL]) + text

def component_frame(blob):
    body = (bytes([KIND_COMPONENT, 0, 0, 0]) + struct.pack("<II", ABI, len(blob))
            + bytes(20) + blob)
    return struct.pack("<I", len(body)) + body

def parse_response(content):
    """The bytes after the length prefix. Returns ("refusal", text) or
    ("component", blob); raises ValueError naming what was wrong."""
    if not content:
        raise ValueError("empty response")
    kind = content[0]
    if kind == KIND_REFUSAL:
        text = content[1:]
        if len(text) > REFUSAL_MAX or not all(0x20 <= b <= 0x7E or b == 0x0A for b in text):
            raise ValueError("refusal text is not printable ASCII or LF within 4096 bytes")
        return "refusal", text
    if kind == KIND_COMPONENT:
        if len(content) < HEADER:
            raise ValueError("component frame shorter than its header")
        if any(content[1:4]) or any(content[12:32]):
            raise ValueError("reserved header bytes are not zero")
        abi, length = struct.unpack_from("<II", content, 4)
        if abi != ABI:
            raise ValueError("ABI version %d, want %d" % (abi, ABI))
        if not 1 <= length <= BLOB_MAX:
            raise ValueError("blob length %d is outside 1..%d" % (length, BLOB_MAX))
        if len(content) != HEADER + length:
            raise ValueError("frame carries %d bytes, header says %d" % (len(content) - HEADER, length))
        return "component", content[HEADER:]
    raise ValueError("unknown response kind 0x%02x" % kind)

def normalise(body):
    return " ".join(body.lower().split())

def germline_key(body, machine=MACHINE):
    s = "%s|abi%d|%s" % (normalise(body), ABI, machine)
    return hashlib.sha256(s.encode("ascii")).hexdigest()[:16]
```
