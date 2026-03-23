from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Sequence

T = TypeVar("T")

class PaginationInput(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class PaginatedResult(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    page_size: int
    total_pages: int
