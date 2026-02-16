import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger("api.timer")

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Start the timer (High precision)
        start_time = time.perf_counter()
        
        # 2. Process the request (go to endpoint)
        response = await call_next(request)
        
        # 3. Stop the timer
        process_time = time.perf_counter() - start_time
        
        # 4. Add header to response (Visible in Swagger/Postman)
        # Convert to milliseconds (e.g., "12.5ms")
        response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"
        
        # 5. Log slow requests (Optional but recommended)
        if process_time > 0.5: # Log warning if slower than 500ms
            logger.warning(f"🐢 Slow Request: {request.url.path} took {process_time:.4f}s")
        else:
            logger.info(f"⚡ Fast Request: {request.url.path} took {process_time:.4f}s")
            
        return response