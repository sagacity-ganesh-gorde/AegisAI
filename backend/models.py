from pydantic import BaseModel
from typing import Optional

class AskRequest(BaseModel):
    question: str
    temperature: Optional[float] = 0.3
    top_k: Optional[int] = 5

class AskResponse(BaseModel):
    answer: str
    sources: list[dict]
    model: str
    gpu_used: bool

class IngestRequest(BaseModel):
    source_type: str
    source_config: dict

class IngestResponse(BaseModel):
    status: str
    chunks_created: int
    documents_processed: int

class TenantResponse(BaseModel):
    name: str
    document_count: int
    index_status: str
