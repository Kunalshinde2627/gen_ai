import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_records.json"


def load_records():
    """Read all records from the JSON file."""
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_record(record_id):
    """Return one record by its id, or None if not found."""
    for record in load_records():
        if record["id"].lower() == record_id.lower():
            return record
    return None


def search_records(keyword):
    """Return records whose topic or summary contains the keyword."""
    kw = keyword.lower()
    return [
        r for r in load_records()
        if kw in r["topic"].lower() or kw in r["summary"].lower()
    ]


def format_record(record):
    """Return a record as printable text."""
    return (
        f"[{record['id']}] {record['topic']}\n"
        f"  {record['summary']}\n"
        f"  Source: {record['source_url']}"
    )