from enum import StrEnum


class SetType(StrEnum):
    STANDARD = "standard"
    DROPSET = "dropset"


class SessionStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class WeekType(StrEnum):
    TRAINING = "training"
    DELOAD = "deload"


class MuscleRole(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"


class MesocycleStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
