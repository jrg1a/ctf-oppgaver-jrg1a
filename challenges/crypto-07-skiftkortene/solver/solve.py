#!/usr/bin/env python3
"""Organizer solver for Skiftkortene."""

from __future__ import annotations

import re
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "dist" / "skiftkort.txt"


def parse_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key] = value
    return fields


def restore_block(block: str, permutation: list[int]) -> str:
    restored = ["?"] * len(permutation)
    for output_position, input_position in enumerate(permutation):
        restored[input_position] = block[output_position]
    return "".join(restored)


def main() -> None:
    fields = parse_fields(ARTIFACT.read_text(encoding="utf-8"))
    block_size = int(fields["BLOKKLENGDE"])
    known = fields["KJENT_KLAR_1"]
    sent = fields["KJENT_SENDT_1"]
    permutation = [known.index(character) for character in sent]

    candidate = "".join(
        restore_block(fields["UKJENT_SENDT"][start:start + block_size], permutation)
        for start in range(0, len(fields["UKJENT_SENDT"]), block_size)
    ).rstrip(fields["FYLLTEGN"])

    match = re.search(r"CTF\{[A-Za-z0-9_]+\}", candidate)
    if not match:
        raise SystemExit(f"Fant ikke flagg i rekonstruert tekst: {candidate!r}")
    print(match.group(0))


if __name__ == "__main__":
    main()

