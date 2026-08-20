"""
Brønn under press — Startpunkt
================================
Installer avhengigheter:
  pip install pymodbus

Bruk:
  python recon_starter.py <IP> [PORT]

Eksempel:
  python recon_starter.py 10.10.10.5
  python recon_starter.py 127.0.0.1 15020
"""

import sys
import inspect
from pymodbus.client import ModbusTcpClient

TARGET_IP   = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
TARGET_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 502
SLAVE_ID    = 1

HR_LABELS = {
    0: "BOP_STATUS      (0=Lukket, 1=Åpen)",
    1: "TRYKK_BAR       (normalt <200 bar)",
    2: "ESD_AKTIV       (0=Av, 1=På)",
    3: "SIGNATUR        (0=OK, 31337=hacket)",
    4: "VENTIL_POSISJON (0-100%)",
}

COIL_LABELS = {
    0: "ESD_BYPASS      (False=Normal, True=Bypass)",
    1: "ALARM_UNDERTRYKK(False=Alarmer på, True=Dempet)",
    2: "FJERNTILGANG    (True=Aktivert)",
    3: "TRYGG_TILSTAND  (True=System gjenopprettet)",
}


def modbus_call(method, **kwargs):
    """Call pymodbus methods across versions using the correct unit-id keyword."""
    unit_keywords = ("device_id", "slave", "unit")
    try:
        parameters = inspect.signature(method).parameters
    except (TypeError, ValueError):
        parameters = {}

    for keyword in unit_keywords:
        if keyword in parameters:
            return method(**kwargs, **{keyword: SLAVE_ID})

    for keyword in unit_keywords:
        try:
            return method(**kwargs, **{keyword: SLAVE_ID})
        except TypeError as exc:
            if "unexpected keyword argument" not in str(exc):
                raise

    return method(**kwargs)


def les_system(client):
    print("\n=== HOLDING REGISTERS ===")
    result = modbus_call(client.read_holding_registers, address=0, count=30)
    if result.isError():
        print(f"Feil: {result}")
        return

    for addr, val in enumerate(result.registers):
        if addr in HR_LABELS:
            label = HR_LABELS[addr]
        elif 10 <= addr <= 27:
            label = f"FLAGG_REG[{addr - 10}]"
        else:
            continue
        print(f"  HR{addr:2d}: {val:6d}  — {label}")

    print("\n=== COILS ===")
    coils = modbus_call(client.read_coils, address=0, count=4)
    if coils.isError():
        print(f"Feil: {coils}")
        return

    for addr, val in enumerate(coils.bits[:4]):
        label = COIL_LABELS.get(addr, "")
        print(f"  C{addr}: {str(val):5s}  — {label}")

    print("\n=== FLAGG-REGISTRE (HR10-HR27) ===")
    flag_regs = result.registers[10:28]
    raw_bytes = b""
    for r in flag_regs:
        raw_bytes += bytes([(r >> 8) & 0xFF, r & 0xFF])
    decoded = raw_bytes.decode("ascii", errors="replace").rstrip("\x00")
    print(f"  ASCII: {decoded}")
    if decoded.startswith("CTF{"):
        print(f"\n  *** FLAGG FUNNET: {decoded} ***")


def main():
    print(f"Kobler til Modbus TCP {TARGET_IP}:{TARGET_PORT}...")
    client = ModbusTcpClient(TARGET_IP, port=TARGET_PORT)

    if not client.connect():
        print("Kunne ikke koble til serveren.")
        sys.exit(1)

    print("Tilkoblet!")
    les_system(client)
    client.close()


if __name__ == "__main__":
    main()
