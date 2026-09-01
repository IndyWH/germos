# Stage 5 — The conversation · spec

**Goal (foundation §7):** the prompt itself: English in, machine code back, verified in the twin, then run. The germline starts as a local cache of proven components. **Done when "make me a clock" produces a running clock.** Proves the loop closes — the Spectrum prompt is back.

**The policy gate, re-checked at this gate as the foundation requires (1 September 2026):** the June 2026 credit-pool change remains **paused**. Anthropic's help centre states that Agent SDK, `claude -p` and third-party app usage still draw from subscription limits, there is no separate credit pool, and any future change will be announced before it takes effect. So the broker keeps shelling out to `claude -p`, no API keys anywhere, and the backend stays one swappable unfrozen function. Re-check at the next stage gate. (The germline cache this stage builds is itself the mitigation if the policy ever tightens: a proven component is never generated twice.)

## The shape

Stage 5 grows on Stage 4's body in three places. The machine the user faces and the twin that rehearses are the **same guest image** — rehearsal is a headless, scripted boot of that image on mlrig, fed through the same wire, watched by screendump and serial. What passes rehearsal is what runs; at Stage 7 the machine becomes metal and the twin stays QEMU, and nothing about this pipeline changes.

**The guest — a third kind of line.** A note (unmarked) journals as ever; `? ` asks as ever; a line marked `! ` asks Claude to *grow something* — `! make me a clock`. Both markers now get the forgiving parse, closing Stage 4's usability finding: the marker character alone, or with any spacing, is recognised, and a marker line that cannot reach the broker says so on the console instead of silently doing nothing. The guest gains a **loader**: a fixed component region in the identity map, a new binary frame arriving over the wire, a jump into the blob with one register pointing at a small **service table** (draw text at cell, console size, poll key, millisecond ticks), and a clean return to the prompt when the component exits (Esc is the convention). One owner still: the component runs on the BSP, in the main loop's stead, and the screen has no other writer while it runs.

**The wire — one new frozen document.** `stage5/GERMLINE.md`: the grow request (printable ASCII like a question, distinguished by its marker byte on the wire), the response — either a text refusal (drawn like an answer) or a length-prefixed **binary component frame** (cap 1 MB) with its entry contract and the service-table ABI — worked-example bytes, and the shared Python parser. Stage 4's `UMBILICAL.md` is frozen and is not touched; questions and notes ride exactly as before.

**The broker — the grow pipeline.** On a grow request: (1) **generate** — `claude -p` with a brief that asks for a flat binary against the published ABI (the brief and folding live in the unfrozen backend, as at Stage 4); (2) **rehearse** — boot the twin headless, deliver the candidate through the wire, judge it by the rehearsal criteria below; (3) **cache** — a passing component lands in `germline/` (gitignored — the machine's own cache, not repo content) keyed by the normalised request, the ABI version and the machine, beside a provenance record: request, date, model, blob hash, rehearsal log; (4) **deliver** — the proven blob goes to the guest. A repeat request is served from the germline with no generation call at all. A failing candidate never reaches the guest: the user sees a refusal naming the failure.

**Rehearsal criteria, this ring:** the twin boots clean, the component loads and runs, the screen changes, no `ERR:` line appears, Esc returns to a live prompt, and a note typed after exit still journals. These are generic — they prove *safe*, not *correct*. Whether the thing on the screen is the thing that was asked for is the oracle's judgement at this ring; per-request acceptance tests generated alongside the code are Stage 6's store-of-plans, not this stage.

## Decisions for the owner

1. **The grow marker.** Recommend `! ` (with the forgiving parse above). The alternative — one marker, with the broker classifying question against request — costs tokens, can misroute, and hides the routing from the user. Explicit beats clever this ring.
2. **What the core provides to grown code.** Recommend the minimal service table above and nothing more — the clock reads the CMOS RTC by its own port I/O, a bespoke driver born at request time, because that is the thesis. The safer alternative (core provides `now()`) proves less. The twin is what makes the bolder version affordable.
3. **Rehearsal depth.** Recommend the generic criteria above, with the clock-specific check living only in this stage's frozen harness. Generated per-request tests are deferred (Stage 6).
4. **The implementing model.** The standing rule is Opus at high effort; Fable 5 at high effort has now shipped Stages 2, 3 and 4 with zero review defects and wrote the Stage 4 code this stage extends. Recommend Fable 5 high; the call is reserved to you.

## Acceptance tests

Written before the code, frozen once written. The automated gate speaks only to the mock and **spends no token**; the cage, the bodyguard and the frozen files all stand.

| # | Test |
|---|---|
| 1 | **Artefact** — PE32+ magics, x86-64, subsystem 10, relocs stripped, packed image (standing). |
| 2 | **Serial** — Stage 4's lines as `S5:`, plus the component-region line in its slot; found = woken = smp. |
| 3 | **The growth, mocked** — the mock serves a canned, committed, hand-written test component; the harness types the grow request; the frame on the wire matches `GERMLINE.md` byte for byte; the component's known picture is on the screen pixel-correct; Esc returns to the prompt; a note before and after persists; `? ping` still answers. At `-smp 2` and `-smp 8`. |
| 4 | **The rehearsal and the germline** — a deliberately faulting blob fails rehearsal, the guest gets the refusal, nothing runs; the good component passes, is cached with its provenance record, and a second identical request is served from the germline with the generation backend never invoked (the mock counts calls). Marker-parse cases: bare `?`, `?x`, bare `!`, `!x` all route correctly. |
| 5 | **Oracle — Wajira, real broker** — `! make me a clock`. Rehearsal runs, passes, and a clock with the right time ticks on GermOS's screen; Esc returns to the prompt; asking again comes from the germline. **His word closes the stage.** |

## Carried and deferred

Everything Stage 4 carried stands. New omissions, by design: one component in memory at a time, cooperatively run, no persistence of components in the notebook (the germline lives broker-side this ring), no component-to-broker traffic while running, 1 MB cap, and the generation brief's quality is the backend's own affair — the gate proves the pipeline, the oracle proves the clock.
