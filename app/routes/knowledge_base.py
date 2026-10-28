from fastapi import APIRouter, Depends, HTTPException, Response, Request
from app.models import KnowledgeBase, KnowledgeBaseInput
from app.store import Store

router = APIRouter(prefix="/api/knowledge-bases", tags=["Knowledge Bases"])

def get_store(request: Request) -> Store:
    return request.app.state.store

@router.post("", response_model=KnowledgeBase, status_code=201)
def create(payload: KnowledgeBaseInput, store: Store = Depends(get_store)):
    return store.create(payload)

@router.get("", response_model=list[KnowledgeBase])
def list_all(store: Store = Depends(get_store)):
    return store.list()

@router.get("/{item_id}", response_model=KnowledgeBase)
def get_one(item_id: int, store: Store = Depends(get_store)):
    item = store.get(item_id)
    if item is None:
        raise HTTPException(404, "Knowledge base not found")
    return item

@router.put("/{item_id}", response_model=KnowledgeBase)
def update(item_id: int, payload: KnowledgeBaseInput, store: Store = Depends(get_store)):
    item = store.update(item_id, payload)
    if item is None:
        raise HTTPException(404, "Knowledge base not found")
    return item

@router.delete("/{item_id}", status_code=204)
def delete(item_id: int, store: Store = Depends(get_store)):
    if not store.delete(item_id):
        raise HTTPException(404, "Knowledge base not found")
    return Response(status_code=204)
