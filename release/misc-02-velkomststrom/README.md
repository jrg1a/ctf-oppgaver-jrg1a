# Velkomststrøm

**Kategori:** Misc
**Poeng:** 50
**Type:** Statisk fil (tekst)
**Vanskelighetsgrad:** Lett (first solve)

---

## Scenario

Nordverk slipper en velkomstpakke til alle som er innom standen
på Teknologidagene. Pakken er «pakket inn» i flere lag med encoding,
ikke for å gjøre den hemmelig, men som en oppvarmingsoppgave.

Pakk ut og finn velkomstkoden.

---

## Vedlegg

- [`velkomst.txt`](dist/velkomst.txt)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Filen ser ut som ren ASCII, men det er bare *yttersjiktet*. Tre lag totalt. |
| 10 poeng | Første lag består bare av hex-tegn. Gjør hvert lag om til bytes før du vurderer neste. |
| 20 poeng | Etter hex-laget følger en vanlig tekst-encoding og til slutt komprimerte data. |

---
