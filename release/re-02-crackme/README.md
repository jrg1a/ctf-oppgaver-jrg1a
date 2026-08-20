# Crack meg

**Kategori:** Reverse Engineering
**Poeng:** 350
**Type:** Statisk fil (Linux ELF binary)
**Vanskelighetsgrad:** Medium

---

## Scenario

Et ukjent program dukket opp på en kompromittert server.
Det beskytter tilgang til et flagg bak en passordsjekk.

Finn passordet og hent flagget.

---

## Vedlegg

- [`crackme`](crackme) (Linux x86-64 ELF)

**Kjør slik:**
```bash
chmod +x crackme
./crackme <passord>
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
| 30 poeng | `strings crackme`, hva ser du i binæren? |
| 55 poeng | `ltrace ./crackme testtest`, følg bibliotekskall |
| 90 poeng | Last binæren inn i Ghidra og finn `sjekk_tegn()`-funksjonen |
| 115 poeng | Se etter en tabell med forventede byteverdier. Passordet kan bygges derfra. |

---
