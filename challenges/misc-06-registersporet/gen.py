#!/usr/bin/env python3
"""Generate a large operator log and a Vim macro recording."""

from __future__ import annotations

import base64
import random
from pathlib import Path


FLAG = "CTF{makroen_samler_spor}"
ROOT = Path(__file__).resolve().parent
LOG_OUT = ROOT / "dist" / "operatordagbok.txt"
MACRO_OUT = ROOT / "dist" / "makroopptak.txt"

EVENTS = (
    "Trykkmåling mottatt fra sone {zone}",
    "Ventiltest fullført uten avvik",
    "Operatør kvitterte rutinemelding {number:04d}",
    "Temperatur stabil etter kontrollrunde",
    "Planlagt synkronisering mot arkivnode",
    "Skiftleder gjennomgikk vedlikeholdslisten",
    "Ingen endring i alarmbildet",
)


def main() -> None:
    encoded = base64.b64encode(FLAG.encode("ascii")).decode("ascii")
    if len(encoded) != 32:
        raise SystemExit("Makroen og writeupen forventer 32 Base64 tegn")

    randomizer = random.Random(0x71A5EED)
    marker_lines = sorted(randomizer.sample(range(8, 272), len(encoded)))
    marker_map = dict(zip(marker_lines, encoded))

    lines = [
        "NORDVERK OPERATORDAGBOK",
        "Terminal: NV-OPS-04",
        "Eksport: 2026-08-19 19:05",
        "",
    ]
    for line_number in range(1, 281):
        if line_number in marker_map:
            character = marker_map[line_number]
            lines.append(
                f"SPOR {line_number:03d} | {character} | kontrollpunkt arkivert"
            )
            continue
        event = randomizer.choice(EVENTS).format(
            zone=randomizer.randint(1, 9),
            number=randomizer.randint(1, 9999),
        )
        hour = 16 + (line_number // 60)
        minute = line_number % 60
        lines.append(f"2026-08-19 {hour:02d}:{minute:02d}:00 INFO {event}")

    macro = [
        "VIM REGISTEROPPTAK",
        "KILDE_REGISTER=q",
        f"REPETISJONER={len(encoded)}",
        "MAAL_REGISTER=Z",
        "OPPTAK=/^SPOR<CR>0f|2l\"Zyl",
        "",
        "Merknad: <CR> betyr Enter i Vims key notation.",
        "",
    ]

    LOG_OUT.parent.mkdir(parents=True, exist_ok=True)
    LOG_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    MACRO_OUT.write_text("\n".join(macro), encoding="utf-8")
    print(f"[+] Skrev {LOG_OUT}")
    print(f"[+] Skrev {MACRO_OUT}")


if __name__ == "__main__":
    main()
