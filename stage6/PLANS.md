# PLANS.md — the store of plans: a plan file, its five-verb tests, and the install

**Stage 6 ring 6b, plan item 1. Frozen behind the hook from item 8.** The
broker's install pipeline and the acceptance checker parse plans by this
document; the twin runs the tests it defines; the three committed plans
are written to it. One text, four readers. If it is wrong, that is a spec
question for the owner, not an edit.

`stage6/GLASS.md` is frozen and untouched, and everything it defines
stands: the kind `0x02` app frame with its 96-byte header — including the
**`installed`** byte at header offset 40, "0 this ring (1 at ring 6b)",
which this ring sets — the four callbacks, the four services, the mode
words (`4` is `installing`), the twin's nine criteria and its
post-delivery hook, the germline's directory shape, the record's fields.
`stage6/HOME.md` (this ring, beside this file) defines what the guest does
with an installed app: the home image, the launch, the undo, the choices
row. This document defines **the plan**, **the tests the twin runs**, and
**the broker's install** — what goes into the frame, and why it is refused.

## A plan is a file

`plans/<name>.md` in the repository, plain ASCII (every byte `0x09`,
`0x0A` or `0x20`–`0x7E`), in exactly this shape:

```
# <name>

## Intent
<one or more lines of plain English>

## Choices
<key> <label>          (zero to four lines)

## Tests
<one verb per line>
```

- **The name** is `[a-z][a-z0-9-]{0,31}` — a lowercase letter, then up to
  31 lowercase letters, digits or hyphens — and equals the file's basename
  without `.md`. It is what `! <name>` launches, what the frame's name
  field carries, and what the choices row shows.
- **The headings** `# <name>`, `## Intent`, `## Choices`, `## Tests` appear
  once each, in that order, the first as the first non-blank line. Any
  other line beginning `#` is an error. Blank lines are ignored everywhere.
- **Intent** is every non-blank line between its heading and the next,
  trailing whitespace trimmed, joined with single newlines: the thing
  Claude builds from. It must not be empty.
- **Choices**: zero to four lines `<key> <label>` — one printable
  non-space key byte, one space, then a label of 1 to 12 printable bytes
  (inner spaces allowed, the ends trimmed). They are the frame's choice
  slots in order, exactly as GLASS.md's `app_header` packs them; the
  choices row shows the first three. The plan's choices are what the
  frame carries: the backend's own `; choice` lines are ignored for an
  install.
- **Tests**: at least one line, each one of the five verbs below.

**A rule for every plan: an app must draw its starting state in `init`.**
The twin takes its screendump B and judges "the app drew nothing" *before*
it runs the plan's tests, so a panel that stays blank until the first key
fails rehearsal before any test runs. Say in the intent what the panel
shows at the start.

## The five verbs

One per line, the verb first, in order; the first that fails ends the run.

| Line | Grammar | What the twin does |
|---|---|---|
| `press <keys>` | everything after `press ` is the keys: one press per byte, each `0x20`–`0x7E` except `` ` `` and `~` (they do not arrive through the monitor); at least one; trailing bytes kept as written | each key is sent to the twin's keyboard through the monitor's `sendkey`, Shift applied where the US layout needs it, 0.2 s apart; with the app in focus every one reaches its `key` callback |
| `wait <ms>` | an integer 1 to 30000 | sleeps that many milliseconds |
| `expect "<text>"` | 1 to 60 printable bytes, no `"` inside, in double quotes; nothing after the closing quote | takes a screendump and reads every cell of the **app panel** against the shared font (a glyph, a block, a blank); passes if some row holds the text as consecutive cells — **anywhere on the panel** — so the intent should say what else is drawn |
| `expect not "<text>"` | as above | passes if no row holds it |
| `expect changed` | nothing after | passes if the app panel's pixels differ from the twin's previous look |

**The twin's look.** Before the first test the twin takes one look (a
screendump). Every `expect` of any form takes a fresh look, **at least
500 ms after the last `press`**, so the app's `key`, a `step` and a frame
have run; `wait` is for apps that need longer. `expect changed` compares
the new look with the previous one; `press` and `wait` do not look.

**The refusal.** When a verb fails, the rehearsal fails with the verb's
line, verbatim, as its phrase; the broker's pipeline refuses the install
with `rehearsal failed: <line>` — `rehearsal failed: expect "a"` for a
build that drew `b`. The nine criteria of GLASS.md are judged first, by
the frozen twin; the plan's tests run only when all nine pass.

## The install

`! install <name>` goes to the broker as an ordinary grow request
(GERMLINE.md's frame, the body `install <name>`); no new marker. The
broker:

1. **Recognises an install:** a body equal to `install`, or beginning
   `install ` — every such body is an install. The rest after `install`,
   trimmed, is `<name>` or `<name>, <amendment>` (split at the first
   comma, both sides trimmed). A rest that is not a well-formed name
   followed by nothing or by a comma and a non-empty amendment, or a
   name with no `plans/<name>.md`, is refused **`no plan named <rest>`**
   before any generation call, mock and real alike — so a typo never
   becomes a grown app called `install`. A plan file that does not parse
   is refused **`plan <name> does not parse: line <n>`**, likewise
   without a call.
2. **Keys the germline by the plan's hash:** the first 16 hex digits of
   `sha256("install <name>|<plan sha256>|<normalised amendment>|abi2|qemu-q35-ovmf")`
   — the plan file's own SHA-256 in hex, the amendment normalised as
   GERMLINE.md normalises a request (empty when there is none). A
   changed plan is a different key. A hit is served with `source` 1.
3. **Generates** from the intent, with the plan's tests, choices and
   any amendment in the brief (the real backend), or from the mock's
   table below.
4. **Rehearses** in the frozen twin through its post-delivery hook, at
   the machine's display (1920x1080) with the home drive, expecting
   seventeen `S6:` lines: the nine criteria, then the plan's tests as
   above. Up to two candidates, the failure fed back, as GLASS.md's
   pipeline does. The twin delivers its candidate with `installed` 0 —
   the write to the home image is the machine's, proven by the gate's
   own guest.
5. **Caches** what passed in the germline under the key above, the
   provenance carrying GLASS.md's fields plus `plan` (the name),
   `plan_sha256`, `amendment` (or `null`), `installed` (`true`) and
   `plan_tests` (one line per verb run: `ok: <line>` or `fail: <line>`).
6. **Delivers** the app frame with **`installed` 1**, the plan's name and
   the plan's choices — from the germline too, so a repeat install
   replaces on the machine.

**The amendment at the door.** `! install <name>, <text>` installs the
same plan with the text added to the brief ("The person installing it
adds: <text>"), keyed separately. The foundation's "install this, but
left-handed".

**The record** for an install is GLASS.md's grow record plus `plan`,
`plan_sha256`, `amendment` and `tests` (the `plan_tests` lines). A
refused install's `answer` is the refusal text.

## The mock's canned table for installs

`python3 broker/plans.py --mock` answers questions from UMBILICAL.md's
table and plain requests from GLASS.md's table, and installs from this
one. It calls nothing outside the repository. The rehearsal still runs,
for real. Every table lookup is one generation call; the `no plan named`
and `does not parse` refusals come before the table and count none.

| Body (exact bytes) | Candidate |
|---|---|
| `install echo` | the bytes of `stage6/echo.bin`; name `echo`; the plan's choices (none) |
| `install liar` | the bytes of `stage6/liar.bin` — runs safely, draws the key **plus one**; name `liar`; it must be refused `rehearsal failed: expect "a"` |
| `install echo, but big` | `stage6/echo.bin` padded with zeros to exactly 4096 bytes — a different build of the same name, for the undo test; name `echo` |
| `install <name>[, <amendment>]` for any other plan file that exists | the refusal `mock: no canned build for plan: <name>` |

## The three committed plans

`plans/echo.md`, `plans/liar.md` and `plans/calculator.md` are frozen with
this document and are its worked examples: `echo` and `liar` share one
intent ("Shows a dash until a key is pressed, then the last key pressed,
as a single character at the top left of the panel. Nothing else is
drawn."), no choices, and the tests

```
press a
expect "a"
press b
expect "b"
expect not "a"
```

`liar`'s canned build draws `b` for `a`, so it is refused at the second
line. `calculator` is the spec's appendix with the owner's two intent
changes of plan amendment A2: two choices, `= result` and `c clear`, and
ten test lines from `press 2+3=` to `expect "-1"`.

## Parsing it cold, in Python

The broker and the checker use this, and nothing more:

```python
import hashlib
import re

NAME_RE = re.compile(r"[a-z][a-z0-9-]{0,31}")
PRESSABLE = set(range(0x20, 0x7F)) - {0x60, 0x7E}      # not ` or ~
EXPECT_MAX = 60
WAIT_MAX = 30000
CHOICES = 4
LABEL_MAX = 12
MACHINE = "qemu-q35-ovmf"


def parse_plan(text):
    """The plan file's text. Returns {"name", "intent", "choices": [(key,
    label bytes)], "tests": [(verb, arg)]} with verbs "press" (arg the
    keys), "wait" (arg the ms), "expect", "expect not" (arg the text) and
    "expect changed" (arg None); raises ValueError("line N: ...")."""
    if not all(b in (0x09, 0x0A) or 0x20 <= b <= 0x7E for b in text.encode("latin-1", "replace")):
        raise ValueError("line 0: the plan is not plain ASCII")
    lines = text.split("\n")
    name = None
    section = None
    seen = []
    intent, choices, tests = [], [], []
    for n, raw in enumerate(lines, 1):
        line = raw.rstrip()
        if not line.strip():
            continue
        if name is None:
            m = re.fullmatch(r"# (%s)" % NAME_RE.pattern, line)
            if not m:
                raise ValueError("line %d: the first line must be '# <name>'" % n)
            name = m.group(1)
            continue
        if line.startswith("#"):
            if line not in ("## Intent", "## Choices", "## Tests") or line in seen \
                    or line != ("## Intent", "## Choices", "## Tests")[len(seen)]:
                raise ValueError("line %d: unexpected heading %r" % (n, line))
            seen.append(line)
            section = line
            continue
        if section == "## Intent":
            intent.append(line.strip())
        elif section == "## Choices":
            m = re.fullmatch(r"(\S) (.{1,%d})" % LABEL_MAX, line.strip())
            if not m or len(choices) >= CHOICES:
                raise ValueError("line %d: a choice is '<key> <label>' (1-12 bytes), four at most" % n)
            choices.append((ord(m.group(1)), m.group(2).strip().encode("ascii")))
        elif section == "## Tests":
            tests.append(parse_test(n, raw.rstrip("\r\n")))
        else:
            raise ValueError("line %d: text before '## Intent'" % n)
    if name is None:
        raise ValueError("line 0: empty plan")
    if len(seen) != 3:
        raise ValueError("line 0: missing section(s) %r" % [s for s in ("## Intent", "## Choices", "## Tests") if s not in seen])
    if not intent:
        raise ValueError("line 0: the intent is empty")
    if not tests:
        raise ValueError("line 0: no tests")
    return {"name": name, "intent": "\n".join(intent), "choices": choices, "tests": tests}


def parse_test(n, line):
    if line.startswith("press "):
        keys = line[6:]
        if not keys or any(ord(c) not in PRESSABLE for c in keys):
            raise ValueError("line %d: press needs one or more keys, printable, not ` or ~" % n)
        return ("press", keys)
    m = re.fullmatch(r"wait (\d+)", line.rstrip())
    if m:
        ms = int(m.group(1))
        if not 1 <= ms <= WAIT_MAX:
            raise ValueError("line %d: wait takes 1 to %d ms" % (n, WAIT_MAX))
        return ("wait", ms)
    if line.rstrip() == "expect changed":
        return ("expect changed", None)
    m = re.fullmatch(r'expect( not)? "([^"]{1,%d})"' % EXPECT_MAX, line.rstrip())
    if m:
        return ("expect not" if m.group(1) else "expect", m.group(2))
    raise ValueError("line %d: not one of the five verbs: %r" % (n, line))


def install_body(body):
    """Is this grow body an install? None if not; else (rest, name,
    amendment) with name None when the rest is not '<name>' or
    '<name>, <amendment>'."""
    if body != "install" and not body.startswith("install "):
        return None
    rest = body[7:].strip()
    name, amendment = rest, None
    if "," in rest:
        name, amendment = (s.strip() for s in rest.split(",", 1))
        if not amendment:
            name = None
    if name is not None and not NAME_RE.fullmatch(name):
        name = None
    return rest, name, amendment


def normalise(body):
    return " ".join(body.lower().split())


def install_key(name, plan_bytes, amendment=None, machine=MACHINE):
    s = "install %s|%s|%s|abi2|%s" % (name, hashlib.sha256(plan_bytes).hexdigest(),
                                      normalise(amendment or ""), machine)
    return hashlib.sha256(s.encode("ascii")).hexdigest()[:16]
```

**Worked example.** `install_body("install echo, but big")` is
`("echo, but big", "echo", "but big")`; `install_body("install Echo")` is
`("Echo", None, None)` → `no plan named Echo`; `install_body("install")`
is `("", None, None)` → `no plan named ` (the rest is empty);
`install_body("installer")` is `None` (a plain request). The key for
`install echo` on this machine is `install_key("echo", <the bytes of
plans/echo.md>)`.
