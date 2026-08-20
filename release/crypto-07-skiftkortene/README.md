# Skiftkortene

**Kategori:** Crypto
**Poeng:** 175
**Type:** Statisk tekstfil
**Vanskelighetsgrad:** Lett / Medium

---

## Scenario

En gammel kortsorterer fra Nordverk stokker tegnene i hver melding før de
lagres. Teknikeren brukte alltid den samme rekkefølgen, og noen av
kalibreringskortene med kjent innhold er bevart.

Finn den opprinnelige kontrollmeldingen.

---

## Vedlegg

- [`skiftkort.txt`](dist/skiftkort.txt)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Tegnene er ikke endret, bare flyttet. Arbeid blokk for blokk. |
| 35 poeng | Det første kjente paret inneholder bare unike tegn. Bruk det til å finne hvor hver posisjon havnet. |
| 70 poeng | Bygg den inverse permutasjonen og bruk den på hver blokk i den ukjente meldingen. |

---
