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
