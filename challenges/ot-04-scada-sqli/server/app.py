"""
CTF Challenge: Fake SCADA HMI — SQL Injection
Flask + SQLite

Sårbarhet: password-feltet er direkte konkatenert i SQL-query.
Filter: blokkerer --, #, /*, og OR (ordgrense) — standard cheat sheets feiler.
Løsning: UNION-basert injection uten trailing comment.
"""

import sqlite3, re, os
from flask import Flask, request, render_template, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB = os.path.join(os.path.dirname(__file__), "scada.db")

BLOCKED = [
    r"--",
    r"#",
    r"/\*",
    r"\bor\b",          # OR som eget ord (blokkerer OR men ikke FLOOR, ORDER)
]

def is_filtered(value: str) -> bool:
    for pattern in BLOCKED:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False


def query_login(username: str, password: str):
    """
    Parameterized på username (trygt), direkte interpolering på password (sårbart).
    Query returnerer (id, username, role).
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    sql = f"SELECT id, username, role FROM users WHERE username=? AND password='{password}'"
    try:
        c.execute(sql, (username,))
        row = c.fetchone()
    except sqlite3.Error:
        row = None
    conn.close()
    return row


@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Filtrer farlige mønstre i password-feltet
        if is_filtered(password):
            error = "Ugyldig tegn i passord."
            return render_template("login.html", error=error)

        user = query_login(username, password)

        if user:
            session["user_id"]  = user[0]
            session["username"] = user[1]
            session["role"]     = user[2]
            return render_template("dashboard.html",
                                   username=user[1],
                                   role=user[2])
        else:
            error = "Ugyldig brukernavn eller passord."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html", error=None)


if __name__ == "__main__":
    from init_db import init
    init()
    app.run(host="0.0.0.0", port=5000, debug=False)
