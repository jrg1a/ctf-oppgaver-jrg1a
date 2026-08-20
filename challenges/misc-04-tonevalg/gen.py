#!/usr/bin/env python3
"""Generate a real DTMF WAV file for Tonevalg."""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


FLAG = "CTF{tone_fra_sentral}"
MESSAGE = "TONE FRA SENTRAL"
OUT = Path(__file__).resolve().parent / "dist" / "tonevalg.wav"

SAMPLE_RATE = 16000
TONE_SECONDS = 0.115
GAP_SECONDS = 0.055
AMPLITUDE = 11800

DTMF = {
    "1": (697, 1209),
    "2": (697, 1336),
    "3": (697, 1477),
    "A": (697, 1633),
    "4": (770, 1209),
    "5": (770, 1336),
    "6": (770, 1477),
    "B": (770, 1633),
    "7": (852, 1209),
    "8": (852, 1336),
    "9": (852, 1477),
    "C": (852, 1633),
    "*": (941, 1209),
    "0": (941, 1336),
    "#": (941, 1477),
    "D": (941, 1633),
}

MULTITAP = {
    "A": "2",
    "B": "22",
    "C": "222",
    "D": "3",
    "E": "33",
    "F": "333",
    "G": "4",
    "H": "44",
    "I": "444",
    "J": "5",
    "K": "55",
    "L": "555",
    "M": "6",
    "N": "66",
    "O": "666",
    "P": "7",
    "Q": "77",
    "R": "777",
    "S": "7777",
    "T": "8",
    "U": "88",
    "V": "888",
    "W": "9",
    "X": "99",
    "Y": "999",
    "Z": "9999",
}


def encode_message(message: str) -> str:
    tokens = ["0" if char == " " else MULTITAP[char] for char in message]
    return "#".join(tokens)


def silence(seconds: float, rng: random.Random) -> list[int]:
    return [rng.randint(-90, 90) for _ in range(round(seconds * SAMPLE_RATE))]


def tone(symbol: str, rng: random.Random) -> list[int]:
    low, high = DTMF[symbol]
    count = round(TONE_SECONDS * SAMPLE_RATE)
    fade = round(0.006 * SAMPLE_RATE)
    samples = []
    for index in range(count):
        envelope = 1.0
        if index < fade:
            envelope = index / fade
        elif index >= count - fade:
            envelope = (count - index - 1) / fade
        value = (
            math.sin(2 * math.pi * low * index / SAMPLE_RATE)
            + math.sin(2 * math.pi * high * index / SAMPLE_RATE)
        )
        value = value * (AMPLITUDE / 2) * envelope + rng.randint(-180, 180)
        samples.append(max(-32768, min(32767, round(value))))
    return samples


def main() -> None:
    rng = random.Random(26062026)
    sequence = encode_message(MESSAGE)
    samples = silence(0.35, rng)
    for symbol in sequence:
        samples.extend(tone(symbol, rng))
        samples.extend(silence(GAP_SECONDS, rng))
    samples.extend(silence(0.35, rng))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))

    print(f"[+] Skrev {OUT}")
    print(f"[+] DTMF sekvens: {sequence}")
    print(f"[+] Forventet flagg: {FLAG}")


if __name__ == "__main__":
    main()

