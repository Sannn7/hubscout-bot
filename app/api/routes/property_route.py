from fastapi import APIRouter, HTTPException
from app.models.schemas import PropertyQuery, APIResponse

router = APIRouter()

@router.post("/query", response_model=APIResponse)
async def query_property(query: PropertyQuery):
    """
    Query property assessment and real estate data.
    
    Future implementation will include:
    - Property value assessments
    - Historical sale data
    - Property characteristics
    """
    try:
        response_text = (
            f"Property query for {query.address}: {query.query}\n\n"
            "Database integration in progress."
        )
        
        return APIResponse(
            answer=response_text,
            sources=["Boston Property Assessment"],
            metadata={"status": "development"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def property_health():
    """Health check for property endpoint."""
    return {"status": "healthy"}
