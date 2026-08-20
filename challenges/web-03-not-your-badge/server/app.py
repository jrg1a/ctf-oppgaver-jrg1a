from __future__ import annotations

from dataclasses import dataclass

from flask import Flask, Response, redirect, render_template_string, request, url_for


FLAG = "CTF{not_your_badge_1007}"

app = Flask(__name__)


@dataclass(frozen=True)
class Badge:
    badge_id: int
    name: str
    company: str
    role: str
    access: str
    note: str


BADGES: dict[int, Badge] = {
    1000: Badge(1000, "Nora Testsen", "DemoPartner AS", "Deltaker", "Expo", "Velkommen til standen."),
    1001: Badge(1001, "Marius Nilsen", "Nordverk", "Standvakt", "Expo + lager", "Mangler navnesnor."),
    1002: Badge(1002, "Sofie Berg", "Nordverk", "Foredragsholder", "Scene B", "Skal ha mikrofon kl. 13:20."),
    1003: Badge(1003, "Jonas Lie", "DemoPartner", "Leverandor", "Expo", "Kun messehall."),
    1004: Badge(1004, "Eli Strand", "Nordverk", "Pressekontakt", "Expo + presse", "Ikke del internplan."),
    1005: Badge(1005, "Ahmed Omar", "Student", "Deltaker", "Expo", "Workshopspor."),
    1006: Badge(1006, "Kari Lund", "Nordverk", "Teknisk vert", "Expo + teknisk", "Skal hente adaptere."),
    1007: Badge(1007, "Servicebadge", "Nordverk", "Beredskap", "Alle soner", f"Internmerknad: {FLAG}"),
    1008: Badge(1008, "Reservebadge", "Nordverk", "Reserve", "Expo", "Ikke utlevert."),
}


BASE_CSS = """
body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f4f7f9;
  color: #17212b;
}
main {
  max-width: 760px;
  margin: 0 auto;
  padding: 56px 24px;
}
.panel, .badge {
  background: #fff;
  border: 1px solid #dce4ea;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(20, 38, 54, 0.08);
}
.panel {
  padding: 28px;
}
.badge {
  overflow: hidden;
}
.badge-head {
  background: #102a43;
  color: #fff;
  padding: 22px 28px;
}
.badge-body {
  padding: 28px;
}
h1 {
  margin: 0 0 12px;
  font-size: 30px;
}
p {
  line-height: 1.55;
}
a, button {
  color: #0b63ce;
}
.button {
  display: inline-block;
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 6px;
  background: #0b63ce;
  color: #fff;
  text-decoration: none;
  font-weight: 650;
}
.meta {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 10px 18px;
  margin-top: 18px;
}
.label {
  color: #657383;
  font-size: 14px;
}
.value {
  font-weight: 650;
}
.note {
  margin-top: 24px;
  padding: 14px 16px;
  border-radius: 6px;
  background: #eef4ff;
  border: 1px solid #c9ddff;
}
code {
  background: #eef2f6;
  padding: 2px 5px;
  border-radius: 4px;
}
"""


PAGE = """
<!doctype html>
<html lang="no">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }}</title>
  <style>{{ css }}</style>
</head>
<body>
  <main>{{ body|safe }}</main>
</body>
</html>
"""


def render_page(title: str, body: str) -> str:
    return render_template_string(PAGE, title=title, body=body, css=BASE_CSS)


@app.route("/")
def index():
    body = """
    <section class="panel">
      <h1>Badgeportalen</h1>
      <p>Velkommen, Nora. Her kan du kontrollere deltakerbadgen din før utskrift.</p>
      <p>Din badge-ID er <code>1000</code>. Batchen for standen ligger i samme nummerområde.</p>
      <a class="button" href="/badge?id=1000">Åpne mitt badge</a>
    </section>
    """
    return render_page("Badgeportalen", body)


@app.route("/badge")
def badge():
    raw_id = request.args.get("id", "")
    if not raw_id:
        return redirect(url_for("index"))
    try:
        badge_id = int(raw_id)
    except ValueError:
        return Response("Badge-ID må være et tall.\n", status=400, mimetype="text/plain")

    record = BADGES.get(badge_id)
    if not record:
        return Response(
            f"Fant ingen badge med id={badge_id} i aktiv utskriftsbatch.\n",
            status=404,
            mimetype="text/plain",
        )

    body = f"""
    <article class="badge">
      <div class="badge-head">
        <h1>{record.name}</h1>
        <p>Badge-ID {record.badge_id}</p>
      </div>
      <div class="badge-body">
        <div class="meta">
          <div class="label">Selskap</div><div class="value">{record.company}</div>
          <div class="label">Rolle</div><div class="value">{record.role}</div>
          <div class="label">Tilgang</div><div class="value">{record.access}</div>
        </div>
        <div class="note">{record.note}</div>
        <p><a href="/">Tilbake</a></p>
      </div>
    </article>
    """
    return render_page(f"Badge {record.badge_id}", body)


@app.route("/healthz")
def healthz():
    return Response("ok\n", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
