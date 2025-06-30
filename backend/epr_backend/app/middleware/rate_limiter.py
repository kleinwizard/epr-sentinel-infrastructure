import time
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 50, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        client_calls = self.clients[client_ip]
        
        while client_calls and client_calls[0] <= current_time - self.period:
            client_calls.popleft()
        
        if len(client_calls) >= self.calls:
            return Response(
                content="Rate limit exceeded. Too many requests.",
                status_code=429,
                headers={"Retry-After": str(self.period)}
            )
        
        client_calls.append(current_time)
        response = await call_next(request)
        return response
