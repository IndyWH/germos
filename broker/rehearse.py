#!/usr/bin/env python3
"""The rehearsal - stage5/GERMLINE.md, "The rehearsal", in code.

Every candidate component boots in the twin before it reaches the guest:
a headless, scripted boot of the SAME guest image, fed through the same
wire. rehearse() starts a one-shot listener on a private port, boots the
image at -smp 2 inside UMBILICAL.md's cage with the guestfwd delivering to
that port, waits for the guest's own ready line, types "! rehearsal"
through the monitor, answers the request with the candidate's component
frame, watches the screen and the serial line, sends Esc, types a note,
and judges the seven criteria in the document's order. It proves SAFE -
boots, loads, runs, faults nothing, returns, the prompt lives - not
correct.

Everything runs inside QEMU, under a scratch directory the caller names
(the broker uses stage5/out/rehearsal/), with exactly two drives, both raw
files created here. No real disk is touched. Nothing here calls Claude.

This file is frozen acceptance machinery from Stage 5 plan item 8: the
rehearsal's verdicts are what acceptance test 4 judges by, so a bent
rehearsal would be a bent criterion. Standard library only.
"""

import hashlib
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from germline import (is_grow, component_frame, BLOB_MAX)  # noqa: E402  (the shared wire)

OVMF = "/usr/share/ovmf/OVMF.fd"
FONT = os.path.join(REPO, "stage2", "font8x8.bin")

DEFAULT_PORT = 9998
SMP = 2
DISK_BYTES = 16 * 1024 * 1024
SECTOR = 512
BUDGET = 90.0           # the whole run, seconds
READY = b"S5: keyboard ready"
LINES = 13
REQUEST = "! rehearsal"
NOTE = "after"
ECHO_WANT = (REQUEST + "\r\n" + NOTE + "\r\n").encode()
ROW = "> " + REQUEST    # the console row the loader must clear, and restore

PHRASES = (
    "the twin did not boot",
    "the component was not delivered",
    "the twin reported an error",
    "the component did not run",
    "the component drew nothing",
    "no live prompt after esc",
    "the twin timed out",
)

KEY_GAP = 0.2
KEYNAMES = {" ": "spc", "!": "shift-1", "\n": "ret"}


def keyname(ch):
    if ch in KEYNAMES:
        return KEYNAMES[ch]
    if ch.islower() and ch.isalpha():
        return ch
    raise ValueError("no monitor key name for %r" % ch)


def cage_netdev(port):
    """UMBILICAL.md's cage, the guestfwd delivered to the rehearsal's port."""
    return "user,id=n0,restrict=on,guestfwd=tcp:10.0.2.4:9999-cmd:nc -N 127.0.0.1 %d" % port


def qemu_argv(image, disk, serial_path, port):
    return [
        "qemu-system-x86_64",
        "-machine", "q35",
        "-m", "256M",
        "-smp", str(SMP),
        "-bios", OVMF,
        "-drive", "format=raw,file=" + image,
        "-drive", "format=raw,file=" + disk + ",if=virtio",
        "-netdev", cage_netdev(port),
        "-device", "virtio-net-pci,netdev=n0",
        "-display", "none",
        "-serial", "file:" + serial_path,
        "-monitor", "stdio",
    ]


# ------------------------------------------------------------ the listener -

class Listener(threading.Thread):
    """One connection: read the request frame, answer with the candidate's
    component frame, close. Reports what happened."""

    def __init__(self, port, blob):
        super().__init__(daemon=True)
        self.port = port
        self.reply = component_frame(blob)
        self.delivered = threading.Event()
        self.request = None
        self.error = None
        self.stop = threading.Event()
        self.sock = None

    def bind(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", self.port))
        except OSError as exc:
            s.close()
            self.error = "cannot bind 127.0.0.1:%d (%s)" % (self.port, exc)
            return False
        s.listen(1)
        s.settimeout(0.5)
        self.sock = s
        return True

    def run(self):
        try:
            while not self.stop.is_set():
                try:
                    conn, _ = self.sock.accept()
                except socket.timeout:
                    continue
                try:
                    conn.settimeout(10.0)
                    n, = struct.unpack("<I", self._exact(conn, 4))
                    if n > 498:
                        raise ValueError("request frame of %d bytes" % n)
                    req = self._exact(conn, n)
                    self.request = req
                    if not is_grow(req):
                        raise ValueError("not a grow request: %r" % req[:32])
                    conn.settimeout(None)
                    conn.sendall(self.reply)
                    self.delivered.set()
                except (ValueError, OSError, struct.error) as exc:
                    self.error = str(exc)
                finally:
                    try:
                        conn.close()
                    except OSError:
                        pass
                return
        finally:
            try:
                self.sock.close()
            except OSError:
                pass

    @staticmethod
    def _exact(conn, n):
        data = b""
        while len(data) < n:
            chunk = conn.recv(n - len(data))
            if not chunk:
                raise ValueError("connection closed after %d of %d bytes" % (len(data), n))
            data += chunk
        return data


# ------------------------------------------------------------ the picture -
# Stage 2's console, as every checker renders it: 16x16 cells from the
# shared font, two colours, +-4 per channel.

BG = (16, 16, 24)
FG = (224, 224, 224)
TOL = 4
CELL = 16


def read_ppm(path):
    data = open(path, "rb").read()
    if not data.startswith(b"P6"):
        raise ValueError("not a binary PPM")
    idx = 2
    fields = []
    while len(fields) < 3:
        while idx < len(data) and data[idx:idx + 1].isspace():
            idx += 1
        if data[idx:idx + 1] == b"#":
            while idx < len(data) and data[idx:idx + 1] != b"\n":
                idx += 1
            continue
        start = idx
        while idx < len(data) and not data[idx:idx + 1].isspace():
            idx += 1
        fields.append(int(data[start:idx]))
    idx += 1
    width, height, maxval = fields
    if maxval != 255:
        raise ValueError("expected an 8-bit PPM")
    pixels = data[idx:]
    if len(pixels) < width * height * 3:
        raise ValueError("truncated PPM")
    return width, height, pixels[:width * height * 3]


def load_font():
    data = open(FONT, "rb").read()
    if len(data) != 1024:
        raise ValueError("font8x8.bin is %d bytes" % len(data))
    return data


def render_cell(font, ch):
    rows = []
    for byte in font[ord(ch) * 8:(ord(ch) + 1) * 8]:
        row = b"".join(bytes(FG if byte >> x & 1 else BG) * 2 for x in range(8))
        rows.append(row)
        rows.append(row)
    return rows


def cell_matches(pixels, width, row, col, want_rows):
    x0 = col * CELL * 3
    for dy in range(CELL):
        base = ((row * CELL + dy) * width) * 3 + x0
        got = pixels[base:base + CELL * 3]
        want = want_rows[dy]
        if got == want:
            continue
        for i in range(CELL * 3):
            if abs(got[i] - want[i]) > TOL:
                return False
    return True


def row_on_screen(shot, text):
    """Is `text`, drawn from column 0, on any console row of the shot?"""
    width, height, pixels = read_ppm(shot)
    font = load_font()
    cells = [render_cell(font, ch) for ch in text]
    rows = height // CELL
    if len(text) > width // CELL:
        return False
    for r in range(rows):
        if all(cell_matches(pixels, width, r, c, w) for c, w in enumerate(cells)):
            return True
    return False


def pure_background(shot):
    width, height, pixels = read_ppm(shot)
    bg_row = bytes(BG) * width
    for y in range(height):
        row = pixels[y * width * 3:(y + 1) * width * 3]
        if row == bg_row:
            continue
        for x in range(width):
            p = row[x * 3:x * 3 + 3]
            if any(abs(p[i] - BG[i]) > TOL for i in range(3)):
                return False
    return True


# ----------------------------------------------------------- the notebook --

def parse_notebook(data):
    if data[0:8] != b"NOTEBOOK":
        raise ValueError("not a notebook")
    version, sector, first, length = struct.unpack_from("<IIQQ", data, 8)
    if version != 1 or sector != SECTOR or first != 1 or length != len(data) // SECTOR - 1:
        raise ValueError("bad notebook header")
    notes = []
    for n in range(1, len(data) // SECTOR):
        rec = data[n * SECTOR:(n + 1) * SECTOR]
        if rec[0:4] != b"NOTE":
            break
        seq, ln, res = struct.unpack_from("<IHH", rec, 4)
        if seq != n or not 1 <= ln <= 500 or res != 0:
            break
        text = rec[12:12 + ln]
        if any(b < 0x20 or b > 0x7E for b in text) or any(rec[12 + ln:]):
            break
        notes.append(text.decode("ascii"))
    return notes


# ------------------------------------------------------------ the driver ---

def rehearse(blob, image, workdir, port=DEFAULT_PORT):
    """Boot the twin, deliver the candidate, judge it. Returns
    (passed, phrase, log_text). phrase is None when it passed."""
    t_start = time.time()
    log = []

    def say(msg):
        log.append(msg)

    say("rehearsal at %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    say("image %s" % image)
    say("blob sha256 %s size %d" % (hashlib.sha256(blob).hexdigest(), len(blob)))

    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    disk = os.path.join(workdir, "notes.img")
    serial_path = os.path.join(workdir, "serial.txt")
    shot_b = os.path.join(workdir, "b.ppm")
    shot_c = os.path.join(workdir, "c.ppm")
    with open(disk, "wb") as fh:
        fh.truncate(DISK_BYTES)

    evidence = {"ready": False, "lines": [], "errs": [], "echo": None,
                "delivered": False, "b": False, "c": False, "notes": None,
                "listener_error": None}

    if not (1 <= len(blob) <= BLOB_MAX):
        say("candidate is %d bytes - outside 1..%d" % (len(blob), BLOB_MAX))
        return judge(evidence, time.time() - t_start, log)
    if not os.path.isfile(image):
        say("no image at %s" % image)
        return judge(evidence, time.time() - t_start, log)
    if not os.path.isfile(OVMF):
        say("no firmware at %s" % OVMF)
        return judge(evidence, time.time() - t_start, log)

    listener = Listener(port, blob)
    if not listener.bind():
        say("listener: %s" % listener.error)
        evidence["listener_error"] = listener.error
        return judge(evidence, time.time() - t_start, log)
    listener.start()

    proc = subprocess.Popen(qemu_argv(image, disk, serial_path, port),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def tell(line):
        try:
            proc.stdin.write(line)
            proc.stdin.flush()
        except (BrokenPipeError, ValueError, OSError):
            pass

    def serial_bytes():
        try:
            with open(serial_path, "rb") as fh:
                return fh.read()
        except OSError:
            return b""

    def type_text(text):
        for ch in text:
            tell(b"sendkey " + keyname(ch).encode() + b"\n")
            time.sleep(KEY_GAP)

    def screendump(path):
        tell(b"screendump " + path.encode() + b"\n")
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

    try:
        deadline = time.time() + 60.0
        while time.time() < deadline:
            time.sleep(0.25)
            if proc.poll() is not None:
                say("qemu exited %d: %s" % (proc.returncode,
                                           proc.stderr.read().decode(errors="replace").strip()[:200]))
                break
            if READY in serial_bytes():
                evidence["ready"] = True
                break
        if evidence["ready"]:
            time.sleep(1.0)
            type_text(REQUEST + "\n")
            if listener.delivered.wait(30.0):
                evidence["delivered"] = True
                say("delivered: the twin asked %r and was sent %d bytes" % (listener.request, len(listener.reply)))
                time.sleep(3.0)
                evidence["b"] = screendump(shot_b)
                tell(b"sendkey esc\n")
                time.sleep(2.0)
                type_text(NOTE + "\n")
                time.sleep(2.0)
                evidence["c"] = screendump(shot_c)
            else:
                say("not delivered: %s" % (listener.error or "the twin never connected"))
        tell(b"quit\n")
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        listener.stop.set()

    cap = serial_bytes()
    text = cap.decode("utf-8", "replace").replace("\r", "")
    evidence["lines"] = re.findall(r"S5: [^\n]*", text)
    evidence["errs"] = re.findall(r"ERR: [^\n]*", text)
    marker = READY + b"\r\n"
    idx = cap.find(marker)
    evidence["echo"] = cap[idx + len(marker):] if idx >= 0 else None
    evidence["listener_error"] = listener.error
    try:
        evidence["notes"] = parse_notebook(open(disk, "rb").read())
    except (OSError, ValueError) as exc:
        evidence["notes"] = None
        say("notebook: %s" % exc)
    evidence["shot_b"] = shot_b
    evidence["shot_c"] = shot_c

    for line in evidence["lines"]:
        say(line)
    for line in evidence["errs"]:
        say(line)
    return judge(evidence, time.time() - t_start, log)


def judge(ev, elapsed, log):
    """GERMLINE.md's seven criteria, in order. Returns (passed, phrase, log)."""
    phrase = None
    if not ev["ready"] or len(ev["lines"]) != LINES:
        phrase = PHRASES[0]
        log.append("fail: %s (ready %s, %d S5: lines)" % (phrase, ev["ready"], len(ev["lines"])))
    elif not ev["delivered"]:
        phrase = PHRASES[1]
        log.append("fail: %s (%s)" % (phrase, ev.get("listener_error") or "no connection"))
    elif ev["errs"]:
        phrase = PHRASES[2]
        log.append("fail: %s (%s)" % (phrase, ev["errs"][0]))
    else:
        b_ok = c_ok = False
        try:
            if ev["b"] and row_on_screen(ev["shot_b"], ROW):
                phrase = PHRASES[3]
            elif not ev["b"] or pure_background(ev["shot_b"]):
                phrase = PHRASES[4]
            else:
                b_ok = True
        except (OSError, ValueError) as exc:
            phrase = PHRASES[4]
            log.append("screendump B unreadable: %s" % exc)
        if b_ok:
            try:
                c_ok = ev["c"] and row_on_screen(ev["shot_c"], ROW)
            except (OSError, ValueError) as exc:
                log.append("screendump C unreadable: %s" % exc)
            if not c_ok:
                phrase = PHRASES[5]
                log.append("fail: %s (the request row is not back on screen)" % phrase)
            elif ev["notes"] != [NOTE]:
                phrase = PHRASES[5]
                log.append("fail: %s (the notebook holds %r, want [%r])" % (phrase, ev["notes"], NOTE))
            elif ev["echo"] != ECHO_WANT:
                phrase = PHRASES[5]
                log.append("fail: %s (the echo after ready is %r, want %r)" % (phrase, ev["echo"], ECHO_WANT))
            elif elapsed > BUDGET:
                phrase = PHRASES[6]
                log.append("fail: %s (%.1f s)" % (phrase, elapsed))
        elif phrase:
            log.append("fail: %s" % phrase)
    if phrase is None:
        for p in PHRASES:
            log.append("ok: not '%s'" % p)
    log.append("elapsed %.1f s" % elapsed)
    return phrase is None, phrase, "\n".join(log) + "\n"


if __name__ == "__main__":
    # A hand run: python3 broker/rehearse.py <blob> [image] [workdir]
    if len(sys.argv) < 2:
        print("usage: rehearse.py <blob> [image] [workdir]")
        sys.exit(2)
    blob = open(sys.argv[1], "rb").read()
    image = sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO, "stage5", "out", "esp.img")
    work = sys.argv[3] if len(sys.argv) > 3 else os.path.join(REPO, "stage5", "out", "rehearsal")
    ok, why, text = rehearse(blob, image, work)
    sys.stdout.write(text)
    print("PASS" if ok else "FAIL: " + why)
    sys.exit(0 if ok else 1)
