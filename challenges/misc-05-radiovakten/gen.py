#!/usr/bin/env python3
"""Generate an ITA2 Baudot bit stream."""

from __future__ import annotations

from pathlib import Path


FLAG = "CTF{radio_vakten_bytter_modus_73}"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist" / "radiotrafikk.txt"

LETTERS = {
    "E": 1, "A": 3, " ": 4, "S": 5, "I": 6, "U": 7,
    "D": 9, "R": 10, "J": 11, "N": 12, "F": 13, "C": 14,
    "K": 15, "T": 16, "Z": 17, "L": 18, "W": 19, "H": 20,
    "Y": 21, "P": 22, "Q": 23, "O": 24, "B": 25, "G": 26,
    "M": 28, "X": 29, "V": 30,
}
FIGURES = {
    "3": 1, "-": 3, " ": 4, "'": 5, "8": 6, "7": 7,
    "4": 10, ",": 12, "!": 13, ":": 14, "(": 15, "5": 16,
    '"': 17, ")": 18, "2": 19, "#": 20, "6": 21, "0": 22,
    "1": 23, "9": 24, "?": 25, "&": 26, ".": 28, "/": 29,
    ";": 30,
}
LTRS = 31
FIGS = 27


def encode(message: str) -> list[int]:
    mode = "letters"
    symbols = [LTRS]
    for character in message:
        if character in LETTERS and character not in FIGURES:
            if mode != "letters":
                symbols.append(LTRS)
                mode = "letters"
            symbols.append(LETTERS[character])
        elif character in FIGURES and character not in LETTERS:
            if mode != "figures":
                symbols.append(FIGS)
                mode = "figures"
            symbols.append(FIGURES[character])
        elif character == " ":
            symbols.append(4)
        else:
            raise ValueError(f"Tegnet {character!r} finnes ikke i valgt ITA2 tabell")
    return symbols


def lsb_bits(value: int) -> str:
    return f"{value:05b}"[::-1]


def main() -> None:
    message = "TEST 123 TEST\r\nRADIO VAKTEN BYTTER MODUS 73"
    message = message.replace("\r\n", " ")
    groups = [lsb_bits(symbol) for symbol in encode(message)]
    wrapped = [" ".join(groups[start:start + 18]) for start in range(0, len(groups), 18)]
    content = [
        "NORDVERK RX CAPTURE 08-19",
        "SYMBOL_BITS=5",
        "BIT_ORDER=LSB_FIRST",
        "FRAMING=5N1",
        "",
        "DATA:",
        *wrapped,
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(content), encoding="ascii")
    print(f"[+] Skrev {OUT}")


if __name__ == "__main__":
    main()

