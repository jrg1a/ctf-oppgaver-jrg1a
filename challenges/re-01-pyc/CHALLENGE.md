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

## Løsningsvei (kun for arrangør)

### Metode 1 — Dekompilering
```bash
pip install decompyle3
decompyle3 agent.pyc
```
Avslører XOR-logikken og `kryptert`-arrayet direkte.

### Metode 2 — Disassembly
```python
import dis, marshal
f = open("agent.pyc", "rb")
f.read(16)   # hopp over magic + metadata
dis.dis(marshal.loads(f.read()))
```

### Metode 3 — XOR brute force
Ekstraher `kryptert`-bytene fra bytekoden og prøv alle 256 nøkler.
Se etter output som starter med `CTF{`.

**Nøkkel:** `0x4B` ('K')
**Flagg:** `CTF{pyc_r3v3rs3d_4g3nt}`
