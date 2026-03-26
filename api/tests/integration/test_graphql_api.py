import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_mesocycle_lifecycle_api(client: AsyncClient, auth_headers: dict):
    # 1. Create Mesocycle
    create_meso_mutation = """
    mutation CreateMesocycle($input: CreateMesocycleInput!) {
        createMesocycle(input: $input) {
            id
            name
            status
        }
    }
    """
    variables = {
        "input": {
            "name": "Strength Phase",
            "description": "API Test meso",
            "startDate": "2026-04-01",
        }
    }

    response = await client.post(
        "/graphql",
        json={"query": create_meso_mutation, "variables": variables},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    meso = data["data"]["createMesocycle"]
    assert meso["name"] == "Strength Phase"
    meso_id = meso["id"]

    # 3. Create Routine and Exercise for Session
    create_ex_mutation = """
    mutation CreateExercise($input: CreateExerciseInput!) {
        createExercise(input: $input) { id name }
    }
    """
    ex_vars = {"input": {"name": "Squat"}}
    resp = await client.post(
        "/graphql", json={"query": create_ex_mutation, "variables": ex_vars}, headers=auth_headers
    )
    assert "errors" not in resp.json()
    ex_id = resp.json()["data"]["createExercise"]["id"]

    create_routine_mutation = """
    mutation CreateRoutine($input: CreateRoutineInput!) {
        createRoutine(input: $input) { id name }
    }
    """
    routine_vars = {"input": {"name": "Leg Day"}}
    resp = await client.post(
        "/graphql",
        json={"query": create_routine_mutation, "variables": routine_vars},
        headers=auth_headers,
    )
    assert "errors" not in resp.json()
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    add_ex_to_routine_mutation = """
    mutation AddEx($routineId: UUID!, $input: AddRoutineExerciseInput!) {
        addRoutineExercise(routineId: $routineId, input: $input) { id }
    }
    """
    add_ex_vars = {"routineId": routine_id, "input": {"exerciseId": ex_id, "order": 1}}
    resp = await client.post(
        "/graphql",
        json={"query": add_ex_to_routine_mutation, "variables": add_ex_vars},
        headers=auth_headers,
    )
    assert "errors" not in resp.json()

    # 4. Add Week and Planned Session
    add_week_mutation = """
    mutation AddWeek($mesoId: UUID!, $input: AddMesocycleWeekInput!) {
        addMesocycleWeek(mesocycleId: $mesoId, input: $input) { id weekNumber }
    }
    """
    week_vars = {
        "mesoId": meso_id,
        "input": {
            "weekNumber": 1,
            "weekType": "TRAINING",
            "startDate": "2026-04-01",
            "endDate": "2026-04-07",
        },
    }
    resp = await client.post(
        "/graphql", json={"query": add_week_mutation, "variables": week_vars}, headers=auth_headers
    )
    week_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    add_ps_mutation = """
    mutation AddPS($weekId: UUID!, $input: AddPlannedSessionInput!) {
        addPlannedSession(mesocycleWeekId: $weekId, input: $input) { id }
    }
    """
    ps_vars = {"weekId": week_id, "input": {"routineId": routine_id, "dayOfWeek": 1}}
    resp = await client.post(
        "/graphql", json={"query": add_ps_mutation, "variables": ps_vars}, headers=auth_headers
    )
    ps_id = resp.json()["data"]["addPlannedSession"]["id"]

    # 5. Start Session
    start_session_mutation = """
    mutation StartSession($psId: UUID!) {
        createSession(input: {plannedSessionId: $psId}) {
            id
            status
            exercises {
                id
                exercise { name }
                sets { id setNumber }
            }
        }
    }
    """
    resp = await client.post(
        "/graphql",
        json={"query": start_session_mutation, "variables": {"psId": ps_id}},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    session_data = resp.json()["data"]["createSession"]
    session_id = session_data["id"]
    assert session_data["status"] == "PLANNED"

    # Actually start it
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { startSession(id: "%s") { id status } }' % session_id},
        headers=auth_headers,
    )
    assert resp.json()["data"]["startSession"]["status"] == "IN_PROGRESS"

    # 6. Log a set
    # First get the set ID
    set_id = session_data["exercises"][0]["sets"][0]["id"]
    log_set_mutation = """
    mutation LogSet($setId: UUID!, $input: LogSetResultInput!) {
        logSetResult(setId: $setId, input: $input) {
            id
            actualReps
            actualWeightKg
        }
    }
    """
    log_vars = {"setId": set_id, "input": {"actualReps": 10, "actualWeightKg": 100.0}}
    resp = await client.post(
        "/graphql", json={"query": log_set_mutation, "variables": log_vars}, headers=auth_headers
    )
    assert resp.status_code == 200
    log_data = resp.json()["data"]["logSetResult"]
    assert log_data["actualReps"] == 10
    assert float(log_data["actualWeightKg"]) == 100.0


@pytest.mark.anyio
async def test_insights_api(client: AsyncClient, auth_headers: dict):
    # Setup: Create Exercise, Routine, Mesocycle, Week, PlannedSession, Session, Log Set
    # 1. Create Exercise
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Deadlift"}) { id } }'},
        headers=auth_headers,
    )
    ex_id = resp.json()["data"]["createExercise"]["id"]

    # 2. Create Routine
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Back Day"}) { id } }'},
        headers=auth_headers,
    )
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    # Add Exercise to Routine
    await client.post(
        "/graphql",
        json={
            "query": "mutation AddEx($rid: UUID!, $eid: UUID!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: 1}) { id } }",
            "variables": {"rid": routine_id, "eid": ex_id},
        },
        headers=auth_headers,
    )

    # 3. Create Mesocycle
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Insight Meso", startDate: "2026-04-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    # 4. Add Week & Planned Session
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation AddW($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 1, weekType: TRAINING, startDate: "2026-04-01", endDate: "2026-04-07"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation AddPS($wid: UUID!, $rid: UUID!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: 1}) { id } }",
            "variables": {"wid": week_id, "rid": routine_id},
        },
        headers=auth_headers,
    )
    ps_id = resp.json()["data"]["addPlannedSession"]["id"]

    # 5. Create & Complete Session
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation CreateS($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id exercises { sets { id } } } }",
            "variables": {"psid": ps_id},
        },
        headers=auth_headers,
    )
    session_data = resp.json()["data"]["createSession"]
    session_id = session_data["id"]
    set_id = session_data["exercises"][0]["sets"][0]["id"]

    await client.post(
        "/graphql",
        json={"query": 'mutation { startSession(id: "%s") { id } }' % session_id},
        headers=auth_headers,
    )

    await client.post(
        "/graphql",
        json={
            "query": "mutation Log($sid: UUID!) { logSetResult(setId: $sid, input: {actualReps: 5, actualWeightKg: 140.0}) { id } }",
            "variables": {"sid": set_id},
        },
        headers=auth_headers,
    )

    await client.post(
        "/graphql",
        json={"query": 'mutation { completeSession(id: "%s") { id } }' % session_id},
        headers=auth_headers,
    )

    # 6. Query Insights
    # Volume Insight
    vol_query = """
    query GetVolume($mid: UUID!) {
        mesocycleVolumeInsight(mesocycleId: $mid) {
            mesocycleId
            totalSets
            weeklyVolumes { weekNumber setCount }
        }
    }
    """
    resp = await client.post(
        "/graphql", json={"query": vol_query, "variables": {"mid": meso_id}}, headers=auth_headers
    )
    assert resp.status_code == 200
    vol_data = resp.json()["data"]["mesocycleVolumeInsight"]
    assert vol_data["totalSets"] >= 1

    # Progressive Overload Insight
    po_query = """
    query GetPO($mid: UUID!, $eid: UUID!) {
        progressiveOverloadInsight(mesocycleId: $mid, exerciseId: $eid) {
            exerciseId
            weeklyProgress { weekNumber maxWeight avgReps }
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
    assert len(po_data["weeklyProgress"]) >= 1
    assert float(po_data["weeklyProgress"][0]["maxWeight"]) == 140.0

    # Exercise History
    hist_query = """
    query GetHist($eid: UUID!) {
        exerciseHistory(exerciseId: $eid) {
            items { id status }
        }
    }
    """
    resp = await client.post(
        "/graphql", json={"query": hist_query, "variables": {"eid": ex_id}}, headers=auth_headers
    )
    assert resp.status_code == 200
    hist_items = resp.json()["data"]["exerciseHistory"]["items"]
    assert any(h["id"] == session_id for h in hist_items)


@pytest.mark.anyio
async def test_calendar_api(client: AsyncClient, auth_headers: dict):
    # Query calendar range
    query = """
    query GetCalendar($start: Date!, $end: Date!) {
        calendarRange(startDate: $start, endDate: $end) {
            date
            isRestDay
            plannedSession { id }
            session { id }
        }
    }
    """
    variables = {"start": "2026-04-01", "end": "2026-04-07"}
    resp = await client.post(
        "/graphql", json={"query": query, "variables": variables}, headers=auth_headers
    )
    assert resp.status_code == 200
    days = resp.json()["data"]["calendarRange"]
    assert len(days) == 7


@pytest.mark.anyio
async def test_backup_api(client: AsyncClient, auth_headers: dict):
    mutation = """
    mutation {
        triggerBackup {
            success
            filename
        }
    }
    """
    resp = await client.post("/graphql", json={"query": mutation}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]["triggerBackup"]
    assert data["success"] is True
    assert data["filename"] is not None


@pytest.mark.anyio
async def test_crud_mutations(client: AsyncClient, auth_headers: dict):
    # 1. Create and Update Exercise
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Old Name"}) { id } }'},
        headers=auth_headers,
    )
    ex_id = resp.json()["data"]["createExercise"]["id"]

    update_mutation = """
    mutation UpdateEx($id: UUID!, $input: UpdateExerciseInput!) {
        updateExercise(id: $id, input: $input) { id name }
    }
    """
    resp = await client.post(
        "/graphql",
        json={"query": update_mutation, "variables": {"id": ex_id, "input": {"name": "New Name"}}},
        headers=auth_headers,
    )
    assert resp.json()["data"]["updateExercise"]["name"] == "New Name"

    # 2. Delete Exercise
    delete_mutation = "mutation DeleteEx($id: UUID!) { deleteExercise(id: $id) }"
    resp = await client.post(
        "/graphql",
        json={"query": delete_mutation, "variables": {"id": ex_id}},
        headers=auth_headers,
    )
    assert resp.json()["data"]["deleteExercise"] is True

    # Verify deleted
    resp = await client.post(
        "/graphql", json={"query": '{ exercise(id: "%s") { id } }' % ex_id}, headers=auth_headers
    )
    # Depending on implementation, it might return null or error.
    # Usually clean architecture returns 404/Error if not found.
    assert "errors" in resp.json() or resp.json()["data"]["exercise"] is None


@pytest.mark.anyio
async def test_bodyweight_api(client: AsyncClient, auth_headers: dict):

    # 1. Log Bodyweight
    mutation = """
    mutation LogBodyweight($input: LogBodyweightInput!) {
        logBodyweight(input: $input) {
            id
            weightKg
            recordedAt
        }
    }
    """
    variables = {
        "input": {"weightKg": 85.5, "recordedAt": "2026-03-23T10:00:00Z", "notes": "Morning weight"}
    }

    response = await client.post(
        "/graphql", json={"query": mutation, "variables": variables}, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert float(data["data"]["logBodyweight"]["weightKg"]) == 85.5

    # 2. Query Bodyweights
    query = "{ bodyweightLogs { items { weightKg } } }"
    response = await client.post("/graphql", json={"query": query}, headers=auth_headers)
    assert response.status_code == 200
    # Use float comparison as some JSON decoders might return numbers as strings
    item = response.json()["data"]["bodyweightLogs"]["items"][0]
    assert float(item["weightKg"]) == 85.5


@pytest.mark.anyio
async def test_error_handling_api(client: AsyncClient, auth_headers: dict):
    # Test invalid UUID
    query = """
    query GetExercise($id: UUID!) {
        exercise(id: $id) { id }
    }
    """
    variables = {"id": "not-a-uuid"}

    response = await client.post(
        "/graphql", json={"query": query, "variables": variables}, headers=auth_headers
    )
    # Strawberry/GraphQL usually returns 200 with errors for validation
    assert response.status_code == 200
    assert "errors" in response.json()


@pytest.mark.anyio
async def test_auth_middleware(client: AsyncClient):
    # Invalid API Key on protected route
    response = await client.post(
        "/graphql",
        json={"query": "{ exercises { items { name } } }"},
        headers={"Authorization": "Bearer invalid"},
    )
    assert response.status_code == 401

    # Missing Auth header on GraphQL
    response = await client.post("/graphql", json={"query": "{ exercises { items { name } } }"})
    assert response.status_code == 401

    # Health check is public (based on middleware code)
    response = await client.get("/health", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 200


@pytest.mark.anyio
async def test_routine_crud_api(client: AsyncClient, auth_headers: dict):
    # 1. Create Routine
    create_mutation = """
    mutation CreateRoutine($input: CreateRoutineInput!) {
        createRoutine(input: $input) { id name description }
    }
    """
    variables = {"input": {"name": "Initial Routine", "description": "Desc"}}
    resp = await client.post(
        "/graphql",
        json={"query": create_mutation, "variables": variables},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]["createRoutine"]
    routine_id = data["id"]
    assert data["name"] == "Initial Routine"

    # 2. Update Routine
    update_mutation = """
    mutation UpdateRoutine($id: UUID!, $input: UpdateRoutineInput!) {
        updateRoutine(id: $id, input: $input) { id name description }
    }
    """
    variables = {"id": routine_id, "input": {"name": "Updated Routine"}}
    resp = await client.post(
        "/graphql",
        json={"query": update_mutation, "variables": variables},
        headers=auth_headers,
    )
    assert resp.json()["data"]["updateRoutine"]["name"] == "Updated Routine"

    # 3. Delete Routine
    delete_mutation = "mutation DeleteRoutine($id: UUID!) { deleteRoutine(id: $id) }"
    resp = await client.post(
        "/graphql",
        json={"query": delete_mutation, "variables": {"id": routine_id}},
        headers=auth_headers,
    )
    assert resp.json()["data"]["deleteRoutine"] is True


@pytest.mark.anyio
async def test_mesocycle_crud_api(client: AsyncClient, auth_headers: dict):
    # 1. Create Mesocycle
    create_mutation = """
    mutation CreateMesocycle($input: CreateMesocycleInput!) {
        createMesocycle(input: $input) { id name status }
    }
    """
    variables = {
        "input": {
            "name": "Initial Meso",
            "startDate": "2026-04-01",
        }
    }
    resp = await client.post(
        "/graphql",
        json={"query": create_mutation, "variables": variables},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]["createMesocycle"]
    meso_id = data["id"]
    assert data["name"] == "Initial Meso"

    # 2. Update Mesocycle
    update_mutation = """
    mutation UpdateMesocycle($id: UUID!, $input: UpdateMesocycleInput!) {
        updateMesocycle(id: $id, input: $input) { id name status }
    }
    """
    variables = {"id": meso_id, "input": {"name": "Updated Meso"}}
    resp = await client.post(
        "/graphql",
        json={"query": update_mutation, "variables": variables},
        headers=auth_headers,
    )
    assert resp.json()["data"]["updateMesocycle"]["name"] == "Updated Meso"

    # 3. Delete Mesocycle
    delete_mutation = "mutation DeleteMesocycle($id: UUID!) { deleteMesocycle(id: $id) }"
    resp = await client.post(
        "/graphql",
        json={"query": delete_mutation, "variables": {"id": meso_id}},
        headers=auth_headers,
    )
    assert resp.json()["data"]["deleteMesocycle"] is True
