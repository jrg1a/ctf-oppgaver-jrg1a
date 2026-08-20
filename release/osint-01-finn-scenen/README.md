# Finn scenen

**Kategori:** OSINT
**Poeng:** 75
**Type:** Statisk fil (frosset OSINT)
**Vanskelighetsgrad:** Lett

---

## Scenario

En frivillig på Teknologidagene fant et beskåret skiltbilde fra
messeområdet. Selve scenenavnet er klippet bort, men *tid* og *tittel*
er fortsatt synlig.

Nordverks sikkerhetsteam har en intern kodebok som mapper hver scene
til en kode. Finn riktig scene, slå opp koden og bygg flagget.

> **NB:** Alt OSINT-materiell er frosset til vedlegg ved publisering.
> Gå *ikke* til teknologidagene.example for å verifisere, programmet
> oppdateres jevnlig, og en korrekt løsning skal ikke avhenge av
> levende data.

---

## Vedlegg

- [`skilt_foto.png`](dist/skilt_foto.png), Beskåret skiltbilde fra messeområdet
- [`program_snapshot.txt`](dist/program_snapshot.txt), Frosset programutdrag
- [`kodebok.md`](dist/kodebok.md), Sal-kode-til-suffiks-mapping

---

## Flaggformat

```
CTF{scene_<bokstav>_<navn>}
```

(formatet er definert i `kodebok.md`)

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Hva er synlig på skiltet? Tittel og tid er to gode indekser inn i programmet. |
| 10 poeng | Bare én rad i programmet matcher *både* tittel og tid. Den raden røper sal-bokstaven. |
| 25 poeng | Kodeboken har en kolonne som allerede er ment å brukes som flagg-suffiks. |

---
