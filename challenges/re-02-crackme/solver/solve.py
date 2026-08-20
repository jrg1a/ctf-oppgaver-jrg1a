"""
LØSNING — RE-02: Crackme

Analyse med Ghidra/IDA avslører:
  - sjekk_lengde(): passordet må være 10 tegn
  - sjekk_tegn(): hvert tegn sammenlignes med forventet[]-arrayet
  - forventet[] = [0x4E, 0x30, 0x72, 0x64, 0x76, 0x65, 0x72, 0x6B, 0x21, 0x3F]
                = "N0rdverk!?"

Raskere: ltrace ./crackme testpassord
  viser kallet til strcmp eller minnesammenligningen

Flagget genereres ved å XOR passordet med flagg_kryptert[]-arrayet.
"""

# Direkte løsning fra analyse:
forventet = [0x4E, 0x30, 0x72, 0x64, 0x76, 0x65, 0x72, 0x6B, 0x21, 0x3F]
passord = "".join(chr(b) for b in forventet)
print(f"Passordet: {passord}")

flagg_kryptert = [
    0x0D, 0x64, 0x34, 0x1F, 0x15, 0x17, 0x46, 0x08,
    0x4A, 0x52, 0x7D, 0x6F, 0x00, 0x57, 0x00, 0x56,
    0x00, 0x18, 0x12, 0x5B, 0x11, 0x5F, 0x19, 0x19
]

flagg = "".join(chr(flagg_kryptert[i] ^ ord(passord[i % len(passord)]))
               for i in range(len(flagg_kryptert)))
print(f"Flagg:     {flagg}")
