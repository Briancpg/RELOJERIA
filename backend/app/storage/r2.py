from dataclasses import dataclass
from uuid import uuid4

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from starlette import status

from app.core.config import settings
from app.core.exceptions import AppError


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def detect_image_content_type(content: bytes) -> str | None:
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return None


@dataclass(frozen=True)
class StoredObject:
    key: str
    public_url: str | None


class R2Storage:
    def __init__(self) -> None:
        if not all(
            [
                settings.r2_endpoint_url,
                settings.r2_access_key_id,
                settings.r2_secret_access_key,
                settings.r2_bucket_name,
            ]
        ):
            raise AppError("R2 storage is not configured")
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )

    def upload_image(self, *, repair_id: int, file_name: str, content_type: str, content: bytes) -> StoredObject:
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise AppError("Unsupported image type")
        if not content:
            raise AppError("Image cannot be empty")
        detected_content_type = detect_image_content_type(content)
        if detected_content_type != content_type:
            raise AppError("Image content does not match its declared type")
        max_bytes = settings.max_image_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise AppError(f"Image exceeds {settings.max_image_upload_mb} MB")

        extension = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else "bin"
        key = f"repairs/{repair_id}/{uuid4()}.{extension}"
        try:
            self.client.put_object(
                Bucket=settings.r2_bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
            )
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "R2Error")
            raise AppError(f"R2 upload failed: {error_code}", status.HTTP_502_BAD_GATEWAY) from exc
        except BotoCoreError as exc:
            raise AppError("R2 upload failed: storage endpoint is not reachable", status.HTTP_502_BAD_GATEWAY) from exc
        public_url = f"{settings.r2_public_base_url.rstrip('/')}/{key}" if settings.r2_public_base_url else None
        return StoredObject(key=key, public_url=public_url)

    def download_image(self, *, key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=settings.r2_bucket_name, Key=key)
            body = response["Body"]
            return body.read()
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code in {"NoSuchKey", "404"}:
                raise AppError("Image not found", status.HTTP_404_NOT_FOUND) from exc
            raise AppError("Image storage is not available", status.HTTP_502_BAD_GATEWAY) from exc
