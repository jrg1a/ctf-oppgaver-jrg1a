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
