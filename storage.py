import os
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
B2_ENDPOINT = os.getenv("B2_ENDPOINT")
B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_REGION = os.getenv("B2_REGION", "us-east-005")

if not all([BUCKET_NAME, B2_ENDPOINT, B2_KEY_ID, B2_APPLICATION_KEY]):
    raise ValueError("Missing Backblaze B2 configuration in environment")

s3 = boto3.client(
    "s3",
    endpoint_url=B2_ENDPOINT,
    aws_access_key_id=B2_KEY_ID,
    aws_secret_access_key=B2_APPLICATION_KEY,
    region_name=B2_REGION,
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
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

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MiB


def upload_file(file, complaint_id):
    if file is None:
        raise ValueError("No file provided")

    mime_type = getattr(file, "content_type", None)
    if mime_type not in ALLOWED_TYPES:
        raise ValueError("Unsupported file type")

    file_obj = getattr(file, "file", None)
    if file_obj is None:
        raise ValueError("Invalid uploaded file object")

    # Determine actual size rather than trusting a client-provided value.
    file_obj.seek(0, 2)
    file_size = file_obj.tell()
    file_obj.seek(0)

    if file_size == 0:
        raise ValueError("Empty file")

    if file_size > MAX_FILE_SIZE:
        raise ValueError("File exceeds 50 MB limit")

    extension = Path(getattr(file, "filename", "") or "").suffix.lower()
    storage_key = f"complaints/{complaint_id}/{uuid4().hex}{extension}"

    try:
        s3.upload_fileobj(
            file_obj,
            BUCKET_NAME,
            storage_key,
            ExtraArgs={"ContentType": mime_type},
        )
    finally:
        if not file_obj.closed:
            file_obj.seek(0)

    return {
        "storage_key": storage_key,
        "mime_type": mime_type,
        "file_size": file_size,
    }


def delete_file(storage_key):
    s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=storage_key,
    )
