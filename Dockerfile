FROM python:3.11-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=120 PIP_RETRIES=5

COPY requirements.txt .

# CPU-only PyTorch: no CUDA libraries, smaller image and lower memory footprint.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt

# Bake model weights into the image so the first request is not a cold download.
RUN python -c "from sentence_transformers import SentenceTransformer as S; S('all-MiniLM-L6-v2'); \
from transformers import AutoTokenizer as T, AutoModelForSeq2SeqLM as M; \
T.from_pretrained('google/flan-t5-small'); M.from_pretrained('google/flan-t5-small')"

COPY app ./app
COPY data ./data
COPY static ./static

EXPOSE 8000

ENV PORT=8000 \
    MALLOC_ARENA_MAX=2 \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
