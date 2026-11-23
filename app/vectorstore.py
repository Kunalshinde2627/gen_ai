import logging
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from app.chunking import build_chunks

logger = logging.getLogger(__name__)

CHROMA_DIR = Path(__file__).resolve().parent.parent / "data" / "chroma"
COLLECTION_NAME = "taxsaathi"
INDEX_BATCH_SIZE = 10

_client = None
_embedder = None
_collection = None


def get_embedder():
    """Get or initialize the DefaultEmbeddingFunction singleton."""
    global _embedder
    if _embedder is None:
        _embedder = embedding_functions.DefaultEmbeddingFunction()
    return _embedder


def get_client():
    """Get or initialize the persistent Chroma client singleton."""
    global _client
    if _client is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client


def get_collection():
    """Open (or create) the persistent Chroma collection as a cached singleton."""
    global _collection
    if _collection is None:
        client = get_client()
        embedder = get_embedder()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedder,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def reset_collection_cache():
    """Reset cached collection reference (useful for testing)."""
    global _collection
    _collection = None


def index_all(batch_size=INDEX_BATCH_SIZE):
    """Embed chunks in small batches to stay within memory limits (upsert)."""
    chunks = build_chunks()
    if not chunks:
        return 0

    collection = get_collection()
    total = len(chunks)
    for i in range(0, total, batch_size):
        batch = chunks[i : i + batch_size]
        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[
                {"source": c["source"], "page": c["page"], "title": c["title"]}
                for c in batch
            ],
        )
    return collection.count()


def query(question, top_k=3, min_score=0.5):
    """Return the closest chunks from Chroma. Score = 1 - cosine distance."""
    if not question or not str(question).strip():
        return []

    try:
        collection = get_collection()
        if collection.count() == 0:
            index_all()
        result = collection.query(query_texts=[question], n_results=top_k)
    except Exception:
        logger.exception(
            "ChromaDB retrieval query failed for question %r",
            question[:50],
        )
        return []

    if not result or not result.get("ids") or not result["ids"] or not result["ids"][0]:
        return []

    hits = []
    for chunk_id, text, meta, distance in zip(
        result["ids"][0],
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        score = round(1 - distance, 3)
        if score >= min_score:
            hits.append({"id": chunk_id, "text": text, "score": score, **meta})
    return hits


if __name__ == "__main__":
    print(f"Indexed {index_all()} chunks into Chroma at {CHROMA_DIR}")