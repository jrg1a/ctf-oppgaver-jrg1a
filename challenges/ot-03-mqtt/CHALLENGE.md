# Ukryptert anlegg

**Kategori:** OT / ICS
**Poeng:** 300
**Type:** Container (MQTT-broker)
**Vanskelighetsgrad:** Medium
**Container:** 2 av 10

---

## Scenario

Et industrianlegg bruker MQTT for å sende sensordata og styre prosesser.
Ingen kryptering. Ingen nettverkssegmentering. Anonym tilkobling er aktivert.

Noen har glemt å fjerne et debug-topic fra produksjonsmiljøet.

Koble til brokeren og se hva som flyter rundt på nettverket, ikke alt
er ment å være offentlig.

---

## Tilkobling

Server: <IP>:<PORT> (MQTT)

---

## Vedlegg

- [`mqtt_recon.py`](mqtt_recon.py)
- [`mqtt_kommandoer.md`](mqtt_kommandoer.md)

Installer avhengigheter:

pip install paho-mqtt==1.6.1

Kjør rekognosering (lytter i 30 sekunder):

python mqtt_recon.py <IP> <PORT>

---

## Flaggformat

CTF{...}

---

## Hints

| Kostnad | Hint |
|---------|------|
| 35 poeng | Se på topic-navn og payload sammen. Hierarkiet sier ofte hva meldingen brukes til. |
| 65 poeng | Debug-meldinger kan lekke mer enn statusverdier. |
| 100 poeng | Når du finner credentials, må MQTT-klienten autentisere før den ber om det sikrede styretopicet. |

---

## Løsningsvei (kun for arrangør)

1. Kjør `mqtt_recon.py` og abonner på `#` (alle topics)
2. Vent ~15 sekunder til `plant/maintenance/debug` publiseres
3. Legg merke til JSON-payloaden med `"user"` og `"pass"`
4. Koble til på nytt med disse credentials
5. Subscribe på `plant/control/secure` → flagget er i JSON-payloaden

```python
import paho.mqtt.client as mqtt

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set("operator", "Pl4tform42!")
client.connect("<IP>", 1883)
client.subscribe("plant/control/secure")
```

**Flagg:** `CTF{mqtt_w1ldcard_cr3d_l3ak}`
