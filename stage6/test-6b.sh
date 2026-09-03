#!/usr/bin/env bash
#
# Stage 6 ring 6b acceptance tests - the gate for the store of plans.
#
# Implements acceptance tests 1 to 4 from stage6/spec.md (ring 6b). Test 5 is
# Wajira's eyeball on a windowed run with the REAL broker - he types
# "! install calculator", does a sum, reboots with the broker off, types
# "! calculator", and the sum still works - and stays manual: his word is
# the gate for the ring.
#
# These tests are written BEFORE the ring's code and are frozen once written
# - a PreToolUse hook blocks the implementer from editing this file during
# implementation and fixes. If a test here is genuinely wrong, that is a spec
# question for the owner, not an edit.
#
# stage6/mkimage.sh, which builds and packs the artefact, is deliberately NOT
# frozen. This file holds the criteria; that one holds the recipe. Test 1 below
# judges the artefact independently of how it was made. Ring 6a's own gate,
# stage6/test.sh, is untouched and still frozen: it boots the SAME binary with
# one disk at 1440x1440 and demands ring 6a's sixteen lines, and it must stay
# green - it is this ring's proof that nothing 6a built has moved.
#
# Everything runs inside QEMU, with OVMF as firmware, the standard VGA device
# stating 1920x1080 through an EDID (the owner's decision at ring 6a's
# oracle: the gate, the twin and the oracle are the same machine again),
# exactly THREE drives per guest - a raw FAT boot image, a raw 16 MB notebook
# image and a raw 16 MB home image (stage6/HOME.md), all under stage6/out/,
# all created here or by the broker's twin under stage6/out/rehearsal/ - and
# the caged network of stage4/UMBILICAL.md: slirp with restrict=on and one
# guestfwd to the broker on 127.0.0.1:9999 (the twin, to its own listener on
# 127.0.0.1:9998). The automated tests talk only to the MOCK broker
# (broker/plans.py --mock), which calls nothing outside the repository; this
# gate never spends a token and never needs the internet. It refuses to run
# at all while anything is listening on either port. The mock's germline is
# stage6/out/germline/, wiped here.
#
# Usage:  ./stage6/test-6b.sh       (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage6/out"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
NOTES="$OUT/notes.img"
HOME_IMG="$OUT/home.img"
OVMF="/usr/share/ovmf/OVMF.fd"
DISK_BYTES=$((16 * 1024 * 1024))

# The cage, spelled once (UMBILICAL.md, "The cage"), with this ring's MAC so
# the guest's "S6: nic" line is checked against a value the assembler cannot
# know. The twin uses the same cage with its own port.
BROKER_PORT=9999
REHEARSAL_PORT=9998
MAC="52:54:00:a1:06:02"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${BROKER_PORT}"
CAGE_DEVICE="virtio-net-pci,netdev=n0,mac=${MAC}"

# The display, spelled once: the standard VGA device stating 1920x1080 as
# its preferred mode through an EDID. Every QEMU line in this gate, the
# checker and the twin (broker/plans.py sets the frozen twin's flags to the
# same) carries this; nothing else is a display we boot with.
DISPLAY="-vga none -device VGA,edid=on,xres=1920,yres=1080"

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 6 ring 6b acceptance tests"
echo "repo: $REPO"
echo

# ------------------------------------------------ the ports must be free ----

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

# The mock's germline and the twin's scratch: fresh for every run.
rm -rf "$OUT/germline" "$OUT/rehearsal"

# ------------------------------------------------------------ helpers -------

rd_u2() { od -An -tu2 -j "$2" -N 2 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
rd_u4() { od -An -tu4 -j "$2" -N 4 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
hexat() { xxd -p -s "$2" -l "$3" "$1" 2>/dev/null | tr -d '\n'; }

# fresh_disk <path> - a brand-new, all-zero 16 MB raw image.
fresh_disk() {
  rm -f "$1"
  truncate -s "$DISK_BYTES" "$1"
}

# ---------------------------------------------------------------- build ------

echo "Build: ./stage6/mkimage.sh"
if "$REPO/stage6/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI carries the MZ and PE magics, machine type x86-64, subsystem EFI
# application, relocations stripped; and esp.img contains it, byte for byte,
# at the UEFI removable-media path. Ring 6a's criteria, on this ring's binary.

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
# serial_check <smp> <disks> <label> [home image]. Boots the image headless
# inside the cage with the display, with a fresh notebook image and - when
# disks is 2 - the given home image, and requires HOME.md's SEVENTEEN S6:
# lines in order (or ring 6a's sixteen when disks is 1 - HOME.md, "Two
# disks": without a second virtio-blk the machine is ring 6a's, line for
# line): "S6: edid <W>x<H>" second and the gop line equal to it; found =
# woken = the -smp value; the console geometry from the mode; the disk's
# sector count from the image the harness made; the notebook formatted;
# "S6: home <N> apps" TWELFTH with the N the caller expects; "S6: nic <mac>"
# with the harness's MAC; the component region 128 mod 4096; the obs page
# page-aligned; "S6: glass core <id>"; "S6: keyboard ready" last. The guest
# waits for keystrokes forever, so exit 124 is the expected outcome.

serial_check() {
  local smp="$1"
  local disks="$2"
  local label="$3"
  local home="${4:-}"
  local want_home="${5:-0}"
  local disk="$OUT/serial.$label.img"
  local cap="$OUT/serial.$label.txt"
  local qerr="$OUT/qemu.$label.err"
  local lines_file="$OUT/s6.$label.txt"
  local rc want_lines=17
  local -a home_drive=()

  rm -f "$cap" "$qerr" "$lines_file"
  fresh_disk "$disk"
  if [ "$disks" = "2" ]; then
    home_drive=(-drive "format=raw,file=$home,if=virtio")
  else
    want_lines=16
  fi

  # shellcheck disable=SC2086
  timeout -k 5 60 qemu-system-x86_64 \
    -machine q35 -m 256M -smp "$smp" \
    -bios "$OVMF" \
    $DISPLAY \
    -drive format=raw,file="$ESP" \
    -drive format=raw,file="$disk",if=virtio \
    "${home_drive[@]}" \
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

  if [ "${#got[@]}" -ne "$want_lines" ]; then
    bad+=("expected exactly $want_lines S6: lines with $disks virtio disk(s), found ${#got[@]}")
  fi
  if grep -aq 'ERR: ' "$cap"; then
    bad+=("the guest reported: $(tr -d '\r' <"$cap" | grep -ao 'ERR: .*' | head -1)")
  fi

  local l w="" h="" ew="" eh=""
  l="${got[0]:-}"; [ "$l" = "S6: alive" ] || bad+=("line 1: got '$l', want 'S6: alive'")

  l="${got[1]:-}"
  if [[ "$l" =~ ^S6:\ edid\ ([0-9]+)x([0-9]+)$ ]]; then
    ew="${BASH_REMATCH[1]}"; eh="${BASH_REMATCH[2]}"
  else
    bad+=("line 2: got '$l', want 'S6: edid <W>x<H>' - the harness gave the device an EDID")
  fi

  l="${got[2]:-}"
  if [[ "$l" =~ ^S6:\ gop\ ([0-9]+)x([0-9]+)\ fb\ 0x([0-9a-f]{16})$ ]]; then
    w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
    [ "${BASH_REMATCH[3]}" != "0000000000000000" ] || bad+=("line 3: framebuffer address is zero")
    if [ -n "$ew" ]; then
      [ "$w" = "$ew" ] && [ "$h" = "$eh" ] || \
        bad+=("line 3: the mode is ${w}x${h}, but the display's EDID prefers ${ew}x${eh}")
    fi
  else
    bad+=("line 3: got '$l', want 'S6: gop <W>x<H> fb 0x<16 hex digits>'")
  fi

  l="${got[3]:-}"; [ "$l" = "S6: boot services exited" ] || bad+=("line 4: got '$l', want 'S6: boot services exited'")
  l="${got[4]:-}"; [ "$l" = "S6: gdt and paging ours" ] || bad+=("line 5: got '$l', want 'S6: gdt and paging ours'")
  l="${got[5]:-}"; [ "$l" = "S6: idt ready" ] || bad+=("line 6: got '$l', want 'S6: idt ready'")

  local found="" woken=""
  l="${got[6]:-}"
  if [[ "$l" =~ ^S6:\ cores\ found\ ([0-9]+)$ ]]; then found="${BASH_REMATCH[1]}"; else bad+=("line 7: got '$l', want 'S6: cores found <N>'"); fi
  l="${got[7]:-}"
  if [[ "$l" =~ ^S6:\ cores\ woken\ ([0-9]+)$ ]]; then woken="${BASH_REMATCH[1]}"; else bad+=("line 8: got '$l', want 'S6: cores woken <N>'"); fi

  l="${got[8]:-}"
  if [[ "$l" =~ ^S6:\ console\ ([0-9]+)x([0-9]+)$ ]]; then
    local cols="${BASH_REMATCH[1]}" rows="${BASH_REMATCH[2]}"
    if [ -n "$w" ] && [ -n "$h" ]; then
      [ "$cols" -eq $((w / 16)) ] || bad+=("line 9: $cols columns, but $w pixels / 16 = $((w / 16))")
      [ "$rows" -eq $((h / 16)) ] || bad+=("line 9: $rows rows, but $h pixels / 16 = $((h / 16))")
    fi
  else
    bad+=("line 9: got '$l', want 'S6: console <COLS>x<ROWS>'")
  fi

  l="${got[9]:-}"
  if [[ "$l" =~ ^S6:\ disk\ ([0-9]+)\ sectors$ ]]; then
    [ "${BASH_REMATCH[1]}" -eq $((DISK_BYTES / 512)) ] || \
      bad+=("line 10: the guest counted ${BASH_REMATCH[1]} sectors, but the image is $((DISK_BYTES / 512)) sectors")
  else
    bad+=("line 10: got '$l', want 'S6: disk <N> sectors'")
  fi

  l="${got[10]:-}"; [ "$l" = "S6: notebook formatted" ] || bad+=("line 11: got '$l', want 'S6: notebook formatted' - the disk was blank")

  # From here the line numbers depend on the disk count: with two disks
  # the home line is twelfth and everything after it moves down one.
  local off=0
  if [ "$disks" = "2" ]; then
    l="${got[11]:-}"; [ "$l" = "S6: home $want_home apps" ] || \
      bad+=("line 12: got '$l', want 'S6: home $want_home apps' (HOME.md, line twelve)")
    off=1
  else
    if printf '%s\n' "${got[@]}" | grep -q '^S6: home '; then
      bad+=("a home line appeared with only one virtio disk - the machine must be ring 6a's, line for line")
    fi
  fi

  l="${got[$((11 + off))]:-}"; [ "$l" = "S6: nic $MAC" ] || bad+=("line $((12 + off)): got '$l', want 'S6: nic $MAC'")

  l="${got[$((12 + off))]:-}"
  if [[ "$l" =~ ^S6:\ component\ region\ 0x([0-9a-f]{16})\ 1048576\ bytes$ ]]; then
    local addr="${BASH_REMATCH[1]}"
    [ "$addr" != "0000000000000000" ] || bad+=("the component region address is zero")
    [ "${addr:0:8}" = "00000000" ] || bad+=("the component region 0x$addr is above 4 GB")
    [ "${addr:13:3}" = "080" ] || bad+=("the component region 0x$addr is not 128 mod 4096")
  else
    bad+=("line $((13 + off)): got '$l', want 'S6: component region 0x<16 hex digits> 1048576 bytes'")
  fi

  l="${got[$((13 + off))]:-}"
  if [[ "$l" =~ ^S6:\ obs\ page\ 0x([0-9a-f]{16})$ ]]; then
    local obs="${BASH_REMATCH[1]}"
    [ "$obs" != "0000000000000000" ] || bad+=("the obs page address is zero")
    [ "${obs:0:8}" = "00000000" ] || bad+=("the obs page 0x$obs is above 4 GB")
    [ "${obs:13:3}" = "000" ] || bad+=("the obs page 0x$obs is not page-aligned")
  else
    bad+=("line $((14 + off)): got '$l', want 'S6: obs page 0x<16 hex digits>'")
  fi

  l="${got[$((14 + off))]:-}"
  [[ "$l" =~ ^S6:\ glass\ core\ [0-9]+$ ]] || bad+=("line $((15 + off)): got '$l', want 'S6: glass core <id>'")

  l="${got[$((15 + off))]:-}"; [ "$l" = "S6: keyboard ready" ] || bad+=("line $((16 + off)): got '$l', want 'S6: keyboard ready'")

  [ -n "$found" ] && [ "$found" != "$smp" ] && bad+=("cores found is $found, but the machine was given -smp $smp")
  [ -n "$woken" ] && [ "$woken" != "$smp" ] && bad+=("cores woken is $woken, but the machine was given -smp $smp")

  if [ "${#bad[@]}" -eq 0 ]; then
    echo "    $label: $want_lines S6: lines, in order, mode ${w}x${h}, found = woken = $smp, $([ "$disks" = 2 ] && echo "${got[11]#S6: }" || echo "no home line"), nic $MAC"
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

# home_formatted_empty <image> - the image parsed from the host by HOME.md:
# the header of a 16 MB disk, sixteen empty entries, nothing else written.
home_formatted_empty() {
  python3 - "$1" "$DISK_BYTES" <<'EOF'
import struct, sys
data = open(sys.argv[1], "rb").read()
want = int(sys.argv[2])
bad = []
if len(data) != want:
    bad.append("the image is %d bytes, the harness made it %d" % (len(data), want))
if data[0:8] != b"GERMHOME":
    bad.append("sector 0 bytes 0-7 are %r, not GERMHOME" % data[0:8])
else:
    fields = struct.unpack_from("<IIQQQQ", data, 8)
    if fields != (1, 512, 1, 8, 9, want // 512):
        bad.append("header fields are %r, want (1, 512, 1, 8, 9, %d)" % (fields, want // 512))
    if any(data[0x30:0x200]):
        bad.append("header padding is not zero")
    if any(data[0x200:0x200 + 8 * 512]):
        bad.append("the table (sectors 1-8) is not all zero after a format")
    if any(data[0x200 + 8 * 512:]):
        bad.append("something beyond the table was written on a fresh image")
for b in bad:
    print("      - " + b)
sys.exit(1 if bad else 0)
EOF
}

# ------------------------------------------------- test 2: the serial lines --
# Three boots. With two fresh disks at -smp 8: the seventeen lines, "S6:
# home 0 apps" twelfth, and the home image parsed from the host afterwards -
# formatted, empty. The SAME home image at -smp 2: "home 0 apps" again and
# the image byte-identical (a recognised image is not reformatted). With one
# disk at -smp 8: exactly ring 6a's sixteen lines and no home line.

echo "Test 2 - Serial, first boot: seventeen S6: lines with the home image, the image formatted, one disk gives sixteen"
if [ ! -f "$ESP" ]; then
  fail "test 2: no image was built"
else
  t2=0
  fresh_disk "$HOME_IMG"
  serial_check 8 2 "two" "$HOME_IMG" 0 || t2=1
  if home_formatted_empty "$HOME_IMG"; then
    echo "    two: the home image parses as a formatted, empty home (HOME.md)"
  else
    echo "    two: the home image is not a freshly formatted home"
    t2=1
  fi
  cp "$HOME_IMG" "$OUT/home.after-first-boot.img"
  serial_check 2 2 "again" "$HOME_IMG" 0 || t2=1
  if cmp -s "$HOME_IMG" "$OUT/home.after-first-boot.img"; then
    echo "    again: the home image is byte-identical after the second boot - recognised, not reformatted"
  else
    echo "    again: the home image changed on a second boot"
    t2=1
  fi
  serial_check 8 1 "one" || t2=1
  if [ "$t2" -eq 0 ]; then
    pass "test 2: serial log matches the spec with two disks, twice, and with one"
  else
    fail "test 2: serial log does not match the spec"
  fi
fi
echo

# ------------------------------------------------- test 3: the install ------
# The thesis, mocked. The checker starts the MOCK broker (broker/plans.py)
# with a wiped germline, boots with both disks, types "! install echo";
# the mock reads plans/echo.md, serves the canned correct build, REHEARSES
# it in a headless boot of a copy of this image at 1920x1080 with a home
# drive and runs the plan's five tests there through the frozen twin's
# hook; the guest writes the build to its home image, says "installed
# echo", runs it in its panel; the checker types into it, journals a note
# beside it, screendumps, Escapes. It demands the seventeen boot lines,
# the echo byte-exact, the record with the plan's fields and the frame
# with installed 1, the germline entry under the plan's key, the home
# image holding exactly that build with the guest's SHA-256 equal to
# hashlib's, the notebook, and the four screens - 'installing' during the
# wait, the one-cell panel, and the installed app on the choices row at
# the prompt. At -smp 2 and -smp 8. The work is in stage6/checkplans.py.

echo "Test 3 - The install: '! install echo' rehearsed against the plan, kept on the home image, run, at -smp 2 and -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 3: no image was built"
else
  installed=0
  python3 "$REPO/stage6/checkplans.py" --install 2 || installed=1
  python3 "$REPO/stage6/checkplans.py" --install 8 || installed=1
  if [ "$installed" -eq 0 ]; then
    pass "test 3: the install held at both -smp 2 and -smp 8"
  else
    fail "test 3: the install did not hold (see above)"
  fi
fi
echo

# TEST_4

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira, in two terminals at the repo root:"
  echo "  python3 broker/plans.py"
  echo "  truncate -s 16M stage6/out/home.img"
  echo "  qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios $OVMF $DISPLAY -drive format=raw,file=stage6/out/esp.img -drive format=raw,file=stage6/out/notes.img,if=virtio -drive format=raw,file=stage6/out/home.img,if=virtio -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0 -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
