# Ukryptert anlegg - kommandoer

Installer avhengigheter:

pip install paho-mqtt==1.6.1

Kjør rekognosering:

python mqtt_recon.py <server>

Hvis oppgaven viser en egen port:

python mqtt_recon.py <server> <port>

Scriptet skriver mottatte MQTT-meldinger i 30 sekunder. Lagre outputen hvis du
vil sammenligne meldinger senere.
