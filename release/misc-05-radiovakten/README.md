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
