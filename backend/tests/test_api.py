import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from backend.main import app
from backend.database import get_session
from backend.models import Log
from datetime import datetime

# Setup test database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_create_log(session):
    client = TestClient(app)
    response = client.post(
        "/logs",
        json={"event": "Pee", "orientation": "Dad"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["event"] == "Pee"
    assert data["orientation"] == "Dad"
    assert "id" in data

def test_ongoing_feed(session):
    client = TestClient(app)
    # Start feed
    client.post("/logs", json={"event": "Feeding", "details": "ongoing", "orientation": "Left", "feed_id": 1})
    
    # Check dashboard
    response = client.get("/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["ongoing_feed"] is not None
    assert data["ongoing_feed"]["orientation"] == "Left"

    # Stop feed
    response = client.post("/logs/Feeding/stop")
    assert response.status_code == 200
    data = response.json()
    assert data["details"] != "ongoing"
    assert ":" in data["details"]

def test_delete_log(session):
    client = TestClient(app)
    post_resp = client.post("/logs", json={"event": "Poop"})
    log_id = post_resp.json()["id"]
    
    del_resp = client.delete(f"/logs/{log_id}")
    assert del_resp.status_code == 200
    
    get_resp = client.get("/logs")
    assert len(get_resp.json()) == 0
