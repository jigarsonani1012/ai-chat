from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.organization import Organization
from app.db.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserRead


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def signup(self, payload: SignupRequest) -> TokenResponse:
        existing = self.db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise ValueError("User already exists")

        organization = Organization(name=payload.organization_name)
        self.db.add(organization)
        self.db.flush()

        user = User(
            organization_id=organization.id,
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return TokenResponse(access_token=create_access_token(user.id), user=UserRead.model_validate(user))

    def login(self, payload: LoginRequest) -> TokenResponse | None:
        user = self.db.query(User).filter(User.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            return None

        return TokenResponse(access_token=create_access_token(user.id), user=UserRead.model_validate(user))
