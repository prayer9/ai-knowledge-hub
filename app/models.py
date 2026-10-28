from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class KnowledgeBaseInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)

class KnowledgeBase(KnowledgeBaseInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class DocumentInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    knowledge_base_id: int
    filename: str
    created_at: datetime
    chunk_count: int = 0


class ChatInput(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class Citation(BaseModel):
    document_id: int
    filename: str
    chunk_id: int
    excerpt: str


class ChatOutput(BaseModel):
    answer: str
    citations: list[Citation]
    mode: str
