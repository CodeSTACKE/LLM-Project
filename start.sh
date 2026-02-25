Bash
#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
sleep 5

# Start FastAPI
uvicorn app:app --host 0.0.0.0 --port 8000