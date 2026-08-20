"""
LØSNING — Velkomststrøm (ikke gi til deltakerne!)

Kjeden er hex → base64 → gzip → tekst.
"""

import base64
import gzip
import re
import sys
from pathlib import Path


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1
                else Path(__file__).parent.parent / "dist" / "velkomst.txt")

    hex_data = path.read_text().strip()
    print(f"[*] Leste {len(hex_data)} hex-tegn fra {path.name}")

    step1 = bytes.fromhex(hex_data)
    print(f"[*] Etter hex-dekod: {len(step1)} byte (sannsynligvis base64)")

    step2 = base64.b64decode(step1)
    print(f"[*] Etter base64: {len(step2)} byte (gzip-magic: {step2[:2].hex()})")

    step3 = gzip.decompress(step2).decode("utf-8")
    print(f"[*] Etter gunzip: {len(step3)} tegn klartekst")
    print()
    print("=== KLARTEKST ===")
    print(step3)
    print("==================")

    # Velkomstteksten inneholder en placeholder "CTF{...}" — hopp over den
    # og plukk den ekte flaggstrengen (alle tegn unntatt punkt/whitespace).
    flags = re.findall(r"CTF\{[^}\s.]+\}", step3)
    if flags:
        print(f"\n*** FLAGG: {flags[-1]} ***")


if __name__ == "__main__":
    main()
