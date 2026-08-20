# Not Your Badge

**Kategori:** Web
**Poeng:** 125
**Type:** Container (Flask-webapplikasjon)
**Vanskelighetsgrad:** Lett
**Container:** 10 av 10

---

## Scenario

Nordverk bruker en enkel badgeportal for konferansestanden. Du har fått lenke
til ditt eget deltakerbadge, men portalen ble laget litt for raskt.

Systemet skal egentlig bare vise badgen som tilhører deg.

Finn badgen som ikke er din, og hent internmerknaden som ligger der.

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
| Gratis | Start på badge-lenken fra forsiden. Hva i URL-en bestemmer hvilken badge som vises? |
| 25 poeng | `id`-parameteren brukes direkte i oppslaget. |
| 50 poeng | Ikke hopp rett til store tall. Badge-ID-ene rundt din egen kan være mer interessante. |

---
