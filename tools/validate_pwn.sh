#!/usr/bin/env bash
#
# validate_pwn.sh — Automatisk ende-til-ende-validering av pwn-oppgavene.
#
# Kjør på en x86-64-maskin (eller med Docker/qemu) der binærene kan kjøres native.
#
#   pwn-00 "Retur til vaktbua"  : statisk fil  -> kjører solver mot binæren
#   pwn-01 "Buffer på boden"    : container    -> docker build + run + solver over nc
#
# Bruk:
#   tools/validate_pwn.sh            # validér begge
#   tools/validate_pwn.sh pwn-00     # bare ret2win-fila
#   tools/validate_pwn.sh pwn-01     # bare container-oppgaven
#
# Krav: bash, python3, pwntools (pip install pwntools), docker (kun for pwn-01).
#
set -uo pipefail

# --- Finn repo-rot uansett hvor scriptet kjøres fra ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PWN00_DIR="$ROOT/challenges/pwn-00-retur-vaktbua"
PWN01_DIR="$ROOT/challenges/pwn-01-buffer-boden"

EXPECT_FLAG_00="CTF{ret2win_forste_steg}"
EXPECT_FLAG_01="CTF{buffer_p4_b0den_ret2win}"

PORT=9999
IMAGE="ctf-pwn01-buffer"
CONTAINER="ctf-pwn01-test"

# --- Farger ---
if [ -t 1 ]; then
  R=$'\033[31m'; G=$'\033[32m'; Y=$'\033[33m'; B=$'\033[36m'; N=$'\033[0m'
else
  R=""; G=""; Y=""; B=""; N=""
fi
ok()   { echo "${G}[PASS]${N} $*"; }
fail() { echo "${R}[FAIL]${N} $*"; }
info() { echo "${B}[*]${N} $*"; }
warn() { echo "${Y}[!]${N} $*"; }

RESULT=0

# ------------------------------------------------------------------
need() { command -v "$1" >/dev/null 2>&1; }

check_pwntools() {
  python3 -c "import pwn" >/dev/null 2>&1
}

# ------------------------------------------------------------------
# pwn-00 — statisk ret2win
# ------------------------------------------------------------------
validate_pwn00() {
  echo
  info "=== pwn-00: Retur til vaktbua (statisk fil) ==="
  local bin="$PWN00_DIR/retur_vaktbua"

  if [ ! -f "$bin" ]; then
    fail "Fant ikke binæren: $bin"; RESULT=1; return
  fi

  # Arkitektur-sjekk
  local arch; arch="$(file -b "$bin" | head -1)"
  info "Binær: $arch"
  case "$arch" in
    *x86-64*) : ;;
    *) warn "Binæren er ikke x86-64 — kjør dette på en x86-maskin, ellers feiler exec." ;;
  esac

  # checksec-forventninger (informativt, krever pwntools)
  if check_pwntools; then
    python3 - "$bin" <<'PY' || true
import sys
from pwn import ELF, context
context.log_level = "error"
e = ELF(sys.argv[1], checksec=False)
print(f"    PIE={e.pie}  NX={e.nx}  canary={e.canary}  win@{hex(e.symbols.get('win',0))}")
assert e.pie is False, "PIE burde være av"
assert e.canary is False, "Canary burde være av"
assert "win" in e.symbols, "win-symbol mangler"
PY
  fi

  info "Kjører arrangør-solver mot binæren..."
  local out
  out="$(python3 "$PWN00_DIR/solver/solve.py" "$bin" 2>&1)"
  if echo "$out" | grep -qF "$EXPECT_FLAG_00"; then
    ok "pwn-00 løst — flagg: $EXPECT_FLAG_00"
  else
    fail "pwn-00 ga ikke forventet flagg."
    echo "$out" | sed 's/^/      /'
    RESULT=1
  fi
}

# ------------------------------------------------------------------
# pwn-01 — container + solver over TCP
# ------------------------------------------------------------------
cleanup_pwn01() {
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
}

validate_pwn01() {
  echo
  info "=== pwn-01: Buffer på boden (container) ==="

  if ! need docker; then
    fail "Docker er ikke installert/tilgjengelig — kan ikke validere pwn-01 ende-til-ende."
    RESULT=1; return
  fi
  if ! check_pwntools; then
    fail "pwntools mangler (pip install pwntools) — solveren trenger det."
    RESULT=1; return
  fi

  trap cleanup_pwn01 RETURN
  cleanup_pwn01

  info "Bygger Docker-image ($IMAGE)..."
  if ! docker build -q -t "$IMAGE" "$PWN01_DIR/server" >/dev/null; then
    fail "docker build feilet."; RESULT=1; return
  fi
  ok "Image bygget."

  info "Starter container på port $PORT..."
  if ! docker run -d --rm --name "$CONTAINER" -p "$PORT:9999" "$IMAGE" >/dev/null; then
    fail "docker run feilet."; RESULT=1; return
  fi

  # Vent til tjenesten svarer
  info "Venter på at tjenesten skal svare..."
  local up=0
  for _ in $(seq 1 20); do
    if (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; then exec 3>&- 3<&-; up=1; break; fi
    sleep 0.5
  done
  if [ "$up" -ne 1 ]; then
    fail "Tjenesten svarte ikke på port $PORT."
    docker logs "$CONTAINER" 2>&1 | sed 's/^/      /'
    RESULT=1; return
  fi
  ok "Tjenesten er oppe."

  info "Kjører arrangør-solver mot 127.0.0.1:$PORT..."
  local out
  out="$(python3 "$PWN01_DIR/solver/solve.py" REMOTE 127.0.0.1 "$PORT" 2>&1)"
  if echo "$out" | grep -qF "$EXPECT_FLAG_01"; then
    ok "pwn-01 løst — flagg: $EXPECT_FLAG_01"
  else
    fail "pwn-01 ga ikke forventet flagg."
    echo "$out" | sed 's/^/      /'
    docker logs "$CONTAINER" 2>&1 | tail -20 | sed 's/^/      [container] /'
    RESULT=1
  fi
}

# ------------------------------------------------------------------
main() {
  local target="${1:-all}"

  if ! need python3; then echo "python3 kreves."; exit 2; fi
  if ! check_pwntools; then
    warn "pwntools ikke funnet. Installer med:  pip install pwntools"
  fi

  case "$target" in
    pwn-00|00) validate_pwn00 ;;
    pwn-01|01) validate_pwn01 ;;
    all)       validate_pwn00; validate_pwn01 ;;
    *) echo "Ukjent mål: $target  (bruk: pwn-00 | pwn-01 | all)"; exit 2 ;;
  esac

  echo
  if [ "$RESULT" -eq 0 ]; then
    echo "${G}=== ALLE VALIDERINGER BESTÅTT ===${N}"
  else
    echo "${R}=== NOEN VALIDERINGER FEILET ===${N}"
  fi
  exit "$RESULT"
}

main "$@"
