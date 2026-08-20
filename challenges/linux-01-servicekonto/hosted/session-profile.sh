if [ "$(id -un 2>/dev/null)" = "ctfplayer" ] && [ -t 0 ]; then
    if [ -z "${CTF_WORKDIR:-}" ]; then
        CTF_WORKDIR="$(mktemp -d /tmp/ctfplayer.XXXXXX 2>/dev/null || true)"
        export CTF_WORKDIR
        if [ -n "$CTF_WORKDIR" ] && [ -d "$CTF_WORKDIR" ]; then
            chmod 700 "$CTF_WORKDIR" 2>/dev/null || true
            cd "$CTF_WORKDIR" 2>/dev/null || true
            printf '\nArbeidsmappe for denne SSH-sesjonen: %s\n' "$CTF_WORKDIR"
            printf 'README ligger i /home/ctfplayer og er skrivebeskyttet.\n\n'
        fi
    fi
fi
