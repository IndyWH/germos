# HOME.md — the home image: where installed apps live, and what the machine does with them

**Stage 6 ring 6b, plan item 1. Frozen behind the hook from item 8.** The
assembler implements this document and the acceptance checker parses by
it; one text, two readers. If it is wrong, that is a spec question for the
owner, not an edit.

`stage3/NOTEBOOK.md` and `stage6/GLASS.md` are frozen and untouched. The
notebook is exactly what it was, on the first virtio disk. This document
adds a **second virtio-blk disk** — the home image — its format, how an
app arrives on it (the `installed` byte of GLASS.md's app frame), how one
is launched from it with nothing on the wire, the one undo, the choices
row's extension, and line twelve of the serial log.

## Two disks

The guest records the **first** virtio-blk device on PCI bus 0 (devices
scanned in ascending order, every function) as the notebook's disk and the
**second** as the home image — drive order, which on QEMU is the order of
the `-drive ...,if=virtio` arguments. Both are driven by the same virtio
code, one request in flight, polled. **With one virtio-blk the machine is
ring 6a's, line for line:** no home line, no home image; an `installed`
frame then draws `no home image: <name> not kept` and the app runs anyway.

## The disk

A raw image of 512-byte sectors, numbered from 0; the harness's is 16 MB
(32768 sectors) but nothing depends on that beyond the header's capacity.
All multi-byte integers are **little endian**. Every byte not named below
is **zero**.

### Sector 0 — the header

| Offset | Size | Type | Value |
|---|---|---|---|
| 0x000 | 8 | ASCII | `GERMHOME` — the magic |
| 0x008 | 4 | u32 | format version, `1` |
| 0x00C | 4 | u32 | sector size in bytes, `512` |
| 0x010 | 8 | u64 | the table's first sector, `1` |
| 0x018 | 8 | u64 | the table's length in sectors, `8` |
| 0x020 | 8 | u64 | the data's first sector, `9` |
| 0x028 | 8 | u64 | the disk's capacity in sectors |
| 0x030 | 464 | — | zero |

A disk is **recognised** when bytes 0–7 read `GERMHOME` and the version is
1. Anything else — a blank disk, a disk from some other life — is
**formatted** on boot: the header is written to sector 0 and sectors 1–8
are written as zeros. The header carries no app count and no free pointer:
both are recovered by scanning the table, so a torn state cannot be
recorded.

### Sectors 1–8 — the table

Sixteen **entries of 256 bytes**, two per sector: entry *i* (0–15) lives
in sector 1 + ⌊i/2⌋ at byte offset (i mod 2) × 256.

| Offset | Size | Type | Value |
|---|---|---|---|
| 0x00 | 32 | ASCII | the **name**, `[a-z][a-z0-9-]{0,31}`, NUL-padded; a zero first byte means an **empty** slot, every byte of which is zero |
| 0x20 | 4 | u32 | the current build's **size** in bytes, 16 to 1,048,576 |
| 0x24 | 4 | u32 | its **first sector** |
| 0x28 | 4 | u32 | its **sectors**, ⌈size / 512⌉ |
| 0x2C | 4 | u32 | zero |
| 0x30 | 32 | bytes | its **SHA-256** |
| 0x50 | 4 | u32 | the **previous build's** size, or 0 when there is none |
| 0x54 | 4 | u32 | its first sector |
| 0x58 | 4 | u32 | its sectors |
| 0x5C | 4 | u32 | zero |
| 0x60 | 32 | bytes | its SHA-256 (all zero when there is none) |
| 0x80 | 52 | bytes | the four **choice slots**, exactly the 52 bytes of the frame's header at offsets 44–95 (GLASS.md, "The wire") |
| 0xB4 | 76 | — | zero |

An entry is **valid** when: the name is well formed and NUL-padded; the
size is in range and the sector count is ⌈size/512⌉; the extent lies in
`[data first, capacity)`; the previous build is either all zero (size,
sectors, first and hash) or valid by the same rule; the zero fields are
zero; the choice slots parse as GLASS.md's do. An invalid non-empty entry
is **ignored** by the guest (never launched, never listed) and may be
overwritten by an install; the checker's parser below raises on one
instead, so a torn entry can never pass a test.

**N**, the number of valid entries, is line twelve: `S6: home <N> apps`
(`1 apps` included — never inflected), printed after the notebook line and
before the NIC line, so `S6: keyboard ready` stays the last line and the
echo contract after it stays Stage 2's. A freshly formatted image says
`S6: home 0 apps`.

**The next free sector** is the larger of the data's first sector and, over
every valid entry, `first + sectors` of the current and of the previous
build. Space behind a build that is no longer referenced is not reclaimed
this ring.

## What becomes an app on disk

An app frame (GLASS.md's kind `0x02`) whose `installed` byte is 1, received
and validated exactly as ring 6a validates it. Then, before the app runs:

1. The blob's bytes after its length, up to the next sector boundary, are
   zeroed in the component region.
2. **The blob's sectors are written first**, from the next free sector.
3. **Then the entry's table sector is written**: an entry of that name
   already present is **replaced** — its current build becomes the
   previous build, the build before that is abandoned — otherwise the
   first empty slot is taken. The choice slots are the frame's.

So an install is one sector write away from either the old state or the
new, never a mixture. The console (never the wire) then says
**`installed <name>`**, and the app runs as any app does.

When there is no empty slot, or the blob does not fit before the capacity,
the app is **not kept**: the console says **`home image full: <name> not
kept`**, one error is counted, and the app runs anyway — it passed the
twin. With no second disk: **`no home image: <name> not kept`**, likewise.

**The SHA-256** is computed by the guest over the blob's `size` bytes at
install time and written into the entry. It is **verified at every
launch**, so the machine runs what the twin proved or says why not.

## What a `!` line does now

After GERMLINE.md's forgiving marker parse gives `!` and a trimmed body:

| The body | What happens |
|---|---|
| empty | `nothing to grow`, as before |
| `undo install <name>` (exactly that prefix, then a name) | **the undo**: a running app is closed first, as any `!` line does; if `<name>` is a valid entry with a previous build, the two builds' fields (size, first, sectors, hash) are **swapped** and the table sector written — the console says **`<name>: previous build restored`**; if the entry has no previous build, **`<name> has no previous build`**; if there is no such entry, **`no app named <name>`**. The one undo this ring has: doing it again swaps back |
| exactly the name of a valid entry | **the launch**: a running app is closed first; the current build's sectors are read into the component region at +128, hashed, and compared with the entry's hash — a mismatch says **`<name>: build does not match its hash`** and runs nothing; otherwise a frame header is synthesised (kind 2, ABI 2, source 0, `installed` 1, the name, the entry's choice slots) and the app runs exactly as a delivered one — **with nothing on the wire: no connection, no byte** — except that neither grows counter moves (no frame was received) |
| anything else | the broker, as ring 6a — with the mode word **`installing`** (mode 4) instead of `growing` while the body begins `install ` |

Names match **exactly, byte for byte**, after the marker parse's trim.
`echo has no previous build`, `no app named …`, `… does not match its
hash`, `home image full …` and `no home image …` each count one in
`errors`; `installed …` and `… previous build restored` do not.

## The choices row

GLASS.md's table, extended for the no-app state: **`? ask   ! grow`**
followed by **`   ! <name>`** for each of the **first three valid entries
in table order** — never more than five items (Hick). With nothing
installed the row is ring 6a's. The two running-app rows are unchanged.
The row is rewritten whenever the table changes and whenever an app
closes.

## Worked example

A fresh 16 MB image after its first boot, sector 0:

```
00000000: 4745 524d 484f 4d45 0100 0000 0002 0000  GERMHOME........
00000010: 0100 0000 0000 0000 0800 0000 0000 0000  ................
00000020: 0900 0000 0000 0000 0080 0000 0000 0000  ................
00000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
... (zeros to 000001f0)
```

`0080 0000 0000 0000` is 32768 sectors. Sectors 1–8 are zero: sixteen
empty entries, `S6: home 0 apps`.

The entry for `echo` after `! install echo` (the committed
`stage6/echo.bin`, 121 bytes, one sector at sector 9), entry 0 at
sector 1 offset 0:

```
00000200: 6563 686f 0000 0000 0000 0000 0000 0000  echo............
00000210: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000220: 7900 0000 0900 0000 0100 0000 0000 0000  y...............
00000230: f127 1761 69e7 1815 1a7e 1df1 1a43 3ef6  .'.ai....~...C>.
00000240: 0897 4653 3517 e45d 31aa c11c e2f4 07d3  ..FS5..]1.......
00000250: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000260: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000270: 0000 0000 0000 0000 0000 0000 0000 0000  ................
... (zeros to 000002f0)
000002f0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

After `! install echo, but big` (the same build padded to 4096 bytes, 8
sectors at sector 10): the current build is the padded one, the previous
is the first (sector 9, 121 bytes, the same hash as above). After
`! undo install echo` the two are swapped back — the first build current
at sector 9, the padded one previous at sector 10 — and `! echo` runs the
first. Both blobs stay on the disk; the next free sector is 18.

## Parsing it cold, in Python

The checker's parser is this, and nothing more:

```python
import re
import struct

SECTOR = 512
MAGIC = b"GERMHOME"
TABLE_FIRST, TABLE_SECTORS, DATA_FIRST = 1, 8, 9
ENTRY = 256
ENTRIES = 16
NAME_RE = re.compile(rb"[a-z][a-z0-9-]{0,31}")
BLOB_MIN, BLOB_MAX = 16, 1048576


def parse_choice_slots(slots):
    """GLASS.md's four 13-byte slots -> [(key, label bytes)]; ValueError."""
    choices = []
    for i in range(4):
        slot = slots[i * 13:(i + 1) * 13]
        if slot[0] == 0:
            if any(slot):
                raise ValueError("an empty choice slot is not all zero")
            continue
        if len(choices) < i:
            raise ValueError("choice slots are not packed from the first")
        label = slot[1:].split(b"\0", 1)[0]
        if not (0x20 <= slot[0] <= 0x7E) or not 1 <= len(label) <= 12 \
                or not all(0x20 <= b <= 0x7E for b in label) or any(slot[1 + len(label):]):
            raise ValueError("a choice is a printable key and a 1..12 byte printable label")
        choices.append((slot[0], label))
    return choices


def parse_build(rec, off, capacity, required):
    size, first, sectors, zero = struct.unpack_from("<IIII", rec, off)
    digest = rec[off + 16:off + 48]
    if not required and size == 0:
        if first or sectors or zero or any(digest):
            raise ValueError("an absent build is not all zero")
        return None
    if not BLOB_MIN <= size <= BLOB_MAX or sectors != (size + SECTOR - 1) // SECTOR or zero \
            or first < DATA_FIRST or first + sectors > capacity:
        raise ValueError("build fields size %d first %d sectors %d are not valid" % (size, first, sectors))
    return {"size": size, "first": first, "sectors": sectors, "sha256": digest.hex()}


def parse_home(data):
    """The whole image. Returns {"capacity", "entries": [entry or None] * 16,
    "next_free"}; an entry is {"name", "current", "previous", "choices"}.
    Raises ValueError on anything the document forbids."""
    if data[0:8] != MAGIC:
        raise ValueError("no GERMHOME magic")
    version, sector, tfirst, tsectors, dfirst, capacity = struct.unpack_from("<IIQQQQ", data, 8)
    if (version, sector, tfirst, tsectors, dfirst) != (1, SECTOR, TABLE_FIRST, TABLE_SECTORS, DATA_FIRST):
        raise ValueError("bad header")
    if capacity != len(data) // SECTOR:
        raise ValueError("header capacity %d, image has %d sectors" % (capacity, len(data) // SECTOR))
    if any(data[0x30:SECTOR]):
        raise ValueError("header padding not zero")
    entries = []
    next_free = DATA_FIRST
    for i in range(ENTRIES):
        base = (TABLE_FIRST + i // 2) * SECTOR + (i % 2) * ENTRY
        rec = data[base:base + ENTRY]
        if rec[0] == 0:
            if any(rec):
                raise ValueError("entry %d: empty slot not all zero" % i)
            entries.append(None)
            continue
        name = rec[0:32].split(b"\0", 1)[0]
        if not NAME_RE.fullmatch(name) or any(rec[len(name):32]):
            raise ValueError("entry %d: bad name %r" % (i, rec[0:32]))
        try:
            current = parse_build(rec, 0x20, capacity, True)
            previous = parse_build(rec, 0x50, capacity, False)
            choices = parse_choice_slots(rec[0x80:0xB4])
        except ValueError as exc:
            raise ValueError("entry %d (%s): %s" % (i, name.decode(), exc))
        if any(rec[0xB4:ENTRY]):
            raise ValueError("entry %d: padding not zero" % i)
        for b in (current, previous):
            if b:
                next_free = max(next_free, b["first"] + b["sectors"])
        entries.append({"name": name.decode("ascii"), "current": current, "previous": previous,
                        "choices": choices})
    return {"capacity": capacity, "entries": entries, "next_free": next_free}


def blob_of(data, build):
    """The build's bytes, from its extent."""
    start = build["first"] * SECTOR
    return data[start:start + build["size"]]
```
