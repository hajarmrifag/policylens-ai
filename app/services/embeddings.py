from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

try:
    _model = SentenceTransformer(MODEL_NAME, local_files_only=True)
except OSError:
    _model = SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = _model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
