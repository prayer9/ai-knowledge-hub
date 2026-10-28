"""Reproducible synthetic retrieval smoke benchmark: python -m scripts.evaluate_retrieval."""
import asyncio
import json
import statistics
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db import Base, ChunkRecord, DocumentRecord, KnowledgeBaseRecord
from app.services.answering import search_chunks

CASES = [
    ("PostgreSQL relational storage", "PostgreSQL stores relational data in tables"),
    ("FastAPI Python web APIs", "FastAPI builds Python web APIs"),
    ("Redis cache memory", "Redis caches application data in memory"),
    ("Docker container images", "Docker packages dependencies into container images"),
    ("React frontend components", "React creates frontend UI components"),
    ("Alembic schema migration", "Alembic manages database schema migration"),
    ("Pydantic typed validation", "Pydantic validates typed Python models"),
    ("JWT signed identity", "JWT carries signed identity claims"),
    ("Nginx reverse proxy", "Nginx works as a reverse proxy"),
    ("Embeddings numerical vectors", "Embeddings represent numerical vectors"),
    ("Cosine similarity angle", "Cosine similarity compares vector angles"),
    ("Pytest automated tests", "Pytest runs automated Python tests"),
    ("TypeScript static typing", "TypeScript supports static typing"),
    ("Chunk overlap boundary", "Chunk overlap repeats boundary text"),
    ("HTTP 404 resource", "HTTP 404 means resource not found"),
    ("CORS cross origin", "CORS controls cross origin requests"),
    ("SQLAlchemy ORM mapping", "SQLAlchemy provides ORM database mapping"),
    ("SSE streaming events", "SSE streams events over HTTP"),
    ("RAG retrieval context", "RAG retrieval supplies external context"),
    ("GitHub Actions CI", "GitHub Actions automates CI tests"),
]


def run():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        kb = KnowledgeBaseRecord(name="Benchmark", description="Synthetic")
        session.add(kb);session.flush()
        ids=[]
        for i, (_, document) in enumerate(CASES):
            doc=DocumentRecord(knowledge_base_id=kb.id, filename=f"case_{i+1:02d}.txt")
            session.add(doc);session.flush()
            session.add(ChunkRecord(document_id=doc.id, position=0, content=document))
            ids.append(doc.id)
        session.commit()
        hits=0;durations=[]
        for i,(question,_) in enumerate(CASES):
            start=time.perf_counter()
            results=asyncio.run(search_chunks(session,kb.id,question,limit=3))
            durations.append((time.perf_counter()-start)*1000)
            hits+=any(doc.id==ids[i] for _,doc in results)
    engine.dispose()
    return {"dataset":"20 synthetic lexical smoke cases","questions":len(CASES),
            "source_hit_at_3":round(hits/len(CASES),3),"median_latency_ms":round(statistics.median(durations),2),
            "note":"Not a production accuracy or latency claim"}


if __name__=="__main__":
    print(json.dumps(run(),ensure_ascii=False,indent=2))
