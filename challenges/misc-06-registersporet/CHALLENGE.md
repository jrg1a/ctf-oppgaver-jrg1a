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

## Løsningsvei (kun for arrangør)

1. Åpne `operatordagbok.txt` i Vim.
2. Tøm målregisteret:

   ```vim
   :let @z=''
   ```

3. Start opptak med `qq`. Tast sekvensen fra `makroopptak.txt`. Skriv søket
   `/^SPOR`, trykk Enter, og tast deretter `0f|2l"Zyl`. Avslutt opptaket med
   `q`.
4. Kjør makroen antallet ganger som står i opptaket:

   ```vim
   32@q
   :reg z
   ```

5. Register `z` inneholder en Base64 streng. Dekod den med:

   ```bash
   base64 -d
   ```

Makroen kan også tolkes manuelt. Den søker etter neste linje som begynner med
`SPOR`, går til det første `|` tegnet, flytter to tegn mot høyre og legger det
aktuelle tegnet til register `Z`.

**Flagg:** `CTF{makroen_samler_spor}`
