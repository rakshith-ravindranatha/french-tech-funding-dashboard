#!/usr/bin/env python3
"""
scrape_eldorado.py
Fetches the latest monthly fundraising data from Eldorado.co
and appends new companies to data/companies.json.

Usage:
    python scripts/scrape_eldorado.py

Requirements:
    pip install requests beautifulsoup4
"""

import json, re, sys
from pathlib import Path
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Install dependencies: pip install requests beautifulsoup4")
    sys.exit(1)

ELDORADO_INDEX = "https://eldorado.co/blog/analyses-des-lev%C3%A9es-de-fonds"
DATA_FILE = Path(__file__).parent.parent / "data" / "companies.json"

MONTH_MAP = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12
}
MONTH_NAMES = {v: k.capitalize() for k, v in MONTH_MAP.items()}


def fetch_article_links():
    """Return list of (url, month, year) for 2026 monthly reports."""
    r = requests.get(ELDORADO_INDEX, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = re.search(r"/(\d{4})/(\d{2})/\d{2}/(\w+)-2026", href)
        if m and m.group(1) == "2026":
            month_word = m.group(3).lower()
            if month_word in MONTH_MAP:
                links.append({
                    "url": "https://eldorado.co" + href if href.startswith("/") else href,
                    "month": MONTH_MAP[month_word],
                    "year": 2026
                })
    return links


def parse_article(url, month):
    """Extract top companies mentioned in a monthly report."""
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    companies = []
    # Look for levée patterns: "CompanyName – XXM€ – Série X"
    text = soup.get_text(" ", strip=True)
    pattern = re.compile(
        r'([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-Za-zÀ-ÿ\s\.\-]+?)\s*[–—-]\s*(\d+(?:[,.]\d+)?)\s*M€\s*[–—-]\s*([\w\s]+)',
        re.UNICODE
    )
    seen = set()
    for m in pattern.finditer(text):
        name = m.group(1).strip()
        amount = float(m.group(2).replace(",", "."))
        stage = m.group(3).strip()
        if name not in seen and amount > 0:
            seen.add(name)
            companies.append({
                "name": name,
                "amount": amount,
                "stage": stage,
                "month": month,
                "monthName": MONTH_NAMES.get(month, str(month)),
                "source": url
            })
    return companies[:10]  # top 10 per article


def main():
    existing = json.loads(DATA_FILE.read_text(encoding="utf-8")) if DATA_FILE.exists() else []
    existing_names = {c["name"].lower() for c in existing}
    max_id = max((c.get("id", 0) for c in existing), default=0)

    links = fetch_article_links()
    print(f"Found {len(links)} 2026 monthly articles")

    new_entries = []
    for link in links:
        print(f"  Parsing {link['url']} …")
        companies = parse_article(link["url"], link["month"])
        for c in companies:
            if c["name"].lower() not in existing_names:
                max_id += 1
                new_entries.append({
                    "id": max_id,
                    "month": c["month"],
                    "monthName": c["monthName"],
                    "name": c["name"],
                    "amount": c["amount"],
                    "stage": c.get("stage", ""),
                    "sector": "",          # fill manually or enhance parser
                    "region": "",
                    "model": "BtoB",
                    "femaleFounded": False,
                    "investors": [],
                    "description": "",
                    "wttj": c["name"].lower().replace(" ", "-"),
                    "linkedin": c["name"].lower().replace(" ", "-"),
                    "_source": c["source"],
                    "_scraped": datetime.today().isoformat()
                })
                existing_names.add(c["name"].lower())

    if new_entries:
        all_data = existing + new_entries
        all_data.sort(key=lambda x: (x["month"], -x["amount"]))
        DATA_FILE.write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✅ Added {len(new_entries)} new companies → data/companies.json")
        print("   Review & enrich: sector, region, description, investors")
    else:
        print("\n✅ No new companies found — data is up to date")


if __name__ == "__main__":
    main()
