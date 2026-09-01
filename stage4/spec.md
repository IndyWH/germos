# Stage 4 spec — The umbilical

**spec.md for Stage 4 · Cowork, 1 September 2026 · status: APPROVED by Wajira, 1 September 2026**

## What we are building

The machine gets its brain's phone line. A virtio-net driver, a deliberately minimal TCP/IP stack, and a broker service on mlrig that relays questions to Claude. Done-when, from the foundation: **the booted OS asks Claude a question and prints the answer.** You type a line starting with `?` at the prompt; the answer appears on the console.

## The policy gate, cleared

The foundation requires the subscription policy re-checked here. Done, 1 September 2026: Anthropic announced (then paused) a June 2026 change moving Agent SDK and `claude -p` usage to a separate credit pool; the current official position is that nothing changed — `claude -p` still draws from Max subscription limits. The broker therefore shells out to `claude -p`, no API keys anywhere, and its Claude backend is one small function, swappable if the policy ever unpauses. Re-check again at Stage 5.

## The safety shape

The twin's network is a cage with one door. QEMU runs the NIC with `restrict=on`, so the guest can reach nothing at all — no LAN, no internet, no mlrig services — except a single forwarded socket (`guestfwd`) that lands on the broker at 127.0.0.1 on mlrig. The umbilical's whole world is one port. The broker holds the only outward connection, over ordinary HTTPS inside `claude -p`. Nothing else changes: QEMU only, the storage bodyguard stays, the plan gate is live.

## The work, in behavioural order

1. Everything Stage 3 proved, kept; serial lines become `S4:`.
2. **The NIC.** Find the virtio-net device on PCI (the stage 3 plumbing generalised: two devices now live on the bus), negotiate modern-only as before, bring up its receive and transmit queues, read the MAC from device config. Log `S4: nic <mac>` (six hex pairs, colon-separated).
3. **The stack, minimal and honest.** Static addressing on slirp's fixed world — guest 10.0.2.15/24, gateway 10.0.2.2 — no DHCP client. ARP: reply and resolve. IPv4 with header checksum. TCP, client-only, one connection at a time: handshake, sequence/acknowledge, a simple retransmit timer, orderly close. No congestion control beyond one-segment-in-flight; no IPv6; no UDP; no DNS — the broker's address is fixed by the cage. Every omission is a recorded decision, not an accident.
4. **The question.** A typed line starting with `? ` is a question, not a note: the text after the marker goes to the broker as one length-prefixed message; the reply is drawn on the console, wrapped, above a fresh prompt. Questions are not saved to the notebook; notes (no marker) behave exactly as Stage 3. While waiting, the console shows a single working indicator; serial carries nothing — the echo contract is unchanged.
5. **The broker.** `broker/broker.py` on mlrig, Python standard library only: listens on 127.0.0.1, speaks the length-prefixed protocol, calls `claude -p <question>` with a timeout, returns the text. A `--mock` mode answers deterministically from a canned table, with no Claude call — the acceptance tests use only the mock; the real backend is exercised by you at test 5. The protocol lives in `stage4/UMBILICAL.md`, byte-exact, like NOTEBOOK.md before it.

## Acceptance tests

Written before the code, frozen behind the hook; the mock broker means the automated gate never spends a token or needs the internet.

1. **Artefact.** PE32+ checks on stage4's binary and image.
2. **Serial.** Fresh boot: Stage 3's lines plus `S4: nic <mac>` in its slot, in order; found = woken = the `-smp` value.
3. **The question round trip.** The harness starts the mock broker, boots the guest, types `? ping` via sendkey. Asserts: the broker received exactly `ping` per UMBILICAL.md; the console screendump shows the mock's canned answer; the serial echo after `keyboard ready` is exactly what was typed and nothing more; the notebook did NOT gain a record. Runs at `-smp 2` and `-smp 8`. A second question in the same boot proves the connection logic survives reuse.
4. **The cage.** The QEMU command in every test carries `restrict=on` with the single guestfwd — asserted by the harness inspecting its own command — and a mock-down run proves failure is a console message (`no answer from the broker`), not a hang or a crash.
5. **Oracle.** You, with the real broker running: boot windowed, ask Claude something true — his word, and Claude's answer on your grown machine's own screen, close the stage.

## Build and run

As Stage 3 from stage4/, plus the network device and the cage:

```
-netdev user,id=n0,restrict=on,guestfwd=tcp:10.0.2.2:9999-tcp:127.0.0.1:9999
-device virtio-net-pci,netdev=n0
```

Broker: `python3 broker/broker.py` (real) or `--mock` (tests). No new packages.

## Decisions recorded at approval (owner, 1 September 2026)

1. **TLS placement.** The guest↔broker link runs plaintext inside the cage this ring — traffic that physically cannot leave mlrig — with TLS to Anthropic in the broker. The pre-built, verified TLS blob joins the guest at the ring where its traffic first touches a real wire (Stage 7), as its own work item. Cryptography is never improvised, per the foundation.
2. **The question marker.** `? ` prefix. Explicit, no hidden modes; notes stay pure.
3. **The stack's omissions.** DHCP, DNS, UDP, IPv6 and congestion control are all out this ring, each a recorded decision.
