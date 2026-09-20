from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ask_endpoint_returns_answer_and_citations():
    response = client.post(
        "/ask",
        json={
            "question": "How should employees secure corporate accounts?"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "answer" in body
    assert "sources" in body
    assert body["sources"][0]["source_id"] == "source_1"
    assert "relevance_score" in body["sources"][0]
