import json
import time
from pathlib import Path

from app.services.chunker import chunk_text
from app.services.document_loader import load_document
from app.services.generator import generate_answer
from app.services.retriever import retrieve


def run_evaluation() -> list[dict]:
    questions = json.loads(
        Path("data/evals/questions.json").read_text(encoding="utf-8")
    )

    document = load_document("data/documents/security_policy.txt")
    chunks = chunk_text(document)

    results = []

    for item in questions:
        sources = retrieve(item["question"], chunks, top_k=3)
        context = "\n\n".join(source["text"] for source in sources)

        start = time.perf_counter()
        answer = generate_answer(item["question"], context)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        results.append(
            {
                "question": item["question"],
                "expected_answer": item["expected_answer"],
                "answerable": item["answerable"],
                "model_answer": answer,
                "latency_ms": latency_ms,
            }
        )

    return results


def score_evaluation(results: list[dict]) -> dict:
    correct = 0

    for item in results:
        answer = item["model_answer"].lower()

        if item["answerable"]:
            expected = item["expected_answer"].lower()
            passed = expected in answer
        else:
            passed = "not have enough information" in answer

        item["passed"] = passed

        if passed:
            correct += 1

    average_latency = (
        sum(item.get("latency_ms", 0.0) for item in results) / len(results)
        if results
        else 0.0
    )

    return {
        "total": len(results),
        "passed": correct,
        "accuracy": correct / len(results) if results else 0.0,
        "average_latency_ms": round(average_latency, 2),
        "results": results,
    }


def score_evaluation(results: list[dict]) -> dict:
    correct = 0

    for item in results:
        answer = item["model_answer"].lower()

        if item["answerable"]:
            expected = item["expected_answer"].lower()
            passed = expected in answer
        else:
            passed = "not have enough information" in answer

        item["passed"] = passed

        if passed:
            correct += 1

    average_latency = (
        sum(item.get("latency_ms", 0.0) for item in results) / len(results)
        if results
        else 0.0
    )

    return {
        "total": len(results),
        "passed": correct,
        "accuracy": correct / len(results) if results else 0.0,
        "average_latency_ms": round(average_latency, 2),
        "results": results,
    }
