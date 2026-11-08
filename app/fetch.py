import re
import time
from pathlib import Path

import requests

HEADERS = {"User-Agent": "TaxSaathi-student-project"}
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

BASE = "https://www.incometax.gov.in/iec/foportal/help"
PAGES = {
    "itr1": f"{BASE}/all-topics/e-filing-services/itr-1",
    "itr1_faq": f"{BASE}/all-topics/e-filing-services/ITR1-FAQ",
    "file_itr1_sahaj": f"{BASE}/all-topics/e-filing-services/file-itr-1-sahaj-online",
    "which_itr": f"{BASE}/identification-and-generation-of-applicable-itr-individual",
}


def fetch_page(url, timeout=30):
    """Download a public web page. Return the HTML text, or None if it fails."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        print("Fetch failed:", error)
        return None


def get_title(html):
    """Return the <title> of an HTML page, or None."""
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def download_all():
    """Save every page in PAGES to data/raw/<name>.html."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in PAGES.items():
        html = fetch_page(url)
        if html is None:
            print(f"SKIPPED {name}")
            continue
        (RAW_DIR / f"{name}.html").write_text(html, encoding="utf-8")
        print(f"Saved {name}.html ({len(html)} characters)")
        time.sleep(1)


if __name__ == "__main__":
    download_all()