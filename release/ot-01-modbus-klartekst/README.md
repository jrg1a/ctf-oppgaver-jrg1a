# Modbus i klartekst

**Kategori:** OT / ICS
**Poeng:** 100
**Type:** Statisk fil (ingen server)
**Vanskelighetsgrad:** Lett

---

## Scenario

Sikkerhetsteamet ditt har fanget opp nettverkstrafikk fra anleggets styringsnett.
En tekniker koblet til en PLC og leste ut sensordata, men noe ser mistenkelig ut.

Kan du finne hva som er lagret i PLC-ens holding registers?

---

## Vedlegg

- [`modbus_capture.pcap`](modbus_capture.pcap)

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 25 poeng | Wireshark-filter: `modbus` |
| 40 poeng | Se etter FC=3 (Read Holding Registers), spesielt på adresse 100+ |

---
