#!/usr/bin/env python3
"""Generate the transposition artifact for Skiftkortene."""

from __future__ import annotations

import random
from pathlib import Path


BLOCK_SIZE = 32
FLAG = "CTF{samme_permutasjon_hver_gang}"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist" / "skiftkort.txt"

CALIBRATION_1 = "0123456789ABCDEFGHIJKLMNOPQRSTUV"
CALIBRATION_2 = "NORDVERK KALIBRERING KORT 0042!!"


def make_permutation() -> list[int]:
    positions = list(range(BLOCK_SIZE))
    random.Random(0x51F7C0DE).shuffle(positions)
    return positions


def pad_blocks(text: str) -> str:
    remainder = len(text) % BLOCK_SIZE
    return text if remainder == 0 else text + "~" * (BLOCK_SIZE - remainder)


def scramble_block(block: str, permutation: list[int]) -> str:
    if len(block) != BLOCK_SIZE:
        raise ValueError("Blokken har feil lengde")
    return "".join(block[position] for position in permutation)


def scramble(text: str, permutation: list[int]) -> str:
    padded = pad_blocks(text)
    return "".join(
        scramble_block(padded[start:start + BLOCK_SIZE], permutation)
        for start in range(0, len(padded), BLOCK_SIZE)
    )


def main() -> None:
    if len(CALIBRATION_1) != BLOCK_SIZE or len(set(CALIBRATION_1)) != BLOCK_SIZE:
        raise SystemExit("Kalibreringsstreng 1 må ha 32 unike tegn")
    if len(CALIBRATION_2) != BLOCK_SIZE:
        raise SystemExit("Kalibreringsstreng 2 må være nøyaktig 32 tegn")

    permutation = make_permutation()
    lines = [
        "NORDVERK KORTSORTERER, DIAGNOSEUTTREKK",
        f"BLOKKLENGDE={BLOCK_SIZE}",
        "FYLLTEGN=~",
        "",
        f"KJENT_KLAR_1={CALIBRATION_1}",
        f"KJENT_SENDT_1={scramble(CALIBRATION_1, permutation)}",
        f"KJENT_KLAR_2={CALIBRATION_2}",
        f"KJENT_SENDT_2={scramble(CALIBRATION_2, permutation)}",
        "",
        f"UKJENT_SENDT={scramble(FLAG, permutation)}",
        "",
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[+] Skrev {OUT}")


if __name__ == "__main__":
    main()

