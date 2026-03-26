from collections import defaultdict, deque
from time import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit_per_minute: int = 60):
        super().__init__(app)
        self.limit_per_minute = limit_per_minute
        self.bucket: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time()
        hits = self.bucket[client_ip]
        while hits and now - hits[0] > 60:
            hits.popleft()
        if len(hits) >= self.limit_per_minute:
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        hits.append(now)
        return await call_next(request)
