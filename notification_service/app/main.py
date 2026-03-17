import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from common.metrics import PrometheusMiddleware
from .consumer import start_consumers
from .router import router

app = FastAPI(title="Notification Service", docs_url="/notification/docs", openapi_url="/notification/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(PrometheusMiddleware, service_name="notification_service")
app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health():
    return {"status": "ok", "service": "notification_service"}

app.include_router(router)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_consumers())
