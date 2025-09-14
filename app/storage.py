import os
import shutil
from pathlib import Path

import boto3
from fastapi import UploadFile

STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "storage"))
S3_BUCKET = os.getenv("S3_BUCKET")

STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def save_file(upload: UploadFile) -> str:
    """Save an uploaded file. Returns the storage path or S3 URI."""
    if S3_BUCKET:
        client = boto3.client("s3")
        client.upload_fileobj(upload.file, S3_BUCKET, upload.filename)
        return f"s3://{S3_BUCKET}/{upload.filename}"
    else:
        destination = STORAGE_DIR / upload.filename
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)
        return str(destination)


def delete_file(path: str) -> None:
    if path.startswith("s3://"):
        client = boto3.client("s3")
        bucket, key = path.replace("s3://", "").split("/", 1)
        client.delete_object(Bucket=bucket, Key=key)
    else:
        try:
            Path(path).unlink()
        except FileNotFoundError:
            pass


def get_file_url(path: str) -> str:
    if path.startswith("s3://"):
        bucket, key = path.replace("s3://", "").split("/", 1)
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    else:
        return "/files/" + Path(path).name
