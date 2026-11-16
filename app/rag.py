from app.llm import ask_llm
from app.vectorstore import query

SYSTEM_PROMPT = """You are TaxSaathi, a helper for freshers with a first salary in India.
Answer ONLY from the numbered sources below. Do not use any other knowledge.
After each fact, add the source number in square brackets, like [1].
If the sources do not contain the answer, reply exactly: I don't know. Please check incometax.gov.in.
Keep the answer short and simple. Do not give investment advice."""

NO_ANSWER = "I don't know. Please check incometax.gov.in."


def answer_question(question, top_k=3):
    """Find the closest chunks, ask the LLM to answer from them, return answer + citations."""
    hits = query(question, top_k=top_k, min_score=0.50)
    print("QUESTION:", question)
    print("RETRIEVED HITS:", hits)
    if not hits:
        return {"answer": NO_ANSWER, "citations": []}

    sources = "\n\n".join(
        f"[{number}] {hit['title']}: {hit['text']}"
        for number, hit in enumerate(hits, start=1)
    )
    user_message = f"Sources:\n{sources}\n\nQuestion: {question}"
    answer = ask_llm(SYSTEM_PROMPT, user_message, temperature=0)
    if NO_ANSWER in answer:
        return {
        "answer": NO_ANSWER,
        "citations": []
    }
    citations = [
        {
            "number": number,
            "id": hit["id"],
            "title": hit["title"],
            "source": hit["source"],
            "score": hit["score"],
        }
        for number, hit in enumerate(hits, start=1)
    ]
    return {"answer": answer, "citations": citations}