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

## Løsningsvei (kun for arrangør)

```bash
# 1. Pakk ut
unzip usb_fra_standen.zip -d usb/

# 2. Inspisér databasen
sqlite3 usb/history.sqlite ".schema"
sqlite3 usb/history.sqlite "SELECT target_path, tab_url, start_time
                           FROM downloads ORDER BY start_time DESC;"

# 3. Finn fotoarkivet i downloads-tabellen
unzip -l usb/downloads/standfoto_mai.zip
unzip usb/downloads/standfoto_mai.zip -d usb/standfoto

# 4. Let i metadata/strings
strings -a usb/standfoto/bilder/*.png | grep "cache_ref"

# 5. Dekod verdien etter cache_ref=
printf 'S0F7dXNiX2gxc3Rfc3FsaXRlX2pha3RldH0=' | base64 -d
```

**Flagg:** `CTF{usb_h1st_sqlite_jaktet}`
