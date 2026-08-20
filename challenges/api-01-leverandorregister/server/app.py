from __future__ import annotations

import base64
import copy
import hashlib
import hmac
import json
import os
import time
from functools import wraps
from typing import Any

from flask import Flask, jsonify, request


FLAG = os.environ.get("FLAG", "CTF{api_mass_assignment_i_leverandorportalen}")
SIGNING_KEY = os.environ.get("SIGNING_KEY", "supplier-demo-signing-key")

app = Flask(__name__)

USERS: dict[str, dict[str, Any]] = {
    "guest": {
        "username": "guest",
        "password": "guest",
        "company": "DemoPartner AS",
        "role": "supplier",
    },
    "oda": {
        "username": "oda",
        "password": "redacted",
        "company": "Nordverk",
        "role": "operator",
    },
}

SUPPLIERS = [
    {
        "id": "demo-partner",
        "name": "DemoPartner AS",
        "status": "approved",
        "contact": "kontakt@demo-partner.example",
    },
    {
        "id": "nordventil",
        "name": "NordVentil Service",
        "status": "pending",
        "contact": "service@nordventil.example",
    },
    {
        "id": "fjord-sensor",
        "name": "Fjord Sensorikk",
        "status": "approved",
        "contact": "ops@fjord-sensor.example",
    },
]

CONTRACTS = [
    {
        "id": "CTR-2026-041",
        "supplier": "NordVentil Service",
        "classification": "internal",
        "summary": "Nødventil-inspeksjon for demoanlegg",
    },
    {
        "id": "CTR-2026-088",
        "supplier": "Fjord Sensorikk",
        "classification": "public",
        "summary": "Kalibrering av stand-sensorer",
    },
]


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def b64url_decode(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def sign(data: bytes) -> str:
    digest = hmac.new(SIGNING_KEY.encode(), data, hashlib.sha256).digest()
    return b64url_encode(digest)


def issue_token(user: dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user["username"],
        "role": user.get("role", "supplier"),
        "company": user.get("company", ""),
        "iat": int(time.time()),
    }
    encoded_header = b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    return f"{encoded_header}.{encoded_payload}.{sign(signing_input)}"


def parse_token(token: str) -> dict[str, Any] | None:
    try:
        encoded_header, encoded_payload, supplied_signature = token.split(".")
        signing_input = f"{encoded_header}.{encoded_payload}".encode()
        expected_signature = sign(signing_input)
        if not hmac.compare_digest(expected_signature, supplied_signature):
            return None
        return json.loads(b64url_decode(encoded_payload))
    except Exception:
        return None


def current_user() -> dict[str, Any] | None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    claims = parse_token(auth.removeprefix("Bearer ").strip())
    if not claims:
        return None
    user = USERS.get(claims.get("sub", ""))
    if not user:
        return None
    return user


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({"error": "missing or invalid bearer token"}), 401
        return func(user, *args, **kwargs)

    return wrapper


def require_admin(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if user.get("role") != "admin":
            return jsonify({"error": "admin role required"}), 403
        return func(user, *args, **kwargs)

    return wrapper


@app.get("/")
def index():
    return jsonify(
        {
            "service": "Nordverk Leverandørregister",
            "version": "2026.05",
            "docs": "/ui",
            "status": "ok",
        }
    )


@app.get("/ui")
def docs():
    return """
<!doctype html>
<html lang="no">
<head>
  <meta charset="utf-8">
  <title>Nordverk Leverandørregister API</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; max-width: 900px; }
    code, pre { background: #f4f4f4; border-radius: 4px; padding: .15rem .35rem; }
    pre { padding: 1rem; overflow-x: auto; }
    li { margin-bottom: .45rem; }
  </style>
</head>
<body>
  <h1>Nordverk Leverandørregister API</h1>
  <p>Eksternt API for leverandørregistrering og kontraktsoversikt.</p>
  <h2>Endepunkter</h2>
  <ul>
    <li><code>GET /api/v1/suppliers</code></li>
    <li><code>POST /api/v1/register</code></li>
    <li><code>POST /api/v1/login</code></li>
    <li><code>GET /api/v1/contracts</code> med <code>Authorization: Bearer &lt;token&gt;</code></li>
    <li><code>GET /openapi.json</code></li>
  </ul>
  <h2>Eksempel</h2>
  <pre>curl -s -X POST /api/v1/register \\
  -H 'Content-Type: application/json' \\
  -d '{"username":"demo","password":"demo","company":"Demo AS"}'</pre>
</body>
</html>
""".strip()


@app.get("/openapi.json")
def openapi():
    return jsonify(
        {
            "openapi": "3.0.0",
            "info": {
                "title": "Nordverk Leverandørregister API",
                "version": "2026.05",
            },
            "paths": {
                "/api/v1/suppliers": {"get": {"summary": "List public suppliers"}},
                "/api/v1/register": {"post": {"summary": "Register supplier user"}},
                "/api/v1/login": {"post": {"summary": "Login and receive token"}},
                "/api/v1/contracts": {"get": {"summary": "List visible contracts"}},
            },
        }
    )


@app.get("/api/v1/suppliers")
def suppliers():
    return jsonify({"suppliers": SUPPLIERS})


@app.post("/api/v1/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    required = {"username", "password", "company"}
    missing = sorted(required - set(data))
    if missing:
        return jsonify({"error": "missing fields", "fields": missing}), 400

    username = str(data["username"]).strip()
    if not username or username in USERS:
        return jsonify({"error": "username unavailable"}), 409

    user = copy.deepcopy(data)
    user["username"] = username
    USERS[username] = user
    public = {key: value for key, value in user.items() if key != "password"}
    return jsonify({"created": public}), 201


@app.post("/api/v1/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    user = USERS.get(str(data.get("username", "")))
    if not user or user.get("password") != data.get("password"):
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({"token": issue_token(user)})


@app.get("/api/v1/contracts")
@require_auth
def contracts(user):
    visible = [
        contract
        for contract in CONTRACTS
        if contract["classification"] == "public" or user.get("role") in {"operator", "admin"}
    ]
    return jsonify({"contracts": visible})


@app.get("/api/v1/_debug/routes")
def debug_routes():
    return jsonify(
        {
            "warning": "debug endpoint should be disabled before production",
            "routes": sorted(rule.rule for rule in app.url_map.iter_rules()),
            "model_fields": {
                "user": ["username", "password", "company", "role"],
                "roles": ["supplier", "operator", "admin"],
            },
        }
    )


@app.get("/api/v1/internal/beredskap")
@require_auth
@require_admin
def beredskap(user):
    return jsonify(
        {
            "requested_by": user["username"],
            "classification": "internal",
            "beredskapskode": FLAG,
            "note": "Kun for godkjente interne administratorer.",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
