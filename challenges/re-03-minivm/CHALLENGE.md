# Virtuell maskin

**Kategori:** Reverse Engineering
**Poeng:** 500
**Type:** Statisk fil (Linux ELF binary)
**Vanskelighetsgrad:** Vanskelig

---

## Scenario

Etterretningen har funnet et avansert program som beskytter en nøkkel
bak en egenutviklet virtuell maskin. Programmet kjører ikke standard
maskinkode, det tolker sin egen bytekode.

Du må forstå instruksjonssettet og reverse-engineere hva maskinen sjekker.

---

## Vedlegg

- [`minivm`](minivm) (Linux x86-64 ELF)

**Kjør slik:**
```bash
chmod +x minivm
./minivm <nøkkel>
```

---

## Flaggformat

```
CTF{<nøkkel>}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 50 poeng | Start med å finne `main()` i Ghidra, det er kortere enn det ser ut |
| 90 poeng | Finn `vm_run()`-funksjonen og kartlegg `switch`-casen, det er instruksjonssettet |
| 130 poeng | Se etter `BYTECODE[]`-arrayet, dump det og analyser mønsteret |
| 180 poeng | Se etter gjentatte blokker som henter ett input-tegn, kombinerer det med en byte og hopper basert på nullresultat. |

---

## VM-instruksjonssett (gis IKKE til deltakerne)

| Opkode | Navn | Operander | Beskrivelse |
|--------|------|-----------|-------------|
| 0x01 | PUSH | imm8 | Dytt umiddelbar verdi på stakken |
| 0x02 | LOAD | idx | Dytt input[idx] på stakken |
| 0x03 | XOR |, | Pop to, dytt XOR |
| 0x04 | ADD | imm8 | Pop en, adder imm8, dytt resultat |
| 0x05 | CMP |, | Pop to, dytt 1 hvis like |
| 0x06 | AND |, | Pop to, dytt AND |
| 0x07 | HALT_OK |, | Avslutt med suksess |
| 0x08 | HALT_FAIL |, | Avslutt med feil |
| 0x09 | JZ | offset | Pop, hopp relativt hvis 0 |

## Løsningsvei (kun for arrangør)

### Steg 1 — Finn bytekoden
I Ghidra: søk etter `BYTECODE[]`-arrayet (ca. 100 bytes).
Alternativt: finn `vm_run()` og se hvilken adresse `vm->code` peker på.

### Steg 2 — Analyser mønsteret
Bytekoden er repetitiv med 8-byte blokker:
```
02 <idx>  — LOAD input[idx]
01 <byte> — PUSH forventet byte
03        — XOR (gir 0 hvis lik)
09 01     — JZ +1 (hopp over HALT_FAIL hvis lik)
08        — HALT_FAIL
```

### Steg 3 — Ekstraher nøkkelen
Samle alle `<byte>`-verdiene etter `PUSH (0x01)`:
```
0x76 0x6D 0x5F 0x6D 0x34 0x67 0x31 0x63 0x5F 0x6B 0x33 0x79
= "vm_m4g1c_k3y"
```

**Flagg:** `CTF{vm_m4g1c_k3y}`
