# CLAUDE.md

Kept short: only what every session needs. The rest is in GATES.md and
GOTCHAS.md. Source of truth is `ai-os-foundation.md`; current state is
`HANDOVER.md`.

## Build and test

Build first with `./stage<N>/mkimage.sh`. `GATES.md` has the full descriptions,
the tools, the mock brokers, the windowed oracle command, and the real
`claude -p` commands, which are the owner's word only.

```bash
./stage0/test.sh         # ~14 s; no ports; built by its nasm line in GATES.md
./stage1/test.sh         # ~4 min; no ports
./stage2/test.sh         # ~76 s; no ports
./stage3/test.sh         # ~4 min; no ports
./stage4/test.sh         # ~2 min; ports free: 9999
./stage5/test.sh         # 229 s on 9 Nov 2026; ports free: 9999 9998
./stage6/test.sh         # ring 6a; 382 s on 9 Nov 2026; ports free: 9999 9998
./stage6/test-6b.sh      # 394 s on 9 Nov 2026; ports free: 9999 9998
./stage6/test-6c.sh      # 206 s on 9 Nov 2026; ports free: 9999 9998
./stage7/test.sh         # ring 7a; ~8 min; ports free: 9999 9998
./stage7/test-7b.sh      # ~5 min; ports free: 9999 9998 9997
./stage7/test-7c.sh      # ~2 min; ports free: 9999 9998 9997
./stage7/test-7d.sh      # about 21 min; ports free: 9999 9998 9997
./stage8/test-8a.sh      # about 43 min; ports free: 9999 9998 9997
./trials/test-trial2.sh  # ring 8t; about 66 min; ports free: 9999 9998 9997
./stage8/test-8b.sh      # about 86 min; ports free: 9999 9998 9997
python3 .claude/hooks/payloads.py # the hook's table; seconds; no ports; 0 wrong or exit 1
```

Each script above is the gate of its stage or ring. It must be green before
every commit that should pass it, and earlier stages stay green forever.

## Conventions

- **Evaluation-first.** Acceptance tests are written before the code they judge.
- **Draft until approved.** The plan file, `plan.md` or `plan-<ring>.md`, is
  committed and approved before any implementation code is written.
- **One commit per numbered item** from the plan file, `plan.md` or
  `plan-<ring>.md`. Small commits; the last known good state is minutes away.
- **Tests green before every commit.** No exceptions once the tests are expected
  to pass.
- **Update `HANDOVER.md` as you go**, not at the end of the week.
- **The second time a mistake is corrected, the correction goes into GOTCHAS.md**
  — under its topic heading.
- **Guarantees are hooks, not requests.** Acceptance tests cannot be edited
  during implementation or a fix; `.claude/hooks/protect-tests.py` blocks it.
  Freezing a new stage's tests is one line: add the paths to `PROTECTED`.
- **The gate is frozen; the builder is not.** `test.sh` and the pixel checkers
  hold the criteria. `mkimage.sh` holds the recipe, and stays fixable.
- **QEMU only, for Claude Code.** A session writes nothing outside this folder
  and touches no real disk device, ever, at any stage. Since Stage 3 the same
  hook is the **storage bodyguard**: any `/dev` path bar the harmless sources and
  sinks, mount/umount/losetup/mkfs and the partitioning tools, `sudo`, a QEMU
  `-drive file=` outside a repo `out/`, the disk shorthands, and `qemu-img`
  outside `out/` are denied in any Bash command, prose included. The only
  disks a session uses are raw files the harness makes under a repo `out/`.
  The flash is the owner's hand alone, and a machine GermOS boots on holds only
  sacrificial disks, never one with real data.
- **The network is a cage too (Stage 4).** In the twin, slirp with
  `restrict=on` and one `guestfwd`: the guest reaches one door and nothing
  else, and every other destination gets a RST. The door is the broker on
  `127.0.0.1:9999`, or from ring 7b the relay on `9997`, which forwards to the
  broker; a rehearsal's door is its own listener on `9998`. The broker binds
  `127.0.0.1` only, and the relay refuses every bind but `10.0.2.4` and
  `127.0.0.1`. On the HP there is no slirp: the guest has no gateway and no
  route, and reaches only the relay on mlrig at `10.0.2.4`. Every automated
  gate talks only to a mock, a stub or `molt.py --collect`, none of which calls
  Claude, and refuses to run while anything else holds its ports, so no gate
  spends a token or reaches the real Claude. A real `claude -p` call is made
  only through `broker/claude_backend.py`, and only on the owner's word, over
  ordinary HTTPS from the broker. The guest link is plaintext: inside the cage
  in the twin, and across the owner's home network on the HP. TLS joins the
  guest at the ring where its traffic first crosses a network he does not own.

## Bare-metal gotchas

`GOTCHAS.md` holds the rest, by topic. Read a section when you reach its area.
Older documents that cite CLAUDE.md for a gotcha now mean that file.

- **NASM and x86:** before writing or reviewing any assembly.
- **UEFI and OVMF:** for boot, the memory map, the ESP, or a triple fault.
- **The framebuffer and the console:** for modes, EDID, pixels, or what prints where.
- **Interrupts and the i8042:** for the APIC, the PIC, `hlt`, or input devices.
- **Virtio:** for a virtio device, a PCI BAR, or DMA.
- **The network and the broker:** for slirp, `guestfwd`, TCP, or `claude -p`.
- **QEMU and the twin:** for a QEMU command, a probe, a new machine, or a monitor parser.
- **Grown code:** for parts, apps, the bench, or a rehearsal.
- **Checkers and counters:** before writing a frozen test, or a number in one.
- **The metal:** for the HP, its LAN, or a stick.

These six stay here. Two apply whatever the ring. `broker/claude_backend.py`
reads the other four from this file by name, and moving one fails ring 8b's gate.

- **Serial before video.** The first observable act of any stage is a serial
  line. A black screen with no serial output means the code died before it ran;
  a black screen *with* serial output means video setup is the bug. This
  distinction is the whole debugging strategy.
- **A halted guest never exits QEMU.** Wrap headless runs in `timeout` and treat
  exit 124 as the expected success signal; any other non-zero exit is real.
- **A 0xE0 scancode prefix swallows its successor.** Ignoring just the prefix
  turns keypad Delete (`E0 53`) into keypad-dot's make code - a stray `.` on
  screen.
- **Two devices on one i8042: read the status byte before port 0x60.**
  Bit 5 says whose byte it is; a handler that reads 0x60 blind puts a
  mouse byte in the keyboard ring. Command-byte bit 5 set means the aux
  port is *disabled* (OVMF leaves 0x67), and PS/2 `dy` counts upwards, so
  the monitor's `mouse_move 10 20` arrives as `28 0a ec` (ring 6c).
- **Nothing survives a call into grown code but memory and the stack.**
  An app may clobber every register but RSP, so loop state around
  `app_call` goes on the stack (pushed before, popped after - `app_call`
  restores RSP from `saved_rsp`), never in R12-R15, whatever the fixture
  happens to preserve. `click_panel`'s button loop passed the gate on the
  point app's courtesy alone (Cowork's pre-oracle review, ring 6c item 12b).
- **An i8042 self-test may re-enable both ports.** A device's power-on
  byte can then sit in the output buffer ahead of the command byte, and
  the `0x20` read takes it as the command byte, clears translation and
  writes it back: a dead keyboard. Disable both ports and drain again
  between the self-test's `0x55` and the command byte's read (ring 7c
  item 15, Cowork's pre-oracle review; the twin cannot show it).

## Working with the hooks

- **Only the hook *registration* is snapshotted at session start; the script is
  re-read on every call.** So a brand-new hook does not fire until the next
  session, but *edits to an already-registered one are live immediately*. (This
  corrects the Stage 0 note, which assumed the stricter case.)
- **The freeze matches prose, deliberately.** A Bash command that merely
  *mentions* a frozen filename near a mutating verb — a commit message, a
  comment, the hook's own `PROTECTED` list — is denied. Reword it, or use the
  Write/Edit tools, which judge the target path only. A false deny costs a
  reworded command; a false allow costs an edited acceptance test.
- **Don't undo a temporary probe with `git checkout --`.** It reverts to HEAD
  and takes the current item's uncommitted work with it. Copy the file aside
  first, and restore from the copy.
- **A heredoc that mentions a frozen file near `open(`/`write` is denied**
  even when it only reads. Edit prose with the Edit tool; if a script must
  mention a frozen name, write the script to a file first and run the file.
- **Commit messages that mention the bodyguard's words go in via `-F`** from
  a file written with the Write tool; `-m` puts the words in the command.
- **The directory rule (ring 8a, the owner's of 25 September 2026).** `rm`,
  `rmdir`, `mv`, `git rm` and `git mv` are denied on the repo root, on a
  directory holding a frozen file (a bare name like `fixtures` included),
  and on a glob that covers one. Name the scratch path itself
  (`rm -rf stage8/out/molt`), never its parent.

## The plan gate

- Exiting plan mode is blocked by a hook until Wajira approves. He reviews the
  plan (via Cowork), then runs, in his own terminal at the repo root:
  echo approved > PLAN_APPROVED
  The hook consumes the marker: one approval opens the gate exactly once.
  Never create or mention PLAN_APPROVED from inside a session - the other
  hook denies every route to it. The plan gate exists because full-auto mode
  otherwise lets a session approve its own plan.
