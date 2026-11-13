
from pathlib import Path
import sys
import json
import time

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.llm import ask_llm

questions = [
    "What is the tax slab for Rs 10 lakh income under the new regime for AY 2026-27?",
    "Which ITR form should I file if I only have salary and bank interest?",
    "Can I file ITR-1 if I have short-term capital gains?",
    "My salary is 6.5 lakh and I have 25,000 FD interest, how much tax do I pay in new regime and do I get rebate?",
    "Is old regime or new regime better for me if I pay 1.5 lakh in PPF and 40,000 health insurance?",
    "When will my refund for last year be credited to my SBI account?",
    "What is Form 16 and how do I use it?",
    "How many days do I have to e-verify my return?",
    "Can I claim HRA exemption in the new regime?",
    "Do I have to pay 4% cess on my tax?"
]

prompt_v1 = """
You are a helpful Indian tax assistant.
Answer the user's question clearly and briefly.
"""

prompt_v2 = (
    (BASE_DIR / "prompts" / "system_prompt.txt").read_text(encoding="utf-8")
    + """
Return ONLY valid JSON with these keys:
{
    "answer": "Your answer",
    "confidence": "high, medium, or low",
    "follow_up": "A helpful follow-up question or null"
}
Do not include markdown code fences.
"""
)

output_file = BASE_DIR / "eval" / "prompt_results.md"

with output_file.open("w", encoding="utf-8") as file:
    file.write("# Prompt Comparison Results\n\n")

    for number, question in enumerate(questions, start=1):
        print(f"Testing Question {number}/10...")

        file.write(f"## Q{number}: {question}\n\n")

        for version, prompt in [
            ("Version 1 - Basic", prompt_v1),
            ("Version 2 - Improved", prompt_v2),
        ]:
            try:
                answer = ask_llm(prompt, question)
                file.write(f"### {version}\n\n")

                try:
                    parsed = json.loads(answer)
                    file.write(f"Answer: {parsed.get('answer', '')}\n\n")
                    file.write(f"Confidence: {parsed.get('confidence', 'N/A')}\n\n")
                    file.write(f"Follow-up: {parsed.get('follow_up', 'N/A')}\n\n")
                except json.JSONDecodeError:
                    file.write(f"{answer}\n\n")

            except Exception as error:
                file.write(f"Error: {error}\n\n")
        time.sleep(20)
        file.write("---\n\n")

print(f"\nComparison completed! Results saved to: {output_file}")
