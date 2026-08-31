#!/usr/bin/env bash
#
# Stage 1 acceptance tests - the gate for the stage.
#
# Implements acceptance tests 1 to 4 from stage1/spec.md. Test 5 is Wajira's
# eyeball on a windowed run and stays manual: his word is the gate for the stage.
#
# These tests are written BEFORE stage1.asm and are frozen once written - a
# PreToolUse hook blocks the implementer from editing this file during
# implementation and fixes. If a test here is genuinely wrong, that is a spec
# question for the owner, not an edit.
#
# stage1/mkimage.sh, which builds and packs the artefact, is deliberately NOT
# frozen. This file holds the criteria; that one holds the recipe. Test 1 below
# judges the artefact independently of how it was made, by reading the PE header
# fields out of the built file and reading BOOTX64.EFI back out of esp.img.
#
# Everything runs inside QEMU, with OVMF as firmware and exactly one drive: a
# raw FAT image under stage1/out/. No real disk device is touched.
#
# Usage:  ./stage1/test.sh          (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage1/out"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
OVMF="/usr/share/ovmf/OVMF.fd"

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 1 acceptance tests"
echo "repo: $REPO"
echo

# ------------------------------------------------------------ helpers -------
# Little-endian integer reads out of a binary, by byte offset.

rd_u2() { od -An -tu2 -j "$2" -N 2 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
rd_u4() { od -An -tu4 -j "$2" -N 4 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
hexat() { xxd -p -s "$2" -l "$3" "$1" 2>/dev/null | tr -d '\n'; }

# ---------------------------------------------------------------- build ------
# The builder is a separate, unfrozen script. A build failure is a TEST failure,
# reported as one - not a crash.

echo "Build: ./stage1/mkimage.sh"
if "$REPO/stage1/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI carries the MZ and PE magics, machine type x86-64, subsystem EFI
# application, relocations stripped; and esp.img contains it, byte for byte, at
# the UEFI removable-media path.

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

# ------------------------------------------------- the serial check ----------
# Shared by test 2 (-smp 8) and test 3 (-smp 2 and -smp 8). Boots the image
# headless and requires the seven S1: lines from the spec, in order, with
# found = woken = the -smp value.
#
# OVMF chatters heavily on COM1 - ANSI escape sequences, BdsDxe: lines - unlike
# SeaBIOS in Stage 0, so a byte-exact whole-stream comparison is not available
# here. Instead every "S1: ..." run is pulled out of the capture in order. That
# is a scan rather than a line-start match, so a stray firmware escape sequence
# sharing a line with our output cannot break the test, while the content of
# each line stays strict.
#
# Requiring EXACTLY seven also catches a triple-fault reboot loop, which would
# repeat the whole sequence rather than produce a wrong one.
#
# The guest halts forever by design, so timeout killing QEMU (exit 124) is the
# expected outcome. Any other non-zero exit is a QEMU failure.

serial_check() {
  local smp="$1"
  local cap="$OUT/serial.$smp.txt"
  local qerr="$OUT/qemu.$smp.err"
  local lines_file="$OUT/s1.$smp.txt"
  local rc

  rm -f "$cap" "$qerr" "$lines_file"

  timeout -k 5 60 qemu-system-x86_64 \
    -machine q35 -m 256M -smp "$smp" \
    -bios "$OVMF" \
    -drive format=raw,file="$ESP" \
    -display none -serial stdio \
    </dev/null >"$cap" 2>"$qerr"
  rc=$?

  if [ "$rc" -ne 124 ] && [ "$rc" -ne 0 ]; then
    echo "    -smp $smp: qemu exited $rc, expected 124 (killed by the 60s timeout)"
    sed 's/^/      /' "$qerr"
    return 1
  fi

  tr -d '\r' <"$cap" 2>/dev/null | grep -ao 'S1: .*' >"$lines_file" 2>/dev/null

  local -a got=()
  mapfile -t got <"$lines_file"

  local bad=()

  if [ "${#got[@]}" -ne 7 ]; then
    bad+=("expected exactly 7 S1: lines, found ${#got[@]}")
    if [ "${#got[@]}" -gt 7 ]; then
      bad+=("more than seven usually means a triple fault and a reboot loop, not a duplicated print")
    fi
  fi

  local l
  l="${got[0]:-}"; [ "$l" = "S1: alive" ] || bad+=("line 1: got '$l', want 'S1: alive'")

  l="${got[1]:-}"
  if [[ "$l" =~ ^S1:\ gop\ ([0-9]+)x([0-9]+)\ fb\ 0x([0-9a-f]{16})$ ]]; then
    local w="${BASH_REMATCH[1]}" h="${BASH_REMATCH[2]}" fb="${BASH_REMATCH[3]}"
    [ "$w" -gt 0 ] || bad+=("line 2: width is $w")
    [ "$h" -gt 0 ] || bad+=("line 2: height is $h")
    [ "$fb" != "0000000000000000" ] || bad+=("line 2: framebuffer address is zero")
  else
    bad+=("line 2: got '$l', want 'S1: gop <W>x<H> fb 0x<16 hex digits>'")
  fi

  l="${got[2]:-}"; [ "$l" = "S1: boot services exited" ] || \
    bad+=("line 3: got '$l', want 'S1: boot services exited'")
  l="${got[3]:-}"; [ "$l" = "S1: gdt and paging ours" ] || \
    bad+=("line 4: got '$l', want 'S1: gdt and paging ours'")

  local found="" woken=""
  l="${got[4]:-}"
  if [[ "$l" =~ ^S1:\ cores\ found\ ([0-9]+)$ ]]; then
    found="${BASH_REMATCH[1]}"
  else
    bad+=("line 5: got '$l', want 'S1: cores found <N>'")
  fi

  l="${got[5]:-}"
  if [[ "$l" =~ ^S1:\ cores\ woken\ ([0-9]+)$ ]]; then
    woken="${BASH_REMATCH[1]}"
  else
    bad+=("line 6: got '$l', want 'S1: cores woken <N>'")
  fi

  l="${got[6]:-}"; [ "$l" = "S1: done" ] || bad+=("line 7: got '$l', want 'S1: done'")

  [ -n "$found" ] && [ "$found" != "$smp" ] && \
    bad+=("cores found is $found, but the machine was given -smp $smp")
  [ -n "$woken" ] && [ "$woken" != "$smp" ] && \
    bad+=("cores woken is $woken, but the machine was given -smp $smp")
  [ -n "$found" ] && [ -n "$woken" ] && [ "$found" != "$woken" ] && \
    bad+=("cores found ($found) and cores woken ($woken) disagree - a core did not check in")

  if [ "${#bad[@]}" -eq 0 ]; then
    echo "    -smp $smp: seven S1: lines, in order, found = woken = $smp"
    return 0
  fi

  echo "    -smp $smp: the serial log is not what the spec asks for"
  for b in "${bad[@]}"; do echo "      - $b"; done
  echo "      whole capture follows (OVMF chatter included):"
  if [ -s "$cap" ]; then
    cat -v "$cap" | sed 's/^/        /'
  else
    echo "        (nothing was captured at all)"
  fi
  return 1
}

# ------------------------------------------------- test 2: the serial lines --

echo "Test 2 - Serial: the seven S1: lines, in order, at -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 2: no image was built"
elif serial_check 8; then
  pass "test 2: serial log matches the spec at -smp 8"
else
  fail "test 2: serial log does not match the spec at -smp 8"
fi
echo

# --------------------------------------------- test 3: scaling with -smp -----
# The spec: "Test 2's logic passes at -smp 2 and -smp 8 - the count must follow
# the machine, not be baked in."
#
# Two independent boots rather than a reuse of test 2's run. There is no time
# pressure on this stage, and independence is worth twenty seconds: a build that
# hard-codes 8 fails at -smp 2, and one that reads the MADT but never wakes
# anything fails on woken at both.

echo "Test 3 - Scaling: the same seven lines at -smp 2 and at -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 3: no image was built"
else
  scaled=0
  serial_check 2 || scaled=1
  serial_check 8 || scaled=1
  if [ "$scaled" -eq 0 ]; then
    pass "test 3: found = woken = the -smp value, at both 2 and 8"
  else
    fail "test 3: the core count does not follow the machine"
  fi
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira runs, from the repo root:"
  echo "  qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios $OVMF -drive format=raw,file=stage1/out/esp.img -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
