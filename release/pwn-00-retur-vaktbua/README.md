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
