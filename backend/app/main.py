from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api.router import api_router
from backend.app.core.config import get_settings
from backend.app.core.database import Base, engine
from backend.app.core.logging import configure_logging, get_logger
from backend.app.core.rate_limit import RateLimitMiddleware
from backend.app.models import image, training_job, user  # noqa: F401
from backend.app.websockets.router import websocket_router

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("starting backend")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("stopping backend")


app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="Production-ready GAN Studio API with DCGAN, CycleGAN, auth, storage, and async training.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, limit_per_minute=settings.rate_limit_per_minute)

app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(websocket_router)
app.mount("/storage", StaticFiles(directory=settings.local_storage_dir.parent), name="storage")


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"message": f"{settings.project_name} is running"}
