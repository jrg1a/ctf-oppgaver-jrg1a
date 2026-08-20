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
