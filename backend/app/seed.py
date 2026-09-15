import hashlib
import json

from .database import Base, SessionLocal, engine
from . import models


def flag_hash(flag: str) -> str:
    return hashlib.sha256(flag.strip().encode()).hexdigest()


FLAG_FORMAT = "AVST{...}"

CHALLENGES = [
    # ---------------- Web Security ----------------
    {
        "title": "Login Bypass 101",
        "category": "Web Security",
        "difficulty": "Easy",
        "description": (
            "The staging login form at /lab/sqli-login trusts user input a little too "
            "much. Can you log in as admin without knowing the password?"
        ),
        "points": 100,
        "flag": "AVST{sql_injection_login_bypass}",
        "hints": [
            "Check what happens when you enter a single quote (') in the username field.",
            "Think about how the backend might build its SQL query using string concatenation.",
            "Try a payload like admin' -- to comment out the rest of the WHERE clause.",
        ],
        "docker_lab": "sqli-lab",
    },
    {
        "title": "Reflected Alert",
        "category": "Web Security",
        "difficulty": "Easy",
        "description": (
            "The search box on /lab/xss-search reflects your query straight into the page. "
            "Can you make the page execute your own JavaScript?"
        ),
        "points": 100,
        "flag": "AVST{reflected_xss_alert_1}",
        "hints": [
            "Try typing plain HTML tags into the search box and see if they render.",
            "The classic payload to test for XSS is <script>alert(1)</script>.",
            "If script tags are filtered, try an event handler like <img src=x onerror=alert(1)>.",
        ],
        "docker_lab": "xss-lab",
    },
    {
        "title": "Invoice Peeker",
        "category": "Web Security",
        "difficulty": "Medium",
        "description": (
            "The billing portal lets you view your own invoice at /invoices/{id}. "
            "The server never checks whether the invoice actually belongs to you. "
            "Can you read someone else's invoice?"
        ),
        "points": 150,
        "flag": "AVST{idor_invoice_leak}",
        "hints": [
            "This bug class is called Insecure Direct Object Reference (IDOR).",
            "Try changing the numeric id in the URL to a nearby value.",
            "The server trusts the id parameter completely — it never re-checks ownership against the logged-in session.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Forge the Token",
        "category": "Web Security",
        "difficulty": "Medium",
        "description": (
            "The API issues JWTs for session management. One of them was leaked in a "
            "public support ticket. The server accepts tokens signed with 'alg: none'. "
            "Can you forge an admin token?"
        ),
        "points": 175,
        "flag": "AVST{jwt_alg_none_forgery}",
        "hints": [
            "Decode the JWT header and payload — they're just base64, not encrypted.",
            "JWT supports an 'alg' field in the header that names the signing algorithm.",
            "Some misconfigured servers will accept a token whose header says \"alg\": \"none\" with an empty signature.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Internal Only",
        "category": "Web Security",
        "difficulty": "Hard",
        "description": (
            "A 'fetch preview' feature on the dashboard requests any URL you give it and "
            "shows the response. It's meant for public images, but the server never "
            "restricts which hosts it can reach. What can you see that you shouldn't?"
        ),
        "points": 225,
        "flag": "AVST{ssrf_metadata_leak}",
        "hints": [
            "This vulnerability class is Server-Side Request Forgery (SSRF).",
            "Cloud servers often expose an internal metadata endpoint at a well-known link-local IP address.",
            "Try pointing the fetch feature at http://169.254.169.254/ instead of a public URL.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Blind Faith",
        "category": "Web Security",
        "difficulty": "Insane",
        "description": (
            "The /lab/sqli-login form from 'Login Bypass 101' has been patched — errors are "
            "now hidden and responses look identical whether the query succeeds or fails. "
            "But timing never lies. Extract the admin password one character at a time."
        ),
        "points": 350,
        "flag": "AVST{blind_time_based_sqli}",
        "hints": [
            "Since there are no visible errors or content differences, you need a side channel — think about response time.",
            "SQLite/MySQL support conditional delay functions you can inject, e.g. based on SUBSTR(password,1,1)='a'.",
            "Automate a binary or brute-force search over each character position, using response delay as your oracle.",
        ],
        "docker_lab": None,
    },
    # ---------------- Cryptography ----------------
    {
        "title": "Caesar's Secret",
        "category": "Cryptography",
        "difficulty": "Easy",
        "description": (
            "We intercepted this message: 'DIVW{fdhvdu_flskhu_lv_hdvb}'. "
            "It looks like a classic substitution cipher."
        ),
        "points": 75,
        "flag": "AVST{caesar_cipher_is_easy}",
        "hints": [
            "This is a Caesar cipher — each letter is shifted by a fixed amount.",
            "Try shifting the letters back by 3 positions.",
            "D -> A, I -> F ... the shift is 3.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Single Byte Shield",
        "category": "Cryptography",
        "difficulty": "Medium",
        "description": (
            "This ciphertext was 'encrypted' by XOR-ing every byte of the flag with the "
            "same single-byte key: "
            "1a1a1a4c081a19095e191b1a5e4e0e1a1c1a094e131f19085e0e1a1c1a1a (hex). "
            "Recover the key and the flag."
        ),
        "points": 150,
        "flag": "AVST{single_byte_xor_recovered}",
        "hints": [
            "Single-byte XOR ciphers can be brute-forced — there are only 256 possible keys.",
            "You know the plaintext starts with 'AVST{' — XOR the first ciphertext byte with 'A' to guess the key.",
            "Once you find a key that produces readable ASCII for the whole message, that's it.",
        ],
        "docker_lab": None,
    },
    {
        "title": "RSA Whisper",
        "category": "Cryptography",
        "difficulty": "Hard",
        "description": (
            "An RSA-encrypted flag was intercepted along with the public key: "
            "n = 3233, e = 17. The modulus looks suspiciously small for real RSA... "
            "ciphertext c = 2790. Recover the flag."
        ),
        "points": 250,
        "flag": "AVST{rsa_small_primes_factored}",
        "hints": [
            "Real RSA uses moduli thousands of bits long — n=3233 is tiny and can be factored by hand or script.",
            "Factor n into its two primes p and q (hint: n = 61 x 53), then compute phi(n) = (p-1)(q-1).",
            "Find d = e^-1 mod phi(n), then decrypt with m = c^d mod n and convert the number back to text.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Padding Oracle Whispers",
        "category": "Cryptography",
        "difficulty": "Insane",
        "description": (
            "A legacy service encrypts cookies with AES-CBC and helpfully returns a distinct "
            "'bad padding' error whenever decryption fails padding validation — but a generic "
            "error otherwise. Given access to this oracle and an intercepted ciphertext, "
            "recover the plaintext flag without ever knowing the key."
        ),
        "points": 400,
        "flag": "AVST{padding_oracle_full_decrypt}",
        "hints": [
            "This is the classic CBC Padding Oracle attack — the server leaks one bit of information per request (valid padding or not).",
            "By manipulating the previous ciphertext block byte-by-byte, you can force each byte of the intermediate state to reveal itself through valid-padding responses.",
            "Recovering one full block requires up to 256 x 16 oracle queries; tools like PadBuster automate this, but understanding the byte-flipping math is the real goal.",
        ],
        "docker_lab": None,
    },
    # ---------------- Forensics ----------------
    {
        "title": "Hidden in Plain Sight",
        "category": "Forensics",
        "difficulty": "Easy",
        "description": (
            "We recovered an image from a suspect's laptop. There might be more to it "
            "than meets the eye. (Hint: check the file's metadata and hidden streams.)"
        ),
        "points": 90,
        "flag": "AVST{steganography_basics}",
        "hints": [
            "Run 'file' and 'strings' on the image to check for hidden text.",
            "Tools like steghide or exiftool can reveal embedded data.",
            "Look for an unusual comment field or appended data after the image's EOF marker.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Packet Secrets",
        "category": "Forensics",
        "difficulty": "Medium",
        "description": (
            "A captured .pcap file shows an employee logging into an internal FTP server "
            "over plain, unencrypted traffic. Somewhere in that traffic is a password "
            "that unlocks the flag."
        ),
        "points": 160,
        "flag": "AVST{plaintext_ftp_credentials}",
        "hints": [
            "Open the capture in Wireshark and filter for the ftp protocol.",
            "FTP sends USER and PASS commands in cleartext — follow the TCP stream.",
            "Use Wireshark's 'Follow > TCP Stream' on the control connection to read the full login exchange.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Deleted But Not Gone",
        "category": "Forensics",
        "difficulty": "Hard",
        "description": (
            "A suspect deleted a file right before shutting down their machine, but "
            "deletion doesn't mean destruction. Analyze the provided disk image and "
            "recover the file's contents."
        ),
        "points": 240,
        "flag": "AVST{file_carving_recovery}",
        "hints": [
            "Deleting a file usually just removes its directory entry — the data blocks often remain until overwritten.",
            "File carving tools like 'foremost' or 'photorec' scan raw disk images for known file signatures (magic bytes).",
            "Look for the file's header/footer magic bytes directly in the raw image with a hex editor if carving tools miss it.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Memory Lane",
        "category": "Forensics",
        "difficulty": "Insane",
        "description": (
            "You've been handed a full RAM dump from a compromised server, taken while "
            "a malicious process was still running. Somewhere in volatile memory is the "
            "decryption key the malware used. Find it and recover the flag."
        ),
        "points": 380,
        "flag": "AVST{memory_forensics_key_extraction}",
        "hints": [
            "Memory forensics frameworks like Volatility can list running processes, network connections, and loaded modules from a raw dump.",
            "Look for suspicious process names, then dump that process's memory region for further string/entropy analysis.",
            "High-entropy byte sequences near suspicious strings are often encryption keys — extract and try them against the accompanying encrypted flag file.",
        ],
        "docker_lab": None,
    },
    # ---------------- Reverse Engineering ----------------
    {
        "title": "Crack the Binary",
        "category": "Reverse Engineering",
        "difficulty": "Easy",
        "description": (
            "A simple compiled program asks for a password before printing the flag. "
            "Disassemble it to find the expected input."
        ),
        "points": 120,
        "flag": "AVST{reversing_is_fun}",
        "hints": [
            "Open the binary in a disassembler like Ghidra or objdump -d.",
            "Search for the comparison instruction (cmp) right after the input is read.",
            "The password is compared against a hardcoded string in the .rodata section.",
        ],
        "docker_lab": None,
    },
    {
        "title": "XOR Armor",
        "category": "Reverse Engineering",
        "difficulty": "Medium",
        "description": (
            "This binary doesn't store the flag as plain text — it decrypts a byte array "
            "with a single-byte XOR key at runtime before comparing it to your input. "
            "Find the key and the flag without running the decryption loop yourself by hand."
        ),
        "points": 170,
        "flag": "AVST{static_xor_deobfuscated}",
        "hints": [
            "Find the encrypted byte array in the binary's data section and the small loop that XORs each byte.",
            "The XOR key is usually a single hardcoded immediate value loaded right before the loop.",
            "Script the same XOR operation in Python against the extracted bytes once you have the key.",
        ],
        "docker_lab": None,
    },
    {
        "title": "The Maze",
        "category": "Reverse Engineering",
        "difficulty": "Hard",
        "description": (
            "This crackme validates your input through five chained functions, each "
            "checking a different transformation of a substring. Trace the control flow "
            "carefully — get any single check wrong and it fails silently."
        ),
        "points": 260,
        "flag": "AVST{multistage_validation_solved}",
        "hints": [
            "Map out the call graph first — identify all five validation functions before diving into any one of them.",
            "Each function likely checks a fixed-length slice of your input; work out the required value for each slice independently.",
            "Consider patching or scripting a debugger (gdb/x64dbg) to print intermediate register values rather than tracing everything by hand.",
        ],
        "docker_lab": None,
    },
    {
        "title": "Anti-Debug Fortress",
        "category": "Reverse Engineering",
        "difficulty": "Insane",
        "description": (
            "This binary actively fights back: it checks for attached debuggers, "
            "measures execution timing to detect single-stepping, and self-modifies "
            "part of its own code at runtime. Defeat its defenses to reach the real "
            "flag-checking routine."
        ),
        "points": 400,
        "flag": "AVST{anti_debug_bypassed}",
        "hints": [
            "Identify the anti-debug checks first (e.g. IsDebuggerPresent, ptrace self-attach, rdtsc timing) — they usually run early and branch on failure.",
            "Patch out or NOP the checks in a copy of the binary, or hook the relevant APIs, rather than fighting them live.",
            "Watch for self-modifying code: the real comparison logic may only exist in memory after an earlier stage decrypts it — dump memory at the right moment.",
        ],
        "docker_lab": None,
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
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
            )
            db.add(challenge)
        db.commit()
        print(f"Seeded {len(CHALLENGES)} challenges.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
