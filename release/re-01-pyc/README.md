# Python-spionen

**Kategori:** Reverse Engineering
**Poeng:** 150
**Type:** Statisk fil (.pyc)
**Vanskelighetsgrad:** Lett

---

## Scenario

Du har kommet over en kompilert Python-fil fra et etterretningsnettverk.
Programmet validerer en agentkode, men kildefilen er ikke tilgjengelig.

Klarer du å finne koden?

---

## Vedlegg

- [`agent.pyc`](agent.pyc)

**Kjør slik:**
```bash
python3 agent.pyc <agentkode>
```

---

## Flaggformat

Flagget er agentkoden du finner, formatert som `CTF{...}`.

---

## Hints

| Kostnad | Hint |
|---------|------|
| 20 poeng | `strings agent.pyc`, hva ser du? |
| 35 poeng | Dekompiler bytekoden med et Python-bytecode-verktøy, eller inspiser den med `dis`. |
| 50 poeng | Koden bruker en enkeltbyte XOR-nøkkel, prøv alle 256 muligheter |

---
