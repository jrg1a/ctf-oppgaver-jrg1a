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

## Løsningsvei (kun for arrangør)

### Metode 1 — Ghidra / IDA
Last inn binæren. Finn `main()` → `sjekk_tegn()`.
Funksjonen sammenligner input byte-for-byte med `forventet[]`-arrayet:
```
[0x4E, 0x30, 0x72, 0x64, 0x76, 0x65, 0x72, 0x6B, 0x21, 0x3F]
= "N0rdverk!?"
```

### Metode 2 — strace / ltrace
```bash
ltrace ./crackme AAAAAAAAAA 2>&1
```
Viser memory-sammenligningen og avslører passordet indirekte.

### Metode 3 — GDB
```bash
gdb ./crackme
b sjekk_tegn
run AAAAAAAAAA
x/10c &forventet
```

**Passord:** `N0rdverk!?`
**Flagg:** `CTF{cr4ckm3_r3v3rs3d_ok}`
