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

## Løsningsvei (kun for arrangør)

### Steg 1 — Inspisér metadata

```bash
exiftool plakat.png
# eller
strings plakat.png | head -20
```

Du finner en `tEXt`-kommentar som sier:
```
Teknologidagene 2026 - poster v1. Ekkoet ligger bak rammen (base64).
Siste tekstlinje i filen er base64. Bruk `tail -n 1`.
```

### Steg 2 — Trekk ut data etter IEND

PNG-er ender ved `IEND`-chunken. Alt etter det er ekstra data:

```bash
tail -n 2 plakat.png
# --ekko--
# S0F7cGxha2F0XzNra18wX2I0a18xZW5kfQ==
```

### Steg 3 — Dekod base64

```bash
tail -n 1 plakat.png | base64 -d
# CTF{plakat_3kk0_b4k_1end}
```

**Flagg:** `CTF{plakat_3kk0_b4k_1end}`
