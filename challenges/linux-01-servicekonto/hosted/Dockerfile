FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV FLAG="CTF{suid_b4se64_reads_r00t}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    coreutils \
    findutils \
    file \
    less \
    vim-tiny \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/sshd && \
    echo 'PermitRootLogin no' >> /etc/ssh/sshd_config && \
    echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config && \
    echo 'AllowTcpForwarding no' >> /etc/ssh/sshd_config && \
    echo 'AllowAgentForwarding no' >> /etc/ssh/sshd_config && \
    echo 'X11Forwarding no' >> /etc/ssh/sshd_config && \
    echo 'PermitTunnel no' >> /etc/ssh/sshd_config && \
    echo 'PermitUserEnvironment no' >> /etc/ssh/sshd_config && \
    echo 'PrintMotd yes' >> /etc/ssh/sshd_config && \
    echo 'Banner /etc/ssh/banner' >> /etc/ssh/sshd_config

RUN useradd -m -s /bin/bash ctfplayer && \
    echo 'ctfplayer:ICS_r0ck5!' | chpasswd

RUN printf '%s\n' "$FLAG" > /root/flag.txt && \
    chown root:root /root/flag.txt && \
    chmod 600 /root/flag.txt && \
    chmod 4755 /usr/bin/base64 && \
    printf '%s\n' \
      'export HISTFILE=/dev/null' \
      'export HISTSIZE=0' \
      'export HISTFILESIZE=0' \
      'set +o history 2>/dev/null || true' \
      > /etc/profile.d/ctf-no-history.sh

COPY hosted/banner.txt /etc/ssh/banner
COPY hosted/README.txt /home/ctfplayer/README.txt
COPY hosted/entrypoint.sh /entrypoint.sh
COPY hosted/session-profile.sh /etc/profile.d/ctf-session.sh

RUN chmod +x /entrypoint.sh && \
    chmod 644 /etc/profile.d/ctf-session.sh && \
    chown root:root /home/ctfplayer /home/ctfplayer/README.txt && \
    chmod 755 /home/ctfplayer && \
    chmod 444 /home/ctfplayer/README.txt

EXPOSE 22

CMD ["/entrypoint.sh"]
