from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService

router = APIRouter()


@router.post("/ask", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def ask(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    service = ChatService(db)
    try:
        return service.answer_question(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
