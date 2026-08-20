"""
CTF Challenge: "USB fra standen" - Forensics, easy/medium.

En USB-pinne ble glemt pa messedisken. ZIP-en inneholder en forenklet
nettleserhistorikk, faktiske nedlastinger og litt vanlig stand-stoy.

Intended path:
  1. Inspiser ZIP-en og finn `history.sqlite`.
  2. Bruk `downloads`-tabellen til a bygge nedlastingstidslinje.
  3. Identifiser standfoto-arkivet som interessant.
  4. Pakk opp arkivet og let i metadata/strings i bildefilene.
  5. Dekod den korte base64-verdien fra PNG-metadata.

Flagg: CTF{usb_h1st_sqlite_jaktet}
"""

from __future__ import annotations

import base64
import io
import json
import shutil
import sqlite3
import struct
import tempfile
import zipfile
import zlib
from pathlib import Path

FLAG = "CTF{usb_h1st_sqlite_jaktet}"
FIXED_ZIP_TIME = (2026, 5, 7, 12, 0, 0)


URLS = [
    ("https://teknologidagene.example/", "Teknologidagene 2026", 5, 1717920000),
    ("https://teknologidagene.example/program/", "Program | Teknologidagene", 3, 1717921200),
    ("https://wiki.nordverk.local/standsetup", "Standoppsett 2026 - Nordverk Wiki", 2, 1717922100),
    ("https://intranet.nordverk.local/leveranser", "Leveranseoversikt", 1, 1717922900),
    ("https://teknologidagene.example/foredrag/state-of-cyber-security-2026", "State of Cyber Security 2026", 4, 1717923500),
    ("https://duckduckgo.com/?q=printer+driver+windows+11", "printer driver - DuckDuckGo", 2, 1717925400),
    ("https://nordverk-share.local/login", "Logg inn", 1, 1717926000),
    ("https://nordverk-share.local/d/standfoto-mai", "Standfoto mai - delt lenke", 1, 1717927210),
    ("https://teknologidagene.example/kart/", "Kart og praktisk info", 2, 1717927900),
]


def zip_add_bytes(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, data)


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def make_png(comment: str, rgb: tuple[int, int, int]) -> bytes:
    """Lag en minimal 1x1 PNG med en tEXt-kommentar."""
    header = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw_scanline = b"\x00" + bytes(rgb)
    idat = zlib.compress(raw_scanline)
    text = b"Comment\x00" + comment.encode("utf-8")
    return (
        header
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"tEXt", text)
        + png_chunk(b"IDAT", idat)
        + png_chunk(b"IEND", b"")
    )


def make_photo_archive() -> bytes:
    encoded_flag = base64.b64encode(FLAG.encode()).decode()
    comments = {
        "IMG_0418.png": "kamera=stand-vest; status=ok",
        "IMG_0419.png": "kamera=stand-vest; status=ok",
        "IMG_0420.png": "kamera=stand-nord; status=uskarp",
        "IMG_0421.png": f"kamera=stand-nord; cache_ref={encoded_flag}",
        "IMG_0422.png": "kamera=stand-sor; status=duplikat",
        "IMG_0423.png": "kamera=stand-sor; status=ok",
        "IMG_0424.png": "kamera=rollup; status=ok",
        "IMG_0425.png": "kamera=rollup; status=ok",
        "IMG_0426.png": "kamera=scene; status=ok",
        "IMG_0427.png": "kamera=scene; status=ok",
        "IMG_0428.png": "kamera=kaffe; status=ikke relevant",
        "IMG_0429.png": "kamera=kaffe; status=ikke relevant",
    }
    manifest = {
        "export": "standfoto-mai",
        "source": "Nordverk stand camera roll",
        "note": "Manifesten er ikke komplett. Metadata i bildefiler er bevart.",
        "files": list(comments),
    }

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zip_add_bytes(zf, "manifest.json", json.dumps(manifest, indent=2).encode())
        for index, (name, comment) in enumerate(comments.items()):
            rgb = ((30 + index * 17) % 255, (80 + index * 23) % 255, (140 + index * 31) % 255)
            zip_add_bytes(zf, f"bilder/{name}", make_png(comment, rgb))
        zip_add_bytes(
            zf,
            "notater/rydding.txt",
            (
                "Sjekket bilder for synlige adgangskort.\n"
                "Ett bilde hadde intern kommentar i metadata og ble markert for gjennomgang.\n"
            ).encode(),
        )
    return buffer.getvalue()


def make_downloads() -> list[tuple[str, str, int, bytes]]:
    photo_archive = make_photo_archive()
    return [
        (
            "program-2026.pdf",
            "https://teknologidagene.example/program/program-2026.pdf",
            1717921260,
            b"%PDF-1.4\n% Placeholder program for Teknologidagene\n",
        ),
        (
            "standoppsett.docx",
            "https://wiki.nordverk.local/standsetup/oppsett.docx",
            1717922160,
            b"PK\x03\x04placeholder docx for standoppsett\n",
        ),
        (
            "leveranseoversikt.xlsx",
            "https://intranet.nordverk.local/leveranser/2026.xlsx",
            1717922960,
            b"PK\x03\x04placeholder xlsx for leveranseoversikt\n",
        ),
        (
            "printer_driver.exe",
            "https://drivers.example.com/printer/v3.exe",
            1717925480,
            b"MZ placeholder PE-binaer for printerdriver\n",
        ),
        (
            "kart_over_omradet.pdf",
            "https://teknologidagene.example/kart/kart.pdf",
            1717925960,
            b"%PDF-1.4\n% Placeholder kart\n",
        ),
        (
            "wifi-info.txt",
            "https://nordverk-share.local/d/wifi-info/raw",
            1717926180,
            b"Gjestewifi: se skilt ved resepsjonen. Ingen flagg her.\n",
        ),
        (
            "standfoto_mai.zip",
            "https://nordverk-share.local/d/standfoto-mai/raw",
            1717927260,
            photo_archive,
        ),
        (
            "kvittering_lunsj.csv",
            "https://teknologidagene.example/mat/kvittering.csv",
            1717928040,
            b"tid,antall,type\n12:10,9,vegetar\n12:10,4,fisk\n",
        ),
    ]


def build_history_db(path: Path, downloads: list[tuple[str, str, int, bytes]]) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    cur = con.cursor()

    cur.execute(
        """
        CREATE TABLE urls (
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT,
            visit_count INTEGER DEFAULT 0,
            last_visit_time INTEGER NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE downloads (
            id INTEGER PRIMARY KEY,
            target_path TEXT NOT NULL,
            tab_url TEXT NOT NULL,
            start_time INTEGER NOT NULL,
            received_bytes INTEGER NOT NULL,
            total_bytes INTEGER NOT NULL,
            mime_type TEXT,
            state INTEGER DEFAULT 1
        )
        """
    )

    for url, title, count, ts in URLS:
        cur.execute(
            "INSERT INTO urls (url, title, visit_count, last_visit_time) VALUES (?, ?, ?, ?)",
            (url, title, count, ts),
        )

    for filename, src_url, ts, content in downloads:
        mime_type = "application/zip" if filename.endswith(".zip") else "application/octet-stream"
        cur.execute(
            "INSERT INTO downloads (target_path, tab_url, start_time, received_bytes, "
            "total_bytes, mime_type, state) VALUES (?, ?, ?, ?, ?, ?, 1)",
            (f"E:\\Downloads\\{filename}", src_url, ts, len(content), len(content), mime_type),
        )

    con.commit()
    con.close()


def main() -> None:
    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)

    tmp_root = Path(tempfile.mkdtemp())
    work = tmp_root / "_build"
    work.mkdir()

    downloads = make_downloads()
    db_path = work / "history.sqlite"
    build_history_db(db_path, downloads)

    dl_dir = work / "downloads"
    dl_dir.mkdir(exist_ok=True)
    for filename, _src, _ts, content in downloads:
        (dl_dir / filename).write_bytes(content)

    (work / "README.txt").write_text(
        "Kopi av funnet USB-pinne. Ikke stol pa filnavn alene.\n",
        encoding="utf-8",
    )
    notes = work / "notes"
    notes.mkdir()
    (notes / "standvakt.txt").write_text(
        "Husk a levere tilbake laserpeker og navneskilt etter siste foredrag.\n",
        encoding="utf-8",
    )
    (notes / "ikke_flagg.txt").write_text(
        "Dette er bare en distraksjon. Ikke alt med klammeparenteser er et flagg.\n",
        encoding="utf-8",
    )

    zip_path = out_dir / "usb_fra_standen.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file_path in sorted(work.rglob("*")):
            if file_path.is_file():
                zip_add_bytes(zf, file_path.relative_to(work).as_posix(), file_path.read_bytes())

    shutil.rmtree(tmp_root)

    print(f"[+] Skrev {zip_path.name}")
    print(f"[+] Inneholder: history.sqlite + {len(downloads)} downloads + ekstra stoy")
    print("[+] Intended: downloads/standfoto_mai.zip -> bilder/IMG_0421.png metadata")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
