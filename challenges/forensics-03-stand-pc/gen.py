#!/usr/bin/env python3
from __future__ import annotations

import base64
import sqlite3
import tempfile
import zipfile
from pathlib import Path


FLAG = "CTF{historikken_husker_mer}"


def create_history(path: Path) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE urls (
          id INTEGER PRIMARY KEY,
          url TEXT NOT NULL,
          title TEXT,
          visit_count INTEGER,
          last_visit_time INTEGER
        );
        CREATE TABLE keyword_search_terms (
          url_id INTEGER,
          term TEXT
        );
        """
    )
    rows = [
        (1, "https://program.teknologidagene.example/program", "Teknologidagene - program", 7, 1337133700),
        (2, "https://status.nordverk.local/login", "Intern status", 3, 1337133900),
        (3, "https://docs.python.org/3/library/sqlite3.html", "sqlite3 docs", 1, 1337134200),
    ]
    con.executemany("INSERT INTO urls VALUES (?, ?, ?, ?, ?)", rows)
    con.executemany(
        "INSERT INTO keyword_search_terms VALUES (?, ?)",
        [
            (2, "stand session cookie"),
            (3, "sqlite browser profile cookies"),
        ],
    )
    con.commit()
    con.close()


def create_cookies(path: Path) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE cookies (
          creation_utc INTEGER,
          host_key TEXT,
          name TEXT,
          value TEXT,
          path TEXT,
          expires_utc INTEGER,
          is_secure INTEGER,
          is_httponly INTEGER
        );
        """
    )
    encoded = base64.b64encode(FLAG.encode()).decode()
    con.executemany(
        "INSERT INTO cookies VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1337133000, ".nordverk.local", "theme", "standmodus", "/", 0, 0, 0),
            (1337133999, ".nordverk.local", "stand_session", encoded, "/", 0, 1, 1),
            (1337134100, ".conference.local", "lang", "nb", "/", 0, 0, 0),
        ],
    )
    con.commit()
    con.close()


def main() -> None:
    root = Path(__file__).resolve().parent
    out = root / "dist" / "stand_pc.zip"
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        profile = (
            Path(tmp)
            / "Users"
            / "standbruker"
            / "AppData"
            / "Local"
            / "ConferenceBrowser"
            / "User Data"
            / "Default"
        )
        profile.mkdir(parents=True)

        create_history(profile / "History")
        create_cookies(profile / "Cookies")
        (Path(tmp) / "Users" / "standbruker" / "Desktop").mkdir(parents=True)
        (Path(tmp) / "Users" / "standbruker" / "Desktop" / "README.txt").write_text(
            "Demo-PC fra Teknologidagene. Nettleserdata ble tatt vare paa for analyse.\n",
            encoding="utf-8",
        )

        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(Path(tmp).rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(tmp))


if __name__ == "__main__":
    main()
