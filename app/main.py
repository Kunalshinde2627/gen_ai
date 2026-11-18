
import json

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.rag import answer_question
from app.vectorstore import query as semantic_query
from app.records import get_record, load_records
from app.smart_search import smart_search
from app.llm import ask_llm

# LangGraph imports
from app.graph import run_graph, resume_graph


app = FastAPI(title="TaxSaathi")


# 1. Request Models
class Question(BaseModel):
    question: str


class AgentRequest(BaseModel):
    question: str
    thread_id: str
    approved: Optional[bool] = None


# 2. Health API
@app.get("/health")
def health():
    return {"status": "ok"}


# 3. Records API
@app.get("/records")
def list_records(limit: int = 10):
    return load_records()[:limit]


@app.get("/records/{record_id}")
def read_record(record_id: str):
    record = get_record(record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    return record


# 4. Search API
@app.get("/search")
def search(q: str):
    return smart_search(q)


# 5. Questions API
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


# 6. Chat API
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
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )


# 7. Semantic Search API
@app.get("/search/semantic")
def search_semantic(q: str, top_k: int = 3):

    return semantic_query(q, top_k=top_k)


# 8. Ask API
@app.post("/ask")
def ask(body: Question):

    return answer_question(body.question)


# 9. Agent API with Human-in-the-Loop
@app.post("/agent")
def agent(body: AgentRequest):

    if not body.thread_id.strip():
        raise HTTPException(
            status_code=400,
            detail="thread_id cannot be empty"
        )

    try:

        # First request: Start graph
        if body.approved is None:

            result = run_graph(
                body.question,
                thread_id=body.thread_id
            )

            interrupts = result.get("__interrupt__", [])

            if interrupts:

                interrupt_data = interrupts[0].value

                return {
                    "status": "awaiting_approval",
                    "thread_id": body.thread_id,
                    "approval_required": interrupt_data
                }

            return {
                "status": "completed",
                "thread_id": body.thread_id,
                "answer": result["answer"]
            }

        # Second request: Resume graph
        else:

            result = resume_graph(
                thread_id=body.thread_id,
                approved=body.approved
            )

            return {
                "status": "completed",
                "thread_id": body.thread_id,
                "approved": body.approved,
                "answer": result["answer"]
            }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
