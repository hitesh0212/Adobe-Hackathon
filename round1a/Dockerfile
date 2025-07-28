# Dockerfile for Round 1A
FROM --platform=linux/amd64 python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the extraction script
COPY extract_outline.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set the entrypoint
CMD ["python", "extract_outline.py"]
