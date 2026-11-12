from app.smart_search import smart_search

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

for number, question in enumerate(QUESTIONS, start=1):
    results = smart_search(question, top_k=2)
    print(f"\nQ{number}: {question}")
    if not results:
        print("   -> I don't know. Please check incometax.gov.in.")
    for record in results:
        print(f"   -> {record['id']} {record['topic']} (score {record['score']})")