import json
import time
from collections import OrderedDict
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "requests.jsonl"
MAX_QUESTION_CHARS = 500
CACHE_SIZE = 100
CACHE_TTL_SECONDS = 3600


class InputRejected(ValueError):
    """Raised when a question is empty or too long."""


def check_input(question):
    """Return the cleaned question, or raise InputRejected."""
    text = (question or "").strip()
    if not text:
        raise InputRejected("Question is empty.")
    if len(text) > MAX_QUESTION_CHARS:
        raise InputRejected(f"Question is too long (max {MAX_QUESTION_CHARS} characters).")
    return text


class AnswerCache:
    """Remember recent answers, so the same question does not call the LLM again."""

    def __init__(self, size=CACHE_SIZE, ttl=CACHE_TTL_SECONDS):
        self.size = size
        self.ttl = ttl
        self.items = OrderedDict()

    @staticmethod
    def _key(question):
        return " ".join(question.lower().split())

    def get(self, question):
        key = self._key(question)
        entry = self.items.get(key)
        if entry is None:
            return None
        saved_at, value = entry
        if time.time() - saved_at > self.ttl:
            del self.items[key]
            return None
        self.items.move_to_end(key)
        return value

    def set(self, question, value):
        key = self._key(question)
        self.items[key] = (time.time(), value)
        self.items.move_to_end(key)
        while len(self.items) > self.size:
            self.items.popitem(last=False)


def log_request(endpoint, question, latency_ms, cached=False, tokens=None, error=None):
    """Append one JSON line per request. Only the first 80 characters of the question are saved."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "endpoint": endpoint,
        "question": question[:80],
        "latency_ms": round(latency_ms),
        "cached": cached,
        "tokens": tokens,
        "error": error,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")