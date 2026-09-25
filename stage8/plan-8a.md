# Stage 8, ring 8a — the floor · implementation plan

**To be committed verbatim as `stage8/plan-8a.md`. Produced in plan mode,
per the foundation's build loop. Nothing below is implemented until Wajira
approves this document by writing the approval marker from his own
terminal; the ExitPlanMode hook holds the gate until then. Plan mode allows
this session to write only this one file and forbids commits and boots, so
— as every ring since 6a — the copy to `stage8/plan-8a.md` and its commit
are the first act after the gate opens, item 0 below, before any other file
is touched. Cowork's amendments while the gate holds are adopted here as
numbered amendments (A1, A2, …) in the section at the end.**

**The model note, for the record:** this ring is implemented on **Opus 5.5
at high effort**, the owner's decision (spec decision 11, 25 September
2026). Recorded here and in `HANDOVER.md` at item 0.

## Context

Stage 7 closed on 25 September 2026 with ring 7d (verdict A). `stage8/spec.md`
(approved by the owner on 25 September 2026, all fourteen decisions settled)
opens **Stage 8, the molt**: the OS replaces the generic core with parts it
grew itself, one slot at a time, behind a floor that cannot be pulled out
from under it. **Ring 8a, the floor**, proves that *a part can fail without
taking the machine with it*. In the twin of the HP, five hand-written
fixture parts for the `i8042` slot meet their fates:

- `good` passes shadow with no disagreement and runs live after `! molt take`;
- `wrong` is caught in shadow and cannot be taken;
- `hang` is reset by the hardware watchdog, and the next boot comes up on the seed's own driver with the part demoted;
- `fault` is named by the blame line and recovered the same way;
- `liar` is refused at the door.

With no part installed, the machine is ring 7d's to the line and to the
pixel. On the HP, by the owner's hand: `good` live, then `hang` live, and
**the HP resets itself** and comes back in recovery.

What this ring builds, from the spec's "Ring 8a — the floor":

- **`stage8/stage8.asm`**, copied from `stage7/stage7.asm` at item 1, byte for byte. At item 14 the loader and SHA-256 move out of it into **`stage8/loader.asm`**, which `stage8.asm` includes. `loader.asm` is frozen at item 16b, after Cowork's review (A6).
- **The slot table**, ABI 3 and the part frame; the `part-` names in the home store; the `molt ` notes; the four `! molt` words; the shadow ring and the comparison for `i8042`.
- **The floor itself:** the TCO watchdog, the pet routine, the health mark, the recovery rules, Esc at power-on, the blame line, and the loader's pages read-only.
- **`broker/molt.py`**, the molt broker, a subclass of the wire broker. `--mock` serves the fixtures and spends nothing.
- **`stage8/PARTS.md`** and **`stage8/SEED.md`**, the frozen documents, and **`stage8/parts.py`**, the host tool that parses them cold.
- **The five fixtures**, `stage8/fixtures/i8042-{good,wrong,hang,fault,liar}.{asm,bin}`.
- **`stage8/test-8a.sh`** and **`stage8/checkmolt.py`**, acceptance tests 1 to 4. They are written before any new guest code, and every run appends to `stage8/out/gate-8a.log`.
- **`stage8/HP-8a.md`**, the owner's day on the HP (test 5), in the shape of `stage7/METAL.md`.

**The owner's decisions, already made, not reopened here:** all fourteen
of the spec's. In particular: the first slot is `i8042` (1); rings 8a to 8g
(2); parts in the home store under `part-` names, with the state in `molt `
notes (3); the loader in its own frozen file, read-only after the handover,
with its own disk read path (4); the PCH's TCO with a 30 s deadline, a 60 s
health window, the recovery table and Esc at power-on (5); a shadow
threshold of 3 boots, 1,000 keyboard bytes, 5,000 mouse packets and 0
disagreements, then probation for 3 healthy boots (8); Opus 5.5 at high
effort (11); the GPS rewrite postponed (12, not raised here); the TRIALS.md
sentence applied by the owner's hand (13 — done this morning, the eighth
freeze opening); the policy gate re-checked at every ring's kickoff (14 —
re-checked by Cowork on 25 September 2026: unchanged).

The standing orders:

- **The gate and the mock.** The automated gate talks only to the mock, spends no token and needs no internet.
- **The cages stand.** The cage, the storage bodyguard and every frozen file stand. `./stage7/test-7d.sh` (with the 7c, 7b and 7a gates inside it) must pass at the end of the ring, and so must every earlier gate.
- **The scope guard.** A frozen file that turns out wrong is never edited: stop at the commit boundary, write the diff unapplied under `stage8/out/`, say so in `HANDOVER.md`, and wait for the owner's hand. Two honest attempts per obstacle, with a real diagnosis between them.
- **The approval marker.** Never create or mention it from inside a session.
- **Commits.** One commit per numbered item; `/clear` between items.
- **Tests and code.** Tests are written before the code they judge. Tests are green before every commit that should pass them.
- **Numbers in frozen tests.** Every number in a frozen test is written from a run or derived by a frozen document's rule, never from arithmetic. Three freeze openings of that class are on the record: ring 6b item 10b, ring 6c item 11b and ring 7b item 10b.
- **The flash.** CC never spells a `/dev` path, never runs `dd` and never flashes anything.
- **The budget.** If the owner says the budget is nearly spent: finish the item, commit, record the state, stop.

The plan is **evaluation-first**:

- **Items 1–3** open the stage on a byte-identical copy of the ring 7d source and measure the four things the spec says a probe must measure before any freeze (D1–D4).
- **Items 4–8** write the documents, the fixtures, the tool and the mock.
- **Items 9–11** write the four acceptance tests. At that point no new instruction of guest code exists in the repository.
- **Item 12** drafts the implementation on a private copy and reads every number the checker needs from a run.
- **Item 13** freezes the acceptance machinery.
- **Items 14–16** bring the code in, in three reviewed commits. After item 16 the session stops for Cowork's review of `loader.asm` (A6).
- **Item 16b** freezes `loader.asm`: the item where the gate first passes on it (A6).
- **Item 17** is the handover and the owner's procedure.

**Tests 1 and 2 go green at item 9** (test 2 is "no part, no change", and
the binary is ring 7d's until item 14). **Test 3 goes green at item 16.**
**Test 4 goes green at item 16b**: from item 13 it is red on one clause by
design, `loader.asm` not yet frozen. Test 5 is Wajira's.

### Environment, measured in this session before planning

This session was read-only. No file was written but this one, no guest was
booted, nothing frozen was touched and no Claude call was made. The working
tree is clean at `076d74b`.

**The toolchain**
- **Versions on mlrig under Omarchy:** NASM 3.02, QEMU 11.1.1, Python 3.14.7, OVMF at `/usr/share/ovmf/OVMF.fd`. The `claude` CLI is now **2.1.282**; the spec said 2.1.280.
- **Out directories:** every `stage0..8/out` exists on this machine. `stage8/out/` holds the kickoff's four files: `apply-trials-label-rule.py`, the two commit texts and `trials-sentence-test1.log`.
- *How measured:* `--version` of each tool; `ls`.

**QEMU: the watchdog, `-icount` and the argv check**
- **The ICH9 TCO's properties.** `ICH9-LPC` has **`noreboot=<bool>` (default off)** and **`enable_tco=<bool>`**, whose default is not printed. `-machine q35` has `wdat=<bool>` (default off). The action is `-action watchdog=reset|shutdown|poweroff|inject-nmi|pause|debug|none`, **default `reset`**. `i6300esb` (PCI) and `ib700` (ISA) are the only watchdog devices.
- **QEMU does not document** whether the ICH9 TCO resets the machine, how its two expiries map to time, or what its status bits hold across a reset. Its manual's only watchdog example is `-device i6300esb -action watchdog=pause`. So D1 measures all of it (the sixth freeze opening's lesson: pin nothing a tool does not document).
- *How measured:* `-device ICH9-LPC,help`, `-machine q35,help`, `-device help`, `-help`, `/usr/share/doc/qemu` searched.
- **`-icount` is TCG only and "incompatible with multi-threaded TCG"** (QEMU's `tcg-icount` page). Its form is `-icount [shift=N|auto][,align=on|off][,sleep=on|off]`. **No gate passes `-accel`**, so every twin already runs TCG. What `rdtsc` returns under it, and whether counts repeat across runs at `-smp 2` and `4`, is D2.
- *How measured:* `/usr/share/doc/qemu/qemu/devel/tcg-icount.html`; grep of `checkmetal.py` and `twin.py`.
- **The frozen `check_argv_7c`** demands exactly five `-device`s, `-cpu IvyBridge`, the one cage and two drives under `checkmetal.OUT`. It inspects neither `-global`, `-icount`, `-action` nor `-no-shutdown`.
  - **An `i6300esb` would make six devices and fail it.** The ICH9 TCO is built into q35 and adds no device, so if D1 finds it resets the twin, 7c's argv check holds unchanged.
- *How measured:* `stage7/checkmetal.py` 916–980.

**The frozen checkers' seams (D3's starting point)**
- **None of the frozen 7c or 7d checkers takes a path by flag or by environment variable.** They are module attributes read at call time:
  - `checkmetal.STICK`, `OUT`, `METAL_OUT`, `DISK`, `GERMLINE`, `REHEARSAL`, `TWIN_WORKDIR` and `ESP`; `checkmetal.qemu_argv`;
  - `checktrials.STICK`, `OUT`, `TRIALS_OUT` and `DISK`;
  - the bound defaults of `checkmetal.check_stick` and `check_stick_tables_unchanged`.
- `checktrials` imported `qemu_argv`, `fresh_stick` and `start_mock` by name, so those are separate bindings.
- The shell gates hard-code `stage7/out` and rebuild from `stage7/stage7.asm`, so the frozen *shell* gates can only ever judge ring 7d's own binary.
- The entry points are `checkmetal.run_stick`, `run_serial(mode, smp)`, `run_stages` and `run_cage`, and `checktrials.run_document`, `run_row`, `run_sitting` and `run_cage`.
- `mkstick.build_table` is deterministic (both GUIDs fixed), so a Stage 8 stick of the same size has the same table sectors.
- *How measured:* read of `checkmetal.py` 51–71, 363–412, 557, 692, 1082; `checktrials.py` 46–58, 309–329, 1172; `stage7/mkstick.py` 33–35.

**The guest: layout, pages and the i8042 path**
- **The layout.** `stage7.asm` is 11,456 lines. The image is at ImageBase `0x400000`: headers, `.text` `0x401000`–`0x408FFF` (32 KB, pure code, no data inside), `.data` `0x409000`–`0x40AFFF`, and BSS to `0x5E0FFF`.
  - **The whole image sits inside one 2 MB identity page.** `build_paging` maps 0–4 GB with 2 MB pages only; there is no 4 KB page-table builder.
  - **CR0.WP is never set** on any core.
  - `.data` mixes constants (`sha_k`, strings, the font, `scan1_map`, `gdt`) with runtime-written variables (`gdtr`, `idtr`, `svc_table`, `fb_*`).
  - **There is no TSS.**
  - `exc_common` prints `ERR: exception <v> at 0x<rip>` and halts **the faulting core only**; the glass core keeps painting.
- *How measured:* read, lines 55–720, 1051–1082, 1947–1960, 10574–10618, 11103–11456; `BOOTX64.EFI` 45,056 bytes.
- **The idle BSP sleeps in `hlt` with IRQ0 masked and no LAPIC timer**, so it wakes only on IRQ1 and IRQ12. A pet that lives only in the main loop would starve on an idle machine; decision 9 answers this.
  - The glass core increments `OBS_FRAMES` (`0x28`) every frame at 60 Hz.
  - No BSP heartbeat exists.
- *How measured:* `main_loop` 1422–1471; `glass_main` 9984–10068; `pic_init` 2015–2044.
- **The i8042 path, about 720 lines.**
  - `irq1_entry` and `irq12_entry` save only RAX, RBX, RCX, RDX, RSI, RDI and R8, and call `i8042_service`. That reads port `0x64` then `0x60` once, and routes by status bit 5 to `mouse_byte` (packet assembly, clamp, obs fields and ring, *in interrupt context*) or to `kbd_push` (raw scancode ring).
  - `kbd_next` decodes in the main loop: E0 swallows its successor; shift; `scan1_map`; no E1; `OBS_KEYS` counted in the consumer.
  - `mouse_init` holds the self-test, the command byte, the mouse reset and the two `i8042:` lines.
- *How measured:* read, 2002–2518, 1802–1868.
- **SHA-256** is `sha256` (4757) and `sha256_block` (4826), with `sha_k` and `sha_init` in `.data`. It has exactly two callers, `home_install` and `home_launch`. `home_undo` reuses `sha_tail` as scratch, which matters when SHA-256 moves. There is no known-answer test today.
- *How measured:* read.
- **The disk read path** is `ahci_find` … `ahci_rw`, `gpt_*`, `blk_rw`, `notebook_init`, `record_valid`, `notebook_replay` and `home_init`, all run from `efi_main` before the glass core and the i8042. The home table is 16 entries of 256 bytes in BSS. `note_verdict_check` runs inside the replay.
- *How measured:* read, 3092–4750, 8639–8848.
- **`bang_line` order:**
  1. empty → broker;
  2. `trial` (5 bytes) → `trial_start`;
  3. `undo install ` → `home_undo`;
  4. a home name → `home_launch`;
  5. otherwise → `grow_request`.
- `line_is_reserved` checks the prefix `trial ` in the Enter path after `parse_marker`. Grown apps run in ring 0 on the BSP stack, called from the main loop, never in interrupt context.
- *How measured:* read, 1554–1566, 4551–4586, 7255–7264.
- **The obs page** is at BSS `0x4D1000` at runtime. Its highest field is `layout_default` at `0x338`, then four reserved zero words at `0x340`–`0x358`, and zero from `0x360` (TRIALS.md). Ring 8a writes nothing to the page with no part installed.
- *How measured:* read, 420–505; TRIALS.md 285–310.

**The broker, the home store and the fixtures**
- **The broker's wire.**
  - The frozen `germline.handle` answers a `0x01` grow or a printable question and drops anything else, so **a molt request must ride as a grow body**, as `install` does (`plans.install_body`).
  - The frame kinds are `0x00` refusal, `0x01` component (ABI 1) and `0x02` app (ABI 2). **Neither `0x03` nor ABI 3 exists.**
  - The germline key is still `qemu-q35-ovmf` in `germline.py`, `glass.py` and `plans.py`.
  - The rehearsal twin hard-codes `! rehearsal` and the app frame, so an 8a part is **not rehearsed**; that is ring 8b's pipeline.
- *How measured:* read, `germline.py` 62, 274–314; `glass.py` 75, 111–127, 201; `plans.py` 168, 404–419; `twin.py` 88–118.
- **The home store (HOME.md, frozen)** has 16 entries. A name must match `[a-z][a-z0-9-]{0,31}`, so `part-i8042` is legal. The entry holds the SHA-256 and the previous build (undo swaps them); a torn entry is ignored; space is never reclaimed.
  - The frozen rules would count a `part-` entry in `home N apps` and list it on the choices row, so **PARTS.md must supersede those sentences** (decision 4).
- *How measured:* `stage6/HOME.md` 52–139.
- **The ring 6 fixture pattern.** Each fixture is a flat `bits 64` / `default rel` blob with a banner that states its fate. Its `.asm` and `.bin` are both in `PROTECTED`, with `!` lines in `.gitignore`. `checkglass.fixture_self_check` re-assembles the source into `out/<name>.check.bin` and demands the committed binary byte for byte.
  - `liar.asm` and `liar.bin` are already frozen basenames (stage6), so the ring 8a fixtures take a slot prefix, `i8042-<fate>`, and no basename collides.
- *How measured:* `stage6/checkglass.py` 660–681; `.gitignore`; `protect-tests.py` 225–296, 485–507.

**The hooks**
- **The hook's rules.** `PROTECTED` is 63 paths. `resolve()` protects an exact basename when it is bare, and a path when it ends in `/`+ a protected path. Write and Edit are judged by the target path only.
- **The proposed names are all writable today:** `stage8/test-8a.sh`, `checkmolt.py`, `parts.py`, `PARTS.md`, `SEED.md`, `loader.asm`, `fixtures/i8042-*.{asm,bin}` and `broker/molt.py` (no basename equals a frozen one).
- **The payload table** has 1678 cases: 1117 deny, 561 allow. `freeze_cases` gives 18 cases per path.
- *How measured:* read of `protect-tests.py`, `payloads.py` 55–83, 858–948.
- **The plan gate:** `.claude/hooks/require-plan-approval.py` denies `ExitPlanMode` until the owner's marker exists, and consumes it once.
- *How measured:* read.

**To be measured at items 1–3, before any test is written.** Plan mode
forbids a boot. Every probe boots a private copy under
`stage8/out/probe8a/`, touches nothing frozen and is never committed. Every
number goes into `HANDOVER.md`'s ring 8a environment table with its date.
The four probes (D1–D4) are specified under items 1–3.

---

## Decisions taken in this plan

1. **The files.** Frozen at item 13:
   - `stage8/PARTS.md`, `stage8/SEED.md`, `stage8/parts.py`;
   - `stage8/test-8a.sh`, `stage8/checkmolt.py`;
   - `stage8/fixtures/i8042-{good,wrong,hang,fault,liar}.asm` and their five `.bin`.

   Frozen at item 16b, after Cowork's review (A6): `stage8/loader.asm`.

   Never frozen (the builder, not the criterion):
   - `stage8/stage8.asm`, `stage8/mkimage.sh`, `stage8/mkstick.py`;
   - `broker/molt.py` (decision 14);
   - `stage8/seed-record.md` (decision 12);
   - `stage8/HP-8a.md`, `stage8/plan-8a.md`.

   The scratch directories are `stage8/out/molt/` (the gate's), `stage8/out/seven/` (test 2's seams) and `stage8/out/probe8a/` (the probes'). The log is `stage8/out/gate-8a.log`.
2. **The slot and ABI 3** (PARTS.md). A slot is a set of three entry pointers, `init`, `byte` and `health`. The slot table holds the generic's pointers by default, and ring 8a fills only `i8042`.
   - **A part** is a flat position-independent blob (`bits 64`, `default rel`, no absolute address; GERMLINE.md's rule). Its **header** is: the magic `PART`, `u8` ABI `3`, the slot name (8 bytes, NUL-padded), the body length, the three entry offsets, a fixture/part name (16 bytes), and the SHA-256 of the body after the header. PARTS.md fixes the byte layout.
   - **The entries:**
     - `init(svc)` does the controller's cold init and the mouse reset; it is called only when live.
     - `byte(status, data, stamp)` takes one byte read by the seed's stub.
     - `health()` answers 0 for ok and a code otherwise.
   - **The ABI 3 service table:** `u32` ABI 3, `u32` size, then PCI config read32/write32, an uncached MMIO mapping, DMA pages below 4 GB, `ticks_ms`, `pit_wait`, one raw serial line (the seed prefixes `part: `), and the slot's upcalls. For `i8042` the upcalls are `key_event(key, stamp)` and `mouse_packet(dx, dy, buttons, stamp)`. There is nothing else: no notebook, no framebuffer, no network.
   - **The calling convention** is the app ABI's: arguments in RDI, RSI, RDX and RCX. The seed treats every register but RSP as clobbered, pushes its loop state and restores RSP from its own save, as `app_call` does.
   - **The part is never called in interrupt context.**
     - With no part loaded, the IRQ path is today's instruction for instruction.
     - With a part in shadow, the stub also appends `(status, byte, stamp)` to a raw ring, and the main loop feeds it to the part.
     - With a part live, the stub appends only; the main loop feeds the part, and the part's upcalls enter the seed at the same key and packet sinks the generic uses (the half of `mouse_byte` after assembly; the key path `handle_key` consumes).
3. **The molt request and the part frame** (PARTS.md; `broker/molt.py`).
   - **The request.** `! molt <slot>` sends a grow request whose body is `molt <slot> cpu <cpuid.1.eax, 8 hex> pci <vvvv:dddd:rr>`.
     - The PCI triple is the slot's device. The `i8042` has no PCI function of its own, so its identity is **the LPC bridge at 00:1f.0**: the Q77 on the HP, ICH9 in the twin.
     - D4 reads the twin's values from a run.
   - **The frame.** The broker answers with a **part frame, kind `0x03`**: `u32 N`, kind, ABI 3, source, 0, `u32 L`, then the threshold (`u32` boots, `u32` keyboard bytes, `u32` mouse packets — decision 7), then the blob, header and body.
   - **The germline key** is `molt <slot>|abi3|<identity>` by PARTS.md's rule. The mock records it; ring 8b uses it.
   - **Checks at install.** The guest refuses a frame that is not kind 3, has a wrong ABI, a header that fails PARTS.md's checks, or a slot other than the one asked. It hashes the body and **refuses a frame whose header hash does not match** (`part refused: <why>`).
4. **The home store and the notebook, superseded in PARTS.md.**
   - **In the home store**, a part is stored under `part-<slot>`, by `home_install` unchanged (blob first, table sector last; the previous build kept). PARTS.md states, as the 7d section did for `! trial`, the sentences of HOME.md it supersedes:
     - a `part-` entry is **not an app**: it is not counted in `S7: home N apps`, not listed on the choices row, and `! part-<slot>` is refused with `part-<slot> is a part`.
   - **On the notebook**, PARTS.md states the sentence of NOTEBOOK.md it supersedes: a typed line beginning `molt ` is refused with `molt is reserved`, counted in `errors`, and journals nothing, beside ring 7d's `trial `.
   - The supersessions live in PARTS.md itself, frozen, so no append to a frozen document is needed this ring.
5. **The four words, the states, the notes and the lines** (PARTS.md). `bang_line` gains one compare before the `trial` check: a body beginning `molt` goes to `molt_word`, before the home lookup and before the broker.
   - **The four words:**
     - `! molt` draws the table in the app panel: each slot, its state, its build's first 16 hex, its shadow counts against its threshold, its probation count.
     - `! molt i8042` fetches a part.
     - `! molt take i8042` promotes it.
     - `! molt undo` steps the slot back one state.
   - **The states per slot:** `generic`, `shadow <sha16>`, `live <sha16>`, `demoted <sha16> <why>`.
     - A new build for a slot replaces its current build (home's previous build keeps the old one), and **the slot returns to the generic while the new build shadows** (deviation 11).
     - **Undo:** live → shadow of the same build; shadow → the previous build in the state it held before this one arrived (home's undo swaps the builds), or `generic` if none; demoted → shadow of the same build. A build the watchdog demoted can never become live by undo alone.
   - **The notes**, NOTEBOOK.md's format unchanged, all machine-written:

     | Note | When |
     |---|---|
     | `molt i8042 shadow <sha16>` | install |
     | `molt i8042 live <sha16>` | take |
     | `molt i8042 undo <state…>` | undo, naming the state it lands in |
     | `molt boot <n> i8042 <shadow\|live>` | before the handover, at every boot that loads a part; `<n>` is one more than the count of `molt boot` notes |
     | `molt healthy <n>` | the health mark |
     | `molt i8042 disagree <n> <k> <generic event> <part event>` | the first sixteen a boot |
     | `molt i8042 count <n> <keyboard bytes> <mouse packets> <disagreements>` | at the health mark and at each `! molt` word; the last in a boot is that boot's total |
     | `molt i8042 demoted <sha16> <watchdog\|unhealthy>` | a demotion |
     | `molt recovery owner` | an Esc recovery |
     | `molt recovery all` | a failure after every live part has passed probation |

   - **The refusals** are console lines, counted in `errors`, journaling nothing: `molt is reserved`, `part-i8042 is a part`, `unknown slot`, `no part to take`, `below threshold: boots b/B keys k/K mouse m/M` (always showing the counts), `disagreements <d>`, `another part is on probation`, `already live`, `nothing to undo`.
   - **The `S8:` serial lines.**
     - Before `S7: keyboard ready` they go through the tee. After it they go raw (the gotcha).
     - They are **printed only on a boot that finds a molt note on the notebook**, so a machine with no molt note prints none.

     | Line | Meaning |
     |---|---|
     | `S8: sha256 ok` | the known answer for `abc` passed |
     | `S8: part i8042 shadow <sha16>` / `S8: part i8042 live <sha16>` | the part loaded |
     | `S8: part i8042 bad hash` / `S8: part i8042 bad header` | refused at the door |
     | `S8: recovery i8042 watchdog` / `S8: recovery i8042 unhealthy` / `S8: recovery owner` / `S8: recovery all` | a recovery boot |
     | `S8: watchdog tco 30 s` / `S8: watchdog tco locked` / `S8: watchdog none` | the watchdog |
     | `S8: healthy <n>` | the health mark |

     A failed known answer prints `ERR: sha256 known answer`, and the boot loads no part.

     **One line per event in the twin (A5).** PARTS.md lists every line the guest can print. Before item 13, PARTS.md and the frozen checker name exactly one expected line for each twin event, taken from D1's run: which watchdog line an armed twin prints, and which recovery line follows a hang. No frozen expectation offers two lines. The alternatives stay only in `stage8/HP-8a.md`, which is not a criterion.
   - **A live part's init** writes its own lines through the service, prefixed `part: ` (for `good`: `part: i8042 self-test ok`, `part: i8042 mouse reset ok`) in place of the generic's `i8042:` pair.
6. **Shadow and the comparison for `i8042`** (PARTS.md).
   - **Events.** An event is `key <code>` or `mouse <dx> <dy> <buttons>`.
     - The generic's events are observed where they leave it: `kbd_next`'s key, and `mouse_byte`'s completed packet.
     - The part's are observed at its upcalls.
     - The two sequences are compared in order, event by event, in the main loop; stamps are not compared.
   - **A disagreement** is a position where they differ, or an event one side has and the other lacks when the other catches up by a PARTS.md bound (one packet or key).
   - **Counts per boot:** keyboard bytes and mouse packets fed to the part, and disagreements. The first sixteen disagreements are notes; a count note is written as decision 5 says.
   - **The threshold** is carried in the part's frame (decision 7).
   - **`! molt take`** checks the sums over the build's shadow boots (the last `count` note of each boot, plus the current boot's counts, journaled first) against the threshold.
     - Boots count only if they loaded the build in shadow.
     - Disagreements must total 0.
7. **The threshold and probation** (PARTS.md).
   - **Where it comes from.** The threshold is pre-registered in a part's plan from ring 8b on, and carried in the frame by the broker. The guest enforces PARTS.md's floor (boots ≥ 1) and demands 0 disagreements always.
   - **The fixtures' thresholds** are pre-registered in PARTS.md's fixture table (deviation 2):

     | Fixture | Boots | Keyboard bytes | Mouse packets |
     |---|---|---|---|
     | `good` | 3 | 1,000 | 5,000 (decision 8's numbers, which the gate and test 5 therefore exercise in full) |
     | `wrong`, `hang`, `fault`, `liar` | 1 | 100 | 100 |

   - **Probation** is 3 healthy boots live.
   - **One part on probation at a time,** and no part of *another* slot enters shadow while one is on probation (`another part is on probation`). A new build for the same slot ends its predecessor's probation (decision 5).
8. **The watchdog, the pet, the health mark and the recovery rules** (loader; PARTS.md states the rules).
   - **The timer.** The loader finds the LPC bridge (00:1f.0) and reads PMBASE (config `0x40`) and RCBA (`0xF0`). It maps the RCBA page uncached with `map_mmio_2m` and reads GCS at `RCBA+0x3410`.
     - It clears `NO_REBOOT`; if the bit will not clear: `S8: watchdog tco locked`, the finding, and decision 5's fallback.
     - It clears `TCO_EN` in `SMI_EN` (`PMBASE+0x30`) so the first expiry is not routed to SMM, and records whether it stuck.
     - It writes `TCO_TMR` for a 30 s deadline **by the Intel 7-series PCH datasheet's rule (A2)**: the tick length, the timer's width, and the reset on the *second* expiry. PARTS.md states the rule and the value it gives. The HP writes the same register on real silicon, so the value comes from the silicon's document, not from QEMU's model. D1 checks that the twin agrees. **If the twin disagrees, item 2 stops and the question goes to the owner.**
     - It clears the status bits, reloads, and clears `TCO_TMR_HLT`.
     - **It arms just before the first part runs**: at the handover, which is where `mouse_init` runs today, and at no boot that loads no part.
     - If D1 shows the ICH9 TCO cannot reset the twin, the twin uses `i6300esb` (decision 5's fallback) through the same pet interface, and the HP's TCO is proven on the metal alone (deviation 13).
   - **The pet** (a loader routine) reloads the timer only when all of these hold since the last pet:
     - the BSP heartbeat has moved;
     - `OBS_FRAMES` has moved;
     - no exception has been taken (a flag the exception handler sets);
     - every live part's `health()` returned 0;
     - the seed's outside check agrees: for `i8042`, the status byte reads neither `0xFF` nor with bit 6 or 7 set, and no ring has overflowed.

     The pet rate-limits itself by the TSC.
   - **The heartbeat and the pet's call sites (A1).** The heartbeat moves at every main loop turn and at every breath of a bounded wait (the wire's TCP poll, the disk's command wait). **The pet routine is called at every one of those points too**, with the same five conditions: at every main loop turn and at every breath of a bounded wait. A long broker wait therefore keeps petting (ring 8b's real grows wait about 70 s against the 30 s deadline), while a part hung in the main loop stops both (deviation 9).
   - **Two waits longer than the deadline must pass with no reset (A1):**
     - a broker request held by the mock for **`HOLD_S`**, PARTS.md's rule: twice the deadline;
     - the health-mark wait on a live boot, idle for 60 s against the 30 s deadline.

     Test 3 proves both.
   - **With a part loaded, the main loop polls instead of `hlt`,** as it does with an app running. There is no timer interrupt; the spec rules one out.
   - **The health mark:** 60 s after `S7: keyboard ready` on a boot that loaded a part, the note `molt healthy <n>`, a count note, and `S8: healthy <n>`.
   - **The recovery rules** are the spec's table, applied by the loader at boot from the notebook and the chipset's surviving status bit:
     - **The evidence bit** is TCO2_STS's `SECOND_TO_STS`, read, recorded and cleared by writing 1. D1 measures whether QEMU keeps it across the reset.
     - **The unhealthy count** is consecutive `molt boot` notes with no `molt healthy` note.
     - **Demotion** applies to the part in shadow or on probation — the only part whose code ran unproven (deviation 1).
     - **Twin and HP may differ (A4, A5).** If QEMU clears the bit, a hang in the twin is found by the two-unhealthy-boots rule instead: the part is still live on the boot after the first reset, the human types past its 100th byte again, and after the second reset comes `S8: recovery i8042 unhealthy`. **Test 3 expects exactly the one path D1 measured in the twin**, fixed before item 13. The HP may take either path, since its firmware may clear the bit during POST. `HP-8a.md` covers both, and whether the HP kept the bit is recorded as a finding of the ring.
   - **Esc at power-on (A3).** Only on a boot that finds a part to load, after the console is up and before the handover:
     - **the loader's own minimal setup first.** Before the window, the loader enables port 1 (`0xAE`) and drains the output buffer. It does not depend on the state the firmware left port 1 and translation in, which the twin cannot show (ring 7c item 15's class);
     - the loader draws `hold Esc for the seed` on the console and polls ports `0x64`/`0x60` for a window of **W = 3 s**. W is a human's window, pre-registered in PARTS.md; the owner may change it at approval. D4's hold measurement sets only the checker's hold;
     - bytes with status bit 5 set are discarded;
     - Esc counts as **held** if an Esc make arrived in the window and no Esc break followed it before the window ended. The make is accepted in **both translated set 1 (`0x01`, break `0x81`) and untranslated set 2 (`0x76`, break `0xF0 0x76`)**, and PARTS.md states both. A real keyboard's typematic repeats and the monitor's `sendkey esc <hold>` both satisfy this;
     - other bytes read in the window are dropped (the boot's typing starts after `ready`).
9. **The blame line and the read-only floor** (loader).
   - **The blame line.** With a part loaded, `exc_common` keeps its line and adds one before it halts: `ERR: exception <v> in part i8042 +<hex offset from the part's first byte>`, or `ERR: exception <v> in seed`. It writes nothing to disk; it sets the exception flag, so the pets stop.
   - **Read-only pages.** `build_paging` splits the 2 MB page holding the image into a 4 KB page table (one BSS page). The **whole `.text`** — `loader.asm`'s code and the constants it keeps inside `.text` (`sha_k`, `sha_init`, its strings) — is mapped read-only. **CR0.WP is set** on the BSP straight after the CR3 load and on every AP in the trampoline, so the protection holds from before the first part runs (deviation 10).
   - **The loader's mutable state** lives in one page-aligned, writable BSS block, `loader_state`, never passed to a part:
     - the pet state (last heartbeat, last frame count, the exception flag, the last pet's TSC);
     - the watchdog's I/O bases and verdict;
     - the recovery state (boot number, unhealthy run, per-slot state and build, evidence read);
     - the Esc window's result;
     - SHA-256's working state (`sha_state`, `sha_w`, `sha_tail`, `sha_digest`, with `home_undo` given its own scratch);
     - the serial line buffer the loader's raw writes use.
   - **Out of scope this ring:** the IDT, GDT and page tables stay writable, since the CPU writes a descriptor's accessed bit, and making them read-only is a later ring's. This is carried, said plainly in PARTS.md.
10. **What `stage8/loader.asm` holds** (decision 4's list, moved at item 14):
    - `efi_main` to the handover: GOP, the memory map, ExitBootServices, the GDT, `build_paging` with the 4 KB split, the IDT and `exc_common` with the blame line;
    - serial (`serial_init`, `serial_raw_puts`, the raw putters);
    - SHA-256 and its constants;
    - the disk *read* path: `ahci_find` … `ahci_rw`'s read side, `gpt_validate`/`gpt_read`, `record_valid`, the notebook scan and the home table read;
    - the door checks;
    - the recovery decision, the Esc window, the watchdog's arm and pet.

    The seed keeps the write paths (`notebook_append`, `home_install`, `gpt_write`), which call the loader's command routine, and every generic slot implementation. After item 16b only the owner's hand opens the loader.
11. **The five fixtures** (`stage8/fixtures/`, hand-written, frozen at item 13; PARTS.md's fixture table). Each has a banner stating its fate, as `stage6/liar.asm` does, and `Built with: nasm -f bin …`.
    - **`i8042-good`** is the seed's own i8042 code packaged as a part: the init with its two `part:` lines, the decoder (E0, shift, `scan1_map`, the quirks included — no E1, exactly the generic) and the packet assembly, with `health()` returning 0.
    - **`i8042-wrong`** is `good` with one scancode decoded as another: `q` (`0x10`) decoded as `w`.
    - **`i8042-hang`** is `good` whose `byte` entry spins forever on its **100th byte after its own `init`** (deviation 1).
    - **`i8042-fault`** is `good` that executes `ud2` on its **first mouse byte after its own `init`** (deviation 1).
    - **`i8042-liar`** is `good` with its name field `liar`. The gate installs it through the mock, then flips one byte of the stored body **on the disk image from the host** (a torn write, deviation 3). The offset and the resulting hashes are PARTS.md's worked example.

    **The offsets.** The `ud2`'s offset in `i8042-fault.bin`, which the blame line must name, is found by the checker in the fixture's bytes, never typed.
12. **SEED.md and the seed record** (deviation 8).
    - **SEED.md (frozen)** defines:
      - the seed: `stage8/out/BOOTX64.EFI` as `stage8/mkimage.sh` builds it from a commit, with NASM's version named (the stick image carries FAT timestamps and is not the seed);
      - how it is rebuilt and hashed;
      - the record's line format: `seed <n> <sha256> <bytes> <commit> <yyyy-mm-dd> nasm <version>`;
      - the rule that the witness uses the latest line;
      - SHA-256's known answer for `abc`;
      - a worked example.
    - **The record** is an unfrozen, append-only file beside it, **`stage8/seed-record.md`**, parsed by `parts.py` by SEED.md's rule; test 1 demands that it parses.
      - Its first line is **seed 0**: item 1's build of the byte-identical copy, whose hash is ring 7d's binary's. Rebuilding that commit's `stage8.asm` reproduces it, and that is SEED.md's worked example.
      - The line for the ring's seed is added at item 17, naming item 16b's commit (a commit cannot carry its own build's hash).
13. **`stage8/parts.py`** (item 7, frozen at item 13). Standard library only; it imports `metal`, `checkdisk` and the HOME.md parser for disks.
    - **Parsing** (the document's own tables and fences, failing loudly on any shape it does not know):
      - `parse_parts_md(text)` and `parse_seed_md(text)`;
      - `part_header(blob)`, `part_frame(blob, threshold)`, `parse_frame(bytes)`;
      - `molt_key(slot, identity)`;
      - `notes_molt(notes)`, `state_of(notes)` (the table `! molt` shows), `counts_of(notes, build)`, `recovery_of(notes, evidence)`;
      - `serial_of(line)`, `parse_seed_record(text)`, `liar_stored(bin)`, `ud2_offset(bin)`;
      - `sha256_kat()`, and `sha_k_rule()`: the 64 round constants from the cube roots of the first 64 primes.
    - **Modes:**
      - `--example`: both documents' worked examples reproduced byte for byte, exit 1 on a difference;
      - `--disk <img>`: DISK.md's table; the notebook's molt notes as the table; the home entry's build and hash;
      - `--serial <log>`: the HP's chart back into the table;
      - `--seed`: the record against the current build.

    Every constant is read from PARTS.md at import, so the document and the tool cannot drift.
14. **`broker/molt.py`** (item 8, **unfrozen**, deviation 5). It subclasses `wire.Wire`, and its `grow()` claims bodies beginning `molt ` (as `plans.Installer` claims `install `).
    - **`--mock --part good|wrong|hang|fault|liar`** (default `good`) answers `! molt i8042` with that fixture's frame: the committed `.bin`, the fixture table's threshold, source 0. It records the request, the identity and the key.
    - A slot other than `i8042` gets a refusal frame, and nothing is rehearsed: the pipeline is ring 8b's.
    - Everything else is `wire.Wire`'s, so `! test app` and the relay behave as at ring 7c.
    - **`--hold-s <s>` (A1)** holds the answer to one named question, `? hold`, for `s` seconds before sending it. It is unfrozen, so the checker never relies on it: test 3 measures the wait itself, from the guest's side (decision 16's `ask_held`).
    - **The criteria stay frozen** because the checker never trusts the mock: it rebuilds each expected frame by PARTS.md's rule from the frozen `.bin` and compares it with the mock's record, byte for byte.
15. **The harness** (items 9–11, frozen at item 13): 7d's shape. The machine is the 7c twin: `-machine q35 -cpu IvyBridge -m 256M`, OVMF, `VGA,edid=on,xres=1920,yres=1080`, the stick over `qemu-xhci` + `usb-storage`, the 64 MB SATA disk on `ide.1`, the e1000e with the HP's MAC on a cage to the relay on 9997, and the PS/2 mouse through the monitor. The argv is **`checkmetal.qemu_argv` itself**, with the stage8 paths (decision 17).
    - **The log.** The first thing `test-8a.sh` does is print `=== ring 8a gate <ISO-8601> commit <short hash> ===` into `stage8/out/gate-8a.log`, then `exec > >(tee -a "$LOG") 2>&1`.
      - `checkmolt.py` run directly writes its own header with the mode and the commit, and tees itself into the same log. Under the gate, `GATE_8A=1` in its environment stops it writing a second header.
      - The chat carries one `PASS`/`FAIL` line per test and the log's path.
    - **Refusals and builds.** The gate refuses to start if anything listens on 9999, 9998 or 9997, and runs `mkdir -p` on every `stage8/out/` directory it uses. It builds with `stage8/mkimage.sh` and `python3 stage8/mkstick.py`. Every boot runs under `timeout -k 5 <T>`, with exit 124 the expected outcome; each `T` is from item 12's run.
16. **The synthetic human** (`checkmolt.py`). It is ring 7d's `drive_7d` step loop, imported from `checktrials` and used with the stage8 bindings. It adds:
    - `("keys", text)`: `sendkey`s at `KEY_GAP`, with the keyboard bytes they make predicted by PARTS.md's rule — set 1 make and break, the shift pair, and four bytes for an E0 key — and checked against the guest's counts, so the count is a rule's output;
    - `("wiggle", n)`: `n` monitor `mouse_move`s, one packet each (ring 6c: packets counted equal packets sent);
    - `("hold_esc", ms)`: `sendkey esc <ms>` when `S8: sha256 ok` lands, just before the loader's window. The hold comes from D4's measurement and is the checker's own, separate from W (A3);
    - `("ask_held", s)` (A1): types `? hold` and Enter. It stamps the host time of the Enter, then polls the guest until the answer is in the conversation surface (read through the monitor), and stamps that too. The step fails if the elapsed time is under `HOLD_S`, if the serial capture shows OVMF's banner or a repeated `S7: alive` in between, or if the answer never lands. The wait is measured on the guest and the capture, so an unfrozen mock option cannot weaken it;
    - `("await", pattern, s)`: waits for a serial line within `s` seconds, such as the health mark, a reset's OVMF banner, or a recovery line;
    - `("flip", offset)`: the liar's host-side byte, done between boots.

    Typing notes and clicking the choices row reuse 7d's steps as they are.

---

## The acceptance tests

- **Test 1** (`test-8a.sh`, then `checkmolt.py --document`):
  - the PE32+ checks as 7d's shell does, on `stage8/out/BOOTX64.EFI`;
  - **the stick as 7c**: `checkmetal.check_stick(stage8/out/stick.img, stage8/out/BOOTX64.EFI)` with explicit arguments;
  - **PARTS.md and SEED.md parsed cold** by `parts.py`, and **their worked examples reproduced byte for byte**:
    - a part header;
    - a part frame for each fixture, and the key;
    - a molt-note sequence and the table it gives;
    - a recovery decision for each row of the spec's table;
    - the liar's stored bytes and both hashes;
    - the seed record's seed 0;
  - **the fixtures reassembled** into `stage8/out/*.check.bin`, byte-identical to the committed `.bin`s, each header valid by PARTS.md;
  - **SHA-256's known answer**: PARTS.md's `abc` digest equals `hashlib`'s, and the 64 round constants in the built EFI equal `sha_k_rule()`;
  - the seed record parses.

  Green at item 9.
- **Test 2** (`checkmolt.py --seven`): no part, no change. The seams, as D3 proves them, point the frozen checks at stage8's build:
  - `checkmetal.run_serial("blank", 8)`, `("again", 4)` and `("novga", 2)`;
  - `checkmetal.run_stages()`, with the mock's twin on `stage8/out/esp.img`;
  - `checktrials.run_row()` and `checktrials.run_sitting()`: a disk carrying ring 7d's notes, three sittings to `trial verdict B`, and the next boot in layout B.

  Each must return success. Then **no `S8:` and no `part:` line in any capture** under `stage8/out/seven/`. Scratch lives there, and the stick copies too. Green at item 9, and green at every commit after.
- **Test 3** (`checkmolt.py --fates`): the fates in the twin at `-smp 4`, with the synthetic human.
  - **Each disk** begins as a fresh 64 MB file booted once blank (19 lines), then gets **a ring-7d-like notebook written from the host** by NOTEBOOK.md's format (40 notes ending `trial verdict A`, like the HP's).
  - **Around every boot:**
    - the notes present before it must be unchanged byte for byte after it;
    - the stick copy's tables are unchanged (`check_stick_tables_unchanged` with the stage8 stick);
    - the mock and relay run only for boots that make a request; nothing listens otherwise (asserted).
  - **Disk G, `good`:**
    - **G1, the install.** `! molt` → the table `i8042 generic`; `molt x` typed → `molt is reserved`; `! molt i8042` → `part i8042 shadow <sha16>` and the note; `! part-i8042` → `part-i8042 is a part`; `! molt take i8042` → the below-threshold refusal with its counts; `S7: home 0 apps` held on the next boot. The mock's record is the frame by PARTS.md's rule, and the identity is D4's.
    - **G2–G4, shadow.** Each boot reads `S8: sha256 ok`, `S8: part i8042 shadow …` and the one watchdog line D1's run fixed (A5). Its `i8042:` pair is the generic's. It gets a third of the threshold's keyboard bytes (notes typed and journaled as typed — the generic did the work) and a third of its packets, then clicks on the choices row, then the health mark. Its count note equals the model's, with 0 disagreements.
    - **G4, the take.** `! molt take i8042` → accepted, `molt i8042 live`.
    - **G5, live.** `S8: part i8042 live`, the two `part:` lines, typing echoed and a click working through the part.
      - **A held request (A1).** With the mock and relay up and `--hold-s` at `HOLD_S` (PARTS.md's rule, twice the deadline), `ask_held`: the wait is at least `HOLD_S` on the guest's side, the answer arrives, and there is no reset.
      - **The idle wait (A1).** The machine is then left idle until the health mark: 60 s with no input against the 30 s deadline, and no OVMF banner in the capture.
      - `! molt undo` → `molt i8042 undo shadow …`; `! molt take i8042` → live again.
    - **G6, Esc.** Esc is held → `S8: recovery owner` with the generic's `i8042:` pair; typing and a click work; `molt recovery owner`; nothing is demoted. The disk is then copied from the host as **disk H**.
    - **G7.** Live again, then the health mark (probation 2).
  - **Disk W, `wrong`:** install; one shadow boot typing a note containing `q` → `molt i8042 disagree …`, the note journaled with `q` (the generic's), the counts met; `! molt take i8042` → `disagreements 1`, nothing promoted.
  - **Disk H, `hang` in good's place** (from G6):
    - `! molt i8042` with the mock on `--part hang` → shadow; the slot is generic.
    - One shadow boot to hang's threshold (hang is unarmed without its init, so there are 0 disagreements); take.
    - The live boot: the human types until the part's 100th byte (the rule counts it). The machine stops, and the checker waits for OVMF's banner in the same capture within **`RESET_S`**.
    - Then **exactly the one path D1 measured, fixed before item 13 (A4, A5)**. Either the next boot's `S8: recovery i8042 watchdog` and `molt i8042 demoted <sha16> watchdog`; or, if D1 found that QEMU clears `SECOND_TO_STS`, the next boot live again, the 100th byte typed again, a second reset within `RESET_S`, then `S8: recovery i8042 unhealthy` and `molt i8042 demoted <sha16> unhealthy`. The checker and PARTS.md carry only the path chosen.
    - The generic's pair; typing and a click work.
  - **Disk F, `fault`:** install, shadow, take. On the live boot, the first `wiggle` → `ERR: exception 6 in part i8042 +<ud2_offset(bin)>`, then the reset within `RESET_S`, then recovery and demotion by the same single path as disk H; typing and a click work.
  - **Disk L, `liar`:** install; the host flips PARTS.md's byte in the stored body. The next boot: `S8: sha256 ok`, `S8: part i8042 bad hash`, no watchdog line, the generic's pair, typing works, no `demoted` note.
  - **The recovery time.** Within the pre-registered time is: the reset's banner within `RESET_S` of the triggering input (PARTS.md's 30 s deadline plus D1's measured expiry granularity), and the recovery line within `RECOVER_S` of the banner (item 12's run).

  Green at item 16.
- **Test 4** (`test-8a.sh`'s self-checks, then `checkmolt.py --cage`, then the earlier gates):
  - **(a)** the harness's own strings, as 7d's: the cage to 9997, the machine, no `esp.img` on any QEMU line, the log and the scratch under `stage8/out/`;
  - **(b)** `check_argv_7c` on the checker's own command, which is `checkmetal.qemu_argv` with the stage8 paths. If D1 forces `i6300esb`, it is `check_argv_8a` instead: 7c's rules with exactly one `i6300esb` (deviation 13). Also `twin.DEFAULT_PORT == 9998` and `wire.RELAY_PORT == 9997`;
  - **(c)** the payload table as a subprocess, exit 0 and `0 wrong`, plus spot checks held as data. **Every ring 8a frozen path, `stage8/loader.asm` among them**, is denied to `Write`, `Edit`, `sed -i`, `>` and a heredoc, while running and reading them is allowed;
  - **(d)** `./stage7/test-7d.sh`, which runs 7d's tests 1–4 and inside its test 4 the 7c, 7b and 7a gates, each on ring 7d's own binary. Exit 0 is required, and the output goes to both logs.

  Red on (c) alone: from item 11 (before the freeze), and from item 13 to item 16 because `loader.asm` is not frozen yet. Green at item 16b (A6).

## What only a run can give, and what a rule fixes

**By rule (PARTS.md's and SEED.md's, computed by `parts.py`, never typed):**
- the frames, the keys and the header checks;
- every note's text but the counts;
- the table `! molt` shows;
- the keyboard bytes a typed text makes, and the packets a wiggle makes;
- the thresholds;
- the 100th-byte point;
- `ud2_offset`, the liar's stored bytes and hashes;
- the recovery decision for each case;
- the known answer and the round constants;
- the seed record's format;
- the 30 s deadline, the 60 s health window, W = 3 s (A3);
- `TCO_TMR` for 30 s, by the PCH datasheet's rule (A2);
- `HOLD_S`, twice the deadline (A1).

**From a run, never from arithmetic:**
- **D1:** whether the twin agrees with the datasheet's `TCO_TMR` (if it does not, item 2 stops, A2); the expiry granularity; the reset's latency (`RESET_S`); whether `SECOND_TO_STS` survives, which fixes the one recovery path test 3 expects (A4, A5); `noreboot`'s effect; the watchdog chosen, and so the one watchdog line (A5).
- **D2:** `-icount`'s repeatability.
- **D4:** the twin's CPUID and LPC identity; the hold time `sendkey` honours; the key and packet rates.
- **Item 12:** each boot's `timeout`; the ready and health waits; `RECOVER_S`; the whole fates run's time.

Each is a named constant in `checkmolt.py` with its date, quoted in `HANDOVER.md`'s environment table.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are green at its commit and which are red by design**:
  - items 0–8 have no ring 8a test;
  - item 9 commits tests 1 and 2 green;
  - items 10–15 keep test 3 red by design and test 4 red on (c) by design;
  - **item 16 turns test 3 green**, with test 4 still red on (c)'s loader clause alone (A6);
  - **item 16b turns test 4 green**: the whole gate;
  - from item 16b all four must be green before the commit.
- **The earlier gates** (the kickoff's I) run **once per commit where the gate is expected green**, only inside test 4 (d): at items 16b and 17. At items 11, 13 and 16 they also run once inside test 4, which is red there only on (c): at item 11 because nothing is frozen yet, and at items 13 and 16 because `loader.asm` is not frozen yet. At item 11 this is how (d) is proven when it is written. Items 14 and 15 change only stage8's source, so their regression is test 2 on stage8's binary, run before each of those commits; the stage7 gates, whose binary they cannot touch, are not re-run there. The three ring 6 gates and Stages 0–5 run on their own binaries before the item 17 commit. Each needs 9999, 9998 and 9997 free; **never two gates at once**.
- Every gate run and every direct checker run appends to `stage8/out/gate-8a.log`. The chat carries the `PASS`/`FAIL` lines and the log's path.
- `HANDOVER.md` is updated at every item, with a final pass at item 17.
- A fault class corrected a second time earns a CLAUDE.md gotcha line.
- Probes are never committed and never undone with `git checkout --`: copy aside, restore from the copy. Every probe boots a private copy under `stage8/out/probe8a/`.
- **The scope guard** governs every item: two honest attempts at any obstacle, with a real diagnosis from the serial log, the obs page, a screendump or the notes on disk — not a re-run. Then stop, record the exact state in `HANDOVER.md`, commit that, and wait for Wajira. A frozen file that needs to change is never edited: the diff is written unapplied under `stage8/out/`, recorded, and the owner applies it.
- **Everything runs inside QEMU** with the caged network, TCG, the IvyBridge CPU, the VGA device at 1920x1080, the stick over `qemu-xhci`, the SATA disk on `ide.1`, and the PS/2 mouse through the monitor.
  - The only disks are raw files under `stage8/out/` (the gate's, test 2's and the probes') and `stage7/out/` (test 4's gates, their own).
  - The mock and the relay bind `127.0.0.1` only.
  - CC never spells a `/dev` path, never runs `dd`, never flashes anything.
  - **No real Claude call is made by this session**; test 5 is Wajira's, and uses the mock too.
- If the owner says the session budget is nearly spent: finish the current item, commit, record the exact state in `HANDOVER.md`, stop.

---

# Part 1 — the probes, the documents and the acceptance machinery, written before the code

## Item 0 — this plan committed; ring 8a opened in HANDOVER and CLAUDE.md

- Copy this file verbatim to `stage8/plan-8a.md`.
- **In `HANDOVER.md`**, update the "Where we are" rows:
  - **Stage**: 8, the molt; ring 8a, the floor, opened 25 September 2026; the spec approved with all fourteen decisions.
  - **Status**: no ring 8a test yet; every earlier gate green on its own binary, as ring 7d closed.
  - **Repo**: unchanged, `/home/indy/Work/germos`.
  - **Machine**: mlrig, Omarchy, kernel 7.2.5-3-omarchy.
  - **Toolchain**: NASM 3.02, QEMU 11.1.1, Python 3.14.7, OVMF, mtools, OpenBSD netcat, xxd, the `claude` CLI 2.1.282.
  - **Model**: **Opus 5.5 at high effort**, spec decision 11.
- **Record the eighth freeze opening:** the TRIALS.md label-width sentence, by the owner's hand, 25 September 2026, commit `076d74b`, with 7d's test 1 green once after it (`stage8/out/trials-sentence-test1.log`). This closes ring 7d's carried item (1).
- **"Next action"** becomes: ring 8a opened; the plan at the gate; item 1 next.
- **A "Ring 8a — the floor" section** in ring 7d's shape: the shape from this plan, an empty test table (tests 1–5), and the items carried from ring 7d:
  - (2) the GPS history, postponed by the owner;
  - (3) zoom-to-fit, done here;
  - (4) Stage 7's caveats;
  - (5) the HP's disk and stick as the trial left them.
- **In `CLAUDE.md`'s windowed block**, add `-display gtk,zoom-to-fit=on` to the windowed QEMU line (spec, carried item 3), with the Edit tool. Headless gates are unaffected.
- One commit: the plan, `HANDOVER.md` and `CLAUDE.md` together.

*Expected at commit:* no ring 8a test exists. Every earlier gate unchanged.

## Item 1 — Stage 8 opened on ring 7d's source; D3, the seams, found by a run

- **Before anything else writes there,** run `mkdir -p stage8/out` (the fresh-clone gotcha; the gate will make its own directories).
- **Copy the source and builders:**
  - `stage7/stage7.asm` → `stage8/stage8.asm`, **byte for byte**;
  - `stage8/mkimage.sh` and `stage8/mkstick.py`: 7c's builders with only the paths changed to `stage8/`, including the font's `incbin` path, which stays `stage2/font8x8.bin`.
- **The build is ring 7d's.** Build, then compare: `stage8/out/BOOTX64.EFI` must equal `stage7/out/BOOTX64.EFI` byte for byte, after a fresh `stage7/mkimage.sh`.
- **D3, the seams, by a run.** A private driver, `stage8/out/probe8a/seams.py`, is never committed. It:
  - imports `checkmetal` and `checktrials`;
  - rebinds `STICK`, `EFI`, `ESP`, `OUT`, `METAL_OUT`, `DISK`, `GERMLINE`, `REHEARSAL`, `TWIN_WORKDIR`, `checktrials.STICK`, `TRIALS_OUT` and `DISK` to `stage8/out/seven/…`, and the two bound defaults;
  - runs `run_stick`, `run_serial` (blank 8, again 4, novga 2), `run_stages`, `run_row` and `run_sitting` on the stage8 build.

  It records:
  - which rebindings each needed;
  - whether any frozen path escaped the rebinding (a file written under `stage7/out/`, found by listing its mtimes before and after);
  - how each `run_*` reports failure: return value, `sys.exit` or exception;
  - the whole run's time.

  **Two honest attempts** if a seam will not hold. If none holds, stop: the fallback (copying stage8's stick and EFI over `stage7/out/` for the run and rebuilding after) goes to the owner as a question, not taken silently.
- **HANDOVER:** the environment table gains D3's findings.
- **The seed record:** `stage8/seed-record.md`'s seed 0 is written at item 6, once SEED.md exists.

*Expected at commit:* `stage8/stage8.asm` byte-identical to `stage7.asm`; the two builders; `HANDOVER.md`. No ring 8a test exists.

## Item 2 — D1, the watchdog, measured

A private copy, `stage8/out/probe8a/tco/stage8.asm`, gains a probe hook after `S7: keyboard ready` that prints raw lines. It is built there by a copy of the builder pointed at that directory, and booted from its own stick copy and disk. It measures:
1. the LPC bridge's IDs, PMBASE, RCBA, GCS and its `NO_REBOOT` bit as OVMF leaves them;
2. whether `NO_REBOOT` clears, and `-global ICH9-LPC.noreboot=on`'s effect on that;
3. `enable_tco`'s default, and `TCO1_CNT`/`TCO_TMR` at rest;
4. with `TCO_TMR` set to *n*, the host time from the arming line to OVMF's first bytes of the next boot in the same capture, for several *n*, **the datasheet's value for 30 s among them (A2)**. This gives the twin's two-expiry mapping and the granularity. **Does the twin agree with the Intel 7-series PCH datasheet's rule** (the tick length, reset on the second expiry)? If it does not, item 2 stops here and the disagreement goes to the owner as a question. The value is never re-derived from QEMU's model;
5. whether QEMU stays running across the reset: the next boot in one process, one capture, and the monitor still answering;
6. **`TCO2_STS` and `TCO1_STS` read at the next boot's earliest point after a watchdog reset, against a cold boot and against a monitor `system_reset`**: does `SECOND_TO_STS` survive?;
7. whether an `SMI_EN.TCO_EN` write sticks under OVMF;
8. the pet: a probe that reloads every second for 90 s and is **not** reset;
9. **the no-evidence path (A4):** with `SECOND_TO_STS` cleared by hand at the next boot's start, the boot counts as unhealthy with no evidence, as the loader's rules will see it. This confirms that the twin can walk that path if item 6 says the bit does not survive.

**If the ICH9 TCO cannot reset the twin**, measure `i6300esb` the same way, with its reload register, its reset, `-action watchdog=reset` and its status after a reset. **Say which one the plan uses, from the run.**

The table goes to `HANDOVER.md`'s environment, with the numbers and **the single choices (A5)** that PARTS.md and the checker will carry:
- the datasheet's `TCO_TMR` and the twin's agreement;
- `RESET_S`'s terms;
- the watchdog chosen, and so **the one watchdog line**;
- whether the evidence bit survives, and so **the one recovery path** test 3 expects.

*Expected at commit:* `HANDOVER.md` only.

## Item 3 — D2, `-icount`; D4, the argv, the Esc hold, the rates, the identity; the hook's verdicts

1. **D2 — `-icount` under QEMU 11.1.1.** A private bench copy runs the generic decoder over a fixed byte stream (a few thousand bytes: keys, E0 pairs, packets) N times after `ready`. Around each byte it reads `rdtsc`, and it prints the per-byte deltas' median, worst and sum.
   - Runs: three repeats each at `-icount shift=0,sleep=off`, `shift=0,align=off,sleep=off` and `shift=auto`, at `-smp 2` and `-smp 4`.
   - It also runs a straight-line loop of a known instruction count, to see whether `rdtsc` advances by exactly count × 2^shift.
   - It records which mode repeats exactly, whether `-smp` changes the numbers, and the wall-time cost.
   - The measures are ring 8b's; they are recorded now, as the spec requires, before any freeze.
2. **D4 — the argv.** Every flag or device D1 chose, run through the frozen `check_argv_7c` as data: pass or fail, and why.
3. **D4 — Esc at power-on through the monitor.** A private copy prints each raw byte its loader-window poll sees, with its TSC ms. Measured:
   - `sendkey esc <hold>` for holds of 100, 1000, 3000 and 10000 ms, sent when a marker line lands: the make at t0, the break at t0 + hold, and no typematic repeats;
   - the same key sent **before ExitBootServices** (is the make eaten by OVMF?);
   - the drift between the marker line reaching the capture and the make reaching the guest;
   - **the loader's minimal setup (A3)** in the copy, enabling port 1 and draining before the window: the Esc make still arrives in set 1 (`0x01`) in the twin.

   These set **only the checker's hold time** (A3). W is PARTS.md's human window, 3 s, pre-registered and not measured.
4. **D4 — rates.**
   - Keys: `sendkey` at `rehearse.KEY_GAP` → keyboard bytes per second, and the count against the rule's prediction for a mixed text (shift, E0 keys).
   - Mouse: `mouse_move` in a tight monitor loop → packets per second, with `OBS_PACKETS` equal to the moves sent, and the i8042 queue never overflowing (`OBS_RESYNCS` 0).

   These size the time to good's threshold.
5. **D4 — the identity.** CPUID leaf 1 EAX under `-cpu IvyBridge`, and the LPC bridge's vendor, device and revision in the twin.
6. **The hook's verdicts** on every command shape this ring will run: the new paths with `Write`; `python3 stage8/parts.py …`; `./stage8/test-8a.sh`; the checker's modes; `nasm -f bin stage8/fixtures/i8042-good.asm -o …`; `cp` of a disk under `stage8/out/`; `rm -rf stage8/out/molt stage8/out/probe8a`. They are fed through a scratch payload script written with the Write tool.

*Expected at commit:* `HANDOVER.md` only.

## Item 4 — `stage8/PARTS.md`

Decisions 2–9 and 11 in one text, in the manner of GLASS.md and TRIALS.md:
- its readers and the sentences it supersedes (HOME.md's app count, choices row and `! <name>`; NOTEBOOK.md's "any typed line is a note");
- the words; the slot table; ABI 3's header, entries, service table and upcalls, with the part never in interrupt context;
- the part frame and the request, with the identity rule;
- the key; the checks at install and at the door; the home names;
- the states and undo; the four words and their refusals; the notes; the `S8:` lines;
- shadow's events and the disagreement rule; the counts; the threshold and its floor; probation and its rules;
- the watchdog: the TCO's registers; **`TCO_TMR` for 30 s by the Intel 7-series PCH datasheet's rule** (the tick length, the timer's width, reset on the second expiry), with the value it gives and D1's confirmation that the twin agrees (A2); the arming point; the pet's five conditions; **the pet called at every main loop turn and at every breath of a bounded wait (A1)**; the polling loop;
- **`HOLD_S`, twice the deadline**: the rule for test 3's held request (A1);
- the health mark;
- **the recovery table** with each row's line and note, the evidence bit as D1 found it, and **the one path the twin takes, named alone as the twin's expectation (A4, A5)**;
- Esc: the loader's minimal setup (enable port 1, drain); **W = 3 s**, the owner's to change at approval; the "held" rule in both set 1 (`0x01`/`0x81`) and set 2 (`0x76`/`0xF0 0x76`); the cue line (A3);
- **one expected line per twin event (A5)**: the watchdog line and the recovery line fixed from D1's run. The alternatives the HP may show are named as the HP's, never as the twin's expectation;
- the blame line; the read-only pages and what stays writable;
- the fixture table (fate, threshold, trigger, banner);
- **"The corpus"**, a heading reserved for ring 8b (decision 7 of the spec puts the corpus in PARTS.md; ring 8b's spec freezes it at 8b's freeze, before the first grow, so ring 8a writes the heading and the rule that it arrives by a freeze opening at 8b's gate — deviation 7);
- worked examples, completed at item 7;
- "Parsing it cold, in Python", the functions `parts.py` will hold, verbatim.

Written with the Write tool.

*Expected at commit:* no ring 8a test yet.

## Item 5 — the five fixtures

`stage8/fixtures/i8042-{good,wrong,hang,fault,liar}.asm`, per decision 11, and each `.bin` assembled with `nasm -f bin`. `.gitignore` gains the five `!stage8/fixtures/i8042-*.bin` lines. `good` is transcribed from `stage7.asm`'s i8042 code (2002–2518, 1802–1868 and the scancode maps), made position-independent, with its state inside the blob. The four others are `good` with their one change, each marked in the banner.

**Proven on the host, no boot:** each assembles byte for byte twice; each header parses by PARTS.md's Python.

*Expected at commit:* no ring 8a test yet.

## Item 6 — `stage8/SEED.md` and the seed record

Decision 12. SEED.md, written with the Write tool, holds:
- the seed's definition;
- the rebuild recipe: `stage8/mkimage.sh` at a commit, NASM 3.02 named;
- the record's line format and rules: append-only, one line per seed version, the latest the witness's;
- SHA-256's known answer;
- the worked example.

`stage8/seed-record.md` holds seed 0: item 1's commit, whose build is byte-identical to ring 7d's 45,056-byte binary. Its hash is taken from the build, never typed.

*Expected at commit:* no ring 8a test yet.

## Item 7 — `stage8/parts.py`; PARTS.md's and SEED.md's worked examples completed

Decision 13 in code. PARTS.md's worked examples filled from the committed fixtures by the tool and cross-checked by hand against the rules:
- a header;
- the five frames' first bytes and hashes;
- a molt-note sequence and its table;
- the recovery cases;
- the liar's flip.

**Proven, no boot:**
- `--example` reproduces every example;
- a PARTS.md with one frame byte altered is refused;
- `--disk` on a formatted 7c disk prints `i8042 generic`;
- `--serial` on a scratch log prints the same table as `--disk` on the notes the same lines make;
- `--seed` names seed 0.

*Expected at commit:* no ring 8a test yet.

## Item 8 — `broker/molt.py`

Decision 14. **Proven, no boot:**
- a scratch client sends each grow body through a running `molt.py --mock --part <f>` on 127.0.0.1:9999, and each answer equals `parts.part_frame(fixture, threshold)`;
- `molt x86 …` gets a refusal frame;
- `! test app`'s body gets `wire.Wire`'s answer;
- the record carries the identity and the key.

*Expected at commit:* no ring 8a test yet.

## Item 9 — `stage8/test-8a.sh` with the log, test 1 and test 2; `checkmolt.py --document` and `--seven`

Decision 15's harness: the header and `tee`, the port refusal, the `mkdir -p`s, the build, the strings. **Test 1** (decision 15). **Test 2**: the seams as D3 found them, then the absence of `S8:` and `part:` lines.

*Expected at commit:* **tests 1 and 2 green**. Test 2 is green because the binary is still ring 7d's (item 1): a "no change" test is honestly green before any change (deviation 15). Quoted from the log.

## Item 10 — `checkmolt.py --fates` (test 3), the synthetic human

Decision 16's steps and the five disks' runs, judged through `parts.py` and the frozen seams. The run constants are named placeholders **marked to be written at item 12** (`RESET_S`, `RECOVER_S`, the timeouts, the waits); the checker refuses to run while any is unset. `test-8a.sh` gains test 3.

*Expected at commit:* tests 1–2 green; **test 3 red**: the checker stops on its unset constants, naming them. Quoted from the log.

## Item 11 — `checkmolt.py --cage` and test 4

The harness's strings, the argv check, the payload table with the spot checks as data, and `./stage7/test-7d.sh`. `test-8a.sh` gains test 4.

*Expected at commit:* tests 1–2 green; test 3 red; **test 4 red on (c) alone**: nothing of ring 8a is in `PROTECTED` yet, while (a), (b) and (d) pass. (d) is the earlier gates' one run at this commit.

## Item 12 — the probe: the implementation drafted privately; test 3's numbers read from a run

This is the ring 7d method, deviation 12 there, 14 here.
- **The draft.** Decisions 2–10 are drafted in full on `stage8/out/probe8a/draft/stage8.asm` (and its `loader.asm`), and built there. Its stick is copied over `stage8/out/stick.img` (scratch, rebuilt by every gate).
- **The run.** `checkmolt.py --fates` runs against it with the unset constants given on the command line for this run only.
- **What the run gives.** From the log: each boot's `timeout`, the ready and health waits, `RESET_S` and `RECOVER_S` (with the D1 terms), the held request's measured wait against `HOLD_S` (A1), and the fates' wall time. The run also confirms that the twin walks **the one recovery path** D1 chose (A4, A5). They are written into `checkmolt.py` as named constants, each with the run's date; the numbers go into `HANDOVER.md`'s environment table.
- **The rules the gate cannot reach, probed and quoted in `HANDOVER.md`:**
  - `S8: watchdog tco locked`: `noreboot=on`, if D1 showed that it locks;
  - the known-answer failure (one constant altered in a copy → `ERR: sha256 known answer`, no part loaded);
  - `another part is on probation` (a second slot stubbed in the copy);
  - `molt recovery all` (good past probation, then a forced hang);
  - **a part's stray write into `.text`** → `ERR: exception 14 in part i8042 +…` and the reset (a copy of `good` that writes one byte there).
- **Cleanup.** The probe is removed from the checker's path: `stage8/out/stick.img` is rebuilt from the repository's source. **Nothing of the draft is committed.** Two honest attempts; the scope guard.

*Expected at commit:* tests 1–2 green; tests 3–4 red on the repository's binary. The constants are set, so test 3 now fails on the first missing `S8:` line, not on a placeholder. `git diff --stat` shows `stage8/checkmolt.py` and `HANDOVER.md` only.

## Item 13 — freeze the ring 8a acceptance machinery

- **`PROTECTED` grows fifteen paths:** `stage8/PARTS.md`, `stage8/SEED.md`, `stage8/parts.py`, `stage8/test-8a.sh`, `stage8/checkmolt.py`, and the ten fixture files. The hook's comment says why each is a criterion or a criterion's parser.
- **`payloads.py` gains `FROZEN_8A`** in `FROZEN_7D`'s manner:
  - `freeze_cases` on the fifteen;
  - the denials of `write`, a heredoc and `sed -i`;
  - the allowances measured at item 3: running the gate, the checker's four modes, `parts.py`'s modes, the log redirection, `Write` on `stage8.asm`, `loader.asm` (until item 16b), the builders, `broker/molt.py`, the seed record, the plan and `HP-8a.md`, the scratch wipe, `git add` of the paths, the ring's words in prose.
- **Before the freeze, the one-expectation check (A5).** A grep of `PARTS.md` and `checkmolt.py` finds no twin expectation that offers two lines: no "or", no second pattern for one event. The watchdog line and the recovery path are D1's alone.
- **The checks.** The table is re-run whole, 0 wrong; immediacy is shown live with one denied `Edit` on `PARTS.md`. Then `./stage8/test-8a.sh` whole, from the log.
- The commit message goes in by `-F`, from a file written with the Write tool.

*Expected at commit:* tests 1–2 green; test 3 red by design; **test 4 red on (c)'s loader clause alone**: the earlier gates are green inside it, the payload table 0 wrong. `git diff --stat 076d74b -- <every earlier PROTECTED path>` is empty.

---

*Everything above is written before any new guest code exists in the
repository. Everything below is the code.*

---

# Part 2 — the implementation

## Item 14 — the loader moved into `stage8/loader.asm`; the read-only floor

- **The move.** Decision 10's move, from the probe's draft: `stage8.asm` does `%include "stage8/loader.asm"` at `.text`'s start. Constants the loader uses move into `.text` beside it; `.data`'s other constants stay.
- **The state.** `loader_state` becomes one page-aligned BSS block, and `home_undo` gets its own scratch.
- **The paging.** The 4 KB split of the image's 2 MB page, `.text` read-only, CR0.WP on the BSP and in the trampoline.
- **No new behaviour:** no slot, no watchdog, no `S8:` line. The NASM positional-define gotcha governs the move: constants stay at the top of `stage8.asm`, and `loader.asm` is included below them.
- **Proven:**
  - a private copy with a deliberate write into `.text` from the main loop faults with `ERR: exception 14 at …` (the line unchanged, since no part is loaded);
  - then **test 2 green on this binary** (the 7c and 7d checks through the seams, no `S8:` line);
  - test 1 green.

*Expected at commit:* tests 1–2 green; test 3 red by design (no `! molt`); test 4 red on (c)'s loader clause. Test 2's run is this commit's regression; the stage7 gates' binary is untouched.

## Item 15 — the slot, ABI 3, the part frame, the home names, the notes, the words, shadow

- **The pieces:**
  - decisions 2–7: the slot table with the generic's pointers;
  - the ABI 3 service table and upcalls;
  - the raw ring, fed from the stubs only when a part is loaded;
  - the part region (1 MB + header, BSS);
  - the molt request with the identity, and the kind-3 frame's checks;
  - `home_install` under `part-i8042`, with the app count, the choices row and `! part-` superseded;
  - the `molt ` prefix refused;
  - the notes, and the four words with their refusals;
  - the door's checks at boot: the known answer, the hash, the header;
  - shadow's comparison and counts, the count notes and the table;
  - take with its threshold, undo, live through the part's `init` and upcalls, the `S8:` lines.
- **Not yet in:** the watchdog, the pet, the health mark, the recovery rules, Esc and the blame line.
- **Probed on a private copy first:** good to its threshold, taken and live at `-smp 2`, `4` and `8`, the notes read back by `parts.py --disk`. Then test 2 on this binary.

*Expected at commit:* tests 1–2 green; **test 3 red** at its first watchdog line (`S8: watchdog …` missing on G2), and on the hang, fault and Esc fates; test 4 red on (c)'s loader clause. Both are said in the commit message from the log.

## Item 16 — the watchdog, the pet, the health mark, the recovery rules, Esc, the blame line — TESTS 1–3 GREEN — then stop for Cowork's review of the loader

- **The pieces:** decision 8 and decision 9's blame line, from the probe:
  - the arming at the handover, with the watchdog D1 chose, and `TCO_TMR` by the datasheet's rule (A2);
  - the pet's five conditions; the heartbeat's breaths **with the pet called at each of them** (A1); the polling main loop while a part is loaded;
  - the health mark;
  - the evidence bit read and cleared;
  - the recovery table and demotion;
  - the Esc window: the loader's minimal setup, W = 3 s, both scancode sets, the cue (A3);
  - the blame line and the exception flag.
- **Probed on a private copy:** hang and fault at `-smp 2` and `8`; the held request and the idle health-mark wait with a part live (A1); and the rules item 12 probed, re-run on this code.
- **The gate:** `./stage8/test-8a.sh` whole: **tests 1–3 green**; test 4 red on (c)'s loader clause alone, with the payload table 0 wrong and the earlier gates green inside it.
- **Then the session stops (A6).** It says so, and names `stage8/loader.asm` for Cowork's review. A defect the review finds is fixed while the file is still open: a further commit before 16b, the gate re-run, never a freeze opening.

*Expected at commit:* tests 1–3 green; test 4 red on (c)'s loader clause alone, by design; the four stage7 gates green inside test 4.

## Item 16b — `loader.asm` frozen — TESTS 1–4 GREEN (A6)

After Cowork's review, and any fixes it asked for, are in:
- **`stage8/loader.asm` joins `PROTECTED`**, and `payloads.py` gains `FROZEN_8A_LOADER`: its 18 freeze cases, with the item 13 allowance for `loader.asm` becoming a denial;
- the payload table is re-run whole, 0 wrong, and immediacy is shown live with one denied `Edit` on `loader.asm`;
- then **`./stage8/test-8a.sh` whole: all four tests green**, with the earlier gates inside test 4;
- **the whole gate's wall time** goes into `CLAUDE.md`'s build block (7d's A4).

The gate cannot pass before the loader is frozen, because test 4 checks the freeze. So **this is the item where the ring's gate first passes on `loader.asm`**, and the freeze is in the same commit (the kickoff's F; A6). The commit message goes in by `-F`.

*Expected at commit:* **all four automated tests green**; the payload table 0 wrong; the four stage7 gates green inside test 4.

## Item 17 — HANDOVER, CLAUDE.md, README, the seed record, the owner's procedure

- **`HANDOVER.md`** to the green-pending-oracle state:
  - what was built;
  - the numbers: D1–D4, item 12's constants, the binary's size, the gate's time;
  - tests 1–4 green from the log, test 5 pending;
  - the findings;
  - the carried items: the IDT, GDT and page tables writable; the rules proven only by probe.
- **`stage8/seed-record.md`** gains the ring's seed, naming item 16b's commit and its build's hash (from the build).
- **`CLAUDE.md`'s build block** gains `./stage8/mkimage.sh`, `python3 stage8/mkstick.py`, `./stage8/test-8a.sh` with its time and boot count, `python3 stage8/parts.py …`, and `python3 broker/molt.py --mock --part <f>`. The gotchas gain only what was corrected twice; first-time candidates are recorded in HANDOVER.
- **`README.md`** gains Stage 8 and ring 8a.
- **`stage8/HP-8a.md`**, the owner's day (Test 5 below).
- **The checks before the commit:** the payload table, 0 wrong; the gate whole (its test 4 is the one run of the stage7 gates); the three ring 6 gates and Stages 0–5 on their own binaries.
- **Then stop.** The commands for the owner's day are printed.

*Green at commit:* all four automated tests, the four stage7 gates inside test 4, the three ring 6 gates, Stages 0–5.

## Test 5 — Wajira's, on the HP: `stage8/HP-8a.md`

`stage8/HP-8a.md` is written at item 17 in METAL.md's shape: the header ("the owner's document — not frozen, not a criterion"), steps 0–10, the debugging table, and "what the twin could not prove". Every windowed QEMU line in it carries `-display gtk,zoom-to-fit=on`. **No step asks the owner to stop and report in the middle of a measured run** (ring 7d's finding): each boot's work runs to the health mark first; he reads the chart and `! molt`'s table after. **No step needs timed coordination between the two machines**: the mock is changed only between boots, while the HP is powered off.

**Before the day**
0. **Once:** `./stage8/mkimage.sh && python3 stage8/mkstick.py`; the serial group (`uucp`), the cable, the PS/2 keyboard and mouse, the Ethernet, and the second address on mlrig, all as in METAL.md.
1. **The flash, by his hand**, of `stage8/out/stick.img` by METAL.md steps 1–3 as they stand: `lsblk`, the by-id path, unmount, `wipefs`, `dd`, `cmp` saying nothing, power-off. **One flash for the whole day.**
2. **Three terminals, by METAL.md step 5:**
   - `python3 broker/molt.py --mock --part good`;
   - the relay on the second address;
   - the chart to `stage8/out/hp-8a.log`.

**`good`, to the threshold and live**
3. **Boot 1.** The chart shows ring 7d's lines, `S7: notebook 277 notes`, and **no `S8:` line**. Type `! molt i8042` → `part i8042 shadow …`. Type `! molt` → the table. Power off.
4. **Boots 2, 3 and 4: shadow.** At each: type about 200 keys of notes and move the mouse for about a minute (the rates from D4 say how long), with some clicks. Then wait for `S8: healthy <n>` on the chart and read `! molt`'s counts. Power off. After boot 4 the counts meet 3 / 1,000 / 5,000 with 0 disagreements; `! molt take i8042` → `molt i8042 live`.
5. **Boot 5: live.** `S8: part i8042 live`, the two `part:` lines, typing and a click working. Wait for `S8: healthy`. Power off.

**Esc, then `hang`**
6. **Boot 6: Esc** (deviation 11; A3). Power on **without touching the keyboard**. Press and hold Esc **only when `hold Esc for the seed` appears on the screen, never at power-on**: Esc on an HP opens its own startup menu. The window is 3 s. Keep holding until the console says `recovery owner`. Expect `S8: recovery owner`, and the keyboard working (the seed's). Power off.
7. **The mock changes, with the HP off:** Ctrl-C the mock; `python3 broker/molt.py --mock --part hang`.
8. **Boot 7.** `S8: part i8042 live` again (Esc left nothing demoted). Type `! molt i8042` → `part i8042 shadow …` (hang, in good's place; the slot is back on the generic). Power off.
9. **Boot 8: hang in shadow.** Type a line and move the mouse briefly (hang's threshold is 1 / 100 / 100). Wait for `S8: healthy`; `! molt take i8042`. Power off.
10. **Boot 9: hang live.** Type. Within a few lines the HP stops answering. **Do nothing.** Within about 30 s it **resets itself**, and the chart shows the firmware's boot.
    - **If the next boot shows `S8: recovery i8042 watchdog`:** the HP kept the evidence bit. The keyboard works on the seed's driver, and `! molt` shows `demoted … watchdog`.
    - **If the chart shows no recovery line after the first reset (A4):** the HP's firmware cleared the bit, and `hang` is still live. **Type again** until the HP stops and resets a second time. Then expect `S8: recovery i8042 unhealthy`, the keyboard on the seed's driver, and `! molt` showing `demoted … unhealthy`.
    - **Whether the HP kept the bit is recorded as a finding of the ring (A4).**
    - **The HP's own deadline (A2).** Read it from the chart's stamps afterwards: from the last typed byte's echo to the first firmware line after the reset. It is recorded as the ring's measured deadline on the metal, against the twin's and the datasheet's.
    - **If the HP never resets** and the chart said `S8: watchdog tco locked`, that is **the ring's finding** (decision 5's fallback): the power button, and the record says so.
11. **Afterwards:** `python3 stage8/parts.py --serial stage8/out/hp-8a.log` prints the day's table from the chart. Photograph the panel's table. His word closes the ring.

---

## Verification

- **Automated:** `./stage8/test-8a.sh` from the repo root.
  - It refuses to start while 9999, 9998 or 9997 is held, and appends everything to `stage8/out/gate-8a.log` under a dated header with the commit.
  - It builds, then runs:
    - test 1: the artefact, the stick, the documents parsed cold, the examples, the fixtures, the known answer;
    - test 2: the 7c and 7d checks on stage8's build through the seams, and no `S8:` line;
    - test 3: the five fates on five disks;
    - test 4: the strings, the argv, the payload table, `./stage7/test-7d.sh` with 7c, 7b and 7a inside it.
  - Exit 0 only if all pass. It is run before every commit from item 16 on (whole from 16b); its time is recorded at item 16b in `CLAUDE.md`.
- **Regression:** test 2 before the items 14 and 15 commits; the stage7 gates inside test 4 at items 11, 13, 16, 16b and 17; the ring 6 gates and Stages 0–5 before the item 17 commit.
- **The hook:** `python3 .claude/hooks/payloads.py` at items 13, 16b and 17: every case, 0 wrong; immediacy shown live at 13 and 16b.
- **Cowork's review of `loader.asm`** between items 16 and 16b (A6).
- **The probes:** items 1, 2, 3 and 12 each quote their numbers in `HANDOVER.md` and the commit message; items 14–16 each quote their private-copy runs.
- **Manual (test 5):** Wajira, by `stage8/HP-8a.md`; his word closes the ring.

## Safety

- **Inside QEMU and loopback.** Everything CC runs is inside QEMU (TCG) or on the host's loopback.
- **The disks.** Every guest has exactly two drives of the harness's own: a copy of `stick.img` and a raw 64 MB disk, both under `stage8/out/` (test 4's gates under `stage7/out/`, their own). They are created by the harness or the probe.
- **The watchdog** resets only the QEMU guest it lives in. With `-action watchdog=reset` (QEMU's default), the process stays up and nothing on the host is touched.
- **The storage bodyguard** is untouched this ring: no new word, no new spelling. Every planned command is read against its rules at item 3, and the hook's own list only grows.
- **The metal.** CC never touches `/dev`, never runs `dd`, never flashes; the flash is the owner's hand by METAL.md.
- **The network** is a cage in every QEMU line, landing on `127.0.0.1`: the relay on 9997 for request boots, nothing for the rest. The mock binds `127.0.0.1` only.
- **No token.** This session makes no Claude call.
- **Earlier frozen files.** Every earlier frozen file is untouched: `git diff --stat 076d74b -- <every earlier PROTECTED path>` is empty at every commit. The only changes outside `stage8/` are `broker/molt.py` (new), the hook's list and payload table (grown), `.gitignore` (five lines), and `HANDOVER.md`, `CLAUDE.md` and `README.md`.
- **The HP's disk.** It is written only by the guest on the owner's day: molt notes after the 277, and a home entry. Test 3 proves earlier notes unchanged on every boot.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| A count or constant in the frozen checker is wrong (the three freeze openings' class) | every count is a rule's output through `parts.py`: bytes from the scancode rule, packets from moves, notes from the state rules, offsets from the fixture's bytes. The only literals from a run are named, dated and taken at item 12 before the freeze |
| QEMU's ICH9 TCO does not reset the twin, or does not keep `SECOND_TO_STS` | D1 measures both before PARTS.md is written: the `i6300esb` fallback with its own argv check, or the `unhealthy` path expected in the twin; one expectation, never two (A5) |
| QEMU's TCO model differs from the silicon's timing | `TCO_TMR` comes from the PCH datasheet's rule, not from the twin; D1 only confirms agreement and stops item 2 if it does not agree; the HP's own deadline is read from the chart at test 5 (A2) |
| The HP's firmware clears `SECOND_TO_STS` in POST, and `hang` survives the first reset | HP-8a.md step 10: type again to the second reset, expect `unhealthy`; whether the bit survived is a finding (A4) |
| The HP's firmware locks `NO_REBOOT` or eats the first expiry in SMM | the loader clears `SMI_EN.TCO_EN` and reports `tco locked`; test 5 records it as the ring's finding; decision 5's fallback |
| Esc held at power-on opens the HP's startup menu, or the firmware leaves port 1 or translation otherwise than the twin | the loader enables port 1 and drains before the window, and accepts set 1 and set 2 (A3); W is 3 s, a human's window; HP-8a.md says press Esc only when `hold Esc for the seed` appears, never at power-on |
| The pet starves on an idle BSP, or during a long broker wait | the polling main loop while a part is loaded; the pet called at every main loop turn and at every breath of a bounded wait (A1); test 3 holds a request for twice the deadline and idles 60 s on a live boot, with no reset allowed |
| The part's own code hangs the stub, or corrupts interrupt state | the part is never called in interrupt context; the stub only queues |
| A part corrupts the loader | `.text` read-only with CR0.WP on every core, proven by a probe; the loader's state never handed to a part; the IDT, GDT and page tables stay writable this ring, said plainly and carried |
| The no-part path drifts from ring 7d's | the IRQ path unchanged instruction for instruction with no part loaded; test 2 on stage8's build at items 9, 14, 15, 16, 16b and 17 |
| The frozen checkers' seams do not hold | D3 proves them on a byte-identical build at item 1, before any test depends on them; a seam that will not hold stops item 1 and goes to the owner |
| Good's threshold (5,000 packets) makes test 3 long | D4 measures the monitor's rate first; the time goes into `CLAUDE.md`; the threshold is the owner's number and is never lowered for the gate |
| `-icount` does not repeat under QEMU 11 | D2 records it before ring 8b's freeze; ring 8b's spec decides |
| `loader.asm` has a defect found after it freezes | Cowork reviews `loader.asm` between items 16 and 16b while it is still open, and fixes land before the freeze (A6); after 16b, the scope guard: the diff unapplied under `stage8/out/`, the owner's hand |
| A frozen file needs to change | the scope guard |
| The gate spends a token | the triple port refusal; only `molt.py --mock` and `wire.py --mock` behind it; the record's calls checked |

---

## Deviations from the spec and the kickoff, for approval

Each is argued from a measured fact or a frozen file. Everything else is
the spec as written.

1. **`hang` and `fault` trigger only after their own `init`.** `hang` spins on its 100th byte, and `fault` executes `ud2` on its first mouse byte, both counted from the part's own `init`. The spec's table makes both *live*, and the only road to live is `! molt take` after shadow, which the guest refuses below the threshold. A part in shadow is never `init`-ed (the spec: one controller). So a trigger counted from the part's `init` leaves both behaving as `good` in shadow; they can be taken, and they fail live, where the spec puts their fate. Demotion is said of "the part in shadow or on probation", since shadow runs the part's code too.
2. **The threshold travels in the part frame; the fixtures' thresholds are PARTS.md's.** The spec pre-registers the threshold in the part's plan, which lives on the host, so the guest needs it from somewhere; the frame is the one channel. `good` carries decision 8's full numbers, so the gate and the owner exercise them. The four failing fixtures carry 1 / 100 / 100, the least that proves the rule, so the owner's day and the gate stay a day and an hour. PARTS.md's floor (1 boot, 0 disagreements) binds every frame.
3. **`liar`'s changed byte is written by the host into the stored part, on the disk image, between boots.** The guest hashes what it receives at install, so a mock-served mismatch is refused at install, not at the door. The spec's fate ("skipped at the door; nothing demoted"; "a torn write is not a verdict") is a torn write, and on a file disk the host can make one exactly. On the HP, `liar` is not part of test 5 (the spec's test 5 has none).
4. **The supersessions of HOME.md and NOTEBOOK.md are stated in PARTS.md, not appended to them.** PARTS.md is frozen at the same freeze and names its readers, so the rule is as fixed as ring 7d's appended section, without a stop for the owner's hand.
5. **`broker/molt.py` is not frozen.** Ring 8b's real grow path lives in it, and the spec keeps "the broker's brief and the grow path" unfrozen. The criterion stays frozen because the checker rebuilds every expected frame from PARTS.md and the frozen `.bin`s and compares it with the mock's record, byte for byte.
6. **The molt request rides as a grow body `molt <slot> <identity>`,** as `install` does, because the frozen `germline.handle` drops any other marker. **The `i8042` slot's identity is the LPC bridge's**, as it has no PCI function of its own.
7. **The `i8042` corpus is not written in ring 8a.** Ring 8b's spec freezes "the plan, the corpus and the verdict rule" at 8b's freeze, before the first real grow. PARTS.md reserves the heading and states that the corpus enters by a planned freeze opening at 8b's gate, so it is written by the ring that uses it.
8. **SEED.md is frozen and the record is not.** SEED.md fixes the seed's definition, the rebuild, the line format and the rule. The record, `stage8/seed-record.md`, is append-only by that rule and checked by `parts.py` (test 1). A commit cannot carry its own build's hash, so each line names an earlier commit.
9. **The heartbeat moves at bounded waits' breaths as well as at main loop turns, and the main loop polls while a part is loaded.** Without a timer interrupt, which the spec rules out, an idle BSP sleeps in `hlt` and a broker wait holds the loop for up to minutes in ring 8b. Either would starve the pet and reset a healthy machine. A hung part still stops both, because it hangs the loop that breathes.
10. **The whole `.text` is read-only from `build_paging` on, on every core, not only the loader's pages after the handover.** `.text` is pure code (measured), so nothing legitimate writes it. Protecting it from before any part runs meets "after the handover" and more. The IDT, GDT and page tables stay writable this ring (the accessed-bit write; a later ring's), said in PARTS.md and carried.
11. **A new build for a slot sends the slot back to the generic while the build shadows, and ends its predecessor's probation. On the HP, Esc is tested on the boot after good's first live boot, before `hang`.** The spec's one-build-per-slot home entry cannot run two builds of one slot, and the probation rule is about blame between slots. After the watchdog demotes `hang` no part is loaded, so an Esc boot then would prove nothing; the live `good` is the strongest case of the owner's way back.
12. **Several disks in test 3, each seeded from the host with a ring-7d-like notebook.** The spec's "every note written before the run unchanged" is proven against notes like the HP's, and the fates keep their blame separate. Disk H starts from disk G's image, so `hang` arrives in good's place, as on the HP.
13. **The twin's watchdog and its recovery line are what D1 measures.** If the ICH9 TCO cannot reset the twin, `i6300esb` is used, the argv check is `check_argv_8a` (7c's rules plus exactly one `i6300esb`), and the HP's TCO is proven on the metal alone. If QEMU clears `SECOND_TO_STS` at reset, the twin shows the `unhealthy` path, and the `watchdog` row is proven by a probe and on the HP.
14. **The implementation is drafted on a private copy before the freeze** (item 12; ring 7d's deviation 12, accepted then). Every number in test 3 comes from a run, and the criteria freeze before the code enters the repository. Said plainly: the draft exists on disk before the freeze, in a gitignored directory, and the freeze protects the criteria from it.
15. **Test 2 is green when written.** It asserts "no part, no change", and the binary is ring 7d's until item 14, so it cannot be red honestly. It guards items 14–16.
16. **Some rules are proven by probes, not by the frozen gate.** These are `tco locked`, a failed known answer, `another part is on probation`, `molt recovery all` and a stray write into `.text`. The twin has one slot, a TCO that is not locked, and no way to break its own constants. Each is exercised on a private copy at items 12 and 16 and quoted in `HANDOVER.md`.
17. **Test 4's earlier gates are one call, `./stage7/test-7d.sh`,** which runs 7d's tests and, inside its test 4, the 7c, 7b and 7a gates on their own binary: all four, once per green commit.

---

## Amendments — Cowork's review, adopted before approval

Cowork reviewed the plan on 25 September 2026 and accepted all seventeen
deviations as argued. It asked for six amendments, A1–A5 required and A6
recommended; all six are adopted here and folded into the items they touch.
Where an amendment and the body disagree, **the amendment governs**.

**A1 (required) — the pet during long waits** (decisions 8, 14, 16; test 3's G5; items 4, 12, 16).
- **The call sites.** The pet routine is called at every breath point of a bounded wait (the wire's TCP poll, the disk's command wait) as well as at every main loop turn, with the same five conditions. A heartbeat that moves while nothing calls the pet would still let the timer expire, and ring 8b's real grows wait about 70 s against the 30 s deadline.
- **The test clause.** Test 3 gains one clause on a boot with a part live (G5): one broker request, `? hold`, is held by the mock for **`HOLD_S`**. `HOLD_S` is PARTS.md's rule, twice the deadline, never typed. The machine is not reset and the answer arrives.
- **How the wait is measured.** The checker measures the elapsed wait itself, from the Enter it sent to the answer in the guest's conversation surface. It demands no OVMF banner in the serial capture between them, so the unfrozen mock option (`molt.py --hold-s`) cannot weaken the criterion.
- **The idle wait.** The health-mark wait on a live boot is idle for 60 s, longer than the deadline, and must pass with no reset.

**A2 (required) — the TCO value on the HP** (decision 8; items 2, 4; HP-8a.md step 10).
- **The rule.** PARTS.md states `TCO_TMR` for 30 s by the Intel 7-series PCH datasheet's rule: the tick length, the timer's width, and the reset on the second expiry. The HP writes the same register on real silicon.
- **The twin's check.** D1 checks that the twin agrees. If it does not, item 2 stops and the question goes to the owner.
- **The metal's number.** HP-8a.md step 10 records the HP's own time, from the last typed byte to the first firmware line after the reset, read from the chart's stamps. That is the ring's measured deadline on the metal.

**A3 (required) — Esc on the HP** (decision 8; items 3, 4, 16; HP-8a.md step 6).
- **The setup.** Before the window, the loader does its own minimal setup: it enables port 1 (`0xAE`) and drains the buffer. So it does not depend on the state the HP's firmware leaves port 1 and translation in, which the twin cannot show (ring 7c item 15's class).
- **Both scancode sets.** The loader accepts the Esc make in translated set 1 (`0x01`, break `0x81`) and in untranslated set 2 (`0x76`, break `0xF0 0x76`). PARTS.md states this.
- **The window.** W is a human's window, **pre-registered in PARTS.md as 3 s**; the owner may change it at approval. D4's hold measurement sets only the checker's hold.
- **HP-8a.md step 6:** press and hold Esc only when `hold Esc for the seed` appears on the screen, never at power-on, because Esc on an HP opens its own startup menu.

**A4 (required) — when the HP gives no evidence** (decision 8; item 2's point 9; test 3's disk H; HP-8a.md step 10).
- **The gap.** If the HP's firmware clears `SECOND_TO_STS` during POST, the first reset brings back a boot with `hang` still live. An idle boot would then reach the health mark and pass `hang`'s probation boot.
- **HP-8a.md step 10:** if the chart shows no recovery line after the first reset, type again until the second reset, then expect `S8: recovery i8042 unhealthy`. Whether the HP kept the bit is recorded as a finding of the ring.
- **Test 3** expects exactly the path D1 measured in the twin.

**A5 (required) — no alternatives in a frozen expectation** (decision 5's lines; decision 8; test 3; items 2, 4, 12, 13).
- **One line per event.** Every place the plan offered a choice ("`S8: watchdog tco 30 s` or D1's line", "watchdog or unhealthy") is resolved to one expectation, taken from D1's run, before item 13. The frozen checker and PARTS.md carry exactly one expected line for each twin event.
- **Where the alternatives live.** They stay only in `stage8/HP-8a.md`, which is not a criterion.
- **The check.** Item 13 greps PARTS.md and `checkmolt.py` for any twin expectation offering two lines before the freeze.

**A6 (recommended) — Cowork's review of the loader before its freeze** (items 16, 16b; conventions; verification).
- **Item 16** commits with tests 1–3 green and test 4 red only on the loader clause. The session then stops and says so, for Cowork's review of `stage8/loader.asm`. Any defect the review finds is fixed while the file is still open, not by a freeze opening.
- **Item 16b** is the freeze: `PROTECTED`, `FROZEN_8A_LOADER`, the payload table 0 wrong, and the whole gate green. The whole gate cannot pass before the loader is frozen, because test 4 checks the freeze, so 16b is the item where the gate first passes on `loader.asm`, and the owner's rule (the kickoff's F) holds.
