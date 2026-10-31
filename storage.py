
import os
import boto3
from uuid import uuid4
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("B2_ENDPOINT_URL"),
    aws_access_key_id=os.getenv("B2_KEY_ID"),
    aws_secret_access_key=os.getenv("B2_APPLICATION_KEY"),
    region_name=os.getenv("B2_REGION")
)

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/ogg",
    "audio/aac",
}


def upload_file(file, complaint_id):

    mime_type = file.content_type

    if mime_type not in ALLOWED_TYPES:
        raise ValueError("Unsupported file type")

    # Check actual uploaded size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > 50 * 1024 * 1024:
        raise ValueError("File exceeds 50 MB limit")

    extension = Path(file.filename or "").suffix.lower()

    storage_key = (
        f"complaints/{complaint_id}/"
        f"{uuid4().hex}{extension}"
    )

    s3.upload_fileobj(
        file.file,
        BUCKET_NAME,
        storage_key,
        ExtraArgs={"ContentType": mime_type}
    )

    return {
        "storage_key": storage_key,
        "mime_type": mime_type,
        "file_size": file_size
    }


def delete_file(storage_key):

    s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=storage_key
    )
