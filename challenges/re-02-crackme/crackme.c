/*
 * CTF Challenge: RE-02 — Crackme
 * Kompiler: gcc -o crackme crackme.c -s -O1
 *
 * Passordet er "N0rdverk!?" og flagget genereres fra det.
 * Logikken er delt over flere funksjoner for å gjøre det
 * litt mer jobb å følge i Ghidra, men ltrace avslører mye.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* Hvert tegn i passordet sjekkes mot en transformert versjon */
static const unsigned char forventet[] = {
    0x4E, 0x30, 0x72, 0x64, 0x76, 0x65, 0x72, 0x6B, 0x21, 0x3F
};
static const int PASSORD_LEN = 10;

/* Flagget er XOR-kryptert med passordet (syklusvis) */
static const unsigned char flagg_kryptert[] = {
    0x0D, 0x64, 0x34, 0x1F, 0x15, 0x17, 0x46, 0x08,
    0x4A, 0x52, 0x7D, 0x6F, 0x00, 0x57, 0x00, 0x56,
    0x00, 0x18, 0x12, 0x5B, 0x11, 0x5F, 0x19, 0x19
};
static const int FLAGG_LEN = 24;

static int sjekk_lengde(const char *s) {
    return (int)strlen(s) == PASSORD_LEN;
}

static int sjekk_tegn(const char *s) {
    for (int i = 0; i < PASSORD_LEN; i++) {
        if ((unsigned char)s[i] != forventet[i])
            return 0;
    }
    return 1;
}

static void skriv_flagg(const char *passord) {
    char flagg[FLAGG_LEN + 1];
    for (int i = 0; i < FLAGG_LEN; i++) {
        flagg[i] = flagg_kryptert[i] ^ passord[i % PASSORD_LEN];
    }
    flagg[FLAGG_LEN] = '\0';
    printf("[+] Riktig passord! Flagg: %s\n", flagg);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Bruk: %s <passord>\n", argv[0]);
        return 1;
    }

    if (!sjekk_lengde(argv[1])) {
        puts("[-] Feil lengde.");
        return 1;
    }

    if (!sjekk_tegn(argv[1])) {
        puts("[-] Feil passord.");
        return 1;
    }

    skriv_flagg(argv[1]);
    return 0;
}
