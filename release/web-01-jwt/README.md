# Operatørportalen

**Kategori:** Web
**Poeng:** 350
**Type:** Container (Flask-webapplikasjon)
**Vanskelighetsgrad:** Medium
**Container:** 5 av 10

---

## Scenario

Nordverks interne operatørportal bruker JWT (JSON Web Tokens)
for autentisering. Du har fått gjestekonto-tilgang for demonstrasjon,
men admin-panelet er kun tilgjengelig for privilegerte brukere.

Finn en måte å oppgradere tilgangen din.

---

## Tilkobling

```
http://<IP>:8080
```

Gjestekonto: `guest` / `guest`

---

## Vedlegg

- [`wordlist.txt`](wordlist.txt), Ordliste med OT-relevante passord

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 30 poeng | Se på cookien du får etter innlogging. Hva slags format er det? |
| 55 poeng | JWT består av tre deler. Payload-delen er lesbar når den dekodes. |
| 90 poeng | HMAC-signaturen bruker et svakt secret. Kan det finnes med ordlisten? |
| 115 poeng | Når signeringshemmeligheten er kjent, kan tokenet signeres på nytt med en annen rolle. |

---
