from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
class BodyweightLog:
    id: UUID
    weight_kg: Decimal
    recorded_at: datetime
    notes: str | None
    created_at: datetime

@strawberry.type
class PaginatedBodyweightLogs:
    items: list[BodyweightLog]
    total: int
    page: int
    page_size: int
    total_pages: int
