#!/usr/bin/env bash
#
# Stage 6 ring 6a acceptance tests - the gate for the ring.
#
# Implements acceptance tests 1 to 4 from stage6/spec.md (ring 6a). Test 5 is
# Wajira's eyeball on a windowed run with the REAL broker - he types "! make
# me a clock", the clock ticks in its own panel while he types a note beside
# it, the obs strip's numbers move, Esc - and stays manual: his word is the
# gate for the ring.
#
# These tests are written BEFORE stage6.asm and are frozen once written - a
# PreToolUse hook blocks the implementer from editing this file during
# implementation and fixes. If a test here is genuinely wrong, that is a spec
# question for the owner, not an edit.
#
# stage6/mkimage.sh, which builds and packs the artefact, is deliberately NOT
# frozen. This file holds the criteria; that one holds the recipe. Test 1 below
# judges the artefact independently of how it was made.
#
# Everything runs inside QEMU, with OVMF as firmware, the standard VGA device
# stating its preferred mode through an EDID (GLASS.md, "The screen"),
# exactly two drives per guest - a raw FAT boot image and a raw 16 MB
# notebook image, both under stage6/out/, both created here or by the
# broker's twin under stage6/out/rehearsal/ - and the caged network of
# stage4/UMBILICAL.md: slirp with restrict=on and one guestfwd to the broker
# on 127.0.0.1:9999 (the twin, to its own listener on 127.0.0.1:9998). The
# automated tests talk only to the MOCK broker (broker/glass.py --mock),
# which calls nothing outside the repository; this gate never spends a token
# and never needs the internet. It refuses to run at all while anything is
# listening on either port, so it can never talk to a real broker by
# accident. The mock's germline is stage6/out/germline/, wiped here, so the
# real germline/ is never read or written by the gate.
#
# Usage:  ./stage6/test.sh          (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage6/out"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
NOTES="$OUT/notes.img"
OVMF="/usr/share/ovmf/OVMF.fd"
DISK_BYTES=$((16 * 1024 * 1024))

# The cage, spelled once. UMBILICAL.md, "The cage": the guest's whole world is
# 10.0.2.4:9999, delivered per connection to the broker on 127.0.0.1:9999 by
# netcat; everything else gets a RST from slirp. The MAC is the harness's
# choice, so the guest's "S6: nic" line can be checked against a value the
# assembler cannot know. The twin uses the same cage with its own port
# (GLASS.md, "The rehearsal").
BROKER_PORT=9999
REHEARSAL_PORT=9998
MAC="52:54:00:a1:06:01"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${BROKER_PORT}"
CAGE_DEVICE="virtio-net-pci,netdev=n0,mac=${MAC}"

# The display, spelled once. GLASS.md, "The screen": the standard VGA device
# stating 1440x1440 as its preferred mode through an EDID - the mode policy
# under test - and, for the run that proves the fallback, the same device
# with its EDID off. Every QEMU line in this gate, the checker and the twin
# carries one of these; nothing else is a display we boot with.
DISPLAY_EDID="-vga none -device VGA,edid=on,xres=1440,yres=1440"
DISPLAY_NONE="-vga none -device VGA,edid=off"

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 6 ring 6a acceptance tests"
echo "repo: $REPO"
echo

# ------------------------------------------------ the ports must be free ----
# The real broker and this gate cannot share 127.0.0.1:9999, and the gate must
# never talk to anything but its own mock; the twin's listener needs 9998 to
# itself. Refuse, loudly, before building.

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

# The mock's germline and the twin's scratch: fresh for every run, so the
# generation-call counts and the entry counts the tests demand are
# deterministic.
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

echo "Build: ./stage6/mkimage.sh"
if "$REPO/stage6/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI carries the MZ and PE magics, machine type x86-64, subsystem EFI
# application, relocations stripped; and esp.img contains it, byte for byte, at
# the UEFI removable-media path. Stage 5's criteria, on Stage 6's binary.

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
# Used by test 2 at -smp 8, on a FRESH disk, inside the cage, with the
# display given. Boots the image headless and requires the sixteen S6: lines
# from GLASS.md, in order: "S6: edid <W>x<H>" or "S6: edid none" second; the
# gop line equal to the EDID's mode when one was stated; found = woken = the
# -smp value; the console geometry agreeing with the mode from the same log;
# the disk's sector count agreeing with the image the harness made; the
# notebook formatted (the disk was blank); "S6: nic <mac>" carrying the MAC
# the harness gave the device; "S6: component region 0x<16 hex> 1048576
# bytes" with the address 128 mod 4096 (a page-aligned region, the ABI 2
# blob at +128); "S6: obs page 0x<16 hex>" page-aligned; "S6: glass core
# <id>"; and "S6: keyboard ready" still last, so the serial contract after
# it stays exactly Stage 2's. The mode's pixel area is left in LAST_AREA so
# the edid=off run can be checked against the EDID run: the highest mode is
# never smaller than the preferred one.
#
# Nothing is listening on either port during this run (the gate checked
# that first), and nothing should need to be: the guest sends nothing on
# the network at boot.
#
# OVMF chatters heavily on COM1, so every "S6: ..." run is pulled out of the
# capture in order - a scan, not a line-start match. Requiring EXACTLY
# sixteen catches a triple-fault reboot loop. The guest waits for
# keystrokes forever by design, so timeout killing QEMU (exit 124) is the
# expected outcome.

LAST_AREA=0

serial_check() {
  local smp="$1"
  local display="$2"
  local label="$3"
  local disk="$OUT/serial.$label.img"
  local cap="$OUT/serial.$label.txt"
  local qerr="$OUT/qemu.$label.err"
  local lines_file="$OUT/s6.$label.txt"
  local rc

  rm -f "$cap" "$qerr" "$lines_file"
  fresh_disk "$disk"

  # shellcheck disable=SC2086
  timeout -k 5 60 qemu-system-x86_64 \
    -machine q35 -m 256M -smp "$smp" \
    -bios "$OVMF" \
    $display \
    -drive format=raw,file="$ESP" \
    -drive format=raw,file="$disk",if=virtio \
    -netdev "$CAGE_NETDEV" \
    -device "$CAGE_DEVICE" \
    -display none -serial stdio \
    </dev/null >"$cap" 2>"$qerr"
  rc=$?

  if [ "$rc" -ne 124 ] && [ "$rc" -ne 0 ]; then
    echo "    $label: qemu exited $rc, expected 124 (killed by the 60s timeout)"
    sed 's/^/      /' "$qerr"
    return 1
  fi

  tr -d '\r' <"$cap" 2>/dev/null | grep -ao 'S6: .*' >"$lines_file" 2>/dev/null

  local -a got=()
  mapfile -t got <"$lines_file"

  local bad=()

  if [ "${#got[@]}" -ne 16 ]; then
    bad+=("expected exactly 16 S6: lines, found ${#got[@]}")
    if [ "${#got[@]}" -gt 16 ]; then
      bad+=("more than sixteen usually means a reboot loop - and with the IDT up it should have been an ERR: exception line instead")
    fi
  fi
  if grep -aq 'ERR: ' "$cap"; then
    bad+=("the guest reported: $(tr -d '\r' <"$cap" | grep -ao 'ERR: .*' | head -1)")
  fi

  local l w="" h="" ew="" eh=""
  l="${got[0]:-}"; [ "$l" = "S6: alive" ] || bad+=("line 1: got '$l', want 'S6: alive'")

  l="${got[1]:-}"
  if [[ "$l" =~ ^S6:\ edid\ ([0-9]+)x([0-9]+)$ ]]; then
    ew="${BASH_REMATCH[1]}"; eh="${BASH_REMATCH[2]}"
    [ "$ew" -gt 0 ] && [ "$eh" -gt 0 ] || bad+=("line 2: degenerate EDID mode ${ew}x${eh}")
  elif [ "$l" != "S6: edid none" ]; then
    bad+=("line 2: got '$l', want 'S6: edid <W>x<H>' or 'S6: edid none'")
  fi

  l="${got[2]:-}"
  if [[ "$l" =~ ^S6:\ gop\ ([0-9]+)x([0-9]+)\ fb\ 0x([0-9a-f]{16})$ ]]; then
    w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
    local fb="${BASH_REMATCH[3]}"
    [ "$w" -gt 0 ] || bad+=("line 3: width is $w")
    [ "$h" -gt 0 ] || bad+=("line 3: height is $h")
    [ "$fb" != "0000000000000000" ] || bad+=("line 3: framebuffer address is zero")
    if [ -n "$ew" ]; then
      [ "$w" = "$ew" ] && [ "$h" = "$eh" ] || \
        bad+=("line 3: the mode is ${w}x${h}, but the display's EDID prefers ${ew}x${eh} - the preferred mode must win when it is stated")
    fi
    LAST_AREA=$((w * h))
  else
    bad+=("line 3: got '$l', want 'S6: gop <W>x<H> fb 0x<16 hex digits>'")
  fi

  l="${got[3]:-}"; [ "$l" = "S6: boot services exited" ] || \
    bad+=("line 4: got '$l', want 'S6: boot services exited'")
  l="${got[4]:-}"; [ "$l" = "S6: gdt and paging ours" ] || \
    bad+=("line 5: got '$l', want 'S6: gdt and paging ours'")
  l="${got[5]:-}"; [ "$l" = "S6: idt ready" ] || \
    bad+=("line 6: got '$l', want 'S6: idt ready'")

  local found="" woken=""
  l="${got[6]:-}"
  if [[ "$l" =~ ^S6:\ cores\ found\ ([0-9]+)$ ]]; then
    found="${BASH_REMATCH[1]}"
  else
    bad+=("line 7: got '$l', want 'S6: cores found <N>'")
  fi

  l="${got[7]:-}"
  if [[ "$l" =~ ^S6:\ cores\ woken\ ([0-9]+)$ ]]; then
    woken="${BASH_REMATCH[1]}"
  else
    bad+=("line 8: got '$l', want 'S6: cores woken <N>'")
  fi

  l="${got[8]:-}"
  if [[ "$l" =~ ^S6:\ console\ ([0-9]+)x([0-9]+)$ ]]; then
    local cols="${BASH_REMATCH[1]}" rows="${BASH_REMATCH[2]}"
    if [ -n "$w" ] && [ -n "$h" ]; then
      [ "$cols" -eq $((w / 16)) ] || \
        bad+=("line 9: $cols columns, but $w pixels / 16 = $((w / 16))")
      [ "$rows" -eq $((h / 16)) ] || \
        bad+=("line 9: $rows rows, but $h pixels / 16 = $((h / 16))")
    fi
    [ "$cols" -ge 40 ] || bad+=("line 9: only $cols columns - too narrow for the glass")
    [ "$rows" -ge 24 ] || bad+=("line 9: only $rows rows - too short for the glass")
  else
    bad+=("line 9: got '$l', want 'S6: console <COLS>x<ROWS>'")
  fi

  l="${got[9]:-}"
  if [[ "$l" =~ ^S6:\ disk\ ([0-9]+)\ sectors$ ]]; then
    local sectors="${BASH_REMATCH[1]}"
    [ "$sectors" -eq $((DISK_BYTES / 512)) ] || \
      bad+=("line 10: the guest counted $sectors sectors, but the image is $DISK_BYTES bytes = $((DISK_BYTES / 512)) sectors")
  else
    bad+=("line 10: got '$l', want 'S6: disk <N> sectors'")
  fi

  l="${got[10]:-}"; [ "$l" = "S6: notebook formatted" ] || \
    bad+=("line 11: got '$l', want 'S6: notebook formatted' - the disk was blank")

  l="${got[11]:-}"; [ "$l" = "S6: nic $MAC" ] || \
    bad+=("line 12: got '$l', want 'S6: nic $MAC' - the MAC the harness gave the device")

  # The component region: sixteen hex digits, not zero, below 4 GB, and
  # 128 mod 4096 (a page-aligned region, the ABI 2 blob at +128). The
  # number is the cap, a constant by design.
  l="${got[12]:-}"
  if [[ "$l" =~ ^S6:\ component\ region\ 0x([0-9a-f]{16})\ 1048576\ bytes$ ]]; then
    local addr="${BASH_REMATCH[1]}"
    [ "$addr" != "0000000000000000" ] || bad+=("line 13: the component region address is zero")
    [ "${addr:0:8}" = "00000000" ] || bad+=("line 13: the component region 0x$addr is above 4 GB, beyond the identity map")
    [ "${addr:13:3}" = "080" ] || bad+=("line 13: the component region 0x$addr is not 128 mod 4096 - a page-aligned region with the blob at +128 ends in 080")
  else
    bad+=("line 13: got '$l', want 'S6: component region 0x<16 hex digits> 1048576 bytes'")
  fi

  # The obs page: page-aligned, not zero, below 4 GB.
  l="${got[13]:-}"
  if [[ "$l" =~ ^S6:\ obs\ page\ 0x([0-9a-f]{16})$ ]]; then
    local obs="${BASH_REMATCH[1]}"
    [ "$obs" != "0000000000000000" ] || bad+=("line 14: the obs page address is zero")
    [ "${obs:0:8}" = "00000000" ] || bad+=("line 14: the obs page 0x$obs is above 4 GB")
    [ "${obs:13:3}" = "000" ] || bad+=("line 14: the obs page 0x$obs is not page-aligned")
  else
    bad+=("line 14: got '$l', want 'S6: obs page 0x<16 hex digits>'")
  fi

  l="${got[14]:-}"
  if ! [[ "$l" =~ ^S6:\ glass\ core\ [0-9]+$ ]]; then
    bad+=("line 15: got '$l', want 'S6: glass core <id>'")
  fi

  l="${got[15]:-}"; [ "$l" = "S6: keyboard ready" ] || \
    bad+=("line 16: got '$l', want 'S6: keyboard ready'")

  [ -n "$found" ] && [ "$found" != "$smp" ] && \
    bad+=("cores found is $found, but the machine was given -smp $smp")
  [ -n "$woken" ] && [ "$woken" != "$smp" ] && \
    bad+=("cores woken is $woken, but the machine was given -smp $smp")
  [ -n "$found" ] && [ -n "$woken" ] && [ "$found" != "$woken" ] && \
    bad+=("cores found ($found) and cores woken ($woken) disagree - a core did not check in")

  if [ "${#bad[@]}" -eq 0 ]; then
    echo "    $label: sixteen S6: lines, in order, ${got[1]#S6: }, mode ${w}x${h}, found = woken = $smp, geometry and sector count agree, notebook formatted, nic $MAC, region ${got[12]#S6: component region }, obs page ${got[13]#S6: obs page }, ${got[14]#S6: }"
    return 0
  fi

  echo "    $label: the serial log is not what the spec asks for"
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
# Three boots. With the EDID at -smp 8: the sixteen lines, the preferred
# mode taken. With the EDID off at -smp 8: "S6: edid none" and the highest
# mode, whose area is never below the preferred one's. At -smp 1, under the
# checker (it needs a monitor to screendump with): the named ERR: line, no
# glass, no keyboard - and the line on the screen, rendered from the shared
# font (plan amendment A3).

echo "Test 2 - Serial, first boot: sixteen S6: lines with the EDID and without, at -smp 8; the named error at -smp 1"
if [ ! -f "$ESP" ]; then
  fail "test 2: no image was built"
else
  t2=0
  serial_check 8 "$DISPLAY_EDID" "edid" || t2=1
  area_edid=$LAST_AREA
  serial_check 8 "$DISPLAY_NONE" "noedid" || t2=1
  if [ "$t2" -eq 0 ]; then
    if [ "$LAST_AREA" -lt "$area_edid" ]; then
      echo "    noedid: the highest mode has area $LAST_AREA, below the EDID run's $area_edid - the fallback is not the highest mode"
      t2=1
    else
      echo "    noedid: the mode's area $LAST_AREA is not below the EDID run's $area_edid"
    fi
  fi
  python3 "$REPO/stage6/checkglass.py" --one-core || t2=1
  if [ "$t2" -eq 0 ]; then
    pass "test 2: serial log matches the spec with the EDID, without it, and at one core"
  else
    fail "test 2: serial log does not match the spec"
  fi
fi
echo

# ------------------------------------------------- test 3: the glass --------
# The soul of the ring, mocked. The checker starts the MOCK broker with a
# wiped germline and a record file, boots inside the cage with the display,
# types a note and "! test app" via the monitor; the mock serves the canned
# test app - after REHEARSING it in a real headless boot of a copy of this
# same image - and the guest runs it in its panel; the checker types a key
# to the app, screendumps, Tabs to the prompt, types a note beside the
# running app, Tabs back, types another key, screendumps, sends Esc, asks
# "? ping", types a note, screendumps again. It demands the sixteen boot
# lines; the echo exactly the five typed lines (the keys to the app, the
# Tabs and the Esc never reach serial); the record holding one grow whose
# raw bytes ARE the request frame, generated once, rehearsed once, answered
# with the app frame the checker rebuilds from stage6/app.bin, then the
# question; the germline holding exactly that abi2 entry with its
# provenance; the notebook holding exactly the three notes; the app's known
# picture in its panel with the keys it was given, the app's choices on the
# choices row, "running test app" on the strip, the conversation intact and
# then restored with "pong" and the prompt below. At -smp 2 and -smp 8. The
# work is in stage6/checkglass.py, which prints its own diagnosis.

echo "Test 3 - The glass: '! test app' rehearsed, run in its panel, a note typed beside it, Esc, at -smp 2 and -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 3: no image was built"
else
  glassed=0
  python3 "$REPO/stage6/checkglass.py" --glass 2 || glassed=1
  python3 "$REPO/stage6/checkglass.py" --glass 8 || glassed=1
  if [ "$glassed" -eq 0 ]; then
    pass "test 3: the app ran in its panel while the conversation stayed alive, at both -smp 2 and -smp 8"
  else
    fail "test 3: the glass did not hold (see above)"
  fi
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira, in two terminals at the repo root:"
  echo "  python3 broker/glass.py"
  echo "  qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios $OVMF $DISPLAY_EDID -drive format=raw,file=stage6/out/esp.img -drive format=raw,file=stage6/out/notes.img,if=virtio -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0 -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
