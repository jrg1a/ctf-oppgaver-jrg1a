#!/usr/bin/env python3
"""Organizer solver for Radiovakten."""

from __future__ import annotations

import re
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "dist" / "radiotrafikk.txt"

LETTERS = {
    1: "E", 3: "A", 4: " ", 5: "S", 6: "I", 7: "U", 9: "D",
    10: "R", 11: "J", 12: "N", 13: "F", 14: "C", 15: "K",
    16: "T", 17: "Z", 18: "L", 19: "W", 20: "H", 21: "Y",
    22: "P", 23: "Q", 24: "O", 25: "B", 26: "G", 28: "M",
    29: "X", 30: "V",
}
FIGURES = {
    1: "3", 3: "-", 4: " ", 5: "'", 6: "8", 7: "7", 10: "4",
    12: ",", 13: "!", 14: ":", 15: "(", 16: "5", 17: '"',
    18: ")", 19: "2", 20: "#", 21: "6", 22: "0", 23: "1",
    24: "9", 25: "?", 26: "&", 28: ".", 29: "/", 30: ";",
}


def main() -> None:
    text = ARTIFACT.read_text(encoding="ascii")
    data = text.split("DATA:\n", 1)[1]
    groups = re.findall(r"\b[01]{5}\b", data)
    mode = LETTERS
    decoded: list[str] = []
    for group in groups:
        value = int(group[::-1], 2)
        if value == 31:
            mode = LETTERS
        elif value == 27:
            mode = FIGURES
        elif value in mode:
            decoded.append(mode[value])

    message = "".join(decoded)
    expected = "RADIO VAKTEN BYTTER MODUS 73"
    if expected not in message:
        raise SystemExit(f"Fant ikke forventet operatørmelding: {message!r}")
    normalized = expected.lower().replace(" ", "_")
    print(f"CTF{{{normalized}}}")


if __name__ == "__main__":
    main()

