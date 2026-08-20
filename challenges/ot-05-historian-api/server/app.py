"""
CTF Challenge: Historian API — Multi-stage IDOR
Flask REST API som simulerer en OT-historikkdatabase.

Steg 1: Finn /api/v1/debug/endpoints (endepunkt-enumering)
Steg 2: IDOR i /api/v1/sensors/<id>/logs — sensor 7 er "restricted" men ikke beskyttet
Steg 3: Base64-kodet loggpost i sensor 7 inneholder et service-token
Steg 4: Bruk tokenet mot /api/v1/admin/flag

Flagg: CTF{h1st0r14n_1d0r_ch41n_c0mpl3t3}
"""

import base64
import json
import os
import time
from functools import wraps
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

FLAG = "CTF{h1st0r14n_1d0r_ch41n_c0mpl3t3}"
SERVICE_TOKEN = "svc-hist-4f8a2c1e-9d3b"

# === Sensordata ===

SENSORS = {
    1: {"name": "TEMP-001",    "type": "temperature", "unit": "C",    "zone": "Process A",  "access": "public"},
    2: {"name": "PRES-002",    "type": "pressure",    "unit": "bar",  "zone": "Process A",  "access": "public"},
    3: {"name": "FLOW-003",    "type": "flow_rate",   "unit": "m3/h", "zone": "Process B",  "access": "public"},
    4: {"name": "VIBR-004",    "type": "vibration",   "unit": "mm/s", "zone": "Process B",  "access": "internal"},
    5: {"name": "LEVEL-005",   "type": "tank_level",  "unit": "%",    "zone": "Storage",    "access": "internal"},
    6: {"name": "RPM-006",     "type": "motor_speed", "unit": "rpm",  "zone": "Utility",    "access": "internal"},
    7: {"name": "SYS-MAINT",   "type": "maintenance", "unit": "log",  "zone": "SYSTEM",     "access": "restricted"},
}

SENSOR_LOGS = {
    1: [
        {"ts": "2026-01-14T06:12:03Z", "value": 68.4, "status": "OK"},
        {"ts": "2026-01-14T07:15:22Z", "value": 69.1, "status": "OK"},
        {"ts": "2026-01-14T08:44:11Z", "value": 71.8, "status": "WARNING_HIGH"},
        {"ts": "2026-01-14T09:02:55Z", "value": 69.3, "status": "OK"},
    ],
    2: [
        {"ts": "2026-01-14T06:12:03Z", "value": 198.2, "status": "OK"},
        {"ts": "2026-01-14T07:45:19Z", "value": 214.7, "status": "ALARM_HIGH"},
        {"ts": "2026-01-14T08:02:55Z", "value": 201.3, "status": "OK"},
    ],
    3: [
        {"ts": "2026-01-14T06:12:03Z", "value": 50.1, "status": "OK"},
        {"ts": "2026-01-14T09:33:41Z", "value": 51.2, "status": "OK"},
    ],
    4: [
        {"ts": "2026-01-14T06:12:03Z", "value": 1.4, "status": "OK"},
        {"ts": "2026-01-14T10:17:08Z", "value": 3.8, "status": "ALARM_HIGH"},
        {"ts": "2026-01-14T11:02:00Z", "value": 1.2, "status": "OK"},
    ],
    5: [
        {"ts": "2026-01-14T06:12:03Z", "value": 72.1, "status": "OK"},
        {"ts": "2026-01-14T12:44:22Z", "value": 68.9, "status": "OK"},
    ],
    6: [
        {"ts": "2026-01-14T06:12:03Z", "value": 1475, "status": "OK"},
        {"ts": "2026-01-14T14:05:37Z", "value": 1480, "status": "OK"},
    ],
    7: [
        {"ts": "2026-01-13T22:00:00Z", "event": "Scheduled maintenance window started"},
        {"ts": "2026-01-13T22:15:33Z", "event": "Config backup completed"},
        {"ts": "2026-01-13T23:01:17Z", "event": "Service credential rotation"},
        {
            "ts": "2026-01-13T23:01:18Z",
            "event": "credential_sync",
            "data": base64.b64encode(json.dumps({
                "service": "historian-admin",
                "token": SERVICE_TOKEN,
                "generated": "2026-01-13T23:01:18Z",
                "note": "auto-generated service token — rotate before next maintenance window"
            }).encode()).decode()
        },
        {"ts": "2026-01-13T23:45:00Z", "event": "Maintenance window closed"},
        {"ts": "2026-01-14T00:00:01Z", "event": "System returned to production mode"},
    ],
}

# === API Endepunkter ===

@app.route("/")
def index():
    return render_template_string(LANDING_HTML)


@app.route("/api/v1/sensors", methods=["GET"])
def list_sensors():
    """Lister offentlige sensorer."""
    public = {
        sid: {"name": s["name"], "type": s["type"], "unit": s["unit"], "zone": s["zone"]}
        for sid, s in SENSORS.items()
        if s["access"] == "public"
    }
    return jsonify({
        "sensors": public,
        "count": len(public),
        "note": "Kun offentlige sensorer vises. Interne og restrikerte sensorer krever tilgang."
    })


@app.route("/api/v1/sensors/<int:sensor_id>", methods=["GET"])
def get_sensor(sensor_id):
    """Hent sensorinfo. Alle ID-er fungerer — ingen autentisering."""
    sensor = SENSORS.get(sensor_id)
    if not sensor:
        return jsonify({"error": "Sensor ikke funnet", "valid_range": "1-7"}), 404
    return jsonify({"id": sensor_id, **sensor})


@app.route("/api/v1/sensors/<int:sensor_id>/logs", methods=["GET"])
def get_sensor_logs(sensor_id):
    """
    Hent sensorlogger. IDOR: sensor 7 er 'restricted' i metadata,
    men det finnes ingen faktisk tilgangskontroll.
    """
    sensor = SENSORS.get(sensor_id)
    if not sensor:
        return jsonify({"error": "Sensor ikke funnet", "valid_range": "1-7"}), 404

    logs = SENSOR_LOGS.get(sensor_id, [])
    return jsonify({
        "sensor_id": sensor_id,
        "sensor_name": sensor["name"],
        "access_level": sensor["access"],
        "log_count": len(logs),
        "logs": logs
    })


@app.route("/api/v1/debug/endpoints", methods=["GET"])
def debug_endpoints():
    """
    Debug-endepunkt som lister alle tilgjengelige ruter.
    Skal ikke være eksponert i produksjon.
    """
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        endpoints.append({
            "path": str(rule),
            "methods": sorted(rule.methods - {"HEAD", "OPTIONS"}),
            "description": app.view_functions[rule.endpoint].__doc__.strip()
                           if app.view_functions[rule.endpoint].__doc__ else ""
        })
    endpoints.sort(key=lambda e: e["path"])
    return jsonify({
        "warning": "Debug-endepunkt — skal fjernes før produksjon!",
        "api_version": "v1",
        "endpoints": endpoints
    })


@app.route("/api/v1/admin/flag", methods=["GET"])
def admin_flag():
    """
    Admin-endepunkt. Krever gyldig service-token i Authorization-header.
    Eksempel: Authorization: Bearer <token>
    """
    auth = request.headers.get("Authorization", "")

    if not auth:
        return jsonify({
            "error": "Mangler Authorization-header",
            "hint": "Forventet format: Authorization: Bearer <service-token>"
        }), 401

    if not auth.startswith("Bearer "):
        return jsonify({
            "error": "Ugyldig Authorization-format",
            "hint": "Forventet format: Authorization: Bearer <service-token>"
        }), 401

    token = auth.split("Bearer ", 1)[1].strip()

    if token != SERVICE_TOKEN:
        return jsonify({
            "error": "Ugyldig service-token",
            "authenticated": False
        }), 403

    return jsonify({
        "status": "Autentisert",
        "role": "historian-admin",
        "flag": FLAG
    })


# === Landing page ===

LANDING_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Nordverk Historian API</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#0d1117; color:#c9d1d9; font-family:'Courier New',monospace; padding:40px; }
    h1 { color:#21a25e; font-size:18px; letter-spacing:3px; margin-bottom:8px; }
    .subtitle { color:#484f58; font-size:12px; margin-bottom:32px; }
    .section { background:#161b22; border:1px solid #30363d; border-radius:4px; padding:20px 24px; margin-bottom:16px; }
    .section h2 { color:#e6edf3; font-size:13px; letter-spacing:2px; margin-bottom:12px; }
    code { background:#0d1117; border:1px solid #30363d; border-radius:3px; padding:2px 6px; font-size:12px; color:#21a25e; }
    pre { background:#0d1117; border:1px solid #30363d; border-radius:3px; padding:12px; font-size:12px; color:#8b949e; overflow-x:auto; margin-top:8px; }
    a { color:#21a25e; text-decoration:none; }
    a:hover { text-decoration:underline; }
    .note { color:#484f58; font-size:11px; margin-top:24px; }
  </style>
</head>
<body>
  <h1>&#9632; NORDVERK HISTORIAN API</h1>
  <div class="subtitle">Industrial Process Data Archive — REST API v1</div>

  <div class="section">
    <h2>TILGJENGELIGE ENDEPUNKTER</h2>
    <pre>GET  /api/v1/sensors          — List offentlige sensorer
GET  /api/v1/sensors/&lt;id&gt;     — Hent sensordetaljer
GET  /api/v1/sensors/&lt;id&gt;/logs — Hent sensorlogger</pre>
  </div>

  <div class="section">
    <h2>EKSEMPEL</h2>
    <pre>curl http://&lt;host&gt;/api/v1/sensors
curl http://&lt;host&gt;/api/v1/sensors/1/logs</pre>
  </div>

  <div class="note">
    Nordverk AS — Platform B Historian Service<br>
    Intern bruk. Uautorisert tilgang loggf&oslash;res.
  </div>
</body>
</html>
"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
