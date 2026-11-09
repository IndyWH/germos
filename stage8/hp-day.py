#!/usr/bin/env python3
"""stage8/hp-day.py - the HP's day for ring 8b (stage8/plan-8b.md, A1).

The owner starts this once on mlrig, before the power button. It checks the
day can run, starts the chart with its way back in, the collect broker and the
relay, sends every order to the HP itself when the chart shows its condition,
and writes everything it sends and sees to stage8/out/hp-8b.log, which Cowork
reads. The owner presses the power button once, uses the keys and the mouse
freely, and types one word here, take, when this program asks.

    python3 stage8/hp-day.py <serial port>

The port is the adapter's, exactly as broker/chart.py names it; no path is
spelled here. --twin SOCK is the proof in the twin: the guest's serial on a
QEMU socket in place of the port. Unfrozen: a tool, not a criterion. It calls
no backend: broker/molt.py --collect only serves the germline.
"""

import argparse
import hashlib
import os
import queue
import re
import socket
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "broker"))
import parts  # noqa: E402
from chart import stamp  # noqa: E402
from claude_backend import refuse_api_keys  # noqa: E402
from molt import part_lookup  # noqa: E402

HP_IDENTITY = "cpu 000306a9 pci 8086:1e47:04"
SLOT = "i8042"
PROBE_PORT = 9995
SECOND_ADDRESS = "10.0.2.4"
POLL_S = 5.0            # between two germos count orders
ANSWER_S = 10.0         # an order's answer on the chart
REMIND_S = 60.0         # how often a wait says what it is waiting for
ORDER_TRIES = 3         # orders unanswered before the day stops
SHADOW_BOOTS = 3
LIVE_BOOTS = 3
MARK = re.compile(r"order: |S8: |S7: |molt: ")


class Stop(Exception):
    """Something the day must not act past: it stops sending."""


class Day:
    def __init__(self, args):
        self.a = args
        self.log_path = args.log
        self.q = queue.Queue()
        self.services = []
        self.sk = None
        self.new_boot()
        self.th = None
        self.taken = None
        self.installed = None
        self.tally = {}

    # -- what is said and what is sent
    def say(self, text):
        print("day: " + text, flush=True)
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write("%s day: %s\n" % (stamp(), text))

    def stop(self, why):
        raise Stop(why)

    def new_boot(self):
        self.ready = self.healthy = False
        self.part = self.owner_esc = None
        self.count = (0, 0, 0)
        self.answer = None

    # -- the chart
    def reader(self):
        buf = b""
        while True:
            try:
                data = self.sk.recv(4096)
            except OSError:
                data = b""
            if not data:
                self.q.put(None)
                return
            buf += data
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                line = raw.replace(b"\r", b"").decode("utf-8", "replace")
                if self.a.twin:
                    with open(self.log_path, "a", encoding="utf-8") as fh:
                        fh.write("%s %s\n" % (stamp(), line))
                self.q.put(line)

    def handle(self, line):
        # The guest's own lines can land after the echo of a half-typed line,
        # as in "the calculator liorder: count 244 0 0". The line is read from
        # its last marker, as parts.py reads the chart.
        if "ERR:" in line:
            self.stop("the HP said: " + line)
        marks = list(MARK.finditer(line))
        if marks:
            line = line[marks[-1].start():]
        if line == "S7: alive":
            self.new_boot()
        elif line == "S7: keyboard ready":
            self.ready = True
        elif line == "S8: recovery owner":
            self.owner_esc = True
        elif line.startswith("S8: recovery"):
            self.stop("the HP said: " + line)
        elif line.startswith("S8: healthy"):
            self.healthy = True
        elif line.startswith("molt: %s disagree" % SLOT):
            self.stop("a disagreement between the generic and the part: " + line)
        elif line == "order: reset failed":
            self.say("The restart did not take. Please press the HP's power button, once, to power it off, and once more to power it on.")
        elif line.startswith("order: count "):
            k, p, d = (int(x) for x in line.split()[2:5])
            self.count = (k, p, d)
            self.answer = "count"
            if d:
                self.stop("the count says %d disagreements" % d)
        elif line.startswith("order: "):
            self.answer = line[len("order: "):]
        else:
            m = re.fullmatch(r"S8: part %s (shadow|live) ([0-9a-f]{16})" % SLOT, line)
            if m:
                self.part = (m.group(1), m.group(2))
                return
            m = re.fullmatch(r"molt: %s shadow ([0-9a-f]{16}) (\d+) (\d+) (\d+)" % SLOT, line)
            if m:
                self.installed = m.group(1)
                self.th = tuple(int(x) for x in m.groups()[1:])
                return
            m = re.fullmatch(r"molt: %s live ([0-9a-f]{16})" % SLOT, line)
            if m:
                self.taken = m.group(1)

    def pump(self, seconds):
        end = time.time() + seconds
        while True:
            left = end - time.time()
            try:
                line = self.q.get(timeout=max(left, 0.0)) if left > 0 else self.q.get_nowait()
            except queue.Empty:
                return
            if line is None:
                self.stop("the serial line closed")
            self.handle(line)

    def until(self, cond, what):
        last = time.time()
        while not cond():
            self.pump(0.2)
            if time.time() - last > REMIND_S:
                self.say("Still waiting for " + what + ".")
                last = time.time()

    def send(self, text):
        self.sk.sendall((text + "\n").encode())
        if self.a.twin:
            with open(self.log_path, "a", encoding="utf-8") as fh:
                fh.write("%s > %s\n" % (stamp(), text))

    def ask(self, text):
        """One order and its first answer; retried while unanswered."""
        for _ in range(ORDER_TRIES):
            self.answer = None
            self.send(text)
            end = time.time() + ANSWER_S
            while self.answer is None and time.time() < end:
                self.pump(0.1)
            if self.answer is not None:
                return self.answer
        self.stop("the HP did not answer %s" % text)

    def word(self, text):
        """A molt order: retried while the guest is busy or the line was garbled."""
        while True:
            a = self.ask(text)
            if a == "done":
                return
            if a == "busy":
                self.say("The HP is busy, or a key was pressed in the last 5 s. Trying again.")
            elif a != "?":
                self.stop("%s was answered: order: %s" % (text, a))
            self.pump(POLL_S + 1)

    def poll(self, index):
        self.ask("germos count")
        self.tally[index] = self.count
        self.pump(POLL_S)

    def restart(self):
        """After a restart the next line of interest is the next boot's ready."""
        while True:
            a = self.ask("germos restart")
            if a == "restart":
                self.say("Restarting the HP.")
                self.ready = False
                return
            self.say("The restart was answered: order: %s. Trying again." % a)
            self.pump(POLL_S)

    def next_boot(self, name):
        self.say("Waiting for %s." % name)
        while True:
            self.until(lambda: self.ready, name + " to reach the keyboard ready line")
            if self.owner_esc:
                self.say("Esc was held at power-on. No part loaded and nothing is demoted. Restarting.")
                self.pump(2.0)
                self.restart()
                continue
            return

    # -- the seven boots
    def boots(self):
        expect = self.sha
        self.next_boot("boot 1, the fetch. Please press the HP's power button now")
        if self.part:
            self.stop("boot 1 loaded a part, %s %s. The plan expects none." % self.part)
        self.pump(2.0)
        self.say("Boot 1: asking the HP to fetch its part.")
        self.word("germos molt %s" % SLOT)
        self.pump(2.0)
        if self.installed != expect:
            self.stop("the fetch did not install the part: installed %r, wanted %s" % (self.installed, expect))
        self.say("Boot 1: installed in shadow, %s, threshold %d boots, %d keys, %d mouse packets." % ((expect,) + self.th))
        self.restart()

        for i in range(1, SHADOW_BOOTS + 1):
            self.next_boot("boot %d, shadow %d" % (i + 1, i))
            if self.part != ("shadow", expect):
                self.stop("boot %d loaded %r, not this part in shadow" % (i + 1, self.part))
            self.say("Boot %d: the part runs in shadow. Use the keys and mouse freely." % (i + 1))
            if i < SHADOW_BOOTS:
                while not self.healthy:
                    self.poll(i)
                self.poll(i)
                self.restart()
        last = SHADOW_BOOTS
        told = 0.0
        while True:
            self.poll(last)
            k = sum(c[0] for c in self.tally.values())
            p = sum(c[1] for c in self.tally.values())
            if self.healthy and k >= self.th[1] and p >= self.th[2]:
                self.say("Boot 4: the counts are met: %d keys and %d mouse packets." % (k, p))
                self.say("Please stop typing on the HP. Type the word take here and press Enter.")
                self.wait_take()
                self.pump(1.0)
                self.word("germos molt take %s" % SLOT)
                self.pump(2.0)
                if self.taken == expect:
                    break
                self.say("The HP refused the take. Keep using the keys and mouse; the counts are checked again.")
            elif time.time() - told > 30:
                self.say("Boot 4: %d of %d keys, %d of %d mouse packets%s." % (
                    k, self.th[1], p, self.th[2], "" if self.healthy else ", waiting for the health mark"))
                told = time.time()
        self.say("The part is taken. It runs live from the next boot.")
        self.restart()

        for i in range(1, LIVE_BOOTS + 1):
            self.next_boot("boot %d, live %d" % (i + 4, i))
            if self.part != ("live", expect):
                self.stop("boot %d loaded %r, not this part live" % (i + 4, self.part))
            self.say("Boot %d: the part is live. Use the keys and mouse freely." % (i + 4))
            told = 0.0
            while True:
                self.poll(1000 + i)
                k, p, _ = self.count
                if self.healthy and (i == LIVE_BOOTS or (k > 0 and p > 0)):
                    break
                if time.time() - told > 30:
                    self.say("Boot %d: %d keys, %d mouse packets so far%s." % (
                        i + 4, k, p, "" if self.healthy else ", waiting for the health mark"))
                    told = time.time()
            if i < LIVE_BOOTS:
                self.restart()

    def wait_take(self):
        while True:
            try:
                line = input()
            except EOFError:
                self.stop("the terminal closed before the word take")
            if line.strip() == "take":
                return
            print("Type the word take, or press Ctrl-C to stop.", flush=True)

    def finish(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "parts.py"), "--serial", self.log_path],
                           capture_output=True, text=True)
        table = [ln for ln in r.stdout.splitlines() if ln.startswith((SLOT + " ", "boots ", "disagreements ", "DISAGREES"))]
        for ln in table:
            self.say(ln)
        if r.returncode or not [ln for ln in table if "probation %d/%d" % (LIVE_BOOTS, LIVE_BOOTS) in ln]:
            self.stop("the chart's table does not say probation %d/%d" % (LIVE_BOOTS, LIVE_BOOTS))
        self.say("All seven boots are done and the table says probation %d/%d. The services stop now." % (LIVE_BOOTS, LIVE_BOOTS))
        self.say("The ring's closing word is yours.")

    # -- the checks and the services
    def preflight(self):
        refuse_api_keys()
        problems = []
        if not self.a.twin:
            if not os.path.exists(self.a.port):
                problems.append("The serial adapter %s is not there." % self.a.port)
            elif not os.access(self.a.port, os.R_OK | os.W_OK):
                problems.append("This login may not open the serial adapter %s. Its group is the fix." % self.a.port)
            ip = subprocess.run(["ip", "-4", "addr", "show", self.a.iface], capture_output=True, text=True)
            if (SECOND_ADDRESS + "/") not in ip.stdout:
                problems.append("%s does not hold the second address %s." % (self.a.iface, SECOND_ADDRESS))
            have = hashlib.sha256(open(os.path.join(OUT, "BOOTX64.EFI"), "rb").read()).hexdigest()
            seeds = [ln.split() for ln in open(os.path.join(HERE, "seed-record.md"), encoding="utf-8") if ln.startswith("seed ")]
            if have != seeds[-1][2]:
                problems.append("The build is %s, not the record's last seed, %s." % (have[:16], seeds[-1][2][:16]))
        ports = [9999, 9998, 9997] + ([] if self.a.twin else [PROBE_PORT])
        for port in ports:
            with socket.socket() as s:
                s.settimeout(0.5)
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    problems.append("Something is already listening on port %d." % port)
        key = parts.molt_key(SLOT, self.a.identity)
        part, prov = part_lookup(self.a.germline, key)
        if part is None:
            problems.append("The germline holds no part for this machine%s." % (
                ": its finding was " + str(prov.get("verdict")) if prov else ""))
        else:
            self.sha = parts.sha16(hashlib.sha256(part).hexdigest())
        if problems:
            for p in problems:
                print(p, flush=True)
            print("Nothing was started.", flush=True)
            return False
        return True

    def start(self, name, argv):
        err = open(os.path.join(OUT, "hp-8b-%s.stderr.txt" % name), "ab")
        self.services.append(subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=err, cwd=REPO))

    def wait_port(self, port, addr="127.0.0.1"):
        for _ in range(100):
            with socket.socket() as s:
                s.settimeout(0.2)
                if s.connect_ex((addr, port)) == 0:
                    return True
            time.sleep(0.1)
        return False

    def start_services(self):
        py = sys.executable
        b = os.path.join(REPO, "broker")
        if self.a.twin:
            bind = ["--bind", "127.0.0.1", "--port", "9997"]
            relay = ("127.0.0.1", 9997)
        else:
            bind, relay = [], (SECOND_ADDRESS, 9999)
            self.start("probe", [py, os.path.join(b, "probe.py"), self.a.port, self.log_path])
            if not self.wait_port(PROBE_PORT):
                self.stop("the chart did not start")
        self.start("broker", [py, os.path.join(b, "molt.py"), "--collect", "--germline", self.a.germline, "--image", os.path.join(OUT, "esp.img"),
                              "--workdir", os.path.join(OUT, "hp-8b-twin"), "--record", os.path.join(OUT, "hp-8b-broker.jsonl")])
        if not self.wait_port(9999):
            self.stop("the collect broker did not start")
        self.start("relay", [py, os.path.join(b, "relay.py")] + bind + ["--log", os.path.join(OUT, "hp-8b-relay.jsonl")])
        if not self.wait_port(relay[1], relay[0]):
            self.stop("the relay did not start")
        if self.a.twin:
            self.sk = socket.socket(socket.AF_UNIX)
            for _ in range(100):
                try:
                    self.sk.connect(self.a.twin)
                    break
                except OSError:
                    time.sleep(0.1)
            else:
                self.stop("the twin's serial socket is not there")
        else:
            self.sk = socket.create_connection(("127.0.0.1", PROBE_PORT))
        threading.Thread(target=self.reader, daemon=True).start()

    def stop_services(self):
        for p in reversed(self.services):
            p.terminate()
        for p in self.services:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("port", nargs="?", default=None, help="the serial adapter, as broker/chart.py names it")
    ap.add_argument("--twin", default=None, metavar="SOCK", help="the guest's serial on this QEMU socket instead of a port")
    ap.add_argument("--identity", default=HP_IDENTITY, help="the machine the part must be keyed to")
    ap.add_argument("--germline", default=os.path.join(REPO, "germline"))
    ap.add_argument("--iface", default="eno2")
    ap.add_argument("--log", default=os.path.join(OUT, "hp-8b.log"))
    args = ap.parse_args(argv)
    if not args.port and not args.twin:
        print("usage: python3 stage8/hp-day.py <serial port>", flush=True)
        return 1
    day = Day(args)
    if not day.preflight():
        return 1
    try:
        day.start_services()
        day.say("The day has started. This program sends every order. Log: %s" % os.path.relpath(args.log, REPO))
        day.boots()
        day.finish()
        return 0
    except Stop as why:
        day.say("STOPPED: %s" % why)
        if args.twin:
            return 1
        day.say("Nothing more will be sent. The services stay up. Tell Cowork to read the log. Ctrl-C ends this program.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        return 1
    except KeyboardInterrupt:
        day.say("Ended by Ctrl-C.")
        return 1
    finally:
        day.stop_services()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
