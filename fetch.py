import re

import requests

HEADERS = {"User-Agent": "TaxSaathi-student-project"}


def fetch_page(url, timeout=15):
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


if __name__ == "__main__":
    url = "https://www.incometax.gov.in"
    html = fetch_page(url)
    if html:
        print("Fetched:", url)
        print("Page length:", len(html))
        print("Title:", get_title(html))
    else:
        print("Could not fetch the page. Check your internet and try again.")