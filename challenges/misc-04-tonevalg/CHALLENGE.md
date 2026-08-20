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

## Løsningsvei (kun for arrangør)

1. Åpne WAV filen i Audacity og velg spektrogramvisning, eller analyser
   frekvensene med et DTMF verktøy.
2. Hver tone består av én lav og én høy DTMF frekvens. Tonene dekodes til:

   ```text
   8#666#66#33#0#333#777#2#0#7777#33#66#8#777#2#555
   ```

3. Del på `#`. Tallet `0` er mellomrom. De øvrige gruppene bruker klassisk
   flertrykksinndata: `2=A`, `22=B`, `222=C`, `3=D` og så videre.
4. Gruppene gir teksten `TONE FRA SENTRAL`.
5. Normaliser teksten etter flaggformatet.

Arrangørsolveren bruker energibasert segmentering og Goertzel algoritmen for
å gjenkjenne de åtte DTMF frekvensene. Den kjenner ikke den ferdige
tonesekvensen på forhånd.

```bash
python3 solver/solve.py
```

**Flagg:** `CTF{tone_fra_sentral}`

