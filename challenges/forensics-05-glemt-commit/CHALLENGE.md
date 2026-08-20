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

## Løsningsvei (kun for arrangør)

1. Pakk ut ZIP filen og gå inn i `arkivsynk`.
2. Bekreft at prosjektet er et Git repository:

   ```bash
   git status
   git log --all --oneline
   ```

3. Se etter slettede filer i historikken:

   ```bash
   git log --all --diff-filter=D --summary
   ```

4. Historikken viser at `config/datasync.env` ble slettet i committet med
   meldingen `Fjern lokal konfigurasjon før deling`.
5. Vis endringen, eller les filen fra foregående commit:

   ```bash
   git show <slettecommit>
   git show <slettecommit>^:config/datasync.env
   ```

6. Verdien `ARCHIVE_RECOVERY_CODE` inneholder flagget.

En alternativ, systematisk kontroll er å søke i alle revisjoner:

```bash
for rev in $(git rev-list --all); do git grep -n 'CTF{' "$rev"; done
```

Arrangørsolver:

```bash
python3 solver/solve.py
```

**Flagg:** `CTF{historikken_husker_alt}`

