from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


class TextExtractor(HTMLParser):
    """Collect the visible text of an HTML page, skipping scripts and menus."""

    SKIP = {"script", "style", "nav", "header", "footer", "noscript", "svg"}
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "div", "br", "tr"}

    def __init__(self):
        super().__init__()
        self.skip_depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth > 0:
            self.skip_depth -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.parts.append(data)


def extract_lines(html, min_length=40):
    """Return the readable lines of a page, each line only once."""
    parser = TextExtractor()
    parser.feed(html)
    text = "".join(parser.parts)
    lines = [" ".join(line.split()) for line in text.split("\n")]
    seen = set()
    result = []
    for line in lines:
        if len(line) >= min_length and line not in seen:
            seen.add(line)
            result.append(line)
    return result


def load_pages():
    """Return {page name: lines} for every saved page, without the shared menu text."""
    pages = {}
    for path in sorted(RAW_DIR.glob("*.html")):
        pages[path.stem] = extract_lines(path.read_text(encoding="utf-8"))

    # A line that appears on every page is menu/footer text, not help content.
    counts = Counter(line for lines in pages.values() for line in set(lines))
    shared = {line for line, count in counts.items() if count == len(pages)}
    return {name: [l for l in lines if l not in shared] for name, lines in pages.items()}


if __name__ == "__main__":
    for name, lines in load_pages().items():
        print(f"\n=== {name}: {len(lines)} lines ===")
        for line in lines[:12]:
            print("-", line[:160])