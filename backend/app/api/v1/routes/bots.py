from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.db.models.bot import Bot
from app.db.models.organization import Organization
from app.schemas.bot import BotCreate, BotPublicConfig, BotRead, BotUpdate
from app.services.bot import BotService

router = APIRouter()


@router.post("/", response_model=BotRead, status_code=status.HTTP_201_CREATED)
def create_bot(
    payload: BotCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> BotRead:
    organization = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    service = BotService(db)
    bot = service.create_bot(organization_id=organization.id, payload=payload)
    return BotRead.model_validate(bot)


@router.get("/", response_model=list[BotRead])
def list_bots(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[BotRead]:
    bots = db.query(Bot).filter(Bot.organization_id == current_user.organization_id).all()
    return [BotRead.model_validate(bot) for bot in bots]


@router.get("/public/{public_key}", response_model=BotPublicConfig)
def public_bot_config(public_key: str, db: Session = Depends(get_db)) -> BotPublicConfig:
    service = BotService(db)
    config = service.get_public_config(public_key)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    return config


@router.patch("/{bot_id}", response_model=BotRead)
def update_bot(
    bot_id: str,
    payload: BotUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> BotRead:
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.organization_id == current_user.organization_id).first()
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    updated = BotService(db).update_bot(bot, payload)
    return BotRead.model_validate(updated)
