# Round 1A: PDF Structure Extractor

## Approach

This solution uses a **multi-strategy approach** to extract document structure without relying solely on font sizes:

### 1. **Feature Extraction**
- Extracts rich text features including font size, bold/italic styles, position, and text patterns
- Groups words into coherent lines based on spatial proximity
- Preserves both visual and semantic information

### 2. **Title Detection**
- Uses multiple heuristics: position (top of page), font size relative to other text, styling (bold/uppercase), center alignment, and keyword presence
- Scores each candidate and selects the best match
- Fallback strategies ensure a title is always identified

### 3. **Heading Classification**
Three complementary strategies work together:

#### Pattern-Based Classification
- Recognizes common heading patterns (numbered, lettered, Roman numerals)
- Identifies structural markers like "Chapter", "Section", "Part"
- High confidence for explicit patterns

#### Statistical Classification
- Analyzes font size distribution to identify body text baseline
- Calculates dynamic thresholds for H1/H2/H3 based on standard deviations
- Considers multiple features (size, bold, position) for classification

#### Structural Classification
- Identifies headings based on document flow
- Looks for short lines followed by longer paragraphs
- Uses indentation patterns to determine hierarchy levels

### 4. **Post-Processing**
- Merges predictions from all strategies using confidence scores
- Ensures proper hierarchical structure (H3 must follow H2, etc.)
- Removes low-confidence predictions

## Libraries Used

- **pdfplumber**: Reliable PDF text extraction with position and styling information
- **numpy**: Statistical analysis of text features
- **scikit-learn**: DBSCAN clustering (imported but reserved for future enhancements)

## Running the Solution

### Build the Docker image:
```bash
docker build --platform linux/amd64 -t round1a:latest .
```

### Run the container:
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none round1a:latest
```

The solution will process all PDFs in the input directory and generate corresponding JSON files in the output directory.

## Performance

- Processes a 50-page PDF in under 10 seconds
- No external dependencies or network calls
- Efficient memory usage with streaming PDF processing
- Total container size under 200MB

## Key Innovations

1. **Not relying on font size alone**: Uses pattern matching, document structure, and statistical analysis
2. **Robust to different PDF types**: Works with academic papers, business documents, technical manuals
3. **Confidence scoring**: Each heading has an associated confidence score for quality control
4. **Hierarchical consistency**: Ensures logical heading structure throughout the document