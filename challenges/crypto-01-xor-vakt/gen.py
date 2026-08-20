"""
CTF Challenge: "Dårlig XOR-vakt" — Crypto, easy

Kort vaktnotat fra Nordverk-anlegget er XOR-kryptert med en kort,
gjentakende nøkkel. Et velkjent uttrykk ("Teknologidagene") inngår
i klarteksten og fungerer som crib.

Flagg: CTF{xor_v4kt_kr1bbsk1lt}
"""

from pathlib import Path

FLAG = "CTF{xor_v4kt_kr1bbsk1lt}"
KEY  = b"NORDVERK"

PLAINTEXT = (
    "VAKTNOTAT - Nordverk Anlegg 3 - Teknologidagene 2026\n"
    "Skift: 06:00-14:00\n"
    "Operatoer: Stein H.\n"
    "\n"
    "Hendelse 04:12 - PLC-2 logger ut/inn-syklus, ingen alarm.\n"
    "Hendelse 06:48 - Tank 7 niva 82 prosent, normal drift.\n"
    "Hendelse 09:30 - Vaktbytte. Ny operatoer overtar.\n"
    "Merknad: Hemmelig tilgangskode for natteskift: " + FLAG + "\n"
    "Slutt vaktnotat - Teknologidagene 2026.\n"
)


def xor_encrypt(plaintext: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(plaintext))


def main():
    pt = PLAINTEXT.encode("utf-8")
    ct = xor_encrypt(pt, KEY)

    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "vaktnotat.bin").write_bytes(ct)
    (out_dir / "vaktnotat.hex").write_text(ct.hex() + "\n")

    print(f"[+] Skrev {len(ct)} byte til dist/vaktnotat.bin")
    print(f"[+] Hex-versjon: dist/vaktnotat.hex")
    print(f"[+] Noekkel (skjult fra deltakere): {KEY!r} ({len(KEY)} byte)")
    print(f"[+] Crib (kjent for deltakere): 'Teknologidagene'")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
