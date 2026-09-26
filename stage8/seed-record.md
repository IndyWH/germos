# seed-record.md — the seeds, one line each

Append-only, by `stage8/SEED.md`'s rules: a line, once committed, is never
changed and never removed, and the witness uses the last line. Each line
names a commit and the SHA-256 of `stage8/out/BOOTX64.EFI` as that
commit's own `stage8/mkimage.sh` builds it in a clean workspace, taken
from the build and never typed. Only the lines inside the fence are read.

- **Seed 0** is ring 8a item 1's commit: `stage8/stage8.asm` copied from `stage7/stage7.asm` byte for byte, a build identical to ring 7d's 45,056-byte binary.

```
seed 0 bbf80635a83beeca2254ef35aa492306d30224950b4f405b434b900475b28cd5 45056 bd613b3 2026-09-25 nasm 3.02
```
