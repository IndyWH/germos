# Stage 4 — implementation plan

**To be committed verbatim as `stage4/plan.md`. Produced in plan mode, per the
foundation's build loop. Nothing below is implemented until Wajira approves
this document by writing the approval marker from his own terminal; the
ExitPlanMode hook holds the gate until then. Plan mode allows this session to
write only this one file, so the copy to `stage4/plan.md` and its commit are
the first act after the gate opens — item 0 below — before any other file is
touched.**

## Context

Stage 3 is closed: on the morning of 1 September 2026 Wajira booted the
machine windowed and it remembered his note. Stage 4 gives GermOS its brain's
phone line — the foundation's *umbilical*: a virtio-net driver on the modern
interface, a deliberately minimal TCP/IP stack, and a broker on mlrig that
relays a typed question to Claude and returns the answer to the machine's own
screen. The done-when, from the foundation: **the booted OS asks Claude a
question and prints the answer.** You type `? ` and a question at the prompt;
the answer appears on the console above a fresh prompt.

`stage4/spec.md` is approved and fixes the behavioural order, the new serial
line, five acceptance tests, the cleared policy gate, and the owner's three
decisions: plaintext inside the cage this ring with TLS living in the broker
(the pre-built TLS blob joins the guest at the ring where its traffic first
touches a real wire), the `? ` question marker, and the recorded omission list
— DHCP, DNS, UDP, IPv6 and congestion control are all out, each a decision.
Two owner decisions were taken at the opening and are in `HANDOVER.md`: Fable
5 at high effort implements this stage, and the subscription policy re-check
passed (`claude -p` still draws from the Max subscription; the June 2026
credit-pool change is paused; re-check again at Stage 5).

The plan is **evaluation-first**, as Stages 1–3 were. Items 1–6 write the
protocol document, the broker with its mock, and the acceptance machinery so
tests 1–4 exist and fail before a single instruction of `stage4.asm` is
written. Item 7 freezes them. Items 8–14 grow the implementation on Stage 3's
proven body, and the gate closes at item 14. Test 5 is Wajira's eyeball with
the real broker running and stays manual.

**The safety shape, restated.** Everything runs inside QEMU. The twin's
network is slirp's user-mode stack with `restrict=on`: the guest can reach
nothing — not the LAN, not the internet, not mlrig's services — except one
forwarded socket that lands on the broker at `127.0.0.1:9999`. That was not
taken on trust: it was measured (below), by sending raw frames into slirp from
the host and watching every other destination get a reset. The broker binds
only `127.0.0.1`. The storage bodyguard stays exactly as it is; the only disks
are raw files under `stage4/out/`. The automated gate uses only the mock
broker and never spends a token or needs the internet; the real backend is
exercised by Wajira alone, at test 5.

### Environment, verified in this session before planning

No new packages. NASM 3.01, QEMU 10.2.1 with libslirp 4.9.1, Python 3.14,
OVMF, mtools, OpenBSD netcat 1.234 (`/usr/bin/nc`, stock Ubuntu), and the
`claude` CLI 2.1.252 on the PATH. Every probe used scratch files under
`stage4/out/` (gitignored, not committed) and a throwaway loopback port
(9911); the host end was always `127.0.0.1`.

The method for the network probes deserves a line, because it is how the
cage was proven **before any guest code exists**: QEMU was started with no
disk and no guest NIC at all, its slirp netdev and a `dgram` netdev joined on
one hub, and a Python script (`stage4/out/wire.py`, scratch) sent Ethernet
frames into the hub as if it were the guest — ARP, IPv4, TCP with real
checksums — and read slirp's replies back. That script is also the working
reference for what `stage4.asm` will do by hand.

| Fact | Verified how |
|---|---|
| A `-device virtio-net-pci,netdev=n0` on q35 presents a **transitional** virtio-net: vendor `1af4`, device `1000`, subsystem `1af4:0001`, at **bus 0 device 2 function 0** — *ahead of* the disk, which stays at device 3. Stage 3's image still boots to `S3: keyboard ready` with the NIC attached: its driver matches by device ID and reads the BAR at runtime, so the new neighbour cost it nothing | `info pci`, `info qtree`, and the serial log of a Stage 3 boot with the NIC attached |
| Its BARs after OVMF: BAR0 I/O at `0x60E0` (legacy), BAR1 32-bit MMIO at `0x81082000` (MSI-X), **BAR4 64-bit prefetchable at `0xC000000000`**, 16 KB — the modern capability region. The disk's BAR4 has moved to **`0xC000004000`**. Both sit in the same 2 MB page, 768 GB up: `map_mmio_2m` covers both with the two spare pages it already spends | the same `info pci` |
| The device offers the QEMU defaults: `csum`, `guest_csum`, `mrg_rxbuf`, `ctrl_vq`, `status`, `indirect_desc`, `event_idx`, TSO/UFO, `any_layout` — all on. This driver accepts only `VIRTIO_NET_F_MAC` and `VERSION_1` | `info qtree` |
| The default MAC is `52:54:00:12:34:56`; `mac=` on the `-device` sets another | `info network`, QEMU docs |
| **libslirp refuses a guestfwd whose guest address is the virtual host `10.0.2.2`** (or the DNS `10.0.2.3`): `Conflicting/invalid host:port in guest forwarding rule`. The spec's `tcp:10.0.2.2:9999` cannot be typed into QEMU as written. slirp's own default guestfwd address is **`10.0.2.4`**, and it answers ARP for it (`52:55:0a:00:02:04`) | QEMU's own error; ARP over the hub |
| **The spec's `-tcp:127.0.0.1:9999` target is a character device, opened once at QEMU startup.** With nothing listening QEMU refuses to start (`Failed to connect ... Could not open guest forwarding device`). With a listener, the host sees one connection at 0.6 s — before any guest frame — shared by every guest connection for the life of the VM, and a guest FIN is never reciprocated. So neither one-connection-per-question nor the spec's mock-down run is possible with that form | probes A, B and S1 |
| **`guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9911`** gives one fresh host connection per guest connection, data both ways, and the guest's FIN reaches the broker as EOF. **Broker down: the handshake completes, then slirp sends RST at once** — a prompt, honest failure. QEMU starts either way | probes S2, S2-down, close probes |
| A broker that answers and closes delivers its bytes at once; slirp's FIN follows only after the guest closes (netcat exits when both sides are done). The guest therefore treats a response as complete by its **length prefix**, then closes, and slirp's FIN arrives immediately | close probes, all three variants |
| **The cage holds.** With `restrict=on`, a SYN to `10.0.2.2:22`, to `10.0.2.3:53`, to an un-forwarded port on `10.0.2.4`, to `127.0.0.1:9911` and to `1.1.1.1:80` each got an immediate RST; ARP is answered only for `.2`, `.3` and the forwarded `.4` | probe CAGE |
| **slirp enforces both checksums.** A SYN with a corrupted TCP checksum, or a corrupted IPv4 header checksum, gets no reply at all; the same SYN with good checksums gets SYN-ACK | probe csum |
| `sendkey shift-slash` reaches the guest as the slash scancode with Shift's make and break around it: Stage 3's unshifted map echoed `/ pinga` for `shift-slash spc p i n g shift-a`. The `? ` marker needs a shifted map | Stage 3 boot via the monitor |
| `claude -p` takes `--output-format text`, `--tools ""` (no tools), `--no-session-persistence`, `--system-prompt`, `--model`, and `--bare` (skips hooks and CLAUDE.md auto-discovery) | `claude --help`; no call was made |
| The bodyguard allows the planned commands: the Stage 4 QEMU line with `-netdev user,...,guestfwd=...-cmd:nc -N 127.0.0.1 9999` and `-device virtio-net-pci,...`, `broker.py --mock ...`, `./stage4/test.sh`, the checker | the hook run directly on each payload, exit 0 |

---

## Deviations from the spec, for approval

Three, each forced by a measured fact or argued from one. Everything else is
the spec as written.

1. **The broker's guest-side address is `10.0.2.4`, not `10.0.2.2`.**
   libslirp rejects a guestfwd on the virtual host's own address. `10.0.2.4`
   is slirp's default for exactly this purpose and is on the guest's own
   /24, so the guest ARPs for the broker directly — no gateway, no route. The
   cage is unchanged: one address, one port.
2. **The guestfwd's host side is `cmd:nc -N 127.0.0.1 9999`, not
   `tcp:127.0.0.1:9999`.** The literal form is a single chardev opened at
   QEMU start: the broker must be up before the machine boots, every
   question shares one host connection, and the mock-down run cannot exist
   because QEMU will not start. The `cmd:` form is what the spec *describes*
   — a guest connection delivered to the listener — and it is what makes
   test 4's mock-down run a prompt RST rather than a refused boot or a
   swallowed request. The dependency is OpenBSD netcat, present on stock
   Ubuntu; `-N` closes netcat's network side when the guest closes, so the
   broker sees a clean EOF. The broker still binds only `127.0.0.1:9999`.
3. **Test 3 types a note between the two questions** and demands the image
   hold exactly that note and nothing else. The spec says the notebook "did
   NOT gain a record"; this is the same assertion made stronger — if a
   question were wrongly journaled, the note would land at sequence 2 and
   the parse would show it — and it is the only place Stage 4's binary
   proves that notes still persist (Stage 3's gate runs Stage 3's binary).

---

## Decisions taken in this plan

Judgement calls inside the approved spec, flagged so Wajira can overrule any
of them at approval rather than find them in a diff.

1. **The twelve serial lines, exactly.** Stage 3's eleven with `S3:` → `S4:`,
   plus **`S4: nic <mac>`** — six lowercase hex pairs, colon-separated — as
   line eleven, between `S4: notebook ...` and `S4: keyboard ready`. The NIC
   is found and brought up with interrupts off and polled, so `keyboard
   ready` stays the last line before `sti` and the serial contract after it
   stays exactly Stage 2's: the raw echo and nothing more. Failures are
   named `ERR:` lines and a halt, as the disk's are (`ERR: no virtio-net
   device on PCI bus 0`, `ERR: virtio-net has no VERSION_1`, and so on).
   Nothing is sent on the network at boot: no ARP, no gratuitous anything.
2. **The wire protocol** (in full in `stage4/UMBILICAL.md`, item 1). One
   TCP connection per question, from `10.0.2.15` to `10.0.2.4:9999`. A
   **frame** is a `u32` little-endian length `N` followed by `N` bytes. The
   guest sends exactly one request frame — `N` from 1 to 498, bytes `0x20`
   to `0x7E` — and reads exactly one response frame — `N` from 0 to 4096,
   every byte `0x20` to `0x7E` or `0x0A`. The guest closes once the whole
   response has arrived; the broker closes after writing its response;
   either order is tolerated. Little endian for the same reason as the
   notebook: one convention across the project's own formats, checked with
   `struct` on the host.
3. **What is a question.** A line whose first two typed bytes are `?` and
   space; the question is every byte after them, verbatim. `?` alone, or
   `?x`, is a note — the marker is explicit and exact. A question of zero
   bytes sends nothing and gives a fresh prompt. Questions never touch the
   notebook; notes (no marker) take exactly Stage 3's path.
4. **The no-answer rule.** Any of: no SYN-ACK after the retries, a RST, a
   FIN before the response frame is complete, a response length above
   4096, or no complete response within the deadline — and the console
   shows exactly **`no answer from the broker`** on its own line, then a
   fresh prompt. Never a hang; never a halt: the machine is not lost because
   its brain is out.
5. **Timers, all counted in PIT breaths of 200 µs** (the disk's idiom). SYN
   retransmitted after 1 s, five tries; the request segment likewise; the
   **response deadline is 150 s** from the request being acknowledged. The
   broker's own `claude -p` timeout is 120 s, after which it answers with a
   text saying so — so in normal life the guest always gets *some* frame
   inside its deadline, and the 150 s is the backstop for a broker that
   died mid-thought. The mock-down case never reaches it: RST is instant.
6. **The stack's shape, and its recorded omissions.** Ethernet II; ARP reply
   (for `10.0.2.15`) and resolve (for `10.0.2.4`, lazily at the first
   question, one-entry cache, three tries a second apart); IPv4 with the
   header checksum computed on send **and verified on receive**; TCP
   client-only with one connection at a time, one segment in flight, MSS
   1460 offered in the SYN, a 4096-byte receive window, in-order delivery
   only (a segment that is not the next expected byte is dropped and the
   current ACK repeated — slirp retransmits), immediate ACKs, orderly close
   with the guest as active closer, and a RST honoured from any state. Out,
   each a decision: DHCP, DNS, UDP, IPv6, congestion control, ICMP, IP
   options and fragments, TCP options beyond MSS, out-of-order reassembly,
   window scaling, keepalives, TIME_WAIT bookkeeping (a fresh source port
   per question makes it moot), and routing — there is no gateway logic at
   all, because the guest's whole world is on-link. The ISN is the low 32
   bits of `rdtsc` at connect; the source port starts at 49152 and
   increments per question.
7. **Bad checksums are silence, on both sides.** A received IPv4 or TCP
   segment with a bad checksum is dropped without a word, as slirp drops
   ours. The twin enforces this (verified), which is exactly why the guest
   must compute them correctly — and why "no reply at all" earns its own
   gotcha line: *suspect the checksum first*.
8. **Virtio-net: two feature bits, two queues, one owner.**
   `VIRTIO_NET_F_MAC` (bit 5 — the spec says the config MAC is valid only
   when it is negotiated) and `VIRTIO_F_VERSION_1` (bit 32), nothing else:
   no mergeable buffers, no offloads, no control queue, no indirect
   descriptors, no event index. With VERSION_1 the per-packet header is 12
   bytes. Queue 0 receives, queue 1 transmits; `num_queues` will read 3 and
   the control queue is left disabled. **Sixteen receive buffers of 2048
   bytes** are posted at bring-up, each one device-writable descriptor
   holding header and frame contiguously (legal under VERSION_1's
   any-layout rule, and QEMU requires a non-mergeable buffer to hold the
   whole packet — 12 + 1514 fits); each is re-posted after it is read. One
   transmit buffer, one transmit descriptor in flight, its completion
   reaped before the next send. Both queues carry `NO_INTERRUPT`; INTx is
   disabled in the command register; the ISR region is never read; only
   the BSP touches any of it. Transmit completion is polled, bounded, and a
   timeout is `ERR: nic transmit timed out` — the one network failure that
   halts, because it means the device is gone, not the broker.
9. **The virtio code becomes per-device.** Stage 3's `vio_common` ..
   `vq_doorbell` globals become a **device block** — capability addresses,
   notify multiplier, and per-queue state (size, mask, last-used, doorbell,
   ring addresses) — one block for the disk, one for the NIC, addressed
   through a base register. `disk_find` splits into a generic PCI
   enumeration that records both BDFs in one pass (`1001`/`1042` is the
   disk, `1000`/`1041` the NIC; first of each wins) and a generic
   `vio_attach(bdf, block)` (command register, capability walk, mapping)
   and `vio_negotiate(block, features)`; `vq_init(block, queue, rings)`
   takes the queue number. `disk_rw`'s behaviour is unchanged byte for
   byte — Stage 4's test 3 parses the notebook it writes.
10. **The shifted keyboard.** A second 128-byte set-1 table for the shifted
    US layout (capitals, the symbols over the digits, `?` over `/`), and a
    shift state driven by the make and break codes of both Shift keys
    (`2A`/`AA`, `36`/`B6`). Caps Lock, Ctrl, Alt stay ignored. Stage 2's
    "unshifted only" caveat retires; this is the smallest thing that makes
    the owner's marker typeable, and a partial table would be stranger than
    a whole one.
11. **The question path, on Enter.** The Enter echo (CRLF on the wire, drawn
    by the tee) is exactly Stage 3's. Then, console-only: a **working
    indicator** — one cell at column 0 of the fresh line cycling `-` `\`
    `|` `/` about four times a second, driven by the same poll loop that
    watches the NIC — erased when the wait ends; then the answer, drawn
    through `console_putc` from column 0 with LF as new line and the
    console's natural wrap at COLS (the spec's "wrapped"); then the prompt.
    Bytes outside `0x20`–`0x7E`/`0x0A` never arrive (the broker guarantees
    it) and are ignored if they do. Serial carries nothing during any of
    this. Interrupts stay enabled while waiting, so the keyboard handler
    keeps buffering — and **keys pressed during the wait are discarded**
    when it ends (ring tail set to head, under `cli`): a key that shows
    nothing for a minute and then appears is a hidden mode, and the screen
    should never owe the user an invisible debt.
12. **The broker** (`broker/broker.py`, item 2): standard library only;
    binds `127.0.0.1` only, exclusively (no reuse-port; a busy port is a
    loud exit, not a shared one); one connection at a time, sequentially;
    prints `listening on 127.0.0.1:<port>` to stdout once bound, so a
    harness can wait for exactly that; reads one request frame per
    UMBILICAL.md with a 10 s read timeout and closes on anything malformed
    (logged to stderr, never a crash); answers with one response frame and
    closes. `--mock` answers from the **canned table**, which lives in
    UMBILICAL.md and is frozen with it: `ping` → `pong`; `hello` → two
    lines, `hello from the mock broker` and `ask me something true at test
    5`; anything else → `mock: no canned answer for: <question>`. `--record
    <path>` appends one JSON line per connection — the raw request bytes as
    hex, the parsed question, the answer, timestamps — so a checker can
    judge the bytes by UMBILICAL.md itself rather than take the mock's word.
    In real mode the answer comes from **`broker/claude_backend.py`**, the
    spec's one small swappable function: `ask(question, timeout)` runs
    `claude -p --output-format text --tools "" --no-session-persistence
    --bare --system-prompt <a two-line brief: plain ASCII, no markdown, a
    few sentences, you are answering a line typed at the prompt of GermOS>
    -- <question>` from an empty temporary working directory, and
    normalises the text to the wire: common Unicode punctuation folded to
    ASCII (dashes, quotes, ellipsis), anything else dropped, CRLF to LF,
    trailing whitespace trimmed, truncated to 4096 bytes with a trailing
    `...`. A non-zero exit becomes `broker: claude failed (<code>)`; a
    timeout becomes `broker: claude did not answer within 120 s`. The
    backend is exercised only by Wajira at test 5; its flags are its own
    business to get right there, and it is unfrozen for exactly that reason.
13. **The freeze boundary — the reasoning the owner asked for.** The freeze
    exists to keep the *criteria* out of the implementer's reach while a red
    test is pushing on them. Ask what a corrupted mock could do to test 3:
    it could not fake `pong` on the screen (the checker renders that from
    the font), but it *could* tolerate a malformed frame — a length prefix
    off by one — and record the intended text anyway, or record `ping`
    without having received it. So the mock's **framing, recording and
    canned table are criteria** and must be frozen; leaving `broker.py`
    open would leave a side door into test 3. The opposite extreme —
    freezing the Claude backend too — would turn every `claude -p` flag or
    normalisation fix into a spec question for a code path the automated
    gate never runs. So the file is split at the trust boundary:
    **`broker/broker.py` (framing, listener, recording, mock table) is
    frozen at item 7** alongside `stage4/UMBILICAL.md`, `stage4/test.sh`
    and `stage4/checkumbilical.py`; **`broker/claude_backend.py` is not**,
    and nor are `stage4/mkimage.sh` (the recipe) and `stage4/stage4.asm`
    (the thing under test). The alternative of making the checker its own
    listener was rejected because the spec says the harness starts *the
    mock broker*, and a second implementation of the protocol on the host
    would be a second thing to keep honest. One consequence to record:
    Stage 5 will want to grow the broker; that plan will ask the owner to
    open the freeze on `broker.py` deliberately, the way a frozen test is
    changed — by decision, not by drift.
14. **The harness chooses the MAC.** Test 2 passes `mac=52:54:00:a1:04:01`
    on the `-device` and demands `S4: nic 52:54:00:a1:04:01` back — the
    disk-sector precedent: the harness made it, so it knows, and a constant
    in the assembler could not pass. Test 3 and 4 do the same. The windowed
    command for Wajira omits `mac=`, so his machine prints QEMU's default.
15. **One driver, four assertions** — `stage4/checkumbilical.py` owns every
    booted run bar test 2's, as `checknotes.py` did. Mode `--question <smp>`
    (test 3): refuse to run unless `127.0.0.1:9999` is free; start `broker.py
    --mock --port 9999 --record <out/broker.<smp>.jsonl>` and wait for its
    `listening` line; fresh disk; boot with the cage and the MAC; wait for
    `S4: keyboard ready`; type `? ping` Enter; wait until the record shows
    a request (bounded at 20 s), settle 2 s; type `keep this` Enter; type
    `? hello` Enter; wait for the second request, settle; screendump; quit;
    stop the mock. Assert: the twelve boot lines with `notebook formatted`
    and the MAC; the echo after `keyboard ready` exactly `? ping\r\nkeep
    this\r\n? hello\r\n`; the record holds **exactly two** connections whose
    raw bytes are `04 00 00 00 70 69 6e 67` and `05 00 00 00 68 65 6c 6c 6f`
    and parse, by UMBILICAL.md, to `ping` and `hello`; the image parses to
    exactly `["keep this"]` with sector 2 not a record; the screendump,
    rendered from `stage2/font8x8.bin`, shows the rows `> ? ping`, `pong`,
    `> keep this`, `> ? hello`, `hello from the mock broker`, `ask me
    something true at test 5`, and `> ` with the block cursor, on seven
    consecutive rows, each strip exactly once, the cell after each answer
    strip blank (no indicator left behind), and only the two console
    colours anywhere. At `-smp 2` and `-smp 8`. Mode `--cage` (test 4): the
    checker asserts its own QEMU argv — exactly one `-netdev`, type `user`,
    containing `restrict=on`, exactly one `guestfwd=`, guest side
    `tcp:10.0.2.4:9999`, host side `cmd:nc -N 127.0.0.1 9999`, no `hostfwd`,
    no `-nic`, no `-net`; then the **mock-down run**: refuse to run unless a
    connect to `127.0.0.1:9999` is *refused* (something listening would
    answer the question, possibly for real — the checker must never be the
    thing that spends a token); fresh disk; boot at `-smp 8`; type `? ping`
    Enter; wait a fixed 6 s; type `still here` Enter; settle; screendump;
    quit. Assert the twelve lines; the echo exactly `? ping\r\nstill
    here\r\n`; the image exactly `["still here"]`; the rows `> ? ping`, `no
    answer from the broker`, `> still here`, `> ` with cursor; two colours.
    The 6 s is a timing assertion in disguise: a guest still waiting would
    have discarded `still here`, and the note's absence fails the run.
    `test.sh` additionally asserts its *own* serial-run command string
    carries the same cage, so both places that spell it are checked.
16. **`test.sh` refuses to run while anything listens on 9999**, before the
    build. The real broker and the gate cannot share a port, and the gate
    must never talk to anything but its own mock.
17. **The prose the hook will dislike.** `nc`, `restrict`, `guestfwd` and
    `netdev` are not bodyguard words (verified). Commit messages go in by
    `-F` regardless, as Stage 3 did.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are expected green at its commit**. Items
  0–7 commit with every Stage 4 test failing **by design** — there is no
  `stage4.asm` yet. From item 8 the stated tests must be green before the
  commit.
- **`./stage0/test.sh`, `./stage1/test.sh`, `./stage2/test.sh` and
  `./stage3/test.sh` stay green throughout** — run as regressions before
  every commit.
- `HANDOVER.md` is updated as we go, with a final pass at item 14.
- Every new fault class earns a CLAUDE.md gotcha line and a regression check.
- Temporary probes are never committed, and never undone with `git checkout
  --`: copy aside, restore from the copy.
- **The scope guard** governs items 9–13, as in Stage 3: two honest attempts
  at any one obstacle — a real diagnosis from the serial log, not a re-run —
  then stop, record the exact state in `HANDOVER.md`, commit that, and wait
  for Wajira.
- **Everything runs inside QEMU with the caged network.** The only disks are
  files under `stage4/out/`, created fresh by the harness. The broker binds
  only `127.0.0.1`. Nothing outside the repo is written, bar scratch files in
  the session temp directory. No real Claude call is made by this session:
  the mock is the only broker the gate ever talks to, and test 5 is Wajira's.

---

# Part 1 — the protocol, the broker, and the acceptance machinery, written before the code

## Item 0 — this plan, committed

Copy this file verbatim to `stage4/plan.md` and commit it. The first act
after the gate opens, before any other file changes.

*Expected at commit:* no Stage 4 tests exist yet. Stages 0–3 green.

## Item 1 — `stage4/UMBILICAL.md`: the wire, byte-exact

The NOTEBOOK.md precedent — one document, implemented by the assembler and
parsed by the checker and the broker. Sections: the cage (the exact `-netdev`
and `-device` lines, why `10.0.2.4`, why `cmd:nc -N`, what everything else
gets — a RST); addressing (`10.0.2.15/24`, the broker at `10.0.2.4:9999`, no
gateway, no route); the frame (offset, size, type, value tables for request
and response; the length and byte-range rules; little endian); the
conversation (one connection per question; the ISN and source-port rules;
the timers of decision 5; the no-answer rule of decision 4, with the exact
console text); the question rule of decision 3; the drawing rule of decision
11; **the mock's canned table**; the record format; and a **worked example**
— the exact bytes of the `ping` request frame and the `pong` response frame
as `xxd` listings, and the same Python parser the checker will contain:

```python
import struct
def read_frame(sock, limit):
    hdr = recv_exact(sock, 4)
    n, = struct.unpack("<I", hdr)
    if n > limit: raise ValueError("frame of %d bytes exceeds %d" % (n, limit))
    return recv_exact(sock, n)
```

Frozen at item 7.

*Expected at commit:* no Stage 4 tests yet. Stages 0–3 green.

## Item 2 — `broker/broker.py` and `broker/claude_backend.py`

Decision 12 in code. `broker.py`: argument parsing (`--mock`, `--port`,
`--record`, `--timeout`), the exclusive `127.0.0.1` bind, the `listening`
line, the sequential accept loop, `read_frame`/`write_frame` per
UMBILICAL.md with the read timeout, the canned table imported from nowhere —
spelled in the file, matching the document — the JSON-lines record, and a
lazy `from claude_backend import ask` only when not `--mock`, so the mock
imports nothing but the standard library. `claude_backend.py`: `ask()` as
decision 12 describes, plus `normalise()`.

Proven on the host alone, no guest: a ten-line scratch client under
`stage4/out/` connects to `--mock` on the throwaway port, sends the `ping`
frame, reads `pong`, sends a malformed frame on a second connection and sees
it closed, and the record shows exactly what happened. `normalise()` is
exercised on a string with an em-dash, curly quotes and a CRLF.

*Expected at commit:* no Stage 4 tests yet. Stages 0–3 green. No Claude call.

## Item 3 — `stage4/mkimage.sh`, the `stage4/test.sh` harness, acceptance test 1

`mkimage.sh` (not frozen — the recipe): Stage 3's, retargeted. `test.sh`
(frozen from item 7): Stage 3's shape plus the port-9999 refusal of decision
16, a `CAGE_NETDEV` / `CAGE_DEVICE` pair used by every QEMU line, and the
self-assertion on those strings (decision 15). **Test 1** — the artefact,
Stage 3's criteria on Stage 4's files.

*Expected at commit:* every Stage 4 test fails — there is no `stage4.asm`.
The non-zero exit quoted in the commit message.

## Item 4 — acceptance test 2 (serial, first boot: the twelve lines)

`serial_check 8` on a fresh disk with the cage and `mac=52:54:00:a1:04:01`,
under `timeout -k 5 60`, exit 124 expected. Exactly twelve `S4:` messages in
order: Stage 3's checks carried over (geometry, sector count, `notebook
formatted`, found = woken = 8) with **line eleven `S4: nic 52:54:00:a1:04:01`**
and line twelve `S4: keyboard ready`. Whole capture printed on failure.

*Expected at commit:* tests 1–2 fail.

## Item 5 — `stage4/checkumbilical.py --question` (test 3)

The driver of decision 15: the mock's lifecycle, the boot, the typing with
record-driven waits, the screendump, the six assertions, and UMBILICAL.md's
`read_frame` applied to the recorded bytes. The font rendering, PPM parsing,
cell matching, colour discipline and boot-line checks are `checknotes.py`'s,
carried over with the twelve-line pattern table. `test.sh` gains **Test 3**:
`--question 2` and `--question 8`, both must pass.

*Expected at commit:* tests 1–3 fail.

## Item 6 — `checkumbilical.py --cage` and the harness self-check (test 4)

The argv assertion and the mock-down run of decision 15; `test.sh`'s check on
its own `CAGE_NETDEV`. `test.sh` gains **Test 4**. All four exist and all
fail; the output goes in the commit message.

*Expected at commit:* tests 1–4 fail.

## Item 7 — freeze the Stage 4 acceptance machinery

`PROTECTED` grows `stage4/test.sh`, `stage4/checkumbilical.py`,
`stage4/UMBILICAL.md`, **`broker/broker.py`** (decision 13).
`stage4/mkimage.sh` and `broker/claude_backend.py` stay unfrozen, and the
hook's own comment says why. `payloads.py` gains the Stage 4 freeze cases
(the mutation battery on each new path; the allowances — running the gate,
`python3 broker/broker.py --mock --port 9999`, `cat stage4/UMBILICAL.md`,
every operation on `stage4/mkimage.sh` and `broker/claude_backend.py`, the
Stage 4 QEMU line with its `-netdev` and `-device`, and the words `nc`,
`restrict`, `guestfwd`, `netdev` in prose) and is re-run whole: every earlier
case judged as before. Immediacy demonstrated live with one denied call.

*Expected at commit:* tests 1–4 still fail; the payload table 0 wrong.

---

*Everything above is written before any implementation code exists.
Everything below is the code.*

---

# Part 2 — the implementation, in the spec's order

## Item 8 — `stage4/stage4.asm`: Stage 3's proven body, `S3` becomes `S4`

Start from `stage3/stage3.asm` whole — nothing removed. Every `S3:` becomes
`S4:`; the header comment is rewritten; the font path stays
`stage2/font8x8.bin`.

*Green at commit:* **test 1.** Tests 2–4 red. Stages 0–3 green.

## Item 9 — two virtio devices on the bus

Decision 9: the device block, the one-pass enumeration recording both BDFs,
`vio_attach`, `vio_negotiate`, `vq_init` taking a queue number, and the disk
code moved onto the block. `S4: nic` does not exist yet; the disk path must
behave identically.

Verified with a **temporary, uncommitted probe** that prints both BDFs and
BAR addresses and each device's `num_queues` over serial: the NIC at `00:02.0`
with its region at `0xC000000000` and `num_queues` 3; the disk at `00:03.0`
at `0xC000004000` and 1 — then removed, copy-aside. And, since the disk code
moved, `./stage4/test.sh` test 3's notebook assertions are not yet runnable
(no question path), so the Stage 3 checker is borrowed by hand once:
`python3 stage3/checknotes.py --persist 2` against a copy of Stage 4's image
placed at Stage 3's path, in scratch, then restored — the notebook must
still parse byte-exact. That is a probe, not a test change.

*Green at commit:* test 1. Tests 2–4 red. Stages 0–3 green.

## Item 10 — virtio-net brought up, and `S4: nic <mac>`

Decision 8: reset, ACKNOWLEDGE, DRIVER, features MAC | VERSION_1, FEATURES_OK
confirmed, the MAC read as six bytes from device config offset 0, queue 0
and queue 1 initialised with their own rings, sixteen receive buffers posted,
DRIVER_OK, then **line eleven**. Every failure a named `ERR:`.

*Green at commit:* **tests 1 and 2** — twelve lines, the MAC the harness
chose. Tests 3–4 red.

## Item 11 — Ethernet, ARP, IPv4, and the checksums

Decision 6's lower half and decision 7: `net_poll` (drain the receive used
ring, dispatch by EtherType, re-post), `net_send` (header, frame, one
descriptor, bounded completion), `inet_csum`, `arp_input` (reply to a request
for our address; cache a reply for the broker's), `arp_resolve` (three tries
a second apart, the poll loop between), `ip_input` (our address, protocol 6,
header checksum verified), `ip_send` (header built, checksum computed,
Ethernet framing, 60-byte minimum padding).

Verified with a **temporary, uncommitted probe** — the only time the guest
speaks on the network before the question path exists: after `S4: nic`,
resolve `10.0.2.4` and print its MAC over serial; expected
`52:55:0a:00:02:04`. Then removed, copy-aside.

*Green at commit:* tests 1–2. Tests 3–4 red.

## Item 12 — the TCP client

Decision 6's upper half, decisions 4 and 5: the connection block (state,
ports, `snd_nxt`, `snd_una`, `rcv_nxt`, the timers), `tcp_input` (checksum
verified with the pseudo-header; RST from any state; SYN-ACK in SYN_SENT;
in-order data and FIN in ESTABLISHED, ACKed at once; ACK of our FIN),
`tcp_output` (segment built with the pseudo-header checksum), `tcp_connect`,
`tcp_send_frame`, `tcp_recv_frame` (assembling the length-prefixed response
into the 4096-byte answer buffer, the deadline running), `tcp_close`, and
`umbilical_ask` tying them together and returning success or the no-answer
verdict. The poll loop that waits on all of this is where the indicator
of decision 11 will tick.

Verified with a **temporary, uncommitted probe**, the mock broker started by
hand on `127.0.0.1:9999`: after `S4: nic`, ask `ping` and print the response
bytes over serial; expected `pong`. Then with the mock stopped: expected the
no-answer verdict within a second. Then removed, copy-aside.

*Green at commit:* tests 1–2. Tests 3–4 red.

## Item 13 — the shifted keyboard

Decision 10: the shifted table, the Shift state in the handler's consumer
(the main loop, which owns translation — the handler still only buffers).
Verified by hand via the monitor: `sendkey shift-slash spc p i n g ret`
echoes `? ping`; `shift-a` echoes `A`; `2` and `shift-2` echo `2` and `@`.

*Green at commit:* tests 1–2. Tests 3–4 red (no question path yet).

## Item 14 — the question, and the gate closes

Decisions 3, 4 and 11: on Enter, the marker test on the line buffer; a
question skips `notebook_append`, draws the indicator, calls `umbilical_ask`,
erases the indicator, draws the answer or `no answer from the broker`,
discards the ring, and prompts; a note takes Stage 3's path unchanged.

*Green at commit:* **all four automated tests** — tests 3 and 4 close here,
at `-smp 2` and `-smp 8`. Full `./stage4/test.sh` output in the commit
message. Stages 0–3 green.

## Item 15 — HANDOVER, gotchas, and the two commands

- `HANDOVER.md` to the green-pending-oracle state: what was built, the BDFs
  and BARs on this machine, tests 1–4 green with output, test 5 pending
  Wajira, the two commands below, caveats carried forward (everything Stage
  3 carried, minus "unshifted only"; the stack's omission list; one
  connection at a time; polled, no NIC interrupts; plaintext inside the cage
  until the TLS ring; the `nc` dependency in the cage line; the broker's
  backend flags as exercised at test 5).
- `CLAUDE.md` gotchas grown with whatever actually bit — candidates already
  visible from the probes: *a guestfwd cannot sit on slirp's own address*;
  *a `-tcp:` guestfwd target is one chardev opened at startup, not a
  connection per guest socket — use `cmd:`*; *slirp drops a bad checksum
  in silence: no reply at all means suspect the checksum first*; *with
  VERSION_1 the virtio-net header is 12 bytes, and a non-mergeable receive
  buffer must hold the whole frame*; *the config MAC is valid only if
  `VIRTIO_NET_F_MAC` was negotiated*.
- Print the two commands for Wajira.

*Green at commit:* all four automated tests, plus Stages 0–3.

---

## Verification

- **Automated:** `./stage4/test.sh` from the repo root — refuses to start if
  anything listens on 9999; builds; tests 1–4 (serial at `-smp 8`; the
  question round trip at `-smp 2` and `-smp 8` with the mock; the cage
  assertion and the mock-down run at `-smp 8`). Five QEMU boots, about three
  minutes. Exit 0 only if all pass. Run before every commit from item 8 on.
- **Regression:** Stages 0–3's `test.sh` green before every commit.
- **The hook:** `python3 .claude/hooks/payloads.py` at item 7 — every case
  from every stage, 0 wrong; immediacy demonstrated live.
- **The probes:** items 9, 11, 12 and 13 each carry a temporary probe whose
  expected output is stated in the item; item 12's is confirmed against the
  mock from the host side by its record file.
- **Manual (test 5):** Wajira, in two terminals at the repo root. The real
  broker:

```
python3 broker/broker.py
```

  and the grown machine, windowed:

```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage4/out/esp.img \
  -drive format=raw,file=stage4/out/notes.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

  He types `? ` and something true, watches the indicator turn, and reads
  Claude's answer on GermOS's own screen. His word closes the stage.

## Safety

Everything runs inside QEMU. Firmware plus exactly two drives, both raw
files under `stage4/out/`, both created by the harness; the bodyguard is
unchanged and still denies every other kind of disk before the shell sees it.
The network is slirp with `restrict=on` and one `guestfwd`; every other
destination was shown to get a RST. The broker binds `127.0.0.1` only. The
automated gate talks only to the mock, never to Claude, and refuses to run if
anything else holds the port. This session makes no Claude call. The only
outward connection in the whole design is `claude -p`'s own HTTPS from the
real broker, started by Wajira's hand at test 5.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| The spec's cage line does not work as written | measured before planning; deviations 1 and 2, with the probe evidence, put to the owner here rather than discovered at item 12 |
| The NIC's region or slot differs from the disk's assumptions | decision 9's per-device blocks and the runtime BAR read; the item 9 probe prints both |
| No packets ever arrive | rx buffers posted before DRIVER_OK; `NO_INTERRUPT` and INTx off as the disk proved; the 12-byte header; the item 11 probe (ARP) isolates the NIC path from TCP |
| No reply at all to a well-formed segment | decision 7: the checksum is the first suspect, and the twin's silence is the evidence; the checker's mock record shows whether anything reached the host |
| The answer is truncated or garbled on screen | the length prefix delimits the response; in-order-only receive with repeat ACKs; the broker's ASCII guarantee; test 3's pixel rows |
| The machine hangs when the broker is down | decision 4's bounded timers and the RST path; test 4's mock-down run with its 6 s note |
| The gate spends a token or talks to the real broker | the port-free preconditions in `test.sh` and the checker; the exclusive bind; the mock imports no backend |
| The mock is bent to pass a red test | decision 13: `broker.py` frozen; the checker judges the recorded bytes by UMBILICAL.md itself |
| Questions leak into the notebook, or notes stop working | test 3's `keep this` between the questions, parsed from the host |
| Two devices, one careless refactor, and the disk breaks | item 9's borrowed persistence check before any NIC code; Stage 4's test 3 parses the notebook at the close |
| A 3 a.m. improvisation around the network | the scope guard in the conventions, and the whole of Part 1 existing before Part 2 |
