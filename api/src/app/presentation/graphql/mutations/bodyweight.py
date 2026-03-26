from typing import Any
from uuid import UUID

import strawberry
from strawberry.types import Info

from app.application.dto.bodyweight import (
    LogBodyweightInput as LogBodyweightDTO,
)
from app.application.dto.bodyweight import (
    UpdateBodyweightInput as UpdateBodyweightDTO,
)
from app.presentation.graphql.context import Context
from app.presentation.graphql.inputs.bodyweight import LogBodyweightInput, UpdateBodyweightInput
from app.presentation.graphql.types.bodyweight import BodyweightLog


def map_bodyweight_log(log: Any) -> BodyweightLog:
    return BodyweightLog(
        id=log.id,
        weight_kg=log.weight_kg,
        recorded_at=log.recorded_at,
        notes=log.notes,
        created_at=log.created_at,
    )


@strawberry.type
class BodyweightMutation:
    @strawberry.mutation
    async def log_bodyweight(
        self, info: Info[Context, None], input: LogBodyweightInput
    ) -> BodyweightLog:
        recorded_at = input.recorded_at
        if recorded_at is None:
            raise ValueError("recorded_at is required")
        dto = LogBodyweightDTO(
            weight_kg=input.weight_kg, recorded_at=recorded_at, notes=input.notes
        )
        log = await info.context.bodyweight_service.log_bodyweight(dto)
        return map_bodyweight_log(log)

    @strawberry.mutation
    async def update_bodyweight_log(
        self, info: Info[Context, None], id: UUID, input: UpdateBodyweightInput
    ) -> BodyweightLog:
        dto = UpdateBodyweightDTO(
            weight_kg=input.weight_kg, recorded_at=input.recorded_at, notes=input.notes
        )
        log = await info.context.bodyweight_service.update_bodyweight_log(id, dto)
        return map_bodyweight_log(log)

    @strawberry.mutation
    async def delete_bodyweight_log(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.bodyweight_service.delete_bodyweight_log(id)
