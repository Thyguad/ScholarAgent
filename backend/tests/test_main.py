from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "scholar-agent-backend",
    }


def test_create_research_task() -> None:
    response = client.post(
        "/research/tasks",
        json={"topic": "LLM Agent for Software Engineering"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"].startswith("task_")
    assert data["topic"] == "LLM Agent for Software Engineering"
    assert data["status"] == "created"


def test_create_research_task_requires_valid_topic() -> None:
    # Pydantic 会在进入业务逻辑前校验输入，避免空主题进入后续 Agent 流程。
    response = client.post("/research/tasks", json={"topic": ""})

    assert response.status_code == 422
