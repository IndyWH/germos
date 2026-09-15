#!/usr/bin/env bash
#
# Stage 7 ring 7b acceptance tests - the gate for the wire.
#
# Implements acceptance tests 1 to 4 from stage7/spec.md (ring 7b), as
# stage7/plan-7b.md and its amendments fix them. Test 5 is Wajira's eyeball
# on a windowed run with the REAL broker behind the relay - "? ping" and
# "! make me a clock" - and stays manual: his word closes the ring.
#
# These tests are written BEFORE the ring's driver code and are frozen once
# written - a PreToolUse hook blocks the implementer from editing this file
# during implementation and fixes. If a test here is genuinely wrong, that
# is a spec question for the owner, not an edit.
#
# stage7/mkimage.sh, which builds and packs the artefact, is deliberately
# NOT frozen; broker/relay.py is not frozen either (the spec's word: a tool,
# held to stage7/WIRE.md by stage7/checkwire.py). This file holds the
# criteria. Ring 7a's gate (stage7/test.sh, stage7/checkdisk.py) is
# untouched and still frozen: it boots the SAME binary with virtio-net only
# and must stay green - the e1000e driver lives beside the virtio-net
# driver, and "S7: link up" is printed on the e1000e path only.
#
# Everything runs inside QEMU, with OVMF as firmware, the patient's CPU
# model (-cpu IvyBridge), the standard VGA device stating 1920x1080 through
# an EDID, exactly TWO drives per guest of this gate's own - the raw FAT
# boot image on q35's SATA (ide.0) and a raw 64 MB disk on ide.1, both
# under stage7/out/ - and the NIC the metal has: an e1000e carrying the
# patient's MAC, on slirp with restrict=on and one guestfwd to the RELAY on
# 127.0.0.1:9997, which forwards to the broker on 127.0.0.1:9999. One boot of
# test 2 adds a virtio-net on a second cage to prove the e1000e is preferred.
# No "if=virtio" in any command of this gate's own (the twin's frozen notes
# disk is the frozen twin's). The automated tests talk only to the MOCK
# broker (broker/wire.py --mock), which calls nothing outside the repository;
# this gate never spends a token and never needs the internet. It refuses
# to run at all while anything is listening on 9999, 9998 or 9997 (a
# connect probe: a port in TIME_WAIT is free). The scratch is stage7/out/wire/.
#
# Usage:  ./stage7/test-7b.sh       (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage7/out"
WIRE="$OUT/wire"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
OVMF="/usr/share/ovmf/OVMF.fd"
DISK_BYTES=$((64 * 1024 * 1024))

# The cage, spelled once (UMBILICAL.md, "The cage"; WIRE.md, "The twin"):
# the guestfwd lands on the relay, and the NIC is the e1000e with the
# patient's MAC so the guest's "S7: nic" line is checked against the value
# the metal must print. The twin uses two cages of the same shape with its
# own listener's port.
BROKER_PORT=9999
REHEARSAL_PORT=9998
RELAY_PORT=9997
MAC="6c:3b:e5:3b:86:45"
VIRTIO_MAC="52:54:00:a1:07:02"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${RELAY_PORT}"
CAGE_DEVICE="e1000e,netdev=n0,mac=${MAC}"
# The second cage of the "both" boot: a virtio-net the guest must NOT choose.
CAGE2_NETDEV="user,id=n1,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${RELAY_PORT}"
CAGE2_DEVICE="virtio-net-pci,netdev=n1,mac=${VIRTIO_MAC}"

# The machine, the display and the disk, spelled once - ring 7a's.
MACHINE="-machine q35 -cpu IvyBridge -m 256M -bios $OVMF"
DISPLAY="-vga none -device VGA,edid=on,xres=1920,yres=1080"
sata_drive() { printf -- '-drive if=none,id=d0,format=raw,file=%s -device ide-hd,drive=d0,bus=ide.1' "$1"; }

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$WIRE"

echo "Stage 7 ring 7b acceptance tests"
echo "repo: $REPO"
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

# The mock's germline, the twin's scratch and the gate's own: fresh for every run.
rm -rf "$WIRE/germline" "$WIRE/rehearsal"

# ------------------------------------------------------------ helpers -------

rd_u2() { od -An -tu2 -j "$2" -N 2 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
rd_u4() { od -An -tu4 -j "$2" -N 4 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
hexat() { xxd -p -s "$2" -l "$3" "$1" 2>/dev/null | tr -d '\n'; }

# fresh_disk <path> - a brand-new, all-zero 64 MB raw image.
fresh_disk() {
  rm -f "$1"
  truncate -s "$DISK_BYTES" "$1"
}

# ---------------------------------------------------------------- build ------

echo "Build: ./stage7/mkimage.sh"
if "$REPO/stage7/mkimage.sh" 2>&1 | sed 's/^/  /'; then
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
    rm -f "$WIRE/extracted.efi"
    mtype -i "$ESP" ::/EFI/BOOT/BOOTX64.EFI >"$WIRE/extracted.efi" 2>/dev/null
    cmp -s "$WIRE/extracted.efi" "$EFI" || \
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
# serial_check <smp> <label> <disk> <mode>. Boots the image headless inside
# the cage with the e1000e, the display, the patient's CPU and the given
# SATA disk on ide.1 (mode "both": a virtio-net on a second cage beside it,
# carrying VIRTIO_MAC), and requires WIRE.md's S7: lines in order:
#   blank    - NINETEEN lines: "S7: gpt written" tenth, the disk line,
#              "S7: notebook formatted", "S7: home 0 apps", "S7: nic" with
#              the patient's MAC, "S7: link up";
#   again    - EIGHTEEN lines: no "gpt written", "S7: notebook 0 notes";
#   both     - as blank, with the virtio-net beside the e1000e: the nic line
#              must carry the e1000e's MAC, never VIRTIO_MAC.
# In every mode: "S7: edid <W>x<H>" second and the gop line equal to it,
# found = woken = the -smp value, the console geometry from the mode, the
# component region 128 mod 4096, the obs page page-aligned, no ERR: line.
# Around every boot the boot image is copied before and compared after by
# the frozen checkdisk.py --esp. The disk line's numbers go into
# DISK_SECTORS, DISK_NOTES, DISK_HOME for the caller. The guest waits for
# keystrokes forever, so exit 124 is the expected outcome.

DISK_SECTORS=""; DISK_NOTES=""; DISK_HOME=""

serial_check() {
  local smp="$1"
  local label="$2"
  local disk="$3"
  local mode="$4"
  local cap="$WIRE/serial.$label.txt"
  local qerr="$WIRE/qemu.$label.err"
  local lines_file="$WIRE/s7.$label.txt"
  local rc want_lines=19
  local -a second=()

  rm -f "$cap" "$qerr" "$lines_file"
  if [ "$mode" = "both" ]; then
    second=(-netdev "$CAGE2_NETDEV" -device "$CAGE2_DEVICE")
  fi
  cp "$ESP" "$WIRE/esp.before.img"

  # shellcheck disable=SC2086
  timeout -k 5 60 qemu-system-x86_64 \
    $MACHINE -smp "$smp" \
    $DISPLAY \
    -drive format=raw,file="$ESP" \
    $(sata_drive "$disk") \
    -netdev "$CAGE_NETDEV" \
    -device "$CAGE_DEVICE" \
    "${second[@]}" \
    -display none -serial stdio \
    </dev/null >"$cap" 2>"$qerr"
  rc=$?

  if [ "$rc" -ne 124 ] && [ "$rc" -ne 0 ]; then
    echo "    $label: qemu exited $rc, expected 124 (killed by the 60s timeout)"
    sed 's/^/      /' "$qerr"
    return 1
  fi

  tr -d '\r' <"$cap" 2>/dev/null | grep -ao 'S7: .*' >"$lines_file" 2>/dev/null

  local -a got=()
  mapfile -t got <"$lines_file"

  local bad=()

  case "$mode" in
    blank|both) want_lines=19 ;;
    again) want_lines=18 ;;
  esac
  if [ "${#got[@]}" -ne "$want_lines" ]; then
    bad+=("expected exactly $want_lines S7: lines in mode $mode, found ${#got[@]}")
  fi
  if grep -aq 'ERR: ' "$cap"; then
    bad+=("the guest reported: $(tr -d '\r' <"$cap" | grep -ao 'ERR: .*' | head -1)")
  fi

  local l w="" h="" ew="" eh=""
  l="${got[0]:-}"; [ "$l" = "S7: alive" ] || bad+=("line 1: got '$l', want 'S7: alive'")

  l="${got[1]:-}"
  if [[ "$l" =~ ^S7:\ edid\ ([0-9]+)x([0-9]+)$ ]]; then
    ew="${BASH_REMATCH[1]}"; eh="${BASH_REMATCH[2]}"
  else
    bad+=("line 2: got '$l', want 'S7: edid <W>x<H>' - the harness gave the device an EDID")
  fi

  l="${got[2]:-}"
  if [[ "$l" =~ ^S7:\ gop\ ([0-9]+)x([0-9]+)\ fb\ 0x([0-9a-f]{16})$ ]]; then
    w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
    [ "${BASH_REMATCH[3]}" != "0000000000000000" ] || bad+=("line 3: framebuffer address is zero")
    if [ -n "$ew" ]; then
      [ "$w" = "$ew" ] && [ "$h" = "$eh" ] || \
        bad+=("line 3: the mode is ${w}x${h}, but the display's EDID prefers ${ew}x${eh}")
    fi
  else
    bad+=("line 3: got '$l', want 'S7: gop <W>x<H> fb 0x<16 hex digits>'")
  fi

  l="${got[3]:-}"; [ "$l" = "S7: boot services exited" ] || bad+=("line 4: got '$l', want 'S7: boot services exited'")
  l="${got[4]:-}"; [ "$l" = "S7: gdt and paging ours" ] || bad+=("line 5: got '$l', want 'S7: gdt and paging ours'")
  l="${got[5]:-}"; [ "$l" = "S7: idt ready" ] || bad+=("line 6: got '$l', want 'S7: idt ready'")

  local found="" woken=""
  l="${got[6]:-}"
  if [[ "$l" =~ ^S7:\ cores\ found\ ([0-9]+)$ ]]; then found="${BASH_REMATCH[1]}"; else bad+=("line 7: got '$l', want 'S7: cores found <N>'"); fi
  l="${got[7]:-}"
  if [[ "$l" =~ ^S7:\ cores\ woken\ ([0-9]+)$ ]]; then woken="${BASH_REMATCH[1]}"; else bad+=("line 8: got '$l', want 'S7: cores woken <N>'"); fi

  l="${got[8]:-}"
  if [[ "$l" =~ ^S7:\ console\ ([0-9]+)x([0-9]+)$ ]]; then
    local cols="${BASH_REMATCH[1]}" rows="${BASH_REMATCH[2]}"
    if [ -n "$w" ] && [ -n "$h" ]; then
      [ "$cols" -eq $((w / 16)) ] || bad+=("line 9: $cols columns, but $w pixels / 16 = $((w / 16))")
      [ "$rows" -eq $((h / 16)) ] || bad+=("line 9: $rows rows, but $h pixels / 16 = $((h / 16))")
    fi
  else
    bad+=("line 9: got '$l', want 'S7: console <COLS>x<ROWS>'")
  fi

  [ -n "$found" ] && [ "$found" != "$smp" ] && bad+=("cores found is $found, but the machine was given -smp $smp")
  [ -n "$woken" ] && [ "$woken" != "$smp" ] && bad+=("cores woken is $woken, but the machine was given -smp $smp")

  local off=0
  if [ "$mode" != "again" ]; then
    l="${got[9]:-}"; [ "$l" = "S7: gpt written" ] || bad+=("line 10: got '$l', want 'S7: gpt written' - the disk was blank")
    off=1
  else
    if printf '%s\n' "${got[@]}" | grep -q '^S7: gpt written'; then
      bad+=("'S7: gpt written' on a recognised disk - the table was rewritten")
    fi
  fi

  l="${got[$((9 + off))]:-}"
  if [[ "$l" =~ ^S7:\ disk\ port\ ([0-9]+)\ ([0-9]+)\ notes\ ([0-9]+)\ home\ ([0-9]+)$ ]]; then
    DISK_SECTORS="${BASH_REMATCH[2]}"; DISK_NOTES="${BASH_REMATCH[3]}"; DISK_HOME="${BASH_REMATCH[4]}"
    [ "$DISK_SECTORS" -eq $((DISK_BYTES / 512)) ] || \
      bad+=("line $((10 + off)): the guest counted $DISK_SECTORS sectors, but the image is $((DISK_BYTES / 512)) sectors")
  else
    bad+=("line $((10 + off)): got '$l', want 'S7: disk port <p> <N> notes <lba> home <lba>'")
  fi

  l="${got[$((10 + off))]:-}"
  if [ "$mode" != "again" ]; then
    [ "$l" = "S7: notebook formatted" ] || bad+=("line $((11 + off)): got '$l', want 'S7: notebook formatted' - the partition was blank")
  else
    [ "$l" = "S7: notebook 0 notes" ] || bad+=("line $((11 + off)): got '$l', want 'S7: notebook 0 notes' - a recognised, empty notebook")
  fi
  l="${got[$((11 + off))]:-}"; [ "$l" = "S7: home 0 apps" ] || bad+=("line $((12 + off)): got '$l', want 'S7: home 0 apps'")

  l="${got[$((12 + off))]:-}"
  [ "$l" = "S7: nic $MAC" ] || bad+=("line $((13 + off)): got '$l', want 'S7: nic $MAC' - the e1000e's own address")
  if [ "$mode" = "both" ] && [ "$l" = "S7: nic $VIRTIO_MAC" ]; then
    bad+=("line $((13 + off)): the guest chose the virtio-net beside the e1000e")
  fi
  l="${got[$((13 + off))]:-}"; [ "$l" = "S7: link up" ] || bad+=("line $((14 + off)): got '$l', want 'S7: link up'")

  l="${got[$((14 + off))]:-}"
  if [[ "$l" =~ ^S7:\ component\ region\ 0x([0-9a-f]{16})\ 1048576\ bytes$ ]]; then
    local addr="${BASH_REMATCH[1]}"
    [ "$addr" != "0000000000000000" ] || bad+=("the component region address is zero")
    [ "${addr:0:8}" = "00000000" ] || bad+=("the component region 0x$addr is above 4 GB")
    [ "${addr:13:3}" = "080" ] || bad+=("the component region 0x$addr is not 128 mod 4096")
  else
    bad+=("line $((15 + off)): got '$l', want 'S7: component region 0x<16 hex digits> 1048576 bytes'")
  fi

  l="${got[$((15 + off))]:-}"
  if [[ "$l" =~ ^S7:\ obs\ page\ 0x([0-9a-f]{16})$ ]]; then
    local obs="${BASH_REMATCH[1]}"
    [ "$obs" != "0000000000000000" ] || bad+=("the obs page address is zero")
    [ "${obs:0:8}" = "00000000" ] || bad+=("the obs page 0x$obs is above 4 GB")
    [ "${obs:13:3}" = "000" ] || bad+=("the obs page 0x$obs is not page-aligned")
  else
    bad+=("line $((16 + off)): got '$l', want 'S7: obs page 0x<16 hex digits>'")
  fi

  l="${got[$((16 + off))]:-}"
  [[ "$l" =~ ^S7:\ glass\ core\ [0-9]+$ ]] || bad+=("line $((17 + off)): got '$l', want 'S7: glass core <id>'")

  l="${got[$((17 + off))]:-}"; [ "$l" = "S7: keyboard ready" ] || bad+=("line $((18 + off)): got '$l', want 'S7: keyboard ready'")

  if ! python3 "$REPO/stage7/checkdisk.py" --esp "$WIRE/esp.before.img" "$ESP" "$EFI"; then
    bad+=("the boot image was written during the boot (see above)")
  fi

  if [ "${#bad[@]}" -eq 0 ]; then
    echo "    $label: $want_lines S7: lines, in order, mode ${w}x${h}, found = woken = $smp, disk $DISK_SECTORS sectors, notes $DISK_NOTES home $DISK_HOME, nic $MAC, link up; the boot image untouched"
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
# Four boots. blank at -smp 8 on a fresh 64 MB disk: nineteen lines with the
# patient's MAC and "S7: link up"; the disk parsed from the host by the
# frozen checkdisk.py --formatted (DISK.md's table byte-exact, both stores
# freshly formatted). again at -smp 4 on the SAME disk: eighteen lines, the
# disk byte-identical afterwards. both at -smp 2 on a fresh disk with a
# virtio-net on a second cage beside the e1000e: nineteen lines, the nic
# line the e1000e's. down at -smp 2 (checkwire.py --down): the e1000e's
# link taken down through the monitor before the guest runs - the lines to
# "S7: nic", then the named error and no keyboard: the wait is bounded.

echo "Test 2 - Serial: nineteen S7: lines on the e1000e with the patient's MAC and link up, eighteen on the same disk, the e1000e preferred beside a virtio-net, the link taken down ending in a named error"
if [ ! -f "$ESP" ]; then
  fail "test 2: no image was built"
else
  t2=0
  DISK="$WIRE/disk.img"
  fresh_disk "$DISK"
  if serial_check 8 "blank" "$DISK" blank; then
    if python3 "$REPO/stage7/checkdisk.py" --formatted "$DISK" "$DISK_SECTORS" "$DISK_NOTES" "$DISK_HOME"; then
      echo "    blank: the disk parses from the host as DISK.md's table, byte for byte, with two freshly formatted stores"
    else
      echo "    blank: the disk is not what DISK.md says a first boot writes"
      t2=1
    fi
  else
    t2=1
  fi
  cp "$DISK" "$WIRE/disk.after-first-boot.img"
  if serial_check 4 "again" "$DISK" again; then
    if cmp -s "$DISK" "$WIRE/disk.after-first-boot.img"; then
      echo "    again: the disk is byte-identical after the second boot - recognised, not reformatted"
    else
      echo "    again: the disk changed on a second boot"
      t2=1
    fi
  else
    t2=1
  fi
  fresh_disk "$WIRE/disk.both.img"
  if serial_check 2 "both" "$WIRE/disk.both.img" both; then
    if python3 "$REPO/stage7/checkdisk.py" --formatted "$WIRE/disk.both.img" "$DISK_SECTORS" "$DISK_NOTES" "$DISK_HOME"; then
      echo "    both: the e1000e chosen beside the virtio-net; the disk formatted as before"
    else
      echo "    both: the disk is not what a first boot writes"
      t2=1
    fi
  else
    t2=1
  fi
  if python3 "$REPO/stage7/checkwire.py" --down 2; then
    echo "    down: the link taken down before the guest ran; the named error inside the bound, no keyboard, no reboot"
  else
    echo "    down: the bounded link wait is not proven (see above)"
    t2=1
  fi
  if [ "$t2" -eq 0 ]; then
    pass "test 2: the serial log matches WIRE.md on the e1000e - a blank disk, a recognised one, both NICs, the link down"
  else
    fail "test 2: the serial log does not match WIRE.md"
  fi
fi
echo

# ------------------------------------------ test 3: the question round trip --
# Stage 4's test 3 on the e1000e through the relay: "? ping" and "? hello"
# round-trip through the relay on 9997 and the mock on 9999, a note between
# them, at -smp 2, 4 and 8; the record, the relay's log agreeing with it, the
# notebook on the notes partition, the screen, and the strip's wire
# counters against the obs page and the log. The work is in
# stage7/checkwire.py --question.

echo "Test 3 - The question on e1000e: '? ping' and '? hello' through the relay and the mock, a note between them, at -smp 2, 4 and 8; the wire counters agree with the relay's log"
if [ ! -f "$ESP" ]; then
  fail "test 3: no image was built"
else
  asked=0
  python3 "$REPO/stage7/checkwire.py" --question 2 || asked=1
  python3 "$REPO/stage7/checkwire.py" --question 4 || asked=1
  python3 "$REPO/stage7/checkwire.py" --question 8 || asked=1
  if [ "$asked" -eq 0 ]; then
    pass "test 3: the machine asked and was answered on the e1000e through the relay, on screen, in the record and in the relay's log, at -smp 2, 4 and 8"
  else
    fail "test 3: the question did not round-trip through the relay (see above)"
  fi
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira, in three terminals at the repo root:"
  echo "  python3 broker/wire.py"
  echo "  python3 broker/relay.py --bind 127.0.0.1 --port $RELAY_PORT"
  echo "  rm -f stage7/out/disk.img; truncate -s 64M stage7/out/disk.img      # only for a blank disk"
  echo "  qemu-system-x86_64 $MACHINE -smp 4 $DISPLAY -drive format=raw,file=stage7/out/esp.img $(sata_drive stage7/out/disk.img) -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 $RELAY_PORT' -device e1000e,netdev=n0,mac=$MAC -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
