def format_sources(results: list[dict]) -> list[dict]:
    return [
        {
            "source_id": f"source_{index + 1}",
            "text": result["text"],
            "relevance_score": round(result["score"], 4),
        }
        for index, result in enumerate(results)
    ]
