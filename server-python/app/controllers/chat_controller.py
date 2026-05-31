
from __future__ import annotations

from fastapi import HTTPException, Response, status

from app.core.config import settings
from app.schemas.chat_schema import ChatCreate, ChatMessageRequest, ChatTitleUpdate
from app.services.chat.chat_service import (
	answer_user_question,
	clear_chat_messages,
	create_chat,
	delete_chat,
	get_chat_by_id,
	get_chat_files,
	get_chat_messages,
	get_user_chats,
	update_chat_title,
)


def _user_id_from_current_user(current_user) -> str:
	if not current_user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

	if isinstance(current_user, dict):
		return str(current_user.get("_id") or current_user.get("id") or "")

	if hasattr(current_user, "id"):
		return str(getattr(current_user, "id"))

	raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


async def create_chat_controller(payload: ChatCreate, current_user):
	user_id = _user_id_from_current_user(current_user)
	chat = await create_chat(user_id, payload.title, payload.description)
	return {"success": True, "message": "Chat created successfully", "chat": chat}


async def get_chats_controller(
	current_user,
	page: int = 1,
	limit: int = 50,
):
	user_id = _user_id_from_current_user(current_user)
	skip = (page - 1) * limit
	chats = await get_user_chats(user_id, limit, skip)
	return {"success": True, "chats": chats, "page": page, "limit": limit}


async def get_chat_controller(chat_id: str, current_user):
	user_id = _user_id_from_current_user(current_user)
	chat = await get_chat_by_id(chat_id, user_id)
	return {"success": True, "chat": chat}


async def send_message_controller(payload: ChatMessageRequest, current_user):
	user_id = _user_id_from_current_user(current_user)
	if not payload.chat_id or not payload.message:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat ID and message are required")

	chat_id = payload.chat_id
	retrieval_options = {}
	if payload.use_rag:
		retrieval_options = {
			"collectionName": settings.CHROMA_COLLECTION_NAME,
			"where": {"user_id": user_id, "chat_id": chat_id},
			"allowFallback": False,
		}

	result = await answer_user_question(
		chat_id=chat_id,
		user_id=user_id,
		question=payload.message,
		use_rag=payload.use_rag,
		retrieval_options=retrieval_options,
	)
	return {
		"success": True,
		"message": "Message sent successfully",
		"userMessage": result["userMessage"],
		"assistantMessage": result["assistantMessage"],
	}


async def get_chat_messages_controller(
	chat_id: str,
	current_user,
	page: int = 1,
	limit: int = 100,
):
	user_id = _user_id_from_current_user(current_user)
	skip = (page - 1) * limit
	messages = await get_chat_messages(chat_id, user_id, limit, skip)
	return {"success": True, "messages": messages, "page": page, "limit": limit}


async def get_chat_files_controller(chat_id: str, current_user):
	user_id = _user_id_from_current_user(current_user)
	files = await get_chat_files(chat_id, user_id)
	return {"success": True, "files": files}


async def update_chat_title_controller(chat_id: str, payload: ChatTitleUpdate, current_user):
	user_id = _user_id_from_current_user(current_user)
	chat = await update_chat_title(chat_id, user_id, payload.title)
	return {"success": True, "message": "Chat title updated", "chat": chat}


async def delete_chat_controller(chat_id: str, current_user):
	user_id = _user_id_from_current_user(current_user)
	result = await delete_chat(chat_id, user_id)
	return {"success": True, "message": result["message"]}


async def clear_chat_messages_controller(chat_id: str, current_user):
	user_id = _user_id_from_current_user(current_user)
	result = await clear_chat_messages(chat_id, user_id)
	return {"success": True, "message": result["message"]}

