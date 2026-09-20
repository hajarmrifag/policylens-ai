# PolicyLens AI

A grounded GenAI assistant for organisational documents with retrieval, citations, evaluation, and prompt-injection testing.

## What it does

- Loads PDF, Markdown, and text documents
- Splits documents into overlapping chunks
- Creates semantic embeddings with MiniLM
- Retrieves the most relevant evidence for a question
- Generates grounded answers with FLAN-T5
- Returns supporting source text and relevance scores
- Refuses unsupported questions using a relevance threshold
- Evaluates answer correctness, refusal behaviour, latency, and adversarial prompts

## Architecture

```text
Document
   ↓
Text extraction
   ↓
Chunking
   ↓
MiniLM embeddings
   ↓
Semantic retrieval
   ↓
Relevant context
   ↓
FLAN-T5
   ↓
Grounded answer + sources
```

## Evaluation

- 4 / 4 evaluation cases passed
- Unsupported questions are refused instead of answered from unrelated context
- Per-query latency is recorded automatically
- Average latency is calculated across the evaluation set

These results apply only to the included small evaluation set.

## Security evaluation

The project includes adversarial tests for:

- requests for administrator credentials
- attempts to reveal hidden instructions or secrets
- attempts to override the source policy with false information

Current result: **3 / 3 security cases passed**.

## API

- `GET /health` — health check
- `POST /query` — retrieve relevant document evidence
- `POST /ask` — generate a grounded answer with sources

Example request:

```json
{
  "question": "How should employees secure corporate accounts?"
}
```

## Tech stack

Python · FastAPI · Sentence Transformers · MiniLM · Hugging Face Transformers · FLAN-T5 · NumPy · PyPDF · Pytest · Docker · GitHub Actions

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Docker

```bash
docker build -t policylens-ai .
docker run --rm -p 8000:8000 policylens-ai
```

## Tests

```bash
python -m pytest -q
```

The current suite contains **11 automated tests**. GitHub Actions runs the suite on pushes and pull requests.

## Limitations

PolicyLens AI is a portfolio and evaluation prototype, not a production knowledge system. The evaluation dataset and adversarial test set are intentionally small, and the relevance threshold would need calibration on a larger corpus before production use.

## Author

**Hajar Mrifag**
Software Engineering student at Sichuan University
