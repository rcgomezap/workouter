from datetime import datetime

import strawberry
from strawberry.types import Info

from app.application.dto.pagination import PaginationInput as PaginationDTO
from app.presentation.graphql.context import Context
from app.presentation.graphql.inputs.pagination import PaginationInput
from app.presentation.graphql.types.bodyweight import BodyweightLog, PaginatedBodyweightLogs


def map_bodyweight_log(log_entity) -> BodyweightLog:
    return BodyweightLog(
        id=log_entity.id,
        weight_kg=log_entity.weight_kg,
        recorded_at=log_entity.recorded_at,
        notes=log_entity.notes,
        created_at=log_entity.created_at,
    )


@strawberry.type
class BodyweightQuery:
    @strawberry.field
    async def bodyweight_logs(
        self,
        info: Info[Context, None],
        pagination: PaginationInput | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> PaginatedBodyweightLogs:
        p_dto = PaginationDTO(
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else 20,
        )

        # Convert datetime to date for service layer
        date_from_filter = date_from.date() if date_from else None
        date_to_filter = date_to.date() if date_to else None

        result = await info.context.bodyweight_service.list_bodyweight_logs(
            pagination=p_dto,
            date_from=date_from_filter,
            date_to=date_to_filter,
        )
        return PaginatedBodyweightLogs(
            items=[map_bodyweight_log(log) for log in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
        )
