from datetime import datetime
from decimal import Decimal

import strawberry


@strawberry.input
class LogBodyweightInput:
    weight_kg: Decimal
    recorded_at: datetime | None = None
    notes: str | None = None

@strawberry.input
class UpdateBodyweightInput:
    weight_kg: Decimal | None = None
    recorded_at: datetime | None = None
    notes: str | None = None
