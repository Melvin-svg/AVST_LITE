import hashlib
import json

from .database import Base, SessionLocal, engine
from . import models
from . import challenge_assets as assets


def flag_hash(flag: str) -> str:
    return hashlib.sha256(flag.strip().encode()).hexdigest()


FLAG_FORMAT = "AVST{...}"

# Files each artifact-based challenge ships, keyed by its flag (so generation and
# verification stay in sync).
FILE_FLAGS = {
    "evidence.png": "AVST{steganography_basics}",
    "capture.pcap": "AVST{plaintext_ftp_credentials}",
    "disk.img": "AVST{file_carving_recovery}",
    "memory.dmp": "AVST{memory_forensics_key_extraction}",
}
CRACKME_FLAGS = {
    "basic": "AVST{reversing_is_fun}",
    "xor": "AVST{static_xor_deobfuscated}",
    "maze": "AVST{multistage_validation_solved}",
    "antidbg": "AVST{anti_debug_bypassed}",
}

# Correct, round-trip-verified crypto puzzle strings (see challenge_assets.py).
CAESAR_CT = assets.caesar_encrypt("AVST{caesar_cipher_is_easy}")  # DYVW{...}, shift +3
XOR_KEY = 0x42
XOR_CT = assets.xor_encrypt_hex("AVST{single_byte_xor_recovered}", XOR_KEY)

CHALLENGES = [
    # ---------------- Web Security ----------------
    {
        "title": "Login Bypass 101",
        "category": "Web Security",
        "difficulty": "Easy",
        "description": (
            "Start the SQL Injection lab (docker/sqli-lab) and open the staging login "
            "form at http://localhost:5001/lab/sqli-login. It builds its SQL query by "
            "concatenating your input directly. Log in as admin without the password to "
            "reveal the flag."
        ),
        "points": 100,
        "flag": "AVST{sql_injection_login_bypass}",
        "hints": [
            "Enter a single quote (') in the username field and watch for a SQL error — that confirms the input reaches the query unescaped.",
            "The query looks like: SELECT * FROM users WHERE username='<you>' AND password='<you>'.",
            "Log in with username  admin' --  and any password. The -- comments out the password check, and the admin row's response contains the flag.",
        ],
        "docker_lab": "sqli-lab",
    },
    {
        "title": "Reflected Alert",
        "category": "Web Security",
        "difficulty": "Easy",
        "description": (
            "Start the XSS lab (docker/xss-lab) and open http://localhost:5002/lab/xss-search. "
            "The search box reflects your query into the page without escaping it. Inject "
            "JavaScript that sets a global flag variable, and the page will reveal the flag "
            "in its title."
        ),
        "points": 100,
        "flag": "AVST{reflected_xss_alert_1}",
        "hints": [
            "Type <b>hi</b> into the search box — if it renders bold, HTML is being injected.",
            "The page checks for window.__avst_xss_triggered. You need to run JavaScript that sets it to true.",
            "Search for:  <script>window.__avst_xss_triggered=true</script>  then check the browser tab title for the flag.",
        ],
        "docker_lab": "xss-lab",
    },
    {
        "title": "Invoice Peeker",
        "category": "Web Security",
        "difficulty": "Medium",
        "description": (
            "A billing portal serves invoices at /invoices/{id}, but never checks whether "
            "the invoice belongs to you. Your own invoice is #1043. Somewhere in the low "
            "id range is an internal invoice containing the flag. (Conceptual challenge — "
            "walk through the reasoning in the AI assistant.)"
        ),
        "points": 150,
        "flag": "AVST{idor_invoice_leak}",
        "hints": [
            "This bug class is Insecure Direct Object Reference (IDOR): the server trusts the id you request.",
            "Since ownership is never verified, you can request invoices that aren't yours by changing the id.",
            "Enumerate low ids (/invoices/1, /invoices/2, ...). The internal invoice #7 holds the flag: AVST{idor_invoice_leak}.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Forge the Token",
        "category": "Web Security",
        "difficulty": "Medium",
        "description": (
            "An API session token leaked in a support ticket:\n\n"
            "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9."
            "eyJ1c2VyIjogImd1ZXN0IiwgInJvbGUiOiAidXNlciJ9.c2lnbmF0dXJl\n\n"
            "The server accepts tokens whose header says \"alg\":\"none\". Decode the token, "
            "understand its structure, then reason out the admin forgery in the assistant."
        ),
        "points": 175,
        "flag": "AVST{jwt_alg_none_forgery}",
        "hints": [
            "A JWT is three base64url parts: header.payload.signature. Decode the first two — they're not encrypted.",
            "The payload is {\"user\":\"guest\",\"role\":\"user\"}. To become admin you'd change role to \"admin\".",
            "With alg:none accepted, you re-encode header {\"alg\":\"none\"} and payload {\"role\":\"admin\"} with an empty signature. Successfully reasoning through this yields: AVST{jwt_alg_none_forgery}.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Internal Only",
        "category": "Web Security",
        "difficulty": "Hard",
        "description": (
            "A 'fetch preview' feature requests any URL you supply and shows the response. "
            "It's meant for public images, but never restricts the target host. Cloud "
            "instances expose an internal metadata service. Reason through what URL leaks "
            "internal credentials."
        ),
        "points": 225,
        "flag": "AVST{ssrf_metadata_leak}",
        "hints": [
            "This is Server-Side Request Forgery (SSRF): the server fetches URLs on your behalf, from inside its own network.",
            "Cloud metadata services live at the link-local address 169.254.169.254.",
            "Pointing the fetch feature at http://169.254.169.254/latest/meta-data/ leaks internal data — the flag for solving this is AVST{ssrf_metadata_leak}.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Blind Faith",
        "category": "Web Security",
        "difficulty": "Insane",
        "description": (
            "The login from 'Login Bypass 101' has been patched so errors and content are "
            "identical whether the query succeeds or fails — but response timing still "
            "leaks. Reason through how you'd extract the admin password one character at a "
            "time using a time-based side channel."
        ),
        "points": 350,
        "flag": "AVST{blind_time_based_sqli}",
        "hints": [
            "With no visible difference in responses, you need a side channel: make the database sleep when a condition is true.",
            "Inject a payload like:  ' OR IF(SUBSTR(password,1,1)='a', SLEEP(2), 0) --  and measure the response time.",
            "Binary-search each character position by timing. Automating this full extraction is the skill; the flag is AVST{blind_time_based_sqli}.",
        ],
        "docker_lab": None,
    },
    # ---------------- Cryptography ----------------
    {
        "title": "Caesar's Secret",
        "category": "Cryptography",
        "difficulty": "Easy",
        "description": (
            "We intercepted this message:\n\n"
            f"    {CAESAR_CT}\n\n"
            "It's a Caesar cipher — every letter shifted by a fixed amount. Decrypt it to "
            "recover the flag."
        ),
        "points": 75,
        "flag": "AVST{caesar_cipher_is_easy}",
        "hints": [
            "A Caesar cipher shifts each letter by a constant. Digits and symbols like { _ } stay unchanged.",
            "The ciphertext starts with D-Y-V-W. The flag starts with A-V-S-T. D->A is a shift of 3.",
            "Shift every letter back by 3 (D->A, Y->V, V->S, W->T ...) to read the full flag.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Single Byte Shield",
        "category": "Cryptography",
        "difficulty": "Medium",
        "description": (
            "This flag was XOR-encrypted with a single repeating byte key. Ciphertext (hex):\n\n"
            f"    {XOR_CT}\n\n"
            "Recover the key and the plaintext flag."
        ),
        "points": 150,
        "flag": "AVST{single_byte_xor_recovered}",
        "hints": [
            "Single-byte XOR has only 256 possible keys — you can brute force all of them.",
            "You know the plaintext starts with 'A' (0x41). XOR the first ciphertext byte (0x03) with 0x41 to get the key: 0x42.",
            "XOR every byte with 0x42 and decode as ASCII to read the flag.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Twin Primes",
        "category": "Cryptography",
        "difficulty": "Hard",
        "description": (
            "An RSA public key and ciphertext were intercepted. The two primes were "
            "generated too close together, making the modulus vulnerable to Fermat "
            "factorization.\n\n"
            f"    n = {assets.RSA_N}\n"
            f"    e = {assets.RSA_E}\n"
            f"    c = {assets.RSA_C}\n\n"
            "Factor n, recover the private key, and decrypt c to bytes to read the flag."
        ),
        "points": 250,
        "flag": "AVST{close_primes_fermat_attack}",
        "hints": [
            "When RSA primes p and q are close, n can be factored fast with Fermat's method: search a from ceil(sqrt(n)) upward until a*a - n is a perfect square b*b; then p=a-b, q=a+b.",
            "With p and q, compute phi=(p-1)*(q-1) and the private exponent d = pow(e, -1, phi).",
            "Decrypt m = pow(c, d, n), then convert the integer to bytes (big-endian) to read the flag.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Padding Oracle Whispers",
        "category": "Cryptography",
        "difficulty": "Insane",
        "description": (
            "A legacy service encrypts cookies with AES-CBC and returns a distinct 'bad "
            "padding' error when decryption fails PKCS#7 validation. Reason through how "
            "this oracle lets you decrypt an intercepted ciphertext without the key."
        ),
        "points": 400,
        "flag": "AVST{padding_oracle_full_decrypt}",
        "hints": [
            "The classic CBC Padding Oracle: the server leaks one bit per request — whether the padding is valid.",
            "By tampering with the previous ciphertext block byte-by-byte, you force valid-padding responses that reveal each intermediate-state byte, then XOR to get plaintext.",
            "Recovering one block needs up to 256*16 oracle queries. Understanding the byte-flipping math is the goal; the flag is AVST{padding_oracle_full_decrypt}.",
        ],
        "docker_lab": None,
    },
    # ---------------- Forensics ----------------
    {
        "title": "Hidden in Plain Sight",
        "category": "Forensics",
        "difficulty": "Easy",
        "description": (
            "Download evidence.png, recovered from a suspect's laptop. The image looks "
            "ordinary, but data is hidden in its metadata and appended after the end of "
            "the file. Find the flag."
        ),
        "points": 90,
        "flag": "AVST{steganography_basics}",
        "hints": [
            "Run  strings evidence.png  — hidden text often survives in PNG tEXt chunks and trailing data.",
            "PNG files end at the IEND chunk. Anything after it is 'extra' data worth inspecting.",
            "Both the 'Secret' tEXt chunk and the appended block at the end of the file contain the flag.",
        ],
        "docker_lab": None,
        "download_file": "evidence.png",
    },
    {
        "title": "Packet Secrets",
        "category": "Forensics",
        "difficulty": "Medium",
        "description": (
            "Download capture.pcap. It shows an employee logging into an internal FTP "
            "server over an unencrypted connection. FTP sends credentials in cleartext — "
            "find the password, which is the flag."
        ),
        "points": 160,
        "flag": "AVST{plaintext_ftp_credentials}",
        "hints": [
            "Open capture.pcap in Wireshark, or just run  strings capture.pcap  for a quick look.",
            "FTP authentication uses USER and PASS commands sent in plain text.",
            "Find the 'PASS ' line — the value after it is the flag.",
        ],
        "docker_lab": None,
        "download_file": "capture.pcap",
    },
    {
        "title": "Deleted But Not Gone",
        "category": "Forensics",
        "difficulty": "Hard",
        "description": (
            "Download disk.img, a raw disk image. A file was deleted right before the "
            "machine shut down, but deletion only removes the directory entry — the data "
            "blocks remain. Carve the deleted file out and recover its contents."
        ),
        "points": 240,
        "flag": "AVST{file_carving_recovery}",
        "hints": [
            "Deleting a file usually leaves its data intact until overwritten. Scan the raw image for file signatures (magic bytes).",
            "PNG files begin with the bytes 89 50 4E 47 ('\\x89PNG') and end at 'IEND'. Search the image for that header.",
            "Carve out the bytes from the PNG header to just after IEND (or run  foremost disk.img ), then run  strings  on the recovered image to read the flag.",
        ],
        "docker_lab": None,
        "download_file": "disk.img",
    },
    {
        "title": "Memory Lane",
        "category": "Forensics",
        "difficulty": "Insane",
        "description": (
            "Download memory.dmp, a RAM capture from a compromised server taken while "
            "malware was running. The malware kept its XOR key and an encrypted 'vault' in "
            "memory. Extract the 32-byte key and decrypt the vault to recover the flag."
        ),
        "points": 380,
        "flag": "AVST{memory_forensics_key_extraction}",
        "hints": [
            "Run  strings memory.dmp  and look for the suspicious process (svch0st.exe) and its config block.",
            "The 32 bytes right after 'KEYBLOB:' are the repeating XOR key. The hex string after 'VAULT_HEX:' is the encrypted flag.",
            "Decode VAULT_HEX from hex, then XOR each byte with key[i % 32] to recover the flag.",
        ],
        "docker_lab": None,
        "download_file": "memory.dmp",
    },
    # ---------------- Reverse Engineering ----------------
    {
        "title": "Crack the Binary",
        "category": "Reverse Engineering",
        "difficulty": "Easy",
        "description": (
            "Download the 'crackme' binary. It asks for a password before printing the "
            "flag. The password is stored in plain text inside the binary — find it, run "
            "the program with it, and read the flag.\n\n"
            "Run with:  chmod +x crackme && ./crackme"
        ),
        "points": 120,
        "flag": "AVST{reversing_is_fun}",
        "hints": [
            "Run  strings crackme  — the expected password is a hardcoded string in the binary.",
            "Look for something that reads like a password (sup3rs3cr3t_...).",
            "Run ./crackme and enter  sup3rs3cr3t_p4ssw0rd  to print the flag.",
        ],
        "docker_lab": None,
        "download_file": "crackme",
    },
    {
        "title": "XOR Armor",
        "category": "Reverse Engineering",
        "difficulty": "Medium",
        "description": (
            "Download 'xor_armor'. It doesn't store the flag as text — it XOR-decrypts a "
            "byte array at runtime with a single-byte key, then compares it to your input. "
            "Extract the encrypted bytes and key statically to recover the flag.\n\n"
            "Run with:  chmod +x xor_armor && ./xor_armor"
        ),
        "points": 170,
        "flag": "AVST{static_xor_deobfuscated}",
        "hints": [
            "Disassemble with  objdump -d xor_armor  (or use radare2/Ghidra) and find the encrypted byte array plus the XOR loop.",
            "The key is a single byte (0x5A) XORed against each element.",
            "XOR each stored byte with 0x5A in a short Python script to reveal the flag, then feed it back to the program to confirm.",
        ],
        "docker_lab": None,
        "download_file": "xor_armor",
    },
    {
        "title": "The Maze",
        "category": "Reverse Engineering",
        "difficulty": "Hard",
        "description": (
            "Download 'the_maze'. It validates your input through five chained checks, "
            "each testing a different transformation of a substring. Trace all five to "
            "reconstruct the flag.\n\n"
            "Run with:  chmod +x the_maze && ./the_maze"
        ),
        "points": 260,
        "flag": "AVST{multistage_validation_solved}",
        "hints": [
            "Map the five stage functions first (stage1..stage5). Each validates a specific slice of the input.",
            "Stage 3 compares a middle slice to a hardcoded string; stage 4 XORs another slice with 0x11 against a fixed array.",
            "Recover each slice independently and concatenate. Reversing all five gives the flag, which the program then accepts.",
        ],
        "docker_lab": None,
        "download_file": "the_maze",
    },
    {
        "title": "Anti-Debug Fortress",
        "category": "Reverse Engineering",
        "difficulty": "Insane",
        "description": (
            "Download 'fortress'. It resists debuggers (ptrace deny-attach), detects "
            "single-stepping by timing, and only reveals the flag after a correct "
            "passphrase — which is stored obfuscated. Recover the passphrase statically to "
            "unlock the encrypted flag.\n\n"
            "Run with:  chmod +x fortress && ./fortress"
        ),
        "points": 400,
        "flag": "AVST{anti_debug_bypassed}",
        "hints": [
            "The passphrase is stored as a byte array XORed with 0x6D — recover it statically instead of fighting the anti-debug checks at runtime.",
            "Find the 'pw' array in the binary, XOR each byte with 0x6D, and read the passphrase.",
            "Run ./fortress and enter  unl0ck_th3_f0rtr3ss  to decrypt and print the flag.",
        ],
        "docker_lab": None,
        "download_file": "fortress",
    },
]


def seed():
    Base.metadata.create_all(bind=engine)

    # Build every downloadable artifact from the flags above (idempotent).
    try:
        assets.generate_all(FILE_FLAGS, CRACKME_FLAGS)
    except Exception as exc:  # generation must never block API startup
        print(f"[seed] asset generation warning: {exc}")

    db = SessionLocal()
    try:
        if db.query(models.Challenge).count() > 0:
            print("Challenges already seeded, skipping.")
            return

        for c in CHALLENGES:
            challenge = models.Challenge(
                title=c["title"],
                category=c["category"],
                difficulty=c["difficulty"],
                description=c["description"],
                points=c["points"],
                flag_hash=flag_hash(c["flag"]),
                flag_format=FLAG_FORMAT,
                hints=json.dumps(c["hints"]),
                docker_lab=c["docker_lab"],
                download_file=c.get("download_file"),
            )
            db.add(challenge)
        db.commit()
        print(f"Seeded {len(CHALLENGES)} challenges.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
