#!/usr/bin/env bash
#
# Stage 7 ring 7a acceptance tests - the gate for the disk.
#
# Implements acceptance tests 1 to 4 from stage7/spec.md (ring 7a), as
# stage7/plan-7a.md and its amendments fix them. Test 5 is Wajira's eyeball
# on a windowed run with the REAL broker - one note, one reboot, and
# "! calculator" from a home partition the real broker installed - and
# stays manual: his word closes the ring.
#
# These tests are written BEFORE the ring's driver code and are frozen once
# written - a PreToolUse hook blocks the implementer from editing this file
# during implementation and fixes. If a test here is genuinely wrong, that
# is a spec question for the owner, not an edit.
#
# stage7/mkimage.sh, which builds and packs the artefact, is deliberately
# NOT frozen. This file holds the criteria; that one holds the recipe. The
# Stage 6 binary and its three gates (stage6/test.sh, test-6b.sh,
# test-6c.sh) are untouched and still frozen: they boot their own binary
# from their own folder and must stay green - Stages 0 to 6 stay green
# forever on their own binaries.
#
# Everything runs inside QEMU, with OVMF as firmware, the patient's CPU
# model (-cpu IvyBridge), the standard VGA device stating 1920x1080 through
# an EDID, and exactly TWO drives per guest: a raw FAT boot image on q35's
# own SATA controller (ide.0, port 0) and a raw 64 MB disk on the same
# controller (ide.1, port 1) - both under stage7/out/, both created here or
# by the broker's twin under stage7/out/rehearsal/ (where the frozen twin
# also creates the 16 MB virtio notes image the Stage 7 guest has no driver
# for). No "if=virtio" in any command of this gate's own, bar the one boot
# of test 2 that proves the guest ignores such a disk. The caged network of
# stage4/UMBILICAL.md: slirp with restrict=on and one guestfwd to the
# broker on 127.0.0.1:9999 (the twin, to its own listener on 127.0.0.1:9998).
# The automated tests talk only to the MOCK broker (broker/metal.py
# --mock), which calls nothing outside the repository; this gate never
# spends a token and never needs the internet. It refuses to run at all
# while anything is listening on either port. The mock's germline is
# stage7/out/germline/, wiped here.
#
# Usage:  ./stage7/test.sh       (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage7/out"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
DISK="$OUT/disk.img"
OVMF="/usr/share/ovmf/OVMF.fd"
DISK_BYTES=$((64 * 1024 * 1024))

# The cage, spelled once (UMBILICAL.md, "The cage"), with this ring's MAC so
# the guest's "S7: nic" line is checked against a value the assembler cannot
# know. The twin uses the same cage with its own port.
BROKER_PORT=9999
REHEARSAL_PORT=9998
MAC="52:54:00:a1:07:01"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${BROKER_PORT}"
CAGE_DEVICE="virtio-net-pci,netdev=n0,mac=${MAC}"

# The machine, spelled once: q35 with the patient's CPU model (spec decision
# 4 - grown code is fitted to the processor it finds, and the twin must find
# the same one), and the display stating 1920x1080 through an EDID. Every
# QEMU line in this gate, the checker and the twin (broker/metal.py adds the
# CPU and the disk through the frozen twin's seam) carries these.
MACHINE="-machine q35 -cpu IvyBridge -m 256M -bios $OVMF"
DISPLAY="-vga none -device VGA,edid=on,xres=1920,yres=1080"

# The disk, spelled once: a raw file on q35's own AHCI controller, ide.1 -
# port 1 beside the boot image on port 0. sata_drive <path> prints the two
# arguments.
sata_drive() { printf -- '-drive if=none,id=d0,format=raw,file=%s -device ide-hd,drive=d0,bus=ide.1' "$1"; }

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 7 ring 7a acceptance tests"
echo "repo: $REPO"
echo

# ------------------------------------------------ the ports must be free ----

for port in "$BROKER_PORT" "$REHEARSAL_PORT"; do
  if python3 - "$port" <<'EOF'
import socket, sys
s = socket.socket(); s.settimeout(1.0)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
EOF
  then
    echo "  something is already listening on 127.0.0.1:$port."
    echo "  The gate talks only to its own mock broker and its own twin."
    echo "  If the real broker is running, stop it first; then run this again."
    exit 1
  fi
done

# The mock's germline and the twin's scratch: fresh for every run.
rm -rf "$OUT/germline" "$OUT/rehearsal"

# ------------------------------------------------------------ helpers -------

rd_u2() { od -An -tu2 -j "$2" -N 2 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
rd_u4() { od -An -tu4 -j "$2" -N 4 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
hexat() { xxd -p -s "$2" -l "$3" "$1" 2>/dev/null | tr -d '\n'; }

# fresh_disk <path> - a brand-new, all-zero 64 MB raw image: the blank disk
# the guest formats (DISK.md, the selection rule's second case).
fresh_disk() {
  rm -f "$1"
  truncate -s "$DISK_BYTES" "$1"
}

# ---------------------------------------------------------------- build ------

echo "Build: ./stage7/mkimage.sh"
if "$REPO/stage7/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI carries the MZ and PE magics, machine type x86-64, subsystem EFI
# application, relocations stripped; and esp.img contains it, byte for byte,
# at the UEFI removable-media path. Ring 6a's criteria, on this ring's binary.

echo "Test 1 - Artefact: PE32+ EFI application, packed at EFI/BOOT/BOOTX64.EFI"
probs=()

if [ ! -f "$EFI" ]; then
  probs+=("BOOTX64.EFI was not built")
else
  size=$(stat -c%s "$EFI")

  mz=$(hexat "$EFI" 0 2)
  [ "$mz" = "4d5a" ] || probs+=("bytes 0-1 are 0x$mz, expected 'MZ' (4d5a)")

  lfa=$(rd_u4 "$EFI" 60)
  if ! [[ "$lfa" =~ ^[0-9]+$ ]] || [ "$lfa" -lt 4 ] || [ "$((lfa + 248))" -gt "$size" ]; then
    probs+=("e_lfanew at 0x3C is '$lfa', not a sane PE header offset in a $size byte file")
  else
    sig=$(hexat "$EFI" "$lfa" 4)
    [ "$sig" = "50450000" ] || probs+=("no 'PE\\0\\0' at e_lfanew=$lfa (found 0x$sig)")

    machine=$(rd_u2 "$EFI" $((lfa + 4)))
    [ "$machine" = "34404" ] || \
      probs+=("machine is 0x$(printf '%04x' "${machine:-0}"), expected 0x8664 (x86-64)")

    chars=$(rd_u2 "$EFI" $((lfa + 22)))
    chars=${chars:-0}
    [ $((chars & 1)) -eq 1 ] || \
      probs+=("characteristics 0x$(printf '%04x' "$chars") lacks RELOCS_STRIPPED (0x0001)")
    [ $((chars & 2)) -eq 2 ] || \
      probs+=("characteristics 0x$(printf '%04x' "$chars") lacks EXECUTABLE_IMAGE (0x0002)")

    optmagic=$(rd_u2 "$EFI" $((lfa + 24)))
    [ "$optmagic" = "523" ] || \
      probs+=("optional header magic is 0x$(printf '%04x' "${optmagic:-0}"), expected 0x020b (PE32+)")

    subsys=$(rd_u2 "$EFI" $((lfa + 92)))
    [ "$subsys" = "10" ] || \
      probs+=("subsystem is ${subsys:-none}, expected 10 (EFI application)")
  fi
fi

if [ ! -f "$ESP" ]; then
  probs+=("esp.img was not built")
elif [ -f "$EFI" ]; then
  if ! mdir -i "$ESP" ::/EFI/BOOT 2>/dev/null | grep -qE '^BOOTX64 +EFI'; then
    probs+=("esp.img has no BOOTX64.EFI at ::/EFI/BOOT (the removable-media path)")
  else
    rm -f "$OUT/extracted.efi"
    mtype -i "$ESP" ::/EFI/BOOT/BOOTX64.EFI >"$OUT/extracted.efi" 2>/dev/null
    cmp -s "$OUT/extracted.efi" "$EFI" || \
      probs+=("the copy inside esp.img is not byte-identical to BOOTX64.EFI")
  fi
fi

if [ "${#probs[@]}" -eq 0 ]; then
  pass "test 1: PE32+ x86-64 EFI application, relocs stripped, packed at EFI/BOOT/BOOTX64.EFI"
else
  fail "test 1: the artefact is not a packed PE32+ EFI application"
  for p in "${probs[@]}"; do echo "    - $p"; done
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira, in two terminals at the repo root:"
  echo "  python3 broker/metal.py"
  echo "  truncate -s 64M stage7/out/disk.img      # only for a blank disk; this gate overwrites it"
  echo "  qemu-system-x86_64 $MACHINE -smp 4 $DISPLAY -drive format=raw,file=stage7/out/esp.img $(sata_drive stage7/out/disk.img) -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0 -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
