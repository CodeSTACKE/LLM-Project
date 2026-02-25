# Multi-stage build: Ollama base + FastAPI app
FROM ollama/ollama:latest

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

# Copy app code
COPY backend/ .

# Expose ports: 8000 for FastAPI, 11434 for Ollama
EXPOSE 8000 11434

# Start both Ollama and FastAPI
CMD ollama serve & sleep 5 && uvicorn app:app --host 0.0.0.0 --port 8000
