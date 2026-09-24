from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load the embedding model on first use, preferring the local cache."""
    try:
        return SentenceTransformer(MODEL_NAME, local_files_only=True)
    except OSError:
        return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = get_model().encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
