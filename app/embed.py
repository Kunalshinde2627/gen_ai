import numpy as np
from chromadb.utils import embedding_functions

from app.chunking import build_chunks

_embedder = embedding_functions.DefaultEmbeddingFunction()
_chunks = None
_matrix = None


def embed_texts(texts):
    """Turn a list of texts into a 2D array of vectors (one row per text)."""
    return np.array(_embedder(texts), dtype=float)


def _load():
    """Embed every chunk once, and keep the vectors in memory."""
    global _chunks, _matrix
    if _chunks is None:
        _chunks = build_chunks()
        vectors = embed_texts([chunk["text"] for chunk in _chunks])
        _matrix = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    return _chunks, _matrix


def semantic_search(query, top_k=3, min_score=0.5):
    """Return the chunks closest in meaning to the query (cosine similarity)."""
    chunks, matrix = _load()
    query_vector = embed_texts([query])[0]
    query_vector = query_vector / np.linalg.norm(query_vector)
    scores = matrix @ query_vector
    best = np.argsort(scores)[::-1][:top_k]
    return [
        {**chunks[i], "score": round(float(scores[i]), 3)}
        for i in best
        if scores[i] >= min_score
    ]