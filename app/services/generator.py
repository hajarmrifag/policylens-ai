from functools import lru_cache

import numpy as np
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.services.embeddings import embed_texts


MODEL_NAME = "google/flan-t5-small"
MIN_RELEVANCE = 0.35

@lru_cache(maxsize=1)
def get_model_components():
    """Load generation assets only when an answer is requested."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, local_files_only=True)
    except OSError:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    return tokenizer, model


REFUSAL = "I do not have enough information in the provided documents."


# The yes/no margin is poorly calibrated on very short contexts (a clean
# single-sentence answer scores about -0.6), so the gate only vetoes on a clearly
# negative signal. Chosen from margins observed on the evaluation questions, so
# treat reported refusal accuracy as calibrated on that set, not held out.
ANSWERABILITY_FLOOR = -0.7


def answerability_margin(question: str, context: str) -> float:
    """Logit(yes) - logit(no) for "does the context contain the needed fact?".

    The embedding gate only measures topical similarity, so questions that stay
    inside the policy domain but ask for a detail no document contains pass it.
    This second signal looks at the content of the evidence rather than its topic.
    """
    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Does the context contain the specific information needed to answer "
        "the question? Answer yes or no."
    )
    tokenizer, model = get_model_components()
    inputs = tokenizer(prompt, return_tensors="pt")
    start = torch.tensor([[model.config.decoder_start_token_id]])
    with torch.inference_mode():
        logits = model(**inputs, decoder_input_ids=start).logits[0, -1]
    yes_id, no_id = tokenizer("yes").input_ids[0], tokenizer("no").input_ids[0]
    return float(logits[yes_id] - logits[no_id])


def generate_answer(question: str, context: str) -> str:
    question_embedding = np.array(embed_texts([question])[0])
    context_embedding = np.array(embed_texts([context])[0])

    relevance = float(context_embedding @ question_embedding)

    if relevance < MIN_RELEVANCE or answerability_margin(question, context) < ANSWERABILITY_FLOOR:
        return REFUSAL

    prompt = (
        "Answer the question using only the provided context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    tokenizer, model = get_model_components()
    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=False,
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
