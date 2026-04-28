from datetime import datetime

from pydantic import BaseModel, HttpUrl


class DocumentUrlCreate(BaseModel):
    bot_id: str
    url: HttpUrl


class DocumentTextCreate(BaseModel):
    bot_id: str
    title: str
    content: str


class DocumentRead(BaseModel):
    id: str
    organization_id: str
    bot_id: str
    source_type: str
    source_name: str
    source_url: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListQuery(BaseModel):
    bot_id: str | None = None
