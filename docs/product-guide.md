# Product, API and deployment guide

[Back to the project](../README.md)

Commands below run from the repository root.


- Polished responsive web workspace at `/`
- Drag-and-drop multi-document ingestion with an 8 MB safety limit
- Cross-document semantic retrieval with document and chunk provenance
- Grounded/refused status, top-match confidence, and query latency
- Ephemeral in-memory uploads: no user documents are written to disk
- Interactive OpenAPI documentation at `/docs`

## Social Impact & SDG Alignment

PolicyLens AI explores a broader question beyond technical performance: how can AI help people navigate complex institutional information without sacrificing accuracy, transparency, or trust?

The project is particularly connected to **UN Sustainable Development Goal 16: Peace, Justice and Strong Institutions**, including the importance of access to information and accountable institutions. Policies, regulations, organisational guidance, and other institutional documents can be difficult to navigate, especially when users must search through long or technical materials to find reliable answers.

PolicyLens experiments with a source-grounded approach. Rather than generating unrestricted responses, the system retrieves relevant evidence, returns supporting source text, and refuses questions when sufficient evidence is unavailable. It also includes adversarial testing against attempts to override its evidence policy or extract sensitive information.

### Current Evidence

* Source-grounded retrieval and answer generation
* Supporting evidence and relevance scores returned with responses
* Refusal mechanism for unsupported questions
* 31-question evaluation across six categories (see [Evaluation](evaluation.md)), reported with its failures
* Retrieval Recall@3 of 100% on the evidence-bearing questions, and 6/6 clearly unsupported questions refused
* 3/3 original prompt-injection security cases passed, plus 4 injection and 4 misleading-premise cases in the larger set
* 18 automated tests with CI through GitHub Actions

The evaluation corpus is four short synthetic policy documents, so these numbers describe a controlled benchmark, not production-scale effectiveness.

### Next Direction

A future version of PolicyLens could explore multilingual and plain-language access to public-interest information, helping users understand complex policy or institutional documents while maintaining traceability to original sources.

This direction also supports **SDG 9: Industry, Innovation and Infrastructure** by exploring how responsible digital innovation can be designed around transparency, accessibility, and public value.


## What it does

- Loads PDF, Markdown, and text documents
- Accepts multiple documents through the browser or API
- Splits documents into overlapping chunks
- Creates semantic embeddings with MiniLM
- Retrieves the most relevant evidence across the selected corpus
- Generates grounded answers with FLAN-T5
- Returns source document, chunk, supporting text, and relevance score
- Refuses unsupported questions using a relevance threshold
- Evaluates answer correctness, refusal behaviour, latency, and adversarial prompts

## Architecture

```text
Documents
   ↓
Text extraction
   ↓
Chunking
   ↓
MiniLM embeddings
   ↓
Cross-document semantic retrieval
   ↓
Relevant context
   ↓
FLAN-T5
   ↓
Grounded answer + confidence + provenance
```

## API

- `GET /health` :  health check
- `GET /documents` :  list documents in the evidence library
- `POST /documents` :  upload a PDF, Markdown, or text document
- `POST /query` :  retrieve relevant evidence with provenance
- `POST /ask` :  generate a grounded answer with sources

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

Open `http://127.0.0.1:8000` for the product or `/docs` for the API.

## Docker

```bash
docker build -t policylens-ai .
docker run --rm -p 8000:8000 policylens-ai
```

## Deploy on Render

`render.yaml` defines a Docker web service with a `/health` check. Model weights are downloaded at image build time, and the container binds to Render's `$PORT`.

1. In Render, choose **New > Blueprint** and select this repository.
2. The Free plan is enough: the image uses CPU-only PyTorch and is tuned to stay under 512 MB. Free instances spin down after inactivity, so the first request can take about a minute.
3. Once the deploy is healthy, open the service URL for the workspace or `/docs` for the API.

## Tests

```bash
python -m pytest -q
```

The suite covers retrieval, generation, citations, refusal behaviour, prompt injection, API health, document ingestion, and upload validation. GitHub Actions runs it on pushes and pull requests.

## Limitations

PolicyLens AI is a portfolio and evaluation prototype, not a production knowledge system. The evaluation corpus is synthetic and small (31 questions, 4 documents), the document registry is in-memory, and the relevance threshold would need calibration on a larger corpus before production use.

## Author

**Hajar Mrifag**
Software Engineering student at Sichuan University
