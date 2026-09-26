# SEED.md — the seed, how it is rebuilt, and the record of its versions

**Stage 8 ring 8a, plan item 6. Frozen behind the hook from item 13.**
`stage8/parts.py` parses by it (`--seed`, and test 1 through
`checkmolt.py --document`), and from ring 8c `broker/witness.py` rebuilds
by it. If it is wrong, that is a spec question for the owner, not an
edit.

The ring's spec is `stage8/spec.md` ("The witness: re-derivation from the
frozen seed"), and the plan is `stage8/plan-8a.md`, decision 12 and
deviation 8. PARTS.md's word **seed** means what this document defines.

This document is frozen. **The record is not**: `stage8/seed-record.md`
is an append-only file beside it, and this document fixes its format and
its rules. A commit cannot carry its own build's hash, so the record
could never live inside a frozen file.

## The seed

**The seed is `stage8/out/BOOTX64.EFI` as `stage8/mkimage.sh` builds it
from one commit of this repository, with a named version of NASM.** It
holds:
- the loader: everything from `efi_main` to the moment the seed hands a slot to a part (spec, "The loader");
- the cryptography: SHA-256 (`sha256`, `sha256_block`, the round constants);
- the generic implementation of every slot, so a boot that loads no part is always a whole machine.

**What the seed is not:**
- **The stick image** (`stage8/out/stick.img`) and **`esp.img`**. They carry the seed, but their FAT holds timestamps, so two builds a minute apart differ, and OVMF may write `NvVars` into a FAT volume at boot (CLAUDE.md). What the guest must never do to the stick is PARTS.md's and the gates' (its tables unchanged). The seed is the EFI inside, byte for byte.
- **Any part.** A brewed part lives on the SATA disk's home store, never on the stick, and is never built by the builder.

**What may change, and how.** Only the loader and the cryptography are
frozen for good: from ring 8a's item 16b, `stage8/loader.asm` is behind
the hook, and only the owner's hand opens it. The seed's other code (the
slot plumbing each ring adds, the generic implementations) may still
change ring by ring through the usual build loop. **Every seed version
the machine or the witness relies on is one line of the record.** A build
that no line names is work in progress, not a seed: nothing trusts it as
the floor.

## The rebuild

A seed is rebuilt from its line alone, in a **clean workspace**:
the commit's own tree and nothing else, no `out/` directory carried over,
and that tree's own builder.

1. **An empty directory.** `parts.py` uses `stage8/out/seed/<n>/` for seed *n*. It is removed and made again first, so a stale file can never make a rebuild pass.
2. **The commit's tree into it:** `git archive <commit> | tar -x -C <dir>`, run at the repo root. `git archive` writes the committed tree only: no untracked file, no `out/` directory, no uncommitted edit.
3. **That tree's builder:** `<dir>/stage8/mkimage.sh`. It assembles from the tree's own root, so the font's `incbin` and, from item 14, `loader.asm` resolve inside the tree. It writes `<dir>/stage8/out/BOOTX64.EFI` and `esp.img`, and nothing outside `<dir>`.
4. **The NASM that runs the builder must be the line's version**, read from the first line of `nasm -v` (`NASM version 3.02 compiled on …` gives `3.02`). A rebuild under another version is **no rebuild**: it is refused with both versions named, and never compared. NASM's `-f bin` output is a function of the source and the assembler, and a different assembler is a different function.
5. **The hash:** SHA-256 of `<dir>/stage8/out/BOOTX64.EFI`, as lowercase hex, and its length in bytes.

**The rebuild agrees** when both equal the line's `<sha256>` and `<bytes>`.
Anything else is a divergence, named with both hashes. It is never a
retry.

`rebuild_script` below is this recipe as one bash line; `parts.py` runs
it and nothing else.

## The record

`stage8/seed-record.md` holds **exactly one fence**: a line that is
exactly three backticks, and a later line that is exactly three backticks.
Every line between them is a seed line, and there is no blank line
inside. Text outside the fence is commentary, and no reader parses it.

**A seed line** is, with single spaces:

```
seed <n> <sha256> <bytes> <commit> <yyyy-mm-dd> nasm <version>
```

| Field | Rule |
|---|---|
| `<n>` | the seed's number, decimal, no leading zero. The first line is `seed 0`, and each line is one more than the line before |
| `<sha256>` | SHA-256 of the build, 64 lowercase hex digits (the rebuild, step 5) |
| `<bytes>` | the build's length in bytes, decimal, no separator |
| `<commit>` | the commit the build is made from, 7 to 40 lowercase hex digits. It must name exactly one commit, and that commit must be an ancestor of the commit that adds the line (a commit cannot carry its own build's hash, so the line always arrives in a later commit) |
| `<yyyy-mm-dd>` | the named commit's committer date, as `git show -s --format=%cs <commit>` prints it: a fact of the commit, never the day the line was typed |
| `<version>` | the NASM version that made the build (the rebuild, step 4) |

**The record's rules:**

1. **Append-only.** A line, once committed, is never changed and never removed. `parts.py` checks this against the file's own history: at every commit that changed the record, its seed lines begin the next such commit's (`append_only`).
2. **One line per seed version.** A line whose `<sha256>` equals the line before's is refused: it is not a new seed.
3. **Dates never go backwards** down the record.
4. **The witness uses the last line, and no other** (`current_seed`). A build that no line names is not a seed (`seed_named` answers `None`).
5. **A line is added only for a build its gate judged.** It names the commit at which every gate that build should pass was green on that build. The line itself goes into a later commit, with the hash taken from the build, never typed.

**Seed 0** is ring 8a item 1's commit, `bd613b3`: `stage8/stage8.asm`
copied from `stage7/stage7.asm` byte for byte, and a build identical to
ring 7d's 45,056-byte binary. Its gate is ring 7d's, green on that binary
at ring 7d's closure, and ring 8a's test 2 runs the frozen 7c and 7d
checks against it. **The ring's seed**, seed 1, is added at ring 8a's item
17, naming item 16b's commit: the first commit at which the whole ring 8a
gate is green, `loader.asm` frozen.

## SHA-256's known answers

The host hashes every seed with SHA-256, so the host's SHA-256 is checked
first, against FIPS 180-2's two examples and the empty message:

| Message | SHA-256 |
|---|---|
| `abc` (3 bytes) | `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` |
| `abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq` (56 bytes, two blocks after padding) | `248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1` |
| the empty message | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The `abc` answer is the same one PARTS.md gives the guest (`S8: sha256
ok`), and the two documents must agree. `seed_kat()` answers true only
when `hashlib` gives all three. A host whose SHA-256 fails it records
nothing and rebuilds nothing.

## Worked example

**Seed 0 recorded.** Ring 8a item 1's build, rebuilt by the recipe above
under NASM 3.02 on 26 September 2026:

```
$ rm -rf stage8/out/seed/0 && mkdir -p stage8/out/seed/0 && git archive bd613b3 | tar -x -C stage8/out/seed/0 && stage8/out/seed/0/stage8/mkimage.sh
mkimage: BOOTX64.EFI 45056 bytes, packed into esp.img
$ sha256sum stage8/out/seed/0/stage8/out/BOOTX64.EFI
bbf80635a83beeca2254ef35aa492306d30224950b4f405b434b900475b28cd5  stage8/out/seed/0/stage8/out/BOOTX64.EFI
```

That is `rebuild_script("bd613b3", "stage8/out/seed/0")`, and the hash is
ring 7d's binary's (`stage7/out/BOOTX64.EFI`, HANDOVER, ring 8a item 1).
`git show -s --format=%cs bd613b3` prints `2026-09-25`. So
`seed_line(0, <that build>, "bd613b3", "2026-09-25", "3.02")` is the
record's first line:

```
seed 0 bbf80635a83beeca2254ef35aa492306d30224950b4f405b434b900475b28cd5 45056 bd613b3 2026-09-25 nasm 3.02
```

and `parse_seed_line` of it is:

```
{'n': 0, 'sha256': 'bbf80635a83beeca2254ef35aa492306d30224950b4f405b434b900475b28cd5', 'bytes': 45056, 'commit': 'bd613b3', 'date': '2026-09-25', 'nasm': '3.02'}
```

With that line alone in the record, `current_seed` is seed 0, and
`seed_named` names the build `0`. The same build with one byte appended
is named `None`.

**Five records refused**, each a fence holding the lines shown, and the
`ValueError` each raises:

| The fence holds | `parse_seed_record` says |
|---|---|
| seed 0's line with its hash's first four digits `BBF8` | `not a seed line: 'seed 0 BBF80635a83beeca2254ef35aa492306d30224950b4f405b434b900475b28cd5 45056 bd613b3 2026-09-25 nasm 3.02'` |
| seed 0's line numbered `seed 1` | `seed 1 where seed 0 belongs` |
| seed 0's line dated `2026-09-31` | `not a day: 2026-09-31` |
| seed 0's line, then the same line numbered `seed 1` | `seed 1 is seed 0's build again` |
| nothing | `the record holds no seed` |

**A history refused.** A record of two lines (seed 0's, then any seed 1)
followed by the one-line record above is refused by `append_only`:
`a seed line was changed or removed`. The same record twice is accepted.

## Parsing it cold, in Python

`stage8/parts.py` executes this block as its own definitions, read from
this file at import, so the tool and the document cannot drift. The git
plumbing (resolving `<commit>`, its ancestry and date, the record's
history) and running `rebuild_script` are `parts.py`'s.

```python
import datetime
import hashlib
import re

SEED_EFI = "stage8/out/BOOTX64.EFI"                 # the seed: this file as the builder leaves it
BUILDER = "stage8/mkimage.sh"                       # the builder, run from the commit's own tree
RECORD = "stage8/seed-record.md"
FENCE = "```"
VERSION = r"\d+\.\d+(?:\.\d+)?"
LINE_RE = re.compile(
    r"seed (0|[1-9]\d*) ([0-9a-f]{64}) ([1-9]\d*) ([0-9a-f]{7,40}) "
    r"(\d{4}-\d{2}-\d{2}) nasm (" + VERSION + r")")
NASM_V_RE = re.compile(r"NASM version (" + VERSION + r")(?: |$)")
KAT = [                                             # FIPS 180-2's examples, and the empty message
    (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
    (b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
     "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
    (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
]


def seed_kat():
    return all(hashlib.sha256(m).hexdigest() == d for m, d in KAT)


def build_id(efi):
    """What a record line says of a build: its SHA-256 and its length."""
    return hashlib.sha256(efi).hexdigest(), len(efi)


def nasm_version(v_output):
    """The version from `nasm -v`'s first line."""
    m = NASM_V_RE.match(v_output.splitlines()[0] if v_output else "")
    if not m:
        raise ValueError("not nasm -v output: %r" % v_output[:60])
    return m.group(1)


def parse_seed_line(line):
    m = LINE_RE.fullmatch(line)
    if not m:
        raise ValueError("not a seed line: %r" % line)
    n, sha, size, commit, date, nasm = m.groups()
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        raise ValueError("not a day: %s" % date) from None
    return {"n": int(n), "sha256": sha, "bytes": int(size),
            "commit": commit, "date": date, "nasm": nasm}


def record_lines(text):
    """The lines inside the record's one fence, which must be its only fence."""
    lines = text.split("\n")
    marks = [i for i, s in enumerate(lines) if s.startswith(FENCE)]
    if len(marks) != 2 or lines[marks[0]] != FENCE or lines[marks[1]] != FENCE:
        raise ValueError("the record must hold exactly one bare ``` fence")
    return lines[marks[0] + 1:marks[1]]


def parse_seed_record(text):
    seeds = [parse_seed_line(s) for s in record_lines(text)]
    if not seeds:
        raise ValueError("the record holds no seed")
    for i, s in enumerate(seeds):
        if s["n"] != i:
            raise ValueError("seed %d where seed %d belongs" % (s["n"], i))
        if i and s["sha256"] == seeds[i - 1]["sha256"]:
            raise ValueError("seed %d is seed %d's build again" % (i, i - 1))
        if i and s["date"] < seeds[i - 1]["date"]:
            raise ValueError("seed %d is dated before seed %d" % (i, i - 1))
    return seeds


def current_seed(seeds):
    """The witness's seed: the record's last line, and no other."""
    return seeds[-1]


def seed_named(seeds, efi):
    """The seed a build is, by hash and length, or None: a build no line names is not a seed."""
    sha, size = build_id(efi)
    for s in seeds:
        if s["sha256"] == sha and s["bytes"] == size:
            return s["n"]
    return None


def append_only(versions):
    """The record's text at each commit that changed it, oldest first: each
    version's seed lines must begin the next version's."""
    prev = []
    for text in versions:
        cur = record_lines(text)
        if cur[:len(prev)] != prev:
            raise ValueError("a seed line was changed or removed")
        prev = cur
    return True


def seed_line(n, efi, commit, date, nasm):
    sha, size = build_id(efi)
    return "seed %d %s %d %s %s nasm %s" % (n, sha, size, commit, date, nasm)


def rebuild_script(commit, workdir):
    """The rebuild, as one bash line run at the repo root: the commit's tree,
    and nothing else, into an empty directory, then that tree's own builder."""
    return ("rm -rf %s && mkdir -p %s && git archive %s | tar -x -C %s && %s/%s"
            % (workdir, workdir, commit, workdir, workdir, BUILDER))
```
