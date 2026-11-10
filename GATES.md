# GATES.md

The full gate descriptions, the tools, the mock brokers and the windowed oracle
command. Moved word for word from CLAUDE.md, which keeps one line per gate.

## Stage 0

```bash
# Stage 0 - closed, kept as a standing regression check
nasm -f bin stage0/stage0.asm -o stage0/out/stage0.img
./stage0/test.sh
```

## Stage 1

```bash
# Stage 1
./stage1/mkimage.sh    # assemble stage1.asm, pack the FAT image (not frozen)
./stage1/test.sh       # acceptance tests 1-4. ~4 min: each halted guest burns
                       # its 60s timeout, which is the expected outcome
```

## Stage 2

```bash
# Stage 2
./stage2/mkimage.sh    # assemble stage2.asm, pack the FAT image (not frozen)
./stage2/test.sh       # acceptance tests 1-4: artefact, nine serial lines,
                       # sendkey typing at -smp 2 and 8, pixel-checked console
```

## Stage 3

```bash
# Stage 3
./stage3/mkimage.sh    # assemble stage3.asm, pack the FAT image (not frozen)
./stage3/test.sh       # acceptance tests 1-4: artefact, eleven serial lines on
                       # a fresh disk, persistence across two boots at -smp 2
                       # and 8 (image parsed from the host), pixel-checked
                       # replay. ~4 min, seven QEMU boots.
```

## Stage 4

```bash
# Stage 4
./stage4/mkimage.sh    # assemble stage4.asm, pack the FAT image (not frozen)
./stage4/test.sh       # acceptance tests 1-4: artefact, twelve serial lines
                       # with the nic MAC, the "? " question round-trip through
                       # the MOCK broker at -smp 2 and 8 (a note between two
                       # questions, the wire echo untouched), and the cage -
                       # restrict=on with one guestfwd asserted, a mock-down
                       # run ending in a console message not a hang. Refuses to
                       # start if anything listens on 9999. Five QEMU boots.
```

## Stage 5

```bash
# Stage 5
./stage5/mkimage.sh    # assemble stage5.asm, pack the FAT image (not frozen)
./stage5/test.sh       # acceptance tests 1-4: the grow request, the component
                       # rehearsed in the twin, the germline; needs 9999 and
                       # 9998 free. Five boots plus six rehearsals, 229 s on
                       # 9 Nov 2026.
```

## Stage 6 ring 6a

```bash
# Stage 6 ring 6a - the glass
./stage6/mkimage.sh    # assemble stage6.asm, pack the FAT image (not frozen)
./stage6/test.sh       # acceptance tests 1-4 at 1440x1440 with ONE virtio disk:
                       # sixteen lines, the app in its panel, the truth on the
                       # strip. 382 s on 9 Nov 2026. Still the regression for
                       # ring 6b: the same binary without a home image is
                       # ring 6a's.
```

## Stage 6 ring 6b

```bash
# Stage 6 ring 6b - the store of plans
./stage6/test-6b.sh    # acceptance tests 1-4 at 1920x1080 with TWO virtio disks
                       # (notes and home): seventeen lines, "! install echo"
                       # rehearsed against the plan's tests, the launch with no
                       # broker, the liar refused, the undo. 394 s on 9 Nov 2026.
```

## Stage 6 ring 6c

```bash
# Stage 6 ring 6c - the pointer
./stage6/test-6c.sh    # acceptance tests 1-4 at 1920x1080 with two virtio disks,
                       # the PS/2 mouse driven through the monitor: seventeen
                       # lines then "S6: mouse ready" on the first packet, the
                       # arrow and the strip's pt field, a click on the choices
                       # row doing what its key does, point in the point app's
                       # panel, packets counted equal packets sent. 206 s on
                       # 9 Nov 2026.
                       # Rings 6a and 6b stay the regressions: the same binary
                       # with a mouse that never moves is ring 6a's to the pixel.
```

## Stage 7 ring 7a

```bash
# Stage 7 ring 7a - the disk
./stage7/mkimage.sh    # assemble stage7.asm, pack the FAT image (not frozen)
./stage7/test.sh       # acceptance tests 1-4 on q35's own AHCI with -cpu
                       # IvyBridge and ONE 64 MB SATA disk the guest partitions
                       # (stage7/DISK.md): eighteen lines on a blank disk and
                       # the table byte-exact, seventeen on the same disk, the
                       # twin's shape with a virtio disk the guest ignores, a
                       # foreign table refused; two notes across a reboot on
                       # the notes partition; ring 6b's store test on the home
                       # partition at -smp 4. Needs 9999 and 9998 free.
                       # ~8 min, twelve boots plus four rehearsals.
```

## Stage 7 ring 7b

```bash
# Stage 7 ring 7b - the wire
./stage7/test-7b.sh    # acceptance tests 1-4 on q35's AHCI with -cpu IvyBridge,
                       # the SATA disk, and an e1000e carrying the HP's MAC on a
                       # cage whose guestfwd lands on the RELAY (9997), which
                       # forwards to the mock on 9999: nineteen lines with
                       # "S7: nic 6c:3b:e5:3b:86:45" and "S7: link up", eighteen
                       # on the same disk, the e1000e preferred beside a
                       # virtio-net, the link taken down through the monitor
                       # ending in a named error; the question through the relay
                       # at -smp 2, 4 and 8 with the relay's log against the
                       # record and the strip; the cage - both argv checks, the
                       # relay's bind rule, a mock-down run, "! test app" and
                       # "! install echo" through the relay, the launch with
                       # nothing on the wire. Needs 9999, 9998 and 9997 free.
                       # ~5 min, ten boots plus two rehearsals. Ring 7a's gate
                       # stays the regression: the same binary on virtio-net.
```

## Stage 7 ring 7c

```bash
# Stage 7 ring 7c - the metal
python3 stage7/mkstick.py   # after mkimage.sh: stage7/out/stick.img - a protective MBR,
                            # a GPT, one 64 MB ESP holding EFI/BOOT/BOOTX64.EFI,
                            # written with mtools at the partition's offset (not frozen)
./stage7/test-7c.sh    # acceptance tests 1-4 on the twin of the HP: the stick
                       # parsed from the host (test 1); a COPY of it booted over
                       # qemu-xhci + usb-storage with NO esp.img on SATA, the
                       # 64 MB SATA disk and the e1000e cage to the relay on
                       # 9997 - nineteen lines at -smp 8, eighteen on the same
                       # disk at 4, "S7: edid none" and the highest mode on
                       # virtio-vga at 2, the "i8042:" pair on every boot, the
                       # stick copy's tables unchanged (test 2); every stage
                       # re-proven in one run of two boots at -smp 4 - typing,
                       # the note across the reboot, "? ping", "! test app",
                       # "! install echo" in wire.py's twin, then with nothing
                       # on the wire the note back and a click on "! echo"
                       # launching it (test 3); the argv checks, the relay's
                       # bind rule, the payload table 0 wrong and the flash's
                       # words and every /dev spelling denied (test 4). Needs
                       # 9999, 9998 and 9997 free. ~2 min, five boots plus two
                       # rehearsals. Rings 7a and 7b stay the regressions on
                       # the same binary from esp.img.
```

## Stage 7 ring 7d

```bash
# Stage 7 ring 7d - the trials
./stage7/test-7d.sh    # acceptance tests 1-4 on the 7c shape, the PS/2 mouse
                       # through the monitor, every run appended to
                       # stage7/out/gate-7d.log: TRIALS.md parsed cold and its
                       # worked examples reproduced; the "! trial" refusal
                       # while an app runs, the sitting's start, layout A's row
                       # to the pixel, block 2's boxes in the surface and on
                       # the screen; three sittings played by a synthetic human
                       # to a scripted verdict B with every median inside the
                       # spec's window, the abort, the default read at boot,
                       # the reserved prefix refused, a click on a box; the
                       # freeze and the payload table, then the 7c, 7b and 7a
                       # gates on the same binary. Needs 9999, 9998 and 9997
                       # free. About 21 min: six boots and one grow of its own,
                       # then the three earlier gates.
python3 stage7/trials.py --disk stage7/out/disk.img   # the sitting tables and the
                       # verdict from a GermOS disk image; --serial LOG from the
                       # HP's chart; --example the document's worked examples
```

## Stage 8 ring 8a

```bash
# Stage 8 ring 8a - the floor
./stage8/mkimage.sh    # assemble stage8.asm (it includes the frozen loader.asm),
                       # pack esp.img (not frozen); the build is the seed
                       # stage8/seed-record.md's last line names
python3 stage8/mkstick.py   # after mkimage.sh: stage8/out/stick.img, 7c's shape
./stage8/test-8a.sh    # acceptance tests 1-4 on the 7c twin, every run
                       # appended to stage8/out/gate-8a.log: the artefact,
                       # PARTS.md and SEED.md read cold, the fixtures, the
                       # known answer; no part, no change (ring 7d's checks on
                       # this build); the five fates - good to its threshold
                       # and live, wrong, hang and fault reset by the watchdog
                       # and demoted, the liar at the door, Esc, the 60 s held
                       # request and the idle health mark; the cage, the
                       # sixteen frozen paths with loader.asm, the payload
                       # table, then ring 7d's gate with 7c, 7b and 7a inside
                       # it. Needs 9999, 9998 and 9997 free. About 43 min
                       # (42.9 at item 16b), test 3 alone about 14: 32
                       # QEMU runs and two rehearsals of its own (21 in test
                       # 3, two of them carried through a watchdog reset),
                       # then ring 7d's gate with its own.
python3 stage8/parts.py --disk stage8/out/molt/disk.G.img   # the molt table and
                       # the door's verdict from a disk image; --serial LOG from
                       # the HP's chart; --seed the record rebuilt; --example
                       # PARTS.md's and SEED.md's worked examples
```

## Ring 8t

```bash
# Ring 8t - trial two (G against B), between rings 8a and 8b; seed 2 in this ring only
./trials/test-trial2.sh   # acceptance tests 1-4 on the 7c twin, every run appended
                       # to trials/out/gate-8t.log with "8t test <n>: PASS|FAIL"
                       # lines and a last "8t gate: PASS|FAIL": TRIALS2.md read
                       # cold, the HP's history rebuilt from the pinned charts;
                       # the G and B rows and the five refusals by '! trial 2' and
                       # by Enter; four sittings to verdict B, the HP's history
                       # to verdict G, the save rule, the times hidden, the boot
                       # line; the payload table and ring 8a's whole gate with
                       # 7d, 7c, 7b and 7a inside it. Starts no broker; needs
                       # 9999, 9998 and 9997 free for 8a's gate. About 66 min.
python3 trials/trials2.py --status trials/out/hp-8t.log   # the blind read of the HP's
                       # chart: procedure facts only, no time or score before a
                       # verdict line; --disk IMG, --serial LOG, --example
```

## Stage 8 ring 8b

```bash
# Stage 8 ring 8b - the first molt; the build is seed 3
./stage8/test-8b.sh    # acceptance tests 1-4 on the 7c twin, every run appended
                       # to stage8/out/gate-8b.log with "8b test <n>: PASS|FAIL"
                       # lines and a last "8b gate: PASS|FAIL": the plan and the
                       # bench read cold, the API-key refusal; the pipeline with
                       # canned parts (fast beats, slow does not); shadow to
                       # live by serial orders and warm restarts, sick to the
                       # watchdog; the payload table and ring 8t's whole gate
                       # with 8a, 7d, 7c, 7b and 7a inside it. Mock only, no
                       # token. Needs 9999, 9998 and 9997 free. About 86 min.
python3 stage8/bench.py --candidate PART.bin   # one boot under -icount at -smp 1:
                       # the differential, the measures and the plan's verdict
                       # (plans/parts/i8042.md, frozen). Exit 0 only on "beats"
python3 stage8/rehearse8b.py PART.bin   # the five-boot rehearsal in the twin
python3 broker/molt.py --grow i8042 --model claude-opus-5-5   # REAL claude -p, the
                       # owner's word only, after Cowork's same-day policy check;
                       # refuses to start with any API key set. --canned and
                       # --backend-cmd are the gate's. --collect serves the
                       # germline and can call no backend at all
python3 stage8/hp-day.py <serial port>   # the HP's day, started by the owner on
                       # mlrig (stage8/HP-8b.md): services, orders, chart to
                       # stage8/out/hp-8b.log, unfrozen; --twin SOCK proves it
PATH=$PWD/stage8/out/toolchain/nasm-3.02/bin:$PATH python3 stage8/parts.py --seed
                       # every seed rebuilt; the private 3.02 from stage8/mknasm.sh
```

## The mock brokers

```bash
# The mock brokers (what the gates talk to; never spend a token)
python3 broker/broker.py --mock --port 9999     # Stage 4
python3 broker/plans.py --mock                  # Stage 6 (answers, apps, installs)
python3 broker/pointer.py --mock                # Stage 6 ring 6c (the point app too)
python3 broker/metal.py --mock                  # Stage 7 (the same table; the twin on SATA)
python3 broker/wire.py --mock                   # Stage 7 ring 7b (the twin with an e1000e on a second cage)
python3 broker/molt.py --mock --part good       # Stage 8 ring 8a: "! molt i8042" answered with a fixture
                                                # (good, wrong, hang, fault or liar); unfrozen
python3 broker/relay.py --bind 127.0.0.1 --port 9997   # the relay in the twin, in front of the broker
                                                # (unfrozen; refuses every bind but 10.0.2.4 and 127.0.0.1)
```

## The hook's payload table

```bash
# The hook's payload table - every freeze and bodyguard case, 0 wrong or exit 1
python3 .claude/hooks/payloads.py
```

## The windowed oracle

Windowed, for the oracle test (Stage 7 ring 7c shape - the twin of the HP,
three terminals: the real broker `python3 broker/wire.py`, the relay
`python3 broker/relay.py --bind 127.0.0.1 --port 9997`, and the machine
booted from a COPY of the stick over qemu-xhci + usb-storage with no
`esp.img` on SATA, on an e1000e carrying the HP's MAC with its cage landing
on the relay; one 64 MB SATA disk the guest partitions on its first boot -
remove `disk.img` first for a blank one, `truncate` on a file already 64 MB
changes nothing, and ring 7a's gate overwrites that path; the copy because QEMU locks
the file it boots and the owner flashes `stick.img` as built; click in the
QEMU window to grab the mouse, Ctrl+Alt+G releases it; for ring 7d's sitting
type `! trial` at the prompt and click the cued item - eighty clicks and
seven rests, Esc abandons it; ring 7b's shape is
the same line with `-drive format=raw,file=stage7/out/esp.img` in place of
the stick's two devices; ring 7a's is that with `virtio-net-pci` and the
guestfwd on 9999 with `python3 broker/metal.py`; Stage 6 keeps its virtio
disks and `broker/pointer.py`, earlier stages drop the drives, the display
and the cage they did not have and point at their own `esp.img` — see
README.md; the HP's own day is `stage7/METAL.md`, ring 8a's `stage8/HP-8a.md`;
ring 8a's twin is this line with `stage8/` for `stage7/` and
`python3 broker/molt.py --mock --part good` as the broker):

```bash
./stage7/mkimage.sh && python3 stage7/mkstick.py
rm -f stage7/out/disk.img; truncate -s 64M stage7/out/disk.img
cp stage7/out/stick.img stage7/out/stick.twin.img
qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd \
  -vga none -device VGA,edid=on,xres=1920,yres=1080 \
  -device qemu-xhci -drive if=none,id=stick,format=raw,file=stage7/out/stick.twin.img -device usb-storage,drive=stick \
  -drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 \
  -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9997' \
  -device e1000e,netdev=n0,mac=6c:3b:e5:3b:86:45 -display gtk,zoom-to-fit=on -serial stdio
```
