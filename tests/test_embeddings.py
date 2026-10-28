import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db import Base, KnowledgeBaseRecord, DocumentRecord, ChunkRecord
from app.services import answering


def test_semantic_ranking(monkeypatch):
    async def fake_embed(texts):
        return [[1.0, 0.0]]
    monkeypatch.setattr(answering, "embed_texts", fake_embed)
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        kb = KnowledgeBaseRecord(name="test", description="")
        session.add(kb);session.flush()
        doc = DocumentRecord(knowledge_base_id=kb.id, filename="notes.txt")
        session.add(doc);session.flush()
        session.add_all([
            ChunkRecord(document_id=doc.id, position=0, content="wrong", embedding=[0.0, 1.0]),
            ChunkRecord(document_id=doc.id, position=1, content="right", embedding=[1.0, 0.0]),
        ])
        session.commit()
        matches = asyncio.run(answering.search_chunks(session, kb.id, "question"))
        assert matches[0][0].content == "right"
    engine.dispose()
