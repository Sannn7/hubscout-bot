from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from pathlib import Path
import logging
from typing import Dict, List
from app.config import config

logger = logging.getLogger(__name__)

class RAGService:
    """
    Retrieval-Augmented Generation service using HuggingFace embeddings and ChromaDB.
    
    This service implements a complete RAG pipeline:
    1. Document loading from knowledge base
    2. Text chunking with overlap
    3. Vector embeddings generation
    4. Semantic similarity search
    5. Context retrieval for question answering
    """
    
    def __init__(self, knowledge_base_path: str = None):
        self.knowledge_base_path = Path(knowledge_base_path or config.KNOWLEDGE_BASE_PATH)
        self.vectorstore = None
        self.retriever = None
        self.embeddings = None
        
        self._initialize_rag_pipeline()
    
    def _initialize_rag_pipeline(self):
        """Initialize the complete RAG pipeline."""
        try:
            logger.info("Initializing RAG pipeline...")
            
            # Load documents from knowledge base
            documents = self._load_documents()
            
            # Split documents into chunks
            chunks = self._chunk_documents(documents)
            
            # Initialize embeddings model
            self._initialize_embeddings()
            
            # Create vector store
            self._create_vector_store(chunks)
            
            # Create retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": config.RETRIEVAL_K}
            )
            
            logger.info("RAG pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            raise
    
    def _load_documents(self) -> List:
        """Load all text documents from knowledge base."""
        documents = []
        
        if not self.knowledge_base_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.knowledge_base_path}"
            )
        
        # Load all .txt files
        for file_path in self.knowledge_base_path.glob("*.txt"):
            logger.info(f"Loading document: {file_path.name}")
            loader = TextLoader(str(file_path), encoding='utf-8')
            documents.extend(loader.load())
        
        if not documents:
            raise ValueError("No documents found in knowledge base")
        
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    
    def _chunk_documents(self, documents: List) -> List:
        """Split documents into chunks with overlap."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from documents")
        return chunks
    
    def _initialize_embeddings(self):
        """Initialize HuggingFace embeddings model."""
        logger.info(f"Loading embeddings model: {config.EMBEDDING_MODEL}")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        logger.info("Embeddings model loaded")
    
    def _create_vector_store(self, chunks: List):
        """Create or load ChromaDB vector store."""
        persist_dir = Path(config.CHROMA_PERSIST_DIR)
        
        # Check if vector store already exists
        if persist_dir.exists() and any(persist_dir.iterdir()):
            logger.info("Loading existing vector store")
            self.vectorstore = Chroma(
                persist_directory=config.CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings
            )
        else:
            logger.info("Creating new vector store")
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=config.CHROMA_PERSIST_DIR
            )
            self.vectorstore.persist()
        
        logger.info(f"Vector store ready with {self.vectorstore._collection.count()} vectors")
    
    def query(self, question: str) -> Dict:
        """
        Query the RAG system with a question.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary containing answer, sources, and retrieved documents
        """
        if self.retriever is None:
            raise RuntimeError("RAG system not initialized")
        
        try:
            # Retrieve relevant documents
            relevant_docs = self.retriever.get_relevant_documents(question)
            
            # Extract unique sources
            sources = list(set([
                doc.metadata.get('source', 'unknown') 
                for doc in relevant_docs
            ]))
            
            # Format answer with retrieved context
            answer = self._format_answer(question, relevant_docs)
            
            return {
                "answer": answer,
                "sources": sources,
                "retrieved_chunks": [doc.page_content for doc in relevant_docs],
                "num_chunks": len(relevant_docs)
            }
            
        except Exception as e:
            logger.error(f"Error during query: {e}")
            raise
    
    def _format_answer(self, question: str, documents: List) -> str:
        """Format the answer using retrieved documents."""
        if not documents:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[Context {i}]\n{doc.page_content}\n")
        
        answer = (
            f"Based on the knowledge base, here is the relevant information:\n\n"
            f"{''.join(context_parts)}"
        )
        
        return answer
    
    def add_documents(self, documents: List):
        """Add new documents to the vector store."""
        if not self.vectorstore:
            raise RuntimeError("Vector store not initialized")
        
        chunks = self._chunk_documents(documents)
        self.vectorstore.add_documents(chunks)
        self.vectorstore.persist()
        logger.info(f"Added {len(chunks)} new chunks to vector store")
    
    def similarity_search(self, query: str, k: int = 3) -> List:
        """Perform similarity search without formatting."""
        if not self.vectorstore:
            raise RuntimeError("Vector store not initialized")
        
        return self.vectorstore.similarity_search(query, k=k)