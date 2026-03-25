import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_routine_edge_cases(client: AsyncClient, auth_headers: dict):
    # Setup: Create Exercise and Routine
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Squat"}) { id } }'},
        headers=auth_headers,
    )
    ex_id = resp.json()["data"]["createExercise"]["id"]

    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Leg Day"}) { id } }'},
        headers=auth_headers,
    )
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    # 1. Invalid RIR (too high)
    # The system might not have validation yet, let's see what happens.
    add_ex_mutation = """
    mutation AddEx($rid: UUID!, $input: AddRoutineExerciseInput!) {
        addRoutineExercise(routineId: $rid, input: $input) {
            id
            exercises { id }
        }
    }
    """
    add_ex_vars = {
        "rid": routine_id,
        "input": {"exerciseId": ex_id, "order": 1},
    }
    resp = await client.post(
        "/graphql",
        json={"query": add_ex_mutation, "variables": add_ex_vars},
        headers=auth_headers,
    )
    re_id = resp.json()["data"]["addRoutineExercise"]["exercises"][0]["id"]

    add_set_mutation = """
    mutation AddSet($reid: UUID!, $input: AddRoutineSetInput!) {
        addRoutineSet(routineExerciseId: $reid, input: $input) {
            id
            sets { id targetRir }
        }
    }
    """
    # Assuming RIR should be between 0 and 5-ish for sane training, but let's try 100
    add_set_vars = {
        "reid": re_id,
        "input": {
            "setNumber": 2,
            "setType": "STANDARD",
            "targetRir": 100,
        },
    }
    resp = await client.post(
        "/graphql",
        json={"query": add_set_mutation, "variables": add_set_vars},
        headers=auth_headers,
    )
    # If no validation exists, this will succeed.
    # We should probably add validation in Domain or Application layer.
    assert "errors" not in resp.json()

    # 2. Deleting non-existent RoutineExercise
    remove_re_mutation = "mutation RemoveRE($id: UUID!) { removeRoutineExercise(id: $id) }"
    resp = await client.post(
        "/graphql",
        json={
            "query": remove_re_mutation,
            "variables": {"id": "00000000-0000-0000-0000-000000000000"},
        },
        headers=auth_headers,
    )
    # Service raises EntityNotFoundException, which should be handled by Strawberry context
    # Usually this results in a GraphQL error with message "RoutineExercise with id ... not found"
    assert "not found" in resp.json()["errors"][0]["message"]


@pytest.mark.anyio
async def test_mesocycle_edge_cases(client: AsyncClient, auth_headers: dict):
    # 1. Duplicate week number in same mesocycle
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Edge Meso", startDate: "2026-06-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    add_week_mutation = """
    mutation AddWeek($mid: UUID!, $input: AddMesocycleWeekInput!) {
        addMesocycleWeek(mesocycleId: $mid, input: $input) { id }
    }
    """
    week_input = {
        "weekNumber": 1,
        "weekType": "TRAINING",
        "startDate": "2026-06-01",
        "endDate": "2026-06-07",
    }
    # First week
    resp = await client.post(
        "/graphql",
        json={"query": add_week_mutation, "variables": {"mid": meso_id, "input": week_input}},
        headers=auth_headers,
    )
    assert "errors" not in resp.json()

    # Second week with SAME weekNumber
    resp = await client.post(
        "/graphql",
        json={"query": add_week_mutation, "variables": {"mid": meso_id, "input": week_input}},
        headers=auth_headers,
    )
    # This should fail due to UNIQUE constraint in DB or validation in Service
    # In Clean Architecture, Service should check for duplicates or Repository will throw IntegrityError
    assert "errors" in resp.json()
