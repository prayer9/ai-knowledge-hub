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
