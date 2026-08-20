FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        socat && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/chal

COPY buffer.c /opt/chal/buffer.c
COPY buffer /opt/chal/buffer
COPY flag.txt /flag.txt

# Tjenesten maa kjoere samme binær som deltakerne faar som vedlegg.
RUN chmod 755 /opt/chal/buffer && \
    chmod 644 /flag.txt

# Lag uprivilegert bruker
RUN groupadd -r -g 1000 ctf && \
    useradd -r -u 1000 -g ctf -m -s /usr/sbin/nologin ctf && \
    chown -R root:ctf /opt/chal /flag.txt && \
    chmod 750 /opt/chal && \
    chmod 640 /flag.txt

EXPOSE 9999

# socat: en frisk prosess per forbindelse, 60s timeout (alarm i binaeren).
# Maks 16 samtidige forbindelser per IP.
CMD ["socat", "-T60", "TCP-LISTEN:9999,reuseaddr,fork", \
     "EXEC:/opt/chal/buffer,stderr,setsid,setgid=1000,setuid=1000"]
