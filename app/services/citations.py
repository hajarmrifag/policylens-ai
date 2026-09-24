def format_sources(results: list[dict]) -> list[dict]:
    formatted = []

    for index, result in enumerate(results):
        citation = {
            "source_id": f"source_{index + 1}",
            "text": result["text"],
            "relevance_score": round(result["score"], 4),
        }

        for key in ("document_id", "document_name", "chunk_index"):
            if key in result:
                citation[key] = result[key]

        formatted.append(citation)

    return formatted
