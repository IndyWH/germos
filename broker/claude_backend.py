"""The broker's Claude backend - two small, swappable functions.

ask(question, timeout) runs `claude -p` on mlrig's Max subscription and
returns plain text fit for the wire (stage4/UMBILICAL.md: printable ASCII
and LF, at most 4096 bytes). grow(request, failure, timeout, model) - Stage
5 - asks for NASM source for a flat binary against stage5/GERMLINE.md's
entry contract and service table, assembles it on the host, feeds an
assembly error back for up to three rounds, and returns the blob or a
refusal. No API key is involved anywhere: the CLI holds its own login. If
the subscription policy ever unpauses, this is the one file to swap.

Deliberately NOT frozen (Stage 4 plan decision 13, Stage 5 decision 15):
the automated gate never runs this file - the tests use the mock - and it
is exercised only by the owner at test 5, so its flags, its brief and its
normalisation must stay fixable there. Stage 4's lesson: --bare skips the
CLI's own login, so it stays off.
"""

import os
import re
import subprocess
import tempfile
import unicodedata

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GERMLINE_DOC = os.path.join(REPO, "stage5", "GERMLINE.md")
BLOB_MAX = 1048576
ASSEMBLY_ROUNDS = 3

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


# ------------------------------------------------------------- Stage 5 ----

def model_name(model=None):
    """The backend's name for the provenance record: the CLI version, and
    the --model if one was given. No call to Claude is made."""
    try:
        out = subprocess.run(["claude", "--version"], capture_output=True, text=True,
                             timeout=20, stdin=subprocess.DEVNULL).stdout.strip().split()
        version = out[0] if out else "unknown"
    except (OSError, subprocess.TimeoutExpired):
        version = "unknown"
    return "claude -p %s%s" % (version, (" --model " + model) if model else "")


def abi_sections():
    """The entry contract and the service table, verbatim from GERMLINE.md,
    so the brief and the frozen document can never disagree."""
    try:
        doc = open(GERMLINE_DOC).read()
    except OSError:
        return ""
    out = []
    for heading in ("## The entry contract", "## The service table"):
        i = doc.find(heading)
        if i < 0:
            continue
        j = doc.find("\n## ", i + 1)
        out.append(doc[i:j if j > 0 else None].strip())
    return "\n\n".join(out)


GROW_BRIEF = (
    "You are writing a program for GermOS, a tiny operating system being grown "
    "on this machine. The user typed one line at its prompt asking for something; "
    "you answer with the machine code, as NASM source for a FLAT BINARY that the "
    "OS will load and call. Rules, all of them hard:\n"
    "- Output ONLY NASM source, nothing else: no prose, no markdown, no code fences. "
    "The first line is `bits 64`, the second `default rel`. It is assembled with "
    "`nasm -f bin`. No `org`, no sections, no `global`, no `extern`, no `%include`.\n"
    "- The first byte of the output is the entry point: the OS does `call` to it "
    "with RDI = the address of the service table described below, and expects a "
    "`ret`. Keep your data after the code. Every memory reference must be "
    "RIP-relative (default rel does this for labels) - no absolute addresses.\n"
    "- Use the service table for all output and input. Do not touch any port, "
    "memory or device except: port I/O you need for the request itself "
    "(the CMOS real-time clock at ports 0x70/0x71 is fine, for example). No "
    "serial port, no keyboard ports, no interrupts, no page tables.\n"
    "- Poll `poll_key` in your main loop and return (with `ret`, stack balanced) "
    "as soon as it returns 0x1B (Escape). Redraw only when something changed, or "
    "on a timer using `ticks_ms`; do not busy-loop the screen.\n"
    "- Stay under 64 KB of code and data. No SSE/AVX. Ring 0, interrupts enabled; "
    "the stack is 16 KB, use under 4 KB.\n"
    "- Preserve RBX, RBP, R12-R15 across your own service calls: the services "
    "preserve them, but clobber RAX, RCX, RDX, RSI, RDI, R8-R11.\n\n"
)


def extract_source(text):
    """The NASM source out of the model's reply: a fenced block if there is
    one, else the text from the first `bits 64` line."""
    m = re.search(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
    src = m.group(1) if m else text
    i = src.find("bits 64")
    if i > 0:
        src = src[i:]
    return src.strip() + "\n"


def grow(request, failure=None, timeout=120.0, model=None):
    """The request in, a blob out - or a refusal string. Never an exception."""
    brief = GROW_BRIEF + abi_sections()
    prompt = "The user asked: %s" % request
    if failure:
        prompt += ("\n\nA previous attempt at this was rejected by the rehearsal in the "
                   "twin: %s. Write it again, more carefully." % failure)
    last_error = "no source produced"
    for _ in range(ASSEMBLY_ROUNDS):
        cmd = ["claude", "-p", "--output-format", "text", "--tools", "",
               "--no-session-persistence", "--system-prompt", brief]
        if model:
            cmd += ["--model", model]
        cmd += ["--", prompt]
        with tempfile.TemporaryDirectory(prefix="germos-grow-") as cwd:
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
            src = extract_source(proc.stdout)
            asm = os.path.join(cwd, "grown.asm")
            blob = os.path.join(cwd, "grown.bin")
            with open(asm, "w") as fh:
                fh.write(src)
            try:
                nasm = subprocess.run(["nasm", "-f", "bin", asm, "-o", blob],
                                      capture_output=True, text=True, timeout=60)
            except (OSError, subprocess.TimeoutExpired) as exc:
                return "broker: could not run nasm (%s)" % exc
            if nasm.returncode == 0 and os.path.isfile(blob):
                data = open(blob, "rb").read()
                if 1 <= len(data) <= BLOB_MAX:
                    return data
                last_error = "the assembled binary is %d bytes, outside 1..%d" % (len(data), BLOB_MAX)
            else:
                last_error = normalise(nasm.stderr).strip().splitlines()[:6]
                last_error = "; ".join(l.split(": ", 1)[-1] for l in last_error) or "nasm failed"
        prompt = ("The user asked: %s\n\nYour previous source did not assemble. nasm said: %s\n"
                  "Write the whole program again, corrected. Output only NASM source."
                  % (request, last_error))
    return normalise("broker: could not grow it - " + str(last_error))
