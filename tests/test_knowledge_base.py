import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db import Base
from app.main import create_app

@pytest.fixture
def client():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with TestClient(create_app(factory)) as c:
        yield c
    engine.dispose()

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_crud(client):
    a = client.post("/api/knowledge-bases", json={"name": "Python"})
    b = client.post("/api/knowledge-bases", json={"name": "AI"})
    assert a.status_code == b.status_code == 201
    assert a.json()["id"] != b.json()["id"]
    assert len(client.get("/api/knowledge-bases").json()) == 2
    item_id = a.json()["id"]
    assert client.get(f"/api/knowledge-bases/{item_id}").status_code == 200
    assert client.put(f"/api/knowledge-bases/{item_id}", json={"name": "Updated"}).json()["name"] == "Updated"
    assert client.delete(f"/api/knowledge-bases/{item_id}").status_code == 204
    assert client.get(f"/api/knowledge-bases/{item_id}").status_code == 404

def test_persists_across_requests(client):
    created = client.post("/api/knowledge-bases", json={"name": "Persistent"}).json()
    assert client.get("/api/knowledge-bases").json()[0]["id"] == created["id"]

@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_missing(client, method):
    kwargs = {"json": {"name": "Test"}} if method == "put" else {}
    assert getattr(client, method)("/api/knowledge-bases/999", **kwargs).status_code == 404

@pytest.mark.parametrize("payload", [{"name": ""}, {"name": "   "}, {"name": "x"*101}, {"name": "Okay", "description": "x"*501}, {"name": "Okay", "extra": 1}])
def test_invalid(client, payload):
    assert client.post("/api/knowledge-bases", json=payload).status_code == 422
