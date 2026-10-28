import os
import re
import math
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import ChunkRecord, DocumentRecord
from app.models import ChatOutput, Citation
from app.services.embeddings import embed_texts


async def search_chunks(session: Session, knowledge_base_id: int, question: str, limit: int = 4):
    rows = session.execute(
        select(ChunkRecord, DocumentRecord).join(DocumentRecord)
        .where(DocumentRecord.knowledge_base_id == knowledge_base_id)
    ).all()
    if rows and all(chunk.embedding for chunk, _ in rows):
        query = await embed_texts([question])
        if query:
            q = query[0]
            def cosine(row):
                v = row[0].embedding
                if len(v) != len(q):
                    return -1.0
                denominator = math.sqrt(sum(x*x for x in v)) * math.sqrt(sum(x*x for x in q))
                return sum(a*b for a,b in zip(v,q))/denominator if denominator else -1.0
            return sorted(rows, key=cosine, reverse=True)[:limit]
    words = set(re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", question.lower()))
    def score(row):
        content = row[0].content.lower()
        terms = set(re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", content))
        return len(words & terms)
    ranked = sorted(rows, key=score, reverse=True)
    return [r for r in ranked if score(r) > 0][:limit]


async def generate_answer(session: Session, kb_id: int, question: str) -> ChatOutput:
    matches = await search_chunks(session, kb_id, question)
    citations = [Citation(document_id=doc.id, filename=doc.filename, chunk_id=chunk.id,
                          excerpt=chunk.content[:200]) for chunk, doc in matches]
    if not matches:
        return ChatOutput(answer="知识库中没有找到相关资料，请补充文档或换一种提问方式。", citations=[], mode="no_match")
    context = "\n\n".join(f"[{i+1}] {chunk.content}" for i, (chunk, _) in enumerate(matches))
    key = os.getenv("LLM_API_KEY", "")
    if not key:
        return ChatOutput(answer="演示检索模式：已找到以下相关资料片段。配置 LLM_API_KEY 后可生成归纳回答。\n\n" + context[:2000], citations=citations, mode="retrieval_demo")
    base = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    prompt = "只根据给定资料回答问题。若资料不足，明确说明不知道。使用中文，引用资料编号。\n资料：\n" + context
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(base + "/chat/completions", headers={"Authorization": f"Bearer {key}"},
                                     json={"model": model, "messages": [{"role": "system", "content": prompt},
                                        {"role": "user", "content": question}], "temperature": 0.2})
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
    return ChatOutput(answer=answer, citations=citations, mode="llm")
