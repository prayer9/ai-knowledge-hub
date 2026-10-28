from io import BytesIO
from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db import Base
from app.main import create_app
from app.services.documents import split_text


def make_client():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return TestClient(create_app(sessionmaker(bind=engine))), engine


def test_upload_chat_and_delete(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    client, engine = make_client()
    with client:
        kb = client.post("/api/knowledge-bases", json={"name": "AI"}).json()["id"]
        path = f"/api/knowledge-bases/{kb}/documents"
        result = client.post(path, files={"file": ("notes.txt", b"FastAPI provides Python APIs and validation")})
        assert result.status_code == 201, result.text
        assert len(client.get(path).json()) == 1
        chat = client.post(f"/api/knowledge-bases/{kb}/chat", json={"question": "What does FastAPI provide?"})
        assert chat.status_code == 200
        assert chat.json()["mode"] == "retrieval_demo"
        assert chat.json()["citations"][0]["filename"] == "notes.txt"
        stream = client.post(f"/api/knowledge-bases/{kb}/chat/stream", json={"question": "FastAPI"})
        assert stream.status_code == 200 and '"type": "done"' in stream.text
        assert client.delete(f"{path}/{result.json()['id']}").status_code == 204
        assert client.get(path).json() == []
    engine.dispose()


def test_invalid_files_and_docx():
    client, engine = make_client()
    with client:
        kb = client.post("/api/knowledge-bases", json={"name": "Docs"}).json()["id"]
        path = f"/api/knowledge-bases/{kb}/documents"
        assert client.post(path, files={"file": ("evil.exe", b"abc")}).status_code == 422
        assert client.post(path, files={"file": ("empty.txt", b"")}).status_code == 422
        doc = Document(); doc.add_paragraph("PostgreSQL stores information")
        stream = BytesIO(); doc.save(stream)
        assert client.post(path, files={"file": ("notes.docx", stream.getvalue())}).status_code == 201
        assert client.post("/api/knowledge-bases/999/chat", json={"question": "hello"}).status_code == 404
    engine.dispose()


def test_overlap():
    assert split_text("abcdefghij", size=6, overlap=2) == ["abcdef", "efghij"]
