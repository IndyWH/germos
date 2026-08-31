#!/usr/bin/env bash
#
# Stage 0 acceptance tests - the gate for the stage.
#
# Implements acceptance tests 1 to 3 from stage0/spec.md. Test 4 is Wajira's
# eyeball on a windowed run and stays manual: his word is the gate for the stage.
#
# These tests are written BEFORE the boot sector code and are frozen once
# written - a PreToolUse hook blocks the implementer from editing this file
# during implementation and fixes. If a test here is genuinely wrong, that is a
# spec question for the owner, not an edit.
#
# Everything runs inside QEMU. No real disk device is touched.
#
# Usage:  ./stage0/test.sh          (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage0/out"
ASM="$REPO/stage0/stage0.asm"
IMG="$OUT/stage0.img"

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 0 acceptance tests"
echo "repo: $REPO"
echo

# ---------------------------------------------------------------- build ------
# The spec's build command, verbatim. A missing source or a NASM error is a test
# failure, reported as one - not a crash. The old image is removed first so a
# stale artefact can never make a test pass.

echo "Build: nasm -f bin stage0/stage0.asm -o stage0/out/stage0.img"
rm -f "$IMG"
if [ ! -f "$ASM" ]; then
  echo "  stage0/stage0.asm does not exist yet - nothing to build"
elif nasm -f bin "$ASM" -o "$IMG" 2>"$OUT/nasm.err"; then
  echo "  ok"
else
  echo "  nasm failed:"
  sed 's/^/    /' "$OUT/nasm.err"
  rm -f "$IMG"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# stage0.img is exactly 512 bytes and its last two bytes are 0x55 0xAA.

echo "Test 1 - Artefact: exactly 512 bytes, boot signature 0x55 0xAA"
if [ ! -f "$IMG" ]; then
  fail "test 1: no image was built"
else
  size=$(stat -c%s "$IMG")
  sig=$(xxd -p -s 510 -l 2 "$IMG")
  if [ "$size" -ne 512 ]; then
    fail "test 1: image is $size bytes, expected exactly 512"
  elif [ "$sig" != "55aa" ]; then
    fail "test 1: last two bytes are 0x${sig:0:2} 0x${sig:2:2}, expected 0x55 0xAA"
  else
    pass "test 1: 512 bytes, signature 0x55 0xAA"
  fi
fi
echo

# ------------------------------------------------- test 2: the serial lines --
# A headless run captures both serial lines, byte-exact and in order. The
# comparison is equality of the whole byte stream against the expected capture -
# not a grep, not a substring - so it enforces the exact text, the CRLF endings,
# the order, and that nothing else was ever sent.
#
# The boot sector halts forever by design, so timeout killing QEMU (exit 124) is
# the expected outcome. Any other non-zero exit is a QEMU failure.

echo "Test 2 - Serial: both lines captured byte-exact, in order"
if [ ! -f "$IMG" ]; then
  fail "test 2: no image was built"
else
  printf 'S0: alive\r\nS0: stripes drawn, hello from the boot sector\r\n' \
    >"$OUT/serial.expected"
  rm -f "$OUT/serial.txt"
  timeout -k 2 10 qemu-system-x86_64 \
    -drive format=raw,file="$IMG" \
    -display none -serial stdio \
    </dev/null >"$OUT/serial.txt" 2>"$OUT/qemu.err"
  rc=$?
  if [ "$rc" -ne 124 ] && [ "$rc" -ne 0 ]; then
    fail "test 2: qemu exited $rc, expected 124 (killed by the 10s timeout)"
    sed 's/^/    /' "$OUT/qemu.err"
  elif cmp -s "$OUT/serial.txt" "$OUT/serial.expected"; then
    pass "test 2: serial capture is byte-exact"
  else
    fail "test 2: serial capture does not match, byte for byte"
    echo "    expected:"
    xxd "$OUT/serial.expected" | sed 's/^/      /'
    echo "    captured:"
    if [ -s "$OUT/serial.txt" ]; then
      xxd "$OUT/serial.txt" | sed 's/^/      /'
    else
      echo "      (nothing)"
    fi
  fi
fi
echo

# ------------------------------------------------------ test 3: the pixels ---
# A scripted run takes a QEMU screendump a few seconds after boot and confirms
# all four stripe colours are present within tolerance, with red/cyan only in
# the top half and blue/yellow only in the bottom half. The work is in
# stage0/checkpixels.py, which prints its own diagnosis on failure.

echo "Test 3 - Pixels: four stripe colours, red/cyan top, blue/yellow bottom"
if [ ! -f "$IMG" ]; then
  fail "test 3: no image was built"
elif python3 "$REPO/stage0/checkpixels.py"; then
  pass "test 3: stripes are on the screen"
else
  fail "test 3: the screen is not the Spectrum stripes (see above)"
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 4 is manual - Wajira runs, from the repo root:"
  echo "  qemu-system-x86_64 -drive format=raw,file=stage0/out/stage0.img -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
