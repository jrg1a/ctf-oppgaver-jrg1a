#!/usr/bin/env python3
"""Organizer solver for Vedlegget i rapporten."""

from __future__ import annotations

import base64
import binascii
import re
import zlib
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "dist" / "revisjonsrapport.pdf"


def main() -> None:
    pdf = ARTIFACT.read_bytes()
    for match in re.finditer(
        rb"/Type /EmbeddedFile.*?stream\r?\n(?P<data>.*?)\r?\nendstream",
        pdf,
        re.DOTALL,
    ):
        payload = match.group("data")
        try:
            attachment = zlib.decompress(payload)
        except zlib.error:
            attachment = payload
        for token in re.findall(rb"[A-Za-z0-9+/]{24,}={0,2}", attachment):
            try:
                decoded = base64.b64decode(token, validate=True)
            except (ValueError, binascii.Error):
                continue
            flag = re.search(rb"CTF\{[A-Za-z0-9_]+\}", decoded)
            if flag:
                print(flag.group(0).decode("ascii"))
                return
    raise SystemExit("Fant ikke flagget i PDF vedleggene")


if __name__ == "__main__":
    main()
