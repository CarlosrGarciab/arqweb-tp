import os
import time
import uuid
from fastapi import FastAPI, Response, Request, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Event Bridge", version="1.0.0")

# Token compartido secreto para validar que el webhook viene realmente de BookStack
SHARED_WEBHOOK_TOKEN = os.getenv("SHARED_WEBHOOK_TOKEN", "mi-token-secreto-seguro")

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

@app.post("/webhook")
async def receive_webhook(request: Request):
    # Validar el token enviado por URL o cabecera
    token = request.query_params.get("token")
    if token != SHARED_WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized webhook token")
    
    body = await request.json()
    
    # Crear el sobre de evento estándar pedido por la cátedra (A3)
    event_envelope = {
        "event_id": str(uuid.uuid4()),
        "type": body.get("event", "unknown.event"),
        "version": "v1",
        "occurred_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "payload": body
    }
    
    print(f"Evento recibido y procesado: {event_envelope['type']}")
    return {"status": "accepted", "event_id": event_envelope["event_id"]}
