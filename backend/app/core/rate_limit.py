import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.redis import get_redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith(f"{settings.api_v1_prefix}/chat"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "anonymous"
        window = int(time.time() // 60)
        key = f"rate_limit:{client_ip}:{window}"

        try:
            redis = get_redis_client()
            count = redis.incr(key)
            if count == 1:
                redis.expire(key, 70)
            if count > settings.rate_limit_per_minute:
                return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        except Exception:
            pass

        return await call_next(request)
