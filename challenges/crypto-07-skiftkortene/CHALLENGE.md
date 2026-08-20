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

## Løsningsvei (kun for arrangør)

1. Sammenlign `KJENT_KLAR_1` med `KJENT_SENDT_1`. Klarteksten består av 32
   unike tegn, så hvert tegn avslører hvilken opprinnelig posisjon som ble
   flyttet til den aktuelle posisjonen i chifferteksten.
2. Kontroller rekkefølgen mot det andre kjente paret. Dette gjør det lett å
   oppdage om kartleggingen er snudd.
3. Del `UKJENT_SENDT` i blokker på 32 tegn.
4. For hver chifferposisjon `i`, plasser tegnet tilbake på posisjonen som ble
   funnet fra første kalibreringskort.
5. Fjern fylltegnet `~` til slutt.

Et kort Pythonutkast er en naturlig løsningsmetode:

```python
perm = [kjent_klar.index(tegn) for tegn in kjent_sendt]
klar = ["?"] * 32
for ut_pos, inn_pos in enumerate(perm):
    klar[inn_pos] = ukjent_blokk[ut_pos]
```

Arrangørsolveren utfører denne kartleggingen for alle blokkene:

```bash
python3 solver/solve.py
```

**Flagg:** `CTF{samme_permutasjon_hver_gang}`

