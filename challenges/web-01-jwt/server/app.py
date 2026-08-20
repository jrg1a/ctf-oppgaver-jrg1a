"""
CTF Challenge: JWT-manipulering — "Operatørportalen"
Flask app med JWT-basert autentisering.

Sårbarhet: Svakt HMAC-secret som kan crackes med ordliste.
Deltakerne logger inn som guest, cracker secret, forger JWT med role=admin.

Secret: platform
Flagg: CTF{jwt_w3ak_s3cr3t_f0rg3d}
"""

import os
import jwt
from flask import Flask, request, render_template, make_response, redirect, jsonify

app = Flask(__name__)

JWT_SECRET = "platform"
FLAG = "CTF{jwt_w3ak_s3cr3t_f0rg3d}"

USERS = {
    "guest": {"password": "guest", "role": "viewer"},
}


def create_token(username, role):
    payload = {
        "sub": username,
        "role": role,
        "iss": "nordverk-portal",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None


@app.route("/")
def index():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = USERS.get(username)
        if user and user["password"] == password:
            token = create_token(username, user["role"])
            resp = make_response(redirect("/dashboard"))
            resp.set_cookie("session_token", token, httponly=False, samesite="Lax")
            return resp
        else:
            error = "Ugyldig brukernavn eller passord."

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    token = request.cookies.get("session_token")
    if not token:
        return redirect("/login")

    claims = verify_token(token)
    if not claims:
        return render_template("login.html", error="Ugyldig eller utløpt token.")

    return render_template("dashboard.html",
                           username=claims.get("sub", "?"),
                           role=claims.get("role", "?"),
                           raw_token=token)


@app.route("/admin")
def admin():
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"error": "Ingen session_token cookie funnet"}), 401

    claims = verify_token(token)
    if not claims:
        return jsonify({"error": "Ugyldig token-signatur"}), 401

    if claims.get("role") != "admin":
        return jsonify({
            "error": "Ingen tilgang",
            "your_role": claims.get("role"),
            "required_role": "admin"
        }), 403

    return render_template("admin.html", flag=FLAG, username=claims.get("sub"))


@app.route("/logout")
def logout():
    resp = make_response(redirect("/login"))
    resp.delete_cookie("session_token")
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
