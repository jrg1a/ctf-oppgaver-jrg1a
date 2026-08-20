#!/usr/bin/env python3
"""Keep only writeups for challenge directories present in this repository."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRITEUPS = ROOT / "docs" / "solution-writeups.md"
ALIASES = {
    "04-mitm-attack": "linux-01-servicekonto",
    "misc-01-ai-chatbot": "password-01-arkivportal",
}


def main() -> None:
    available = {path.name for path in (ROOT / "challenges").iterdir() if path.is_dir()}
    source = WRITEUPS.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^## (?P<title>.+?) \(`(?P<slug>[^`]+)`\)\n", source, re.M))

    sections: list[tuple[str, str, str]] = []
    for index, match in enumerate(matches):
        slug = ALIASES.get(match.group("slug"), match.group("slug"))
        if slug not in available:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        body = source[match.end() : end].rstrip()
        body = re.sub(r'^<a id="[^"]+"></a>\n?', "", body, flags=re.M).strip()
        sections.append((match.group("title"), slug, body))

    lines = [
        "# Løsningswriteups for CTF-oppgaver",
        "",
        "Dette dokumentet er for arrangører og validering. Det skal ikke følge",
        "deltakerpakken som genereres i `release/`.",
        "",
        "## Innhold",
        "",
    ]
    lines.extend(f"- [{title}](#{slug})" for title, slug, _ in sections)
    lines.append("")

    for title, slug, body in sections:
        lines.extend((f'<a id="{slug}"></a>', "", f"## {title} (`{slug}`)", "", body, ""))

    WRITEUPS.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"[+] Skrev {len(sections)} writeups til {WRITEUPS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
