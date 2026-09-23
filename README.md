# PolicyLens AI

A grounded GenAI assistant for organisational documents with retrieval, citations, evaluation, and prompt-injection testing.

## Social Impact & SDG Alignment

PolicyLens AI explores a broader question beyond technical performance: how can AI help people navigate complex institutional information without sacrificing accuracy, transparency, or trust?

The project is particularly connected to **UN Sustainable Development Goal 16: Peace, Justice and Strong Institutions**, including the importance of access to information and accountable institutions. Policies, regulations, organisational guidance, and other institutional documents can be difficult to navigate, especially when users must search through long or technical materials to find reliable answers.

PolicyLens experiments with a source-grounded approach. Rather than generating unrestricted responses, the system retrieves relevant evidence, returns supporting source text, and refuses questions when sufficient evidence is unavailable. It also includes adversarial testing against attempts to override its evidence policy or extract sensitive information.

### Current Evidence

* Source-grounded retrieval and answer generation
* Supporting evidence and relevance scores returned with responses
* Refusal mechanism for unsupported questions
* 4/4 included evaluation cases passed
* 3/3 included adversarial security cases passed
* 11 automated tests with CI through GitHub Actions

These results apply to a deliberately small prototype evaluation set and should not be interpreted as evidence of production-scale effectiveness.

### Next Direction

A future version of PolicyLens could explore multilingual and plain-language access to public-interest information, helping users understand complex policy or institutional documents while maintaining traceability to original sources.

This direction also supports **SDG 9: Industry, Innovation and Infrastructure** by exploring how responsible digital innovation can be designed around transparency, accessibility, and public value.


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
