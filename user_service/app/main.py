import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from common.db import create_db_and_tables
from common.config import settings
from common.metrics import PrometheusMiddleware
from .router import router as user_router

app = FastAPI(title="User Service", docs_url="/user/docs", openapi_url="/user/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(PrometheusMiddleware, service_name="user_service")
app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health():
    return {"status": "ok", "service": "user_service"}

app.include_router(user_router)

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
