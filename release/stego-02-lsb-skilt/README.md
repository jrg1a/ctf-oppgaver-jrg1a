# Det blå skiltet

**Kategori:** Stego
**Poeng:** 200
**Type:** Statisk fil (PNG)
**Vanskelighetsgrad:** Medium

---

## Scenario

Grafikkteamet har sendt over et lite informasjonsskilt til standen. Filen
ser helt normal ut, men en av ingeniørene insisterer på at "det blå laget"
inneholder mer enn bare farge.

Finn meldingen i bildet.

---

## Vedlegg

- [`skilt.png`](dist/skilt.png)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Dette er ikke metadata eller data etter IEND. Se på pikslene. |
| 40 poeng | Den minst signifikante biten i blåkanalen er interessant. |
| 80 poeng | De første 32 bitene er meldingslengden i bytes, deretter kommer ASCII-meldingen. |

---
