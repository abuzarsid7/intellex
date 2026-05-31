
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Optional
import logging

from bson import ObjectId
from pymongo import ReturnDocument

from app.core.config import settings
from app.core.database import get_database
from app.services.ai.llm_service import generate_ai_response
from app.services.ai.llm_service import generate_rag_response
from app.services.rag.retrieval_service import retrieve_document_context
from app.services.files.file_service import get_chat_files


CHATS_COLLECTION = "chats"
MESSAGES_COLLECTION = "messages"
MONGO_DB_NAME = settings.MONGO_DB_NAME


logger = logging.getLogger("intellex.chat")


def _db():
	return get_database(MONGO_DB_NAME)


def _chats():
	return _db()[CHATS_COLLECTION]


def _messages():
	return _db()[MESSAGES_COLLECTION]


async def ensure_chat_storage_indexes() -> None:
	"""Create the chat/message indexes used by the application."""
	await _chats().create_index([("userId", 1), ("createdAt", -1)])
	await _messages().create_index([("chatId", 1), ("createdAt", 1)])
	await _messages().create_index([("chat", 1), ("created_at", 1)])


def _to_object_id(value: str) -> ObjectId:
	try:
		return ObjectId(value)
	except Exception as exc:
		raise ValueError("Invalid id") from exc


def _chat_id_filter(chat_id: str) -> dict[str, Any]:
	filters: list[dict[str, Any]] = [{"_id": chat_id}]
	try:
		filters.append({"_id": _to_object_id(chat_id)})
	except Exception:
		pass
	return {"$or": filters}


def _legacy_chat_message_filter(chat_id: str) -> dict[str, Any] | None:
	try:
		return {"chat": _to_object_id(chat_id)}
	except Exception:
		return None


def _chat_user_filter(user_id: str) -> dict[str, Any]:
	legacy_filter: dict[str, Any] | None = None
	try:
		legacy_filter = {"user": _to_object_id(user_id)}
	except Exception:
		legacy_filter = None

	return {
		"$or": [
			{"userId": user_id},
			*([legacy_filter] if legacy_filter else []),
		],
	}


def _serialize_chat(chat: dict[str, Any]) -> dict[str, Any]:
	user_id = chat.get("userId") or chat.get("user")
	return {
		"_id": str(chat.get("_id") or chat.get("id") or ""),
		"userId": str(user_id) if user_id else None,
		"title": chat.get("title"),
		"createdAt": chat.get("createdAt") or chat.get("created_at"),
		"updatedAt": chat.get("updatedAt") or chat.get("updated_at"),
	}


def _serialize_message(message: dict[str, Any]) -> dict[str, Any]:
	chat_id = message.get("chatId") or message.get("chat")
	created_at = message.get("createdAt") or message.get("created_at")
	return {
		"_id": str(message.get("_id") or message.get("id") or ""),
		"chatId": str(chat_id) if chat_id else None,
		"role": message.get("role"),
		"content": message.get("content"),
		"createdAt": created_at,
	}


async def create_chat(user_id: str, title: str = "New Chat", description: str | None = None) -> dict[str, Any]:
	try:
		now = datetime.now(timezone.utc)
		chat_id = f"chat_{uuid4().hex}"
		document = {
			"_id": chat_id,
			"userId": user_id,
			"title": title or "New Chat",
			"createdAt": now,
			"updatedAt": now,
		}
		result = await _chats().insert_one(document)
		created = await _chats().find_one({"_id": result.inserted_id})
		if not created:
			raise ValueError("Failed to create chat")
		logger.info("Created chat %s for user %s", result.inserted_id, user_id)
		return _serialize_chat(created)
	except Exception as exc:
		raise RuntimeError(f"Failed to create chat: {exc}") from exc


async def get_user_chats(user_id: str, limit: int = 50, skip: int = 0) -> list[dict[str, Any]]:
	try:
		cursor = (
			_chats()
			.find(_chat_user_filter(user_id))
			.sort("createdAt", -1)
			.skip(skip)
			.limit(limit)
		)
		return [_serialize_chat(chat) async for chat in cursor]
	except Exception as exc:
		raise RuntimeError(f"Failed to fetch chats: {exc}") from exc


async def get_chat_by_id(chat_id: str, user_id: str) -> dict[str, Any]:
	try:
		chat = await _chats().find_one({"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]})
		if not chat:
			raise ValueError("Chat not found")

		legacy_filter = _legacy_chat_message_filter(chat_id)
		if legacy_filter:
			message_count = await _messages().count_documents({"$or": [{"chatId": chat_id}, legacy_filter]})
		else:
			message_count = await _messages().count_documents({"chatId": chat_id})
		result = _serialize_chat(chat)
		result["messageCount"] = message_count
		return result
	except Exception as exc:
		raise RuntimeError(f"Failed to fetch chat: {exc}") from exc


async def update_chat_title(chat_id: str, user_id: str, title: str) -> dict[str, Any]:
	try:
		chat = await _chats().find_one_and_update(
			{"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]},
			{"$set": {"title": title, "updatedAt": datetime.now(timezone.utc)}},
			return_document=ReturnDocument.AFTER,
		)
		if not chat:
			raise ValueError("Chat not found")
		return _serialize_chat(chat)
	except Exception as exc:
		raise RuntimeError(f"Failed to update chat: {exc}") from exc


async def delete_chat(chat_id: str, user_id: str) -> dict[str, str]:
	try:
		chat = await _chats().find_one({"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]})
		if not chat:
			raise ValueError("Chat not found")

		message_filter = {"chatId": chat_id}
		legacy_message_filter = _legacy_chat_message_filter(chat_id)
		if legacy_message_filter:
			message_filter = {"$or": [message_filter, legacy_message_filter]}
		await _messages().delete_many(message_filter)
		chat_delete_filter = {"_id": chat_id}
		try:
			chat_delete_filter = {"$or": [{"_id": chat_id}, {"_id": _to_object_id(chat_id)}]}
		except Exception:
			pass
		await _chats().delete_one(chat_delete_filter)
		return {"message": "Chat deleted successfully"}
	except Exception as exc:
		raise RuntimeError(f"Failed to delete chat: {exc}") from exc


async def add_message(chat_id: str, role: str, content: str, user_id: str) -> dict[str, Any]:
	try:
		chat = await _chats().find_one({"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]})
		if not chat:
			raise ValueError("Chat not found")

		now = datetime.now(timezone.utc)
		document = {
			"chatId": chat_id,
			"role": role,
			"content": content,
			"createdAt": now,
		}
		result = await _messages().insert_one(document)
		created = await _messages().find_one({"_id": result.inserted_id})
		if not created:
			raise ValueError("Failed to add message")
		return _serialize_message(created)
	except Exception as exc:
		raise RuntimeError(f"Failed to add message: {exc}") from exc


async def get_chat_messages(chat_id: str, user_id: str, limit: int = 100, skip: int = 0) -> list[dict[str, Any]]:
	try:
		chat = await _chats().find_one({"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]})
		if not chat:
			raise ValueError("Chat not found")

		cursor = (
			_messages()
			.find({"chatId": chat_id})
			.sort("createdAt", 1)
			.skip(skip)
			.limit(limit)
		)
		messages = [_serialize_message(message) async for message in cursor]
		if messages:
			return messages
		legacy_cursor = (
			_messages()
			.find(_legacy_chat_message_filter(chat_id) or {"chatId": chat_id})
			.sort("created_at", 1)
			.skip(skip)
			.limit(limit)
		)
		return [_serialize_message(message) async for message in legacy_cursor]
	except Exception as exc:
		raise RuntimeError(f"Failed to fetch messages: {exc}") from exc


async def get_recent_messages(chat_id: str, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
	try:
		chat = await _chats().find_one({"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]})
		if not chat:
			raise ValueError("Chat not found")

		cursor = _messages().find({"chatId": chat_id}).sort("createdAt", -1).limit(limit)
		messages = [_serialize_message(message) async for message in cursor]
		if not messages:
			legacy_filter = _legacy_chat_message_filter(chat_id)
			legacy_cursor = _messages().find(legacy_filter or {"chatId": chat_id}).sort("created_at", -1).limit(limit)
			messages = [_serialize_message(message) async for message in legacy_cursor]
		messages.reverse()
		return messages
	except Exception as exc:
		raise RuntimeError(f"Failed to fetch recent messages: {exc}") from exc


async def clear_chat_messages(chat_id: str, user_id: str) -> dict[str, str]:
	try:
		chat = await _chats().find_one({"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]})
		if not chat:
			raise ValueError("Chat not found")

		message_filter = {"chatId": chat_id}
		legacy_message_filter = _legacy_chat_message_filter(chat_id)
		if legacy_message_filter:
			message_filter = {"$or": [message_filter, legacy_message_filter]}
		await _messages().delete_many(message_filter)
		return {"message": "Chat messages cleared successfully"}
	except Exception as exc:
		raise RuntimeError(f"Failed to clear messages: {exc}") from exc


def _build_question_prompt(user_message: str, context: str, history: list[dict[str, Any]] | None = None) -> str:
	history = history or []
	history_lines = []
	for message in history:
		role = str(message.get("role") or "user").strip().capitalize()
		content = str(message.get("content") or "").strip()
		if content:
			history_lines.append(f"{role}: {content}")

	sections = [
		"You are a helpful assistant answering questions about uploaded documents.",
		"Use the retrieved context as the primary source of truth.",
		"If the context is insufficient, say so clearly.",
		"",
		"Retrieved context:",
		context.strip() if context else "",
		"",
		"Conversation history:",
		"\n".join(history_lines) if history_lines else "None",
		"",
		f"User question: {user_message.strip()}",
	]
	return "\n".join(section for section in sections if section is not None)


def _synthetic_message(chat_id: str, role: str, content: str) -> dict[str, Any]:
	return {
		"_id": f"temp_{uuid4().hex}",
		"chatId": chat_id,
		"role": role,
		"content": content,
		"createdAt": datetime.now(timezone.utc),
	}


async def answer_user_question(
	*,
	chat_id: str,
	user_id: str,
	question: str,
	use_rag: bool = True,
	history_limit: int = 10,
	retrieval_options: dict[str, Any] | None = None,
	llm_model: str | None = None,
	create_chat_if_missing: bool = True,
	chat_title: str | None = None,
) -> dict[str, Any]:
	question_text = str(question or "").strip()
	if not question_text:
		raise ValueError("Question is required")

	chat = await _chats().find_one({"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]})
	if not chat:
		if not create_chat_if_missing:
			raise ValueError("Chat not found")
		chat = await _chats().find_one_and_update(
			{"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]},
			{"$setOnInsert": {
				"userId": user_id,
				"title": chat_title or "New Chat",
				"createdAt": datetime.now(timezone.utc),
				"updatedAt": datetime.now(timezone.utc),
			}},
			upsert=True,
			return_document=ReturnDocument.AFTER,
		)

	recent_messages = await get_recent_messages(chat_id, user_id, limit=history_limit)
	retrieval = {"chunks": [], "context": ""}
	context = ""
	collection_name = settings.CHROMA_COLLECTION_NAME
	logger.info("answer_user_question chat_id=%s collection_name=%s use_rag=%s", chat_id, collection_name, use_rag)
	if use_rag:
		try:
			retrieval = retrieve_document_context(question_text, {**(retrieval_options or {}), "collectionName": collection_name})
		except Exception:
			logger.exception("RAG retrieval failed for chat_id=%s", chat_id)
			retrieval = {"chunks": [], "context": ""}
		context = retrieval.get("context") or ""
	prompt = _build_question_prompt(question_text, context, recent_messages)

	conversation_history = [
		{"role": message.get("role"), "content": message.get("content")}
		for message in recent_messages
	]

	if use_rag:
		answer = generate_rag_response(
			user_message=question_text,
			document_context=context,
			history=conversation_history,
			model=llm_model,
		)
	else:
		answer = generate_ai_response(
			user_message=question_text,
			history=conversation_history,
			model=llm_model,
		)

	try:
		user_saved = await add_message(chat_id, "user", question_text, user_id)
	except Exception:
		logger.exception("Failed to persist user message for chat_id=%s", chat_id)
		user_saved = _synthetic_message(chat_id, "user", question_text)

	try:
		assistant_saved = await add_message(chat_id, "assistant", answer, user_id)
	except Exception:
		logger.exception("Failed to persist assistant message for chat_id=%s", chat_id)
		assistant_saved = _synthetic_message(chat_id, "assistant", answer)

	await _chats().update_one(
		{"$and": [_chat_id_filter(chat_id), _chat_user_filter(user_id)]},
		{"$set": {"updatedAt": datetime.now(timezone.utc)}}
	)

	return {
		"chatId": chat_id,
		"userMessage": user_saved,
		"assistantMessage": assistant_saved,
		"answer": answer,
		"retrieval": retrieval,
		"prompt": prompt,
	}


__all__ = [
	"ensure_chat_storage_indexes",
	"create_chat",
	"get_user_chats",
	"get_chat_by_id",
	"get_chat_files",
	"update_chat_title",
	"delete_chat",
	"add_message",
	"get_chat_messages",
	"get_recent_messages",
	"clear_chat_messages",
	"answer_user_question",
]
