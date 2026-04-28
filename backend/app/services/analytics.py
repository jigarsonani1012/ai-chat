import json

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.analytics import AnalyticsEvent
from app.db.models.chat import ChatMessage, ChatSession
from app.db.models.escalation import EscalationEvent
from app.schemas.analytics import AnalyticsOverview, ConversationDetail, ConversationSummary, MessageRead


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def track_event(
        self,
        organization_id: str,
        bot_id: str,
        event_type: str,
        session_id: str | None = None,
        message_text: str | None = None,
        confidence: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        self.db.add(
            AnalyticsEvent(
                organization_id=organization_id,
                bot_id=bot_id,
                session_id=session_id,
                event_type=event_type,
                message_text=message_text,
                confidence=confidence,
                metadata_json=json.dumps(metadata or {}),
            )
        )

    def list_conversations(self, organization_id: str) -> list[ConversationSummary]:
        sessions = (
            self.db.query(ChatSession)
            .filter(ChatSession.organization_id == organization_id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )
        results: list[ConversationSummary] = []
        for session in sessions:
            messages = (
                self.db.query(ChatMessage)
                .filter(ChatMessage.session_id == session.id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )
            last_message = messages[-1].content if messages else None
            results.append(
                ConversationSummary(
                    session_id=session.id,
                    bot_id=session.bot_id,
                    created_at=session.created_at,
                    user_identifier=session.user_identifier,
                    message_count=len(messages),
                    last_message=last_message,
                )
            )
        return results

    def get_conversation_detail(self, organization_id: str, session_id: str) -> ConversationDetail | None:
        session = (
            self.db.query(ChatSession)
            .filter(ChatSession.organization_id == organization_id, ChatSession.id == session_id)
            .first()
        )
        if not session:
            return None
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
        return ConversationDetail(
            session_id=session.id,
            messages=[MessageRead.model_validate(message) for message in messages],
        )

    def get_overview(self, organization_id: str) -> AnalyticsOverview:
        total_sessions = self.db.query(func.count(ChatSession.id)).filter(ChatSession.organization_id == organization_id).scalar() or 0
        total_messages = (
            self.db.query(func.count(ChatMessage.id))
            .join(ChatSession, ChatMessage.session_id == ChatSession.id)
            .filter(ChatSession.organization_id == organization_id)
            .scalar()
            or 0
        )
        escalations = (
            self.db.query(func.count(EscalationEvent.id))
            .filter(EscalationEvent.organization_id == organization_id)
            .scalar()
            or 0
        )
        unanswered_questions = (
            self.db.query(func.count(AnalyticsEvent.id))
            .filter(
                AnalyticsEvent.organization_id == organization_id,
                AnalyticsEvent.event_type == "unanswered_question",
            )
            .scalar()
            or 0
        )
        top_question_rows = (
            self.db.query(AnalyticsEvent.message_text, func.count(AnalyticsEvent.id).label("count"))
            .filter(
                AnalyticsEvent.organization_id == organization_id,
                AnalyticsEvent.event_type == "question_asked",
                AnalyticsEvent.message_text.is_not(None),
            )
            .group_by(AnalyticsEvent.message_text)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(5)
            .all()
        )
        return AnalyticsOverview(
            total_sessions=total_sessions,
            total_messages=total_messages,
            escalations=escalations,
            unanswered_questions=unanswered_questions,
            top_questions=[row[0] for row in top_question_rows],
        )
