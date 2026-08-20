"""
LØSNING — Dårlig XOR-vakt (ikke gi til deltakerne!)

Strategi:
  1. Vi kjenner crib "Teknologidagene" finnes i klarteksten.
  2. Skann alle posisjoner i ciphertexten. For hver posisjon i, hent
     ut ct[i:i+16] XOR "Teknologidagene" som kandidat-nøkkelstrøm.
  3. Den ekte nøkkelen er kort og gjentakende, så kandidat-strømmen
     må være periodisk. Test perioder 1..12 og se hvilken som passer.
  4. Bruk den utledede nøkkelen til å dekryptere hele filen,
     og let etter CTF{...}.
"""

import sys
import re
from pathlib import Path

CRIB = b"Teknologidagene"


def find_period(s: bytes, max_period: int = 12) -> int | None:
    """Finn minste p slik at s[i] == s[i % p] for alle i."""
    for p in range(1, max_period + 1):
        if all(s[i] == s[i % p] for i in range(len(s))):
            return p
    return None


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def solve(ct: bytes):
    print(f"[*] Ciphertext: {len(ct)} byte")
    print(f"[*] Crib: {CRIB!r} ({len(CRIB)} byte)")
    print()

    # For hver mulig offset i ciphertexten, prøv å oppdage en periodisk
    # nøkkel når vi XOR-er crib mot den biten.
    for i in range(len(ct) - len(CRIB)):
        candidate = xor(ct[i:i + len(CRIB)], CRIB)
        period = find_period(candidate)
        if period and period >= 3:
            # Skift kandidat-nøkkelen tilbake slik at posisjon 0
            # tilsvarer starten av nøkkelen i kjøretid.
            shift = i % period
            key = candidate[period - shift:period] + candidate[:period - shift]
            key = bytes(key[j % period] for j in range(period))

            # Verifiser ved å dekryptere og sjekke for ASCII-aktig output.
            pt_try = bytes(c ^ key[j % period] for j, c in enumerate(ct))
            if all(0x09 <= b <= 0x7e or b in (0x0a, 0x0d) for b in pt_try):
                print(f"[+] Crib funnet ved offset {i}, periode={period}")
                print(f"[+] Nøkkel: {key!r}")
                print()
                print("=== KLARTEKST ===")
                print(pt_try.decode("utf-8", errors="replace"))
                print("==================")

                m = re.search(rb"CTF\{[^}]+\}", pt_try)
                if m:
                    flag = m.group(0).decode()
                    print(f"\n*** FLAGG: {flag} ***")
                    return flag
                return None

    print("[-] Ingen passende nøkkel funnet.")
    return None


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = Path(__file__).parent.parent / "dist" / "vaktnotat.bin"
    ct = path.read_bytes()
    solve(ct)


if __name__ == "__main__":
    main()
