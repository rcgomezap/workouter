from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dto.exercise import ExerciseDTO, ExerciseMuscleGroupDTO, MuscleGroupDTO
from app.domain.enums import MuscleRole
from app.presentation.graphql.inputs.exercise import MuscleGroupAssignmentInput
from app.presentation.graphql.mutations.exercise import ExerciseMutation
from app.presentation.graphql.types.enums import MuscleRole as GraphqlMuscleRole


@pytest.mark.asyncio
async def test_assign_muscle_groups_returns_mapped_muscle_groups() -> None:
    exercise_id = uuid4()
    muscle_group_id = uuid4()
    service_result = ExerciseDTO(
        id=exercise_id,
        name="Row",
        muscle_groups=[
            ExerciseMuscleGroupDTO(
                muscle_group=MuscleGroupDTO(id=muscle_group_id, name="Lats"),
                role=MuscleRole.PRIMARY,
            )
        ],
    )

    exercise_service = SimpleNamespace(assign_muscle_groups=AsyncMock(return_value=service_result))
    info = SimpleNamespace(context=SimpleNamespace(exercise_service=exercise_service))
    mutation = ExerciseMutation()

    result = await mutation.assign_muscle_groups(
        info,
        exercise_id=exercise_id,
        muscle_group_ids=[
            MuscleGroupAssignmentInput(
                muscle_group_id=muscle_group_id,
                role=GraphqlMuscleRole.PRIMARY,
            )
        ],
    )

    assert len(result.muscle_groups) == 1
    assert result.muscle_groups[0].role == GraphqlMuscleRole.PRIMARY
    assert result.muscle_groups[0].muscle_group.id == muscle_group_id
