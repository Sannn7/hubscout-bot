from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes.permits import router as permits_router
from app.api.routes.transit import router as transit_router
from app.api.routes.neighborhood import router as neighborhood_router
from app.api.routes.property_route import router as property_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HubScout API",
    description="AI-powered Boston real estate assistant combining RAG and structured data queries",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "HubScout API",
        "version": "1.0.0"
    }

app.include_router(permits_router, prefix="/api/v1/permits", tags=["permits"])
app.include_router(transit_router, prefix="/api/v1/transit", tags=["transit"])
app.include_router(neighborhood_router, prefix="/api/v1/neighborhood", tags=["neighborhood"])
app.include_router(property_router, prefix="/api/v1/property", tags=["property"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)