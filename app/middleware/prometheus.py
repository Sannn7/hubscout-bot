"""
Prometheus metrics middleware for FastAPI.
"""

from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request
import time

# Metrics
REQUEST_COUNT = Counter(
    'hubscout_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'hubscout_request_duration_seconds',
    'Request latency',
    ['method', 'endpoint']
)

RAG_RETRIEVAL_TIME = Histogram(
    'hubscout_rag_retrieval_seconds',
    'RAG retrieval time'
)

VECTOR_SEARCH_TIME = Histogram(
    'hubscout_vector_search_seconds',
    'Vector search time'
)

async def prometheus_middleware(request: Request, call_next):
    """Track request metrics."""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response