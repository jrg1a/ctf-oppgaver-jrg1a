# Klippet og limt

**Kategori:** Forensics
**Poeng:** 200
**Type:** Statisk fil
**Vanskelighetsgrad:** Medium

---

## Scenario

Et bildearkiv ble kopiert via et ustabilt mellomlager. I etterkant ligger bare
en binær fil igjen. Ingen av filtypene kjennes igjen direkte, men noen
signaturer dukker opp på mistenkelig jevne avstander.

Rekonstruer innholdet og sett sammen meldingen.

---

## Vedlegg

- [`utklipp.bin`](dist/utklipp.bin)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Søk etter kjente filsignaturer i den binære filen. |
| 40 poeng | PNG starter med samme 8 byte hver gang. Se på avstanden mellom treffene. |
| 80 poeng | Dataene er flettet sammen i like store blokker. Del filen i strømmer og trim hver strøm ved PNG sin `IEND` chunk. |

---
