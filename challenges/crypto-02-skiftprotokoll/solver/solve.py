"""
LØSNING — Skiftprotokollen (ikke gi til deltakerne!)
"""

from pathlib import Path
import re
import sys


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ"
LOWER_ALPHABET = ALPHABET.lower()


def caesar(text: str, shift: int) -> str:
    out = []
    for ch in text:
        if ch in ALPHABET:
            out.append(ALPHABET[(ALPHABET.index(ch) - shift) % len(ALPHABET)])
        elif ch in LOWER_ALPHABET:
            out.append(LOWER_ALPHABET[(LOWER_ALPHABET.index(ch) - shift) % len(LOWER_ALPHABET)])
        else:
            out.append(ch)
    return "".join(out)


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "dist" / "skiftprotokoll.txt"
    ciphertext = path.read_text(encoding="utf-8")
    for shift in range(len(ALPHABET)):
        plaintext = caesar(ciphertext, shift)
        if "CTF{" in plaintext:
            print(f"[+] Skift: {shift}")
            print(plaintext)
            match = re.search(r"CTF\{[^}]+\}", plaintext)
            if match:
                print(f"*** FLAGG: {match.group(0)} ***")
            return 0
    raise SystemExit("Fant ikke flagget")


if __name__ == "__main__":
    raise SystemExit(main())
