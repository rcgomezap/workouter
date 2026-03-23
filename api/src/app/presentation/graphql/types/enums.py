import strawberry
from enum import StrEnum

@strawberry.enum
class SetType(StrEnum):
    STANDARD = "standard"
    DROPSET = "dropset"

@strawberry.enum
class SessionStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

@strawberry.enum
class WeekType(StrEnum):
    TRAINING = "training"
    DELOAD = "deload"

@strawberry.enum
class MuscleRole(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"

@strawberry.enum
class MesocycleStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
