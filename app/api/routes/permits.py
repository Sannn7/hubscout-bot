from fastapi import APIRouter, HTTPException
from app.models.schemas import PermitQuery, APIResponse

router = APIRouter()

@router.post("/search", response_model=APIResponse)
async def search_permits(query: PermitQuery):
    """
    Search for construction permits near a location.
    
    Future implementation will include:
    - Spatial queries on permit database
    - Filtering by permit type and date
    - Integration with Boston Open Data
    """
    try:
        response_text = (
            f"Permit search for {query.address or 'coordinates'} "
            f"within {query.radius_miles} miles.\n\n"
            "Database integration in progress."
        )
        
        return APIResponse(
            answer=response_text,
            sources=["Boston Open Data Portal"],
            metadata={"status": "development"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def permits_health():
    """Health check for permits endpoint."""
    return {"status": "healthy"}