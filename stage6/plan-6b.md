# Stage 6, ring 6b — the store of plans · implementation plan

**To be committed verbatim as `stage6/plan-6b.md`. Produced in plan mode, per
the foundation's build loop. Nothing below is implemented until Wajira
approves this document by writing the approval marker from his own terminal;
the ExitPlanMode hook holds the gate until then. Plan mode allows this
session to write only this one file and forbids commits, so — exactly as
ring 6a did — the copy to `stage6/plan-6b.md` and its commit are the first
act after the gate opens, item 0 below, before any other file is touched.
Cowork's amendments while the gate holds are adopted here as numbered
amendments (A1, A2, …) at the end of the document.**

## Context

Ring 6a is closed: on 2 September 2026 `! make me a clock` ticked in its
own panel while a note was typed beside it and the strip's numbers moved.
This is **ring 6b, the store of plans** — the thesis item of Stage 6 and of
the foundation's five load-bearing ideas: an application is distributed as
an architect's plan (intent in English plus acceptance tests), the binary is
grown on-site at install time, rehearsed in the twin **against the plan's
own tests**, kept on the machine, and launched after a reboot with the
broker gone. The done-when: **`! install calculator` from
`plans/calculator.md` gives a working calculator; reboot with no broker;
`! calculator` still runs it.**

What this ring builds, from `stage6/spec.md`: the plan file format in a
new frozen `stage6/PLANS.md` (name, Intent, Choices, Tests in the
five-verb language — `press`, `wait`, `expect`, `expect not`, `expect
changed`); the home image in a new frozen `stage6/HOME.md` (a header, a
table of apps with name, size, SHA-256, sectors and the previous build's
sectors for undo, then the blobs) on a second raw disk `stage6/out/home.img`
on a second virtio-blk device; the serial line `S6: home <N> apps`; the
`installed` flag in the kind `0x02` header meaning the guest writes the app
to the home image before running it; launch without the broker (`! echo`
runs an installed app from disk with nothing on the wire); `! undo install
<name>`; the choices row naming up to three installed apps at the prompt;
a new broker module that imports `glass.py` and `twin.py` without editing
them and rehearses each install through `twin.rehearse`'s post-delivery
hook; a refused install naming the failed test in the plan's own words;
the unfrozen backend gaining the plan brief; the fixtures `plans/echo.md`,
`plans/liar.md`, `plans/calculator.md`; and acceptance tests 1–4 written
red before any code and frozen. **The owner's decision at ring 6a's
oracle: windowed runs use 1920x1080** — so this ring's gate, twin and
oracle all run at 1920x1080 and the twin is the exact machine again, while
ring 6a's frozen gate stays at 1440x1440 and must still pass.

The kickoff's standing orders: the automated gate talks only to the mock,
spends no token and needs no internet; the real `claude -p` backend is
exercised only by the owner at test 5; **the cage, the storage bodyguard
and every frozen file stand** — `stage6/GLASS.md`, `broker/glass.py`,
`broker/twin.py`, `stage6/test.sh`, `stage6/checkglass.py`, the three 6a
fixtures and every earlier stage's files stay byte for byte, and
`./stage6/test.sh` plus Stages 0–5 must still pass at the end of the ring.
If a frozen file needs to change, the session stops at the scope guard,
writes the diff unapplied under `stage6/out/`, records it in `HANDOVER.md`
and says so. This ring is implemented on **Fable 5.1 at medium effort as
the owner's experiment**, to be compared with Opus at high (Stages 0 and
1) and Fable at high (Stages 2 to 6a); Cowork reviews to the same standard
as every ring — recorded in `HANDOVER.md` at item 0.

The plan is **evaluation-first**. Items 1–7 write the two documents, the
plans and their fixtures, the broker module and the acceptance machinery so
that tests 1–4 exist and fail before a single new instruction of
`stage6.asm` is written. Item 8 freezes them. Items 9–11 grow the guest
and the gate closes at item 11. Item 12 is the handover. Test 5 is
Wajira's, with the real broker.

### Environment, measured in this session before planning

No new packages: NASM 3.01, QEMU 10.2.1, Python 3.14, OVMF, mtools, netcat,
the `claude` CLI. Every probe booted a **private copy** of the committed
ring 6a image under `stage6/out/probe6b/` (gitignored, removed at item 0);
no Claude call was made; nothing frozen was touched.

| Fact | Measured how |
|---|---|
| **With `-vga none -device VGA,edid=on,xres=1920,yres=1080` and a second `-drive ...,if=virtio`, PCI bus 0 holds: the VGA at device 1 (BAR2, the EDID, at `0x81084000`); the NIC `1af4:1000` at device 2 (BAR4 `0xc000000000`); the first virtio-blk `1af4:1001` at device 3 (BAR4 `0xc000004000`); the second virtio-blk at device 4 (BAR4 `0xc000008000`, BAR1 `0x81081000`).** `info block` names them `virtio0` = the first `-drive` (notes) and `virtio1` = the second (home): **drive order is PCI device order**, and the guest's scan walks devices 0–31 ascending, so "the first virtio-blk found" is the first drive and "the second found" is the second | the monitor's `info pci` and `info block` on the ring 6a image |
| **The ring 6a image boots to its sixteen lines with the second drive present and ignores it**: `S6: edid 1920x1080`, `gop 1920x1080`, **`console 120x67`**, `disk 32768 sectors` (the first drive), region `0x4c8080`, obs page `0x4c7000`, `glass core 1` | the serial capture of that boot |
| **`pci_scan` records the first virtio-blk only** (`cmp dword [rbp + VIO_FOUND], 0; jne .next_fn` — "first of each kind wins") into `disk_dev`; `disk_find`, `disk_negotiate`, `disk_queue_init` and `disk_rw` each `lea rbp, [disk_dev]` and share `req_hdr`, `req_status` and the `disk_vq_*` rings. To record both by drive order: a third device block `home_dev`, and the scan's blk match falls through to it when `disk_dev` is already found. `disk_rw` becomes `blk_rw` with the device block in RBP and the capacity in the block; two thin wrappers keep the callers | read, `stage6/stage6.asm` lines 1660–1736 and 2002–2183 |
| **The twin's seams are as amendment A2 promised:** `twin.rehearse(blob, name, choices, image, workdir, port=9998, extra_args=(), lines=16, after=None)`; `extra_args` are appended to the QEMU command after the NIC device; `lines` is the exact `S6:` count the first criterion demands; **`after(driver, xp)` is called between screendump B and Esc, while the app runs**, and its list of phrases is judged only after the nine criteria pass (`judge`, `ev["after"]`); a hook that raises is a failed hook. `Driver` offers `tell`, `type_text`, `screendump`, `serial_bytes`, `xp`, `read_obs`, `read_surface`. **`VGA_ARGS` is a module-level list read at `qemu_argv` call time**, so a caller may replace it. **`rehearse` wipes its `workdir` with `rmtree` before booting**, so a second drive for the twin cannot live inside the workdir. The listener replies with `app_frame(blob, name, choices)` — **`installed` 0 in every rehearsal** | read, `broker/twin.py` |
| **Two two-drive guests run side by side** — a gate-shaped guest on `stage6/out/probe6b/` and a twin-shaped one on its own copies under `stage6/out/probe6b/twin/`, each with esp, notes and home, both to sixteen lines at 120x67 | run 2 |
| **Every printable ASCII key but two types through the monitor and echoes byte-exact:** a full US key-name table (`shift-equal` for `+`, `shift-8` for `*`, `slash`, `minus`, `equal`, `comma`, `shift-apostrophe`, …) sent 96 keys at a 0.1 s gap and the serial echo was the 94 characters `!` through `}` plus space, exactly; **`` ` `` and `~` (scancode 0x29) do not arrive** — QEMU's `grave` key name does not reach the guest's map. So the calculator's `+ - * / =` and every digit are typeable in the twin, and the `press` verb excludes those two characters | run 3, the echo compared byte for byte |
| **A no-broker boot puts nothing on the wire unasked (A3):** the obs page read through the monitor just after `keyboard ready`, again after ten quiet seconds, and again after a note typed, gave `wire_conns 0 bytes_in 0 bytes_out 0` all three times; a `! echo` typed on the ring 6a image (which sends it to the wire) then gave `wire_conns 1 bytes_in 244 bytes_out 243` — the ARP exchange, the SYN and slirp's RST. So test 4's launch assertion compares two reads rather than trusting zero, and a launch that leaked to the wire would show as one connection and about 240 bytes each way | run 4, `Driver.read_obs` on a two-disk boot with 9999 closed |
| A ring 6a rehearsal takes **14 s** wall clock (boot, delivery, the three seconds, Esc, the note, quit); the plan's tests will add about a second per verb, well inside the twin's 90 s budget | `stage6/out/germline/*/rehearsal.log`, `mock.stderr.txt` |
| **The frozen frame rules already admit `installed` 1:** GLASS.md's table says `installed`: 0 this ring (1 at ring 6b); `app_header(..., installed=0)` takes it as a parameter; `parse_response` accepts 0 or 1; the guest's `app_valid` accepts `<= 1` (`cmp byte [rsi + APPH_INSTALLED], 1; ja .no`); `MODES[4]` is already `installing` in the frozen renderer and in the guest's `mode_words` | read, `stage6/GLASS.md`, `broker/glass.py`, `stage6/stage6.asm` |
| **The bodyguard allows every planned command**: the gate's and the oracle's QEMU lines with three drives under `stage6/out/`, the twin's with `stage6/out/rehearsal/twin/esp.img`, `.../twin/notes.img` and `stage6/out/rehearsal/home.img`, `truncate -s 16M` of both home images, `cp stage6/out/esp.img stage6/out/rehearsal/twin/esp.img`, `./stage6/test-6b.sh`, `python3 stage6/checkplans.py --install 2` and `--store`, `python3 broker/plans.py --mock …` and bare, `cat plans/calculator.md`, `nasm -f bin stage6/echo.asm -o stage6/echo.bin` (allowed until item 8 freezes the binary; `-o stage6/out/echo.check.bin` after), `git add` of the new files, `rm -rf stage6/out/germline stage6/out/rehearsal`, the review copy's `cp` and `rm`; `Write` on each new path allowed, on `stage6/test.sh` denied | the hook run directly on each payload |
| The ring 6a checker's driver, picture, record, germline and notebook helpers are importable from the frozen `stage6/checkglass.py` (`main` is guarded); its `drive` spells two drives and 1440x1440, so the new checker spells its own QEMU line and imports the rest | read |

---

## Deviations from the spec and the kickoff, for approval

Each argued from a measured fact or a frozen file. Everything else is the
spec as written.

1. **Without a second virtio-blk the machine is ring 6a's, line for line.**
   The frozen `stage6/test.sh` builds `stage6/stage6.asm` — the very source
   this ring grows — and boots it with one virtio disk demanding exactly
   sixteen `S6:` lines and the 6a choices row. So `S6: home <N> apps`
   appears only when a second virtio-blk exists; with one disk there is no
   home line, an `installed` frame draws `no home image: <name> not kept`
   and runs the app anyway, and nothing else differs. The 6a gate is the
   ring's regression on the same binary; the 6b gate always gives two disks.
2. **The home line is `S6: home <N> apps` in every case — `S6: home 0 apps`
   after a blank image is formatted.** One line shape instead of the
   notebook's two; "a blank home image is formatted on first boot" is
   asserted from the host by parsing the image after the boot, which is
   the stronger check.
3. **An install may carry an amendment at the door: `! install <name>, <text>`.**
   The foundation's "install this, but left-handed", made real because
   test 4 needs it: the mock has one canned build of `echo`, so "re-install
   replaces, undo brings the previous build back, hash-checked" would compare
   two byte-identical builds. `install echo, but big` is a mock table entry
   — the same build padded with zeros to 4096 bytes, a different hash and
   size under the same name — so the undo test swaps two builds that
   differ. The amendment is free text after the comma, keyed into the
   germline with the plan's hash, put in the real backend's brief.
4. **The twin's home image lives at `stage6/out/rehearsal/home.img`, beside
   a twin workdir of `stage6/out/rehearsal/twin/`** — the frozen `rehearse`
   wipes its workdir, so the second drive is a sibling, re-created blank
   before every rehearsal by the broker module.
5. **The rehearsal runs the plan's tests against an app delivered with
   `installed` 0.** The frozen listener sends the frame without the flag;
   the guest-side write to the home image is proven by the gate's own
   guest (tests 3 and 4), not by the twin.
6. **A failed plan test is refused as `rehearsal failed: <the test line>`**
   — the frozen `Glazier` prefixes every twin failure with `rehearsal
   failed: `, and the phrase the hook returns is the failing line verbatim
   (`expect "a"`). In the plan's own words, as the spec asks.
7. **`press` may not press `` ` `` or `~`** (measured: they do not arrive
   through the monitor). The grammar says so; no committed plan needs them.
8. **The choices-row table in GLASS.md is extended by HOME.md, not edited.**
   With no app running the row is `? ask   ! grow` followed by up to three
   `! <name>` items for installed apps — identical to 6a's when nothing is
   installed. The two running-app rows are unchanged (they already hold
   four items; Hick).
9. **A launch from the home image counts in neither `g` field** — the obs
   page's layout is frozen and the launch receives no frame. The mode word
   `running <name>` and the conversation record it.
10. **`plans/calculator.md` needs no adjustment for the grammar:** every
    one of its lines parses under the grammar below (`press 2+3=` presses
    four keys; `expect not "5"`; the two choices `= result` and `c
    clear`). It is copied byte for byte from the spec's appendix — after
    the owner's two intent changes of A2 are made there at item 2; the
    five tests stay exactly as written.

---

## Decisions taken in this plan

1. **The seventeen serial lines**, in order: `S6: alive`; `S6: edid …`;
   `S6: gop …`; `S6: boot services exited`; `S6: gdt and paging ours`;
   `S6: idt ready`; `S6: cores found <N>`; `S6: cores woken <N>`;
   `S6: console <C>x<R>`; `S6: disk <N> sectors` (the notebook's disk);
   `S6: notebook formatted` | `S6: notebook <N> notes`; **`S6: home <N>
   apps`** (line 12, the number of valid table entries after a blank or
   foreign image was formatted); `S6: nic <mac>`; `S6: component region
   …`; `S6: obs page …`; `S6: glass core <id>`; `S6: keyboard ready`.
   Without a second virtio-blk line 12 is absent and the rest stand
   (deviation 1). The gate's display is **1920x1080**: console 120x67;
   regions strip rows 0–1, choices rows 65–66, conversation rows 2–64 ×
   columns 0–59, app panel rows 2–64 × columns 60–119 — never baked in, read
   from the guest's own log as ever.
2. **The second disk in the guest** (`stage6.asm`, item 9): `pci_scan`
   records the first virtio-blk into `disk_dev` and the second into
   `home_dev` (a third `VIO_BLOCK_SIZE` block); each block gains a `u32`
   capacity field (`VIO_SECTORS`, the block grows by 8 bytes — the file is
   unfrozen). `disk_rw` becomes **`blk_rw`** — RBP = the device block; the
   capacity, the queue block and the rings come from it — with `disk_rw`
   and `home_rw` as wrappers; `req_hdr`/`req_status` stay shared (one
   request in flight, BSP only). `home_find` (attach if found, no error if
   absent), `home_negotiate` (VERSION_1, capacity as two halves, the 2^32
   limit), `home_queue_init` on its own 4 KB-aligned rings, `home_init`
   (HOME.md's format-or-scan, the table kept in RAM) — all after
   `notebook_init`, before `nic_find`, interrupts off, polled.
3. **The home image** (`stage6/HOME.md`, item 1): a raw image of 512-byte
   sectors, little-endian, every unnamed byte zero.
   - **Sector 0, the header:** `0x000` `GERMHOME` (8); `0x008` u32 version
     `1`; `0x00C` u32 sector size `512`; `0x010` u64 table first sector
     `1`; `0x018` u64 table sectors `8`; `0x020` u64 data first sector
     `9`; `0x028` u64 capacity in sectors; the rest zero. **Recognised**
     when the magic and version match; anything else is **formatted** on
     boot: the header written, sectors 1–8 zeroed, `S6: home 0 apps`.
   - **Sectors 1–8, the table:** sixteen **entries of 256 bytes**, two per
     sector, entry *i* at sector 1 + ⌊i/2⌋, offset (i mod 2) × 256:
     `0x00` name (32, NUL-padded, the plan-name alphabet below; a zero
     first byte means an empty slot, every byte zero); `0x20` u32 size
     (the current build, 16 to 1,048,576); `0x24` u32 first sector;
     `0x28` u32 sectors (= ⌈size/512⌉); `0x2C` zero; `0x30` SHA-256 (32);
     `0x50`–`0x7F` the **previous build** in the same shape (size, first,
     sectors, zero, hash), all zero when there is none; `0x80` the four
     **choice slots** (52 bytes, exactly the frame's); `0xB4`–`0xFF` zero.
     An entry is **valid** when the name is well formed, the size in
     range, the sector count right, the extent within `[data first,
     capacity)`, and the previous build empty or valid by the same rule;
     an invalid entry is ignored on boot and may be overwritten. **N** =
     valid entries. **No count in the header, no free-list:** the next
     free sector is `max(data first, max over valid entries of first +
     sectors, current and previous)` — recovered by scanning, as the
     notebook's count is; space behind an abandoned build is not
     reclaimed this ring (a caveat).
   - **What becomes an app on disk:** an app frame with `installed` 1,
     received and validated. The blob's tail is zeroed to the sector
     boundary; **the blob's sectors are written first, then the entry's
     table sector** — an install is one sector write away from either
     the old state or the new, never a mixture. An existing name is
     **replaced**: its current build becomes the previous build and the
     build before that is abandoned. A new name takes the first empty
     slot. No slot, or the blob does not fit: the app is **not kept**
     and runs anyway, with a console line and an error counted.
   - **The console lines** (HOME.md): `installed <name>`; `home image
     full: <name> not kept`; `no home image: <name> not kept`;
     `<name>: previous build restored`; `<name> has no previous build`;
     `no app named <name>`; `<name>: build does not match its hash`. All
     but the first and the fourth count one in `errors`.
   - **The SHA-256** is the guest's own, computed over the blob at
     install time and written into the entry, and **verified at every
     launch** before the build runs: the machine runs what the twin
     proved, or says why not. The test checks the guest's hash against
     Python's `hashlib` on the same bytes.
   - **Worked example bytes** in HOME.md: the header of a 16 MB image;
     the entry for `echo` after one install (its size, sectors at 9, its
     hash); the same entry after `install echo, but big` and after the
     undo; `parse_home(data)` in Python — the checker's parser, verbatim.
4. **What a `!` line does in the guest** (item 11), after `parse_marker`
   gives `!` and a trimmed body: an empty body → `nothing to grow` as
   before; a body beginning `undo install ` → the **undo** path (the name
   after it; a running app is closed first as any `!` does; the entry's
   two builds are swapped and the table sector written; the line
   `<name>: previous build restored`, or `<name> has no previous build`,
   or `no app named <name>`); a body **equal to a valid entry's name** →
   the **launch** path: the current build's sectors are read into the
   component region at +128, hashed, compared with the entry's hash
   (`<name>: build does not match its hash` and an error otherwise), a
   frame header synthesised at region +32 (kind 2, ABI 2, source 0,
   `installed` 1, the name, the entry's choices) and `run_app` called
   with a flag that skips the `g` counters (deviation 9) — **nothing on
   the wire: no connection, no bytes**; anything else → the broker as at
   6a, with **`mode` = 4 `installing`** instead of `growing` when the
   body begins `install ` (the strip's word). Names match exactly, byte
   for byte, after the marker parse's trim.
5. **The install write in the guest** (item 10): in `grow_request`, after
   `app_valid` passes and before `run_app`: if the header's `installed`
   byte is 1, `home_install` (decision 3) — with no `home_dev` found, the
   `no home image` line; then the app runs. The console line lands before
   the app's prompt line, so the conversation reads `> ! install echo`,
   `installed echo`, then the prompt.
6. **The choices row at the prompt** (HOME.md extends GLASS.md's table —
   deviation 8): `? ask   ! grow` then, for the first three valid entries
   in table order, `   ! <name>` each. Never more than five items. Written
   by `choices_update` whenever the table changes or an app closes. The
   running-app rows are 6a's.
7. **The plan file** (`stage6/PLANS.md`, item 1): `plans/<name>.md`, UTF-8
   ASCII only, in this exact shape:
   ```
   # <name>

   ## Intent
   <one or more lines of plain English>

   ## Choices
   <key> <label>          (zero to four lines)

   ## Tests
   <one verb per line>
   ```
   **The name** is `[a-z][a-z0-9-]{0,31}`, equal to the file's basename;
   it is what `! <name>` launches and what the frame carries. **Intent**
   is everything between its heading and the next; the text Claude builds
   from. **Choices**: `<key> <label>`, one printable non-space key, a
   label of 1–12 printable bytes — exactly the frame's choice slots, in
   order; the choices row shows the first three. **Tests**, the five
   verbs, one per line, blank lines ignored, anything else a parse error:
   - `press <keys>` — everything after `press ` is the keys, one press per
     byte, each `0x20`–`0x7E` bar `` ` `` and `~` (deviation 7); at least
     one; delivered to the app's `key` callback through the twin's
     keyboard (the monitor's `sendkey`, 0.2 s apart) with Shift where the
     US layout needs it.
   - `wait <ms>` — the twin sleeps that long, 1 to 30000.
   - `expect "<text>"` — the text (1–60 bytes, printable, no `"`) is on
     some row of the **app panel** as consecutive cells: the twin takes a
     screendump, reads every panel cell against the shared font (a glyph,
     a block, a blank) and searches each row for the text. **`expect`
     matches anywhere on the panel**, so a plan's intent should say what
     else is drawn (the calculator's "Nothing else is drawn" is not
     decoration; an echo app that drew `last key: a` would pass `expect
     "a"` before any key).
   - `expect not "<text>"` — no row holds it.
   - `expect changed` — the app panel's pixels differ from the last time
     the twin looked (the previous `expect` of any form, or the look it
     takes just before the first test).
   Every `expect` looks **at least 500 ms after the last `press`** so the
   app's `key` and `step` and a frame have run; `wait` is for apps that
   need longer. The tests run in order; **the first verb that fails ends
   the run and its line, verbatim, is the failure phrase** (deviation 6).
   **A rule for every plan (A1): an app must draw its starting state in
   `init`.** The frozen twin takes screendump B and judges "the app drew
   nothing" *before* it calls the hook, so a panel that is blank until the
   first key fails rehearsal before the plan's tests ever run. PLANS.md
   states it, the three committed intents obey it, and the backend's brief
   says the same sentence.
   PLANS.md carries the grammar as a table, the three committed plans as
   worked examples, and `parse_plan(text)` in Python — the parser the
   broker and the checker share.
8. **The twin runs the plan's tests** through the frozen `after` hook: the
   broker module builds a closure over the parsed tests; called with
   `(driver, xp)` it finds the obs page address in the twin's serial
   capture, reads `cols`/`rows` from the page for the regions, takes its
   first look (screendump), then walks the verbs — `press` via `driver.tell`
   with the module's key-name table (twin's `keyname` covers only what 6a
   typed), `wait` via `sleep`, the three `expect`s via screendump and
   `rehearse.read_ppm`/`render_cell`/`cell_matches` — and returns `[line]`
   at the first failure or `[]`. The verdict of every verb (`ok: press a`,
   `fail: expect "a"`) goes into the record's `tests` field and the
   provenance's `plan_tests`. The nine 6a criteria are judged first, by
   the frozen twin, exactly as before.
9. **The broker module — `broker/plans.py`** (item 3, frozen at item 8),
   standard library only, importing the frozen `glass` (`Glazier`,
   `app_frame`, `refusal_frame`, `glass_lookup`, `germline_write`,
   `mock_generate`, `normalise`, `MACHINE`, `ABI`, the constants), `twin`
   (`rehearse`, `VGA_ARGS`, `qemu_argv`), `rehearse` (the picture helpers)
   and `broker`/`germline` (`serve`, `mock_answer`, `to_wire`, `log`) —
   **editing none of them**:
   - **`twin.VGA_ARGS = ["-vga", "none", "-device", "VGA,edid=on,xres=1920,yres=1080"]`
     at import**, so every rehearsal this module runs is on the machine's
     display; the module's `DISPLAY` constant is the one place the flags
     are spelled, and test 4 asserts the twin's argv carries them.
   - **`Installer(Glazier)`**: `grow(body)` dispatches — a body of the form
     `install <name>` or `install <name>, <amendment>` goes to
     **`install(name, amendment)`**; anything else to the inherited
     `Glazier.grow` (so `! make me a clock` still works through this
     broker, rehearsed on the 1080p twin with the home drive). `install`
     is a new method built from `glass.py`'s exported pieces, modelled on
     `grow` (the tries loop, the failure fed back, the call counter, the
     record fields), differing where the spec says: it **reads
     `plans/<name>.md`** (`no plan named <name>` refused with no call if
     there is no such file; `plan <name> does not parse: line <n>`
     likewise). **A4: every body that begins with the word `install` is
     an install** — `install` alone, `install` followed by anything that
     is not a plan name (`install Echo`, `install my app`, `install ,x`),
     or a name with no plan file — and is refused `no plan named <rest>`
     (the rest of the body after `install`, trimmed; empty for `install`
     alone) before any generation call, in the mock and the real backend
     alike, so a typo never becomes a grown app called `install`; **keys the germline** as the first 16 hex digits of
     `sha256("install <name>|<plan sha256>|<normalised amendment>|abi2|qemu-q35-ovmf")`
     — a changed plan is a different key; calls `generate(body, failure,
     plan)` with the parsed plan; **rehearses through the module's
     `rehearse_plan`** — which re-creates `stage6/out/rehearsal/home.img`
     blank, then calls `twin.rehearse(blob, plan.name, plan.choices,
     image, workdir, port, extra_args=["-drive", "format=raw,file=<home>,if=virtio"],
     lines=17, after=<the tests hook>)`; the plain path's rehearse
     callable is the same wrapper without a hook; on a pass **writes the
     germline** with `germline_write(..., extra={"plan": name,
     "plan_sha256": …, "amendment": …, "installed": True, "plan_tests":
     […]})`; and **delivers `app_frame(blob, name, plan.choices, source,
     installed=1)`** — from the germline with `source` 1 and `installed`
     1 still set, so a re-install served from the cache replaces on the
     machine. The record's fields are `grow`'s plus `plan`, `plan_sha256`,
     `amendment`, `tests`.
   - **The mock** (`--mock`, the table frozen in PLANS.md): questions from
     UMBILICAL.md's table; a plain request from GLASS.md's table (imported
     `mock_generate`); an install: `install echo` → `stage6/echo.bin`,
     name `echo`, the plan's choices; `install liar` → `stage6/liar.bin`;
     `install echo, but big` → `echo.bin` padded with zeros to exactly
     4096 bytes (deviation 3); any other body naming an existing plan →
     the refusal `mock: no canned build for plan: <name>`; a body naming
     no plan file, or `install` alone or with a malformed name (A4) → `no
     plan named <rest>` before any table lookup (no generation call
     counted, mock and real alike). Every table lookup is one generation
     call.
   - **`main`**: `glass.py`'s flags with `--workdir` defaulting to
     `stage6/out/rehearsal/twin` (deviation 4) and `--plans` defaulting to
     `plans/`; `serve` from the frozen `germline.py` with an `Installer`.
   - Exposed for the checker: `DISPLAY`, `TWIN_HOME`, `twin_extra_args()`,
     `install_key(name, plan_bytes, amendment)`, `plan_keyname(ch)`,
     `read_panel_rows(shot, obs)`, the mock table's constants.
10. **The real backend** (`broker/claude_backend.py`, unfrozen):
    `grow(request, failure, timeout, model, abi=2, plan=None)`. With a
    plan, the brief is `APP_BRIEF` plus the GLASS.md sections plus a plan
    section: "You are building the app named `<name>` from this plan.
    Intent: … The choices row will show these keys, handle them: … After
    it is built the twin will run these tests against it, in order; the
    build must pass every one: … `expect "<text>"` means that text is
    somewhere on the app's panel; `expect not` that it is nowhere; draw
    only what the intent says. **Draw the starting state in `init`: a
    panel that is blank until the first key fails rehearsal before the
    tests run** (A1)." plus the amendment ("The person installing
    it adds: …"); the name delivered is the plan's, the choices the plan's
    (any `; choice` lines are ignored); a rehearsal failure fed back
    quotes the failed test. Never run by the gate.
11. **The fixtures** (item 2), hand-written ABI 2 NASM under 1 KB, source
    and binary committed and frozen, `.gitignore` gaining `!stage6/echo.bin`
    and `!stage6/liar.bin`: **`stage6/echo.asm`** — `init` draws a single
    **`-` at panel row 1, column 1** (A1: the starting state, so
    screendump B is not blank), `key` replaces that cell with the key,
    `step` and `exit` return: the app panel holds exactly one glyph — a
    dash, then the last key — and nothing else (so `expect "a"` proves
    the key, not a label). **`stage6/liar.asm`** — the same `init`, with
    `key` drawing the key **plus one** (`a` → `b`): runs safely, passes
    every 6a criterion, fails its plan's `expect "a"`. **The plans:**
    `plans/echo.md` — intent "Shows a dash until a key is pressed, then
    the last key pressed, as a single character at the top left of the
    panel. Nothing else is drawn."; no choices; tests `press a`, `expect
    "a"`, `press b`, `expect "b"`, `expect not "a"`. `plans/liar.md` —
    the same intent and tests under the name `liar` (a plan whose canned
    build lies). `plans/calculator.md` — the spec's appendix, byte for
    byte, after A2's two intent changes are made in the spec (deviation
    10).
12. **The harness** — `stage6/test-6b.sh` (6a's shape; frozen at item 8):
    refuses to run while 9999 or 9998 is held; the cage with
    **`mac=52:54:00:a1:06:02`**; **the display spelled once:**
    `DISPLAY="-vga none -device VGA,edid=on,xres=1920,yres=1080"`; wipes
    `stage6/out/germline/` and `stage6/out/rehearsal/`; builds with the
    unfrozen `stage6/mkimage.sh`; test 1; test 2; test 3 (`checkplans.py
    --install 2` and `--install 8`); test 4 (`--store`); the cage and
    display self-assertions. **`stage6/checkplans.py`**: its own
    `qemu_argv` (three drives, the 1080p flags, the cage) and `drive`
    (checkglass's step vocabulary plus `("home", label)` to snapshot the
    home image mid-run is unnecessary — the image is parsed after each
    boot), importing checkglass's picture, record, germline, notebook and
    mock-lifecycle helpers where they fit and spelling its own where the
    line count, the key, the broker or the frame differ; `parse_home` from
    HOME.md; `parse_plan` from PLANS.md; a mock started as
    `broker/plans.py --mock` with the gate's germline and the twin workdir.
    - **Test 1** (`test-6b.sh`): the artefact, 6a's criteria.
    - **Test 2** (`test-6b.sh`, three boots): at `-smp 8` with fresh notes
      and home images: **seventeen** lines in order with the 6a
      cross-checks, `S6: home 0 apps` twelfth, exit 124; the home image
      parsed from the host afterwards: a valid header for a 32768-sector
      disk, sixteen empty entries, sectors 1–8 zero; then the **same** home
      image booted again at `-smp 2`: `home 0 apps` again and the image
      **byte-identical** to before (a recognised image is not reformatted);
      then a boot with **one** virtio disk at `-smp 8`: exactly sixteen
      lines, no home line (deviation 1 — the 6a gate's shape, asserted here
      too).
    - **`--install <smp>`** (test 3): mock up, germline wiped, fresh notes
      and home; boot; `before` ⏎; `! install echo` ⏎; sleep 3; **obs I,
      screendump I**; wait for the record (150 s); settle 3 s; `q`; settle;
      **screendump A, obs A**; Tab; `mid` ⏎; Tab; `z`; **screendump B**;
      Esc; settle 2; `after` ⏎; settle; **screendump C**; quit. Assert: the
      seventeen boot lines with the MAC; the echo after ready exactly
      `before\r\n! install echo\r\nmid\r\nafter\r\n`; the record: one grow
      whose raw bytes are the request frame for `install echo`, `source
      generated`, `generation_calls 1`, `rehearsals ["pass"]`,
      `answer_kind app`, `answer_sha256` = `app_frame(echo.bin, b"echo",
      [], 0, installed=1)`, `name echo`, `plan echo`, `plan_sha256` =
      sha256 of `plans/echo.md`, `amendment null`, `tests` = the five
      `ok:` lines; the germline: one entry under `install_key("echo", …)`,
      the blob byte-identical, provenance with `abi 2`, `installed true`,
      `plan`, `plan_sha256`, `plan_tests`, a `rehearsal.log` with
      **seventeen** `S6:` lines, no `ERR:`, the nine `ok: not` lines and
      `ok: the post-delivery hook found nothing`; **the home image**: one
      valid entry `echo`, size = len(echo.bin), sectors ⌈size/512⌉ at
      sector 9, hash = `hashlib.sha256(echo.bin)`, previous all zero,
      choices all zero, the blob's sectors holding the build then zeros,
      every other entry zero; the notebook `["before", "mid", "after"]`;
      **screen I**: the mode field `installing`, `installing` in obs
      `mode` (4), the choices row `? ask   ! grow`, the app panel blank;
      **screen A**: the app panel's cell (1, 1) is `q` (the `-` drawn by
      `init` replaced) and every other
      panel cell blank; the choices row `Esc exit   Tab prompt`; the mode
      field `running echo`; the conversation `> before`, `> ! install
      echo`, `installed echo`, the prompt; obs A: `mode 3`, `name echo`,
      `focus 1`, `grows_generated 1`, `errors 0`; **screen B**: cell (1, 1)
      `z`, `> mid` under `installed echo`; **screen C**: the app panel
      background, **the choices row `? ask   ! grow   ! echo`**, mode
      `prompt`, the conversation through `> after` and the prompt; two
      colours everywhere.
    - **`--store`** (test 4, `-smp 8`): the argv assertions — the
      checker's own QEMU line (the cage on 9999, the 1080p device, three
      drives under `stage6/out/`) and the twin's as `plans.py` builds it
      (`twin.qemu_argv(..., extra_args=plans.twin_extra_args())` after
      `import plans`: `twin.VGA_ARGS` equal to the 1080p flags, the cage
      on 9998, three drives under `stage6/out/`); the fixtures' self-check
      (`echo`, `liar`); `parse_plan` on the three committed plans, the
      calculator's ten test lines and two choices as expected. Then
      **boot A** (mock up, germline wiped, record A, fresh notes and home):
      `! install echo` ⏎ (wait 150 s), settle, Esc, quit — the home image
      parsed: `echo` at sector 9, its hash; the first extent remembered.
      **Boot B, no broker** — the mock stopped, the checker asserting
      9999 closed, the same home image, fresh notes: **`S6: home 1 apps`**
      twelfth; **obs R** (read once, right after ready); **screendump P**:
      the choices row `? ask   ! grow   ! echo`; `! echo` ⏎; settle 2;
      `b`; settle; **screendump L, obs L**: cell (1, 1) `b`, mode field
      `running echo`, obs `mode 3`, `name echo`, **`wire_conns 0`, and
      `bytes_in` and `bytes_out` equal to obs R's** (A3 — measured: zero
      on this machine, but the assertion is "unchanged between the two
      reads", never "zero"; a leaked launch would show one connection and
      about 240 bytes each way), `grows_generated 0`, `grows_served 0`,
      `errors 0`; Esc; `! undo install echo` ⏎; settle;
      **screendump U**: the conversation `> ! echo`, `> ! undo install
      echo`, `echo has no previous build`, the prompt; obs `errors 1`;
      quit; the echo after ready exactly `! echo\r\n! undo install echo\r\n`;
      the home image **unchanged** byte for byte. **Boot C** (mock up,
      germline **kept**, record C, the same home, fresh notes): `! install
      liar` ⏎ (wait 240 s: two rehearsals), settle; `! install echo, but
      big` ⏎ (wait 150 s), settle 3; Esc; `! install echo` ⏎ (wait 20 s —
      the germline); settle 3; Esc; `! undo install echo` ⏎; settle; `!
      echo` ⏎; settle 2; `c`; settle; **screendump E**; Esc; `last` ⏎;
      settle; **surfaces D, screendump D, obs D2**; quit. Assert: record C
      in order — `install liar` refused after `["fail: expect \"a\""] * 2`
      (calls 3; the answer `rehearsal failed: expect "a"`, its frame
      hash; `tests` ending in the failing line); `install echo, but big`
      generated (call 4, `["pass"]`, the frame `app_frame(echo.bin + zeros
      to 4096, b"echo", [], 0, installed=1)`, `amendment "but big"`);
      `install echo` **germline** (still 4, `[]`, the frame with `source`
      1 and `installed` 1); the germline exactly two entries (echo; echo
      with the amendment), the liar absent; **the home image**: entry
      `echo` with **current = the first build** (sector 9, echo.bin's
      hash — the undo brought it back) and **previous = the padded build**
      (4096 bytes, 8 sectors, its own hash, at a later extent), both
      extents holding their builds byte for byte, N = 1; the notebook
      `["last"]`; the echo after ready the six typed lines; **screen E**:
      cell (1, 1) `c`, `running echo`; **screen D**: the strip against
      obs D/D2 cell by cell (checkglass's `check_strip`), every region
      outside the app panel equal to its surface, mode `prompt`, the
      choices row `? ask   ! grow   ! echo`, obs `errors 1` (the refusal),
      `grows_generated 1`, `grows_served 1`, the conversation `> ! install
      liar`, `rehearsal failed: expect "a"`, `> ! install echo, but big`,
      `installed echo`, `> ! install echo`, `installed echo`, `> ! undo
      install echo`, `echo: previous build restored`, `> ! echo`, `> last`,
      the prompt (wrapped at the panel's width where longer); two colours.
    The gate's cost: eight boots of its own (three in test 2, two in test
    3, three in test 4) plus six rehearsals (echo twice in test 3; echo,
    liar twice, echo-but-big in test 4), about twelve minutes.
13. **The freeze boundary** (item 8): `stage6/PLANS.md`, `stage6/HOME.md`,
    `plans/echo.md`, `plans/liar.md`, `plans/calculator.md`,
    `stage6/echo.asm`, `stage6/echo.bin`, `stage6/liar.asm`,
    `stage6/liar.bin`, `broker/plans.py`, `stage6/test-6b.sh`,
    `stage6/checkplans.py` — twelve paths. Not frozen: `stage6/mkimage.sh`,
    `stage6/stage6.asm`, `broker/claude_backend.py`, `stage6/plan-6b.md`.
    Everything frozen before stands untouched.
14. **The two commands for the oracle** (test 5), from the repo root:
    `python3 broker/plans.py` and
    ```
    truncate -s 16M stage6/out/home.img
    qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
      -vga none -device VGA,edid=on,xres=1920,yres=1080 \
      -drive format=raw,file=stage6/out/esp.img \
      -drive format=raw,file=stage6/out/notes.img,if=virtio \
      -drive format=raw,file=stage6/out/home.img,if=virtio \
      -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
      -device virtio-net-pci,netdev=n0 -serial stdio
    ```
    He types `! install calculator`; the strip says `installing` while
    Claude builds and the twin runs the plan's five tests; `installed
    calculator`, the calculator in its panel with `= result   c clear
    Esc exit   Tab prompt` on the row; he does a sum; Esc; he quits QEMU,
    stops the broker, boots the same command again: `S6: home 1 apps`,
    `! calculator` on the choices row; `! calculator`; the sum again. His
    word closes the ring.
15. **The prose the hook will dislike.** The new frozen basenames
    (`PLANS.md`, `HOME.md`, `echo.md`, `liar.md`, `calculator.md`,
    `echo.asm`, `echo.bin`, `liar.asm`, `liar.bin`, `plans.py`,
    `test-6b.sh`, `checkplans.py`) join the prose rule; commit messages
    go in by `-F` from a file written with the Write tool. Note `plans.py`
    and `plans/` share a stem: a `cp`/`rm`/`>` near either will be denied
    and reworded.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are expected green at its commit**. Items
  0–8 commit with every ring 6b test failing **by design**. From item 9 the
  stated tests must be green before the commit.
- **`./stage0/test.sh` … `./stage5/test.sh` and ring 6a's `./stage6/test.sh`
  stay green throughout** — run as regressions before every commit from
  item 9 (Stage 4's, 5's and 6a's need 9999 free, 5's and 6a's 9998 too;
  no two gates at once). Ring 6a's gate is the same binary with one disk
  at 1440x1440: it is this ring's proof that nothing 6a built has moved.
- `HANDOVER.md` is updated as we go, with a final pass at item 12; the
  model-and-effort record goes in at item 0.
- Every new fault class earns a CLAUDE.md gotcha line; the second time a
  mistake is corrected its line goes in.
- Temporary probes are never committed and never undone with `git checkout
  --`: copy aside, restore from the copy.
- **The scope guard** governs items 9–12: two honest attempts at any one
  obstacle — a real diagnosis from the serial log, the rehearsal log, the
  obs page or the parsed home image, not a re-run — then stop, record the
  exact state in `HANDOVER.md`, commit that, and wait for Wajira. A frozen
  file that needs to change is never edited: the diff is written unapplied
  under `stage6/out/`, recorded, and the owner applies it.
- **Everything runs inside QEMU with the caged network and the VGA device.**
  The only disks are raw files under `stage6/out/` (the gate's three; the
  twin's copies under `stage6/out/rehearsal/twin/` and its home at
  `stage6/out/rehearsal/home.img`), created fresh by the harness or the
  broker. Both brokers bind only `127.0.0.1`. Nothing outside the repo is
  written, bar scratch files in the session temp directory. **No real
  Claude call is made by this session**: the mock is the only broker the
  gate ever talks to, `claude_backend.grow` is never run here, and test 5
  is Wajira's.
- If the owner says the session budget is nearly spent: finish the current
  item, commit, record the exact state in `HANDOVER.md`, stop.

---

# Part 1 — the documents, the plans and fixtures, the broker module and the acceptance machinery, written before the code

## Item 0 — this plan, committed

Copy this file verbatim to `stage6/plan-6b.md` and commit it. The first act
after the gate opens. In the same act, delete `stage6/plan-6b.review.md`
(Cowork's review copy, never committed) and the probe artefacts under
`stage6/out/probe6b/`; record in `HANDOVER.md` that ring 6b is implemented
on Fable 5.1 at medium effort as the owner's experiment, to be compared
with Opus at high (Stages 0 and 1) and Fable at high (Stages 2 to 6a), and
that Cowork reviews to the same standard as every ring.

*Expected at commit:* no ring 6b tests exist yet. Stages 0–5 and ring 6a
green (unchanged).

## Item 1 — `stage6/PLANS.md` and `stage6/HOME.md`, byte-exact

Decisions 3, 4, 6, 7 and 8 as two documents in the GLASS.md manner: what
each adds to the frozen documents and what it leaves alone (GLASS.md's
frame, its `installed` byte and mode 4, referenced not restated). PLANS.md:
the file shape, the name alphabet, the choices, the five verbs as a table
with the exact grammar and how the twin runs each, the settle rule, the
first-failure rule and the refusal text, the broker's install pipeline
(the plan read, the brief, the key with the plan's hash and the amendment,
the rehearsal with seventeen lines and the hook, the delivery with
`installed` 1, the record's and provenance's extra fields), the amendment
at the door, the mock's table, the three committed plans as worked
examples, and `parse_plan(text)` in Python. HOME.md: the disk, the header,
the table entry, validity, the free-sector rule, what becomes an app on
disk and the write order, replace and undo, the launch and the hash check,
the console lines and which count as errors, the choices row's extension,
line 12 and the one-disk case, worked-example bytes, and `parse_home(data)`
in Python.

*Expected at commit:* no ring 6b tests yet. Everything green as before.

## Item 2 — the plans and the fixtures

First, A2: the owner's two changes to the calculator's intent are made in
`stage6/spec.md`'s appendix — the one edit that file receives, recorded in
`HANDOVER.md` as the owner's approval at the 6b plan gate — so the appendix
reads: "A four-function calculator for whole numbers. The panel shows a
single line: the number being typed, or the result of the last sum; it
shows 0 before anything is typed and after c clears. Digits 0 to 9 type a
number. The keys + - * / choose an operation. = shows the result, which
may be negative. c clears everything. Division is whole-number division;
dividing by zero shows the word error until the next key, which clears it.
Numbers larger than nine digits show error the same way. Nothing else is
drawn." — the choices and the five tests untouched. Then `plans/echo.md`,
`plans/liar.md` (A1's intents), `plans/calculator.md` **copied from the
spec's appendix** byte for byte; `stage6/echo.asm`, `stage6/liar.asm`
(A1: the dash from `init`) and their binaries, the `.gitignore`
exceptions, each binary's size and SHA-256 in the commit message and in
HOME.md's worked example. Proven on the host alone with a
scratch script: each blob's offsets are inside it,
`parse_response(app_frame(blob, name, choices, 0, 1))` round-trips with
`installed` 1, the three plans parse under a first cut of `parse_plan`,
and the calculator's lines come out exactly as the appendix wrote them.

*Expected at commit:* no ring 6b tests yet.

## Item 3 — `broker/plans.py`, and the backend's plan brief

Decisions 8, 9 and 10 in code. Proven on the host alone, no guest, no
Claude call, against `--mock` on a throwaway port with `--image` pointing
at a file that does not exist: `ping` → `pong`; `x` → `mock: no canned
component for: x` (the inherited path); `install nothing` → `no plan named
nothing` with `generation_calls` unchanged; `install echo` → the pipeline
into the twin, which fails `the twin did not boot` twice (no image), the
record carrying `plan echo` and its hash; an `Installer` given a stub
rehearse callable that always passes delivers a frame whose byte 44 is 1
and writes provenance with `installed true` and `plan_tests`; the tests
hook, given a fake driver that returns canned screendumps, passes echo's
five verbs and fails liar's at `expect "a"`; `twin.VGA_ARGS` reads
1920x1080 after `import plans` while `checkglass.DISPLAY_EDID` still reads
1440x1440; `install_key` differs between `echo` and `echo, but big`;
`install`, `install Echo` and `install my app` are each refused `no plan
named …` with the call counter unchanged (A4).

**Then one real twin run, no token, before anything is frozen (A1):**
`broker/plans.py`'s `rehearse_plan` called by hand on `stage6/echo.bin`
with `plans/echo.md`'s tests against the committed ring 6a image at
1920x1080 with the home drive — **must pass all nine criteria and all
five verbs** (`ok: not '…'` nine times, `ok: the post-delivery hook found
nothing`, seventeen `S6:` lines) — and on `stage6/liar.bin` with
`plans/liar.md`'s tests — **must fail at `expect "a"`** with the nine
criteria passed first. Both rehearsal logs are quoted in the item 3 commit
message. Never freeze a fixture that has not run in the twin. (The ring
6a image has no home line; the hand run passes `lines=16` for this one
check and says so in the log; the frozen module default stays 17.)

*Expected at commit:* no ring 6b tests yet. No Claude call.

## Item 4 — `stage6/test-6b.sh` and acceptance test 1

Decision 12's harness with test 1. The three-drive QEMU line, the 1080p
display spelled once, the new MAC, the port refusals, the wipes.

*Expected at commit:* every ring 6b test fails (the binary has no home
line). The non-zero exit quoted in the commit message.

## Item 5 — acceptance test 2 (seventeen lines, the home formatted, one disk)

Decision 12's test 2: `serial_check` grown to seventeen positional lines
with the home line twelfth and a `disks` argument; the host-side parse of
the home image after the first boot (the header and the empty table, via a
`python3 -` block that only reads); the second boot's byte-identity; the
one-disk boot's sixteen lines.

*Expected at commit:* tests 1–2 fail.

## Item 6 — `stage6/checkplans.py --install` (test 3)

Decision 12's first mode: the driver with three drives and the 1080p
display, the seventeen-line pattern table, the plans mock, `parse_home`,
`parse_plan`, the echo fixture's one-cell picture check, the install
record and germline checks with the plan fields, the home-image check, the
four screens. `test-6b.sh` gains test 3 at `-smp 2` and `-smp 8`.

*Expected at commit:* tests 1–3 fail.

## Item 7 — `checkplans.py --store` (test 4)

Decision 12's second mode: the argv assertions on the checker's and the
module's twin command, the three boots, the no-broker assertion (port 9999
closed before boot B, the obs wire counters zero after the launch), the
record and germline judged entry by entry, the undo proven by the home
image's two extents and hashes, the screens. `test-6b.sh` gains test 4.

*Expected at commit:* tests 1–4 fail.

## Item 8 — freeze the ring 6b acceptance machinery

`PROTECTED` grows the twelve paths of decision 13, the hook's comment says
why each is a criterion and why `mkimage.sh`, `stage6.asm`,
`claude_backend.py` and `plan-6b.md` are not. `payloads.py` gains the ring
6b group: `freeze_cases` on each new path, the `-o` side door on each new
binary, the allowances measured above (the three-drive gate and oracle
lines, the twin's line with its sibling home image, both `truncate`s,
running the gate and the checker, `python3 broker/plans.py --mock …` and
bare, `cat plans/calculator.md`, `nasm … -o stage6/out/echo.check.bin`,
every operation on the unfrozen four, `rm -rf stage6/out/germline
stage6/out/rehearsal`) and the denials (`Write` on each, `nasm -o` over
`stage6/echo.bin`, a heredoc writing `plans/echo.md`). Re-run whole, 0
wrong; immediacy demonstrated live with one denied call.

*Expected at commit:* tests 1–4 still fail; the payload table 0 wrong.

---

*Everything above is written before any implementation code exists.
Everything below is the code.*

---

# Part 2 — the implementation, in the spec's order

## Item 9 — the second disk, the home image, line twelve

Decisions 1, 2 and 3 in `stage6/stage6.asm`: `home_dev` and `pci_scan`'s
second match; `VIO_SECTORS` in the block; `blk_rw` with the wrappers;
`home_find`/`home_negotiate`/`home_queue_init` on their own rings; the
table in RAM (`home_table`, 4 KB), `home_init` (format or scan, the entry
validity rule, the next-free-sector rule, N), line 12; the one-disk case
silent. Verified with a **temporary, uncommitted probe** (copy aside): a
two-disk boot prints `S6: home 0 apps` and the host parses the formatted
image; a second boot on it prints the same and leaves it byte-identical;
`./stage6/test.sh`'s one-disk shape gives sixteen lines.

*Green at commit:* **tests 1 and 2.** Tests 3–4 red. Stages 0–5 and ring
6a green.

## Item 10 — SHA-256, the install write, `installing`

Decisions 3 and 5: `sha256(ptr, len) → 32 bytes` in the guest — the
standard algorithm, the 64-entry K table in data, message schedule and
rounds in a straight loop, padding handled in the routine — **verified on
the host first**: the routine assembled with `nasm -f elf64` into a tiny
Linux program under the session scratchpad and its digests of the fixtures
and of a 4096-byte and a 1,048,576-byte buffer compared with `sha256sum`,
before it ever runs in the guest. Then `home_install` (the tail zeroed, the
blob's sectors written from the region, the entry built or replaced, its
table sector written, the console lines, `errors`), called from
`grow_request` on `installed` 1; `mode` 4 when the body begins `install `;
the `no home image` line without a second disk.

Verified by hand against `plans.py --mock`: `! install echo` shows
`installing` on the strip, `installed echo`, the app; the host parses the
entry and its hash equals `hashlib`'s; `! install echo, but big` replaces
and the previous fields fill.

*Green at commit:* tests 1 and 2. Tests 3–4 red (the choices row and the
launch are item 11).

## Item 11 — the choices row, the launch, the undo

Decisions 4 and 6: `choices_update`'s no-app row with up to three
installed names; the `!` dispatch — `undo install <name>`, a body equal to
an installed name (the read into the region, the hash check, the
synthesised header, `run_app` without the `g` count), else the wire;
the console lines. Verified by hand first, then the gate.

*Green at commit:* **all four automated tests** at `-smp 2` and `-smp 8`.
Full `./stage6/test-6b.sh` output in the commit message. `./stage6/test.sh`
and Stages 0–5 green.

## Item 12 — HANDOVER, gotchas, README, the payload table, the two commands

`HANDOVER.md` to the green-pending-oracle state (what was built, the
addresses and geometry on this build, tests 1–4 green with output, test 5
pending with decision 14's commands, the caveats: space behind an
abandoned build not reclaimed; sixteen apps; names by exact match; a home
launch counts in neither `g` field; the twin rehearses with `installed` 0;
drive order is the contract for which disk is which; no watchdog still);
`CLAUDE.md`'s build block gains `./stage6/test-6b.sh` and the second
correction of anything that bit twice; `README.md`'s running section gains
ring 6b's commands at 1920x1080 with both drives; `python3
.claude/hooks/payloads.py` re-run, 0 wrong; the two commands printed for
Wajira; stop.

*Green at commit:* all four automated tests, ring 6a's gate, Stages 0–5.

---

## Verification

- **Automated:** `./stage6/test-6b.sh` from the repo root — refuses to start
  if anything listens on 9999 or 9998; builds; tests 1–4 (three serial
  boots; the install at `-smp 2` and `-smp 8` against the mock, each with a
  rehearsal that runs echo's five tests; the store run with the no-broker
  reboot, the liar refused twice, the amended re-install and the undo
  proven from the parsed image). About twelve minutes. Exit 0 only if all
  pass. Run before every commit from item 9 on.
- **Regression:** `./stage6/test.sh` (ring 6a, the same binary with one
  disk at 1440x1440) and Stages 0–5's gates green before every commit from
  item 9.
- **The hook:** `python3 .claude/hooks/payloads.py` at items 8 and 12 —
  every case from every stage, 0 wrong; immediacy demonstrated live.
- **The probes:** item 3 (host-only), 9, 10 (the host-side SHA-256 check
  before the guest) and 11 each state their expected output.
- **Manual (test 5):** Wajira, decision 14's commands. `! install
  calculator`; a sum; QEMU quit and the broker stopped; the same QEMU
  command again; `! calculator`; the sum again. His word closes the ring.

## Safety

Everything runs inside QEMU. Firmware, the VGA device, and exactly three
drives per guest — raw files under `stage6/out/` (the twin's copies under
`stage6/out/rehearsal/twin/`, its home beside them) — created by the harness
or the broker; the bodyguard is unchanged and was run on every planned
command before this plan was written. The network is slirp with
`restrict=on` and one `guestfwd` in every QEMU line, the twin's included;
the brokers bind `127.0.0.1` only; test 4's no-broker boot proves a launch
from disk opens no connection. The automated gate talks only to the mock,
never to Claude, and refuses to run if anything else holds either port. An
installed app runs at ring 0 with the whole machine in reach — the thesis —
and the rehearsal against the plan's own tests is now the mitigation *and*
the correctness check the foundation prescribes; the hash at launch means
the machine runs what the twin proved. This session makes no Claude call
and never runs `claude_backend.grow`. Every existing frozen file is
untouched: `git diff --stat` against `2956e83` on every `PROTECTED` path is
empty at every commit, and `./stage6/test.sh` is green at the end of the
ring.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| The second disk is not where the guest looks, or the drives swap | measured: drive order is PCI device order on this machine, the scan walks ascending; the home image is recognised by its own magic and a foreign one is formatted, never read as apps |
| The 6a gate breaks on the new binary | deviation 1 is a design rule, asserted by 6b's own test 2 (the one-disk boot gives sixteen lines) and by running `./stage6/test.sh` before every commit |
| The guest's SHA-256 is wrong | verified on the host against `sha256sum` before it runs in the guest; test 3 compares the entry's hash with `hashlib`; a wrong hash refuses its own launch, loudly |
| A torn install | the blob's sectors are written before the entry's sector; the table is one sector write from either state |
| The plan's tests pass a wrong build | the liar fixture must be refused at `expect "a"`; `expect` reads the screen through the font, not the app's word for it |
| The tests hook outruns the app | the 500 ms settle after a press, `wait` for more; the twin's 90 s budget bounds a slow plan |
| The twin's monitor cannot type a plan's key | measured: 94 printables arrive; the grammar excludes the two that do not |
| A frozen file needs to change | the scope guard: stop, the diff unapplied under `stage6/out/`, the owner's hand |
| The gate spends a token | the double port refusal; the mock's table; `claude_backend` imported only outside `--mock`; the call counts demanded by the record checks |
| Hick's five | the row is built from the first three entries by construction; the checker asserts the exact row text |
| A fixture that has never run in the twin is frozen wrong | A1: item 3 rehearses echo and liar for real in the twin before item 8 freezes them, and quotes the logs |

---

## Amendments — Cowork's review, adopted before approval

Cowork approved the plan with four amendments and accepted all ten
deviations.

**A1 — Blocking: an app must draw its starting state in `init`.** The
frozen twin takes screendump B and judges "the app drew nothing" before it
calls the `after` hook, so a panel that is blank until the first key fails
rehearsal before the plan's tests run. The echo and liar fixtures draw a
single `-` at panel row 1, column 1 in `init`, and `key` replaces it; their
intents read "shows a dash until a key is pressed, then the last key
pressed, as a single character at the top left; nothing else is drawn".
PLANS.md states the rule for every plan; the backend's plan brief says the
same sentence. And item 3 gains one real twin run, no token, before
anything is frozen: `rehearse_plan` on `stage6/echo.bin` with
`plans/echo.md`'s tests must pass all nine criteria and all five verbs, and
on `stage6/liar.bin` must fail at `expect "a"`; both rehearsal logs are
quoted in the item 3 commit message. Never freeze a fixture that has not
run in the twin. (Decisions 7, 10, 11 and 12, items 2 and 3, the risk
table updated.)

**A2 — The calculator's intent, two owner-approved changes.** The line
shows `0` before anything is typed and after `c` clears; dividing by zero
shows the word `error` until the next key, which clears it; numbers larger
than nine digits show `error` the same way. The appendix in
`stage6/spec.md` is updated to match at item 2 — the one edit that file
receives, recorded in `HANDOVER.md` as the owner's approval at the 6b plan
gate — and `plans/calculator.md` is copied from there. The five tests stay
exactly as written. (Deviation 10, decision 11 and item 2 updated.)

**A3 — Test 4's no-broker launch compares two reads.** `bytes_in` and
`bytes_out` are not asserted to be zero, because slirp may put unsolicited
bytes on the wire at boot; the obs page is read once after `keyboard
ready` and once after the launch, and the assertion is `wire_conns` 0 and
`bytes_in` and `bytes_out` unchanged between the two reads. Measured
before writing the assertion (the environment table): on this machine the
counters were zero after ready, after ten quiet seconds and after a note,
and a `!` that reaches the wire with no broker costs one connection and
244/243 bytes. (Decision 12 and the environment table updated.)

**A4 — `install` with no name, or with something that is not a plan name,
is refused `no plan named <rest>`** before any generation call, in the
mock and the real backend alike, so a typo never becomes a grown app
called `install`. (Decision 9 and item 3 updated.)

**Also, at item 0:** `stage6/plan-6b.review.md` — Cowork's review copy —
is deleted alongside the probe artefacts and never committed.
