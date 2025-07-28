#!/usr/bin/env python3
"""
Persona-Driven Document Intelligence for Adobe Hackathon Round 1B
Extracts and ranks relevant sections based on persona and job-to-be-done
"""
import os
os.environ['NLTK_DATA'] = '/usr/local/nltk_data'

import nltk
from nltk.tokenize import sent_tokenize

nltk.data.path.append("/usr/local/nltk_data")



import json
import re
import sys
from datetime import datetime
from typing import List, Dict, Tuple
import fitz  # PyMuPDF
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

class DocumentIntelligence:
    def __init__(self):
        # Use a small, efficient model that fits within constraints
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def extract_document_structure(self, pdf_path):
        """Extract structured content from PDF"""
        doc = fitz.open(pdf_path)
        sections = []
        current_section = None
        
        for page_num, page in enumerate(doc):
            text_dict = page.get_text("dict")
            page_sections = []
            
            for block in text_dict["blocks"]:
                if block["type"] == 0:  # Text block
                    block_text = ""
                    block_info = {
                        "bbox": block["bbox"],
                        "page": page_num + 1,
                        "font_sizes": [],
                        "is_bold": False
                    }
                    
                    for line in block["lines"]:
                        for span in line["spans"]:
                            block_text += span["text"]
                            block_info["font_sizes"].append(span["size"])
                            if span["flags"] & 2**4:  # Bold
                                block_info["is_bold"] = True
                    
                    block_text = block_text.strip()
                    if block_text:
                        # Determine if this is a section header
                        avg_font_size = np.mean(block_info["font_sizes"]) if block_info["font_sizes"] else 0
                        is_header = (
                            (avg_font_size > 12 and len(block_text) < 100) or
                            block_info["is_bold"] or
                            re.match(r'^\d+\.?\s+\w+', block_text) or
                            any(kw in block_text.lower() for kw in ['chapter', 'section', 'introduction', 'conclusion'])
                        )
                        
                        if is_header and len(block_text.split()) < 15:
                            if current_section:
                                sections.append(current_section)
                            current_section = {
                                "title": block_text,
                                "page": block_info["page"],
                                "content": "",
                                "subsections": []
                            }
                        else:
                            if current_section:
                                current_section["content"] += " " + block_text
                            else:
                                # Create a default section if none exists
                                current_section = {
                                    "title": f"Page {block_info['page']}",
                                    "page": block_info["page"],
                                    "content": block_text,
                                    "subsections": []
                                }
        
        if current_section:
            sections.append(current_section)
        
        doc.close()
        
        # Extract subsections from content
        for section in sections:
            section["subsections"] = self.extract_subsections(section["content"])
        
        return sections
    
    def extract_subsections(self, content):
        """Extract meaningful subsections from section content"""
        sentences = sent_tokenize(content)
        subsections = []
        
        # Group sentences into paragraphs
        current_para = []
        for sent in sentences:
            current_para.append(sent)
            # Start new paragraph after certain conditions
            if len(current_para) >= 3 or sent.endswith(':') or len(' '.join(current_para)) > 200:
                if current_para:
                    para_text = ' '.join(current_para)
                    if len(para_text.split()) > 10:  # Meaningful content
                        subsections.append({
                            "text": para_text,
                            "summary": self.generate_summary(para_text)
                        })
                current_para = []
        
        # Add remaining paragraph
        if current_para:
            para_text = ' '.join(current_para)
            if len(para_text.split()) > 10:
                subsections.append({
                    "text": para_text,
                    "summary": self.generate_summary(para_text)
                })
        
        return subsections
    
    def generate_summary(self, text):
        """Generate a concise summary of the text"""
        words = text.split()
        if len(words) <= 30:
            return text
        
        # Simple extractive summary - take first and key sentences
        sentences = sent_tokenize(text)
        if len(sentences) <= 2:
            return text
        
        # Return first sentence + most important middle sentence
        return sentences[0]
    
    def calculate_relevance(self, section_embedding, query_embedding, persona_embedding):
        """Calculate relevance score for a section"""
        # Combine query and persona embeddings with weights
        combined_embedding = 0.7 * query_embedding + 0.3 * persona_embedding
        
        # Calculate cosine similarity
        similarity = cosine_similarity([section_embedding], [combined_embedding])[0][0]
        
        return similarity
    
    def process_documents(self, config):
        """Main processing function"""
        documents = config["documents"]
        persona = config["persona"]
        job_to_be_done = config["job_to_be_done"]
        
        # Create embeddings for persona and job
        persona_text = f"{persona}"
        persona_embedding = self.model.encode(persona_text)
        job_embedding = self.model.encode(job_to_be_done)
        
        all_sections = []
        all_subsections = []
        
        # Process each document
        for doc_path in documents:
            doc_name = os.path.basename(doc_path)
            sections = self.extract_document_structure(doc_path)
            
            # Process sections
            for section in sections:
                # Create section embedding
                section_text = f"{section['title']} {section['content'][:500]}"
                section_embedding = self.model.encode(section_text)
                
                # Calculate relevance
                relevance = self.calculate_relevance(
                    section_embedding, job_embedding, persona_embedding
                )
                
                all_sections.append({
                    "document": doc_name,
                    "page": section["page"],
                    "title": section["title"],
                    "relevance": float(relevance),
                    "content_preview": section["content"][:200] + "..." if len(section["content"]) > 200 else section["content"]
                })
                
                # Process subsections
                for idx, subsection in enumerate(section["subsections"]):
                    subsection_embedding = self.model.encode(subsection["summary"])
                    sub_relevance = self.calculate_relevance(
                        subsection_embedding, job_embedding, persona_embedding
                    )
                    
                    all_subsections.append({
                        "document": doc_name,
                        "section_title": section["title"],
                        "page": section["page"],
                        "subsection_idx": idx,
                        "refined_text": subsection["summary"],
                        "relevance": float(sub_relevance)
                    })
        
        # Sort by relevance and assign importance ranks
        all_sections.sort(key=lambda x: x["relevance"], reverse=True)
        all_subsections.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Assign importance ranks
        for idx, section in enumerate(all_sections):
            section["importance_rank"] = idx + 1
            del section["relevance"]  # Remove internal score
        
        for idx, subsection in enumerate(all_subsections):
            subsection["importance_rank"] = idx + 1
            del subsection["relevance"]
        
        # Keep top relevant items
        top_sections = all_sections[:15]  # Top 15 sections
        top_subsections = all_subsections[:20]  # Top 20 subsections
        
        return {
            "metadata": {
                "input_documents": [os.path.basename(doc) for doc in documents],
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": top_sections,
            "subsection_analysis": top_subsections
        }
    
    def run(self, input_dir="/app/input", output_dir="/app/output"):
        """Run the document intelligence system"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Read configuration
        config_path = os.path.join(input_dir, "config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update document paths
        config["documents"] = [
            os.path.join(input_dir, doc) for doc in config["documents"]
        ]
        
        # Process documents
        self.logger.info("Processing documents...")
        result = self.process_documents(config)
        
        # Save output
        output_path = os.path.join(output_dir, "output.json")
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        self.logger.info(f"Output saved to {output_path}")

def main():
    intelligence = DocumentIntelligence()
    
    if os.path.exists("/app/input"):
        intelligence.run()
    else:
        # Local testing
        if len(sys.argv) > 1:
            config_path = sys.argv[1]
            with open(config_path, 'r') as f:
                config = json.load(f)
            result = intelligence.process_documents(config)
            print(json.dumps(result, indent=2))
        else:
            print("Usage: python document_intelligence.py <config.json>")

if __name__ == "__main__":
    main()