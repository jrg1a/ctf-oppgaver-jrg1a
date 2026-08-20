# Arkivportalen

**Kategori:** Password Forensics
**Poeng:** 250
**Type:** Statisk ZIP og lokal HTML
**Vanskelighetsgrad:** Medium

---

## Scenario

Et lite standteam hos Nordverk har sendt over en kopi av et gammelt
arkivområde og en passordliste de brukte under riggingen av demoen.

Arkivet er pakket i en passordbeskyttet ZIP. Inne i arkivet ligger en lokal
statusportal som skal åpnes i nettleseren, men portalen krever en dagskode.

Finn dagskoden, lås opp portalen og hent flagget.

---

## Vedlegg

- [`standarkiv.zip`](dist/standarkiv.zip), Passordbeskyttet arkiv
- [`passordliste.txt`](dist/passordliste.txt), Liten lekket passordliste

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 20 poeng | ZIP-passordet er ikke tilfeldig. Bruk passordlisten som følger med. |
| 40 poeng | Klassiske ZIP-cracking-verktøy kan bruke en liten ordliste uten å brute-force hele nøkkelrommet. |
| 60 poeng | Etter utpakking: les logger nøye. Debug-linjer kan inneholde kodet informasjon. |
| 80 poeng | Portalen forventer dagskoden i normalisert form, ikke nødvendigvis slik den først dukker opp i loggen. |

---
