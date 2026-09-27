#!/usr/bin/env bash
#
# Stage 8 ring 8a acceptance tests - the gate for the floor.
#
# Implements acceptance tests 1 to 4 from stage8/spec.md, as
# stage8/plan-8a.md, its amendments and stage8/PARTS.md fix them. Test 5 is
# Wajira's: good to the threshold and live, Esc, and hang live on the HP
# until the HP resets itself (stage8/HP-8a.md); his word closes the ring.
#
# These tests are written BEFORE the ring's guest code and are frozen once
# written - a PreToolUse hook blocks the implementer from editing this file
# during implementation and fixes. If a test here is genuinely wrong, that
# is a spec question for the owner, not an edit.
#
# stage8/mkimage.sh, stage8/mkstick.py, stage8/stage8.asm and broker/molt.py
# are deliberately NOT frozen. This file, stage8/checkmolt.py,
# stage8/parts.py, stage8/PARTS.md, stage8/SEED.md and the five fixtures
# hold the criteria. The earlier gates are untouched and still frozen: they
# boot ring 7d's own binary and must stay green.
#
# Everything runs inside QEMU with OVMF, the patient's CPU model (-cpu
# IvyBridge), the standard VGA device stating 1920x1080 through an EDID, a
# COPY of stage8/out/stick.img on usb-storage behind qemu-xhci, one raw 64 MB
# disk on ide.1, the e1000e carrying the patient's MAC on slirp with
# restrict=on and one guestfwd to the RELAY on 127.0.0.1:9997, and the PS/2
# mouse driven through the monitor. Every drive is a raw file under
# stage8/out/. Every request goes to a MOCK broker, which calls nothing
# outside the repository. This gate never spends a token and never needs
# the internet. It refuses to run at all while anything is listening on
# 9999, 9998 or 9997.
#
# Every run appends its whole output to stage8/out/gate-8a.log under a dated
# header (plan decision 15); the terminal sees the same lines.
#
# Usage:  ./stage8/test-8a.sh       (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage8/out"
MOLT="$OUT/molt"
SEVEN="$OUT/seven"
EFI="$OUT/BOOTX64.EFI"
STICK="$OUT/stick.img"
LOG="$OUT/gate-8a.log"
OVMF="/usr/share/ovmf/OVMF.fd"

mkdir -p "$OUT" "$MOLT" "$SEVEN"
{
  echo
  echo "=== ring 8a gate $(date -Is) commit $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo none) ==="
} >> "$LOG"
exec > >(tee -a "$LOG") 2>&1

# The checker writes no second header under the gate: this one holds the log.
export GATE_8A=1

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

echo "Stage 8 ring 8a acceptance tests"
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

echo "Build: ./stage8/mkimage.sh, then python3 stage8/mkstick.py"
if "$REPO/stage8/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
if python3 "$REPO/stage8/mkstick.py" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (the stick was not built)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI a PE32+ EFI application (ring 6a's criteria); then
# checkmolt.py --document: the stick as ring 7c's frozen checker parses it;
# PARTS.md and SEED.md read cold by parts.py with every worked example
# reproduced byte for byte; the five fixtures reassembled byte-identical,
# each header valid; SHA-256's known answer and the round constants in the
# build; the seed record parsed and append-only.

echo "Test 1 - Artefact and the documents: PE32+; the stick as 7c; PARTS.md and SEED.md read cold, the worked examples reproduced byte for byte; the fixtures reassembled; SHA-256's known answer; the seed record"
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
fi
if [ -f "$EFI" ] && [ -f "$STICK" ]; then
  python3 "$REPO/stage8/checkmolt.py" --document || probs+=("the stick, the documents, the fixtures, SHA-256 or the seed record are not what PARTS.md and SEED.md say (see above)")
fi

if [ "${#probs[@]}" -eq 0 ]; then
  pass "test 1: PE32+ x86-64 EFI application; the stick as 7c; PARTS.md and SEED.md read cold and every worked example reproduced; the five fixtures; SHA-256's known answer; the seed record"
else
  fail "test 1: the artefact or the documents are not what the spec asks for"
  for p in "${probs[@]}"; do echo "    - $p"; done
fi
echo

# ------------------------------------------ test 2: no part, no change ------
# checkmolt.py --seven: ring 7c's and ring 7d's frozen checks pointed at
# stage8's build through their module seams (D3): the serial boots blank 8,
# again 4 and novga 2; the stages run with the mock's twin on
# stage8/out/esp.img; the row; the sittings to verdict B and the next
# boot in layout B. Each returns success; nothing outside stage8/out/
# changes; no capture under stage8/out/seven/ holds an S8:, part: or
# molt: line.

echo "Test 2 - No part, no change: the 7c serial boots and stages, the 7d row and sittings, on stage8's build; no S8:, part: or molt: line"
if [ ! -f "$STICK" ] || [ ! -f "$EFI" ]; then
  fail "test 2: no stick was built"
elif python3 "$REPO/stage8/checkmolt.py" --seven; then
  pass "test 2: with no part installed the Stage 8 binary is ring 7d's to every frozen 7c and 7d check, and says nothing of ring 8a"
else
  fail "test 2: with no part installed the Stage 8 binary is not ring 7d's (see above)"
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira's, on the HP, by stage8/HP-8a.md."
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
