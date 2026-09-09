# DISK.md — one SATA disk, two partitions: where the notebook and the home live from Stage 7

**Stage 7 ring 7a, plan item 2. Frozen behind the hook from item 8.** The
assembler implements this document and the acceptance checker parses by
it; one text, two readers. If it is wrong, that is a spec question for the
owner, not an edit.

`stage3/NOTEBOOK.md` and `stage6/HOME.md` are frozen and untouched. Both
formats stand byte for byte; what changes is where they live. Until Stage 6
each was a raw image on its own virtio-blk device. From ring 7a there is no
virtio-blk: there is **one SATA disk on an AHCI controller**, carrying a
**GPT the guest writes itself**, with **two partitions** — *notes* and
*home*, 16 MB each — and each partition is exactly the raw image it
replaces, moved to an LBA offset. This document is the disk: how it is
found, how it is recognised, what the guest writes when it is blank, where
the two partitions are, what the serial lines say, and how a checker reads
it cold from the host.

## The controller and the port

The guest drives the first PCI function on bus 0 of class `0x01`, subclass
`0x06`, programming interface `0x01` — an AHCI 1.0 host bus adapter — per
the AHCI 1.3 specification: its ABAR (BAR5) mapped uncached wherever the
firmware put it, `GHC.AE` set, `GHC.IE` clear, interrupts never enabled,
INTx disabled at the function, bus mastering set before any address is
handed over. **Every implemented port whose `PxSSTS` says a device is
present and active (`DET` 3, `IPM` 1) and whose `PxSIG` is
`0x00000101` — a SATA disk — is identified** (`IDENTIFY DEVICE`) and its
first two sectors read. Then **one port is chosen by the selection rule
below**, stopped (`ST` then `FRE`, each awaited), given a command list and
a FIS receive area from the guest's own memory, and started. From then on
every transfer is one command in slot 0 — `READ DMA EXT` (`0x25`) or
`WRITE DMA EXT` (`0x35`), one 512-byte sector, LBA48 — polled to
completion with a bounded wait. The disk's sector size must be 512 bytes
and its sector count below 2^32; anything else is a named error.

## The selection rule

A disk is classified from its first two sectors and, when they carry a
table, from that table. The guest's five words:

| Word | The disk holds |
|---|---|
| `germos` | a **recognised GermOS table** (below) |
| `blank` | sectors 0 and 1 entirely zero |
| `gpt` | a valid GPT (the signature, a valid header, a valid entry array) that does **not** hold both GermOS partitions — someone else's table |
| `torn` | the `EFI PART` signature at sector 1 with an invalid header or array — a broken or half-written table, GermOS's or anyone's |
| `other` | anything else — an MBR, a boot sector, a filesystem, data |

The rule, in order:

1. **The chosen port is the one holding a `germos` disk.** The first such
   port in port order, if more than one.
2. **If none, the chosen port is the one holding a `blank` disk**, the
   first in port order — and **that disk is formatted**: the table below is
   written, and the guest prints `S7: gpt written`.
3. **If none: `ERR: no GermOS disk and no blank disk - port <p>: <word>,
   …`**, one clause per identified port in port order, and the machine
   halts. **A `gpt`, `torn` or `other` disk is never written.** The twin
   always carries its boot image on port 0 as an `other` disk beside the
   GermOS disk on port 1; on the metal the owner zeroes a drive's first
   sectors from the live USB before the first boot, and GermOS formats it.

A disk is **recognised** when its sector 1 is a valid GPT header — the
signature `EFI PART`, revision `0x00010000`, header size 92, the header
CRC-32 correct (computed over the 92 bytes with the CRC field zero),
reserved zero, `MyLBA` 1, `PartitionEntryLBA` 2, 128 entries of 128
bytes, the usable range inside the disk, the rest of the sector zero — and
its entry array (LBAs 2–33) has the CRC-32 the header names **and holds an
entry of each GermOS type GUID**. Each such partition's descriptor is
its entry's first LBA and its length in sectors (`LastLBA − FirstLBA +
1`), both required below 2^32 and inside the usable range. The first entry
of each type wins. The backup header is written on format and read never:
a damaged primary is `torn`, not recovered, this ring.

## The table the guest writes

All integers are **little endian**. `N` is the disk's sector count from
`IDENTIFY DEVICE`. Every byte not named below is **zero**. The guest writes
these thirty-six sectors, one command each, in this order: LBA 0, LBA 1,
LBAs 2–33, LBAs `N−33` … `N−2`, LBA `N−1`; then sector 0 of each partition
is written as zeros (so a stale header from an earlier life at the same
LBA can never be read back), and the two stores format themselves on the
same boot exactly as their documents say.

A disk of fewer than **67,617 sectors** (about 33 MB: the smallest whose
last usable LBA, `N − 34`, still holds the home partition's last sector,
67,583) is `ERR: disk too small for the two partitions` before anything is
written.

### LBA 0 — the protective MBR

| Offset | Size | Value |
|---|---|---|
| 0x000 | 446 | zero (no boot code, no disk signature) |
| 0x1BE | 16 | one partition entry: boot indicator `0x00`; starting CHS `00 02 00`; OS type **`0xEE`**; ending CHS `FF FF FF`; starting LBA 1 (u32); size in LBAs `min(N − 1, 0xFFFFFFFF)` (u32) |
| 0x1CE | 48 | three zero entries |
| 0x1FE | 2 | `55 AA` |

### LBA 1 — the header (and LBA `N−1`, the backup)

| Offset | Size | Type | Value |
|---|---|---|---|
| 0x00 | 8 | ASCII | `EFI PART` |
| 0x08 | 4 | u32 | revision, `0x00010000` |
| 0x0C | 4 | u32 | header size, `92` |
| 0x10 | 4 | u32 | the header's CRC-32, over the 92 bytes with this field zero |
| 0x14 | 4 | u32 | reserved, zero |
| 0x18 | 8 | u64 | `MyLBA`: `1` — the backup says `N − 1` |
| 0x20 | 8 | u64 | `AlternateLBA`: `N − 1` — the backup says `1` |
| 0x28 | 8 | u64 | `FirstUsableLBA`, `34` |
| 0x30 | 8 | u64 | `LastUsableLBA`, `N − 34` |
| 0x38 | 16 | GUID | the disk GUID, `2b74a505-e246-469d-8d73-3bfdc52a8df0` |
| 0x48 | 8 | u64 | `PartitionEntryLBA`: `2` — the backup says `N − 33` |
| 0x50 | 4 | u32 | number of entries, `128` |
| 0x54 | 4 | u32 | size of an entry, `128` |
| 0x58 | 4 | u32 | the entry array's CRC-32, over all 16,384 bytes |
| 0x5C | 420 | — | zero |

### LBAs 2–33 — the entry array (and LBAs `N−33` … `N−2`, its backup)

128 entries of 128 bytes, 16,384 bytes over 32 sectors. Entry 0 is the
notes partition, entry 1 the home; entries 2–127 are zero.

| Offset | Size | Type | Entry 0 — notes | Entry 1 — home |
|---|---|---|---|---|
| 0x00 | 16 | GUID | the type: **`50845557-ee34-4731-8b83-d1d6f14fd8c5`** (GermOS notes) | **`456d4007-d803-41a0-a661-ca736ddcf96b`** (GermOS home) |
| 0x10 | 16 | GUID | the partition: `6e5d297e-0ecb-48c5-92c8-4a93f4e98d44` | `82bc9169-ce31-4fd9-bf05-63c7521726eb` |
| 0x20 | 8 | u64 | `FirstLBA` **2048** | **34816** |
| 0x28 | 8 | u64 | `LastLBA` 34815 | 67583 |
| 0x30 | 8 | u64 | attributes, zero | zero |
| 0x38 | 72 | UTF-16LE | `GermOS notes`, NUL-padded | `GermOS home` |

Each partition is **32,768 sectors — 16 MB** — and begins on a 1 MiB
boundary (2048 sectors), the alignment every firmware and tool expects.
The type GUIDs are GermOS's own and fixed for ever. **The disk GUID and
the two partition GUIDs are fixed too**: one patient, one disk, this
stage — so the whole table is a function of `N` alone, and a checker
compares what the guest wrote with what this document's own Python builds,
byte for byte. Uniqueness across disks is carried.

### GUIDs on disk

A GUID's first three fields are stored little-endian (the mixed order the
GPT specification inherits from Microsoft); the last two are stored as
written. So `50845557-ee34-4731-8b83-d1d6f14fd8c5` is the sixteen bytes
`57 55 84 50 34 ee 31 47 8b 83 d1 d6 f1 4f d8 c5` — Python's
`uuid.UUID(...).bytes_le`. All five, as stored:

```
notes type  50845557-ee34-4731-8b83-d1d6f14fd8c5 -> 5755845034ee31478b83d1d6f14fd8c5
home type   456d4007-d803-41a0-a661-ca736ddcf96b -> 07406d4503d8a041a661ca736ddcf96b
disk        2b74a505-e246-469d-8d73-3bfdc52a8df0 -> 05a5742b46e29d468d733bfdc52a8df0
notes       6e5d297e-0ecb-48c5-92c8-4a93f4e98d44 -> 7e295d6ecb0ec54892c84a93f4e98d44
home        82bc9169-ce31-4fd9-bf05-63c7521726eb -> 6991bc8231ced94fbf0563c7521726eb
```

### The CRC

CRC-32 as the UEFI specification requires: the reflected polynomial
`0xEDB88320`, initial value all ones, final complement — the CRC of zlib,
Ethernet and PNG. Its check value over the ASCII bytes `123456789` is
**`0xCBF43926`**; the guest's routine and the checker's `zlib.crc32` both
give it, and that is how the two are known to be the same function.

## The partitions, and the two frozen formats inside them

The notes partition is a NOTEBOOK.md disk of 32,768 sectors: sector 0 of
the partition (LBA 2048) holds the `NOTEBOOK` header with journal length
**32,767**, note *n* lives at partition sector *n* (LBA 2048 + *n*), and
NOTEBOOK.md's worked example is what the partition's first two sectors
hold after `remember me`, byte for byte. The home partition is a HOME.md
disk of 32,768 sectors: the `GERMHOME` header at LBA 34816 with capacity
**32,768**, the table at partition sectors 1–8, the data from partition
sector 9 (LBA 34825). Every sector number in either document is relative
to its partition; the guest adds the partition's first LBA and nothing
else. A parser given the partition's bytes — `partition_bytes` below —
sees exactly the image it always saw.

This document supersedes one paragraph of HOME.md, "Two disks": there is
no virtio-blk, the home is not "the second virtio-blk device", and a
machine with a GermOS disk always has a home — `S7: home <N> apps` is
printed on every boot. HOME.md's "no home image: <name> not kept" case
cannot arise. Everything else in HOME.md and NOTEBOOK.md stands.

## The serial lines

On a boot that formats a blank disk the guest prints, after `S7: console
<C>x<R>`:

```
S7: gpt written
S7: disk port <p> <N> notes 2048 home 34816
S7: notebook formatted
S7: home 0 apps
```

On a boot that recognises the disk the first line is absent and the other
three report what is there (`S7: notebook <n> notes`, `S7: home <n>
apps`). So a formatting boot prints **eighteen** `S7:` lines and a
recognising boot **seventeen** — Stage 6 ring 6c's seventeen with line ten
reshaped: `<p>` is the chosen port's index, `<N>` the whole disk's sector
count from `IDENTIFY DEVICE`, and the two LBAs are the partitions' first
sectors as the table names them (2048 and 34816 on a table this document
wrote; whatever the entries say on any table it recognises).

The obs page (GLASS.md) gains three `u64` words, written once at boot,
superseding the ring 6c section's "`0x2C0` onward is zero" from `0x2C0`:

| Offset | Field | Meaning |
|---|---|---|
| `0x2C0` | `ahci_cap` | the HBA's `CAP` register |
| `0x2C8` | `ahci_pi` | the HBA's `PI` register (ports implemented) |
| `0x2D0` | `ahci_port` | the chosen port's index |

`0x2D8` onward is zero this ring.

## The errors

Every failure is a named `ERR:` line and a halt, never a silent write and
never a hang. In the order the boot can meet them:

| Line | When |
|---|---|
| `ERR: no AHCI controller on PCI bus 0` | no function of class `0x010601` |
| `ERR: no SATA disk on any AHCI port` | no implemented port with `DET` 3, `IPM` 1 and the SATA signature within the bounded wait |
| `ERR: AHCI port would not stop` | `PxCMD.CR` or `PxCMD.FR` still set after the bounded wait |
| `ERR: disk request timed out` | `PxCI` still set after the bounded wait |
| `ERR: disk request failed - task file error` | `PxIS.TFES` or `PxTFD.ERR` after a command |
| `ERR: disk sector is not 512 bytes` | `IDENTIFY DEVICE` word 106 bit 12 set with words 117–118 not 256 |
| `ERR: disk has 2^32 sectors or more - beyond this stage` | the LBA48 count does not fit 32 bits |
| `ERR: no GermOS disk and no blank disk - port 0: other, port 1: gpt` | the selection rule's third case; one clause per identified port |
| `ERR: disk too small for the two partitions` | a blank disk of fewer than 67,617 sectors |
| `ERR: disk request beyond the capacity` | a sector beyond the partition or the disk — a bug, as before |

## Worked example

A blank 64 MB disk — 131,072 sectors — after its first boot. Every byte
below is the output of the Python at the end of this document, run on
`N = 131072`; the guest writes the same bytes.

Sector 0, the protective MBR (bytes 0x000–0x1AF zero):

```
000001b0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000001c0: 0200 eeff ffff 0100 0000 ffff 0100 0000  ................
000001d0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000001e0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000001f0: 0000 0000 0000 0000 0000 0000 0000 55aa  ..............U.
```

`0200 ee` at 0x1C1: starting CHS `00 02 00`, type `0xEE`; `ffff 0100 0000`
at 0x1C8: the 131,071 sectors from LBA 1 to the end.

Sector 1, the header (zeros from 0x25C to the end of the sector):

```
00000200: 4546 4920 5041 5254 0000 0100 5c00 0000  EFI PART....\...
00000210: b723 2040 0000 0000 0100 0000 0000 0000  .# @............
00000220: ffff 0100 0000 0000 2200 0000 0000 0000  ........".......
00000230: deff 0100 0000 0000 05a5 742b 46e2 9d46  ..........t+F..F
00000240: 8d73 3bfd c52a 8df0 0200 0000 0000 0000  .s;..*..........
00000250: 8000 0000 8000 0000 b9e1 dbc8 0000 0000  ................
```

The header CRC `0x402023b7`; `MyLBA` 1, `AlternateLBA` 131,071, usable
34 … 131,038 (`deff 0100`); the disk GUID; entries at LBA 2, 128 of 128
bytes; the array CRC **`0xc8dbe1b9`**.

Sector 2, entries 0 and 1 (bytes 0x100–0x1FF of the sector, and sectors
3–33, zero):

```
00000400: 5755 8450 34ee 3147 8b83 d1d6 f14f d8c5  WU.P4.1G.....O..
00000410: 7e29 5d6e cb0e c548 92c8 4a93 f4e9 8d44  ~)]n...H..J....D
00000420: 0008 0000 0000 0000 ff87 0000 0000 0000  ................
00000430: 0000 0000 0000 0000 4700 6500 7200 6d00  ........G.e.r.m.
00000440: 4f00 5300 2000 6e00 6f00 7400 6500 7300  O.S. .n.o.t.e.s.
00000450: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000460: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000470: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000480: 0740 6d45 03d8 a041 a661 ca73 6ddc f96b  .@mE...A.a.sm..k
00000490: 6991 bc82 31ce d94f bf05 63c7 5217 26eb  i...1..O..c.R.&.
000004a0: 0088 0000 0000 0000 ff07 0100 0000 0000  ................
000004b0: 0000 0000 0000 0000 4700 6500 7200 6d00  ........G.e.r.m.
000004c0: 4f00 5300 2000 6800 6f00 6d00 6500 0000  O.S. .h.o.m.e...
000004d0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000004e0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000004f0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

`0008 0000` at 0x420 is 2048, `ff87 0000` is 34,815; `0088 0000` at 0x4A0
is 34,816, `ff07 0100` is 67,583.

Sectors 131,039–131,070 are sectors 2–33 again. Sector 131,071, the backup
header — `MyLBA` and `AlternateLBA` swapped, the entries at 131,039
(`dfff 0100`), its own CRC `0xce2cef72`, the same array CRC:

```
03fffe00: 4546 4920 5041 5254 0000 0100 5c00 0000  EFI PART....\...
03fffe10: 72ef 2cce 0000 0000 ffff 0100 0000 0000  r.,.............
03fffe20: 0100 0000 0000 0000 2200 0000 0000 0000  ........".......
03fffe30: deff 0100 0000 0000 05a5 742b 46e2 9d46  ..........t+F..F
03fffe40: 8d73 3bfd c52a 8df0 dfff 0100 0000 0000  .s;..*..........
03fffe50: 8000 0000 8000 0000 b9e1 dbc8 0000 0000  ................
```

Then, on the same boot, LBA 2048 becomes NOTEBOOK.md's header with journal
length 32,767 (`ff7f 0000 0000 0000` at its offset 0x18) and LBA 2049 five
hundred and twelve zeros; LBA 34816 becomes HOME.md's header with capacity
32,768 (`0080 0000 0000 0000` at its offset 0x28) and LBAs 34817–34824
zeros. The serial log says `S7: gpt written`, `S7: disk port 1 131072
notes 2048 home 34816`, `S7: notebook formatted`, `S7: home 0 apps`. Every
other sector of the disk is untouched. On the host, `blkid -p` names the
image `PTTYPE="gpt"` with the disk GUID as `PTUUID`, and `partx -s` lists
`GermOS notes` at 2048–34815 and `GermOS home` at 34816–67583, 16M each,
with their GUIDs.

## Parsing it cold, in Python

The checker's reader, the table builder it compares against, and the
guest's classification, and nothing more. `parse_gpt` is the recognition
rule; `classify` is the selection rule's five words; `build_gpt` is what
the guest writes; `check_table` is the byte-for-byte comparison;
`partition_bytes` hands a partition to NOTEBOOK.md's and HOME.md's own
parsers.

```python
import struct
import uuid
import zlib

SECTOR = 512
ENTRIES, ENTRY = 128, 128            # the entry array: 128 entries of 128 bytes
ENTRY_SECTORS = ENTRIES * ENTRY // SECTOR            # 32
HEADER_SIZE = 92
FIRST_USABLE = 2 + ENTRY_SECTORS                     # 34: the MBR, the header, the array
NOTES_TYPE = uuid.UUID("50845557-ee34-4731-8b83-d1d6f14fd8c5")   # GermOS notes
HOME_TYPE = uuid.UUID("456d4007-d803-41a0-a661-ca736ddcf96b")    # GermOS home
DISK_GUID = uuid.UUID("2b74a505-e246-469d-8d73-3bfdc52a8df0")
NOTES_GUID = uuid.UUID("6e5d297e-0ecb-48c5-92c8-4a93f4e98d44")
HOME_GUID = uuid.UUID("82bc9169-ce31-4fd9-bf05-63c7521726eb")
PART_SECTORS = 32768                                 # 16 MB, each partition
NOTES_FIRST = 2048                                   # 1 MiB alignment
HOME_FIRST = NOTES_FIRST + PART_SECTORS              # 34816
NOTES_NAME, HOME_NAME = "GermOS notes", "GermOS home"
CRC_CHECK = 0xCBF43926                               # crc32(b"123456789"), the standard's check value


def min_sectors():
    """The smallest disk: the last usable LBA, N - 34, must be the home
    partition's last sector or beyond."""
    return HOME_FIRST + PART_SECTORS - 1 + FIRST_USABLE


def guid_bytes(u):
    """A GUID as GPT stores it: the first three fields little-endian."""
    return u.bytes_le


def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF


def protective_mbr(n):
    entry = struct.pack("<B3sB3sII", 0x00, b"\x00\x02\x00", 0xEE, b"\xff\xff\xff", 1, min(n - 1, 0xFFFFFFFF))
    return bytes(446) + entry + bytes(48) + b"\x55\xaa"


def partition_entries():
    """The 16 KB array: entry 0 the notes partition, entry 1 the home, the rest zero."""
    def entry(type_guid, guid, first, last, name):
        nm = name.encode("utf-16-le")
        return guid_bytes(type_guid) + guid_bytes(guid) + struct.pack("<QQQ", first, last, 0) + nm + bytes(72 - len(nm))
    data = entry(NOTES_TYPE, NOTES_GUID, NOTES_FIRST, NOTES_FIRST + PART_SECTORS - 1, NOTES_NAME)
    data += entry(HOME_TYPE, HOME_GUID, HOME_FIRST, HOME_FIRST + PART_SECTORS - 1, HOME_NAME)
    return data + bytes(ENTRIES * ENTRY - len(data))


def gpt_header(n, my_lba, alt_lba, entries_lba, entries_crc):
    """One header sector; the CRC computed over the 92 bytes with its own field zero."""
    body = b"EFI PART" + struct.pack("<IIIIQQQQ", 0x00010000, HEADER_SIZE, 0, 0,
                                     my_lba, alt_lba, FIRST_USABLE, n - FIRST_USABLE)
    body += guid_bytes(DISK_GUID) + struct.pack("<QIII", entries_lba, ENTRIES, ENTRY, entries_crc)
    body = body[:16] + struct.pack("<I", crc32(body)) + body[20:]
    return body + bytes(SECTOR - HEADER_SIZE)


def build_gpt(n):
    """Every sector the guest writes when it formats a blank disk of n
    sectors, as {lba: 512 bytes}: the MBR, the header, the 32 array
    sectors, the backup array at n-33, the backup header at n-1."""
    if n < min_sectors():
        raise ValueError("a disk of %d sectors is too small; %d is the least" % (n, min_sectors()))
    entries = partition_entries()
    ecrc = crc32(entries)
    out = {0: protective_mbr(n), 1: gpt_header(n, 1, n - 1, 2, ecrc), n - 1: gpt_header(n, n - 1, 1, n - 33, ecrc)}
    for i in range(ENTRY_SECTORS):
        out[2 + i] = entries[i * SECTOR:(i + 1) * SECTOR]
        out[n - 33 + i] = entries[i * SECTOR:(i + 1) * SECTOR]
    return out


def parse_header(hdr, n):
    """A header sector by the recognition rule: the signature, revision 1.0,
    size 92, its own CRC, MyLBA 1, 128 entries of 128 bytes at LBA 2, the
    usable range inside the disk, the tail zero. Returns the entries' CRC."""
    if hdr[0:8] != b"EFI PART":
        raise ValueError("no EFI PART signature")
    rev, size, hcrc, res, my, alt, first, last = struct.unpack_from("<IIIIQQQQ", hdr, 8)
    elba, count, esize, ecrc = struct.unpack_from("<QIII", hdr, 72)
    if rev != 0x00010000 or size != HEADER_SIZE or res != 0:
        raise ValueError("header revision %#x size %d reserved %d" % (rev, size, res))
    if crc32(hdr[:16] + bytes(4) + hdr[20:HEADER_SIZE]) != hcrc:
        raise ValueError("header CRC does not match")
    if my != 1 or elba != 2 or count != ENTRIES or esize != ENTRY:
        raise ValueError("MyLBA %d entries at %d, %d of %d bytes" % (my, elba, count, esize))
    if alt >= n or first < FIRST_USABLE or last >= n or last < first:
        raise ValueError("alternate %d usable %d..%d on a disk of %d" % (alt, first, last, n))
    if any(hdr[HEADER_SIZE:]):
        raise ValueError("header tail not zero")
    return ecrc, (first, last)


def parse_entries(entries, usable):
    out = []
    for i in range(ENTRIES):
        e = entries[i * ENTRY:(i + 1) * ENTRY]
        if not any(e[0:16]):
            if any(e):
                raise ValueError("entry %d: unused but not zero" % i)
            continue
        t = uuid.UUID(bytes_le=e[0:16])
        g = uuid.UUID(bytes_le=e[16:32])
        first, last, attrs = struct.unpack_from("<QQQ", e, 32)
        name = e[56:128].decode("utf-16-le").split("\0", 1)[0]
        if first < usable[0] or last > usable[1] or last < first:
            raise ValueError("entry %d: %d..%d outside the usable range" % (i, first, last))
        out.append({"index": i, "type": t, "guid": g, "first": first, "last": last,
                    "sectors": last - first + 1, "attrs": attrs, "name": name})
    return out


def parse_gpt(data):
    """The whole disk, by the guest's recognition rule (the primary header,
    the array, both type GUIDs present). Returns {"sectors", "disk_guid",
    "entries", "notes": (first, sectors), "home": (first, sectors)}.
    ValueError on anything the document forbids."""
    if len(data) % SECTOR:
        raise ValueError("not a whole number of sectors")
    n = len(data) // SECTOR
    if n < 2 + ENTRY_SECTORS:
        raise ValueError("too short to hold a table")
    ecrc, usable = parse_header(data[SECTOR:2 * SECTOR], n)
    entries = data[2 * SECTOR:(2 + ENTRY_SECTORS) * SECTOR]
    if crc32(entries) != ecrc:
        raise ValueError("entry array CRC does not match")
    parsed = parse_entries(entries, usable)
    found = {}
    for e in parsed:
        for key, t in (("notes", NOTES_TYPE), ("home", HOME_TYPE)):
            if e["type"] == t and key not in found:
                found[key] = (e["first"], e["sectors"])
    if "notes" not in found or "home" not in found:
        raise ValueError("a valid table without both GermOS partitions (found %s)" % sorted(found))
    return {"sectors": n, "disk_guid": uuid.UUID(bytes_le=data[SECTOR + 56:SECTOR + 72]),
            "entries": parsed, "notes": found["notes"], "home": found["home"]}


def classify(data):
    """What a disk holds, in the guest's five words: germos, blank, gpt (a
    valid table without both GermOS partitions), torn (the signature with
    an invalid header or array), other (an MBR, a boot sector, data)."""
    if len(data) >= 2 * SECTOR and not any(data[:2 * SECTOR]):
        return "blank"
    try:
        parse_gpt(data)
        return "germos"
    except ValueError as exc:
        if data[SECTOR:SECTOR + 8] != b"EFI PART":
            return "other"
        return "gpt" if "without both" in str(exc) else "torn"


def partition_bytes(data, part):
    first, sectors = part
    return data[first * SECTOR:(first + sectors) * SECTOR]


def check_table(data):
    """A disk the guest formatted, from the host: every sector build_gpt
    names byte-identical, the backup included. Returns a list of problems."""
    n = len(data) // SECTOR
    problems = []
    try:
        want = build_gpt(n)
    except ValueError as exc:
        return [str(exc)]
    for lba in sorted(want):
        got = data[lba * SECTOR:(lba + 1) * SECTOR]
        if got != want[lba]:
            off = next(i for i in range(SECTOR) if got[i] != want[lba][i])
            problems.append("sector %d differs from the document's table at byte 0x%x" % (lba, off))
    return problems
```
