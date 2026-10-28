from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.main import create_app


def test_persistence_after_app_restart(tmp_path):
    db_file = tmp_path / "knowledge.db"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with TestClient(create_app(factory)) as first:
        response = first.post("/api/knowledge-bases", json={"name": "Survives restart"})
        assert response.status_code == 201
    with TestClient(create_app(factory)) as second:
        assert second.get("/api/knowledge-bases").json()[0]["name"] == "Survives restart"
    engine.dispose()
