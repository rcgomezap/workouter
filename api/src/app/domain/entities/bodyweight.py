from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class BodyweightLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    weight_kg: Decimal
    recorded_at: datetime
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
