# Stand-PC-en

**Kategori:** Forensics
**Poeng:** 250
**Type:** Statisk fil (ZIP)
**Vanskelighetsgrad:** Medium

---

## Scenario

En demo-PC på standen ble brukt av mange personer gjennom dagen. Før den
ble ryddet bort tok IT en liten kopi av brukerprofilen.

Finn sporene i profilen og hent ut flagget.

---

## Vedlegg

- [`stand_pc.zip`](dist/stand_pc.zip)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Dette ligner en nettleserprofil, ikke et vanlig dokumentarkiv. |
| 50 poeng | SQLite-filene i profilen er mer interessante enn tekstfilene. |
| 100 poeng | Se i Cookies-databasen etter noe som er base64-enkodet. |

---
