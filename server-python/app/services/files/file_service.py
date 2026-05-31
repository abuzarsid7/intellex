from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any
import logging

from app.core.config import settings
from app.core.database import get_database


FILES_COLLECTION = "files"
MONGO_DB_NAME = settings.MONGO_DB_NAME


logger = logging.getLogger("intellex.files")


def _db():
	return get_database(MONGO_DB_NAME)


def _files():
	return _db()[FILES_COLLECTION]


async def ensure_file_storage_indexes() -> None:
	await _files().create_index([("chatId", 1), ("uploadedAt", -1)])
	await _files().create_index([("userId", 1), ("uploadedAt", -1)])


async def add_uploaded_file(*, chat_id: str, user_id: str, filename: str, file_id: str) -> dict[str, Any]:
	now = datetime.now(timezone.utc)
	document = {
		"_id": f"file_{uuid4().hex}",
		"file_id": file_id,
		"chatId": chat_id,
		"userId": user_id,
		"filename": filename,
		"uploadedAt": now,
	}
	result = await _files().insert_one(document)
	created = await _files().find_one({"_id": result.inserted_id})
	if not created:
		created = document
	logger.info("Stored file %s for chat %s", filename, chat_id)
	return {
		"_id": str(created.get("_id") or document["_id"]),
		"file_id": created.get("file_id") or file_id,
		"chatId": created.get("chatId"),
		"userId": created.get("userId"),
		"filename": created.get("filename"),
		"uploadedAt": created.get("uploadedAt") or created.get("uploaded_at"),
	}


async def get_chat_files(chat_id: str, user_id: str | None = None) -> list[dict[str, Any]]:
	query: dict[str, Any] = {"chatId": chat_id}
	if user_id:
		query["userId"] = user_id

	cursor = _files().find(query).sort("uploadedAt", -1)
	files: list[dict[str, Any]] = []
	async for file in cursor:
		files.append(
			{
				"_id": str(file.get("_id") or ""),
				"file_id": file.get("file_id"),
				"chatId": file.get("chatId"),
				"userId": file.get("userId"),
				"filename": file.get("filename"),
				"uploadedAt": file.get("uploadedAt") or file.get("uploaded_at"),
			}
		)
	return files


__all__ = ["FILES_COLLECTION", "ensure_file_storage_indexes", "add_uploaded_file", "get_chat_files"]
