# Backup-lekkasje

**Kategori:** Web
**Poeng:** 150
**Type:** Container (Flask-webapplikasjon)
**Vanskelighetsgrad:** Lett
**Container:** 7 av 10

---

## Scenario

Nordverk satte opp en liten intern infoside for konferansestanden.
Utvikleren sier at alt sensitivt er fjernet før deploy, men gamle filer
har en tendens til å bli liggende.

Finn backupfilen og hent lekkasjen.

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
| Gratis | Start med `robots.txt`. |
| 25 poeng | Backupfiler får ofte endelser som `.bak`, `.old` eller `~`. |
| 50 poeng | Konfigurasjonsfiler inneholder ofte hemmeligheter som aldri skulle vært deployet. |

---
