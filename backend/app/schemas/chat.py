from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    public_bot_key: str
    message: str
    session_id: str | None = None
    user_identifier: str | None = None
    history: list[ChatMessageIn] = []


class SourceItem(BaseModel):
    document_id: str
    source_name: str
    source_url: str | None = None
    excerpt: str
    score: float


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[SourceItem]
    confidence: str
    escalation_triggered: bool
    escalation_intent: str | None = None
