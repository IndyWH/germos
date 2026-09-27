#!/usr/bin/env python3
"""Stage 8 ring 8a - the molt's host tool: stage8/PARTS.md and
stage8/SEED.md read cold.

Both documents' Python blocks are executed here as this module's
definitions, and their prose tables - the header, the service table, the
frame, the install checks, the numbers of the watchdog, the Esc window and
the health mark, the fixture table - are parsed and compared with those
definitions, so the tool and the documents cannot drift. What SEED.md
leaves to this tool is the git plumbing: resolving a record line's commit,
its ancestry and its committer date, the record's own history, and running
rebuild_script. Frozen behind the hook from ring 8a plan item 13.

Modes (from the repo root):

  --example        both documents' worked examples reproduced byte for byte
                   (test 1); --parts DOC and --seeddoc DOC read another copy
  --disk IMG       a GermOS SATA disk image (DISK.md's table): the notes
                   partition's molt notes as the table `! molt` draws, and
                   each slot's home entry with the door's verdict on it
  --serial LOG     a serial log or the HP's chart: its "molt:" lines read
                   back as notes, then the same table; its S8: lines listed
  --seed           the record by SEED.md's rules against git, every seed
                   rebuilt in a clean workspace, and the current build named

Exit 0 when everything agrees with the documents; 1 when a document does
not parse, an example is not reproduced, a molt note breaks PARTS.md's
grammar, or the record or a rebuild disagrees.
"""

import hashlib
import os
import re
import struct
import subprocess
import sys
import textwrap
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PARTS_DOC = os.path.join(HERE, "PARTS.md")
SEED_DOC = os.path.join(HERE, "SEED.md")
FIXTURE_DIR = os.path.join(HERE, "fixtures")
FATES = ["good", "wrong", "hang", "fault", "liar"]
MODULES = ("hashlib", "re", "struct", "datetime")


# ------------------------------------------------------- reading prose --

def _fences(text):
    """Every fenced block, in order: (info string, body)."""
    return [(m.group(1).strip(), m.group(2).rstrip("\n"))
            for m in re.finditer(r"^```([^\n]*)\n(.*?)^```", text, re.M | re.S)]


def _section(text, heading, level=2):
    """From a heading that begins with `heading` to the next of its level or above."""
    marks = "#" * level
    m = re.search(r"^%s %s.*?(?=^#{1,%d} |\Z)" % (marks, re.escape(heading), level), text, re.M | re.S)
    if not m:
        raise ValueError("no section %r" % heading)
    return m.group(0)


def _norm(s):
    return re.sub(r"\s+", " ", s)


def _ticks(s):
    """The backticked spans of prose, fenced blocks removed first."""
    return re.findall(r"`([^`]+)`", _norm(re.sub(r"^```[^\n]*\n.*?^```", "", s, flags=re.M | re.S)))


def _rows(section, first=0):
    """The rows of the section's table number `first`, header and rule dropped;
    cells split on unescaped pipes and stripped."""
    tables, cur = [], []
    for line in section.split("\n"):
        if line.startswith("|"):
            cur.append(line)
        elif cur:
            tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    if len(tables) <= first:
        raise ValueError("no table %d in %r" % (first, section[:40]))
    rows = tables[first]
    if len(rows) < 3 or not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", rows[1].replace(" ", "")):
        raise ValueError("a table without a header and a rule in %r" % section[:40])
    return [[c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", r.strip())[1:-1]] for r in rows[2:]]


def _num(s):
    return int(s.replace(",", ""))


def _find(pattern, text, what):
    m = re.search(pattern, _norm(text))
    if not m:
        raise ValueError("the document does not say %s where it should" % what)
    return m


def _bullets(section):
    """The section's list items, each joined onto one line."""
    out = []
    for line in section.split("\n"):
        if line.startswith("- "):
            out.append(line[2:])
        elif out and line.startswith("  ") and line.strip():
            out[-1] += " " + line.strip()
    return out


def xxd(data, base=0):
    """`xxd`'s default rendering, line for line."""
    out = []
    for off in range(0, len(data), 16):
        chunk = data[off:off + 16]
        cells = ["%02x" % b for b in chunk] + ["  "] * (16 - len(chunk))
        hexpart = " ".join("".join(cells[i:i + 2]) for i in range(0, 16, 2))
        text = "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in chunk)
        out.append("%08x: %s  %s" % (base + off, hexpart, text))
    return "\n".join(out)


# ---------------------------------------------------- the two documents --

def parse_parts_md(text):
    """PARTS.md's data: its tables and numbers, its worked examples, its Python.
    Fails loudly on a shape it does not know."""
    doc = {}
    part = _section(text, "A part")
    doc["header_rows"] = [(int(r[0]), r[1], r[2]) for r in _rows(part, 0)]
    doc["part_max"] = _num(_find(r"at most \*\*([\d,]+) bytes\*\*", part, "the part's largest size").group(1))
    svc = _section(text, "ABI 3's service table")
    doc["service_rows"] = [(int(r[0]), int(r[1]), r[2]) for r in _rows(svc, 0)]
    req = _section(text, "The request and the part frame")
    doc["frame_rows"] = [(int(r[0]), r[1], r[2]) for r in _rows(req, 0)]
    doc["install_whys"] = [_ticks(r[1])[0] for r in _rows(req, 1)]
    words = _section(text, "The four words")
    doc["refusals"] = [b for i, b in _fences(words) if i == ""][0].split("\n")
    wd = _section(text, "The watchdog")
    doc["deadline_s"] = int(_find(r"`TCO_TMR` for a (\d+) s deadline", wd, "the deadline").group(1))
    doc["tick_s"] = float(_find(r"is clocked at approximately ([\d.]+) seconds", wd, "the TCO's tick").group(1))
    doc["tco_tmr"] = int(_find(r"gives `TCO_TMR` = (\d+)\*\*", wd, "TCO_TMR's value").group(1))
    doc["pet_ms"] = _num(_find(r"at most one reload per ([\d,]+) ms", wd, "the pet's rate").group(1))
    doc["hold_s"] = int(_find(r"`HOLD_S` = twice the deadline = (\d+) s", wd, "HOLD_S").group(1))
    health = _section(text, "The health mark")
    doc["health_ms"] = _num(_find(r"([\d,]+) ms by the TSC after", health, "the health window").group(1))
    esc = _section(text, "Esc at power-on")
    doc["w_ms"] = _num(_find(r"W = ([\d,]+) ms", esc, "the Esc window").group(1))
    m = _find(r"set 1, `0x([0-9A-F]{2})`\*\* \(break `0x([0-9A-F]{2})`\).*?set 2, `0x([0-9A-F]{2})`\*\* "
              r"\(break `0x([0-9A-F]{2}) 0x([0-9A-F]{2})`\)", esc, "the Esc codes")
    doc["esc"] = tuple(int(g, 16) for g in m.groups())
    thr = _section(text, "The threshold, its floor, and probation")
    doc["floor"] = int(_find(r"at least (\d+) boot", thr, "the floor").group(1))
    doc["probation"] = int(_find(r"\*\*Probation\*\* is (\d+) healthy boots", thr, "probation").group(1))
    notes = _section(text, "The notes")
    doc["disagree_notes"] = {"sixteen": 16}[_find(r"the first (\w+) a boot", notes, "the disagree notes' limit").group(1)]
    doc["s8_lines"] = [_ticks(r[0])[0] for r in _rows(_section(text, "The serial lines"), 0)]
    fx = _section(text, "The fixtures")
    doc["fixtures"] = []
    for r in _rows(fx, 0):
        f, name = _ticks(r[0])[0], _ticks(r[1])[0]
        thr_cell = [_num(x) for x in re.findall(r"[\d,]+\d|\d", r[4])]
        if len(thr_cell) != 3:
            raise ValueError("the fixture table's threshold for %s is not three numbers" % f)
        doc["fixtures"].append((f, name, tuple(thr_cell), r[3]))
    ex = _section(text, "Worked examples")
    doc["examples"] = {}
    for m in re.finditer(r"^### (.+?)\n(.*?)(?=^### |\Z)", ex, re.M | re.S):
        doc["examples"][m.group(1).strip()] = m.group(2)
    py = [b for i, b in _fences(_section(text, "Parsing it cold")) if i == "python"]
    if len(py) != 1:
        raise ValueError("PARTS.md's Python section wants one python fence")
    doc["python"] = py[0]
    return doc


def parse_seed_md(text):
    """SEED.md's data: the line's field table, the known answers, the worked example, its Python."""
    doc = {}
    doc["fields"] = [_ticks(r[0])[0] for r in _rows(_section(text, "The record"), 0)]
    doc["kat"] = []
    for r in _rows(_section(text, "SHA-256's known answers"), 0):
        msg = _ticks(r[0])[0] if "`" in r[0] else ""
        doc["kat"].append((msg.encode("ascii"), _ticks(r[1])[0]))
    ex = _section(text, "Worked example")
    doc["example"] = ex
    doc["example_fences"] = [b for i, b in _fences(ex) if i == ""]
    doc["refused"] = [(r[0], _ticks(r[1])[0]) for r in _rows(ex, 0)]
    py = [b for i, b in _fences(_section(text, "Parsing it cold")) if i == "python"]
    if len(py) != 1:
        raise ValueError("SEED.md's Python section wants one python fence")
    doc["python"] = py[0]
    return doc


def _exec(source, path):
    ns = {}
    exec(compile(source, path, "exec"), ns)
    return {k: v for k, v in ns.items() if not k.startswith("__")}


def load(parts_path=PARTS_DOC, seed_path=SEED_DOC):
    """Execute both documents' Python and check it against their prose.
    Returns (the parsed documents, one namespace holding both blocks)."""
    ptext = open(parts_path, encoding="utf-8").read()
    stext = open(seed_path, encoding="utf-8").read()
    pdoc, sdoc = parse_parts_md(ptext), parse_seed_md(stext)
    pns, sns = _exec(pdoc["python"], parts_path), _exec(sdoc["python"], seed_path)
    clash = (set(pns) & set(sns)) - set(MODULES)
    if clash:
        raise ValueError("PARTS.md and SEED.md both define %s" % sorted(clash))
    n = types.SimpleNamespace(**pns, **{k: v for k, v in sns.items() if k not in pns})
    problems = []

    def want(ok, what):
        if not ok:
            problems.append(what)

    rows = pdoc["header_rows"]
    want(all(rows[i][0] + int(rows[i][1]) == rows[i + 1][0] for i in range(len(rows) - 2)),
         "the header table's rows do not follow one another")
    want(rows[-1][0] == n.PART_HEADER and rows[-1][1] == "B", "the header table's body is not at PART_HEADER")
    want(rows[-2][0] + int(rows[-2][1]) == n.PART_HEADER, "the header table's last field does not end at PART_HEADER")
    want(pdoc["part_max"] == n.PART_MAX, "the prose's largest part is not PART_MAX")
    svc = pdoc["service_rows"]
    want(all(svc[i][0] + svc[i][1] == svc[i + 1][0] for i in range(len(svc) - 1)), "the service table's rows do not follow one another")
    want(_ticks(svc[0][2])[-1] == str(n.ABI), "the service table's ABI is not ABI")
    want(_ticks(svc[1][2])[-1] == str(svc[-1][0] + svc[-1][1]), "the service table's size is not its last offset and size")
    fr = pdoc["frame_rows"]
    want(all(fr[i][0] + int(fr[i][1]) == fr[i + 1][0] for i in range(len(fr) - 1)), "the frame table's rows do not follow one another")
    want(fr[-1][0] == 4 + n.FRAME_HEADER and _ticks(fr[-1][1]) == ["L"], "the frame table's part is not after the 32-byte header")
    want(_ticks(fr[1][2])[0] == "0x%02x" % n.KIND_PART, "the frame table's kind is not KIND_PART")
    want(_ticks(fr[2][2])[0] == str(n.ABI), "the frame table's ABI is not ABI")
    want(pdoc["install_whys"] == ["not a part frame", "too large", "below the floor", "bad header", "bad hash", "wrong slot"],
         "the install checks' whys are not the six this tool knows, in order")
    want(pdoc["deadline_s"] == n.DEADLINE_S, "the prose's deadline is not DEADLINE_S")
    want(pdoc["tick_s"] == n.TICK_S, "the prose's tick is not TICK_S")
    want(pdoc["tco_tmr"] == n.tco_tmr(), "the prose's TCO_TMR is not tco_tmr()")
    want(pdoc["pet_ms"] == n.PET_MS, "the prose's pet rate is not PET_MS")
    want(pdoc["hold_s"] == n.HOLD_S, "the prose's HOLD_S is not HOLD_S")
    want(pdoc["health_ms"] == 1000 * n.HEALTH_S, "the prose's health window is not HEALTH_S")
    want(pdoc["w_ms"] == n.W_MS, "the prose's W is not W_MS")
    e = pdoc["esc"]
    want((e[0], e[1]) == n.ESC_SET1 and (e[2], e[3]) == n.ESC_SET2 and e[4] == e[2], "the prose's Esc codes are not ESC_SET1 and ESC_SET2")
    want(pdoc["floor"] == n.FLOOR_BOOTS, "the prose's floor is not FLOOR_BOOTS")
    want(pdoc["probation"] == n.PROBATION, "the prose's probation is not PROBATION")
    want(pdoc["disagree_notes"] == n.DISAGREE_NOTES, "the prose's disagree notes are not DISAGREE_NOTES")
    want("S8: watchdog tco %d s" % n.DEADLINE_S in pdoc["s8_lines"], "the serial lines lack the armed watchdog's line")
    fx = pdoc["fixtures"]
    want([f for f, _, _, _ in fx] == ["i8042-" + f for f in FATES], "the fixture table's rows are not the five fates in order")
    want({name: t for _, name, t, _ in fx} == n.FIXTURES, "the fixture table's thresholds are not FIXTURES")
    want(all(f == "i8042-" + name for f, name, _, _ in fx), "a fixture's name field is not its fate")
    want(fx[FATES.index("hang")][3] == "the %dth byte after `init`" % n.HANG_BYTE, "the fixture table's hang point is not HANG_BYTE")
    want(sdoc["fields"] == ["<n>", "<sha256>", "<bytes>", "<commit>", "<yyyy-mm-dd>", "<version>"],
         "SEED.md's field table is not the line's six fields")
    want(sdoc["kat"] == n.KAT, "SEED.md's known-answer table is not KAT")
    want(n.KAT[0] == (b"abc", n.KAT_ABC), "SEED.md's abc answer is not PARTS.md's")
    if problems:
        raise ValueError("; ".join(problems))
    return (pdoc, sdoc), n


DOCUMENTS, _NS = load()
for _name, _value in vars(_NS).items():
    if _name not in MODULES:
        globals()[_name] = _value


# ------------------------------------------------------- the fixtures --

def fixture_path(fate, ext=".bin"):
    return os.path.join(FIXTURE_DIR, "i8042-%s%s" % (fate, ext))


def fixture(fate):
    with open(fixture_path(fate), "rb") as fh:
        return fh.read()


def fixture_frame(fate, source=0):
    """The frame the mock must serve for a fixture: its .bin, the fixture table's threshold."""
    return part_frame(fixture(fate), FIXTURES[fate], source)


def install_note(slot, part, threshold):
    return "molt %s shadow %s %d %d %d" % ((slot, sha16(hashlib.sha256(part).hexdigest())) + tuple(threshold))


def sha_k_in(efi):
    """Offsets in a build where the 64 round constants lie, little endian, in order."""
    k = struct.pack("<64I", *sha_k_rule())
    return [m.start() for m in re.finditer(re.escape(k), efi)]


def _commas(v):
    return "{:,}".format(v)


def render_fixture(fate):
    """The worked example of one fixture, as PARTS.md gives it."""
    part = fixture(fate)
    f = check_part(part, "i8042")
    frame = fixture_frame(fate)
    build = f["build"]
    out = ["#### `i8042-%s`" % fate, ""]
    out.append("%s bytes: the header and a %s-byte body. `init` at %d, `byte` at %d and `health` at %d. "
               "Its build is `%s`, so its `<sha16>` is `%s`, and its install note is `%s`."
               % (_commas(len(part)), _commas(f["body"]), f["init"], f["byte"], f["health"], build,
                  sha16(build), install_note("i8042", part, FIXTURES[fate])))
    out += ["", "```", xxd(part[:PART_HEADER]), "```", ""]
    out.append("Its frame is %s bytes (`N` = %s = 32 + %s):"
               % (_commas(len(frame)), _commas(len(frame) - 4), _commas(len(part))))
    out += ["", "```", xxd(frame[:40]), "```"]
    if fate == "fault":
        off = ud2_offset(part)
        out += ["", "Its one `ud2` is at byte %d of the part, so its blame line is `%s`."
                % (off, blame_line(6, "i8042", off))]
    if fate == "liar":
        good = fixture("good")
        stored = liar_stored(part)
        out += ["", "%s The torn write turns byte %d from `%02x` to `%02x`. The home entry keeps the build `%s`, "
                "the stored bytes now hash to `%s`, and the door says `S8: part i8042 bad hash`."
                % ("Its body is `good`'s byte for byte, and only the name field differs."
                   if part[PART_HEADER:] == good[PART_HEADER:] else "Its body is not `good`'s.",
                   PART_HEADER, part[PART_HEADER], stored[PART_HEADER], build, hashlib.sha256(stored).hexdigest())]
    return "\n".join(textwrap.fill(p, 74, break_long_words=False, break_on_hyphens=False)
                     if p and not p.startswith(("#", "`", "0")) else p for p in out)


# ------------------------------------------------- the worked examples --

def _sub(s, names):
    """A worked example's stand-in letters (`G`, `H`) replaced by the builds they stand for."""
    return " ".join(names.get(w, w) for w in s.split(" "))


def check_examples(docs, n):
    """Every worked example of both documents, reproduced from the rules. Returns problems."""
    pdoc, sdoc = docs
    ex = pdoc["examples"]
    problems = []

    def want(ok, what):
        if not ok:
            problems.append(what)

    # The twin's request and key.
    s = ex["The twin's request and key"]
    t = _ticks(s)
    ident = t[0]
    m = re.fullmatch(r"cpu ([0-9a-f]{8}) pci ([0-9a-f]{4}):([0-9a-f]{4}):([0-9a-f]{2})", ident)
    want(m and n.identity(*(int(g, 16) for g in m.groups())) == ident, "request: the identity is not identity()'s")
    body = n.request_body("i8042", ident)
    frame = n.request_frame("i8042", ident)
    want(body in t, "request: the body is not request_body()'s")
    want("%d bytes, and the frame is %d" % (len(body), len(frame)) in _norm(s), "request: the lengths")
    want([b for i, b in _fences(s) if i == ""] == [xxd(frame)], "request: the frame's bytes")
    want(n.molt_key("i8042", ident) in t, "request: the key is not molt_key()'s")

    # A part and its frame.
    s = ex["A part and its frame"]
    t = _ticks(s)
    ebody = bytes([0xC3, 0xC3, 0x31, 0xC0, 0xC3])
    part = n.part_header("i8042", "example", ebody, 96, 97, 98) + ebody
    build = hashlib.sha256(part).hexdigest()
    frame = n.part_frame(part, (1, 100, 100))
    fences = [b for i, b in _fences(s) if i == ""]
    want(fences == [xxd(part), xxd(frame[:40])], "part: the part's or the frame's bytes")
    want(hashlib.sha256(ebody).hexdigest() in t, "part: the body's hash")
    want("the part is %d bytes" % len(part) in _norm(s), "part: its length")
    want(build in t and n.sha16(build) in t, "part: its build and sha16")
    want("is %d bytes (`N` = %d = 32 + %d)" % (len(frame), len(frame) - 4, len(part)) in _norm(s), "part: the frame's length")
    try:
        f = n.check_part(part, "i8042")
        want(f["build"] == build and f["name"] == "example", "part: check_part's fields")
        pf = n.parse_frame(frame, "i8042")
        want(pf[0] == "part" and pf[2] == part and pf[3] == (1, 100, 100) and pf[4] == 0, "part: parse_frame's fields")
    except ValueError as exc:
        problems.append("part: refused by its own rules: %s" % exc)
    stored = n.liar_stored(part)
    want("from `%02x` to `%02x`" % (part[96], stored[96]) in _norm(s), "part: the torn write's byte")
    want(hashlib.sha256(stored).hexdigest() in t, "part: the torn write's hash")
    try:
        n.check_part(stored)
        problems.append("part: the torn write passes check_part")
    except ValueError as exc:
        want(str(exc) == "bad hash", "part: the torn write is %s, not bad hash" % exc)

    # The install checks, each why produced by parse_frame in the table's order.
    good = fixture("good")
    gf = n.part_frame(good, n.FIXTURES["good"])
    big = bytearray(n.part_frame(b"\0" * (n.PART_MAX + 1), (1, 1, 1)))
    bad_magic = bytearray(gf)
    bad_magic[36] ^= 0x20
    bad_body = bytearray(gf)
    bad_body[36 + n.PART_HEADER] ^= 0x01
    cases = [(gf[:-1], "i8042"), (bytes(big), "i8042"), (n.part_frame(good, (0, 100, 100)), "i8042"),
             (bytes(bad_magic), "i8042"), (bytes(bad_body), "i8042"), (gf, "disk")]
    got = []
    for fb, slot in cases:
        try:
            n.parse_frame(fb, slot)
            got.append("accepted")
        except ValueError as exc:
            got.append(str(exc))
    want(got == pdoc["install_whys"], "install checks: parse_frame answers %r" % got)
    want(n.parse_frame(n.part_frame(good, (1, 0, 0)), "i8042")[0] == "part", "install checks: the floor is boots alone")

    # The refusals the take and the undo draw are the four words' list.
    inst = "molt i8042 shadow %s 1 100 100" % ("a" * 16)
    said = [n.take_of(["hello"], "disk"), n.take_of(["hello"], "i8042"), n.take_of([inst, "molt i8042 live " + "a" * 16], "i8042"),
            n.undo_of(["hello"], None)[0],
            re.sub(r"(\w+) (\d+)/(\d+)", lambda m: "%s <%s>/<%s>" % (m.group(1), m.group(1)[0], m.group(1)[0].upper()),
                   n.take_of([inst], "i8042"))]
    want(said[:4] == ["unknown slot", "no part to take", "already live", "nothing to undo"]
         and all(x in pdoc["refusals"] for x in said), "refusals: the take and the undo draw %r" % said)

    # The fixtures' frames and the liar.
    s = ex["The fixtures' frames and the liar"]
    subs = {m.group(1): m.group(0).rstrip("\n")
            for m in re.finditer(r"^#### `i8042-(\w+)`\n.*?(?=^#### |\Z)", s, re.M | re.S)}
    want(list(subs) == FATES, "fixtures: the subsections are %r, not the five fates in order" % list(subs))
    for fate in FATES:
        if fate not in subs:
            continue
        mine = render_fixture(fate)
        want([b for _, b in _fences(subs[fate])] == [b for _, b in _fences(mine)], "fixtures: %s's bytes" % fate)
        want(_norm(subs[fate]).strip() == _norm(mine).strip(), "fixtures: %s's text is not render_fixture's" % fate)
        try:
            f = n.check_part(fixture(fate), "i8042")
            want(f["name"] == fate, "fixtures: %s's name field is %s" % (fate, f["name"]))
        except ValueError as exc:
            problems.append("fixtures: %s refused: %s" % (fate, exc))
    want(fixture("liar")[n.PART_HEADER:] == good[n.PART_HEADER:], "fixtures: the liar's body is not good's")
    want(all(b"\x0f\x0b" not in fixture(f)[n.PART_HEADER:] for f in FATES if f != "fault"), "fixtures: a ud2 outside fault")

    # A slot's history, and the table at each step.
    s = ex["A slot's history, and the table at each step"]
    names = {"G": "a" * 16, "H": "b" * 16}
    fences = [b for i, b in _fences(s) if i == ""]
    gnotes = [_sub(x, names) for x in fences[0].split("\n")]
    hnotes = gnotes + [_sub(x, names) for x in fences[1].split("\n")]
    bl = [set(_sub(x, names) for x in _ticks(b)) for b in _bullets(s)]
    for i, note in enumerate(hnotes):
        p = n.parse_note(note)
        if p is None:
            problems.append("history: %r is not a molt note" % note)
            continue
        if p["kind"] == "boot":
            want(p["boot"] == n.boot_number(hnotes[:i]), "history: %r is not numbered by the rule" % note)
        if p["kind"] == "take":
            want(n.take_of(hnotes[:i], "i8042") == note, "history: the take before %r answers %r" % (note, n.take_of(hnotes[:i], "i8042")))
        if p["kind"] == "undo":
            want(n.undo_of(hnotes[:i], None) == (note, False), "history: the undo before %r" % note)
    first = n.table_of(gnotes[:1])
    want(all(r in bl[0] for r in first) and n.take_of(gnotes[:1], "i8042") in bl[0], "history: the table after the first note")
    k = [i for i, x in enumerate(gnotes) if x == "molt i8042 live " + "a" * 16][0]
    want(n.table_of(gnotes[:k])[1] in bl[1] and gnotes[k] in bl[1], "history: boot 3's take")
    u = [i for i, x in enumerate(gnotes) if x.startswith("molt i8042 undo")][0]
    want(gnotes[u] in bl[2], "history: boot 4's undo")
    want(n.boot_number(gnotes[:gnotes.index("molt recovery owner") + 1]) == 5, "history: the boot after the Esc boot")
    want(len(bl) == 9, "history: %d bullets, this tool knows 9" % len(bl))
    want(all(r in bl[4] for r in n.table_of(gnotes)) and n.probation_of(gnotes, "i8042") == 2, "history: the table at the end of G")
    d = n.recovery_of(hnotes, True)
    want(n.on_probation(hnotes, "i8042") and n.probation_of(hnotes, "i8042") == 0, "history: H is not on probation 0 of 3")
    want(all(x in bl[6] for x in n.recovery_notes(d) + [n.recovery_line(d)]), "history: boot 8's recovery")
    demoted = hnotes + n.recovery_notes(d)
    want(n.table_of(demoted) == ["i8042 demoted %s watchdog" % ("b" * 16)] and n.table_of(demoted)[0] in bl[7],
         "history: the table after the demotion")
    und = n.undo_of(demoted, None)
    want(und[0] in bl[8] and n.counts_of(demoted + [und[0]], "i8042") == (0, 0, 0, 0), "history: the undo from demoted")

    # The undo from shadow.
    s = ex["The undo from shadow"]
    t = [_sub(x, names) for x in _ticks(s)]
    three = t[0:3]
    want(n.state_of(three, "i8042") == ("shadow", "b" * 16) and n.arrival(three, "i8042")[1] == ("live", "a" * 16),
         "undo: the state and the state before H")
    want(n.undo_of(three, "a" * 16) == ("molt i8042 undo live " + "a" * 16, True) and n.undo_of(three, "a" * 16)[0] in t,
         "undo: with the previous build G")
    want(n.undo_of(three, "c" * 16) == ("molt i8042 undo generic", False) == n.undo_of(three, None)
         and "molt i8042 undo generic" in t, "undo: with another previous build, or none")
    want(n.undo_of(three[:1], "a" * 16) == ("molt i8042 undo generic", False), "undo: a first install")
    want(n.undo_of(["hello"], None) == ("nothing to undo", False) and "nothing to undo" in t, "undo: no molt state")

    # The recovery decisions.
    s = ex["The recovery decisions"]
    rows = _rows(s, 0)
    g4 = ["molt i8042 shadow %s 1 1 1" % ("a" * 16), "molt i8042 live " + "a" * 16]
    for b in (1, 2, 3):
        g4 += ["molt boot %d i8042 live" % b, "molt healthy %d" % b]
    g4 += ["molt boot 4 i8042 live"]
    cases = [hnotes, hnotes, hnotes + ["molt boot 8 i8042 live"], g4,
             hnotes + ["molt i8042 demoted %s watchdog" % ("b" * 16)]]
    want(len(rows) == len(cases), "recovery: %d rows, this tool knows %d" % (len(rows), len(cases)))
    want(_sub(_ticks(rows[3][0])[0], names) == g4[0], "recovery: row 4's history")
    for r, notes in zip(rows, cases):
        d = n.recovery_of(notes, {"set": True, "clear": False}[r[1]])
        said = [_sub(x, names) for x in _ticks(r[2]) if x.startswith(("molt ", "S8: "))]
        if d[0] == "load":
            run = re.search(r"run is (\d+)", r[2])
            want(not said and run and int(run.group(1)) == n.unhealthy_run(notes), "recovery: row %r" % r[2])
        else:
            want(said == n.recovery_notes(d) + [n.recovery_line(d)], "recovery: row %r gives %r" % (r[2], d))

    # Esc.
    for r in _rows(ex["Esc"], 0):
        bs = [int(x, 16) for x in _ticks(r[0])[0].split(" ")]
        want(n.esc_held(bs) == (r[1] == "yes"), "Esc: %s" % r[0])

    # The keyboard bytes of a typed text.
    s = ex["The keyboard bytes of a typed text"]
    text = _ticks(s)[0]
    keys = list(text) + ["left", "right", "up", "down"]
    by = [n.key_bytes(x) for x in keys]
    want("make %d keys" % len(keys) in _norm(s), "keyboard: the key count")
    want("%d plain keys at 2 bytes: %d" % (by.count(2), 2 * by.count(2)) in _norm(s), "keyboard: the plain keys")
    shifted = [x for x in keys if len(x) == 1 and n.key_bytes(x) == 4]
    want("%d shifted keys (%s) at 4 bytes: %d" % (len(shifted), ", ".join("`%s`" % x for x in shifted), 4 * len(shifted))
         in _norm(s), "keyboard: the shifted keys")
    want("**%d keyboard bytes**" % n.keyboard_bytes(keys) in _norm(s), "keyboard: the total")

    # The watchdog, and SHA-256.
    s = ex["The watchdog, and SHA-256"]
    want("= **%d**" % n.tco_tmr() in _norm(s), "watchdog: TCO_TMR")
    want([b for i, b in _fences(s) if i == ""] == [n.KAT_ABC] and n.sha256_kat(), "SHA-256: abc")
    k = n.sha_k_rule()
    want(len(k) == 64 and "`0x%08x`" % k[0] in s and "`0x%08x`" % k[-1] in s, "SHA-256: the first and last round constants")

    # SEED.md's worked example.
    s = sdoc["example"]
    fences = sdoc["example_fences"]
    m = re.search(r'`rebuild_script\("(\w+)", "([\w/]+)"\)`', _norm(s))
    rec = open(os.path.join(REPO, n.RECORD), encoding="utf-8").read()
    try:
        seeds = n.parse_seed_record(rec)
        line0 = n.record_lines(rec)[0]
    except ValueError as exc:
        return problems + ["the record: %s" % exc]
    sd = seeds[0]
    want(m and fences[0].split("\n")[0] == "$ " + n.rebuild_script(m.group(1), m.group(2)), "seed: the rebuild's command")
    want(fences[0].split("\n")[1] == "mkimage: BOOTX64.EFI %d bytes, packed into esp.img" % sd["bytes"], "seed: the build's size")
    want(fences[0].split("\n")[3] == "%s  %s/stage8/out/BOOTX64.EFI" % (sd["sha256"], m.group(2) if m else "?"), "seed: the build's hash")
    want(fences[1] == line0 and m and sd["commit"] == m.group(1), "seed: the record's first line is not the document's")
    want(fences[2] == repr(n.parse_seed_line(line0)), "seed: parse_seed_line's dict")
    want("prints `%s`" % sd["date"] in _norm(s), "seed: the commit's date")
    want(n.current_seed(n.parse_seed_record("```\n%s\n```\n" % line0)) == sd,
         "seed: current_seed")  # the example's claim is of its one-line record
    wrapped = "```\n%s\n```\n"
    upper = line0.replace("seed 0 " + sd["sha256"][:4], "seed 0 " + sd["sha256"][:4].upper(), 1)
    variants = [wrapped % upper, wrapped % line0.replace("seed 0", "seed 1", 1),
                wrapped % line0.replace(sd["date"], "2026-09-31"),
                wrapped % (line0 + "\n" + line0.replace("seed 0", "seed 1", 1)), "```\n```\n"]
    got = []
    for v in variants:
        try:
            n.parse_seed_record(v)
            got.append("accepted")
        except ValueError as exc:
            got.append(str(exc))
    want(got == [b for _, b in sdoc["refused"]], "seed: the refused records answer %r" % got)
    two = wrapped % (line0 + "\n" + "seed 1 %s 1 %s %s nasm 3.02" % ("0" * 64, sd["commit"], sd["date"]))
    try:
        n.append_only([two, wrapped % line0])
        problems.append("seed: a shortened history is accepted")
    except ValueError as exc:
        want(str(exc) == "a seed line was changed or removed" and "`%s`" % exc in _norm(s), "seed: the history's refusal")
    want(n.append_only([wrapped % line0, wrapped % line0]), "seed: the same record twice")
    want(n.seed_kat(), "seed: the host's SHA-256")
    return problems


def run_example(parts_path=PARTS_DOC, seed_path=SEED_DOC):
    try:
        docs, n = load(parts_path, seed_path)
        problems = check_examples(docs, n)
    except (ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
        problems = ["the documents do not parse: %s" % exc]
    for p in problems:
        print("FAIL: " + p)
    if not problems:
        print("PARTS.md and SEED.md read cold, their Python agreeing with their prose, and every worked example "
              "reproduced: PARTS.md's %s; the install checks' six refusals; SEED.md's seed 0, its five refused "
              "records and its history" % "; ".join(docs[0]["examples"]))
    return 1 if problems else 0


# ------------------------------------------------------------ the record --

def check_notes(notes):
    """Every note that begins with the molt prefix must parse by PARTS.md."""
    return ["not a molt note by PARTS.md: %r" % t for t in notes if t.startswith(NOTE_PREFIX) and parse_note(t) is None]


def report_table(notes):
    ms = notes_molt(notes)
    for row in table_of(notes):
        print(row)
    print()
    print("molt notes %d; next boot %d; unhealthy run %d; if the evidence were set: %s"
          % (len(ms), boot_number(notes), unhealthy_run(notes),
             recovery_line(recovery_of(notes, True)) or "no recovery"))
    return check_notes(notes)


def _disk_modules():
    """DISK.md's Python (broker/metal.py), NOTEBOOK.md's parser (through the
    frozen checkdisk) and HOME.md's (the frozen checkplans), imported only
    when a disk is read."""
    for sub in ("stage7", "broker"):
        if os.path.join(REPO, sub) not in sys.path:
            sys.path.insert(0, os.path.join(REPO, sub))
    import metal
    import checkdisk            # puts stage3 and stage6 on the path
    import checkplans
    return metal, checkdisk, checkplans


def notes_of_disk(data):
    """The notes partition of a GermOS disk image, by DISK.md and NOTEBOOK.md."""
    metal, checkdisk, _ = _disk_modules()
    return checkdisk.parse_notebook(metal.partition_bytes(data, metal.parse_gpt(data)["notes"]))


def home_of_disk(data):
    """The home partition's bytes and HOME.md's parse of it."""
    metal, _, checkplans = _disk_modules()
    part = metal.partition_bytes(data, metal.parse_gpt(data)["home"])
    return part, checkplans.parse_home(part)


def door_of(notes, slot, entry, blob):
    """PARTS.md's door, step 5: None when the slot loads nothing, else the S8: line."""
    st = state_of(notes, slot)
    if st[0] not in ("shadow", "live"):
        return None
    if entry is None or entry["current"]["sha256"][:16] != st[1] or hashlib.sha256(blob).hexdigest() != entry["current"]["sha256"]:
        return "S8: part %s bad hash" % slot
    try:
        check_part(blob, slot)
    except ValueError:
        return "S8: part %s bad header" % slot
    return "S8: part %s %s %s" % (slot, st[0], st[1])


def run_disk(path):
    with open(path, "rb") as fh:
        data = fh.read()
    notes = notes_of_disk(data)
    problems = report_table(notes)
    part, home = home_of_disk(data)
    metal, _, cp = _disk_modules()
    table = metal.parse_gpt(data)
    print("table: %d sectors, notes at %d, home at %d" % (table["sectors"], table["notes"][0], table["home"][0]))
    print("notes %d; home: %d app(s), %d part(s)"
          % (len(notes), sum(1 for e in home["entries"] if e and not is_part_name(e["name"])),
             sum(1 for e in home["entries"] if e and is_part_name(e["name"]))))
    for slot in SLOTS:
        entry = next((e for e in home["entries"] if e and e["name"] == home_name(slot)), None)
        if entry is None:
            print("%s: no home entry" % home_name(slot))
        else:
            prev = entry["previous"]["sha256"][:16] if entry["previous"] else "none"
            print("%s: current %s %d bytes, previous %s" % (home_name(slot), entry["current"]["sha256"][:16],
                                                        entry["current"]["size"], prev))
        blob = cp.blob_of(part, entry["current"]) if entry else b""
        door = door_of(notes, slot, entry, blob)
        print("door: %s" % (door or "%s loads nothing" % slot))
    for p in problems:
        print("DISAGREES: " + p)
    return 1 if problems else 0


def notes_of_serial(text):
    out = []
    for raw in text.replace("\r", "").split("\n"):
        m = re.search(r"%s .*$" % re.escape(SERIAL_PREFIX), raw)
        if m:
            out.append(note_of_serial(m.group(0)))
    return out


def run_serial(path):
    with open(path, "rb") as fh:
        text = fh.read().decode("utf-8", "replace")
    notes = notes_of_serial(text)
    problems = report_table(notes)
    s8 = [m.group(0) for m in re.finditer(r"S8: [^\r\n]*", text)]
    print("S8: lines %d" % len(s8))
    for line in s8:
        print("  " + line)
    for p in problems:
        print("DISAGREES: " + p)
    return 1 if problems else 0


# ---------------------------------------------------- git and the seed --

def git(*args):
    r = subprocess.run(["git"] + list(args), cwd=REPO, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def resolve_commit(c):
    """The one commit a record line names, in full; ValueError otherwise."""
    rc, out = git("rev-parse", "--verify", "--quiet", c + "^{commit}")
    if rc or not re.fullmatch(r"[0-9a-f]{40}", out) or not out.startswith(c):
        raise ValueError("%s names no single commit" % c)
    return out


def commit_date(full):
    return git("show", "-s", "--format=%cs", full)[1]


def is_ancestor(a, b):
    return git("merge-base", "--is-ancestor", a, b)[0] == 0


def record_versions():
    """[(commit or "worktree", text)], oldest first: the record at every commit
    that changed it, then the working tree's if it differs from the last."""
    out = []
    for c in git("log", "--format=%H", "--reverse", "--", RECORD)[1].split():
        out.append((c, git("show", "%s:%s" % (c, RECORD))[1] + "\n"))
    work = open(os.path.join(REPO, RECORD), encoding="utf-8").read()
    if not out or out[-1][1].strip() != work.strip():
        out.append(("worktree", work))
    return out


def rebuild(seed):
    """SEED.md's recipe for one line: (sha256, bytes) of the rebuilt EFI; ValueError on a refusal."""
    rc = subprocess.run(["nasm", "-v"], capture_output=True, text=True)
    have = nasm_version(rc.stdout)
    if have != seed["nasm"]:
        raise ValueError("no rebuild: the line names nasm %s and this host has %s" % (seed["nasm"], have))
    work = "stage8/out/seed/%d" % seed["n"]
    r = subprocess.run(["bash", "-c", rebuild_script(seed["commit"], work)], cwd=REPO, capture_output=True, text=True)
    if r.returncode:
        raise ValueError("the rebuild failed: %s" % (r.stderr.strip() or r.stdout.strip())[-300:])
    with open(os.path.join(REPO, work, SEED_EFI), "rb") as fh:
        return build_id(fh.read())


def run_seed():
    problems = []
    if not seed_kat():
        print("FAIL: this host's SHA-256 fails SEED.md's known answers; nothing is rebuilt")
        return 1
    versions = record_versions()
    try:
        seeds = parse_seed_record(versions[-1][1])
        append_only([t for _, t in versions])
    except ValueError as exc:
        print("FAIL: the record: %s" % exc)
        return 1
    for s in seeds:
        adder = next((c for c, t in versions if any(x.startswith("seed %d " % s["n"]) for x in record_lines(t))), "worktree")
        try:
            full = resolve_commit(s["commit"])
            if adder == "worktree":
                ok = is_ancestor(full, "HEAD")
            else:
                ok = is_ancestor(full, adder) and full != adder
            if not ok:
                raise ValueError("%s is not an ancestor of the commit that adds its line" % s["commit"])
            if commit_date(full) != s["date"]:
                raise ValueError("%s's committer date is %s, the line says %s" % (s["commit"], commit_date(full), s["date"]))
            sha, size = rebuild(s)
            if (sha, size) != (s["sha256"], s["bytes"]):
                raise ValueError("the rebuild is %s %d bytes, the line says %s %d" % (sha, size, s["sha256"], s["bytes"]))
            print("seed %d: %s at %s (%s), rebuilt under nasm %s: %s %d bytes, agrees"
                  % (s["n"], s["commit"], full[:12], s["date"], s["nasm"], sha, size))
        except ValueError as exc:
            problems.append("seed %d: %s" % (s["n"], exc))
    cur = current_seed(seeds)
    print("the witness's seed is seed %d (%s)" % (cur["n"], cur["sha256"][:16]))
    efi = os.path.join(REPO, SEED_EFI)
    if os.path.exists(efi):
        with open(efi, "rb") as fh:
            data = fh.read()
        named = seed_named(seeds, data)
        print("%s (%d bytes, %s) is %s" % (SEED_EFI, len(data), build_id(data)[0][:16],
                                           "seed %d" % named if named is not None else "no seed: no line names it"))
    else:
        print("%s is not built" % SEED_EFI)
    for p in problems:
        print("FAIL: " + p)
    return 1 if problems else 0


def main(argv):
    if argv[:1] == ["--example"]:
        opts = dict(zip(argv[1::2], argv[2::2]))
        if len(argv) % 2 == 0 or set(opts) - {"--parts", "--seeddoc"}:
            print("usage: parts.py --example [--parts DOC] [--seeddoc DOC]")
            return 1
        return run_example(opts.get("--parts", PARTS_DOC), opts.get("--seeddoc", SEED_DOC))
    if len(argv) == 2 and argv[0] == "--disk":
        return run_disk(argv[1])
    if len(argv) == 2 and argv[0] == "--serial":
        return run_serial(argv[1])
    if argv == ["--seed"]:
        return run_seed()
    print("usage: parts.py --example [--parts DOC] [--seeddoc DOC] | --disk IMG | --serial LOG | --seed")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
