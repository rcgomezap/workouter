from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.application.dto.pagination import PaginatedResult

class BodyweightLogDTO(BaseModel):
    id: UUID
    weight_kg: Decimal
    recorded_at: datetime
    notes: str | None = None
    created_at: datetime

class LogBodyweightInput(BaseModel):
    weight_kg: Decimal
    recorded_at: datetime
    notes: str | None = None

class UpdateBodyweightInput(BaseModel):
    weight_kg: Decimal | None = None
    recorded_at: datetime | None = None
    notes: str | None = None

class PaginatedBodyweightLogs(PaginatedResult[BodyweightLogDTO]):
    pass
