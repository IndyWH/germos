#!/usr/bin/env python3
"""The Stage 6 twin - stage6/GLASS.md, "The rehearsal", in code.

Every candidate app boots in the twin before it reaches the guest: a
headless, scripted boot of a private byte-identical copy of the guest
image, with the standard VGA device and its EDID, fed through the same
wire. rehearse() starts a one-shot listener on a private port, boots the
copy at -smp 2 inside UMBILICAL.md's cage with the guestfwd delivering to
that port, waits for the guest's own ready line, types "! rehearsal"
through the monitor, answers the request with the candidate's app frame,
reads the obs page and the surfaces through the monitor's xp, watches the
screen and the serial line, sends Esc, types a note, and judges the nine
criteria in the document's order. It proves SAFE - boots, loads, runs,
keeps its budget, stays in its panel, faults nothing, exits, the prompt
lives - not correct.

Composable, for the rings after this one (plan amendment A2): extra QEMU
arguments, the number of S6: lines expected, and a post-delivery hook -
a callable given the driver and its xp reader while the app is still
running, whose phrases are judged after the nine. The defaults are ring
6a exactly.

Everything runs inside QEMU, under a scratch directory the caller names
(the broker uses stage6/out/rehearsal/), with exactly two drives, both raw
files created here. No real disk is touched. Nothing here calls Claude.

This file is frozen acceptance machinery from ring 6a plan item 8: the
twin's verdicts are what acceptance test 4 judges by, so a bent twin would
be a bent criterion. Standard library only.
"""

import hashlib
import os
import re
import select
import shutil
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from glass import (app_frame, parse_obs, regions, is_grow, LINES, CELL_BLOCK,  # noqa: E402
                   STEP_BUDGET_MS, BLOB_MAX)
from rehearse import (Listener, cage_netdev, read_ppm, load_font, render_cell,  # noqa: E402
                      cell_matches, row_on_screen, parse_notebook, BG, FG, TOL, CELL,
                      OVMF, DISK_BYTES, KEY_GAP)

DEFAULT_PORT = 9998
SMP = 2
BUDGET = 90.0           # the whole run, seconds
READY = b"S6: keyboard ready"
REQUEST = "! rehearsal"
NOTE = "after"
ECHO_WANT = (REQUEST + "\r\n" + NOTE + "\r\n").encode()
ROW = "> " + REQUEST    # the console row that must be back on screen after Esc
OBS_PAGE_BYTES = 0x240  # what parse_obs needs

# The display, spelled once: the standard VGA device stating 1440x1440 as
# its preferred mode through an EDID (GLASS.md, "The screen").
VGA_ARGS = ["-vga", "none", "-device", "VGA,edid=on,xres=1440,yres=1440"]

PHRASES = (
    "the twin did not boot",
    "the app was not delivered",
    "the twin reported an error",
    "the app did not run",
    "the app drew nothing",
    "the app missed its budget",
    "the app drew outside its panel",
    "no live prompt after esc",
    "the twin timed out",
)

KEYNAMES = {" ": "spc", "!": "shift-1", "?": "shift-slash", "\n": "ret", "\x1b": "esc", "\t": "tab"}


def keyname(ch):
    if ch in KEYNAMES:
        return KEYNAMES[ch]
    if (ch.islower() and ch.isalpha()) or ch.isdigit():
        return ch
    raise ValueError("no monitor key name for %r" % ch)


def qemu_argv(image, disk, serial_path, port, extra_args=()):
    """The one place the twin's QEMU command is spelled. Test 4 inspects it."""
    return [
        "qemu-system-x86_64",
        "-machine", "q35",
        "-m", "256M",
        "-smp", str(SMP),
        "-bios", OVMF,
    ] + VGA_ARGS + [
        "-drive", "format=raw,file=" + image,
        "-drive", "format=raw,file=" + disk + ",if=virtio",
        "-netdev", cage_netdev(port),
        "-device", "virtio-net-pci,netdev=n0",
    ] + list(extra_args) + [
        "-display", "none",
        "-serial", "file:" + serial_path,
        "-monitor", "stdio",
    ]


class AppListener(Listener):
    """Stage 5's one-shot listener, replying with an app frame."""

    def __init__(self, port, reply):
        super().__init__(port, bytes(16))
        self.reply = reply


# ------------------------------------------------------------ the driver ---

XP_LINE = re.compile(rb"([0-9a-f]{16}): ((?:0x[0-9a-f]+ ?)+)")


class Driver:
    """The monitor on the twin's stdin, its output on stdout, the serial
    capture in a file. What a post-delivery hook is given."""

    def __init__(self, proc, serial_path, workdir):
        self.proc = proc
        self.serial_path = serial_path
        self.workdir = workdir

    def tell(self, line):
        try:
            self.proc.stdin.write(line if isinstance(line, bytes) else line.encode())
            self.proc.stdin.flush()
        except (BrokenPipeError, ValueError, OSError):
            pass

    def type_text(self, text):
        for ch in text:
            self.tell(b"sendkey " + keyname(ch).encode() + b"\n")
            time.sleep(KEY_GAP)

    def serial_bytes(self):
        try:
            with open(self.serial_path, "rb") as fh:
                return fh.read()
        except OSError:
            return b""

    def screendump(self, path):
        if os.path.exists(path):
            os.remove(path)
        self.tell(b"screendump " + path.encode() + b"\n")
        deadline = time.time() + 15.0
        last = -1
        while time.time() < deadline:
            time.sleep(0.2)
            if os.path.exists(path):
                size = os.path.getsize(path)
                if size > 0 and size == last:
                    return True
                last = size
        return False

    def _drain(self, wait=0.0):
        out = b""
        end = time.time() + wait
        while True:
            r, _, _ = select.select([self.proc.stdout], [], [], max(0.0, end - time.time()))
            if not r:
                break
            chunk = os.read(self.proc.stdout.fileno(), 65536)
            if not chunk:
                break
            out += chunk
            end = time.time() + 0.05
        return out

    def xp(self, addr, count, unit="b", timeout=20.0):
        """xp /<count>x<unit> <addr> through the monitor; the bytes read, in
        address order. unit is "b" (bytes) or "g" (u64, little-endian)."""
        self._drain()
        self.tell(b"xp /%dx%s 0x%x\n" % (count, unit.encode(), addr))
        buf = b""
        deadline = time.time() + timeout
        want = count if unit == "b" else count * 8
        while time.time() < deadline:
            buf += self._drain(0.3)
            data = self._parse_xp(buf, unit)
            if len(data) >= want and buf.rstrip().endswith(b"(qemu)"):
                return data[:want]
        data = self._parse_xp(buf, unit)
        if len(data) >= want:
            return data[:want]
        raise ValueError("xp read %d of %d bytes from the monitor" % (len(data), want))

    @staticmethod
    def _parse_xp(buf, unit):
        out = b""
        for m in XP_LINE.finditer(buf):
            for tok in m.group(2).split():
                v = int(tok, 16)
                out += bytes([v]) if unit == "b" else struct.pack("<Q", v)
        return out

    def read_obs(self, addr):
        return parse_obs(self.xp(addr, OBS_PAGE_BYTES // 8, "g"))

    def read_surface(self, desc):
        """A surface's cells, from its descriptor in the obs page."""
        n = desc["rows"] * desc["cols"]
        return self.xp(desc["cells"], n, "b")


# ------------------------------------------------------------ the picture -

def cell_pixels(font, byte, cursor=False):
    if cursor or byte == CELL_BLOCK:
        return [bytes(FG) * CELL] * CELL
    if 0x20 <= byte <= 0x7E:
        return render_cell(font, chr(byte))
    return [bytes(BG) * CELL] * CELL


def surface_mismatch(shot, desc, cells, font):
    """The first cell of the region whose pixels are not what the surface
    says, as (row, col), or None. The cursor is overlaid on its cell."""
    width, height, pixels = read_ppm(shot)
    rows, cols = desc["rows"], desc["cols"]
    cur = desc["cursor"]
    cur_on = bool(cur >> 31 & 1)
    cur_row, cur_col = (cur >> 16) & 0x7FFF, cur & 0xFFFF
    for r in range(rows):
        for c in range(cols):
            sr, sc = desc["row0"] + r, desc["col0"] + c
            if (sr + 1) * CELL > height or (sc + 1) * CELL > width:
                return (r, c)
            want = cell_pixels(font, cells[r * cols + c], cur_on and (r, c) == (cur_row, cur_col))
            if not cell_matches(pixels, width, sr, sc, want):
                return (r, c)
    return None


def region_background(shot, region):
    """Is the region (row0, col0, rows, cols) pure background?"""
    width, height, pixels = read_ppm(shot)
    row0, col0, rows, cols = region
    blank = [bytes(BG) * CELL] * CELL
    for r in range(rows):
        for c in range(cols):
            if not cell_matches(pixels, width, row0 + r, col0 + c, blank):
                return False
    return True


# ------------------------------------------------------------ the twin -----

def rehearse(blob, name, choices, image, workdir, port=DEFAULT_PORT,
             extra_args=(), lines=LINES, after=None):
    """Boot the twin, deliver the candidate, judge it. Returns
    (passed, phrase, log_text). phrase is None when it passed."""
    t_start = time.time()
    log = []

    def say(msg):
        log.append(msg)

    say("rehearsal at %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    say("image %s" % image)
    say("blob sha256 %s size %d name %r choices %r" % (hashlib.sha256(blob).hexdigest(), len(blob), name, choices))

    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    disk = os.path.join(workdir, "notes.img")
    twin = os.path.join(workdir, "esp.img")     # a private, byte-identical copy of the
                                                # image: QEMU locks the file a guest boots from
    serial_path = os.path.join(workdir, "serial.txt")
    shot_b = os.path.join(workdir, "b.ppm")
    shot_c = os.path.join(workdir, "c.ppm")
    with open(disk, "wb") as fh:
        fh.truncate(DISK_BYTES)
    if os.path.isfile(image):
        shutil.copyfile(image, twin)

    ev = {"ready": False, "lines": [], "errs": [], "echo": None, "delivered": False,
          "b": False, "c": False, "notes": None, "listener_error": None,
          "obs_b": None, "obs_c": None, "conversation": None, "choices": None,
          "name": name, "after": None, "lines_want": lines}

    try:
        reply = app_frame(blob, name, choices)
    except ValueError as exc:
        say("candidate is not a legal app frame: %s" % exc)
        return judge(ev, time.time() - t_start, log)
    if not os.path.isfile(image):
        say("no image at %s" % image)
        return judge(ev, time.time() - t_start, log)
    if not os.path.isfile(OVMF):
        say("no firmware at %s" % OVMF)
        return judge(ev, time.time() - t_start, log)

    listener = AppListener(port, reply)
    if not listener.bind():
        say("listener: %s" % listener.error)
        ev["listener_error"] = listener.error
        return judge(ev, time.time() - t_start, log)
    listener.start()

    proc = subprocess.Popen(qemu_argv(twin, disk, serial_path, port, extra_args),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    drv = Driver(proc, serial_path, workdir)

    try:
        deadline = time.time() + 60.0
        while time.time() < deadline:
            time.sleep(0.25)
            if proc.poll() is not None:
                say("qemu exited %d: %s" % (proc.returncode,
                                           proc.stderr.read().decode(errors="replace").strip()[:200]))
                break
            if READY in drv.serial_bytes():
                ev["ready"] = True
                break
        if ev["ready"]:
            time.sleep(1.0)
            drv.type_text(REQUEST + "\n")
            if listener.delivered.wait(30.0):
                ev["delivered"] = True
                say("delivered: the twin asked %r and was sent %d bytes" % (listener.request, len(listener.reply)))
                time.sleep(3.0)
                text = drv.serial_bytes().decode("utf-8", "replace").replace("\r", "")
                m = re.search(r"S6: obs page 0x([0-9a-f]{16})", text)
                if m:
                    obs_addr = int(m.group(1), 16)
                    try:
                        ev["obs_b"] = drv.read_obs(obs_addr)
                        ev["conversation"] = drv.read_surface(ev["obs_b"]["conversation"])
                        ev["choices"] = drv.read_surface(ev["obs_b"]["choices"])
                    except ValueError as exc:
                        say("xp: %s" % exc)
                else:
                    say("no obs page line on serial")
                ev["b"] = drv.screendump(shot_b)
                if after is not None:
                    try:
                        ev["after"] = list(after(drv, drv.xp) or [])
                    except Exception as exc:  # a hook that raises is a failed hook
                        ev["after"] = ["the post-delivery hook failed: %s" % exc]
                drv.tell(b"sendkey esc\n")
                time.sleep(2.0)
                drv.type_text(NOTE + "\n")
                time.sleep(2.0)
                if m:
                    try:
                        ev["obs_c"] = drv.read_obs(obs_addr)
                    except ValueError as exc:
                        say("xp after esc: %s" % exc)
                ev["c"] = drv.screendump(shot_c)
            else:
                say("not delivered: %s" % (listener.error or "the twin never connected"))
        drv.tell(b"quit\n")
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        try:
            proc.stdin.close()
        except OSError:
            pass
        listener.stop.set()

    cap = drv.serial_bytes()
    text = cap.decode("utf-8", "replace").replace("\r", "")
    ev["lines"] = re.findall(r"S6: [^\n]*", text)
    ev["errs"] = re.findall(r"ERR: [^\n]*", text)
    marker = READY + b"\r\n"
    idx = cap.find(marker)
    ev["echo"] = cap[idx + len(marker):] if idx >= 0 else None
    ev["listener_error"] = listener.error
    try:
        ev["notes"] = parse_notebook(open(disk, "rb").read())
    except (OSError, ValueError) as exc:
        ev["notes"] = None
        say("notebook: %s" % exc)
    ev["shot_b"] = shot_b
    ev["shot_c"] = shot_c

    for line in ev["lines"]:
        say(line)
    for line in ev["errs"]:
        say(line)
    if ev["obs_b"]:
        o = ev["obs_b"]
        t = max(o["tsc_per_ms"], 1)
        say("obs after delivery: mode %d name %r steps %d step_worst %.1f ms frames %d frame_worst %.1f ms"
            % (o["mode"], o["name"], o["steps"], o["step_worst"] / t, o["frames"], o["frame_worst"] / t))
    if ev["obs_c"]:
        say("obs after esc: mode %d frames %d" % (ev["obs_c"]["mode"], ev["obs_c"]["frames"]))
    return judge(ev, time.time() - t_start, log)


def judge(ev, elapsed, log):
    """GLASS.md's nine criteria, in order, then the post-delivery hook's
    phrases. Returns (passed, phrase, log)."""
    phrase = None
    o = ev["obs_b"]
    if not ev["ready"] or len(ev["lines"]) != ev["lines_want"]:
        phrase = PHRASES[0]
        log.append("fail: %s (ready %s, %d S6: lines, want %d)" % (phrase, ev["ready"], len(ev["lines"]), ev["lines_want"]))
    elif not ev["delivered"]:
        phrase = PHRASES[1]
        log.append("fail: %s (%s)" % (phrase, ev.get("listener_error") or "no connection"))
    elif ev["errs"]:
        phrase = PHRASES[2]
        log.append("fail: %s (%s)" % (phrase, ev["errs"][0]))
    elif o is None or o["mode"] != 3 or o["name"].encode() != ev["name"] or o["steps"] < 1:
        phrase = PHRASES[3]
        log.append("fail: %s (%s)" % (phrase, "no obs page read" if o is None else
                                      "mode %d name %r steps %d" % (o["mode"], o["name"], o["steps"])))
    else:
        regs = regions(o["cols"], o["rows"])
        try:
            font = load_font()
            if not ev["b"] or regs is None or region_background(ev["shot_b"], regs["app"]):
                phrase = PHRASES[4]
                log.append("fail: %s" % phrase)
            elif o["step_worst"] > STEP_BUDGET_MS * max(o["tsc_per_ms"], 1):
                phrase = PHRASES[5]
                log.append("fail: %s (worst step %.1f ms)" % (phrase, o["step_worst"] / max(o["tsc_per_ms"], 1)))
            else:
                bad = None
                for which in ("conversation", "choices"):
                    cells = ev[which]
                    if cells is None:
                        bad = (which, "unread")
                        break
                    at = surface_mismatch(ev["shot_b"], o[which], cells, font)
                    if at is not None:
                        bad = (which, at)
                        break
                if bad:
                    phrase = PHRASES[6]
                    log.append("fail: %s (%s surface, cell %r)" % (phrase, bad[0], bad[1]))
        except (OSError, ValueError) as exc:
            phrase = PHRASES[4]
            log.append("fail: %s (screendump unreadable: %s)" % (phrase, exc))
        if phrase is None:
            c_ok = False
            try:
                c_ok = ev["c"] and row_on_screen(ev["shot_c"], ROW)
            except (OSError, ValueError) as exc:
                log.append("screendump C unreadable: %s" % exc)
            oc = ev["obs_c"]
            if not c_ok:
                phrase = PHRASES[7]
                log.append("fail: %s (the request row is not back on screen)" % phrase)
            elif oc is None or oc["mode"] != 0:
                phrase = PHRASES[7]
                log.append("fail: %s (the obs page says mode %s, not prompt)" % (phrase, oc and oc["mode"]))
            elif ev["notes"] != [NOTE]:
                phrase = PHRASES[7]
                log.append("fail: %s (the notebook holds %r, want [%r])" % (phrase, ev["notes"], NOTE))
            elif ev["echo"] != ECHO_WANT:
                phrase = PHRASES[7]
                log.append("fail: %s (the echo after ready is %r, want %r)" % (phrase, ev["echo"], ECHO_WANT))
            elif elapsed > BUDGET:
                phrase = PHRASES[8]
                log.append("fail: %s (%.1f s)" % (phrase, elapsed))
    if phrase is None:
        for p in PHRASES:
            log.append("ok: not '%s'" % p)
        if ev.get("after"):
            phrase = ev["after"][0]
            for p in ev["after"]:
                log.append("fail: %s (post-delivery hook)" % p)
        elif ev.get("after") is not None:
            log.append("ok: the post-delivery hook found nothing")
    log.append("elapsed %.1f s" % elapsed)
    return phrase is None, phrase, "\n".join(log) + "\n"


if __name__ == "__main__":
    # A hand run: python3 broker/twin.py <blob> [name] [image] [workdir]
    if len(sys.argv) < 2:
        print("usage: twin.py <blob> [name] [image] [workdir]")
        sys.exit(2)
    blob = open(sys.argv[1], "rb").read()
    name = (sys.argv[2] if len(sys.argv) > 2 else os.path.basename(sys.argv[1]).split(".")[0]).encode()
    image = sys.argv[3] if len(sys.argv) > 3 else os.path.join(REPO, "stage6", "out", "esp.img")
    work = sys.argv[4] if len(sys.argv) > 4 else os.path.join(REPO, "stage6", "out", "rehearsal")
    ok, why, text = rehearse(blob, name, [], image, work)
    sys.stdout.write(text)
    print("PASS" if ok else "FAIL: " + why)
    sys.exit(0 if ok else 1)
