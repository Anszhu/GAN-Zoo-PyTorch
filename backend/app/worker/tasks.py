from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.core.logging import get_logger
from backend.app.models.training_job import TrainingJob
from backend.app.services.training_service import training_service
from backend.app.worker.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="train_dcgan")
def train_dcgan_task(job_id: str) -> dict[str, str]:
    db: Session = SessionLocal()
    job = None
    try:
        job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
        if not job:
            raise ValueError(f"training job {job_id} not found")

        job.status = "running"
        db.commit()

        checkpoint_path, metrics_json = training_service.train_dcgan(
            dataset_name=job.dataset_name,
            epochs=job.epochs,
            batch_size=job.batch_size,
            latent_dim=job.latent_dim,
            learning_rate=float(job.learning_rate),
            beta1=float(job.beta1),
            image_size=job.image_size,
        )
        job.status = "completed"
        job.checkpoint_path = checkpoint_path
        job.metrics_json = metrics_json
        db.commit()
        return {"job_id": job.id, "status": job.status}
    except Exception as exc:
        if job is not None:
            job.status = "failed"
            job.error_message = str(exc)
            db.commit()
        logger.exception("training task failed")
        raise
    finally:
        db.close()
