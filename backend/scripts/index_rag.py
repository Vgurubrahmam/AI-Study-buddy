"""
Index PDFs to RAG Script
Load processed PDF chunks into RAG vector store for retrieval
"""

import sys
import os
import argparse
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.pdf_processor import PDFProcessor
from app.ml.rag_service import get_rag_service
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Index PDFs into RAG vector store"
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing vector store before indexing"
    )
    
    parser.add_argument(
        "--process-pdfs",
        action="store_true",
        help="Process PDFs first before indexing"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("AI Study Buddy - RAG Indexing")
    logger.info("=" * 60)
    
    # Initialize RAG service
    rag = get_rag_service()
    rag.initialize()
    
    # Optionally clear existing data
    if args.clear:
        logger.info("Clearing existing vector store...")
        rag.clear_collection()
    
    # Optionally process PDFs first
    if args.process_pdfs:
        logger.info("Processing PDFs...")
        processor = PDFProcessor()
        result = processor.process_all_pdfs()
        logger.info(f"Processed {result.get('files_processed', 0)} files")
    
    # Load chunks to RAG
    processor = PDFProcessor()
    count = processor.load_chunks_to_rag()
    
    # Print stats
    stats = rag.get_stats()
    
    logger.info("\n" + "=" * 60)
    logger.info("Indexing Complete!")
    logger.info("=" * 60)
    logger.info(f"Documents indexed: {count}")
    logger.info(f"Total documents in store: {stats['document_count']}")
    logger.info(f"Persist directory: {stats['persist_directory']}")


if __name__ == "__main__":
    main()
