#!/usr/bin/env python3
"""Generate a local Git forensics challenge with deterministic commits."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


FLAG = "CTF{historikken_husker_alt}"
OUT = Path(__file__).resolve().parent / "dist" / "arkivsynk.zip"
ZIP_TIME = (2026, 6, 26, 12, 0, 0)


def git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def commit(repo: Path, message: str, timestamp: str) -> None:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Nordverk Utvikling",
            "GIT_AUTHOR_EMAIL": "utvikling@nordverk.invalid",
            "GIT_COMMITTER_NAME": "Nordverk Utvikling",
            "GIT_COMMITTER_EMAIL": "utvikling@nordverk.invalid",
            "GIT_AUTHOR_DATE": timestamp,
            "GIT_COMMITTER_DATE": timestamp,
        }
    )
    git(repo, "add", "-A", env=env)
    git(repo, "commit", "-m", message, env=env)


def write(repo: Path, relative: str, content: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def zip_repository(repo: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(repo.rglob("*")):
            if not path.is_file():
                continue
            relative = Path("arkivsynk") / path.relative_to(repo)
            info = zipfile.ZipInfo(relative.as_posix(), ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, path.read_bytes())


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_name:
        repo = Path(temp_name) / "arkivsynk"
        repo.mkdir()
        subprocess.run(
            ["git", "-c", "init.defaultBranch=main", "init", str(repo)],
            check=True,
            capture_output=True,
            text=True,
        )
        shutil.rmtree(repo / ".git" / "hooks", ignore_errors=True)

        write(
            repo,
            "README.md",
            "# Arkivsynk\n\nLite verktøy for å kontrollere nattlige arkivjobber.\n",
        )
        write(repo, "scripts/healthcheck.sh", "#!/bin/sh\necho arkivsynk: ok\n")
        commit(repo, "Initialiser driftsverktøy", "2026-05-04T08:15:00+02:00")

        write(
            repo,
            "config/datasync.env",
            "SYNC_TARGET=sftp://archive.nordverk.invalid/incoming\n"
            "SYNC_USER=archive-worker\n"
            f"ARCHIVE_RECOVERY_CODE={FLAG}\n",
        )
        commit(repo, "Legg til synkroniseringsoppsett", "2026-05-04T09:05:00+02:00")

        write(
            repo,
            "docs/drift.md",
            "# Drift\n\nJobben kjører klokken 02:15 og skriver status til `logs/`.\n",
        )
        write(repo, "scripts/healthcheck.sh", "#!/bin/sh\necho arkivsynk: status=ok\n")
        commit(repo, "Dokumenter nattlig arkivjobb", "2026-05-05T11:20:00+02:00")

        (repo / "config" / "datasync.env").unlink()
        write(repo, ".gitignore", "config/datasync.env\nlogs/\n")
        commit(repo, "Fjern lokal konfigurasjon før deling", "2026-05-06T13:40:00+02:00")

        write(
            repo,
            "config/example.env",
            "SYNC_TARGET=sftp://host/path\nSYNC_USER=service-account\n"
            "ARCHIVE_RECOVERY_CODE=sett_inn_lokal_verdi\n",
        )
        commit(repo, "Legg til eksempelkonfigurasjon", "2026-05-06T14:10:00+02:00")

        write(
            repo,
            "CHANGELOG.md",
            "# Endringer\n\n* Klargjort prosjektet for sikkerhetsgjennomgang.\n",
        )
        commit(repo, "Klargjør leveranse", "2026-05-07T08:30:00+02:00")

        zip_repository(repo, OUT)

    print(f"[+] Skrev {OUT}")
    print(f"[+] Forventet flagg: {FLAG}")


if __name__ == "__main__":
    main()
