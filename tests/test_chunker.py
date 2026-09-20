from app.services.chunker import chunk_text


def test_chunk_text_with_overlap():
    text = "A" * 1200

    chunks = chunk_text(text, chunk_size=500, overlap=100)

    assert len(chunks) == 3
    assert len(chunks[0]) == 500
    assert len(chunks[1]) == 500
    assert len(chunks[2]) == 400
