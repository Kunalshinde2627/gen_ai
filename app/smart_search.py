from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.records import load_records

_records = load_records()
_texts = [f"{r['topic']} {r['summary']}" for r in _records]

_vectorizer = TfidfVectorizer(stop_words="english")
_matrix = _vectorizer.fit_transform(_texts)


def smart_search(query, top_k=3, min_score=0.1):
    """Rank records by TF-IDF cosine similarity to the query.

    Records scoring below min_score are dropped, so an unrelated
    question returns an empty list (the honest "I don't know").
    """
    query_vector = _vectorizer.transform([query])
    scores = cosine_similarity(query_vector, _matrix).ravel()
    ranked = sorted(zip(scores, _records), key=lambda pair: pair[0], reverse=True)
    return [
        {**record, "score": round(float(score), 3)}
        for score, record in ranked[:top_k]
        if score >= min_score
    ]