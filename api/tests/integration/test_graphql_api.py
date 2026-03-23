import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import date


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
