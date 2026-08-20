# Tonevalg

**Kategori:** Misc
**Poeng:** 125
**Type:** Statisk fil (WAV)
**Vanskelighetsgrad:** Lett / Medium

---

## Scenario

En gammel telefonmodul i alarmsentralen lagret et kort lydopptak rett før den
ble koblet fra. Opptaket består av tydelige toner og korte pauser.

Finn meldingen som ble tastet inn.

---

## Vedlegg

- [`tonevalg.wav`](dist/tonevalg.wav)

---

## Flaggformat

Skriv den dekodede meldingen med små bokstaver og understrek mellom ordene:

```text
CTF{dekodet_melding}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Se på et spektrogram. Hver tone består av to tydelige frekvenser. |
| 25 poeng | Frekvensparene følger DTMF tastaturet fra vanlige telefoner. |
| 50 poeng | Etter at tonene er blitt til tegn, skiller `#` bokstavgrupper og `0` markerer mellomrom. Bruk flertrykksmetoden fra eldre mobiltelefoner. |

---
