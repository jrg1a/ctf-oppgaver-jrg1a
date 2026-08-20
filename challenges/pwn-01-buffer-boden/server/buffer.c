// CTF Challenge: "Buffer på boden" — Pwn, medium
//
// En liten interaktiv "messe-bod" som registrerer besoekende.
// Sårbarhet: gets() inn i en 64-byte buffer.
// Maal: hopp til win() (ret2win), faa printet flagget.
//
// Kompiler:
//   gcc -fno-stack-protector -no-pie -m64 -O0 -o buffer buffer.c
//
// Flagg: CTF{buffer_p4_b0den_ret2win}

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void win(void) {
    FILE *f = fopen("/flag.txt", "r");
    if (!f) {
        puts("[!] flag.txt mangler — kontakt arrangoer.");
        return;
    }
    char buf[128];
    if (fgets(buf, sizeof(buf), f)) {
        printf("[+] Velkommen som VIP-gjest! Flagg: %s", buf);
    }
    fclose(f);
    fflush(stdout);
}

void greet(void) {
    char name[64];
    puts("=================================");
    puts(" Nordverk - Velkomstbod");
    puts("=================================");
    puts("");
    printf("Skriv inn besoekende sitt navn: ");
    fflush(stdout);

    // Sårbar: gets() har ingen lengdesjekk.
    gets(name);

    printf("Hei, %s! Du er logget som vanlig gjest.\n", name);
    fflush(stdout);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    alarm(60);  // 60s timeout per forbindelse
    greet();
    puts("Ha en fin dag paa Teknologidagene!");
    return 0;
}
