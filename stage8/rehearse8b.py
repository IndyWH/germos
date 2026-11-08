#!/usr/bin/env python3
"""stage8/rehearse8b.py - a part's rehearsal in the twin (stage8/plan-8b.md).

The spec's gates 1 and 3, for one part, on the twin of the HP. The part goes
through the guest's own path, by the words a human types: a blank disk; the
fetch through the relay and a mock (a frame carrying the part and a small
threshold, so the rehearsal is short); a shadow boot to that threshold; the
take; two boots with the part live.

    Gate 1: the twin boots, the part loads, no ERR:, no exception, health()
    answers (the health mark, with the part's live pet behind it).
    Gate 3: typing through the part, a note across a reboot, a click on the
    choices row, and ring 7d's synthetic human playing a sitting through the
    part's decode.

Everything is judged here and in the frozen helpers of rings 7c, 7d and 8a,
imported at their seams. Mock only: this file spends no token. It is frozen
at ring 8b item 14 for the reason ring 5 froze rehearse.py.

    python3 stage8/rehearse8b.py PART.bin [--workdir DIR]

Prints one "rehearsal: ..." line for each boot and a last line
"rehearsal: PASS" or "rehearsal: FAIL <why>". Exit 0 on PASS.
"""

import argparse
import hashlib
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "broker"))
import checkmolt as cm  # noqa: E402  - ring 8a's frozen checker: the twin, the human, the fates' boot
import parts  # noqa: E402
checkmetal = cm.checkmetal
checktrials = cm.checktrials

SLOT = "i8042"
THRESHOLD = (1, 60, 60)         # the rehearsal's own: one boot, a little of each
MOLT_PY = os.path.join(REPO, "broker", "molt.py")
NOTE_A = "this line crosses a reboot"
NOTE_B = "more words through the part so that it decodes well past a hundred bytes of input"
NOTE_PACKETS = 60
SITTING = checktrials.SCRIPT_1   # sitting 1, as ring 7d's gate plays it


def serve_argv(part_path, record):
    """The part in a frame through broker/molt.py's mock path."""
    return [sys.executable, MOLT_PY, "--mock", "--part-file", part_path,
            "--part-threshold", ",".join(str(x) for x in THRESHOLD), "--port", str(checkmetal.BROKER_PORT),
            "--record", record, "--germline", cm.MOLT_GERMLINE, "--image", cm.ESP, "--workdir", cm.MOLT_TWIN,
            "--rehearsal-port", str(checkmetal.REHEARSAL_PORT), "--plans", cm.PLANS_DIR]


def point_seams(workdir, stick):
    cm.OUT = workdir
    cm.MOLT_OUT = workdir
    cm.STICK = stick
    cm.MOLT_GERMLINE = os.path.join(workdir, "germline")
    cm.MOLT_TWIN = os.path.join(workdir, "twin")
    cm.point_molt_seams()
    checktrials.STICK = stick
    checktrials.TRIALS_OUT = workdir


class Rehearsal:
    def __init__(self, part_path, workdir, say):
        self.part_path = part_path
        self.part = open(part_path, "rb").read()
        self.workdir = workdir
        self.say = say
        self.problems = []
        self.f = cm.Fates(parts)
        self.sha16 = parts.sha16(hashlib.sha256(self.part).hexdigest())

    def boot(self, disk, tag, steps, fate=None):
        t = time.time()
        reads, problems = self.f.boot(disk, tag, steps, fate=fate)
        if reads is not None:
            errs = re.findall(rb"(?:ERR|exception)[^\r\n]*", reads["capture"])
            if errs:
                problems = problems + ["%s: the guest said %r" % (tag, errs[0].decode("latin-1"))]
            bad = re.findall(rb"S8: recovery [^\r\n]*", reads["capture"])
            if bad:
                problems = problems + ["%s: %s" % (tag, bad[0].decode("latin-1"))]
        self.problems += problems
        self.say("rehearsal: boot %s, %.1f s, %s" % (tag, time.time() - t, "ok" if not problems else "; ".join(problems)))
        return reads if not problems else None

    def run(self):
        self.f.timings = []
        cm.molt_argv = lambda fate, record, hold_s=None: serve_argv(self.part_path, record)
        disk = os.path.join(self.workdir, "disk.r.img")
        checkmetal.fresh_disk(disk)
        if not self.boot(disk, "r-blank", [("ready", "ready"), ("sleep", 1.0)]):
            return False
        line = "! molt %s\n" % SLOT
        steps = [("ready", "ready"), ("keys", line),
                 ("await", rb"molt: %s shadow %s " % (SLOT.encode(), self.sha16.encode()), cm.ANSWER_S, "installed", None),
                 ("sleep", cm.WORD_S)]
        if not self.boot(disk, "r-fetch", steps, fate="good"):
            return False
        # Shadow to the small threshold, and the take.
        _, K, M = THRESHOLD
        notes, _ = cm.typed_notes(K, 0, parts)
        steps = [("ready", "ready")] + [("keys", t + "\n") for t in notes] + [
            ("wiggle", M + (M % 2)), ("sleep", 1.0), ("keys", "! molt take %s\n" % SLOT),
            ("await", rb"molt: %s live %s" % (SLOT.encode(), self.sha16.encode()), cm.ANSWER_S, "taken", None),
            ("sleep", cm.WORD_S)]
        if not self.boot(disk, "r-shadow", steps):
            return False
        # Live: typing, a click, the health mark.
        n_notes = len(self.f.notes(disk))
        steps = [("ready", "ready"), ("keys", NOTE_A + "\n"), ("keys", NOTE_B + "\n"), ("wiggle", NOTE_PACKETS),
                 ("click", "key", ord("!")), ("keys", " molt\n"), ("sleep", cm.WORD_S), ("surfaces", "w"),
                 ("await", rb"S8: healthy \d+\r\n", parts.HEALTH_S + cm.HEALTH_SLACK_S, "healthy", "ready")]
        reads = self.boot(disk, "r-live1", steps)
        if not reads:
            return False
        if not re.search(rb"S8: part %s live %s\r\n" % (SLOT.encode(), self.sha16.encode()), reads["capture"]):
            self.problems.append("r-live1: the part did not load live")
            return False
        rows = checktrials.conv_rows(reads["w"]["conversation"], reads["w"]["obs"])
        if rows[-2:] != ["> ! molt", ">"]:
            self.problems.append("r-live1: the click on the choices row and ' molt' left %r" % rows[-3:])
            return False
        got = self.f.notes(disk)
        if NOTE_A not in got[n_notes:] or NOTE_B not in got[n_notes:]:
            self.problems.append("r-live1: the notes typed through the part are not on the disk: %r" % got[n_notes:])
            return False
        # Live again: the note back across the reboot, then a sitting.
        results, problems = self.sitting(disk, NOTE_A)
        self.problems += problems
        self.say("rehearsal: boot r-sitting: %s" % ("ok" if not problems else "; ".join(problems)))
        return not problems

    def sitting(self, disk, note):
        copy = checkmetal.fresh_stick(os.path.join(self.workdir, "stick.r-sitting.img"))
        serial = os.path.join(self.workdir, "serial.r-sitting.txt")
        results, capture, reads, events, err = checktrials.boot_and_play(
            cm.FATES_SMP, disk, copy, serial, SITTING, "r",
            extra_before=[("surfaces", "start")], read_at_rest=False)
        os.remove(copy)
        if err:
            cm.checkglass.dump_capture(capture)
            return None, ["the sitting: %s" % err]
        problems = []
        if not re.search(rb"S8: part %s live %s\r\n" % (SLOT.encode(), self.sha16.encode()), capture):
            problems.append("the sitting's boot did not load the part live")
        if re.search(rb"ERR[^\r\n]*|S8: recovery", capture):
            problems.append("the sitting's boot said an error or a recovery")
        rows = checktrials.conv_rows(reads["start"]["conversation"], reads["start"]["obs"])
        if ("> " + note) not in rows and note not in rows:
            problems.append("the note did not come back across the reboot: the replay's rows end %r" % rows[-4:])
        trial = [n for n in checktrials.notes_on_disk(disk) if n.startswith("trial ")]
        problems += checktrials.compare_notes(trial, SITTING, "the sitting through the part")
        return results, problems


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("part")
    ap.add_argument("--workdir", default=os.path.join(HERE, "out", "rehearse8b"))
    ap.add_argument("--stick", default=os.path.join(HERE, "out", "stick.img"))
    args = ap.parse_args(argv)
    shutil.rmtree(args.workdir, ignore_errors=True)
    os.makedirs(args.workdir)
    point_seams(args.workdir, args.stick)
    t0 = time.time()

    def say(line):
        print(line, flush=True)

    r = Rehearsal(args.part, args.workdir, say)
    try:
        parts.check_part(r.part, SLOT)
    except ValueError as exc:
        print("rehearsal: FAIL the door: %s" % exc, flush=True)
        return 1
    ok = r.run()
    if ok and not r.problems:
        print("rehearsal: PASS %.1f s" % (time.time() - t0), flush=True)
        return 0
    print("rehearsal: FAIL %s" % "; ".join(r.problems or ["the rehearsal stopped"]), flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
