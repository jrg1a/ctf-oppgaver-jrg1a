# Morse på releet

**Kategori:** Misc
**Poeng:** 100
**Type:** Statisk fil (CSV)
**Vanskelighetsgrad:** Lett

---

## Scenario

Et gammelt nødrele på Nordverk-standen har logget av/på-pulser fra
en testmelding. Ingen husker lenger hva operatøren sendte, men rytmen ser
veldig kjent ut.

Tolk pulsene og finn flagget.

---

## Vedlegg

- [`relay_log.csv`](dist/relay_log.csv)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Korte og lange ON-pulser er prikker og streker. |
| 20 poeng | OFF-pulser på omtrent tre tidsenheter markerer nytt tegn. |
| 40 poeng | Bruk internasjonal Morse. Parentes-kodene brukes for `{` og `}`, og `_` finnes som `..--.-`. |

---
