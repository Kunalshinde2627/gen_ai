
import json
import re

from app.llm import ask_llm
from app.rag import NO_ANSWER, answer_question
from app.tools import (
    new_regime_tax_calculator,
    old_regime_tax_calculator
)

MAX_STEPS = 5

SYSTEM_PROMPT = """You are TaxSaathi, an income tax assistant for freshers in India.

You will receive a question and tool result.

Explain the provided tool result in simple English.
Do not invent or change any tax amount.
Reply with one JSON object only:
{"action": "final", "input": "your answer"}
"""


def to_number(value):
    return int(
        float(
            str(value)
            .replace(",", "")
            .replace("₹", "")
            .replace("Rs", "")
            .strip()
        )
    )


def extract_amount(text):
    """Extract lakh or numeric amounts from question."""

    text = text.lower().replace(",", "")

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(lakh|lakhs)",
        text
    )

    if match:
        return int(float(match.group(1)) * 100000)

    match = re.search(r"(\d+(?:\.\d+)?)", text)

    if match:
        return int(float(match.group(1)))

    return None




def calculate_tax(question, regime):
    """Calculate tax using Python calculator."""

    text = question.lower().replace(",", "")

    # Extract salary: 6.5 lakh
    salary_match = re.search(
        r"salary\s*(?:is)?\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs)?",
        text
    )

    if not salary_match:
        return None

    salary = float(salary_match.group(1))

    if salary_match.group(2):
        salary *= 100000

    # Extract FD interest: 25,000 FD interest
    fd_interest = 0

    fd_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(lakh|lakhs)?\s*(?:rs\.?|₹)?\s*fd\s+interest",
        text
    )

    if not fd_match:
        fd_match = re.search(
            r"fd\s+interest\s*(?:is)?\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs)?",
            text
        )

    if fd_match:
        fd_interest = float(fd_match.group(1))

        if fd_match.group(2):
            fd_interest *= 100000

    # Calculate taxable income
    if regime == "new":
        taxable_income = salary + fd_interest - 75000
        calculator = new_regime_tax_calculator
    else:
        taxable_income = salary + fd_interest - 50000
        calculator = old_regime_tax_calculator

    taxable_income = max(0, int(taxable_income))

    result = calculator(taxable_income)

    return {
        "taxable_income": result["taxable_income"],
        "slab_tax": result["slab_tax"],
        "rebate_87a": result["rebate_87a"],
        "cess_4_percent": result["cess_4_percent"],
        "total_tax": result["total_tax"]
    }



def run_agent(question):

    steps = []
    lower_question = question.lower()

    # Detect tax calculation questions
    is_tax_question = any(
        word in lower_question
        for word in [
            "tax",
            "payable",
            "how much do i pay",
            "calculate"
        ]
    )

    if is_tax_question:

        if "new regime" in lower_question:
            regime = "new"

        elif "old regime" in lower_question:
            regime = "old"

        else:
            return {
                "answer": "Please specify whether you want the new regime or old regime.",
                "steps": steps
            }

        result = calculate_tax(question, regime)

        if result is None:
            return {
                "answer": "Please provide your salary amount.",
                "steps": steps
            }

        tool_name = (
            "new_regime_tax"
            if regime == "new"
            else "old_regime_tax"
        )

        steps.append({
            "tool": tool_name,
            "input": result["taxable_income"],
            "result": json.dumps(result)
        })

        answer = (
            f"Your taxable income is Rs "
            f"{result['taxable_income']:,}. "
            f"Tax before rebate is Rs "
            f"{result['slab_tax']:,}. "
            f"Section 87A rebate is Rs "
            f"{result['rebate_87a']:,}. "
            f"Cess is Rs "
            f"{result['cess_4_percent']:,}. "
            f"Your final tax payable is Rs "
            f"{result['total_tax']:,}."
        )

        return {
            "answer": answer,
            "steps": steps
        }

    # Non-calculation questions use RAG
    try:
        rag_result = answer_question(question)
        answer = rag_result["answer"]

        steps.append({
            "tool": "search_rules",
            "input": question,
            "result": answer
        })

        if answer == NO_ANSWER or "I don't know" in answer:
            answer = "I don't know. Please check incometax.gov.in."

        return {
            "answer": answer,
            "steps": steps
        }

    except Exception:
        return {
            "answer": NO_ANSWER,
            "steps": steps
        }


if __name__ == "__main__":

    question = input("Ask TaxSaathi: ")

    output = run_agent(question)

    for number, step in enumerate(output["steps"], start=1):
        print(f"\nStep {number}: {step['tool']}")
        print("  ->", step["result"])

    print("\nANSWER:", output["answer"])
