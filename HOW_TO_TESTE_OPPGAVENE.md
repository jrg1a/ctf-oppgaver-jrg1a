# Slik tester du oppgavene lokalt

Guiden dekker lokalt oppsett, gjennomspilling og kontroll av oppgavene.

- Øve som deltaker, uten å se løsninger.
- Verifisere som arrangør at artefakter, containere, flagg og releasepakke
  fungerer.

Kommandoene under kjøres fra repo-roten:

```bash
cd /sti/til/CTF-oppgaver
```

## 1. Første gangs oppsett

Du trenger:

- Docker Desktop, startet og klar.
- Python 3.
- `curl`, `nc` og `ssh`, som normalt finnes på macOS.

Installer Python-avhengigheter i et lokalt miljø:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-organizer.txt
```

Bygg Linux x86_64-binærene som deltakerne skal få:

```bash
./tools/build_linux_binaries.sh
```

Sjekk at de faktisk er Linux x86_64:

```bash
file challenges/re-02-crackme/crackme \
     challenges/re-03-minivm/minivm \
     challenges/pwn-01-buffer-boden/server/buffer
```

Du skal se `ELF 64-bit ... x86-64`, ikke `Mach-O` eller `ARM`.

Lag deltakerpakken:

```bash
python3 tools/export_release.py
```

Dette lager `release/`, der løsningstekst og arrangørfiler er fjernet fra
deltaker-README-ene.

## 2. Øve som deltaker

Bruk `release/` når du vil spille uten spoilers:

```bash
cd release
```

Hver oppgave har en `README.md`. For statiske oppgaver ligger vedleggene i
samme release-mappe. For liveoppgaver må du starte serveren fra originalmappen
under `challenges/`, men lese oppgaveteksten fra `release/`.

Eksempel:

```bash
# Les deltakertekst
less release/web-01-jwt/README.md

# Start server fra arbeidsmappen
docker build -t ctf-web-01 challenges/web-01-jwt/server
docker run --rm --name ctf-web-01 -p 8080:5000 ctf-web-01
```

Åpne deretter `http://127.0.0.1:8080`.

## 3. Statiske oppgaver

Disse trenger ikke Docker for å spilles. Les `release/<oppgave>/README.md` og
jobb med vedleggene.

For arrangør-verifisering kan du kjøre solverne:

```bash
python3 challenges/misc-02-velkomststrom/solver/solve.py
python3 challenges/crypto-01-xor-vakt/solver/solve.py
python3 challenges/osint-01-finn-scenen/solver/solve.py
python3 challenges/stego-01-plakat-ekko/solver/solve.py
python3 challenges/forensics-01-usb-stand/solver/solve.py
python3 challenges/forensics-02-mailspor/solver/solve.py
python3 challenges/network-01-dns-lekkasje/solver/solve.py
python3 challenges/ot-01-modbus-klartekst/solver/solve.py
python3 challenges/re-01-pyc/solver/solve.py
python3 challenges/re-02-crackme/solver/solve.py
python3 challenges/re-03-minivm/solver/solve.py
```

For å teste de nybygde Linux-binærene i et Linux-miljø:

```bash
docker run --rm --platform linux/amd64 \
  -v "$PWD:/work" -w /work gcc:13-bookworm \
  bash -lc 'challenges/re-02-crackme/crackme N0rdverk!?; challenges/re-03-minivm/minivm vm_m4g1c_k3y'
```

## 4. Web og Flask-oppgaver

Alle Flask-containerne lytter internt på `5000`. Lokalt mapper vi dem til
`8080`, som matcher oppgavetekstene.

Kjør én weboppgave om gangen på `8080`:

```bash
docker build -t ctf-oppgave challenges/<oppgave>/server
docker run --rm --name ctf-oppgave -p 8080:5000 ctf-oppgave
```

Åpne `http://127.0.0.1:8080`.

Stopp med `Ctrl+C` hvis du kjører foreground, eller:

```bash
docker rm -f ctf-oppgave
```

### web-01-jwt

```bash
docker build -t ctf-web-01 challenges/web-01-jwt/server
docker run --rm --name ctf-web-01 -p 8080:5000 ctf-web-01
```

Spill:

```text
http://127.0.0.1:8080
guest / guest
```

Arrangør-sjekk:

```bash
python3 challenges/web-01-jwt/solver/solve.py http://127.0.0.1:8080 challenges/web-01-jwt/wordlist.txt
```

### web-02-backup-lekkasje

```bash
docker build -t ctf-web-02 challenges/web-02-backup-lekkasje/server
docker run --rm --name ctf-web-02 -p 8080:5000 ctf-web-02
```

Spill:

```text
http://127.0.0.1:8080
```

Arrangør-sjekk:

```bash
python3 challenges/web-02-backup-lekkasje/solver/solve.py http://127.0.0.1:8080
```

### web-03-not-your-badge

```bash
docker build -t ctf-web-03 challenges/web-03-not-your-badge/server
docker run --rm --name ctf-web-03 -p 8080:5000 ctf-web-03
```

Spill:

```text
http://127.0.0.1:8080
```

Arrangør-sjekk:

```bash
python3 challenges/web-03-not-your-badge/solver/solve.py http://127.0.0.1:8080
```

### password-01-arkivportal

Statisk ZIP/HTML-oppgave.

Spill:

```bash
cd release/password-01-arkivportal
zip2john dist/standarkiv.zip > hash.txt
john --wordlist=dist/passordliste.txt hash.txt
unzip dist/standarkiv.zip
open portal/portal.html
```

Arrangør-sjekk:

```bash
python3 challenges/password-01-arkivportal/solver/solve.py
```

### ot-04-scada-sqli

```bash
docker build -t ctf-ot-04 challenges/ot-04-scada-sqli/server
docker run --rm --name ctf-ot-04 -p 8080:5000 ctf-ot-04
```

Spill:

```text
http://127.0.0.1:8080
```

Arrangør-sjekk:

```bash
python3 challenges/ot-04-scada-sqli/solver/solve.py http://127.0.0.1:8080
```

### ot-05-historian-api

```bash
docker build -t ctf-ot-05 challenges/ot-05-historian-api/server
docker run --rm --name ctf-ot-05 -p 8080:5000 ctf-ot-05
```

Spill:

```text
http://127.0.0.1:8080
```

Arrangør-sjekk:

```bash
python3 challenges/ot-05-historian-api/solver/solve.py http://127.0.0.1:8080
```

## 5. OT- og nettverkstjenester

### ot-02-bop-modbus

Containeren lytter på Modbus TCP port `502` internt. Lokalt bruker vi
`15020` for å unngå problemer med privilegerte porter.

```bash
docker build -t ctf-ot-02 challenges/ot-02-bop-modbus/server
docker run --rm --name ctf-ot-02 -p 15020:502 ctf-ot-02
```

Spill med recon-scriptet:

```bash
python3 challenges/ot-02-bop-modbus/recon_starter.py 127.0.0.1 15020
```

Arrangør-sjekk:

```bash
python3 challenges/ot-02-bop-modbus/solver/solve.py 127.0.0.1 15020
```

Serveren isolerer state per TCP-tilkobling. Etter at solver har hentet flagget,
skal en ny kjøring av `recon_starter.py` fortsatt vise sabotert starttilstand og
tomme flaggregistre.

### ot-03-mqtt

```bash
docker build -t ctf-ot-03 challenges/ot-03-mqtt/server
docker run --rm --name ctf-ot-03 -p 1883:1883 ctf-ot-03
```

Spill med recon-scriptet:

```bash
python3 challenges/ot-03-mqtt/mqtt_recon.py 127.0.0.1 1883
```

Arrangør-sjekk:

```bash
python3 challenges/ot-03-mqtt/solver/solve.py 127.0.0.1 1883
```

## 6. Pwn-oppgaven

Bygg og kjør som `linux/amd64`, spesielt på Apple Silicon:

```bash
docker build --platform linux/amd64 -t ctf-pwn-01 challenges/pwn-01-buffer-boden/server
docker run --platform linux/amd64 --rm --name ctf-pwn-01 -p 9999:9999 ctf-pwn-01
```

Spill:

```bash
nc 127.0.0.1 9999
```

Arrangør-sjekk:

```bash
python3 challenges/pwn-01-buffer-boden/solver/solve.py REMOTE 127.0.0.1 9999
```

Hvis `pwntools` mangler:

```bash
pip install -r requirements-pwn.txt
```

## 7. Servicekontoen

Denne oppgaven er en SSH-basert Linux privilege escalation.

Start:

```bash
docker build -t ctf-servicekontoen -f challenges/linux-01-servicekonto/hosted/Dockerfile challenges/linux-01-servicekonto
docker run --rm --name ctf-servicekontoen-test -d -p 2222:22 ctf-servicekontoen
```

Spill som deltaker:

```bash
ssh ctfplayer@127.0.0.1 -p 2222
```

Passord:

```text
ICS_r0ck5!
```

Inne på serveren:

```bash
cat README.txt
id
find / -perm -4000 -type f 2>/dev/null
base64 /root/flag.txt | base64 -d
```

Arrangør-sjekk uten SSH:

```bash
docker exec ctf-servicekontoen-test stat -c '%A %U %G %n' /usr/bin/base64 /root/flag.txt
docker exec --user ctfplayer ctf-servicekontoen-test bash -lc 'base64 /root/flag.txt | base64 -d'
```

Du skal kunne lese:

```text
CTF{suid_b4se64_reads_r00t}
```

Stopp og rydd:

```bash
docker stop ctf-servicekontoen-test
```

## 8. Byggsjekk av alle Dockerfiles

Kjør dette for å sjekke at alle containeroppgaver bygger som `linux/amd64`:

```bash
for dockerfile in $(find challenges -name Dockerfile | sort); do
  ctx=$(dirname "$dockerfile")
  tag="ctf-buildcheck-$(echo "$ctx" | tr "/" "-" | tr "_" "-"):test"
  echo "==> $ctx"
  docker build --platform linux/amd64 -t "$tag" "$ctx"
done
```

Dette tester build, men ikke nødvendigvis at oppgaven kan løses. Bruk
seksjonene over for runtime-sjekk.

## 9. Release-sjekk før publisering

Kjør:

```bash
./tools/build_linux_binaries.sh
python3 tools/export_release.py
```

Sjekk at releasepakken ikke inneholder løsningstekst:

```bash
rg -n "^## Løsningsvei|^## VM-instruksjonssett|\\*\\*Flagg:\\*\\*" release
```

Hvis kommandoen ikke skriver noe, er det bra.

Sjekk at alle oppgaver kom med:

```bash
find challenges -maxdepth 2 -name CHALLENGE.md | wc -l
find release -maxdepth 2 -name README.md | wc -l
```

Tallene bør være like.

Sjekk at ingen testcontainere står igjen:

```bash
docker ps
```

Stopp enkeltcontainere ved behov:

```bash
docker rm -f <container-navn>
```

## 10. Når du endrer en oppgave

Bruk denne lille rutinen:

```bash
# Hvis oppgaven har gen.py
python3 challenges/<oppgave>/gen.py

# Hvis den har Linux-binær
./tools/build_linux_binaries.sh

# Hvis den har Dockerfile
docker build --platform linux/amd64 -t ctf-test challenges/<oppgave>/server

# Kjør solver/smoke-test
python3 challenges/<oppgave>/solver/solve.py

# Oppdater release
python3 tools/export_release.py
```

For containeroppgaver der solver trenger URL/IP, bruk kommandoene i seksjonene
over.

## 11. Vanlige problemer

**Docker svarer med permission denied på socket**

Docker Desktop er enten ikke startet, eller sandboxen må ha tilgang. Start
Docker Desktop og prøv igjen.

**Porten er opptatt**

Finn prosessen eller bruk en annen host-port:

```bash
docker run --rm -p 18080:5000 ...
python3 challenges/web-02-backup-lekkasje/solver/solve.py http://127.0.0.1:18080
```

**Apple Silicon kjører feil arkitektur**

Bruk `--platform linux/amd64` på pwn og build-sjekker:

```bash
docker build --platform linux/amd64 ...
docker run --platform linux/amd64 ...
```

**Python mangler pakker**

Aktiver venv og installer arrangøravhengigheter:

```bash
source .venv/bin/activate
pip install -r requirements-organizer.txt
```

**Jeg vil bare spille, ikke se løsninger**

Bruk kun `release/` for tekst og vedlegg. Ikke åpne `solver/`, `solution/`,
`gen.py` eller `server/` før du er ferdig.
