from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_document_library_includes_demo_policy():
    response = client.get("/documents")
    assert response.status_code == 200
    assert any(document["name"] == "security_policy.txt" for document in response.json()["documents"])


def test_upload_text_document_adds_it_to_library():
    response = client.post(
        "/documents",
        files={"file": ("leave-policy.txt", BytesIO(b"Employees receive 25 days of leave."), "text/plain")},
    )
    assert response.status_code == 201
    document = response.json()["document"]
    assert document["name"] == "leave-policy.txt"
    assert document["chunks"] == 1


def test_upload_rejects_unsupported_file_type():
    response = client.post(
        "/documents",
        files={"file": ("policy.exe", BytesIO(b"not a policy"), "application/octet-stream")},
    )
    assert response.status_code == 415
