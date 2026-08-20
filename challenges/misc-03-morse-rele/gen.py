#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


FLAG = "CTF{MORSE_PA_RELEET_ER_KLASSIKER}"
UNIT_MS = 120

MORSE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "{": "-.--.",
    "}": "-.--.-",
    "_": "..--.-",
}


def main() -> None:
    out = Path(__file__).resolve().parent / "dist" / "relay_log.csv"
    out.parent.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[int, int, str]] = []
    timestamp = 0
    for char in FLAG:
        code = MORSE[char]
        for symbol in code:
            duration = UNIT_MS if symbol == "." else UNIT_MS * 3
            rows.append((timestamp, duration, "ON"))
            timestamp += duration
            rows.append((timestamp, UNIT_MS, "OFF"))
            timestamp += UNIT_MS

        start, duration, state = rows[-1]
        rows[-1] = (start, duration + UNIT_MS * 2, state)
        timestamp += UNIT_MS * 2

    lines = [
        "# Capture: Nordverk relay controller, channel 3",
        "# Unit calibration: shortest ON pulse is one time unit",
        "start_ms,duration_ms,state",
    ]
    lines.extend(f"{start},{duration},{state}" for start, duration, state in rows)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
