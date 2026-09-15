import hashlib
import json

from .database import Base, SessionLocal, engine
from . import models


def flag_hash(flag: str) -> str:
    return hashlib.sha256(flag.strip().encode()).hexdigest()


CHALLENGES = [
    {
        "title": "Login Bypass 101",
        "category": "Web Security",
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
        "title": "Caesar's Secret",
        "category": "Cryptography",
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
        "title": "Hidden in Plain Sight",
        "category": "Forensics",
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
        "title": "Crack the Binary",
        "category": "Reverse Engineering",
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
                description=c["description"],
                points=c["points"],
                flag_hash=flag_hash(c["flag"]),
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
