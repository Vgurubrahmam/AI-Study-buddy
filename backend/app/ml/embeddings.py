"""
Embedding Service
Handles text embeddings for RAG (Retrieval-Augmented Generation)
"""

from sentence_transformers import SentenceTransformer
from typing import List, Optional, Union
import numpy as np
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using sentence-transformers.
    Used for semantic search in RAG pipeline.
    """
    
    def __init__(self):
        self.model = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the embedding model"""
        if self._initialized:
            return
        
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        
        try:
            self.model = SentenceTransformer(settings.embedding_model)
            self._initialized = True
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array of embeddings
        """
        if not self._initialized:
            self.initialize()
        
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            numpy array of embeddings (num_texts x embedding_dim)
        """
        if not self._initialized:
            self.initialize()
        
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding optimized for queries (semantic search).
        
        Args:
            query: Search query text
            
        Returns:
            numpy array embedding
        """
        return self.embed_text(query)
    
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """
        Generate embeddings optimized for documents.
        
        Args:
            documents: List of document texts
            
        Returns:
            numpy array of embeddings
        """
        return self.embed_texts(documents)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score (0-1)
        """
        from numpy.linalg import norm
        
        return float(np.dot(embedding1, embedding2) / (norm(embedding1) * norm(embedding2)))
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model"""
        if not self._initialized:
            self.initialize()
        
        return self.model.get_sentence_embedding_dimension()
    
    def is_initialized(self) -> bool:
        """Check if model is initialized"""
        return self._initialized


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get the embedding service singleton.
    Lazy initialization - model loads on first use.
    """
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    
    return _embedding_service
