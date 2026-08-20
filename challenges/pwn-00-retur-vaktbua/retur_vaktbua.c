#include <stdio.h>
#include <string.h>
#include <unistd.h>

char *gets(char *s);

static const unsigned char FLAG_XOR[] = {
    0x74, 0x63, 0x71, 0x4c, 0x45, 0x52, 0x43, 0x05,
    0x40, 0x5e, 0x59, 0x68, 0x51, 0x58, 0x45, 0x44,
    0x43, 0x52, 0x68, 0x44, 0x43, 0x52, 0x50, 0x4a
};

__attribute__((noinline, force_align_arg_pointer))
void win(void) {
    char flag[sizeof(FLAG_XOR) + 1];

    for (size_t i = 0; i < sizeof(FLAG_XOR); i++) {
        flag[i] = (char)(FLAG_XOR[i] ^ 0x37);
    }
    flag[sizeof(FLAG_XOR)] = '\0';

    puts("[+] Vaktbua åpner VIP-døren.");
    printf("[+] Flagg: %s\n", flag);
    fflush(stdout);
    _exit(0);
}

void registrer(void) {
    char navn[32];

    puts("=================================");
    puts(" Nordverk - Retur til vaktbua");
    puts("=================================");
    printf("Skriv navnet ditt: ");
    fflush(stdout);

    gets(navn);

    printf("Hei, %s. Du står fortsatt i vanlig kø.\n", navn);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    alarm(30);
    registrer();
    puts("Vaktbua lukker vinduet.");
    return 0;
}
