# Raymonds RSA

**Kategori:** Crypto
**Poeng:** 225
**Type:** Statisk JSON
**Vanskelighetsgrad:** Medium

---

## Scenario

Raymond i Nordverk har sendt en kryptert nøkkelmelding til resepsjonen.
Han bruker RSA og insisterer på at tallene er store nok til en demo.

Noe med nøkkelgenereringen hans virker likevel litt for ryddig.

Finn plaintexten og lever flagget.

---

## Vedlegg

- [`raymond_rsa.json`](dist/raymond_rsa.json), offentlig nøkkel og ciphertext

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 20 poeng | Dette er vanlig RSA: `c = m^e mod n`. Start med å se på `n`. |
| 35 poeng | Du skal ikke angripe `e`. Du skal prøve å faktorisere `n`. |
| 55 poeng | Hvis `p` og `q` ligger nær hverandre, er Fermats faktoriseringsmetode veldig effektiv. |
| 75 poeng | Når `n` er faktorisert, er resten standard RSA-dekryptering med privat eksponent. |

---
