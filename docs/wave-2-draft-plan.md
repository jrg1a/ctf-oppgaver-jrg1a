# Andre pulje, validerte statiske oppgaver

Denne puljen består av seks statiske oppgaver. De er bygget som egne norske
varianter med Nordverk som fiktivt miljø. Ingen original challengekode eller
originale deltakerfiler er kopiert.

Oppgavene er validert og flyttet inn i hovedoversikten. Generatorer, solvere og
release-eksport er kontrollert. De mest verktøyavhengige oppgavene er i tillegg
testet med vanlige deltakerverktøy: `pdfdetach` for PDF-vedlegg, Sleuth Kit
inne i Debian-container for FAT12-gjenoppretting, og både Vim og Neovim for
makrooppgaven.

## Oversikt

| Slug | Oppgave | Kategori | Poeng | Hovedteknikk | Anslått tid |
|---|---|---|---:|---|---:|
| `crypto-07-skiftkortene` | Skiftkortene | Crypto | 175 | Kjent klartekst og invers permutasjon | 20 til 35 min |
| `crypto-08-gjenbrukt-nokkelstrom` | Samme strøm to ganger | Crypto | 200 | Gjenbrukt XOR nøkkelstrøm | 20 til 40 min |
| `forensics-08-slettet-skiftlogg` | Slettet skiftlogg | Forensics | 200 | Slettet fil i FAT12 | 25 til 45 min |
| `forensics-09-vedlegget-i-pdf` | Vedlegget i rapporten | Forensics | 150 | Innebygd PDF vedlegg | 15 til 30 min |
| `misc-05-radiovakten` | Radiovakten | Misc | 225 | ITA2 og bokstav eller tallmodus | 30 til 50 min |
| `misc-06-registersporet` | Registersporet | Misc | 175 | Repetert Vim makro og registre | 20 til 40 min |

## Inspirasjon

- `Skiftkortene` bygger på den generelle mekanikken i
  [shufflebox fra DownUnderCTF 2024](https://github.com/DownUnderCTF/Challenges_2024_Public/tree/main/beginner/shufflebox).
- `Slettet skiftlogg` er en lokal og enklere variant av filsystemtankegangen i
  [Network Disk Forensics fra DownUnderCTF 2025](https://github.com/DownUnderCTF/Challenges_2025_Public/tree/main/beginner/for_golf_beginner)
  og [Orphan fra BSidesSF 2026](https://github.com/BSidesSF/ctf-2026-release/tree/main/orphan).
- `Radiovakten` bruker samme historiske tegnfamilie som
  [Intercepted Transmissions fra DownUnderCTF 2024](https://github.com/DownUnderCTF/Challenges_2024_Public/tree/main/beginner/intercepted-transmissions),
  men har egen melding, egen generator og en enklere ITA2 strøm.
- `Registersporet` er inspirert av bruk av Vim makroer og registre i
  [As per my last email fra DownUnderCTF 2025](https://github.com/DownUnderCTF/Challenges_2025_Public/tree/main/beginner/vimfu).
- `Samme strøm to ganger` og `Vedlegget i rapporten` er egne varianter av to
  veletablerte CTF mønstre, henholdsvis nøkkelstrømgjenbruk og analyse av
  innebygde PDF objekter.

## Valideringsstatus

1. Generatorene er kjørt på nytt, og artefaktene er deterministiske.
2. Alle seks arrangørsolvere returnerer forventet flagg.
3. PDF-oppgaven er testet med `pdfinfo`, `pdfdetach -list` og
   `pdfdetach -saveall`.
4. FAT12-oppgaven er testet med `file`, `fsstat`, `fls -d`, `icat` og
   `gzip -dc`.
5. Registersporet er replayet i Vim og Neovim med samme registerinnhold.
6. Direkte råflagg er kontrollert i deltakerartefaktene med `rg` og `strings`.
7. Oppgavene er lagt inn i `README.md`, valideringsmanifestet, samlet writeup og
   release-eksport.
