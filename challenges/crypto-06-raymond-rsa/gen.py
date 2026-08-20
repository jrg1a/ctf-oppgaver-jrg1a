#!/usr/bin/env python3
"""Generate Raymonds RSA.

RSA with a larger modulus than the old intro task, but with p and q close
enough for Fermat factorization.
"""

from __future__ import annotations

import json
import random
from pathlib import Path


FLAG = b"CTF{ferm4t_fant_raymonds_primer}"
E = 65537
SEED = 20260608


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41):
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


def next_prime(n: int) -> int:
    if n <= 2:
        return 2
    n |= 1
    while not is_probable_prime(n):
        n += 2
    return n


def main() -> None:
    rng = random.Random(SEED)
    base = rng.getrandbits(256) | (1 << 255) | 1
    p = next_prime(base)
    q = next_prime(p + (1 << 24) + 1337)
    while ((p - 1) * (q - 1)) % E == 0:
        q = next_prime(q + 2)

    n = p * q
    m = int.from_bytes(FLAG, "big")
    if m >= n:
        raise ValueError("flag integer is too large for modulus")
    c = pow(m, E, n)

    out = {
        "e": E,
        "n": n,
        "c": c,
        "note": "Raymond kalte dette en stor demonøkkel. Primtallene hans var litt for ryddige.",
    }

    out_dir = Path(__file__).parent / "dist"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "raymond_rsa.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[+] p={p}")
    print(f"[+] q={q}")
    print(f"[+] n has {n.bit_length()} bits")
    print(f"[+] flag={FLAG.decode()}")


if __name__ == "__main__":
    main()
