"""
Losning - USB fra standen.

Dette er en kontrollsolver for arrangor: den folger intended path uten a
hardkode filen som inneholder flagget.
"""

from __future__ import annotations

import base64
import re
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path


def extract_zip(zip_path: Path, out_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(out_dir)


def find_downloads(db_path: Path) -> list[tuple[str, str, int, int]]:
    con = sqlite3.connect(db_path)
    try:
        return con.execute(
            "SELECT target_path, tab_url, start_time, received_bytes "
            "FROM downloads ORDER BY start_time DESC"
        ).fetchall()
    finally:
        con.close()


def find_cache_ref(photo_dir: Path) -> str:
    pattern = re.compile(rb"cache_ref=([A-Za-z0-9+/=]+)")
    for path in sorted(photo_dir.rglob("*")):
        if not path.is_file():
            continue
        match = pattern.search(path.read_bytes())
        if match:
            print(f"[*] Fant cache_ref i {path.relative_to(photo_dir)}")
            return match.group(1).decode()
    raise RuntimeError("fant ingen cache_ref i fotoarkivet")


def main() -> None:
    zip_path = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else Path(__file__).parent.parent / "dist" / "usb_fra_standen.zip"
    )

    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        extract_zip(zip_path, tmp)
        print(f"[*] Pakket ut til {tmp}")

        rows = find_downloads(tmp / "history.sqlite")
        print(f"[*] Fant {len(rows)} nedlastinger:")
        for target_path, tab_url, start_time, received_bytes in rows:
            print(f"    {start_time}  {received_bytes:5d} bytes  {target_path}  <- {tab_url}")

        archive_row = next(row for row in rows if row[0].endswith("standfoto_mai.zip"))
        archive_name = archive_row[0].split("\\")[-1]
        archive_path = tmp / "downloads" / archive_name
        print(f"\n[*] Mistenkelig fotoarkiv: downloads/{archive_name}")

        photo_dir = tmp / "standfoto"
        extract_zip(archive_path, photo_dir)
        encoded = find_cache_ref(photo_dir)
        decoded = base64.b64decode(encoded).decode()
        print(f"[*] Dekodet cache_ref: {decoded}")

        match = re.search(r"CTF\{[^}\s]+\}", decoded)
        if not match:
            raise RuntimeError("dekodet verdi inneholdt ikke flagg")
        print(f"\n*** FLAGG: {match.group(0)} ***")


if __name__ == "__main__":
    main()
