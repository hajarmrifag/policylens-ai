import numpy as np
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.services.embeddings import embed_texts


MODEL_NAME = "google/flan-t5-small"
MIN_RELEVANCE = 0.35

_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_answer(question: str, context: str) -> str:
    question_embedding = np.array(embed_texts([question])[0])
    context_embedding = np.array(embed_texts([context])[0])

    relevance = float(context_embedding @ question_embedding)

    if relevance < MIN_RELEVANCE:
        return "I do not have enough information in the provided documents."

    prompt = (
        "Answer the question using only the provided context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    inputs = _tokenizer(prompt, return_tensors="pt")

    outputs = _model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=False,
    )

    return _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
