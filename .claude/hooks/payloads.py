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
]]

# --- Stage 3: the storage bodyguard - allowances ---------------------------
CASES += [(c, ALLOW, "bodyguard allows: " + w) for c, w in [
    (bash("dd if=/dev/zero of=stage3/out/x.img bs=1M count=16 status=none"), "dd from /dev/zero into out/"),
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
    (write("stage4/test.sh"), ALLOW, "stage3 freeze allows: creating the next stage's test file"),
    (write("stage4/NOTEBOOK.md"), ALLOW, "stage3 freeze allows: a later stage's format document"),
    (bash("nasm -f bin stage3/stage3.asm -o stage3/out/BOOTX64.EFI"), ALLOW, "stage3 freeze allows: assembling"),
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
