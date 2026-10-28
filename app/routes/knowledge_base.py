from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import KnowledgeBaseRecord, get_session
from app.models import KnowledgeBase, KnowledgeBaseInput

router = APIRouter(prefix="/api/knowledge-bases", tags=["Knowledge Bases"])

@router.post("", response_model=KnowledgeBase, status_code=201)
def create(payload: KnowledgeBaseInput, session: Session = Depends(get_session)):
    item = KnowledgeBaseRecord(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.get("", response_model=list[KnowledgeBase])
def list_all(session: Session = Depends(get_session)):
    return session.scalars(select(KnowledgeBaseRecord).order_by(KnowledgeBaseRecord.id)).all()

@router.get("/{item_id}", response_model=KnowledgeBase)
def get_one(item_id: int, session: Session = Depends(get_session)):
    item = session.get(KnowledgeBaseRecord, item_id)
    if item is None:
        raise HTTPException(404, "Knowledge base not found")
    return item

@router.put("/{item_id}", response_model=KnowledgeBase)
def update(item_id: int, payload: KnowledgeBaseInput, session: Session = Depends(get_session)):
    item = session.get(KnowledgeBaseRecord, item_id)
    if item is None:
        raise HTTPException(404, "Knowledge base not found")
    item.name = payload.name
    item.description = payload.description
    session.commit()
    session.refresh(item)
    return item

@router.delete("/{item_id}", status_code=204)
def delete(item_id: int, session: Session = Depends(get_session)):
    item = session.get(KnowledgeBaseRecord, item_id)
    if item is None:
        raise HTTPException(404, "Knowledge base not found")
    session.delete(item)
    session.commit()
    return Response(status_code=204)
