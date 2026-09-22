FROM python:3.11-slim

WORKDIR /app

# System deps for curl (healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# ── Step 1: Install CPU-only PyTorch (prevents 3GB download) ──
RUN pip install --no-cache-dir \
    torch==2.2.2 \
    --index-url https://download.pytorch.org/whl/cpu

# ── Step 2: Install remaining Python dependencies ─────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Step 3: Copy application source ───────────────────────────
COPY app/ ./app/
COPY workers/ ./workers/

# Ensure the root directory is in the python path
ENV PYTHONPATH=/app

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
