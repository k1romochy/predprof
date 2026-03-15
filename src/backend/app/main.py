import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import async_session_factory, engine
from .core.exceptions import AppException, app_exception_handler
from .models import Base
from .repositories.user import UserRepository
from .routers import admin, analytics, auth, predict
from .services.auth import hash_password

logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        repo = UserRepository(session)
        existing = await repo.get_by_username(settings.admin_username)
        if not existing:
            await repo.create(
                username=settings.admin_username,
                hashed_password=hash_password(settings.admin_password),
                first_name="Admin",
                last_name="Admin",
                role="admin",
            )
            logger.info("Admin user created")

    yield

    await engine.dispose()


app = FastAPI(title="Alien Signal Classifier API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(predict.router)
app.include_router(analytics.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
