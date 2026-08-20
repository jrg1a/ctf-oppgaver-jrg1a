# Samme strøm to ganger

**Kategori:** Crypto
**Poeng:** 200
**Type:** Statisk JSON
**Vanskelighetsgrad:** Medium

---

## Scenario

To sambandspakker ble kryptert av samme nødaggregat. Dokumentasjonen sier at
systemet bruker en XOR basert nøkkelstrøm, men en omstart gjorde at telleren
begynte på nytt. Klarteksten til den første, rutinemessige statusmeldingen er
kjent.

Gjenopprett innholdet i den andre pakken.

---

## Vedlegg

- [`samband.json`](dist/samband.json)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | XOR er sin egen inverse. Skriv de tre relevante bytefølgene under hverandre. |
| 40 poeng | `klartekst_a XOR chiffer_a` gir nøkkelstrømmen som ble brukt på pakke A. |
| 80 poeng | Omstarten gjorde at nøyaktig samme nøkkelstrøm ble brukt fra byte null i pakke B. |

---
