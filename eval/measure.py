import json
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app import main
from app.observability import LOG_FILE

EVAL_SET = Path(__file__).resolve().parent / "eval_set.json"


def percentile(values, share):
    values = sorted(values)
    return values[int(share * (len(values) - 1))] if values else 0


def main_run():
    questions = [row["question"] for row in json.loads(EVAL_SET.read_text(encoding="utf-8"))]
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    main.ask_cache.items.clear()
    client = TestClient(main.app, raise_server_exceptions=False)

    for round_number in (1, 2):
        print(f"\nRound {round_number}")
        for number, question in enumerate(questions, start=1):
            response = client.post("/ask", json={"question": question})
            print(f"  Q{number}: HTTP {response.status_code}")
            time.sleep(2)

    rows = [json.loads(line) for line in LOG_FILE.read_text(encoding="utf-8").splitlines()]
    ok = [r for r in rows if not r["error"]]
    cached = [r for r in ok if r["cached"]]
    fresh = [r for r in ok if not r["cached"]]
    with_llm = [r for r in fresh if r["tokens"]]

    print("\n--- Numbers for the README ---")
    print("requests logged:", len(rows), "| errors:", len(rows) - len(ok))
    print("cache hit rate:", f"{100 * len(cached) / max(len(ok), 1):.0f}%")
    if fresh:
        latencies = [r["latency_ms"] for r in fresh]
        print("uncached latency: avg", round(sum(latencies) / len(latencies)),
              "ms | p95", percentile(latencies, 0.95), "ms")
    if cached:
        print("cached latency: avg", round(sum(r["latency_ms"] for r in cached) / len(cached)), "ms")
    if with_llm:
        tokens = [r["tokens"] for r in with_llm]
        print("tokens per LLM request: avg", round(sum(tokens) / len(tokens)),
              "| max", max(tokens), "| calls that used the LLM:", len(with_llm))
        print("total tokens for", len(with_llm), "LLM requests:", sum(tokens))


if __name__ == "__main__":
    main_run()