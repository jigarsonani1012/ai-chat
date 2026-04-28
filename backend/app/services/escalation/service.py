import json

from sqlalchemy.orm import Session

from app.db.models.bot import Bot
from app.db.models.escalation import EscalationEvent
from app.services.tasks import TaskDispatcher


class EscalationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.task_dispatcher = TaskDispatcher()

    def maybe_escalate(
        self,
        bot: Bot,
        session_id: str,
        intent: str,
        reason: str,
        transcript: list[dict],
        sources: list[dict],
    ) -> bool:
        if intent == "general" and reason != "low_confidence":
            return False

        recipient = bot.escalation_emails.get(intent) or bot.escalation_emails.get("technical_support")
        payload = {
            "bot_name": bot.name,
            "session_id": session_id,
            "intent": intent,
            "reason": reason,
            "transcript": transcript,
            "sources": sources,
        }

        event = EscalationEvent(
            organization_id=bot.organization_id,
            bot_id=bot.id,
            session_id=session_id,
            intent=intent,
            reason=reason,
            recipient_email=recipient,
            payload=json.dumps(payload),
            delivered=False,
        )
        self.db.add(event)
        self.db.commit()
        self.task_dispatcher.dispatch_escalation_email(event.id)
        return True
