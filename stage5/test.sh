#!/usr/bin/env bash
#
# Stage 5 acceptance tests - the gate for the stage.
#
# Implements acceptance tests 1 to 4 from stage5/spec.md. Test 5 is Wajira's
# eyeball on a windowed run with the REAL broker - he types "! make me a
# clock", the twin rehearses what Claude wrote, and a clock ticks on the
# machine's own screen - and stays manual: his word is the gate for the
# stage.
#
# These tests are written BEFORE stage5.asm and are frozen once written - a
# PreToolUse hook blocks the implementer from editing this file during
# implementation and fixes. If a test here is genuinely wrong, that is a spec
# question for the owner, not an edit.
#
# stage5/mkimage.sh, which builds and packs the artefact, is deliberately NOT
# frozen. This file holds the criteria; that one holds the recipe. Test 1 below
# judges the artefact independently of how it was made.
#
# Everything runs inside QEMU, with OVMF as firmware, exactly two drives per
# guest - a raw FAT boot image and a raw 16 MB notebook image, both under
# stage5/out/, both created here or by the broker's rehearsal under
# stage5/out/rehearsal/ - and the caged network of stage4/UMBILICAL.md:
# slirp with restrict=on and one guestfwd to the broker on 127.0.0.1:9999
# (the rehearsal's twin, to its own listener on 127.0.0.1:9998). The
# automated tests talk only to the MOCK broker (broker/germline.py --mock),
# which calls nothing outside the repository; this gate never spends a token
# and never needs the internet. It refuses to run at all while anything is
# listening on either port, so it can never talk to a real broker by
# accident. The mock's germline is stage5/out/germline/, wiped here, so the
# real germline/ is never read or written by the gate.
#
# Usage:  ./stage5/test.sh          (from anywhere)
# Exit 0 only if every automated test passed.

set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO/stage5/out"
EFI="$OUT/BOOTX64.EFI"
ESP="$OUT/esp.img"
NOTES="$OUT/notes.img"
OVMF="/usr/share/ovmf/OVMF.fd"
DISK_BYTES=$((16 * 1024 * 1024))

# The cage, spelled once. UMBILICAL.md, "The cage": the guest's whole world is
# 10.0.2.4:9999, delivered per connection to the broker on 127.0.0.1:9999 by
# netcat; everything else gets a RST from slirp. The MAC is the harness's
# choice, so the guest's "S5: nic" line can be checked against a value the
# assembler cannot know. The rehearsal's twin uses the same cage with its
# own port (GERMLINE.md, "The rehearsal").
BROKER_PORT=9999
REHEARSAL_PORT=9998
MAC="52:54:00:a1:05:01"
CAGE_NETDEV="user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:${BROKER_PORT}-cmd:nc -N 127.0.0.1 ${BROKER_PORT}"
CAGE_DEVICE="virtio-net-pci,netdev=n0,mac=${MAC}"

fails=0
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; fails=$((fails + 1)); }

mkdir -p "$OUT"

echo "Stage 5 acceptance tests"
echo "repo: $REPO"
echo

# ------------------------------------------------ the ports must be free ----
# The real broker and this gate cannot share 127.0.0.1:9999, and the gate must
# never talk to anything but its own mock; the rehearsal's listener needs
# 9998 to itself. Refuse, loudly, before building.

for port in "$BROKER_PORT" "$REHEARSAL_PORT"; do
  if python3 - "$port" <<'EOF'
import socket, sys
s = socket.socket(); s.settimeout(1.0)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
EOF
  then
    echo "  something is already listening on 127.0.0.1:$port."
    echo "  The gate talks only to its own mock broker and its own rehearsal listener."
    echo "  If the real broker is running, stop it first; then run this again."
    exit 1
  fi
done

# The mock's germline: fresh for every run, so the generation-call counts
# and the entry counts the tests demand are deterministic.
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

echo "Build: ./stage5/mkimage.sh"
if "$REPO/stage5/mkimage.sh" 2>&1 | sed 's/^/  /'; then
  :
else
  echo "  (build failed)"
fi
echo

# --------------------------------------------------- test 1: the artefact ----
# BOOTX64.EFI carries the MZ and PE magics, machine type x86-64, subsystem EFI
# application, relocations stripped; and esp.img contains it, byte for byte, at
# the UEFI removable-media path. Stage 4's criteria, on Stage 5's binary.

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
# headless and requires the thirteen S5: lines from the spec, in order: Stage
# 4's twelve - found = woken = the -smp value, the console geometry agreeing
# with the GOP mode from the same log, the disk's sector count agreeing with
# the image the harness made, the notebook formatted (the disk was blank),
# "S5: nic <mac>" carrying the MAC the harness gave the device - plus
# "S5: component region 0x<16 hex> 1048576 bytes" as line twelve
# (GERMLINE.md, "The component region, and line twelve"): the address where
# a component's first instruction will live, non-zero, below 4 GB, and 64
# mod 4096 because the region is page-aligned and the blob sits at +64; the
# number is the cap - and "S5: keyboard ready" still last, so the serial
# contract after it stays exactly Stage 2's.
#
# Nothing is listening on either port during this run (the gate checked
# that first), and nothing should need to be: the guest sends nothing on
# the network at boot.
#
# OVMF chatters heavily on COM1, so every "S5: ..." run is pulled out of the
# capture in order - a scan, not a line-start match. Requiring EXACTLY
# thirteen catches a triple-fault reboot loop. The guest waits for
# keystrokes forever by design, so timeout killing QEMU (exit 124) is the
# expected outcome.

serial_check() {
  local smp="$1"
  local disk="$OUT/serial.$smp.img"
  local cap="$OUT/serial.$smp.txt"
  local qerr="$OUT/qemu.$smp.err"
  local lines_file="$OUT/s5.$smp.txt"
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

  tr -d '\r' <"$cap" 2>/dev/null | grep -ao 'S5: .*' >"$lines_file" 2>/dev/null

  local -a got=()
  mapfile -t got <"$lines_file"

  local bad=()

  if [ "${#got[@]}" -ne 13 ]; then
    bad+=("expected exactly 13 S5: lines, found ${#got[@]}")
    if [ "${#got[@]}" -gt 13 ]; then
      bad+=("more than thirteen usually means a reboot loop - and with the IDT up it should have been an ERR: exception line instead")
    fi
  fi

  local l w="" h=""
  l="${got[0]:-}"; [ "$l" = "S5: alive" ] || bad+=("line 1: got '$l', want 'S5: alive'")

  l="${got[1]:-}"
  if [[ "$l" =~ ^S5:\ gop\ ([0-9]+)x([0-9]+)\ fb\ 0x([0-9a-f]{16})$ ]]; then
    w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
    local fb="${BASH_REMATCH[3]}"
    [ "$w" -gt 0 ] || bad+=("line 2: width is $w")
    [ "$h" -gt 0 ] || bad+=("line 2: height is $h")
    [ "$fb" != "0000000000000000" ] || bad+=("line 2: framebuffer address is zero")
  else
    bad+=("line 2: got '$l', want 'S5: gop <W>x<H> fb 0x<16 hex digits>'")
  fi

  l="${got[2]:-}"; [ "$l" = "S5: boot services exited" ] || \
    bad+=("line 3: got '$l', want 'S5: boot services exited'")
  l="${got[3]:-}"; [ "$l" = "S5: gdt and paging ours" ] || \
    bad+=("line 4: got '$l', want 'S5: gdt and paging ours'")
  l="${got[4]:-}"; [ "$l" = "S5: idt ready" ] || \
    bad+=("line 5: got '$l', want 'S5: idt ready'")

  local found="" woken=""
  l="${got[5]:-}"
  if [[ "$l" =~ ^S5:\ cores\ found\ ([0-9]+)$ ]]; then
    found="${BASH_REMATCH[1]}"
  else
    bad+=("line 6: got '$l', want 'S5: cores found <N>'")
  fi

  l="${got[6]:-}"
  if [[ "$l" =~ ^S5:\ cores\ woken\ ([0-9]+)$ ]]; then
    woken="${BASH_REMATCH[1]}"
  else
    bad+=("line 7: got '$l', want 'S5: cores woken <N>'")
  fi

  l="${got[7]:-}"
  if [[ "$l" =~ ^S5:\ console\ ([0-9]+)x([0-9]+)$ ]]; then
    local cols="${BASH_REMATCH[1]}" rows="${BASH_REMATCH[2]}"
    if [ -n "$w" ] && [ -n "$h" ]; then
      [ "$cols" -eq $((w / 16)) ] || \
        bad+=("line 8: $cols columns, but $w pixels / 16 = $((w / 16))")
      [ "$rows" -eq $((h / 16)) ] || \
        bad+=("line 8: $rows rows, but $h pixels / 16 = $((h / 16))")
    fi
    [ "$cols" -ge 40 ] || bad+=("line 8: only $cols columns - too narrow for the boot log")
    [ "$rows" -ge 24 ] || bad+=("line 8: only $rows rows - too short for the boot log, a conversation and a component")
  else
    bad+=("line 8: got '$l', want 'S5: console <COLS>x<ROWS>'")
  fi

  l="${got[8]:-}"
  if [[ "$l" =~ ^S5:\ disk\ ([0-9]+)\ sectors$ ]]; then
    local sectors="${BASH_REMATCH[1]}"
    [ "$sectors" -eq $((DISK_BYTES / 512)) ] || \
      bad+=("line 9: the guest counted $sectors sectors, but the image is $DISK_BYTES bytes = $((DISK_BYTES / 512)) sectors")
  else
    bad+=("line 9: got '$l', want 'S5: disk <N> sectors'")
  fi

  l="${got[9]:-}"; [ "$l" = "S5: notebook formatted" ] || \
    bad+=("line 10: got '$l', want 'S5: notebook formatted' - the disk was blank")

  l="${got[10]:-}"; [ "$l" = "S5: nic $MAC" ] || \
    bad+=("line 11: got '$l', want 'S5: nic $MAC' - the MAC the harness gave the device")

  # The component region. The address is where a component's first
  # instruction will live: sixteen hex digits, not zero, below 4 GB (the
  # identity map), and 64 mod 4096 (a page-aligned region, the blob at +64).
  # The number is the cap, a constant by design.
  l="${got[11]:-}"
  if [[ "$l" =~ ^S5:\ component\ region\ 0x([0-9a-f]{16})\ 1048576\ bytes$ ]]; then
    local addr="${BASH_REMATCH[1]}"
    [ "$addr" != "0000000000000000" ] || bad+=("line 12: the component region address is zero")
    [ "${addr:0:8}" = "00000000" ] || bad+=("line 12: the component region 0x$addr is above 4 GB, beyond the identity map")
    [ "${addr:13:3}" = "040" ] || bad+=("line 12: the component region 0x$addr is not 64 mod 4096 - a page-aligned region with the blob at +64 ends in 040")
  else
    bad+=("line 12: got '$l', want 'S5: component region 0x<16 hex digits> 1048576 bytes'")
  fi

  l="${got[12]:-}"; [ "$l" = "S5: keyboard ready" ] || \
    bad+=("line 13: got '$l', want 'S5: keyboard ready'")

  [ -n "$found" ] && [ "$found" != "$smp" ] && \
    bad+=("cores found is $found, but the machine was given -smp $smp")
  [ -n "$woken" ] && [ "$woken" != "$smp" ] && \
    bad+=("cores woken is $woken, but the machine was given -smp $smp")
  [ -n "$found" ] && [ -n "$woken" ] && [ "$found" != "$woken" ] && \
    bad+=("cores found ($found) and cores woken ($woken) disagree - a core did not check in")

  if [ "${#bad[@]}" -eq 0 ]; then
    echo "    -smp $smp: thirteen S5: lines, in order, found = woken = $smp, geometry and sector count agree, notebook formatted, nic $MAC, component region ${got[11]#S5: component region }"
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

echo "Test 2 - Serial, first boot: the thirteen S5: lines on a fresh disk inside the cage, at -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 2: no image was built"
elif serial_check 8; then
  pass "test 2: serial log matches the spec at -smp 8"
else
  fail "test 2: serial log does not match the spec at -smp 8"
fi
echo

# ------------------------------------------------- test 3: the growth -------
# The soul of the stage, mocked. The checker starts the Stage 5 MOCK broker
# with a wiped germline and a record file, boots inside the cage, types a
# note, "? ping" and "! test component" via the monitor; the mock serves the
# canned test component - after REHEARSING it in a real headless boot of
# this same image - and the guest loads and runs it; the checker types a key
# while it runs, screendumps, sends Esc, types a note, screendumps again. It
# demands the thirteen boot lines; the echo exactly the four typed lines; the
# record holding the question and one grow whose raw bytes ARE GERMLINE.md's
# frame, generated once, rehearsed once, answered with the component frame
# the checker rebuilds from stage5/component.bin; the germline holding
# exactly that entry with its provenance; the notebook holding exactly the
# two notes; the component's five strips on a cleared screen with the key it
# was given; and the conversation restored with the prompt below. At -smp 2
# and -smp 8. The work is in stage5/checkgermline.py, which prints its own
# diagnosis.

echo "Test 3 - The growth: '! test component' rehearsed, served, run, a key seen, Esc, at -smp 2 and -smp 8"
if [ ! -f "$ESP" ]; then
  fail "test 3: no image was built"
else
  grown=0
  python3 "$REPO/stage5/checkgermline.py" --grow 2 || grown=1
  python3 "$REPO/stage5/checkgermline.py" --grow 8 || grown=1
  if [ "$grown" -eq 0 ]; then
    pass "test 3: the machine grew a component, ran it, and came back to its prompt, at both -smp 2 and -smp 8"
  else
    fail "test 3: the growth did not round-trip (see above)"
  fi
fi
echo

# --------------------------------------- test 4: the rehearsal and the germline
# Two halves. First this harness inspects its OWN cage string - the one
# every QEMU line above was given - and the checker inspects its own QEMU
# argv and the rehearsal's: slirp user mode, restrict=on, exactly one
# guestfwd, to tcp:10.0.2.4:9999, delivered by nc to 127.0.0.1 on 9999 (the
# gate's guest) and 9998 (the rehearsal's twin), no hostfwd. Then the long
# run at -smp 8: a deliberately faulting blob fails rehearsal twice and the
# guest gets the refusal, nothing runs; the good component passes, is cached
# with its provenance, and a second identical request is served from the
# germline with the generation backend never invoked - the mock counts
# calls; the component padded to exactly the 1 MB cap is rehearsed, streamed
# whole and run; and the marker-parse cases - bare "?", "?x", bare "!",
# "!x" - each route to the line GERMLINE.md fixes. The work is in
# stage5/checkgermline.py --germline.

echo "Test 4 - The rehearsal and the germline: a faulting blob refused, the good one cached and served, the 1 MB cap streamed, the markers parsed"
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
IFS=',' read -ra dev_fields <<<"$CAGE_DEVICE"
dev_ok=0
if [ "${dev_fields[0]:-}" = "virtio-net-pci" ]; then
  has_nd=0; has_mac=0
  for f in "${dev_fields[@]:1}"; do
    [ "$f" = "netdev=n0" ] && has_nd=1
    [ "$f" = "mac=$MAC" ] && has_mac=1
  done
  [ "$has_nd" -eq 1 ] && [ "$has_mac" -eq 1 ] && dev_ok=1
fi
[ "$dev_ok" -eq 1 ] || \
  cage_probs+=("the device is not a virtio-net-pci on netdev n0 with the harness's MAC: $CAGE_DEVICE")

if [ "${#cage_probs[@]}" -ne 0 ]; then
  fail "test 4: this harness's own cage string is not the cage"
  for p in "${cage_probs[@]}"; do echo "    - $p"; done
else
  echo "    the harness's own -netdev carries restrict=on and the single guestfwd to 10.0.2.4:9999 via nc to 127.0.0.1:9999"
  if [ ! -f "$ESP" ]; then
    fail "test 4: no image was built"
  elif python3 "$REPO/stage5/checkgermline.py" --germline; then
    pass "test 4: rehearsed, refused, cached, served from the germline, the cap streamed, the markers parsed - inside the cage"
  else
    fail "test 4: the germline is not proven (see above)"
  fi
fi
echo

# ------------------------------------------------------------- summary -------

if [ "$fails" -eq 0 ]; then
  echo "All automated tests passed."
  echo
  echo "Test 5 is manual - Wajira, in two terminals at the repo root:"
  echo "  python3 broker/germline.py"
  echo "  qemu-system-x86_64 -machine q35 -m 256M -smp 8 -bios $OVMF -drive format=raw,file=stage5/out/esp.img -drive format=raw,file=stage5/out/notes.img,if=virtio -netdev 'user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 9999' -device virtio-net-pci,netdev=n0 -serial stdio"
  exit 0
else
  echo "$fails test(s) failed."
  exit 1
fi
