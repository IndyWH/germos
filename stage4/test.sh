#!/usr/bin/env bash
#
# Stage 4 acceptance tests - the gate for the stage.
#
# Implements acceptance tests 1 to 4 from stage4/spec.md. Test 5 is Wajira's
# eyeball on a windowed run with the REAL broker - he types "? " and something
# true and reads Claude's answer on the machine's own screen - and stays
# manual: his word is the gate for the stage.
#
# These tests are written BEFORE stage4.asm and are frozen once written - a
# PreToolUse hook blocks the implementer from editing this file during
# implementation and fixes. If a test here is genuinely wrong, that is a spec
# question for the owner, not an edit.
#
# stage4/mkimage.sh, which builds and packs the artefact, is deliberately NOT
# frozen. This file holds the criteria; that one holds the recipe. Test 1 below
# judges the artefact independently of how it was made.
#
# Everything runs inside QEMU, with OVMF as firmware, exactly two drives - a
# raw FAT boot image and a raw 16 MB notebook image, both under stage4/out/,
# both created here - and the caged network of stage4/UMBILICAL.md: slirp with
# restrict=on and one guestfwd to the broker on 127.0.0.1:9999. The automated
# tests talk only to the MOCK broker (broker/broker.py --mock), which calls
# nothing; this gate never spends a token and never needs the internet. It
# refuses to run at all while anything is listening on the broker's port,
# so it can never talk to a real broker by accident.
#
# Usage:  ./stage4/test.sh          (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage4/out"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
NOTES="$OUT/notes.img"
OVMF="/usr/share/ovmf/OVMF.fd"
DISK_BYTES=$((16 * 1024 * 1024))

# The cage, spelled once. UMBILICAL.md, "The cage": the guest's whole world is
# 10.0.2.4:9999, delivered per connection to the broker on 127.0.0.1:9999 by
# netcat; everything else gets a RST from slirp. The MAC is the harness's
# choice, so the guest's "S4: nic" line can be checked against a value the
# assembler cannot know.
BROKER_PORT=9999
MAC="52:54:00:a1:04:01"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${BROKER_PORT}"
CAGE_DEVICE="virtio-net-pci,netdev=n0,mac=${MAC}"

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 4 acceptance tests"
echo "repo: $REPO"
echo

# ------------------------------------------------ the port must be free ------
# The real broker and this gate cannot share 127.0.0.1:9999, and the gate must
# never talk to anything but its own mock. Refuse, loudly, before building.

if python3 - "$BROKER_PORT" <<'EOF'
import socket, sys
s = socket.socket(); s.settimeout(1.0)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
EOF
then
  echo "  something is already listening on 127.0.0.1:$BROKER_PORT."
  echo "  The gate talks only to its own mock broker. If the real broker is running,"
  echo "  stop it first; then run this again."
  exit 1
fi

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

echo "Build: ./stage4/mkimage.sh"
if "$REPO/stage4/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI carries the MZ and PE magics, machine type x86-64, subsystem EFI
# application, relocations stripped; and esp.img contains it, byte for byte, at
# the UEFI removable-media path. Stage 3's criteria, on Stage 4's binary.

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
# Used by test 2 at -smp 8, on a FRESH disk, inside the cage. Boots the image
# headless and requires the twelve S4: lines from the spec, in order: Stage
# 3's eleven, with found = woken = the -smp value, the console geometry
# agreeing with the GOP mode from the same log, the disk's sector count
# agreeing with the image the harness made, the notebook formatted (the disk
# was blank), plus "S4: nic <mac>" as line eleven carrying the MAC the harness
# gave the device - and "S4: keyboard ready" still last, so the serial
# contract after it stays exactly Stage 2's.
#
# Nothing is listening on the broker's port during this run (the gate checked
# that first), and nothing should need to be: the guest sends nothing on the
# network at boot.
#
# OVMF chatters heavily on COM1, so every "S4: ..." run is pulled out of the
# capture in order - a scan, not a line-start match. Requiring EXACTLY twelve
# catches a triple-fault reboot loop. The guest waits for keystrokes forever
# by design, so timeout killing QEMU (exit 124) is the expected outcome.

serial_check() {
  local smp="$1"
  local disk="$OUT/serial.$smp.img"
  local cap="$OUT/serial.$smp.txt"
  local qerr="$OUT/qemu.$smp.err"
  local lines_file="$OUT/s4.$smp.txt"
  local rc

  rm -f "$cap" "$qerr" "$lines_file"
  fresh_disk "$disk"

  timeout -k 5 60 qemu-system-x86_64 \
    -machine q35 -m 256M -smp "$smp" \
    -bios "$OVMF" \
    -drive format=raw,file="$ESP" \
    -drive format=raw,file="$disk",if=virtio \
    -netdev "$CAGE_NETDEV" \
    -device "$CAGE_DEVICE" \
    -display none -serial stdio \
    </dev/null >"$cap" 2>"$qerr"
  rc=$?

  if [ "$rc" -ne 124 ] && [ "$rc" -ne 0 ]; then
    echo "    -smp $smp: qemu exited $rc, expected 124 (killed by the 60s timeout)"
    sed 's/^/      /' "$qerr"
    return 1
  fi

  tr -d '\r' <"$cap" 2>/dev/null | grep -ao 'S4: .*' >"$lines_file" 2>/dev/null

  local -a got=()
  mapfile -t got <"$lines_file"

  local bad=()

  if [ "${#got[@]}" -ne 12 ]; then
    bad+=("expected exactly 12 S4: lines, found ${#got[@]}")
    if [ "${#got[@]}" -gt 12 ]; then
      bad+=("more than twelve usually means a reboot loop - and with the IDT up it should have been an ERR: exception line instead")
    fi
  fi

  local l w="" h=""
  l="${got[0]:-}"; [ "$l" = "S4: alive" ] || bad+=("line 1: got '$l', want 'S4: alive'")

  l="${got[1]:-}"
  if [[ "$l" =~ ^S4:\ gop\ ([0-9]+)x([0-9]+)\ fb\ 0x([0-9a-f]{16})$ ]]; then
    w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
    local fb="${BASH_REMATCH[3]}"
    [ "$w" -gt 0 ] || bad+=("line 2: width is $w")
    [ "$h" -gt 0 ] || bad+=("line 2: height is $h")
    [ "$fb" != "0000000000000000" ] || bad+=("line 2: framebuffer address is zero")
  else
    bad+=("line 2: got '$l', want 'S4: gop <W>x<H> fb 0x<16 hex digits>'")
  fi

  l="${got[2]:-}"; [ "$l" = "S4: boot services exited" ] || \
    bad+=("line 3: got '$l', want 'S4: boot services exited'")
  l="${got[3]:-}"; [ "$l" = "S4: gdt and paging ours" ] || \
    bad+=("line 4: got '$l', want 'S4: gdt and paging ours'")
  l="${got[4]:-}"; [ "$l" = "S4: idt ready" ] || \
    bad+=("line 5: got '$l', want 'S4: idt ready'")

  local found="" woken=""
  l="${got[5]:-}"
  if [[ "$l" =~ ^S4:\ cores\ found\ ([0-9]+)$ ]]; then
    found="${BASH_REMATCH[1]}"
  else
    bad+=("line 6: got '$l', want 'S4: cores found <N>'")
  fi

  l="${got[6]:-}"
  if [[ "$l" =~ ^S4:\ cores\ woken\ ([0-9]+)$ ]]; then
    woken="${BASH_REMATCH[1]}"
  else
    bad+=("line 7: got '$l', want 'S4: cores woken <N>'")
  fi

  l="${got[7]:-}"
  if [[ "$l" =~ ^S4:\ console\ ([0-9]+)x([0-9]+)$ ]]; then
    local cols="${BASH_REMATCH[1]}" rows="${BASH_REMATCH[2]}"
    if [ -n "$w" ] && [ -n "$h" ]; then
      [ "$cols" -eq $((w / 16)) ] || \
        bad+=("line 8: $cols columns, but $w pixels / 16 = $((w / 16))")
      [ "$rows" -eq $((h / 16)) ] || \
        bad+=("line 8: $rows rows, but $h pixels / 16 = $((h / 16))")
    fi
    [ "$cols" -ge 40 ] || bad+=("line 8: only $cols columns - too narrow for the boot log")
    [ "$rows" -ge 20 ] || bad+=("line 8: only $rows rows - too short for the boot log, a question, an answer and a prompt")
  else
    bad+=("line 8: got '$l', want 'S4: console <COLS>x<ROWS>'")
  fi

  l="${got[8]:-}"
  if [[ "$l" =~ ^S4:\ disk\ ([0-9]+)\ sectors$ ]]; then
    local sectors="${BASH_REMATCH[1]}"
    [ "$sectors" -eq $((DISK_BYTES / 512)) ] || \
      bad+=("line 9: the guest counted $sectors sectors, but the image is $DISK_BYTES bytes = $((DISK_BYTES / 512)) sectors")
  else
    bad+=("line 9: got '$l', want 'S4: disk <N> sectors'")
  fi

  l="${got[9]:-}"; [ "$l" = "S4: notebook formatted" ] || \
    bad+=("line 10: got '$l', want 'S4: notebook formatted' - the disk was blank")

  # The NIC. The harness gave the device its MAC, so it knows exactly what the
  # guest must have read out of the device configuration.
  l="${got[10]:-}"; [ "$l" = "S4: nic $MAC" ] || \
    bad+=("line 11: got '$l', want 'S4: nic $MAC' - the MAC the harness gave the device")

  l="${got[11]:-}"; [ "$l" = "S4: keyboard ready" ] || \
    bad+=("line 12: got '$l', want 'S4: keyboard ready'")

  [ -n "$found" ] && [ "$found" != "$smp" ] && \
    bad+=("cores found is $found, but the machine was given -smp $smp")
  [ -n "$woken" ] && [ "$woken" != "$smp" ] && \
    bad+=("cores woken is $woken, but the machine was given -smp $smp")
  [ -n "$found" ] && [ -n "$woken" ] && [ "$found" != "$woken" ] && \
    bad+=("cores found ($found) and cores woken ($woken) disagree - a core did not check in")

  if [ "${#bad[@]}" -eq 0 ]; then
    echo "    -smp $smp: twelve S4: lines, in order, found = woken = $smp, geometry and sector count agree, notebook formatted, nic $MAC"
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

echo "Test 2 - Serial, first boot: the twelve S4: lines on a fresh disk inside the cage, at -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 2: no image was built"
elif serial_check 8; then
  pass "test 2: serial log matches the spec at -smp 8"
else
  fail "test 2: serial log does not match the spec at -smp 8"
fi
echo

# ------------------------------------------ test 3: the question round trip --
# The soul of the stage. The checker starts the MOCK broker with a record
# file, boots inside the cage, types "? ping", a note, and "? hello" via the
# monitor, and screendumps. It demands the twelve boot lines; the echo exactly
# the three typed lines; the broker's record holding exactly two connections
# whose raw bytes ARE the frames for "ping" and "hello" by UMBILICAL.md's own
# rule; the notebook holding exactly the note and nothing for the questions;
# and both answers on the screen, pixel-correct from the shared font, with
# the prompt below. At -smp 2 and -smp 8. The work is in
# stage4/checkumbilical.py, which prints its own diagnosis.

echo "Test 3 - The question: '? ping' and '? hello' round-trip through the mock broker, a note between them, at -smp 2 and -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 3: no image was built"
else
  asked=0
  python3 "$REPO/stage4/checkumbilical.py" --question 2 || asked=1
  python3 "$REPO/stage4/checkumbilical.py" --question 8 || asked=1
  if [ "$asked" -eq 0 ]; then
    pass "test 3: the machine asked and was answered, on screen and in the broker's record, at both -smp 2 and -smp 8"
  else
    fail "test 3: the question did not round-trip (see above)"
  fi
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira, in two terminals at the repo root:"
  echo "  python3 broker/broker.py"
  echo "  qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios $OVMF -drive format=raw,file=stage4/out/esp.img -drive format=raw,file=stage4/out/notes.img,if=virtio -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0 -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
