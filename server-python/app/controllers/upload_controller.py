
from __future__ import annotations

from pathlib import Path
from typing import Any
import logging

from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from app.core.config import settings
from app.middleware.upload_middleware import build_tmp_path, validate_pdf_upload
from app.services.rag.ingest_service import ingest_parsed_document
from app.services.files.file_service import add_uploaded_file

logger = logging.getLogger("intellex.upload")
from app.schemas.upload_schema import (
	UploadParsedDocument,
	UploadParsedPage,
	UploadResponse,
	UploadFileInfo,
	UploadIngestionResult,
)


def _user_id_from_current_user(current_user) -> str:
	if not current_user:
		return ""

	if isinstance(current_user, dict):
		return str(current_user.get("_id") or current_user.get("id") or "")

	if hasattr(current_user, "id"):
		return str(getattr(current_user, "id"))

	return ""


def _build_file_id(filename: str | None) -> str:
	name = Path(filename or "").stem.strip().lower()
	if not name:
		return f"file_{int(__import__('time').time() * 1000)}"

	file_id = []
	for character in name:
		if character.isalnum():
			file_id.append(character)
		elif file_id and file_id[-1] != "_":
			file_id.append("_")

	value = "".join(file_id).strip("_")
	return value or f"file_{int(__import__('time').time() * 1000)}"


async def _save_upload_to_tmp(file: UploadFile) -> tuple[Path, int]:
	destination = build_tmp_path(file.filename or "upload.pdf")
	size = 0

	try:
		with destination.open("wb") as buffer:
			while True:
				chunk = await file.read(1024 * 1024)
				if not chunk:
					break

				size += len(chunk)
				if size > 20 * 1024 * 1024:
					raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")

				buffer.write(chunk)
	finally:
		await file.close()

	return destination, size


def _parse_pdf(path: Path) -> UploadParsedDocument:
	reader = PdfReader(str(path))
	pages: list[UploadParsedPage] = []
	page_text_parts: list[str] = []

	for page_number, page in enumerate(reader.pages, start=1):
		text = page.extract_text() or ""
		pages.append(UploadParsedPage(page_number=page_number, text=text))
		if text:
			page_text_parts.append(text)

	return UploadParsedDocument(pages=pages, text="\n\n".join(page_text_parts))


async def upload_pdf(file: UploadFile, chat_id: str | None = None, current_user=None) -> UploadResponse:
	await validate_pdf_upload(file)
	tmp_path, size = await _save_upload_to_tmp(file)

	try:
		user_id = _user_id_from_current_user(current_user)
		if not user_id:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

		file_id = _build_file_id(file.filename or tmp_path.name)
		logger.info("upload_pdf start chat_id=%s filename=%s", chat_id, file.filename)
		parsed = _parse_pdf(tmp_path)
		stored_file = await add_uploaded_file(
			chat_id=chat_id or "",
			user_id=user_id,
			filename=file.filename or tmp_path.name,
			file_id=file_id,
		)

		ingestion_success = True
		ingestion_metadata: dict[str, Any] = {
			"sourceId": file_id,
			"collectionName": settings.CHROMA_COLLECTION_NAME,
			"storedCount": 0,
			"ids": [],
		}
		chunk_count = 0

		if parsed.text.strip():
			try:
				ingestion_result = ingest_parsed_document(
					parsed={
						"text": parsed.text,
						"pages": [{"page_number": page.page_number, "text": page.text} for page in parsed.pages],
						"numpages": len(parsed.pages),
					},
					file={
						"originalname": file.filename or "",
						"filename": tmp_path.name,
						"path": str(tmp_path),
						"mimetype": file.content_type or "application/pdf",
						"size": size,
						"file_id": file_id,
					},
					collection_name=settings.CHROMA_COLLECTION_NAME,
					metadata={
						"user_id": user_id,
						"chat_id": chat_id,
						"file_id": file_id,
					},
				)
				chunk_count = ingestion_result["chunkCount"]
				ingestion_metadata = {
					"sourceId": ingestion_result["sourceId"],
					"collectionName": ingestion_result["collectionName"],
					"storedCount": ingestion_result["storedCount"],
					"ids": ingestion_result["ids"],
				}
			except Exception as exc:
				ingestion_success = False
				logger.exception("upload_pdf ingestion failed chat_id=%s filename=%s", chat_id, file.filename)
				ingestion_metadata = {
					"sourceId": file_id,
					"collectionName": settings.CHROMA_COLLECTION_NAME,
					"storedCount": 0,
					"ids": [],
					"error": str(exc),
				}
		else:
			ingestion_success = False
			logger.warning("upload_pdf no extractable text chat_id=%s filename=%s", chat_id, file.filename)

		logger.info("upload_pdf complete chat_id=%s success=%s", chat_id, ingestion_success)
		ingestion = UploadIngestionResult(
			success=ingestion_success,
			chunk_count=chunk_count,
			metadata=ingestion_metadata,
		)

		return UploadResponse(
			file=UploadFileInfo(
				originalname=file.filename or "",
				filename=tmp_path.name,
				path=str(tmp_path),
				mimetype=file.content_type or "application/pdf",
				size=size,
			),
			parsed=parsed,
			ingestion=ingestion,
			storedFile=stored_file,
		)
	finally:
		try:
			tmp_path.unlink(missing_ok=True)
		except Exception:
			pass

