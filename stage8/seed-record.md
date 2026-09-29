# seed-record.md — the seeds, one line each

Append-only, by `stage8/SEED.md`'s rules: a line, once committed, is never
changed and never removed, and the witness uses the last line. Each line
names a commit and the SHA-256 of `stage8/out/BOOTX64.EFI` as that
commit's own `stage8/mkimage.sh` builds it in a clean workspace, taken
from the build and never typed. Only the lines inside the fence are read.

- **Seed 0** is ring 8a item 1's commit: `stage8/stage8.asm` copied from `stage7/stage7.asm` byte for byte, a build identical to ring 7d's 45,056-byte binary.
- **Seed 1** is ring 8a item 16b's commit, `fc64a07`: the first commit at which the whole ring 8a gate is green (`./stage8/test-8a.sh`, all four tests, 42.9 min), with `stage8/loader.asm` frozen. Its build is 57,344 bytes. The line was taken at item 17 from a rebuild by SEED.md's recipe (`git archive fc64a07` into an emptied `stage8/out/seed/1/`, that tree's `stage8/mkimage.sh`, NASM 3.02) and written by `parts.seed_line`, never typed.
- **Seed 2** is ring 8t item 12's commit, `93d5f85`: trial two in the seed (`trials/TRIALS2.md`), the first commit at which the whole ring 8t gate is green (`./trials/test-trial2.sh`, all four tests, 65.9 min, ring 8a's gate green inside its test 4). Its build is 61,440 bytes. The line was taken at ring 8t item 13 from a rebuild by SEED.md's recipe (`git archive 93d5f85` into an emptied `stage8/out/seed/2/`, that tree's `stage8/mkimage.sh`, NASM 3.02) and written by `parts.seed_line`, never typed.

```
seed 0 bbf80635a83beeca2254ef35aa492306d30224950b4f405b434b900475b28cd5 45056 bd613b3 2026-09-25 nasm 3.02
seed 1 9e81c7b5d24ac363d2d8711e31044a70b4946ff72f1173b429eec6c478fcff77 57344 fc64a07 2026-09-27 nasm 3.02
seed 2 c221feca2508f7b648afd8b041ff9d34b26c8c3d94a0d0d04f016414228e5105 61440 93d5f85 2026-09-29 nasm 3.02
```
