import strawberry
import structlog

from app.domain.exceptions import (
    ConflictException,
    DomainException,
    EntityNotFoundException,
    ValidationException,
)

logger = structlog.get_logger(__name__)

class ErrorHandlerExtension(strawberry.extensions.SchemaExtension):
    def on_operation(self):
        yield
        result = self.execution_context.result
        if result and result.errors:
            for error in result.errors:
                if error.original_error:
                    exc = error.original_error
                    if isinstance(exc, EntityNotFoundException):
                        error.extensions = {"code": "NOT_FOUND"}
                    elif isinstance(exc, ConflictException):
                        error.extensions = {"code": "CONFLICT"}
                    elif isinstance(exc, ValidationException):
                        error.extensions = {"code": "VALIDATION_ERROR"}
                    elif isinstance(exc, DomainException):
                        error.extensions = {"code": "DOMAIN_ERROR"}
                    else:
                        logger.exception("unexpected_error", error=str(exc))
                        error.extensions = {"code": "INTERNAL_ERROR"}
