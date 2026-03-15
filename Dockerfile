FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
# Install dependencies only (not the package itself) for layer caching
RUN pip install --no-cache-dir $(python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    deps = tomllib.load(f)['project']['dependencies']
for d in deps:
    print(d)
")

# Pre-download the sentence-transformers model into the image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# --- runtime stage ---
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages and cached model from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface

# Copy application code
COPY skhand/ skhand/
COPY data/knowledge/ data/knowledge/
COPY pyproject.toml .

EXPOSE 8080

CMD ["uvicorn", "skhand.web.app:app", "--host", "0.0.0.0", "--port", "8080"]
