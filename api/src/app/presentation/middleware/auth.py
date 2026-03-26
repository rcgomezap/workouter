from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.config.loader import load_config as get_config


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in {"/health", "/docs", "/openapi.json"}:
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
