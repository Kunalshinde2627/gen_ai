import json
import re
import time
from pathlib import Path

import requests

from app.rag import answer_question

EVAL_DIR = Path(__file__).resolve().parent
EVAL_SET = EVAL_DIR / "eval_set.json"
RESULTS_JSON = EVAL_DIR / "eval_results.json"
RESULTS_MD = EVAL_DIR / "eval_results.md"

CONFIGS = [
    {"name": "A", "top_k": 3},
    {"name": "B", "top_k": 5},
]
CITATION = re.compile(r"\[\d+\]")


def normalise(text):
    """Make spaces and hyphens plain, and treat 'old tax regime' as 'old regime'."""
    for old, new in [("\u202f", " "), ("\u00a0", " "), ("\u2011", "-"), ("\u2010", "-"), ("\u2013", "-")]:
        text = text.replace(old, new)
    return text.lower().replace("tax regime", "regime")


def is_refusal(answer):
    text = normalise(answer).strip().replace("\u2019", "'")
    return text.startswith("i don't know")


def ask_with_retry(question, top_k, attempts=3):
    """Call the RAG pipeline. If the network or the API fails, wait and try again."""
    for attempt in range(1, attempts + 1):
        try:
            return answer_question(question, top_k=top_k), None
        except (RuntimeError, requests.exceptions.RequestException) as error:
            print(f"   attempt {attempt} failed: {str(error)[:90]}")
            if attempt < attempts:
                time.sleep(10 * attempt)
    return {"answer": "ERROR: the API call failed", "citations": []}, "api_error"


def run_config(config, rows):
    results = []
    for row in rows:
        out, error = ask_with_retry(row["question"], config["top_k"])
        answer = out["answer"]
        refused = error is None and is_refusal(answer)
        keyword = row["expected_keyword"].lower()
        correct = error is None and bool(keyword) and keyword in normalise(answer) and not refused
        cited = error is None and bool(CITATION.search(answer)) and not refused
        if row["answerable"]:
            passed = correct and cited
        else:
            passed = refused
        results.append({
            "id": row["id"],
            "answerable": row["answerable"],
            "answer": answer,
            "citations": [c["id"] for c in out["citations"]],
            "error": error,
            "correct": correct,
            "cited": cited,
            "refused": refused,
            "passed": passed,
        })
        label = "ERROR" if error else ("PASS" if passed else "FAIL")
        print(f"  config {config['name']} Q{row['id']}: {label}")
        time.sleep(2)
    return results


def summarise(config, results):
    answerable = [r for r in results if r["answerable"]]
    unanswerable = [r for r in results if not r["answerable"]]
    return {
        "config": config["name"],
        "top_k": config["top_k"],
        "correct": sum(r["correct"] for r in answerable),
        "answerable_total": len(answerable),
        "cited": sum(r["cited"] for r in answerable),
        "refused": sum(r["refused"] for r in unanswerable),
        "unanswerable_total": len(unanswerable),
        "passed": sum(r["passed"] for r in results),
        "total": len(results),
        "errors": sum(1 for r in results if r["error"]),
    }


def make_table(summaries, winner):
    lines = [
        "| Config | top_k | Correct | Cited | Refused when unanswerable | Score |",
        "|--------|-------|---------|-------|---------------------------|-------|",
    ]
    for s in summaries:
        mark = " (winner)" if s is winner else ""
        lines.append(
            f"| {s['config']}{mark} | {s['top_k']} "
            f"| {s['correct']}/{s['answerable_total']} "
            f"| {s['cited']}/{s['answerable_total']} "
            f"| {s['refused']}/{s['unanswerable_total']} "
            f"| {s['passed']}/{s['total']} |"
        )
    return "\n".join(lines)


def main():
    rows = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    all_results, summaries = {}, []
    for config in CONFIGS:
        print(f"\nRunning config {config['name']} (top_k={config['top_k']})")
        results = run_config(config, rows)
        all_results[config["name"]] = results
        summaries.append(summarise(config, results))

    # Winner: highest score, then most correct, then the smaller top_k
    winner = max(summaries, key=lambda s: (s["passed"], s["correct"], -s["top_k"]))
    table = make_table(summaries, winner)

    RESULTS_JSON.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    RESULTS_MD.write_text("# RAG evaluation\n\n" + table + "\n", encoding="utf-8")
    print("\n" + table)
    for s in summaries:
        if s["errors"]:
            print(f"Warning: config {s['config']} had {s['errors']} network errors. Run again for a fair score.")
    print(f"\nWinner: config {winner['config']} (top_k={winner['top_k']})")


if __name__ == "__main__":
    main()