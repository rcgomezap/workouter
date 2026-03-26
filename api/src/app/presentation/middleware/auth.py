from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.loader import load_config as get_config


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if (
            request.url.path == "/health"
            or request.url.path == "/docs"
            or request.url.path == "/openapi.json"
        ):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        config = get_config()

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        if token != config.auth.api_key:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        return await call_next(request)
