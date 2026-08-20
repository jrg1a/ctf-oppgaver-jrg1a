"""
LØSNING (ikke gi til deltakerne!)
Riktig sekvens for å gjenopprette BOP-systemet og hente flagget.
"""

import sys
import inspect
from pymodbus.client import ModbusTcpClient

TARGET_IP   = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
TARGET_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 502
SLAVE_ID    = 1


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


def read_flag(client):
    result = modbus_call(client.read_holding_registers, address=10, count=18)
    raw = b""
    for r in result.registers:
        raw += bytes([(r >> 8) & 0xFF, r & 0xFF])
    return raw.decode("ascii", errors="replace").rstrip("\x00")


def main():
    client = ModbusTcpClient(TARGET_IP, port=TARGET_PORT)
    client.connect()

    print("[*] Steg 1: Slår av ESD bypass (C0 = False)")
    modbus_call(client.write_coil, address=0, value=False)

    print("[*] Steg 2: Lukker BOP (HR0 = 0)")
    modbus_call(client.write_register, address=0, value=0)

    print("[*] Steg 3: Aktiverer ESD (HR2 = 1)")
    modbus_call(client.write_register, address=2, value=1)

    print("[*] Steg 4: Stenger ventil (HR4 = 0)")
    modbus_call(client.write_register, address=4, value=0)

    print("[*] Steg 5: Skrur på alarmer (C1 = False)")
    modbus_call(client.write_coil, address=1, value=False)

    flag = read_flag(client)
    if flag.startswith("CTF{"):
        print(f"\n[+] FLAGG: {flag}")
    else:
        print(f"[-] Sekvens ikke fullstendig ennå. HR10-27: {flag!r}")

    client.close()


if __name__ == "__main__":
    main()
