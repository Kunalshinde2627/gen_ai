
from fastapi.testclient import TestClient

from app import main
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_endpoint_with_fake_llm(monkeypatch):
    def fake_answer_question(question):
        return {
            "answer": "Income tax is tax on income. [1]",
            "citations": [
                {
                    "number": 1,
                    "id": "doc1",
                    "title": "Income Tax",
                    "source": "income.pdf",
                    "score": 0.9,
                }
            ],
        }

    monkeypatch.setattr(
        main, "answer_question", fake_answer_question
    )

    response = client.post(
        "/ask",
        json={"question": "What is income tax?"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Income tax is tax on income. [1]"
    assert len(response.json()["citations"]) == 1


def test_ask_endpoint_with_empty_question_result(monkeypatch):
    def fake_answer_question(question):
        return {
            "answer": "I don't know. Please check incometax.gov.in.",
            "citations": [],
        }

    monkeypatch.setattr(
        main, "answer_question", fake_answer_question
    )

    response = client.post(
        "/ask",
        json={"question": "Unknown topic"},
    )

    assert response.status_code == 200
    assert response.json()["citations"] == []


def test_ask_endpoint_validation():
    response = client.post("/ask", json={})

    assert response.status_code == 422
