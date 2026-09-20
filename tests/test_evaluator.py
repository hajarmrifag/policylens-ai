from app.services.evaluator import score_evaluation


def test_score_evaluation():
    results = [
        {
            "question": "Q1",
            "expected_answer": "multi-factor authentication",
            "answerable": True,
            "model_answer": "Multi-factor authentication",
        },
        {
            "question": "Q2",
            "expected_answer": None,
            "answerable": False,
            "model_answer": "I do not have enough information in the provided documents.",
        },
    ]

    scored = score_evaluation(results)

    assert scored["total"] == 2
    assert scored["passed"] == 2
    assert scored["accuracy"] == 1.0
