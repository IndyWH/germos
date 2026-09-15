#!/usr/bin/env python3
"""The GermOS chart - the serial reader for the metal's day (Stage 7 ring
7c, stage7/METAL.md step 5).

The HP's COM A reaches mlrig through a null-modem cable and a USB-to-serial
adapter. This reads that port at 115200 8N1, prints every line to the
terminal as it arrives, and tees it to a file with a timestamp - the
observation chart the review reads afterwards and the file that goes into
history/ beside the photograph. Standard library only: termios, no
pyserial, no new package. Unfrozen: a tool, not a criterion.

Usage:
    python3 broker/chart.py /dev/ttyUSB0 stage7/out/metal.log

Start it BEFORE the HP is powered on, so "S7: alive" is the first line in
the file. Ctrl-C ends it with the file complete; a port that cannot be
opened is a loud exit 2 with the reason.

The open is O_RDWR | O_NOCTTY | O_NONBLOCK, then termios is set with
CLOCAL among the flags, then O_NONBLOCK is cleared (plan-7c.md A1): a
serial open without O_NONBLOCK blocks until DCD is asserted while CLOCAL
is still clear in the driver's default termios, and a three-wire
null-modem cable never asserts DCD - the reader would hang at open and
print nothing, and the first suspect on the day would wrongly be the HP.
"""

import datetime
import fcntl
import os
import sys
import termios

BAUD = termios.B115200


def open_port(path):
    """The port, raw, 115200 8N1, blocking reads of at least one byte -
    opened non-blocking first so a missing DCD cannot hold the open."""
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attr = termios.tcgetattr(fd)
    attr[0] = 0                                                  # iflag: no IXON/IXOFF, no ICRNL, no parity checks
    attr[1] = 0                                                  # oflag: no OPOST
    attr[2] = termios.CS8 | termios.CREAD | termios.CLOCAL       # cflag: 8 bits, receive, ignore modem lines;
    attr[3] = 0                                                  #        PARENB and CSTOPB clear - N, 1
    attr[4] = BAUD                                               # lflag: raw - no ICANON, no ECHO, no ISIG
    attr[5] = BAUD
    cc = list(attr[6])
    cc[termios.VMIN] = 1
    cc[termios.VTIME] = 0
    attr[6] = cc
    termios.tcsetattr(fd, termios.TCSANOW, attr)
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
    return fd


def stamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: python3 broker/chart.py <serial port> <log file>\n")
        return 2
    port, log_path = argv
    try:
        fd = open_port(port)
    except OSError as exc:
        sys.stderr.write("chart: cannot open %s: %s\n" % (port, exc))
        return 2
    try:
        log = open(log_path, "a", encoding="utf-8")
    except OSError as exc:
        sys.stderr.write("chart: cannot open %s: %s\n" % (log_path, exc))
        os.close(fd)
        return 2
    sys.stderr.write("chart: reading %s at 115200 8N1, teeing to %s (Ctrl-C ends it)\n" % (port, log_path))
    sys.stderr.flush()

    def emit(raw):
        line = raw.replace(b"\r", b"").decode("utf-8", "replace")
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        log.write("%s %s\n" % (stamp(), line))
        log.flush()

    buf = b""
    try:
        while True:
            try:
                chunk = os.read(fd, 4096)
            except InterruptedError:
                continue
            if not chunk:
                break                    # the adapter went away: end with the file complete
            buf += chunk
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                emit(raw)
    except KeyboardInterrupt:
        pass
    finally:
        if buf:
            emit(buf)                    # a partial line at the end is kept, not lost
        log.close()
        os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
