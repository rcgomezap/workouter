import strawberry
from uuid import UUID
from datetime import datetime
from strawberry.types import Info
from app.presentation.graphql.context import Context
from app.presentation.graphql.types.bodyweight import BodyweightLog, PaginatedBodyweightLogs
from app.presentation.graphql.inputs.pagination import PaginationInput
from app.application.dto.pagination import PaginationInput as PaginationDTO

def map_bodyweight_log(l) -> BodyweightLog:
    return BodyweightLog(
        id=l.id,
        weight_kg=l.weight_kg,
        recorded_at=l.recorded_at,
        notes=l.notes,
        created_at=l.created_at
    )

@strawberry.type
class BodyweightQuery:
    @strawberry.field
    async def bodyweight_logs(
        self, 
        info: Info[Context, None], 
        pagination: PaginationInput | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> PaginatedBodyweightLogs:
        p_dto = PaginationDTO(
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else 20
        )
        result = await info.context.bodyweight_service.list_logs(p_dto, date_from, date_to)
        return PaginatedBodyweightLogs(
            items=[map_bodyweight_log(l) for l in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages
        )
