import json

from app.models import TaxRecord

REQUIRED_FIELDS = ["id", "topic", "regime", "summary", "source_url"]


def ingest(path="data/records.json"):
    """Load records from JSON, check every field, return a list of TaxRecord."""
    with open(path, encoding="utf-8") as f:
        raw_records = json.load(f)

    records = []
    for item in raw_records:
        missing = [field for field in REQUIRED_FIELDS if field not in item]
        if missing:
            raise ValueError(f"Record {item.get('id', '?')} is missing fields: {missing}")
        records.append(TaxRecord(**{field: item[field] for field in REQUIRED_FIELDS}))
    return records


if __name__ == "__main__":
    records = ingest()
    print(f"Loaded {len(records)} records.")
    for record in records[:3]:
        print(record.short())