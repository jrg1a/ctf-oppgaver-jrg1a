# Velkomststrøm

**Kategori:** Misc
**Poeng:** 50
**Type:** Statisk fil (tekst)
**Vanskelighetsgrad:** Lett (first solve)

---

## Scenario

Nordverk slipper en velkomstpakke til alle som er innom standen
på Teknologidagene. Pakken er «pakket inn» i flere lag med encoding,
ikke for å gjøre den hemmelig, men som en oppvarmingsoppgave.

Pakk ut og finn velkomstkoden.

---

## Vedlegg

- [`velkomst.txt`](dist/velkomst.txt)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Filen ser ut som ren ASCII, men det er bare *yttersjiktet*. Tre lag totalt. |
| 10 poeng | Første lag består bare av hex-tegn. Gjør hvert lag om til bytes før du vurderer neste. |
| 20 poeng | Etter hex-laget følger en vanlig tekst-encoding og til slutt komprimerte data. |

---

## Løsningsvei (kun for arrangør)

```bash
# 1. Hex-dekoding
xxd -r -p velkomst.txt > step1.b64

# 2. Base64-dekoding
base64 -d step1.b64 > step2.gz

# 3. Gzip-dekompresjon
gunzip -c step2.gz
```

Eller en-linje:
```bash
xxd -r -p velkomst.txt | base64 -d | gunzip
```

**Flagg:** `CTF{v3lk0mst_str0m_h1tch3d}`
