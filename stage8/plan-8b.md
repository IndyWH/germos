# Stage 8, ring 8b — the first molt · implementation plan

**To be committed verbatim as `stage8/plan-8b.md` at item 0. Written in plan
mode. Nothing below is implemented until the owner opens the plan gate from
his own terminal. Cowork's amendments while the gate holds are added at the
end as A1, A2 and so on.**

**The model note:** CC on Opus 5.5 at high effort for this ring. Recorded in
`HANDOVER.md` at item 0.

## Context

Ring 8a built the floor: a part can fail without taking the machine with it.
Ring 8t closed tonight with verdict B. Ring 8b is the first real molt:
GermOS grows an `i8042` driver for the HP that **beats the one it was given**.

**Done when** (spec): the part, grown by the real backend from its plan and
keyed to the HP's identity, beats the generic in the twin by the plan's
pre-registered rule, passes its shadow threshold on the HP, and runs live
after a reboot and through probation. By the owner's sign-off.

**The owner's rulings of 8 November 2026 are binding here:** A (`i8042`), B
(his hands do two things on the day), C (fewest boots, counted by name), D (a
warm restart proposed for his judgement), E (3 boots stands).

### What this session measured, read-only

No file was written but this one. No guest was booted and no Claude call was
made. `git` is clean at `309ef82`.

| Fact | Result | How |
|---|---|---|
| NASM | Ubuntu has 3.01, the record names 3.02 | `nasm -v`, `seed-record.md` |
| 3.01 against 3.02 | `stage8/out/BOOTX64.EFI`, built tonight by 3.01, is `c221feca…`, **seed 2's hash exactly** | `sha256sum` |
| `parts.py --seed` | It rebuilds **every** line and refuses a version mismatch, so on this host it fails on seeds 0, 1 and 2 | read `run_seed`, `rebuild`. Not run: it writes under `stage8/out/seed/` |
| Guest's wait on a grow | `GROW_TICKS` is **600 s** | `stage8.asm:4737` |
| Serial input on the HP | **Proven.** The ring 7c monitor took commands over COM1 on 18 September, through `broker/probe.py` on `127.0.0.1:9995` | `METAL.md` section 10 |
| LAN port on Ubuntu | `eno2`, `192.168.1.107/24`, no `10.0.2.4` | `ip -br addr` |
| ufw tonight | `ENABLED=no` in `/etc/ufw/ufw.conf` | read |
| Trial-two refusal | `a part is in the pointer's slot` guards `! trial 2` only, so `! trial` can run through a part. To be confirmed by probe | `stage8.asm:6869` |
| Ring 8a's probes | `stage8/out/probe8a/` is **gone** with the Omarchy drive. Item 2 re-measures; nothing leans on it | `ls` |
| HP's disk | 1,087 notes, `part-i8042` current `hang`, previous `good`, state `demoted … unhealthy` | HANDOVER, ring 8t closure |

## The owner's decisions, 8 November 2026

**Settled:** Question 1 yes, Question 2 keep 3 boots, Question 3 five percent
on each secondary, Question 4 yes, Question 5 Opus 5.5, Question 6 yes. **All
fifteen deviations accepted.** Cowork's amendments A1 to A5 are folded in and
listed at the end. The reasoning below stays as the record.

### Question 1 — ruling D: the warm restart. Recommended: yes

**What it is.** `germos restart`, a line sent to the HP over the serial cable
from mlrig. In order (A4):
1. The guest says `order: restart` on serial and draws **`restarting in 3 s`** on the console, so a human mid-word sees why the screen went.
2. The main loop keeps running for 3 s, so input is still fed and compared and no ring overflows.
3. It journals the boot's count note, flushes the disk and writes `0x06` to port `0xCF9`.

It is a full firmware reboot from the stick.

**Why serial, not the two routes the ruling names.** A typed word needs the
owner's hands, or a key typed by accident. A broker frame can only answer a
request the guest has made, so nothing could start it.

| | |
|---|---|
| **What it costs** | About 40 lines in `stage8.asm` beside the order line. One rule in the PARTS.md section. About six checks in test 3. No tokens. A few seconds a boot |
| **The frozen loader** | **Not touched.** The code is in `stage8.asm`. The loader already halts a leftover TCO timer at step 1 of every boot with a molt note (8a finding 2) |
| **Risk 1: a reset before the health mark** | An unhealthy boot counts towards a demotion. The order is refused with `order: not healthy yet` on a boot that loaded a part |
| **Risk 2: losing a note** | The count note and the flush come first. Test 3 parses the disk after each restart |
| **Risk 3: `0xCF9` does nothing on the Q77** | The HP has never run it, though four TCO resets on 28 September came back on the stick. A second write of `0x0E`, then an 8042 pulse, then `order: reset failed`. **Fallback: the owner presses the power button and the day still works** |
| **Risk 4: the 82579LM after a warm reset** | Ring 8e's caveat. The wire is only needed on boot 1, which follows a power-on |
| **Risk 5: an accidental reset** | Not from typing. The order exists only on the serial line, after a fixed prefix |

**If he says no:** the same seven boots, each by the power button. Seven
presses instead of one. The order line stays, because ruling B needs it.

### Question 2 — ruling E: a shorter shadow. Recommended: keep 3 boots

3 boots is unchanged here. A shorter shadow would be sound for this slot. The
comparison is exact and byte by byte, so a boot adds only a fresh decoder
state, and `init` is not shadowed at all, so probation covers it. But with the
warm restart, boots 2 and 3 of shadow cost about two minutes each. The reason
to shorten has gone. It would also be a change to a pre-registered number
before the first grow. Decision 8 stands unless he amends it.

### Question 3 — the secondary margins. Recommended: 5 % on each

The spec fixes the primary at 5 % and leaves "its margin" to the plan. The
plan registers 5 % for worst case per byte and 5 % for size, one number with
no room to tune. Size 5 % means at most 1,209 bytes against `good`'s 1,152.

### Question 4 — the live boots. Recommended: he keeps typing

Ruling B names free use "during shadow". A live part that never sees a real
key has proven only its `init`. **Settled, yes:** the same free use through
boots 5 to 7, for as long as he likes. At least one key and one mouse move on
boot 5 proves the live path, so `stage8/hp-day.py` holds boot 5's restart until
`germos count` shows both, and says so in its terminal.

### Question 5 — the model for the grow. Recommended: Opus 5.5

`--model claude-opus-5-5` for the grow, recorded in the germline's provenance.

### Question 6 — one download. Recommended: yes

Item 1 fetches `nasm-3.02.tar.xz` from `nasm.us` and builds it under
`stage8/out/toolchain/`. See "The NASM question".

## The NASM question

**The rule.** SEED.md step 4: a rebuild under another version is no rebuild.
`run_seed` applies it to every line. So one host needs one version for all
lines, and today's lines all name 3.02.

**Recommended, needing no frozen file opened:** a private NASM 3.02 under
`stage8/out/toolchain/nasm-3.02/`, made by an unfrozen `stage8/mknasm.sh`.
- `PATH=stage8/out/toolchain/nasm-3.02/bin:$PATH python3 stage8/parts.py --seed` then rebuilds seeds 0, 1 and 2.
- **Those three hashes are the proof that this compiler is 3.02.** No trust in the download is needed.
- Seed 3's line says `nasm 3.02`, as built by it.
- Ubuntu's 3.01 stays the daily compiler, as tonight's gate ran. At item 17 both are built and compared. If they ever differ, that is a stop.

**The alternative, if he declines the download:** seed 3's line says `nasm
3.01`, which is true. Then `--seed` fails on some line on every host, for
ever. Making it green needs the owner to open the frozen `parts.py`. Lines 0
to 2 stay as they are in both routes, because the record is append-only.

## The design

### The pipeline: grown before it is asked for

The real grow takes longer than the guest's 600 s wait: up to six `claude -p`
rounds, the bench, then a twin rehearsal with several 60 s health marks. So
**the grow runs on mlrig first**, and the machine then collects the answer.
CC runs it, on the owner's word, at item 19 (A5). The identity comes from the
plan's Identity row. The gate gives another with `--identity`.

```
python3 broker/molt.py --grow i8042 --model claude-opus-5-5 2>&1 | tee stage8/out/grow-8b.log
```

1. **Candidate.** Real: `claude -p`, by the brief below. Gate: a canned fixture.
2. **The door.** `parts.check_part`, PARTS.md's own Python.
3. **The bench** (one boot under `-icount`): events and costs.
4. **Differential.** Events identical to the generic's, event for event.
5. **The measures** by the plan's rule. Cheap steps first, so a loser costs no twin time.
6. **The rehearsal** in the twin (`stage8/rehearse8b.py`): spec gates 1 and 3.
7. **The verdict**, printed and written under `germline/<key>/`. On `beats`, the part is stored under the key.

At most **2 candidates**. Any failure, a gate or a measure, spends one. The
second brief carries the first's failure. Pre-registered in the plan.

**`! molt i8042` over the wire never starts a grow.** It answers at once from
the germline: a part frame with `source` 1 if the guest's own identity builds
that key, otherwise a refusal. **The identity is still read by the guest at
the request**, so a part reaches only the machine it was grown for.

**What this buys on rulings B and C:** the verdict is known before the HP is
powered on. If `the generic stays`, the HP day costs **zero boots**.

### The real backend (unfrozen)

In `broker/claude_backend.py` and `broker/molt.py`:
- The brief carries **`plans/parts/i8042.md` verbatim**, the key `molt i8042|abi3|cpu 000306a9 pci 8086:1e47:04`, PARTS.md's "A part" and "ABI 3's service table" sections verbatim, and the i8042 gotcha bullets read from CLAUDE.md by name, so it cannot drift. It says the part is **for this machine only**.
- The model writes a flat body whose first 12 bytes are `dd init, byte, health`. The host wraps it with `parts.part_header`, because a model cannot know its own SHA-256.
- **`refuse_api_keys()`** runs at start-up and before every call. Any variable matching `API_KEY`, or `ANTHROPIC_AUTH_TOKEN`, ends the process with a named refusal before anything is spawned.
- **`--backend-cmd`** lets the gate point the path at a stub, so the real path is tested without a token.
- **`--collect`** serves the germline and calls no backend at all. The HP day runs this, so a stray `? x` or `! x` typed during free use spends nothing.
- `--timeout 900` for a grow.

### The bench

`stage8/bench.asm` is a small EFI of its own, on the twin's machine shape.
- It runs `cli`, builds its own identity map and never returns to the firmware, so OVMF's NX and timer cannot touch it.
- **The generic through the slot interface is `stage8/fixtures/i8042-good.bin`**, which PARTS.md defines as the generic's decoder exactly and which was frozen before any grow.
- Blocks alternate generic, grown, grown, generic, for eight blocks. Each block starts from a fresh copy of the decoder.
- **The cost of a byte** is the instructions from the `byte` entry to its first upcall, or to its `ret` if it makes no event. The cost of a do-nothing decoder, measured in the same boot, is subtracted.
- It prints every cost and every event on serial. `stage8/bench.py` computes everything. The guest computes nothing.

**The stated limit.** `good` stands for the generic. Its equality is by
construction and by 22,726 real packets at 0 disagreements on the HP, not by
this corpus. The E1 and lost-byte cases have never met the seed's own code
side by side. The real generic is exercised against the part in shadow, in
test 3 and on the HP.

### The order line (ruling B)

The owner's hands must not type `! molt`. The HP's serial input is proven, so:

- **Only on a boot whose notebook holds a molt note.** With no molt note, the machine is ring 7d's and reads no serial byte.
- On those boots the main loop polls instead of halting, as `part_loop` already does.
- A line must begin `germos `. Anything else is dropped with `order: ?`.
- **Six orders:** `germos molt`, `germos molt i8042`, `germos molt take i8042`, `germos molt undo`, `germos restart`, `germos count`.
- **`germos count` is read-only** (added to serve A1). It answers `order: count <keys> <packets> <d>` for this boot. It journals nothing, touches no panel and is never busy, so the day driver can watch the counts while the owner types. `germos molt` could not: it writes a note each time and waits for a gap in the typing.
- A `molt` order goes through `handle_key`, the path a click takes, as the matching `! molt …` line.
- If a key arrived in the last 5 s, the answer is `order: busy` and the driver retries. An unfinished line older than that is discarded, so a word left half-typed on the HP cannot hold up the take.
- **A take order is sent only after the owner's word**, typed in the driver's terminal.
- Everything sent comes from `stage8/hp-day.py` (A1), through `broker/probe.py` on `127.0.0.1:9995`.
- The channel is a physical cable to mlrig. The network cage is unchanged.

### The TSC medians on the metal

On a shadow boot the guest times both decoders with the TSC on every real
byte, into two histograms in BSS. Each count point prints a raw line:
`tsc: i8042 <boot> generic <median> part <median> bytes <n>`. They confirm;
they do not decide. See deviation 6.

### What stays out of the seed

The bench, the rehearsal and the verdict live on the host. The seed gains only
the order line, the restart and the medians, all in `stage8.asm`. **`loader.asm`
is not touched this ring.**

## `plans/parts/i8042.md`, the pre-registration

Committed at item 4, frozen at item 14, before any real grow. Its git commit
is the timestamp. Headings are parsed cold by `bench.py`.

| Section | Content |
|---|---|
| Intent | Fewer instructions on the human's input path, for this machine |
| Identity | `cpu 000306a9 pci 8086:1e47:04`, the HP's, from ring 8a's closure |
| Contract | PARTS.md's entries, and the generic's rules exactly: E0 swallows its successor, shift state, both 128-byte maps verbatim, no E1, a packet's first byte has bit 3 set, stamps as PARTS.md says |
| Corpus | A Python block that yields `(status, byte)`, with its SHA-256 pinned |
| Measures | Primary, median cost per byte. Secondaries, worst case per byte and `96 + B` bytes |
| Margins | Primary at least 5 % lower. Each secondary no more than 5 % worse (Question 3). Integer rule: `part * 100 <= generic * 95` |
| Threshold | 3 boots, 1,000 keyboard bytes, 5,000 mouse packets, 0 disagreements (decision 8). Probation 3 healthy boots |
| Candidates | At most 2 |
| Verdict rule | A Python block: `beats` or `the generic stays`, with every number |

**The corpus covers:** every make and break code; both shifts around makes;
`E0` before every byte value; the `E1` pause sequence; typematic runs; mouse
packets with every button, sign and overflow bit; a lost byte in the middle of
a packet and the resync after it; keyboard bytes between mouse bytes and
inside an `E0`; and a run of plain typing and pointer motion. Keyboard and
mouse bytes are near equal in number, so the median is not one device's.

A plan amended after a failed verdict is a new pre-registration, a new commit,
by the owner's word.

## The acceptance tests

`stage8/test-8b.sh` and `stage8/checkmolt8b.py`, written first. Every run
appends to `stage8/out/gate-8b.log`, with `8b test <n>: PASS|FAIL` lines and a
last `8b gate: PASS|FAIL`. Mock only, no token. It refuses to start if
anything listens on 9999, 9998 or 9997, and it runs alone.

| # | Test | Red until |
|---|---|---|
| 1 | **Artefact and documents.** As 8a. The plan parsed cold, its measures and threshold read back, the corpus hash. `bench.asm` and the three canned fixtures reassembled byte for byte. The PARTS.md section read. The API-key refusal, with a stub proving nothing was spawned. The brief captured through the stub holds the plan, the key, ABI 3, the gotchas and "this machine only" | item 13 |
| 2 | **The pipeline, mocked.** `--grow` with canned parts. `fast` (other code, same events): door, bench, differential, rule, rehearsal, `beats`; then `! molt i8042` delivers it in shadow with `source` 1. `slow`: `the generic stays`, the guest gets a refusal, no note, home unchanged. `wrong` fails the differential; `hang` fails the rehearsal. A guest with another identity is refused. `--collect` calls nothing | item 15 |
| 3 | **Shadow to live, in the twin.** Synthetic human and orders over a serial chardev. Fetch; three shadow boots by restart; take refused below threshold; take; three live boots to probation 3; typing, a note across a reboot, a click; a sitting through the part (`! trial`). `sick`'s `health` fails, the pets stop, the watchdog resets, recovery. `tsc:` lines on shadow boots. `restarting in 3 s` on the console and at least 3 s from `order: restart` to the firmware's first byte. `germos count` against the disk's count note. Every order's refusal. Orders inert with no molt note. Notes before the run unchanged, the stick's tables unchanged | item 16 |
| 4 | **The bodyguard and the regressions.** New paths in `PROTECTED`, payload cases 0 wrong, the argv checks. Then `./trials/test-trial2.sh`, which holds 8a, 7d, 7c, 7b and 7a inside it | item 14, then 16 |
| 5 | **The owner, on the HP.** Below | oracle |

**Expected numbers come from runs.** Item 12 runs a private draft of the guest
and reads each constant from it. Nothing is typed from arithmetic.

## Every deviation from the spec

| # | Deviation | Reason |
|---|---|---|
| 1 | The grow runs on mlrig before the machine asks; `! molt i8042` collects it (test 5 says the grow follows the ask) | The guest waits 600 s and the pipeline is longer. The verdict is known before any boot. The guest's own identity must still match the key |
| 2 | The bench is its own small frozen EFI on the twin's machine shape, not a boot of the seed | No bench path in the seed. A frozen harness cannot drift when the seed changes |
| 3 | The generic in the bench is the frozen `i8042-good.bin` | It is the generic through the slot interface, frozen before any grow. Limit stated above |
| 4 | The cost is entry to first upcall, or to `ret` if there is no event, less a null decoder | The spec's "to the event" has no meaning for a byte that makes none. The overhead is not decoder work |
| 5 | The bench runs at `-smp 1` if item 2 confirms it | The counter is global; other vCPUs would add to it |
| 6 | The TSC medians go on the serial chart, not the notebook | PARTS.md's frozen note grammar has no such note, and `check_notes` fails a `molt ` note that does not parse. They confirm; they do not decide. The chart goes to `history/` |
| 7 | A new input channel, the serial order line, which the spec does not have | Ruling B. Only on boots with a molt note; six fixed orders (the sixth, read-only, added to serve A1) |
| 8 | The warm restart, and three shadow boots in one sitting where test 5 says "sessions" | Rulings B and D. Decision 8 counts boots, and each is a full firmware reboot. If D is declined, this falls away |
| 9 | The corpus lives in the plan. PARTS.md gets a pointer with the SHA-256 | The kickoff puts it in the plan. PARTS.md already reserves a planned opening. One text, pinned from the other |
| 10 | Test 4 runs ring 8t's gate, which holds 8a's | Seed 3 must keep trial two green too. A superset of the spec's |
| 11 | The rehearsal and the bench are frozen as well as the plan, corpus and rule | A bent bench is a bent verdict. Ring 5 froze `rehearse.py` for this reason |
| 12 | A third canned part, `sick` | The spec's "the pet routine sees `health()`" needs a part whose `health` fails |
| 13 | **One exception to ruling B:** the stick moves once, before the day (plug into mlrig, `trials/hp-stick.sh`, plug into the HP) | Seed 3 is a new binary and the flash is the owner's hand by standing rule |
| 14 | Free use of the keys on the live boots too (Question 4) | A live part should meet a real key |
| 15 | A private draft of the guest before the freeze (item 12) | 8a deviation 14, accepted then. Numbers from runs |

## Conventions for every item

- One commit per item. Tests that should pass are green before each commit.
- Commit messages through `git commit -F` from a file.
- The whole gate is run alone. Earlier gates go one at a time.
- **A frozen file that turns out wrong is never edited.** Stop, write the diff unapplied under `stage8/out/`, and wait for the owner.
- Two honest attempts per obstacle, with a diagnosis between them.
- CC never spells a device path, never flashes and never runs the sudo block.
- **Every block the owner pastes has no quotation marks** (A3), in HP-8b.md and at every stop.
- **Cowork is never given a step that starts a service or sends an order** (A1). Its shell sees only the repo folder. It reads and reviews.

## Part 1 — probes and machinery, before the code

**Item 0 — the plan and the record.** `stage8/plan-8b.md`. HANDOVER: Where we
are, with Machine (Ubuntu 26.10), Toolchain (tonight's versions), Model (CC on
Opus 5.5 at high effort); tonight's gate and policy check; `probe8a` gone.
CLAUDE.md's fresh-clone gotcha becomes `mkdir -p stage{0..8}/out trials/out
stage7/out/metal`, as the second correction.

**Item 1 — the toolchain.** First, `gcc`, `make` and `xz` are checked on mlrig
(A2). If any is missing, stop and give the owner one `sudo apt` block, with no
quotation marks. Then `stage8/mknasm.sh`. `parts.py --seed` on the private
3.02: seeds 0, 1 and 2 rebuilt and agreeing.

**Item 2 — the bench probes, private, under `stage8/out/probe8b/`.**
1. `-icount shift=0,sleep=off` on QEMU 11.0.3: a known count of instructions gives that delta plus a constant, at `-smp 1`, 2 and 4.
2. Five repeats each. The counts must be identical. **If they are not, stop: it is a spec question.**
3. The alternation: generic against generic gives zero difference in every block, so order has no effect.
4. The own identity map and `cli`. The null decoder's cost.
5. The wall time.

**Item 3 — the serial and restart probes, private.**
1. A chardev with a logfile delivers lines to a private draft, in `main_loop` and in `part_loop`.
2. `0xCF9` resets q35. The stick boots again, the disk persists, no evidence bit, no recovery, the leftover TCO causes no reset.
3. A `tsc:` and an `order:` line are invisible to the frozen 8a and 8t checks.
4. The argv: how the chardev passes `check_argv_7c`.
5. `! trial` runs through a live part.
6. Each pipeline step's time, and the hook's verdict on every new command shape, the tee to `grow-8b.log` and `stage8/hp-day.py` among them.
7. The 3 s notice: input keeps flowing with no overflow, and the time to the firmware's first byte.

**Item 4 — `plans/parts/i8042.md`,** written and committed. No grow exists yet.

**Item 5 — the canned parts.** `stage8/fixtures/i8042-{fast,slow,sick}.{asm,bin}`.
If `fast` cannot be made to beat `good` by 5 %, that is a finding the owner
hears before the freeze.

**Item 6 — `stage8/bench.asm` and `stage8/bench.py`.** The plan read cold, the
verdict by its rule.

**Item 7 — `stage8/rehearse8b.py`.** Built on `checkmolt`'s synthetic human by
import, at its seams.

**Item 8 — `broker/molt.py`, the real path.** `--grow`, `--collect`,
`--backend-cmd`, `refuse_api_keys`, `PART_BRIEF`. Unfrozen. Exercised only
through the stub.

**Item 9 — `test-8b.sh`, tests 1 and 2.** Red.

**Item 10 — test 3.** Red.

**Item 11 — test 4.** Red.

**Item 12 — the draft.** The guest code on a private copy. Each constant read
from a run. The checker runs against the draft until every clause is proven
able to pass.

**Item 13 — the PARTS.md section. STOP for the owner.** CC writes
`stage8/out/parts-8b-section.md`: the corpus pointer and hash, the order line,
the restart, the `tsc:` line, and a sentence superseding "The corpus". **This
is the project's eleventh freeze opening, planned, by the owner's hand:** one
`cat >>` onto `stage8/PARTS.md`, the block with no quotation marks. No
existing line changes. Then `python3
stage8/parts.py --example`, run once.

**Item 14 — the freeze.** Added to `PROTECTED`: `plans/parts/i8042.md`, the
three canned parts, `bench.asm`, `bench.py`, `rehearse8b.py`, `test-8b.sh`,
`checkmolt8b.py`. Payload cases added, 0 wrong.

## Part 2 — the implementation

**Item 15 — the order line, the read-only count and the restart with its 3 s
notice (A4).** Test 2 green; test 3 partly.

**Item 16 — the TSC medians.** Tests 1 to 3 green.

**Item 17 — seed 3 and the paperwork.** The whole gate green alone, about
110 minutes (an estimate; item 3 measures the pieces). Then, in the next
commit, seed 3's line from a rebuild under 3.02, compared with 3.01's build.
HANDOVER, CLAUDE.md's ring 8b block, README. Stages 0 to 6 green once.

**Item 18 — `stage8/hp-day.py` and `stage8/HP-8b.md`.** The day driver (A1,
unfrozen) and the owner's day.
- **Proven end to end in the twin:** the driver in a twin mode, the guest's serial on a chardev in place of the port, the synthetic human at the keys, `take` fed to its terminal. `parts.py --serial` must read the driver's log unchanged.
- **The connection for `eno2` (A3).** The hook denies CC the word for NetworkManager's tool, so this is one paste by the owner at this stop, into a repo file CC then reads:

```bash
nmcli -g UUID,DEVICE connection show > stage8/out/eno2-connection.txt
```

  HP-8b.md's sudo block then carries that UUID written out, which has no spaces and needs no quotation marks.

**STOP: green pending the oracle.**

**Item 19 — the real grow, in its own step (A5).** On the owner's word, after
Cowork has re-checked the policy gate that day. CC runs the command under "The
pipeline" once. Its whole output is in `stage8/out/grow-8b.log`, and the file
goes to `history/` at the closure. **STOP: the verdict is reported, and the
flash waits for it.**

## Test 5 — the owner, on the HP

### Before the HP is touched

1. **The policy gate**, re-checked by Cowork on the day of the grow.
2. **The grow, item 19, run by CC on the owner's word.** Real `claude -p`, on mlrig, no API key, whole output in `stage8/out/grow-8b.log`. **If `the generic stays`: no flash and no boot.** The finding is recorded, and he chooses between amending the plan and another slot.
3. **If it beats:** the stick moves once, by `trials/hp-stick.sh`.
4. **mlrig again on Ubuntu, one sudo block for the owner.** `<UUID>` is written out in HP-8b.md from item 18's file:

```bash
sudo nmcli con mod <UUID> +ipv4.addresses 10.0.2.4/24
sudo nmcli con up <UUID>
sudo ufw status | grep -qw active && sudo ufw allow in on eno2 from 10.0.2.15 to 10.0.2.4 port 9999 proto tcp comment germos-hp
ip -4 addr show eno2
```

The `con up` drops mlrig's LAN for a moment. `ip -4` must list both addresses.
If `eno2` is unmanaged, `sudo ip addr add 10.0.2.4/24 dev eno2` instead.

5. **The day driver, one command by the owner on mlrig, before the power button:**

```bash
python3 stage8/hp-day.py
```

### What `stage8/hp-day.py` does (A1)

- **It checks first,** and stops with one plain line if anything is wrong: the adapter, the second address, the ports free, and the build equal to the record's last seed.
- **It starts** the chart with its way back in (`broker/probe.py`), `broker/molt.py --collect` and `broker/relay.py`.
- **It sends every order itself** when the chart shows its condition, by the table below.
- **It writes everything it sends and sees** to `stage8/out/hp-8b.log` in the repo. Cowork reads that file.
- **It stops the services at the end,** and says the ring's closing word is his.

### The boots, by name (ruling C)

**Seven is the fewest the spec allows:** a fetch, because a part loads only
at boot; three shadow boots (decision 8); three healthy live boots
(probation). The 8a safety cases are not repeated.

| Boot | Name | Started by | Purpose | Ends when |
|---|---|---|---|---|
| 1 | fetch | **the owner's one press** | Seed 3 on the HP, 1,087 notes, the demoted part unloaded. `germos molt i8042` installs the part | `molt: i8042 shadow <sha16> 3 1000 5000`, then restart |
| 2 | shadow 1 | restart | Real traffic beside the generic | `S8: healthy <n>`, then restart |
| 3 | shadow 2 | restart | The same | the same |
| 4 | shadow 3 | restart | Runs on until the driver's `germos count`, added to the earlier boots' notes by `parts.py`'s rule, reaches 1,000 and 5,000 | The driver stops and asks in its own terminal. **He types `take`.** It sends `germos molt take i8042`, then restart |
| 5 | live, probation 1 | restart | `init` on the real controller, keys and mouse through the part | `S8: healthy <n>` and at least one key and one packet, then restart |
| 6 | live, probation 2 | restart | The same | the same |
| 7 | live, probation 3 | restart | The same | `S8: healthy <n>`, the table says `probation 3/3`. **His word closes the ring** |

**His hands on the HP:** one press of the power button, then the keys and
mouse, freely. He reads nothing and reports nothing on the HP. On mlrig he
starts the driver and types one word, `take`. Cowork reads
`stage8/out/hp-8b.log`. About 30 minutes, an estimate from ring 8a's day.

**If something goes otherwise**, the driver does this and says so in its
terminal and the log:
- `S8: recovery owner`: Esc was pressed in the window. Nothing is demoted. It sends restart.
- A `disagree` note, an `ERR:` line or any other recovery: it stops sending and leaves the services up. PARTS.md's stated limit on discarded keys is the first suspect for a disagreement. Cowork reads the log, and the owner decides.
- `order: reset failed`: it asks him to press the power button, and carries on from the chart.
- A hang or a fault on a live boot: the floor proven at 8a takes it, and the finding is recorded.

**At the end:** the chart, the verdict and any photographs into `history/`
that day (ring 8t's finding), the record in HANDOVER, the owner's `git push`.

## Verification

- `./stage8/test-8b.sh`, whole and alone, ends `8b gate: PASS`.
- `PATH=stage8/out/toolchain/nasm-3.02/bin:$PATH python3 stage8/parts.py --seed` agrees on all four seeds.
- `python3 .claude/hooks/payloads.py` ends 0 wrong.
- `stage8/hp-day.py` in its twin mode drives all seven boots to `probation 3/3`, and `parts.py --serial` reads its log.
- The real grow, in `stage8/out/grow-8b.log`, prints `beats` or `the generic stays`, with every number.
- `stage8/out/hp-8b.log` read by `python3 stage8/parts.py --serial` shows `live` and `probation 3/3`.

## Risks

| Risk | Likelihood | What absorbs it |
|---|---|---|
| The grown part does not beat the generic | **High** (the spec says certain it may not) | A result, recorded. No boots spent. The owner amends or moves on |
| `-icount` does not repeat under QEMU 11.0.3 | Low | Item 2 stops before anything freezes |
| Polling on boots with a molt note disturbs an earlier gate | Low | Item 3, and test 4 |
| `0xCF9` fails on the Q77 | Low | The power button |
| A human's typing trips the discard limit | Low | `--collect` answers at once, so nothing is held back. Never met on 28 September |
| Time and tokens | Low | At most 2 candidates, 6 calls. The gate spends none |

## The stops

1. **The plan gate.** Now.
2. **Item 13, the planned freeze opening.** Any other opening is a stop too, with the diff unapplied under `stage8/out/`.
3. **Item 18, green pending the oracle,** with the owner's one paste for `eno2`.
4. **Item 19, before the real grow:** Cowork's policy re-check that day, then the owner's word. And after it: the verdict is reported before any flash.

## Amendments — Cowork's review, adopted 8 November 2026

- **A1 (blocking). No step has Cowork start a service or send an order.** Its shell sees only the repo folder. `stage8/hp-day.py`, unfrozen, is started by the owner with one command on mlrig, and does the starting, the sending and the logging to `stage8/out/hp-8b.log`. On shadow 3 it asks in its own terminal, and he types `take`. Replaces `hp-8b.service` and `hp-order.py`.
- **A2.** Item 1 checks `gcc`, `make` and `xz` first. If any is missing, stop and give the owner one `sudo apt` block.
- **A3.** Every block the owner pastes has no quotation marks. The sudo block is rewritten, and the connection for `eno2` is read at item 18.
- **A4.** Before a restart the guest prints `restarting in 3 s` on the console as well as the order line on serial, waits 3 s, then resets.
- **A5.** The real grow is run by CC on the owner's word, in its own step, item 19, after Cowork re-checks the policy gate that day, with its whole output in `stage8/out/grow-8b.log`.

**Two small additions made while folding A1 in, for the review:**
- A sixth order, `germos count`, read-only. A1's "when the counts are met" needs the counts while the owner is typing.
- An unfinished line older than 5 s is discarded when an order arrives, so a half-typed word on the HP cannot block the take.

## For Cowork's review

The owner copies this plan to where Cowork can read it:

```bash
cp /home/indy/.claude/plans/pasted-content-id-5684-ring-8b-hidden-gray.md /home/indy/Projects/germos/stage8/out/plan-8b.review.md
```
