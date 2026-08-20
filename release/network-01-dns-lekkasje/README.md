# DNS i sidesporet

**Kategori:** Network
**Poeng:** 125
**Type:** Statisk fil (PCAP)
**Vanskelighetsgrad:** Lett

---

## Scenario

Nordverk oppdaget uvanlig DNS-trafikk fra en maskin som ble brukt under
riggingen til Teknologidagene. Det ser ikke ut som klassisk surfing, men
heller ikke som en stor filoverføring.

Analyser trafikken og finn hva som ble smuglet ut via DNS.

---

## Vedlegg

- [`dns_lekkasje.pcap`](dist/dns_lekkasje.pcap)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Filtrer på `dns`. Hvilke domener skiller seg ut fra vanlig trafikk? |
| 25 poeng | Se på subdomenene under `exfil.ctf-lab.nordverk.local`. |
| 50 poeng | Første label har både rekkefølge og hex-data. Sortér på tallet og dekod hex. |

---
