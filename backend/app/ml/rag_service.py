"""
RAG (Retrieval-Augmented Generation) Service
Combines vector search with LLM generation for context-aware responses
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional, Tuple
import logging
import os

from app.config import settings
from app.ml.embeddings import get_embedding_service

logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation service using ChromaDB for vector storage.
    Enhances LLM responses with relevant context from study materials.
    """
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialized = False
    
    def initialize(self):
        """Initialize ChromaDB and create/load collection"""
        if self._initialized:
            return
        
        logger.info("Initializing RAG service with ChromaDB...")
        
        try:
            # Ensure persist directory exists
            os.makedirs(settings.chroma_persist_dir, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection for study materials
            self.collection = self.client.get_or_create_collection(
                name="study_materials",
                metadata={"description": "AI Study Buddy knowledge base"}
            )
            
            self._initialized = True
            logger.info(f"RAG service initialized. Collection has {self.collection.count()} documents.")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> int:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document texts
            metadatas: Optional metadata for each document
            ids: Optional custom IDs (generated if not provided)
            
        Returns:
            Number of documents added
        """
        if not self._initialized:
            self.initialize()
        
        if not documents:
            return 0
        
        # Generate IDs if not provided
        if ids is None:
            existing_count = self.collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
        
        # Generate embeddings
        embedding_service = get_embedding_service()
        embeddings = embedding_service.embed_documents(documents).tolist()
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas or [{}] * len(documents),
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")
        return len(documents)
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for relevant documents using semantic similarity.
        
        Args:
            query: Search query
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            List of relevant documents with metadata and scores
        """
        if not self._initialized:
            self.initialize()
        
        # Generate query embedding
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.embed_query(query).tolist()
        
        # Search collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "document": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                    "id": results["ids"][0][i] if results["ids"] else None
                })
        
        return formatted_results
    
    def get_context_for_query(
        self,
        query: str,
        n_results: int = 3,
        max_context_length: int = 2000
    ) -> str:
        """
        Get formatted context string for augmenting LLM response.
        
        Args:
            query: User's question
            n_results: Number of documents to retrieve
            max_context_length: Maximum characters for context
            
        Returns:
            Formatted context string
        """
        results = self.search(query, n_results=n_results)
        
        if not results:
            return ""
        
        context_parts = []
        total_length = 0
        
        for i, result in enumerate(results):
            doc = result["document"]
            metadata = result["metadata"]
            
            # Check length limit
            if total_length + len(doc) > max_context_length:
                # Truncate if needed
                remaining = max_context_length - total_length
                if remaining > 100:
                    doc = doc[:remaining] + "..."
                else:
                    break
            
            # Format context with metadata
            source = metadata.get("source", "Study Material")
            section = metadata.get("section", "")
            
            context_part = f"[Source: {source}"
            if section:
                context_part += f" - {section}"
            context_part += f"]\n{doc}"
            
            context_parts.append(context_part)
            total_length += len(doc)
        
        return "\n\n".join(context_parts)
    
    def delete_documents(self, ids: List[str]) -> int:
        """
        Delete documents from the vector store.
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            Number of documents deleted
        """
        if not self._initialized:
            self.initialize()
        
        self.collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents from vector store")
        return len(ids)
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        if not self._initialized:
            self.initialize()
        
        # Delete and recreate collection
        self.client.delete_collection("study_materials")
        self.collection = self.client.create_collection(
            name="study_materials",
            metadata={"description": "AI Study Buddy knowledge base"}
        )
        logger.info("Cleared vector store collection")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        if not self._initialized:
            self.initialize()
        
        return {
            "document_count": self.collection.count(),
            "collection_name": "study_materials",
            "persist_directory": settings.chroma_persist_dir
        }
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get the RAG service singleton.
    Lazy initialization - loads on first use.
    """
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RAGService()
    
    return _rag_service
