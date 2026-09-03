# Stage 6 — Growth · spec

**Approved by the owner, 1 September 2026**, all recommendations taken (decisions 1–8 below). Implementation: Fable 5.1 at high effort.

**Goal (foundation §7):** a simple compositor and GUI, more devices, and the store-of-plans prototype: install an application from a plan file. The compositor ships with the machine's obs chart from day one — border stripes reborn as truthful, live telemetry — and the DE takes its shape from the human-factors constitution (foundation §5), not from existing desktops. **Proves the machine can grow a face and a store.**

**The policy gate, re-checked at this gate as the foundation requires (1 September 2026):** Anthropic's help centre still says the June 2026 credit-pool change is **paused** — "nothing has changed: Claude Agent SDK, `claude -p`, and third-party app usage still draw from your subscription's usage limits", and "when we have an update, we'll share it before anything takes effect". So the broker keeps shelling out to `claude -p`, no API keys anywhere, and the backend stays one swappable unfrozen function. The germline remains the mitigation if the policy ever tightens. Re-check at the Stage 7 gate.

## Why this stage is three rings

Stage 6 is bigger than any stage before it. Split into three rings, each with its own plan gate, its own frozen tests, its own done-when you can see, and its own fresh CC session. Every ring obeys the stage rules: small enough to finish, ends with something visible, gated before the next grows.

| Ring | Name | What it proves | Done when |
|---|---|---|---|
| 6a | **The glass** | The screen has one owner, the machine tells the truth about itself, and the conversation stays alive while an app runs | `! make me a clock` ticks in its own panel while you type a note beside it, and the obs strip shows real numbers |
| 6b | **The store of plans** | An application can be installed from a plan, rehearsed against the plan's own tests, kept on the machine, and launched after a reboot with the broker gone | `! install calculator` from `plans/calculator.md` gives a working calculator; reboot with no broker; `! calculator` still runs it |
| 6c | **The pointer** | A device arrives only because the constitution demands it | Click a choice on the choices row and it happens; pointer input-to-photon is a number on the obs strip |

The recommended order is glass → plans → pointer. The store of plans is the thesis item; the pointer is a device, and it is the one ring that can slip without weakening the stage. (Decision 1.)

## The constitution, applied

Every design choice below is traced to one clause of foundation §5. Nothing is borrowed from an existing desktop.

- **One owner of the screen.** A dedicated core — the **glass core** — does nothing but composite and draw the obs strip. After it starts, the BSP never writes a pixel again. (The concurrency doctrine's one absolute law.)
- **The human is the highest-priority device.** The glass core is the interactive path's reserved core, the first of the foundation's mixed-criticality promise. This ring it is the first available AP; at Stage 7 it is chosen by topology.
- **Born instrumented.** Every counter on the obs strip is incremented by the thing doing the work, in one shared **obs page**, and drawn by the glass core. Nothing on the strip is estimated.
- **Few choices at a time (Hick).** A **choices row** on the bottom edge shows what you can do right now — never more than five things — and nothing else. At the prompt it shows the markers and the installed apps. While an app runs it shows the app's declared choices and Esc.
- **Targets on edges (Fitts).** The obs strip is the top edge; the choices row is the bottom edge. Both are the width of the screen. When the pointer arrives (6c) the choices row is where it clicks.
- **No hidden modes.** The current mode is always named in the obs strip — `prompt`, `asking`, `growing`, `installing`, `running <app>` — so the state of the machine is never a guess. Stage 4's first user typed `?` without a space and the machine silently did nothing; the mode word and the choices row are the structural cure.
- **Recognition over recall.** The markers are on screen. Installed apps are named on screen. You never have to remember a command.
- **Undo, not are-you-sure.** Nothing in Stage 6 asks for confirmation. Esc always closes an app and the conversation comes back exactly as it was. Re-installing replaces without asking; the previous build is kept on the home image until the next install replaces it (one step of undo, `! undo install` — 6b).
- **Attention is the scarcest resource.** Nothing pops up. The outcome of a grow or an install is one line in the conversation, where you were already looking. Asynchronous events only ever change the strip or add a line.
- **Time-to-done and error rate, never engagement.** The obs page records, for every request, the time from Enter to the prompt coming back, and counts the errors the machine shows (`nothing to grow`, `bad component frame`, refusals). These are the measurements an N-of-1 trial needs. The trials themselves are a later ring (decision 5).
- **The conversation is the root.** The DE grows panels out of the conversation: the conversation is one panel, a running app is another. There is no grid of applications and no desktop.

## Ring 6a — the glass

**The screen.** The mode is the display's preferred one when it states it, else the highest (decision 8) — 1440x1440 here, 90x90 cells. Four regions on the same 16x16-cell grid the console uses, all sizes measured from the mode at boot, never baked in. On this machine: the **obs strip**, top, two rows; the **choices row**, bottom, two rows; between them the **conversation panel**, left, half the columns, the Stage 5 console unchanged in behaviour; and the **app panel**, right, the remaining columns. With no app running the app panel is background. (Decision 2.)

**Surfaces and the compositor.** Each region is a **surface**: a back buffer in ordinary RAM, written by whoever owns the region, with a dirty rectangle. The glass core loops for ever: for each dirty surface, copy the dirty cells to the uncached framebuffer, clear the flag, count the frame and its microseconds; then redraw the obs strip from the obs page; then pause until the next frame slot (a fixed cadence from the TSC — 60 frames a second — the glass core needs no timer interrupt because it has nothing else to do). Producer and consumer never share a lock: x86 stores are seen in order, there is no compiler to reorder anything, and a torn cell lasts one frame. A single-core machine is a named `ERR:` — this ring wants two cores or more, and the gate runs at `-smp 2` and `-smp 8` as ever. The APs Stage 1 woke and parked supply the glass core; the rest stay parked.

**The obs strip, day one.** Uptime; the mode word; the glass core's APIC id; frames drawn and the last and worst frame time in ms; **input-to-photon** — the time from the keyboard interrupt stamping a key to the frame that painted its echo reaching the framebuffer, last and worst; keys buffered, high-water; notes on disk and disk requests with their total wait; wire connections, bytes in and out, time spent waiting on the broker; grows generated and grows served from the germline; the running app's name and its last and worst step time; errors shown. Two rows, drawn from the shared font in the two console colours, labels short. Every number is a counter or a stamp in the obs page. The harness checks the strip's text by rendering the font, exactly as every pixel test before it.

**ABI 2 — an app is four callbacks, not a loop.** Stage 5's component took the whole screen and the whole processor until Esc. Stage 6's takes a panel and a turn. The blob's first bytes are a small table: `init(services)`, `step()`, `key(byte)`, `exit()`. The BSP's main loop calls `step` once per pass and `key` for each key while the app has focus; the conversation keeps running in between, so you can type a note while the clock ticks. A `step` is expected back within a budget — **50 ms** — and the obs strip shows how long each one took. The service table becomes ABI 2: `draw_text` draws into the app's own panel (row and column relative to the panel), plus `panel_size`, `ticks_ms`, and `fill(row, col, rows, cols, colour)` so an app can clear or block-colour its panel without spelling spaces. No `poll_key` — keys arrive by callback. Focus: a running app has the keys except Esc; Esc calls `exit` and hands focus back to the prompt. (Decision 3.)

**The wire — one new frozen document, `stage6/GLASS.md`.** The grow request is Stage 5's, byte for byte. The response gains **kind `0x02`**, the ABI 2 frame: a header of 96 bytes — kind, ABI `2`, blob length, a 32-byte name, an `installed` flag (6b), up to four declared choices as key plus a 12-byte label, reserved zeros — then the blob. A Stage 6 guest draws `bad component frame` for kind `0x01`: ABI 1 has no callbacks. `stage5/GERMLINE.md` and `stage4/UMBILICAL.md` are frozen and untouched; the Stage 5 binary and gate keep passing.

**The broker.** New files only: `broker/glass.py` (the ABI 2 pipeline — generate, rehearse, cache, deliver — importing Stage 4's frozen framing; `--mock` with a canned table; frozen) and `broker/twin.py` (the Stage 6 twin driver; frozen). Stage 5's `germline.py` and `rehearse.py` are frozen and stay as they are, serving Stage 5's gate. Germline keys carry `abi2`, so nothing cached at Stage 5 is ever served to a Stage 6 guest. The backend brief in `broker/claude_backend.py` (unfrozen) grows an ABI 2 mode that lifts the callback contract from `GLASS.md` verbatim.

**Rehearsal criteria, ring 6a.** Stage 5's seven, restated for a Stage 6 image (its own line count, its own screens), plus two the glass makes possible: **`the app missed its budget`** — any `step` over 50 ms in the twin, read straight out of the obs page — and **`the app drew outside its panel`** — a pixel in the conversation panel changed while the app ran and nothing was typed. The twin and the harness read the obs page through QEMU's monitor (`xp`), never through serial: the guest prints `S6: obs page 0x<address>` at boot, and the serial echo contract after `keyboard ready` stays exactly Stage 2's. The rehearsal still proves *safe*; 6b adds *correct*.

**Mock table, ring 6a:** `test app` — a hand-written, committed ABI 2 fixture that draws its name, echoes keys into its panel, and declares two choices; `big` — the fixture padded to the cap; `fault` — `ud2` in `init`; `hog` — a `step` that burns 200 ms; `escapee` — draws one cell outside its panel. `fault`, `hog` and `escapee` must be refused.

**Acceptance tests, ring 6a** (written first, frozen, mock only, no token):

| # | Test |
|---|---|
| 1 | **Artefact** — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image (standing). |
| 2 | **Serial** — Stage 5's lines as `S6:`, plus `S6: edid <W>x<H>` (or `S6: edid none`), `S6: obs page 0x<address>` and `S6: glass core <id>` in their slots; the mode line reports the EDID's preferred mode when one was given, and the highest mode when the harness boots without an EDID; found = woken = smp; the echo contract after `keyboard ready` unchanged; at `-smp 1` a named `ERR:` and no glass. |
| 3 | **The glass, mocked** — `! test app` runs in the app panel with its name and choices on the choices row; a note typed while it runs journals and echoes in the conversation panel; a key sent to the app appears in the panel and not on the wire; Esc closes it, the choices row returns to the prompt's, the conversation is intact; `? ping` still answers. At `-smp 2` and `-smp 8`. |
| 4 | **The truth on the strip** — after the harness has typed exactly N keys, asked exactly Q questions, written exactly M notes and grown exactly G apps, the strip says so, byte for byte, and the obs page read through the monitor agrees with the strip; frames strictly increase between two screendumps a second apart; the mode word matches the state at each screendump (`prompt`, `running test app`, and — with the mock told to hold its answer — `growing`); `fault`, `hog` and `escapee` are each refused with the right phrase and never reach the screen; nothing outside the app panel changes while `test app` runs. |
| 5 | **Oracle — Wajira, real broker** — `! make me a clock`: the clock ticks in its panel; he types a note beside it; the strip's numbers move; Esc. **His word closes the ring.** |

## Ring 6b — the store of plans

**A plan is a file.** `plans/<name>.md` in the repository, frozen once approved, in the format `stage6/PLANS.md` defines: the name; **Intent** — the application in plain English, the thing Claude builds from; **Choices** — up to four keys with labels, the ones the choices row shows; **Tests** — the plan's own acceptance tests, in a five-verb language the twin runs: `press <keys>`, `wait <ms>`, `expect "<text>"` (that row is on the panel, rendered from the shared font), `expect not "<text>"`, `expect changed`. This is the magazine type-in listing reborn: readable by anyone, and the review of an app is the review of its plan.

**Install.** `! install <name>` goes to the broker like any grow (no new marker — Hick). The broker reads `plans/<name>.md`, generates from the intent with the plan's own tests in the brief, rehearses in the twin **against the plan's tests** on top of ring 6a's safety criteria — this is the per-request rehearsal Stage 5 deferred here — caches the proven build in the germline keyed by the plan's hash, and delivers it with the `installed` flag set. The guest writes it to the **home image** and runs it. A refused install says which test failed, in the plan's own words.

**The home image.** A second raw disk under `stage6/out/`, `home.img`, a second virtio-blk device (the driver is already per-device since Stage 4), format frozen in `stage6/HOME.md`: a header, a table of apps (name, size, SHA-256, sectors, the previous build's sectors for undo), the blobs. The notebook and `stage3/NOTEBOOK.md` are untouched. `S6: home <N> apps` joins the serial lines. (Decision 4.)

**Launch without the broker.** A `!` line whose body is exactly an installed app's name launches it from the home image with nothing on the wire. Anything else still goes to the broker. The choices row names the installed apps at the prompt, so you never have to remember them. `! undo install <name>` swaps the previous build back — the one undo this ring has, in place of any are-you-sure.

**Mock table, ring 6b:** `install echo` from `plans/echo.md` (a fixture plan: show the last key; tests `press a`, `expect "a"`) with a hand-written correct build; `install liar` from `plans/liar.md`, whose canned build runs safely but draws `b` for `a` — it must fail the plan's tests, proving the tests are judged, not only safety.

**Acceptance tests, ring 6b:**

| # | Test |
|---|---|
| 1 | **Artefact** (standing). |
| 2 | **Serial** — the 6a lines plus `S6: home <N> apps`; a blank home image is formatted on first boot. |
| 3 | **Install, mocked** — `! install echo`: the twin runs the plan's tests and passes; the frame carries the name and the `installed` flag per `GLASS.md`; the app runs in its panel; `home.img` parsed from the host holds exactly that build with its hash; the germline entry's provenance names the plan and its hash. At `-smp 2` and `-smp 8`. |
| 4 | **The store keeps its word** — reboot the same home image **with no broker listening**: `S6: home 1 apps`, `echo` on the choices row, `! echo` runs from disk with nothing on the wire; `! install liar` is refused naming the failed test; re-installing `echo` replaces and `! undo install echo` brings the previous build back, hash-checked from the host. |
| 5 | **Oracle — Wajira, real broker** — `! install calculator` from the plan in the appendix; he does a sum; reboot with the broker off; `! calculator`; the sum still works. **His word closes the ring.** |

## Ring 6c — the pointer

**Why now and not before.** The choices row has targets on an edge. Fitts's law is about pointing at targets; without a pointer it is a keyboard hint. The N-of-1 trials the owner wants (layout A against B, measured in speed and errors) are pointing tasks. So the design demands a pointer at this ring and not earlier.

**The device.** The PS/2 mouse on the i8042's auxiliary port, IRQ12, three-byte packets, interrupt-driven into a ring exactly as the keyboard is. This is also the first time the i8042 is configured rather than inherited — the controller command byte is written to enable the auxiliary port and its interrupt — which retires part of Stage 2's "not reconfigured" debt. `S6: mouse ready` joins the serial lines. QEMU's `-device` for the tablet is deliberately not used: the PS/2 path is what Stage 7 metal will have.

**The cursor and the click.** The glass core draws the cursor — a small arrow, one cell — as the last thing in every frame, from the pointer position the interrupt handler keeps in the obs page; pointer **input-to-photon** joins the strip. A click on a choices-row target does what its key would do. A click anywhere in the app panel calls a new ABI 2 callback `point(row, col, button)`; the ABI version stays 2 with the table one entry longer, and `GLASS.md` is extended by a new frozen section rather than edited (the 6a section stands byte for byte).

**Acceptance tests, ring 6c:**

| # | Test |
|---|---|
| 1 | **Artefact** (standing). |
| 2 | **Serial** — the 6b lines plus `S6: mouse ready`. |
| 3 | **The pointer, driven by the monitor** — `mouse_move` and `mouse_button` through QEMU's monitor: the cursor is at the expected cell in a screendump; a click on the `? ask` target is the same as the key; a click in `test app`'s panel reaches `point` and the app draws the cell it was given; the wire is untouched. At `-smp 2` and `-smp 8`. |
| 4 | **The strip tells the truth about the pointer** — packets counted equal packets sent; the cursor never lags its position by more than one frame across a scripted sweep; pointer input-to-photon is on the strip and below budget. |
| 5 | **Oracle — Wajira** — clicks his way through the choices row and into the calculator. **His word closes the ring and the stage.** |

## Decisions for the owner

1. **The ring order and the split.** Recommend three rings, glass → plans → pointer, one plan gate and one fresh CC session each, with the pointer allowed to slip to the end of the stage if budget bites. The alternative — one big stage — breaks the "small enough to finish" rule and puts three frozen documents behind one gate.
2. **The layout.** Recommend fixed regions this ring: obs strip top, choices row bottom, conversation left, app right, all measured from the mode. The alternative (the conversation takes the whole width until an app appears, then shrinks) is better by Hick but re-wraps the conversation on every launch; it is a later ring's refinement once the trials can measure it.
3. **The glass core and ABI 2.** Recommend both now. The dedicated core is the constitution's one absolute law and is cheap on Stage 1's woken APs; the callback ABI is what lets the conversation stay alive without a scheduler, and it turns the step budget into a rehearsal criterion — the foundation's "feels instant is a number" in miniature. The alternative — compositor on the BSP, apps as loops — keeps single-core simplicity but means the screen has two owners and the conversation freezes while an app runs. A watchdog that preempts a hung `step` is deferred: the rehearsal catches it in the twin first, as at Stage 5.
4. **Where installed apps live.** Recommend a second image, `home.img`, with its own frozen format, over extending the notebook. The notebook's format is frozen and its journal rule (ends at the first invalid record) makes a shared image fragile. Two raw files under `out/` cost nothing and the bodyguard covers both.
5. **N-of-1 trials.** Recommend measuring now and trialling later: every request's time-to-done, every error shown, every input-to-photon is recorded in the obs page from ring 6a, so a later ring can run layout A against B on real numbers. Running a trial this stage would be measuring an interface that has existed for a day.
6. **The first plan.** Recommend the calculator (appendix) as the ring 6b oracle: its tests are exact (`2+3=` shows `5`), it is first on your own trial-app list, and it is the first app to be a plan rather than a request. The clock stays a request.
7. **The implementing model and effort.** The standing rule is Opus at high effort; Fable 5 at high effort has shipped Stages 2–5 with zero review defects. Ring 6a is the project's first real concurrency work and its first frozen document with a pixel budget in it. Recommend Fable at **high** effort. **Decided at approval: Fable 5.1 at high effort implements Stage 6; Cowork specs and reviews on the same.**
8. **The screen mode.** Stage 1's rule — the highest GOP mode by pixel count — gives 2048x2048 here, taller than the owner's 5120x1440 monitor; OVMF's fixed mode list has no 1440x1440. The one way a mode joins that list is the way a real monitor adds one: OVMF reads the display's EDID and puts its preferred mode first. Recommend the constitutional rule from ring 6a: **the display's preferred mode if it states one, otherwise the highest** — a monitor driven off its native mode is blurry, and at Stage 7 the real monitor's EDID is exactly what the OS should listen to. In the twin the guest reads the EDID from the standard VGA device's own memory (a PCI lookup of the display class, the EDID BAR, 128 bytes, the preferred width and height parsed from the first detailed timing descriptor), and every QEMU command — the gate, the twin and the oracle's windowed run alike — gains `-vga none -device VGA,edid=on,xres=1440,yres=1440`. The console becomes 90x90 cells on this machine; the tests keep reading the resolution from the guest's own log, so nothing is baked in. The `yres` number is the owner's to adjust (a 1440-tall window plus its title and menu bars overflows a 1440 monitor; `-full-screen` gives 1440x1440 exactly with black bars either side). The simpler alternative — a height cap as a build constant — needs no EDID code but leaves the OS deaf to what the monitor says. **Decided at approval: the EDID route, 1440x1440.**

**Decisions 1–6 were taken as recommended at approval, 1 September 2026.**

## Carried and deferred

Everything Stage 5 carried stands: one machine, one firmware; the x2APIC and trampoline paths unproven; the stack's omissions; plaintext inside the cage; a component runs at ring 0 with the whole machine in reach, and the rehearsal is the mitigation. New omissions, by design: one app at a time; cooperative stepping with a budget but no preemption and no watchdog; a torn cell may last one frame; no timer interrupt; no audio; no NVMe; no pointer acceleration; grown-but-not-installed apps still live only for the session; the choices row is text, not drawn targets; the trials are recorded for, not run.

The automated gate for every ring speaks only to the mock and spends no token. The cage, the bodyguard and every frozen file stand. Nothing outside the repository is written.

## Appendix — the first plan, `plans/calculator.md`

Read at ring 6b; frozen once you approve it. The tests are what the twin runs.

```
# calculator

## Intent
A four-function calculator for whole numbers. The panel shows a single line: the
number being typed, or the result of the last sum; it shows 0 before anything is
typed and after c clears. Digits 0 to 9 type a number. The keys + - * / choose
an operation. = shows the result, which may be negative. c clears everything.
Division is whole-number division; dividing by zero shows the word error until
the next key, which clears it. Numbers larger than nine digits show error the
same way. Nothing else is drawn.

## Choices
= result
c clear

## Tests
press 2+3=
expect "5"
press c
expect not "5"
press 12*12=
expect "144"
press 7/0=
expect "error"
press 9-10=
expect "-1"
```
