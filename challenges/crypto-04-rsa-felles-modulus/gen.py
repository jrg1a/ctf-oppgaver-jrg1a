"""
Generer To nøkler, samme modul.

RSA common modulus attack.
Flagg: CTF{rsa_common_modulus_gjor_vondt}
"""

from __future__ import annotations

import json
import random
from pathlib import Path


FLAG = "CTF{rsa_common_modulus_gjor_vondt}"
RNG = random.Random(0x20260525)


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    if n in small_primes:
        return True
    if any(n % p == 0 for p in small_primes):
        return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in [2, 3, 5, 7, 11, 13, 17]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(bits: int) -> int:
    while True:
        candidate = RNG.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(candidate):
            return candidate


def main() -> None:
    p = random_prime(384)
    q = random_prime(384)
    n = p * q
    e1 = 17
    e2 = 65537
    message = f"Nordverk emergency RSA note: {FLAG}".encode()
    m = int.from_bytes(message, "big")
    assert m < n

    data = {
        "n": n,
        "e1": e1,
        "c1": pow(m, e1, n),
        "e2": e2,
        "c2": pow(m, e2, n),
        "note": "Same plaintext. Same modulus. Different public exponents.",
    }
    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "rsa_felles_modulus.json").write_text(json.dumps(data, indent=2) + "\n")
    print("[+] Skrev dist/rsa_felles_modulus.json")
    print(f"[+] Flagg: {FLAG}")


if __name__ == "__main__":
    main()
