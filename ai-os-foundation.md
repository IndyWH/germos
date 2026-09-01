# GermOS — the homegrown operating system

**Foundation document — version 1.9, 1 September 2026** (v1.1 added Stage 8 — the molt; v1.2 the concurrency doctrine; v1.3 the meat-bag law; v1.4 the human-factors constitution; v1.5 Hick's law first and the LCARS clause; v1.6 the build loop from the AI-Native SDLC playbook; v1.7 the ignition key; v1.8 WSL2 retired — mlrig runs native Ubuntu; v1.9 the name)

**Named by the owner, 1 September 2026: GermOS.** Both meanings are intended — the germline it grows from, and the benign germ that settles in a machine, phones a faraway server, and starts mutating. It drew its first pixel the day before it got its name, as the old working-title rule required. The name reserved for the future shared germline network across machines: Mycelium.

**Status: live.** Work began 31 August 2026 — consultation-ai is public and the paper is submitted. This document remains the single source of truth.

**Team:** Wajira (product owner), Claude Cowork (design and specs, on Fable at high effort), Claude Code (implementation on mlrig under native Ubuntu, on Opus at high effort).

One more thing before the contents. This document is itself the first artefact of the idea it describes: an architect's plan written in plain English, meant to be grown into software. When the project starts, nobody re-reads code to find out what we intended. They re-read this.

---

## 1. The vision, in one sentence

An operating system that is grown on each machine rather than shipped to it: a small trusted core boots the computer and connects it to Claude, which writes everything else — kernel, drivers, applications — as machine code fitted to that exact hardware, and nothing touches the real machine until it has survived a rehearsal on a copy.

## 2. Why we are building it

The Sinclair Spectrum gave its owner two things that later computers took away. The whole machine was knowable — one person could hold the memory map in their head. And feedback was instant — you typed, and the machine answered. The Windows era delivered vastly more power, but buried both qualities under layers of abstraction, and the magic went with them.

LLMs brought the feeling back at the application layer. Consultation-ai is the proof: speak intent, working software appears, instant results. This project pushes the same arrangement all the way down to the metal. The machine becomes knowable again — not by being simple, but because the knower scales.

Everything in the design follows from one rule:

**Nothing that exists for human convenience is allowed to run at runtime.**

Human convenience belongs in the conversation, at authorship time. The machine runs only what the machine needs. This does not abolish the human-facing interpreter — it promotes it. Claude is the last interpreter, moved out of the machine and into the cloud, with English as the source language. An interpreter pays the translation cost on every run, forever, on your CPU. Claude pays it once, at authorship. Interpretation stops being an overhead and becomes an event.

## 3. The five load-bearing ideas

**The ISO is the new ROM.** One small, frozen, trusted piece: boot the machine, scan the hardware, light up the screen, reach the network, speak TLS to Claude. This is the umbilical cord. Everything above it is grown, not installed. The Spectrum booted into BASIC because Sinclair assumed the owner was a programmer. This OS boots into a conversation, because it assumes the owner employs one. And the core is never deleted, only demoted: the day the OS grows its own kernel, the frozen core becomes the recovery floor it can always fall back to. The Spectrum's ROM was physically unwritable, and that was the point.

**Bespoke code for the exact machine.** Claude emits machine code tuned to the processor it found — its instruction sets, its cache sizes, its core layout. Compilers are deleted from the machine. The assembler stays: labels are bookkeeping, one-to-one with the bytes, notation rather than abstraction. And we spend cleverness where it pays — across a whole program a good compiler gets within a few percent of perfect, so the large wins live in the hot loops, and that is where the attention goes. The same fitting applies across cores. Software idled seven of eight cores for a generation because sequential code is what human minds naturally write — sequential-by-default was one more human convenience running at runtime, and under our rule it goes. Grown programs are structured as small independent tasks from birth and scheduled by work stealing — idle cores take work from busy ones — so the machine uses every core the moment work can be split, and only then: Amdahl's law sets the ceiling, and some chains of work are serial by nature.

**The twin does the trusting.** A compiler's real job was to be the one part of the pipeline that never hallucinates. Delete it, and every emitted byte is an unchecked act — so determinism must be replaced with rehearsal. The boot-time hardware scan configures a digital twin: an emulated copy of the exact machine (QEMU, at first, on mlrig). Every driver and every kernel piece is born in the twin, fuzzed and crashed there, and only then flashed to the metal. The OS never learns on the real disk. The checking machinery is not overhead. It is the invention.

**The germline.** Generated components go into a shared cache, keyed by hardware and by the plan that produced them. The first machine of a given model pays the generation cost; every machine after inherits the proven result. Crash telemetry is selection pressure. An exploit on one machine becomes the herd's immunity. And because every machine's binaries are bespoke, the monoculture that makes today's exploits portable simply does not exist. The OS evolves — literally, with the cloud as the germline.

**The store of plans.** Applications are distributed as architect's plans: intent written in English, plus acceptance tests. The binary is grown on-site at install time, fitted to the ground it lands on — a different building from the same plan on a 4090 rig than on an old laptop. Installation is a conversation, so every install can amend the plan at the door ("install this, but left-handed"). Review becomes legible: the thing under review is readable by anyone. This is the magazine type-in listing reborn, with Claude doing the typing. (In Star Trek terms: a replicator for software — patterns stored as intent, materialised on demand, fitted to whoever asks.)

## 4. What we respect — the walls that stay

The silicon keeps its interpreters. A modern x86 chip translates machine code into micro-operations, renames registers, executes out of order, and its microcode is signed. We can be the last abstraction. We cannot be the zeroth.

The platform mandates one interpreter of its own. Firmware hands over power and thermal control as ACPI bytecode. We write that interpreter without complaint and move on.

Signed firmware is a permission wall, not a knowledge wall. NVIDIA acceleration and most WiFi run only vendor-signed blobs, and no amount of intelligence reasons past a signature check. We ship the blobs, as Linux does, and grow everything around them.

Standards are our allies. UEFI GOP gives pixels with no GPU driver. NVMe is a clean spec of queues and doorbells. XHCI covers USB. QEMU's virtio devices are simpler still. We drive the standardised interfaces first and leave the long tail for later, or for never.

The umbilical is frozen and boring. The network and TLS stack in the ISO is pre-built, verified, and never improvised — hand-rolled cryptography is where projects go to die. And it stays frozen even after the OS learns to brew its own parts: rewriting working cryptography is all risk and no reward. The loader and the crypto are the conserved core, and they are permanent (see Stage 8).

## 5. How we verify — the medical model

There is no human-readable source to audit, so verification is behavioural, and the method is the one Wajira already practises on the world's oldest undocumented legacy system.

Acceptance tests are written at spec time, before the code exists — the trial protocol precedes the treatment. Fuzzing and property tests run in the twin — in vitro before the patient. A serial log runs from the first byte of stage 0 — the observations chart. Telemetry follows every flash to real hardware — post-market surveillance. When something breaks: symptom, differential, test, treat.

Team conventions carry over unchanged: evaluation-first, draft-until-approved, code-enforced guarantees over polite requests, one commit per numbered item, tests green before every commit, HANDOVER.md updated as we go.

Concurrency gets its own clinic. Race conditions are the nondeterministic bugs — fine for a thousand runs, fatal on run one thousand and one — so the twin re-runs concurrent code with deliberately shuffled timings and race detectors until the schedule space is well explored. One law is absolute once there are pixels worth protecting: the thread that owns the screen does nothing else. And a standing convention from the owner: established evidence first. The project builds on the settled results of computer science — preemptive scheduling, work stealing, message passing over shared memory, supervision trees — and invents only where the literature runs out.

The human is the highest-priority device. The industries where lag kills — avionics, cars, medical devices — settled this long ago with mixed-criticality design: critical tasks get reserved, guaranteed resources, and everything else is best-effort, taking the leftovers. Desktops did it backwards and treated the person as just another process. Our kernel reserves the interactive path — input, cursor, audio, compositor — on a core of its own, chosen with knowledge of the machine's exact topology. Audio runs under deadline scheduling. Priority inheritance is mandatory (the lesson NASA learned when Pathfinder kept rebooting itself on Mars). And the kernel watches its own responsiveness and throttles heavy work the moment the human path misses a budget — homeostasis, not hope. The budgets are acceptance tests: in the twin, a compile from hell burns every core while a synthetic user types, scrolls and plays audio, and the build fails if input-to-photon exceeds budget or a single audio buffer arrives late. "Feels instant" is a number here, not a mood.

The kernel is born instrumented. Every queue is counted and every stall accounted from the first commit — how long each task waited for CPU, memory or disk is precisely what "heavy" means — and the numbers sit in a cheap shared page the UI reads at will. Progress indicators stop lying, because the thing drawing them is the thing doing the scheduling. The Spectrum showed its work as border stripes while the tape loaded; ours return as live telemetry — the machine's own obs chart.

The interface is evidence-based — the human-factors constitution. Human factors began in 1943, when crashed bombers taught engineers that "pilot error" is usually design error, and medicine later adopted the same discipline for its checklists and ampoule labels — so this DE is designed by a field its owner already practises. It is not a copy of existing desktops: those all descend from one 1984 office metaphor, a population-average design forced by shipping one binary to a billion people. Ours is grown, so it obeys the settled results instead. Few choices at a time (Hick) — the owner's first law, and the structural one: each panel shows what the current task needs and nothing else. Targets are big, close, and placed on edges and corners, where they are easiest to hit (Fitts). Recognition over recall, because working memory holds only a few items. No hidden modes — mode confusion has killed pilots. Undo everywhere instead of are-you-sure dialogs, because confirmation breeds the alert fatigue that plagues clinical software, while reversibility forgives. System status always visible — the obs chart. And attention is treated as the scarcest resource: notifications are triaged and batched like a good ward round, never interrupt-driven. The kernel guards the human's milliseconds; the DE guards their minutes.

Because every machine serves a known person, the evidence goes one level deeper than any existing desktop can: the DE may run N-of-1 trials — layout A against layout B, measured in speed and errors for this specific human — and fit the interface to its person the way the kernel fits the silicon. Accessibility stops being a settings panel and becomes the default consequence of a fitted interface. Since software materialises on request, the DE organises around the task at hand rather than around a grid of applications, growing its panels out of the conversation. The north star is the Enterprise's LCARS panels — but where every imitation copied the graphics, we build the premise the fiction assumed and no imitation could supply: an intelligence behind the glass, curating each panel for the task. We take the premise and the calm; the on-screen costume itself would fail this constitution. And one metric rule is constitutional: the DE optimises time-to-done and error rate, never engagement. A good tool wants its human to leave sooner.

The build loop — adopted from Anthropic's AI-Native SDLC playbook (August 2026). The playbook is written for enterprises, but its core loop is our team of three at a different scale, so we take the parts that fit. Every piece of work travels as committed files: intent.md (the owner's ask — what and why), spec.md (Cowork's one-page design), plan.md (CC's implementation plan, produced in plan mode and approved before any code is written), then code with tests. Git history is the audit trail. The repo carries a CLAUDE.md kept under one page — build and test commands, conventions, common bare-metal mistakes — with the playbook's best rule adopted verbatim: the second time a mistake is corrected, the correction goes into CLAUDE.md. Guarantees we care about become hooks, not requests: CC is mechanically blocked from editing acceptance tests during a fix, and from touching the frozen umbilical and crypto paths — the conserved core gets a bodyguard, not a polite notice. Every black-screen bug becomes a permanent regression eval in the twin, so no bug gets to happen twice. A light REVIEW.md tells Cowork how to review CC's diffs: bugs first, then safety, then spec alignment, nits capped. The enterprise machinery — managed settings, compliance feeds, deployment committees — we ignore until the day this project somehow acquires employees.

## 6. Tools and cost

NASM for assembly. QEMU as the twin's first body, with its monitor, snapshots, and gdb stub as the diagnostic kit. Git and HANDOVER.md as the coordination channel. Cowork writes specs; CC implements from one consolidated block per session.

Cost: the whole project runs inside the existing Max subscription — Cowork sessions, CC sessions, and (under current policy) even the future umbilical, since Agent SDK and `claude -p` usage draws from subscription limits. No API tokens. The policy is re-checked at Stage 4, not before. This is a kilobyte-scale project; it will barely dent the weekly allowance.

## 7. The stages — growth rings

Every stage obeys three rules: small enough to finish, ends with something you can see, and gated — acceptance tests pass in the twin before the next ring grows.

1. **Stage 0 — First pixel.** A 512-byte boot sector running in QEMU: clear the screen, draw something (Spectrum loading stripes have been proposed), say hello over serial. Proves something can be grown from nothing. An afternoon.

2. **Stage 1 — Owning the processor.** The UEFI boot path: 64-bit long mode, paging, every core woken and counted, the GOP framebuffer, pixels drawn at native resolution. (Stage 0 uses the romantic BIOS path for its 512-byte purity; from here on we take the practical UEFI road. Flagged as a recommendation, not a law.) Proves full control of the CPU.

3. **Stage 2 — Senses.** Keyboard input and a text console on the framebuffer; the serial debug channel becomes permanent. Proves the machine is interactive.

4. **Stage 3 — Memory of its own.** Block storage (virtio first, NVMe second) and a simple filesystem. **Hard safety rule: storage code touches only QEMU disk images until Stage 7, and never any disk holding real data.** Proves the OS keeps what it grows.

5. **Stage 4 — The umbilical.** Network driver, minimal TCP/IP, the frozen TLS stack, and a broker service on mlrig that relays to Claude. Done when the booted OS asks Claude a question and prints the answer. Proves the OS has a brain. (Subscription policy re-checked here.)

6. **Stage 5 — The conversation.** The prompt itself: English in, machine code back, verified in the twin, then run. The germline starts as a local cache of proven components. Done when "make me a clock" produces a running clock. Proves the loop closes — the Spectrum prompt is back.

7. **Stage 6 — Growth.** A simple compositor and GUI, more devices, and the store-of-plans prototype: install an application from a plan file. The compositor ships with the machine's obs chart from day one — border stripes reborn as truthful, live telemetry — and the DE takes its shape from the human-factors constitution, not from existing desktops.

8. **Stage 7 — Metal.** A sacrificial machine (owner decision when the time comes — a cheap mini PC or a retired laptop), boot from USB, and every prior stage re-proven on real hardware. Proves it was never just a simulation.

9. **Stage 8 — The molt.** The OS replaces the generic core with parts it grew itself, one component at a time — drivers first, kernel proper last. Each brewed part must beat the generic one in the twin, then run in shadow alongside it before taking over, like a registrar working under supervision before being signed off. The old core is demoted to a recovery slot, never deleted, and a watchdog boots it if the brewed system fails its health checks. Every so often the system is re-derived from the frozen seed and compared against the brewed line — the independent witness against a self-perpetuating fault. Two parts never molt: the loader and the cryptography, the mitochondria of the system. Done when the machine reboots into a kernel it grew itself and survives a week. Proves the OS is self-hosting.

Beyond Stage 8 lies the horizon rather than the roadmap: the shared germline across machines, the public store of plans, evolution proper — and the slow shrinking of the frozen seed toward a few auditable kilobytes.

## 8. Risks, with likelihood

**Certain — black-screen debugging.** Bare-metal bugs give a blank screen, not an error message. Mitigation: the serial log from byte one, QEMU snapshots, and commits so small that the last known good state is minutes away.

**Certain — the world shifts under a long project.** Models, policies, and tools will change between stages. Mitigation: re-check assumptions at stage gates, never mid-stage.

**High — stalls and motivation dips.** Long gaps are already planned for; the danger is a stage that drags. Mitigation: stages sized to an evening or a weekend, each ending in something visible.

**Medium — subtly wrong emitted code.** The hallucination tax. Mitigation: the twin, acceptance tests written before the code, and disassembly review on anything that touches storage or memory maps.

**Low but fatal — damage to real hardware or data.** Mitigation: the hard rule at Stage 3, QEMU-only until Stage 7, sacrificial hardware only, and mlrig's own disks never in the blast radius.

**Low — usage-limit pressure.** Kilobyte-scale sources and short sessions. Mitigation if it bites: Sonnet for mechanical chores, `/clear` between numbered items, serial output read from the tail of a log file.

## 9. What this is not

Not a Linux replacement. Not a product. Not secure enough to trust with anything that matters. Never, under any circumstances, connected to clinical work or patient data. It is a laboratory for one thesis — that software can be grown rather than shipped — and the most fun available per kilobyte.

## 10. Day one, when it comes

1. Open a Cowork session (Fable, high effort) and point it at this document and the saved conversation.
2. Cowork writes the Stage 0 spec: one page — the bytes, the layout, the acceptance tests.
3. Wajira approves it. CC (Opus, high effort) starts in plan mode and commits plan.md; once the plan is approved, it implements from one consolidated block. QEMU goes onto mlrig.
4. Pixels by teatime. HANDOVER.md and CLAUDE.md are started in the new repository, and this document lives at its root.

**Decisions already made:** Fable specs and Opus-at-high implements; work starts after consultation-ai is public and the paper is submitted; no API spend; the stage order above. Recorded at Stage 0 approval (31 August 2026): mlrig runs native Ubuntu 26.04 — WSL2 is retired; the repo lives at /home/indy/Projects/ai-os under the neutral placeholder name.

**Decisions reserved for the owner:** the name; the Stage 7 hardware; anything a stage spec flags as a judgement call.

## 11. The ignition key

On the day: start a fresh Cowork session on Fable at high effort, attach this document, and paste the following as the first message. (Used 31 August 2026 — kept for the record.)

```
We are starting the AI OS project today. A previous session and I designed it together: an operating system grown on each machine rather than shipped to it, starting from a 512-byte boot sector. I have attached the foundation document, ai-os-foundation.md. It is the single source of truth: vision, rules, stages, build loop, and team conventions. Consultation-ai is public and the paper is submitted, so the project is live. This session is for speccing and runs on Fable at high effort. Claude Code implements on Opus at high effort. Read the whole document first, then work in this order.

1. Confirm in a few lines what we are building and what Stage 0 proves, so I know the document landed.

2. Write the Stage 0 spec for my approval: one page, the exact bytes and layout of the boot sector, the QEMU run command, and the acceptance tests, following the day-one script and the build loop in the document. Stage 0 output should include the Spectrum loading stripes.

3. Wait for my approval, and never move past a step until I have pasted back any output you asked for.

4. After approval, give me the Claude Code kickoff prompt as one consolidated block in the accessible style: CC starts in plan mode, commits plan.md for my approval, then implements with one commit per numbered item and tests green before each commit. Include the QEMU and NASM install steps for Ubuntu on mlrig at the start of the block, and have CC create the repository with HANDOVER.md, CLAUDE.md and this foundation document at its root.

5. The goal for today is the document's Stage 0 done-when: visible output in QEMU plus a hello over serial. Pixels by teatime.
```

*A dream with acceptance criteria is called a specification. This is one.*
