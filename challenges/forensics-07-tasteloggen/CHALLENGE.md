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

## Løsningsvei (kun for arrangør)

1. Åpne PCAP filen i Wireshark.
2. Filtrer på USB interrupt transfers og se etter datafelt:

   ```text
   usb.transfer_type == 0x01 && usb.capdata
   ```

3. Tastaturrapportene er 8 byte lange. Typisk format er:

   ```text
   modifier, reservert, key1, key2, key3, key4, key5, key6
   ```

   Rapporten `00 00 00 00 00 00 00 00` betyr at tastene slippes.

4. Eksporter `usb.capdata` med tshark eller kopier verdiene fra Wireshark:

   ```bash
   tshark -r tasteloggen.pcap -Y 'usb.transfer_type == 0x01 && usb.capdata' \
     -T fields -e usb.capdata
   ```

5. Oversett HID usage ID til tegn med en vanlig USB HID tastaturtabell. For
   eksempel er `0x04` bokstaven `a`, `0x05` er `b`, `0x28` er Enter, og Shift
   ligger i modifier byte.
6. Den rekonstruerte terminalteksten inneholder en `export` kommando med
   `RECOVERY_CODE`. Verdien er flagget.

Arrangørsolveren parser PCAP og USBPcap headerne direkte:

```bash
python3 solver/solve.py
```

**Flagg:** `CTF{usb_hid_tastene_husker}`
