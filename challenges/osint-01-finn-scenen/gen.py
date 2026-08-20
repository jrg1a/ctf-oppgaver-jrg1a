"""
CTF Challenge: "Finn scenen" — OSINT, easy

Frosset OSINT (alt ligger i vedlegg, ingen levende nettsider). Tre artefakter:

  1. program_snapshot.txt  — frosset utdrag fra Teknologidagene-programmet
  2. skilt_foto.png        — beskaaret foto av et skilt fra messeomraadet
                              (scenenavnet er overmalt, men tid/tittel/sal
                              er synlig)
  3. kodebok.md            — Nordverks interne kodebok som mapper
                              hver scene til en flagg-suffiks

Loesningssti:
  - Bildet viser tid+tittel+salnavn fra et foredrag.
  - Tittelen + tiden matcher EN rad i program_snapshot.txt -> det
    avsloerer hvilken SCENE foredraget er paa.
  - Slå scenen opp i kodebok.md -> hent flagg-suffiks.

Flagg: CTF{scene_b_storsalen}
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FLAG = "CTF{scene_b_storsalen}"

# Frosset utdrag av programmet
PROGRAM = """TEKNOLOGIDAGENE 2026 - PROGRAMUTDRAG (frosset 2026-05-20)
==============================================================

TORSDAG 11. JUNI

10:00  Scene A - Lille sal      "AI for det offentlige Norge"
                                    Foredragsholder: Mari Lien
11:00  Scene B - Storsalen      "State of Cyber Security 2026"
                                    Foredragsholder: Olav Berg
11:00  Scene C - Glassrommet    "Klimagass-data fra industrien"
                                    Foredragsholder: Inga Johansen
12:00  Scene D - Verkstedet     "Hands-on: Sikker IoT i praksis"
                                    Workshop, paamelding kreves
13:00  Scene B - Storsalen      "Securing Norway's Digital Future"
                                    Foredragsholder: Hans Eide
13:00  Scene A - Lille sal      "Norge som teknologinasjon"
                                    Panel
14:00  Scene E - Atriet         "Stand-up: Tech-tabber"
                                    Underholdning
15:00  Scene B - Storsalen      "OT/ICS - lærdommer fra 2025"
                                    Foredragsholder: Tone Aas
15:00  Scene F - Bibliotek      "Norske kvinner i tech"
                                    Panel
"""


# Kodebok som mapper sal -> flagg-suffiks
KODEBOK = """# Nordverk intern kodebok - Teknologidagene 2026
*Brukes av sikkerhetsteamet for sceneverifisering. Roteres aarlig.*

| Sal-kode | Sal-navn      | Flagg-suffiks       |
|----------|---------------|---------------------|
| A        | Lille sal     | scene_a_lillesal    |
| B        | Storsalen     | scene_b_storsalen   |
| C        | Glassrommet   | scene_c_glassrommet |
| D        | Verkstedet    | scene_d_verkstedet  |
| E        | Atriet        | scene_e_atriet      |
| F        | Bibliotek     | scene_f_bibliotek   |

*Bygg flagget paa formen: `CTF{<flagg-suffiks>}`*
"""


def make_skilt_image(out_path: Path):
    """Et beskaaret 'skilt-foto' der scenenavn er overmalt med svart blokk."""
    W, H = 800, 460
    img = Image.new("RGB", (W, H), (235, 235, 230))
    draw = ImageDraw.Draw(img)

    try:
        font_big   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_med   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except OSError:
        font_big = font_med = font_small = ImageFont.load_default()

    # Festival-banner
    draw.rectangle([(0, 0), (W, 90)], fill=(20, 50, 100))
    draw.text((30, 30), "TEKNOLOGIDAGENE 2026", fill="white", font=font_big)

    # Tittel paa foredraget (synlig)
    draw.text((30, 130), '"State of Cyber Security 2026"', fill=(20, 20, 20), font=font_big)
    draw.text((30, 200), "Foredragsholder: Olav Berg",     fill=(60, 60, 60), font=font_med)

    # Tid (synlig)
    draw.text((30, 260), "Torsdag 11. juni  -  kl. 11:00", fill=(60, 60, 60), font=font_med)

    # "Sal" - skiltet, men selve scenenavnet er overmalt
    draw.text((30, 320), "Sal:", fill=(60, 60, 60), font=font_med)
    # svart sensur-blokk over scenenavn
    draw.rectangle([(115, 320), (430, 360)], fill=(15, 15, 15))
    draw.text((150, 326), "[KLIPPET BORT]", fill=(180, 180, 180), font=font_small)

    # Liten footer
    draw.text((30, 400), "Foto: messeomraadet, Nordverks stand", fill=(120, 120, 120), font=font_small)

    img.save(out_path, "PNG")


def main():
    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)

    (out_dir / "program_snapshot.txt").write_text(PROGRAM, encoding="utf-8")
    (out_dir / "kodebok.md").write_text(KODEBOK, encoding="utf-8")
    make_skilt_image(out_dir / "skilt_foto.png")

    print(f"[+] Skrev program_snapshot.txt, kodebok.md, skilt_foto.png")
    print(f"[+] Korrekt scene: B (Storsalen), 11:00, 'State of Cyber Security 2026'")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
