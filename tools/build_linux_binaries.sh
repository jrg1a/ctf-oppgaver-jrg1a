#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cat <<'MSG'
Building participant binaries as Linux x86_64.

Requires Docker Desktop/daemon and the gcc:13-bookworm image.
If the image is not present locally, Docker will pull it.
MSG

docker run --rm --platform linux/amd64 \
  -v "$ROOT:/work" \
  -w /work \
  gcc:13-bookworm \
  bash -lc '
set -euo pipefail

gcc -s -O1 -o challenges/re-02-crackme/crackme challenges/re-02-crackme/crackme.c
gcc -s -O1 -o challenges/re-03-minivm/minivm challenges/re-03-minivm/minivm.c
gcc -fno-stack-protector -no-pie -m64 -O0 \
  -o challenges/pwn-00-retur-vaktbua/retur_vaktbua \
  challenges/pwn-00-retur-vaktbua/retur_vaktbua.c
gcc -fno-stack-protector -no-pie -m64 -O0 \
  -o challenges/pwn-01-buffer-boden/server/buffer \
  challenges/pwn-01-buffer-boden/server/buffer.c

file challenges/re-02-crackme/crackme \
     challenges/re-03-minivm/minivm \
     challenges/pwn-00-retur-vaktbua/retur_vaktbua \
     challenges/pwn-01-buffer-boden/server/buffer
'
