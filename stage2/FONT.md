# stage2/font8x8.bin — provenance

One font, used twice: `stage2.asm` includes this file verbatim (`incbin`), and
the frozen pixel checker `stage2/checktext.py` renders its expected text from
the same bytes. The file is frozen alongside the acceptance tests from plan
item 6 — the checker's expectations are derived from it, so an editable font
would be an editable criterion.

## Source

- **Project:** font8x8 by Daniel Hepper — <https://github.com/dhepper/font8x8>
- **File:** `font8x8_basic.h`, fetched from
  `https://raw.githubusercontent.com/dhepper/font8x8/master/font8x8_basic.h`
  on 31 August 2026
- **Upstream sha256:**
  `49d8df366296b203ca3211bc0672cf2a762135bf12710735b6292756b19dffd5`
- **Licence:** public domain, per the upstream README ("Every pixel is free" —
  the font data is derived from the public-domain 8x8 font used by many retro
  systems). No licensing questions, retro-correct — the owner's decision 2 at
  spec approval.

## Layout

1024 bytes: 128 glyphs (ASCII 0x00–0x7F), 8 bytes per glyph at offset
`codepoint * 8`. One byte per row, top row first. **Bit 0 (LSB) is the
leftmost pixel.**

- **font8x8.bin sha256:**
  `66bba26c3b351634ed4dd3ad7561f6cc892e1727d4887204bd4d1d3883a18b37`

Both hashes are also pinned in `stage2/plan.md`, recorded when the layout was
verified by rendering glyphs in the planning session.

## Conversion recipe

Mechanical extraction of the 128 `{ 0x.., ... }` initialisers, in order:

```python
import re
raw = open('font8x8_basic.h').read()
blocks = re.findall(
    r'\{\s*((?:0x[0-9A-Fa-f]{2}\s*,\s*){7}0x[0-9A-Fa-f]{2})\s*\}', raw)
assert len(blocks) == 128
data = bytes(int(x, 16) for b in blocks
             for x in re.findall(r'0x[0-9A-Fa-f]{2}', b))
open('font8x8.bin', 'wb').write(data)
```

## Evidence

Glyph 0x41 ('A'), bytes `0c 1e 33 33 3f 33 33 00`, rendered LSB-leftmost:

```
..##....
.####...
##..##..
##..##..
######..
##..##..
##..##..
........
```
