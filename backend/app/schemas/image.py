from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ModelType = Literal["dcgan", "cyclegan", "stylegan"]


class GenerateRequest(BaseModel):
    model_type: ModelType = "dcgan"
    num_images: int = Field(default=4, ge=1, le=16)
    latent_dim: int = Field(default=100, ge=16, le=512)
    checkpoint_name: str | None = None
    image_size: int = Field(default=64, ge=32, le=256)
    prompt: str | None = Field(default=None, max_length=500)


class TransformRequest(BaseModel):
    checkpoint_name: str | None = None
    direction: Literal["summer2winter", "winter2summer", "horse2zebra", "zebra2horse"] = "summer2winter"


class UploadResponse(BaseModel):
    image_id: str
    filename: str
    url: str
    message: str


class GeneratedImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_type: str
    prompt: str | None
    original_filename: str | None
    storage_key: str
    public_url: str
    width: int
    height: int
    created_at: datetime


class GenerateResponse(BaseModel):
    model_type: str
    images: list[GeneratedImageResponse]
    message: str

