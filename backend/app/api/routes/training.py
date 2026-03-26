from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.training_job import TrainingJob
from backend.app.models.user import User
from backend.app.schemas.training import TrainRequest, TrainingJobResponse
from backend.app.worker.tasks import train_dcgan_task

router = APIRouter()


@router.post("/train", response_model=TrainingJobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_training_job(
    payload: TrainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrainingJobResponse:
    if payload.model_type != "dcgan":
        raise HTTPException(status_code=501, detail="async training is implemented for dcgan in this starter")

    job = TrainingJob(
        user_id=current_user.id,
        model_type=payload.model_type,
        dataset_name=payload.dataset_name,
        status="queued",
        epochs=payload.epochs,
        batch_size=payload.batch_size,
        latent_dim=payload.latent_dim,
        learning_rate=str(payload.learning_rate),
        beta1=str(payload.beta1),
        image_size=payload.image_size,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    train_dcgan_task.delay(job.id)
    return TrainingJobResponse.model_validate(job)


@router.get("/training-jobs", response_model=list[TrainingJobResponse])
def list_training_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TrainingJobResponse]:
    jobs = db.query(TrainingJob).filter(TrainingJob.user_id == current_user.id).order_by(TrainingJob.created_at.desc()).all()
    return [TrainingJobResponse.model_validate(job) for job in jobs]
