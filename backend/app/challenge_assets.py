"""Generates the real artifacts students download and solve.

Every puzzle string and file here is derived from the challenge's actual flag, so a
correct solution always yields exactly the flag stored in the database.
"""

import os
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

FILES_DIR = Path(__file__).resolve().parent.parent / "challenge_files"


# --------------------------------------------------------------------------
# Cryptography puzzle generation
# --------------------------------------------------------------------------

def caesar_encrypt(text: str, shift: int = 3) -> str:
    out = []
    for ch in text:
        if ch.isalpha():
            base = ord("a") if ch.islower() else ord("A")
            out.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            out.append(ch)
    return "".join(out)


def xor_encrypt_hex(text: str, key: int) -> str:
    return bytes(b ^ key for b in text.encode()).hex()


# RSA with two primes that sit very close together, so Fermat factorisation
# recovers them instantly. Verified: pow(RSA_C, d, RSA_N) == the flag bytes.
RSA_P = 1021562916192451394165434769499684636316603
RSA_Q = 1021562916192451394165434769499902279237447
RSA_N = RSA_P * RSA_Q
RSA_E = 65537
RSA_FLAG = "AVST{close_primes_fermat_attack}"
RSA_C = pow(int.from_bytes(RSA_FLAG.encode(), "big"), RSA_E, RSA_N)


# --------------------------------------------------------------------------
# Binary artifact generation
# --------------------------------------------------------------------------

def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_stego_png(flag: str, path: Path) -> None:
    """A valid 64x64 PNG carrying the flag in a tEXt chunk and after IEND."""
    width = height = 64
    raw = b""
    for y in range(height):
        raw += b"\x00" + bytes(((x * 4 + y * 2) % 256) for x in range(width))

    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
    png += _png_chunk(b"tEXt", b"Comment\x00evidence photo - do not distribute")
    png += _png_chunk(b"tEXt", b"Secret\x00" + flag.encode())
    png += _png_chunk(b"IDAT", zlib.compress(raw, 9))
    png += _png_chunk(b"IEND", b"")
    png += b"\n--- appended data ---\n" + flag.encode() + b"\n"

    path.write_bytes(png)


def _tcp_packet(src_ip, dst_ip, sport, dport, seq, ack, payload: bytes) -> bytes:
    """Ethernet + IPv4 + TCP frame carrying `payload`."""
    eth = b"\x00\x0c\x29\x1a\x2b\x3c" + b"\x00\x50\x56\xc0\x00\x08" + b"\x08\x00"

    tcp_len = 20
    tcp = struct.pack(
        ">HHIIBBHHH", sport, dport, seq, ack, (tcp_len // 4) << 4, 0x18, 8192, 0, 0
    )
    tcp += payload

    total_len = 20 + len(tcp)
    ip = struct.pack(
        ">BBHHHBBH4s4s",
        0x45, 0, total_len, 0x1234, 0x4000, 64, 6, 0,
        bytes(int(o) for o in src_ip.split(".")),
        bytes(int(o) for o in dst_ip.split(".")),
    )
    checksum = 0
    for i in range(0, len(ip), 2):
        checksum += (ip[i] << 8) + ip[i + 1]
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    ip = ip[:10] + struct.pack(">H", ~checksum & 0xFFFF) + ip[12:]

    return eth + ip + tcp


def write_ftp_pcap(flag: str, path: Path) -> None:
    """A real libpcap file containing a cleartext FTP login whose password is the flag."""
    out = struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)  # DLT_EN10MB

    conversation = [
        (True, b"220 corp-ftp01 FTP server (Version 6.00LS) ready.\r\n"),
        (False, b"USER jmathews\r\n"),
        (True, b"331 Password required for jmathews.\r\n"),
        (False, b"PASS " + flag.encode() + b"\r\n"),
        (True, b"230 User jmathews logged in.\r\n"),
        (False, b"SYST\r\n"),
        (True, b"215 UNIX Type: L8\r\n"),
        (False, b"QUIT\r\n"),
        (True, b"221 Goodbye.\r\n"),
    ]

    ts = 1757923200
    seq_c, seq_s = 1000, 5000
    for i, (from_server, payload) in enumerate(conversation):
        if from_server:
            pkt = _tcp_packet("192.168.1.50", "192.168.1.101", 21, 49512, seq_s, seq_c, payload)
            seq_s += len(payload)
        else:
            pkt = _tcp_packet("192.168.1.101", "192.168.1.50", 49512, 21, seq_c, seq_s, payload)
            seq_c += len(payload)
        out += struct.pack("<IIII", ts, i * 120000, len(pkt), len(pkt)) + pkt

    path.write_bytes(out)


def write_disk_image(flag: str, path: Path) -> None:
    """Raw image where a 'deleted' PNG survives in unallocated space, carvable by signature."""
    block = 512
    image = bytearray()

    image += b"AVSTFS01" + b"\x00" * (block - 8)  # superblock

    # Directory table: the deleted entry's name is zeroed out, data blocks untouched.
    directory = bytearray()
    directory += b"readme.txt".ljust(32, b"\x00") + struct.pack("<II", 4, 64)
    directory += b"\x00" * 32 + struct.pack("<II", 8, 0)  # <- deleted entry
    directory += b"notes.txt".ljust(32, b"\x00") + struct.pack("<II", 20, 48)
    image += directory.ljust(block * 3, b"\x00")

    image += b"Nothing to see here. Routine maintenance log.\n".ljust(block * 4, b"\x00")

    secret = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    secret.close()
    write_stego_png(flag, Path(secret.name))
    payload = Path(secret.name).read_bytes()
    os.unlink(secret.name)

    padded = payload + b"\x00" * ((block - len(payload) % block) % block)
    image += padded

    image += b"Quarterly review scheduled for Monday.\n".ljust(block * 6, b"\x00")
    image += bytes((i * 7 + 13) % 256 for i in range(block * 8))

    path.write_bytes(bytes(image))


def write_memory_dump(flag: str, path: Path) -> None:
    """Synthetic RAM dump: a 32-byte key sits near the malicious process, and the
    flag is stored XOR-encrypted with that key."""
    key = bytes((i * 31 + 7) % 256 for i in range(32))
    encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(flag.encode()))

    dump = bytearray()
    dump += bytes((i * 13 + 5) % 256 for i in range(4096))

    dump += b"\n=== PROCESS LIST ===\n"
    for pid, name in [
        (1, "launchd"), (412, "sshd"), (908, "nginx"), (1204, "postgres"),
        (2317, "svch0st.exe"), (2410, "python3"),
    ]:
        dump += f"PID {pid:<6} {name}\n".encode()

    dump += b"\n=== PID 2317 svch0st.exe : HEAP REGION 0x7ffd2a00 ===\n"
    dump += b"cfg.beacon_interval=60\n"
    dump += b"cfg.c2=185.203.116.44:8443\n"
    dump += b"cfg.crypto=xor-repeating-key\n"
    dump += b"cfg.key_len=32\n"
    dump += b"KEYBLOB:" + key + b"\n"
    # hex-encoded so the ciphertext can never contain a delimiter byte
    dump += b"VAULT_HEX:" + encrypted.hex().encode() + b"\n"
    dump += b"cfg.wipe_on_exit=false\n"

    dump += bytes((i * 29 + 11) % 256 for i in range(4096))
    path.write_bytes(bytes(dump))


# --------------------------------------------------------------------------
# Reverse-engineering binaries
# --------------------------------------------------------------------------

def _xor_array(text: str, key: int) -> str:
    return ", ".join(f"0x{b ^ key:02x}" for b in text.encode())


def crackme_sources(flags: dict) -> dict:
    """C source for each reverse-engineering binary, keyed by output filename."""
    basic = flags["basic"]
    xor_flag = flags["xor"]
    maze = flags["maze"]
    antidbg = flags["antidbg"]

    xor_key = 0x5A
    antidbg_key = 0x3B

    return {
        "crackme": f"""
#include <stdio.h>
#include <string.h>

int main(void) {{
    char input[128];
    printf("Enter password: ");
    if (!fgets(input, sizeof(input), stdin)) return 1;
    input[strcspn(input, "\\n")] = 0;

    if (strcmp(input, "sup3rs3cr3t_p4ssw0rd") == 0) {{
        printf("Access granted. Flag: {basic}\\n");
        return 0;
    }}
    printf("Access denied.\\n");
    return 1;
}}
""",
        "xor_armor": f"""
#include <stdio.h>
#include <string.h>

static unsigned char enc[] = {{ {_xor_array(xor_flag, xor_key)} }};
static const unsigned char k = 0x{xor_key:02x};

int main(void) {{
    char input[128];
    unsigned char dec[sizeof(enc) + 1];
    size_t i;

    for (i = 0; i < sizeof(enc); i++) dec[i] = enc[i] ^ k;
    dec[sizeof(enc)] = 0;

    printf("Enter the flag: ");
    if (!fgets(input, sizeof(input), stdin)) return 1;
    input[strcspn(input, "\\n")] = 0;

    if (strcmp(input, (char *)dec) == 0) printf("Correct!\\n");
    else printf("Nope.\\n");
    return 0;
}}
""",
        "the_maze": f"""
#include <stdio.h>
#include <string.h>

/* input layout: AVST{{ + 5 segments + }} */
static int stage1(const char *s) {{ return strncmp(s, "AVST{{", 5) == 0; }}
static int stage2(const char *s) {{
    int sum = 0; for (int i = 5; i < 11; i++) sum += s[i];
    return sum == {sum(ord(c) for c in maze[5:11])};
}}
static int stage3(const char *s) {{
    for (int i = 5; i < 11; i++) if (s[i] != "{maze[5:11]}"[i-5]) return 0;
    return 1;
}}
static int stage4(const char *s) {{
    char buf[32]; int n = 0;
    for (int i = 11; i < 11 + {len(maze[11:-1])}; i++) buf[n++] = s[i] ^ 0x11;
    buf[n] = 0;
    static const char want[] = {{ {_xor_array(maze[11:-1], 0x11)}, 0 }};
    return memcmp(buf, want, n) == 0;
}}
static int stage5(const char *s) {{ return s[strlen(s)-1] == '}}' && strlen(s) == {len(maze)}; }}

int main(void) {{
    char input[128];
    printf("Enter the flag: ");
    if (!fgets(input, sizeof(input), stdin)) return 1;
    input[strcspn(input, "\\n")] = 0;

    if (stage1(input) && stage2(input) && stage3(input) && stage4(input) && stage5(input))
        printf("Correct! You escaped the maze.\\n");
    else
        printf("Wrong.\\n");
    return 0;
}}
""",
        "fortress": f"""
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <unistd.h>

#ifdef __APPLE__
#include <sys/ptrace.h>
#define DENY_ATTACH() ptrace(PT_DENY_ATTACH, 0, 0, 0)
#else
#include <sys/ptrace.h>
#define DENY_ATTACH() ptrace(PTRACE_TRACEME, 0, 0, 0)
#endif

static unsigned char enc[] = {{ {_xor_array(antidbg, antidbg_key)} }};
static unsigned char pw[] = {{ {_xor_array("unl0ck_th3_f0rtr3ss", 0x6D)} }};

static int debugger_present(void) {{
    if (DENY_ATTACH() < 0) return 1;
    return 0;
}}

static int stepping_detected(void) {{
    clock_t a = clock();
    volatile int x = 0;
    for (int i = 0; i < 1000; i++) x += i;
    clock_t b = clock();
    return (double)(b - a) / CLOCKS_PER_SEC > 0.5;
}}

int main(void) {{
    char input[128];
    char want[sizeof(pw) + 1];

    if (debugger_present()) {{ printf("Nice try, debugger.\\n"); return 1; }}
    if (stepping_detected()) {{ printf("Single-stepping detected.\\n"); return 1; }}

    for (size_t i = 0; i < sizeof(pw); i++) want[i] = pw[i] ^ 0x6d;
    want[sizeof(pw)] = 0;

    printf("Passphrase: ");
    if (!fgets(input, sizeof(input), stdin)) return 1;
    input[strcspn(input, "\\n")] = 0;

    if (strcmp(input, want) != 0) {{ printf("The gate stays shut.\\n"); return 1; }}

    char dec[sizeof(enc) + 1];
    for (size_t i = 0; i < sizeof(enc); i++) dec[i] = enc[i] ^ 0x{antidbg_key:02x};
    dec[sizeof(enc)] = 0;

    printf("Fortress breached. Flag: %s\\n", dec);
    return 0;
}}
""",
    }


def compile_crackmes(flags: dict) -> list:
    """Compile the RE binaries with the system C compiler. Returns filenames built."""
    compiler = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
    if not compiler:
        return []

    built = []
    for name, source in crackme_sources(flags).items():
        target = FILES_DIR / name
        if target.exists():
            built.append(name)
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".c", delete=False) as fh:
            fh.write(source)
            src_path = fh.name
        try:
            result = subprocess.run(
                [compiler, "-w", "-O0", src_path, "-o", str(target)],
                capture_output=True,
                timeout=60,
            )
            if result.returncode == 0:
                built.append(name)
            else:
                print(f"[assets] failed to build {name}: {result.stderr.decode()[:200]}")
        except (subprocess.SubprocessError, OSError) as exc:
            print(f"[assets] failed to build {name}: {exc}")
        finally:
            os.unlink(src_path)
    return built


# --------------------------------------------------------------------------

def generate_all(file_flags: dict, crackme_flags: dict) -> list:
    """Create every downloadable artifact. Idempotent — existing files are kept."""
    FILES_DIR.mkdir(parents=True, exist_ok=True)

    builders = {
        "evidence.png": write_stego_png,
        "capture.pcap": write_ftp_pcap,
        "disk.img": write_disk_image,
        "memory.dmp": write_memory_dump,
    }

    created = []
    for filename, builder in builders.items():
        target = FILES_DIR / filename
        if not target.exists():
            builder(file_flags[filename], target)
        created.append(filename)

    created.extend(compile_crackmes(crackme_flags))
    return created
