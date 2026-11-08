import json
from pathlib import Path

from app.extract import load_pages
from app.fetch import PAGES

OUTPUT = Path(__file__).resolve().parent.parent / "data" / "records.json"
CHUNK_SIZE = 350  # start a new record after about this many characters


def guess_regime(text):
    """Tag a record as old / new / both from the words it contains."""
    lower = text.lower()
    has_old = "old tax regime" in lower or "old regime" in lower
    has_new = "new tax regime" in lower or "new regime" in lower
    if has_old and not has_new:
        return "old"
    if has_new and not has_old:
        return "new"
    return "both"


def build_records():
    records = []
    seen = set()
    for page_name, lines in load_pages().items():
        chunk = []
        for line in lines + [None]:
            if line is not None:
                chunk.append(line)
            if chunk and (line is None or sum(len(x) for x in chunk) >= CHUNK_SIZE):
                summary = " ".join(chunk)[:700]
                if summary not in seen:
                    seen.add(summary)
                    records.append({
                        "id": f"IT{len(records) + 1:03d}",
                        "topic": chunk[0][:90],
                        "regime": guess_regime(summary),
                        "summary": summary,
                        "source_url": PAGES[page_name],
                    })
                chunk = []
    return records


if __name__ == "__main__":
    records = build_records()
    OUTPUT.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(records)} records to {OUTPUT.name}")
    for record in records[:3]:
        print(record["id"], "|", record["topic"])