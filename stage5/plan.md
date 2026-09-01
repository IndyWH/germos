# Stage 5 — implementation plan

**To be committed verbatim as `stage5/plan.md`. Produced in plan mode, per the
foundation's build loop. Nothing below is implemented until Wajira approves
this document by writing the approval marker from his own terminal; the
ExitPlanMode hook holds the gate until then. Plan mode allows this session to
write only this one file, so — exactly as Stage 4 did — the copy to
`stage5/plan.md` and its commit are the first act after the gate opens, item
0 below, before any other file is touched.**

## Context

Stage 4 is closed: on 1 September 2026 the booted machine asked Claude a
question over its own TCP stack and printed the answer. Stage 5 closes the
loop the whole project exists for — the foundation's *conversation*: English
in, machine code back, verified in the twin, then run; the germline as a
local cache of proven components. The done-when: **"make me a clock"
produces a running clock.** You type `! make me a clock` at the prompt; the
broker asks Claude for a flat binary against a published ABI, rehearses it
in a headless boot of the very same guest image, caches what passes, and
delivers it; the guest loads it into a fixed region and jumps in; Esc brings
the prompt back; asking again is served from the germline with no generation
call at all.

`stage5/spec.md` is approved and fixes the shape (the third kind of line,
the forgiving marker parse, the loader and the four-entry service table,
one new frozen document `stage5/GERMLINE.md`, the four-step broker pipeline,
the generic rehearsal criteria), the five acceptance tests, the cleared
policy gate (`claude -p` still on the Max subscription, no API keys, next
re-check at Stage 6), and the owner's four decisions — `! ` as the grow
marker with the forgiving parse, the minimal service table with the clock
reading the CMOS RTC by its own port I/O, generic rehearsal criteria this
ring, and Fable 5 at high effort implementing (the model this session runs
on, by the owner's launch). Stage 4's test 5 finding — `?` without the space
went silently to the notebook — is closed by the marker parse here.

The kickoff's standing orders, restated: the automated gate talks only to
the mock and spends no token and needs no internet; the real `claude -p`
backend is exercised only by the owner at test 5; **the cage, the storage
bodyguard and every existing frozen file stand**; `stage4/UMBILICAL.md` is
frozen and untouched — the new wire lives entirely in `stage5/GERMLINE.md`.

The plan is **evaluation-first**, as Stages 1–4 were. Items 1–7 write the
wire document, the test component, the broker's grow pipeline and the
acceptance machinery so that tests 1–4 exist and fail before a single
instruction of `stage5.asm` is written. Item 8 freezes them. Items 9–13
grow the implementation on Stage 4's proven body and the gate closes at
item 13. Test 5 is Wajira's, with the real broker.

### Environment, verified in this session before planning

No new packages: NASM 3.01, QEMU 10.2.1, Python 3.14 with Pillow, OVMF,
mtools, OpenBSD netcat, the `claude` CLI 2.1.252. The probes below ran on a
patched **scratch copy** of `stage4.asm` built and booted under
`stage4/out/` (never committed, removed afterwards); no Claude call was
made.

| Fact | Verified how |
|---|---|
| **A 1 MB + 4 KB region declared in BSS loads and is usable.** With `comp_region: resb 0x101000` added, `image_size` is 1,847,296 bytes, OVMF loads it at the preferred base as before, and all twelve Stage 4 lines still appear; the region lands at **`0x4b4000`** on this build (it will move a little with Stage 5's code, which is why the guest reports it on serial) | the probe's `P: region`, `P: image_size` lines and the twelve `S4:` lines |
| **Code copied into that region executes.** A four-byte blob (`lea eax,[rdi+1]; ret`) copied to region+32 and called with `EDI = 0x1234` returned **4661** — even though EFER reads **`0xd00`**, NXE on: our own page tables carry no NX bits, so under our CR3 every mapped page is executable. No memory-map hunting, no new mapping, no attribute change is needed | `P: blob call returned 4661`, `P: efer 0x0000000000000d00` |
| **The TSC runs at about 2.998 GHz here**: 29,978,396 ticks across one `pit_wait(PIT_10MS)`. A millisecond is about 3.0 M ticks; calibrating once at boot against the PIT gives the ticks service with no new interrupt | `P: tsc per 10ms 29978396` |
| The monitor's **`sendkey shift-1` arrives as `!`** through Stage 4's shifted table; **`sendkey esc`** reaches the guest as scancode `01`, which the current tables map to 0 (nothing echoed) — the Esc convention needs one table entry | echo after ready was exactly `!xy\r\n` for `shift-1 x esc y ret` |
| The bodyguard allows every planned command: `python3 broker/germline.py --mock --port 9999 --germline stage5/out/germline --record ...`, the rehearsal QEMU line with its drives under `stage5/out/rehearsal/` and its `guestfwd ... nc -N 127.0.0.1 9998`, `./stage5/test.sh`, the checker, `nasm -f bin stage5/component.asm -o stage5/component.bin`, `rm -rf stage5/out/germline`, `ls germline/` | the hook run directly on each payload, exit 0 |
| The Stage 4 image's memory layout, as the loader carries it forward: the image at `0x400000`, BSS inside it (`absolute`), the BSP stack 16 KB, `rx_stream` 4+4096, `tcp_input` copying in-order data into `rx_stream` bounded by `RX_STREAM_MAX`, `tcp_recv_response` judging the frame by its prefix, `ask_question` drawing through `console_putc`, `console_scroll` already re-rendering the whole screen from the shadow, the keyboard translation (E0, Shift, two tables) living in `main_loop` | read, `stage4/stage4.asm` |
| `claude -p` still takes `--output-format text`, `--tools ""`, `--no-session-persistence`, `--system-prompt`, `--model`; `--bare` exists and stays off (Stage 4's gotcha) | `claude --help`; no call was made |

---

## Deviations from the spec, for approval

Three, each argued from a fact above or from the kickoff's orders. Everything
else is the spec as written.

1. **`broker/broker.py` stays frozen and byte-identical; the Stage 5 broker
   is `broker/germline.py`, which imports the frozen framing.** Stage 4's
   plan decision 13 said Stage 5 "will ask the owner to open the freeze on
   `broker.py`". The kickoff instead says every existing frozen file stands,
   and there is a clean way to obey it: `germline.py` imports `read_frame`,
   `frame`, `valid_request`, `to_wire`, `mock_answer`, `RecordingSocket` and
   `Recorder` from `broker.py` — one implementation of the frame, exactly as
   decision 13 wanted — and adds its own accept loop, the marker-byte
   dispatch and the grow pipeline. Questions ride through the very code the
   Stage 4 gate froze; Stage 4's gate keeps running its own mock unchanged.
   The cost: the Stage 5 command for the owner is `python3
   broker/germline.py`, not `broker.py` — one broker that answers both
   kinds of line. `germline.py` is frozen at item 8 for decision 13's
   reason (its mock table, its record and its cache are criteria).
2. **The guest allows 600 s for a grow response, not the 150 s of a
   question.** A grow is generation (up to 120 s) plus rehearsal (a headless
   boot, up to 90 s), and the pipeline allows one retry with the failure
   fed back (decision 9), so the honest bound is about 420 s. Questions keep
   UMBILICAL.md's 150 s exactly. The indicator turns throughout.
3. **Test 3 types one key while the component runs**, and demands the
   component show it (`key: k`), before Esc. The spec's test 3 proves the
   picture and Esc; this proves the third service, `poll_key`, returns a
   key and not just Esc — the one part of the ABI the spec's picture alone
   would leave untested. Two screendumps: during, and after Esc.

---

## Decisions taken in this plan

Judgement calls inside the approved spec, flagged so Wajira can overrule any
of them at approval rather than find them in a diff.

1. **The thirteen serial lines, exactly.** Stage 4's twelve with `S4:` →
   `S5:`, plus **line twelve `S5: component region 0x<16 hex> 1048576
   bytes`** between `S5: nic <mac>` and `S5: keyboard ready`: the address is
   where a component's first byte will live (the region base plus 32, see
   decision 3), and the number is the cap. `keyboard ready` stays last, so
   the serial contract after it stays exactly Stage 2's. The checker asserts
   the address is non-zero, below 4 GB, and ≡ 64 mod 4096 (decision 4: a
   page-aligned region, the blob at +64), and the cap is 1048576 — a
   constant in the assembler could pass the last check, and that is fine:
   the cap *is* a constant.
2. **The forgiving marker parse** (GERMLINE.md, "What is a question, what
   is a request"; supersedes UMBILICAL.md's "What is a question" for
   Stage 5 binaries — that document is untouched, and Stage 4's `? ...`
   form gives byte-identical wire traffic under the new rule). On Enter:
   skip leading spaces; if the first byte is `?` it is a **question**, if
   `!` a **request**, otherwise a **note** (Stage 3's path unchanged, empty
   line no note). The body is everything after the marker with leading and
   trailing spaces removed: `? ping`, `?ping`, `?   ping  ` and ` ? ping`
   all ask `ping`. An empty body draws, console-only, **`nothing to ask`**
   or **`nothing to grow`** on its own line, then the prompt — never
   silence, never the notebook. A marker line is never journaled. A note
   that merely contains `?` or `!` later in the line is still a note.
3. **The wire, one document** (`stage5/GERMLINE.md`, item 1). The frame is
   UMBILICAL.md's (`u32` little-endian length, then bytes); the connection,
   addressing, cage and timers are UMBILICAL.md's, referenced not restated.
   - **A grow request** is a request frame whose **first byte is `0x01`**,
     followed by the request text: 1 to 497 bytes, `0x20`–`0x7E`. The
     marker byte is deliberately *not* printable: a question's text is any
     printable bytes, so `!` as the marker would make `? !something`
     unaskable; `0x01` can never be typed and never collides. Stage 4's
     frozen `broker.py` rejects such a frame as "not printable" — which is
     right: a Stage 4 broker cannot grow.
   - **A grow response** is one frame of `N` bytes whose **first byte is
     the kind**: **`0x00` — a refusal**, the remaining `N−1` bytes text as a
     question's answer (`0x20`–`0x7E` or LF, at most 4096), drawn exactly
     like an answer; **`0x01` — a component**, followed by a 31-byte header
     and the blob: bytes 1–3 zero; bytes 4–7 `u32` ABI version, `1`; bytes
     8–11 `u32 L`, the blob length, 1 to 1,048,576; bytes 12–31 zero,
     reserved — kind byte plus header is 32 bytes, so **the blob begins at
     byte 32 of the frame** and `N = 32 + L`. A frame that says otherwise (kind unknown, ABI not 1, `L` zero or
     over the cap, `N ≠ 32 + L`) draws **`bad component frame`** and the
     prompt. A response whose `N` exceeds 32 + 1,048,576 is invalid (the
     no-answer rule).
   - **The deadline** for a grow response is **600 s** from the request
     being acknowledged (deviation 2); the no-answer rule and its console
     text are UMBILICAL.md's, unchanged.
   - Worked-example bytes: the request frame for `! test component`
     (`0f 00 00 00 01 74 65 73 74 20 63 6f 6d 70 6f 6e 65 6e 74`), a
     refusal frame, and a component frame for the four-byte blob `8d 47 01
     c3` (`24 00 00 00 01 00 00 00 01 00 00 00 04 00 00 00` then 20 zero
     bytes then the blob); and the boundary stated in bytes: the largest
     legal frame, `N = 32 + 1,048,576`, received at `comp_region + 28`,
     **ends exactly at `comp_region + 0x100040`**, the region's last byte
     (Cowork's amendment); the shared Python parser (`parse_response`,
     `component_frame`, `refusal_frame`, `grow_request`) printed in the
     document and used verbatim by the broker, the rehearsal and the checker.
4. **The component region lives in the image's BSS** — measured, not
   assumed (the environment table): **`comp_region: resb 0x100040`**,
   page-aligned, immediately before the page tables. A grow response is
   received *straight into it*, no staging buffer and no second copy: the
   stream begins at **`comp_region + 28`**, so the 4-byte length prefix
   occupies +28..+31, the kind byte and the 31-byte header +32..+63, and
   the blob — byte 32 of the frame — begins at **`comp_region + 64`**,
   64-aligned; the largest legal frame (4 + 32 + 1,048,576 bytes) ends
   exactly at +0x100040. Line 12 prints `comp_region + 64`, the address
   the component's first instruction will have. (Stated once here so the
   arithmetic is reviewed, not discovered.)
5. **The entry contract** (GERMLINE.md, "The entry contract"). The core
   `call`s the blob's first byte in 64-bit long mode, ring 0, on the
   identity map, with **`RDI` = the address of the service table**, the
   direction flag clear, interrupts enabled, `RSP` 16-byte aligned before
   the `call`, on the BSP's stack (16 KB; a component should use under
   4 KB). The blob returns with `ret` with `RSP` as it found it; it may
   clobber every other register; `RAX` on return is ignored. It must be
   **position-independent** (`default rel`, no absolute addresses — its
   load address differs per build and is told to it only by line 12), may
   keep writable data inside itself (the region is ordinary RAM), may use
   port I/O (the clock reads the CMOS RTC at `0x70`/`0x71` — the owner's
   decision 2), and must touch nothing else the core owns: no serial, no
   framebuffer except through the table, no keyboard ports, no notebook,
   no network. **Esc is the convention**: when `poll_key` returns `0x1B`
   the component returns promptly. A component that never returns is a
   hang the rehearsal is there to catch (the no-return case on the real
   machine is a carried caveat this ring: there is no watchdog).
6. **The service table ABI** (GERMLINE.md, "The service table"): at `RDI`,
   `u32` ABI version `1`; `u32` table size `40`; then four `u64` function
   addresses. Calls: arguments in `RDI`, `RSI`, `RDX`, `RCX`; result in
   `RAX`; the service preserves `RBX`, `RBP`, `RSP`, `R12`–`R15` and may
   clobber `RAX`, `RCX`, `RDX`, `RSI`, `RDI`, `R8`–`R11`; no stack
   alignment requirement; `DF` clear on both sides.
   - **`+8 draw_text(row, col, ptr, len)`** — draws `len` bytes from `ptr`
     at cell (`row`, `col`), each advancing one column, from the shared
     font in the two console colours; stops at the right edge; a row or
     column outside the console draws nothing; a byte outside `0x20`–`0x7E`
     draws as a space. **Pixels only**: the console shadow is not touched,
     which is what lets the core restore the conversation on exit.
   - **`+16 console_size()`** — `RAX` = `cols | rows << 32`.
   - **`+24 poll_key()`** — `RAX` = the next key as an ASCII byte (with
     Shift applied: printables, `13` Enter, `8` Backspace, **`0x1B` Esc**),
     or `0` if none is waiting. Keys taken by a component are **not echoed
     to serial** and never reach the prompt.
   - **`+32 ticks_ms()`** — `RAX` = milliseconds since boot, `u64`,
     monotonic, from the TSC calibrated once at boot against the PIT (the
     environment table: about 3.0 M ticks a millisecond here).
   Exactly the four the spec names; a component that wants a clear screen
   draws spaces.
7. **What the screen does around a component.** On a valid component
   frame: the indicator is stopped, the cursor erased, **the framebuffer
   cleared to the background** (the shadow kept), the component called;
   on return, **the whole console is re-rendered from the shadow**
   (`console_scroll`'s re-render loop, factored out as `console_redraw`),
   any keys still in the ring are discarded (`cli`, tail = head — the
   Stage 4 rule), and the prompt is drawn on the fresh line. The
   conversation comes back exactly as it was, with a new prompt under the
   request. The screen has one owner throughout: the component draws only
   through `draw_text`, on the BSP, in the main loop's stead.
8. **The keyboard, refactored not changed.** The translation in
   `main_loop` (E0 swallow, Shift state, the two tables) becomes
   **`kbd_next`** — returns `AL` = a translated byte or 0 with the ring
   empty — called by the main loop and by `poll_key`. Scancode `01` maps to
   `0x1B` in both tables; the main loop ignores `0x1B` (Esc at the prompt
   does nothing). The handler is untouched: it still only buffers.
9. **The broker** — `broker/germline.py`, item 3, frozen at item 8. One
   file, standard library only, importing the frozen framing from
   `broker.py`; binds `127.0.0.1` only, one connection at a time, prints
   `listening on 127.0.0.1:<port>` once bound (the Stage 4 contract, so the
   harness waits for exactly that). Per connection: one request frame; if
   its first byte is not `0x01` it is a **question** and takes Stage 4's
   path unchanged (`mock_answer` in `--mock`, `claude_backend.ask` in real
   mode, `to_wire`, one response frame); if it is `0x01` it is a **grow**
   request and runs the pipeline: **(1) generate** — the backend returns a
   candidate blob or a refusal text (`--mock`: the canned table of decision
   12; real: `claude_backend.grow`); **(2) rehearse** — `rehearse.py`
   (decision 10) boots the twin and judges the candidate; on failure, and
   if tries remain (**`--tries`, default 2**), the backend is asked again
   with the failure named; **(3) cache** — a passing blob is written to the
   germline (decision 11); **(4) deliver** — the component frame. A
   candidate that fails every try becomes the refusal **`rehearsal failed:
   <reason>`** with the reason one of the fixed phrases of decision 10;
   a backend refusal is delivered as its text. A repeat request is served
   from the germline **before** step 1 — the backend is never invoked. The
   **record** (`--record`, one JSON line per connection, appended when it
   ends) is Stage 4's for a question and, for a grow, carries `kind:
   "grow"`, `request` (raw hex, as Stage 4), `text`, `key`, `source`
   (`germline` | `generated` | `refused`), `generation_calls` (the
   backend's running call count for this broker process — **the mock
   counts calls**, and so does the real path), `rehearsals` (a list of
   `pass` / `fail: <phrase>`), `answer_kind` (`component` | `refusal`),
   `answer_sha256` (of the whole response frame) and `answer` (the refusal
   text, or null). `--germline <dir>` names the cache (default `germline/`
   at the repo root, gitignored); `--image <esp.img>` names the twin's boot
   image for the rehearsal (default `stage5/out/esp.img`); `--port`,
   `--timeout` as Stage 4. In `--mock` mode the generation backend is the
   canned table and nothing outside the repo is ever called; the rehearsal
   still boots a real QEMU, because the rehearsal is what test 4 judges.
10. **The rehearsal** — `broker/rehearse.py`, item 3, frozen at item 8: the
    twin driver and the generic criteria of the spec. `rehearse(blob,
    image, workdir, port)` returns `(passed, phrase, log)`. It starts a
    one-shot listener on a private port (**9998** in the gate and by
    default; it must be free — the harness checks), boots the image
    headless at `-smp 2` with a fresh 16 MB notebook image and the cage of
    UMBILICAL.md whose `guestfwd` delivers to that port, the monitor on
    stdio, serial to a file, everything under `stage5/out/rehearsal/`;
    waits for `S5: keyboard ready` (60 s); types `! rehearsal` and Enter
    via `sendkey`; the listener answers the request with the candidate's
    component frame and closes; the driver waits for the listener to
    report the delivery (30 s), then 3 s more; takes **screendump B** (the
    component running); sends `esc`; waits 2 s; types `after` and Enter;
    waits 2 s; **screendump C** (the prompt back); quits. The criteria,
    judged in this order, each a fixed phrase that names the failure:
    **`the twin did not boot`** (no ready line, or not exactly the
    thirteen `S5:` lines); **`the component was not delivered`** (the
    listener never saw the request or could not send); **`the twin
    reported an error`** (any `ERR:` in the serial capture — an exception,
    a halt); **`the component did not run`** (the row `> ! rehearsal`,
    rendered from the shared font, is still on screen in B — the loader
    never cleared the console and took over); **`the component drew
    nothing`** (B is pure background); **`no live prompt after esc`** (the
    row `> ! rehearsal` is not back on screen in C, the notebook image does
    not parse to exactly `["after"]`, or the serial echo after ready is not
    exactly `! rehearsal\r\nafter\r\n`); **`the twin timed out`** (the whole
    run over 90 s). `passed` is true only if none fired. The `ud2` blob of
    decision 12 fails at the third phrase: the loader clears and calls,
    the fault is immediate, and the IDT's `ERR: exception 6` is on serial
    before anything else is judged. The log is the criteria's verdicts,
    the thirteen lines and the timing, and it is what the provenance
    record keeps. A rehearsal never touches the germline;
    `stage5/out/rehearsal/` is scratch, wiped per run.
11. **The germline** (GERMLINE.md, "The germline"): a directory per
    proven component under the cache root, named by the **key** = the
    first 16 hex digits of SHA-256 over `<normalised request>|abi1|<machine>`,
    where the normalised request is the text lowercased, whitespace runs
    collapsed to one space, stripped; and the **machine** this ring is the
    twin's identity string **`qemu-q35-ovmf`** — the machine the user faces
    and the twin are the same guest image (the spec), so one key serves
    both; at Stage 7 the string becomes the scanned hardware. Each directory
    holds **`component.bin`** (the blob), **`provenance.json`** (`request`,
    `normalised`, `abi`, `machine`, `date` ISO-8601 UTC, `model` — the
    backend's name: `mock`, or `claude -p <cli version>` plus `--model` if
    given, `sha256` of the blob, `size`, `tries`, `rehearsal` — the passing
    verdict's phrases and timing) and **`rehearsal.log`**. Serving from
    the germline re-reads `component.bin` and checks its `sha256` against
    the record; a mismatch is treated as a miss.
12. **The mock's canned table for grows**, frozen with `germline.py`:
    **`test component`** → the bytes of `stage5/component.bin`; **`big`**
    → the bytes of `stage5/component.bin` padded with zeros to **exactly
    1,048,576 bytes**, the cap (Cowork's amendment: the padding sits after
    the code and never executes, so it rehearses, runs and returns exactly
    like the test component — and proves the 1 MB boundary, the full
    `32 + 1,048,576` byte frame streamed into the guest, before test 5);
    **`fault`** → the two bytes `0f 0b` (`ud2`: an invalid-opcode exception the
    moment it runs, so the IDT prints `ERR: exception 6` and halts — the
    spec's "deliberately faulting blob"); anything else → the refusal
    **`mock: no canned component for: <text>`** with no candidate and no
    rehearsal. Every lookup counts as a generation call, so the checker
    can state the exact count after each line.
13. **The real generation backend** — `claude_backend.grow(request,
    failure, timeout)`, item 3, **not frozen** (Stage 4's boundary): a
    `claude -p` call with a brief that carries GERMLINE.md's entry contract
    and service-table sections verbatim and asks for **NASM source** for a
    flat binary (`bits 64`, `default rel`, no `org`, entry at the first
    byte, position-independent, the ABI's register rules, at most 1 MB) —
    nothing about clocks; the source is assembled on the host with `nasm
    -f bin`; an assembly error is fed back for up to three rounds inside
    the one generation call; the result is the blob, or a refusal naming
    the last error. `failure`, when the pipeline retries after a
    rehearsal, is the phrase and the twin's `ERR:` line if any. The brief's
    quality is the backend's own affair, as the spec says: the gate proves
    the pipeline, the oracle proves the clock.
14. **The test component** — `stage5/component.asm` (hand-written, item 2)
    and its assembled `stage5/component.bin`, **both frozen** at item 8,
    the binary gitignore-excepted like the font, and the checker's
    self-check that `nasm -f bin` on the source reproduces the binary
    byte for byte. What it does, through the table only: draws at row 2
    column 4 **`germline test component`**; at row 4 column 4 **`console
    <cols>x<rows>`** from `console_size` (its own decimal conversion); at
    row 6 column 4 **`ticks ok`** once `ticks_ms` has advanced (or `ticks
    stuck` after a bounded spin); at row 8 column 4 **`key: -`**, replaced
    by `key: <ch>` for each printable key `poll_key` returns; at row 10
    column 4 **`esc returns to the prompt`**; then polls until Esc and
    returns. Under 512 bytes. The checker renders every one of those
    strips from the font at those exact cells — the "known picture".
15. **The freeze boundary.** Frozen at item 8: `stage5/test.sh`,
    `stage5/checkgermline.py`, `stage5/GERMLINE.md`,
    `stage5/component.asm`, `stage5/component.bin`, `broker/germline.py`,
    `broker/rehearse.py` — the last two because the mock table, the
    record, the cache and the rehearsal verdicts are what tests 3 and 4
    judge by (a bent rehearsal could pass a faulting blob). Not frozen:
    `stage5/mkimage.sh` (the recipe), `stage5/stage5.asm` (the thing under
    test), `broker/claude_backend.py` (the one function the gate never
    runs). `broker/broker.py` and everything frozen before stand
    untouched. `germline/` is gitignored.
16. **The harness** — `stage5/test.sh` (Stage 4's shape): refuses to run
    while anything listens on **9999 or 9998**; the cage strings with
    **`mac=52:54:00:a1:05:01`**; builds; test 1; test 2 (`serial_check 8`,
    thirteen lines); test 3 (`checkgermline.py --grow 2` and `--grow 8`);
    test 4 (`--germline`); its own cage self-assertion as Stage 4's.
    **`stage5/checkgermline.py`** owns every booted run bar test 2's, on
    `checkumbilical.py`'s driver (mock lifecycle, `drive` with steps,
    record-driven waits, the font renderer, `check_screen`, the notebook
    parser), extended with GERMLINE.md's parser, a `wait_record` that can
    wait on a *field* (a grow entry with `source` set), key names for `!`
    (`shift-1`) and Esc (`esc`), and a `screen_differs` check. It wipes
    `stage5/out/germline/` before each mode, so counts are deterministic.
    - **`--grow <smp>`** (test 3): mock up with the gate's germline dir;
      fresh disk; boot; type `before` ⏎; `? ping` ⏎, wait for record 1;
      **`! test component`** ⏎, wait for the grow entry (bounded 150 s —
      it rehearses), settle 3 s; type `k`, settle 1 s; **screendump A**;
      `esc`, settle 2 s; `after` ⏎, settle; **screendump B**; quit. Assert:
      the thirteen boot lines with the MAC and line 12's shape; the echo
      after ready **exactly** `before\r\n? ping\r\n! test component\r\nafter\r\n`
      (the `k` and Esc never reach serial); the record holds exactly two
      connections — `ping` answered `pong`, and a grow whose raw bytes are
      the frame of GERMLINE.md's worked example for `test component`, with
      `source: generated`, `generation_calls: 1`, `rehearsals: ["pass"]`,
      `answer_kind: component` and `answer_sha256` equal to the SHA-256 of
      the component frame the checker builds from `stage5/component.bin`;
      the germline holds one entry whose `component.bin` is that file;
      the notebook parses to exactly `["before", "after"]`; **screen A**
      shows the test component's five strips at their cells with `key: k`,
      nothing else but background (two colours only, and every other cell
      blank — the console was cleared); **screen B** shows the rows `>
      before`, `> ? ping`, `pong`, `> ! test component`, `> after` and the
      prompt with the block cursor, consecutive, the conversation restored.
    - **`--germline`** (test 4, at `-smp 8`): the cage argv assertion
      (Stage 4's, port 9999 and now the harness's own rehearsal cage string
      for 9998); mock up, cache wiped; fresh disk; boot; **`! fault`** ⏎,
      wait for its entry (bounded 240 s: two rehearsals), settle; **`! test
      component`** ⏎, wait, settle 3 s, `esc`, settle 2 s; **`! test
      component`** ⏎ again, wait for its entry (bounded 20 s: no
      rehearsal), settle 3 s, `esc`, settle; **`! big`** ⏎, wait for its
      entry (bounded 150 s: one rehearsal, and a 1 MB frame to stream),
      settle 3 s, **screendump A** (the 1 MB component running), `esc`,
      settle 2 s; then the marker cases: `?` ⏎, `?x` ⏎ (wait record), `!`
      ⏎, `!x` ⏎ (wait record), each with a settle; `last` ⏎; **screendump
      B**; quit. Assert: the boot lines; the echo exactly the nine typed
      lines; the record holds in order: grow `fault` (`source: refused`,
      `generation_calls: 2`, `rehearsals: ["fail: the twin reported an
      error", "fail: the twin reported an error"]`, `answer_kind: refusal`,
      `answer: "rehearsal failed: the twin reported an error"`), grow `test
      component` (`generated`, calls **3**, `["pass"]`, component), grow
      `test component` (**`germline`**, calls **still 3**, `rehearsals:
      []`, component, same `answer_sha256`), grow `big` (`generated`, calls
      **4**, `["pass"]`, component, `answer_sha256` equal to the SHA-256 of
      the component frame the checker builds from the padded blob — a
      frame of exactly `4 + 32 + 1,048,576` bytes), question `x` (`mock: no
      canned answer for: x`), grow `x` (`refused`, calls **5**, `rehearsals:
      []`, `answer: "mock: no canned component for: x"`) — and nothing for
      the bare markers, which send nothing; the germline holds exactly
      **two** entries: one whose `component.bin` is byte-identical to
      `stage5/component.bin` with `provenance.json` carrying `request:
      "test component"`, `size: <the file's size>`, and one whose
      `component.bin` is that file padded with zeros to 1,048,576 bytes
      with `request: "big"`, `size: 1048576` — each with `abi: 1`,
      `machine: "qemu-q35-ovmf"`, `model: "mock"`, the matching `sha256`, a
      `date` that parses, a `rehearsal` with the phrases all clear, and a
      `rehearsal.log` holding the thirteen `S5:` lines; the notebook
      parses to exactly `["last"]`; **screen A** shows the test component's
      five strips at their cells with `key: -` and nothing else but
      background — the 1 MB blob ran and drew, its padding never reached;
      **screen B** shows, consecutive: `> ! fault`, `rehearsal failed: the
      twin reported an error`, `> ! test component`, `> ! test component`,
      `> ! big`, `> ?`, `nothing to ask`, `> ?x`, `mock: no canned answer
      for: x`, `> !`, `nothing to grow`, `> !x`, `mock: no canned component
      for: x`, `> last`, the prompt; two colours only.
    The gate's cost: five boots of its own plus six rehearsal boots (two
    in test 3, four in test 4 — `fault` twice, `test component`, `big`),
    about eight minutes. Rehearsals run while the gate's own guest waits
    on the wire — two QEMUs at once, on different ports, in different
    `out/` directories.
17. **The two commands for the oracle** (test 5), from the repo root:
    `python3 broker/germline.py` and the Stage 4 windowed line with
    `stage5/out/esp.img` and `stage5/out/notes.img`. He types `! make me a
    clock`; the indicator turns while Claude writes and the twin rehearses;
    a clock ticks; Esc returns the prompt; `! make me a clock` again comes
    from `germline/` at once. His word closes the stage.
18. **The prose the hook will dislike.** The new frozen basenames
    (`GERMLINE.md`, `germline.py`, `rehearse.py`, `component.asm`,
    `component.bin`, `checkgermline.py`) join the prose rule; commit
    messages go in by `-F` from a file written with the Write tool, as
    before. `germline/` the directory is not a frozen name.

---

## Conventions for every item

- One commit per numbered item; `/clear` between items.
- Each item states **which tests are expected green at its commit**. Items
  0–8 commit with every Stage 5 test failing **by design** — there is no
  `stage5.asm` yet. From item 9 the stated tests must be green before the
  commit.
- **`./stage0/test.sh` … `./stage4/test.sh` stay green throughout** — run
  as regressions before every commit (Stage 4's needs 9999 free, as does
  Stage 5's; the two gates never run at once).
- `HANDOVER.md` is updated as we go, with a final pass at item 13.
- Every new fault class earns a CLAUDE.md gotcha line and a regression check.
- Temporary probes are never committed, and never undone with `git checkout
  --`: copy aside, restore from the copy.
- **The scope guard** governs items 10–13: two honest attempts at any one
  obstacle — a real diagnosis from the serial log or the rehearsal log,
  not a re-run — then stop, record the exact state in `HANDOVER.md`,
  commit that, and wait for Wajira.
- **Everything runs inside QEMU with the caged network.** The only disks
  are files under `stage5/out/` (the gate's, and the rehearsal's under
  `stage5/out/rehearsal/`), created fresh by the harness or the broker.
  Both brokers bind only `127.0.0.1`. Nothing outside the repo is written,
  bar scratch files in the session temp directory. **No real Claude call
  is made by this session:** the mock is the only broker the gate ever
  talks to, `claude_backend.grow` is never run here, and test 5 is
  Wajira's.

---

# Part 1 — the wire, the test component, the broker, and the acceptance machinery, written before the code

## Item 0 — this plan, committed

Copy this file verbatim to `stage5/plan.md` and commit it. The first act
after the gate opens, before any other file changes.

*Expected at commit:* no Stage 5 tests exist yet. Stages 0–4 green.

## Item 1 — `stage5/GERMLINE.md`: the new wire, byte-exact

Decisions 2–7 and 11 as one document, the NOTEBOOK.md / UMBILICAL.md
precedent: implemented by the assembler and the test component, parsed by
the broker, the rehearsal and the checker. Sections: what it adds to
UMBILICAL.md and what it leaves alone; what is a question, what is a
request (the forgiving parse, the two empty-body lines); the grow request
frame; the grow response frame — refusal and component, offsets and ranges
in a table; the deadline; the component region and line 12; the entry
contract; the service table (offsets, calling convention, the four
services, each precisely); what the screen does around a component; the
refusal phrases (`rehearsal failed: …`, the seven phrases, `bad component
frame`, `no answer from the broker` by reference); the germline (key,
normalisation, machine string, directory contents, provenance fields); the
mock's grow table; the record's grow fields; the worked-example bytes of
decision 3; and **"Parsing it cold, in Python"** — `grow_request(text)`,
`refusal_frame(text)`, `component_frame(blob)`, `parse_response(frame)`,
`normalise(text)`, `germline_key(text, machine)` — the exact functions the
three Python readers import or reproduce.

*Expected at commit:* no Stage 5 tests yet. Stages 0–4 green.

## Item 2 — `stage5/component.asm` and `stage5/component.bin`: the test component

Decision 14: hand-written NASM, `bits 64`, `default rel`, the entry at its
first byte, `RDI` kept in `R12` for the table, a `putdec`, the five strips,
the ticks check (a bounded spin on `ticks_ms` — 2 M calls at most — then
`ticks ok` or `ticks stuck`), the key loop (`0x1B` returns; a printable
redraws `key: <ch>`; others ignored). Assembled with `nasm -f bin
stage5/component.asm -o stage5/component.bin`; `.gitignore` gains
`!stage5/component.bin` (the font precedent); its SHA-256 and size go into
the commit message and into `GERMLINE.md`'s germline example.

Proven on the host alone: a fifteen-line scratch Python "core" under the
session temp directory disassembles nothing and runs nothing — it only
checks the blob's size, that it begins with a `push`/`mov` and contains the
five strings, and that `parse_response(component_frame(blob))` round-trips.
(The blob first *runs* at item 12, in the guest; that is the point of
writing it now.)

*Expected at commit:* no Stage 5 tests yet. Stages 0–4 green.

## Item 3 — `broker/germline.py`, `broker/rehearse.py`, and `claude_backend.grow`

Decisions 9–13 in code. `germline.py`: the imports from the frozen
`broker.py`; `argparse` (`--mock`, `--port`, `--record`, `--timeout`,
`--germline`, `--image`, `--tries`, `--rehearsal-port`); the listener and
the `listening` line; `handle` — read one frame, dispatch on the marker
byte; `answer_question` (Stage 4's path); `grow` (the pipeline, the
counter, the record fields); the germline lookup, write and verify;
`mock_generate` with the canned table (reads `stage5/component.bin` at
call time). `rehearse.py`: decision 10 whole — the one-shot listener, the
QEMU argv (spelled once, the cage from UMBILICAL.md with the rehearsal
port), the monitor driver (Stage 4's `drive` shape), the screendumps, the
font renderer for the request row (the checker's, carried over), the seven
criteria, the log. `claude_backend.py` gains `grow()` (decision 13)
beside the untouched `ask()`.

Proven on the host alone, no guest, no Claude call, with a scratch client
under the session temp directory against `--mock` on a throwaway port and
`--image` pointing at a file that does not exist yet: a `ping` question
answers `pong` through the imported frame code; a grow `x` returns the
`mock: no canned component for: x` refusal with `generation_calls: 1`; a
grow `test component` runs the pipeline into the rehearsal, which fails
with **`the twin did not boot`** (no image), twice, and the guest-side
answer is the `rehearsal failed: the twin did not boot` refusal — the
retry, the count of 3 and the record's fields all visible in the record
file; a malformed frame closes the connection; the germline directory is
still empty. `normalise` and `germline_key` are exercised on the spec's
own examples.

*Expected at commit:* no Stage 5 tests yet. Stages 0–4 green. No Claude
call.

## Item 4 — `stage5/mkimage.sh`, the `stage5/test.sh` harness, acceptance test 1

`mkimage.sh` (not frozen): Stage 4's, retargeted. `test.sh` (frozen from
item 8): Stage 4's shape plus the double port refusal (9999 and 9998), the
Stage 5 cage strings with the new MAC, the wipe of `stage5/out/germline/`,
and the self-assertion on the cage strings. **Test 1** — the artefact,
Stage 4's criteria on Stage 5's files.

*Expected at commit:* every Stage 5 test fails — there is no `stage5.asm`.
The non-zero exit quoted in the commit message.

## Item 5 — acceptance test 2 (serial, first boot: the thirteen lines)

`serial_check 8` on a fresh disk inside the cage with the MAC, under
`timeout -k 5 60`, exit 124 expected. Exactly thirteen `S5:` messages in
order: Stage 4's checks carried over, **line twelve** per decision 1 (the
address 16 hex digits, non-zero, below `0x100000000`, ≡ 64 mod 4096; the
cap `1048576 bytes`), line thirteen `S5: keyboard ready`. Whole capture
printed on failure.

*Expected at commit:* tests 1–2 fail.

## Item 6 — `stage5/checkgermline.py --grow` (test 3)

Decision 16's first mode: `checkumbilical.py`'s driver carried over with
the thirteen-line pattern table, GERMLINE.md's parser, the field-aware
`wait_record`, the two screendumps, the key names for `!` and Esc, the
cleared-screen assertion (every cell outside the five strips blank), and
the twelve assertions. `test.sh` gains **Test 3**: `--grow 2` and `--grow
8`, both must pass.

*Expected at commit:* tests 1–3 fail.

## Item 7 — `checkgermline.py --germline` (test 4)

Decision 16's second mode: the argv assertions for both cages, the long
scripted run, the record judged entry by entry with the exact
`generation_calls` sequence 2 / 3 / 3 / 4 / 5, the two germline entries
judged against `stage5/component.bin` and its zero-padded 1 MB twin with
the provenance fields, the screendump of the 1 MB component running, the
marker-parse rows, the notebook. `test.sh` gains **Test 4**. All four exist and all
fail; the output goes in the commit message.

*Expected at commit:* tests 1–4 fail.

## Item 8 — freeze the Stage 5 acceptance machinery

`PROTECTED` grows the seven paths of decision 15, and the hook's own
comment says why each is a criterion and why `mkimage.sh`, `stage5.asm`
and `claude_backend.py` are not. `payloads.py` gains the Stage 5 group: the
mutation battery on each new path (`freeze_cases`), the allowances —
running the gate and the checker, `python3 broker/germline.py --mock …`,
`python3 broker/germline.py`, the rehearsal QEMU line with both drives
under `stage5/out/rehearsal/`, `cat stage5/GERMLINE.md`, every operation on `stage5/mkimage.sh`,
`stage5/stage5.asm` and `broker/claude_backend.py`, `ls germline/` and
`rm -rf stage5/out/germline` — and is re-run whole: every earlier case
judged as before, 0 wrong. Immediacy demonstrated live with one denied
call.

**One hole the pre-planning check exposed, closed here:** the hook's
mutation patterns know redirects, `sed -i`, `tee`, `mv`/`cp`/`rm`, `git
checkout` and interpreter scripts — but not an assembler's `-o`. `nasm -f
bin stage5/component.asm -o stage5/component.bin` was **allowed** when
run against the hook today, and with `component.bin` frozen that is a
side door. Item 8 adds one mutation pattern, `-o <frozen path>` (any tool
writing its output there), with its payload cases, so the frozen binary
can only be rebuilt by the owner's decision. The checker's self-check
assembles the source to `stage5/out/` and compares, never over the
frozen file.

*Expected at commit:* tests 1–4 still fail; the payload table 0 wrong.

---

*Everything above is written before any implementation code exists.
Everything below is the code.*

---

# Part 2 — the implementation, in the spec's order

## Item 9 — `stage5/stage5.asm`: Stage 4's proven body, `S4` becomes `S5`

Start from `stage4/stage4.asm` whole — nothing removed. Every `S4:` becomes
`S5:`; the header comment is rewritten; the font path stays
`stage2/font8x8.bin`.

*Green at commit:* **test 1.** Tests 2–4 red. Stages 0–4 green.

## Item 10 — the region, the ticks, the keyboard, and line twelve

Decisions 1, 4, 6 and 8: `comp_region` in BSS before the page tables; the
TSC calibration at boot (`rdtsc` around one `pit_wait(PIT_10MS)`, with
interrupts off, before the console; `tsc_per_ms` and `tsc_boot` in BSS);
`kbd_next` factored out of `main_loop`, which now calls it; `0x1B` in both
tables, ignored at the prompt; **line twelve**.

Verified with a **temporary, uncommitted probe** that prints `tsc_per_ms`
and, after ready, one `ticks_ms` value a second apart over serial (expected
about 1000 apart) — then removed, copy-aside.

*Green at commit:* **tests 1 and 2** — thirteen lines. Tests 3–4 red.

## Item 11 — the marker parse and the third kind of line

Decisions 2 and 3 in the guest, and deviation 2: `parse_marker` on Enter
(leading spaces, the marker, the trimmed body); `nothing to ask` / `nothing
to grow`; `ask_question` takes the body by pointer and length; `umbilical_ask`
generalised with **`rx_dst`, `rx_max` and the deadline as parameters**
(`tcp_input`'s copy and `tcp_recv_response`'s bound read them; a question
passes `rx_stream`, 4+4096, 150 s; a request passes `comp_region + 28`,
4+32+1 MB, 600 s); `grow_request` builds the `0x01` frame, asks, and on a
refusal frame draws the text like an answer, on a component frame validates
it (decision 3) — and, this item only, draws **`bad component frame`** for
every valid frame too, since there is no loader yet — on no answer draws the
no-answer line.

Verified with a **temporary, uncommitted probe**, `germline.py --mock`
started by hand: `!x` draws the mock's refusal; `? ping` still draws `pong`;
`?` and `!` draw their two lines; `! test component` drives a full rehearsal
(which **fails** with `the component did not run` — the twin at this item
has no loader either, so the request row is still on its screen — proving
the rehearsal's failure path end to end from the guest's chair), and the
refusal `rehearsal failed: the component did not run` reaches the screen.
Then removed, copy-aside.

*Green at commit:* tests 1–2. Tests 3–4 red.

## Item 12 — the loader and the service table

Decisions 5, 6 and 7: the service table in `.data` (its entries filled at
boot with RIP-relative `lea`s — no absolute addresses); `svc_draw_text`,
`svc_console_size`, `svc_poll_key` (on `kbd_next`), `svc_ticks_ms`;
`console_redraw` factored out of `console_scroll`; `run_component` — stop
the indicator, erase the cursor, clear the framebuffer, `call` with `RDI`
= the table, on return redraw, discard the ring, newline if needed, prompt.
`grow_request`'s valid-frame path now runs the component.

Verified first by hand, `germline.py --mock` by hand: `! test component`
rehearses, passes, is cached, runs — the five strips on screen, `k` shows,
Esc restores the conversation; a second `! test component` comes from the
germline at once; `! fault` is refused after two rehearsals with the twin's
`ERR: exception 6` in the rehearsal log; `! big` streams the full
`4 + 32 + 1,048,576` byte frame to `comp_region + 0x100040`, rehearses,
runs and returns like the test component.

*Green at commit:* **all four automated tests** — tests 3 and 4 close here,
at `-smp 2` and `-smp 8`. Full `./stage5/test.sh` output in the commit
message. Stages 0–4 green.

## Item 13 — HANDOVER, gotchas, and the two commands

- `HANDOVER.md` to the green-pending-oracle state: what was built, the
  region address on this build, tests 1–4 green with output, test 5 pending
  Wajira, the two commands, caveats carried forward (everything Stage 4
  carried; one component at a time, cooperatively run, no watchdog for a
  component that never returns; the machine string is the twin's this ring;
  the rehearsal proves safe not correct; the generation brief's quality is
  the backend's own; no component persistence; the 600 s grow deadline;
  `germline/` is per machine and gitignored).
- `CLAUDE.md` gotchas grown with whatever actually bit — candidates
  already visible: *EFER.NXE is on under OVMF, but our own tables carry no
  NX bits, so BSS executes — a region needs no mapping change*; *the
  marker byte on the wire is non-printable on purpose*; *two QEMUs at once
  need two ports and two `out/` directories*; *a monitor `sendkey` while a
  component polls is consumed silently — the serial echo contract still
  holds because the component, not the prompt, took the key*.
- `README.md`'s running section gains Stage 5's two commands.
- Print the two commands for Wajira.

*Green at commit:* all four automated tests, plus Stages 0–4.

---

## Verification

- **Automated:** `./stage5/test.sh` from the repo root — refuses to start
  if anything listens on 9999 or 9998; builds; tests 1–4 (serial at `-smp
  8`; the growth at `-smp 2` and `-smp 8` with the mock, each with one
  rehearsal; the germline run at `-smp 8` with four rehearsals, the last
  streaming a frame of exactly the cap). About eight minutes. Exit 0 only if all pass. Run before every commit from item
  9 on.
- **Regression:** Stages 0–4's `test.sh` green before every commit.
- **The hook:** `python3 .claude/hooks/payloads.py` at item 8 — every case
  from every stage, 0 wrong; immediacy demonstrated live.
- **The probes:** items 3 (host-only), 10, 11 and 12 each state their
  expected output; item 11's rehearsal failure and item 12's rehearsal pass
  are both confirmed from the record file and the rehearsal log on the host.
- **Manual (test 5):** Wajira, in two terminals at the repo root. The real
  broker:

```
python3 broker/germline.py
```

  and the grown machine, windowed:

```
qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd \
  -drive format=raw,file=stage5/out/esp.img \
  -drive format=raw,file=stage5/out/notes.img,if=virtio \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' \
  -device virtio-net-pci,netdev=n0 -serial stdio
```

  He types `! make me a clock`, watches the indicator turn while Claude
  writes and the twin rehearses, and a clock with the right time ticks on
  GermOS's screen; Esc returns the prompt; asking again comes from
  `germline/`. His word closes the stage.

## Safety

Everything runs inside QEMU. Firmware plus exactly two drives per guest,
raw files under `stage5/out/` (the rehearsal's under
`stage5/out/rehearsal/`), created by the harness or the broker; the
bodyguard is unchanged and still denies every other kind of disk before
the shell sees it. The network is slirp with `restrict=on` and one
`guestfwd` in every QEMU line, the rehearsal's included; the brokers bind
`127.0.0.1` only. The automated gate talks only to the mock, never to
Claude, and refuses to run if anything else holds either port. A grown
component runs at ring 0 with the whole machine in reach — that is the
thesis, and the rehearsal in the twin is the mitigation the foundation
prescribes; it proves *safe* (boots, runs, no fault, returns, the prompt
lives), not *correct*. This session makes no Claude call and never runs
`claude_backend.grow`. The only outward connection in the whole design is
`claude -p`'s own HTTPS from the real broker, started by Wajira's hand at
test 5. Every existing frozen file is untouched: `git diff --stat` against
`beef02e` on the `PROTECTED` paths of Stages 0–4 is empty at every commit.

## Risks, and what absorbs them

| Risk | Absorbed by |
|---|---|
| The region cannot be executed or does not load | measured before planning: the blob ran from BSS with NXE on; line 12 reports where it landed |
| A 1 MB frame stalls the 4096-byte window stack, or the cap is off by one | in-order receive with immediate ACKs already streams; `rx_dst`/`rx_max` are the only change; the item 11 probe receives the real frame before any loader exists; test 4's `big` streams a frame of exactly the cap into the guest and runs it, so the boundary is proven by the gate, not at test 5 |
| The component wrecks the console, the ring or the stack | pixels-only `draw_text`, the shadow redraw, the ring discard, the 16 KB stack and the entry contract's rules; the rehearsal's `after` note proves the prompt lives |
| A generated blob hangs the real machine | the rehearsal's 90 s bound catches it in the twin first; the no-watchdog case is a recorded caveat |
| The rehearsal is bent to pass | `rehearse.py` frozen; test 4's `ud2` blob must fail with the fixed phrase; the checker reads the rehearsal log |
| The gate spends a token or reaches Claude | the double port refusal; the mock's generation table; `grow()` imported only outside `--mock`; the mock counts and the checker demands the counts |
| Two QEMUs collide | different ports (9999 / 9998), different `out/` directories, different MACs; the harness checks both ports free before starting |
| `?` without a space again goes to the notebook | decision 2, and test 4's four marker rows judged pixel by pixel |
| The clock is wrong at test 5 | the gate proves the pipeline; the brief is unfrozen and fixable there (Stage 4's `--bare` lesson); a rehearsal failure is a named phrase, and the record on the host says which |
| A 3 a.m. improvisation around the loader | the scope guard, and the whole of Part 1 existing before Part 2 |
