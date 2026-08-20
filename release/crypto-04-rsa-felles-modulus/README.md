# To nøkler, samme modul

**Kategori:** Crypto
**Poeng:** 275
**Type:** Statisk fil (ingen server)
**Vanskelighetsgrad:** Medium

---

## Scenario

Nordverk har to gamle RSA-profiler for samme meldingsformat. Begge ble
brukt til å kryptere samme beredskapshemmelighet, og noen antok at to
forskjellige offentlige eksponenter var nok separasjon.

Men modulverdien er identisk.

Hent meldingen.

---

## Vedlegg

- [`rsa_felles_modulus.json`](dist/rsa_felles_modulus.json)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 30 poeng | Samme melding er kryptert med samme `n`, men to ulike `e`. |
| 60 poeng | Hvis `gcd(e1, e2) = 1`, kan Bezout hjelpe deg. |
| 90 poeng | Bruk utvidet Euklid til å finne `a` og `b` slik at `a*e1 + b*e2 = 1`. |

---
