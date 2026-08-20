# Leverandørregisteret

**Kategori:** Web
**Poeng:** 300
**Type:** Container (Flask REST API)
**Vanskelighetsgrad:** Medium
**Container:** 10 av 10

---

## Scenario

Nordverk har åpnet et nytt leverandørregister for konferansestanden. API-et
skal bare vise ufarlige firmadata til eksterne leverandører, mens interne
kontrakter og beredskapsnotater skal være skjult bak rollebasert tilgang.

Utviklerne har rukket å publisere dokumentasjonen, men sikkerhetsteamet er
ikke helt overbevist om at rollemodellen er ferdig testet.

Finn den interne beredskapskoden.

---

## Tilkobling

```
http://<IP>:8080
```

Start gjerne på `/ui`.

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 35 poeng | API-dokumentasjon viser ofte bare den pene fasaden. Se etter endepunkter som ikke hører hjemme i produksjon. |
| 65 poeng | Hva skjer hvis klienten sender flere felter enn skjemaet egentlig trenger? |
| 100 poeng | Rollen er en del av serverens brukerobjekt. Hvem får lov til å bestemme den? |

---

## Løsningsvei

1. Gå til `/ui` og se dokumenterte endepunkter.
2. Kall `/api/v1/_debug/routes` for å finne skjulte interne ruter.
3. Registrer en ny bruker med mass-assignment:
   `{"username":"x","password":"x","company":"x","role":"admin"}`.
4. Logg inn og bruk tokenet mot `/api/v1/internal/beredskap`.
5. Flagget ligger i feltet `beredskapskode`.

**Flagg:** `CTF{api_mass_assignment_i_leverandorportalen}`
