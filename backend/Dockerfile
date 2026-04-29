# backend/Dockerfile
FROM python:3.10-slim

# Create a non-root user (required by Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies for OpenCV (run as root temporarily)
USER root
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
USER user

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY --chown=user . .

# Pre-download DeepFace weights during build so the server starts fast
RUN python -c "from deepface import DeepFace; import numpy as np; DeepFace.analyze(np.zeros((48, 48, 3), dtype=np.uint8), actions=['emotion'], enforce_detection=False)"

# Hugging Face Spaces exposes port 7860 by default
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
