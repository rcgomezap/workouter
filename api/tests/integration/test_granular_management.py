import pytest
from httpx import AsyncClient
from uuid import UUID


@pytest.mark.anyio
async def test_routine_granular_management_api(client: AsyncClient, auth_headers: dict):
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
        json={"query": 'mutation { createRoutine(input: {name: "Chest Day"}) { id } }'},
        headers=auth_headers,
    )
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    # 3. Add Exercise to Routine
    add_ex_mutation = """
    mutation AddEx($rid: UUID!, $input: AddRoutineExerciseInput!) {
        addRoutineExercise(routineId: $rid, input: $input) {
            id
            exercises {
                id
                order
                notes
            }
        }
    }
    """
    add_ex_vars = {
        "rid": routine_id,
        "input": {"exerciseId": ex_id, "order": 1, "notes": "Initial note"},
    }
    resp = await client.post(
        "/graphql",
        json={"query": add_ex_mutation, "variables": add_ex_vars},
        headers=auth_headers,
    )
    routine_data = resp.json()["data"]["addRoutineExercise"]
    re_id = routine_data["exercises"][0]["id"]
    assert routine_data["exercises"][0]["notes"] == "Initial note"

    # 4. Update Routine Exercise
    update_re_mutation = """
    mutation UpdateRE($id: UUID!, $input: UpdateRoutineExerciseInput!) {
        updateRoutineExercise(id: $id, input: $input) {
            id
            notes
            order
        }
    }
    """
    update_re_vars = {"id": re_id, "input": {"notes": "Updated note", "order": 2}}
    resp = await client.post(
        "/graphql",
        json={"query": update_re_mutation, "variables": update_re_vars},
        headers=auth_headers,
    )
    re_data = resp.json()["data"]["updateRoutineExercise"]
    assert re_data["notes"] == "Updated note"
    assert re_data["order"] == 2

    # 5. Add Routine Set
    add_set_mutation = """
    mutation AddSet($reid: UUID!, $input: AddRoutineSetInput!) {
        addRoutineSet(routineExerciseId: $reid, input: $input) {
            id
            sets {
                id
                targetRepsMin
                targetRepsMax
            }
        }
    }
    """
    add_set_vars = {
        "reid": re_id,
        "input": {
            "setNumber": 1,
            "setType": "STANDARD",
            "targetRepsMin": 8,
            "targetRepsMax": 12,
            "targetRir": 2,
        },
    }
    resp = await client.post(
        "/graphql",
        json={"query": add_set_mutation, "variables": add_set_vars},
        headers=auth_headers,
    )
    re_data = resp.json()["data"]["addRoutineSet"]
    set_id = re_data["sets"][0]["id"]
    assert re_data["sets"][0]["targetRepsMin"] == 8

    # 6. Update Routine Set
    update_set_mutation = """
    mutation UpdateSet($id: UUID!, $input: UpdateRoutineSetInput!) {
        updateRoutineSet(id: $id, input: $input) {
            id
            targetRepsMin
            targetRepsMax
        }
    }
    """
    update_set_vars = {"id": set_id, "input": {"targetRepsMin": 10, "targetRepsMax": 15}}
    resp = await client.post(
        "/graphql",
        json={"query": update_set_mutation, "variables": update_set_vars},
        headers=auth_headers,
    )
    set_data = resp.json()["data"]["updateRoutineSet"]
    assert set_data["targetRepsMin"] == 10
    assert set_data["targetRepsMax"] == 15

    # 7. Remove Routine Set
    remove_set_mutation = "mutation RemoveSet($id: UUID!) { removeRoutineSet(id: $id) }"
    resp = await client.post(
        "/graphql",
        json={"query": remove_set_mutation, "variables": {"id": set_id}},
        headers=auth_headers,
    )
    assert resp.json()["data"]["removeRoutineSet"] is True

    # 8. Remove Routine Exercise
    remove_re_mutation = "mutation RemoveRE($id: UUID!) { removeRoutineExercise(id: $id) }"
    resp = await client.post(
        "/graphql",
        json={"query": remove_re_mutation, "variables": {"id": re_id}},
        headers=auth_headers,
    )
    assert resp.json()["data"]["removeRoutineExercise"] is True


@pytest.mark.anyio
async def test_mesocycle_granular_management_api(client: AsyncClient, auth_headers: dict):
    # 1. Create Mesocycle
    create_meso_mutation = """
    mutation CreateMeso($input: CreateMesocycleInput!) {
        createMesocycle(input: $input) { id }
    }
    """
    meso_vars = {"input": {"name": "Granular Meso", "startDate": "2026-05-01"}}
    resp = await client.post(
        "/graphql",
        json={"query": create_meso_mutation, "variables": meso_vars},
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    # 2. Add Mesocycle Week
    add_week_mutation = """
    mutation AddWeek($mid: UUID!, $input: AddMesocycleWeekInput!) {
        addMesocycleWeek(mesocycleId: $mid, input: $input) {
            id
            weekNumber
            weekType
        }
    }
    """
    week_vars = {
        "mid": meso_id,
        "input": {
            "weekNumber": 1,
            "weekType": "TRAINING",
            "startDate": "2026-05-01",
            "endDate": "2026-05-07",
        },
    }
    resp = await client.post(
        "/graphql",
        json={"query": add_week_mutation, "variables": week_vars},
        headers=auth_headers,
    )
    week_data = resp.json()["data"]["addMesocycleWeek"]
    week_id = week_data["id"]
    assert week_data["weekNumber"] == 1

    # 3. Update Mesocycle Week
    update_week_mutation = """
    mutation UpdateWeek($id: UUID!, $input: UpdateMesocycleWeekInput!) {
        updateMesocycleWeek(id: $id, input: $input) {
            id
            weekType
        }
    }
    """
    update_week_vars = {"id": week_id, "input": {"weekType": "DELOAD"}}
    resp = await client.post(
        "/graphql",
        json={"query": update_week_mutation, "variables": update_week_vars},
        headers=auth_headers,
    )
    assert resp.json()["data"]["updateMesocycleWeek"]["weekType"] == "DELOAD"

    # 4. Add Planned Session
    # First need a routine
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Meso Routine"}) { id } }'},
        headers=auth_headers,
    )
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    add_ps_mutation = """
    mutation AddPS($wid: UUID!, $input: AddPlannedSessionInput!) {
        addPlannedSession(mesocycleWeekId: $wid, input: $input) {
            id
            dayOfWeek
            notes
        }
    }
    """
    ps_vars = {
        "wid": week_id,
        "input": {"routineId": routine_id, "dayOfWeek": 1, "notes": "Initial PS"},
    }
    resp = await client.post(
        "/graphql",
        json={"query": add_ps_mutation, "variables": ps_vars},
        headers=auth_headers,
    )
    ps_data = resp.json()["data"]["addPlannedSession"]
    ps_id = ps_data["id"]
    assert ps_data["notes"] == "Initial PS"

    # 5. Update Planned Session
    update_ps_mutation = """
    mutation UpdatePS($id: UUID!, $input: UpdatePlannedSessionInput!) {
        updatePlannedSession(id: $id, input: $input) {
            id
            notes
            dayOfWeek
        }
    }
    """
    update_ps_vars = {"id": ps_id, "input": {"notes": "Updated PS", "dayOfWeek": 2}}
    resp = await client.post(
        "/graphql",
        json={"query": update_ps_mutation, "variables": update_ps_vars},
        headers=auth_headers,
    )
    ps_data = resp.json()["data"]["updatePlannedSession"]
    assert ps_data["notes"] == "Updated PS"
    assert ps_data["dayOfWeek"] == 2

    # 6. Remove Planned Session
    remove_ps_mutation = "mutation RemovePS($id: UUID!) { removePlannedSession(id: $id) }"
    resp = await client.post(
        "/graphql",
        json={"query": remove_ps_mutation, "variables": {"id": ps_id}},
        headers=auth_headers,
    )
    assert resp.json()["data"]["removePlannedSession"] is True

    # 7. Remove Mesocycle Week
    remove_week_mutation = "mutation RemoveWeek($id: UUID!) { removeMesocycleWeek(id: $id) }"
    resp = await client.post(
        "/graphql",
        json={"query": remove_week_mutation, "variables": {"id": week_id}},
        headers=auth_headers,
    )
    assert resp.json()["data"]["removeMesocycleWeek"] is True
