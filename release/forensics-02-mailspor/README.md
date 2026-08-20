# Mailspor

**Kategori:** Forensics
**Poeng:** 150
**Type:** Statisk fil (EML)
**Vanskelighetsgrad:** Lett / Medium

---

## Scenario

En ansatt i Nordverk videresendte en mistenkelig e-post fra messen.
Avsenderen ser nesten riktig ut, men sikkerhetsteamet vil vite hva som
faktisk ligger i meldingen før noen klikker.

Analyser e-posten, sjekk sporene i headerne og dekod MIME-vedlegget.

---

## Vedlegg

- [`mistenkelig_epost.eml`](dist/mistenkelig_epost.eml)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Ikke åpne lenkene i nettleseren. Les e-posten som tekst først. |
| 25 poeng | MIME-vedlegg er ofte base64-kodet. Finn HTML-vedlegget. |
| 50 poeng | Flagget ligger ikke i vanlig brødtekst, men i den dekodede landingssiden. |

---
