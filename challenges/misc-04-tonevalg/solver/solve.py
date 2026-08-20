#!/usr/bin/env python3
"""Organizer solver for Tonevalg using DTMF frequency detection."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path


WAV = Path(__file__).resolve().parents[1] / "dist" / "tonevalg.wav"
LOW = (697, 770, 852, 941)
HIGH = (1209, 1336, 1477, 1633)
KEYPAD = (
    ("1", "2", "3", "A"),
    ("4", "5", "6", "B"),
    ("7", "8", "9", "C"),
    ("*", "0", "#", "D"),
)
MULTITAP = {
    "2": "ABC",
    "3": "DEF",
    "4": "GHI",
    "5": "JKL",
    "6": "MNO",
    "7": "PQRS",
    "8": "TUV",
    "9": "WXYZ",
}


def read_samples(path: Path) -> tuple[int, list[int]]:
    with wave.open(str(path), "rb") as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError("Forventer mono WAV med 16 bit samples")
        rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
    return rate, list(struct.unpack(f"<{len(frames) // 2}h", frames))


def active_segments(samples: list[int], rate: int) -> list[list[int]]:
    frame_size = max(1, round(rate * 0.01))
    active = []
    for offset in range(0, len(samples), frame_size):
        frame = samples[offset : offset + frame_size]
        rms = math.sqrt(sum(value * value for value in frame) / max(1, len(frame)))
        active.append(rms > 1200)

    segments = []
    start = None
    for index, is_active in enumerate(active + [False]):
        if is_active and start is None:
            start = index * frame_size
        elif not is_active and start is not None:
            end = min(index * frame_size, len(samples))
            if end - start >= rate * 0.05:
                segments.append(samples[start:end])
            start = None
    return segments


def goertzel_power(samples: list[int], rate: int, frequency: int) -> float:
    omega = 2.0 * math.pi * frequency / rate
    coefficient = 2.0 * math.cos(omega)
    previous = 0.0
    previous_two = 0.0
    for sample in samples:
        current = sample + coefficient * previous - previous_two
        previous_two = previous
        previous = current
    return previous_two**2 + previous**2 - coefficient * previous * previous_two


def detect_symbol(samples: list[int], rate: int) -> str:
    low_index = max(
        range(len(LOW)), key=lambda index: goertzel_power(samples, rate, LOW[index])
    )
    high_index = max(
        range(len(HIGH)),
        key=lambda index: goertzel_power(samples, rate, HIGH[index]),
    )
    return KEYPAD[low_index][high_index]


def decode_multitap(sequence: str) -> str:
    output = []
    for group in sequence.split("#"):
        if group == "0":
            output.append(" ")
            continue
        if not group or len(set(group)) != 1 or group[0] not in MULTITAP:
            raise ValueError(f"Ugyldig flertrykksgruppe: {group!r}")
        letters = MULTITAP[group[0]]
        if len(group) > len(letters):
            raise ValueError(f"For mange trykk i gruppe: {group!r}")
        output.append(letters[len(group) - 1])
    return "".join(output)


def main() -> None:
    rate, samples = read_samples(WAV)
    segments = active_segments(samples, rate)
    sequence = "".join(detect_symbol(segment, rate) for segment in segments)
    message = decode_multitap(sequence)
    flag = "CTF{" + message.lower().replace(" ", "_") + "}"

    print(f"[*] Fant {len(segments)} toner")
    print(f"[*] DTMF: {sequence}")
    print(f"[*] Melding: {message}")
    print(f"\n*** FLAGG: {flag} ***")


if __name__ == "__main__":
    main()

