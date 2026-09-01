#!/usr/bin/env bash
#
# Stage 5 acceptance tests - the gate for the stage.
#
# Implements acceptance tests 1 to 4 from stage5/spec.md. Test 5 is Wajira's
# eyeball on a windowed run with the REAL broker - he types "! make me a
# clock", the twin rehearses what Claude wrote, and a clock ticks on the
# machine's own screen - and stays manual: his word is the gate for the
# stage.
#
# These tests are written BEFORE stage5.asm and are frozen once written - a
# PreToolUse hook blocks the implementer from editing this file during
# implementation and fixes. If a test here is genuinely wrong, that is a spec
# question for the owner, not an edit.
#
# stage5/mkimage.sh, which builds and packs the artefact, is deliberately NOT
# frozen. This file holds the criteria; that one holds the recipe. Test 1 below
# judges the artefact independently of how it was made.
#
# Everything runs inside QEMU, with OVMF as firmware, exactly two drives per
# guest - a raw FAT boot image and a raw 16 MB notebook image, both under
# stage5/out/, both created here or by the broker's rehearsal under
# stage5/out/rehearsal/ - and the caged network of stage4/UMBILICAL.md:
# slirp with restrict=on and one guestfwd to the broker on 127.0.0.1:9999
# (the rehearsal's twin, to its own listener on 127.0.0.1:9998). The
# automated tests talk only to the MOCK broker (broker/germline.py --mock),
# which calls nothing outside the repository; this gate never spends a token
# and never needs the internet. It refuses to run at all while anything is
# listening on either port, so it can never talk to a real broker by
# accident. The mock's germline is stage5/out/germline/, wiped here, so the
# real germline/ is never read or written by the gate.
#
# Usage:  ./stage5/test.sh          (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage5/out"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
NOTES="$OUT/notes.img"
OVMF="/usr/share/ovmf/OVMF.fd"
DISK_BYTES=$((16 * 1024 * 1024))

# The cage, spelled once. UMBILICAL.md, "The cage": the guest's whole world is
# 10.0.2.4:9999, delivered per connection to the broker on 127.0.0.1:9999 by
# netcat; everything else gets a RST from slirp. The MAC is the harness's
# choice, so the guest's "S5: nic" line can be checked against a value the
# assembler cannot know. The rehearsal's twin uses the same cage with its
# own port (GERMLINE.md, "The rehearsal").
BROKER_PORT=9999
REHEARSAL_PORT=9998
MAC="52:54:00:a1:05:01"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${BROKER_PORT}"
CAGE_DEVICE="virtio-net-pci,netdev=n0,mac=${MAC}"

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 5 acceptance tests"
echo "repo: $REPO"
echo

# ------------------------------------------------ the ports must be free ----
# The real broker and this gate cannot share 127.0.0.1:9999, and the gate must
# never talk to anything but its own mock; the rehearsal's listener needs
# 9998 to itself. Refuse, loudly, before building.

for port in "$BROKER_PORT" "$REHEARSAL_PORT"; do
  if python3 - "$port" <<'EOF'
import socket, sys
s = socket.socket(); s.settimeout(1.0)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
EOF
  then
    echo "  something is already listening on 127.0.0.1:$port."
    echo "  The gate talks only to its own mock broker and its own rehearsal listener."
    echo "  If the real broker is running, stop it first; then run this again."
    exit 1
  fi
done

# The mock's germline: fresh for every run, so the generation-call counts
# and the entry counts the tests demand are deterministic.
rm -rf "$OUT/germline" "$OUT/rehearsal"

# ------------------------------------------------------------ helpers -------
# Little-endian integer reads out of a binary, by byte offset.

rd_u2() { od -An -tu2 -j "$2" -N 2 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
rd_u4() { od -An -tu4 -j "$2" -N 4 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
hexat() { xxd -p -s "$2" -l "$3" "$1" 2>/dev/null | tr -d '\n'; }

# fresh_disk <path> - a brand-new, all-zero 16 MB raw image. Removed first so
# that no note from an earlier run can survive into this one.
fresh_disk() {
  rm -f "$1"
  truncate -s "$DISK_BYTES" "$1"
}

# ---------------------------------------------------------------- build ------
# The builder is a separate, unfrozen script. A build failure is a TEST
# failure, reported as one - not a crash.

echo "Build: ./stage5/mkimage.sh"
if "$REPO/stage5/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI carries the MZ and PE magics, machine type x86-64, subsystem EFI
# application, relocations stripped; and esp.img contains it, byte for byte, at
# the UEFI removable-media path. Stage 4's criteria, on Stage 5's binary.

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
  echo "  python3 broker/germline.py"
  echo "  qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios $OVMF -drive format=raw,file=stage5/out/esp.img -drive format=raw,file=stage5/out/notes.img,if=virtio -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0 -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
