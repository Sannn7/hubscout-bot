from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class PermitQuery(BaseModel):
    address: Optional[str] = Field(None, description="Property address")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    radius_miles: float = Field(default=0.5, description="Search radius in miles")
    query: Optional[str] = Field(None, description="Natural language question")

class TransitQuery(BaseModel):
    location: str = Field(..., description="Location name or address")
    query: str = Field(..., description="Transit-related question")

class NeighborhoodQuery(BaseModel):
    neighborhood_name: Optional[str] = Field(None, description="Neighborhood name")
    query: str = Field(..., description="Question about neighborhood")

class PropertyQuery(BaseModel):
    address: Optional[str] = Field(None, description="Property address")
    query: str = Field(..., description="Property-related question")

class APIResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None