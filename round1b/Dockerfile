FROM --platform=linux/amd64 python:3.9-slim

# Install required system packages
RUN apt-get update && apt-get install -y \
    libgomp1 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SentenceTransformer model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('/app/model')"

# Download NLTK punkt tokenizer model
RUN mkdir -p /usr/local/nltk_data && \
    python3 -m nltk.downloader -d /usr/local/nltk_data punkt

# Set environment variables for NLTK and SentenceTransformer
ENV NLTK_DATA=/usr/local/nltk_data
ENV SENTENCE_TRANSFORMERS_HOME=/app

# Copy code
COPY document_intelligence.py .

# Create input/output folders
RUN mkdir -p /app/input /app/output

# Run the app
CMD ["python", "document_intelligence.py"]
