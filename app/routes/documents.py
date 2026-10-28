from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db import ChunkRecord, DocumentRecord, KnowledgeBaseRecord, get_session
from app.models import DocumentInfo
from app.services.documents import MAX_BYTES, extract_text, split_text
from app.services.embeddings import embed_texts

router = APIRouter(prefix="/api/knowledge-bases/{kb_id}/documents", tags=["Documents"])


@router.post("", response_model=DocumentInfo, status_code=201)
async def upload_document(kb_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
    if session.get(KnowledgeBaseRecord, kb_id) is None:
        raise HTTPException(404, "Knowledge base not found")
    filename = Path(file.filename or "").name[:255]
    content = await file.read(MAX_BYTES + 1)
    await file.close()
    try:
        text = extract_text(filename, content)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    doc = DocumentRecord(knowledge_base_id=kb_id, filename=filename)
    parts = split_text(text)
    try:
        vectors = await embed_texts(parts)
    except Exception as exc:
        raise HTTPException(502, "Embedding provider is unavailable") from exc
    session.add(doc)
    session.flush()
    session.add_all([ChunkRecord(document_id=doc.id, position=i, content=part,
                                 embedding=vectors[i] if vectors else None) for i, part in enumerate(parts)])
    session.commit()
    session.refresh(doc)
    return DocumentInfo.model_validate(doc).model_copy(update={"chunk_count": len(parts)})


@router.get("", response_model=list[DocumentInfo])
def list_documents(kb_id: int, session: Session = Depends(get_session)):
    if session.get(KnowledgeBaseRecord, kb_id) is None:
        raise HTTPException(404, "Knowledge base not found")
    rows = session.execute(select(DocumentRecord, func.count(ChunkRecord.id)).outerjoin(ChunkRecord)
                           .where(DocumentRecord.knowledge_base_id == kb_id)
                           .group_by(DocumentRecord.id).order_by(DocumentRecord.id)).all()
    return [DocumentInfo.model_validate(doc).model_copy(update={"chunk_count": count}) for doc, count in rows]


@router.delete("/{document_id}", status_code=204)
def delete_document(kb_id: int, document_id: int, session: Session = Depends(get_session)):
    doc = session.get(DocumentRecord, document_id)
    if doc is None or doc.knowledge_base_id != kb_id:
        raise HTTPException(404, "Document not found")
    session.delete(doc)
    session.commit()
