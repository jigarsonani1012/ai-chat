import json

import dramatiq

from app.db.models.document import Document
from app.db.models.escalation import EscalationEvent
from app.db.session import SessionLocal
from app.services.email.service import EmailService
from app.services.ingestion.service import IngestionService
from app.workers.broker import redis_broker  # noqa: F401


@dramatiq.actor
def ingest_url_actor(document_id: str) -> None:
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        if not document.bot:
            return
        IngestionService(db).process_url_document(document)
    finally:
        db.close()


@dramatiq.actor
def deliver_escalation_email_actor(escalation_event_id: str) -> None:
    db = SessionLocal()
    try:
        event = db.query(EscalationEvent).filter(EscalationEvent.id == escalation_event_id).first()
        if not event or event.delivered:
            return

        payload = json.loads(event.payload)
        subject = f"[{payload.get('bot_name', 'Bot')}] Chat escalation: {event.intent}"
        lines = [
            f"Bot: {payload.get('bot_name', 'Bot')}",
            f"Session ID: {payload['session_id']}",
            f"Intent: {payload['intent']}",
            f"Reason: {payload['reason']}",
            "",
            "Conversation:",
        ]
        for item in payload["transcript"]:
            lines.append(f"- {item['role']}: {item['content']}")
        if payload["sources"]:
            lines.append("")
            lines.append("Retrieved Sources:")
            for source in payload["sources"]:
                lines.append(f"- {source['source_name']} (score={source['score']:.3f})")

        EmailService().send(
            to_email=event.recipient_email,
            subject=subject,
            body="\n".join(lines),
        )
        event.delivered = True
        db.commit()
    finally:
        db.close()
