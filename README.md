# TaxSaathi

Helps a fresher with a first salary understand old vs new tax regime,
which ITR form to file and how much tax is due.

## Who is it for
A fresher who has received a first salary.

## Data source
Income Tax Department: https://www.incometax.gov.in
(4 help pages saved in `data/raw`, plus my own short tax records in `data/sample_records.json`.)

## Features
- Menu-driven command line interface
- Keyword search and TF-IDF smart search
- Semantic search with embeddings and a Chroma vector store
- RAG: answers from retrieved chunks, with [n] citations
- "I don't know" when the data cannot answer
- REST API with FastAPI
- Evaluation of 15 questions with a winner table

## Tech
Python, FastAPI, pandas, scikit-learn, Chroma, Groq (LLM), GitHub

## How to run

1. Install the libraries:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file (see `.env.example`) and add your own Groq API key:
   ```
   GROQ_API_KEY=your-key-here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

3. Build the vector store (once):
   ```
   python -m app.vectorstore
   ```

4. Run the menu (command line):
   ```
   python -m app.cli
   ```

5. Run the API server:
   ```
   python -m uvicorn app.main:app --reload
   ```

6. Open in the browser:
   - http://127.0.0.1:8000/docs (try every endpoint here)
   - http://127.0.0.1:8000/health
   - http://127.0.0.1:8000/records/R08
   - http://127.0.0.1:8000/search?q=80C
   - http://127.0.0.1:8000/search/semantic?q=What is Form 16
   - `POST /ask` with `{"question": "What is Form 16 and how do I use it?"}`

## RAG evaluation

I wrote 15 questions in `eval/eval_set.json`: 13 can be answered from my data and 2 cannot.
Each answer is scored on three things:
- **Correct:** the answer contains the expected keyword.
- **Cited:** the answer has a [n] citation.
- **Refused:** for the 2 unanswerable questions, TaxSaathi says "I don't know".

I compared two settings: how many chunks are given to the LLM (`top_k` = 3 or 5).

| Config | top_k | Correct | Cited | Refused when unanswerable | Score |
|--------|-------|---------|-------|---------------------------|-------|
| A (winner) | 3 | 11/13 | 12/13 | 2/2 | 13/15 |
| B | 5 | 10/13 | 11/13 | 2/2 | 11/15 |

**Winner: config A (top_k=3).** With 5 chunks the LLM got more less-relevant text and answered worse.

**Failures of config A (2 of 15):**
- **Q1** (slab for Rs 10 lakh, new regime): retrieval returned R08, R07 and R06 (80C and rebate records), not R01 (the slab record). So the answer talked about the rebate instead of the 10% slab.
- **Q5** (old vs new regime with PPF and health insurance): no chunk scored 0.5 or more, so TaxSaathi said "I don't know". This is the safe behaviour, because my data has the rules but no calculator to compare the two regimes.

Q6 (SBI refund date) and Q15 (which mutual fund to buy) cannot be answered from my data. TaxSaathi refused both.

Run the evaluation:
```
python -m eval.run_eval
```

## Notes
- This is a learning project. Always check the final numbers on incometax.gov.in.
- `.env` (the API key) is never committed.