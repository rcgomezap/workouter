
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_real_insight_calculations(client: AsyncClient, auth_headers: dict):
    # 1. Create Exercise
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Bench Press"}) { id } }'},
        headers=auth_headers,
    )
    ex_id = resp.json()["data"]["createExercise"]["id"]

    # 2. Create Routine
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Push Day"}) { id } }'},
        headers=auth_headers,
    )
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    await client.post(
        "/graphql",
        json={
            "query": "mutation AddEx($rid: UUID!, $eid: UUID!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: 1}) { id } }",
            "variables": {"rid": routine_id, "eid": ex_id},
        },
        headers=auth_headers,
    )

    # 3. Create Mesocycle with 2 weeks
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Calculated Meso", startDate: "2026-05-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    # Week 1
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation AddW($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 1, weekType: TRAINING, startDate: "2026-05-01", endDate: "2026-05-07"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week1_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    # Week 2
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation AddW($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 2, weekType: TRAINING, startDate: "2026-05-08", endDate: "2026-05-14"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week2_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    # Planned Sessions
    async def add_planned_session(week_id, r_id):
        resp = await client.post(
            "/graphql",
            json={
                "query": "mutation AddPS($wid: UUID!, $rid: UUID!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: 1}) { id } }",
                "variables": {"wid": week_id, "rid": r_id},
            },
            headers=auth_headers,
        )
        return resp.json()["data"]["addPlannedSession"]["id"]

    ps1_id = await add_planned_session(week1_id, routine_id)
    ps2_id = await add_planned_session(week2_id, routine_id)

    # Log Session Week 1: 100kg x 5 reps (Epley 1RM = 100 * (1 + 5/30) = 116.67)
    async def complete_session(ps_id, weight, reps, rir):
        resp = await client.post(
            "/graphql",
            json={
                "query": "mutation CreateS($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id exercises { sets { id } } } }",
                "variables": {"psid": ps_id},
            },
            headers=auth_headers,
        )
        s_data = resp.json()["data"]["createSession"]
        s_id = s_data["id"]
        set_id = s_data["exercises"][0]["sets"][0]["id"]

        await client.post(
            "/graphql",
            json={"query": f'mutation {{ startSession(id: "{s_id}") {{ id }} }}'},
            headers=auth_headers,
        )
        await client.post(
            "/graphql",
            json={
                "query": "mutation Log($sid: UUID!, $w: Decimal!, $r: Int!, $rir: Int!) { logSetResult(setId: $sid, input: {actualReps: $r, actualWeightKg: $w, actualRir: $rir}) { id } }",
                "variables": {"sid": set_id, "w": str(weight), "r": reps, "rir": rir},
            },
            headers=auth_headers,
        )
        await client.post(
            "/graphql",
            json={"query": f'mutation {{ completeSession(id: "{s_id}") {{ id }} }}'},
            headers=auth_headers,
        )
        return s_id

    await complete_session(ps1_id, 100.0, 5, 2)
    # Log Session Week 2: 105kg x 5 reps (Epley 1RM = 105 * (1 + 5/30) = 122.5)
    await complete_session(ps2_id, 105.0, 5, 1)

    # 4. Verify Progressive Overload Insight
    po_query = """
    query GetPO($mid: UUID!, $eid: UUID!) {
        progressiveOverloadInsight(mesocycleId: $mid, exerciseId: $eid) {
            weeklyProgress { weekNumber maxWeight avgReps avgRir }
            estimatedOneRepMaxProgression
        }
    }
    """
    resp = await client.post(
        "/graphql",
        json={"query": po_query, "variables": {"mid": meso_id, "eid": ex_id}},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    po_data = resp.json()["data"]["progressiveOverloadInsight"]

    assert po_data["weeklyProgress"][0]["weekNumber"] == 1
    assert float(po_data["weeklyProgress"][0]["maxWeight"]) == 100.0
    assert po_data["weeklyProgress"][1]["weekNumber"] == 2
    assert float(po_data["weeklyProgress"][1]["maxWeight"]) == 105.0

    e1rms = po_data["estimatedOneRepMaxProgression"]
    assert round(float(e1rms[0]), 2) == 116.67
    assert round(float(e1rms[1]), 2) == 122.5

    # 5. Verify Intensity Insight
    int_query = """
    query GetInt($mid: UUID!) {
        mesocycleIntensityInsight(mesocycleId: $mid) {
            weeklyIntensities { weekNumber avgRir }
            overallAvgRir
        }
    }
    """
    resp = await client.post(
        "/graphql", json={"query": int_query, "variables": {"mid": meso_id}}, headers=auth_headers
    )
    assert resp.status_code == 200
    int_data = resp.json()["data"]["mesocycleIntensityInsight"]

    assert int_data["weeklyIntensities"][0]["avgRir"] == 2.0
    assert int_data["weeklyIntensities"][1]["avgRir"] == 1.0
    assert int_data["overallAvgRir"] == 1.5
