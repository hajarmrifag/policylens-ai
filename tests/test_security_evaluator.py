from app.services.security_evaluator import (
    run_security_evaluation,
    score_security_evaluation,
)


def test_security_evaluation_passes():
    results = run_security_evaluation()
    scored = score_security_evaluation(results)

    assert scored["security_pass_rate"] == 1.0
