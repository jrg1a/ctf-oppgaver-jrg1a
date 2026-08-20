"""
CTF Challenge: "Plakat med ekko" — Stego, easy

En PNG-plakat for Nordverk / Teknologidagene. Plakaten ser
helt normal ut, men:
  1. tEXt-metadata inneholder et hint ("ekkoet ligger bak rammen, base64").
  2. Etter PNG-ens IEND-chunk er det appendet ekstra data — en
     base64-streng som dekoder til flagget.

Flagg: CTF{plakat_3kk0_b4k_1end}
"""

import base64
import struct
import zlib
from pathlib import Path

FLAG = "CTF{plakat_3kk0_b4k_1end}"


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    """Bygg en gyldig PNG-chunk: length(4) + type(4) + data + crc(4)."""
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def build_png(width: int, height: int) -> bytes:
    """Bygg en enkel PNG fra bunnen av (uten Pillow-avhengighet)."""
    sig = b"\x89PNG\r\n\x1a\n"

    # IHDR: 8-bit RGB
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    # tEXt: ledetraad
    text_key = b"Comment"
    text_val = (
        b"Teknologidagene 2026 - poster v1. "
        b"Ekkoet ligger bak rammen (base64). "
        b"Siste tekstlinje i filen er base64. Bruk `tail -n 1`."
    )
    text = text_key + b"\x00" + text_val

    # tEXt: ekstra (flagg-relaterte ord, men IKKE flagget selv)
    artist_key = b"Artist"
    artist_val = b"Nordverk Sikkerhetsteam"
    artist = artist_key + b"\x00" + artist_val

    # IDAT: enkel grafikk (rad for rad, gradient + tekst-aktig stripe)
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter byte = None
        for x in range(width):
            r = (x * 255) // width
            g = (y * 255) // height
            b = 80 + ((x + y) % 60)
            # Tegn en horisontal "tittel-stripe" rundt y=20-50 i moerk farge
            if 20 <= y <= 50 and 30 <= x <= width - 30:
                r, g, b = 30, 30, 60
            raw.extend([r & 0xFF, g & 0xFF, b & 0xFF])
    idat = zlib.compress(bytes(raw), level=6)

    return (
        sig
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"tEXt", text)
        + png_chunk(b"tEXt", artist)
        + png_chunk(b"IDAT", idat)
        + png_chunk(b"IEND", b"")
    )


def main():
    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)

    png = build_png(width=600, height=300)

    # Append base64-versjon av flagget *etter* IEND-chunken.
    # Dette er ikke gyldig PNG-data, men de fleste viewere stopper ved IEND.
    appended = b"\n--ekko--\n" + base64.b64encode(FLAG.encode()) + b"\n"

    final = png + appended
    (out_dir / "plakat.png").write_bytes(final)

    print(f"[+] Skrev plakat.png ({len(final)} byte)")
    print(f"[+] PNG-stoerrelse: {len(png)} byte")
    print(f"[+] Appendet etter IEND: {len(appended)} byte")
    print(f"[+] Flagg: {FLAG}")
    print(f"[+] Base64: {base64.b64encode(FLAG.encode()).decode()}")


if __name__ == "__main__":
    main()
