from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.models.image import GeneratedImage
from backend.app.models.user import User
from backend.app.schemas.image import (
    GenerateRequest,
    GenerateResponse,
    GeneratedImageResponse,
    TransformRequest,
    UploadResponse,
)
from backend.app.services.gan_service import gan_service
from backend.app.services.storage import storage_service

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_201_CREATED)
def generate_images(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GenerateResponse:
    if payload.model_type == "stylegan":
        raise HTTPException(status_code=501, detail="stylegan integration requires external pretrained weights")
    if payload.model_type != "dcgan":
        raise HTTPException(status_code=400, detail="use /transform for CycleGAN workflows")

    images_bytes = gan_service.generate_dcgan(
        latent_dim=payload.latent_dim,
        num_images=payload.num_images,
        checkpoint_name=payload.checkpoint_name,
        image_size=payload.image_size,
    )
    records: list[GeneratedImage] = []
    for content in images_bytes:
        storage_key, public_url = storage_service.save_bytes(content, prefix="generated")
        record = GeneratedImage(
            user_id=current_user.id,
            model_type=payload.model_type,
            prompt=payload.prompt,
            storage_key=storage_key,
            public_url=public_url,
            width=payload.image_size,
            height=payload.image_size,
        )
        db.add(record)
        records.append(record)

    db.commit()
    for record in records:
        db.refresh(record)

    return GenerateResponse(
        model_type=payload.model_type,
        images=[GeneratedImageResponse.model_validate(record) for record in records],
        message="images generated successfully",
    )


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UploadResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="only image uploads are supported")

    storage_key, public_url = await storage_service.save_upload(file)
    record = GeneratedImage(
        user_id=current_user.id,
        model_type="upload",
        original_filename=file.filename,
        storage_key=storage_key,
        public_url=public_url,
        width=0,
        height=0,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return UploadResponse(image_id=record.id, filename=file.filename or storage_key, url=public_url, message="upload complete")


@router.post("/transform", response_model=GeneratedImageResponse, status_code=status.HTTP_201_CREATED)
async def transform_image(
    file: UploadFile = File(...),
    checkpoint_name: str | None = Form(default=None),
    direction: str = Form(default="summer2winter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GeneratedImageResponse:
    payload = TransformRequest(checkpoint_name=checkpoint_name, direction=direction)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="only image uploads are supported")

    transformed = gan_service.transform_cyclegan(await file.read(), payload.checkpoint_name)
    storage_key, public_url = storage_service.save_bytes(transformed, prefix=f"transform-{payload.direction}")
    record = GeneratedImage(
        user_id=current_user.id,
        model_type="cyclegan",
        original_filename=file.filename,
        prompt=payload.direction,
        storage_key=storage_key,
        public_url=public_url,
        width=256,
        height=256,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return GeneratedImageResponse.model_validate(record)


@router.get("/images", response_model=list[GeneratedImageResponse])
def list_images(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GeneratedImageResponse]:
    records = (
        db.query(GeneratedImage)
        .filter(GeneratedImage.user_id == current_user.id)
        .order_by(GeneratedImage.created_at.desc())
        .all()
    )
    return [GeneratedImageResponse.model_validate(record) for record in records]
