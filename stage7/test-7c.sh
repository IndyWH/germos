#!/usr/bin/env bash
#
# Stage 7 ring 7c acceptance tests - the gate for the metal.
#
# Implements acceptance tests 1 to 4 from stage7/spec.md (ring 7c), as
# stage7/plan-7c.md and its amendments fix them. Test 5 is Wajira's, on the
# HP itself, by stage7/METAL.md: his word closes the ring and the stage.
#
# These tests are written BEFORE the ring's guest code and are frozen once
# written - a PreToolUse hook blocks the implementer from editing this file
# during implementation and fixes. If a test here is genuinely wrong, that
# is a spec question for the owner, not an edit.
#
# stage7/mkimage.sh and stage7/mkstick.py, which build and pack the artefact
# and the stick, are deliberately NOT frozen; broker/relay.py and
# broker/chart.py are tools, not frozen; stage7/METAL.md is the owner's
# procedure, reviewed, not a criterion. This file and stage7/checkmetal.py
# hold the criteria. Ring 7a's and ring 7b's gates are untouched and still
# frozen: they boot the SAME binary from esp.img on SATA and must stay green.
#
# Everything runs inside QEMU with OVMF as firmware, the patient's CPU model
# (-cpu IvyBridge), the standard VGA device stating 1920x1080 through an
# EDID (one boot of test 2 uses virtio-vga instead, a display that is not
# QEMU's VGA, to see "S7: edid none"), the stick as the firmware will see it
# - a COPY of stage7/out/stick.img on usb-storage behind qemu-xhci, never
# the file itself and never esp.img on SATA - one raw 64 MB disk on ide.1,
# and the NIC the metal has: an e1000e carrying the patient's MAC on slirp
# with restrict=on and one guestfwd to the RELAY on 127.0.0.1:9997, which
# forwards to the broker on 127.0.0.1:9999. Every drive is a raw file under
# stage7/out/metal/. The automated tests talk only to the MOCK broker
# (broker/wire.py --mock), which calls nothing outside the repository; this
# gate never spends a token and never needs the internet. It refuses to run
# at all while anything is listening on 9999, 9998 or 9997 (a connect probe:
# a port in TIME_WAIT is free).
#
# Usage:  ./stage7/test-7c.sh       (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage7/out"
METAL="$OUT/metal"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
STICK="$OUT/stick.img"
OVMF="/usr/share/ovmf/OVMF.fd"
DISK_BYTES=$((64 * 1024 * 1024))

# The cage, spelled once (UMBILICAL.md, "The cage"; WIRE.md, "The twin"):
# the guestfwd lands on the relay, and the NIC is the e1000e with the
# patient's MAC.
BROKER_PORT=9999
REHEARSAL_PORT=9998
RELAY_PORT=9997
MAC="6c:3b:e5:3b:86:45"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${RELAY_PORT}"
CAGE_DEVICE="e1000e,netdev=n0,mac=${MAC}"

# The machine, the two displays, the disk and the stick, spelled once.
MACHINE="-machine q35 -cpu IvyBridge -m 256M -bios $OVMF"
DISPLAY="-vga none -device VGA,edid=on,xres=1920,yres=1080"
NOVGA="-vga none -device virtio-vga,edid=on"
sata_drive() { printf -- '-drive if=none,id=d0,format=raw,file=%s -device ide-hd,drive=d0,bus=ide.1' "$1"; }
stick_drive() { printf -- '-device qemu-xhci -drive if=none,id=stick,format=raw,file=%s -device usb-storage,drive=stick' "$1"; }

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$METAL"

echo "Stage 7 ring 7c acceptance tests"
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
rm -rf "$METAL/germline" "$METAL/rehearsal"

# ------------------------------------------------------------ helpers -------

rd_u2() { od -An -tu2 -j "$2" -N 2 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
rd_u4() { od -An -tu4 -j "$2" -N 4 --endian=little "$1" 2>/dev/null | tr -d ' \n'; }
hexat() { xxd -p -s "$2" -l "$3" "$1" 2>/dev/null | tr -d '\n'; }

# ---------------------------------------------------------------- build ------

echo "Build: ./stage7/mkimage.sh, then python3 stage7/mkstick.py"
if "$REPO/stage7/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
if python3 "$REPO/stage7/mkstick.py" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (the stick was not built)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI carries the MZ and PE magics, machine type x86-64, subsystem EFI
# application, relocations stripped (ring 6a's criteria, on this ring's
# binary); and stick.img, parsed from the host before any boot, is a
# protective MBR, a valid GPT with one EFI System Partition, and holds that
# same file at EFI/BOOT/BOOTX64.EFI byte for byte (checkmetal.py --stick).

echo "Test 1 - Artefact: PE32+ EFI application; the stick a protective MBR, a GPT, one ESP holding EFI/BOOT/BOOTX64.EFI byte-identical"
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

if [ ! -f "$STICK" ]; then
  probs+=("stick.img was not built")
elif [ -f "$EFI" ]; then
  if ! python3 "$REPO/stage7/checkmetal.py" --stick; then
    probs+=("the stick is not what plan-7c.md asks for (see above)")
  fi
fi

if [ "${#probs[@]}" -eq 0 ]; then
  pass "test 1: PE32+ x86-64 EFI application, relocs stripped; the stick a protective MBR, a GPT, one ESP holding it byte for byte"
else
  fail "test 1: the artefact or the stick is not what the spec asks for"
  for p in "${probs[@]}"; do echo "    - $p"; done
fi
echo

# ------------------------------------------------- test 2: the serial lines --
# Three boots from a fresh COPY of the stick over xhci + usb-storage, no
# esp.img on SATA (checkmetal.py --serial): blank at -smp 8 on a fresh 64 MB
# disk - nineteen S7: lines with "S7: disk port 1", the patient's MAC and
# "S7: link up", the disk parsed from the host by the frozen checkdisk.py
# --formatted; again at -smp 4 on the SAME disk - eighteen lines, the disk
# byte-identical; novga at -smp 2 on a fresh disk with virtio-vga in place of
# QEMU's VGA - "S7: edid none" and the highest mode the display lists. On
# every boot the i8042: pair between the glass core's line and the
# keyboard's, and the stick copy's tables unchanged afterwards.

echo "Test 2 - Serial, the metal configuration: the stick over USB with the SATA disk and the e1000e - nineteen lines, eighteen on the same disk, edid none on a display that is not QEMU's; the i8042 self-test and mouse reset lines"
if [ ! -f "$STICK" ] || [ ! -f "$EFI" ]; then
  fail "test 2: no stick was built"
else
  t2=0
  if python3 "$REPO/stage7/checkmetal.py" --serial blank 8; then
    if python3 "$REPO/stage7/checkdisk.py" --formatted "$METAL/disk.img" $((DISK_BYTES / 512)) 2048 34816; then
      echo "    blank: the disk parses from the host as DISK.md's table, byte for byte, with two freshly formatted stores"
    else
      echo "    blank: the disk is not what DISK.md says a first boot writes"
      t2=1
    fi
  else
    t2=1
  fi
  python3 "$REPO/stage7/checkmetal.py" --serial again 4 || t2=1
  python3 "$REPO/stage7/checkmetal.py" --serial novga 2 || t2=1
  if [ "$t2" -eq 0 ]; then
    pass "test 2: the serial log matches plan-7c.md from the stick - a blank disk, a recognised one, a display that is not QEMU's VGA; the i8042 lines on every boot"
  else
    fail "test 2: the serial log does not match plan-7c.md"
  fi
fi
echo

# ------------------------------------ test 3: every stage in one run -------
# One scripted run of two boots at -smp 4 from one stick copy on one disk
# (checkmetal.py --stages). Boot A with the relay and the mock: Stage 2's
# typing and the note, Stage 4's "? ping", ring 6a's "! test app" in its
# panel, ring 6b's "! install echo" rehearsed in wire.py's twin - the
# record, the relay's log, the germline, both partitions, the twin's disk,
# screen A, the obs page. Boot B with 9999 and 9997 closed: the note back
# (Stage 3), the arrow on the first move and a click on "! echo" launching
# it from the home partition (ring 6c's click, ring 6b's launch), a key to
# it, the strip's pointer field, Esc; the disk and the stick copy untouched.

echo "Test 3 - Every stage re-proven in the twin of the HP: one scripted run, two boots at -smp 4 - typing, the note across the reboot, the question, the test app, the install, the click launching echo with nothing on the wire"
if [ ! -f "$STICK" ] || [ ! -f "$EFI" ]; then
  fail "test 3: no stick was built"
elif python3 "$REPO/stage7/checkmetal.py" --stages; then
  pass "test 3: every stage re-proven in the twin of the HP in one run"
else
  fail "test 3: a stage is not re-proven (see above)"
fi
echo

# ----------------------------------------- test 4: the bodyguard, extended --
# Two halves. First this harness inspects its OWN cage, machine, display,
# stick and disk strings - and that no line of its own names esp.img; then
# stage7/checkmetal.py --cage: the checker's argv (the stick over xhci, no
# esp.img) and the twin's as broker/wire.py builds it, the relay's bind
# rule on the host, the payload table 0 wrong, and the spot checks - the
# flash's words and every /dev spelling denied, the harmless sources and
# sinks and this ring's tools allowed.

echo "Test 4 - The bodyguard, extended: the harness's strings, the argv checks, the relay's bind rule, the payload table 0 wrong, the flash's words and every device spelling denied to CC"
cage_probs=()
case "$CAGE_NETDEV" in
  user,*) : ;;
  *) cage_probs+=("the netdev is not slirp user mode: $CAGE_NETDEV") ;;
esac
case ",$CAGE_NETDEV," in
  *,restrict=on,*) : ;;
  *) cage_probs+=("the netdev lacks restrict=on: $CAGE_NETDEV") ;;
esac
n_fwd=$(printf '%s' "$CAGE_NETDEV" | grep -o 'guestfwd=' | wc -l)
[ "$n_fwd" -eq 1 ] || cage_probs+=("expected exactly one guestfwd, found $n_fwd: $CAGE_NETDEV")
printf '%s' "$CAGE_NETDEV" | grep -qE "guestfwd=tcp:10\.0\.2\.4:9999-cmd:nc -N 127\.0\.0\.1 ${RELAY_PORT}(,|\$)" || \
  cage_probs+=("the guestfwd is not tcp:10.0.2.4:9999 via 'nc -N 127.0.0.1 ${RELAY_PORT}': $CAGE_NETDEV")
case "$CAGE_NETDEV" in
  *hostfwd*) cage_probs+=("the netdev opens a hostfwd: $CAGE_NETDEV") ;;
esac
[ "$CAGE_DEVICE" = "e1000e,netdev=n0,mac=$MAC" ] || \
  cage_probs+=("the device is not an e1000e on netdev n0 with the patient's MAC: $CAGE_DEVICE")
[ "$MAC" = "6c:3b:e5:3b:86:45" ] || cage_probs+=("the MAC is not the patient's: $MAC")
[ "$DISPLAY" = "-vga none -device VGA,edid=on,xres=1920,yres=1080" ] || \
  cage_probs+=("the display is not the standard VGA device with the 1920x1080 EDID: $DISPLAY")
[ "$NOVGA" = "-vga none -device virtio-vga,edid=on" ] || \
  cage_probs+=("the other display is not virtio-vga, a device that is not QEMU's VGA: $NOVGA")
[ "$MACHINE" = "-machine q35 -cpu IvyBridge -m 256M -bios $OVMF" ] || \
  cage_probs+=("the machine is not q35 on the patient's CPU with OVMF: $MACHINE")
[ "$(sata_drive "$METAL/disk.img")" = "-drive if=none,id=d0,format=raw,file=$METAL/disk.img -device ide-hd,drive=d0,bus=ide.1" ] || \
  cage_probs+=("the disk is not the raw file under stage7/out/metal/ on an ide-hd at ide.1: $(sata_drive "$METAL/disk.img")")
[ "$(stick_drive "$METAL/stick.x.img")" = "-device qemu-xhci -drive if=none,id=stick,format=raw,file=$METAL/stick.x.img -device usb-storage,drive=stick" ] || \
  cage_probs+=("the stick is not a raw copy under stage7/out/metal/ on usb-storage behind qemu-xhci: $(stick_drive "$METAL/stick.x.img")")
case "$METAL" in
  "$OUT"/*) : ;;
  *) cage_probs+=("the scratch $METAL is not under stage7/out/") ;;
esac
if grep -qE 'qemu-system-x86_64.*esp\.img' "${BASH_SOURCE[0]}"; then
  cage_probs+=("a QEMU line of this harness names esp.img - the stick is the only boot medium on the twin of the HP")
fi

if [ "${#cage_probs[@]}" -ne 0 ]; then
  fail "test 4: this harness's own cage, machine, display, stick or disk string is not the twin of the HP"
  for p in "${cage_probs[@]}"; do echo "    - $p"; done
else
  echo "    the harness's own -netdev string carries restrict=on and the single guestfwd to 10.0.2.4:9999 via nc to the relay on 127.0.0.1:$RELAY_PORT; the NIC is the e1000e with the patient's MAC; the machine is q35 on IvyBridge; the displays are the VGA device with the 1920x1080 EDID and virtio-vga; the stick is a copy on usb-storage behind qemu-xhci and the disk a raw file on ide.1, both under stage7/out/metal/; no QEMU line names esp.img"
  if python3 "$REPO/stage7/checkmetal.py" --cage; then
    pass "test 4: the bodyguard holds - the argv checks, the relay's rule, the payload table 0 wrong, the flash denied to CC"
  else
    fail "test 4: the bodyguard is not proven (see above)"
  fi
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira, on the HP, by stage7/METAL.md. The twin of the HP, windowed, in three terminals at the repo root:"
  echo "  python3 broker/wire.py"
  echo "  python3 broker/relay.py --bind 127.0.0.1 --port $RELAY_PORT"
  echo "  rm -f stage7/out/disk.img; truncate -s 64M stage7/out/disk.img      # only for a blank disk"
  echo "  cp stage7/out/stick.img stage7/out/stick.twin.img                   # QEMU boots a copy; the owner flashes the file"
  echo "  qemu-system-x86_64 $MACHINE -smp 4 $DISPLAY $(stick_drive stage7/out/stick.twin.img) $(sata_drive stage7/out/disk.img) -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 $RELAY_PORT' -device e1000e,netdev=n0,mac=$MAC -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
