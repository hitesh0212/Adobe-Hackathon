#!/usr/bin/env python3
"""
PDF Outline Extractor for Adobe Hackathon Round 1A
Extracts title and hierarchical headings (H1, H2, H3) from PDFs
"""

import json
import os
import re
import sys
from typing import List, Dict, Tuple
import fitz  # PyMuPDF
from collections import defaultdict
import numpy as np

class PDFOutlineExtractor:
    def __init__(self):
        self.heading_patterns = {
            'numbered': [
                r'^\s*(\d+\.?)\s+(.+)$',  # 1. Introduction
                r'^\s*(\d+\.\d+\.?)\s+(.+)$',  # 1.1 Overview
                r'^\s*(\d+\.\d+\.\d+\.?)\s+(.+)$',  # 1.1.1 Details
                r'^\s*([A-Z]\.?)\s+(.+)$',  # A. Section
                r'^\s*([IVX]+\.?)\s+(.+)$',  # Roman numerals
            ],
            'keywords': [
                'introduction', 'conclusion', 'abstract', 'summary',
                'chapter', 'section', 'overview', 'background',
                'methodology', 'results', 'discussion', 'references'
            ]
        }
    
    def extract_text_with_formatting(self, page):
        """Extract text blocks with formatting information"""
        blocks = []
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    line_text = ""
                    line_info = {
                        "bbox": line["bbox"],
                        "spans": []
                    }
                    
                    for span in line["spans"]:
                        line_text += span["text"]
                        line_info["spans"].append({
                            "text": span["text"],
                            "font": span["font"],
                            "size": round(span["size"], 1),
                            "flags": span["flags"]
                        })
                    
                    if line_text.strip():
                        blocks.append({
                            "text": line_text.strip(),
                            "info": line_info,
                            "page": page.number + 1
                        })
        
        return blocks
    
    def calculate_font_statistics(self, blocks):
        """Calculate font size statistics for the document"""
        font_sizes = defaultdict(int)
        
        for block in blocks:
            for span in block["info"]["spans"]:
                size = span["size"]
                font_sizes[size] += len(span["text"])
        
        # Find the most common font size (likely body text)
        if font_sizes:
            body_size = max(font_sizes.items(), key=lambda x: x[1])[0]
            all_sizes = sorted(font_sizes.keys(), reverse=True)
            
            return {
                "body_size": body_size,
                "sizes": all_sizes,
                "size_distribution": dict(font_sizes)
            }
        
        return None
    
    def is_likely_heading(self, block, font_stats):
        """Determine if a text block is likely a heading"""
        text = block["text"]
        
        # Check if text is too long to be a heading
        if len(text) > 200:
            return False, 0
        
        # Check for numbered patterns
        for pattern in self.heading_patterns['numbered']:
            if re.match(pattern, text):
                # Determine level based on pattern
                if '.' not in pattern or pattern.count('\.') == 1:
                    level = 1
                elif pattern.count('\.') == 2:
                    level = 2
                else:
                    level = 3
                return True, level
        
        # Check font characteristics
        if font_stats and block["info"]["spans"]:
            main_span = max(block["info"]["spans"], key=lambda x: len(x["text"]))
            font_size = main_span["size"]
            is_bold = main_span["flags"] & 2**4  # Bold flag
            
            # Size-based detection with context
            if font_size > font_stats["body_size"] * 1.2 or is_bold:
                # Check for keyword indicators
                text_lower = text.lower()
                has_keyword = any(kw in text_lower for kw in self.heading_patterns['keywords'])
                
                # Determine level based on size
                if font_size > font_stats["body_size"] * 1.5:
                    level = 1
                elif font_size > font_stats["body_size"] * 1.3:
                    level = 2
                else:
                    level = 3
                
                # Additional checks
                if len(text.split()) <= 10:  # Short enough to be a heading
                    if has_keyword or is_bold or text.isupper():
                        return True, level
                    # Check if it's at the beginning of a line and capitalized
                    if text[0].isupper() and not text.endswith('.'):
                        return True, level
        
        return False, 0
    
    def extract_title(self, blocks, first_page_blocks):
        """Extract the document title from the first page"""
        if not first_page_blocks:
            return "Untitled Document"
        
        # Look for the largest text on the first page
        max_size = 0
        title_candidate = None
        
        for block in first_page_blocks[:10]:  # Check first 10 blocks
            if block["info"]["spans"]:
                main_span = max(block["info"]["spans"], key=lambda x: len(x["text"]))
                if main_span["size"] > max_size and len(block["text"]) < 150:
                    max_size = main_span["size"]
                    title_candidate = block["text"]
        
        return title_candidate or "Untitled Document"
    
    def process_pdf(self, pdf_path):
        """Main processing function"""
        try:
            doc = fitz.open(pdf_path)
            all_blocks = []
            
            # Extract all text blocks
            for page_num, page in enumerate(doc):
                blocks = self.extract_text_with_formatting(page)
                all_blocks.extend(blocks)
            
            # Calculate font statistics
            font_stats = self.calculate_font_statistics(all_blocks)
            
            # Extract title from first page
            first_page_blocks = [b for b in all_blocks if b["page"] == 1]
            title = self.extract_title(all_blocks, first_page_blocks)
            
            # Extract headings
            headings = []
            seen_headings = set()
            
            for block in all_blocks:
                is_heading, level = self.is_likely_heading(block, font_stats)
                
                if is_heading:
                    heading_text = block["text"]
                    # Clean heading text
                    heading_text = re.sub(r'^\s*[\d\.\-\•\*]+\s*', '', heading_text)
                    heading_text = heading_text.strip()
                    
                    # Avoid duplicates
                    if heading_text and heading_text not in seen_headings:
                        seen_headings.add(heading_text)
                        headings.append({
                            "level": f"H{level}",
                            "text": heading_text,
                            "page": block["page"]
                        })
            
            # Sort headings by page number
            headings.sort(key=lambda x: x["page"])
            
            doc.close()
            
            return {
                "title": title,
                "outline": headings
            }
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}", file=sys.stderr)
            return {
                "title": "Error Processing Document",
                "outline": []
            }
    
    def process_directory(self, input_dir="/app/input", output_dir="/app/output"):
        """Process all PDFs in the input directory"""
        os.makedirs(output_dir, exist_ok=True)
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, filename.replace('.pdf', '.json'))
                
                print(f"Processing {filename}...")
                result = self.process_pdf(pdf_path)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"Completed {filename}")

def main():
    extractor = PDFOutlineExtractor()
    
    # Check if running in Docker
    if os.path.exists("/app/input"):
        extractor.process_directory()
    else:
        # Local testing
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            result = extractor.process_pdf(pdf_path)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Usage: python extract_outline.py <pdf_path>")

if __name__ == "__main__":
    main()