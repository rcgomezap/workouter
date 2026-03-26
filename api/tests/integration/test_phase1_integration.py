import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.infrastructure.database.models.routine import RoutineTable
from app.infrastructure.database.models.session import SessionTable, SessionSetTable
from app.infrastructure.database.models.bodyweight import BodyweightLogTable
from app.presentation.graphql.schema import schema


# 1. Schema Consistency Tests
async def test_schema_export_matches_runtime():
    """Ensure exported schema.graphql is up-to-date with runtime schema."""
    try:
        with open("schema.graphql", "r") as f:
            exported_schema = f.read().strip()
    except FileNotFoundError:
        pytest.fail("schema.graphql not found. Please run 'src/export_schema.py > schema.graphql'")

    runtime_schema = str(schema).strip()

    # DEBUG: Print runtime schema snippet for exerciseHistory
    import re

    match = re.search(r"exerciseHistory\(.*?\)", runtime_schema)
    if match:
        print(f"DEBUG: runtime exerciseHistory: {match.group(0)}")
    else:
        print("DEBUG: exerciseHistory not found in runtime schema")

    # Normalize line endings and whitespace for comparison
    exported_schema = "\n".join(
        [line.rstrip() for line in exported_schema.splitlines() if line.strip()]
    )
    runtime_schema = "\n".join(
        [line.rstrip() for line in runtime_schema.splitlines() if line.strip()]
    )

    assert exported_schema == runtime_schema, (
        "schema.graphql is out of sync with the runtime schema. "
        "Please run 'PYTHONPATH=src uv run python src/export_schema.py > schema.graphql' to update it."
    )


# 2. Exercise History Integration Tests
@pytest.mark.anyio
async def test_exercise_history_full_flow(client: AsyncClient, auth_headers: dict):
    """Test exercise history across multiple routines and sessions"""
    # 1. Create Exercise
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Squat"}) { id } }'},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    ex_id = resp.json()["data"]["createExercise"]["id"]

    # 2. Create Routines A and B
    routine_ids = []
    for name in ["Routine A", "Routine B"]:
        resp = await client.post(
            "/graphql",
            json={"query": f'mutation {{ createRoutine(input: {{name: "{name}"}}) {{ id }} }}'},
            headers=auth_headers,
        )
        routine_ids.append(resp.json()["data"]["createRoutine"]["id"])

    routine_a_id, routine_b_id = routine_ids

    # 3. Add Exercise to both routines
    for rid in routine_ids:
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
            "query": 'mutation { createMesocycle(input: {name: "Meso 1", startDate: "2026-05-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    # 5. Create 2 weeks
    week_ids = []
    for i in range(1, 3):
        start_date = (datetime(2026, 5, 1) + timedelta(weeks=i - 1)).strftime("%Y-%m-%d")
        end_date = (datetime(2026, 5, 7) + timedelta(weeks=i - 1)).strftime("%Y-%m-%d")
        resp = await client.post(
            "/graphql",
            json={
                "query": f'mutation AddW($mid: UUID!) {{ addMesocycleWeek(mesocycleId: $mid, input: {{weekNumber: {i}, weekType: TRAINING, startDate: "{start_date}", endDate: "{end_date}"}}) {{ id }} }}',
                "variables": {"mid": meso_id},
            },
            headers=auth_headers,
        )
        week_ids.append(resp.json()["data"]["addMesocycleWeek"]["id"])

    # 6. Create Sessions (2 per routine, total 4)
    # Week 1: Routine A (Session 1), Routine B (Session 2)
    # Week 2: Routine A (Session 3), Routine B (Session 4)
    sessions = []
    for week_idx, week_id in enumerate(week_ids):
        for routine_idx, routine_id in enumerate(routine_ids):
            # Create Planned Session
            resp = await client.post(
                "/graphql",
                json={
                    "query": "mutation AddPS($wid: UUID!, $rid: UUID!, $dow: Int!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: $dow}) { id } }",
                    "variables": {"wid": week_id, "rid": routine_id, "dow": routine_idx + 1},
                },
                headers=auth_headers,
            )

            # Check for errors
            if "errors" in resp.json():
                pytest.fail(f"AddPlannedSession failed: {resp.json()}")

            ps_id = resp.json()["data"]["addPlannedSession"]["id"]

            # Create Session
            resp = await client.post(
                "/graphql",
                json={
                    "query": "mutation CreateS($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id } }",
                    "variables": {"psid": ps_id},
                },
                headers=auth_headers,
            )
            session_id = resp.json()["data"]["createSession"]["id"]

            # Start Session
            await client.post(
                "/graphql",
                json={"query": f'mutation {{ startSession(id: "{session_id}") {{ id }} }}'},
                headers=auth_headers,
            )

            # Add Set (simulating logging)
            # Find session exercise id first
            resp = await client.post(
                "/graphql",
                json={
                    "query": f'query {{ session(id: "{session_id}") {{ exercises {{ id exercise {{ id }} }} }} }}'
                },
                headers=auth_headers,
            )
            sess_exercises = resp.json()["data"]["session"]["exercises"]
            sess_ex_id = next(ex["id"] for ex in sess_exercises if ex["exercise"]["id"] == ex_id)

            await client.post(
                "/graphql",
                json={
                    "query": "mutation AddSet($seid: UUID!) { addSet(sessionExerciseId: $seid, input: {setNumber: 1, setType: NORMAL, weightKg: 100, reps: 5, rir: 2}) { id } }",
                    "variables": {"seid": sess_ex_id},
                },
                headers=auth_headers,
            )

            # Complete Session
            await client.post(
                "/graphql",
                json={"query": f'mutation {{ completeSession(id: "{session_id}") {{ id }} }}'},
                headers=auth_headers,
            )
            sessions.append({"id": session_id, "routine_id": routine_id})

    # 7. Query History without filter (expect 4 sessions)
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
    data = resp.json()["data"]["exerciseHistory"]
    assert data["total"] == 4

    # 8. Query History with Routine A filter (expect 2 sessions)
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
    data = resp.json()["data"]["exerciseHistory"]
    assert data["total"] == 2
    for item in data["items"]:
        assert item["routineId"] == routine_a_id

# 5. Cascade Deletion Tests
@pytest.mark.anyio
async def test_delete_routine_cascades(client: AsyncClient, auth_headers: dict):
    """Test deleting a routine properly cascades/unlinks sessions and logs"""
    # 1. Create Routine
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "To Delete"}) { id } }'},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    # 2. Create Exercise
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Ex To Delete"}) { id } }'},
        headers=auth_headers,
    )
    ex_id = resp.json()["data"]["createExercise"]["id"]

    # 3. Add Exercise to Routine
    await client.post(
        "/graphql",
        json={
            "query": "mutation AddEx($rid: UUID!, $eid: UUID!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: 1}) { id } }",
            "variables": {"rid": routine_id, "eid": ex_id},
        },
        headers=auth_headers,
    )

    # 4. Create Mesocycle & Week
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Meso Delete", startDate: "2026-06-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation AddW($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 1, weekType: TRAINING, startDate: "2026-06-01", endDate: "2026-06-07"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    # 5. Create Planned Session linked to Routine
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation AddPS($wid: UUID!, $rid: UUID!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: 1}) { id } }",
            "variables": {"wid": week_id, "rid": routine_id},
        },
        headers=auth_headers,
    )
    if "errors" in resp.json():
        pytest.fail(f"AddPlannedSession failed: {resp.json()}")

    ps_id = resp.json()["data"]["addPlannedSession"]["id"]

    # 6. Create Session
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation CreateS($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id } }",
            "variables": {"psid": ps_id},
        },
        headers=auth_headers,
    )
    session_id = resp.json()["data"]["createSession"]["id"]

    # 7. Delete Routine
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation DeleteR($id: UUID!) { deleteRoutine(id: $id) }",
            "variables": {"id": routine_id},
        },
        headers=auth_headers,
    )

    # If the mutation fails due to integrity error, it's a bug in the data model config for cascading.
    if resp.status_code != 200 or "errors" in resp.json():
        # Ideally we should fail here, but let's see the error.
        print("Delete failed:", resp.json())
        pytest.fail(f"Delete Routine failed: {resp.json()}")

    assert resp.json().get("data", {}).get("deleteRoutine") is True

    # 8. Verify Session still exists but routine_id is None (or session is deleted if that was the intent)
    resp = await client.post(
        "/graphql",
        json={"query": f'query {{ session(id: "{session_id}") {{ id routineId }} }}'},
        headers=auth_headers,
    )

    # Note: If cascade delete was configured on PlannedSession->Routine, the PlannedSession would be deleted.
    # And if cascade delete was on Session->PlannedSession, the Session would be deleted.
    # So retrieving it might return null.

    session_data = resp.json()["data"]["session"]

    if session_data:
        # If session exists, routineId must be null if it was unlinked, or it might still be there if we didn't refresh?
        # But if it was deleted, session_data is None.
        assert session_data["routineId"] is None, "Session should be unlinked from deleted routine"
    else:
        # Session deleted - also valid "cascade" behavior
        pass


# 6. Concurrent Operation Tests
@pytest.mark.anyio
async def test_concurrent_set_logging(client: AsyncClient, auth_headers: dict):
    """Test multiple users logging sets simultaneously (simulated)"""
    # 1. Setup Session
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Concurrent Routine"}) { id } }'},
        headers=auth_headers,
    )
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Concurrent Ex"}) { id } }'},
        headers=auth_headers,
    )
    ex_id = resp.json()["data"]["createExercise"]["id"]

    await client.post(
        "/graphql",
        json={
            "query": "mutation AddEx($rid: UUID!, $eid: UUID!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: 1}) { id } }",
            "variables": {"rid": routine_id, "eid": ex_id},
        },
        headers=auth_headers,
    )

    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Concurrent Meso", startDate: "2026-07-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation AddW($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 1, weekType: TRAINING, startDate: "2026-07-01", endDate: "2026-07-07"}) { id } }',
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
    if "errors" in resp.json():
        pytest.fail(f"AddPlannedSession failed: {resp.json()}")

    ps_id = resp.json()["data"]["addPlannedSession"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation CreateS($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id } }",
            "variables": {"psid": ps_id},
        },
        headers=auth_headers,
    )
    session_id = resp.json()["data"]["createSession"]["id"]

    await client.post(
        "/graphql",
        json={"query": f'mutation {{ startSession(id: "{session_id}") {{ id }} }}'},
        headers=auth_headers,
    )

    # Get SessionExercise ID
    resp = await client.post(
        "/graphql",
        json={"query": f'query {{ session(id: "{session_id}") {{ exercises {{ id }} }} }}'},
        headers=auth_headers,
    )
    sex_id = resp.json()["data"]["session"]["exercises"][0]["id"]

    # 2. Concurrent Requests to add sets
    async def add_set(idx):
        return await client.post(
            "/graphql",
            json={
                "query": "mutation AddSet($seid: UUID!, $sn: Int!) { addSessionSet(sessionExerciseId: $seid, input: {setNumber: $sn, setType: STANDARD, targetWeightKg: 100, targetReps: 5}) { id } }",
                "variables": {"seid": sex_id, "sn": idx},
            },
            headers=auth_headers,
        )

    # Launch 5 concurrent requests
    # Start from 2 because createSession copies the routine's default set (setNumber=1)
    tasks = [add_set(i) for i in range(2, 7)]
    responses = await asyncio.gather(*tasks)

    for r in responses:
        assert r.status_code == 200, r.text
        assert "errors" not in r.json()

        # Verify 6 sets created (1 default + 5 added)
        resp = await client.post(
            "/graphql",
            json={
                "query": f'query {{ session(id: "{session_id}") {{ exercises {{ sets {{ id setNumber }} }} }} }}'
            },
            headers=auth_headers,
        )
        sets = resp.json()["data"]["session"]["exercises"][0]["sets"]
        assert len(sets) == 6
        set_numbers = sorted([s["setNumber"] for s in sets])
        assert set_numbers == [1, 2, 3, 4, 5, 6]
