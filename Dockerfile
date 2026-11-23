
FROM python:3.13-slim

WORKDIR /app

# Limit memory and concurrency overhead on low-memory environments (Render Free 512MB)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    ONNXRUNTIME_INTRA_OP_NUM_THREADS=1 \
    ONNXRUNTIME_INTER_OP_NUM_THREADS=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-build vector store and download embedding model during build time
RUN python -m app.vectorstore

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
