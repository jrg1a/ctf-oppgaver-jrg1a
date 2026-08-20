#!/usr/bin/env python3
"""Generate Arkivportalen static artifacts."""

from __future__ import annotations

import base64
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

ZIP_PASSWORD = "Nordverk2026!"
DAGSKODE = "nordlys"
FLAG = "CTF{zip_j0hn_b64_portal}"

WORDLIST = [
    "sommer2026",
    "Konferanse2026",
    "Velkommen1",
    "Nordverk2025!",
    "Nordverk2026!",
    "DemoAnlegg",
    "Plattform42",
    "nordlys",
    "Standpassord",
    "Nordverk!",
    "Sikkerhet2026",
]


def fnv1a(text: str) -> int:
    value = 2166136261
    for byte in text.encode("utf-8"):
        value ^= byte
        value = (value * 16777619) & 0xFFFFFFFF
    return value


def encrypted_flag() -> list[int]:
    key = DAGSKODE.encode("utf-8")
    return [byte ^ key[index % len(key)] for index, byte in enumerate(FLAG.encode("utf-8"))]


def write_portal(path: Path) -> None:
    cipher = ", ".join(str(value) for value in encrypted_flag())
    expected_hash = fnv1a(DAGSKODE)
    path.write_text(
        f"""<!doctype html>
<html lang="no">
<head>
  <meta charset="utf-8">
  <title>Nordverk Arkivportal</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 3rem; max-width: 720px; }}
    label, input, button {{ font-size: 1rem; }}
    input {{ padding: .55rem; min-width: 18rem; }}
    button {{ padding: .6rem .9rem; }}
    #resultat {{ margin-top: 1.5rem; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>Nordverk Arkivportal</h1>
  <p>Oppgi dagskode for å åpne statusnotatet fra standarkivet.</p>
  <label for="kode">Dagskode</label>
  <input id="kode" autocomplete="off">
  <button id="apne">Åpne</button>
  <p id="resultat"></p>
  <script>
    const cipher = [{cipher}];
    const expected = {expected_hash};

    function fnv1a(text) {{
      let value = 2166136261;
      for (const ch of new TextEncoder().encode(text)) {{
        value ^= ch;
        value = Math.imul(value, 16777619) >>> 0;
      }}
      return value >>> 0;
    }}

    document.querySelector("#apne").addEventListener("click", () => {{
      const kode = document.querySelector("#kode").value.trim().toLowerCase();
      const resultat = document.querySelector("#resultat");
      if (!kode || fnv1a(kode) !== expected) {{
        resultat.textContent = "Feil dagskode.";
        return;
      }}
      const bytes = cipher.map((value, index) => value ^ kode.charCodeAt(index % kode.length));
      resultat.textContent = new TextDecoder().decode(Uint8Array.from(bytes));
    }});
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    DIST.mkdir(exist_ok=True)
    (DIST / "passordliste.txt").write_text("\n".join(WORDLIST) + "\n", encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        archive_root = tmp / "standarkiv"
        (archive_root / "logger").mkdir(parents=True)
        (archive_root / "notater").mkdir()
        (archive_root / "portal").mkdir()

        (archive_root / "README.txt").write_text(
            "Nordverk standarkiv\n"
            "=====================\n\n"
            "Kopi fra gammel standrigg. Innholdet er ikke ryddet,\n"
            "og logger, notater og lokal portal kan hore sammen.\n",
            encoding="utf-8",
        )
        (archive_root / "logger" / "hendelser.log").write_text(
            "2026-06-08T08:12:03Z INFO  stand sync startet\n"
            "2026-06-08T08:12:15Z DEBUG cache_b64=U1RBVFVTOk9L\n"
            "2026-06-08T08:14:55Z INFO  kopierte besøksstatistikk\n"
            f"2026-06-08T08:17:42Z DEBUG dagskode_b64={base64.b64encode(b'SKIFT-NORDLYS').decode()}\n"
            "2026-06-08T08:18:01Z WARN  gammel portal ligger fortsatt i portal/\n",
            encoding="utf-8",
        )
        (archive_root / "notater" / "kodepraksis.txt").write_text(
            "Kodepraksis for gammel arkivportal\n"
            "=================================\n\n"
            "Dagskoder i logger skrives ofte som SKIFT-<KODEORD>.\n"
            "Portalen bruker bare delen etter SKIFT-, normalisert til små bokstaver.\n",
            encoding="utf-8",
        )
        write_portal(archive_root / "portal" / "portal.html")

        output = DIST / "standarkiv.zip"
        output.unlink(missing_ok=True)
        subprocess.run(
            ["zip", "-qr", "-P", ZIP_PASSWORD, str(output), "README.txt", "logger", "notater", "portal"],
            cwd=archive_root,
            check=True,
        )

    print(f"[+] Skrev {DIST / 'standarkiv.zip'}")
    print(f"[+] Skrev {DIST / 'passordliste.txt'}")
    print(f"[+] ZIP-passord: {ZIP_PASSWORD}")
    print(f"[+] Dagskode: {DAGSKODE}")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
