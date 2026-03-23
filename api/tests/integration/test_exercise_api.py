import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
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

    assert response.status_code == 200
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

    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert data["data"]["exercise"]["name"] == "Bench Press"


@pytest.mark.anyio
async def test_exercise_query_unauthorized(client: AsyncClient):
    query = "{ exercises { items { name } } }"
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 401
