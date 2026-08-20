#!/usr/bin/env python3
"""Solver for Mailspor."""

from __future__ import annotations

import re
from email import policy
from email.parser import BytesParser
from pathlib import Path


EML = Path(__file__).resolve().parents[1] / "dist" / "mistenkelig_epost.eml"


def main() -> None:
    msg = BytesParser(policy=policy.default).parsebytes(EML.read_bytes())

    print(f"From: {msg['from']}")
    print(f"Reply-To: {msg['reply-to']}")
    print(f"Authentication-Results: {msg['authentication-results']}")

    for part in msg.walk():
        filename = part.get_filename()
        if not filename:
            continue
        payload = part.get_content()
        match = re.search(r"CTF\{[^}]+\}", payload)
        if match:
            print(f"\n[+] Fant flagg i {filename}")
            print(f"*** FLAGG: {match.group(0)} ***")
            return

    raise SystemExit("Fant ikke CTF{...} i MIME-vedleggene")


if __name__ == "__main__":
    main()

