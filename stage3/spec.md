# Stage 3 spec — Memory of its own

**spec.md for Stage 3 · Cowork, 1 September 2026 · status: APPROVED by Wajira, 1 September 2026**

## What we are building

The machine learns to remember. A virtio block driver, a deliberately tiny filesystem, and one visible behaviour that proves the foundation's done-when — the OS keeps what it grows: **everything you type at the prompt is kept on disk, and the next boot greets you with it.** Type a note tonight; tomorrow's boot shows it back.

## The hard safety rule, first

From the foundation, verbatim: *storage code touches only QEMU disk images until Stage 7, and never any disk holding real data.* For an overnight, unattended stage this becomes mechanical, not behavioural: before any implementation code is written, the guard hook grows a **storage bodyguard** — Bash calls mentioning `/dev/` block devices (`/dev/sd*`, `/dev/nvme*`, `/dev/disk*`, `/dev/mapper`), `mount`, `losetup`, `mkfs`, or a QEMU `-drive` whose file sits outside the repo's `out/` directories are denied outright (`/dev/zero` and `/dev/urandom` stay allowed as sources). The only disk in this stage's world is a raw file the test harness creates fresh under `stage3/out/`.

## The work, in behavioural order

1. Everything Stage 2 proved, kept: the console, the keyboard, the IDT, the cores. Serial lines become `S3:`.
2. **The disk.** Find the virtio-blk device on the PCI bus, negotiate, and read/write 512-byte sectors through its virtqueue. Log `S3: disk <N> sectors`. (NVMe is the foundation's "second"; it is deferred to a later ring, not smuggled into this one.)
3. **The notebook.** A minimal filesystem of our own design — a magic header plus an append-only journal of notes — fully specified in `stage3/NOTEBOOK.md` so the acceptance tests can parse the disk image from the outside with a Python checker, the way the font is shared in Stage 2. A blank disk is formatted on first boot: `S3: notebook formatted`. A recognised disk replays: `S3: notebook <N> notes`, and the notes appear on the console above the prompt.
4. **The behaviour.** Every line you finish with Enter is appended to the notebook — written through to disk before the new prompt appears, so a power cut after the prompt loses nothing. The serial echo contract stays exactly Stage 2's.

## Acceptance tests

Written before the code, frozen behind the hook — and test 3 is the soul of the stage.

1. **Artefact.** PE32+ checks on stage3's binary and image.
2. **Serial, first boot.** Fresh blank disk: the Stage 2 lines plus `S3: disk <N> sectors` and `S3: notebook formatted`, in order; found = woken = the `-smp` value.
3. **Persistence.** Run one: type `remember me` and Enter via sendkey, quit. The checker parses the disk image *from the host* and finds the note, byte-exact, per NOTEBOOK.md. Run two, same image, fresh QEMU: the boot log says `S3: notebook 1 notes` and the console shows `remember me` above the prompt — the machine's first memory surviving its first death. Runs at `-smp 2` and `-smp 8`.
4. **Pixels.** After run two, the screendump shows the replayed note and the prompt, glyph-correct, nothing but the two console colours.
5. **Oracle.** You, in the morning: boot it windowed, read what you typed the night before, add a note, reboot, see both. Your word closes the stage.

## Build and run

As Stage 2, from stage3/, plus the disk: the harness creates `stage3/out/notes.img` (raw, 16 MB) and the run command gains `-drive format=raw,file=stage3/out/notes.img,if=virtio` as a second drive after the boot image. No new packages.

## Rules carried forward

QEMU only; the storage bodyguard above; serial before video; one owner per device; every new fault class a gotcha and a regression check; Stage 0–2 tests green throughout.

## Decisions recorded at approval (owner, 1 September 2026)

1. **Filesystem shape.** Our own append-only notebook format, spec'd in stage3/NOTEBOOK.md and parsed independently by the tests — the smallest honest thing that proves persistence, in the store-of-plans spirit.
2. **What persists.** Every entered line, automatically. The reboot greeting is the demo.
3. **Overnight scope guard.** In force: if virtio negotiation fights back, stop, record, leave the rest for morning. No improvising around a storage device at 3 a.m.
