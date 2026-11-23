from app.records import load_records

_records = None
_vectorizer = None
_matrix = None
_cosine_similarity = None


def _get_search_artifacts():
    """Lazily load scikit-learn and compute TF-IDF matrix only on first search request."""
    global _records, _vectorizer, _matrix, _cosine_similarity
    if _vectorizer is None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        _records = load_records()
        _texts = [f"{r['topic']} {r['summary']}" for r in _records]
        _vectorizer = TfidfVectorizer(stop_words="english")
        _matrix = _vectorizer.fit_transform(_texts)
        _cosine_similarity = cosine_similarity
    return _records, _vectorizer, _matrix, _cosine_similarity


def smart_search(query, top_k=3, min_score=0.1):
    """Rank records by TF-IDF cosine similarity to the query.

    Records scoring below min_score are dropped, so an unrelated
    question returns an empty list (the honest "I don't know").
    """
    if not query or not str(query).strip():
        return []

    records, vectorizer, matrix, cosine_sim = _get_search_artifacts()
    query_vector = vectorizer.transform([query])
    scores = cosine_sim(query_vector, matrix).ravel()
    ranked = sorted(zip(scores, records), key=lambda pair: pair[0], reverse=True)
    return [
        {**record, "score": round(float(score), 3)}
        for score, record in ranked[:top_k]
        if score >= min_score
    ]