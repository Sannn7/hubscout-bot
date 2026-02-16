from fastapi import APIRouter, HTTPException
from app.models.schemas import NeighborhoodQuery, APIResponse
from app.services.rag_service import RAGService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize RAG service
rag_service = None

try:
    logger.info("Initializing RAG service for neighborhood queries...")
    rag_service = RAGService()
    logger.info("RAG service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG service: {e}")

@router.post("/query", response_model=APIResponse)
async def query_neighborhood(query: NeighborhoodQuery):
    """
    Query neighborhood information using RAG (Retrieval-Augmented Generation).
    
    This endpoint uses semantic search over a knowledge base of neighborhood
    descriptions to answer questions about Boston neighborhoods.
    
    Example queries:
    - "What are the transit options in Back Bay?"
    - "Tell me about neighborhoods near MIT"
    - "Which areas have good restaurants?"
    """
    try:
        if rag_service is None:
            raise HTTPException(
                status_code=503,
                detail="RAG service unavailable. Check server logs for initialization errors."
            )
        
        result = rag_service.query(query.query)
        
        return APIResponse(
            answer=result["answer"],
            sources=result["sources"],
            metadata={
                "retrieved_chunks": result["retrieved_chunks"],
                "num_chunks": result["num_chunks"]
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing neighborhood query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def neighborhood_health():
    """Health check for neighborhood endpoint."""
    return {
        "status": "healthy",
        "rag_enabled": rag_service is not None
    }