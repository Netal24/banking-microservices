import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from common.db import create_db_and_tables
from common.metrics import PrometheusMiddleware
from .router import router

app = FastAPI(title="Transaction Service", docs_url="/transaction/docs", openapi_url="/transaction/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(PrometheusMiddleware, service_name="transaction_service")
app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health():
    return {"status": "ok", "service": "transaction_service"}

app.include_router(router)

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
