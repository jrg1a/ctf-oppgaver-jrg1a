"""
LØSNING — Finn scenen (ikke gi til deltakerne!)

Demonstrerer cross-referencing programmatisk:
  1. Plukk ut tittel og tid fra skiltet (her hardkodet — i praksis OCR
     eller manuell avlesning).
  2. Søk programutdraget etter rad som matcher tittel + tid -> sal-bokstav.
  3. Slå opp sal-bokstaven i kodeboken -> flagg-suffiks.
  4. Bygg flagget.
"""

import re
import sys
from pathlib import Path

# I praksis ville deltakerne lest dette av bildet selv
SKILT_TITTEL = "State of Cyber Security 2026"
SKILT_TID    = "11:00"


def main():
    base = Path(sys.argv[1] if len(sys.argv) > 1
                else Path(__file__).parent.parent / "dist")

    program = (base / "program_snapshot.txt").read_text(encoding="utf-8")
    kodebok = (base / "kodebok.md").read_text(encoding="utf-8")

    # Steg 1: finn riktig rad i programmet
    pattern = re.compile(
        rf'{re.escape(SKILT_TID)}\s+Scene\s+([A-Z])\s+-\s+(\S+)\s+"{re.escape(SKILT_TITTEL)}"'
    )
    m = pattern.search(program)
    if not m:
        print("[-] Fant ikke matchende rad i programmet")
        sys.exit(1)
    sal_kode, sal_navn = m.group(1), m.group(2)
    print(f"[+] Match i program: Sal {sal_kode} ({sal_navn})")

    # Steg 2: slå opp sal-koden i kodeboken
    code_pat = re.compile(rf"\|\s*{sal_kode}\s*\|\s*\S+\s*\|\s*(\S+)\s*\|")
    m2 = code_pat.search(kodebok)
    if not m2:
        print("[-] Fant ikke sal-koden i kodeboken")
        sys.exit(1)
    suffix = m2.group(1)

    flag = f"CTF{{{suffix}}}"
    print(f"[+] Flagg-suffiks fra kodebok: {suffix}")
    print(f"\n*** FLAGG: {flag} ***")


if __name__ == "__main__":
    main()
