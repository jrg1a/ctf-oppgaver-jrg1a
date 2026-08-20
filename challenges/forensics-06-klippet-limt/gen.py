#!/usr/bin/env python3
"""Generate the interleaved PNG artifact for Klippet og limt."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin


FLAG = "CTF{blokker_flettet_tre_veier}"
BLOCK_SIZE = 512
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist" / "utklipp.bin"

FRAGMENTS = (
    "CTF{blokker_",
    "flettet_tre_",
    "veier}",
)

PALETTES = (
    ((238, 246, 255), (33, 86, 142), (13, 38, 68)),
    ((241, 250, 238), (42, 122, 83), (20, 55, 38)),
    ((255, 246, 235), (176, 83, 38), (80, 35, 20)),
)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    )
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def make_png(fragment: str, number: int) -> bytes:
    background, accent, text = PALETTES[number - 1]
    image = Image.new("RGB", (900, 340), background)
    draw = ImageDraw.Draw(image)
    title_font = load_font(42)
    mono_font = load_font(54)
    small_font = load_font(24)

    draw.rectangle((0, 0, 900, 62), fill=accent)
    draw.text((28, 15), f"Arkivfragment {number}/3", fill=(255, 255, 255), font=small_font)

    draw.line((36, 110, 864, 110), fill=accent, width=4)
    draw.text((54, 130), "Gjenopprettet bit:", fill=text, font=title_font)

    y = 205
    for line in wrap(fragment, width=18):
        draw.text((84, y), line, fill=text, font=mono_font)
        y += 64

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("Fragment", fragment, zip=True)
    pnginfo.add_text("Order", str(number), zip=True)

    buffer = BytesIO()
    image.save(buffer, format="PNG", pnginfo=pnginfo, optimize=False)
    return buffer.getvalue()


def pad_blocks(data: bytes, blocks: int) -> bytes:
    target = blocks * BLOCK_SIZE
    return data + b"\x00" * (target - len(data))


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    images = [make_png(fragment, index) for index, fragment in enumerate(FRAGMENTS, 1)]
    max_blocks = max((len(image) + BLOCK_SIZE - 1) // BLOCK_SIZE for image in images)
    padded = [pad_blocks(image, max_blocks) for image in images]

    interleaved = bytearray()
    for block_index in range(max_blocks):
        start = block_index * BLOCK_SIZE
        end = start + BLOCK_SIZE
        for image in padded:
            interleaved.extend(image[start:end])

    OUT.write_bytes(bytes(interleaved))
    print(f"[+] Skrev {OUT} ({len(interleaved)} byte)")
    print(f"[+] Blokkstorrelse: {BLOCK_SIZE}, strommer: {len(images)}")
    print(f"[+] Forventet flagg: {FLAG}")


if __name__ == "__main__":
    main()
