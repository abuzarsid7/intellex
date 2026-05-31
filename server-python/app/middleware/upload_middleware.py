from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi import HTTPException, UploadFile, status


TMP_DIR = Path.cwd() / "uploads" / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_SIZE = 20 * 1024 * 1024
PDF_MIME_TYPES = {"application/pdf"}


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    safe = re.sub(r"[^a-zA-Z0-9.\- _]", "_", name)
    return safe or "upload.pdf"


async def validate_pdf_upload(file: UploadFile) -> None:
    extension = Path(file.filename or "").suffix.lower()
    if file.content_type not in PDF_MIME_TYPES and extension != ".pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    # FastAPI reads the whole file lazily, so validate the declared size only after saving.


def build_tmp_path(filename: str) -> Path:
    safe_name = sanitize_filename(filename)
    timestamp = int(__import__("time").time() * 1000)
    return TMP_DIR / f"{timestamp}-{safe_name}"
