from fastapi import FastAPI

app = FastAPI(
    title="PolicyLens AI",
    description="A grounded GenAI assistant for organisational documents.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "PolicyLens AI",
        "status": "running",
        "purpose": "Grounded document intelligence with evaluation and security testing",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}

from pydantic import BaseModel

from app.services.chunker import chunk_text
from app.services.document_loader import load_document
from app.services.retriever import retrieve


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query_documents(request: QueryRequest):
    text = load_document("data/documents/security_policy.txt")
    chunks = chunk_text(text)

    results = retrieve(request.question, chunks, top_k=3)

    return {
        "question": request.question,
        "sources": results,
    }

from app.services.generator import generate_answer
from app.services.citations import format_sources

@app.post("/ask")
def ask_documents(request: QueryRequest):
    text = load_document("data/documents/security_policy.txt")
    chunks = chunk_text(text)

    sources = retrieve(request.question, chunks, top_k=3)
    context = "\n\n".join(source["text"] for source in sources)

    answer = generate_answer(request.question, context)

    return {
        "question": request.question,
        "answer": answer,
        "sources": format_sources(sources),
    }
