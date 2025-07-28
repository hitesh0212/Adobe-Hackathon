# Approach Explanation - Round 1B

## Overview
Our solution implements a persona-driven document intelligence system that extracts and ranks relevant sections from multiple PDFs based on a specific user persona and their job-to-be-done.

## Methodology

### 1. Document Structure Extraction
We parse each PDF to identify natural sections based on:
- Font size variations and bold text (potential headers)
- Numbered patterns (1., 1.1, etc.)
- Keyword indicators (Chapter, Section, Introduction)
- Page boundaries and content flow

### 2. Semantic Understanding
We use the `all-MiniLM-L6-v2` model from sentence-transformers, which:
- Provides high-quality embeddings in just 22MB
- Runs efficiently on CPU
- Captures semantic meaning for relevance matching

### 3. Relevance Calculation
Our ranking algorithm:
- Creates embeddings for persona description and job-to-be-done
- Combines them with 70% weight on job and 30% on persona
- Calculates cosine similarity with each section/subsection
- Ranks by relevance score

### 4. Subsection Analysis
For granular insights:
- Splits sections into meaningful paragraphs
- Generates concise summaries for each
- Independently ranks subsections for fine-grained relevance

### 5. Optimization Strategies
- Pre-download model during Docker build to avoid runtime delays
- Process documents in parallel where possible
- Limit output to top 15 sections and 20 subsections
- Use extractive summarization for speed

## Why This Approach Works
1. **Generic**: No domain-specific assumptions, works across research papers, financial reports, textbooks
2. **Fast**: Completes processing in under 60 seconds for multiple documents
3. **Accurate**: Semantic embeddings capture meaning beyond keyword matching
4. **Scalable**: Can handle varying document counts and complexity