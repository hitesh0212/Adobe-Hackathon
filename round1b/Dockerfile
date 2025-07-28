# Dockerfile for Round 1B
FROM --platform=linux/amd64 python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the model during build to avoid runtime download
RUN python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); model.save('/app/model')"

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt')"

# Copy the main script
COPY document_intelligence.py .

# Create directories
RUN mkdir -p /app/input /app/output

# Set environment variable to use pre-downloaded model
ENV SENTENCE_TRANSFORMERS_HOME=/app

# Run the script
CMD ["python", "document_intelligence.py"]

