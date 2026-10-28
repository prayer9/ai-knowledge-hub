import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db import KnowledgeBaseRecord, get_session
from app.models import ChatInput, ChatOutput
from app.services.answering import generate_answer

router = APIRouter(prefix="/api/knowledge-bases/{kb_id}", tags=["Chat"])


async def answer(kb_id: int, payload: ChatInput, session: Session) -> ChatOutput:
    if session.get(KnowledgeBaseRecord, kb_id) is None:
        raise HTTPException(404, "Knowledge base not found")
    try:
        return await generate_answer(session, kb_id, payload.question)
    except Exception as exc:
        # Do not leak upstream credentials or provider error bodies.
        raise HTTPException(502, "LLM provider is unavailable") from exc


@router.post("/chat", response_model=ChatOutput)
async def chat(kb_id: int, payload: ChatInput, session: Session = Depends(get_session)):
    return await answer(kb_id, payload, session)


@router.post("/chat/stream")
async def stream_chat(kb_id: int, payload: ChatInput, session: Session = Depends(get_session)):
    result = await answer(kb_id, payload, session)

    async def events():
        # The provider response is collected before SSE emission in this MVP.
        for i in range(0, len(result.answer), 40):
            yield f"data: {json.dumps({'type': 'delta', 'text': result.answer[i:i+40]}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'citations': [c.model_dump() for c in result.citations], 'mode': result.mode}, ensure_ascii=False)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
