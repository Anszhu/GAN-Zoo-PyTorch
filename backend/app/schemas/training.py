from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TrainRequest(BaseModel):
    model_type: Literal["dcgan", "cyclegan"] = "dcgan"
    dataset_name: Literal["mnist", "celeba", "custom"] = "mnist"
    epochs: int = Field(default=5, ge=1, le=500)
    batch_size: int = Field(default=64, ge=8, le=512)
    latent_dim: int = Field(default=100, ge=16, le=512)
    learning_rate: float = Field(default=0.0002, gt=0, le=0.01)
    beta1: float = Field(default=0.5, ge=0, lt=1)
    image_size: int = Field(default=64, ge=32, le=256)


class TrainingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_type: str
    dataset_name: str
    status: str
    epochs: int
    batch_size: int
    latent_dim: int
    learning_rate: str
    beta1: str
    image_size: int
    checkpoint_path: str | None
    metrics_json: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
