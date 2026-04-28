from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.rate_limit import RateLimitMiddleware
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_application() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    cors_origins = [
        settings.public_widget_origin,
        settings.admin_dashboard_origin,
        *settings.extra_cors_origins,
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(dict.fromkeys(cors_origins)),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_application()
