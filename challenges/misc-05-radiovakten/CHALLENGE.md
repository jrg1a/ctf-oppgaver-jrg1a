# Radiovakten

**Kategori:** Misc
**Poeng:** 225
**Type:** Statisk tekstfil
**Vanskelighetsgrad:** Medium

---

## Scenario

En smalbåndsmottaker fanget opp en kort bitstrøm fra Nordverks gamle
fjernskriver. Mottakeren oppgir symbolbredden og bitrekkefølgen, men ikke
tegnsettet. Trafikken inneholder både bokstaver og tall.

Dekod operatørmeldingen og lever inn innholdet i standard flaggformat.

---

## Vedlegg

- [`radiotrafikk.txt`](dist/radiotrafikk.txt)

---

## Flaggformat

Bruk små bokstaver og understrek mellom ordene:

```text
CTF{dekodet_operatormelding}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Fem bits gir ikke nok verdier til bokstaver, tall og tegn samtidig. Noen symboler må derfor endre modus. |
| 45 poeng | Se etter ITA2, også kjent som Baudot Murray kode. |
| 90 poeng | Verdiene 27 og 31 skifter mellom FIGURES og LETTERS. Bitene i hvert symbol er lagret med laveste bit først. |

---

## Løsningsvei (kun for arrangør)

1. Les mottakerhodet. Hvert symbol består av fem bits, og bitene står med
   laveste bit først.
2. Del strømmen i grupper på fem og snu bitrekkefølgen i hver gruppe før den
   tolkes som et tall.
3. Bruk en ITA2 tabell. Symbol 31 velger bokstavtabellen, mens symbol 27 velger
   talltabellen.
4. Dekodingen gir en kort kalibreringslinje etterfulgt av:

   ```text
   RADIO VAKTEN BYTTER MODUS 73
   ```

5. Normaliser meldingen etter flaggformatet.

Oppgaven kan løses med CyberChef sin Baudot funksjon dersom bitrekkefølgen
justeres, eller med et kort skript som holder rede på gjeldende tabell.

**Flagg:** `CTF{radio_vakten_bytter_modus_73}`

