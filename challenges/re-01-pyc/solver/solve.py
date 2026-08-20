"""
LØSNING — RE-01: Python-spionen

Metode 1: Dekompiler .pyc med pycdc eller decompyle3
  pip install decompyle3
  decompyle3 agent.pyc

Metode 2: XOR brute force (enkeltbyte nøkkel, 0x00–0xFF)
  Ser etter strenger som starter med 'CTF{'

Metode 3: dis-modulen (disassemble bytekode)
  python3 -c "import dis, marshal; f=open('agent.pyc','rb'); f.read(16); dis.dis(marshal.loads(f.read()))"

Nedenfor: brute force av XOR-nøkkel.
"""

# Ekstraher de XOR-krypterte bytene fra .pyc (kjent fra disassembly)
kryptert = [
    0x08, 0x1F, 0x0D, 0x30, 0x3B, 0x32, 0x28, 0x14,
    0x39, 0x78, 0x3D, 0x78, 0x39, 0x38, 0x78, 0x2F,
    0x14, 0x7F, 0x2C, 0x78, 0x25, 0x3F, 0x36
]

print("=== Brute force XOR-nøkkel ===")
for key in range(256):
    decoded = "".join(chr(b ^ key) for b in kryptert)
    if decoded.startswith("CTF{") and decoded.endswith("}"):
        print(f"Nøkkel: 0x{key:02X} ({chr(key)})")
        print(f"Flagg:  {decoded}")
