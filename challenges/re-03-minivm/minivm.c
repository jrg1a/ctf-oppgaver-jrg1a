/*
 * CTF Challenge: RE-03 — Mini-VM
 * Kompiler: gcc -o minivm minivm.c -s -O1
 *
 * En liten stack-basert virtuell maskin kjører et program som
 * validerer en hemmelig nøkkelstreng.
 *
 * VM-instruksjoner:
 *   0x01 PUSH <imm8>  — dytt umiddelbar verdi på stakken
 *   0x02 LOAD <idx>   — dytt input[idx] på stakken
 *   0x03 XOR          — pop to verdier, dytt XOR-resultat
 *   0x04 ADD <imm8>   — pop en verdi, adder imm8, dytt resultat
 *   0x05 CMP          — pop to verdier, dytt 1 hvis like, 0 ellers
 *   0x06 AND          — pop to verdier, dytt bitwise AND
 *   0x07 HALT_OK      — avslutt med suksess
 *   0x08 HALT_FAIL    — avslutt med feil
 *   0x09 JZ <offset>  — pop verdi, hopp relativ offset hvis null
 *
 * Bytekoden under validerer at input er riktig nøkkel.
 * Flagget = "CTF{" + nøkkel + "}"
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define STACK_SIZE 64
#define MAX_INPUT  32

typedef struct {
    uint8_t  stack[STACK_SIZE];
    int      sp;        /* stack pointer */
    int      ip;        /* instruction pointer */
    uint8_t *code;
    int      code_len;
    uint8_t *input;
    int      input_len;
    int      halted;
    int      success;
} VM;

static void vm_push(VM *vm, uint8_t val) {
    if (vm->sp >= STACK_SIZE) { vm->halted = 1; return; }
    vm->stack[vm->sp++] = val;
}

static uint8_t vm_pop(VM *vm) {
    if (vm->sp <= 0) { vm->halted = 1; return 0; }
    return vm->stack[--vm->sp];
}

static void vm_run(VM *vm) {
    while (!vm->halted && vm->ip < vm->code_len) {
        uint8_t op = vm->code[vm->ip++];
        uint8_t a, b;
        int8_t  offset;

        switch (op) {
            case 0x01: /* PUSH imm8 */
                vm_push(vm, vm->code[vm->ip++]);
                break;
            case 0x02: /* LOAD idx */
                a = vm->code[vm->ip++];
                vm_push(vm, (a < vm->input_len) ? vm->input[a] : 0);
                break;
            case 0x03: /* XOR */
                a = vm_pop(vm); b = vm_pop(vm);
                vm_push(vm, a ^ b);
                break;
            case 0x04: /* ADD imm8 */
                a = vm_pop(vm);
                vm_push(vm, a + vm->code[vm->ip++]);
                break;
            case 0x05: /* CMP */
                a = vm_pop(vm); b = vm_pop(vm);
                vm_push(vm, (a == b) ? 1 : 0);
                break;
            case 0x06: /* AND */
                a = vm_pop(vm); b = vm_pop(vm);
                vm_push(vm, a & b);
                break;
            case 0x07: /* HALT_OK */
                vm->halted = 1; vm->success = 1;
                break;
            case 0x08: /* HALT_FAIL */
                vm->halted = 1; vm->success = 0;
                break;
            case 0x09: /* JZ offset */
                offset = (int8_t)vm->code[vm->ip++];
                a = vm_pop(vm);
                if (a == 0) vm->ip += offset;
                break;
            default:
                vm->halted = 1;
        }
    }
}

/*
 * Bytekoden validerer nøkkelen "vm_m4g1c_k3y" tegn for tegn.
 *
 * For hvert tegn i:
 *   LOAD i          → dytt input[i]
 *   PUSH expected   → dytt forventet tegn (transformert)
 *   XOR             → XOR de to
 *   PUSH transform  → dytt transformasjonskonstant
 *   CMP             → sjekk om like (XOR-resultat == transformasjonskonstant)
 *   JZ +2           → hopp over HALT_OK hvis ulik (dvs. feil)
 *   HALT_FAIL
 * ... gjenta for alle tegn ...
 * HALT_OK
 *
 * Faktisk sjekk: input[i] XOR key[i] == transform[i]
 * Dvs. input[i] == key[i] XOR transform[i] == expected[i]
 *
 * Nøkkel: "vm_m4g1c_k3y"  (12 tegn)
 */
/*
 * Bytekode-logikk per tegn (bruker XOR, ikke CMP):
 *   LOAD i         → push input[i]
 *   PUSH expected  → push expected byte
 *   XOR            → push (input[i] XOR expected) = 0x00 hvis riktig
 *   JZ +1          → hopp over HALT_FAIL hvis 0 (riktig tegn)
 *   HALT_FAIL      → avslutt med feil hvis vi ikke hoppet
 */
static const uint8_t BYTECODE[] = {
    /* tegn 0: 'v' = 0x76 */
    0x02, 0x00,   /* LOAD 0       */
    0x01, 0x76,   /* PUSH 'v'     */
    0x03,         /* XOR → 0 hvis lik */
    0x09, 0x01,   /* JZ +1        */
    0x08,         /* HALT_FAIL    */

    /* tegn 1: 'm' = 0x6D */
    0x02, 0x01, 0x01, 0x6D, 0x03, 0x09, 0x01, 0x08,

    /* tegn 2: '_' = 0x5F */
    0x02, 0x02, 0x01, 0x5F, 0x03, 0x09, 0x01, 0x08,

    /* tegn 3: 'm' = 0x6D */
    0x02, 0x03, 0x01, 0x6D, 0x03, 0x09, 0x01, 0x08,

    /* tegn 4: '4' = 0x34 */
    0x02, 0x04, 0x01, 0x34, 0x03, 0x09, 0x01, 0x08,

    /* tegn 5: 'g' = 0x67 */
    0x02, 0x05, 0x01, 0x67, 0x03, 0x09, 0x01, 0x08,

    /* tegn 6: '1' = 0x31 */
    0x02, 0x06, 0x01, 0x31, 0x03, 0x09, 0x01, 0x08,

    /* tegn 7: 'c' = 0x63 */
    0x02, 0x07, 0x01, 0x63, 0x03, 0x09, 0x01, 0x08,

    /* tegn 8: '_' = 0x5F */
    0x02, 0x08, 0x01, 0x5F, 0x03, 0x09, 0x01, 0x08,

    /* tegn 9: 'k' = 0x6B */
    0x02, 0x09, 0x01, 0x6B, 0x03, 0x09, 0x01, 0x08,

    /* tegn 10: '3' = 0x33 */
    0x02, 0x0A, 0x01, 0x33, 0x03, 0x09, 0x01, 0x08,

    /* tegn 11: 'y' = 0x79 */
    0x02, 0x0B, 0x01, 0x79, 0x03, 0x09, 0x01, 0x08,

    /* Alle tegn riktige */
    0x07   /* HALT_OK */
};

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Bruk: %s <nøkkel>\n", argv[0]);
        return 1;
    }

    const char *input = argv[1];
    int input_len = (int)strlen(input);

    if (input_len != 12) {
        puts("[-] Feil lengde. Nøkkelen er 12 tegn.");
        return 1;
    }

    VM vm = {0};
    vm.code      = (uint8_t *)BYTECODE;
    vm.code_len  = (int)sizeof(BYTECODE);
    vm.input     = (uint8_t *)input;
    vm.input_len = input_len;

    vm_run(&vm);

    if (vm.success) {
        /* Flagget er nøkkelen pakket inn i CTF{...} */
        printf("[+] Korrekt nøkkel! Flagg: CTF{%s}\n", input);
    } else {
        puts("[-] Feil nøkkel. Den virtuelle maskinen er ikke fornøyd.");
    }

    return vm.success ? 0 : 1;
}
