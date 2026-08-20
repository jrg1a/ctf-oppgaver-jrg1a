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

## Løsningsvei (kun for arrangør)

Dette er en RSA-oppgave med nære primtall. `n` er mye større enn fjorårets
intro-eksempel, men svakheten er fortsatt at `n` kan faktoriseres.

### Steg 1 — Les nøkkelen

`raymond_rsa.json` inneholder `e`, `n` og `c`.

RSA-dekryptering krever privat eksponent `d`, og for å finne `d` må man først
finne `phi(n)`. Det krever faktorene `p` og `q`.

### Steg 2 — Bruk Fermat-faktorisering

Hvis `p` og `q` er nær hverandre, kan vi skrive:

```text
n = p*q = a^2 - b^2 = (a-b)(a+b)
```

Start ved `a = ceil(sqrt(n))` og øk `a` til `a^2 - n` er et perfekt kvadrat.
Da er:

```text
p = a - b
q = a + b
```

### Steg 3 — Dekrypter RSA

```python
import json
import math

data = json.load(open("raymond_rsa.json"))
e, n, c = data["e"], data["n"], data["c"]

a = math.isqrt(n)
if a * a < n:
    a += 1

while True:
    b2 = a * a - n
    b = math.isqrt(b2)
    if b * b == b2:
        break
    a += 1

p = a - b
q = a + b
assert p * q == n

phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)

plaintext = m.to_bytes((m.bit_length() + 7) // 8, "big")
print(plaintext.decode())
```

**Flagg:** `CTF{ferm4t_fant_raymonds_primer}`
