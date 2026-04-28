from secrets import token_urlsafe

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import TimestampMixin, UUIDMixin
from app.db.session import Base


def default_escalation_emails() -> dict[str, str]:
    return {
        "refund": "billing@example.com",
        "complaint": "support@example.com",
        "urgent": "priority@example.com",
        "sales": "sales@example.com",
        "technical_support": "support@example.com",
        "billing": "billing@example.com",
    }


class Bot(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "bots"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    public_key: Mapped[str] = mapped_column(String(255), unique=True, default=lambda: f"pk_{token_urlsafe(24)}")
    welcome_message: Mapped[str] = mapped_column(
        Text,
        default="Hi, how can I help you today using the available documentation?",
    )
    primary_color: Mapped[str] = mapped_column(String(32), default="#14532d")
    escalation_emails: Mapped[dict] = mapped_column(
        JSON,
        default=default_escalation_emails,
    )

    organization = relationship("Organization", back_populates="bots")
    documents = relationship("Document", back_populates="bot")
