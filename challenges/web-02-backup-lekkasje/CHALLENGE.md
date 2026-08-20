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

## Løsningsvei (kun for arrangør)

1. Besøk `/robots.txt`.
2. Finn `Disallow: /backup/`.
3. Besøk `/backup/`. Kataloglisting er deaktivert, men 403-responsen gir en
   liten nudge mot gamle Flask config-backups.
4. Enumerer filnavn i backup-mappen. Med SecLists kan oppgaven løses
   deterministisk uten ren intuisjon:

   ```bash
   ffuf -u <URL>/backup/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-small-files.txt
   ```

   Dette gir treff på `/backup/config.py.bak`. Manuell vei er å kombinere
   nudget om Flask/config-backups med hintet om `.bak`, `.old` og `~`.
5. Hent `/backup/config.py.bak`.
6. Les flagget i `LEGACY_INCIDENT_TOKEN`.

**Flagg:** `CTF{r0b0ts_og_b4ckup_fant}`
