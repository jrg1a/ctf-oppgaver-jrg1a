#!/usr/bin/env bash
#
# validate_all.sh — Ende-til-ende-validering av HELE CTF-en.
#
# Kjører arrangør-solveren for hver oppgave, starter containere der det trengs,
# og sjekker at det forventede flagget faktisk kommer ut. Bygd for macOS
# (bash 3.2) og Linux. Pwn-binærene kjøres som linux/amd64 (Apple Silicon OK).
#
# Bruk:
#   tools/validate_all.sh                 # alt
#   tools/validate_all.sh static          # bare statiske oppgaver (ingen Docker)
#   tools/validate_all.sh web modbus mqtt # utvalgte typer
#   tools/validate_all.sh ot-02-bop-modbus crypto-01-xor-vakt   # navngitte oppgaver
#   SKIP_DOCKER=1 tools/validate_all.sh   # hopp over alt som krever Docker
#
# Typer: static web modbus mqtt pwn ssh manual
#
# Krav:
#   - python3 + avhengigheter:  pip install -r requirements-organizer.txt
#   - valgfritt: PYTHON_BIN=.venv/bin/python3 PWN_PYTHON_BIN=/path/to/pwn/python
#   - Docker Desktop (for web/modbus/mqtt/pwn/ssh)
#   - sshpass er IKKE nødvendig — ssh-oppgaven verifiseres via `docker exec`.
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CH="$ROOT/challenges"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PWN_PYTHON_BIN="${PWN_PYTHON_BIN:-$PYTHON_BIN}"

# ---------- farger ----------
if [ -t 1 ]; then
  R=$'\033[31m'; G=$'\033[32m'; Y=$'\033[33m'; B=$'\033[36m'; D=$'\033[2m'; N=$'\033[0m'
else R=""; G=""; Y=""; B=""; D=""; N=""; fi
ok()   { echo "${G}[PASS]${N} $*"; }
bad()  { echo "${R}[FAIL]${N} $*"; }
skip() { echo "${Y}[SKIP]${N} $*"; }
info() { echo "${B}[*]${N} $*"; }
sub()  { echo "${D}      $*${N}"; }

PASS=0; FAILED=0; SKIPPED=0
FAIL_NAMES=""

# ---------- portabel timeout ----------
TIMEOUT_BIN=""
if command -v timeout >/dev/null 2>&1; then TIMEOUT_BIN="timeout"
elif command -v gtimeout >/dev/null 2>&1; then TIMEOUT_BIN="gtimeout"; fi

run_to() {   # run_to <sekunder> <cmd...>
  local secs="$1"; shift
  if [ -n "$TIMEOUT_BIN" ]; then
    "$TIMEOUT_BIN" "$secs" "$@"
  else
    "$PYTHON_BIN" "$ROOT/tools/run_with_timeout.py" "$secs" "$@"
  fi
}

have_docker() { command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; }

wait_tcp() {   # wait_tcp host port timeout_s
  local host="$1" port="$2" t="${3:-20}" i=0
  while [ "$i" -lt "$((t*2))" ]; do
    if (exec 3<>"/dev/tcp/$host/$port") 2>/dev/null; then exec 3>&- 3<&-; return 0; fi
    sleep 0.5; i=$((i+1))
  done
  return 1
}

wait_http() {  # wait_http url timeout_s
  local url="$1" t="${2:-30}" i=0
  while [ "$i" -lt "$((t*2))" ]; do
    local code; code="$(curl -s -o /dev/null -w '%{http_code}' "$url" 2>/dev/null)"
    [ "$code" != "000" ] && [ -n "$code" ] && return 0
    sleep 0.5; i=$((i+1))
  done
  return 1
}

# ---------- resultat-hjelpere ----------
report() {  # report <name> <expected_flag> <actual_output>
  local name="$1" expect="$2" out="$3"
  if echo "$out" | grep -qF "$expect"; then
    ok "$name  ->  $expect"; PASS=$((PASS+1))
  else
    bad "$name  (forventet $expect)"
    echo "$out" | tail -6 | sed 's/^/        /'
    FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"
  fi
}

# =========================================================
#  MANIFEST:  name|type|expected_flag|extra
#  type: static web modbus mqtt pwn ssh manual
#  extra: web -> ekstra solver-arg (f.eks. wordlist);  manual -> notat
# =========================================================
MANIFEST='
crypto-01-xor-vakt|static|CTF{xor_v4kt_kr1bbsk1lt}|
crypto-02-skiftprotokoll|static|CTF{rot_med_norsk_alfabet}|
crypto-03-vigenere-beredskap|static|CTF{vigenere_er_fortsatt_klassiker}|
crypto-04-rsa-felles-modulus|static|CTF{rsa_common_modulus_gjor_vondt}|
crypto-05-lcg-sensorstrom|static|CTF{lcg_er_ikke_streamkrypto}|
crypto-06-raymond-rsa|static|CTF{ferm4t_fant_raymonds_primer}|
crypto-07-skiftkortene|static|CTF{samme_permutasjon_hver_gang}|
crypto-08-gjenbrukt-nokkelstrom|static|CTF{aldri_gjenbruk_en_nokkelstrom}|
forensics-01-usb-stand|static|CTF{usb_h1st_sqlite_jaktet}|
forensics-02-mailspor|static|CTF{mail_h3ad3rs_og_m1me}|
forensics-03-stand-pc|static|CTF{historikken_husker_mer}|
forensics-04-brukeragenten|static|CTF{nikto_2.5.0}|
forensics-05-glemt-commit|static|CTF{historikken_husker_alt}|
forensics-06-klippet-limt|static|CTF{blokker_flettet_tre_veier}|
forensics-07-tasteloggen|static|CTF{usb_hid_tastene_husker}|
forensics-08-slettet-skiftlogg|static|CTF{slettet_betyr_ikke_borte}|
forensics-09-vedlegget-i-pdf|static|CTF{pdf_vedlegg_gjemmer_mer}|
password-01-arkivportal|static|CTF{zip_j0hn_b64_portal}|
misc-02-velkomststrom|static|CTF{v3lk0mst_str0m_h1tch3d}|
misc-03-morse-rele|static|CTF{MORSE_PA_RELEET_ER_KLASSIKER}|
misc-04-tonevalg|static|CTF{tone_fra_sentral}|
misc-05-radiovakten|static|CTF{radio_vakten_bytter_modus_73}|
misc-06-registersporet|static|CTF{makroen_samler_spor}|
network-01-dns-lekkasje|static|CTF{dns_l3kkasje_i_subdomener}|
network-02-http-basic|static|CTF{basic_auth_er_bare_base64}|
osint-01-finn-scenen|static|CTF{scene_b_storsalen}|
ot-01-modbus-klartekst|static|CTF{m0dbus_1s_n0t_s3cur3}|
pwn-00-retur-vaktbua|pwnfile|CTF{ret2win_forste_steg}|
re-01-pyc|static|CTF{pyc_r3v3rs3d_4g3nt}|
re-02-crackme|static|CTF{cr4ckm3_r3v3rs3d_ok}|
re-03-minivm|static|CTF{vm_m4g1c_k3y}|
stego-01-plakat-ekko|static|CTF{plakat_3kk0_b4k_1end}|
stego-02-lsb-skilt|static|CTF{lsb_i_bla_kanalen}|
api-01-leverandorregister|web|CTF{api_mass_assignment_i_leverandorportalen}|
web-01-jwt|web|CTF{jwt_w3ak_s3cr3t_f0rg3d}|WORDLIST
web-02-backup-lekkasje|web|CTF{r0b0ts_og_b4ckup_fant}|
web-03-not-your-badge|web|CTF{not_your_badge_1007}|
ot-04-scada-sqli|web|CTF{uni0n_b4sed_sc4d4_pwn3d}|
ot-05-historian-api|web|CTF{h1st0r14n_1d0r_ch41n_c0mpl3t3}|
ot-02-bop-modbus|modbus|CTF{bop_r3st0r3d_bl0w0ut_pr3v3nt3d}|
ot-03-mqtt|mqtt|CTF{mqtt_w1ldcard_cr3d_l3ak}|
pwn-01-buffer-boden|pwn|CTF{buffer_p4_b0den_ret2win}|
linux-01-servicekonto|ssh|CTF{suid_b4se64_reads_r00t}|
'

# =========================================================
#  Type-handlers
# =========================================================
validate_static() {  # name expect extra
  local name="$1" expect="$2"
  local solver="$CH/$name/solver/solve.py"
  [ -f "$solver" ] || { bad "$name  (mangler solver)"; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return; }
  local out; out="$(cd "$ROOT" && run_to 60 "$PYTHON_BIN" "$solver" 2>&1)"
  report "$name" "$expect" "$out"
}

validate_pwnfile() {  # pwn-00: solver execer en Linux x86-64-binær -> kjør i container
  local name="$1" expect="$2"
  local dir="$CH/$name"
  # 1) Native kjøring er bare mulig på Linux x86_64 (binæren er en Linux ELF).
  if [ "$(uname -s)" = "Linux" ] && [ "$(uname -m)" = "x86_64" ]; then
    chmod +x "$dir/$name" 2>/dev/null
    local out; out="$(cd "$ROOT" && run_to 60 "$PYTHON_BIN" "$dir/solver/solve.py" 2>&1)"
    report "$name" "$expect" "$out"; return
  fi
  # 2) Ellers: kjør solveren inne i en linux/amd64-container (binutils for nm + python3)
  have_docker || { skip "$name  (krever Linux x86-64 eller Docker)"; SKIPPED=$((SKIPPED+1)); return; }
  local runner="ctf-val-pwn-runner"
  if ! docker image inspect "$runner" >/dev/null 2>&1; then
    info "$name: bygger hjelpe-image (python+binutils, engangs)..."
    printf 'FROM python:3.11-slim\nRUN apt-get update && apt-get install -y --no-install-recommends binutils && rm -rf /var/lib/apt/lists/*\n' \
      | docker build --platform linux/amd64 -q -t "$runner" - >/dev/null 2>&1 \
      || { bad "$name (kunne ikke bygge hjelpe-image)"; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return; }
  fi
  info "$name: kjører solver i linux/amd64-container..."
  local out; out="$(run_to 60 docker run --rm --platform linux/amd64 \
      -v "$dir:/c" -w /c "$runner" \
      sh -c 'chmod +x retur_vaktbua && python3 solver/solve.py retur_vaktbua' 2>&1)"
  report "$name" "$expect" "$out"
}

validate_web() {  # name expect extra(WORDLIST?)
  local name="$1" expect="$2" extra="${3:-}"
  have_docker || { skip "$name  (Docker utilgjengelig)"; SKIPPED=$((SKIPPED+1)); return; }
  local img="ctf-val-$name" cont="ctf-val-$name"
  docker rm -f "$cont" >/dev/null 2>&1
  info "$name: docker build..."
  if ! docker build -q -t "$img" "$CH/$name/server" >/dev/null 2>/tmp/bld.$$; then
    bad "$name  (build feilet)"; tail -4 /tmp/bld.$$ | sed 's/^/        /'; rm -f /tmp/bld.$$
    FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return
  fi
  rm -f /tmp/bld.$$
  docker run -d --rm --name "$cont" -p 8080:5000 "$img" >/dev/null 2>&1
  if ! wait_http "http://127.0.0.1:8080" 30; then
    bad "$name  (tjenesten svarte ikke på 8080)"; docker logs "$cont" 2>&1 | tail -6 | sed 's/^/        /'
    docker rm -f "$cont" >/dev/null 2>&1; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return
  fi
  local args=( "http://127.0.0.1:8080" )
  [ "$extra" = "WORDLIST" ] && args+=( "$CH/$name/wordlist.txt" )
  local out; out="$(cd "$ROOT" && run_to 60 "$PYTHON_BIN" "$CH/$name/solver/solve.py" "${args[@]}" 2>&1)"
  docker rm -f "$cont" >/dev/null 2>&1
  report "$name" "$expect" "$out"
}

validate_modbus() {  # name expect
  local name="$1" expect="$2"
  have_docker || { skip "$name  (Docker utilgjengelig)"; SKIPPED=$((SKIPPED+1)); return; }
  local cont="ctf-val-$name"
  docker rm -f "$cont" >/dev/null 2>&1
  info "$name: docker build + run (15020:502)..."
  docker build -q -t "ctf-val-$name" "$CH/$name/server" >/dev/null 2>&1 || { bad "$name (build feilet)"; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return; }
  docker run -d --rm --name "$cont" -p 15020:502 "ctf-val-$name" >/dev/null 2>&1
  wait_tcp 127.0.0.1 15020 20 || { bad "$name (port 15020 svarte ikke)"; docker rm -f "$cont" >/dev/null 2>&1; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return; }
  local out; out="$(run_to 40 "$PYTHON_BIN" "$CH/$name/solver/solve.py" 127.0.0.1 15020 2>&1)"
  docker rm -f "$cont" >/dev/null 2>&1
  report "$name" "$expect" "$out"
}

validate_mqtt() {  # name expect
  local name="$1" expect="$2"
  have_docker || { skip "$name  (Docker utilgjengelig)"; SKIPPED=$((SKIPPED+1)); return; }
  local cont="ctf-val-$name"
  docker rm -f "$cont" >/dev/null 2>&1
  info "$name: docker build + run (1883:1883)..."
  docker build -q -t "ctf-val-$name" "$CH/$name/server" >/dev/null 2>&1 || { bad "$name (build feilet)"; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return; }
  docker run -d --rm --name "$cont" -p 1883:1883 "ctf-val-$name" >/dev/null 2>&1
  wait_tcp 127.0.0.1 1883 20 || { bad "$name (port 1883 svarte ikke)"; docker rm -f "$cont" >/dev/null 2>&1; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return; }
  sleep 5   # la publisher komme i gang
  local out; out="$(run_to 50 "$PYTHON_BIN" "$CH/$name/solver/solve.py" 127.0.0.1 1883 2>&1)"
  docker rm -f "$cont" >/dev/null 2>&1
  report "$name" "$expect" "$out"
}

validate_pwn() {  # name expect (pwn-01, amd64)
  local name="$1" expect="$2"
  have_docker || { skip "$name  (Docker utilgjengelig)"; SKIPPED=$((SKIPPED+1)); return; }
  local cont="ctf-val-$name"
  docker rm -f "$cont" >/dev/null 2>&1
  info "$name: docker build + run (9999, linux/amd64)..."
  docker build --platform linux/amd64 -q -t "ctf-val-$name" "$CH/$name/server" >/dev/null 2>&1 || { bad "$name (build feilet)"; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return; }
  docker run -d --rm --platform linux/amd64 --name "$cont" -p 9999:9999 "ctf-val-$name" >/dev/null 2>&1
  wait_tcp 127.0.0.1 9999 20 || { bad "$name (port 9999 svarte ikke)"; docker rm -f "$cont" >/dev/null 2>&1; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return; }
  local out; out="$(run_to 60 "$PWN_PYTHON_BIN" "$CH/$name/solver/solve.py" REMOTE 127.0.0.1 9999 2>&1)"
  docker rm -f "$cont" >/dev/null 2>&1
  report "$name" "$expect" "$out"
}

validate_ssh() {  # linux-01-servicekonto: verifiser via docker exec
  local name="$1" expect="$2"
  have_docker || { skip "$name  (Docker utilgjengelig)"; SKIPPED=$((SKIPPED+1)); return; }
  local cont="ctf-val-$name"
  docker rm -f "$cont" >/dev/null 2>&1
  info "$name: docker build (hosted) + run (2222:22)..."
  docker build -q -t "ctf-val-$name" -f "$CH/$name/hosted/Dockerfile" "$CH/$name" >/dev/null 2>&1 || { bad "$name (build feilet)"; FAILED=$((FAILED+1)); FAIL_NAMES="$FAIL_NAMES $name"; return; }
  docker run -d --rm --name "$cont" -p 2222:22 "ctf-val-$name" >/dev/null 2>&1
  sleep 3
  # SUID-base64 priv-esc: les root-flagget som ctfplayer
  local out; out="$(docker exec --user ctfplayer "$cont" bash -lc 'base64 /root/flag.txt | base64 -d' 2>&1)"
  docker rm -f "$cont" >/dev/null 2>&1
  report "$name" "$expect" "$out"
}

validate_manual() {  # name expect note
  local name="$1" expect="$2" note="${3:-}"
  skip "$name  (manuell sjekk) — forventet $expect"
  [ -n "$note" ] && sub "$note"
  SKIPPED=$((SKIPPED+1))
}

dispatch() {  # name type expect extra
  case "$2" in
    static)  validate_static   "$1" "$3" "$4" ;;
    pwnfile) validate_pwnfile  "$1" "$3" ;;
    web)     validate_web      "$1" "$3" "$4" ;;
    modbus) validate_modbus "$1" "$3" ;;
    mqtt)   validate_mqtt   "$1" "$3" ;;
    pwn)    validate_pwn    "$1" "$3" ;;
    ssh)    validate_ssh    "$1" "$3" ;;
    manual) validate_manual "$1" "$3" "$4" ;;
    *) bad "$1 (ukjent type $2)" ;;
  esac
}

# =========================================================
#  Argument-filter: ingen=alt, ellers typer og/eller navn
# =========================================================
want() {  # want <name> <type>  -> 0 hvis skal kjøres
  if [ ${#FILTERS[@]} -eq 0 ]; then return 0; fi
  local f
  for f in "${FILTERS[@]}"; do
    [ "$f" = "$1" ] && return 0
    [ "$f" = "$2" ] && return 0
    [ "$f" = "pwn" ] && [ "$2" = "pwnfile" ] && return 0
  done
  return 1
}

# --- Kjør uten pipe slik at tellerne overlever (pipe lager subshell i bash 3.2) ---
run_all() {
  FILTERS=( "$@" )
  command -v "$PYTHON_BIN" >/dev/null 2>&1 || { echo "$PYTHON_BIN kreves"; exit 2; }
  [ "${SKIP_DOCKER:-0}" = "1" ] && info "SKIP_DOCKER=1 — hopper over Docker-oppgaver"
  echo "${B}====== CTF-oppgaver — validering ======${N}"

  local line name type expect extra
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    name="${line%%|*}"; rest="${line#*|}"
    type="${rest%%|*}"; rest="${rest#*|}"
    expect="${rest%%|*}"; extra="${rest#*|}"
    want "$name" "$type" || continue
    if [ "${SKIP_DOCKER:-0}" = "1" ] && [ "$type" != "static" ] && [ "$type" != "manual" ]; then
      skip "$name  (Docker hoppet over)"; SKIPPED=$((SKIPPED+1)); continue
    fi
    dispatch "$name" "$type" "$expect" "$extra"
  done <<EOF
$(echo "$MANIFEST")
EOF

  echo
  echo "${B}====== OPPSUMMERING ======${N}"
  echo "  ${G}Bestått: $PASS${N}   ${R}Feilet: $FAILED${N}   ${Y}Hoppet over: $SKIPPED${N}"
  [ -n "$FAIL_NAMES" ] && echo "  ${R}Feilet:${N}$FAIL_NAMES"
  [ "$FAILED" -eq 0 ] && { echo "${G}Alle kjørte valideringer bestått.${N}"; exit 0; } || exit 1
}

run_all "$@"
