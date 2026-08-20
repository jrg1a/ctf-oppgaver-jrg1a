# Skiftprotokollen

**Kategori:** Crypto
**Poeng:** 75
**Type:** Statisk fil (ingen server)
**Vanskelighetsgrad:** Lett

---

## Scenario

En gammel skiftprotokoll fra Nordverk ble sendt over et internt
radiosamband. Operatørene brukte en enkel klassisk substitusjon fordi
"det ikke er ekte hemmeligheter i skiftloggen".

Sikkerhetsteamet er ikke like overbevist.

Finn meldingen og hent ut flagget.

---

## Vedlegg

- [`skiftprotokoll.txt`](dist/skiftprotokoll.txt)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Dette er en Caesar/ROT-variant, ikke moderne krypto. |
| 10 poeng | Norsk tekst gir mange tydelige ord når riktig skift er valgt. |
| 25 poeng | Prøv alle 29 skift i alfabetet `ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ`. |

---

## Løsningsvei (kun for arrangør)

Bruk norsk alfabet med 29 tegn og test alle mulige Caesar-skift.
Riktig skift er `11`.

**Flagg:** `CTF{rot_med_norsk_alfabet}`
