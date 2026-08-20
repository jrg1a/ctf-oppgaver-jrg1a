from flask import Flask, Response, render_template_string


app = Flask(__name__)

FLAG = "CTF{r0b0ts_og_b4ckup_fant}"

INDEX_HTML = """
<!doctype html>
<html lang="no">
<head>
  <meta charset="utf-8">
  <title>Nordverk Konferansestand</title>
  <style>
    body { margin: 0; font-family: system-ui, sans-serif; background: #101820; color: #f2f5f7; }
    main { max-width: 760px; margin: 0 auto; padding: 64px 24px; }
    h1 { color: #7bd88f; font-size: 28px; margin-bottom: 8px; }
    p { color: #bac7d1; line-height: 1.6; }
    code { color: #7bd88f; }
  </style>
</head>
<body>
  <main>
    <h1>Nordverk Konferansestand</h1>
    <p>Intern infoside for vaktliste, riggstatus og demomiljø.</p>
    <p>Status: <code>production</code></p>
  </main>
</body>
</html>
"""

BACKUP = f"""# config.py - gammel backup fra staging
ENV = "staging"
DEBUG = True
DATABASE_URL = "sqlite:///demo_stand.db"
ADMIN_USER = "standadmin"
ADMIN_PASSWORD = "byttet-for-deploy"
LEGACY_INCIDENT_TOKEN = "{FLAG}"
"""


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/robots.txt")
def robots():
    return Response(
        "User-agent: *\nDisallow: /backup/\nDisallow: /admin-staging/\n",
        mimetype="text/plain",
    )


@app.route("/backup/config.py.bak")
def backup():
    return Response(BACKUP, mimetype="text/plain")


@app.route("/backup/")
def backup_index():
    return Response(
        "Directory listing disabled.\n"
        "TODO WEB-42: rydd gamle Flask config-backups før produksjon.\n",
        mimetype="text/plain",
        status=403,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
