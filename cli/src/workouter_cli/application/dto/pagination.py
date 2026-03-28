"""Pagination DTOs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PaginationInput(BaseModel):
    """Common pagination input contract."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100, alias="pageSize")


class PaginationResult(BaseModel):
    """Pagination metadata for list outputs."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100, alias="pageSize")
    total_pages: int = Field(ge=0, alias="totalPages")
