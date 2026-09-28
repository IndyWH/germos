#!/usr/bin/env python3
"""Ring 8t - trial two's host tool: trials/TRIALS2.md read cold.

The document's own Python block is executed here as this module's
definitions (with the frozen parse_obs_7d and mode_word_7d of
stage7/trials.py supplied by name), and the document's prose - the cue
table, the orders, the obs row, the twin's G columns - is parsed and
compared with those definitions, so the tool and the document cannot
drift. Frozen behind the hook from plan item 9.

Modes (from the repo root):

  --example [--doc PATH]  every worked example reproduced byte for byte (test 1)
  --disk IMG              a GermOS SATA disk image: the trial-two notes as
                          sitting tables, every block note checked against its
                          own hits, the verdict, the boot line
  --serial LOG            a serial log or chart: its "trial2:" lines read back
                          as notes, then the same report
  --status LOG            the blind read for Cowork: procedure facts only -
                          each boot's line, each sitting opened, done or
                          aborted, the counts, the preference saved - and no
                          time or score until a "trial2: verdict" line exists

Exit 0 when the record agrees with the rules; 1 when a block note
disagrees with its hits, when the document does not parse, or when an
example is not reproduced.
"""

import contextlib
import importlib.util
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DOC = os.path.join(HERE, "TRIALS2.md")
for _d in ("stage3", "stage6", "stage7", "broker"):
    sys.path.insert(0, os.path.join(REPO, _d))


def _trial_one():
    """stage7/trials.py, frozen, by its path: trial one's tool and its page parser."""
    spec = importlib.util.spec_from_file_location("trials", os.path.join(REPO, "stage7", "trials.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["trials"] = mod
    spec.loader.exec_module(mod)
    return mod


T1 = _trial_one()


def _fences(text):
    out = []
    for m in re.finditer(r"^```([^\n]*)\n(.*?)^```", text, re.M | re.S):
        out.append((m.group(1).strip(), m.group(2).rstrip("\n")))
    return out


def _section(text, heading):
    m = re.search(r"^## %s.*?(?=^## |\Z)" % re.escape(heading), text, re.M | re.S)
    if not m:
        raise ValueError("TRIALS2.md has no section %r" % heading)
    return m.group(0)


def _plain(text, heading, count):
    got = [b for i, b in _fences(_section(text, heading)) if i == ""]
    if len(got) != count:
        raise ValueError("%s wants %d fence(s), it has %d" % (heading, count, len(got)))
    return got


def _spans(s):
    return [tuple(int(x) for x in p.split("–")) for p in re.findall(r"\d+–\d+", s)]


def parse_trials2_md(text):
    """The document's data from its prose and fences; fails loudly on a shape it does not know."""
    doc = {}
    design = _section(text, "The design")
    rows = _plain(text, "The design", 1)[0].splitlines()
    cues = []
    for i, line in enumerate(rows):
        m = re.fullmatch(r"block (\d+): ([a-z ]+)", line)
        if not m or int(m.group(1)) != i:
            raise ValueError("the cue table's line %r is not 'block N: words'" % line)
        cues.append(m.group(2))
    doc["warmup"], doc["cues"] = cues[0], cues[1:]
    m = re.search(r"odd sittings `([GB]{4} [GB]{4})`, even sittings `([GB]{4} [GB]{4})`", design)
    if not m:
        raise ValueError("the block order sentence is not where the design puts it")
    doc["orders"] = {1: m.group(1), 0: m.group(2)}
    obs = _section(text, "The obs page")
    doc["obs"] = {m.group(2): int(m.group(1), 16) for m in re.finditer(r"^\| `(0x[0-9A-F]+)` \| `(\w+)` \|", obs, re.M)}
    if not doc["obs"]:
        raise ValueError("no obs rows")
    row = _section(text, "The row and the items")
    twin = {}
    for name, key in (("four-item row", 4), ("two-item prompt row", 2), ("three-item prompt row", 3)):
        m = re.search(r"the %s[^`\n]*`([^`]+)`: labels at (.*?); `\|` at ([^;.\n]*)" % re.escape(name), row)
        if not m:
            raise ValueError("the twin's %s is not stated" % name)
        labels = m.group(1).split("   ")
        seps = [int(x) for x in re.findall(r"\d+", m.group(3))]
        twin[key] = (labels, _spans(m.group(2)), seps)
    doc["twin_rows"] = twin
    a = _plain(text, "Worked example A", 3)
    doc["a_notes"], doc["a_end"], doc["a_table"] = a[0].splitlines(), a[1].splitlines(), a[2].splitlines()
    b = _plain(text, "Worked example B", 3)
    doc["b_notes"], doc["b_d"], doc["b_panel"] = b[0].splitlines(), b[1].splitlines(), b[2].splitlines()
    doc["c_notes"] = _plain(text, "Worked example C", 1)[0].splitlines()
    d = _plain(text, "Worked example D", 3)
    doc["d_notes"], doc["d_d"], doc["d_panel"] = d[0].splitlines(), d[1].splitlines(), d[2].splitlines()
    doc["e_molt"] = _plain(text, "Worked example E", 1)[0].splitlines()
    f = _plain(text, "Worked example F", 2)
    doc["f_chart"], doc["f_status"] = f[0].splitlines(), f[1].splitlines()
    py = [b for i, b in _fences(_section(text, "Parsing it cold")) if i == "python"]
    if len(py) != 1:
        raise ValueError("the Python section wants one python fence")
    doc["python"] = py[0]
    return doc


def load(path=DOC):
    """Execute the document's Python and check it against the document's prose."""
    text = open(path, encoding="utf-8").read()
    doc = parse_trials2_md(text)
    ns = {"parse_obs_7d": T1.parse_obs_7d, "mode_word_7d": T1.mode_word_7d}
    exec(compile(doc["python"], path, "exec"), ns)
    if ns["CUES"] != doc["cues"] or ns["WARMUP"] != doc["warmup"]:
        raise ValueError("the Python's cue table differs from the document's")
    if ns["ORDERS"] != doc["orders"]:
        raise ValueError("the Python's ORDERS differ from the document's sentence")
    if ns["OBS_8T"] != doc["obs"]:
        raise ValueError("the Python's OBS_8T differs from the document's obs table: %r vs %r" % (ns["OBS_8T"], doc["obs"]))
    for n, (labels, spans, seps) in doc["twin_rows"].items():
        if len(labels) != n or ns["grouped_columns"](120, labels) != (spans, seps):
            raise ValueError("the twin's %d-item G row: the prose says %r %r, the rule gives %r"
                             % (n, spans, seps, ns["grouped_columns"](120, labels)))
    try:
        ns["check_cue_table"]()
    except AssertionError as exc:
        raise ValueError("the cue table breaks its constraints: %s" % (exc.args[0] if exc.args else "a count"))
    return doc, ns


DOCUMENT, _NS = load()
for _name, _value in _NS.items():
    if not _name.startswith("_") and _name not in ("parse_obs_7d", "mode_word_7d", "struct"):
        globals()[_name] = _value


# ------------------------------------------------------------ the record --

def notes_of_disk(path):
    """The notes partition of a GermOS disk image, by DISK.md and NOTEBOOK.md."""
    import metal
    import checkdisk
    data = checkdisk.read_image(path)
    table = metal.parse_gpt(data)
    return checkdisk.parse_notebook(metal.partition_bytes(data, table["notes"]))


def chart_lines(path):
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8", "replace").replace("\r", "").split("\n")


def notes_of_chart(lines):
    """The trial-two notes a chart carries: every "trial2:" line, wherever it lands in a
    line, bar the two boot lines."""
    out = []
    for raw in lines:
        i = raw.find(SERIAL_PREFIX)
        if i < 0:
            continue
        line = raw[i:]
        if line.startswith("trial2: due ") or line.startswith("trial2: concluded "):
            continue
        out.append(note_of_serial(line))
    return out


def report(notes):
    problems = check_blocks(notes)
    tables = table_of(notes)
    if not tables:
        print("no sittings")
    for _, rows in tables:
        print("\n".join(rows))
        print()
    v = verdict_detail(notes)
    if v is None:
        print("no verdict: %d done sitting(s), %d needed"
              % (sum(1 for s in sittings_of(notes) if s["end"] == "done"), SITTINGS_NEEDED))
    else:
        sittings, d, total, mean = v
        print("verdict %s: sittings %s, d %s, S %d, mean %d" % (verdict_of(notes), sittings, " ".join(map(str, d)), total, mean))
        noted = [p for p in map(parse_note, notes) if p and p["kind"] == "verdict"]
        if noted and (noted[0]["layout"], noted[0]["mean"]) != (verdict_of(notes), mean):
            problems.append("the verdict note says %s %d, the rule gives %s %d"
                            % (noted[0]["layout"], noted[0]["mean"], verdict_of(notes), mean))
    print("boot line: %s" % (boot_line(notes) or "none"))
    for p in problems:
        print("DISAGREES: " + p)
    return 0 if not problems else 1


def _captured(fn, *args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        fn(*args)
    return out.getvalue()


def _script_of(notes, sitting):
    """The script a sitting's notes were made from (the inverse of notes_of, for a done sitting)."""
    ps = [p for p in map(parse_note, notes) if p and p.get("sitting") == sitting]
    blk = {}
    for p in ps:
        if p["kind"] in ("hit", "miss"):
            e = blk.setdefault(p["block"], {"ms": [], "miss": []})
            if p["kind"] == "hit":
                e["ms"].append(p["ms"])
            else:
                e["miss"].append(p["cue"])
    prefer = [p["answer"] for p in ps if p["kind"] == "prefer"]
    return {"sitting": sitting, "warmup": blk[0], "blocks": [blk[b] for b in range(1, BLOCKS + 1)],
            "abort": None, "prefer": prefer[0] if prefer else None}


def run_example(doc=DOCUMENT):
    problems = []

    def want(cond, what):
        if not cond:
            problems.append(what)

    a = doc["a_notes"]
    want(len(a) == 184, "example A: %d notes, the document says 184" % len(a))
    want(notes_of(_script_of(a, 1)) == a, "example A: notes_of the same script does not reproduce the notes")
    want(not check_blocks(a), "example A: " + "; ".join(check_blocks(a)))
    want(len(table_of(a)) == 1 and table_of(a)[0][1] == doc["a_table"], "example A: the table is not the document's")
    want(end_lines(a, 1) == doc["a_end"], "example A: the end lines are not the document's")
    want(verdict_of(a) is None and sitting_number(a) == 2 and in_progress(a), "example A: a verdict, or the next sitting is not 2")
    want(boot_line(a) == "trial2: due sitting 2" and offer(a) == "trial 2 sitting 2: press Enter to start",
         "example A: the boot line or the offer")
    want(default_layout(a) == 0, "example A: the default is not A")
    want([note_of_serial(serial_of(n)) for n in a] == a and serial_of(a[1]) == "trial2: 1 0 G 1 %s" % a[1].split()[-1],
         "example A: the serial rule")
    s = sittings_of(a)[0]
    want(counts(s) == ((160, 2), (10, 1)), "example A: the counts are %r" % (counts(s),))
    altered = list(a)
    i = next(k for k, t in enumerate(a) if t.startswith("trial2 block 1 1 "))
    w = altered[i].split(" ")
    altered[i] = " ".join(w[:-1] + [str(int(w[-1]) + 1)])
    want(check_blocks(altered) == ["sitting 1 block 1: the score of its hits is %s, the block note says %d"
                                   % (w[-1], int(w[-1]) + 1)],
         "example A altered by one: not refused with the block named: %r" % check_blocks(altered))

    b = doc["b_notes"]
    v = verdict_detail(b)
    want(v is not None and [" ".join(map(str, v[1])), str(v[2]), str(v[3])] == doc["b_d"], "example B: d, S or the mean: %r" % (v,))
    want(verdict_of(b) == "B" and verdict_note(b) in b and verdict_panel(b) == doc["b_panel"], "example B: the verdict or the panel")
    want(boot_line(b) == "trial2: concluded verdict B default B" and default_layout(b) == 1 and offer(b) is None,
         "example B: the boot line, the default or the offer")

    c = doc["c_notes"]
    want(verdict_note(c[:-1]) == c[-1] == "trial2 verdict G 0", "example C: S 0 is not verdict G 0")
    for block, layout_letter, note in ((8, "G", "trial2 verdict B 0"), (7, "B", "trial2 verdict G 0")):
        old = "trial2 block 4 %d %s 20 0 1500" % (block, layout_letter)
        varied = [t.replace("1500", "1515") if t == old else t for t in c[:-1]]
        want(old in c and verdict_note(varied) == note, "example C: block %d at 1515 does not give %s" % (block, note))
    for delta, note in ((16, "trial2 verdict B 1"), (-16, "trial2 verdict G -1")):
        old = "trial2 block 4 8 G 20 0 1500"
        varied = [t.replace("1500", str(1500 + delta)) if t == old else t for t in c[:-1]]
        want(verdict_note(varied) == note, "example C: S %d does not give %s" % (delta, note))

    d = doc["d_notes"]
    v = verdict_detail(d)
    want(v is not None and v[0] == [1, 3, 4, 5] and [" ".join(map(str, v[1])), str(v[2]), str(v[3])] == doc["d_d"],
         "example D: the sittings judged, d, S or the mean: %r" % (v,))
    want(verdict_of(d) == "G" and verdict_panel(d) == doc["d_panel"], "example D: the verdict or the panel")
    want(boot_line(d) == "trial2: concluded verdict G default G" and default_layout(d) == 2, "example D: the boot line or the default")
    want(sittings_of(d)[1]["end"] == "aborted" and sittings_of(d)[1]["aborted"] == 3, "example D: sitting 2's abort")

    one = T1.DOCUMENT["example_b_notes"]
    base = _captured(T1.report, one)
    e = one + doc["e_molt"] + a
    want(_captured(T1.report, e) == base and default_layout(e) == 1, "example E: trial one's report changed, or the default")
    e2 = e + d
    want(_captured(T1.report, e2) == base and default_layout(e2) == 2, "example E with D: trial one's report changed, or the default")

    status = status_of(doc["f_chart"])
    want(status == doc["f_status"], "example F: the blind read is %r" % status)
    secret = {str(p["ms"]) for p in map(parse_note, a) if p and p["kind"] == "hit"}
    secret |= {str(p["score"]) for p in map(parse_note, a) if p and p["kind"] == "block"}
    leaked = sorted(secret & set(re.findall(r"-?\d+", "\n".join(status))))
    want(not leaked, "example F: the blind read shows %s" % leaked)
    want(notes_of_chart(doc["f_chart"]) == a, "example F: the chart's notes are not example A's")

    for p in problems:
        print("FAIL: " + p)
    if not problems:
        print("every worked example reproduced: A's 184 notes, its end lines, table and serial lines, a score altered "
              "by one refused; B verdict B, S %s, mean %s; C S 0, 15, -15, 16, -16 at the boundary; D verdict G over "
              "sittings 1, 3, 4, 5; E trial one's report unchanged with both families; F the blind read, no ms or score"
              % (doc["b_d"][1], doc["b_d"][2]))
    return 1 if problems else 0


def run_status(path):
    lines = chart_lines(path)
    for line in status_of(lines):
        print(line)
    notes = notes_of_chart(lines)
    if any((parse_note(t) or {}).get("kind") == "verdict" for t in notes):
        print()
        return report(notes)
    return 0


def main(argv):
    if argv[:1] == ["--example"]:
        if argv == ["--example"]:
            return run_example()
        if len(argv) == 3 and argv[1] == "--doc":
            try:
                doc, _ = load(argv[2])
            except (ValueError, KeyError, IndexError) as exc:
                print("FAIL: %s does not parse: %s" % (argv[2], exc))
                return 1
            return run_example(doc)
    if len(argv) == 2 and argv[0] == "--disk":
        return report(notes_of_disk(argv[1]))
    if len(argv) == 2 and argv[0] == "--serial":
        return report(notes_of_chart(chart_lines(argv[1])))
    if len(argv) == 2 and argv[0] == "--status":
        return run_status(argv[1])
    print("usage: trials2.py --example [--doc PATH] | --disk IMG | --serial LOG | --status LOG")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
