# Samme strøm to ganger

**Kategori:** Crypto
**Poeng:** 200
**Type:** Statisk JSON
**Vanskelighetsgrad:** Medium

---

## Scenario

To sambandspakker ble kryptert av samme nødaggregat. Dokumentasjonen sier at
systemet bruker en XOR basert nøkkelstrøm, men en omstart gjorde at telleren
begynte på nytt. Klarteksten til den første, rutinemessige statusmeldingen er
kjent.

Gjenopprett innholdet i den andre pakken.

---

## Vedlegg

- [`samband.json`](dist/samband.json)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | XOR er sin egen inverse. Skriv de tre relevante bytefølgene under hverandre. |
| 40 poeng | `klartekst_a XOR chiffer_a` gir nøkkelstrømmen som ble brukt på pakke A. |
| 80 poeng | Omstarten gjorde at nøyaktig samme nøkkelstrøm ble brukt fra byte null i pakke B. |

---

## Løsningsvei (kun for arrangør)

1. Les `known_plaintext_a` som byte og dekod `ciphertext_a_hex` fra hex.
2. XOR klarteksten med chifferteksten. Resultatet er nøkkelstrømmen:

   ```text
   K = P_a XOR C_a
   ```

3. Dekod `ciphertext_b_hex` og XOR den med `K`:

   ```text
   P_b = C_b XOR K
   ```

4. Den dekrypterte teksten inneholder flagget. Oppgaven krever ikke at
   deltakeren finner eller gjetter den opprinnelige nøkkelen. Feilen er selve
   gjenbruken av nøkkelstrømmen.

Dette kan gjøres i CyberChef med `From Hex` og `XOR`, eller med et kort skript:

```python
stream = bytes(a ^ b for a, b in zip(known, cipher_a))
plain_b = bytes(a ^ b for a, b in zip(cipher_b, stream))
```

**Flagg:** `CTF{aldri_gjenbruk_en_nokkelstrom}`

