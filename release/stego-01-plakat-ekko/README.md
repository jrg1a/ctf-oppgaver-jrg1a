# Plakat med ekko

**Kategori:** Stego
**Poeng:** 100
**Type:** Statisk fil (PNG)
**Vanskelighetsgrad:** Lett

---

## Scenario

Nordverk har trykket en plakat for Teknologidagene 2026.
Designteamet sier at filen «bare er en plakat», men sikkerhetsteamet
mistenker at noen har gjemt en hemmelighet i den.

Klarer du finne ekkoet?

---

## Vedlegg

- [`plakat.png`](dist/plakat.png)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Bildet kan se normalt ut, men filstørrelsen er litt for stor. |
| 25 poeng | Sjekk PNG-metadata med `exiftool plakat.png` eller `pngcheck -t plakat.png`. |
| 50 poeng | PNG-en slutter ved `IEND`-chunken. Hva ligger *etter* den? Prøv `tail -n 1 plakat.png`. |

---
