from uuid import UUID


class DomainException(Exception):
    """Base exception for domain layer"""

    message: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """Exception raised when an entity is not found"""

    def __init__(self, entity_name: str, entity_id: UUID) -> None:
        self.message = f"{entity_name} with id {entity_id} not found"
        super().__init__(self.message)


class ConflictException(DomainException):
    """Exception raised when an operation violates a business rule or referential integrity"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ValidationException(DomainException):
    """Exception raised when domain validation fails"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
