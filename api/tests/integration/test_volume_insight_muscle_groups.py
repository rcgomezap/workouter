"""Integration tests for Volume Insight with per-muscle-group weekly breakdown."""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_volume_without_filter_multiple_muscle_groups_per_week(
    client: AsyncClient, auth_headers: dict
):
    """Test that weekly volumes show per-muscle-group breakdown when no filter is applied."""
    # 1. Get muscle groups
    resp = await client.post(
        "/graphql",
        json={"query": "query { muscleGroups { id name } }"},
        headers=auth_headers,
    )
    muscle_groups = resp.json()["data"]["muscleGroups"]
    chest_mg = next(mg for mg in muscle_groups if mg["name"] == "Chest")
    biceps_mg = next(mg for mg in muscle_groups if mg["name"] == "Biceps")

    # 2. Create exercises with different muscle groups
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Bench Press"}) { id } }'},
        headers=auth_headers,
    )
    bench_id = resp.json()["data"]["createExercise"]["id"]

    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Bicep Curl"}) { id } }'},
        headers=auth_headers,
    )
    curl_id = resp.json()["data"]["createExercise"]["id"]

    # 3. Assign muscle groups
    await client.post(
        "/graphql",
        json={
            "query": "mutation Assign($eid: UUID!, $mgs: [MuscleGroupAssignmentInput!]!) { assignMuscleGroups(exerciseId: $eid, muscleGroupIds: $mgs) { id } }",
            "variables": {
                "eid": bench_id,
                "mgs": [{"muscleGroupId": chest_mg["id"], "role": "PRIMARY"}],
            },
        },
        headers=auth_headers,
    )

    await client.post(
        "/graphql",
        json={
            "query": "mutation Assign($eid: UUID!, $mgs: [MuscleGroupAssignmentInput!]!) { assignMuscleGroups(exerciseId: $eid, muscleGroupIds: $mgs) { id } }",
            "variables": {
                "eid": curl_id,
                "mgs": [{"muscleGroupId": biceps_mg["id"], "role": "PRIMARY"}],
            },
        },
        headers=auth_headers,
    )

    # 4. Create routine with both exercises
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Push Pull"}) { id } }'},
        headers=auth_headers,
    )
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Add($rid: UUID!, $eid: UUID!, $order: Int!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: $order}) { id } }",
            "variables": {"rid": routine_id, "eid": bench_id, "order": 1},
        },
        headers=auth_headers,
    )
    bench_re_id = resp.json()["data"]["addRoutineExercise"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Add($rid: UUID!, $eid: UUID!, $order: Int!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: $order}) { id } }",
            "variables": {"rid": routine_id, "eid": curl_id, "order": 2},
        },
        headers=auth_headers,
    )
    curl_re_id = resp.json()["data"]["addRoutineExercise"]["id"]

    # Add extra routine sets so sessions can log multiple sets per exercise
    for set_number in (2, 3, 4):
        await client.post(
            "/graphql",
            json={
                "query": "mutation AddSet($reid: UUID!, $input: AddRoutineSetInput!) { addRoutineSet(routineExerciseId: $reid, input: $input) { id } }",
                "variables": {
                    "reid": bench_re_id,
                    "input": {
                        "setNumber": set_number,
                        "setType": "STANDARD",
                        "targetRepsMin": 8,
                        "targetRepsMax": 12,
                        "targetRir": 2,
                    },
                },
            },
            headers=auth_headers,
        )

    for set_number in (2, 3):
        await client.post(
            "/graphql",
            json={
                "query": "mutation AddSet($reid: UUID!, $input: AddRoutineSetInput!) { addRoutineSet(routineExerciseId: $reid, input: $input) { id } }",
                "variables": {
                    "reid": curl_re_id,
                    "input": {
                        "setNumber": set_number,
                        "setType": "STANDARD",
                        "targetRepsMin": 8,
                        "targetRepsMax": 12,
                        "targetRir": 2,
                    },
                },
            },
            headers=auth_headers,
        )

    # 5. Create mesocycle with 2 weeks
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Volume Test", startDate: "2026-06-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation Add($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 1, weekType: TRAINING, startDate: "2026-06-01", endDate: "2026-06-07"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week1_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation Add($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 2, weekType: TRAINING, startDate: "2026-06-08", endDate: "2026-06-14"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week2_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    # 6. Create planned sessions
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Add($wid: UUID!, $rid: UUID!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: 1}) { id } }",
            "variables": {"wid": week1_id, "rid": routine_id},
        },
        headers=auth_headers,
    )
    ps1_id = resp.json()["data"]["addPlannedSession"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Add($wid: UUID!, $rid: UUID!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: 1}) { id } }",
            "variables": {"wid": week2_id, "rid": routine_id},
        },
        headers=auth_headers,
    )
    ps2_id = resp.json()["data"]["addPlannedSession"]["id"]

    # 7. Complete sessions with sets
    async def complete_session_with_sets(ps_id, bench_sets, curl_sets):
        resp = await client.post(
            "/graphql",
            json={
                "query": "mutation Create($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id exercises { id exercise { name } sets { id } } } }",
                "variables": {"psid": ps_id},
            },
            headers=auth_headers,
        )
        session_data = resp.json()["data"]["createSession"]
        session_id = session_data["id"]

        # Start session
        await client.post(
            "/graphql",
            json={"query": f'mutation {{ startSession(id: "{session_id}") {{ id }} }}'},
            headers=auth_headers,
        )

        # Log sets for each exercise
        for ex_data in session_data["exercises"]:
            ex_name = ex_data["exercise"]["name"]
            set_count = bench_sets if ex_name == "Bench Press" else curl_sets

            for i in range(set_count):
                set_id = ex_data["sets"][i]["id"] if i < len(ex_data["sets"]) else None
                if set_id:
                    await client.post(
                        "/graphql",
                        json={
                            "query": "mutation Log($sid: UUID!, $w: Decimal!, $r: Int!) { logSetResult(setId: $sid, input: {actualReps: $r, actualWeightKg: $w, actualRir: 2}) { id } }",
                            "variables": {"sid": set_id, "w": "100.0", "r": 10},
                        },
                        headers=auth_headers,
                    )

        # Complete session
        await client.post(
            "/graphql",
            json={"query": f'mutation {{ completeSession(id: "{session_id}") {{ id }} }}'},
            headers=auth_headers,
        )

    # Week 1: 1 set bench, 1 set curl
    await complete_session_with_sets(ps1_id, 1, 1)
    # Week 2: 1 set bench, 1 set curl
    await complete_session_with_sets(ps2_id, 1, 1)

    # 8. Query volume insight WITHOUT filter
    vol_query = """
    query GetVolume($mid: UUID!) {
        mesocycleVolumeInsight(mesocycleId: $mid) {
            mesocycleId
            totalSets
            weeklyVolumes { 
                weekNumber 
                muscleGroupId 
                muscleGroupName 
                setCount 
            }
            muscleGroupBreakdown {
                muscleGroupId
                muscleGroupName
                totalSets
            }
        }
    }
    """
    resp = await client.post(
        "/graphql",
        json={"query": vol_query, "variables": {"mid": meso_id}},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]["mesocycleVolumeInsight"]

    # 9. Assertions
    weekly_volumes = data["weeklyVolumes"]

    # Should have entries for week 1 (Chest + Biceps) and week 2 (Chest + Biceps) = 4 entries
    assert len(weekly_volumes) == 4

    # Find specific entries
    week1_chest = next(
        (wv for wv in weekly_volumes if wv["weekNumber"] == 1 and wv["muscleGroupName"] == "Chest"),
        None,
    )
    week1_biceps = next(
        (
            wv
            for wv in weekly_volumes
            if wv["weekNumber"] == 1 and wv["muscleGroupName"] == "Biceps"
        ),
        None,
    )
    week2_chest = next(
        (wv for wv in weekly_volumes if wv["weekNumber"] == 2 and wv["muscleGroupName"] == "Chest"),
        None,
    )
    week2_biceps = next(
        (
            wv
            for wv in weekly_volumes
            if wv["weekNumber"] == 2 and wv["muscleGroupName"] == "Biceps"
        ),
        None,
    )

    assert week1_chest is not None
    assert week1_chest["setCount"] == 1
    assert week1_chest["muscleGroupId"] == chest_mg["id"]

    assert week1_biceps is not None
    assert week1_biceps["setCount"] == 1
    assert week1_biceps["muscleGroupId"] == biceps_mg["id"]

    assert week2_chest is not None
    assert week2_chest["setCount"] == 1
    assert week2_chest["muscleGroupId"] == chest_mg["id"]

    assert week2_biceps is not None
    assert week2_biceps["setCount"] == 1
    assert week2_biceps["muscleGroupId"] == biceps_mg["id"]

    # Verify ordering: should be by week number, then muscle group name
    # Week 1: Biceps (alphabetically before Chest), Chest
    # Week 2: Biceps, Chest
    assert weekly_volumes[0]["weekNumber"] == 1
    assert weekly_volumes[0]["muscleGroupName"] == "Biceps"
    assert weekly_volumes[1]["weekNumber"] == 1
    assert weekly_volumes[1]["muscleGroupName"] == "Chest"
    assert weekly_volumes[2]["weekNumber"] == 2
    assert weekly_volumes[2]["muscleGroupName"] == "Biceps"
    assert weekly_volumes[3]["weekNumber"] == 2
    assert weekly_volumes[3]["muscleGroupName"] == "Chest"

    # Verify muscle group breakdown totals
    chest_breakdown = next(
        (mg for mg in data["muscleGroupBreakdown"] if mg["muscleGroupName"] == "Chest"), None
    )
    biceps_breakdown = next(
        (mg for mg in data["muscleGroupBreakdown"] if mg["muscleGroupName"] == "Biceps"), None
    )

    assert chest_breakdown is not None
    assert chest_breakdown["totalSets"] == 2  # 1 + 1
    assert biceps_breakdown is not None
    assert biceps_breakdown["totalSets"] == 2  # 1 + 1

    # Total sets should be sum of all muscle group sets
    assert data["totalSets"] == 4  # 2 + 2


@pytest.mark.anyio
async def test_volume_with_filter_single_muscle_group(client: AsyncClient, auth_headers: dict):
    """Test that filtering by muscleGroupId returns only that muscle group's weekly volumes."""
    # 1. Get muscle groups
    resp = await client.post(
        "/graphql",
        json={"query": "query { muscleGroups { id name } }"},
        headers=auth_headers,
    )
    muscle_groups = resp.json()["data"]["muscleGroups"]
    chest_mg = next(mg for mg in muscle_groups if mg["name"] == "Chest")
    triceps_mg = next(mg for mg in muscle_groups if mg["name"] == "Triceps")

    # 2. Create exercises
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Bench Press Filter"}) { id } }'},
        headers=auth_headers,
    )
    bench_id = resp.json()["data"]["createExercise"]["id"]

    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Tricep Dips"}) { id } }'},
        headers=auth_headers,
    )
    dips_id = resp.json()["data"]["createExercise"]["id"]

    # 3. Assign muscle groups
    await client.post(
        "/graphql",
        json={
            "query": "mutation Assign($eid: UUID!, $mgs: [MuscleGroupAssignmentInput!]!) { assignMuscleGroups(exerciseId: $eid, muscleGroupIds: $mgs) { id } }",
            "variables": {
                "eid": bench_id,
                "mgs": [{"muscleGroupId": chest_mg["id"], "role": "PRIMARY"}],
            },
        },
        headers=auth_headers,
    )

    await client.post(
        "/graphql",
        json={
            "query": "mutation Assign($eid: UUID!, $mgs: [MuscleGroupAssignmentInput!]!) { assignMuscleGroups(exerciseId: $eid, muscleGroupIds: $mgs) { id } }",
            "variables": {
                "eid": dips_id,
                "mgs": [{"muscleGroupId": triceps_mg["id"], "role": "PRIMARY"}],
            },
        },
        headers=auth_headers,
    )

    # 4. Create routine, mesocycle, and sessions (simplified)
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Filter Test"}) { id } }'},
        headers=auth_headers,
    )
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Add($rid: UUID!, $eid: UUID!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: 1}) { id } }",
            "variables": {"rid": routine_id, "eid": bench_id},
        },
        headers=auth_headers,
    )
    bench_re_id = resp.json()["data"]["addRoutineExercise"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Add($rid: UUID!, $eid: UUID!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: 2}) { id } }",
            "variables": {"rid": routine_id, "eid": dips_id},
        },
        headers=auth_headers,
    )
    dips_re_id = resp.json()["data"]["addRoutineExercise"]["id"]

    for re_id in (bench_re_id, dips_re_id):
        for set_number in (2, 3):
            await client.post(
                "/graphql",
                json={
                    "query": "mutation AddSet($reid: UUID!, $input: AddRoutineSetInput!) { addRoutineSet(routineExerciseId: $reid, input: $input) { id } }",
                    "variables": {
                        "reid": re_id,
                        "input": {
                            "setNumber": set_number,
                            "setType": "STANDARD",
                            "targetRepsMin": 8,
                            "targetRepsMax": 12,
                            "targetRir": 2,
                        },
                    },
                },
                headers=auth_headers,
            )

    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Filter Meso", startDate: "2026-07-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation Add($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 1, weekType: TRAINING, startDate: "2026-07-01", endDate: "2026-07-07"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week1_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Add($wid: UUID!, $rid: UUID!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: 1}) { id } }",
            "variables": {"wid": week1_id, "rid": routine_id},
        },
        headers=auth_headers,
    )
    ps_id = resp.json()["data"]["addPlannedSession"]["id"]

    # 5. Complete session with sets
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Create($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id exercises { id sets { id } } } }",
            "variables": {"psid": ps_id},
        },
        headers=auth_headers,
    )
    session_data = resp.json()["data"]["createSession"]
    session_id = session_data["id"]

    await client.post(
        "/graphql",
        json={"query": f'mutation {{ startSession(id: "{session_id}") {{ id }} }}'},
        headers=auth_headers,
    )

    # Log 1 set for each exercise
    for ex_data in session_data["exercises"]:
        for i in range(min(1, len(ex_data["sets"]))):
            set_id = ex_data["sets"][i]["id"]
            await client.post(
                "/graphql",
                json={
                    "query": 'mutation Log($sid: UUID!) { logSetResult(setId: $sid, input: {actualReps: 10, actualWeightKg: "100.0", actualRir: 2}) { id } }',
                    "variables": {"sid": set_id},
                },
                headers=auth_headers,
            )

    await client.post(
        "/graphql",
        json={"query": f'mutation {{ completeSession(id: "{session_id}") {{ id }} }}'},
        headers=auth_headers,
    )

    # 6. Query WITH filter for Chest only
    vol_query = """
    query GetVolume($mid: UUID!, $mgid: UUID!) {
        mesocycleVolumeInsight(mesocycleId: $mid, muscleGroupId: $mgid) {
            weeklyVolumes { 
                weekNumber 
                muscleGroupId 
                muscleGroupName 
                setCount 
            }
        }
    }
    """
    resp = await client.post(
        "/graphql",
        json={"query": vol_query, "variables": {"mid": meso_id, "mgid": chest_mg["id"]}},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]["mesocycleVolumeInsight"]

    # 7. Assertions
    weekly_volumes = data["weeklyVolumes"]

    # Should only have Chest entries, no Triceps
    assert len(weekly_volumes) == 1
    assert weekly_volumes[0]["weekNumber"] == 1
    assert weekly_volumes[0]["muscleGroupId"] == chest_mg["id"]
    assert weekly_volumes[0]["muscleGroupName"] == "Chest"
    assert weekly_volumes[0]["setCount"] == 1

    # No Triceps entries should be present
    triceps_entries = [wv for wv in weekly_volumes if wv["muscleGroupName"] == "Triceps"]
    assert len(triceps_entries) == 0


@pytest.mark.anyio
async def test_volume_exercise_with_multiple_muscle_groups_counts_for_all(
    client: AsyncClient, auth_headers: dict
):
    """Test that exercises with multiple muscle groups count sets for ALL muscle groups."""
    # 1. Get muscle groups
    resp = await client.post(
        "/graphql",
        json={"query": "query { muscleGroups { id name } }"},
        headers=auth_headers,
    )
    muscle_groups = resp.json()["data"]["muscleGroups"]
    chest_mg = next(mg for mg in muscle_groups if mg["name"] == "Chest")
    triceps_mg = next(mg for mg in muscle_groups if mg["name"] == "Triceps")

    # 2. Create exercise with multiple muscle groups (Bench Press: Chest PRIMARY, Triceps SECONDARY)
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createExercise(input: {name: "Bench Press Multi"}) { id } }'},
        headers=auth_headers,
    )
    bench_id = resp.json()["data"]["createExercise"]["id"]

    await client.post(
        "/graphql",
        json={
            "query": "mutation Assign($eid: UUID!, $mgs: [MuscleGroupAssignmentInput!]!) { assignMuscleGroups(exerciseId: $eid, muscleGroupIds: $mgs) { id } }",
            "variables": {
                "eid": bench_id,
                "mgs": [
                    {"muscleGroupId": chest_mg["id"], "role": "PRIMARY"},
                    {"muscleGroupId": triceps_mg["id"], "role": "SECONDARY"},
                ],
            },
        },
        headers=auth_headers,
    )

    # 3. Create routine, mesocycle, session
    resp = await client.post(
        "/graphql",
        json={"query": 'mutation { createRoutine(input: {name: "Multi MG"}) { id } }'},
        headers=auth_headers,
    )
    routine_id = resp.json()["data"]["createRoutine"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Add($rid: UUID!, $eid: UUID!) { addRoutineExercise(routineId: $rid, input: {exerciseId: $eid, order: 1}) { id } }",
            "variables": {"rid": routine_id, "eid": bench_id},
        },
        headers=auth_headers,
    )
    bench_re_id = resp.json()["data"]["addRoutineExercise"]["id"]

    for set_number in (2, 3):
        await client.post(
            "/graphql",
            json={
                "query": "mutation AddSet($reid: UUID!, $input: AddRoutineSetInput!) { addRoutineSet(routineExerciseId: $reid, input: $input) { id } }",
                "variables": {
                    "reid": bench_re_id,
                    "input": {
                        "setNumber": set_number,
                        "setType": "STANDARD",
                        "targetRepsMin": 8,
                        "targetRepsMax": 12,
                        "targetRir": 2,
                    },
                },
            },
            headers=auth_headers,
        )

    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Multi MG Meso", startDate: "2026-08-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation Add($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 1, weekType: TRAINING, startDate: "2026-08-01", endDate: "2026-08-07"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )
    week1_id = resp.json()["data"]["addMesocycleWeek"]["id"]

    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Add($wid: UUID!, $rid: UUID!) { addPlannedSession(mesocycleWeekId: $wid, input: {routineId: $rid, dayOfWeek: 1}) { id } }",
            "variables": {"wid": week1_id, "rid": routine_id},
        },
        headers=auth_headers,
    )
    ps_id = resp.json()["data"]["addPlannedSession"]["id"]

    # 4. Complete session with 1 set
    resp = await client.post(
        "/graphql",
        json={
            "query": "mutation Create($psid: UUID!) { createSession(input: {plannedSessionId: $psid}) { id exercises { sets { id } } } }",
            "variables": {"psid": ps_id},
        },
        headers=auth_headers,
    )
    session_data = resp.json()["data"]["createSession"]
    session_id = session_data["id"]

    await client.post(
        "/graphql",
        json={"query": f'mutation {{ startSession(id: "{session_id}") {{ id }} }}'},
        headers=auth_headers,
    )

    for i in range(1):
        set_id = session_data["exercises"][0]["sets"][i]["id"]
        await client.post(
            "/graphql",
            json={
                "query": 'mutation Log($sid: UUID!) { logSetResult(setId: $sid, input: {actualReps: 10, actualWeightKg: "100.0", actualRir: 2}) { id } }',
                "variables": {"sid": set_id},
            },
            headers=auth_headers,
        )

    await client.post(
        "/graphql",
        json={"query": f'mutation {{ completeSession(id: "{session_id}") {{ id }} }}'},
        headers=auth_headers,
    )

    # 5. Query volume insight
    vol_query = """
    query GetVolume($mid: UUID!) {
        mesocycleVolumeInsight(mesocycleId: $mid) {
            weeklyVolumes { 
                weekNumber 
                muscleGroupName 
                setCount 
            }
        }
    }
    """
    resp = await client.post(
        "/graphql",
        json={"query": vol_query, "variables": {"mid": meso_id}},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]["mesocycleVolumeInsight"]

    # 6. Assertions - Both Chest and Triceps should have 1 set
    weekly_volumes = data["weeklyVolumes"]
    assert len(weekly_volumes) == 2

    chest_entry = next((wv for wv in weekly_volumes if wv["muscleGroupName"] == "Chest"), None)
    triceps_entry = next((wv for wv in weekly_volumes if wv["muscleGroupName"] == "Triceps"), None)

    assert chest_entry is not None
    assert chest_entry["setCount"] == 1
    assert triceps_entry is not None
    assert triceps_entry["setCount"] == 1  # Same set counted for both muscle groups


@pytest.mark.anyio
async def test_volume_empty_mesocycle_returns_empty_weekly_volumes(
    client: AsyncClient, auth_headers: dict
):
    """Test that an empty mesocycle returns empty weekly volumes array."""
    resp = await client.post(
        "/graphql",
        json={
            "query": 'mutation { createMesocycle(input: {name: "Empty Meso", startDate: "2026-09-01"}) { id } }'
        },
        headers=auth_headers,
    )
    meso_id = resp.json()["data"]["createMesocycle"]["id"]

    # Add a week but no sessions
    await client.post(
        "/graphql",
        json={
            "query": 'mutation Add($mid: UUID!) { addMesocycleWeek(mesocycleId: $mid, input: {weekNumber: 1, weekType: TRAINING, startDate: "2026-09-01", endDate: "2026-09-07"}) { id } }',
            "variables": {"mid": meso_id},
        },
        headers=auth_headers,
    )

    vol_query = """
    query GetVolume($mid: UUID!) {
        mesocycleVolumeInsight(mesocycleId: $mid) {
            weeklyVolumes { weekNumber muscleGroupName setCount }
            totalSets
        }
    }
    """
    resp = await client.post(
        "/graphql",
        json={"query": vol_query, "variables": {"mid": meso_id}},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]["mesocycleVolumeInsight"]

    assert data["weeklyVolumes"] == []
    assert data["totalSets"] == 0
