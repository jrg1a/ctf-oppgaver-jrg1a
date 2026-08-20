# Registersporet

**Kategori:** Misc
**Poeng:** 175
**Type:** Statiske tekstfiler
**Vanskelighetsgrad:** Medium

---

## Scenario

En operatør brukte Vim til å hente bestemte tegn fra en stor dagbok. Selve
resultatet ble aldri lagret, men et opptak av makroen og den opprinnelige
dagboken er bevart.

Gjenskap arbeidsflyten og finn meldingen som endte i Vim registeret.

---

## Vedlegg

- [`operatordagbok.txt`](dist/operatordagbok.txt)
- [`makroopptak.txt`](dist/makroopptak.txt)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Åpne dagboken i Vim. Makroen søker, flytter markøren og kopierer ett tegn om gangen. |
| 35 poeng | Stor bokstav i et Vim registernavn betyr at nytt innhold legges til i stedet for å overskrive. |
| 70 poeng | Tøm register `z`, ta opp tastene i register `q`, kjør makroen oppgitt antall ganger og vis registrene med `:reg`. |

---
