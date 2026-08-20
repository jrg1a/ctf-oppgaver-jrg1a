# Tasteloggen

**Kategori:** Forensics
**Poeng:** 225
**Type:** Statisk fil (USB PCAP)
**Vanskelighetsgrad:** Medium

---

## Scenario

En feilsøkingsmaskin hadde USB logging aktivert mens en operatør skrev noen
kommandoer i terminalen. Nettverksloggen er borte, men USB opptaket ligger
igjen.

Finn teksten som ble skrevet på tastaturet.

---

## Vedlegg

- [`tasteloggen.pcap`](dist/tasteloggen.pcap)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Se etter interrupt transfers fra et USB tastatur. |
| 45 poeng | Tastaturdata ligger i HID rapporter på 8 byte. Byte 0 er modifier, og tastene ligger fra byte 2. |
| 90 poeng | Bruk en USB HID usage table for å oversette keycodes. Husk Shift for store bokstaver og symboler. |

---
