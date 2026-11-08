from dataclasses import dataclass


@dataclass
class TaxRecord:
    """One tax record, with the same fields as sample_records.json."""
    id: str
    topic: str
    regime: str
    summary: str
    source_url: str

    def short(self):
        return f"[{self.id}] {self.topic}"