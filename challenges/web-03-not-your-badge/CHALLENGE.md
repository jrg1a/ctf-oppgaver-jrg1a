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

## Løsningsvei

1. Åpne forsiden og klikk på ditt badge.
2. URL-en blir `/badge?id=1000`.
3. Endre tallet manuelt, eller bruk et lite løp mot nærliggende ID-er:

   ```bash
   for id in $(seq 1000 1010); do
     curl -s "<URL>/badge?id=$id" | grep -E "KA\\{|Badge-ID"
   done
   ```

4. Badge `1007` tilhører ikke deltakeren og viser internmerknaden med flagget.

**Flagg:** `CTF{not_your_badge_1007}`
