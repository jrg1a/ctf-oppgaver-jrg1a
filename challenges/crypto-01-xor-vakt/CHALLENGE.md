# Vaktnotatet

**Kategori:** Crypto
**Poeng:** 100
**Type:** Statisk fil (ingen server)
**Vanskelighetsgrad:** Lett

---

## Scenario

Nordverk lekket nylig en intern vaktnotat-fil til en publikumskanal.
Filen er ikke lesbar som tekst, men den virker heller ikke som et vanlig
arkiv, bilde eller dokumentformat.

På anlegget følger vaktnotater en fast mal, og arrangørnavnet dukker ofte
opp i teksten.

Finn klarteksten og les ut tilgangskoden.

---

## Vedlegg

- [`vaktnotat.bin`](dist/vaktnotat.bin), Kryptert vaktnotat
- [`vaktnotat.hex`](dist/vaktnotat.hex), Samme innhold vist som hex

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Start med rå byteverdier. Dette ligner ikke ZIP/PNG/PDF eller vanlig tekstencoding. |
| 10 poeng | Vaktnotater fra dette miljøet pleier å nevne «Teknologidagene». Prøv det som kjent klartekst. |
| 20 poeng | Kombiner kjent klartekst med ciphertext byte for byte. Hvis resultatet begynner å gjenta seg, har du funnet nøkkelstrømmen. |
| 30 poeng | Operasjonen er repeating-key XOR. Nøkkelen er navnet på den fiktive virksomheten i oppgaveteksten. |

---

## Løsningsvei (kun for arrangør)

### Steg 1 — Finn nøkkellengden

Test en Hamming-distanse / Kasiski-aktig analyse, eller bare bruk crib-lengden.

### Steg 2 — Crib-dragging

Vi vet at klarteksten inneholder `"Teknologidagene"`. Søk etter posisjoner
i ciphertexten der `ct[i:i+16] XOR "Teknologidagene"` gir en sammenhengende,
periodisk nøkkel.

### Steg 3 — Dekrypter

Når nøkkelen er funnet (`NORDVERK`), XOR-dekrypter hele filen.
Flagget står på linjen «Hemmelig tilgangskode for natteskift: ...».

**Nøkkel:** `NORDVERK`
**Flagg:** `CTF{xor_v4kt_kr1bbsk1lt}`
