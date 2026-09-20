from app.services.benchmark import measure_generation_latency


def test_measure_generation_latency():
    result = measure_generation_latency(
        "How should employees secure corporate accounts?",
        "Employees must use multi-factor authentication for all corporate accounts.",
    )

    assert "answer" in result
    assert "latency_seconds" in result
    assert result["latency_seconds"] >= 0
