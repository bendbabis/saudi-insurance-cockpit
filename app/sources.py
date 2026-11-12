"""Low-risk, allowlisted official source discovery; no automatic publication of numeric values."""
import hashlib
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("SIIC_DB_PATH", str(ROOT / "data" / "sources.sqlite3")))
SOURCES = {
    "ia_quarterly": ("Insurance Authority quarterly reports", "https://www.ia.gov.sa/en/information-center/reports/quarterly-publications"),
    "ia_annual": ("Insurance Authority annual reports", "https://www.ia.gov.sa/en/information-center/reports/annual-publications"),
    "sama_statistics": ("SAMA statistics", "https://www.sama.gov.sa/en-US/EconomicReports/Pages/default.aspx"),
}
ALLOWED_HOSTS = {"www.ia.gov.sa", "ia.gov.sa", "www.sama.gov.sa", "sama.gov.sa"}


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS source_events (
        id TEXT PRIMARY KEY, source_key TEXT NOT NULL, title TEXT NOT NULL,
        url TEXT NOT NULL, discovered_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'UNVERIFIED_DOCUMENT')""")
    db.execute("""CREATE TABLE IF NOT EXISTS source_checks (
        source_key TEXT PRIMARY KEY, last_checked TEXT, status TEXT, message TEXT,
        documents_seen INTEGER NOT NULL DEFAULT 0)""")
    db.commit()
    return db


def approved_url(url: str) -> bool:
    p = urlparse(url)
    return p.scheme == "https" and p.hostname in ALLOWED_HOSTS and not p.username and not p.password and p.port in (None, 443)


def discover_links(html: str, base_url: str):
    dom = BeautifulSoup(html, "html.parser")
    seen = set()
    for a in dom.select("a[href]"):
        href = urljoin(base_url, a.get("href", ""))
        href = href.split("#")[0]
        if not approved_url(href) or href in seen:
            continue
        title = " ".join(a.get_text(" ", strip=True).split())[:240]
        if len(title) < 3:
            continue
        if any(x in (title + " " + href).lower() for x in ("report", "insurance", "annual", "quarter", ".pdf", "statistics")):
            seen.add(href)
            yield {"title": title, "url": href}


def refresh_sources() -> dict:
    report = {}
    with connect() as db:
        for key, (name, url) in SOURCES.items():
            now = datetime.now(timezone.utc).isoformat()
            found = 0
            try:
                with httpx.Client(timeout=15, follow_redirects=False, headers={"User-Agent":"SIIC-SourceMonitor/0.1 (+https://github.com/bendbabis/saudi-insurance-cockpit)"}) as client:
                    response = client.get(url)
                response.raise_for_status()
                if response.is_redirect:
                    raise ValueError("Redirect not followed for security")
                if "text/html" not in response.headers.get("content-type", ""):
                    raise ValueError("Expected HTML index page")
                if len(response.content) > 4_000_000:
                    raise ValueError("Source page exceeds maximum size")
                for item in discover_links(response.text, url):
                    digest = hashlib.sha256(item["url"].encode()).hexdigest()[:32]
                    cur = db.execute("INSERT OR IGNORE INTO source_events(id,source_key,title,url,discovered_at) VALUES(?,?,?,?,?)",
                                     (digest,key,item["title"],item["url"],now))
                    found += max(0, cur.rowcount)
                status, message = "OK", f"{found} newly discovered links; content not validated"
            except (httpx.HTTPError, ValueError) as err:
                status, message = "ERROR", str(err)[:350]
            db.execute("""INSERT INTO source_checks(source_key,last_checked,status,message,documents_seen)
                          VALUES (?,?,?,?,?) ON CONFLICT(source_key) DO UPDATE SET
                          last_checked=excluded.last_checked,status=excluded.status,
                          message=excluded.message,documents_seen=source_checks.documents_seen+excluded.documents_seen""",
                       (key,now,status,message,found))
            report[key] = {"name":name,"url":url,"status":status,"new_links":found,"message":message}
        db.commit()
    return report


def catalog() -> dict:
    with connect() as db:
        checks = {r["source_key"]:dict(r) for r in db.execute("SELECT * FROM source_checks")}
        docs = [dict(r) for r in db.execute("SELECT * FROM source_events ORDER BY discovered_at DESC LIMIT 80")]
    return {"sources":[{"id":key,"name":name,"url":url,**checks.get(key,{"status":"NOT_CHECKED","last_checked":None,"message":"Not yet fetched","documents_seen":0})}
                       for key,(name,url) in SOURCES.items()],
            "discovered":docs,
            "methodology":"Discovery of URLs only. Documents and numbers have not been extracted or validated. No silent dashboard update."}
