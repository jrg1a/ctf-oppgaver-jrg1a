# Det glemte committet

**Kategori:** Forensics
**Poeng:** 150
**Type:** Statisk fil (Git repository i ZIP)
**Vanskelighetsgrad:** Lett / Medium

---

## Scenario

Et lite verktøy for arkivsynkronisering ble pakket og sendt til
sikkerhetsgjennomgang. Utvikleren sier at en intern gjenopprettingskode ble
fjernet før pakken ble laget.

Undersøk prosjektet og finn koden som ikke lenger finnes i siste versjon.

---

## Vedlegg

- [`arkivsynk.zip`](dist/arkivsynk.zip)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Den skjulte `.git` mappen er en del av vedlegget. |
| 30 poeng | `git log --all --oneline` viser mer enn filene i arbeidsmappen. |
| 60 poeng | Let etter commits som slettet filer, og bruk `git show` for å lese filen før slettingen. |

---
