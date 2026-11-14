
import json

from pathlib import Path

from app.vectorstore import query as semantic_query
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.records import get_record, load_records
from app.smart_search import smart_search
from app.llm import ask_llm

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
        return {
            "answer": "I don't know. Please check incometax.gov.in.",
            "sources": []
        }

    best = results[0]
    return {
        "answer": best["summary"],
        "sources": [best["source_url"]]
    }


@app.post("/chat")
def chat(body: Question):
    
    system_prompt = (
        Path("prompts/system_prompt.txt").read_text(encoding="utf-8")
        + """

        Return ONLY valid JSON with these three keys:
        {
            "answer": "Your answer to the question",
            "confidence": "high, medium, or low",
            "follow_up": "One helpful follow-up question or null"
        }

        Do not include markdown code fences.
        """
    )


    try:
        response = ask_llm(system_prompt, body.question)
        result = json.loads(response)

        return {
            "answer": result["answer"],
            "confidence": result["confidence"],
            "follow_up": result["follow_up"]
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="LLM returned an invalid JSON response"
        )

    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error))

    

@app.get("/search/semantic")
def search_semantic(q: str, top_k: int = 3):
    """Find the chunks closest in meaning to the question (Chroma)."""
    return semantic_query(q, top_k=top_k)
