"""The broker's Claude backend - two small, swappable functions.

ask(question, timeout) runs `claude -p` on mlrig's Max subscription and
returns plain text fit for the wire (stage4/UMBILICAL.md: printable ASCII
and LF, at most 4096 bytes). grow(request, failure, timeout, model) - Stage
5 - asks for NASM source for a flat binary against stage5/GERMLINE.md's
entry contract and service table, assembles it on the host, feeds an
assembly error back for up to three rounds, and returns the blob or a
refusal. grow(..., abi=2) - Stage 6 ring 6a - asks instead for an ABI 2
app against stage6/GLASS.md's callback contract (four offsets first, the
four services, a panel of its own), names it after the request, reads any
`; choice <key> <label>` lines the source declares, and returns ("app",
blob, name, choices) or ("refusal", text). No API key is involved anywhere:
the CLI holds its own login. If the subscription policy ever unpauses,
this is the one file to swap.

Deliberately NOT frozen (Stage 4 plan decision 13, Stage 5 decision 15):
the automated gate never runs this file - the tests use the mock - and it
is exercised only by the owner at test 5, so its flags, its brief and its
normalisation must stay fixable there. Stage 4's lesson: --bare skips the
CLI's own login, so it stays off.
"""

import os
import re
import struct
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


# ------------------------------------------------------------- Stage 6 ----

GLASS_DOC = os.path.join(REPO, "stage6", "GLASS.md")
NAME_MAX = 32
CHOICE_LINE = re.compile(r"^\s*;\s*choice\s+(\S)\s+(.{1,12}?)\s*$", re.M)


def glass_sections():
    """The callback contract and what the screen does around an app,
    verbatim from GLASS.md, so the brief and the frozen document can never
    disagree."""
    try:
        doc = open(GLASS_DOC).read()
    except OSError:
        return ""
    out = []
    for heading in ("## An app is four callbacks", "## Running an app"):
        i = doc.find(heading)
        if i < 0:
            continue
        j = doc.find("\n## ", i + 1)
        out.append(doc[i:j if j > 0 else None].strip())
    return "\n\n".join(out)


APP_BRIEF = (
    "You are writing an app for GermOS, a tiny operating system being grown "
    "on this machine. The user typed one line at its prompt asking for something; "
    "you answer with the machine code, as NASM source for a FLAT BINARY that the "
    "OS will load into a panel of its screen and drive through four callbacks. "
    "Rules, all of them hard:\n"
    "- Output ONLY NASM source, nothing else: no prose, no markdown, no code fences. "
    "The first line is `bits 64`, the second `default rel`. It is assembled with "
    "`nasm -f bin`. No `org`, no sections, no `global`, no `extern`, no `%include`.\n"
    "- The first 16 bytes of the output are four u32 offsets from the start of the "
    "blob - init, step, key, exit - written as `dd init, step, key, exit` with those "
    "labels; the code follows. Every memory reference must be RIP-relative (default "
    "rel does this for labels) - no absolute addresses. Keep your data after the code; "
    "keep the service table pointer init receives in a data qword for the others.\n"
    "- Draw ONLY through the services, into your own panel: draw_text and fill with "
    "rows and columns relative to the panel, panel_size for its size, ticks_ms for "
    "time. Do not touch any port, memory or device except port I/O the request "
    "itself needs (the CMOS real-time clock at ports 0x70/0x71 is fine, for example). "
    "No serial port, no keyboard ports, no framebuffer, no interrupts, no page tables.\n"
    "- step is called about every 10 ms and must return within a few milliseconds - "
    "never spin, never wait inside it; redraw only when something changed. key is "
    "called with the key in RDI. Each callback returns with ret, stack balanced.\n"
    "- Stay under 64 KB of code and data. No SSE/AVX. Ring 0, interrupts enabled; "
    "use under 4 KB of stack.\n"
    "- Preserve RBX, RBP, R12-R15 across your own service calls: the services "
    "preserve them, but clobber RAX, RCX, RDX, RSI, RDI, R8-R11.\n"
    "- You may declare up to four keyboard choices the screen will show, one per "
    "comment line placed immediately after the `default rel` line: `; choice <key> "
    "<label>` with a one-character key and a "
    "label of at most 12 characters. Handle those keys in key.\n\n"
)


def app_name(request):
    name = "".join(ch for ch in request if 0x20 <= ord(ch) <= 0x7E).strip()[:NAME_MAX]
    return (name or "app").encode("ascii")


def app_choices(src):
    out = []
    for m in CHOICE_LINE.finditer(src):
        key, label = m.group(1), m.group(2).strip()
        if 0x20 <= ord(key) <= 0x7E and label and all(0x20 <= ord(c) <= 0x7E for c in label):
            out.append((ord(key), label.encode("ascii")))
        if len(out) == 4:
            break
    return out


PLAN_RULE = (
    "- Draw the starting state in init: a panel that is blank until the first "
    "key fails rehearsal before the tests run.\n\n"
)


def plan_brief(plan, amendment=None):
    """Ring 6b: the plan's intent, choices and tests as the brief's last
    section (stage6/PLANS.md, 'The install')."""
    out = ["\n\nYou are building the app named `%s` from this plan.\n" % plan["name"],
           "Intent: %s\n" % plan["intent"]]
    if plan["choices"]:
        out.append("The choices row will show these keys; handle each in key: "
                   + ", ".join("%s (%s)" % (chr(k), l.decode("ascii")) for k, l in plan["choices"]) + ".\n")
    out.append("After it is built the twin will run these tests against it, in order, and "
               "the build must pass every one:\n")
    for verb, arg in plan["tests"]:
        if verb == "press":
            out.append("  press %s\n" % arg)
        elif verb == "wait":
            out.append("  wait %d\n" % arg)
        elif verb == "expect changed":
            out.append("  expect changed\n")
        else:
            out.append('  %s "%s"\n' % (verb, arg))
    out.append("`press <keys>` sends each character to key, 0.2 s apart; `expect \"<text>\"` "
               "means that text is somewhere on the app's panel, read cell by cell; `expect not` "
               "that it is nowhere; `expect changed` that the panel changed since the twin last "
               "looked. Draw only what the intent says. Draw the starting state in init: a panel "
               "that is blank until the first key fails rehearsal before the tests run.\n")
    if amendment:
        out.append("The person installing it adds: %s\n" % amendment)
    return "".join(out)


def grow(request, failure=None, timeout=120.0, model=None, abi=1, plan=None):
    """The request in, a blob out - or a refusal. Never an exception.
    abi=1 (Stage 5): a blob (bytes) or a refusal string. abi=2 (Stage 6):
    ("app", blob, name, choices) or ("refusal", text). With a plan (ring
    6b, a parsed plans/<name>.md, optionally with an amendment under
    plan["amendment"]): the plan brief, the plan's name and choices."""
    if abi == 2:
        brief = APP_BRIEF + (PLAN_RULE if plan else "") + glass_sections()
        if plan:
            brief += plan_brief(plan, plan.get("amendment"))
        result = _grow(request, failure, timeout, model, brief, True)
        if isinstance(result, tuple):
            blob, src = result
            try:
                offs = struct.unpack_from("<IIII", blob, 0) if len(blob) >= 16 else None
            except struct.error:
                offs = None
            if offs is None or any(o >= len(blob) for o in offs):
                return ("refusal", "broker: the assembled app does not begin with four offsets inside it")
            if plan:
                return ("app", blob, plan["name"].encode("ascii"), list(plan["choices"]))
            return ("app", blob, app_name(request), app_choices(src))
        return ("refusal", result)
    return _grow(request, failure, timeout, model, GROW_BRIEF + abi_sections(), False)


def _grow(request, failure, timeout, model, brief, want_source):
    """The claude -p rounds. Returns the blob (bytes), or (blob, source)
    when want_source, or a refusal string."""
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
                    return (data, src) if want_source else data
                last_error = "the assembled binary is %d bytes, outside 1..%d" % (len(data), BLOB_MAX)
            else:
                last_error = normalise(nasm.stderr).strip().splitlines()[:6]
                last_error = "; ".join(l.split(": ", 1)[-1] for l in last_error) or "nasm failed"
        prompt = ("The user asked: %s\n\nYour previous source did not assemble. nasm said: %s\n"
                  "Write the whole program again, corrected. Output only NASM source."
                  % (request, last_error))
    return normalise("broker: could not grow it - " + str(last_error))
