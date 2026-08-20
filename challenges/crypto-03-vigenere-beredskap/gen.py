"""
Generer Beredskapsfrasen.

Vigenere med A-Z og nøkkel NORDVERK.
Flagg: CTF{vigenere_er_fortsatt_klassiker}
"""

from pathlib import Path


KEY = "NORDVERK"
FLAG = "CTF{vigenere_er_fortsatt_klassiker}"

PLAINTEXT = """NORDVERK BEREDSKAPSMELDING
RESERVENOKKELEN TIL DEMOANLEGGET ER LAGRET HOS VAKTLEDER
FLAGGET ER CTF{vigenere_er_fortsatt_klassiker}
SLUTT
"""


def encrypt(text: str, key: str) -> str:
    out = []
    j = 0
    for ch in text:
        upper = ch.upper()
        if "A" <= ch <= "Z":
            shift = ord(key[j % len(key)]) - ord("A")
            out.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
            j += 1
        elif "a" <= ch <= "z":
            shift = ord(key[j % len(key)]) - ord("A")
            out.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
            j += 1
        else:
            out.append(ch)
    return "".join(out)


def main() -> None:
    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "beredskap.txt").write_text(encrypt(PLAINTEXT, KEY), encoding="utf-8")
    print("[+] Skrev dist/beredskap.txt")
    print(f"[+] Nøkkel: {KEY}")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
