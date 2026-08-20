# CTF-oppgaver

En gjenbrukbar samling norske CTF-oppgaver innen krypto, forensics, web,
reversering, pwn, nettverk, stego, Linux og OT/ICS.

Oppgavene bruker et fiktivt miljø kalt **Nordverk** og flaggformatet
`CTF{...}`. Repoet er laget for arrangører og inneholder derfor flagg,
serverkode, generatorer, solvere og løsningsforklaringer. Hold repoet privat
mens en konkurranse pågår.

## Oppgaver

| Slug | Oppgave | Kategori | Poeng | Type |
|---|---|---|---:|---|
| `misc-02-velkomststrom` | Velkomststrøm | Misc | 50 | Statisk tekst |
| `crypto-02-skiftprotokoll` | Skiftprotokollen | Crypto | 75 | Statisk fil |
| `osint-01-finn-scenen` | Finn scenen | OSINT | 75 | Statisk kildejakt |
| `crypto-01-xor-vakt` | Vaktnotatet | Crypto | 100 | Statisk fil |
| `forensics-04-brukeragenten` | Brukeragenten | Forensics | 100 | Statisk PCAP |
| `misc-03-morse-rele` | Morse på releet | Misc | 100 | Statisk CSV |
| `ot-01-modbus-klartekst` | Modbus i klartekst | OT / ICS | 100 | Statisk PCAP |
| `pwn-00-retur-vaktbua` | Retur til vaktbua | Pwn | 100 | Statisk ELF |
| `stego-01-plakat-ekko` | Plakat med ekko | Stego | 100 | Statisk PNG |
| `misc-04-tonevalg` | Tonevalg | Misc | 125 | Statisk WAV |
| `network-01-dns-lekkasje` | DNS i sidesporet | Network | 125 | Statisk PCAP |
| `web-03-not-your-badge` | Not Your Badge | Web | 125 | Flask-container |
| `crypto-03-vigenere-beredskap` | Beredskapsfrasen | Crypto | 150 | Statisk fil |
| `forensics-01-usb-stand` | USB fra standen | Forensics | 150 | Statisk ZIP |
| `forensics-02-mailspor` | Mailspor | Forensics | 150 | Statisk EML |
| `forensics-05-glemt-commit` | Det glemte committet | Forensics | 150 | Statisk Git i ZIP |
| `forensics-09-vedlegget-i-pdf` | Vedlegget i rapporten | Forensics | 150 | Statisk PDF |
| `re-01-pyc` | Python-spionen | Reverse Engineering | 150 | Statisk PYC |
| `web-02-backup-lekkasje` | Backup-lekkasje | Web | 150 | Flask-container |
| `crypto-07-skiftkortene` | Skiftkortene | Crypto | 175 | Statisk tekstfil |
| `misc-06-registersporet` | Registersporet | Misc | 175 | Statiske tekstfiler |
| `network-02-http-basic` | Basic på tråden | Network | 175 | Statisk PCAP |
| `crypto-08-gjenbrukt-nokkelstrom` | Samme strøm to ganger | Crypto | 200 | Statisk JSON |
| `forensics-06-klippet-limt` | Klippet og limt | Forensics | 200 | Statisk binærfil |
| `forensics-08-slettet-skiftlogg` | Slettet skiftlogg | Forensics | 200 | Statisk diskbilde |
| `pwn-01-buffer-boden` | Buffer på boden | Pwn | 200 | TCP-container |
| `stego-02-lsb-skilt` | Det blå skiltet | Stego | 200 | Statisk PNG |
| `crypto-06-raymond-rsa` | Raymonds RSA | Crypto | 225 | Statisk JSON |
| `forensics-07-tasteloggen` | Tasteloggen | Forensics | 225 | Statisk USB PCAP |
| `misc-05-radiovakten` | Radiovakten | Misc | 225 | Statisk tekstfil |
| `linux-01-servicekonto` | Servicekontoen | Linux | 250 | SSH-container |
| `forensics-03-stand-pc` | Stand-PC-en | Forensics | 250 | Statisk ZIP |
| `password-01-arkivportal` | Arkivportalen | Password Forensics | 250 | Statisk ZIP |
| `crypto-04-rsa-felles-modulus` | To nøkler, samme modul | Crypto | 275 | Statisk JSON |
| `api-01-leverandorregister` | Leverandørregisteret | Web | 300 | Flask API |
| `ot-02-bop-modbus` | Brønn under press | OT / ICS | 300 | Modbus-container |
| `ot-03-mqtt` | Ukryptert anlegg | OT / ICS | 300 | MQTT-container |
| `re-02-crackme` | Crack meg | Reverse Engineering | 350 | Statisk ELF |
| `web-01-jwt` | Operatørportalen | Web | 350 | Flask-container |
| `crypto-05-lcg-sensorstrom` | Sensorstrømmen | Crypto | 400 | Statisk JSON |
| `ot-04-scada-sqli` | HMI Tilgang | Web | 400 | Flask-container |
| `ot-05-historian-api` | Historikkarkivet | Web | 500 | Flask API |
| `re-03-minivm` | Virtuell maskin | Reverse Engineering | 500 | Statisk ELF |

## Struktur

- `challenges/` inneholder arrangørkilde, servere, generatorer og solvere.
- `release/` genereres med deltakertekst og vedlegg uten løsninger.
- `docs/solution-writeups.md` inneholder samlet løsningsguide for arrangører.
- `tools/` inneholder bygging, validering, eksport og CTFd-deployment.

## Kom i gang

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-organizer.txt
python3 tools/export_release.py
```

Solverne for pwn-oppgavene bruker pwntools. Installer dette separat ved behov,
helst med Python 3.11 eller i et Linux-miljo:

```bash
pip install -r requirements-pwn.txt
```

Bygg Linux-binærer med Docker:

```bash
./tools/build_linux_binaries.sh
```

Kjør hele valideringen:

```bash
./tools/validate_all.sh
```

Se [HOW_TO_TESTE_OPPGAVENE.md](HOW_TO_TESTE_OPPGAVENE.md) for detaljert
lokal testing og [docs/solution-writeups.md](docs/solution-writeups.md) for
arrangørwriteups. Se [docs/new-challenge-ideas.md](docs/new-challenge-ideas.md)
for den prioriterte backloggen med nye statiske oppgaver, og
[docs/wave-2-draft-plan.md](docs/wave-2-draft-plan.md) for notater om andre
pulje.

