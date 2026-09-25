import asyncio
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import re
import time
from typing import Optional

from fastapi import APIRouter, Depends, Query
import httpx

from .. import models, schemas
from ..auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cve", tags=["cve"])

CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "cve_cache.json"
CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
CACHE_TTL_SECONDS = 1800  # 30 minutes

# In-memory cache structures
_memory_cache: list[schemas.CVEOut] = []
_last_fetch_time: Optional[float] = None
_cache_lock = asyncio.Lock()
_raw_vuln_count: int = 0
_last_synced_str: str = ""

LANDMARK_CVES: list[schemas.CVEOut] = [
    schemas.CVEOut(
        cve_id="CVE-2021-44228",
        name="Log4Shell",
        vendor="Apache",
        product="Log4j",
        description=(
            "A critical remote code execution vulnerability in the Apache Log4j "
            "logging library, triggered via crafted JNDI lookup strings in log input."
        ),
        year=2021,
        related_category="Web Security",
        severity="Critical",
        ransomware_use="Known",
        cwes=["CWE-502", "CWE-917"],
        required_action="Upgrade log4j to 2.17.1 or higher, remove JndiLookup class.",
        vendor_advisory_url="https://logging.apache.org/log4j/2.x/security.html",
        nvd_url="https://nvd.nist.gov/vuln/detail/CVE-2021-44228",
        is_realtime=False,
    ),
    schemas.CVEOut(
        cve_id="CVE-2017-0144",
        name="EternalBlue",
        vendor="Microsoft",
        product="Windows SMBv1",
        description=(
            "An SMBv1 protocol remote code execution exploit developed by the NSA and leaked publicly, "
            "later weaponized worldwide to spread the WannaCry ransomware worm."
        ),
        year=2017,
        related_category="Network",
        severity="Critical",
        ransomware_use="Known",
        cwes=["CWE-119"],
        required_action="Disable SMBv1 and apply Microsoft Security Bulletin MS17-010.",
        vendor_advisory_url="https://docs.microsoft.com/en-us/security-updates/securitybulletins/2017/ms17-010",
        nvd_url="https://nvd.nist.gov/vuln/detail/CVE-2017-0144",
        is_realtime=False,
    ),
    schemas.CVEOut(
        cve_id="CVE-2014-0160",
        name="Heartbleed",
        vendor="OpenSSL",
        product="OpenSSL",
        description=(
            "A catastrophic buffer over-read bug in the OpenSSL TLS heartbeat extension allowing "
            "unauthenticated remote attackers to dump process memory containing server private keys."
        ),
        year=2014,
        related_category="Cryptography",
        severity="Critical",
        ransomware_use="Unknown",
        cwes=["CWE-125", "CWE-119"],
        required_action="Upgrade OpenSSL to 1.0.1g or rebuild with -DOPENSSL_NO_HEARTBEATS.",
        vendor_advisory_url="https://heartbleed.com/",
        nvd_url="https://nvd.nist.gov/vuln/detail/CVE-2014-0160",
        is_realtime=False,
    ),
    schemas.CVEOut(
        cve_id="CVE-2019-0708",
        name="BlueKeep",
        vendor="Microsoft",
        product="Remote Desktop Services",
        description=(
            "A pre-authentication wormable remote code execution vulnerability in Microsoft Remote "
            "Desktop Protocol (RDP) allowing network-level code execution without credentials."
        ),
        year=2019,
        related_category="Network",
        severity="Critical",
        ransomware_use="Known",
        cwes=["CWE-416"],
        required_action="Apply security update KB4499175 or disable Remote Desktop Services.",
        vendor_advisory_url="https://msrc.microsoft.com/update-guide/vulnerability/CVE-2019-0708",
        nvd_url="https://nvd.nist.gov/vuln/detail/CVE-2019-0708",
        is_realtime=False,
    ),
    schemas.CVEOut(
        cve_id="CVE-2020-1472",
        name="Zerologon",
        vendor="Microsoft",
        product="Netlogon Remote Protocol",
        description=(
            "An elevation of privilege flaw in the AES-CFB8 implementation of Netlogon that lets "
            "an unauthenticated attacker establish a vulnerable secure channel and take over domain controllers."
        ),
        year=2020,
        related_category="Cryptography",
        severity="Critical",
        ransomware_use="Known",
        cwes=["CWE-330", "CWE-326"],
        required_action="Enforce Netlogon secure channel connections across all Windows Domain Controllers.",
        vendor_advisory_url="https://msrc.microsoft.com/update-guide/vulnerability/CVE-2020-1472",
        nvd_url="https://nvd.nist.gov/vuln/detail/CVE-2020-1472",
        is_realtime=False,
    ),
]


def classify_cve(name: str, desc: str, cwes: list[str]) -> str:
    text = f"{name} {desc}".lower()
    cwe_set = {c.strip().upper() for c in cwes if c}

    web_cwes = {
        "CWE-22", "CWE-23", "CWE-35", "CWE-36",
        "CWE-79", "CWE-80", "CWE-89", "CWE-94",
        "CWE-352", "CWE-434", "CWE-918", "CWE-287",
        "CWE-306", "CWE-862", "CWE-863", "CWE-502",
        "CWE-77", "CWE-78", "CWE-284"
    }

    if any(k in text for k in [
        "path traversal", "directory traversal", "sql injection", "cross-site",
        "xss", "file upload", "ssrf", "csrf", "deserialization", "template injection",
        "command injection", "remote code execution", "rce", "bypass", "broken access"
    ]):
        return "Web Security"
    if any(c in web_cwes for c in cwe_set):
        return "Web Security"

    if any(k in text for k in [
        "buffer overflow", "heap-based", "stack-based", "use-after-free", "out-of-bounds",
        "memory corruption", "integer overflow", "null pointer", "double free", "type confusion"
    ]):
        return "Reverse Engineering"
    if any(c in {
        "CWE-119", "CWE-120", "CWE-121", "CWE-122", "CWE-125",
        "CWE-787", "CWE-416", "CWE-190", "CWE-476", "CWE-415"
    } for c in cwe_set):
        return "Reverse Engineering"

    if any(k in text for k in [
        "cryptograph", "certificate validation", "weak key", "improper certificate",
        "signature verification", "cipher", "encryption", "decryption"
    ]):
        return "Cryptography"
    if any(c in {"CWE-310", "CWE-326", "CWE-327", "CWE-330", "CWE-347", "CWE-295"} for c in cwe_set):
        return "Cryptography"

    if any(k in text for k in [
        "denial of service", "packet", "smb", "dns", "bgp", "sniff",
        "network", "man-in-the-middle", "router", "firewall", "switch", "vpn"
    ]):
        return "Network"

    return "General Security"


def parse_kev_item(item: dict) -> schemas.CVEOut:
    cve_id = item.get("cveID", "").strip()
    name = item.get("vulnerabilityName", "").strip() or cve_id
    desc = item.get("shortDescription", "").strip()
    date_added = item.get("dateAdded", "").strip()
    cwes = item.get("cwes", [])
    if isinstance(cwes, str):
        cwes = [cwes]

    year = 2026
    match = re.search(r"CVE-(\d{4})-", cve_id)
    if match:
        try:
            year = int(match.group(1))
        except ValueError:
            pass
    elif date_added:
        try:
            year = int(date_added.split("-")[0])
        except (ValueError, IndexError):
            pass

    notes = item.get("notes", "")
    urls = re.findall(r"https?://[^\s;]+", notes)
    vendor_advisory_url = urls[0] if urls else None

    is_ransomware = item.get("knownRansomwareCampaignUse", "").lower() == "known"
    is_rce = "remote code execution" in desc.lower() or "rce" in desc.lower()
    severity = "Critical" if (is_ransomware or is_rce) else "High"

    category = classify_cve(name, desc, cwes)

    return schemas.CVEOut(
        cve_id=cve_id,
        name=name,
        vendor=item.get("vendorProject", "").strip() or None,
        product=item.get("product", "").strip() or None,
        description=desc,
        year=year,
        date_added=date_added or None,
        related_category=category,
        severity=severity,
        ransomware_use=item.get("knownRansomwareCampaignUse", "Unknown"),
        cwes=cwes,
        required_action=item.get("requiredAction", "").strip() or None,
        vendor_advisory_url=vendor_advisory_url,
        nvd_url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
        is_realtime=True,
    )


async def load_cve_catalog(force_refresh: bool = False) -> list[schemas.CVEOut]:
    global _memory_cache, _last_fetch_time, _raw_vuln_count, _last_synced_str

    now = time.time()
    if (
        not force_refresh
        and _memory_cache
        and _last_fetch_time
        and (now - _last_fetch_time < CACHE_TTL_SECONDS)
    ):
        return _memory_cache

    async with _cache_lock:
        # Double check after acquiring lock
        if (
            not force_refresh
            and _memory_cache
            and _last_fetch_time
            and (now - _last_fetch_time < CACHE_TTL_SECONDS)
        ):
            return _memory_cache

        data: Optional[dict] = None

        # 1. Attempt live fetch from CISA KEV
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(CISA_KEV_URL)
                if res.status_code == 200:
                    data = res.json()
                    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f)
                    _last_synced_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                    logger.info("Successfully fetched live CVEs from CISA KEV.")
        except Exception as e:
            logger.warning(f"Failed to fetch live CVEs from CISA KEV: {e}. Falling back to disk cache.")

        # 2. Fall back to local disk cache if live fetch failed
        if not data and CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not _last_synced_str:
                    mtime = CACHE_FILE.stat().st_mtime
                    _last_synced_str = datetime.fromtimestamp(mtime, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                logger.info("Loaded CVEs from local disk cache.")
            except Exception as e:
                logger.error(f"Failed to read local CVE cache file: {e}")

        # 3. Parse items
        live_list: list[schemas.CVEOut] = []
        if data and "vulnerabilities" in data:
            vulns = data["vulnerabilities"]
            _raw_vuln_count = len(vulns)
            # Sort with newest dateAdded first
            sorted_vulns = sorted(vulns, key=lambda x: x.get("dateAdded", ""), reverse=True)
            for item in sorted_vulns:
                try:
                    live_list.append(parse_kev_item(item))
                except Exception:
                    continue

        # If live_list is empty, use landmarks
        if not live_list:
            _memory_cache = list(LANDMARK_CVES)
            _raw_vuln_count = len(LANDMARK_CVES)
            _last_synced_str = "Offline Mode"
        else:
            # Combine: live CVEs first, followed by historical landmarks
            _memory_cache = live_list + LANDMARK_CVES

        _last_fetch_time = time.time()
        return _memory_cache


@router.get("", response_model=list[schemas.CVEOut])
async def list_cves(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search CVE ID, vendor, or keywords"),
    tab: Optional[str] = Query("all", description="all, realtime, ransomware, or landmarks"),
    limit: int = Query(80, ge=1, le=500),
    refresh: bool = Query(False, description="Force refresh from live feed"),
    current_user: models.User = Depends(get_current_user),
):
    all_cves = await load_cve_catalog(force_refresh=refresh)
    results = all_cves

    # Tab filters
    if tab == "realtime":
        results = [c for c in results if c.is_realtime]
    elif tab == "ransomware":
        results = [c for c in results if c.ransomware_use == "Known"]
    elif tab == "landmarks":
        results = [c for c in results if not c.is_realtime]

    # Category filter
    if category and category != "All":
        results = [c for c in results if c.related_category.lower() == category.lower()]

    # Search filter
    if search:
        s = search.strip().lower()
        results = [
            c for c in results
            if s in c.cve_id.lower()
            or s in c.name.lower()
            or (c.vendor and s in c.vendor.lower())
            or (c.product and s in c.product.lower())
            or s in c.description.lower()
        ]

    return results[:limit]


@router.get("/stats", response_model=schemas.CVEStats)
async def get_cve_stats(
    current_user: models.User = Depends(get_current_user),
):
    cves = await load_cve_catalog(force_refresh=False)
    count_2026 = sum(1 for c in cves if c.year == 2026 and c.is_realtime)
    count_2025 = sum(1 for c in cves if c.year == 2025 and c.is_realtime)
    ransomware_count = sum(1 for c in cves if c.ransomware_use == "Known")

    return schemas.CVEStats(
        total_tracked=_raw_vuln_count or len(cves),
        count_2026=count_2026,
        count_2025=count_2025,
        ransomware_count=ransomware_count,
        last_synced=_last_synced_str or "Just now",
        source="CISA Known Exploited Vulnerabilities (KEV) Live Feed",
    )
