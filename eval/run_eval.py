
import json
from pathlib import Path

from app.rag import answer_question

BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_FILE = BASE_DIR / "eval" / "eval_set.json"


def evaluate(top_k):
    with open(EVAL_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    results = []

    for item in questions:
        response = answer_question(
            item["question"],
            top_k=top_k
        )

        answer = response["answer"]

        results.append({
            "id": item["id"],
            "question": item["question"],
            "expected": item["expected"],
            "actual": answer,
            "citations_count": len(response["citations"]),
            "citations": response["citations"]
        })

    return results


if __name__ == "__main__":

    for top_k in [3, 5]:
        results = evaluate(top_k)

        print(f"\n===== TOP K = {top_k} =====")

        for result in results:
            print(f"\n{result['id']}: {result['question']}")
            print(f"Expected: {result['expected']}")
            print(f"Actual: {result['actual']}")
            print(f"Citations: {result['citations_count']}")

        output_file = BASE_DIR / "eval" / f"results_top_{top_k}.json"

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=2, ensure_ascii=False)

        print(f"\nResults saved: {output_file}")
