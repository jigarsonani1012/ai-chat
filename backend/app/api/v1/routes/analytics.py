from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.schemas.analytics import AnalyticsOverview
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
def analytics_overview(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> AnalyticsOverview:
    return AnalyticsService(db).get_overview(current_user.organization_id)
