from pathlib import Path

from app.embed import semantic_search

OUTPUT = Path(__file__).resolve().parent / "search_results.md"

QUESTIONS = [
    "What is the tax slab for Rs 10 lakh income under the new regime for AY 2026-27?",
    "Which ITR form should I file if I only have salary and bank interest?",
    "Can I file ITR-1 if I have short-term capital gains?",
    "My salary is 6.5 lakh and I have 25,000 FD interest, how much tax do I pay in new regime and do I get rebate?",
    "Is old regime or new regime better for me if I pay 1.5 lakh in PPF and 40,000 health insurance?",
    "When will my refund for last year be credited to my SBI account?",
    "What is Form 16 and how do I use it?",
    "How many days do I have to e-verify my return?",
    "Can I claim HRA exemption in the new regime?",
    "Do I have to pay 4% cess on my tax?",
]


def main():
    lines = [
        "# Semantic search results",
        "",
        "Top 3 chunks for each of my 10 TaxSaathi questions.",
        "Score is cosine similarity (1.0 = same meaning). Below 0.5 counts as no match.",
        "",
    ]
    for number, question in enumerate(QUESTIONS, start=1):
        hits = semantic_search(question, top_k=3)
        lines += [f"## Q{number}. {question}", ""]
        if not hits:
            lines += ["No match. TaxSaathi should say: I don't know.", ""]
            continue
        for hit in hits:
            snippet = hit["text"][:160].replace("\n", " ")
            lines.append(f"- **{hit['id']}** (score {hit['score']}) {hit['title'][:70]}")
            lines.append(f"  - {snippet}")
            lines.append(f"  - source: {hit['source']}")
        lines.append("")
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {OUTPUT.name} for {len(QUESTIONS)} questions")


if __name__ == "__main__":
    main()