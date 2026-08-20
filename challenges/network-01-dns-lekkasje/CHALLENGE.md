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

## Løsningsvei (kun for arrangør)

1. Åpne PCAP i Wireshark eller bruk `tshark -r dns_lekkasje.pcap -Y dns`.
2. Finn queries til `NN-<hex>.exfil.ctf-lab.nordverk.local`.
3. Sortér etter `NN`, sett sammen hex-verdiene og dekod til ASCII.

Eksempel:
```bash
python3 solver/solve.py
```

**Flagg:** `CTF{dns_l3kkasje_i_subdomener}`
