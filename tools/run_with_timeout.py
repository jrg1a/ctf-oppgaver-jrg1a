#!/usr/bin/env python3
"""Run a command with a portable timeout for macOS and Linux."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: run_with_timeout.py SECONDS COMMAND [ARG ...]", file=sys.stderr)
        return 2

    seconds = float(sys.argv[1])
    try:
        return subprocess.run(sys.argv[2:], timeout=seconds).returncode
    except subprocess.TimeoutExpired:
        print(f"command timed out after {seconds:g} seconds", file=sys.stderr)
        return 124


if __name__ == "__main__":
    raise SystemExit(main())
