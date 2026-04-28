from sqlalchemy.orm import Session

from app.db.models.bot import Bot, default_escalation_emails
from app.schemas.bot import BotCreate, BotPublicConfig, BotUpdate


class BotService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_bot(self, organization_id: str, payload: BotCreate) -> Bot:
        bot = Bot(
            organization_id=organization_id,
            name=payload.name,
            welcome_message=payload.welcome_message
            or "Hi, how can I help you today using the available documentation?",
            primary_color=payload.primary_color or "#14532d",
            escalation_emails=payload.escalation_emails or default_escalation_emails(),
        )
        self.db.add(bot)
        self.db.commit()
        self.db.refresh(bot)
        return bot

    def get_public_config(self, public_key: str) -> BotPublicConfig | None:
        bot = self.db.query(Bot).filter(Bot.public_key == public_key).first()
        if not bot:
            return None
        return BotPublicConfig(
            id=bot.id,
            name=bot.name,
            public_key=bot.public_key,
            welcome_message=bot.welcome_message,
            primary_color=bot.primary_color,
        )

    def update_bot(self, bot: Bot, payload: BotUpdate) -> Bot:
        if payload.name is not None:
            bot.name = payload.name
        if payload.welcome_message is not None:
            bot.welcome_message = payload.welcome_message
        if payload.primary_color is not None:
            bot.primary_color = payload.primary_color
        if payload.escalation_emails is not None:
            bot.escalation_emails = payload.escalation_emails
        self.db.commit()
        self.db.refresh(bot)
        return bot
