"""The broker's Claude backend - one small, swappable function.

ask(question, timeout) runs `claude -p` on mlrig's Max subscription and
returns plain text fit for the wire (stage4/UMBILICAL.md: printable ASCII
and LF, at most 4096 bytes). No API key is involved anywhere: the CLI holds
its own login. If the subscription policy ever unpauses, this is the one
function to swap (Stage 4 spec, the policy gate).

Deliberately NOT frozen (plan decision 13): the automated gate never runs
this file - the tests use broker.py --mock - and it is exercised only by the
owner at test 5, so its flags and its normalisation must stay fixable.
"""

import os
import subprocess
import tempfile
import unicodedata

BRIEF = (
    "You are answering a single line typed at the prompt of GermOS, a tiny "
    "operating system that is being grown on this machine and has just "
    "learned to speak to you. Answer in plain ASCII text only: no markdown, "
    "no bullet points, no code fences. Be brief - a few sentences at most."
)

FOLD = {
    "—": "-", "–": "-", "−": "-", "‘": "'", "’": "'",
    "“": '"', "”": '"', "…": "...", " ": " ", "\t": "    ",
    "•": "*", "·": "*", "→": "->", "←": "<-",
}

WIRE_MAX = 4096


def normalise(text):
    """Fold common punctuation to ASCII, drop what will not fold, CRLF to LF,
    trim trailing whitespace, cap at the wire's maximum."""
    for k, v in FOLD.items():
        text = text.replace(k, v)
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(ch for ch in text if 0x20 <= ord(ch) <= 0x7E or ch == "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n")).strip()
    if len(text) > WIRE_MAX:
        text = text[:WIRE_MAX - 3].rstrip() + "..."
    return text


def ask(question, timeout=120.0):
    """The question in, the answer out - always a string, never an exception:
    a failure is a sentence the machine can print."""
    cmd = [
        "claude", "-p",
        "--output-format", "text",
        "--tools", "",
        "--no-session-persistence",
        "--bare",
        "--system-prompt", BRIEF,
        "--", question,
    ]
    with tempfile.TemporaryDirectory(prefix="germos-broker-") as cwd:
        try:
            proc = subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL,
                                  capture_output=True, text=True, timeout=timeout,
                                  env=dict(os.environ, TERM="dumb"))
        except subprocess.TimeoutExpired:
            return "broker: claude did not answer within %d s" % int(timeout)
        except OSError as exc:
            return "broker: could not run claude (%s)" % exc
    if proc.returncode != 0:
        tail = normalise(proc.stderr or proc.stdout).strip().splitlines()[-1:] or [""]
        return "broker: claude failed (%d) %s" % (proc.returncode, tail[0])
    answer = normalise(proc.stdout)
    return answer if answer else "broker: claude returned an empty answer"
