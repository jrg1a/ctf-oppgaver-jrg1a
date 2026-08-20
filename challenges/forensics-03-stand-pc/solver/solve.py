#!/usr/bin/env python3
from __future__ import annotations

import base64
import sqlite3
import tempfile
import zipfile
from pathlib import Path


def main() -> None:
    archive_path = Path(__file__).resolve().parents[1] / "dist" / "stand_pc.zip"
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(archive_path) as archive:
            cookie_name = next(name for name in archive.namelist() if name.endswith("/Cookies"))
            archive.extract(cookie_name, tmp)

        cookie_db = Path(tmp) / cookie_name
        con = sqlite3.connect(cookie_db)
        (value,) = con.execute(
            "SELECT value FROM cookies WHERE name = 'stand_session'"
        ).fetchone()
        con.close()

    print(base64.b64decode(value).decode())


if __name__ == "__main__":
    main()
