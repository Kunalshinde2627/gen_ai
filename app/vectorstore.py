from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from app.chunking import build_chunks

CHROMA_DIR = Path(__file__).resolve().parent.parent / "data" / "chroma"
COLLECTION_NAME = "taxsaathi"

_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_embedder = embedding_functions.DefaultEmbeddingFunction()


def get_collection():
    """Open (or create) the persistent Chroma collection."""
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedder,
        metadata={"hnsw:space": "cosine"},
    )


def index_all():
    """Embed every chunk and store it in Chroma. Safe to run again (upsert)."""
    chunks = build_chunks()
    collection = get_collection()
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[
            {"source": c["source"], "page": c["page"], "title": c["title"]}
            for c in chunks
        ],
    )
    return collection.count()


def query(question, top_k=3, min_score=0.5):
    """Return the closest chunks from Chroma. Score = 1 - cosine distance."""
    collection = get_collection()
    if collection.count() == 0:
        index_all()
    result = collection.query(query_texts=[question], n_results=top_k)

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