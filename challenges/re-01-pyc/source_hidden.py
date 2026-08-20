# Denne filen kompileres til .pyc og distribueres UTEN denne kildefilen.
# Deltakerne får kun agent.pyc

import sys

def sjekk_agent(kode):
    # Flagget er XOR-kryptert med nøkkel 0x4B ("K" i ASCII)
    kryptert = [
        0x08, 0x1F, 0x0D, 0x30, 0x3B, 0x32, 0x28, 0x14,
        0x39, 0x78, 0x3D, 0x78, 0x39, 0x38, 0x78, 0x2F,
        0x14, 0x7F, 0x2C, 0x78, 0x25, 0x3F, 0x36
    ]
    flagg = "".join(chr(b ^ 0x4B) for b in kryptert)

    if kode == flagg:
        print(f"[+] Identitet bekreftet. Velkommen, agent.")
        print(f"[+] Flagg: {flagg}")
    else:
        print("[-] Ugyldig agentkode. Tilgang nektet.")

if len(sys.argv) != 2:
    print(f"Bruk: python agent.pyc <agentkode>")
    sys.exit(1)

sjekk_agent(sys.argv[1])
