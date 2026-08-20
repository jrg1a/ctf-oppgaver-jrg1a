#!/usr/bin/env python3
"""Generate a PDF with two embedded text attachments."""

from __future__ import annotations

import base64
import zlib
from pathlib import Path


FLAG = "CTF{pdf_vedlegg_gjemmer_mer}"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist" / "revisjonsrapport.pdf"


def stream_object(dictionary: bytes, data: bytes) -> bytes:
    return dictionary + b"\nstream\n" + data + b"\nendstream"


def build_pdf() -> bytes:
    page_text = (
        b"BT\n/F1 20 Tf\n72 760 Td\n(Nordverk revisjonsrapport) Tj\n"
        b"0 -34 Td\n/F1 11 Tf\n(Status: gjennomgaatt) Tj\n"
        b"0 -18 Td\n(Synlige avvik: ingen) Tj\n"
        b"0 -36 Td\n(Referanse: RV-2026-0819) Tj\nET"
    )
    secret_b64 = base64.b64encode(FLAG.encode("ascii"))
    secret = (
        b"KONTROLLNOTAT\n"
        b"Koding: Base64\n"
        b"Verdi: " + secret_b64 + b"\n"
    )
    decoy = (
        b"OVERFOERINGSNOTAT\n"
        b"Rapporten ble eksportert med dokumentvedlegg aktivert.\n"
        b"Kontroller alle filer som fulgte med dokumentet.\n"
    )

    compressed_secret = zlib.compress(secret)
    compressed_decoy = zlib.compress(decoy)
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R /Names << /EmbeddedFiles 10 0 R >> /PageMode /UseAttachments >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        stream_object(f"<< /Length {len(page_text)} >>".encode(), page_text),
        stream_object(
            f"<< /Type /EmbeddedFile /Subtype /text#2Fplain /Filter /FlateDecode /Length {len(compressed_secret)} >>".encode(),
            compressed_secret,
        ),
        b"<< /Type /Filespec /F (kontrollnotat.txt) /UF (kontrollnotat.txt) /Desc (Internt kontrollnotat) /EF << /F 6 0 R /UF 6 0 R >> >>",
        stream_object(
            f"<< /Type /EmbeddedFile /Subtype /text#2Fplain /Filter /FlateDecode /Length {len(compressed_decoy)} >>".encode(),
            compressed_decoy,
        ),
        b"<< /Type /Filespec /F (lesmeg.txt) /UF (lesmeg.txt) /Desc (Overfoeringsnotat) /EF << /F 8 0 R /UF 8 0 R >> >>",
        b"<< /Names [(kontrollnotat.txt) 7 0 R (lesmeg.txt) 9 0 R] >>",
        b"<< /Title (Nordverk revisjonsrapport) /Author (Internrevisjon) /Subject (Kontroll av dokumentleveranse) /Creator (Nordverk rapportgenerator) >>",
    ]

    pdf = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R /Info 11 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(build_pdf())
    print(f"[+] Skrev {OUT}")


if __name__ == "__main__":
    main()
