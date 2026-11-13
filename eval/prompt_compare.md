
# Prompt Comparison – TaxSaathi

## 1. Objective

The objective is to compare two prompt versions using 10 real-world Indian income tax questions and evaluate their response quality.

## 2. Prompt Version 1 – Basic Prompt

You are a helpful Indian tax assistant.

Answer the user's question clearly and briefly.

## 3. Prompt Version 2 – Improved Prompt

You are TaxSaathi, an Indian income tax assistant.

Instructions:
- Give accurate and clear answers.
- Use simple language for beginners.
- Explain tax concepts with examples whenever helpful.
- Never invent tax rules, rates, or deadlines.
- If unsure, recommend checking incometax.gov.in.
- Return answers in a structured JSON format.
- Include answer, confidence, and follow_up fields.

## 4. Evaluation Questions

1. What is the tax slab for Rs 10 lakh income under the new regime for AY 2026-27?
2. Which ITR form should I file if I only have salary and bank interest?
3. Can I file ITR-1 if I have short-term capital gains?
4. My salary is 6.5 lakh and I have 25,000 FD interest, how much tax do I pay in new regime and do I get rebate?
5. Is old regime or new regime better for me if I pay 1.5 lakh in PPF and 40,000 health insurance?
6. When will my refund for last year be credited to my SBI account?
7. What is Form 16 and how do I use it?
8. How many days do I have to e-verify my return?
9. Can I claim HRA exemption in the new regime?
10. Do I have to pay 4% cess on my tax?

## 5. Comparison Criteria

| Criteria | Version 1 – Basic | Version 2 – Improved |
|---|---|---|
| Response format | Free-form text | Structured JSON |
| Clarity | General explanation | Beginner-friendly instructions |
| Confidence | Not provided | Included |
| Follow-up | Not required | Included |
| Tax safety | Limited instructions | Includes verification guidance |
| Consistency | Less structured | More structured |

## 6. Observations

- Both prompts generated responses for the 10 evaluation questions.
- The basic prompt returned free-form answers.
- The improved prompt returned structured answers with answer, confidence, and follow-up fields.
- The improved prompt provided clearer instructions for handling Indian income tax questions.
- Some tax information, especially tax slabs and calculations, still requires verification against official Income Tax Department sources.

## 7. Conclusion

The improved prompt provides a more consistent and structured response format than the basic prompt.

However, prompt engineering alone does not guarantee factual accuracy. Tax rates, eligibility conditions, deadlines, and calculations must be verified using official Income Tax Department information.

Therefore, Version 2 is preferred for the TaxSaathi project because it provides structured responses and better guidance for users.
