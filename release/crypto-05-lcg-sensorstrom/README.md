# Sensorstrømmen

**Kategori:** Crypto
**Poeng:** 400
**Type:** Statisk fil (ingen server)
**Vanskelighetsgrad:** Medium / Vanskelig

---

## Scenario

Et testoppsett for sensordata bruker en hjemmelaget "stream cipher".
Utvikleren tok en lineær kongruensgenerator, brukte output som nøkkelstrøm,
og tenkte at det var godt nok siden parameterne ikke står i klienten.

En feilsøkingslogg lekket noen rå PRNG-verdier rett før kryptering.

Rekonstruer generatoren og dekrypter meldingen.

---

## Vedlegg

- [`sensorstrom.json`](dist/sensorstrom.json)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 50 poeng | Generatoren er `x[n+1] = (a*x[n] + c) mod m`. |
| 90 poeng | Du får nok påfølgende outputs til å løse for `a` og `c`. |
| 140 poeng | Hvis `x1 - x0` har invers modulo `m`, er `a = (x2 - x1) * inv(x1 - x0) mod m`. |

---
