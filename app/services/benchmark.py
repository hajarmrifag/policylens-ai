import time

from app.services.generator import generate_answer


def measure_generation_latency(question: str, context: str) -> dict:
    start = time.perf_counter()

    answer = generate_answer(question, context)

    elapsed = time.perf_counter() - start

    return {
        "answer": answer,
        "latency_seconds": round(elapsed, 3),
    }
