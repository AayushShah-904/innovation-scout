# --- Backend Dockerfile (FastAPI) ---
# Render will use this to build and run the Python backend

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the fastembed ONNX model during build
# so the first request isn't slow on Render's cold start
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"

# Copy the entire project source code
COPY . .

# Render dynamically assigns a PORT environment variable — we must use it
# Default to 8000 for local Docker runs
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
