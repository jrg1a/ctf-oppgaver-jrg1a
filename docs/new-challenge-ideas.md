# Nye oppgaveideer

Dette dokumentet er en kuratert backlogg for en CTF på omtrent tre timer.
Første prioritet er klassiske, statiske oppgaver som kan lastes ned fra CTFd og
løses lokalt uten en delt container eller en ekstern konto.

## Prinsipp for gjenbruk

Vi gjenbruker oppgaveideen og den faglige mekanikken, ikke flagg, historier
eller ferdige deltakerfiler. Hver oppgave skal få:

- egen norsk tekst og eget fiktivt miljø
- egne genererte artefakter og flagg i formatet `CTF{...}`
- dokumentert inspirasjonskilde og kontrollert lisens
- generator, validator og detaljert arrangørwriteup
- minst én deterministisk løsningssti med vanlige CTF-verktøy

Et offentlig GitHub-repository er ikke automatisk fritt lisensiert. Kode eller
artefakter kopieres derfor bare når lisensen uttrykkelig tillater det. Å bygge
en ny oppgave rundt samme generelle teknikk er som regel både tryggere og
bedre tilpasset deltakerne.

## Kildekontroll

Kildene er kontrollert før videre arbeid. Statusen under gjelder direkte
gjenbruk av kode og artefakter, ikke generelle faglige ideer som PCAP-analyse,
DTMF eller Git-historikk.

| Kilde | Lisensstatus | Hvordan vi bruker den |
|---|---|---|
| [DownUnderCTF 2024](https://github.com/DownUnderCTF/Challenges_2024_Public) | Ingen eksplisitt lisens funnet | Idéinspirasjon. Vi lager all kode og alle deltakerfiler selv. |
| [DownUnderCTF 2025](https://github.com/DownUnderCTF/Challenges_2025_Public) | Ingen eksplisitt lisens funnet | Idéinspirasjon. Vi lager all kode og alle deltakerfiler selv. |
| [BSidesSF 2026](https://github.com/BSidesSF/ctf-2026-release) | README sier at arkivet er utgitt uten lisens | Idéinspirasjon, ikke direkte kopiering. |
| [IrisCTF 2025](https://github.com/IrisSec/IrisCTF-2025-Challenges) | MIT | Kan tilpasses med bevart lisens- og opphavsmerknad. Egne artefakter foretrekkes fortsatt. |
| [My CTF Challenges](https://github.com/sahuang/my-ctf-challenges) | MIT | Kan tilpasses med bevart lisens- og opphavsmerknad. |
| [CTFd Challenge Assets](https://github.com/zachflower/ctfd-challenge-assets) | MIT | Egnet som referanse for helt enkle introduksjonsoppgaver. |
| [Google CTF](https://github.com/google/google-ctf) | Apache 2.0 | Juridisk ryddig, men de fleste oppgavene er for avanserte for første pulje. |
| [RITSEC CTF 2019](https://github.com/ritsec/RITSEC-CTF-2019) | GPLv3 | Kan brukes, men copyleft gjør direkte gjenbruk mindre praktisk i denne samlingen. |
| [picoCTF 2019-eksempler](https://github.com/picoCTF/picoCTF-2019-example-problems) | Ingen eksplisitt lisens funnet | Idéinspirasjon, ikke direkte kopiering. |

## Besluttet byggerekkefølge

Første bølge bør gi nye ferdigheter uten å gjenta de 32 eksisterende
oppgavene. Alle fem er statiske, kan løses lokalt og skal genereres fra bunnen
av i dette repoet.

| Rekkefølge | Oppgave | Begrunnelse |
|---:|---|---|
| 1 | Brukeragenten | Kort og tydelig Wireshark-oppgave som gir en trygg inngang til PCAP-analyse. |
| 2 | Tonevalg | Første lydoppgave i samlingen, med en deterministisk DTMF-løsningssti. |
| 3 | Det glemte committet | Lærer praktisk Git-forensics uten nettjeneste eller ekstern konto. |
| 4 | Klippet og limt | Robust binær rekonstruksjon som kan erstatte mer skjør bilde-stego. |
| 5 | Tasteloggen | Egen USB HID-PCAP inspirert av MIT-lisensierte `deldeldel` fra IrisCTF 2025. |

Andre bølge er `Skiftkortene`, `Slettet skiftlogg` og `Tallknuseren`.
`Makroen husker` utsettes til vi har en pålitelig XLSM-generator og har testet
statisk analyse på både Kali og vanlig Linux. `Radiovakten` beholdes som en
senere mediumoppgave fordi kodetabellen og skifttegnene gir høyere tidsbruk.

## Anbefalt første pulje

| Prioritet | Arbeidstittel | Kategori | Poeng | Artefakt | Anslått tid |
|---:|---|---|---:|---|---:|
| 1 | Brukeragenten | Forensics | 100 | PCAP | 10-20 min |
| 2 | Tonevalg | Misc | 125 | WAV | 15-25 min |
| 3 | Det glemte committet | Forensics | 150 | Git-repository i ZIP | 15-30 min |
| 4 | Skiftkortene | Crypto | 175 | Tekstfil | 20-35 min |
| 5 | Slettet skiftlogg | Forensics | 175 | FAT-diskbilde | 25-40 min |
| 6 | Tallknuseren | Reverse Engineering | 200 | x86-64 ELF | 25-45 min |
| 7 | Klippet og limt | Stego / Forensics | 200 | Binærfil med PNG-data | 30-45 min |
| 8 | Makroen husker | Forensics | 225 | XLSM | 30-50 min |
| 9 | Gjenbrukt nøkkelstrøm | Crypto | 225 | To chiffertekster | 30-50 min |
| 10 | Radiovakten | Misc / Crypto | 250 | Bitstrøm | 40-60 min |

### 1. Brukeragenten

**Idé:** En PCAP inneholder vanlig nettlesertrafikk og en kort skanning mot en
intern webserver. Deltakeren skal identifisere verktøyet og versjonen fra en
avvikende HTTP `User-Agent`, og levere for eksempel
`CTF{nikto_2.1.6}`.

**Klassisk løsningssti:** Åpne filen i Wireshark, filtrer på
`http.user_agent`, sammenlign verdiene og inspiser den avvikende forespørselen.
`tshark -r capture.pcapng -Y http.user_agent -T fields -e http.user_agent`
skal være en like gyldig terminalbasert metode.

**Hvorfor den passer:** Oppgaven lærer filtrering og protokollfelter uten å
kreve at deltakeren kjenner et skjult filnavn. Den er inspirert av
[Baby's First Forensics fra DownUnderCTF 2024](https://github.com/DownUnderCTF/Challenges_2024_Public/tree/main/forensics/babys-first-forensics),
men PCAP-en bygges fra bunnen av med vår egen trafikk.

### 2. Tonevalg

**Idé:** En WAV-fil inneholder DTMF-toner. De første tonene gir et kort nummer
eller en bokstavsekvens. Resultatet leder til en enkel sluttdekoding, for
eksempel tastaturbokstaver eller ASCII-siffer.

**Klassisk løsningssti:** Inspiser lydfilen i Audacity eller med et DTMF-verktøy,
identifiser frekvensparene og slå dem opp i DTMF-tabellen. Et tydelig kalibrerings-
eller eksempelparti i starten hindrer ren gjetting.

**Hvorfor den passer:** Lydforensics mangler i samlingen, og resultatet er
deterministisk. Konseptet er inspirert av
[Down To Modulate Frequencies! fra DownUnderCTF 2025](https://github.com/DownUnderCTF/Challenges_2025_Public/tree/main/beginner/dtmf).

### 3. Det glemte committet

**Idé:** Deltakeren får et lite Git-repository pakket som ZIP. En hemmelighet
ble fjernet fra siste versjon, men ligger i historikken. Støyen består av noen
realistiske commits, branches og en slettet konfigurasjonsfil.

**Klassisk løsningssti:** Bruk `git log --all --oneline`, `git show` og eventuelt
`git diff` for å finne når filen ble fjernet. Ingen nettjeneste eller GitHub-
konto er nødvendig.

**Hvorfor den passer:** Dette beholder læringsverdien fra en OSINT-oppgave om
gamle commits, men gjør oppgaven stabil og helt lokal.

### 4. Skiftkortene

**Idé:** En ukjent permutasjon stokker alle tegnposisjonene i blokker med fast
lengde. To kjente inn- og ut-par gjør det mulig å finne permutasjonen entydig.
Den samme permutasjonen er brukt på en tredje, ukjent melding med flagget.

**Klassisk løsningssti:** Sammenlign posisjoner i de kjente parene, bygg den
inverse permutasjonen og bruk den på flaggblokken. CyberChef kan hjelpe med
første inspeksjon, men et kort Python-skript er naturlig når rekkefølgen skal
anvendes systematisk.

**Hvorfor den passer:** Dette introduserer transposisjonskrypto uten
frekvensgjetting. Konseptet er inspirert av
[shufflebox fra DownUnderCTF 2024](https://github.com/DownUnderCTF/Challenges_2024_Public/tree/main/beginner/shufflebox),
som hadde 582 løsninger og var klassifisert som en nybegynneroppgave.

### 5. Slettet skiftlogg

**Idé:** Et lite FAT-diskbilde inneholder vanlige dokumenter og én slettet fil.
Flagget ligger i den slettede filen, gjerne sammen med en distraksjon som ser
ut som et flagg, men har feil format eller kontrollsum.

**Klassisk løsningssti:** Identifiser filsystemet med `file`, list slettede
oppføringer med Autopsy eller `fls`, og hent riktig inode med `icat`. `strings`
kan gi et spor, men bør ikke alene returnere hele flagget.

**Hvorfor den passer:** Dette er klassisk filsystemforensics. Varianten er
inspirert av [Orphan fra BSidesSF 2026](https://github.com/BSidesSF/ctf-2026-release/tree/main/orphan),
men FAT og en vanlig slettet fil gir en snillere og mer plattformvennlig oppgave
enn originalens ulenkede inode i ext2.

### 6. Tallknuseren

**Idé:** Et lite x86-64-program ber om to heltall. Valideringen ser umulig ut,
men en signed/unsigned-konvertering eller 32-bits overflow gjør at ett bestemt
inputpar passerer. Riktig input dekoder et innebygd, lett obfuskert flagg, slik
at oppgaven fungerer helt lokalt.

**Klassisk løsningssti:** Kjør `file` og `checksec`, åpne binæren i Ghidra eller
Cutter, finn inputkontrollen og legg merke til bredden og fortegnet på heltallene.
Bekreft kandidatverdiene ved å kjøre programmet. Flagget skal ikke kunne hentes
direkte med `strings`.

**Hvorfor den passer:** Dette er en kompakt introduksjon til dekompilering og
heltallsrepresentasjon. Konseptet er inspirert av
[number mashing fra DownUnderCTF 2024](https://github.com/DownUnderCTF/Challenges_2024_Public/tree/main/beginner/number-mashing),
men vi bygger en egen x86-64-binær som ikke trenger server eller ekstern
`flag.txt`.

### 7. Klippet og limt

**Idé:** Tre små PNG-filer er delt i like store blokker og lagt annenhver gang
i én binærfil. Hvert bilde inneholder en del av flagget. Blokkstørrelsen kan
antydes gjennom filstørrelse, repeterende PNG-signaturer eller et rimelig hint.

**Klassisk løsningssti:** Bruk `xxd`, `binwalk` eller et kort Python-skript til
å fordele blokk 0, 3, 6 til første fil, blokk 1, 4, 7 til andre fil og så videre.
Her er et lite skript en naturlig del av oppgaven fordi selve utfordringen er
å forstå og reversere datastrukturen.

**Hvorfor den passer:** Dette er en robust erstatning for stego som avhenger av
skjøre bildeverktøy. Konseptet er inspirert av
[scrapbooking fra DownUnderCTF 2025](https://github.com/DownUnderCTF/Challenges_2025_Public/tree/main/misc/scrapbooking).

### 8. Makroen husker

**Idé:** En XLSM-fil inneholder en deaktivert makro som bygger en kodet streng
fra flere celler. Deltakeren skal ikke kjøre makroen, men analysere den statisk.
Dekodingen bør bestå av én kjent operasjon, for eksempel Base64 etter at
strengbitene er satt i riktig rekkefølge.

**Klassisk løsningssti:** Kjør `olevba dokument.xlsm`, les VBA-koden, følg
strengbyggingen og dekod sluttverdien med `base64 -d` eller CyberChef.

**Hvorfor den passer:** Oppgaven introduserer dokumentforensics og trygg
makroanalyse. Den er en nedskalert variant av
[Macro Magic fra DownUnderCTF 2024](https://github.com/DownUnderCTF/Challenges_2024_Public/tree/main/forensics/macromagic),
uten den ekstra PCAP-delen.

### 9. Gjenbrukt nøkkelstrøm

**Idé:** To meldinger er kryptert med samme XOR-nøkkelstrøm. Den ene har en
kjent eller sterkt forutsigbar innledning, slik at deltakeren kan hente ut nok
av nøkkelstrømmen til å dekryptere den andre.

**Klassisk løsningssti:** XOR chiffertekstene, bruk det oppgitte crib-et og
arbeid videre i CyberChef, `xorsearch` eller et kort lokalt skript. Writeupen
skal forklare hvorfor `C1 XOR C2` fjerner nøkkelstrømmen.

**Hvorfor den passer:** Samlingen har klassiske substitusjoner og RSA, men
mangler nonce- eller nøkkelgjenbruk. Oppgaven gir et tydelig kryptografisk
poeng uten store tall eller server.

### 10. Radiovakten

**Idé:** En tekstfil inneholder en bitstrøm kodet med Baudot eller CCIR 476.
Meldingen bruker både bokstav- og tallmodus, slik at deltakeren må forstå
skifttegnene og ikke bare gjøre en enkel tabelloppslag.

**Klassisk løsningssti:** Finn riktig tegnbredde fra mønsteret, del bitstrømmen
i grupper, identifiser kontroll- og skifttegn og dekod med en tabell eller et
kort skript.

**Hvorfor den passer:** Den gir en ordentlig mediumoppgave innen signaler og
encoding. Konseptet er inspirert av
[Intercepted Transmissions fra DownUnderCTF 2024](https://github.com/DownUnderCTF/Challenges_2024_Public/tree/main/beginner/intercepted-transmissions).

## Gode reserveideer

| Arbeidstittel | Kategori | Vanskelighet | Kommentar |
|---|---|---|---|
| Lokalbrukeren | Forensics | Medium | SAM- og SYSTEM-filer, dump og crack én svak NTLM-hash. Inspirert av [SAM I AM](https://github.com/DownUnderCTF/Challenges_2024_Public/tree/main/forensics/samiam). Krever mer testdata og større verktøyterskel. |
| Frekvensalfabetet | Misc | Medium | WAV med kalibreringstoner A-Z og deretter skjult melding. Inspirert av [BeepBeep](https://github.com/DownUnderCTF/Challenges_2025_Public/tree/main/misc/beepbeep). Mer arbeid og høyere matte-/verktøyterskel enn DTMF. |
| To bilder samtidig | Stego | Medium | To PNG-filer ligger bytevis og linjevis flettet. Inspirert av [Seeing Double](https://github.com/BSidesSF/ctf-2026-release/tree/main/seeing-double). Velg denne eller Klippet og limt, ikke begge i samme korte CTF. |
| Vedlegget i PDF-en | Forensics | Lett | PDF med metadata, innebygd vedlegg og en slettet kommentar. Fin introduksjon til `pdfinfo`, `pdfdetach` og `exiftool`. |
| Delvis QR | Stego | Lett / medium | Flere ufullstendige QR-bilder må legges oppå hverandre eller XOR-es. Må valideres med flere QR-lesere for å unngå den tidligere stego-feilen. |

## Oppgaver vi foreløpig bør styre unna

- Live OSINT som avhenger av X, GitLab, Discord eller en annen ekstern konto.
- Oppgaver som krever en spesialpatchet dekoder eller en bestemt gammel
  bibliotekversjon.
- Delte tilstandsfulle tjenester der én deltaker kan endre løsningen for andre.
- Esolang-oppgaver der hovedvanskeligheten er å gjette hvilket obskurt språk
  som er brukt.
- Flere nesten like bilde- eller arkivoppgaver i samme tre timers konkurranse.

Eksempler på interessante, men for spesialiserte oppgaver er Image Progress og
CDImage i [BSidesSF 2026-arkivet](https://github.com/BSidesSF/ctf-2026-release).
[Google CTF-arkivet](https://github.com/google/google-ctf) er omfattende og
Apache 2.0-lisensiert, men mange av tjenestene inneholder tilsiktede sårbarheter
og skal ikke kjøres direkte på produksjonsinfrastruktur. Det egner seg bedre som
idébank for en senere, mer avansert pulje.

## Kildearkiver

- [DownUnderCTF 2024, filer og offisielle løsninger](https://github.com/DownUnderCTF/Challenges_2024_Public)
- [DownUnderCTF 2025, filer og offisielle løsninger](https://github.com/DownUnderCTF/Challenges_2025_Public)
- [BSidesSF 2026 release](https://github.com/BSidesSF/ctf-2026-release)
- [Google CTF, 2017 til 2025](https://github.com/google/google-ctf)
- [RITSEC CTF 2019](https://github.com/ritsec/RITSEC-CTF-2019)
- [picoCTF 2019 example problems](https://github.com/picoCTF/picoCTF-2019-example-problems)
