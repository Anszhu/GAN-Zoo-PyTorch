from fastapi import APIRouter

from backend.app.api.routes import auth, images, training

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(images.router, tags=["images"])
api_router.include_router(training.router, tags=["training"])

