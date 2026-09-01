#!/usr/bin/env bash
#
# Stage 3 acceptance tests - the gate for the stage.
#
# Implements acceptance tests 1 to 4 from stage3/spec.md. Test 5 is Wajira's
# eyeball on a windowed run - boot, read last night's note, add one, reboot,
# see both - and stays manual: his word is the gate for the stage.
#
# These tests are written BEFORE stage3.asm and are frozen once written - a
# PreToolUse hook blocks the implementer from editing this file during
# implementation and fixes. If a test here is genuinely wrong, that is a spec
# question for the owner, not an edit.
#
# stage3/mkimage.sh, which builds and packs the artefact, is deliberately NOT
# frozen. This file holds the criteria; that one holds the recipe. Test 1 below
# judges the artefact independently of how it was made, by reading the PE
# header fields out of the built file and reading BOOTX64.EFI back out of
# esp.img.
#
# Everything runs inside QEMU, with OVMF as firmware and exactly two drives: a
# raw FAT boot image and a raw 16 MB notebook image, both under stage3/out/,
# both created here. No real disk device is touched - and from plan item 1 the
# hook denies any command that tries.
#
# Usage:  ./stage3/test.sh          (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage3/out"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
NOTES="$OUT/notes.img"
OVMF="/usr/share/ovmf/OVMF.fd"
DISK_BYTES=$((16 * 1024 * 1024))

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 3 acceptance tests"
echo "repo: $REPO"
echo

# ------------------------------------------------------------ helpers -------
# Little-endian integer reads out of a binary, by byte offset.

rd_u2() { od -An -tu2 -j "$2" -N 2 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
rd_u4() { od -An -tu4 -j "$2" -N 4 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
hexat() { xxd -p -s "$2" -l "$3" "$1" 2>/dev/null | tr -d '\n'; }

# fresh_disk <path> - a brand-new, all-zero 16 MB raw image. Removed first so
# that no note from an earlier run can survive into this one. A sparse file:
# QEMU reads the holes as zeros, which is exactly the blank disk the
# first-boot format path expects.
fresh_disk() {
  rm -f "$1"
  truncate -s "$DISK_BYTES" "$1"
}

# ---------------------------------------------------------------- build ------
# The builder is a separate, unfrozen script. A build failure is a TEST
# failure, reported as one - not a crash.

echo "Build: ./stage3/mkimage.sh"
if "$REPO/stage3/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI carries the MZ and PE magics, machine type x86-64, subsystem EFI
# application, relocations stripped; and esp.img contains it, byte for byte, at
# the UEFI removable-media path. Stage 2's criteria, on Stage 3's binary.

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
# Used by test 2 at -smp 8, on a FRESH disk. Boots the image headless and
# requires the eleven S3: lines from the spec, in order, with found = woken =
# the -smp value, the console geometry agreeing with the GOP mode from the
# same log, the disk's sector count agreeing with the image the harness made,
# and the notebook reporting itself formatted - because the disk was blank.
#
# OVMF chatters heavily on COM1, so every "S3: ..." run is pulled out of the
# capture in order - a scan, not a line-start match, so a stray firmware escape
# sequence sharing a line with our output cannot break the test, while the
# content of each line stays strict.
#
# Requiring EXACTLY eleven catches a triple-fault reboot loop, which would
# repeat the whole sequence - though with the IDT up a fault should instead
# appear as an "ERR: exception" line, printed with the failing capture below.
#
# The guest waits for keystrokes forever by design, so timeout killing QEMU
# (exit 124) is the expected outcome. Any other non-zero exit is a QEMU
# failure.

serial_check() {
  local smp="$1"
  local disk="$OUT/serial.$smp.img"
  local cap="$OUT/serial.$smp.txt"
  local qerr="$OUT/qemu.$smp.err"
  local lines_file="$OUT/s3.$smp.txt"
  local rc

  rm -f "$cap" "$qerr" "$lines_file"
  fresh_disk "$disk"

  timeout -k 5 60 qemu-system-x86_64 \
    -machine q35 -m 256M -smp "$smp" \
    -bios "$OVMF" \
    -drive format=raw,file="$ESP" \
    -drive format=raw,file="$disk",if=virtio \
    -display none -serial stdio \
    </dev/null >"$cap" 2>"$qerr"
  rc=$?

  if [ "$rc" -ne 124 ] && [ "$rc" -ne 0 ]; then
    echo "    -smp $smp: qemu exited $rc, expected 124 (killed by the 60s timeout)"
    sed 's/^/      /' "$qerr"
    return 1
  fi

  tr -d '\r' <"$cap" 2>/dev/null | grep -ao 'S3: .*' >"$lines_file" 2>/dev/null

  local -a got=()
  mapfile -t got <"$lines_file"

  local bad=()

  if [ "${#got[@]}" -ne 11 ]; then
    bad+=("expected exactly 11 S3: lines, found ${#got[@]}")
    if [ "${#got[@]}" -gt 11 ]; then
      bad+=("more than eleven usually means a reboot loop - and with the IDT up it should have been an ERR: exception line instead")
    fi
  fi

  local l w="" h=""
  l="${got[0]:-}"; [ "$l" = "S3: alive" ] || bad+=("line 1: got '$l', want 'S3: alive'")

  l="${got[1]:-}"
  if [[ "$l" =~ ^S3:\ gop\ ([0-9]+)x([0-9]+)\ fb\ 0x([0-9a-f]{16})$ ]]; then
    w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
    local fb="${BASH_REMATCH[3]}"
    [ "$w" -gt 0 ] || bad+=("line 2: width is $w")
    [ "$h" -gt 0 ] || bad+=("line 2: height is $h")
    [ "$fb" != "0000000000000000" ] || bad+=("line 2: framebuffer address is zero")
  else
    bad+=("line 2: got '$l', want 'S3: gop <W>x<H> fb 0x<16 hex digits>'")
  fi

  l="${got[2]:-}"; [ "$l" = "S3: boot services exited" ] || \
    bad+=("line 3: got '$l', want 'S3: boot services exited'")
  l="${got[3]:-}"; [ "$l" = "S3: gdt and paging ours" ] || \
    bad+=("line 4: got '$l', want 'S3: gdt and paging ours'")
  l="${got[4]:-}"; [ "$l" = "S3: idt ready" ] || \
    bad+=("line 5: got '$l', want 'S3: idt ready'")

  local found="" woken=""
  l="${got[5]:-}"
  if [[ "$l" =~ ^S3:\ cores\ found\ ([0-9]+)$ ]]; then
    found="${BASH_REMATCH[1]}"
  else
    bad+=("line 6: got '$l', want 'S3: cores found <N>'")
  fi

  l="${got[6]:-}"
  if [[ "$l" =~ ^S3:\ cores\ woken\ ([0-9]+)$ ]]; then
    woken="${BASH_REMATCH[1]}"
  else
    bad+=("line 7: got '$l', want 'S3: cores woken <N>'")
  fi

  # The console geometry must be the arithmetic consequence of the GOP mode
  # reported two lines up: 16x16 pixel cells (the 8x8 font scaled 2x), integer
  # division. One rule, applied on both sides of the serial cable. Fourteen
  # rows is the least that holds eleven boot lines, a note, and a prompt.
  l="${got[7]:-}"
  if [[ "$l" =~ ^S3:\ console\ ([0-9]+)x([0-9]+)$ ]]; then
    local cols="${BASH_REMATCH[1]}" rows="${BASH_REMATCH[2]}"
    if [ -n "$w" ] && [ -n "$h" ]; then
      [ "$cols" -eq $((w / 16)) ] || \
        bad+=("line 8: $cols columns, but $w pixels / 16 = $((w / 16))")
      [ "$rows" -eq $((h / 16)) ] || \
        bad+=("line 8: $rows rows, but $h pixels / 16 = $((h / 16))")
    fi
    [ "$cols" -ge 40 ] || bad+=("line 8: only $cols columns - too narrow for the boot log")
    [ "$rows" -ge 14 ] || bad+=("line 8: only $rows rows - too short for the boot log, a note and a prompt")
  else
    bad+=("line 8: got '$l', want 'S3: console <COLS>x<ROWS>'")
  fi

  # The disk. The harness made it, so it knows exactly how many 512-byte
  # sectors the guest must have counted.
  l="${got[8]:-}"
  if [[ "$l" =~ ^S3:\ disk\ ([0-9]+)\ sectors$ ]]; then
    local sectors="${BASH_REMATCH[1]}"
    [ "$sectors" -eq $((DISK_BYTES / 512)) ] || \
      bad+=("line 9: the guest counted $sectors sectors, but the image is $DISK_BYTES bytes = $((DISK_BYTES / 512)) sectors")
  else
    bad+=("line 9: got '$l', want 'S3: disk <N> sectors'")
  fi

  # A fresh, all-zero disk has no header, so this boot must format it.
  l="${got[9]:-}"; [ "$l" = "S3: notebook formatted" ] || \
    bad+=("line 10: got '$l', want 'S3: notebook formatted' - the disk was blank")

  l="${got[10]:-}"; [ "$l" = "S3: keyboard ready" ] || \
    bad+=("line 11: got '$l', want 'S3: keyboard ready'")

  [ -n "$found" ] && [ "$found" != "$smp" ] && \
    bad+=("cores found is $found, but the machine was given -smp $smp")
  [ -n "$woken" ] && [ "$woken" != "$smp" ] && \
    bad+=("cores woken is $woken, but the machine was given -smp $smp")
  [ -n "$found" ] && [ -n "$woken" ] && [ "$found" != "$woken" ] && \
    bad+=("cores found ($found) and cores woken ($woken) disagree - a core did not check in")

  if [ "${#bad[@]}" -eq 0 ]; then
    echo "    -smp $smp: eleven S3: lines, in order, found = woken = $smp, geometry and sector count agree, notebook formatted"
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

echo "Test 2 - Serial, first boot: the eleven S3: lines on a fresh disk, at -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 2: no image was built"
elif serial_check 8; then
  pass "test 2: serial log matches the spec at -smp 8"
else
  fail "test 2: serial log does not match the spec at -smp 8"
fi
echo

# ------------------------------------------------ test 3: persistence --------
# The soul of the stage. Run one: a fresh disk, "remember me" and Enter typed
# via the QEMU monitor, quit; the disk image parsed FROM THE HOST by
# NOTEBOOK.md must hold that one note, byte-exact. Run two: the same image in
# a fresh QEMU must log "S3: notebook 1 notes", put nothing on the wire after
# "S3: keyboard ready", and leave the image untouched. At -smp 2 and -smp 8 -
# memory must follow the machine, not the core count. The work is in
# stage3/checknotes.py, which drives both boots and prints its own diagnosis.

echo "Test 3 - Persistence: type 'remember me', reboot the same disk, the machine remembers, at -smp 2 and -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 3: no image was built"
else
  kept=0
  python3 "$REPO/stage3/checknotes.py" --persist 2 || kept=1
  python3 "$REPO/stage3/checknotes.py" --persist 8 || kept=1
  if [ "$kept" -eq 0 ]; then
    pass "test 3: the note survived a reboot, on disk and on the console, at both -smp 2 and -smp 8"
  else
    fail "test 3: the machine does not keep what it is told (see above)"
  fi
fi
echo

# ------------------------------------------------ test 4: the picture --------
# After the second boot, a screendump: the replayed "remember me" rendered
# pixel-correct from the same font file the assembly includes, the prompt and
# cursor on the row directly below it, and nothing but the two console
# colours anywhere on screen. The work is in stage3/checknotes.py --pixels,
# which drives its own two boots at -smp 8 and prints its own diagnosis.

echo "Test 4 - Pixels: the replayed note above the prompt, rendered from the shared font"
if [ ! -f "$ESP" ]; then
  fail "test 4: no image was built"
elif python3 "$REPO/stage3/checknotes.py" --pixels; then
  pass "test 4: the picture shows the remembered note, the prompt, and the two colours only"
else
  fail "test 4: the screen does not show what the machine remembered (see above)"
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira runs, from the repo root:"
  echo "  qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios $OVMF -drive format=raw,file=stage3/out/esp.img -drive format=raw,file=stage3/out/notes.img,if=virtio -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
