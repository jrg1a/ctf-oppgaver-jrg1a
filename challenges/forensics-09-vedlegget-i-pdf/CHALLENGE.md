# Vedlegget i rapporten

**Kategori:** Forensics
**Poeng:** 150
**Type:** Statisk PDF
**Vanskelighetsgrad:** Lett / Medium

---

## Scenario

En revisjonsrapport fra Nordverk ser fullstendig ut når den åpnes i
nettleseren, men overføringsloggen hevder at dokumentet inneholdt mer enn den
synlige siden.

Undersøk hele PDF strukturen og finn kontrollkoden.

---

## Vedlegg

- [`revisjonsrapport.pdf`](dist/revisjonsrapport.pdf)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | En PDF kan inneholde mer enn tekst, bilder og synlige sider. |
| 30 poeng | Prøv `pdfdetach -list revisjonsrapport.pdf`. |
| 60 poeng | Lagre alle innebygde vedlegg, les kontrollnotatet og dekod verdien det inneholder. |

---

## Løsningsvei (kun for arrangør)

1. Start med vanlige PDF verktøy:

   ```bash
   pdfinfo revisjonsrapport.pdf
   exiftool revisjonsrapport.pdf
   pdfdetach -list revisjonsrapport.pdf
   ```

2. `pdfdetach` viser to innebygde filer. Hent dem ut:

   ```bash
   mkdir vedlegg
   pdfdetach -saveall -o vedlegg revisjonsrapport.pdf
   ls -la vedlegg
   ```

3. `lesmeg.txt` er et ordinært overføringsnotat. `kontrollnotat.txt` inneholder
   en Base64 verdi.
4. Dekod verdien:

   ```bash
   base64 -d
   ```

   Det gir flagget direkte.

**Flagg:** `CTF{pdf_vedlegg_gjemmer_mer}`

