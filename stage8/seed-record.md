# seed-record.md — the seeds, one line each

Append-only, by `stage8/SEED.md`'s rules: a line, once committed, is never
changed and never removed, and the witness uses the last line. Each line
names a commit and the SHA-256 of `stage8/out/BOOTX64.EFI` as that
commit's own `stage8/mkimage.sh` builds it in a clean workspace, taken
from the build and never typed. Only the lines inside the fence are read.

- **Seed 0** is ring 8a item 1's commit: `stage8/stage8.asm` copied from `stage7/stage7.asm` byte for byte, a build identical to ring 7d's 45,056-byte binary.
- **Seed 1** is ring 8a item 16b's commit, `fc64a07`: the first commit at which the whole ring 8a gate is green (`./stage8/test-8a.sh`, all four tests, 42.9 min), with `stage8/loader.asm` frozen. Its build is 57,344 bytes. The line was taken at item 17 from a rebuild by SEED.md's recipe (`git archive fc64a07` into an emptied `stage8/out/seed/1/`, that tree's `stage8/mkimage.sh`, NASM 3.02) and written by `parts.seed_line`, never typed.

```
seed 0 bbf80635a83beeca2254ef35aa492306d30224950b4f405b434b900475b28cd5 45056 bd613b3 2026-09-25 nasm 3.02
seed 1 9e81c7b5d24ac363d2d8711e31044a70b4946ff72f1173b429eec6c478fcff77 57344 fc64a07 2026-09-27 nasm 3.02
```
