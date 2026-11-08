#!/usr/bin/env bash
# stage8/mknasm.sh - a private NASM 3.02 for the seed record (not frozen).
#
# SEED.md step 4: a rebuild under another version is no rebuild, and every
# line of seed-record.md names 3.02. Ubuntu's apt has 3.01, which stays the
# daily compiler. This builds 3.02 under stage8/out/toolchain/nasm-3.02/ and
# touches nothing outside it. The proof that it is 3.02 is not this script:
# it is seeds 0, 1 and 2 rebuilding to their recorded hashes under it:
#
#   PATH=stage8/out/toolchain/nasm-3.02/bin:$PATH python3 stage8/parts.py --seed
set -euo pipefail
cd "$(dirname "$0")/.."

VER=3.02
URL="https://www.nasm.us/pub/nasm/releasebuilds/$VER/nasm-$VER.tar.xz"
TOP=stage8/out/toolchain
PREFIX="$PWD/$TOP/nasm-$VER"

if [ -x "$PREFIX/bin/nasm" ]; then
    "$PREFIX/bin/nasm" -v
    echo "mknasm: already built at $TOP/nasm-$VER"
    exit 0
fi

for tool in gcc make xz curl; do
    command -v "$tool" >/dev/null || { echo "mknasm: $tool is missing" >&2; exit 1; }
done

mkdir -p "$TOP/src"
if [ ! -f "$TOP/src/nasm-$VER.tar.xz" ]; then
    curl -fsSL --proto '=https' -o "$TOP/src/nasm-$VER.tar.xz.part" "$URL"
    mv "$TOP/src/nasm-$VER.tar.xz.part" "$TOP/src/nasm-$VER.tar.xz"
fi
sha256sum "$TOP/src/nasm-$VER.tar.xz"

rm -rf "$TOP/src/nasm-$VER"
tar -xJf "$TOP/src/nasm-$VER.tar.xz" -C "$TOP/src"
(
    cd "$TOP/src/nasm-$VER"
    ./configure --prefix="$PREFIX" >/dev/null
    make -j8 nasm >/dev/null
)
mkdir -p "$PREFIX/bin"
cp "$TOP/src/nasm-$VER/nasm" "$PREFIX/bin/nasm"
"$PREFIX/bin/nasm" -v
echo "mknasm: built at $TOP/nasm-$VER"
