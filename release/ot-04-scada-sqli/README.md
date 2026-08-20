# HMI Tilgang

**Kategori:** Web
**Poeng:** 400
**Type:** Container (Flask-webapplikasjon)
**Vanskelighetsgrad:** Medium / Vanskelig
**Container:** 3 av 10

---

## Scenario

Nordverks SCADA-system har et webbasert HMI-panel for operatør-innlogging.
Sikkerhetsteamet mistenker at autentiseringen kan omgås.

En intern revisjon avdekket at historikk-databasen kan inneholde sensitiv data
som ikke skal være tilgjengelig for eksterne. Kom deg inn og finn ut hva som
ligger der.

---

## Tilkobling

```
http://<IP>:8080
```

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 50 poeng | Prøv å manipulere passord-feltet, er det SQL bak? |
| 90 poeng | Noen mønstre er filtrert. Hva kan du bruke i stedet for `OR` og `--`? |
| 140 poeng | `UNION SELECT` kan være relevant, men queryen må være balansert uten trailing comment |

---
