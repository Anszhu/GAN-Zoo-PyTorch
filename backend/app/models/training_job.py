from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class TrainingJob(Base):
    __tablename__ = "training_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    model_type: Mapped[str] = mapped_column(String(32))
    dataset_name: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    epochs: Mapped[int] = mapped_column(Integer, default=5)
    batch_size: Mapped[int] = mapped_column(Integer, default=64)
    latent_dim: Mapped[int] = mapped_column(Integer, default=100)
    learning_rate: Mapped[str] = mapped_column(String(32), default="0.0002")
    beta1: Mapped[str] = mapped_column(String(32), default="0.5")
    image_size: Mapped[int] = mapped_column(Integer, default=64)
    checkpoint_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="jobs")
