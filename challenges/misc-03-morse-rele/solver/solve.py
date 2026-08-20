#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


REVERSE = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    "-.--.": "{",
    "-.--.-": "}",
    "..--.-": "_",
}


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "dist" / "relay_log.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [
            row
            for row in csv.DictReader(line for line in handle if not line.startswith("#"))
        ]

    on_durations = [int(row["duration_ms"]) for row in rows if row["state"] == "ON"]
    unit = min(on_durations)

    decoded: list[str] = []
    current = ""
    for row in rows:
        duration = int(row["duration_ms"])
        if row["state"] == "ON":
            current += "." if duration < unit * 2 else "-"
        elif current and duration >= unit * 2.5:
            decoded.append(REVERSE[current])
            current = ""

    if current:
        decoded.append(REVERSE[current])

    print("".join(decoded))


if __name__ == "__main__":
    main()
