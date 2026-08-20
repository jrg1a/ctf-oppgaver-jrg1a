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
