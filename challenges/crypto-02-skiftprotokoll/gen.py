"""
Generer Skiftprotokollen.

Caesar/ROT over norsk alfabet.
Flagg: CTF{rot_med_norsk_alfabet}
"""

from pathlib import Path


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ"
LOWER_ALPHABET = ALPHABET.lower()
SHIFT = 11
FLAG = "CTF{rot_med_norsk_alfabet}"

PLAINTEXT = """SKIFTPROTOKOLL NORDVERK ANLEGG TRE
DAGSKIFTET MELDER NORMAL DRIFT I TANKSYV OG VENTILHUSET
KODE FOR KVELDSVAKT ER CTF{rot_med_norsk_alfabet}
SLUTT MELDING
"""


def caesar(text: str, shift: int) -> str:
    out = []
    for ch in text:
        if ch in ALPHABET:
            out.append(ALPHABET[(ALPHABET.index(ch) + shift) % len(ALPHABET)])
        elif ch in LOWER_ALPHABET:
            out.append(LOWER_ALPHABET[(LOWER_ALPHABET.index(ch) + shift) % len(LOWER_ALPHABET)])
        else:
            out.append(ch)
    return "".join(out)


def main() -> None:
    ciphertext = caesar(PLAINTEXT, SHIFT)
    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "skiftprotokoll.txt").write_text(ciphertext, encoding="utf-8")
    print("[+] Skrev dist/skiftprotokoll.txt")
    print(f"[+] Skift: {SHIFT}")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
