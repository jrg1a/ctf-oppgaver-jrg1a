"""
LØSNING — Beredskapsfrasen (ikke gi til deltakerne!)
"""

from pathlib import Path
import re
import sys


KEY = "NORDVERK"


def decrypt(text: str, key: str) -> str:
    out = []
    j = 0
    for ch in text:
        if "A" <= ch <= "Z":
            shift = ord(key[j % len(key)]) - ord("A")
            out.append(chr((ord(ch) - ord("A") - shift) % 26 + ord("A")))
            j += 1
        elif "a" <= ch <= "z":
            shift = ord(key[j % len(key)]) - ord("A")
            out.append(chr((ord(ch) - ord("a") - shift) % 26 + ord("a")))
            j += 1
        else:
            out.append(ch)
    return "".join(out)


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "dist" / "beredskap.txt"
    plaintext = decrypt(path.read_text(encoding="utf-8"), KEY)
    print(plaintext)
    match = re.search(r"CTF\{[^}]+\}", plaintext)
    if match:
        print(f"*** FLAGG: {match.group(0)} ***")
        return 0
    raise SystemExit("Fant ikke flagget")


if __name__ == "__main__":
    raise SystemExit(main())
