#!/usr/bin/env bash
# trials/hp-stick.sh - write ring 8t's stick for the HP (Cowork's; the
# owner runs it). stage7/METAL.md steps 1-3 as one checked script: it
# rebuilds the stick, checks the build is the seed in the record, finds
# the one USB disk, asks for one key, writes, compares and powers the
# stick off. Everything it prints also goes to trials/out/hp-stick.log.
#
# Run at the repo root, with the stick plugged into mlrig and nothing
# else on USB storage:   ./trials/hp-stick.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p trials/out
exec > >(tee -a trials/out/hp-stick.log) 2>&1
stop() { echo "STOP: $*"; echo "Nothing more was done."; exit 1; }
echo "=== hp-stick $(date -Iseconds) at $(git log -1 --format=%h) ==="

# 1. The build, and the seed it must be
./stage8/mkimage.sh >/dev/null
python3 stage8/mkstick.py
IMG=stage8/out/stick.img
EFI=stage8/out/BOOTX64.EFI
SIZE=$(stat -c %s "$IMG")
SEED=$(awk '$1=="seed"{n=$2} END{print n}' stage8/seed-record.md)
WANT=$(awk '$1=="seed"{h=$3} END{print h}' stage8/seed-record.md)
HAVE=$(sha256sum "$EFI" | cut -d' ' -f1)
[ "$HAVE" = "$WANT" ] || stop "BOOTX64.EFI is ${HAVE:0:16}, but the record's last seed ($SEED) is ${WANT:0:16}"
echo "build: seed $SEED (${HAVE:0:16}), stick image $SIZE bytes"

# 2. Exactly one USB disk, the stick's size, nothing of mlrig's
mapfile -t USB < <(lsblk -dnpo NAME,TRAN,TYPE | awk '$2=="usb" && $3=="disk" {print $1}')
if [ "${#USB[@]}" -ne 1 ]; then
    lsblk -o NAME,SIZE,MODEL,TRAN
    stop "${#USB[@]} USB disks seen; exactly one, the stick, must be plugged in"
fi
DEV=${USB[0]}
BYTES=$(lsblk -dnbo SIZE "$DEV")
[ "$BYTES" -ge "$SIZE" ] || stop "$DEV is smaller than the image"
[ "$BYTES" -le $((256 * 1024 * 1024 * 1024)) ] || stop "$DEV is larger than 256 GB; not a stick"
if lsblk -nro MOUNTPOINTS "$DEV" | grep -qE '^/(boot|home|usr|var)?(/|$)'; then
    stop "$DEV holds a system mount"
fi
ID=""
for p in /dev/disk/by-id/usb-*; do
    [[ $p == *-part* ]] && continue
    [ "$(readlink -f "$p")" = "$DEV" ] && ID=$p
done
[ -n "$ID" ] || stop "no by-id name for $DEV"
lsblk -o NAME,SIZE,MODEL,TRAN,MOUNTPOINTS "$DEV"
echo "This erases $(lsblk -dno MODEL "$DEV" | xargs), $((BYTES / 1000000000)) GB: $ID"
read -r -n1 -p "Press y to write the stick, any other key to stop: " KEY </dev/tty
echo
[ "$KEY" = y ] || stop "not confirmed"

# 3. Unmount, wipe the old signatures, write, compare
unmount_all() {
    lsblk -nrpo NAME,MOUNTPOINTS "$DEV" | awk 'NF==2 {print $1}' | while read -r part; do
        udisksctl unmount -b "$part"
    done
}
unmount_all
for part in $(lsblk -nrpo NAME,TYPE "$DEV" | awk '$2=="part" {print $1}'); do
    sudo wipefs -a "$part"
done
sudo wipefs -a "$ID"
sudo dd if="$IMG" of="$ID" bs=4M oflag=direct conv=fsync status=progress
sync
sudo blockdev --flushbufs "$ID"
sudo cmp -n "$SIZE" "$IMG" "$ID" || stop "the stick does not match the image; run the script again"
udevadm settle
sleep 2
if lsblk -nro MOUNTPOINTS "$DEV" | grep -q .; then
    echo "the desktop mounted the new partition; unmounting and comparing again"
    unmount_all
    sudo cmp -n "$SIZE" "$IMG" "$ID" || stop "the stick changed after the write; run the script again"
fi
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS "$DEV"
lsblk -nro FSTYPE "$DEV" | grep -qx vfat || stop "no vfat partition on the stick after the write"
echo "cmp: the stick matches the image byte for byte; the partition is vfat"

# 4. Power it off, so nothing is half-written when it comes out
udisksctl power-off -b "$ID"
echo "DONE: seed $SEED is on the stick. Unplug it and put it in the HP."
