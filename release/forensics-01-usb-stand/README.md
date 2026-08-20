# USB fra standen

**Kategori:** Forensics
**Poeng:** 150
**Type:** Statisk fil (ZIP med SQLite + nedlastinger + fotoarkiv)
**Vanskelighetsgrad:** Lett / Medium

---

## Scenario

Etter siste foredrag på Teknologidagene fant en frivillig en glemt
USB-pinne ved Nordverks stand. Innholdet er imaget og lagt i et
ZIP-arkiv. Sikkerhetsteamet ønsker å vite hva personen har gjort
*på messen*, særlig om det ble lastet ned noe sensitivt.

Pakk ut, bygg en tidslinje, og finn ut hvilken nedlasting som bør undersøkes
nærmere. Ikke stol på filnavn alene.

---

## Vedlegg

- [`usb_fra_standen.zip`](dist/usb_fra_standen.zip)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Det ligger en SQLite-database i ZIP-en. Start med tabellene og filoversikten. |
| 20 poeng | `downloads`-tabellen gir en tidslinje, men den mest interessante filen er ikke nødvendigvis den aller siste. |
| 35 poeng | Ett av vedleggene er et arkiv med bilder. Metadata og `strings` kan være mer nyttig enn å åpne bildene visuelt. |
| 50 poeng | Se etter en kort `cache_ref` i fotoarkivet og gjør den lesbar. |

---
