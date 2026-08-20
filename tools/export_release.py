#!/usr/bin/env python3
"""Create player-facing challenge packages without organizer solutions."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHALLENGES = ROOT / "challenges"

SOLUTION_HEADINGS = (
    "## Løsningsvei",
    "## Losningsvei",
    "## VM-instruksjonssett",
)

PLAYER_FILES = {
    "linux-01-servicekonto": [],
    "api-01-leverandorregister": [],
    "crypto-01-xor-vakt": [],
    "forensics-01-usb-stand": [],
    "password-01-arkivportal": [],
    "misc-02-velkomststrom": [],
    "osint-01-finn-scenen": [],
    "ot-01-modbus-klartekst": ["modbus_capture.pcap"],
    "ot-02-bop-modbus": ["recon_starter.py", "registerkart.md"],
    "ot-03-mqtt": ["mqtt_recon.py", "mqtt_kommandoer.md"],
    "ot-04-scada-sqli": [],
    "ot-05-historian-api": [],
    "pwn-00-retur-vaktbua": ["retur_vaktbua"],
    "pwn-01-buffer-boden": ["server/buffer"],
    "re-01-pyc": ["agent.pyc"],
    "re-02-crackme": ["crackme"],
    "re-03-minivm": ["minivm"],
    "stego-01-plakat-ekko": [],
    "web-01-jwt": ["wordlist.txt"],
    "network-01-dns-lekkasje": [],
    "forensics-02-mailspor": [],
    "web-02-backup-lekkasje": [],
    "web-03-not-your-badge": [],
}


def strip_solution(text: str) -> str:
    lines = text.splitlines()
    keep: list[str] = []
    for line in lines:
        if any(line.startswith(heading) for heading in SOLUTION_HEADINGS):
            break
        keep.append(line)
    return "\n".join(keep).rstrip() + "\n"


def copy_path(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def export_challenge(chal_dir: Path, out_dir: Path) -> None:
    name = chal_dir.name
    target = out_dir / name
    target.mkdir(parents=True, exist_ok=True)

    challenge_md = chal_dir / "CHALLENGE.md"
    if challenge_md.exists():
        (target / "README.md").write_text(
            strip_solution(challenge_md.read_text(encoding="utf-8")),
            encoding="utf-8",
        )

    dist = chal_dir / "dist"
    if dist.exists():
        copy_path(dist, target / "dist")

    for rel in PLAYER_FILES.get(name, []):
        src = chal_dir / rel
        if not src.exists():
            print(f"[warn] Missing expected player file: {src.relative_to(ROOT)}")
            continue
        copy_path(src, target / rel)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output",
        nargs="?",
        default=str(ROOT / "release"),
        help="Output directory. Defaults to ./release",
    )
    args = parser.parse_args()

    out_dir = Path(args.output).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    exported = []
    for chal_dir in sorted(p for p in CHALLENGES.iterdir() if p.is_dir()):
        export_challenge(chal_dir, out_dir)
        exported.append(chal_dir.name)

    manifest = ["# CTF-oppgaver release", "", "Player-facing challenge packages:", ""]
    manifest.extend(f"- {name}" for name in exported)
    manifest.append("")
    (out_dir / "MANIFEST.md").write_text("\n".join(manifest), encoding="utf-8")

    print(f"[+] Exported {len(exported)} challenges to {out_dir}")


if __name__ == "__main__":
    main()
