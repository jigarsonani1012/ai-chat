from datetime import datetime

from pydantic import BaseModel


class ConversationSummary(BaseModel):
    session_id: str
    bot_id: str
    created_at: datetime
    user_identifier: str | None = None
    message_count: int
    last_message: str | None = None


class MessageRead(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    source_json: str | None = None

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    session_id: str
    messages: list[MessageRead]


class AnalyticsOverview(BaseModel):
    total_sessions: int
    total_messages: int
    escalations: int
    unanswered_questions: int
    top_questions: list[str]
