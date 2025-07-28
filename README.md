# Main README.md (Repository Root)

# Adobe India Hackathon 2025 - Connecting the Dots

This repository contains solutions for both rounds of the Adobe India Hackathon.

## Round 1A: PDF Outline Extractor
Extracts structured outlines (Title, H1, H2, H3) from PDF documents using advanced text analysis.

## Round 1B: Persona-Driven Document Intelligence  
Intelligently extracts and ranks document sections based on user personas and their specific tasks.

### Team Adobe ke Cuties 
- Hitesh mehta
- Adtiya Pratap Singh
- Prashant Kaushik

### Repository Structure
```
├── round1a/          # PDF outline extraction solution
└── round1b/          # Document intelligence solution
```

---

# round1a/README.md

# Round 1A: PDF Outline Extractor

## Overview
This solution extracts hierarchical document structure from PDFs without relying solely on font sizes.

## Approach
1. **Multi-Modal Detection**: Combines font size, text patterns, positioning, and formatting
2. **Pattern Recognition**: Identifies numbered sections (1., 1.1, 1.1.1) and keyword patterns
3. **Statistical Analysis**: Determines body text size and identifies deviations
4. **Context Awareness**: Uses position, capitalization, and surrounding content

## Key Features
- Handles PDFs where font size alone is unreliable
- Supports multiple heading numbering schemes
- Extracts clean, hierarchical JSON output
- Processes 50-page PDFs in under 10 seconds

## Build and Run
```bash
# Build
docker build --platform linux/amd64 -t outline-extractor .

# Run
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none outline-extractor
```

## Dependencies
- PyMuPDF: Efficient PDF parsing
- NumPy: Statistical analysis

---

# round1b/README.md

# Round 1B: Persona-Driven Document Intelligence

## Overview
Extracts and ranks relevant document sections based on user personas and their specific job-to-be-done.

## Approach
1. **Semantic Understanding**: Uses sentence transformers for meaning-based matching
2. **Persona Modeling**: Combines role, expertise, and focus areas into embeddings
3. **Intelligent Ranking**: Weights job requirements (70%) and persona context (30%)
4. **Granular Analysis**: Extracts both sections and subsections for detailed insights

## Key Features
- Works across domains (research, finance, education)
- CPU-optimized with efficient transformer model
- Processes multiple documents in under 60 seconds
- Returns structured JSON with importance rankings

## Build and Run
```bash
# Build (includes model download)
docker build --platform linux/amd64 -t doc-intelligence .

# Run
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none doc-intelligence
```

## Input Format
Place `config.json` in input directory:
```json
{
  "documents": ["doc1.pdf", "doc2.pdf"],
  "persona": {
    "role": "Role Description",
    "expertise": "Domain Expertise",
    "focus_areas": "Specific Interests"
  },
  "job_to_be_done": "Specific task description"
}
```

## Dependencies
- PyMuPDF: PDF parsing
- Sentence-Transformers: Semantic embeddings
- Scikit-learn: Similarity calculations
- NLTK: Text processing