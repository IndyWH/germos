#!/usr/bin/env bash
#
# Stage 8 ring 8b acceptance tests - the gate for the first molt.
#
# Implements acceptance tests 1 to 4 of stage8/spec.md as stage8/plan-8b.md
# fixes them. Test 5 is Wajira's, on the HP (stage8/HP-8b.md); his word closes
# the ring.
#
# These tests are written BEFORE the ring's guest code and are frozen once
# written - a PreToolUse hook blocks the implementer from editing this file
# during implementation and fixes. If a test here is genuinely wrong, that is
# a spec question for the owner, not an edit.
#
# stage8/mkimage.sh, stage8/mkstick.py, stage8/stage8.asm and broker/molt.py
# are deliberately NOT frozen. This file, stage8/checkmolt8b.py,
# stage8/bench.asm, stage8/bench.py, stage8/rehearse8b.py, plans/parts/i8042.md
# and the three canned parts hold the criteria.
#
# Everything runs inside QEMU on the twin of the HP. Every request goes to a
# mock or to the germline's collect path, which calls nothing outside the
# repository. This gate never spends a token and never needs the internet.
# It refuses to run at all while anything is listening on 9999, 9998 or 9997.
#
# Every run appends its whole output to stage8/out/gate-8b.log under a dated
# header, with "8b test <n>: PASS|FAIL" lines and a last "8b gate: PASS|FAIL".
#
# Usage:  ./stage8/test-8b.sh [1 2 3 4]    (from anywhere; no argument: all)
# Exit 0 only if every test asked for passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage8/out"
LOG="$OUT/gate-8b.log"

mkdir -p "$OUT"
REV="$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo none)"
if [ "$REV" != none ] && ! git --no-optional-locks -C "$REPO" diff --quiet HEAD 2>/dev/null; then
  REV="$REV+uncommitted"
fi
{
  echo
  echo "=== ring 8b gate $(date -Is) commit $REV ==="
} >> "$LOG"
exec > >(tee -a "$LOG") 2>&1

export GATE_8B=1
fails=0
want="${*:-1 2 3 4}"
ran=""

echo "Stage 8 ring 8b acceptance tests"
echo "repo: $REPO"
echo "log:  $LOG"
echo

for port in 9999 9998 9997; do
  if python3 - "$port" <<'EOF'
import socket, sys
s = socket.socket(); s.settimeout(1.0)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
EOF
  then
    echo "  something is already listening on 127.0.0.1:$port."
    echo "  The gate talks only to its own mock, its own twin and its own relay. Stop it, then run this again."
    echo "8b gate: FAIL"
    exit 1
  fi
done

echo "Build: ./stage8/mkimage.sh, then python3 stage8/mkstick.py"
"$REPO/stage8/mkimage.sh" 2>&1 | sed 's/^/  /'
python3 "$REPO/stage8/mkstick.py" 2>&1 | sed 's/^/  /'
echo

one() {
  # one <n> <title> <checker mode>
  case " $want " in *" $1 "*) : ;; *) return ;; esac
  ran="$ran $1"
  echo "Test $1 - $2"
  t0=$(date +%s)
  if python3 "$REPO/stage8/checkmolt8b.py" "$3"; then
    echo "8b test $1: PASS ($(( $(date +%s) - t0 )) s)"
  else
    echo "8b test $1: FAIL ($(( $(date +%s) - t0 )) s)"
    fails=$((fails + 1))
  fi
  echo
}

one 1 "Artefact and documents: PE32+, the plan parsed cold, the corpus, the canned parts and the bench reassembled, the PARTS.md section, the API-key refusal, the brief" --document
one 2 "The pipeline, mocked: fast beats and is delivered with source 1; slow, wrong and hang stay out; another identity refused; --collect calls nothing" --pipeline
one 3 "Shadow to live, in the twin: orders, restarts, the take, probation, a sitting through the part, the sick part and the watchdog" --shadow

case " $want " in *" 4 "*)
  ran="$ran 4"
  echo "Test 4 - The bodyguard and the regressions: the new frozen paths, the payload table, the argv checks; the whole of ring 8t's gate (8a, 7d, 7c, 7b and 7a inside it)"
  t0=$(date +%s)
  t4=0
  python3 "$REPO/stage8/checkmolt8b.py" --cage || t4=1
  if [ "$t4" -eq 0 ]; then
    echo "    --- ./trials/test-trial2.sh ---"
    "$REPO/trials/test-trial2.sh" || t4=1
  fi
  if [ "$t4" -eq 0 ]; then
    echo "8b test 4: PASS ($(( $(date +%s) - t0 )) s)"
  else
    echo "8b test 4: FAIL ($(( $(date +%s) - t0 )) s)"
    fails=$((fails + 1))
  fi
  echo
  ;;
esac

if [ "$fails" -eq 0 ]; then
  echo "8b gate: PASS (tests$ran)"
  echo
  echo "Test 5 is manual - Wajira's, on the HP, by stage8/HP-8b.md."
  exit 0
fi
echo "8b gate: FAIL ($fails of tests$ran)"
exit 1
