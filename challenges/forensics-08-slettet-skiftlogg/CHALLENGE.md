# Slettet skiftlogg

**Kategori:** Forensics
**Poeng:** 200
**Type:** Statisk diskbilde
**Vanskelighetsgrad:** Medium

---

## Scenario

Et minnekort fra en eldre vedlikeholdsterminal ble levert inn etter en
hendelse. Den synlige skiftloggen inneholder bare ordinære målinger, men en
tekniker mener at en annen logg nylig ble slettet.

Finn og gjenopprett den slettede loggen.

---

## Vedlegg

- [`skiftminne.img`](dist/skiftminne.img)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Identifiser filsystemet før du forsøker å montere eller søke i bildet. |
| 45 poeng | Sleuth Kit kan liste slettede katalogoppføringer med `fls -d`. |
| 90 poeng | Bruk metadataadressen fra `fls` sammen med `icat`. Kontroller deretter filtypen på det du gjenopprettet. |

---

## Løsningsvei (kun for arrangør)

1. Identifiser bildet:

   ```bash
   file skiftminne.img
   fsstat skiftminne.img
   ```

   Det er et lite FAT12 filsystem.
2. List katalogoppføringer, inkludert slettede filer:

   ```bash
   fls -r -d skiftminne.img
   ```

3. Finn den slettede oppføringen som ender på `KIFTLOG.GZ`. Den første bokstaven
   i et slettet FAT filnavn er normalt erstattet med markøren `0xe5`.
4. Bruk metadataadressen som `fls` viser:

   ```bash
   icat skiftminne.img <metadataadresse> > gjenopprettet.gz
   file gjenopprettet.gz
   gzip -dc gjenopprettet.gz
   ```

5. Den utpakkede skiftloggen inneholder flagget. Den aktive filen
   `SKIFT.TXT` inneholder en eldre kontrollkode med feil flaggformat og er bare
   en distraksjon.

**Flagg:** `CTF{slettet_betyr_ikke_borte}`

