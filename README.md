# TaxSaathi

Helps a fresher with a first salary understand old vs new tax regime,
which ITR form to file and how much tax is due.

## Who is it for
A fresher who has received a first salary.

## Data source
Income Tax Department: https://www.incometax.gov.in

## Features
- Tax information records (JSON)
- Menu-driven command line interface
- Keyword search
- REST API with FastAPI
- Old vs new regime tax comparison (planned)

## Tech
Python, JSON, FastAPI, pandas, scikit-learn, GitHub

## How to run

1. Install the libraries:
   ```
   pip install -r requirements.txt
   ```

2. Run the menu (command line):
   ```
   python -m app.cli
   ```

3. Run the API server:
   ```
   python -m uvicorn app.main:app --reload
   ```

4. Open in the browser:
   - http://127.0.0.1:8000/health
   - http://127.0.0.1:8000/records?limit=3
   - http://127.0.0.1:8000/records/R08
   - http://127.0.0.1:8000/search?q=80C
   - http://127.0.0.1:8000/docs