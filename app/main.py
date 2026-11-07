from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.records import get_record, load_records
from app.smart_search import smart_search

app = FastAPI(title="TaxSaathi")


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/records")
def list_records(limit: int = 10):
    return load_records()[:limit]


@app.get("/records/{record_id}")
def read_record(record_id: str):
    record = get_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@app.get("/search")
def search(q: str):
    return smart_search(q)


@app.post("/questions")
def ask_question(body: Question):
    results = smart_search(body.question, top_k=1)
    if not results:
        return {"answer": "I don't know. Please check incometax.gov.in.", "sources": []}
    best = results[0]
    return {"answer": best["summary"], "sources": [best["source_url"]]}