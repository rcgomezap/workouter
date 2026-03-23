from datetime import datetime, UTC
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class BaseEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TimestampedEntity(BaseEntity):
    pass
