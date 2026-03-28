from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.services.insight_service import InsightService
from workouter_cli.domain.entities.insight import (
    IntensityInsight,
    ProgressiveOverloadInsight,
    VolumeInsight,
)
from workouter_cli.domain.entities.session import Session


def _volume_insight() -> VolumeInsight:
    return VolumeInsight(
        mesocycle_id="22222222-2222-2222-2222-222222222222",
        weekly_volumes=(),
        total_sets=12,
        muscle_group_breakdown=(),
    )


def _intensity_insight() -> IntensityInsight:
    return IntensityInsight(
        mesocycle_id="22222222-2222-2222-2222-222222222222",
        weekly_intensities=(),
        overall_avg_rir=2.0,
    )


def _overload_insight() -> ProgressiveOverloadInsight:
    return ProgressiveOverloadInsight(
        exercise_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        mesocycle_id="22222222-2222-2222-2222-222222222222",
        weekly_progress=(),
        estimated_one_rep_max_progression=(100.0,),
    )


def _session() -> Session:
    return Session(
        id="11111111-1111-1111-1111-111111111111",
        planned_session_id=None,
        mesocycle_id="22222222-2222-2222-2222-222222222222",
        routine_id="33333333-3333-3333-3333-333333333333",
        status="COMPLETED",
        started_at="2026-01-01T10:00:00Z",
        completed_at="2026-01-01T11:00:00Z",
        notes=None,
        exercises=(),
    )


@pytest.mark.asyncio
async def test_insight_service_delegates(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.volume = AsyncMock(return_value=_volume_insight())
    repository.intensity = AsyncMock(return_value=_intensity_insight())
    repository.overload = AsyncMock(return_value=_overload_insight())
    repository.history = AsyncMock(return_value=([_session()], {"total": 1}))

    service = InsightService(insight_repository=repository)

    volume = await service.volume("22222222-2222-2222-2222-222222222222")
    intensity = await service.intensity("22222222-2222-2222-2222-222222222222")
    overload = await service.overload(
        "22222222-2222-2222-2222-222222222222",
        "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    )
    items, pagination = await service.history("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

    assert volume.total_sets == 12
    assert intensity.overall_avg_rir == 2.0
    assert overload.estimated_one_rep_max_progression[0] == 100.0
    assert len(items) == 1
    assert pagination["total"] == 1

    repository.volume.assert_awaited_once_with(
        mesocycle_id="22222222-2222-2222-2222-222222222222",
        muscle_group_id=None,
    )
    repository.intensity.assert_awaited_once_with(
        mesocycle_id="22222222-2222-2222-2222-222222222222"
    )
    repository.overload.assert_awaited_once_with(
        mesocycle_id="22222222-2222-2222-2222-222222222222",
        exercise_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    )
    repository.history.assert_awaited_once_with(
        exercise_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        routine_id=None,
        page=1,
        page_size=20,
    )
