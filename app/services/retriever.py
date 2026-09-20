import numpy as np

from app.services.embeddings import embed_texts


def retrieve(query: str, chunks: list[str], top_k: int = 3) -> list[dict]:
    if not chunks:
        return []

    query_embedding = np.array(embed_texts([query])[0])
    chunk_embeddings = np.array(embed_texts(chunks))

    scores = chunk_embeddings @ query_embedding

    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {
            "text": chunks[index],
            "score": float(scores[index]),
        }
        for index in top_indices
    ]
