FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application assets
COPY backend ./backend
COPY ml/model.pkl ./ml/model.pkl
COPY frontend ./frontend

# Support dynamic PORT environment variable (defaults to 8000 for local/Render, or 7860 for Hugging Face)
ENV PORT=8000
EXPOSE 8000 7860

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
