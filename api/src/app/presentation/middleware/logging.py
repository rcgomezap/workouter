import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        method = request.method
        path = request.url.path

        logger.info(
            "request_started",
            method=method,
            path=path,
        )

        try:
            response = await call_next(request)
        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_failed",
                method=method,
                path=path,
                duration_ms=round(process_time, 2),
                exception=str(e),
            )
            raise e

        process_time = (time.perf_counter() - start_time) * 1000

        logger.info(
            "request_finished",
            method=method,
            path=path,
            status_code=response.status_code,
            duration_ms=round(process_time, 2),
        )

        return response
