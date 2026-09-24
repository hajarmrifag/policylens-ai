import json
from pathlib import Path

from app.services.evaluator import load_corpus, score_evaluation

CATEGORIES = {
    "supported",
    "unsupported",
    "misleading",
    "prompt_injection",
    "partial_evidence",
    "conflict",
}


def test_question_set_is_broad_and_well_formed():
    questions = json.loads(Path("data/evals/questions.json").read_text(encoding="utf-8"))

    assert len(questions) >= 25
    assert {q["category"] for q in questions} == CATEGORIES
    assert len({q["id"] for q in questions}) == len(questions)


def test_evidence_phrases_exist_in_corpus():
    corpus = " ".join(" ".join(r["text"].split()) for r in load_corpus()).lower()
    questions = json.loads(Path("data/evals/questions.json").read_text(encoding="utf-8"))

    for question in questions:
        phrase = question.get("evidence_phrase")
        if phrase:
            assert phrase.lower() in corpus, question["id"]


def test_corpus_contains_multiple_documents_with_a_superseded_version():
    names = {record["document_name"] for record in load_corpus()}

    assert len(names) >= 4
    assert "information_security_policy_2022_archive.md" in names


def test_score_evaluation_reports_per_metric_rates():
    refusal = "I do not have enough information in the provided documents."
    results = [
        {"id": "a", "category": "supported", "answerable": True,
         "expected_any": ["14"], "model_answer": "14 characters", "retrieval_hit": True},
        {"id": "b", "category": "conflict", "answerable": True,
         "expected_any": ["14"], "forbidden": ["10"], "model_answer": "10 characters",
         "retrieval_hit": True},
        {"id": "c", "category": "unsupported", "answerable": False, "model_answer": refusal},
        {"id": "d", "category": "partial_evidence", "answerable": False, "model_answer": "42"},
        {"id": "e", "category": "prompt_injection", "answerable": False,
         "forbidden": ["password is"], "model_answer": refusal},
    ]

    scored = score_evaluation(results)

    assert scored["answerable_accuracy"] == 0.5
    assert scored["refusal_accuracy"] == 0.5
    assert scored["adversarial_pass_rate"] == 1.0
    assert scored["retrieval_recall_at_k"] == 1.0
    assert scored["by_category"]["conflict"] == {"passed": 0, "total": 1}
