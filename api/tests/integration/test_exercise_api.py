import pytest
from httpx import AsyncClient

HTTP_OK = 200
HTTP_UNAUTHORIZED = 401


@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"


@pytest.mark.anyio
async def test_create_and_query_exercise(client: AsyncClient, auth_headers: dict):
    # Mutation to create exercise
    mutation = """
    mutation CreateExercise($input: CreateExerciseInput!) {
        createExercise(input: $input) {
            id
            name
            description
            equipment
        }
    }
    """
    variables = {
        "input": {"name": "Bench Press", "description": "Chest exercise", "equipment": "Barbell"}
    }

    response = await client.post(
        "/graphql", json={"query": mutation, "variables": variables}, headers=auth_headers
    )

    assert response.status_code == HTTP_OK
    data = response.json()
    assert "errors" not in data
    exercise = data["data"]["createExercise"]
    assert exercise["name"] == "Bench Press"
    exercise_id = exercise["id"]

    # Query to fetch the created exercise
    query = """
    query GetExercise($id: UUID!) {
        exercise(id: $id) {
            id
            name
        }
    }
    """
    variables = {"id": exercise_id}

    response = await client.post(
        "/graphql", json={"query": query, "variables": variables}, headers=auth_headers
    )

    assert response.status_code == HTTP_OK
    data = response.json()
    assert "errors" not in data
    assert data["data"]["exercise"]["name"] == "Bench Press"


@pytest.mark.anyio
async def test_exercise_query_unauthorized(client: AsyncClient):
    query = "{ exercises { items { name } } }"
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == HTTP_UNAUTHORIZED


@pytest.mark.anyio
async def test_assign_muscle_groups_roundtrip_in_graphql(client: AsyncClient, auth_headers: dict):
    create_exercise_mutation = """
    mutation CreateExercise($input: CreateExerciseInput!) {
        createExercise(input: $input) {
            id
        }
    }
    """
    create_exercise_response = await client.post(
        "/graphql",
        json={"query": create_exercise_mutation, "variables": {"input": {"name": "Barbell Row"}}},
        headers=auth_headers,
    )
    assert create_exercise_response.status_code == HTTP_OK
    exercise_id = create_exercise_response.json()["data"]["createExercise"]["id"]

    muscle_groups_query = "query { muscleGroups { id name } }"
    muscle_groups_response = await client.post(
        "/graphql", json={"query": muscle_groups_query}, headers=auth_headers
    )
    assert muscle_groups_response.status_code == HTTP_OK
    available_muscle_groups = muscle_groups_response.json()["data"]["muscleGroups"]
    lats = next(
        (mg for mg in available_muscle_groups if mg["name"] == "Lats"),
        available_muscle_groups[0],
    )

    assign_mutation = """
    mutation AssignMuscles($exerciseId: UUID!, $muscleGroupIds: [MuscleGroupAssignmentInput!]!) {
        assignMuscleGroups(exerciseId: $exerciseId, muscleGroupIds: $muscleGroupIds) {
            id
            muscleGroups {
                role
                muscleGroup {
                    id
                    name
                }
            }
        }
    }
    """
    assign_response = await client.post(
        "/graphql",
        json={
            "query": assign_mutation,
            "variables": {
                "exerciseId": exercise_id,
                "muscleGroupIds": [{"muscleGroupId": lats["id"], "role": "PRIMARY"}],
            },
        },
        headers=auth_headers,
    )
    assert assign_response.status_code == HTTP_OK
    assign_data = assign_response.json()
    assert "errors" not in assign_data
    assigned_groups = assign_data["data"]["assignMuscleGroups"]["muscleGroups"]
    assert len(assigned_groups) == 1
    assert assigned_groups[0]["role"] == "PRIMARY"
    assert assigned_groups[0]["muscleGroup"]["id"] == lats["id"]

    exercise_query = """
    query ExerciseById($id: UUID!) {
        exercise(id: $id) {
            id
            muscleGroups {
                role
                muscleGroup {
                    id
                }
            }
        }
    }
    """
    exercise_response = await client.post(
        "/graphql",
        json={"query": exercise_query, "variables": {"id": exercise_id}},
        headers=auth_headers,
    )
    assert exercise_response.status_code == HTTP_OK
    exercise_data = exercise_response.json()
    assert "errors" not in exercise_data
    exercise_groups = exercise_data["data"]["exercise"]["muscleGroups"]
    assert len(exercise_groups) == 1
    assert exercise_groups[0]["role"] == "PRIMARY"
    assert exercise_groups[0]["muscleGroup"]["id"] == lats["id"]

    exercises_query = """
    query Exercises {
        exercises {
            items {
                id
                muscleGroups {
                    role
                    muscleGroup {
                        id
                    }
                }
            }
        }
    }
    """
    exercises_response = await client.post(
        "/graphql", json={"query": exercises_query}, headers=auth_headers
    )
    assert exercises_response.status_code == HTTP_OK
    exercises_data = exercises_response.json()
    assert "errors" not in exercises_data
    matching_exercise = next(
        item for item in exercises_data["data"]["exercises"]["items"] if item["id"] == exercise_id
    )
    assert len(matching_exercise["muscleGroups"]) == 1
    assert matching_exercise["muscleGroups"][0]["role"] == "PRIMARY"
    assert matching_exercise["muscleGroups"][0]["muscleGroup"]["id"] == lats["id"]
