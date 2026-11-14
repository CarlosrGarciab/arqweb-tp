yimport os
import time
import requests
from fastapi import FastAPI, Response, Query
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Search Service", version="1.0.0")

BOOKSTACK_API_URL = os.getenv("BOOKSTACK_API_URL", "https://bookstack.miempresapro.com/api")
BOOKSTACK_TOKEN_ID = os.getenv("BOOKSTACK_TOKEN_ID", "")
BOOKSTACK_TOKEN_SECRET = os.getenv("BOOKSTACK_TOKEN_SECRET", "")

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency in seconds', ['method', 'endpoint'])

@app.middleware("http")
async def add_metrics_and_headers(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    endpoint = request.url.path
    method = request.method
    status = response.status_code
    
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
    
    return response

@app.get("/healthz")
def healthz():
    return {"status": "healthy"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Soportamos tanto / como /v2/search para evitar problemas de rutas con Nginx
@app.get("/")
@app.get("/v2/search")
def search(q: str = Query(..., description="Query de búsqueda")):
    headers = {
        "Authorization": f"Token {BOOKSTACK_TOKEN_ID}:{BOOKSTACK_TOKEN_SECRET}",
        "Content-Type": "application/json"
    }
    
    try:
	print(f"URL FINAL {BOOKSTACK_API_URL/search}", flush=True)
        # verify=False desactiva la validación del certificado autofirmado SSL de BookStack
        response = requests.get(
            f"{BOOKSTACK_API_URL}/search",
            params={"query": q},
            headers=headers,
            verify=False,
            timeout=10
        )
    
        if response.status_code != 200:
            return {
                "error": "Error al conectar con BookStack",
                "status_code": response.status_code,
                "details": response.text
            }
            
        return response.json()
    except Exception as e:
        return {
            "error": "Excepción al conectar con BookStack",
            "details": str(e)
        }
