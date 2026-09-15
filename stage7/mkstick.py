#!/usr/bin/env python3
"""Stage 7 ring 7c: the stick - stage7/out/stick.img, the image the owner
flashes to a USB stick by his own hand and the gate boots as a copy over
qemu-xhci + usb-storage.

A protective MBR, a GPT (the header at LBA 1, its backup at the last LBA,
128 entries of 128 bytes after each) with exactly one partition - an EFI
System Partition of the standard type GUID, 64 MB at LBA 2048 - formatted
FAT32 and filled with EFI/BOOT/BOOTX64.EFI by mtools at the partition's
offset (the image@@offset form). No loop device, no /dev, no root, nothing
outside stage7/out/. The build to pack is stage7/out/BOOTX64.EFI, which
stage7/mkimage.sh assembles first.

This file is DELIBERATELY NOT FROZEN, like every builder: it is the recipe,
not a criterion. stage7/test-7c.sh's test 1 judges what comes out - the
MBR, both tables, the one entry, the file read back byte for byte - so a
packing problem is fixable without disturbing a frozen file. The constants
below are the ones the checker imports; a number here is a number there.

Usage:  python3 stage7/mkstick.py        (from anywhere)
Exit 0 only if stick.img was written and mdir lists the file at the offset.
"""

import os
import struct
import subprocess
import sys
import uuid
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
EFI = os.path.join(OUT, "BOOTX64.EFI")
STICK = os.path.join(OUT, "stick.img")

SECTOR = 512
STICK_SECTORS = 135168                    # 66 MiB: 1 MiB before the ESP, 64 MiB of ESP, the backup table after
ESP_FIRST = 2048                          # 1 MiB alignment
ESP_SECTORS = 131072                      # 64 MB, the spec's size
ESP_LAST = ESP_FIRST + ESP_SECTORS - 1    # 133119
ESP_OFFSET = ESP_FIRST * SECTOR           # what mtools is told
ENTRIES, ENTRY = 128, 128
ENTRY_SECTORS = ENTRIES * ENTRY // SECTOR # 32
FIRST_USABLE = 2 + ENTRY_SECTORS          # 34
LAST_USABLE = STICK_SECTORS - 2 - ENTRY_SECTORS
ESP_TYPE = uuid.UUID("C12A7328-F81F-11D2-BA4B-00A0C93EC93B")   # EFI System Partition
DISK_GUID = uuid.UUID("7c0d1e2f-3a4b-4c5d-8e6f-70a1b2c3d4e5")  # fixed: the same stick every build
PART_GUID = uuid.UUID("0a1b2c3d-4e5f-4a6b-9c7d-8e9f0a1b2c3d")
PART_NAME = "EFI System"
VOLUME = "GERMOS"
MFORMAT_FLAGS = ["-F", "-T", str(ESP_SECTORS)]   # FAT32, the partition's size in sectors (item 1)


def guid_bytes(u):
    return u.bytes_le


def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF


def protective_mbr(n):
    """One 0xEE entry from LBA 1 to the end of the disk, the boot signature."""
    mbr = bytearray(SECTOR)
    mbr[446:462] = bytes([0x00, 0x00, 0x02, 0x00, 0xEE, 0xFF, 0xFF, 0xFF]) + struct.pack("<II", 1, min(n - 1, 0xFFFFFFFF))
    mbr[510:512] = b"\x55\xAA"
    return bytes(mbr)


def partition_entries():
    """Entry 0 the ESP; the other 127 zero."""
    e = bytearray(ENTRIES * ENTRY)
    e[0:16] = guid_bytes(ESP_TYPE)
    e[16:32] = guid_bytes(PART_GUID)
    e[32:48] = struct.pack("<QQ", ESP_FIRST, ESP_LAST)
    e[48:56] = struct.pack("<Q", 0)
    name = PART_NAME.encode("utf-16-le")
    e[56:56 + len(name)] = name
    return bytes(e)


def gpt_header(n, my_lba, alt_lba, entries_lba, entries_crc):
    h = bytearray(92)
    h[0:8] = b"EFI PART"
    h[8:12] = struct.pack("<I", 0x00010000)
    h[12:16] = struct.pack("<I", 92)
    h[24:32] = struct.pack("<Q", my_lba)
    h[32:40] = struct.pack("<Q", alt_lba)
    h[40:48] = struct.pack("<Q", FIRST_USABLE)
    h[48:56] = struct.pack("<Q", n - 2 - ENTRY_SECTORS)
    h[56:72] = guid_bytes(DISK_GUID)
    h[72:80] = struct.pack("<Q", entries_lba)
    h[80:84] = struct.pack("<I", ENTRIES)
    h[84:88] = struct.pack("<I", ENTRY)
    h[88:92] = struct.pack("<I", entries_crc)
    h[16:20] = struct.pack("<I", crc32(bytes(h)))
    return bytes(h) + bytes(SECTOR - 92)


def build_table(n=STICK_SECTORS):
    """{lba: 512 bytes} for every sector the tables occupy - what the
    checker compares a booted copy against."""
    entries = partition_entries()
    ecrc = crc32(entries)
    table = {0: protective_mbr(n),
             1: gpt_header(n, 1, n - 1, 2, ecrc),
             n - 1: gpt_header(n, n - 1, 1, n - 1 - ENTRY_SECTORS, ecrc)}
    for i in range(ENTRY_SECTORS):
        chunk = entries[i * SECTOR:(i + 1) * SECTOR]
        table[2 + i] = chunk
        table[n - 1 - ENTRY_SECTORS + i] = chunk
    return table


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        sys.stderr.write("mkstick: %s failed:\n%s\n" % (cmd[0], r.stderr.rstrip()))
    return r


def main():
    if not os.path.isfile(EFI):
        sys.stderr.write("mkstick: %s does not exist - run ./stage7/mkimage.sh first\n" % os.path.relpath(EFI, REPO))
        return 1
    os.makedirs(OUT, exist_ok=True)
    if os.path.exists(STICK):
        os.remove(STICK)                  # a stale stick can never make a test pass
    img = bytearray(STICK_SECTORS * SECTOR)
    for lba, data in build_table().items():
        img[lba * SECTOR:(lba + 1) * SECTOR] = data
    with open(STICK, "wb") as fh:
        fh.write(img)
    at = "%s@@%d" % (STICK, ESP_OFFSET)
    for cmd in (["mformat", "-i", at] + MFORMAT_FLAGS + ["-v", VOLUME, "::"],
                ["mmd", "-i", at, "::/EFI", "::/EFI/BOOT"],
                ["mcopy", "-i", at, EFI, "::/EFI/BOOT/BOOTX64.EFI"]):
        if run(cmd).returncode:
            os.remove(STICK)
            return 1
    r = run(["mdir", "-i", at, "::/EFI/BOOT"])
    if r.returncode or "BOOTX64  EFI" not in r.stdout:
        sys.stderr.write("mkstick: mdir at the offset does not list BOOTX64.EFI\n")
        os.remove(STICK)
        return 1
    print("mkstick: stick.img %d bytes (%d sectors); the ESP at LBA %d..%d holds EFI/BOOT/BOOTX64.EFI, %d bytes"
          % (len(img), STICK_SECTORS, ESP_FIRST, ESP_LAST, os.path.getsize(EFI)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
