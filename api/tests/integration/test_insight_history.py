import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_exercise_history_filtering_by_routine(client: AsyncClient, auth_headers: dict):
    # 1. Create Exercise
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Bench Press"}) { id } }'},
        headers=auth_headers,
    )
    ex_id = resp.json()["data"]["createExercise"]["id"]

    # 2. Create Routine A and Routine B
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Routine A"}) { id } }'},
        headers=auth_headers,
    )
    routine_a_id = resp.json()["data"]["createRoutine"]["id"]

    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Routine B"}) { id } }'},
        headers=auth_headers,
    )
    routine_b_id = resp.json()["data"]["createRoutine"]["id"]

    # 3. Add Exercise to both routines
    for rid in [routine_a_id, routine_b_id]:
        await client.post(
            "/graphql",
            json={
                "query": "mutation AddEx($rid: UUID!, $eid: UUID!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: 1}) { id } }",
                "variables": {"rid": rid, "eid": ex_id},
            },
            headers=auth_headers,
        )

    # 4. Create Mesocycle
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Test Meso", startDate: "2026-04-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    # 5. Add Week 1
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation AddW($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 1, weekType: TRAINING, startDate: "2026-04-01", endDate: "2026-04-07"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week1_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    # 5b. Add Week 2
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation AddW($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 2, weekType: TRAINING, startDate: "2026-04-08", endDate: "2026-04-14"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week2_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    # 6. Add Planned Session for Routine A (Week 1)
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation AddPS($wid: UUID!, $rid: UUID!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: 1}) { id } }",
            "variables": {"wid": week1_id, "rid": routine_a_id},
        },
        headers=auth_headers,
    )
    if "errors" in resp.json():
        print("Error adding PS A:", resp.json())
    ps_a_id = resp.json()["data"]["addPlannedSession"]["id"]

    # 7. Add Planned Session for Routine B (Week 2)
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation AddPS($wid: UUID!, $rid: UUID!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: 1}) { id } }",
            "variables": {"wid": week2_id, "rid": routine_b_id},
        },
        headers=auth_headers,
    )
    if "errors" in resp.json():
        print("Error adding PS B:", resp.json())
    ps_b_id = resp.json()["data"]["addPlannedSession"]["id"]

    # 8. Create and Complete Session A
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation CreateS($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id } }",
            "variables": {"psid": ps_a_id},
        },
        headers=auth_headers,
    )
    session_a_id = resp.json()["data"]["createSession"]["id"]
    await client.post(
        "/graphql",
        json={"query": 'mutation { startSession(id: "%s") { id } }' % session_a_id},
        headers=auth_headers,
    )
    await client.post(
        "/graphql",
        json={"query": 'mutation { completeSession(id: "%s") { id } }' % session_a_id},
        headers=auth_headers,
    )

    # 9. Create and Complete Session B
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation CreateS($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id } }",
            "variables": {"psid": ps_b_id},
        },
        headers=auth_headers,
    )
    session_b_id = resp.json()["data"]["createSession"]["id"]
    await client.post(
        "/graphql",
        json={"query": 'mutation { startSession(id: "%s") { id } }' % session_b_id},
        headers=auth_headers,
    )
    await client.post(
        "/graphql",
        json={"query": 'mutation { completeSession(id: "%s") { id } }' % session_b_id},
        headers=auth_headers,
    )

    # 10. Query Exercise History WITHOUT filter
    # Should return both sessions
    query_all = """
    query GetHist($eid: UUID!) {
        exerciseHistory(exerciseId: $eid) {
            items { id routineId }
            total
        }
    }
    """
    resp = await client.post(
        "/graphql", json={"query": query_all, "variables": {"eid": ex_id}}, headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()["data"]["exerciseHistory"]
    assert data["total"] == 2
    ids = [item["id"] for item in data["items"]]
    assert session_a_id in ids
    assert session_b_id in ids

    # 11. Query Exercise History WITH filter for Routine A
    # Should return only session A
    query_filtered = """
    query GetHist($eid: UUID!, $rid: UUID!) {
        exerciseHistory(exerciseId: $eid, routineId: $rid) {
            items { id routineId }
            total
        }
    }
    """
    resp = await client.post(
        "/graphql",
        json={"query": query_filtered, "variables": {"eid": ex_id, "rid": routine_a_id}},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]["exerciseHistory"]
    assert data["total"] == 1
    assert data["items"][0]["id"] == session_a_id
    assert data["items"][0]["routineId"] == routine_a_id
