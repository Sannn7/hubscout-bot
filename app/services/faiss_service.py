"""
FAISS-based vector search service for fast retrieval over 350K+ records.
"""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    """
    FAISS vector store for efficient similarity search.
    Significantly faster than ChromaDB for large-scale retrieval.
    """
    
    def __init__(self, index_path: str = "data/indexes/faiss_index"):
        self.index_path = Path(index_path)
        self.index = None
        self.documents = []
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.dimension = 384
        
    def build_index(self, texts: List[str], use_gpu: bool = False):
        """
        Build FAISS index from texts.
        
        Args:
            texts: List of text documents to index
            use_gpu: Whether to use GPU for indexing (faster for large datasets)
        """
        logger.info(f"Building FAISS index for {len(texts)} documents...")
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Create FAISS index
        if use_gpu:
            # Use GPU-accelerated index
            res = faiss.StandardGpuResources()
            index_flat = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.index_cpu_to_gpu(res, 0, index_flat)
        else:
            # Use CPU index with IVF for faster search
            # IVF (Inverted File Index) partitions vectors for faster search
            nlist = 100  # number of clusters
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.index.train(embeddings)
        
        # Add vectors to index
        self.index.add(embeddings)
        self.documents = texts
        
        logger.info(f"Index built with {self.index.ntotal} vectors")
        
    def save_index(self):
        """Save FAISS index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save index
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))
        
        # Save documents
        with open(self.index_path / "documents.pkl", "wb") as f:
            pickle.dump(self.documents, f)
        
        logger.info(f"Index saved to {self.index_path}")
    
    def load_index(self):
        """Load FAISS index from disk."""
        index_file = self.index_path / "index.faiss"
        docs_file = self.index_path / "documents.pkl"
        
        if not index_file.exists():
            raise FileNotFoundError(f"Index not found at {index_file}")
        
        self.index = faiss.read_index(str(index_file))
        
        with open(docs_file, "rb") as f:
            self.documents = pickle.load(f)
        
        logger.info(f"Index loaded: {self.index.ntotal} vectors")
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar documents.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of (document, distance) tuples
        """
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))
        
        return results