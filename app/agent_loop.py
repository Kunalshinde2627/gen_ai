
import json
import re

from app.rag import NO_ANSWER, answer_question
from app.tools import (
    compare_regimes,
    new_regime_tax_calculator,
    old_regime_tax_calculator,
)


def extract_salary(question):
    text = question.lower().replace(",", "")

    salary_patterns = [
        r"salary\s*(?:is|of)?\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs)?",
        r"(\d+(?:\.\d+)?)\s*(lakh|lakhs)?\s*(?:rs\.?|₹)?\s*salary",
    ]

    for pattern in salary_patterns:
        match = re.search(pattern, text)

        if match:
            salary = float(match.group(1))

            if match.group(2):
                salary *= 100000

            return int(salary)

    return None


def extract_fd_interest(question):
    text = question.lower().replace(",", "")

    patterns = [
        r"(\d+(?:\.\d+)?)\s*(lakh|lakhs)?\s*(?:rs\.?|₹)?\s*fd\s+interest",
        r"fd\s+interest\s*(?:is)?\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s*(lakh|lakhs)?",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            amount = float(match.group(1))

            if match.group(2):
                amount *= 100000

            return int(amount)

    return 0


def calculate_tax(question, regime):
    salary = extract_salary(question)

    if salary is None:
        return None

    fd_interest = extract_fd_interest(question)

    if regime == "new":
        taxable_income = salary + fd_interest - 75000
        calculator = new_regime_tax_calculator
    else:
        taxable_income = salary + fd_interest - 50000
        calculator = old_regime_tax_calculator

    taxable_income = max(0, int(taxable_income))

    return calculator(taxable_income)


def calculate_regime_comparison(question):
    salary = extract_salary(question)

    if salary is None:
        return None

    fd_interest = extract_fd_interest(question)

    # Existing project assumptions:
    # New regime standard deduction = Rs 75,000
    # Old regime standard deduction = Rs 50,000

    new_taxable_income = max(
        0,
        salary + fd_interest - 75000,
    )

    old_taxable_income = max(
        0,
        salary + fd_interest - 50000,
    )

    result = compare_regimes(
        new_taxable_income,
        old_taxable_income,
    )

    result["gross_salary"] = salary
    result["fd_interest"] = fd_interest

    return result


def run_agent(question):
    steps = []
    citations = []

    lower_question = question.lower()

    # Detect tax calculation questions
    calculation_keywords = [
        "calculate tax",
        "calculate my tax",
        "tax calculation",
        "tax payable",
        "how much tax",
        "how much do i pay",
        "tax on my salary",
        "tax on salary",
        "income tax on",
        "compute tax",
    ]

    is_tax_calculation = any(
        keyword in lower_question
        for keyword in calculation_keywords
    )

    # Detect regime comparison questions
    comparison_keywords = [
        "compare regimes",
        "compare regime",
        "compare old and new",
        "compare new and old",
        "old vs new",
        "new vs old",
        "which regime is better",
        "which regime is best",
        "regime comparison",
    ]

    is_comparison = any(
        keyword in lower_question
        for keyword in comparison_keywords
    )

    # Regime comparison
    if is_comparison:
        result = calculate_regime_comparison(question)

        if result is None:
            return {
                "answer": "Please provide your annual salary to compare both regimes.",
                "steps": steps,
                "citations": citations,
                "comparison": None,
            }

        steps.append({
            "tool": "compare_regimes",
            "input": {
                "new_taxable_income": result["new_regime"]["taxable_income"],
                "old_taxable_income": result["old_regime"]["taxable_income"],
            },
            "result": json.dumps(result),
        })

        if result["better_regime"] == "new":
            better_text = "New Regime is better."
        elif result["better_regime"] == "old":
            better_text = "Old Regime is better."
        else:
            better_text = "Both regimes have equal tax."

        answer = (
            f"Your annual salary is Rs {result['gross_salary']:,}. "
            f"FD interest is Rs {result['fd_interest']:,}. "
            f"New Regime tax is Rs {result['new_regime']['total_tax']:,}. "
            f"Old Regime tax is Rs {result['old_regime']['total_tax']:,}. "
            f"{better_text} "
            f"Tax difference is Rs {result['tax_saving']:,}."
        )

        return {
            "answer": answer,
            "steps": steps,
            "citations": citations,
            "comparison": result,
        }

    # Single-regime tax calculation
    if is_tax_calculation:
        if "new regime" in lower_question:
            regime = "new"
        elif "old regime" in lower_question:
            regime = "old"
        else:
            return {
                "answer": "Please specify whether you want the new regime or old regime.",
                "steps": steps,
                "citations": citations,
                "comparison": None,
            }

        result = calculate_tax(question, regime)

        if result is None:
            return {
                "answer": "Please provide your salary amount.",
                "steps": steps,
                "citations": citations,
                "comparison": None,
            }

        tool_name = (
            "new_regime_tax"
            if regime == "new"
            else "old_regime_tax"
        )

        steps.append({
            "tool": tool_name,
            "input": result["taxable_income"],
            "result": json.dumps(result),
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
            "steps": steps,
            "citations": citations,
            "comparison": None,
        }

    # General questions use RAG
    try:
        rag_result = answer_question(question)

        answer = rag_result["answer"]
        citations = rag_result.get("citations", [])

        steps.append({
            "tool": "search_rules",
            "input": question,
            "result": answer,
        })

        if answer == NO_ANSWER or "I don't know" in answer:
            answer = NO_ANSWER
            citations = []

        return {
            "answer": answer,
            "steps": steps,
            "citations": citations,
            "comparison": None,
        }

    except Exception as error:  # noqa: BLE001
        print("RAG ERROR:", error)

        return {
            "answer": NO_ANSWER,
            "steps": steps,
            "citations": [],
            "comparison": None,
        }


if __name__ == "__main__":
    question = input("Ask TaxSaathi: ")

    output = run_agent(question)

    for number, step in enumerate(output["steps"], start=1):
        print(f"\nStep {number}: {step['tool']}")
        print("  ->", step["result"])

    print("\nANSWER:", output["answer"])
    print("\nCOMPARISON:", output.get("comparison"))
    print("\nCITATIONS:", output["citations"])
