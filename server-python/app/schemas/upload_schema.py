
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class UploadFileInfo(BaseModel):
	originalname: str
	filename: str
	path: str
	mimetype: str
	size: int


class UploadParsedPage(BaseModel):
	page_number: int = Field(..., ge=1)
	text: str


class UploadParsedDocument(BaseModel):
	pages: list[UploadParsedPage]
	text: str


class UploadIngestionResult(BaseModel):
	success: bool = True
	chunk_count: int = 0
	metadata: dict[str, Any] = Field(default_factory=dict)


class UploadStoredFile(BaseModel):
	_id: str
	file_id: str | None = None
	chatId: str
	userId: str
	filename: str
	uploadedAt: Any


class UploadResponse(BaseModel):
	success: bool = True
	file: UploadFileInfo
	parsed: UploadParsedDocument
	ingestion: UploadIngestionResult
	storedFile: UploadStoredFile | None = None

