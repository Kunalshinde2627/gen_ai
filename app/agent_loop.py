import json
import re

from app.llm import ask_llm
from app.rag import NO_ANSWER, answer_question
from app.tools import new_regime_tax_calculator, old_regime_tax_calculator

MAX_STEPS = 5



SYSTEM_PROMPT = """You are TaxSaathi, an agent that helps a fresher in India with income tax.

You can use these tools. Reply with ONE JSON object only, nothing else.

1. search_rules: look up a tax rule, form or deadline in the Income Tax data.
   {"action": "search_rules", "input": "your search question"}

2. new_regime_tax: calculate tax in the new regime (AY 2026-27) from TAXABLE income.
   {"action": "new_regime_tax", "input": 600000}

3. old_regime_tax: calculate tax in the old regime from TAXABLE income.
   {"action": "old_regime_tax", "input": 600000}

4. final: give the final answer to the user.
   {"action": "final", "input": "your answer"}

Rules:

- Taxable income in the new regime = salary + other income - 75,000 standard deduction.
- Taxable income in the old regime = salary + other income - 50,000 standard deduction - 80C (max 150,000) - 80D.

- IMPORTANT: If the user asks how much tax they need to pay, ALWAYS call the appropriate calculator tool first.
- For new regime questions, use new_regime_tax.
- For old regime questions, use old_regime_tax.
- Do not call search_rules for tax calculation questions.
- Use search_rules only for tax rules, forms and deadlines.

- When a calculator tool returns total_tax, use that exact value.
- Never calculate or modify the tax amount yourself.
- Explain the calculator result in simple language.
- Do not invent rebate limits or tax amounts.

- If a search says "I don't know", or the question is about something else (refund dates, investment advice), the final answer is:
  I don't know. Please check incometax.gov.in.

- Do not guess.
- Keep the final answer short, with amounts in rupees.
"""





def parse_action(text):
    """Pull the first JSON object out of the LLM reply. Return None if there is none."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def to_number(value):
    return int(float(str(value).replace(",", "").replace("\u20b9", "").strip()))


def run_tool(action, value):
    """Run one tool and return its result as text for the LLM."""
    if action == "search_rules":
        return answer_question(str(value))["answer"]
    if action in ("new_regime_tax", "old_regime_tax"):
        calculator = new_regime_tax_calculator if action == "new_regime_tax" else old_regime_tax_calculator
        result = calculator(to_number(value))
        return json.dumps({
            "taxable_income": result["taxable_income"],
            "slab_tax": result["slab_tax"],
            "rebate_87a": result["rebate_87a"],
            "cess_4_percent": result["cess_4_percent"],
            "total_tax": result["total_tax"],
        })
    return f"Unknown tool: {action}"


def run_agent(question):
    """Let the LLM pick tools, one step at a time, until it gives a final answer."""
    transcript = f"Question: {question}"
    steps = []
    for _ in range(MAX_STEPS):
        reply = ask_llm(SYSTEM_PROMPT, transcript, temperature=0)
        action = parse_action(reply)
        if action is None or "action" not in action:
            transcript += "\nYour last reply was not valid JSON. Reply with one JSON object."
            continue

        name, value = action["action"], action.get("input", "")
        if name == "final":
            return {"answer": str(value), "steps": steps}

        try:
            result = run_tool(name, value)
        except (ValueError, TypeError):
            result = "Error: the input for this tool must be a number."
        steps.append({"tool": name, "input": value, "result": result})
        transcript += f"\nAction: {json.dumps(action)}\nResult: {result}"

    return {"answer": NO_ANSWER, "steps": steps}


if __name__ == "__main__":
    question = input("Ask TaxSaathi: ")
    out = run_agent(question)
    for number, step in enumerate(out["steps"], start=1):
        print(f"\nStep {number}: {step['tool']}({step['input']})")
        print("  ->", str(step["result"])[:200])
    print("\nANSWER:", out["answer"])