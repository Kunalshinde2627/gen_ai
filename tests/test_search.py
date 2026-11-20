
from app import vectorstore


def test_query_returns_matching_results(monkeypatch):
    class FakeCollection:
        def count(self):
            return 2

        def query(self, **kwargs):
            return {
                "ids": [["doc1", "doc2"]],
                "documents": [["Income tax information", "GST information"]],
                "metadatas": [
                    [
                        {"source": "income.pdf", "page": 1, "title": "Income Tax"},
                        {"source": "gst.pdf", "page": 2, "title": "GST"},
                    ]
                ],
                "distances": [[0.1, 0.8]],
            }

    monkeypatch.setattr(
        vectorstore, "get_collection", lambda: FakeCollection()
    )

    result = vectorstore.query("income tax", top_k=2, min_score=0.5)

    assert len(result) == 1
    assert result[0]["id"] == "doc1"
    assert result[0]["score"] == 0.9


def test_query_returns_empty_when_no_match(monkeypatch):
    class FakeCollection:
        def count(self):
            return 2

        def query(self, **kwargs):
            return {
                "ids": [["doc1"]],
                "documents": [["GST information"]],
                "metadatas": [[{"source": "gst.pdf", "page": 1, "title": "GST"}]],
                "distances": [[0.9]],
            }

    monkeypatch.setattr(
        vectorstore, "get_collection", lambda: FakeCollection()
    )

    result = vectorstore.query("income tax", min_score=0.5)

    assert result == []


def test_query_indexes_when_collection_empty(monkeypatch):
    class FakeCollection:
        def count(self):
            return 0

        def query(self, **kwargs):
            return {
                "ids": [["doc1"]],
                "documents": [["Income tax information"]],
                "metadatas": [[{"source": "income.pdf", "page": 1, "title": "Income Tax"}]],
                "distances": [[0.1]],
            }

    collection = FakeCollection()

    monkeypatch.setattr(
        vectorstore, "get_collection", lambda: collection
    )
    monkeypatch.setattr(vectorstore, "index_all", lambda: 1)

    result = vectorstore.query("income tax")

    assert len(result) == 1
    assert result[0]["id"] == "doc1"
