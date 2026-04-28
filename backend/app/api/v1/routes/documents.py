from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.db.models.bot import Bot
from app.db.models.document import Document
from app.schemas.document import DocumentRead, DocumentTextCreate, DocumentUrlCreate
from app.services.ingestion.service import IngestionService

router = APIRouter()


@router.get("/", response_model=list[DocumentRead])
def list_documents(
    bot_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[DocumentRead]:
    query = db.query(Document).filter(Document.organization_id == current_user.organization_id)
    if bot_id:
        query = query.filter(Document.bot_id == bot_id)
    documents = query.order_by(Document.created_at.desc()).all()
    return [DocumentRead.model_validate(document) for document in documents]


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    bot_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> DocumentRead:
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.organization_id == current_user.organization_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    service = IngestionService(db)
    document = await service.ingest_upload(bot=bot, upload=file)
    return DocumentRead.model_validate(document)


@router.post("/url", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def ingest_url(
    payload: DocumentUrlCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> DocumentRead:
    bot = db.query(Bot).filter(Bot.id == payload.bot_id, Bot.organization_id == current_user.organization_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    service = IngestionService(db)
    document = service.ingest_url(bot=bot, payload=payload)
    return DocumentRead.model_validate(document)


@router.post("/text", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def ingest_text(
    payload: DocumentTextCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> DocumentRead:
    bot = db.query(Bot).filter(Bot.id == payload.bot_id, Bot.organization_id == current_user.organization_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    service = IngestionService(db)
    document = service.ingest_text(bot=bot, payload=payload)
    return DocumentRead.model_validate(document)
