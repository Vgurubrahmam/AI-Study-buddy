"""
PDF Processor
Extracts text from PDF files and generates training data for fine-tuning
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
import json

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

from app.config import settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Processes PDF files for training data extraction and RAG indexing.
    Supports multiple PDF libraries with fallback.
    """
    
    def __init__(self, pdf_dir: Optional[str] = None):
        self.pdf_dir = pdf_dir or settings.study_pdfs_dir
        self.output_dir = settings.training_data_dir
        
        # Ensure directories exist
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        text = ""
        
        # Try pdfplumber first (better formatting)
        if pdfplumber:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                return text.strip()
            except Exception as e:
                logger.warning(f"pdfplumber failed for {pdf_path}: {e}")
        
        # Fallback to PyPDF2
        if PdfReader:
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                return text.strip()
            except Exception as e:
                logger.warning(f"PyPDF2 failed for {pdf_path}: {e}")
        
        raise RuntimeError(f"No PDF library available or extraction failed for {pdf_path}")
    
    def extract_sections(self, text: str) -> List[Dict]:
        """
        Extract sections/chapters from text based on common patterns.
        
        Args:
            text: Full text content
            
        Returns:
            List of section dictionaries with title and content
        """
        sections = []
        
        # Common section patterns
        patterns = [
            r'(?:^|\n)(Chapter\s+\d+[:\s]+[^\n]+)',
            r'(?:^|\n)(Section\s+\d+(?:\.\d+)?[:\s]+[^\n]+)',
            r'(?:^|\n)(\d+\.\s+[A-Z][^\n]+)',
            r'(?:^|\n)([A-Z][A-Z\s]+)(?=\n)',  # ALL CAPS headers
        ]
        
        # Find all potential headers
        headers = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                headers.append((match.start(), match.group(1).strip()))
        
        # Sort by position
        headers.sort(key=lambda x: x[0])
        
        # Extract content between headers
        for i, (pos, title) in enumerate(headers):
            start = pos
            end = headers[i + 1][0] if i + 1 < len(headers) else len(text)
            
            content = text[start:end].strip()
            # Remove the title from content
            content = content[len(title):].strip()
            
            if content and len(content) > 100:  # Only keep substantial sections
                sections.append({
                    "title": title,
                    "content": content
                })
        
        # If no sections found, treat whole text as one section
        if not sections and text:
            sections.append({
                "title": "Document",
                "content": text
            })
        
        return sections
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[str]:
        """
        Split text into overlapping chunks for embedding.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end near chunk boundary
                for sep in ['. ', '.\n', '! ', '? ']:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep > start + chunk_size // 2:
                        end = last_sep + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def generate_qa_pairs(
        self,
        text: str,
        section_title: str = ""
    ) -> List[Dict]:
        """
        Generate question-answer pairs from text content.
        Uses heuristics to create educational Q&A pairs.
        
        Args:
            text: Text content to generate Q&A from
            section_title: Optional section title for context
            
        Returns:
            List of Q&A pair dictionaries
        """
        qa_pairs = []
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 50]
        
        for para in paragraphs:
            # Skip if too short or looks like a list
            if len(para) < 100 or para.count('\n') > 5:
                continue
            
            # Generate different question types
            
            # 1. Explanation question
            first_sentence = para.split('.')[0] + '.'
            if len(first_sentence) > 20:
                # Extract key concept (first noun phrase or technical term)
                words = first_sentence.split()
                if len(words) > 3:
                    concept = ' '.join(words[:5]).rstrip('.,')
                    qa_pairs.append({
                        "instruction": f"Explain {concept}",
                        "context": section_title,
                        "response": para
                    })
            
            # 2. What is question
            definitions = re.findall(r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s+(?:is|are|refers to|means)', para)
            for term in definitions[:2]:  # Limit to 2 per paragraph
                qa_pairs.append({
                    "instruction": f"What is {term}?",
                    "context": section_title,
                    "response": para
                })
            
            # 3. How does question (for process descriptions)
            if any(word in para.lower() for word in ['process', 'method', 'algorithm', 'technique', 'step']):
                qa_pairs.append({
                    "instruction": f"How does this work? {first_sentence}",
                    "context": section_title,
                    "response": para
                })
        
        return qa_pairs
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Process a single PDF file completely.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted data
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        filename = os.path.basename(pdf_path)
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        logger.info(f"Extracted {len(text)} characters from {filename}")
        
        # Extract sections
        sections = self.extract_sections(text)
        logger.info(f"Found {len(sections)} sections")
        
        # Generate chunks for RAG
        chunks = []
        for section in sections:
            section_chunks = self.chunk_text(section["content"])
            for chunk in section_chunks:
                chunks.append({
                    "text": chunk,
                    "source": filename,
                    "section": section["title"]
                })
        logger.info(f"Generated {len(chunks)} chunks for RAG")
        
        # Generate Q&A pairs for fine-tuning
        qa_pairs = []
        for section in sections:
            pairs = self.generate_qa_pairs(section["content"], section["title"])
            qa_pairs.extend(pairs)
        logger.info(f"Generated {len(qa_pairs)} Q&A pairs")
        
        return {
            "filename": filename,
            "text_length": len(text),
            "sections": len(sections),
            "chunks": chunks,
            "qa_pairs": qa_pairs
        }
    
    def process_all_pdfs(self) -> Dict:
        """
        Process all PDF files in the study_pdfs directory.
        
        Returns:
            Summary of processing results
        """
        pdf_files = list(Path(self.pdf_dir).glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.pdf_dir}")
            return {
                "status": "no_files",
                "pdf_dir": self.pdf_dir,
                "files_processed": 0
            }
        
        all_chunks = []
        all_qa_pairs = []
        results = []
        
        for pdf_path in pdf_files:
            try:
                result = self.process_pdf(str(pdf_path))
                all_chunks.extend(result["chunks"])
                all_qa_pairs.extend(result["qa_pairs"])
                results.append({
                    "file": result["filename"],
                    "status": "success",
                    "chunks": len(result["chunks"]),
                    "qa_pairs": len(result["qa_pairs"])
                })
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {e}")
                results.append({
                    "file": str(pdf_path.name),
                    "status": "failed",
                    "error": str(e)
                })
        
        # Save training data
        training_data_path = os.path.join(self.output_dir, "training_data.json")
        with open(training_data_path, 'w', encoding='utf-8') as f:
            json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(all_qa_pairs)} Q&A pairs to {training_data_path}")
        
        # Save chunks for RAG
        chunks_path = os.path.join(self.output_dir, "rag_chunks.json")
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(all_chunks)} chunks to {chunks_path}")
        
        return {
            "status": "completed",
            "files_processed": len(pdf_files),
            "total_chunks": len(all_chunks),
            "total_qa_pairs": len(all_qa_pairs),
            "results": results,
            "output_dir": self.output_dir
        }
    
    def load_chunks_to_rag(self) -> int:
        """
        Load processed chunks into RAG vector store.
        
        Returns:
            Number of documents added
        """
        from app.ml.rag_service import get_rag_service
        
        chunks_path = os.path.join(self.output_dir, "rag_chunks.json")
        
        if not os.path.exists(chunks_path):
            logger.warning("No chunks file found. Run process_all_pdfs first.")
            return 0
        
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        if not chunks:
            return 0
        
        rag = get_rag_service()
        rag.initialize()
        
        # Prepare documents and metadata
        documents = [c["text"] for c in chunks]
        metadatas = [{"source": c["source"], "section": c["section"]} for c in chunks]
        
        # Add to vector store
        count = rag.add_documents(documents, metadatas)
        
        logger.info(f"Loaded {count} chunks into RAG vector store")
        return count


# Convenience function
def get_pdf_processor() -> PDFProcessor:
    """Get a PDF processor instance"""
    return PDFProcessor()
