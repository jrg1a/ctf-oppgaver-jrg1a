# Nye oppgaveideer

Forslagene under passer som statiske oppgaver og krever ingen delt tjeneste.
De bør få egne artefakter, norsk oppgavetekst, generator, solver og
løsningsforklaring før de publiseres.

## Forslag

| Oppgave | Kategori | Nivå | Idé |
|---|---|---|---|
| Lokalbrukeren | Forensics | Medium | Analyser SAM- og SYSTEM-filer, hent én NTLM-hash og knekk et svakt passord. |
| Frekvensalfabetet | Misc | Medium | Bruk kalibreringstoner til å dekode en melding i en WAV-fil. |
| To bilder samtidig | Forensics | Medium | Skill to bilder som er flettet sammen bytevis eller linjevis. |
| Delvis QR | Stego | Lett / medium | Sett sammen flere ufullstendige QR-bilder for å hente meldingen. |
| Minnefragmentet | Forensics | Medium | Finn en prosess, kommando eller nøkkel i et lite minneuttrekk. |
| PCAP med filoverføring | Network | Lett / medium | Rekonstruer en fil over FTP, SMB eller ukryptert HTTP. |

## Krav

- Oppgaven skal kunne løses med dokumenterte og tilgjengelige verktøy.
- Løsningsstien skal være deterministisk og ikke avhenge av gjetting.
- Vedlegg skal ikke inneholde flagget som lesbar tekst med mindre det er
  tilsiktet.
- Artefakter skal testes på nytt etter at de er eksportert til `release/`.
- Ekstern kode og ferdige artefakter skal bare brukes når lisensen tillater
  det. Inspirasjonskilden skal oppgis i arrangørdokumentasjonen.

## Kilder til inspirasjon

Disse arkivene inneholder offentlige CTF-oppgaver og løsningsforklaringer:

- [DownUnderCTF 2024](https://github.com/DownUnderCTF/Challenges_2024_Public)
- [DownUnderCTF 2025](https://github.com/DownUnderCTF/Challenges_2025_Public)
- [BSidesSF 2026](https://github.com/BSidesSF/ctf-2026-release)
- [IrisCTF 2025](https://github.com/IrisSec/IrisCTF-2025-Challenges)
- [Google CTF](https://github.com/google/google-ctf)
- [RITSEC CTF 2019](https://github.com/ritsec/RITSEC-CTF-2019)
- [picoCTF 2019-eksempler](https://github.com/picoCTF/picoCTF-2019-example-problems)

Et offentlig repository er ikke nødvendigvis fritt lisensiert. Kontroller
lisensen før kode eller artefakter gjenbrukes. Det er normalt tryggest å lage
egne filer rundt den samme faglige teknikken.
