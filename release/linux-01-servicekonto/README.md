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
