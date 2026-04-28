from pydantic import BaseModel


class BotCreate(BaseModel):
    name: str
    welcome_message: str | None = None
    primary_color: str | None = None
    escalation_emails: dict[str, str] | None = None


class BotUpdate(BaseModel):
    name: str | None = None
    welcome_message: str | None = None
    primary_color: str | None = None
    escalation_emails: dict[str, str] | None = None


class BotRead(BaseModel):
    id: str
    organization_id: str
    name: str
    public_key: str
    welcome_message: str
    primary_color: str
    escalation_emails: dict

    model_config = {"from_attributes": True}


class BotPublicConfig(BaseModel):
    id: str
    name: str
    public_key: str
    welcome_message: str
    primary_color: str
