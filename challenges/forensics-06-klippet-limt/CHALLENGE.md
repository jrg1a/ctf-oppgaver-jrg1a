# Klippet og limt

**Kategori:** Forensics
**Poeng:** 200
**Type:** Statisk fil
**Vanskelighetsgrad:** Medium

---

## Scenario

Et bildearkiv ble kopiert via et ustabilt mellomlager. I etterkant ligger bare
en binær fil igjen. Ingen av filtypene kjennes igjen direkte, men noen
signaturer dukker opp på mistenkelig jevne avstander.

Rekonstruer innholdet og sett sammen meldingen.

---

## Vedlegg

- [`utklipp.bin`](dist/utklipp.bin)

---

## Flaggformat

```text
CTF{...}
```

---

## Hints

| Kostnad | Hint |
|---------|------|
| Gratis | Søk etter kjente filsignaturer i den binære filen. |
| 40 poeng | PNG starter med samme 8 byte hver gang. Se på avstanden mellom treffene. |
| 80 poeng | Dataene er flettet sammen i like store blokker. Del filen i strømmer og trim hver strøm ved PNG sin `IEND` chunk. |

---

## Løsningsvei (kun for arrangør)

1. Start med filtype og signaturer:

   ```bash
   file utklipp.bin
   xxd -l 1600 utklipp.bin
   binwalk utklipp.bin
   ```

2. `file` kjenner ikke igjen hele filen, men `xxd` eller `binwalk` viser flere
   PNG signaturer. De tre første ligger ved offset `0`, `512` og `1024`.
3. Avstanden viser at blokker på 512 byte fra tre ulike PNG filer er flettet
   sammen i rekkefølge:

   ```text
   bilde1 blokk0, bilde2 blokk0, bilde3 blokk0,
   bilde1 blokk1, bilde2 blokk1, bilde3 blokk1, ...
   ```

4. Del den store filen i grupper på `3 * 512` byte. Første 512 byte i hver
   gruppe hører til bilde 1, neste 512 til bilde 2 og siste 512 til bilde 3.
5. Trim hver rekonstruerte strøm etter PNG chunk `IEND`, og åpne bildene.
   Hvert bilde inneholder en del av flagget.
6. Sett fragmentene sammen i rekkefølge.

En kompakt kontroll kan gjøres slik:

```python
from pathlib import Path

blob = Path("utklipp.bin").read_bytes()
block = 512
streams = [bytearray() for _ in range(3)]

for group in range(0, len(blob), block * 3):
    for index in range(3):
        streams[index] += blob[group + index * block:group + (index + 1) * block]

for index, data in enumerate(streams, 1):
    end = data.index(b"\x00\x00\x00\x00IEND") + 12
    Path(f"rekonstruert-{index}.png").write_bytes(data[:end])
```

Arrangørsolveren gjør samme deinterleaving, parser PNG metadata og skriver ut
flagget:

```bash
python3 solver/solve.py
```

**Flagg:** `CTF{blokker_flettet_tre_veier}`
