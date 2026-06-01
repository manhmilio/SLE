import io
import uuid
from functools import lru_cache

from minio import Minio
from minio.error import S3Error

from app.core.config import settings

# Các loại file ảnh cho phép
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

# Giới hạn 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_USE_SSL,
    )


def ensure_bucket_exists(bucket_name: str) -> None:
    """Tạo bucket nếu chưa tồn tại."""
    client = get_minio_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        # Public read policy để truy cập ảnh qua URL
        policy = f"""{{
            "Version": "2012-10-17",
            "Statement": [{{
                "Effect": "Allow",
                "Principal": {{"AWS": ["*"]}},
                "Action": ["s3:GetObject"],
                "Resource": ["arn:aws:s3:::{bucket_name}/*"]
            }}]
        }}"""
        client.set_bucket_policy(bucket_name, policy)


def upload_avatar(file_data: bytes, content_type: str, user_id: uuid.UUID) -> str:
    """
    Upload ảnh avatar lên MinIO.
    Trả về public URL của ảnh.
    Raises ValueError nếu file không hợp lệ.
    """
    # Validate content type
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(
            f"File type not allowed. Accepted: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    # Validate file size
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds 5MB limit")

    # Tạo tên file unique theo user_id
    ext = content_type.split("/")[-1]   # jpeg / png / webp / gif
    if ext == "jpeg":
        ext = "jpg"
    object_name = f"{user_id}/avatar.{ext}"

    bucket = settings.MINIO_BUCKET_AVATARS
    ensure_bucket_exists(bucket)

    client = get_minio_client()
    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=io.BytesIO(file_data),
        length=len(file_data),
        content_type=content_type,
    )

    # Trả về public URL
    # Nếu dùng presigned URL (private bucket): client.presigned_get_object(...)
    endpoint = settings.MINIO_ENDPOINT
    scheme = "https" if settings.MINIO_USE_SSL else "http"
    return f"{scheme}://{endpoint}/{bucket}/{object_name}"