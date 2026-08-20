"""
LØSNING — Plakat med ekko (ikke gi til deltakerne!)

  1. Les plakat.png som binær.
  2. Finn IEND-markøren (chunk-type 'IEND' + 4 byte CRC) — alt etter er
     appendet data.
  3. Skann appendet data for base64 og dekod.
"""

import base64
import re
import sys
from pathlib import Path


def find_iend_end(data: bytes) -> int:
    """Returner offset rett etter IEND-chunkens CRC (slutten av gyldig PNG)."""
    idx = data.find(b"IEND")
    if idx == -1:
        raise ValueError("Ingen IEND funnet — ikke en PNG?")
    # IEND-chunk-typen, deretter 4 byte CRC
    return idx + 4 + 4


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1
                else Path(__file__).parent.parent / "dist" / "plakat.png")
    data = path.read_bytes()
    print(f"[*] Leste {len(data)} byte fra {path.name}")

    end = find_iend_end(data)
    appended = data[end:]
    print(f"[*] Gyldig PNG slutter ved byte {end}")
    print(f"[*] Appendet etter IEND: {len(appended)} byte")
    print(f"[*] Innhold: {appended!r}")

    # Plukk ut base64-aktige strenger fra appendet data
    candidates = re.findall(rb"[A-Za-z0-9+/]{8,}={0,2}", appended)
    for c in candidates:
        try:
            decoded = base64.b64decode(c, validate=True)
            text = decoded.decode("utf-8", errors="ignore")
            if "CTF{" in text:
                print(f"\n*** FLAGG: {text} ***")
                return
        except Exception:
            continue

    print("[-] Fant ikke flagget i appendet base64.")


if __name__ == "__main__":
    main()
