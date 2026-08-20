#!/usr/bin/env python3
"""Deploy the generalized challenge collection to a CTFd instance.

The script reads player-facing text from release/*/README.md and organizer
flags from challenges/*/CHALLENGE.md or challenge.yml.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "release"
CHALLENGES_DIR = ROOT / "challenges"
JSON_HEADERS = {"Content-Type": "application/json"}
CONNECTION_PLACEHOLDERS = ("<IP>", "<PORT>", "@<IP>", "{host}", "{port}")
PREVIOUS_CHALLENGE_NAMES: dict[str, tuple[str, ...]] = {}


@dataclass
class Challenge:
    slug: str
    name: str
    category: str
    value: int
    description: str
    connection_info: str | None
    flag: str
    hints: list[dict[str, Any]]
    files: list[Path]


def section(text: str, heading: str) -> str | None:
    pattern = rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^---\n|^## |\Z)"
    match = re.search(pattern, text, flags=re.M | re.S)
    if not match:
        return None
    return match.group("body").strip()


def strip_metadata(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]

    cleaned: list[str] = []
    metadata = re.compile(
        r"^\*\*(Kategori|Poeng|Type|Vanskelighetsgrad|Container):\*\*"
    )
    for line in lines:
        if metadata.match(line):
            continue
        cleaned.append(line)

    text = "\n".join(cleaned).strip()
    text = re.sub(r"\n?---\n?\s*(?=---|\Z)", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_section(text: str, heading: str) -> str:
    pattern = rf"^---\n\n## {re.escape(heading)}\n.*?(?=^---\n\n## |\Z)"
    text = re.sub(pattern, "", text, flags=re.M | re.S)
    pattern = rf"^## {re.escape(heading)}\n.*?(?=^---\n|^## |\Z)"
    return re.sub(pattern, "", text, flags=re.M | re.S).strip()


def replace_section(text: str, heading: str, body: str) -> str:
    replacement = f"## {heading}\n\n{body.strip()}\n\n"
    pattern = rf"^## {re.escape(heading)}\n.*?(?=^---\n|^## |\Z)"
    if re.search(pattern, text, flags=re.M | re.S):
        text = re.sub(pattern, replacement, text, flags=re.M | re.S)
    elif re.search(rf"^{re.escape(heading)}\n", text, flags=re.M):
        plain_replacement = f"{heading}\n\n{body.strip()}\n\n"
        plain_pattern = rf"^{re.escape(heading)}\n.*?(?=^[A-ZÆØÅ][^\n]{{0,60}}\n\n|\Z)"
        text = re.sub(plain_pattern, plain_replacement, text, flags=re.M | re.S)
    else:
        text = f"{text.rstrip()}\n\n---\n\n{replacement}"
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def has_connection_placeholder(text: str | None) -> bool:
    return bool(text and any(marker in text for marker in CONNECTION_PLACEHOLDERS))


def sanitize_attachment_links(text: str) -> str:
    return re.sub(r"\[`([^`]+)`\]\([^)]+\)", r"\1", text)


def plain_ctfd_description(text: str) -> str:
    """Keep CTFd descriptions readable even when the theme skips Markdown."""
    text = sanitize_attachment_links(text)
    text = re.sub(r"```[a-zA-Z0-9_-]*\n?", "", text)
    text = text.replace("```", "")
    text = re.sub(r"^[ \t]*---[ \t]*$\n?", "\n", text, flags=re.M)
    text = re.sub(r"^##\s+(.+)$", r"\1", text, flags=re.M)
    text = re.sub(r"\*\*([^*\n]+):\*\*", r"\1:", text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`\n]+)`", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_meta(readme: str) -> tuple[str, int]:
    category_match = re.search(r"^\*\*Kategori:\*\*\s*(.+)$", readme, re.M)
    value_match = re.search(r"^\*\*Poeng:\*\*\s*(\d+)$", readme, re.M)
    if not category_match or not value_match:
        raise ValueError("missing Kategori/Poeng metadata")
    return category_match.group(1).strip(), int(value_match.group(1))


def read_title(readme: str) -> str:
    match = re.search(r"^#\s+(.+)$", readme, re.M)
    if not match:
        raise ValueError("missing markdown title")
    return match.group(1).strip()


def read_flag(slug: str) -> str:
    challenge_md = CHALLENGES_DIR / slug / "CHALLENGE.md"
    if challenge_md.exists():
        text = challenge_md.read_text(encoding="utf-8")
        match = re.search(r"\*\*Flagg:\*\*\s*`([^`]+)`", text)
        if match:
            return match.group(1)

    challenge_yml = CHALLENGES_DIR / slug / "challenge.yml"
    if challenge_yml.exists():
        text = challenge_yml.read_text(encoding="utf-8")
        match = re.search(r'^flag:\s*["\']?([^"\']+)["\']?\s*$', text, re.M)
        if match:
            return match.group(1).strip()

    raise ValueError(f"missing organizer flag for {slug}")


def parse_hint_cost(cost_text: str) -> int:
    cost_text = cost_text.strip()
    if cost_text.lower() == "gratis":
        return 0
    match = re.search(r"\d+", cost_text)
    if not match:
        raise ValueError(f"could not parse hint cost: {cost_text!r}")
    return int(match.group(0))


def parse_hints(readme: str) -> list[dict[str, Any]]:
    hints_md = section(readme, "Hints")
    if not hints_md:
        return []

    hints: list[dict[str, Any]] = []
    for line in hints_md.splitlines():
        line = line.strip()
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= {"-"}:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() == "kostnad":
            continue
        hints.append(
            {
                "content": cells[1].replace(r"\|", "|").strip(),
                "cost": parse_hint_cost(cells[0]),
            }
        )
    return hints


def parse_files(slug: str, readme: str) -> list[Path]:
    attachments_md = section(readme, "Vedlegg")
    if not attachments_md:
        return []

    release_root = RELEASE_DIR / slug
    files: list[Path] = []
    for target in re.findall(r"\[`[^`]+`\]\(([^)]+)\)", attachments_md):
        target_path = (release_root / target).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"{slug}: referenced attachment not found: {target}")
        files.append(target_path)
    return files


def load_challenges() -> list[Challenge]:
    challenges: list[Challenge] = []
    for readme_path in sorted(RELEASE_DIR.glob("*/README.md")):
        slug = readme_path.parent.name
        readme = readme_path.read_text(encoding="utf-8")
        name = read_title(readme)
        category, value = read_meta(readme)
        connection_info = section(readme, "Tilkobling")

        description = strip_metadata(readme)
        description = remove_section(description, "Hints")
        description = plain_ctfd_description(description)
        description = re.sub(r"\n{3,}", "\n\n", description).strip()

        challenges.append(
            Challenge(
                slug=slug,
                name=name,
                category=category,
                value=value,
                description=description,
                connection_info=connection_info,
                flag=read_flag(slug),
                hints=parse_hints(readme),
                files=parse_files(slug, readme),
            )
        )
    return challenges


def api_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/api/v1/{path.lstrip('/')}"


def expect_success(response: requests.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"{response.request.method} {response.url} returned non-JSON "
            f"{response.status_code}: {response.text[:300]}"
        ) from exc

    if response.status_code >= 400 or not payload.get("success", False):
        raise RuntimeError(
            f"{response.request.method} {response.url} failed "
            f"{response.status_code}: {json.dumps(payload, ensure_ascii=False)}"
        )
    return payload


def list_existing(session: requests.Session, base_url: str) -> dict[str, dict[str, Any]]:
    response = session.get(
        api_url(base_url, "challenges"),
        params={"view": "admin"},
        headers=JSON_HEADERS,
        timeout=20,
    )
    data = expect_success(response)["data"]
    return {item["name"]: item for item in data}


def list_all_existing(
    session: requests.Session, base_url: str
) -> list[dict[str, Any]]:
    response = session.get(
        api_url(base_url, "challenges"),
        params={"view": "admin"},
        headers=JSON_HEADERS,
        timeout=20,
    )
    return expect_success(response)["data"]


def get_challenge_detail(
    session: requests.Session, base_url: str, challenge_id: int
) -> dict[str, Any]:
    response = session.get(
        api_url(base_url, f"challenges/{challenge_id}"),
        headers=JSON_HEADERS,
        timeout=20,
    )
    return expect_success(response)["data"]


def create_or_update_challenge(
    session: requests.Session,
    base_url: str,
    challenge: Challenge,
    existing: dict[str, dict[str, Any]],
    *,
    update_existing: bool,
    visible: bool,
) -> tuple[int, str]:
    payload: dict[str, Any] = {
        "name": challenge.name,
        "category": challenge.category,
        "description": challenge.description,
        "value": challenge.value,
        "type": "standard",
        "state": "visible" if visible else "hidden",
        "max_attempts": 0,
    }
    payload["connection_info"] = challenge.connection_info or ""

    current = existing.get(challenge.name)
    if not current:
        for previous_name in PREVIOUS_CHALLENGE_NAMES.get(challenge.slug, ()):
            current = existing.get(previous_name)
            if current:
                break
    if current:
        challenge_id = int(current["id"])
        if update_existing:
            if has_connection_placeholder(challenge.connection_info):
                detail = get_challenge_detail(session, base_url, challenge_id)
                current_connection = detail.get("connection_info") or section(
                    detail.get("description") or "", "Tilkobling"
                )
                if current_connection and not has_connection_placeholder(
                    current_connection
                ):
                    payload["connection_info"] = current_connection
                    payload["description"] = replace_section(
                        payload["description"], "Tilkobling", current_connection
                    )
            response = session.patch(
                api_url(base_url, f"challenges/{challenge_id}"),
                json=payload,
                headers=JSON_HEADERS,
                timeout=20,
            )
            expect_success(response)
            return challenge_id, "updated"
        return challenge_id, "exists"

    response = session.post(
        api_url(base_url, "challenges"),
        json=payload,
        headers=JSON_HEADERS,
        timeout=20,
    )
    data = expect_success(response)["data"]
    return int(data["id"]), "created"


def add_flag(session: requests.Session, base_url: str, challenge_id: int, flag: str) -> str:
    response = session.get(
        api_url(base_url, "flags"),
        params={"challenge_id": challenge_id},
        headers=JSON_HEADERS,
        timeout=20,
    )
    flags = expect_success(response)["data"]
    stale_flags = [item for item in flags if item.get("content") != flag]
    for stale in stale_flags:
        response = session.delete(
            api_url(base_url, f"flags/{stale['id']}"),
            headers=JSON_HEADERS,
            timeout=20,
        )
        expect_success(response)

    if any(item.get("content") == flag for item in flags):
        return "replaced" if stale_flags else "exists"

    response = session.post(
        api_url(base_url, "flags"),
        json={
            "challenge_id": challenge_id,
            "type": "static",
            "content": flag,
            "data": "case_sensitive",
        },
        headers=JSON_HEADERS,
        timeout=20,
    )
    expect_success(response)
    return "replaced" if stale_flags else "created"


def add_hints(
    session: requests.Session,
    base_url: str,
    challenge_id: int,
    hints: list[dict[str, Any]],
) -> tuple[int, int]:
    response = session.get(
        api_url(base_url, f"challenges/{challenge_id}/hints"),
        headers=JSON_HEADERS,
        timeout=20,
    )
    existing = expect_success(response)["data"]
    desired_pairs = {(hint["content"], int(hint["cost"])) for hint in hints}
    for item in existing:
        pair = (item.get("content"), int(item.get("cost", 0)))
        if pair not in desired_pairs:
            response = session.delete(
                api_url(base_url, f"hints/{item['id']}"),
                headers=JSON_HEADERS,
                timeout=20,
            )
            expect_success(response)

    existing_pairs = {(item.get("content"), int(item.get("cost", 0))) for item in existing}

    created = 0
    skipped = 0
    for hint in hints:
        pair = (hint["content"], int(hint["cost"]))
        if pair in existing_pairs:
            skipped += 1
            continue
        response = session.post(
            api_url(base_url, "hints"),
            json={"challenge_id": challenge_id, **hint},
            headers=JSON_HEADERS,
            timeout=20,
        )
        expect_success(response)
        created += 1
    return created, skipped


def add_files(
    session: requests.Session,
    base_url: str,
    challenge_id: int,
    files: list[Path],
) -> tuple[int, int]:
    response = session.get(
        api_url(base_url, f"challenges/{challenge_id}/files"),
        headers=JSON_HEADERS,
        timeout=20,
    )
    existing = expect_success(response)["data"]
    existing_names = {Path(item.get("location", "")).name for item in existing}

    created = 0
    skipped = 0
    for file_path in files:
        if file_path.name in existing_names:
            skipped += 1
            continue
        with file_path.open("rb") as handle:
            response = session.post(
                api_url(base_url, "files"),
                data={"challenge_id": str(challenge_id), "type": "challenge"},
                files={"file": (file_path.name, handle)},
                timeout=120,
            )
        expect_success(response)
        created += 1
    return created, skipped


def dry_run(challenges: list[Challenge]) -> None:
    rows = []
    for challenge in challenges:
        rows.append(
            {
                "slug": challenge.slug,
                "name": challenge.name,
                "category": challenge.category,
                "value": challenge.value,
                "hints": len(challenge.hints),
                "files": [path.name for path in challenge.files],
                "flag": challenge.flag,
            }
        )
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def deploy(args: argparse.Namespace, challenges: list[Challenge]) -> None:
    token = args.token or os.environ.get("CTFD_TOKEN")
    if args.token_file:
        token = Path(args.token_file).read_text(encoding="utf-8").strip()
    if not token:
        raise SystemExit("Missing API token. Pass --token, --token-file, or set CTFD_TOKEN.")

    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Token {token}",
            "Accept": "application/json",
        }
    )

    if args.dedupe:
        dedupe_challenges(session, args.url, challenges)
        return

    existing = list_existing(session, args.url)
    for challenge in challenges:
        challenge_id, challenge_status = create_or_update_challenge(
            session,
            args.url,
            challenge,
            existing,
            update_existing=args.update_existing,
            visible=args.visible,
        )

        flag_status = add_flag(session, args.url, challenge_id, challenge.flag)
        hints_created, hints_skipped = add_hints(
            session, args.url, challenge_id, challenge.hints
        )
        files_created, files_skipped = add_files(
            session, args.url, challenge_id, challenge.files
        )
        print(
            f"{challenge.name}: challenge={challenge_status}, flag={flag_status}, "
            f"hints=+{hints_created}/{hints_skipped} existing, "
            f"files=+{files_created}/{files_skipped} existing"
        )


def dedupe_challenges(
    session: requests.Session, base_url: str, challenges: list[Challenge]
) -> None:
    names = {challenge.name for challenge in challenges}
    groups: dict[str, list[dict[str, Any]]] = {name: [] for name in names}
    for item in list_all_existing(session, base_url):
        if item.get("name") in groups:
            groups[item["name"]].append(item)

    for name in sorted(groups):
        items = sorted(groups[name], key=lambda item: int(item["id"]))
        if len(items) <= 1:
            print(f"{name}: {len(items)} copy, nothing to delete")
            continue

        keep = items[0]
        for item in items[1:]:
            response = session.delete(
                api_url(base_url, f"challenges/{int(item['id'])}"),
                headers=JSON_HEADERS,
                timeout=20,
            )
            expect_success(response)
            print(f"{name}: deleted duplicate id={item['id']}, kept id={keep['id']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default=os.environ.get("CTFD_URL", "https://ctfd.example"),
        help="Base URL for the CTFd instance.",
    )
    parser.add_argument(
        "--token",
        help="CTFd admin access token. Can also be supplied via CTFD_TOKEN.",
    )
    parser.add_argument(
        "--token-file",
        help="Path to a file containing the CTFd admin access token.",
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Patch metadata for challenges that already exist.",
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Create/update challenges as visible. Default is hidden.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print parsed challenge metadata without touching CTFd.",
    )
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Delete duplicate challenges by name, keeping the lowest ID.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    challenges = load_challenges()
    if args.dry_run:
        dry_run(challenges)
        return 0
    deploy(args, challenges)
    return 0


if __name__ == "__main__":
    sys.exit(main())
