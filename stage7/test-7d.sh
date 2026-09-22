#!/usr/bin/env bash
#
# Stage 7 ring 7d acceptance tests - the gate for the trials.
#
# Implements acceptance tests 1 to 4 from stage7/spec-7d.md, as
# stage7/plan-7d.md, its amendments and stage7/TRIALS.md fix them. Test 5 is
# Wajira's: sitting 1 in the windowed twin, sittings 2 and 3 on the HP; his
# word on the third sitting closes the ring.
#
# These tests are written BEFORE the ring's guest code and are frozen once
# written - a PreToolUse hook blocks the implementer from editing this file
# during implementation and fixes. If a test here is genuinely wrong, that
# is a spec question for the owner, not an edit.
#
# stage7/mkimage.sh and stage7/mkstick.py are deliberately NOT frozen;
# stage7/glass-7d-section.md is the owner's to append. This file,
# stage7/checktrials.py, stage7/trials.py and stage7/TRIALS.md hold the
# criteria. Rings 7a, 7b and 7c's gates are untouched and still frozen: they
# boot the SAME binary and must stay green - test 4 runs them.
#
# Everything runs inside QEMU with OVMF, the patient's CPU model (-cpu
# IvyBridge), the standard VGA device stating 1920x1080 through an EDID, a
# COPY of stage7/out/stick.img on usb-storage behind qemu-xhci, one raw 64 MB
# disk on ide.1, the e1000e carrying the patient's MAC on slirp with
# restrict=on and one guestfwd to the RELAY on 127.0.0.1:9997, and the PS/2
# mouse driven through the monitor. Every drive is a raw file under
# stage7/out/trials/. The one request of this gate (test 2's grow of the test
# app) goes to the MOCK broker (broker/wire.py --mock), which calls nothing
# outside the repository; the trial itself sends nothing. This gate never
# spends a token and never needs the internet. It refuses to run at all
# while anything is listening on 9999, 9998 or 9997.
#
# Every run appends its whole output to stage7/out/gate-7d.log under a dated
# header (plan decision 8); the terminal sees the same lines.
#
# Usage:  ./stage7/test-7d.sh       (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage7/out"
TRIALS="$OUT/trials"
EFI="$OUT/BOOTX64.EFI"
STICK="$OUT/stick.img"
LOG="$OUT/gate-7d.log"
OVMF="/usr/share/ovmf/OVMF.fd"

mkdir -p "$TRIALS"
{
  echo
  echo "=== ring 7d gate $(date -Is) commit $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo none) ==="
} >> "$LOG"
exec > >(tee -a "$LOG") 2>&1

# The cage, spelled once, exactly as ring 7c's gate spells it (the relay on
# 9997 forwards to the broker on 9999).
BROKER_PORT=9999
REHEARSAL_PORT=9998
RELAY_PORT=9997
MAC="6c:3b:e5:3b:86:45"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${RELAY_PORT}"
CAGE_DEVICE="e1000e,netdev=n0,mac=${MAC}"
MACHINE="-machine q35 -cpu IvyBridge -m 256M -bios $OVMF"
DISPLAY="-vga none -device VGA,edid=on,xres=1920,yres=1080"
sata_drive() { printf -- '-drive if=none,id=d0,format=raw,file=%s -device ide-hd,drive=d0,bus=ide.1' "$1"; }
stick_drive() { printf -- '-device qemu-xhci -drive if=none,id=stick,format=raw,file=%s -device usb-storage,drive=stick' "$1"; }

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

echo "Stage 7 ring 7d acceptance tests"
echo "repo: $REPO"
echo "log:  $LOG"
echo

# ------------------------------------------------ the ports must be free ----

for port in "$BROKER_PORT" "$REHEARSAL_PORT" "$RELAY_PORT"; do
  if python3 - "$port" <<'EOF'
import socket, sys
s = socket.socket(); s.settimeout(1.0)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
EOF
  then
    echo "  something is already listening on 127.0.0.1:$port."
    echo "  The gate talks only to its own mock broker, its own twin and its own relay."
    echo "  If the real broker or the relay is running, stop it first; then run this again."
    exit 1
  fi
done

# ------------------------------------------------------------ helpers -------

rd_u2() { od -An -tu2 -j "$2" -N 2 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
rd_u4() { od -An -tu4 -j "$2" -N 4 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
hexat() { xxd -p -s "$2" -l "$3" "$1" 2>/dev/null | tr -d '\n'; }

# ---------------------------------------------------------------- build ------

echo "Build: ./stage7/mkimage.sh, then python3 stage7/mkstick.py"
if "$REPO/stage7/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
if python3 "$REPO/stage7/mkstick.py" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (the stick was not built)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI a PE32+ EFI application (ring 6a's criteria); the stick as ring
# 7c's frozen checker parses it; TRIALS.md parsed cold and both worked
# examples reproduced by trials.py (checktrials.py --document).

echo "Test 1 - Artefact and the document: PE32+; the stick as 7c; TRIALS.md parsed cold, the worked examples reproduced byte for byte"
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
    [ "$machine" = "34404" ] || probs+=("machine is 0x$(printf '%04x' "${machine:-0}"), expected 0x8664 (x86-64)")
    chars=$(rd_u2 "$EFI" $((lfa + 22)))
    chars=${chars:-0}
    [ $((chars & 1)) -eq 1 ] || probs+=("characteristics 0x$(printf '%04x' "$chars") lacks RELOCS_STRIPPED (0x0001)")
    [ $((chars & 2)) -eq 2 ] || probs+=("characteristics 0x$(printf '%04x' "$chars") lacks EXECUTABLE_IMAGE (0x0002)")
    optmagic=$(rd_u2 "$EFI" $((lfa + 24)))
    [ "$optmagic" = "523" ] || probs+=("optional header magic is 0x$(printf '%04x' "${optmagic:-0}"), expected 0x020b (PE32+)")
    subsys=$(rd_u2 "$EFI" $((lfa + 92)))
    [ "$subsys" = "10" ] || probs+=("subsystem is ${subsys:-none}, expected 10 (EFI application)")
  fi
fi

if [ ! -f "$STICK" ]; then
  probs+=("stick.img was not built")
elif [ -f "$EFI" ]; then
  python3 "$REPO/stage7/checkmetal.py" --stick || probs+=("the stick is not what ring 7c's checker asks for (see above)")
fi
python3 "$REPO/stage7/checktrials.py" --document || probs+=("TRIALS.md does not parse cold, or the worked examples are not reproduced (see above)")

if [ "${#probs[@]}" -eq 0 ]; then
  pass "test 1: PE32+ x86-64 EFI application; the stick as 7c; TRIALS.md parsed cold and both worked examples reproduced"
else
  fail "test 1: the artefact or the document is not what the spec asks for"
  for p in "${probs[@]}"; do echo "    - $p"; done
fi
echo

# ------------------------------------------------- test 2: the row ----------
# One boot at -smp 4 from a fresh stick copy on a fresh disk, the relay and
# the mock up for one grow (checktrials.py --row): the boot lines as 7c
# judges them; "! trial" while the test app runs refused with "an app is
# running", nothing journaled; then "! trial" - the serial line, "trial A
# 1/8" on the strip, ring 6c's four-item row to the pixel, the cue line;
# block 1 played on layout A; block 2's row as TRIALS.md's boxes in the
# surface's bytes and on the screen.

echo "Test 2 - Serial and the row, both layouts: the refusal while an app runs, the sitting line, ring 6c's row to the pixel on the A block, the boxes on the B block"
if [ ! -f "$STICK" ] || [ ! -f "$EFI" ]; then
  fail "test 2: no stick was built"
elif python3 "$REPO/stage7/checktrials.py" --row; then
  pass "test 2: both layouts of the row as TRIALS.md draws them, the refusal, the cue"
else
  fail "test 2: the row is not what TRIALS.md says (see above)"
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira: sitting 1 in the windowed twin of the HP (three terminals at the repo root), sittings 2 and 3 on the HP by stage7/METAL.md:"
  echo "  python3 broker/wire.py"
  echo "  python3 broker/relay.py --bind 127.0.0.1 --port $RELAY_PORT"
  echo "  rm -f stage7/out/disk.img; truncate -s 64M stage7/out/disk.img      # only for a blank disk"
  echo "  cp stage7/out/stick.img stage7/out/stick.twin.img                   # QEMU boots a copy; the owner flashes the file"
  echo "  qemu-system-x86_64 $MACHINE -smp 4 $DISPLAY $(stick_drive stage7/out/stick.twin.img) $(sata_drive stage7/out/disk.img) -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 $RELAY_PORT' -device e1000e,netdev=n0,mac=$MAC -serial stdio"
  echo "  then click in the QEMU window to grab the mouse and type: ! trial"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
