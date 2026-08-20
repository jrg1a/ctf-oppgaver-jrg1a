# Brukeragenten

**Kategori:** Forensics
**Poeng:** 100
**Type:** Statisk fil (PCAP)
**Vanskelighetsgrad:** Lett

---

## Scenario

En intern webserver fikk plutselig mange forespørsler mot sider som ikke
finnes. Samtidig finnes det vanlig nettlesertrafikk i opptaket.

Finn hvilket verktøy som skapte den avvikende trafikken, inkludert
versjonsnummeret.

---

## Vedlegg

- [`brukeragenten.pcap`](dist/brukeragenten.pcap)

---

## Flaggformat

Skriv verktøynavn og versjon med små bokstaver:

```text
CTF{verktøy_versjon}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Sammenlign HTTP forespørslene. Hvilket felt beskriver klientprogrammet? |
| 20 poeng | Wireshark filteret `http.user_agent` viser bare pakker som oppgir en brukeragent. |
| 40 poeng | Ett verktøy sender langt flere forespørsler enn de vanlige nettleserne. Navn og versjon står i samme header. |

---

## Løsningsvei (kun for arrangør)

1. Åpne PCAP filen i Wireshark.
2. Bruk displayfilteret `http.request` og legg feltet `http.user_agent` til
   som kolonne, eller filtrer direkte med `http.user_agent`.
3. De vanlige klientene identifiserer seg som Firefox, Chromium, curl og et
   oppdateringsverktøy. Den klart hyppigste avvikende verdien inneholder
   `Nikto/2.5.0`.
4. Normaliser verktøynavnet til små bokstaver og behold versjonsnummeret.

Terminalbasert kontroll:

```bash
tshark -r brukeragenten.pcap -Y http.user_agent \
  -T fields -e http.user_agent | sort | uniq -c | sort -nr
```

Arrangørsolveren leser HTTP headerne fra TCP payloadene og gjør den samme
sammenligningen:

```bash
python3 solver/solve.py
```

**Flagg:** `CTF{nikto_2.5.0}`

