from fastapi import APIRouter, Depends

from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/api/cve", tags=["cve"])

CVE_LIST = [
    schemas.CVEOut(
        cve_id="CVE-2021-44228",
        name="Log4Shell",
        description=(
            "A critical remote code execution vulnerability in the Apache Log4j "
            "logging library, triggered via crafted JNDI lookup strings in log input."
        ),
        year=2021,
        related_category="Web Security",
    ),
    schemas.CVEOut(
        cve_id="CVE-2017-0144",
        name="EternalBlue",
        description=(
            "An SMBv1 protocol exploit developed by the NSA and leaked publicly, "
            "later used to spread the WannaCry ransomware worm."
        ),
        year=2017,
        related_category="Network / Reverse Engineering",
    ),
    schemas.CVEOut(
        cve_id="CVE-2014-0160",
        name="Heartbleed",
        description=(
            "A buffer over-read bug in the OpenSSL heartbeat extension that allowed "
            "attackers to read sensitive memory, including private keys."
        ),
        year=2014,
        related_category="Cryptography",
    ),
    schemas.CVEOut(
        cve_id="CVE-2019-0708",
        name="BlueKeep",
        description=(
            "A wormable vulnerability in Remote Desktop Services allowing "
            "unauthenticated remote code execution."
        ),
        year=2019,
        related_category="Network",
    ),
    schemas.CVEOut(
        cve_id="CVE-2020-1472",
        name="Zerologon",
        description=(
            "A privilege escalation vulnerability in the Netlogon protocol that lets "
            "an attacker impersonate a domain controller."
        ),
        year=2020,
        related_category="Forensics",
    ),
]


@router.get("", response_model=list[schemas.CVEOut])
def list_cves(current_user: models.User = Depends(get_current_user)):
    return CVE_LIST
