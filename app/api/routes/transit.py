from fastapi import APIRouter, HTTPException
from app.models.schemas import TransitQuery, APIResponse
from app.services.transit_service import TransitService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize transit service
try:
    transit_service = TransitService()
except Exception as e:
    logger.error(f"Failed to initialize transit service: {e}")
    transit_service = None

@router.post("/query", response_model=APIResponse)
async def query_transit(query: TransitQuery):
    """
    Query MBTA transit data using structured GTFS queries.
    
    This endpoint handles questions about:
    - Stop and station locations
    - Route information
    - Transit schedules
    
    Example queries:
    - "What stops are near Harvard?"
    - "Show me all Orange Line stations"
    """
    try:
        if transit_service is None:
            raise HTTPException(
                status_code=503,
                detail="Transit service unavailable"
            )
        
        result = transit_service.handle_query(query.location, query.query)
        
        return APIResponse(
            answer=result["answer"],
            sources=["MBTA GTFS Data"],
            metadata={"data": result["data"]}
        )
        
    except Exception as e:
        logger.error(f"Error processing transit query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def transit_health():
    """Health check for transit endpoint."""
    return {
        "status": "healthy",
        "service_enabled": transit_service is not None
    }