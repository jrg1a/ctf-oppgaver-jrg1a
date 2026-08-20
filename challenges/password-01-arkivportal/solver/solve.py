#!/usr/bin/env python3
"""Organizer solver for Arkivportalen."""

from __future__ import annotations

import base64
import re
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def crack_zip(zip_path: Path, wordlist_path: Path) -> str:
    with zipfile.ZipFile(zip_path) as archive:
        first_file = next(name for name in archive.namelist() if not name.endswith("/"))
        for password in wordlist_path.read_text(encoding="utf-8").splitlines():
            try:
                archive.read(first_file, pwd=password.encode("utf-8"))
            except RuntimeError:
                continue
            return password
    raise RuntimeError("Fant ikke ZIP-passord")


def fnv1a(text: str) -> int:
    value = 2166136261
    for byte in text.encode("utf-8"):
        value ^= byte
        value = (value * 16777619) & 0xFFFFFFFF
    return value


def main() -> int:
    zip_path = DIST / "standarkiv.zip"
    wordlist_path = DIST / "passordliste.txt"
    password = crack_zip(zip_path, wordlist_path)
    print(f"[+] ZIP-passord: {password}")

    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(tmp, pwd=password.encode("utf-8"))

        log_text = (tmp / "logger" / "hendelser.log").read_text(encoding="utf-8")
        encoded = re.search(r"dagskode_b64=([A-Za-z0-9+/=]+)", log_text).group(1)
        decoded = base64.b64decode(encoded).decode("utf-8")
        dagskode = decoded.split("-", 1)[1].lower()
        print(f"[+] Dagskode: {dagskode}")

        portal = (tmp / "portal" / "portal.html").read_text(encoding="utf-8")
        expected = int(re.search(r"const expected = (\d+);", portal).group(1))
        if fnv1a(dagskode) != expected:
            raise RuntimeError("Dagskode matcher ikke portalhash")

        cipher = [
            int(value)
            for value in re.search(r"const cipher = \[([^\]]+)\];", portal)
            .group(1)
            .split(",")
        ]
        flag = "".join(
            chr(value ^ ord(dagskode[index % len(dagskode)]))
            for index, value in enumerate(cipher)
        )
        print(flag)
        if not re.fullmatch(r"CTF\{[^}]+\}", flag):
            raise RuntimeError("Fant ikke gyldig flagg")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
