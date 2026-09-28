#!/usr/bin/env bash
#
# Ring 8t acceptance tests - the gate for trial two (G against B).
#
# Implements acceptance tests 1 to 4 of trials/spec-trial2.md (section 11,
# with Amendment 1), as trials/plan-8t.md, its amendments A1-A5 and
# trials/TRIALS2.md fix them. Test 5 is Wajira's: four sittings on the HP,
# one a boot, by trials/HP-8t.md; his word closes the ring.
#
# These tests are written BEFORE the ring's guest code and are frozen once
# written - a PreToolUse hook blocks the implementer from editing this file
# during implementation and fixes. If a test here is genuinely wrong, that
# is a spec question for the owner, not an edit.
#
# stage8/stage8.asm, stage8/mkimage.sh and stage8/mkstick.py are
# deliberately NOT frozen. This file, trials/checktrials2.py,
# trials/trials2.py and trials/TRIALS2.md hold the criteria. The earlier
# gates are untouched and still frozen; test 4 runs ring 8a's whole gate,
# with ring 7d's, 7c's, 7b's and 7a's inside it.
#
# Everything runs inside QEMU with OVMF, the patient's CPU model (-cpu
# IvyBridge), the standard VGA device stating 1920x1080 through an EDID, a
# COPY of stage8/out/stick.img on usb-storage behind qemu-xhci, one raw 64 MB
# disk on ide.1, the e1000e carrying the patient's MAC on slirp with
# restrict=on and one guestfwd to 127.0.0.1:9997 (nothing listens there in
# this ring's own tests: a trial sends nothing over the wire), and the PS/2
# mouse driven through the monitor. Every drive is a raw file under
# trials/out/. This gate never spends a token and never needs the internet.
# It refuses to run at all while anything is listening on 9999, 9998 or 9997.
#
# Every run appends its whole output to trials/out/gate-8t.log under a dated
# header, then one summary line per test ("8t test <n>: PASS|FAIL ...") and a
# last line "8t gate: PASS" or "8t gate: FAIL" (plan D6).
#
# Usage:  ./trials/test-trial2.sh       (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/trials/out"
T8="$OUT/t8"
S8OUT="$REPO/stage8/out"
EFI="$S8OUT/BOOTX64.EFI"
STICK="$S8OUT/stick.img"
LOG="$OUT/gate-8t.log"
OVMF="/usr/share/ovmf/OVMF.fd"

mkdir -p "$OUT" "$T8"
REV="$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo none)"
if [ "$REV" != none ] && ! git --no-optional-locks -C "$REPO" diff --quiet HEAD 2>/dev/null; then
  REV="$REV+uncommitted"
fi
{
  echo
  echo "=== ring 8t gate $(date -Is) commit $REV ==="
} >> "$LOG"
exec > >(tee -a "$LOG") 2>&1

# The checker writes no second header under the gate: this one holds the log.
export GATE_8T=1

# The cage, spelled once, exactly as ring 7c's gate spells it.
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
summary=()
pass() { printf '  PASS  %s\n' "$2"; summary+=("8t test $1: PASS - $2"); }
fail() { printf '  FAIL  %s\n' "$2"; summary+=("8t test $1: FAIL - $2"); fails=$((fails + 1)); }

echo "Ring 8t acceptance tests - trial two"
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
    echo "  Test 4 runs ring 8a's gate, which talks only to its own mock broker, twin and relay."
    echo "  If the real broker or the relay is running, stop it first; then run this again."
    echo
    echo "8t gate: FAIL - 127.0.0.1:$port is busy; no test ran"
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

# --------------------------------------------------- test 1: the documents ---
# BOOTX64.EFI a PE32+ EFI application (ring 6a's criteria); then
# checktrials2.py --document: the stick as ring 7c's frozen checker parses
# it; TRIALS2.md read cold by trials2.py with every worked example
# reproduced; the HP's history rebuilt from the pinned charts meeting every
# checkpoint, written to a host-formatted disk and read back by the frozen
# parsers; the run's G rows and trial_number's offset equal to the rule.

echo "Test 1 - The documents: PE32+; the stick as 7c; TRIALS2.md read cold, the worked examples reproduced; the blind read; the HP's history; the G rows"
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
  python3 "$REPO/trials/checktrials2.py" --document || probs+=("the stick, TRIALS2.md, the HP's history or the G rows are not what the documents say (see above)")
fi

if [ "${#probs[@]}" -eq 0 ]; then
  pass 1 "PE32+ x86-64 EFI application; the stick as 7c; TRIALS2.md read cold and every worked example reproduced; the blind read; the HP's history and home read back; the G rows by rule"
else
  fail 1 "the artefact or the documents are not what the spec asks for"
  for p in "${probs[@]}"; do echo "    - $p"; done
fi
echo

# ------------------------------------------ test 2: the rows and the refusals -
# checktrials2.py --rows, four disks at -smp 4. R1, blank: no boot line and
# no offer; '! trial 2' opens sitting 1 with the warm-up's G row to the
# pixel, its B row at cue 6, block 1, Esc in block 2 and the saved line;
# then the refusals and the widened reserved prefix. C: trial two concluded
# (verdict G): the boot line, no offer, the prompt row in G, the refusal, an
# empty Enter plain, a click on a G zone and on a '|'. S: good in shadow
# with a sitting done and the calculator: the offer; 'an app is running' and
# the part refusal, each by '! trial 2' and by an empty Enter. L: good live.

echo "Test 2 - The rows and the refusals: G and B to the pixel, the five refusals by '! trial 2' and by Enter, the reserved prefix"
if [ ! -f "$STICK" ] || [ ! -f "$EFI" ]; then
  fail 2 "no stick was built"
elif python3 "$REPO/trials/checktrials2.py" --rows; then
  pass 2 "the G and B rows as TRIALS2.md draws them, every refusal in its order by '! trial 2' and by an empty Enter, the reserved prefix"
else
  fail 2 "the rows or the refusals are not what TRIALS2.md says (see above)"
fi
echo

# ------------------------------------------------------------- summary -------

for line in "${summary[@]}"; do
  echo "$line"
done
if [ "$fails" -eq 0 ]; then
  echo "8t gate: PASS"
  echo
  echo "Test 5 is manual - Wajira's, on the HP, by trials/HP-8t.md."
  exit 0
else
  echo "8t gate: FAIL - $fails test(s) failed"
  exit 1
fi
