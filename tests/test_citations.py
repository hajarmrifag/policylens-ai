from app.services.citations import format_sources


def test_format_sources():
    results = [
        {
            "text": "Employees must use multi-factor authentication.",
            "score": 0.6816789305731367,
        }
    ]

    formatted = format_sources(results)

    assert formatted == [
        {
            "source_id": "source_1",
            "text": "Employees must use multi-factor authentication.",
            "relevance_score": 0.6817,
        }
    ]
