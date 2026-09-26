# PARTS.md — the molt: slots, parts, and the floor under them

**Stage 8 ring 8a, plan item 4. Frozen behind the hook from item 13.** The
assembler implements this document; `stage8/parts.py`,
`stage8/checkmolt.py` and `broker/molt.py` parse by it. One text, four
readers. If it is wrong, that is a spec question for the owner, not an
edit.

The ring's spec is `stage8/spec.md`, and the plan is `stage8/plan-8a.md`
with Cowork's amendments A1–A6. This document is the spec made exact for
ring 8a. Its numbers come from the probes of items 2 and 3 (`HANDOVER.md`,
ring 8a, items 2 and 3) or from a rule stated here, never from arithmetic
typed into a test.

Everything NOTEBOOK.md, GERMLINE.md, GLASS.md (with its 6c and 7d
sections), HOME.md, DISK.md, WIRE.md and TRIALS.md say still stands,
except the sentences below that this document supersedes. **It supersedes
five sentences:**

1. **HOME.md, line twelve:** "**N**, the number of valid entries, is line twelve". From this ring on, N counts the valid entries whose names do **not** begin `part-`. A part is not an app.
2. **HOME.md, the choices row:** "the **first three valid entries in table order**". It now reads the first three valid entries whose names do not begin `part-`.
3. **HOME.md, what a `!` line does:** a body that begins `part-`, whether alone or after `undo install `, is answered by the machine before the home lookup and before the broker. The console says **`<name> is a part`**, where `<name>` is the word beginning `part-`. One is counted in `errors`, nothing is sent, nothing is launched and nothing is swapped. A part is never launched as an app, and its builds change only through the `! molt` words. Separately, a `!` body that is exactly `molt` or begins `molt ` goes to the molt words below, before the home lookup and before the broker, as `trial` does.
4. **GLASS.md, the wire:** an app frame whose name begins `part-` is not run: `bad component frame`. So no app can ever be installed over a part's home entry.
5. **NOTEBOOK.md, what becomes a note:** a typed line whose first five bytes are `molt ` is never a note. It is refused with **`molt is reserved`**, one is counted in `errors`, and nothing is journaled. The journal's `molt ` prefix belongs to the machine alone, as `trial ` does (GLASS.md's 7d section).

**With no `molt` note on the notebook, the machine is ring 7d's to the
line and to the pixel.** The loader reads the notebook at every boot. When
no note begins `molt `, it prints no `S8:` line, arms nothing, polls for
nothing and loads nothing, and the IRQ path is ring 7d's instruction for
instruction. Every rule below applies only once a `molt` note exists.

## The words

| Word | Meaning |
|---|---|
| **seed** | `stage8/out/BOOTX64.EFI` as `stage8/mkimage.sh` builds it (SEED.md): the loader, SHA-256, and the generic implementation of every slot |
| **slot** | a named job the seed can hand to a part |
| **part** | a blob that fills one slot: a 96-byte header, then its body |
| **build** | a part's identity: the SHA-256 of the whole part, header and body. **`<sha16>`** is its first 16 hex digits, lowercase. It is also the hash HOME.md's entry holds |
| **generic** | the seed's own implementation of a slot, never deleted |
| **shadow** | the part is fed the machine's real input, but the generic's answer is the one used, and every disagreement is counted |
| **live** | the part does the work; the generic waits in the seed |
| **probation** | a live build's first three healthy live boots |
| **demoted** | sent back to the generic by the watchdog or by two unhealthy boots |

## The slot table

The seed holds one entry per slot: the slot's name, its state this boot
(generic, shadow or live), and three entry addresses. By default these are
the generic's own. **Ring 8a's table holds one slot, `i8042`**: the
keyboard and the mouse behind the 8042 controller. `disk`, `wire` and
`kernel` join the table in rings 8d, 8e and 8f. They are words the note
grammar knows, but this ring's guest answers each with `unknown slot`.
There is no slot for the loader or for SHA-256, and a header that names
one is refused (below).

## A part

A part is a flat, position-independent blob: `bits 64`, `default rel`,
and no absolute address of its own (GERMLINE.md's rule). It may keep
writable data inside itself. **Its state must be valid as it is stored**,
because in shadow its `byte` entry is called without its `init` ever
running. All integers are little endian.

| Offset | Size | Value |
|---|---|---|
| 0 | 4 | `PART`, the magic |
| 4 | 1 | the ABI, **`3`** |
| 5 | 3 | zero |
| 8 | 8 | the **slot**, ASCII, NUL-padded |
| 16 | 4 | `u32` the **body length** B, at least 1 |
| 20 | 4 | `u32` the **`init`** entry's offset |
| 24 | 4 | `u32` the **`byte`** entry's offset |
| 28 | 4 | `u32` the **`health`** entry's offset |
| 32 | 16 | the **name**, `[a-z0-9][a-z0-9-]{0,15}`, NUL-padded |
| 48 | 32 | the **SHA-256 of the body** |
| 80 | 16 | zero |
| 96 | B | the body |

The whole part (`96 + B` bytes) is at most **65,536 bytes**. Each entry
offset counts from the part's first byte, the header's `P`, and lies in
`[96, 96 + B)`.

**A header is valid** when:
- the magic, the ABI and every zero field are right;
- the slot is one of this ring's slot table;
- the body length equals the part's length less 96;
- the three offsets lie in the body;
- the name is well formed and NUL-padded;
- the body hashes to bytes 48–79.

A body whose hash fails is **`bad hash`**; every other failure is **`bad
header`**.

**Where a part runs.** Each slot has a **part region** in the seed's BSS:
65,536 bytes, page-aligned, writable and executable. At boot the loader
copies the part there with its header at the region's first byte. So an
entry's address is the region plus its offset, and the blame line's offset
is the faulting RIP less the region. The part region is never the
component region, so a part and an app run side by side.

**The entries, for `i8042`:**

- **`init(svc)`**, `RDI` = the service table. It does the controller's cold init and the mouse's reset, identification and enable, the work `mouse_init` does for the generic. It may use ports `0x60` and `0x64`. It is **called only on a boot that loads the part live**, once, where the generic's `mouse_init` would run. `RAX` on return is ignored.
- **`byte(status, data, stamp, svc)`**: `RDI` = the status byte, `RSI` = the data byte, `RDX` = the TSC when the seed's stub read them, `RCX` = the service table. It is **called once for every byte the controller delivers, in arrival order**, keyboard and mouse alike (status bit 5 says whose). The seed's stub has already read port `0x64` and then port `0x60` once, as the gotcha requires, so **`byte` never touches the controller's ports**. It reports what it decodes through the upcalls.
- **`health(svc)`**, `RDI` = the service table. It answers `RAX` = 0 for healthy, and any other value is a failure code. It is called by the pet routine on a boot that loads the part live, never in shadow.

**The calling convention** is GLASS.md's for an app:
- 64-bit long mode, ring 0, the seed's identity map, interrupts enabled, `DF` clear;
- `RSP + 8` 16-byte aligned at entry, on the boot processor's stack; a part should use under 4 KB;
- each entry returns with `ret` and `RSP` as it found it, and may clobber every other register. The seed keeps its loop state in memory and on its own stack, as `app_call` does (CLAUDE.md, "Nothing survives a call into grown code").

A part touches nothing else the seed owns:
- no serial port but through the service;
- no framebuffer, notebook, network, interrupt table, page tables or PIC;
- no port but its slot's, and in `byte` not even those.

## ABI 3's service table

| Offset | Size | Value |
|---|---|---|
| 0 | 4 | `u32` ABI version, `3` |
| 4 | 4 | `u32` table size in bytes, `80` |
| 8 | 8 | address of `pci_read32` |
| 16 | 8 | address of `pci_write32` |
| 24 | 8 | address of `map_mmio` |
| 32 | 8 | address of `dma_pages` |
| 40 | 8 | address of `ticks_ms` |
| 48 | 8 | address of `pit_wait` |
| 56 | 8 | address of `serial_line` |
| 64 | 8 | address of `key_event`, the first upcall |
| 72 | 8 | address of `mouse_packet`, the second upcall |

**Calling a service** is GLASS.md's rule: arguments in `RDI`, `RSI`,
`RDX` and `RCX`, the result in `RAX`. A service preserves `RBX`, `RBP`,
`RSP` and `R12`–`R15`.

- **`pci_read32(bdf, reg)`** and **`pci_write32(bdf, reg, value)`**: `bdf` = bus << 16 | device << 11 | function << 8; `reg` a multiple of 4 below 256. Mechanism #1, as the seed reads. `pci_write32` answers 1 when it wrote, and 0 when it refused (below).
- **`map_mmio(phys, bytes)`**: maps the 2 MB pages covering the range uncached and answers the address to use (the identity), or 0 when it refused (below).
- **`dma_pages(count)`**: `count` zeroed 4 KB pages below 4 GB, physically contiguous, from the slot's own pool of 16 pages for the boot. It answers the address, or 0 when the pool cannot give them. Pages are never freed.
- **`ticks_ms()`**: milliseconds since boot, `u64`, monotonic (the seed's `ticks_ms`).
- **`pit_wait(ms)`**: waits `ms` milliseconds, 1 to 1,000, on the PIT.
- **`serial_line(ptr, len)`**: writes `part: ` followed by `len` bytes (at most 120, and a byte outside `0x20`–`0x7E` goes as `?`), then CR LF, to the UART **raw**, never through the tee.
- **`key_event(key, stamp)`**: one decoded key. `key` is exactly what the generic's `kbd_next` returns: a printable with Shift applied, `13` Enter, `8` Backspace, `9` Tab or `0x1B` Esc. `stamp` is the TSC of the byte that completed it.
- **`mouse_packet(dx, dy, buttons, stamp)`**: one completed packet. `dx` and `dy` are the packet's second and third bytes, sign-extended, with `dy` positive upwards as PS/2 sends it. `buttons` is the first byte's low three bits. `stamp` is the TSC of the packet's first byte.

**What the services refuse** (Cowork's review, 26 September 2026). Each
refusal answers 0, and a refused `pci_write32` writes nothing.

- **`map_mmio` refuses any range whose 2 MB pages overlap RAM**, as the UEFI memory map the loader kept at ExitBootServices records it. RAM here is every descriptor whose type is neither `EfiMemoryMappedIO` (11) nor `EfiMemoryMappedIOPortSpace` (12). The test is on the 2 MB pages, not only the range asked for, because those pages are what `map_mmio` would map. So a part can never get the seed's image back as a writable page, and can never replace the read-only 4 KB split of the image's 2 MB page with a writable one.
- **`pci_write32` and `map_mmio` refuse the watchdog's own hardware:**
  - `pci_write32` refuses every register of the LPC bridge at 00:1f.0, the function whose config space holds PMBASE, RCBA and the ACPI enable;
  - `map_mmio` refuses any range whose 2 MB pages overlap the RCBA window, RCBA to RCBA + 16 KB, which holds GCS and `NO_REBOOT`;
  - the PMBASE range (PMBASE to PMBASE + 128, the TCO registers among them) is I/O space, and no ABI 3 service reaches an I/O port at all.

**The honest limit:** a part runs in ring 0, so these refusals guard the
floor against a part's mistakes, not against a part that means harm. A
part's own `out` instruction, a write through the seed's identity map or
a cleared CR0.WP is beyond any service's reach. The check on grown code is
ring 8b's pipeline: the plan, the twin's rehearsal, the differential
check and shadow.

**In shadow the part gets a shadow table** at the same offsets:
- `pci_read32` and `ticks_ms` work;
- `pci_write32`, `map_mmio`, `dma_pages`, `pit_wait` and `serial_line` do nothing and answer 0;
- the upcalls record the part's events for the comparison and reach nothing else.

There is one controller, so a shadowed part must never act on it. **Live,
the upcalls enter the seed at the generic's own sinks.** A key goes where
`kbd_next`'s result goes: `OBS_KEYS` counts it and `handle_key` consumes
it. A packet goes where `mouse_byte`'s completed packet goes: the clamp,
the cell word, the buttons, the presses, `OBS_PACKETS` and the mouse
ring.

## Never in interrupt context

A part is only ever called from the boot processor's main loop and the
loader's boot path, never from an interrupt handler:

- **No part in the slot:** the IRQ1 and IRQ12 path is ring 7d's, instruction for instruction.
- **A part in shadow:** the stub does all it does today. It also appends `(status, byte, stamp)` to a **raw ring** of 256 entries. The main loop feeds every entry to the part's `byte`, **before it takes the generic's next key**.
- **A part live:** the stub appends to the raw ring and does nothing else. The generic's decoder does not run, and the main loop feeds the part.

A raw entry dropped because the ring was full counts as an **overflow**.

**With a part loaded, the main loop polls instead of halting**, as it does
while an app runs. There is no timer interrupt, and the spec rules one
out.

## The request and the part frame

**`! molt i8042`** closes a running app, as any `!` line does, and sends
GERMLINE.md's grow request. The mode word is `growing`, as for any grow.
The body is:

```
molt <slot> cpu <cpuid.1.eax as 8 hex digits> pci <vendor>:<device>:<revision>
```

The hex is lowercase. The vendor and device are 4 digits and the revision
2. The PCI triple is the slot's device. **The `i8042` has no PCI function
of its own, so its identity is the LPC bridge at 00:1f.0**: the Q77's on
the HP and the ICH9's in the twin. The twin's identity, read by item 3's
probe, is `cpu 000306a9 pci 8086:2918:02`. CPUID leaf 1's EBX is left out
because it carries the logical processor count, which moves with `-smp`.

**The germline key** for a part is `molt <slot>|abi3|<identity>`, where
the identity is the body's words after the slot. The key is keyed to the
machine, not to `qemu-q35-ovmf`. The mock records it; ring 8b's germline
uses it.

**The answer** is exactly one frame (GERMLINE.md): a **refusal**, kind
`0x00`, drawn as an answer, or a **part**, kind `0x03`:

| Offset | Size | Value |
|---|---|---|
| 0 | 4 | `u32 N` = 32 + `L` |
| 4 | 1 | `0x03`, the kind |
| 5 | 1 | the ABI, **`3`** |
| 6 | 1 | `source`: `0` generated, `1` served from the germline |
| 7 | 1 | zero |
| 8 | 4 | `u32 L`, the part's length, header included |
| 12 | 4 | `u32` the threshold's **boots** |
| 16 | 4 | `u32` the threshold's **keyboard bytes** |
| 20 | 4 | `u32` the threshold's **mouse packets** |
| 24 | 12 | zero |
| 36 | `L` | the part |

The kind byte and the 31 bytes after it are the **32-byte header**. The
frame is received into the component region as GERMLINE.md's are: the
length prefix at region + 28, the header at + 32, the part at region + 64.

**The checks at install**, in this order. The first that fails refuses the
frame with **`part refused: <why>`** on the console. One is counted in
`errors`; nothing is stored and nothing is journaled.

| Check | `<why>` |
|---|---|
| `N` = the bytes received; kind `0x03`; ABI 3; `source` ≤ 1; bytes 7 and 24–35 zero; `N` = 32 + `L` | `not a part frame` |
| `L` ≤ 65,536 | `too large` |
| the threshold's boots ≥ 1 (**the floor**) | `below the floor` |
| the header is valid, its body's hash aside | `bad header` |
| the part's body hashes to its header's hash | `bad hash` |
| the header's slot is the slot asked for | `wrong slot` |

A refusal frame is drawn as GERMLINE.md says; no answer is GERMLINE.md's
no-answer rule. An app or component frame in answer to a molt request
fails the first check.

**Storing it.** A valid part is stored by HOME.md's install, unchanged:
- the name is **`part-<slot>`**, and the four choice slots are all zero;
- the blob's sectors are written first and the table sector last;
- a present `part-<slot>` entry's current build becomes its previous build.

Only then is the install note journaled (below). The console says **`part
<slot> shadow <sha16>`**. When the home image is full, HOME.md's
**`home image full: part-<slot> not kept`** is drawn, one error is
counted, and nothing is journaled.

## The four words

`! molt …` is parsed after GERMLINE.md's marker parse and trim. The body
`molt` or a body beginning `molt ` goes here; anything else takes its
usual road.

| The body | What happens |
|---|---|
| `molt` | **the table**: the app panel is cleared and holds the table (below). Nothing goes to the conversation |
| `molt <slot>` | **the fetch**: the request above, then the install or its refusal |
| `molt take <slot>` | **the take** (below) |
| `molt undo` | **the undo** (below) |
| anything else beginning `molt ` | `unknown slot` |

`<slot>` must be in this ring's slot table, or the answer is `unknown
slot` and nothing is sent. **On a boot that loaded a part, every one of
the four words first journals the slot's count note** (below) with the
boot's counts so far.

**The refusals** are console lines. Each counts one in `errors` and
journals nothing:

```
molt is reserved
part-i8042 is a part
unknown slot
no part to take
below threshold: boots <b>/<B> keys <k>/<K> mouse <m>/<M>
disagreements <d>
another part is on probation
already live
nothing to undo
```

**The take** answers, in this order:
- `unknown slot`;
- `already live` if the slot is live;
- `no part to take` unless it is in shadow;
- `another part is on probation` if a part of another slot is;
- `disagreements <d>` if the shadow disagreements sum above 0;
- the below-threshold line, with every count shown, if any count is under its threshold.

Otherwise it journals `molt <slot> live <sha16>`, and the console says
the same. **The new state takes effect at the next boot**, as every state
change does: the loader reads the state at boot, and nothing is loaded or
unloaded in the middle of a boot.

**The table**, one row per panel row from row 0, column 0. For each slot
in the table:
- the row `<slot> <state>`;
- when the state is shadow or live, two more rows:

```
i8042 shadow 4e8e873b8d817d1e
boots 2/3 keys 680/1000 mouse 3400/5000
disagreements 0 probation 0/3
```

The counts are the shadow counts (below) against the build's threshold,
and the probation count is out of 3. A generic or demoted slot has its one
row: `i8042 generic`, or `i8042 demoted <sha16> <why>`. The panel keeps
the table until something else clears it.

## The notes

Every molt event is one note, NOTEBOOK.md's record unchanged, written by
the machine alone. The rules are TRIALS.md's: printable ASCII, single
spaces, and decimal numbers with no leading zeros.

| Note | When |
|---|---|
| `molt <slot> shadow <sha16> <boots> <keys> <packets>` | an install, with the frame's threshold |
| `molt <slot> live <sha16>` | a take |
| `molt <slot> undo <state>` | an undo, naming the state it lands in: `generic`, `shadow <sha16>`, `live <sha16>` or `demoted <sha16> <why>` |
| `molt <slot> demoted <sha16> <why>` | a demotion; `<why>` is `watchdog` or `unhealthy` |
| `molt boot <n> <slot> <shadow\|live>` | at every boot that loads a part, before the handover; the slot and state pair repeats for each slot loaded. `<n>` is one more than the number of `molt boot` notes |
| `molt healthy <n>` | the health mark of boot `<n>` |
| `molt <slot> count <n> <keys> <packets> <d>` | at the health mark, and at each `! molt` word, on a boot that loaded the slot. It carries the boot's counts so far, and the last in a boot is that boot's total |
| `molt <slot> disagree <n> <k> <generic event> <part event>` | a disagreement, the first sixteen a boot. `<k>` is the event's position this boot, from 1 |
| `molt recovery owner` | Esc held at power-on |
| `molt recovery all` | a recovery that demoted every live part, after its demoted notes |

**An event is written** `k<hex>` for a key (two lowercase hex digits,
`k71` for `q`), `m<dx>,<dy>,<buttons>` for a packet (`m-3,12,1`), and `-`
for none.

**Each note also goes to serial** at the moment it is journaled, raw
UART, never the tee, as the note with its first word replaced. The serial
line is `molt:` followed by the note from its fifth byte, for example
`molt: i8042 live 4e8e873b8d817d1e` and `molt: healthy 7`. So the HP's
chart carries the molt record without a flash to read the disk, and
`parts.py --serial` reads it back. `S7: notebook N notes` counts the molt
notes, the boot's replay draws them, and `n` on the strip counts them.

## The states and the undo

A slot's state is read from its notes alone, in journal order, starting
from `generic`:
- an install note gives `shadow <sha16>`;
- a take gives `live <sha16>`;
- a demotion gives `demoted <sha16> <why>`;
- an undo gives the state it names.

Notes of other kinds leave the state unchanged. **A new build for a slot
replaces its current build and shadows** while the slot's work goes back
to the generic. That ends its predecessor's probation, whatever state the
predecessor was in.

**The undo** acts on the slot whose state changed last. It is `nothing to
undo` if there is none, or if that slot is generic.

| From | To |
|---|---|
| `live <X>` | `shadow <X>`, keeping its counts |
| `demoted <X> <why>` | `shadow <X>`; the counts start again |
| `shadow <X>` | the state the slot was in just before `X`'s last install note, **if** that state names a build and that build is the first 16 hex of the home entry's previous build. The two builds are then swapped by HOME.md's undo and its table-sector write. Otherwise `generic`, and the home entry is untouched |

The undo journals `molt <slot> undo <state>`, and the console says the
same. **A build the watchdog demoted can never become live by undo
alone**: undo takes it to shadow, and shadow must earn its threshold
again before a take.

## Shadow: the events and the comparison

In shadow, both decoders see the same bytes in the same order:
- **The generic's events** are observed where they leave it: each key `kbd_next` returns, and each packet `mouse_byte` completes.
- **The part's events** are its upcalls.
- The two sequences are **compared in order**: the generic's *k*-th event this boot against the part's *k*-th. Stamps are never compared.

**The comparison** runs at every main loop turn, over the positions both
sides have reached. A position where the two events differ is **one
disagreement**. At each **count point** (the health mark and each `! molt`
word), the raw ring is first drained into the part. Then every event one
side has beyond the other's last is one more disagreement, and those
extra events are dropped, so the two sides start level again.

**The counts per boot**, for a slot in shadow:
- **keyboard bytes**: bytes with status bit 5 clear handed to the part;
- **mouse packets**: the packets the generic completed from bytes handed to the part;
- **disagreements**: as above.

On a live boot the counts are the part's own: its keyboard bytes, and its
`mouse_packet` upcalls. Disagreements are 0 there, since nothing is
compared.

**The keyboard bytes a typed key makes** on a translated PS/2 keyboard,
which the checker predicts:

| Key | Bytes |
|---|---|
| a plain key | 2: make, break |
| a shifted key | 4: shift make, make, break, shift break |
| an extended key (the arrows and the editing block) | 4: `E0`, make, `E0`, break |

Item 3 measured this rule in the twin: 124 bytes predicted and 124
counted for a mixed text of 53 keys. **One monitor `mouse_move` makes one
packet** when moves are paced 1 ms apart or more; moves sent back to back
are coalesced by QEMU and do not.

## The threshold, its floor, and probation

**The threshold** travels in the part's frame and is journaled in the
install note. From ring 8b on it is pre-registered in the part's plan;
the fixtures' thresholds are pre-registered in the fixture table below.
**The floor** binds every frame: at least 1 boot. The guest demands **0
disagreements always**.

**The shadow counts** for the take are summed over the build's **shadow
boots**. A shadow boot is a boot whose `molt boot` note loaded the slot in
shadow while this build was its state. Only boots since the build last
entered shadow count, whether it entered by an install or by an undo from
`demoted`. An undo from `live` keeps them. Each shadow boot gives its
**last** count note. The current boot's count is journaled by the take
word itself, first, so it is among them.

**Probation** is 3 healthy boots, each a boot that loaded the build live
and journaled its `molt healthy` note, counted since the build last
entered shadow. **One part is on probation at a time.** No part of
another slot enters shadow while one is on probation: its fetch answers
`another part is on probation` and sends nothing, and so does its take.

## The boot with a molt note

In order, from the loader. All of it runs on the boot processor with
interrupts off, **after `S7: glass core <n>` and before the controller's
init**: the `i8042:` pair or the part's `part:` pair. Until `S7: keyboard
ready`, the `S8:` lines go through the tee as boot-log lines, and the
`molt:` mirror lines go raw.

1. **SHA-256's known answer**: the digest of `abc` must be `ba7816bf…f20015ad` (below). Pass: `S8: sha256 ok`. Fail: `ERR: sha256 known answer`, and the boot is the seed's alone. It loads no part, journals nothing, arms nothing, and prints no further `S8:` line.
2. **The evidence**: `TCO2_STS.SECOND_TO_STS` is read, then cleared (below).
3. **The recovery decision** (the table below). A recovery journals its notes and prints its line, and no part loads.
4. **Esc** (below), if a slot is in shadow or live. The console draws `hold Esc for the seed`, and the window runs. Esc held: `molt recovery owner`, `S8: recovery owner`, and no part loads.
5. **The door**, for each slot in shadow or live. The home entry `part-<slot>` must exist; its current build's first 16 hex must equal the state's `<sha16>`; and its bytes must hash to the entry's SHA-256. Otherwise the line is `S8: part <slot> bad hash`, the slot stays generic, and nothing is demoted: a torn write is not a verdict. If the header is not valid: `S8: part <slot> bad header`, likewise. Otherwise the part is copied to its region: `S8: part <slot> <shadow|live> <sha16>`.
6. If any part loaded: **the boot note** `molt boot <n> …`, then **the watchdog is armed** and its line printed.
7. For `i8042`, a live part's `init(svc)` runs and writes its own lines (for the fixtures, `part: i8042 self-test ok` and `part: i8042 mouse reset ok`). Otherwise the generic's `mouse_init` runs, with its `i8042:` pair.
8. `S7: keyboard ready`, and the boot goes on as ring 7d's.

The notes journaled here are on the disk before the boot's replay, so the
replay draws them.

## The watchdog

**The timer is the PCH's TCO**: the Q77's on the HP and q35's ICH9 in
the twin. The loader finds the LPC bridge at 00:1f.0 (vendor `8086`) and
reads:

| Register | Where | What the loader does with it |
|---|---|---|
| PMBASE | config `0x40`, bits 15:7 | the ACPI I/O base; **TCOBASE = PMBASE + `0x60`** |
| RCBA | config `0xF0`, bits 31:14 | the root complex's base, mapped uncached with `map_mmio_2m` |
| GCS | RCBA + `0x3410`, bit 5 `NO_REBOOT` | cleared, then read back |
| SMI_EN | PMBASE + `0x30`, bit 13 `TCO_EN` | cleared, so the first expiry is not routed to SMM |
| `TCO_RLD` | TCOBASE + `0x00` | any write reloads the timer: **the pet** |
| `TCO1_STS` | TCOBASE + `0x04`, bit 3 `TIMEOUT` | cleared by writing 1 |
| `TCO2_STS` | TCOBASE + `0x06`, bit 1 `SECOND_TO_STS`, bit 2 `BOOT_STS` | **the evidence**; cleared by writing 1, `SECOND_TO_STS` before `BOOT_STS` |
| `TCO1_CNT` | TCOBASE + `0x08`, bit 11 `TCO_TMR_HLT`, bit 12 `TCO_LOCK`, bit 8 `NMI_NOW` | halted while it is set up; `NMI_NOW` is write-1-to-clear, so it is never written back |
| `TCO_TMR` | TCOBASE + `0x12`, bits 9:0 | the count |

**`TCO_TMR` for a 30 s deadline, by the Intel 7 Series / C216 Chipset
Family PCH Datasheet (326776-003), the Q77's:**
- the timer "is clocked at approximately 0.6 seconds" (§13.9.11), with 10 bits, and values 0 and 1 are ignored;
- the first expiry sets `TIMEOUT` and the count starts again;
- "the TCO timer times out twice and the PCH asserts PLTRST#" (§5.14.1.1).

So the deadline is 2 × `TCO_TMR` × 0.6 s, and **30 s gives `TCO_TMR` =
25**. The HP writes the same register on its own silicon. **The twin
agrees**, measured at item 2: the reset came at 2 × *n* × 0.6 s for *n* =
2, 4, 10, 25 and 50, and 31.0 s from the arming line to OVMF's first byte
at *n* = 25.

**Arming**, just before the first part runs (step 6 above), and at no boot
that loads no part:
1. Halt the timer.
2. Clear `NO_REBOOT`. If it reads back set: `S8: watchdog tco locked`, and the boot goes on unguarded. This is decision 5's fallback: the unhealthy count and the power button.
3. Clear `TCO_EN`.
4. Write `TCO_TMR` = 25.
5. Clear `TIMEOUT`, then `SECOND_TO_STS`, then `BOOT_STS`.
6. Reload, then unhalt.
7. Print `S8: watchdog tco 30 s`.

With no Intel LPC bridge at 00:1f.0, or a PMBASE of 0, the line is `S8:
watchdog none`, and the boot likewise goes on unguarded.

**The pet** is a loader routine. It reloads the timer only when all five
of these have held since the last pet:
1. the boot processor's heartbeat has moved;
2. `OBS_FRAMES` has moved;
3. no exception has been taken (a flag `exc_common` sets);
4. every live part's `health()` answered 0;
5. the seed's outside check of each loaded slot agrees. For `i8042`: the status byte at `0x64` reads neither `0xFF` nor with bit 6 or bit 7 set, and no ring has overflowed (the keyboard ring, the mouse ring, the raw ring).

It rate-limits itself: **at most one reload per 1,000 ms by the TSC**.

**The heartbeat and the pet's call sites (A1).** The heartbeat moves at
every main loop turn and at every breath of a bounded wait: the wire's TCP
poll and the disk's command wait. **The pet routine is called at every
one of those points.** So a broker wait longer than the deadline keeps the
machine alive, while a part hung in the main loop stops both the
heartbeat and the pet.

**Two waits longer than the deadline pass with no reset:**
- a broker request held for **`HOLD_S` = twice the deadline = 60 s**;
- the idle health-mark wait of a live boot, 60 s.

**`RESET_S`, the time from the triggering input to OVMF's first byte of
the next boot, has three terms:**
- the 30 s deadline, counted from the last reload;
- plus at most one pet interval (1 s), from the last reload to the hang;
- plus the reset to OVMF's first byte, 1.14 s at worst in the twin (item 2, `-smp 8`).

Item 2 found no tick error. The checker's number is written from item 12's
run.

## The health mark

On a boot that loaded a part, the main loop takes the health mark at its
first turn **60,000 ms by the TSC after `S7: keyboard ready`**. It
journals `molt healthy <n>`, then each loaded slot's count note, then
writes `S8: healthy <n>` to the UART raw. A boot is **unhealthy** until it
earns that note.

## The recovery table

The loader applies these at step 3 of every boot with a molt note:

| What the loader finds | What it does | Notes | Line |
|---|---|---|---|
| `SECOND_TO_STS` set: the last reset was the watchdog's | recovery: no part loads, and the **blamed** part is demoted | `molt <slot> demoted <sha16> watchdog` | `S8: recovery <slot> watchdog` |
| no evidence, and the **unhealthy run** is 1 | tries the parts again | — | — |
| no evidence, and the unhealthy run is 2 or more | recovery: the blamed part is demoted | `molt <slot> demoted <sha16> unhealthy` | `S8: recovery <slot> unhealthy` |
| either recovery, with no part in shadow or on probation but some live | recovery: every live part is demoted | a demoted note each, then `molt recovery all` | `S8: recovery all` |
| a part whose hash does not match its home entry | step 5: that part is skipped and the generic serves | — | `S8: part <slot> bad hash` |
| Esc held at power-on | step 4: recovery, nothing demoted | `molt recovery owner` | `S8: recovery owner` |

**The blamed part** is the part in shadow or on probation. Rules above
keep it unique: one part on probation at a time, and no other slot
shadowing while one is. **The unhealthy run** is the number of `molt boot`
notes since the last `molt healthy`, demoted or `molt recovery` note. When
the evidence is set but no slot is in shadow or live, it is cleared and
nothing else happens.

**The evidence as item 2 found it in the twin:**
- `SECOND_TO_STS` and `BOOT_STS` **survive the watchdog's reset** and a monitor `system_reset`, in every one of 14 resets;
- only a new QEMU process clears them, as RSMRST# does on silicon;
- a hang's boot and its recovery boot are therefore one QEMU process.

**So the twin's expectation after a live part hangs or faults is exactly
one path:** the next boot prints `S8: recovery i8042 watchdog` and
journals `molt i8042 demoted <sha16> watchdog`. The HP's firmware may
behave otherwise; the owner's procedure, `stage8/HP-8a.md`, says what to
do there, and it is not a criterion.

## Esc at power-on

The owner's way back needs no command. It runs only on a boot that has a
part to load (step 4), after the console is up and before the handover:

1. **The loader's own minimal setup first (A3).** Wait for the input buffer to empty, write `0xAE` (enable port 1), and drain the output buffer. Nothing depends on the state the firmware left the controller in.
2. Draw **`hold Esc for the seed`** on the console, and on the console alone.
3. Poll ports `0x64`/`0x60` for a window of **W = 3,000 ms by the TSC**. W is a human's window, pre-registered here; the owner may change it at approval.
4. Discard bytes with status bit 5 set.
5. **Esc is held** if an Esc make arrived in the window and no Esc break followed it before the window ended. Typematic repeats are makes and keep it held.
   - The make is accepted in **translated set 1, `0x01`** (break `0x81`), and in **untranslated set 2, `0x76`** (break `0xF0 0x76`).
   - A `0x76` straight after `0xF0` is a break, not a make.
6. Drop every other byte read in the window. The boot's typing starts after `ready`.

**In the twin, as item 3 measured:**
- the command byte after the setup is `0x67`, so translation is on;
- the make arrives as `0x01` within 1 ms of the line before the window;
- the break arrives at the hold's end, and there are no repeats;
- an Esc sent before ExitBootServices loses its make to the firmware, so it is not held.

A key held from power-on is therefore never a hold. On the HP, Esc at
power-on also opens the firmware's own menu. The owner presses Esc only
when `hold Esc for the seed` appears. The checker's hold, `sendkey esc
5000`, is sent when `S8: sha256 ok` lands. That value is the checker's
own, not W.

## The serial lines

Every `S8:` line the guest can print is listed here. They are **printed
only on a boot whose notebook holds a molt note.**

| Line | When |
|---|---|
| `S8: sha256 ok` | the known answer passed (step 1) |
| `S8: recovery <slot> watchdog` | the evidence, and the slot's part blamed |
| `S8: recovery <slot> unhealthy` | two unhealthy boots, and the slot's part blamed |
| `S8: recovery all` | a recovery with every live part demoted |
| `S8: recovery owner` | Esc held |
| `S8: part <slot> shadow <sha16>` | the slot's part loaded in shadow |
| `S8: part <slot> live <sha16>` | the slot's part loaded live |
| `S8: part <slot> bad hash` | the door refused its hash |
| `S8: part <slot> bad header` | the door refused its header |
| `S8: watchdog tco 30 s` | the TCO armed |
| `S8: watchdog tco locked` | `NO_REBOOT` would not clear |
| `S8: watchdog none` | no TCO found |
| `S8: healthy <n>` | the health mark, raw |

Beside them are `ERR: sha256 known answer`, the blame line below, and the
`molt:` mirror of each note.

**One expected line per twin event (A5).** For every event of the twin's
fates this document names exactly one line, fixed from the run of item 2:
- **an armed boot prints `S8: watchdog tco 30 s`**, since the twin's `NO_REBOOT` clears and its TCO is found;
- **the boot after a live part hangs or faults prints `S8: recovery i8042 watchdog`**, since the evidence survives.

The lines that belong to other machines stay out of every twin
expectation: `tco locked` and `none`, `recovery … unhealthy`, and
`recovery all`. These rules are exercised by the probes of items 12 and
16, and the HP's may appear on its chart.

## The blame line

With a part loaded, `exc_common` prints its own line as ever: `ERR:
exception <v> at 0x<rip>`. Before it halts, it adds one more:

```
ERR: exception <v> in part <slot> +0x<offset, 8 hex digits>
ERR: exception <v> in seed
```

The first form is for a RIP inside a loaded part's region, and the offset
is from the part's first byte, the header's `P`. The second is for any
other RIP. The exception writes nothing to the disk. It sets the flag
that stops the pets, and the watchdog does the rest. With no part loaded,
`exc_common` is ring 7d's.

## The read-only floor

**The whole `.text` is read-only**, on every core, from `build_paging` on.
That is the loader's code and the constants it keeps inside `.text`
(`sha_k`, `sha_init` and its strings):
- `build_paging` splits the 2 MB page that holds the image into 4 KB pages;
- CR0.WP is set on the boot processor straight after the CR3 load, and on every AP in the trampoline.

So a stray write into the seed's code faults with a blame line instead
of quietly changing the floor.

The loader's mutable state lives in one page-aligned, writable BSS block,
never passed to a part:
- the pet's state;
- the watchdog's I/O bases;
- the recovery state;
- the Esc window's result;
- SHA-256's working state;
- the loader's serial line buffer.

**Out of scope this ring, said plainly:** the IDT, the GDT and the page
tables stay writable, because the processor writes a descriptor's
accessed bit. Making them read-only is a later ring's.

## The fixtures

Five hand-written parts for the `i8042` slot, in `stage8/fixtures/`, each
an `.asm` and its `.bin`. They are built with `nasm -f bin
stage8/fixtures/i8042-<fate>.asm -o stage8/fixtures/i8042-<fate>.bin`.
Each `.asm` opens with a banner that names the fixture and states its
fate as this table does, as `stage6/liar.asm` does.

| Fixture | Name field | What it is | Trigger | Threshold (boots, keyboard bytes, mouse packets) | Fate in the twin |
|---|---|---|---|---|---|
| `i8042-good` | `good` | the seed's own i8042 code as a part. `init` is `mouse_init`'s work, with the two lines `part: i8042 self-test ok` and `part: i8042 mouse reset ok`. `byte` is the generic's decoder and packet assembly exactly (E0 swallows its successor, shift, `scan1_map`, no E1). `health` answers 0 | — | 3, 1,000, 5,000 | shadow with 0 disagreements; taken; live; typing and a click work through it |
| `i8042-wrong` | `wrong` | `good`, with make code `0x10` decoded as `0x11`'s key: `q` as `w`, `Q` as `W` | every `q` | 1, 100, 100 | shadow counts the disagreement; the take answers `disagreements <d>` |
| `i8042-hang` | `hang` | `good`, whose `byte` spins for ever on its 100th call after its own `init` | the 100th byte after `init` | 1, 100, 100 | behaves as `good` in shadow (never `init`-ed); live, the machine hangs, the watchdog resets it, and the next boot is `S8: recovery i8042 watchdog` with `hang` demoted |
| `i8042-fault` | `fault` | `good`, which executes its one `ud2` (`0F 0B`) on its first mouse byte after its own `init` | the first byte with status bit 5 set after `init` | 1, 100, 100 | as `good` in shadow; live, `ERR: exception 6 in part i8042 +0x<ud2's offset>`, the reset, and the same recovery |
| `i8042-liar` | `liar` | `good` with its name field `liar` | — | 1, 100, 100 | installed through the mock, then **the host flips bit 0 of the body's first byte** (the part's byte 96) in the stored build on the disk image. The next boot prints `S8: part i8042 bad hash`, the generic serves, and nothing is demoted |

Every number here is a rule's output for the checker: the thresholds, the
100th-byte point (by the key-byte rule), `ud2`'s offset (found in the
`.bin`, never typed), and the liar's stored bytes and hashes.

## The corpus

**Reserved for ring 8b.** The spec's corpus for `i8042` belongs in this
document: every make and break code, the `E0` and `E1` sequences,
typematic runs, mouse packets with every sign and overflow bit, a lost
byte in the middle of a packet, and keyboard and mouse bytes interleaved.
Ring 8b's spec freezes "the plan, the corpus and the verdict rule" at 8b's
freeze, before the first grow. So the corpus enters this document **by a
planned freeze opening at ring 8b's gate, by the owner's hand**. Ring 8a
writes only this heading and this rule (plan deviation 7).

## Worked examples

### The twin's request and key

The twin's identity is `cpu 000306a9 pci 8086:2918:02` (item 3). The
request body is `molt i8042 cpu 000306a9 pci 8086:2918:02`, 40 bytes, and
the frame is 45:

```
00000000: 2900 0000 016d 6f6c 7420 6938 3034 3220  )....molt i8042 
00000010: 6370 7520 3030 3033 3036 6139 2070 6369  cpu 000306a9 pci
00000020: 2038 3038 363a 3239 3138 3a30 32          8086:2918:02
```

The germline key is `molt i8042|abi3|cpu 000306a9 pci 8086:2918:02`.

### A part and its frame

A made-up part, not a fixture: slot `i8042`, name `example`, and a 5-byte
body. `init` at 96 is a `ret`, `byte` at 97 is a `ret`, and `health` at
98 is `xor eax, eax` then `ret`. The body's SHA-256 is
`2453b19ba707f1cc70397e39b7e6bfea53134a09b88eb28d8a2029b0f7e62ff7`, and
the part is 101 bytes:

```
00000000: 5041 5254 0300 0000 6938 3034 3200 0000  PART....i8042...
00000010: 0500 0000 6000 0000 6100 0000 6200 0000  ....`...a...b...
00000020: 6578 616d 706c 6500 0000 0000 0000 0000  example.........
00000030: 2453 b19b a707 f1cc 7039 7e39 b7e6 bfea  $S......p9~9....
00000040: 5313 4a09 b88e b28d 8a20 29b0 f7e6 2ff7  S.J...... ).../.
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000060: c3c3 31c0 c3                             ..1..
```

Its build is
`4e8e873b8d817d1e0ad7f01be16a1b774ac9373197ebfdc01f2ef3fc6b663fc0`, so its
`<sha16>` is `4e8e873b8d817d1e`. Its frame, with the threshold 1, 100,
100 and source 0, is 137 bytes (`N` = 133 = 32 + 101). The first 40
bytes:

```
00000000: 8500 0000 0303 0000 6500 0000 0100 0000  ........e.......
00000010: 6400 0000 6400 0000 0000 0000 0000 0000  d...d...........
00000020: 0000 0000 5041 5254                      ....PART
```

Its torn write, the liar's rule applied to it, turns byte 96 from `c3` to
`c2`. The stored build's SHA-256 is then
`7907554485da9f4aca81116e1c60cf4a5f18bda2e29050eba51590120c281b75`, which
no longer matches the entry, so the door says `S8: part i8042 bad hash`.

### The fixtures' frames and the liar

Each fixture's `.bin` in `stage8/fixtures/` is its part, as committed.
For each, this section gives:
- its length and its three entries;
- its build, its `<sha16>`, and its install note with the fixture table's threshold;
- its 96-byte header;
- the first 40 bytes of its frame, source 0.

`fault` adds its `ud2`'s offset and its blame line. `liar` adds the torn
write's byte and both hashes. `parts.py` renders each subsection from the
`.bin` (`render_fixture`), and `--example` demands this text.

#### `i8042-good`

1,152 bytes: the header and a 1,056-byte body. `init` at 96, `byte` at 382
and `health` at 611. Its build is
`4fe6beefc4bc57d0e9ff23f4c605d85950eb99537371756f1b61ac441f8d2785`, so its
`<sha16>` is `4fe6beefc4bc57d0`, and its install note is `molt i8042
shadow 4fe6beefc4bc57d0 3 1000 5000`.

```
00000000: 5041 5254 0300 0000 6938 3034 3200 0000  PART....i8042...
00000010: 2004 0000 6000 0000 7e01 0000 6302 0000   ...`...~...c...
00000020: 676f 6f64 0000 0000 0000 0000 0000 0000  good............
00000030: 7241 4bc7 239d da02 2c6e d99e 4409 4767  rAK.#...,n..D.Gg
00000040: 33b2 aa28 df7a 8605 b250 acca 68f0 2d48  3..(.z...P..h.-H
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

Its frame is 1,188 bytes (`N` = 1,184 = 32 + 1,152):

```
00000000: a004 0000 0303 0000 8004 0000 0300 0000  ................
00000010: e803 0000 8813 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 5041 5254                      ....PART
```

#### `i8042-wrong`

1,152 bytes: the header and a 1,056-byte body. `init` at 96, `byte` at 382
and `health` at 611. Its build is
`b41ddccde138ea239ecb6ee309d95b69578eecd49d2273aa1a1680343c41317d`, so its
`<sha16>` is `b41ddccde138ea23`, and its install note is `molt i8042
shadow b41ddccde138ea23 1 100 100`.

```
00000000: 5041 5254 0300 0000 6938 3034 3200 0000  PART....i8042...
00000010: 2004 0000 6000 0000 7e01 0000 6302 0000   ...`...~...c...
00000020: 7772 6f6e 6700 0000 0000 0000 0000 0000  wrong...........
00000030: 03d8 09db 91e6 e611 e12e ad40 3767 137a  ...........@7g.z
00000040: be76 152f ae5f 99bc 2259 78db 1033 f502  .v./._.."Yx..3..
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

Its frame is 1,188 bytes (`N` = 1,184 = 32 + 1,152):

```
00000000: a004 0000 0303 0000 8004 0000 0100 0000  ................
00000010: 6400 0000 6400 0000 0000 0000 0000 0000  d...d...........
00000020: 0000 0000 5041 5254                      ....PART
```

#### `i8042-hang`

1,176 bytes: the header and a 1,080-byte body. `init` at 96, `byte` at 382
and `health` at 637. Its build is
`f0668b687c68cab0bed99268bb539d6bfb5d9ab30b2ecbf1013e5b0d5defee77`, so its
`<sha16>` is `f0668b687c68cab0`, and its install note is `molt i8042
shadow f0668b687c68cab0 1 100 100`.

```
00000000: 5041 5254 0300 0000 6938 3034 3200 0000  PART....i8042...
00000010: 3804 0000 6000 0000 7e01 0000 7d02 0000  8...`...~...}...
00000020: 6861 6e67 0000 0000 0000 0000 0000 0000  hang............
00000030: 5dd9 c1ed 0567 c1bd 4c37 889e 23bf de88  ]....g..L7..#...
00000040: 4c32 a330 5307 cac6 ffc0 2d0d 94e9 2368  L2.0S.....-...#h
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

Its frame is 1,212 bytes (`N` = 1,208 = 32 + 1,176):

```
00000000: b804 0000 0303 0000 9804 0000 0100 0000  ................
00000010: 6400 0000 6400 0000 0000 0000 0000 0000  d...d...........
00000020: 0000 0000 5041 5254                      ....PART
```

#### `i8042-fault`

1,160 bytes: the header and a 1,064-byte body. `init` at 96, `byte` at 382
and `health` at 622. Its build is
`99e9f923a568309e9be3336bc978b92c8578081acb25f3352822fd70d2e0cb62`, so its
`<sha16>` is `99e9f923a568309e`, and its install note is `molt i8042
shadow 99e9f923a568309e 1 100 100`.

```
00000000: 5041 5254 0300 0000 6938 3034 3200 0000  PART....i8042...
00000010: 2804 0000 6000 0000 7e01 0000 6e02 0000  (...`...~...n...
00000020: 6661 756c 7400 0000 0000 0000 0000 0000  fault...........
00000030: 0d7a 46d3 7083 2b24 4c50 f398 3c7d 7144  .zF.p.+$LP..<}qD
00000040: 657a b6df 47de d21a b9dd d0d9 d691 e436  ez..G..........6
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

Its frame is 1,196 bytes (`N` = 1,192 = 32 + 1,160):

```
00000000: a804 0000 0303 0000 8804 0000 0100 0000  ................
00000010: 6400 0000 6400 0000 0000 0000 0000 0000  d...d...........
00000020: 0000 0000 5041 5254                      ....PART
```

Its one `ud2` is at byte 507 of the part, so its blame line is `ERR:
exception 6 in part i8042 +0x000001fb`.

#### `i8042-liar`

1,152 bytes: the header and a 1,056-byte body. `init` at 96, `byte` at 382
and `health` at 611. Its build is
`f15e77a8966e95e366fcb74130077a70665187bd151c96e9720043d44f38b68a`, so its
`<sha16>` is `f15e77a8966e95e3`, and its install note is `molt i8042
shadow f15e77a8966e95e3 1 100 100`.

```
00000000: 5041 5254 0300 0000 6938 3034 3200 0000  PART....i8042...
00000010: 2004 0000 6000 0000 7e01 0000 6302 0000   ...`...~...c...
00000020: 6c69 6172 0000 0000 0000 0000 0000 0000  liar............
00000030: 7241 4bc7 239d da02 2c6e d99e 4409 4767  rAK.#...,n..D.Gg
00000040: 33b2 aa28 df7a 8605 b250 acca 68f0 2d48  3..(.z...P..h.-H
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

Its frame is 1,188 bytes (`N` = 1,184 = 32 + 1,152):

```
00000000: a004 0000 0303 0000 8004 0000 0100 0000  ................
00000010: 6400 0000 6400 0000 0000 0000 0000 0000  d...d...........
00000020: 0000 0000 5041 5254                      ....PART
```

Its body is `good`'s byte for byte, and only the name field differs. The
torn write turns byte 96 from `48` to `49`. The home entry keeps the build
`f15e77a8966e95e366fcb74130077a70665187bd151c96e9720043d44f38b68a`, the
stored bytes now hash to
`2ae3a89fa1d700b407e1cc754c87e14d86a18251e28af1b6393f3302d6baf684`, and
the door says `S8: part i8042 bad hash`.

### A slot's history, and the table at each step

`G` stands for a build's `<sha16>`, `aaaaaaaaaaaaaaaa`, and `H` for a
second, `bbbbbbbbbbbbbbbb`. These are the notes of disk G's run in
outline. Their counts are made up, and the notes before the first molt
note are elided.

```
molt i8042 shadow G 3 1000 5000
molt boot 1 i8042 shadow
molt healthy 1
molt i8042 count 1 340 1700 0
molt boot 2 i8042 shadow
molt healthy 2
molt i8042 count 2 340 1700 0
molt boot 3 i8042 shadow
molt healthy 3
molt i8042 count 3 340 1700 0
molt i8042 count 3 340 1700 0
molt i8042 live G
molt boot 4 i8042 live
molt healthy 4
molt i8042 count 4 50 20 0
molt i8042 count 4 50 20 0
molt i8042 undo shadow G
molt i8042 count 4 50 20 0
molt i8042 live G
molt recovery owner
molt boot 5 i8042 live
molt healthy 5
molt i8042 count 5 10 10 0
```

- After the first note, `! molt` shows `i8042 shadow G`, `boots 0/3 keys 0/1000 mouse 0/5000` and `disagreements 0 probation 0/3`. A take then answers `below threshold: boots 0/3 keys 0/1000 mouse 0/5000`.
- Boot 3's take journals its count note, the second `count 3`, and passes: `boots 3/3 keys 1020/1000 mouse 5100/5000` → `molt i8042 live G`.
- Boot 4's undo (live → shadow) journals its count, then `molt i8042 undo shadow G`. The take journals its count again and passes on the same three shadow boots, because an undo from live keeps them.
- `molt recovery owner` is the Esc boot. It loaded nothing and wrote no boot note, so the next `molt boot` is numbered 5.
- At the end, `! molt` shows `i8042 live G`, `boots 3/3 keys 1020/1000 mouse 5100/5000` and `disagreements 0 probation 2/3`: boots 4 and 5 were healthy live.

Then disk H's history, which continues from here:

```
molt i8042 shadow H 1 100 100
molt boot 6 i8042 shadow
molt healthy 6
molt i8042 count 6 120 150 0
molt i8042 count 6 120 150 0
molt i8042 live H
molt boot 7 i8042 live
```

- Boot 7 hangs, and the watchdog resets the machine.
- At boot 8 the evidence is set, `H` is on probation (0 of 3), and the decision is a recovery: `molt i8042 demoted H watchdog` and `S8: recovery i8042 watchdog`.
- `! molt` then shows the one row `i8042 demoted bbbbbbbbbbbbbbbb watchdog`.
- `! molt undo` would journal `molt i8042 undo shadow H`, and `H`'s counts would start again.

### The undo from shadow

After `molt i8042 shadow G 3 1000 5000`, `molt i8042 live G` and `molt
i8042 shadow H 1 100 100`, the slot is `shadow H`. The state before `H`'s
install was `live G`.

- If the home entry's previous build begins `aaaaaaaaaaaaaaaa`, `! molt undo` journals **`molt i8042 undo live G`** and swaps the entry's two builds.
- With any other previous build, or none, it journals **`molt i8042 undo generic`** and leaves the entry alone.
- A slot whose only note is its first install undoes to `generic`.
- A notebook with no molt state note answers `nothing to undo`.

### The recovery decisions

Each row applies the recovery table to a history and an evidence bit:

| The notes end with | Evidence | Decision |
|---|---|---|
| `… molt i8042 live H`, `molt boot 7 i8042 live` | set | `molt i8042 demoted H watchdog`, `S8: recovery i8042 watchdog` |
| the same | clear | the unhealthy run is 1: load the parts again |
| the same, then `molt boot 8 i8042 live` | clear | the run is 2: `molt i8042 demoted H unhealthy`, `S8: recovery i8042 unhealthy` |
| `molt i8042 shadow G 1 1 1`, `molt i8042 live G`, then boots 1–3 live, each with its `molt healthy`, then `molt boot 4 i8042 live` | set | `G` is past probation, so every live part is demoted: `molt i8042 demoted G watchdog`, `molt recovery all`, `S8: recovery all` |
| `… molt i8042 demoted H watchdog` | clear | the run is 0: load the parts (none is in shadow or live, so none loads) |

### Esc

Bytes read in the window, and whether Esc is held:

| Bytes | Held |
|---|---|
| `01` | yes |
| `01 01 01` (typematic) | yes |
| `01 81` | no |
| `81` (a break with no make, from a key pressed before ExitBootServices) | no |
| `76` | yes |
| `76 F0 76` | no |

### The keyboard bytes of a typed text

`The Quick brown fox, 42 jumps! Over? the lazy dog`, then Left, Right, Up
and Down, make 53 keys:
- 44 plain keys at 2 bytes: 88;
- 5 shifted keys (`T`, `Q`, `!`, `O`, `?`) at 4 bytes: 20;
- 4 arrows at 4 bytes: 16.

That is **124 keyboard bytes**: item 3 counted 124.

### The watchdog, and SHA-256

`TCO_TMR` = 30 / (2 × 0.6) = **25**. SHA-256 of `abc`:

```
ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```

The first round constant, `sha_k_rule()[0]`, is `0x428a2f98`, the
fractional part of ∛2. The last is `0xc67178f2`, from ∛311.

## Parsing it cold, in Python

`stage8/parts.py` executes this block as its own definitions, read from
this file at import, so the tool and the document cannot drift.
`checkmolt.py` and `broker/molt.py` use the tool. A note list is the
notebook's notes as strings, in journal order.

```python
import hashlib
import re
import struct

SLOTS = ["i8042"]                                   # the slot table this ring; disk, wire, kernel join later
SLOT_WORDS = ["i8042", "disk", "wire", "kernel"]    # the four Stage 8 slots; no slot for the loader or SHA-256
PART_MAGIC = b"PART"
ABI = 3
PART_HEADER = 96
PART_MAX = 65536                                    # header and body together
FRAME_HEADER = 32                                   # the kind byte and the 31 after it
KIND_REFUSAL, KIND_PART = 0x00, 0x03
GROW_MARKER = 0x01
NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,15}")
SHA16_RE = re.compile(r"[0-9a-f]{16}")
EVENT_RE = re.compile(r"-|k[0-9a-f]{2}|m-?\d+,-?\d+,[0-7]")
NOTE_PREFIX, SERIAL_PREFIX, HOME_PREFIX = "molt ", "molt:", "part-"
FLOOR_BOOTS = 1
PROBATION = 3
DISAGREE_NOTES = 16                                 # the first sixteen a boot are notes
DEADLINE_S = 30
TICK_S = 0.6                                        # the 7-series PCH's TCO tick
HEALTH_S = 60
HOLD_S = 2 * DEADLINE_S
PET_MS = 1000                                       # the pet's own rate limit
W_MS = 3000                                         # the Esc window, a human's
ESC_SET1 = (0x01, 0x81)                             # make, break (translated)
ESC_SET2 = (0x76, 0xF0)                             # make; break is F0 then 76
FIXTURES = {                                        # fate threshold: boots, keyboard bytes, mouse packets
    "good": (3, 1000, 5000), "wrong": (1, 100, 100), "hang": (1, 100, 100),
    "fault": (1, 100, 100), "liar": (1, 100, 100),
}
HANG_BYTE = 100                                     # hang spins on its 100th byte after its own init
KAT_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def tco_tmr(deadline_s=DEADLINE_S):
    """The datasheet's rule: two expiries of TCO_TMR ticks of 0.6 s reset the machine."""
    v = round(deadline_s / (2 * TICK_S))
    assert 2 <= v <= 1023 and abs(2 * v * TICK_S - deadline_s) < 1e-9
    return v


def sha256_kat():
    return hashlib.sha256(b"abc").hexdigest() == KAT_ABC


def sha_k_rule():
    """SHA-256's 64 round constants: the first 32 bits of the fractional parts of
    the cube roots of the first 64 primes, in exact integer arithmetic."""
    primes, n = [], 2
    while len(primes) < 64:
        if all(n % p for p in primes if p * p <= n):
            primes.append(n)
        n += 1
    out = []
    for p in primes:
        lo, hi = 0, 1 << 48                         # floor(cbrt(p) * 2**32) by bisection
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if mid ** 3 <= p << 96:
                lo = mid
            else:
                hi = mid - 1
        out.append(lo & 0xFFFFFFFF)
    return out


def identity(cpuid_eax, vendor, device, rev):
    return "cpu %08x pci %04x:%04x:%02x" % (cpuid_eax, vendor, device, rev)


def request_body(slot, ident):
    return "molt %s %s" % (slot, ident)


def request_frame(slot, ident):
    body = request_body(slot, ident).encode("ascii")
    return struct.pack("<I", 1 + len(body)) + bytes([GROW_MARKER]) + body


def molt_key(slot, ident):
    return "molt %s|abi%d|%s" % (slot, ABI, ident)


def part_header(slot, name, body, init, byte, health):
    """The 96-byte header for a body; the entry offsets count from the header's first byte."""
    h = PART_MAGIC + bytes([ABI, 0, 0, 0]) + slot.encode().ljust(8, b"\0")
    h += struct.pack("<IIII", len(body), init, byte, health)
    h += name.encode().ljust(16, b"\0") + hashlib.sha256(body).digest()
    return h + bytes(PART_HEADER - len(h))


def check_part(part, slot=None):
    """A part's header by this document; returns its fields or raises ValueError(why)."""
    if not PART_HEADER < len(part) <= PART_MAX:
        raise ValueError("bad header")
    if part[0:4] != PART_MAGIC or part[4] != ABI or any(part[5:8]):
        raise ValueError("bad header")
    s = part[8:16].split(b"\0", 1)[0]
    if s.decode("latin-1") not in SLOTS or any(part[8 + len(s):16]):
        raise ValueError("bad header")
    blen, init, byte, health = struct.unpack_from("<IIII", part, 16)
    if blen != len(part) - PART_HEADER:
        raise ValueError("bad header")
    for off in (init, byte, health):
        if not PART_HEADER <= off < len(part):
            raise ValueError("bad header")
    name = part[32:48].split(b"\0", 1)[0].decode("latin-1")
    if not NAME_RE.fullmatch(name) or any(part[32 + len(name):48]) or any(part[80:PART_HEADER]):
        raise ValueError("bad header")
    if hashlib.sha256(part[PART_HEADER:]).digest() != part[48:80]:
        raise ValueError("bad hash")
    slot_name = s.decode()
    if slot is not None and slot_name != slot:
        raise ValueError("wrong slot")
    return {"slot": slot_name, "name": name, "body": blen, "init": init, "byte": byte, "health": health,
            "build": hashlib.sha256(part).hexdigest()}


def part_frame(part, threshold, source=0):
    boots, keys, packets = threshold
    head = bytes([KIND_PART, ABI, source, 0]) + struct.pack("<IIII", len(part), boots, keys, packets)
    head += bytes(FRAME_HEADER - len(head))
    return struct.pack("<I", FRAME_HEADER + len(part)) + head + part


def parse_frame(frame, slot):
    """A molt request's answer: ("refusal", text), ("part", fields, part, threshold, source),
    or ValueError(why) with why the words after "part refused: "."""
    if len(frame) < 5:
        raise ValueError("not a part frame")
    n, = struct.unpack_from("<I", frame, 0)
    if n != len(frame) - 4:
        raise ValueError("not a part frame")
    if frame[4] == KIND_REFUSAL:
        return ("refusal", frame[5:].decode("latin-1"))
    if frame[4] != KIND_PART or n < FRAME_HEADER:
        raise ValueError("not a part frame")
    abi, source, zero = frame[5], frame[6], frame[7]
    length, boots, keys, packets = struct.unpack_from("<IIII", frame, 8)
    if abi != ABI or source > 1 or zero or any(frame[24:36]) or n != FRAME_HEADER + length:
        raise ValueError("not a part frame")
    if length > PART_MAX:
        raise ValueError("too large")
    if boots < FLOOR_BOOTS:
        raise ValueError("below the floor")
    part = frame[36:]
    fields = check_part(part, slot)
    return ("part", fields, part, (boots, keys, packets), source)


def sha16(build):
    return build[:16]


def key_bytes(ch):
    """Keyboard bytes one sendkey makes on a translated PS/2 keyboard: a plain key
    make and break, a shifted one inside a shift pair, an E0 key two E0 pairs."""
    if ch in ("up", "down", "left", "right", "home", "end", "pgup", "pgdn", "insert", "delete"):
        return 4
    if len(ch) == 1 and (ch.isupper() or ch in '!@#$%^&*()_+{}|:"<>?~'):
        return 4
    return 2


def keyboard_bytes(keys):
    return sum(key_bytes(k) for k in keys)


def ev_key(code):
    return "k%02x" % code


def ev_mouse(dx, dy, buttons):
    return "m%d,%d,%d" % (dx, dy, buttons)


def parse_note(text):
    """A molt note's fields, or None for any other note."""
    w = text.split(" ")
    if not text.startswith(NOTE_PREFIX) or "" in w:
        return None
    try:
        if w[1] == "boot" and len(w) >= 5 and len(w) % 2 == 1:
            pairs = list(zip(w[3::2], w[4::2]))
            if all(s in SLOT_WORDS and st in ("shadow", "live") for s, st in pairs):
                return {"kind": "boot", "boot": int(w[2]), "slots": dict(pairs)}
            return None
        if w[1] == "healthy" and len(w) == 3:
            return {"kind": "healthy", "boot": int(w[2])}
        if w[1] == "recovery" and len(w) == 3 and w[2] in ("owner", "all"):
            return {"kind": "recovery", "who": w[2]}
        if w[1] not in SLOT_WORDS or len(w) < 3:
            return None
        slot, verb = w[1], w[2]
        if verb == "shadow" and len(w) == 7 and SHA16_RE.fullmatch(w[3]):
            return {"kind": "install", "slot": slot, "build": w[3],
                    "threshold": (int(w[4]), int(w[5]), int(w[6]))}
        if verb == "live" and len(w) == 4 and SHA16_RE.fullmatch(w[3]):
            return {"kind": "take", "slot": slot, "build": w[3]}
        if verb == "demoted" and len(w) == 5 and SHA16_RE.fullmatch(w[3]) and w[4] in ("watchdog", "unhealthy"):
            return {"kind": "demoted", "slot": slot, "build": w[3], "why": w[4]}
        if verb == "undo":
            st = state_words(w[3:])
            return {"kind": "undo", "slot": slot, "state": st} if st else None
        if verb == "count" and len(w) == 7:
            return {"kind": "count", "slot": slot, "boot": int(w[3]), "keys": int(w[4]),
                    "packets": int(w[5]), "disagree": int(w[6])}
        if verb == "disagree" and len(w) == 7 and EVENT_RE.fullmatch(w[5]) and EVENT_RE.fullmatch(w[6]):
            return {"kind": "disagree", "slot": slot, "boot": int(w[3]), "at": int(w[4]),
                    "generic": w[5], "part": w[6]}
    except ValueError:
        return None
    return None


def state_words(w):
    """("generic",) or (state, sha16[, why]) from a note's words, or None."""
    if w == ["generic"]:
        return ("generic",)
    if len(w) == 2 and w[0] in ("shadow", "live") and SHA16_RE.fullmatch(w[1]):
        return (w[0], w[1])
    if len(w) == 3 and w[0] == "demoted" and SHA16_RE.fullmatch(w[1]) and w[2] in ("watchdog", "unhealthy"):
        return ("demoted", w[1], w[2])
    return None


def state_text(st):
    return " ".join(st)


def notes_molt(notes):
    return [p for p in (parse_note(t) for t in notes) if p]


def history(notes, slot):
    """The slot's states in order: [(index into the molt notes, state)], from generic."""
    out = [(-1, ("generic",))]
    for i, p in enumerate(notes_molt(notes)):
        if p.get("slot") == slot and p["kind"] in ("install", "take", "demoted", "undo"):
            out.append((i, state_after(out[-1][1], p)))
    return out


def state_of(notes, slot):
    return history(notes, slot)[-1][1]


def arrival(notes, slot):
    """(index, the state before) of the current build's last install note."""
    h = history(notes, slot)
    build = h[-1][1][1] if len(h[-1][1]) > 1 else None
    ms = notes_molt(notes)
    for j in range(len(h) - 1, 0, -1):
        i, st = h[j]
        if ms[i]["kind"] == "install" and st[1] == build:
            return i, h[j - 1][1]
    return None, ("generic",)


def shadow_start(notes, slot):
    """Where the current build last entered shadow by install or by undo from demoted."""
    h = history(notes, slot)
    ms = notes_molt(notes)
    for j in range(len(h) - 1, 0, -1):
        i, st = h[j]
        if ms[i]["kind"] == "install":
            return i
        if ms[i]["kind"] == "undo" and st[0] == "shadow" and h[j - 1][1][0] == "demoted":
            return i
    return None


def threshold_of(notes, slot, build):
    for p in reversed(notes_molt(notes)):
        if p["kind"] == "install" and p["slot"] == slot and p["build"] == build:
            return p["threshold"]
    return None


def state_after(st, p):
    """The slot's state after one of its notes."""
    if p["kind"] == "install":
        return ("shadow", p["build"])
    if p["kind"] == "take":
        return ("live", p["build"])
    if p["kind"] == "demoted":
        return ("demoted", p["build"], p["why"])
    if p["kind"] == "undo":
        return p["state"]
    return st


def state_of_at(ms, slot, upto):
    """The slot's state just before molt note number upto."""
    st = ("generic",)
    for p in ms[:upto]:
        if p.get("slot") == slot:
            st = state_after(st, p)
    return st


def counts_of(notes, slot):
    """(boots, keyboard bytes, mouse packets, disagreements) over the current build's shadow
    boots since it last entered shadow: each boot's last count note."""
    st = state_of(notes, slot)
    start = shadow_start(notes, slot)
    if st[0] not in ("shadow", "live") or start is None:
        return (0, 0, 0, 0)
    ms = notes_molt(notes)
    shadow_boots = set()
    for i, p in enumerate(ms):
        if i > start and p["kind"] == "boot" and p["slots"].get(slot) == "shadow" \
                and state_of_at(ms, slot, i)[1] == st[1]:
            shadow_boots.add(p["boot"])
    last = {}
    for i, p in enumerate(ms):
        if i > start and p["kind"] == "count" and p["slot"] == slot and p["boot"] in shadow_boots:
            last[p["boot"]] = p
    return (len(shadow_boots), sum(p["keys"] for p in last.values()),
            sum(p["packets"] for p in last.values()), sum(p["disagree"] for p in last.values()))


def probation_of(notes, slot):
    """Healthy boots that loaded the current build live, since it last entered shadow."""
    st = state_of(notes, slot)
    start = shadow_start(notes, slot)
    if st[0] != "live" or start is None:
        return 0
    ms = notes_molt(notes)
    live_boots = {p["boot"] for i, p in enumerate(ms) if i > start and p["kind"] == "boot"
                  and p["slots"].get(slot) == "live" and state_of_at(ms, slot, i)[1] == st[1]}
    return len({p["boot"] for i, p in enumerate(ms) if i > start and p["kind"] == "healthy"
                and p["boot"] in live_boots})


def on_probation(notes, slot):
    st = state_of(notes, slot)
    return st[0] == "live" and probation_of(notes, slot) < PROBATION


def take_of(notes, slot):
    """The take word's answer: the note it journals, or the refusal it draws."""
    if slot not in SLOTS:
        return "unknown slot"
    st = state_of(notes, slot)
    if st[0] == "live":
        return "already live"
    if st[0] != "shadow":
        return "no part to take"
    if any(on_probation(notes, s) for s in SLOTS if s != slot):
        return "another part is on probation"
    b, k, m, d = counts_of(notes, slot)
    if d:
        return "disagreements %d" % d
    B, K, M = threshold_of(notes, slot, st[1])
    if b < B or k < K or m < M:
        return "below threshold: boots %d/%d keys %d/%d mouse %d/%d" % (b, B, k, K, m, M)
    return "molt %s live %s" % (slot, st[1])


def undo_of(notes, previous16):
    """The undo word's answer for the slot whose state changed last. previous16 is the first
    16 hex of the home entry's previous build, or None. Returns (note or refusal, swap)."""
    ms = notes_molt(notes)
    slot = next((p["slot"] for p in reversed(ms) if p["kind"] in ("install", "take", "demoted", "undo")), None)
    if slot is None:
        return "nothing to undo", False
    st = state_of(notes, slot)
    if st[0] == "live":
        land, swap = ("shadow", st[1]), False
    elif st[0] == "demoted":
        land, swap = ("shadow", st[1]), False
    elif st[0] == "shadow":
        _, before = arrival(notes, slot)
        if before[0] != "generic" and before[1] == previous16:
            land, swap = before, True
        else:
            land, swap = ("generic",), False
    else:
        return "nothing to undo", False
    return "molt %s undo %s" % (slot, state_text(land)), swap


def unhealthy_run(notes):
    """Boot notes since the last healthy, demoted or recovery note."""
    run = 0
    for p in notes_molt(notes):
        if p["kind"] == "boot":
            run += 1
        elif p["kind"] in ("healthy", "demoted", "recovery"):
            run = 0
    return run


def recovery_of(notes, evidence):
    """The loader's decision at a boot with molt notes, before the Esc window: ("load",) or
    ("recovery", why, [(slot, sha16) demoted], all). evidence is SECOND_TO_STS as read."""
    if evidence:
        why = "watchdog"
    elif unhealthy_run(notes) >= 2:
        why = "unhealthy"
    else:
        return ("load",)
    running = [(s, state_of(notes, s)) for s in SLOTS if state_of(notes, s)[0] in ("shadow", "live")]
    blamed = [(s, st[1]) for s, st in running if st[0] == "shadow" or on_probation(notes, s)]
    if blamed:
        return ("recovery", why, blamed[:1], False)
    if running:
        return ("recovery", why, [(s, st[1]) for s, st in running], True)
    return ("load",)


def recovery_notes(decision):
    if decision[0] != "recovery":
        return []
    _, why, demoted, everything = decision
    out = ["molt %s demoted %s %s" % (s, b, why) for s, b in demoted]
    return out + (["molt recovery all"] if everything else [])


def recovery_line(decision):
    if decision[0] != "recovery":
        return None
    _, why, demoted, everything = decision
    return "S8: recovery all" if everything else "S8: recovery %s %s" % (demoted[0][0], why)


def boot_number(notes):
    return 1 + sum(1 for p in notes_molt(notes) if p["kind"] == "boot")


def esc_held(bytes_in_window):
    """The held rule over the bytes read in the window (status bit 5 clear), in order."""
    held, prev = False, None
    for b in bytes_in_window:
        if b in (ESC_SET1[0], ESC_SET2[0]) and prev != 0xF0:
            held = True
        elif b == ESC_SET1[1] or (b == ESC_SET2[0] and prev == 0xF0):
            held = False
        prev = b
    return held


def table_of(notes):
    """The rows `! molt` draws in the app panel."""
    rows = []
    for s in SLOTS:
        st = state_of(notes, s)
        rows.append("%s %s" % (s, state_text(st)))
        if st[0] not in ("shadow", "live"):
            continue
        b, k, m, d = counts_of(notes, s)
        B, K, M = threshold_of(notes, s, st[1]) or (0, 0, 0)
        rows.append("boots %d/%d keys %d/%d mouse %d/%d" % (b, B, k, K, m, M))
        rows.append("disagreements %d probation %d/%d" % (d, probation_of(notes, s), PROBATION))
    return rows


def serial_of(note):
    return SERIAL_PREFIX + note[4:]


def note_of_serial(line):
    return "molt" + line[len(SERIAL_PREFIX):]


def is_reserved(line):
    return line.startswith(NOTE_PREFIX)


def home_name(slot):
    return HOME_PREFIX + slot


def is_part_name(name):
    return name.startswith(HOME_PREFIX)


def liar_stored(part):
    """The liar's torn write: bit 0 of the body's first byte flipped in the stored build."""
    b = bytearray(part)
    b[PART_HEADER] ^= 0x01
    return bytes(b)


def ud2_offset(part):
    """The offset from the part's first byte of its one ud2 (0F 0B)."""
    hits = [i for i in range(PART_HEADER, len(part) - 1) if part[i:i + 2] == b"\x0f\x0b"]
    if len(hits) != 1:
        raise ValueError("expected exactly one ud2 in the body, found %d" % len(hits))
    return hits[0]


def blame_line(vector, slot=None, offset=None):
    if slot is None:
        return "ERR: exception %d in seed" % vector
    return "ERR: exception %d in part %s +0x%08x" % (vector, slot, offset)
```
