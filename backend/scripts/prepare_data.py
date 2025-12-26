"""
Data Preparation Script
Processes PDFs and prepares training data for fine-tuning
"""

import sys
import os
import argparse
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.pdf_processor import PDFProcessor
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Process PDFs and prepare training data for AI Study Buddy"
    )
    
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default=settings.study_pdfs_dir,
        help="Directory containing PDF files"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=settings.training_data_dir,
        help="Directory to save processed data"
    )
    
    parser.add_argument(
        "--load-to-rag",
        action="store_true",
        help="Also load chunks into RAG vector store"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("AI Study Buddy - Data Preparation")
    logger.info("=" * 60)
    
    # Initialize processor
    processor = PDFProcessor(pdf_dir=args.pdf_dir)
    processor.output_dir = args.output_dir
    
    # Process all PDFs
    logger.info(f"Processing PDFs from: {args.pdf_dir}")
    result = processor.process_all_pdfs()
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("Processing Summary")
    logger.info("=" * 60)
    logger.info(f"Status: {result['status']}")
    logger.info(f"Files processed: {result.get('files_processed', 0)}")
    logger.info(f"Total chunks: {result.get('total_chunks', 0)}")
    logger.info(f"Total Q&A pairs: {result.get('total_qa_pairs', 0)}")
    logger.info(f"Output directory: {result.get('output_dir', '')}")
    
    if 'results' in result:
        logger.info("\nPer-file results:")
        for r in result['results']:
            status_icon = "✓" if r['status'] == 'success' else "✗"
            logger.info(f"  {status_icon} {r['file']}: {r.get('chunks', 0)} chunks, {r.get('qa_pairs', 0)} Q&A pairs")
    
    # Optionally load to RAG
    if args.load_to_rag and result.get('total_chunks', 0) > 0:
        logger.info("\nLoading chunks to RAG vector store...")
        count = processor.load_chunks_to_rag()
        logger.info(f"Loaded {count} documents to RAG")
    
    logger.info("\n" + "=" * 60)
    logger.info("Data preparation complete!")
    logger.info("=" * 60)
    
    if result.get('total_qa_pairs', 0) > 0:
        logger.info(f"\nNext step: Run fine-tuning with:")
        logger.info(f"  python scripts/train.py")


if __name__ == "__main__":
    main()
