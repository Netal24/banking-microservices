import time
from prometheus_client import Counter, Histogram, Gauge
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["service", "endpoint"],
)
ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Active HTTP requests",
    ["service"],
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        endpoint = request.url.path
        ACTIVE_REQUESTS.labels(service=self.service_name).inc()
        start = time.perf_counter()
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as exc:
            status = 500
            raise exc
        finally:
            duration = time.perf_counter() - start
            ACTIVE_REQUESTS.labels(service=self.service_name).dec()
            REQUEST_LATENCY.labels(service=self.service_name, endpoint=endpoint).observe(duration)
            REQUEST_COUNT.labels(
                service=self.service_name,
                method=request.method,
                endpoint=endpoint,
                http_status=status,
            ).inc()
        return response
