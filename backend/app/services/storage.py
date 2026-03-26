from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import Config
from fastapi import UploadFile

from backend.app.core.config import get_settings

settings = get_settings()


class StorageService:
    def __init__(self) -> None:
        self.base_dir = settings.local_storage_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.s3_client = None
        if settings.aws_s3_enabled and settings.aws_s3_bucket:
            self.s3_client = boto3.client(
                "s3",
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                config=Config(signature_version="s3v4"),
            )

    def save_bytes(self, content: bytes, suffix: str = ".png", prefix: str = "generated") -> tuple[str, str]:
        filename = f"{prefix}-{uuid4().hex}{suffix}"
        local_path = self.base_dir / filename
        local_path.write_bytes(content)
        if self.s3_client:
            self.s3_client.upload_file(str(local_path), settings.aws_s3_bucket, filename)
            url = f"https://{settings.aws_s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{filename}"
            return filename, url
        return filename, f"/storage/images/{filename}"

    async def save_upload(self, upload: UploadFile) -> tuple[str, str]:
        content = await upload.read()
        suffix = Path(upload.filename or "upload.png").suffix or ".png"
        return self.save_bytes(content, suffix=suffix, prefix="upload")

    def open_local(self, storage_key: str) -> BytesIO:
        return BytesIO((self.base_dir / storage_key).read_bytes())


storage_service = StorageService()

