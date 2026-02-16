from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Data Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    GTFS_PATH = BASE_DIR / "data" / "raw" / "mbta" / "MBTA_GTFS"
    KNOWLEDGE_BASE_PATH = BASE_DIR / "data" / "knowledge_base"
    
    # Vector Store
    CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")
    
    # RAG Configuration
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    RETRIEVAL_K = 3
    
    # OpenAI (optional)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

config = Config()