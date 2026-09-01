# NOTEBOOK.md — the on-disk format of the notebook

**Stage 3, plan item 2. Frozen behind the hook from item 7.** The assembler
implements this document and the acceptance checker parses by it; one text,
two readers. If it is wrong, that is a spec question for the owner, not an
edit.

The notebook is the smallest honest filesystem that proves persistence: a
magic header in the first sector and an append-only journal of notes behind
it, one note per sector. It is the store-of-plans spirit at kilobyte scale —
a format a reader can check with `xxd`.

## The disk

A raw image of 512-byte sectors, numbered from 0. The image the harness makes
is 16 MB — 32768 sectors — but nothing in the format depends on that number
beyond the header's journal length. All multi-byte integers are **little
endian**. Every byte not named below is **zero**.

## Sector 0 — the header

| Offset | Size | Type | Value |
|---|---|---|---|
| 0x000 | 8 | ASCII | `NOTEBOOK` — the magic |
| 0x008 | 4 | u32 | format version, `1` |
| 0x00C | 4 | u32 | sector size in bytes, `512` |
| 0x010 | 8 | u64 | first journal sector, `1` |
| 0x018 | 8 | u64 | journal length in sectors: the disk's capacity in sectors minus 1 |
| 0x020 | 480 | — | zero |

A disk is **recognised** when bytes 0–7 read `NOTEBOOK` and the version is 1.
Anything else — a blank disk, a disk from some other life — is **formatted**
on boot: the header above is written to sector 0 and sector 1 is written as
512 zero bytes, so a stale record from an earlier use of the disk can never
be read back as a note. The machine then logs `S3: notebook formatted`.

The header carries **no note count**. A journal recovers its count by
scanning (below); a counter in the header would need a second write per note,
and a second write is a second window for a torn state.

## Sectors 1 onward — the journal

One note per sector, in order, with no gaps. Note *n* (counting from 1) lives
in sector *n*.

| Offset | Size | Type | Value |
|---|---|---|---|
| 0x000 | 4 | ASCII | `NOTE` — the record magic |
| 0x004 | 4 | u32 | sequence number: *n*, the note's number, equal to its sector index |
| 0x008 | 2 | u16 | length of the text in bytes, **1 to 500** inclusive |
| 0x00A | 2 | u16 | reserved, zero |
| 0x00C | *length* | bytes | the text: printable ASCII, each byte **0x20 to 0x7E** inclusive |
| 0x00C + *length* | rest | — | zero, to the end of the sector |

A sector is a **valid record** when all of these hold: the magic is `NOTE`,
the sequence number equals the sector index, the length is in range, the
reserved field is zero, every text byte is printable, and every byte after
the text is zero. **The journal ends at the first sector that is not a valid
record.** The number of valid records before it is the note count *N*, and
the machine logs `S3: notebook N notes` (`1 notes` included — the word is
never inflected). The next note is written to sector *N* + 1.

Both readers — the assembler on boot and the checker on the host — apply the
same rule, so a torn or foreign sector ends the journal in both places
identically.

## What becomes a note

The bytes typed at the prompt between one Enter and the next, after
backspaces are applied. Every such line is appended **before the next prompt
appears**: a prompt on screen means the note is on the disk.

- An **empty line is not a note**. Enter on an empty line writes nothing.
- A line is capped at **500 bytes**, the record's capacity. A key that would
  make the line longer is ignored — not echoed, not drawn — so the screen and
  the disk always agree.
- When the journal is **full** — the next sector index would equal the disk's
  capacity — the line is not written and the machine carries on. No error is
  raised over a full diary.

On a recognised disk, every note is drawn on the console on boot, in order,
one per line from column 0, text only, immediately above the first prompt.
Notes are drawn on the console only; they are never sent over serial.

## Worked example

A fresh 16 MB image after the first boot, then `remember me` and Enter typed
at the prompt. This is exactly what acceptance test 3 demands, byte for byte.

Sector 0:

```
00000000: 4e4f 5445 424f 4f4b 0100 0000 0002 0000  NOTEBOOK........
00000010: 0100 0000 0000 0000 ff7f 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
... (zeros to 000001f0)
000001f0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

`ff7f 0000 0000 0000` is 32767: the 32768 sectors of a 16 MB disk, less the
header.

Sector 1:

```
00000200: 4e4f 5445 0100 0000 0b00 0000 7265 6d65  NOTE........reme
00000210: 6d62 6572 206d 6500 0000 0000 0000 0000  mber me.........
00000220: 0000 0000 0000 0000 0000 0000 0000 0000  ................
... (zeros to 000003f0)
000003f0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

Sequence 1, length 11 (`0b00`), reserved zero, the eleven bytes of text, then
zeros. Sector 2 is all zero — not a record — so the journal holds exactly one
note, and the next boot logs `S3: notebook 1 notes`.

## Parsing it cold, in Python

The checker's parser is this, and nothing more:

```python
import struct
def parse_notebook(data):
    if data[0:8] != b"NOTEBOOK": raise ValueError("no magic")
    version, sector, first, length = struct.unpack_from("<IIQQ", data, 8)
    if version != 1 or sector != 512 or first != 1: raise ValueError("bad header")
    if length != len(data) // 512 - 1: raise ValueError("bad journal length")
    if any(data[0x20:0x200]): raise ValueError("header padding not zero")
    notes = []
    for n in range(1, len(data) // 512):
        rec = data[n * 512:(n + 1) * 512]
        if rec[0:4] != b"NOTE": break
        seq, ln, res = struct.unpack_from("<IHH", rec, 4)
        if seq != n or not 1 <= ln <= 500 or res != 0: break
        text = rec[12:12 + ln]
        if any(b < 0x20 or b > 0x7E for b in text) or any(rec[12 + ln:]): break
        notes.append(text.decode("ascii"))
    return notes
```
