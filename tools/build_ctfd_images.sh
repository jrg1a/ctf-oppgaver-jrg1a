#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRY="${REGISTRY:-local}"
PLATFORM="${PLATFORM:-linux/amd64}"

images=(
  "ctf-linux-01-servicekonto|$ROOT/challenges/linux-01-servicekonto|hosted/Dockerfile"
  "ctf-api-01-leverandorregister|$ROOT/challenges/api-01-leverandorregister/server|Dockerfile"
  "ctf-ot-02-bop-modbus|$ROOT/challenges/ot-02-bop-modbus/server|Dockerfile"
  "ctf-ot-03-mqtt|$ROOT/challenges/ot-03-mqtt/server|Dockerfile"
  "ctf-ot-04-scada-sqli|$ROOT/challenges/ot-04-scada-sqli/server|Dockerfile"
  "ctf-ot-05-historian-api|$ROOT/challenges/ot-05-historian-api/server|Dockerfile"
  "ctf-pwn-01-buffer-boden|$ROOT/challenges/pwn-01-buffer-boden/server|Dockerfile"
  "ctf-web-01-jwt|$ROOT/challenges/web-01-jwt/server|Dockerfile"
  "ctf-web-02-backup-lekkasje|$ROOT/challenges/web-02-backup-lekkasje/server|Dockerfile"
  "ctf-web-03-not-your-badge|$ROOT/challenges/web-03-not-your-badge/server|Dockerfile"
)

usage() {
  cat <<'EOF'
Usage: tools/build_ctfd_images.sh [build|push|build-push]

Environment:
  REGISTRY   Registry prefix. Default: local
  PLATFORM   Build platform. Default: linux/amd64

Examples:
  tools/build_ctfd_images.sh build
  REGISTRY=registry.example/ctf tools/build_ctfd_images.sh build-push
  tools/build_ctfd_images.sh push
EOF
}

build_images() {
  for item in "${images[@]}"; do
    IFS='|' read -r name context dockerfile <<<"$item"
    tag="$REGISTRY/$name"
    echo "==> Building $tag from $context/$dockerfile"
    docker buildx build \
      --platform "$PLATFORM" \
      --file "$context/$dockerfile" \
      --tag "$tag" \
      --load \
      "$context"
  done
}

push_images() {
  for item in "${images[@]}"; do
    IFS='|' read -r name _context _dockerfile <<<"$item"
    tag="$REGISTRY/$name"
    echo "==> Pushing $tag"
    docker push "$tag"
  done
}

case "${1:-build}" in
  build)
    build_images
    ;;
  push)
    push_images
    ;;
  build-push)
    build_images
    push_images
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
