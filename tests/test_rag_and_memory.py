import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import vectorstore
from app.main import app
from app.rag import NO_ANSWER, answer_question

client = TestClient(app)


def test_vectorstore_singleton_instances():
    """Verify that get_client, get_embedder, and get_collection return singleton instances."""
    client1 = vectorstore.get_client()
    client2 = vectorstore.get_client()
    assert client1 is client2

    embedder1 = vectorstore.get_embedder()
    embedder2 = vectorstore.get_embedder()
    assert embedder1 is embedder2

    coll1 = vectorstore.get_collection()
    coll2 = vectorstore.get_collection()
    assert coll1 is coll2


def test_vectorstore_query_empty_or_whitespace():
    """Verify query handles invalid or whitespace questions safely without searching."""
    assert vectorstore.query("") == []
    assert vectorstore.query("   ") == []
    assert vectorstore.query(None) == []


def test_vectorstore_empty_collection_handling(monkeypatch):
    """Test behavior when collection is empty and indexing yields 0 chunks."""
    class EmptyCollection:
        def count(self):
            return 0

        def query(self, **kwargs):
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    empty_coll = EmptyCollection()
    monkeypatch.setattr(vectorstore, "get_collection", lambda: empty_coll)
    monkeypatch.setattr(vectorstore, "index_all", lambda **kwargs: 0)

    results = vectorstore.query("some tax question")
    assert results == []


def test_vectorstore_query_exception_handling(monkeypatch):
    """Test that query returns [] if ChromaDB throws an unexpected exception."""
    class FailingCollection:
        def count(self):
            return 5

        def query(self, **kwargs):
            raise RuntimeError("Database connection corrupted")

    monkeypatch.setattr(vectorstore, "get_collection", lambda: FailingCollection())
    results = vectorstore.query("what is tax?")
    assert results == []


def test_index_all_batching(monkeypatch):
    """Test that index_all batches documents rather than sending all at once."""
    fake_chunks = [
        {"id": f"chunk_{i}", "text": f"text {i}", "source": f"src {i}", "page": f"p {i}", "title": f"t {i}"}
        for i in range(25)
    ]
    upsert_calls = []

    class MockBatchCollection:
        def upsert(self, ids, documents, metadatas):
            upsert_calls.append(len(ids))

        def count(self):
            return len(fake_chunks)

    mock_coll = MockBatchCollection()
    monkeypatch.setattr(vectorstore, "build_chunks", lambda: fake_chunks)
    monkeypatch.setattr(vectorstore, "get_collection", lambda: mock_coll)

    total = vectorstore.index_all(batch_size=10)
    assert total == 25
    # For 25 items with batch_size=10, there should be 3 batches: 10, 10, 5
    assert upsert_calls == [10, 10, 5]


def test_rag_retrieval_success(monkeypatch):
    """Test RAG retrieval end-to-end with mocked LLM response."""
    fake_hits = [
        {"id": "doc1", "title": "ITR Filing", "text": "File ITR by July 31.", "source": "itr.gov.in", "score": 0.85}
    ]
    monkeypatch.setattr("app.rag.query", lambda *args, **kwargs: fake_hits)

    with patch("app.rag.ask_llm", return_value="File your ITR by July 31. [1]"):
        res = answer_question("When is ITR due?")
        assert res["answer"] == "File your ITR by July 31. [1]"
        assert len(res["citations"]) == 1
        assert res["citations"][0]["id"] == "doc1"
        assert res["citations"][0]["score"] == 0.85


def test_rag_retrieval_no_hits(monkeypatch):
    """Test RAG returns NO_ANSWER when no chunks match threshold."""
    monkeypatch.setattr("app.rag.query", lambda *args, **kwargs: [])
    res = answer_question("Unknown extraterrestrial tax policy?")
    assert res["answer"] == NO_ANSWER
    assert res["citations"] == []


def test_agent_approval_flow():
    """Test full human approval workflow: request -> awaiting_approval -> approved -> completed."""
    thread_id = f"test_thread_{uuid.uuid4()}"

    # Step 1: Initial request (comparison question triggers calculation and approval)
    res1 = client.post(
        "/agent",
        json={"question": "Compare old and new regimes for salary 12 lakh", "thread_id": thread_id}
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "awaiting_approval"
    assert "approval_required" in data1
    assert data1["thread_id"] == thread_id

    # Step 2: Human approves the request
    res2 = client.post(
        "/agent",
        json={"question": "Compare old and new regimes for salary 12 lakh", "thread_id": thread_id, "approved": True}
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "completed"
    assert data2["approved"] is True
    assert "New Regime tax" in data2["answer"]


def test_agent_rejection_flow():
    """Test human rejection workflow: request -> awaiting_approval -> rejected -> rejected message."""
    thread_id = f"test_thread_{uuid.uuid4()}"

    # Step 1: Initial request
    res1 = client.post(
        "/agent",
        json={"question": "Compare old and new regimes for salary 10 lakh", "thread_id": thread_id}
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "awaiting_approval"

    # Step 2: Human rejects the request
    res2 = client.post(
        "/agent",
        json={"question": "Compare old and new regimes for salary 10 lakh", "thread_id": thread_id, "approved": False}
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "completed"
    assert data2["approved"] is False
    assert data2["answer"] == "Answer was not approved by the user."
    assert data2["sources"] == []


def test_agent_invalid_empty_inputs():
    """Test empty/invalid question and thread_id handling."""
    # Empty thread_id
    res_empty_thread = client.post(
        "/agent",
        json={"question": "Calculate tax on salary 10 lakh", "thread_id": "   "}
    )
    assert res_empty_thread.status_code == 400
    assert "thread_id cannot be empty" in res_empty_thread.json()["detail"]

    # Empty question on start
    res_empty_q = client.post(
        "/agent",
        json={"question": "   ", "thread_id": "thread_valid"}
    )
    assert res_empty_q.status_code == 400
    assert "question cannot be empty" in res_empty_q.json()["detail"]


def test_endpoints_empty_questions():
    """Test search and question endpoints with empty/whitespace input."""
    # GET /search with empty string
    res_search = client.get("/search?q=   ")
    assert res_search.status_code == 200
    assert res_search.json() == []

    # GET /search/semantic with empty string
    res_sem = client.get("/search/semantic?q=   ")
    assert res_sem.status_code == 200
    assert res_sem.json() == []

    # POST /questions with empty string
    res_q = client.post("/questions", json={"question": "   "})
    assert res_q.status_code == 200
    assert res_q.json()["answer"] == NO_ANSWER
