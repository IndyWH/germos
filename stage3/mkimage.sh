#!/usr/bin/env bash
#
# Stage 3 build and pack.
#
# Assembles stage3/stage3.asm into a PE32+ UEFI application and packs it into a
# FAT image at the UEFI removable-media path, EFI/BOOT/BOOTX64.EFI, where OVMF
# looks for it. Stage 2's proven recipe, retargeted.
#
# This script is DELIBERATELY NOT FROZEN, unlike stage3/test.sh,
# stage3/checknotes.py and stage3/NOTEBOOK.md. It is the recipe, not a
# criterion. The spec's acceptance test 1 judges the artefact that comes out of
# here - the PE header fields, and esp.img read back with mdir/mtype - so a
# packing problem must be fixable without disturbing a frozen file. No packing
# trick can fake booting in QEMU, which is what tests 2 to 4 actually measure.
#
# Everything is written inside stage3/out/. No block device is touched, no loop
# mount is taken, and dd writes only to a file in that directory.
#
# Usage:  ./stage3/mkimage.sh        (from anywhere)
# Exit 0 only if BOOTX64.EFI and esp.img were both built.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage3/out"
ASM="$REPO/stage3/stage3.asm"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"

mkdir -p "$OUT"

# Old artefacts go first, so a stale file can never make a test pass.
rm -f "$EFI" "$ESP"

# ------------------------------------------------------------- assemble ------

if [ ! -f "$ASM" ]; then
  echo "mkimage: stage3/stage3.asm does not exist yet - nothing to build" >&2
  exit 1
fi

# Assembled from the repo root: stage3.asm incbins the font by its
# repo-relative path, so the same path works here and in the checker.
if ! (cd "$REPO" && nasm -f bin "$ASM" -o "$EFI" 2>"$OUT/nasm.err"); then
  echo "mkimage: nasm failed:" >&2
  sed 's/^/    /' "$OUT/nasm.err" >&2
  rm -f "$EFI"
  exit 1
fi

# ----------------------------------------------------------------- pack ------
# A partitionless FAT image, formatted and filled by mtools - no root, no loop
# mount, no partition table. Confirmed to boot under OVMF in Stage 1.

if ! dd if=/dev/zero of="$ESP" bs=1M count=48 status=none; then
  echo "mkimage: could not create $ESP" >&2
  exit 1
fi

if ! mformat -i "$ESP" -F -v ESP :: 2>"$OUT/mtools.err"; then
  echo "mkimage: mformat failed:" >&2
  sed 's/^/    /' "$OUT/mtools.err" >&2
  rm -f "$ESP"
  exit 1
fi

if ! mmd -i "$ESP" ::/EFI ::/EFI/BOOT 2>"$OUT/mtools.err"; then
  echo "mkimage: mmd failed:" >&2
  sed 's/^/    /' "$OUT/mtools.err" >&2
  rm -f "$ESP"
  exit 1
fi

if ! mcopy -i "$ESP" "$EFI" ::/EFI/BOOT/BOOTX64.EFI 2>"$OUT/mtools.err"; then
  echo "mkimage: mcopy failed:" >&2
  sed 's/^/    /' "$OUT/mtools.err" >&2
  rm -f "$ESP"
  exit 1
fi

echo "mkimage: BOOTX64.EFI $(stat -c%s "$EFI") bytes, packed into esp.img"
exit 0
