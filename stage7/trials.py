#!/usr/bin/env python3
"""Stage 7 ring 7d - the trial's host tool: stage7/TRIALS.md read cold.

The document's own Python block is executed here as this module's
definitions (with the frozen parse_obs_6c and mode_word supplied by name),
and the document's prose tables - the cue table, the obs table - are
parsed and compared with those definitions, so the tool and the document
cannot drift. Frozen behind the hook from plan item 8.

Modes (from the repo root):

  --example        both worked examples reproduced byte for byte (test 1)
  --disk IMG       a GermOS SATA disk image (DISK.md's table): the notes
                   partition's trial notes as sitting tables, the block
                   notes checked against their own hits, the verdict
  --serial LOG     a serial log or chart: its "trial:" lines read back as
                   notes, then the same tables and verdict

Exit 0 when the record agrees with the rules; 1 when a block note
disagrees with its hits, when the document does not parse, or when an
example is not reproduced.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DOC = os.path.join(HERE, "TRIALS.md")
sys.path.insert(0, os.path.join(REPO, "broker"))
sys.path.insert(0, os.path.join(REPO, "stage7"))
from glass import mode_word          # noqa: E402  - the 6a section's mode word
from pointer import parse_obs_6c     # noqa: E402  - the 6c section's page parser


def _fences(text):
    """Every fenced block in the document, in order: (info string, body)."""
    out = []
    for m in re.finditer(r"^```([^\n]*)\n(.*?)^```", text, re.M | re.S):
        out.append((m.group(1).strip(), m.group(2).rstrip("\n")))
    return out


def _section(text, heading):
    m = re.search(r"^## %s.*?(?=^## |\Z)" % re.escape(heading), text, re.M | re.S)
    if not m:
        raise ValueError("TRIALS.md has no section %r" % heading)
    return m.group(0)


def parse_trials_md(text):
    """The document's data: the cue table from its fence, the obs table from
    its rows, the worked examples from their fences, the Python from its
    fence. Fails loudly on a shape it does not know."""
    doc = {}
    design = _section(text, "The design")
    cue_fence = [b for i, b in _fences(design) if i == ""][0]
    rows = []
    for line in cue_fence.splitlines():
        m = re.fullmatch(r"block (\d+): ((?:[a-z]+ ){9}[a-z]+)", line)
        if not m or int(m.group(1)) != len(rows) + 1:
            raise ValueError("the cue table's line %r is not 'block N: ten words'" % line)
        rows.append(m.group(2))
    doc["cues"] = rows
    m = re.search(r"odd sittings `([AB]{4} [AB]{4})`, even sittings `([AB]{4} [AB]{4})`", design)
    if not m:
        raise ValueError("the block order sentence is not where the design puts it")
    doc["orders"] = {1: m.group(1), 0: m.group(2)}
    obs = _section(text, "The obs page")
    fields = {}
    for m in re.finditer(r"^\| `(0x[0-9A-F]+)` \| `(\w+)` \|", obs, re.M):
        fields[m.group(2)] = int(m.group(1), 16)
    if not fields:
        raise ValueError("no obs rows")
    doc["obs"] = fields
    m = re.search(r"from\n`(0x[0-9A-F]+)`, is zero", obs)
    if not m:
        raise ValueError("the obs section does not say where the page is zero from")
    doc["obs_zero_from"] = int(m.group(1), 16)
    ex_a = [b for i, b in _fences(_section(text, "Worked example A")) if i == ""]
    if len(ex_a) != 2:
        raise ValueError("worked example A wants two fences: the notes and the table")
    doc["example_a_notes"], doc["example_a_table"] = ex_a[0].splitlines(), ex_a[1].splitlines()
    ex_b = [b for i, b in _fences(_section(text, "Worked example B")) if i == ""]
    if len(ex_b) != 1:
        raise ValueError("worked example B wants one fence")
    doc["example_b_notes"] = ex_b[0].splitlines()
    py = [b for i, b in _fences(_section(text, "Parsing it cold")) if i == "python"]
    if len(py) != 1:
        raise ValueError("the Python section wants one python fence")
    doc["python"] = py[0]
    return doc


def load(path=DOC):
    """Execute the document's Python and check it against the document's tables."""
    text = open(path, encoding="utf-8").read()
    doc = parse_trials_md(text)
    ns = {"parse_obs_6c": parse_obs_6c, "mode_word": mode_word}
    exec(compile(doc["python"], path, "exec"), ns)
    if ns["CUES"] != doc["cues"]:
        raise ValueError("the Python's CUES differ from the document's cue table")
    if ns["ORDERS"] != doc["orders"]:
        raise ValueError("the Python's ORDERS differ from the document's sentence")
    if ns["OBS_7D"] != doc["obs"]:
        raise ValueError("the Python's OBS_7D differs from the document's obs table: %r vs %r" % (ns["OBS_7D"], doc["obs"]))
    if ns["OBS_PAGE_BYTES_7D"] != doc["obs_zero_from"]:
        raise ValueError("the Python's OBS_PAGE_BYTES_7D differs from the document's zero rule")
    ns["check_cue_table"]()
    return doc, ns


DOCUMENT, _NS = load()
for _name, _value in _NS.items():
    if not _name.startswith("_") and _name not in ("parse_obs_6c", "mode_word", "struct"):
        globals()[_name] = _value


# ------------------------------------------------------------ the record --

def notes_of_disk(path):
    """The notes partition of a GermOS disk image, by DISK.md and NOTEBOOK.md."""
    import metal
    import checkdisk
    data = checkdisk.read_image(path)
    table = metal.parse_gpt(data)
    return checkdisk.parse_notebook(metal.partition_bytes(data, table["notes"]))


def notes_of_serial(path):
    out = []
    with open(path, "rb") as fh:
        for raw in fh.read().decode("utf-8", "replace").replace("\r", "").split("\n"):
            m = re.search(r"trial: .*$", raw)
            if m:
                out.append(note_of_serial(m.group(0)))
    return out


def report(notes):
    problems = check_blocks(notes)
    tables = table_of(notes)
    if not tables:
        print("no sittings")
    for sitting, rows in tables:
        print("\n".join(rows))
        print()
    d = verdict_detail(notes)
    if d is None:
        print("no verdict: %d done sitting(s), %d needed" % (sum(1 for s in sittings_of(notes) if s["end"] == "done"), SITTINGS_NEEDED))
    else:
        sittings, wins, ma, mb = d
        print("verdict %s: sittings %s, wins for B %d of %d (%d needed), misses A %d B %d"
              % (verdict_of(notes), sittings, wins, PAIRS_NEEDED, WINS_NEEDED, ma, mb))
    for p in problems:
        print("DISAGREES: " + p)
    return 0 if not problems else 1


def run_example():
    problems = []
    a = DOCUMENT["example_a_notes"]
    tables = table_of(a)
    if len(tables) != 1 or tables[0][1] != DOCUMENT["example_a_table"]:
        problems.append("example A: the table is not the document's")
    if check_blocks(a):
        problems.append("example A: " + "; ".join(check_blocks(a)))
    if verdict_of(a) is not None:
        problems.append("example A: a verdict from one sitting")
    if sitting_number(a) != 2 or default_layout(a) != 0:
        problems.append("example A: the next sitting is not 2, or the default is not A")
    if len(a) != 93:
        problems.append("example A: %d notes, the document says 93" % len(a))
    script = {"sitting": 1, "blocks": [], "abort": None}
    for s in sittings_of(a):
        for b in range(1, BLOCKS + 1):
            script["blocks"].append({"ms": s["hits"][b], "miss": [p["cue"] for p in map(parse_note, a)
                                                                  if p and p["kind"] == "miss" and p["block"] == b]})
    if notes_of(script) != a:
        problems.append("example A: notes_of the same script does not reproduce the notes")
    if [serial_of(n) for n in a][:2] != ["trial: sitting 1 ABBA BAAB", "trial: 1 1 A 1 312"]:
        problems.append("example A: the serial rule")
    if [note_of_serial(serial_of(n)) for n in a] != a:
        problems.append("example A: the serial rule does not round-trip")
    b = DOCUMENT["example_b_notes"]
    d = verdict_detail(b)
    if d is None or d[0] != [1, 3, 4] or d[1] != 10 or (d[2], d[3]) != (2, 2) or verdict_of(b) != "B":
        problems.append("example B: the verdict detail is %r" % (d,))
    if b[-1] != "trial verdict B" or default_layout(b) != 1 or sitting_number(b) != 5:
        problems.append("example B: the last note, the default or the next sitting")
    rows = dict(table_of(b))
    if rows[2][-1] != "aborted 3" or len(rows[2]) != 4 or rows[4][-1] != "verdict B" or rows[1][-1] != "done":
        problems.append("example B: the tables' last rows")
    altered = list(a)
    altered[11] = "trial block 1 1 A 10 0 304"
    if check_blocks(altered) != ["sitting 1 block 1: the median of its hits is 303, the block note says 304"]:
        problems.append("example A altered by one: not refused with the block named: %r" % check_blocks(altered))
    for p in problems:
        print("FAIL: " + p)
    if not problems:
        print("both worked examples reproduced: A's 93 notes, its table and its serial lines; B's verdict B by 10 of 12 "
              "with misses 2 against 2 over sittings 1, 3 and 4; a block median altered by one is refused")
    return 1 if problems else 0


def main(argv):
    if argv == ["--example"]:
        return run_example()
    if len(argv) == 2 and argv[0] == "--disk":
        return report(notes_of_disk(argv[1]))
    if len(argv) == 2 and argv[0] == "--serial":
        return report(notes_of_serial(argv[1]))
    print("usage: trials.py --example | --disk IMG | --serial LOG")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
