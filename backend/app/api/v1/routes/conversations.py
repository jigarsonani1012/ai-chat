from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.schemas.analytics import ConversationDetail, ConversationSummary
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/", response_model=list[ConversationSummary])
def list_conversations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ConversationSummary]:
    return AnalyticsService(db).list_conversations(current_user.organization_id)


@router.get("/{session_id}", response_model=ConversationDetail)
def conversation_detail(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ConversationDetail:
    detail = AnalyticsService(db).get_conversation_detail(current_user.organization_id, session_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return detail
