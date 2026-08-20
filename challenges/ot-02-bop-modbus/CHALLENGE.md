# Brønn under press

**Kategori:** OT / ICS
**Poeng:** 300
**Type:** Container (Modbus TCP-server)
**Vanskelighetsgrad:** Medium
**Container:** 1 av 10

---

## Scenario

En offshore-boreplattform er blitt sabotert. BOP-systemet (Blowout Preventer) er
kompromittert via uautentisert Modbus TCP, akkurat slik FrostyGoop-malware
opererte i 2024.

Alarmer er dempet. ESD er forbigått. Trykket stiger.

Du har fått et rekognoserings-script som startpunkt. Analyser systemtilstanden
og gjenopprett sikker drift. Flagget låses opp når systemet er trygt igjen.

---

## Tilkobling

```
Server: <IP>:<PORT> (Modbus TCP)
```

---

## Vedlegg

- [`recon_starter.py`](recon_starter.py)
- [`registerkart.md`](registerkart.md)

**Installer avhengigheter:**
```bash
pip install pymodbus
```

**Kjør rekognosering:**
```bash
python recon_starter.py <IP> <PORT>
```

Bruk ett script eller en interaktiv Modbus-klient når du skriver endringer og
leser flaggregistrene. Tilstanden holdes på samme TCP-tilkobling.

---

## Registerkart

Registerkartet ligger også som vedlegg i `registerkart.md`.

```text
Holding registers
HR0       BOP_STATUS        0 = Lukket/Trygt, 1 = Åpen/Farlig
HR1       TRYKK_BAR         Brønntrykk, normalt < 200 bar
HR2       ESD_AKTIV         0 = Av, 1 = På
HR3       SIGNATUR          0 = OK, 31337 = kompromittert
HR4       VENTIL_POSISJON   0-100 %
HR10-27   FLAGG             Låst til systemet er gjenopprettet

Coils
C0        ESD_BYPASS        False = Normal, True = Bypass aktiv
C1        ALARM_UNDERTRYKK  False = Alarmer på, True = Dempet
C2        FJERNTILGANG      True = Aktivert
C3        TRYGG_TILSTAND    True = System gjenopprettet
```

---

## Flaggformat

```
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| 35 poeng | Recon-scriptet leser bare status. Løsningen krever at du endrer tilstanden. |
| 65 poeng | Les om `write_register()` og `write_coil()` i pymodbus |
| 100 poeng | Noe må skrus av FØR du endrer selve BOP-status |

---

## Løsningsvei (kun for arrangør)

Riktig gjenopprettingssekvens:

```python
client.write_coil(0, False)     # C0: Slå av ESD bypass
client.write_register(0, 0)     # HR0: Lukk BOP
client.write_register(2, 1)     # HR2: Aktiver ESD
client.write_register(4, 0)     # HR4: Steng ventil
client.write_coil(1, False)     # C1: Skru på alarmer
# → Flagget skrives til HR10–HR27
```

**Flagg:** `CTF{bop_r3st0r3d_bl0w0ut_pr3v3nt3d}`
