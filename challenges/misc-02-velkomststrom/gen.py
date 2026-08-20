"""
CTF Challenge: "Velkomststrøm" — Misc, easy

En "first solve" for nybegynnere. Et velkomstvedlegg er pakket i en
enkel encoding-kjede:

    klartekst -> gzip -> base64 -> hex

Deltakerne må reverse-engineere kjeden steg for steg.

Flagg: CTF{v3lk0mst_str0m_h1tch3d}
"""

import base64
import gzip
from pathlib import Path

FLAG = "CTF{v3lk0mst_str0m_h1tch3d}"

PLAINTEXT = (
    "Velkommen til Nordverk CTF @ Teknologidagene 2026!\n"
    "\n"
    "Du har naa loest din foerste oppgave - den er ment som en mykstart\n"
    "for nye CTF-spillere. Faktisk loesing krever bare en terminal og\n"
    "litt taalmodighet med encoding-kjeder.\n"
    "\n"
    "Hver oppgave i dette settet ender med et flagg paa formen CTF{...}.\n"
    "Lim det inn i scoreboardet, og kos deg videre med festivalen.\n"
    "\n"
    "Velkomstkode: " + FLAG + "\n"
)


def main():
    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)

    raw = PLAINTEXT.encode("utf-8")
    print(f"[*] Klartekst: {len(raw)} byte")

    # Steg 1: gzip
    step1 = gzip.compress(raw)
    print(f"[*] Etter gzip: {len(step1)} byte (magic: {step1[:2].hex()})")

    # Steg 2: base64
    step2 = base64.b64encode(step1)
    print(f"[*] Etter base64: {len(step2)} byte")

    # Steg 3: hex
    step3 = step2.hex().encode()
    print(f"[*] Etter hex: {len(step3)} byte")

    out = out_dir / "velkomst.txt"
    out.write_bytes(step3 + b"\n")
    print(f"[+] Skrev {out.name}")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
