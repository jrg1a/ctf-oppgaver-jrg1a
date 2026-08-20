# Historikkarkivet

**Kategori:** Web
**Poeng:** 500
**Type:** Container (Flask REST API)
**Vanskelighetsgrad:** Vanskelig
**Container:** 4 av 10

---

## Scenario

Nordverk har satt opp en REST API for å eksponere prosessdata fra
historikk-databasen til interne dashboards. API-et skal kun gi tilgang
til offentlige sensordata, men et internt sikkerhetsteam mistenker at
tilgangskontrollene ikke er implementert korrekt.

Utforsk API-et grundig. Finn ut hva som egentlig er tilgjengelig, og
hva som burde vært låst ned.

---

## Tilkobling

```
http://<IP>:8080
```

Landing page viser dokumenterte endepunkter. Men er det alt?

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 25 poeng | API-et har flere endepunkter enn de dokumenterte. Prøv vanlige stier. |
| 50 poeng | Bare 3 sensorer er "offentlige", men finnes det flere? Hva skjer om du endrer ID? |
| 75 poeng | En av loggpostene inneholder kodet data. Sjekk feltnavn nøye. |
| 100 poeng | Den kodede verdien er tekstvennlig og kan dekodes med vanlige base64-verktøy. |
| 150 poeng | Noen API-endepunkter forventer Bearer-token. Let etter hvor en slik verdi kan lekke. |

---
