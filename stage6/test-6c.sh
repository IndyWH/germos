#!/usr/bin/env bash
#
# Stage 6 ring 6c acceptance tests - the gate for the pointer.
#
# Implements acceptance tests 1 to 4 from stage6/spec.md (ring 6c), as
# stage6/plan-6c.md fixes them. Test 5 is Wajira's eyeball on a windowed run
# with the REAL broker - he clicks his way through the choices row and into
# the calculator - and stays manual: his word closes the ring and the stage.
#
# These tests are written BEFORE the ring's code and are frozen once written
# - a PreToolUse hook blocks the implementer from editing this file during
# implementation and fixes. If a test here is genuinely wrong, that is a spec
# question for the owner, not an edit.
#
# stage6/mkimage.sh, which builds and packs the artefact, is deliberately NOT
# frozen. This file holds the criteria; that one holds the recipe. Ring 6a's
# gate (stage6/test.sh, one disk, 1440x1440) and ring 6b's (stage6/test-6b.sh,
# two disks, 1920x1080) are untouched and still frozen: they boot the SAME
# binary with a mouse that never moves, and they must stay green - GLASS.md's
# ring 6c section promises that such a machine is ring 6a's to the line and
# to the pixel, and those two gates are the proof.
#
# Everything runs inside QEMU, with OVMF as firmware, the standard VGA device
# stating 1920x1080 through an EDID, exactly THREE drives per guest - a raw
# FAT boot image, a raw 16 MB notebook image and a raw 16 MB home image, all
# under stage6/out/, all created here or by the broker's twin under
# stage6/out/rehearsal/ - and the caged network of stage4/UMBILICAL.md: slirp
# with restrict=on and one guestfwd to the broker on 127.0.0.1:9999 (the twin,
# to its own listener on 127.0.0.1:9998). The mouse is QEMU's PS/2 mouse on
# the i8042, driven through the monitor's mouse_move and mouse_button. The
# automated tests talk only to the MOCK broker (broker/pointer.py --mock),
# which calls nothing outside the repository; this gate never spends a token
# and never needs the internet. It refuses to run at all while anything is
# listening on either port. The mock's germline is stage6/out/germline/,
# wiped here.
#
# Usage:  ./stage6/test-6c.sh       (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage6/out"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
OVMF="/usr/share/ovmf/OVMF.fd"

# The cage, spelled once (UMBILICAL.md, "The cage"), with this ring's MAC so
# the guest's "S6: nic" line is checked against a value the assembler cannot
# know. The twin uses the same cage with its own port.
BROKER_PORT=9999
REHEARSAL_PORT=9998
MAC="52:54:00:a1:06:03"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${BROKER_PORT}"
CAGE_DEVICE="virtio-net-pci,netdev=n0,mac=${MAC}"

# The display, spelled once: the standard VGA device stating 1920x1080 as
# its preferred mode through an EDID - the owner's windowed geometry, the
# twin's (broker/plans.py, imported by broker/pointer.py) and this gate's.
DISPLAY="-vga none -device VGA,edid=on,xres=1920,yres=1080"

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 6 ring 6c acceptance tests"
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

# ------------------------------------------------- test 2: the serial lines --
# Two boots, at -smp 8 and -smp 2, under the checker (it needs the monitor to
# move the mouse with): the seventeen lines of ring 6b before any packet, the
# mouse identified at boot in the obs page, the frozen strip and surface
# checks passing on a screendump before the first packet; then one
# mouse_move, and EIGHTEEN lines with "S6: mouse ready" eighteenth, the echo
# after "S6: keyboard ready" exactly that one line, the arrow at the page's
# cell, the strip's third field. The work is in stage6/checkpointer.py.

echo "Test 2 - Serial: seventeen lines and the 6a glass before any packet; one move, then 'S6: mouse ready' eighteenth, the arrow, the field"
if [ ! -f "$ESP" ]; then
  fail "test 2: no image was built"
else
  t2=0
  python3 "$REPO/stage6/checkpointer.py" --serial 8 || t2=1
  python3 "$REPO/stage6/checkpointer.py" --serial 2 || t2=1
  if [ "$t2" -eq 0 ]; then
    pass "test 2: the mouse identified at boot, silent until it speaks, then the eighteenth line, the arrow and the field, at -smp 8 and -smp 2"
  else
    fail "test 2: the serial log, the page or the screen is not what the section asks for"
  fi
fi
echo

# ------------------------------------------------- test 3: the pointer ------
# The soul of the ring, mocked: the cursor appears on the first move; a click
# on "? ask" types the marker; "! point app" rehearsed and run; three buttons
# in its panel reach point and draw their digits; "c clear", "Tab prompt",
# "Tab app", a gap and "Esc exit" clicked; the frozen test app clicked on
# harmlessly. At -smp 2 and -smp 8. The work is in stage6/checkpointer.py.

echo "Test 3 - The pointer: a click on '? ask' types the marker; '! point app' rehearsed and run, three buttons reach point; the row clicked; the test app clicked harmlessly"
if [ ! -f "$ESP" ]; then
  fail "test 3: no image was built"
else
  pointed=0
  python3 "$REPO/stage6/checkpointer.py" --point 2 || pointed=1
  python3 "$REPO/stage6/checkpointer.py" --point 8 || pointed=1
  if [ "$pointed" -eq 0 ]; then
    pass "test 3: a click does what its key does and point draws the cell it was given, at both -smp 2 and -smp 8"
  else
    fail "test 3: the pointer did not hold (see above)"
  fi
fi
echo

# --------------------------------------------- test 4: the truth about the pointer
# The pre-packet screen judged by the frozen 6a checks; a scripted sweep with
# the arrow at the page's cell and the old cell restored at every screendump;
# packets counted equal packets sent; the buttons on an empty spot; the
# install and the launch by click, with text on the line and without; the
# strip's field against the page. The work is in stage6/checkpointer.py.
# First this harness inspects its OWN cage and display strings; the checker
# inspects its own QEMU argv and the twin's as broker/pointer.py inherits it.

echo "Test 4 - The truth about the pointer: 6a's glass before the first packet, the sweep, packets counted equal packets sent, the launch by click"
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
printf '%s' "$CAGE_NETDEV" | grep -qE 'guestfwd=tcp:10\.0\.2\.4:9999-cmd:nc -N 127\.0\.0\.1 9999(,|$)' || \
  cage_probs+=("the guestfwd is not tcp:10.0.2.4:9999 via 'nc -N 127.0.0.1 9999': $CAGE_NETDEV")
case "$CAGE_NETDEV" in
  *hostfwd*) cage_probs+=("the netdev opens a hostfwd: $CAGE_NETDEV") ;;
esac
[ "$CAGE_DEVICE" = "virtio-net-pci,netdev=n0,mac=$MAC" ] || \
  cage_probs+=("the device is not a virtio-net-pci on netdev n0 with the harness's MAC: $CAGE_DEVICE")
[ "$DISPLAY" = "-vga none -device VGA,edid=on,xres=1920,yres=1080" ] || \
  cage_probs+=("the display is not the standard VGA device with the 1920x1080 EDID: $DISPLAY")

if [ "${#cage_probs[@]}" -ne 0 ]; then
  fail "test 4: this harness's own cage or display string is not the cage"
  for p in "${cage_probs[@]}"; do echo "    - $p"; done
else
  echo "    the harness's own -netdev carries restrict=on and the single guestfwd to 10.0.2.4:9999 via nc to 127.0.0.1:9999; the display is the VGA device with the 1920x1080 EDID"
  if [ ! -f "$ESP" ]; then
    fail "test 4: no image was built"
  elif python3 "$REPO/stage6/checkpointer.py" --truth; then
    pass "test 4: the truth about the pointer - packets counted equal packets sent, the cursor where the page says, the launch by click on an empty line only"
  else
    fail "test 4: the truth is not told (see above)"
  fi
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira, in two terminals at the repo root:"
  echo "  python3 broker/pointer.py"
  echo "  qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios $OVMF $DISPLAY -drive format=raw,file=stage6/out/esp.img -drive format=raw,file=stage6/out/notes.img,if=virtio -drive format=raw,file=stage6/out/home.img,if=virtio -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0 -serial stdio"
  echo "  (click in the QEMU window to grab the mouse; Ctrl+Alt+G releases it; truncate -s 16M stage6/out/home.img first for a blank home)"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
