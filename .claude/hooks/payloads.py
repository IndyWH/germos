#!/usr/bin/env python3
"""The payload table for .claude/hooks/protect-tests.py.

Every case below is a tool call as the hook would see it, with the verdict it
must give: DENY (exit 2) or ALLOW (exit 0). The table is fed straight into the
hook script, one JSON payload at a time, exactly as the harness feeds it.

Committed from Stage 3 on so that a reviewer can re-run it. The Stage 0, 1 and
2 groups are reconstructed from those stages' commit records - the earlier
tables lived in the session scratchpad - and the Stage 3 groups are new: the
storage bodyguard's denials and allowances (plan item 1) and the Stage 3
freeze (plan item 7).

Run:  python3 .claude/hooks/payloads.py
Exit 0 only if every payload is judged as the table says.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "protect-tests.py")
REPO = os.path.dirname(os.path.dirname(HERE))

DENY, ALLOW = "DENY", "ALLOW"

# The frozen files as of each stage's freeze. Stage 3's are added at item 7.
FROZEN_0 = ["stage0/test.sh", "stage0/checkpixels.py"]
FROZEN_1 = ["stage1/test.sh", "stage1/checkbands.py"]
FROZEN_2 = ["stage2/test.sh", "stage2/checktext.py", "stage2/font8x8.bin"]
FROZEN_3 = ["stage3/test.sh", "stage3/checknotes.py", "stage3/NOTEBOOK.md"]
FROZEN_4 = ["stage4/test.sh", "stage4/checkumbilical.py", "stage4/UMBILICAL.md", "broker/broker.py"]
FROZEN_5 = ["stage5/test.sh", "stage5/checkgermline.py", "stage5/GERMLINE.md",
            "stage5/component.asm", "stage5/component.bin", "broker/germline.py", "broker/rehearse.py"]
FROZEN_6 = ["stage6/test.sh", "stage6/checkglass.py", "stage6/GLASS.md",
            "stage6/app.asm", "stage6/app.bin", "stage6/hog.asm", "stage6/hog.bin",
            "stage6/escapee.asm", "stage6/escapee.bin", "broker/glass.py", "broker/twin.py"]
FROZEN = FROZEN_0 + FROZEN_1 + FROZEN_2


def bash(cmd):
    return ("Bash", {"command": cmd})


def write(path):
    return ("Write", {"file_path": path, "content": "x"})


def edit(path):
    return ("Edit", {"file_path": path, "old_string": "a", "new_string": "b"})


def freeze_cases(paths):
    """The mutation battery every frozen path must survive, and the
    allowances that must survive the freeze."""
    cases = []
    for p in paths:
        base = os.path.basename(p)
        absolute = os.path.join(REPO, p)
        cases += [
            (write(p), DENY, "Write"),
            (edit(p), DENY, "Edit"),
            (write(absolute), DENY, "Write, absolute path"),
            (bash("sed -i 's/PASS/FAIL/' %s" % p), DENY, "sed -i"),
            (bash("echo x | tee %s" % p), DENY, "tee"),
            (bash("echo x > %s" % p), DENY, "redirect >"),
            (bash("echo x >> %s" % p), DENY, "redirect >>"),
            (bash("mv %s %s.bak" % (p, p)), DENY, "mv"),
            (bash("cp /tmp/x %s" % p), DENY, "cp over"),
            (bash("rm -f %s" % p), DENY, "rm"),
            (bash("chmod 644 %s" % p), DENY, "chmod"),
            (bash("git checkout -- %s" % p), DENY, "git checkout"),
            (bash("python3 - <<'EOF'\nopen('%s','w').write('')\nEOF" % p),
             DENY, "writing python heredoc"),
            (bash("sed -i 's/a/b/' %s" % base), DENY, "bare basename, sed -i"),
            (bash("rm %s" % base), DENY, "bare basename, rm"),
            (bash("cat %s" % p), ALLOW, "cat"),
            (bash("grep -n PASS %s | head" % p), ALLOW, "grep"),
            (bash("sha256sum %s" % p), ALLOW, "sha256sum"),
        ]
    return cases


CASES = []

# --- Stage 0, 1 and 2: the freeze -----------------------------------------
CASES += [(c, v, "stage0-2 freeze: " + w) for c, v, w in freeze_cases(FROZEN)]
CASES += [
    (bash("./stage0/test.sh"), ALLOW, "running the Stage 0 gate"),
    (bash("./stage1/test.sh > /tmp/stage1.log 2>&1"), ALLOW, "gate output redirected"),
    (bash("./stage2/test.sh 2>&1 | tail -20"), ALLOW, "gate piped"),
    (bash("python3 stage2/checktext.py --type 8"), ALLOW, "running the checker"),
    (bash("python3 stage2/checktext.py --pixels"), ALLOW, "running the checker"),
    (bash("python3 stage1/checkbands.py 8"), ALLOW, "running the checker"),
    (bash("sed -i 's/48/64/' stage2/mkimage.sh"), ALLOW, "the builder is not frozen"),
    (bash("echo x > stage2/FONT.md"), ALLOW, "paperwork is not frozen"),
    (bash("cp stage2/mkimage.sh stage3/mkimage.sh"), ALLOW, "copying the builder"),
    (bash("chmod +x stage3/mkimage.sh"), ALLOW, "a new stage's builder"),
    (bash("git checkout -- stage2/mkimage.sh"), ALLOW, "git on the builder"),
    (write("stage2/mkimage.sh"), ALLOW, "Write the builder"),
    (write("stage9/test.sh"), ALLOW, "creating another stage's test file"),
    (write("stage9/checktext.py"), ALLOW, "creating another stage's checker"),
    (bash("echo hi > mytest.sh"), ALLOW, "a similarly named file"),
    (bash("echo hi > stage2/out/test.sh.log"), ALLOW, "a similarly named log"),
    (bash("ls stage2/"), ALLOW, "listing"),
    (bash("git log --oneline -5"), ALLOW, "git log"),
]

# --- Stage 3: the storage bodyguard - denials ------------------------------
QEMU = "qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios /usr/share/ovmf/OVMF.fd "
CASES += [(c, DENY, "bodyguard: " + w) for c, w in [
    (bash("ls -l /dev/sda"), "/dev/sd"),
    (bash("dd if=/dev/zero of=/dev/sdb bs=1M"), "dd onto /dev/sd"),
    (bash("cat /dev/nvme0n1 | head -c 512 | xxd"), "/dev/nvme"),
    (bash("ls /dev/disk/by-id"), "/dev/disk"),
    (bash("ls /dev/mapper"), "/dev/mapper"),
    (bash("ls /dev/hda"), "/dev/hd"),
    (bash("ls /dev/vda"), "/dev/vd"),
    (bash("ls /dev/loop0"), "/dev/loop"),
    (bash("ls /dev/mmcblk0"), "/dev/mmcblk"),
    (bash("ls /dev/md0"), "/dev/md"),
    (bash("ls /dev/dm-0"), "/dev/dm-"),
    (bash("ls /dev/block"), "/dev/block"),
    (bash("cat /dev/xyz"), "an unknown /dev node"),
    (bash("ls /dev/"), "the /dev directory itself"),
    (bash("mount stage3/out/notes.img /mnt"), "mount"),
    (bash("umount /mnt"), "umount"),
    (bash("losetup -f stage3/out/notes.img"), "losetup"),
    (bash("mkfs.ext4 stage3/out/notes.img"), "mkfs.ext4"),
    (bash("mkfs -t vfat stage3/out/notes.img"), "mkfs -t"),
    (bash("fdisk -l"), "fdisk"),
    (bash("sfdisk -l"), "sfdisk"),
    (bash("gdisk -l stage3/out/notes.img"), "gdisk"),
    (bash("parted -l"), "parted"),
    (bash("wipefs -a stage3/out/notes.img"), "wipefs"),
    (bash("blkdiscard stage3/out/notes.img"), "blkdiscard"),
    (bash("sudo ls"), "sudo"),
    (bash("echo 'no loop mount is taken' > msg.txt"), "the word in prose"),
    (bash("git commit -m 'no loop mount is taken'"), "the word in a commit message"),
    (bash(QEMU + "-drive format=raw,file=/tmp/x.img"), "-drive outside the repo"),
    (bash(QEMU + "-drive format=raw,file=/home/indy/x.img"), "-drive in the home directory"),
    (bash(QEMU + "-drive format=raw,file=stage3/notes.img,if=virtio"), "-drive in the repo but not under out/"),
    (bash(QEMU + "-drive format=raw,file=../elsewhere/out/x.img"), "-drive climbing with .."),
    (bash(QEMU + "-drive format=raw,file=stage3/out/../../x.img"), "-drive climbing out of out/"),
    (bash(QEMU + "-drive file=$IMG,format=raw"), "-drive with a shell variable"),
    (bash(QEMU + '-drive "format=raw,file=$ESP"'), "-drive with a quoted variable"),
    (bash(QEMU + "-drive format=raw,file=~/x.img"), "-drive with a tilde"),
    (bash(QEMU + "-drive format=raw,file=" + REPO + "/stage3/x.img"), "-drive absolute, not under out/"),
    (bash(QEMU + "-drive format=raw,file=stage3/out/esp.img -drive format=raw,file=/tmp/notes.img,if=virtio"),
     "one good drive and one bad"),
    (bash(QEMU + "-hda stage3/out/notes.img"), "-hda"),
    (bash(QEMU + "-hdb stage3/out/notes.img"), "-hdb"),
    (bash(QEMU + "-cdrom stage3/out/x.iso"), "-cdrom"),
    (bash(QEMU + "-fda stage3/out/x.img"), "-fda"),
    (bash(QEMU + "-blockdev driver=file,filename=stage3/out/notes.img,node-name=d"), "-blockdev"),
    (bash(QEMU + "-pflash /usr/share/ovmf/OVMF.fd"), "-pflash"),
    (bash(QEMU + "-sd stage3/out/x.img"), "-sd"),
    (bash("qemu-img create -f raw /tmp/x.img 16M"), "qemu-img outside out/"),
    (bash("qemu-img convert -O raw stage3/out/a.img /tmp/b.img"), "qemu-img with one bad path"),
    (bash("qemu-img info ~/x.img"), "qemu-img with a tilde"),
    (bash("qemu-img create -f raw $OUT/x.img 16M"), "qemu-img with a variable"),
    (write("/dev/sda"), "Write to a device node"),
    (edit("/dev/nvme0n1"), "Edit of a device node"),
    (write("/dev/null"), "Write even to /dev/null - no reason to"),
    # Was an allowance ("dd from /dev/zero into out/") until Stage 7 ring 7c
    # made dd the flash's verb, denied at the prompt whatever its target;
    # the builders keep their dd inside their scripts, unseen by the hook.
    (bash("dd if=/dev/zero of=stage3/out/x.img bs=1M count=16 status=none"), "dd at the prompt, even into out/ (ring 7c)"),
]]

# --- Stage 3: the storage bodyguard - allowances ---------------------------
CASES += [(c, ALLOW, "bodyguard allows: " + w) for c, w in [
    (bash("truncate -s 16M stage3/out/notes.img"), "truncate in out/"),
    (bash("rm -f stage3/out/notes.img && truncate -s 16M stage3/out/notes.img"), "fresh disk idiom"),
    (bash("head -c 16 /dev/urandom | xxd"), "/dev/urandom as a source"),
    (bash("head -c 8 /dev/random | xxd"), "/dev/random as a source"),
    (bash("cat /dev/null"), "/dev/null"),
    (bash("echo x > /dev/null 2>&1"), "/dev/null as a sink"),
    (bash("cmd < /dev/stdin"), "/dev/stdin"),
    (bash("ls /dev/fd/0"), "/dev/fd"),
    (bash("echo x > /dev/tty"), "/dev/tty"),
    (bash(QEMU + "-drive format=raw,file=stage2/out/esp.img -serial stdio"), "the Stage 2 command"),
    (bash(QEMU + "-drive format=raw,file=stage3/out/esp.img -drive format=raw,file=stage3/out/notes.img,if=virtio -serial stdio"),
     "the Stage 3 command, two drives"),
    (bash(QEMU + "-drive format=raw,file=" + REPO + "/stage3/out/notes.img,if=virtio"), "absolute path under out/"),
    (bash(QEMU + "-drive 'format=raw,file=stage3/out/notes.img,if=virtio'"), "single-quoted -drive"),
    (bash(QEMU + '-drive "format=raw,file=stage3/out/notes.img,if=virtio"'), "double-quoted -drive"),
    (bash(QEMU + "-drive format=raw,file=./stage3/out/notes.img,if=virtio"), "dot-relative path under out/"),
    (bash(QEMU + "-drive format=raw,file=out/notes.img,if=virtio"), "out/ at the top of a stage directory"),
    (bash(QEMU + "-drive if=none,id=x -display none"), "-drive with no file= at all"),
    (bash(QEMU + "-display none -serial stdio"), "-bios alone, no drive"),
    (bash("qemu-img info stage3/out/notes.img"), "qemu-img on out/"),
    (bash("qemu-img create -f raw stage3/out/notes.img 16M"), "qemu-img create in out/"),
    (bash("qemu-img --version"), "qemu-img with no path"),
    (bash("./stage2/test.sh"), "the Stage 2 gate"),
    (bash("./stage3/test.sh"), "the Stage 3 gate"),
    (bash("python3 stage3/checknotes.py --persist 8"), "the Stage 3 checker"),
    (bash("xxd -s 512 -l 64 stage3/out/probe.img"), "reading an image in out/"),
    (bash("echo 'the amount of data'"), "'amount' is not 'mount'"),
    (bash("echo mountpoint"), "'mountpoint' is not 'mount'"),
    (bash("echo departed"), "'departed' is not 'parted'"),
    (bash("git commit -F msg.txt"), "commit message from a file"),
    (bash("grep -c sd stage3/plan.md"), "'sd' without /dev"),
    (bash("ls stage3/out/"), "listing out/"),
    (bash("nasm -f bin stage3/stage3.asm -o stage3/out/BOOTX64.EFI"), "assembling"),
    (bash("mformat -i stage3/out/esp.img -F -v ESP ::"), "mtools on an image in out/"),
    (bash("printf 'info pci\\nquit\\n' | " + QEMU + "-drive format=raw,file=stage2/out/esp.img -monitor stdio"),
     "monitor over stdio"),
    (write("stage3/out/notes.img"), "Write into out/"),
]]

# --- Stage 3: the freeze (plan item 7) --------------------------------------
CASES += [(c, v, "stage3 freeze: " + w) for c, v, w in freeze_cases(FROZEN_3)]
CASES += [
    (write("stage3/NOTEBOOK.md"), DENY, "stage3 freeze: the format is a criterion"),
    (bash("./stage3/test.sh"), ALLOW, "stage3 freeze allows: running the gate"),
    (bash("./stage3/test.sh > stage3/out/gate.log 2>&1"), ALLOW, "stage3 freeze allows: gate output redirected"),
    (bash("python3 stage3/checknotes.py --persist 8"), ALLOW, "stage3 freeze allows: the checker"),
    (bash("python3 stage3/checknotes.py --pixels"), ALLOW, "stage3 freeze allows: the checker"),
    (bash("cat stage3/NOTEBOOK.md"), ALLOW, "stage3 freeze allows: reading the format"),
    (bash("grep -n NOTE stage3/NOTEBOOK.md"), ALLOW, "stage3 freeze allows: grepping the format"),
    (bash("sed -i 's/48/64/' stage3/mkimage.sh"), ALLOW, "stage3 freeze allows: the builder is not frozen"),
    (write("stage3/mkimage.sh"), ALLOW, "stage3 freeze allows: Write the builder"),
    (write("stage3/stage3.asm"), ALLOW, "stage3 freeze allows: Write the implementation"),
    (write("stage3/plan.md"), ALLOW, "stage3 freeze allows: the plan is paperwork"),
    # Was stage4/test.sh until Stage 4 froze it, then stage5/test.sh until
    # Stage 5 did, then stage6/test.sh until ring 6a did - the case moves on
    # a stage each time.
    (write("stage8/test.sh"), ALLOW, "stage3 freeze allows: creating a later stage's test file"),
    (write("stage4/NOTEBOOK.md"), ALLOW, "stage3 freeze allows: a later stage's format document"),
    (bash("nasm -f bin stage3/stage3.asm -o stage3/out/BOOTX64.EFI"), ALLOW, "stage3 freeze allows: assembling"),
]

# --- Stage 4: the freeze (plan item 7), and the cage in commands -------------
CAGE = ("-netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' "
        "-device virtio-net-pci,netdev=n0,mac=52:54:00:a1:04:01 ")
CASES += [(c, v, "stage4 freeze: " + w) for c, v, w in freeze_cases(FROZEN_4)]
CASES += [
    (write("stage4/UMBILICAL.md"), DENY, "stage4 freeze: the protocol is a criterion"),
    (write("broker/broker.py"), DENY, "stage4 freeze: the mock's framing and record are criteria"),
    (bash("python3 - <<'EOF'\nopen('broker/broker.py','a').write('x')\nEOF"), DENY, "stage4 freeze: python appending to the broker"),
    (bash("./stage4/test.sh"), ALLOW, "stage4 freeze allows: running the gate"),
    (bash("./stage4/test.sh > stage4/out/gate.log 2>&1"), ALLOW, "stage4 freeze allows: gate output redirected"),
    (bash("python3 stage4/checkumbilical.py --question 8"), ALLOW, "stage4 freeze allows: the checker"),
    (bash("python3 stage4/checkumbilical.py --cage"), ALLOW, "stage4 freeze allows: the checker"),
    (bash("python3 broker/broker.py --mock"), ALLOW, "stage4 freeze allows: running the mock"),
    (bash("python3 broker/broker.py --mock --port 9999 --record stage4/out/broker.jsonl"),
     ALLOW, "stage4 freeze allows: the mock with a record file"),
    (bash("python3 broker/broker.py"), ALLOW, "stage4 freeze allows: the real broker"),
    (bash("cat stage4/UMBILICAL.md"), ALLOW, "stage4 freeze allows: reading the protocol"),
    (bash("grep -n frame stage4/UMBILICAL.md broker/broker.py"), ALLOW, "stage4 freeze allows: grepping"),
    (bash("sed -i 's/48/64/' stage4/mkimage.sh"), ALLOW, "stage4 freeze allows: the builder is not frozen"),
    (write("stage4/mkimage.sh"), ALLOW, "stage4 freeze allows: Write the builder"),
    (write("broker/claude_backend.py"), ALLOW, "stage4 freeze allows: the Claude backend is not frozen"),
    (bash("sed -i 's/--bare//' broker/claude_backend.py"), ALLOW, "stage4 freeze allows: fixing the backend's flags"),
    (write("stage4/stage4.asm"), ALLOW, "stage4 freeze allows: Write the implementation"),
    (write("stage4/plan.md"), ALLOW, "stage4 freeze allows: the plan is paperwork"),
    (write("stage8/test.sh"), ALLOW, "stage4 freeze allows: creating a later stage's test file"),
    (write("stage5/UMBILICAL.md"), ALLOW, "stage4 freeze allows: a later stage's document"),
    (bash("nasm -f bin stage4/stage4.asm -o stage4/out/BOOTX64.EFI"), ALLOW, "stage4 freeze allows: assembling"),
    (bash(QEMU + "-drive format=raw,file=stage4/out/esp.img -drive format=raw,file=stage4/out/notes.img,if=virtio "
          + CAGE + "-serial stdio"), ALLOW, "bodyguard allows: the Stage 4 command with the cage"),
    (bash(QEMU + "-drive format=raw,file=stage4/out/esp.img -drive format=raw,file=stage4/out/notes.img,if=virtio "
          + CAGE + "-display none -serial file:stage4/out/serial.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's Stage 4 command"),
    (bash("nc -N 127.0.0.1 9999"), ALLOW, "bodyguard allows: netcat to loopback"),
    (bash("echo 'restrict=on and one guestfwd on the netdev'"), ALLOW, "bodyguard allows: the cage's words in prose"),
    (bash("ss -ltn | grep 9999"), ALLOW, "bodyguard allows: looking at listeners"),
    (bash("truncate -s 16M stage4/out/notes.img"), ALLOW, "bodyguard allows: a fresh Stage 4 disk"),
    (bash(QEMU + "-drive format=raw,file=/tmp/esp.img " + CAGE), DENY, "bodyguard: the cage does not excuse a bad drive"),
]

# --- Stage 5: the freeze (plan item 8), the -o rule, the rehearsal's cage ----
CAGE5 = ("-netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' "
         "-device virtio-net-pci,netdev=n0,mac=52:54:00:a1:05:01 ")
REHEARSAL_CAGE = ("-netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9998' "
                  "-device virtio-net-pci,netdev=n0 ")
CASES += [(c, v, "stage5 freeze: " + w) for c, v, w in freeze_cases(FROZEN_5)]
CASES += [
    (write("stage5/GERMLINE.md"), DENY, "stage5 freeze: the wire document is a criterion"),
    (write("stage5/component.asm"), DENY, "stage5 freeze: the test component's source"),
    (write("stage5/component.bin"), DENY, "stage5 freeze: the test component's binary"),
    (write("broker/germline.py"), DENY, "stage5 freeze: the mock table, record and cache are criteria"),
    (write("broker/rehearse.py"), DENY, "stage5 freeze: the rehearsal's verdicts are criteria"),
    (bash("nasm -f bin stage5/component.asm -o stage5/component.bin"), DENY, "stage5 freeze: -o over the frozen binary (the side door)"),
    (bash("cd stage5 && nasm -f bin component.asm -o component.bin"), DENY, "stage5 freeze: -o over the bare basename"),
    (bash("nasm -f bin stage5/component.asm -o=stage5/component.bin"), DENY, "stage5 freeze: -o= over the frozen binary"),
    (bash("gcc -o broker/rehearse.py x.c"), DENY, "stage5 freeze: any tool's -o aimed at a frozen file"),
    (bash("python3 - <<'EOF'\nopen('broker/germline.py','w').write('x')\nEOF"), DENY, "stage5 freeze: python writing the broker"),
    (bash("nasm -f bin stage5/component.asm -o stage5/out/component.check.bin"), ALLOW, "stage5 freeze allows: the checker's self-check assembles to out/"),
    (bash("nasm -f bin stage5/stage5.asm -o stage5/out/BOOTX64.EFI"), ALLOW, "stage5 freeze allows: assembling the implementation"),
    (bash("./stage5/test.sh"), ALLOW, "stage5 freeze allows: running the gate"),
    (bash("./stage5/test.sh > stage5/out/gate.log 2>&1"), ALLOW, "stage5 freeze allows: gate output redirected"),
    (bash("python3 stage5/checkgermline.py --grow 2"), ALLOW, "stage5 freeze allows: the checker"),
    (bash("python3 stage5/checkgermline.py --germline"), ALLOW, "stage5 freeze allows: the checker"),
    (bash("python3 broker/germline.py --mock --port 9999 --germline stage5/out/germline --image stage5/out/esp.img "
          "--workdir stage5/out/rehearsal --record stage5/out/broker.germline.jsonl"),
     ALLOW, "stage5 freeze allows: the mock with the gate's germline"),
    (bash("python3 broker/germline.py"), ALLOW, "stage5 freeze allows: the real broker"),
    (bash("python3 broker/rehearse.py stage5/component.bin"), ALLOW, "stage5 freeze allows: a hand rehearsal"),
    (bash("cat stage5/GERMLINE.md"), ALLOW, "stage5 freeze allows: reading the wire document"),
    (bash("grep -n grow stage5/GERMLINE.md broker/germline.py broker/rehearse.py"), ALLOW, "stage5 freeze allows: grepping"),
    (bash("sha256sum stage5/component.bin"), ALLOW, "stage5 freeze allows: hashing the binary"),
    (bash("objdump -D -b binary -m i386:x86-64 stage5/component.bin"), ALLOW, "stage5 freeze allows: disassembling the binary"),
    (bash("sed -i 's/48/64/' stage5/mkimage.sh"), ALLOW, "stage5 freeze allows: the builder is not frozen"),
    (write("stage5/mkimage.sh"), ALLOW, "stage5 freeze allows: Write the builder"),
    (write("stage5/stage5.asm"), ALLOW, "stage5 freeze allows: Write the implementation"),
    (write("broker/claude_backend.py"), ALLOW, "stage5 freeze allows: the Claude backend is not frozen"),
    (bash("sed -i 's/ASSEMBLY_ROUNDS = 3/ASSEMBLY_ROUNDS = 4/' broker/claude_backend.py"), ALLOW, "stage5 freeze allows: fixing the backend"),
    (write("stage5/plan.md"), ALLOW, "stage5 freeze allows: the plan is paperwork"),
    (write("stage8/test.sh"), ALLOW, "stage5 freeze allows: creating the next stage's test file"),
    (write("stage6/GERMLINE.md"), ALLOW, "stage5 freeze allows: a later stage's document"),
    (write("stage6/component.bin"), ALLOW, "stage5 freeze allows: a later stage's component"),
    (bash("ls germline/"), ALLOW, "stage5 freeze allows: the germline directory is not the broker file"),
    (bash("rm -rf germline/"), ALLOW, "stage5 freeze allows: clearing the machine's own cache"),
    (bash("rm -rf stage5/out/germline stage5/out/rehearsal"), ALLOW, "stage5 freeze allows: clearing the gate's scratch"),
    (bash("git add stage5/GERMLINE.md broker/germline.py broker/rehearse.py"), ALLOW, "stage5 freeze allows: git add"),
    (bash("git commit -F msg.txt"), ALLOW, "stage5 freeze allows: commit from a file"),
    (bash(QEMU + "-drive format=raw,file=stage5/out/esp.img -drive format=raw,file=stage5/out/notes.img,if=virtio "
          + CAGE5 + "-display none -serial file:stage5/out/serial.grow.8.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's Stage 5 command"),
    (bash("qemu-system-x86_64 -machine q35 -m 256M -smp 2 -bios /usr/share/ovmf/OVMF.fd "
          "-drive format=raw,file=stage5/out/esp.img -drive format=raw,file=stage5/out/rehearsal/notes.img,if=virtio "
          + REHEARSAL_CAGE + "-display none -serial file:stage5/out/rehearsal/serial.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the rehearsal's command, drives under stage5/out/rehearsal/"),
    # Item 8b: the twin boots a private copy of the image, itself under the
    # rehearsal's scratch directory - QEMU locks the file a guest boots from.
    (bash("qemu-system-x86_64 -machine q35 -m 256M -smp 2 -bios /usr/share/ovmf/OVMF.fd "
          "-drive format=raw,file=stage5/out/rehearsal/esp.img -drive format=raw,file=stage5/out/rehearsal/notes.img,if=virtio "
          + REHEARSAL_CAGE + "-display none -serial file:stage5/out/rehearsal/serial.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the rehearsal's command with the twin's private copy of the image"),
    (bash("cp stage5/out/esp.img stage5/out/rehearsal/esp.img"), ALLOW, "bodyguard allows: copying the image for the twin, out/ to out/"),
    (bash(QEMU + "-drive format=raw,file=stage5/out/esp.img -drive format=raw,file=germline/notes.img,if=virtio " + REHEARSAL_CAGE),
     DENY, "bodyguard: a drive under germline/ is not under an out/"),
    (bash("echo 'the germline caches a component after rehearsal'"), ALLOW, "bodyguard allows: the stage's words in prose"),
]

# --- Stage 6 ring 6a: the freeze (plan item 8), the display, the twin ------
CAGE6 = ("-netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' "
         "-device virtio-net-pci,netdev=n0,mac=52:54:00:a1:06:01 ")
TWIN_CAGE = ("-netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9998' "
             "-device virtio-net-pci,netdev=n0 ")
DISPLAY6 = "-vga none -device VGA,edid=on,xres=1440,yres=1440 "
CASES += [(c, v, "stage6 freeze: " + w) for c, v, w in freeze_cases(FROZEN_6)]
CASES += [
    (write("stage6/GLASS.md"), DENY, "stage6 freeze: the glass document is a criterion"),
    (write("stage6/app.asm"), DENY, "stage6 freeze: the test app's source"),
    (write("stage6/app.bin"), DENY, "stage6 freeze: the test app's binary"),
    (write("stage6/hog.bin"), DENY, "stage6 freeze: the hog's binary"),
    (write("stage6/escapee.bin"), DENY, "stage6 freeze: the escapee's binary"),
    (write("broker/glass.py"), DENY, "stage6 freeze: the mock table, record and cache are criteria"),
    (write("broker/twin.py"), DENY, "stage6 freeze: the twin's verdicts are criteria"),
    (bash("nasm -f bin stage6/app.asm -o stage6/app.bin"), DENY, "stage6 freeze: -o over the frozen test app"),
    (bash("nasm -f bin stage6/hog.asm -o stage6/hog.bin"), DENY, "stage6 freeze: -o over the frozen hog"),
    (bash("nasm -f bin stage6/escapee.asm -o stage6/escapee.bin"), DENY, "stage6 freeze: -o over the frozen escapee"),
    (bash("cd stage6 && nasm -f bin app.asm -o app.bin"), DENY, "stage6 freeze: -o over the bare basename"),
    (bash("python3 - <<'EOF'\nopen('broker/twin.py','w').write('x')\nEOF"), DENY, "stage6 freeze: python writing the twin"),
    (bash("nasm -f bin stage6/app.asm -o stage6/out/app.check.bin"), ALLOW, "stage6 freeze allows: the checker's self-check assembles to out/"),
    (bash("nasm -f bin stage6/hog.asm -o stage6/out/hog.check.bin"), ALLOW, "stage6 freeze allows: the hog's self-check to out/"),
    (bash("nasm -f bin stage6/stage6.asm -o stage6/out/BOOTX64.EFI"), ALLOW, "stage6 freeze allows: assembling the implementation"),
    (bash("./stage6/test.sh"), ALLOW, "stage6 freeze allows: running the gate"),
    (bash("./stage6/test.sh > stage6/out/gate.log 2>&1"), ALLOW, "stage6 freeze allows: gate output redirected"),
    (bash("python3 stage6/checkglass.py --glass 2"), ALLOW, "stage6 freeze allows: the checker"),
    (bash("python3 stage6/checkglass.py --truth"), ALLOW, "stage6 freeze allows: the checker"),
    (bash("python3 stage6/checkglass.py --one-core"), ALLOW, "stage6 freeze allows: the checker"),
    (bash("python3 broker/glass.py --mock --port 9999 --germline stage6/out/germline --image stage6/out/esp.img "
          "--workdir stage6/out/rehearsal --record stage6/out/broker.truth.jsonl"),
     ALLOW, "stage6 freeze allows: the mock with the gate's germline"),
    (bash("python3 broker/glass.py"), ALLOW, "stage6 freeze allows: the real broker"),
    (bash("python3 broker/twin.py stage6/app.bin"), ALLOW, "stage6 freeze allows: a hand rehearsal in the twin"),
    (bash("cat stage6/GLASS.md"), ALLOW, "stage6 freeze allows: reading the glass document"),
    (bash("grep -n obs stage6/GLASS.md broker/glass.py broker/twin.py"), ALLOW, "stage6 freeze allows: grepping"),
    (bash("sha256sum stage6/app.bin stage6/hog.bin stage6/escapee.bin"), ALLOW, "stage6 freeze allows: hashing the fixtures"),
    (bash("objdump -D -b binary -m i386:x86-64 stage6/escapee.bin"), ALLOW, "stage6 freeze allows: disassembling a fixture"),
    (bash("sed -i 's/48/64/' stage6/mkimage.sh"), ALLOW, "stage6 freeze allows: the builder is not frozen"),
    (write("stage6/mkimage.sh"), ALLOW, "stage6 freeze allows: Write the builder"),
    (write("stage6/stage6.asm"), ALLOW, "stage6 freeze allows: Write the implementation"),
    (write("broker/claude_backend.py"), ALLOW, "stage6 freeze allows: the Claude backend is not frozen"),
    (write("stage6/plan-6a.md"), ALLOW, "stage6 freeze allows: the plan is paperwork"),
    (write("stage6/plan-6b.md"), ALLOW, "stage6 freeze allows: the next ring's plan"),
    (write("stage8/test.sh"), ALLOW, "stage6 freeze allows: creating the next stage's test file"),
    # Were stage6/PLANS.md and stage6/HOME.md until ring 6b froze them - the
    # case moves on a ring, as the "later stage's test file" case does.
    (write("stage6/POINTER.md"), ALLOW, "stage6 freeze allows: a later ring's document"),
    (bash("rm -rf stage6/out/germline stage6/out/rehearsal"), ALLOW, "stage6 freeze allows: clearing the gate's scratch"),
    (bash("git add stage6/GLASS.md broker/glass.py broker/twin.py"), ALLOW, "stage6 freeze allows: git add"),
    (bash("git commit -F msg.txt"), ALLOW, "stage6 freeze allows: commit from a file"),
    (bash(QEMU + DISPLAY6 + "-drive format=raw,file=stage6/out/esp.img -drive format=raw,file=stage6/out/notes.img,if=virtio "
          + CAGE6 + "-serial stdio"), ALLOW, "bodyguard allows: the oracle's Stage 6 command with the display"),
    (bash(QEMU + DISPLAY6 + "-drive format=raw,file=stage6/out/esp.img -drive format=raw,file=stage6/out/notes.img,if=virtio "
          + CAGE6 + "-display none -serial file:stage6/out/serial.truth.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's Stage 6 command"),
    (bash(QEMU + "-vga none -device VGA,edid=off -drive format=raw,file=stage6/out/esp.img "
          "-drive format=raw,file=stage6/out/serial.noedid.img,if=virtio " + CAGE6 + "-display none -serial stdio"),
     ALLOW, "bodyguard allows: the no-EDID run"),
    (bash("qemu-system-x86_64 -machine q35 -m 256M -smp 2 -bios /usr/share/ovmf/OVMF.fd " + DISPLAY6
          + "-drive format=raw,file=stage6/out/rehearsal/esp.img -drive format=raw,file=stage6/out/rehearsal/notes.img,if=virtio "
          + TWIN_CAGE + "-display none -serial file:stage6/out/rehearsal/serial.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the twin's command with its private copy of the image"),
    (bash("cp stage6/out/esp.img stage6/out/rehearsal/esp.img"), ALLOW, "bodyguard allows: copying the image for the twin, out/ to out/"),
    (bash("printf 'info pci\\nxp /128xb 0x81082000\\nquit\\n' | " + QEMU + DISPLAY6
          + "-drive format=raw,file=stage6/out/esp.img -display none -monitor stdio"),
     ALLOW, "bodyguard allows: reading the EDID BAR through the monitor"),
    (bash(QEMU + DISPLAY6 + "-drive format=raw,file=/tmp/esp.img " + CAGE6), DENY, "bodyguard: the display does not excuse a bad drive"),
    (bash("echo 'the glass core composites the surfaces from the obs page'"), ALLOW, "bodyguard allows: the ring's words in prose"),
]

# --- Stage 6 ring 6b: the freeze (plan item 8), the home drive, the twin ----
# The twelve paths of ring 6b's plan decision 13; the mutation battery on
# each; the -o side door on each new binary; the allowances measured before
# the plan - the three-drive gate and oracle lines at 1920x1080, the twin's
# line with its sibling home image, the truncates, the gate, the checker,
# the mock and the real broker, reading the plans, the unfrozen four.
DISPLAY6B = "-vga none -device VGA,edid=on,xres=1920,yres=1080 "
CAGE6B = "-netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0,mac=52:54:00:a1:06:02 "
FROZEN_6B = ["stage6/PLANS.md", "stage6/HOME.md", "plans/echo.md", "plans/liar.md", "plans/calculator.md",
             "stage6/echo.asm", "stage6/echo.bin", "stage6/liar.asm", "stage6/liar.bin",
             "broker/plans.py", "stage6/test-6b.sh", "stage6/checkplans.py"]
CASES += [(c, v, "ring 6b freeze: " + w) for c, v, w in freeze_cases(FROZEN_6B)]
CASES += [
    (write("stage6/PLANS.md"), DENY, "ring 6b freeze: the plan document is a criterion"),
    (write("stage6/HOME.md"), DENY, "ring 6b freeze: the home image's format is a criterion"),
    (write("plans/calculator.md"), DENY, "ring 6b freeze: the owner's approved plan"),
    (write("plans/echo.md"), DENY, "ring 6b freeze: the twin's tests are the plan"),
    (write("broker/plans.py"), DENY, "ring 6b freeze: the dispatch, the key, the mock table and the record"),
    (write("stage6/checkplans.py"), DENY, "ring 6b freeze: the checker"),
    (write("stage6/test-6b.sh"), DENY, "ring 6b freeze: the gate"),
    (bash("nasm -f bin stage6/echo.asm -o stage6/echo.bin"), DENY, "ring 6b freeze: -o over the frozen echo"),
    (bash("nasm -f bin stage6/liar.asm -o stage6/liar.bin"), DENY, "ring 6b freeze: -o over the frozen liar"),
    (bash("python3 - <<'EOF'\nopen('plans/echo.md','w').write('x')\nEOF"), DENY, "ring 6b freeze: python writing a plan"),
    (bash("sed -i 's/expect/expect not/' plans/liar.md"), DENY, "ring 6b freeze: sed -i on a plan"),
    (bash("nasm -f bin stage6/echo.asm -o stage6/out/echo.check.bin"), ALLOW, "ring 6b freeze allows: the checker's self-check to out/"),
    (bash("nasm -f bin stage6/liar.asm -o stage6/out/liar.check.bin"), ALLOW, "ring 6b freeze allows: the liar's self-check to out/"),
    (bash("./stage6/test-6b.sh"), ALLOW, "ring 6b freeze allows: running the gate"),
    (bash("./stage6/test-6b.sh > stage6/out/gate6b.log 2>&1"), ALLOW, "ring 6b freeze allows: gate output redirected"),
    (bash("./stage6/test.sh"), ALLOW, "ring 6b freeze allows: ring 6a's gate as the regression"),
    (bash("python3 stage6/checkplans.py --install 2"), ALLOW, "ring 6b freeze allows: the checker"),
    (bash("python3 stage6/checkplans.py --store"), ALLOW, "ring 6b freeze allows: the checker"),
    (bash("python3 broker/plans.py --mock --port 9999 --germline stage6/out/germline --image stage6/out/esp.img "
          "--workdir stage6/out/rehearsal/twin --record stage6/out/broker.install.2.jsonl --plans plans"),
     ALLOW, "ring 6b freeze allows: the mock with the gate's germline"),
    (bash("python3 broker/plans.py"), ALLOW, "ring 6b freeze allows: the real broker"),
    (bash("python3 broker/plans.py --rehearse stage6/echo.bin plans/echo.md --lines 16"), ALLOW, "ring 6b freeze allows: a hand rehearsal against a plan"),
    (bash("cat plans/calculator.md"), ALLOW, "ring 6b freeze allows: reading a plan"),
    (bash("cat stage6/PLANS.md stage6/HOME.md"), ALLOW, "ring 6b freeze allows: reading the documents"),
    (bash("grep -n home stage6/HOME.md broker/plans.py stage6/checkplans.py"), ALLOW, "ring 6b freeze allows: grepping"),
    (bash("sha256sum stage6/echo.bin stage6/liar.bin plans/calculator.md"), ALLOW, "ring 6b freeze allows: hashing"),
    (bash("objdump -D -b binary -m i386:x86-64 stage6/liar.bin"), ALLOW, "ring 6b freeze allows: disassembling a fixture"),
    (write("stage6/stage6.asm"), ALLOW, "ring 6b freeze allows: Write the implementation"),
    (write("stage6/mkimage.sh"), ALLOW, "ring 6b freeze allows: the builder is not frozen"),
    (write("broker/claude_backend.py"), ALLOW, "ring 6b freeze allows: the Claude backend is not frozen"),
    (write("stage6/plan-6b.md"), ALLOW, "ring 6b freeze allows: the plan is paperwork"),
    (write("stage6/plan-6c.md"), ALLOW, "ring 6b freeze allows: the next ring's plan"),
    (write("plans/clock.md"), ALLOW, "ring 6b freeze allows: a new plan is not a frozen one"),
    # Was stage6/POINTER.md until ring 6c put its document into GLASS.md by
    # the owner's hand - the case moves on a stage.
    (write("stage7/GLASS.md"), ALLOW, "ring 6b freeze allows: a later stage's document"),
    (bash("rm -rf stage6/out/germline stage6/out/rehearsal"), ALLOW, "ring 6b freeze allows: clearing the gate's scratch"),
    (bash("truncate -s 16M stage6/out/home.img"), ALLOW, "bodyguard allows: the home image under out/"),
    (bash("truncate -s 16M stage6/out/rehearsal/home.img"), ALLOW, "bodyguard allows: the twin's home image under out/"),
    (bash("cp stage6/out/esp.img stage6/out/rehearsal/twin/esp.img"), ALLOW, "bodyguard allows: the twin's copy, out/ to out/"),
    (bash("git add stage6/PLANS.md stage6/HOME.md plans/echo.md plans/liar.md plans/calculator.md broker/plans.py"), ALLOW, "ring 6b freeze allows: git add"),
    (bash(QEMU + DISPLAY6B + "-drive format=raw,file=stage6/out/esp.img -drive format=raw,file=stage6/out/notes.img,if=virtio "
          "-drive format=raw,file=stage6/out/home.img,if=virtio " + CAGE6B + "-serial stdio"),
     ALLOW, "bodyguard allows: the oracle's ring 6b command with three drives"),
    (bash(QEMU + DISPLAY6B + "-drive format=raw,file=stage6/out/esp.img -drive format=raw,file=stage6/out/notes.img,if=virtio "
          "-drive format=raw,file=stage6/out/home.img,if=virtio " + CAGE6B
          + "-display none -serial file:stage6/out/serial.store.b.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's ring 6b command"),
    (bash("qemu-system-x86_64 -machine q35 -m 256M -smp 2 -bios /usr/share/ovmf/OVMF.fd " + DISPLAY6B
          + "-drive format=raw,file=stage6/out/rehearsal/twin/esp.img -drive format=raw,file=stage6/out/rehearsal/twin/notes.img,if=virtio "
          "-drive format=raw,file=stage6/out/rehearsal/home.img,if=virtio " + TWIN_CAGE
          + "-display none -serial file:stage6/out/rehearsal/twin/serial.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the twin's command with its sibling home image"),
    (bash(QEMU + DISPLAY6B + "-drive format=raw,file=stage6/out/esp.img -drive format=raw,file=/home/indy/home.img,if=virtio " + CAGE6B),
     DENY, "bodyguard: a home image outside out/ is denied like any other drive"),
    (bash("echo 'the store of plans keeps the previous build for undo'"), ALLOW, "bodyguard allows: the ring's words in prose"),
]


# --- Stage 6 ring 6c: the freeze (plan item 8), the mouse, the owner's append --
# The five paths of ring 6c's plan decision 14; the mutation battery on
# each; the -o side door on the new binary; the allowances measured before
# the plan - the 6c gate, oracle and checker lines with this ring's MAC, the
# mock and the real broker, the hand rehearsal, the three checker modes, the
# read-only proofs of GLASS.md's old text and git add on it, the probe's
# mouse line - and the denials: the append into GLASS.md is the owner's.
CAGE6C = "-netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0,mac=52:54:00:a1:06:03 "
FROZEN_6C = ["stage6/pointer.asm", "stage6/pointer.bin", "broker/pointer.py", "stage6/test-6c.sh", "stage6/checkpointer.py"]
CASES += [(c, v, "ring 6c freeze: " + w) for c, v, w in freeze_cases(FROZEN_6C)]
CASES += [
    (write("stage6/pointer.asm"), DENY, "ring 6c freeze: the point app's source"),
    (write("stage6/pointer.bin"), DENY, "ring 6c freeze: the point app's binary"),
    (write("broker/pointer.py"), DENY, "ring 6c freeze: the mock row, the refusal and the section's Python"),
    (write("stage6/checkpointer.py"), DENY, "ring 6c freeze: the checker"),
    (write("stage6/test-6c.sh"), DENY, "ring 6c freeze: the gate"),
    (write("stage6/GLASS.md"), DENY, "ring 6c freeze: the glass document, its 6c section included"),
    (bash("nasm -f bin stage6/pointer.asm -o stage6/pointer.bin"), DENY, "ring 6c freeze: -o over the frozen point app"),
    (bash("cat stage6/out/glass-6c-section.md >> stage6/GLASS.md"), DENY, "ring 6c freeze: the append is the owner's hand, never this session's"),
    (bash("python3 - <<'EOF'\nopen('broker/pointer.py','w').write('x')\nEOF"), DENY, "ring 6c freeze: python writing the broker module"),
    (bash("sed -i 's/hit/miss/' stage6/checkpointer.py"), DENY, "ring 6c freeze: sed -i on the checker"),
    (bash("nasm -f bin stage6/pointer.asm -o stage6/out/pointer.check.bin"), ALLOW, "ring 6c freeze allows: the checker's self-check to out/"),
    (bash("./stage6/test-6c.sh"), ALLOW, "ring 6c freeze allows: running the gate"),
    (bash("./stage6/test-6c.sh > stage6/out/gate6c.log 2>&1"), ALLOW, "ring 6c freeze allows: gate output redirected"),
    (bash("./stage6/test.sh && ./stage6/test-6b.sh"), ALLOW, "ring 6c freeze allows: the two earlier ring gates as regressions"),
    (bash("python3 stage6/checkpointer.py --serial 8"), ALLOW, "ring 6c freeze allows: the checker"),
    (bash("python3 stage6/checkpointer.py --point 2"), ALLOW, "ring 6c freeze allows: the checker"),
    (bash("python3 stage6/checkpointer.py --truth"), ALLOW, "ring 6c freeze allows: the checker"),
    (bash("python3 broker/pointer.py --mock --port 9999 --germline stage6/out/germline --image stage6/out/esp.img "
          "--workdir stage6/out/rehearsal/twin --record stage6/out/broker.point.2.jsonl --plans plans"),
     ALLOW, "ring 6c freeze allows: the mock with the gate's germline"),
    (bash("python3 broker/pointer.py"), ALLOW, "ring 6c freeze allows: the real broker"),
    (bash("python3 broker/pointer.py --rehearse-app stage6/pointer.bin 'point app'"), ALLOW, "ring 6c freeze allows: a hand rehearsal in this ring's twin"),
    (bash("python3 broker/twin.py stage6/pointer.bin 'point app'"), ALLOW, "ring 6c freeze allows: a hand rehearsal in the 6a twin"),
    (bash("cat stage6/out/glass-6c-section.md"), ALLOW, "ring 6c freeze allows: reading the section's draft"),
    (bash("head -n 777 stage6/GLASS.md | sha256sum"), ALLOW, "ring 6c freeze allows: hashing the old text"),
    (bash("git show HEAD:stage6/GLASS.md | sha256sum"), ALLOW, "ring 6c freeze allows: hashing the committed text"),
    (bash("cmp <(head -n 777 stage6/GLASS.md) <(git show HEAD:stage6/GLASS.md)"), ALLOW, "ring 6c freeze allows: proving the old text byte-identical"),
    (bash("git diff --stat stage6/GLASS.md"), ALLOW, "ring 6c freeze allows: the diff of the owner's append"),
    (bash("git add stage6/GLASS.md stage6/plan-6c.md"), ALLOW, "ring 6c freeze allows: git add after the owner's append"),
    (bash("grep -n POINTER2 stage6/GLASS.md broker/pointer.py stage6/checkpointer.py"), ALLOW, "ring 6c freeze allows: grepping"),
    (bash("sha256sum stage6/pointer.bin stage6/app.bin"), ALLOW, "ring 6c freeze allows: hashing the fixtures"),
    (bash("objdump -D -b binary -m i386:x86-64 stage6/pointer.bin"), ALLOW, "ring 6c freeze allows: disassembling the fixture"),
    (write("stage6/stage6.asm"), ALLOW, "ring 6c freeze allows: Write the implementation"),
    (write("stage6/mkimage.sh"), ALLOW, "ring 6c freeze allows: the builder is not frozen"),
    (write("broker/claude_backend.py"), ALLOW, "ring 6c freeze allows: the Claude backend is not frozen"),
    (write("stage6/plan-6c.md"), ALLOW, "ring 6c freeze allows: the plan is paperwork"),
    (write("stage6/out/glass-6c-section.md"), ALLOW, "ring 6c freeze allows: the section's draft under out/"),
    (write("stage8/test.sh"), ALLOW, "ring 6c freeze allows: creating the next stage's test file"),
    (write("stage7/pointer.py"), ALLOW, "ring 6c freeze allows: a later stage's file of the same name"),
    (bash("rm -rf stage6/out/germline stage6/out/rehearsal stage6/out/probe6c"), ALLOW, "ring 6c freeze allows: clearing the gate's scratch and the probe"),
    (bash("git add stage6/pointer.asm stage6/pointer.bin broker/pointer.py stage6/test-6c.sh stage6/checkpointer.py"), ALLOW, "ring 6c freeze allows: git add"),
    (bash(QEMU + DISPLAY6B + "-drive format=raw,file=stage6/out/esp.img -drive format=raw,file=stage6/out/notes.img,if=virtio "
          "-drive format=raw,file=stage6/out/home.img,if=virtio " + CAGE6C + "-serial stdio"),
     ALLOW, "bodyguard allows: the oracle's ring 6c command with three drives"),
    (bash(QEMU + DISPLAY6B + "-drive format=raw,file=stage6/out/esp.img -drive format=raw,file=stage6/out/notes.img,if=virtio "
          "-drive format=raw,file=stage6/out/home.img,if=virtio " + CAGE6C
          + "-display none -serial file:stage6/out/serial.point.2.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's ring 6c command"),
    (bash("printf 'mouse_move 10 20\\nmouse_button 1\\nmouse_button 0\\nquit\\n' | " + QEMU
          + "-drive format=raw,file=stage6/out/probe6c/mouse.img -display none -monitor stdio"),
     ALLOW, "bodyguard allows: the mouse probe under out/, driven through the monitor"),
    (bash(QEMU + DISPLAY6B + "-drive format=raw,file=stage6/out/esp.img -drive format=raw,file=/home/indy/mouse.img,if=virtio " + CAGE6C),
     DENY, "bodyguard: a drive outside out/ is denied whatever the ring"),
    (bash("echo 'the pointer clicks the choices row and the strip says pt'"), ALLOW, "bodyguard allows: the ring's words in prose"),
]


# --- Stage 7 ring 7a: the freeze (plan item 8, amendment A3), the SATA disk --
# The three paths frozen at item 8 (broker/metal.py joins at item 10, after
# the gate has passed nine of nine through it - its cases are added then);
# the mutation battery on each; the allowances measured before the plan -
# the gate, the checker's modes, the mock and the real broker, the hand
# rehearsals, the Stage 7 QEMU lines of the gate, the checker, the twin
# (the frozen virtio notes disk beside the SATA disk) and the oracle, the
# 64 MB disk and its copies under out/, the two host witnesses, the probe's
# scratch - and the denials: a SATA drive whose file= lies outside out/, a
# disk attached by a shorthand. The "next stage's test file" case above has
# moved on to stage8/test.sh.
QEMU7 = "qemu-system-x86_64 -machine q35 -cpu IvyBridge -m 256M -smp 4 -bios /usr/share/ovmf/OVMF.fd "
SATA7 = "-drive if=none,id=d0,format=raw,file=stage7/out/disk.img -device ide-hd,drive=d0,bus=ide.1 "
CAGE7 = "-netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0,mac=52:54:00:a1:07:01 "
FROZEN_7A = ["stage7/DISK.md", "stage7/test.sh", "stage7/checkdisk.py", "broker/metal.py"]
CASES += [(c, v, "ring 7a freeze: " + w) for c, v, w in freeze_cases(FROZEN_7A)]
CASES += [
    (write("stage7/DISK.md"), DENY, "ring 7a freeze: the disk document"),
    (write("stage7/test.sh"), DENY, "ring 7a freeze: the gate"),
    (write("stage7/checkdisk.py"), DENY, "ring 7a freeze: the checker"),
    (bash("python3 - <<'EOF'\nopen('stage7/checkdisk.py','w').write('x')\nEOF"), DENY, "ring 7a freeze: python writing the checker"),
    (bash("sed -i 's/18/17/' stage7/test.sh"), DENY, "ring 7a freeze: sed -i on the gate"),
    (bash("cat stage7/out/disk-section.md >> stage7/DISK.md"), DENY, "ring 7a freeze: appending to the document"),
    (write("broker/metal.py"), DENY, "ring 7a freeze: the broker module, frozen at item 10 after nine of nine (A3)"),
    (bash("python3 - <<'EOF'\nopen('broker/metal.py','w').write('x')\nEOF"), DENY, "ring 7a freeze: python writing the broker module"),
    (bash("sed -i 's/IvyBridge/Haswell/' broker/metal.py"), DENY, "ring 7a freeze: sed -i on the twin's CPU"),
    (bash("git add broker/metal.py"), ALLOW, "ring 7a freeze allows: git add at its freeze"),
    (write("stage8/metal.py"), ALLOW, "ring 7a freeze allows: a later stage's file of the same name"),
    (write("stage7/stage7.asm"), ALLOW, "ring 7a freeze allows: Write the implementation"),
    (write("stage7/mkimage.sh"), ALLOW, "ring 7a freeze allows: the builder is not frozen"),
    (write("broker/claude_backend.py"), ALLOW, "ring 7a freeze allows: the Claude backend is not frozen"),
    (write("stage7/plan-7a.md"), ALLOW, "ring 7a freeze allows: the plan is paperwork"),
    (write("stage7/spec.md"), ALLOW, "ring 7a freeze allows: the spec is paperwork"),
    (write("stage8/DISK.md"), ALLOW, "ring 7a freeze allows: a later stage's document of the same name"),
    (bash("./stage7/test.sh"), ALLOW, "ring 7a freeze allows: running the gate"),
    (bash("./stage7/test.sh > stage7/out/gate.log 2>&1"), ALLOW, "ring 7a freeze allows: gate output redirected"),
    (bash("./stage6/test.sh && ./stage6/test-6b.sh && ./stage6/test-6c.sh"), ALLOW, "ring 7a freeze allows: the three ring 6 gates as regressions"),
    (bash("python3 stage7/checkdisk.py --formatted stage7/out/disk.img 131072 2048 34816"), ALLOW, "ring 7a freeze allows: the checker's host mode"),
    (bash("python3 stage7/checkdisk.py --foreign stage7/out/disk.foreign.img"), ALLOW, "ring 7a freeze allows: the checker writing the foreign disk under out/"),
    (bash("python3 stage7/checkdisk.py --esp stage7/out/esp.before.img stage7/out/esp.img stage7/out/BOOTX64.EFI"), ALLOW, "ring 7a freeze allows: the checker's boot-image check"),
    (bash("python3 stage7/checkdisk.py --persist 2"), ALLOW, "ring 7a freeze allows: the checker"),
    (bash("python3 stage7/checkdisk.py --store"), ALLOW, "ring 7a freeze allows: the checker"),
    (bash("python3 broker/metal.py --mock --port 9999 --germline stage7/out/germline --image stage7/out/esp.img "
          "--workdir stage7/out/rehearsal/twin --record stage7/out/broker.store.a.jsonl --plans plans"),
     ALLOW, "ring 7a freeze allows: the mock with the gate's germline"),
    (bash("python3 broker/metal.py"), ALLOW, "ring 7a freeze allows: the real broker"),
    (bash("python3 broker/metal.py --rehearse-app stage6/app.bin 'test app'"), ALLOW, "ring 7a freeze allows: a hand rehearsal in this ring's twin"),
    (bash("python3 broker/metal.py --rehearse stage6/echo.bin plans/echo.md"), ALLOW, "ring 7a freeze allows: a hand rehearsal against a plan"),
    (bash("truncate -s 64M stage7/out/disk.img"), ALLOW, "bodyguard allows: the 64 MB disk under out/"),
    (bash("cp stage7/out/disk.img stage7/out/disk.oracle.img"), ALLOW, "bodyguard allows: the oracle's keepsake, out/ to out/"),
    (bash("cp stage7/out/esp.img stage7/out/rehearsal/twin/esp.img"), ALLOW, "bodyguard allows: the twin's copy, out/ to out/"),
    (bash("blkid -p stage7/out/disk.img"), ALLOW, "bodyguard allows: the host witness on an image file"),
    (bash("partx -s stage7/out/disk.img"), ALLOW, "bodyguard allows: the host witness on an image file"),
    (bash("cmp stage7/out/disk.img stage7/out/disk.after-first-boot.img"), ALLOW, "bodyguard allows: comparing two images under out/"),
    (bash("grep -n 'EFI PART' stage7/DISK.md broker/metal.py stage7/checkdisk.py"), ALLOW, "ring 7a freeze allows: grepping"),
    (bash("rm -rf stage7/out/germline stage7/out/rehearsal stage7/out/probe7a"), ALLOW, "ring 7a freeze allows: clearing the gate's scratch and the probe"),
    (bash("git add stage7/DISK.md stage7/test.sh stage7/checkdisk.py .claude/hooks/protect-tests.py .claude/hooks/payloads.py"), ALLOW, "ring 7a freeze allows: git add"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img " + SATA7 + CAGE7 + "-serial stdio"),
     ALLOW, "bodyguard allows: the oracle's Stage 7 command - the ESP and the SATA disk"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img " + SATA7 + CAGE7
          + "-display none -serial file:stage7/out/serial.store.a.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's Stage 7 command"),
    (bash("timeout -k 5 60 " + QEMU7.replace("-smp 4", "-smp 8") + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img " + SATA7
          + "-drive format=raw,file=stage7/out/notes.virtio.img,if=virtio " + CAGE7 + "-display none -serial stdio"),
     ALLOW, "bodyguard allows: the gate's virtio boot - the one if=virtio in a Stage 7 command"),
    (bash("qemu-system-x86_64 -machine q35 -m 256M -smp 2 -bios /usr/share/ovmf/OVMF.fd " + DISPLAY6B
          + "-drive format=raw,file=stage7/out/rehearsal/twin/esp.img -drive format=raw,file=stage7/out/rehearsal/twin/notes.img,if=virtio "
          + TWIN_CAGE + "-cpu IvyBridge -drive if=none,id=d0,format=raw,file=stage7/out/rehearsal/twin/disk.img -device ide-hd,drive=d0,bus=ide.1 "
          + "-display none -serial file:stage7/out/rehearsal/twin/serial.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the twin's command as broker/metal.py builds it"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/probe7a/probe.img " + SATA7.replace("stage7/out/disk.img", "stage7/out/probe7a/disk.probe4.img")
          + CAGE7 + "-display none -serial stdio"),
     ALLOW, "bodyguard allows: the item 1 probe under out/"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img -drive if=none,id=d0,format=raw,file=/home/indy/disk.img -device ide-hd,drive=d0,bus=ide.1 " + CAGE7),
     DENY, "bodyguard: a SATA drive outside out/ is denied like any other drive"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img -hdb stage7/out/disk.img " + CAGE7),
     DENY, "bodyguard: a disk attached by a shorthand is denied even under out/"),
    (bash("echo 'one sata disk with a gpt, two partitions, the notebook and the home inside'"), ALLOW, "bodyguard allows: the ring's words in prose"),
]


# --- Stage 7 ring 7b: the freeze (plan item 8, deviation 10), the e1000e, the relay --
# The three paths frozen at item 8 (broker/wire.py joins at item 10, after
# the gate has passed nine of nine through it - its cases are added then);
# the mutation battery on each; the allowances measured before the plan -
# the gate, the checker's three modes, the mock and the real broker, the
# hand rehearsals, the relay with each of its flags (the refusal of a bad
# address is the relay's own, not the hook's), the Stage 7 QEMU lines of
# the gate (the e1000e cage), the "both" boot (a second cage), the "down"
# boot (started paused, the monitor on stdio), the twin (two cages), the
# oracle and the probe, the scratch under out/ - and the denials: a SATA
# drive or a boot image outside out/ on an e1000e line, a shorthand.
WIRE7B = "-drive if=none,id=d0,format=raw,file=stage7/out/wire/disk.img -device ide-hd,drive=d0,bus=ide.1 "
CAGE7B = "-netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9997' -device e1000e,netdev=n0,mac=6c:3b:e5:3b:86:45 "
CAGE7B_2 = "-netdev 'user,id=n1,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9997' -device virtio-net-pci,netdev=n1,mac=52:54:00:a1:07:02 "
TWIN_CAGE_7B = "-netdev 'user,id=n1,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9998' -device e1000e,netdev=n1,mac=6c:3b:e5:3b:86:45 "
FROZEN_7B = ["stage7/WIRE.md", "stage7/test-7b.sh", "stage7/checkwire.py", "broker/wire.py"]
CASES += [(c, v, "ring 7b freeze: " + w) for c, v, w in freeze_cases(FROZEN_7B)]
CASES += [
    (write("broker/wire.py"), DENY, "ring 7b freeze: the broker module, frozen at item 10 after nine of nine (deviation 10)"),
    (bash("python3 - <<'EOF'\nopen('broker/wire.py','w').write('x')\nEOF"), DENY, "ring 7b freeze: python writing the broker module"),
    (bash("sed -i 's/LINES = 19/LINES = 18/' broker/wire.py"), DENY, "ring 7b freeze: sed -i on the twin's line count"),
    (bash("git add broker/wire.py"), ALLOW, "ring 7b freeze allows: git add at its freeze"),
    (write("stage8/wire.py"), ALLOW, "ring 7b freeze allows: a later stage's file of the same name"),
    (write("stage7/WIRE.md"), DENY, "ring 7b freeze: the wire document"),
    (write("stage7/test-7b.sh"), DENY, "ring 7b freeze: the gate"),
    (write("stage7/checkwire.py"), DENY, "ring 7b freeze: the checker"),
    (bash("python3 - <<'EOF'\nopen('stage7/checkwire.py','w').write('x')\nEOF"), DENY, "ring 7b freeze: python writing the checker"),
    (bash("sed -i 's/19/18/' stage7/test-7b.sh"), DENY, "ring 7b freeze: sed -i on the gate"),
    (bash("cat stage7/out/wire-section.md >> stage7/WIRE.md"), DENY, "ring 7b freeze: appending to the document"),
    (write("broker/relay.py"), ALLOW, "ring 7b freeze allows: the relay is a tool, not frozen (the spec)"),
    (bash("sed -i 's/CHUNK = 65536/CHUNK = 32768/' broker/relay.py"), ALLOW, "ring 7b freeze allows: fixing the relay"),
    (write("stage7/stage7.asm"), ALLOW, "ring 7b freeze allows: Write the implementation"),
    (write("stage7/mkimage.sh"), ALLOW, "ring 7b freeze allows: the builder is not frozen"),
    (write("broker/claude_backend.py"), ALLOW, "ring 7b freeze allows: the Claude backend is not frozen"),
    (write("stage7/plan-7b.md"), ALLOW, "ring 7b freeze allows: the plan is paperwork"),
    (write("stage8/WIRE.md"), ALLOW, "ring 7b freeze allows: a later stage's document of the same name"),
    (write("stage8/checkwire.py"), ALLOW, "ring 7b freeze allows: a later stage's checker of the same name"),
    (write("stage8/test-7b.sh"), ALLOW, "ring 7b freeze allows: a later stage's file of the same name"),
    (bash("./stage7/test-7b.sh"), ALLOW, "ring 7b freeze allows: running the gate"),
    (bash("./stage7/test-7b.sh > stage7/out/wire.gate.log 2>&1"), ALLOW, "ring 7b freeze allows: gate output redirected"),
    (bash("./stage7/test.sh && ./stage7/test-7b.sh"), ALLOW, "ring 7b freeze allows: both Stage 7 gates in turn"),
    (bash("python3 stage7/checkwire.py --down 2"), ALLOW, "ring 7b freeze allows: the checker's link-down mode"),
    (bash("python3 stage7/checkwire.py --question 8"), ALLOW, "ring 7b freeze allows: the checker"),
    (bash("python3 stage7/checkwire.py --cage"), ALLOW, "ring 7b freeze allows: the checker"),
    (bash("python3 broker/wire.py --mock --port 9999 --germline stage7/out/wire/germline --image stage7/out/esp.img "
          "--workdir stage7/out/wire/rehearsal/twin --record stage7/out/wire/broker.cage.jsonl --plans plans"),
     ALLOW, "ring 7b freeze allows: the mock with the gate's germline"),
    (bash("python3 broker/wire.py"), ALLOW, "ring 7b freeze allows: the real broker"),
    (bash("python3 broker/wire.py --rehearse-app stage6/app.bin 'test app'"), ALLOW, "ring 7b freeze allows: a hand rehearsal in this ring's twin"),
    (bash("python3 broker/wire.py --rehearse stage6/echo.bin plans/echo.md"), ALLOW, "ring 7b freeze allows: a hand rehearsal against a plan"),
    (bash("python3 broker/relay.py"), ALLOW, "ring 7b freeze allows: the relay on the HP's day"),
    (bash("python3 broker/relay.py --bind 127.0.0.1 --port 9997 --log stage7/out/wire/relay.question.2.jsonl"),
     ALLOW, "ring 7b freeze allows: the relay in the twin"),
    (bash("python3 broker/relay.py --bind 0.0.0.0 --port 9997"), ALLOW, "ring 7b freeze allows: the relay's refusal is its own, not the hook's"),
    (bash("printf 'set_link e1000e.0 off\\ncont\\n'"), ALLOW, "bodyguard allows: the monitor's words in prose"),
    (bash("grep -n 'link up' stage7/WIRE.md stage7/checkwire.py broker/wire.py"), ALLOW, "ring 7b freeze allows: grepping"),
    (bash("rm -rf stage7/out/wire stage7/out/probe7b"), ALLOW, "ring 7b freeze allows: clearing the gate's scratch and the probe"),
    (bash("git add stage7/WIRE.md stage7/test-7b.sh stage7/checkwire.py .claude/hooks/protect-tests.py .claude/hooks/payloads.py"), ALLOW, "ring 7b freeze allows: git add"),
    (bash("timeout -k 5 60 " + QEMU7.replace("-smp 4", "-smp 8") + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img " + WIRE7B + CAGE7B
          + "-display none -serial stdio"),
     ALLOW, "bodyguard allows: the gate's e1000e boot"),
    (bash("timeout -k 5 60 " + QEMU7.replace("-smp 4", "-smp 2") + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img "
          + WIRE7B.replace("disk.img", "disk.both.img") + CAGE7B + CAGE7B_2 + "-display none -serial stdio"),
     ALLOW, "bodyguard allows: the gate's both-NICs boot - two cages"),
    (bash(QEMU7.replace("-smp 4", "-smp 2") + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img "
          + WIRE7B.replace("disk.img", "disk.down.img") + CAGE7B + "-S -display none -serial file:stage7/out/wire/serial.down.2.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's link-down boot, started paused"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img " + WIRE7B + CAGE7B
          + "-display none -serial file:stage7/out/wire/serial.cage.grow.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's e1000e command"),
    (bash("qemu-system-x86_64 -machine q35 -m 256M -smp 2 -bios /usr/share/ovmf/OVMF.fd " + DISPLAY6B
          + "-drive format=raw,file=stage7/out/wire/rehearsal/twin/esp.img -drive format=raw,file=stage7/out/wire/rehearsal/twin/notes.img,if=virtio "
          + TWIN_CAGE + "-cpu IvyBridge -drive if=none,id=d0,format=raw,file=stage7/out/wire/rehearsal/twin/disk.img -device ide-hd,drive=d0,bus=ide.1 "
          + TWIN_CAGE_7B + "-display none -serial file:stage7/out/wire/rehearsal/twin/serial.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the twin's command as broker/wire.py builds it - two cages"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img " + SATA7 + CAGE7B + "-serial stdio"),
     ALLOW, "bodyguard allows: the oracle's ring 7b command"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/probe7b/esp.probe.img " + SATA7.replace("stage7/out/disk.img", "stage7/out/probe7b/disk.4.img")
          + CAGE7B + "-display none -serial file:stage7/out/probe7b/serial.4.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the item 1 probe under out/"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img -drive if=none,id=d0,format=raw,file=/home/indy/disk.img -device ide-hd,drive=d0,bus=ide.1 " + CAGE7B),
     DENY, "bodyguard: a SATA drive outside out/ is denied on an e1000e line too"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=/tmp/esp.img " + WIRE7B + CAGE7B),
     DENY, "bodyguard: a boot image outside out/ is denied whatever the NIC"),
    (bash(QEMU7 + DISPLAY6B + "-drive format=raw,file=stage7/out/esp.img -hdb stage7/out/wire/disk.img " + CAGE7B),
     DENY, "bodyguard: a disk attached by a shorthand is denied even under out/"),
    (bash("echo 'the e1000e on the home switch behind the relay, link up on the metal'"), ALLOW, "bodyguard allows: the ring's words in prose"),
]


# --- Stage 7 ring 7c: the freeze (plan item 6), the stick, the twin of the HP --
# The two paths frozen at item 6; the mutation battery on each; the
# allowances measured before the plan and at item 1 - the gate, the
# checker's modes, the builder and the tools (mkstick.py, relay.py,
# chart.py, METAL.md) writable, the mtools lines at the partition's offset,
# the stick boot (a COPY of the stick on usb-storage behind qemu-xhci, no
# esp.img on SATA), the novga boot on virtio-vga, the twin's line as
# broker/wire.py builds it (ring 7b's, unchanged), the oracle's windowed
# line, the scratch wipe - and the denials: a stick or a disk outside out/,
# a shorthand. The bodyguard's new words and spellings join at item 13.
STICK7C = "-device qemu-xhci -drive if=none,id=stick,format=raw,file=stage7/out/metal/stick.blank.img -device usb-storage,drive=stick "
METAL7C = "-drive if=none,id=d0,format=raw,file=stage7/out/metal/disk.img -device ide-hd,drive=d0,bus=ide.1 "
NOVGA7C = "-vga none -device virtio-vga,edid=on "
FROZEN_7C = ["stage7/test-7c.sh", "stage7/checkmetal.py"]
CASES += [(c, v, "ring 7c freeze: " + w) for c, v, w in freeze_cases(FROZEN_7C)]
CASES += [
    (write("stage7/test-7c.sh"), DENY, "ring 7c freeze: the gate"),
    (write("stage7/checkmetal.py"), DENY, "ring 7c freeze: the checker"),
    (bash("python3 - <<'EOF'\nopen('stage7/checkmetal.py','w').write('x')\nEOF"), DENY, "ring 7c freeze: python writing the checker"),
    (bash("sed -i 's/reset ok/none/' stage7/checkmetal.py"), DENY, "ring 7c freeze: sed -i on the i8042 lines"),
    (bash("sed -i 's/novga 2/novga 4/' stage7/test-7c.sh"), DENY, "ring 7c freeze: sed -i on the gate"),
    (write("stage7/METAL.md"), ALLOW, "ring 7c freeze allows: the owner's procedure is not frozen"),
    (write("stage7/mkstick.py"), ALLOW, "ring 7c freeze allows: the builder is not frozen"),
    (write("broker/relay.py"), ALLOW, "ring 7c freeze allows: the relay is a tool"),
    (write("broker/chart.py"), ALLOW, "ring 7c freeze allows: the serial reader is a tool"),
    (write("broker/probe.py"), ALLOW, "ring 7c freeze allows: the monitor's tool (item 20)"),
    (write("stage7/stage7.asm"), ALLOW, "ring 7c freeze allows: Write the implementation"),
    (write("stage7/mkimage.sh"), ALLOW, "ring 7c freeze allows: the builder is not frozen"),
    (write("stage7/plan-7c.md"), ALLOW, "ring 7c freeze allows: the plan is paperwork"),
    (write("stage8/test-7c.sh"), ALLOW, "ring 7c freeze allows: a later stage's file of the same name"),
    (write("stage8/checkmetal.py"), ALLOW, "ring 7c freeze allows: a later stage's checker of the same name"),
    (bash("./stage7/test-7c.sh"), ALLOW, "ring 7c freeze allows: running the gate"),
    (bash("./stage7/test-7c.sh > stage7/out/gate7c.log 2>&1"), ALLOW, "ring 7c freeze allows: gate output redirected"),
    (bash("./stage7/test.sh && ./stage7/test-7b.sh && ./stage7/test-7c.sh"), ALLOW, "ring 7c freeze allows: the three Stage 7 gates in turn"),
    (bash("python3 stage7/checkmetal.py --stick"), ALLOW, "ring 7c freeze allows: the checker's stick mode"),
    (bash("python3 stage7/checkmetal.py --serial novga 2"), ALLOW, "ring 7c freeze allows: the checker's serial mode"),
    (bash("python3 stage7/checkmetal.py --stages"), ALLOW, "ring 7c freeze allows: the checker"),
    (bash("python3 stage7/checkmetal.py --cage"), ALLOW, "ring 7c freeze allows: the checker"),
    (bash("python3 stage7/mkstick.py"), ALLOW, "ring 7c freeze allows: building the stick"),
    (bash("python3 broker/chart.py"), ALLOW, "ring 7c freeze allows: the serial reader's usage"),
    (bash("python3 broker/probe.py"), ALLOW, "ring 7c freeze allows: the monitor's tool's usage (item 20)"),
    (bash("mformat -i stage7/out/stick.img@@1048576 -F -T 131072 -v GERMOS ::"), ALLOW, "bodyguard allows: mformat at the partition's offset, under out/"),
    (bash("mcopy -i stage7/out/stick.img@@1048576 stage7/out/BOOTX64.EFI ::/EFI/BOOT/BOOTX64.EFI"), ALLOW, "bodyguard allows: mcopy at the offset"),
    (bash("mdir -i stage7/out/stick.img@@1048576 ::/EFI/BOOT"), ALLOW, "bodyguard allows: mdir at the offset"),
    (bash("mtype -i stage7/out/stick.img@@1048576 ::/EFI/BOOT/BOOTX64.EFI | cmp - stage7/out/BOOTX64.EFI"), ALLOW, "bodyguard allows: mtype at the offset"),
    (bash("cp stage7/out/stick.img stage7/out/metal/stick.blank.img"), ALLOW, "bodyguard allows: the stick copied for a boot, out/ to out/"),
    (bash("cp stage7/out/stick.img stage7/out/stick.twin.img"), ALLOW, "bodyguard allows: the oracle's stick copy"),
    (bash("blkid -p stage7/out/stick.img"), ALLOW, "bodyguard allows: the host witness on the stick image"),
    (bash("partx -s stage7/out/stick.img"), ALLOW, "bodyguard allows: the host witness on the stick image"),
    (bash("grep -n 'i8042' stage7/test-7c.sh stage7/checkmetal.py"), ALLOW, "ring 7c freeze allows: grepping"),
    (bash("rm -rf stage7/out/metal stage7/out/probe7c"), ALLOW, "ring 7c freeze allows: clearing the gate's scratch and the probe"),
    (bash("git add stage7/test-7c.sh stage7/checkmetal.py .claude/hooks/protect-tests.py .claude/hooks/payloads.py"), ALLOW, "ring 7c freeze allows: git add"),
    (bash("timeout -k 5 60 " + QEMU7.replace("-smp 4", "-smp 8") + DISPLAY6B + STICK7C + METAL7C + CAGE7B + "-display none -serial stdio"),
     ALLOW, "bodyguard allows: the gate's stick boot - a copy on usb-storage behind xhci, no esp.img"),
    (bash(QEMU7.replace("-smp 4", "-smp 2") + NOVGA7C + STICK7C.replace("stick.blank.img", "stick.novga.img") + METAL7C + CAGE7B
          + "-display none -serial file:stage7/out/metal/serial.novga.2.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's novga boot on virtio-vga"),
    (bash(QEMU7 + DISPLAY6B + STICK7C.replace("stick.blank.img", "stick.stages.img") + METAL7C + CAGE7B
          + "-display none -serial file:stage7/out/metal/serial.stages.a.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's stages boot"),
    (bash("qemu-system-x86_64 -machine q35 -m 256M -smp 2 -bios /usr/share/ovmf/OVMF.fd " + DISPLAY6B
          + "-drive format=raw,file=stage7/out/metal/rehearsal/twin/esp.img -drive format=raw,file=stage7/out/metal/rehearsal/twin/notes.img,if=virtio "
          + TWIN_CAGE + "-cpu IvyBridge -drive if=none,id=d0,format=raw,file=stage7/out/metal/rehearsal/twin/disk.img -device ide-hd,drive=d0,bus=ide.1 "
          + TWIN_CAGE_7B + "-display none -serial file:stage7/out/metal/rehearsal/twin/serial.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the twin's command as broker/wire.py builds it under the metal scratch"),
    (bash(QEMU7 + DISPLAY6B + STICK7C.replace("stage7/out/metal/stick.blank.img", "stage7/out/stick.twin.img") + SATA7 + CAGE7B + "-serial stdio"),
     ALLOW, "bodyguard allows: the oracle's windowed twin of the HP"),
    (bash(QEMU7 + DISPLAY6B + STICK7C.replace("stage7/out/metal/stick.blank.img", "stage7/out/probe7c/stick.usb4.img")
          + METAL7C.replace("stage7/out/metal/disk.img", "stage7/out/probe7c/disk.usb4.img") + CAGE7B
          + "-display none -serial file:stage7/out/probe7c/serial.usb4.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the item 1 probe under out/"),
    (bash(QEMU7 + DISPLAY6B + "-device qemu-xhci -drive if=none,id=stick,format=raw,file=/home/indy/stick.img -device usb-storage,drive=stick " + METAL7C + CAGE7B),
     DENY, "bodyguard: a stick outside out/ is denied like any other drive"),
    (bash(QEMU7 + DISPLAY6B + STICK7C + "-drive if=none,id=d0,format=raw,file=/tmp/disk.img -device ide-hd,drive=d0,bus=ide.1 " + CAGE7B),
     DENY, "bodyguard: a SATA disk outside out/ is denied beside a stick"),
    (bash(QEMU7 + DISPLAY6B + STICK7C + "-hdb stage7/out/metal/disk.img " + CAGE7B),
     DENY, "bodyguard: a disk attached by a shorthand is denied even under out/"),
    (bash("echo 'the stick over usb-storage behind xhci, edid none on virtio-vga, the i8042 self-test'"), ALLOW, "bodyguard allows: the ring's words in prose"),
]

# --- Stage 7 ring 7c: the bodyguard extended (plan item 13, decision 7, A4) --
# The flash's words and every device spelling, measured at item 1 through
# the scratch payload script and denied here; the harmless sources, sinks
# and this ring's tools allowed. The spellings live in this file as data;
# a command line never spells them.
CASES += [(c, DENY, "ring 7c bodyguard: " + w) for c, w in [
    (bash('ls "/dev"/sda'), "a quoted split of the device path"),
    (bash("ls /de\\v/sda"), "a backslash inside the word"),
    (bash("ls \\/dev\\/sda"), "escaped slashes"),
    (bash("ls $'/dev/sda'"), "an ANSI-C quoted path"),
    (bash("ls '/dev/'sda"), "a quoted prefix"),
    (bash('ls "/dev/sda"'), "a quoted path"),
    (bash("ls //dev/sda"), "a doubled leading slash"),
    (bash("ls /dev//sda"), "a doubled inner slash"),
    (bash("ls /dev/./sda"), "a dot segment"),
    (bash("ls /dev"), "the device directory bare"),
    (bash("ls /dev/"), "the device directory with a slash"),
    (bash("ls /dev/ttyUSB0"), "the serial adapter's port"),
    (bash("ls /dev/ttyS0"), "a named terminal"),
    (bash("ls /dev/ttyACM0"), "a named terminal"),
    (bash("ls /dev/serial/by-id/"), "the serial by-id directory"),
    (bash("ls /dev/disk/by-id/usb-x"), "the stick's by-id path"),
    (bash("echo dd"), "dd as a word"),
    (bash("dd if=stage7/out/stick.img of=stage7/out/x.img bs=4M"), "dd even between two files under out/"),
    (bash("echo of=x"), "of= as a word"),
    (bash("echo by-id"), "by-id as a word"),
    (bash("echo ttyUSB"), "ttyUSB as a word"),
    (bash("echo nmcli"), "nmcli as a word"),
    (bash("git commit -m 'flashed with dd by the by-id path'"), "the flash's words in a commit message"),
    (bash("grep -n by-id stage7/METAL.md"), "the word in a grep - reword it"),
    (bash("sudo udisksctl unmount -b /dev/disk/by-id/usb-x-part1"), "the owner's step in a command"),
]]
CASES += [(c, ALLOW, "ring 7c bodyguard allows: " + w) for c, w in [
    (bash("ls /devel/x"), "a path that begins with the four letters and goes on (A4)"),
    (bash("cat stage7/out/devices.txt"), "a word that begins with them (A4)"),
    (bash("echo add odd dd-x ddd"), "dd inside other words or hyphenated"),
    (bash("echo x > /dev/tty"), "the terminal itself, still a sink"),
    (bash("ls /dev/pts/3"), "a pty"),
    (bash('echo x > "/dev/null"'), "a quoted sink"),
    (bash("cmd </dev/null >x 2>/dev/null"), "the gates' redirections"),
    (bash("head -c 16 /dev/urandom | xxd"), "a source, still"),
    (bash("echo lsblk"), "lsblk is not denied"),
    (bash("python3 .claude/hooks/payloads.py"), "the table itself"),
    (bash("python3 stage7/out/probe7c/spellings.py"), "the probe that holds the spellings as data"),
    (bash("python3 broker/chart.py"), "the serial reader's usage - its port is named inside the file"),
    (bash("python3 broker/probe.py"), "the monitor's tool's usage - its port is argv[1], never in its source (item 20)"),
    (bash("git commit -F msg.txt"), "a commit message from a file"),
    (bash("echo 'the flash is the owner'\\''s hand; the stick as built'"), "the ring's words in prose"),
]]

# --- Stage 7 ring 7d: the freeze (plan item 8, decision 11) -----------------
# The four files of the trials frozen - the document, the tool, the gate,
# the checker - and the allowances this ring runs: the gate (its output to
# the log), the checker's four modes, the tool's three, the probe's private
# copy under out/ built and booted, the section file the owner appends,
# the guest and the builders written, the ring's words in prose.
TRIALS7D = "-drive if=none,id=d0,format=raw,file=stage7/out/trials/disk.img -device ide-hd,drive=d0,bus=ide.1 "
STICK7D = "-device qemu-xhci -drive if=none,id=stick,format=raw,file=stage7/out/trials/stick.sitting.img -device usb-storage,drive=stick "
FROZEN_7D = ["stage7/TRIALS.md", "stage7/test-7d.sh", "stage7/checktrials.py", "stage7/trials.py"]
CASES += [(c, v, "ring 7d freeze: " + w) for c, v, w in freeze_cases(FROZEN_7D)]
CASES += [
    (write("stage7/TRIALS.md"), DENY, "ring 7d freeze: the document"),
    (write("stage7/trials.py"), DENY, "ring 7d freeze: the tool"),
    (write("stage7/checktrials.py"), DENY, "ring 7d freeze: the checker"),
    (write("stage7/test-7d.sh"), DENY, "ring 7d freeze: the gate"),
    (edit("stage7/TRIALS.md"), DENY, "ring 7d freeze: Edit on the document"),
    (bash("python3 - <<'EOF'\nopen('stage7/trials.py','w').write('x')\nEOF"), DENY, "ring 7d freeze: python writing the tool"),
    (bash("sed -i 's/OFFSET_MS = 39/OFFSET_MS = 40/' stage7/checktrials.py"), DENY, "ring 7d freeze: sed -i on a timing constant"),
    (bash("sed -i 's/ABBA BAAB/BAAB ABBA/' stage7/TRIALS.md"), DENY, "ring 7d freeze: sed -i on the order"),
    (bash("cat stage7/glass-7d-section.md >> stage6/GLASS.md"), DENY, "ring 7d freeze: the append to GLASS.md is the owner's hand"),
    (bash("echo x >> stage7/TRIALS.md"), DENY, "ring 7d freeze: appending to the document"),
    (write("stage7/glass-7d-section.md"), ALLOW, "ring 7d freeze allows: the section file the owner appends"),
    (write("stage7/stage7.asm"), ALLOW, "ring 7d freeze allows: Write the implementation"),
    (write("stage7/mkimage.sh"), ALLOW, "ring 7d freeze allows: the builder is not frozen"),
    (write("stage7/mkstick.py"), ALLOW, "ring 7d freeze allows: the stick's builder is not frozen"),
    (write("stage7/plan-7d.md"), ALLOW, "ring 7d freeze allows: the plan is paperwork"),
    (write("stage7/out/probe7d/stage7.asm"), ALLOW, "ring 7d freeze allows: the probe's private copy under out/"),
    (write("stage8/TRIALS.md"), ALLOW, "ring 7d freeze allows: a later stage's document of the same name"),
    (write("stage8/trials.py"), ALLOW, "ring 7d freeze allows: a later stage's tool of the same name"),
    (bash("./stage7/test-7d.sh"), ALLOW, "ring 7d freeze allows: running the gate"),
    (bash("./stage7/test-7d.sh 2>&1 | tail -20"), ALLOW, "ring 7d freeze allows: the gate piped"),
    (bash("tail -5 stage7/out/gate-7d.log"), ALLOW, "ring 7d freeze allows: reading the gate's log"),
    (bash("echo x >> stage7/out/gate-7d.log"), ALLOW, "ring 7d freeze allows: appending to the gate's log under out/"),
    (bash("python3 stage7/checktrials.py --document"), ALLOW, "ring 7d freeze allows: the checker's document mode"),
    (bash("python3 stage7/checktrials.py --row"), ALLOW, "ring 7d freeze allows: the checker's row mode"),
    (bash("python3 stage7/checktrials.py --sitting"), ALLOW, "ring 7d freeze allows: the checker's sitting mode"),
    (bash("python3 stage7/checktrials.py --cage"), ALLOW, "ring 7d freeze allows: the checker's cage mode"),
    (bash("python3 stage7/trials.py --example"), ALLOW, "ring 7d freeze allows: the tool on the worked examples"),
    (bash("python3 stage7/trials.py --disk stage7/out/trials/disk.img"), ALLOW, "ring 7d freeze allows: the tool on a disk image"),
    (bash("python3 stage7/trials.py --serial stage7/out/metal.log"), ALLOW, "ring 7d freeze allows: the tool on the chart"),
    (bash("cat stage7/TRIALS.md | head -40"), ALLOW, "ring 7d freeze allows: reading the document"),
    (bash("grep -n 'OFFSET' stage7/checktrials.py"), ALLOW, "ring 7d freeze allows: grepping the checker"),
    (bash("nasm -f bin stage7/out/probe7d/stage7.asm -o stage7/out/probe7d/out/BOOTX64.EFI"), ALLOW, "ring 7d freeze allows: assembling the probe under out/"),
    (bash("cp stage7/out/probe7d/out/stick.img stage7/out/stick.img"), ALLOW, "bodyguard allows: the probe's stick over the scratch stick, out/ to out/"),
    (bash("rm -rf stage7/out/trials stage7/out/probe7d"), ALLOW, "ring 7d freeze allows: clearing the gate's scratch and the probe"),
    (bash("git add stage7/TRIALS.md stage7/test-7d.sh stage7/checktrials.py stage7/trials.py .claude/hooks/protect-tests.py .claude/hooks/payloads.py"),
     ALLOW, "ring 7d freeze allows: git add"),
    (bash("git commit -F msg.txt"), ALLOW, "ring 7d freeze allows: a commit message from a file"),
    (bash(QEMU7 + DISPLAY6B + STICK7D + TRIALS7D + CAGE7B + "-display none -serial file:stage7/out/trials/serial.sitting.1.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the checker's sitting boot under the trials scratch"),
    (bash(QEMU7 + DISPLAY6B + STICK7D.replace("stage7/out/trials/stick.sitting.img", "stage7/out/probe7d/measure.stick.img")
          + TRIALS7D.replace("stage7/out/trials/disk.img", "stage7/out/probe7d/measure.disk.img") + CAGE7B
          + "-display none -serial file:stage7/out/probe7d/measure.serial.txt -monitor stdio"),
     ALLOW, "bodyguard allows: the item 7 probe's boot under out/"),
    (bash(QEMU7 + DISPLAY6B + STICK7D + "-drive if=none,id=d0,format=raw,file=/tmp/trial.img -device ide-hd,drive=d0,bus=ide.1 " + CAGE7B),
     DENY, "bodyguard: a trial disk outside out/ is denied"),
    (bash("echo 'the trial, the cue, the hit, the miss, layout B, the synthetic human, the verdict'"), ALLOW, "bodyguard allows: the ring's words in prose"),
]


def run(case):
    tool, tool_input = case
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input})
    proc = subprocess.run(
        [sys.executable, HOOK], input=payload.encode(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO))
    if proc.returncode == 0:
        return ALLOW, proc.stderr.decode()
    if proc.returncode == 2:
        return DENY, proc.stderr.decode()
    return "EXIT %d" % proc.returncode, proc.stderr.decode()


def main():
    wrong = 0
    counts = {DENY: 0, ALLOW: 0}
    for case, want, label in CASES:
        got, stderr = run(case)
        counts[want] = counts.get(want, 0) + 1
        ok = got == want
        if not ok:
            wrong += 1
        tool, tool_input = case
        shown = tool_input.get("command") or tool_input.get("file_path") or ""
        shown = shown.replace("\n", "\\n")
        if len(shown) > 70:
            shown = shown[:67] + "..."
        print("  %s  want %-5s got %-5s  %-45s %s: %s"
              % ("ok  " if ok else "WRONG", want, got, label[:45], tool, shown))
        if not ok and stderr:
            for line in stderr.strip().splitlines()[:3]:
                print("           | " + line)
    print()
    print("%d payloads: %d must be denied, %d must be allowed, %d wrong"
          % (len(CASES), counts[DENY], counts[ALLOW], wrong))
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
