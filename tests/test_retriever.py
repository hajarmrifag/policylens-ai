from app.services.retriever import retrieve


def test_retrieve_returns_relevant_chunk():
    chunks = [
        "Employees must use multi-factor authentication for all corporate accounts.",
        "Annual leave requests should be submitted to the line manager.",
        "Office equipment must be returned when employment ends.",
    ]

    results = retrieve(
        "How should employees secure corporate accounts?",
        chunks,
        top_k=1,
    )

    assert len(results) == 1
    assert "multi-factor authentication" in results[0]["text"].lower()
