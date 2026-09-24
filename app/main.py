from __future__ import annotations

import hashlib
import time
from pathlib import Path
from threading import RLock
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.services.chunker import chunk_text
from app.services.citations import format_sources
from app.services.document_loader import load_document, load_document_bytes
from app.services.generator import MIN_RELEVANCE, generate_answer
from app.services.retriever import retrieve, retrieve_records


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DEFAULT_DOCUMENT = BASE_DIR / "data" / "documents" / "security_policy.txt"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    document_ids: Optional[List[str]] = None


class DocumentRegistry:
    """Small, thread-safe in-memory corpus for the interactive demo."""

    def __init__(self) -> None:
        self._documents: dict[str, dict] = {}
        self._lock = RLock()

    def add(self, name: str, text: str, *, is_demo: bool = False) -> dict:
        normalized = " ".join(text.split())
        if not normalized:
            raise ValueError("The document does not contain readable text.")

        digest = hashlib.sha256(f"{name}\n{normalized}".encode()).hexdigest()[:12]
        chunks = chunk_text(normalized)
        document = {
            "id": digest,
            "name": Path(name).name,
            "characters": len(normalized),
            "chunks": chunks,
            "is_demo": is_demo,
        }
        with self._lock:
            self._documents[digest] = document
        return self.metadata(document)

    def list(self) -> list[dict]:
        with self._lock:
            return [self.metadata(document) for document in self._documents.values()]

    def records(self, document_ids: Optional[List[str]] = None) -> list[dict]:
        with self._lock:
            selected = list(self._documents.values())
            if document_ids:
                wanted = set(document_ids)
                selected = [document for document in selected if document["id"] in wanted]

            return [
                {
                    "text": chunk,
                    "document_id": document["id"],
                    "document_name": document["name"],
                    "chunk_index": index,
                }
                for document in selected
                for index, chunk in enumerate(document["chunks"])
            ]

    @staticmethod
    def metadata(document: dict) -> dict:
        return {
            "id": document["id"],
            "name": document["name"],
            "characters": document["characters"],
            "chunks": len(document["chunks"]),
            "is_demo": document["is_demo"],
        }


registry = DocumentRegistry()
registry.add(DEFAULT_DOCUMENT.name, load_document(str(DEFAULT_DOCUMENT)), is_demo=True)

app = FastAPI(
    title="PolicyLens AI",
    description="Evidence-first document intelligence with inspectable citations.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def product_ui():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/documents")
def list_documents():
    return {"documents": registry.list()}


@app.post("/documents", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    safe_name = Path(file.filename or "document").name
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, "Upload a PDF, Markdown, or text document.")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Document exceeds the 8 MB upload limit.")

    try:
        text = load_document_bytes(safe_name, content)
        document = registry.add(safe_name, text)
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc

    return {"document": document}


@app.post("/query")
def query_documents(request: QueryRequest):
    records = registry.records(request.document_ids)
    if not records:
        raise HTTPException(404, "No matching documents are available.")

    return {
        "question": request.question,
        "sources": format_sources(retrieve_records(request.question, records, top_k=3)),
    }


@app.post("/ask")
def ask_documents(request: QueryRequest):
    started_at = time.perf_counter()
    records = registry.records(request.document_ids)
    if not records:
        raise HTTPException(404, "No matching documents are available.")

    sources = retrieve_records(request.question, records, top_k=3)
    context = "\n\n".join(source["text"] for source in sources)
    answer = generate_answer(request.question, context)
    confidence = max((source["score"] for source in sources), default=0.0)
    refused = confidence < MIN_RELEVANCE or answer.startswith("I do not have enough")

    return {
        "question": request.question,
        "answer": answer,
        "status": "insufficient_evidence" if refused else "grounded",
        "confidence": round(confidence, 4),
        "latency_ms": round((time.perf_counter() - started_at) * 1000),
        "sources": format_sources(sources),
    }


# Compatibility hook for users of the original single-document prototype.
def query_default_document(question: str) -> list[dict]:
    text = load_document(str(DEFAULT_DOCUMENT))
    return retrieve(question, chunk_text(text), top_k=3)
