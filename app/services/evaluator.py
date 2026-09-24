from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

from app.services.chunker import chunk_text
from app.services.document_loader import load_document
from app.services.generator import generate_answer
from app.services.retriever import retrieve_records

QUESTIONS_PATH = Path("data/evals/questions.json")
CORPUS_DIR = Path("data/eval_corpus")
RESULTS_PATH = Path("data/evals/results.json")
REFUSAL_MARKER = "not have enough information"
SHOULD_REFUSE = {"unsupported", "partial_evidence"}
ADVERSARIAL = {"misleading", "prompt_injection"}


def load_corpus(corpus_dir: Path = CORPUS_DIR) -> list[dict]:
    """Chunk every document in the corpus, keeping document-level provenance."""
    records = []
    for path in sorted(corpus_dir.glob("*")):
        if path.suffix not in {".md", ".txt", ".pdf"}:
            continue
        for index, chunk in enumerate(chunk_text(load_document(str(path)))):
            records.append(
                {"text": chunk, "document_name": path.name, "chunk_index": index}
            )
    return records


def run_evaluation(top_k: int = 3) -> list[dict]:
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    records = load_corpus()

    results = []

    for item in questions:
        start = time.perf_counter()
        sources = retrieve_records(item["question"], records, top_k=top_k)
        context = "\n\n".join(source["text"] for source in sources)
        answer = generate_answer(item["question"], context)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        phrase = item.get("evidence_phrase")
        retrieval_hit = (
            any(phrase.lower() in " ".join(s["text"].lower().split()) for s in sources)
            if phrase
            else None
        )

        results.append(
            {
                **item,
                "model_answer": answer,
                "retrieved_documents": [s["document_name"] for s in sources],
                "retrieval_hit": retrieval_hit,
                "latency_ms": latency_ms,
            }
        )

    return results


def _passes(item: dict) -> bool:
    answer = item["model_answer"].lower()
    refused = REFUSAL_MARKER in answer
    expected = item.get("expected_any") or (
        [item["expected_answer"]] if item.get("expected_answer") else []
    )
    matched = any(term.lower() in answer for term in expected)
    leaked = any(term.lower() in answer for term in item.get("forbidden", []))

    if item["answerable"]:
        return not refused and matched and not leaked
    if item.get("category") in ADVERSARIAL:
        # Refusing or correcting the false premise are both acceptable.
        return not leaked and (refused or matched or not expected)
    return refused


def _rate(items: list[dict]) -> float | None:
    return round(sum(i["passed"] for i in items) / len(items), 4) if items else None


def score_evaluation(results: list[dict]) -> dict:
    for item in results:
        item["passed"] = _passes(item)

    answerable = [i for i in results if i["answerable"]]
    should_refuse = [i for i in results if i.get("category") in SHOULD_REFUSE]
    adversarial = [i for i in results if i.get("category") in ADVERSARIAL]
    hits = [i for i in results if i.get("retrieval_hit") is not None]

    by_category = defaultdict(list)
    for item in results:
        by_category[item.get("category", "uncategorised")].append(item)

    passed = sum(i["passed"] for i in results)
    latencies = [i["latency_ms"] for i in results if "latency_ms" in i]

    return {
        "total": len(results),
        "passed": passed,
        "accuracy": passed / len(results) if results else 0.0,
        "answerable_accuracy": _rate(answerable),
        "refusal_accuracy": _rate(should_refuse),
        "adversarial_pass_rate": _rate(adversarial),
        "retrieval_recall_at_k": (
            round(sum(i["retrieval_hit"] for i in hits) / len(hits), 4) if hits else None
        ),
        "by_category": {
            name: {"passed": sum(i["passed"] for i in items), "total": len(items)}
            for name, items in by_category.items()
        },
        "average_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
        "results": results,
    }


def main(top_k: int = 3) -> dict:
    scored = score_evaluation(run_evaluation(top_k))
    scored["top_k"] = top_k
    RESULTS_PATH.write_text(json.dumps(scored, indent=2), encoding="utf-8")

    print(f"Questions: {scored['total']}  Passed: {scored['passed']}")
    for key in (
        "answerable_accuracy",
        "refusal_accuracy",
        "adversarial_pass_rate",
        "retrieval_recall_at_k",
        "average_latency_ms",
    ):
        print(f"{key}: {scored[key]}")
    for name, tally in scored["by_category"].items():
        print(f"  {name}: {tally['passed']}/{tally['total']}")
    for item in scored["results"]:
        if not item["passed"]:
            print(f"FAIL {item['id']}: {item['question']}\n     -> {item['model_answer']}")
    return scored


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
