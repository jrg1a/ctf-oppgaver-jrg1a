#!/usr/bin/env python3
"""Generate phishing EML artifact."""

from __future__ import annotations

from email.message import EmailMessage
from email.policy import SMTP
from pathlib import Path


FLAG = "CTF{mail_h3ad3rs_og_m1me}"
OUT = Path(__file__).resolve().parent / "dist" / "mistenkelig_epost.eml"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    msg = EmailMessage(policy=SMTP)
    msg["From"] = "Nordverk Sikkerhet <sikkerhet@nordverk-secure.example>"
    msg["To"] = "messe-team@nordverk.local"
    msg["Reply-To"] = "support@n0rdverk.example"
    msg["Subject"] = "Haster: bekreft konferansetilgang"
    msg["Date"] = "Thu, 11 Jun 2026 08:14:22 +0200"
    msg["Message-ID"] = "<konferanse-verify-260611@nordverk-secure.example>"
    msg["Received"] = "from mail-gw.n0rdverk.example (203.0.113.77) by mx.nordverk.local"
    msg["Authentication-Results"] = (
        "mx.nordverk.local; spf=fail smtp.mailfrom=nordverk-secure.example; "
        "dkim=none; dmarc=fail"
    )

    msg.set_content(
        "Hei,\n\n"
        "Vi må bekrefte tilgangen din til konferanseportalen før dagens sesjoner.\n"
        "Se vedlegget for detaljer.\n\n"
        "Nordverk Sikkerhet\n"
    )

    html = f"""<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Nordverk Konferanseinnlogging</title></head>
  <body>
    <h1>Bekreft konferansetilgang</h1>
    <p>Session timeout. Logg inn på nytt:</p>
    <a href="https://n0rdverk.example/login?ticket={FLAG}">Fortsett</a>
    <!-- incident-token: {FLAG} -->
  </body>
</html>
"""
    msg.add_attachment(html, subtype="html", filename="konferanse-login.html")

    OUT.write_bytes(msg.as_bytes())
    print(f"[+] Skrev {OUT}")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()

