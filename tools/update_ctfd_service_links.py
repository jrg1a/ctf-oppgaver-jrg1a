#!/usr/bin/env python3
"""Update CTFd challenge connection text from Hosted CTFd services.

This is intentionally separate from deploy_ctfd.py because service hostnames
and allocated TCP ports are environment-specific.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests

import deploy_ctfd


JSON_HEADERS = {"Content-Type": "application/json"}
MAX_SERVICE_ID = 50

SERVICE_NAMES = {
    "linux-01-servicekonto": "ctf-linux-01-servicekonto",
    "api-01-leverandorregister": "ctf-api-01-leverandorregister",
    "ot-02-bop-modbus": "ctf-ot-02-bop-modbus",
    "ot-03-mqtt": "ctf-ot-03-mqtt",
    "ot-04-scada-sqli": "ctf-ot-04-scada-sqli",
    "ot-05-historian-api": "ctf-ot-05-historian-api",
    "pwn-01-buffer-boden": "ctf-pwn-01-buffer-boden",
    "web-01-jwt": "ctf-web-01-jwt",
    "web-02-backup-lekkasje": "ctf-web-02-backup-lekkasje",
    "web-03-not-your-badge": "ctf-web-03-not-your-badge",
}

TCP_SERVICE_SLUGS = {
    "linux-01-servicekonto",
    "ot-02-bop-modbus",
    "ot-03-mqtt",
    "pwn-01-buffer-boden",
}


def api_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/api/v1/{path.lstrip('/')}"


def expect_json(response: requests.Response) -> dict[str, Any] | None:
    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type:
        return None
    payload = response.json()
    if response.status_code >= 400 or not payload.get("success", False):
        raise RuntimeError(
            f"{response.request.method} {response.url} failed "
            f"{response.status_code}: {json.dumps(payload, ensure_ascii=False)}"
        )
    return payload


def list_services(session: requests.Session, base_url: str) -> dict[str, dict[str, Any]]:
    services: dict[str, dict[str, Any]] = {}
    for service_id in range(1, MAX_SERVICE_ID + 1):
        response = session.get(
            api_url(base_url, f"services/{service_id}"),
            headers=JSON_HEADERS,
            timeout=20,
        )
        if response.status_code == 404:
            continue
        payload = expect_json(response)
        if not payload:
            continue
        data = payload.get("data") or {}
        if data.get("name"):
            services[data["name"]] = data
    return services


def expose_tcp_services(
    session: requests.Session,
    base_url: str,
    services: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    for slug in sorted(TCP_SERVICE_SLUGS):
        service_name = SERVICE_NAMES[slug]
        service = services[service_name]
        if service.get("tcp_hostname") and service.get("tcp_port"):
            continue
        response = session.patch(
            api_url(base_url, f"services/{service['id']}"),
            data=json.dumps({"expose": True}),
            headers=JSON_HEADERS,
            timeout=30,
        )
        expect_json(response)
        refreshed = session.get(
            api_url(base_url, f"services/{service['id']}"),
            headers=JSON_HEADERS,
            timeout=20,
        )
        payload = expect_json(refreshed)
        if payload:
            services[service_name] = payload["data"]
    return services


def code_block(text: str) -> str:
    return text.rstrip()


def connection_for(slug: str, service: dict[str, Any]) -> str:
    hostname = service.get("hostname")
    tcp_hostname = service.get("tcp_hostname")
    tcp_port = service.get("tcp_port")
    if not hostname:
        raise ValueError(f"{slug}: service has no hostname")
    if slug in TCP_SERVICE_SLUGS and (not tcp_hostname or not tcp_port):
        raise ValueError(f"{slug}: service has no allocated TCP port")

    web_url = f"https://{hostname}"
    if slug == "linux-01-servicekonto":
        return code_block(
            f"ssh ctfplayer@{tcp_hostname} -p {tcp_port}\n"
            "Passord: ICS_r0ck5!"
        )
    if slug == "ot-02-bop-modbus":
        return code_block(f"Server: {tcp_hostname}:{tcp_port} (Modbus TCP)")
    if slug == "ot-03-mqtt":
        return code_block(f"Server: {tcp_hostname}:{tcp_port} (MQTT)")
    if slug == "pwn-01-buffer-boden":
        return code_block(f"nc {tcp_hostname} {tcp_port}")
    if slug == "api-01-leverandorregister":
        return f"Åpne: {web_url}\n\nStart gjerne på /ui."
    if slug == "web-01-jwt":
        return f"Åpne: {web_url}\n\nGjestekonto: guest / guest"
    if slug == "ot-05-historian-api":
        return f"Åpne: {web_url}\n\nLanding page viser dokumenterte endepunkter. Men er det alt?"
    return f"Åpne: {web_url}"


def replace_tilkobling(description: str, connection: str) -> str:
    replacement = f"Tilkobling\n\n{connection.strip()}\n\n"
    patterns = (
        r"^## Tilkobling\n.*?(?=^---\n|^## |\Z)",
        r"^Tilkobling\n.*?(?=^(Vedlegg|Registerkart|Flaggformat)\n|\Z)",
    )
    updated = description
    for pattern in patterns:
        if re.search(pattern, updated, flags=re.M | re.S):
            updated = re.sub(pattern, replacement, updated, flags=re.M | re.S)
            break
    else:
        updated = f"{description.rstrip()}\n\n{replacement}"
    updated = re.sub(r"\n{3,}", "\n\n", updated)
    return updated.strip()


def replace_inline_placeholders(
    slug: str, description: str, service: dict[str, Any]
) -> str:
    tcp_hostname = service.get("tcp_hostname")
    tcp_port = service.get("tcp_port")
    if slug == "ot-02-bop-modbus":
        return re.sub(
            r"python recon_starter\.py\s+<IP>(?:\s+<PORT>)?",
            f"python recon_starter.py {tcp_hostname} {tcp_port}",
            description,
        )
    if slug == "ot-03-mqtt":
        return re.sub(
            r"python mqtt_recon\.py\s+<IP>(?:\s+<PORT>)?",
            f"python mqtt_recon.py {tcp_hostname} {tcp_port}",
            description,
        )
    return description


def list_challenges(
    session: requests.Session, base_url: str
) -> dict[str, dict[str, Any]]:
    response = session.get(
        api_url(base_url, "challenges"),
        params={"view": "admin"},
        headers=JSON_HEADERS,
        timeout=20,
    )
    payload = expect_json(response)
    if not payload:
        raise RuntimeError("Challenge API returned non-JSON response")
    return {item["name"]: item for item in payload["data"]}


def update_challenges(
    session: requests.Session,
    base_url: str,
    services: dict[str, dict[str, Any]],
    *,
    dry_run: bool,
) -> None:
    challenges = {challenge.slug: challenge for challenge in deploy_ctfd.load_challenges()}
    existing = list_challenges(session, base_url)

    for slug, service_name in SERVICE_NAMES.items():
        challenge = challenges[slug]
        service = services[service_name]
        connection = connection_for(slug, service)
        description = replace_tilkobling(challenge.description, connection)
        description = replace_inline_placeholders(slug, description, service)

        current = existing.get(challenge.name)
        if not current:
            for previous_name in deploy_ctfd.PREVIOUS_CHALLENGE_NAMES.get(slug, ()):
                current = existing.get(previous_name)
                if current:
                    break
        if not current:
            raise RuntimeError(f"Could not find CTFd challenge named {challenge.name!r}")

        summary = {
            "challenge": challenge.name,
            "service": service_name,
            "connection_info": connection,
        }
        if dry_run:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            continue

        response = session.patch(
            api_url(base_url, f"challenges/{current['id']}"),
            data=json.dumps(
                {
                    "description": description,
                    "connection_info": connection,
                }
            ),
            headers=JSON_HEADERS,
            timeout=20,
        )
        expect_json(response)
        print(f"{challenge.name}: updated from {service_name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url", default=os.environ.get("CTFD_URL", "https://ctfd.example")
    )
    parser.add_argument("--token", help="CTFd admin access token")
    parser.add_argument("--token-file", help="Path containing a CTFd admin token")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = args.token or os.environ.get("CTFD_TOKEN")
    if args.token_file:
        token = Path(args.token_file).read_text(encoding="utf-8").strip()
    if not token:
        raise SystemExit("Missing token. Pass --token, --token-file, or set CTFD_TOKEN.")

    session = requests.Session()
    session.headers.update({"Authorization": f"Token {token}", "Accept": "application/json"})

    services = list_services(session, args.url)
    missing = sorted(set(SERVICE_NAMES.values()) - set(services))
    if missing:
        raise RuntimeError(f"Missing CTFd services: {', '.join(missing)}")

    services = expose_tcp_services(session, args.url, services)
    update_challenges(session, args.url, services, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
