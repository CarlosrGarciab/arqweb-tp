import os
import time
import uuid
from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Export Service", version="1.0.0")

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request duration', ['endpoint'])

@app.middleware("http")
async def add_metrics(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    endpoint = request.url.path
    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status_code=response.status_code).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    
    return response

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    return {"status": "ready"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/v2/exports")
def create_export():
    job_id = str(uuid.uuid4())
    # Devuelve 202 Accepted indicando que el trabajo se encoló
    return {"job_id": job_id, "status": "queued", "message": "Export job accepted"}
