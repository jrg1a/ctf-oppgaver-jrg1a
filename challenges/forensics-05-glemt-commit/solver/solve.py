#!/usr/bin/env python3
"""Organizer solver for Det glemte committet."""

from __future__ import annotations

import re
import subprocess
import tempfile
import zipfile
from pathlib import Path


ARCHIVE = Path(__file__).resolve().parents[1] / "dist" / "arkivsynk.zip"
FLAG_PATTERN = re.compile(r"CTF\{[^}\s]+\}")


def run(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )
    return result.stdout


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_name:
        root = Path(temp_name)
        with zipfile.ZipFile(ARCHIVE) as zf:
            zf.extractall(root)
        repo = root / "arkivsynk"

        print("[*] Commit historikk:")
        print(run(repo, "log", "--all", "--oneline").rstrip())

        revisions = run(repo, "rev-list", "--all").splitlines()
        for revision in revisions:
            result = run(
                repo,
                "grep",
                "-I",
                "-n",
                "-E",
                r"CTF\{[^}]+\}",
                revision,
                check=False,
            )
            match = FLAG_PATTERN.search(result)
            if match:
                print(f"\n[*] Fant hemmeligheten i revisjon {revision[:12]}")
                print(result.strip())
                print(f"\n*** FLAGG: {match.group(0)} ***")
                return

    raise SystemExit("Fant ikke flagg i Git historikken")


if __name__ == "__main__":
    main()

