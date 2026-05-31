
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.controllers.chat_controller import (
	clear_chat_messages_controller,
	create_chat_controller,
	delete_chat_controller,
	get_chat_controller,
	get_chat_files_controller,
	get_chat_messages_controller,
	get_chats_controller,
	send_message_controller,
	update_chat_title_controller,
)
from app.middleware.auth_middleware import get_current_user
from app.schemas.chat_schema import ChatCreate, ChatMessageRequest, ChatTitleUpdate


router = APIRouter(prefix="/api/chat")


@router.post("/")
async def create_chat(payload: ChatCreate, current_user=Depends(get_current_user)):
	return await create_chat_controller(payload, current_user)


@router.get("/")
async def get_chats(
	current_user=Depends(get_current_user),
	page: int = Query(default=1, ge=1),
	limit: int = Query(default=50, ge=1, le=100),
):
	return await get_chats_controller(current_user, page=page, limit=limit)


@router.post("/message")
async def send_message(payload: ChatMessageRequest, current_user=Depends(get_current_user)):
	return await send_message_controller(payload, current_user)


@router.get("/{chat_id}")
async def get_chat(chat_id: str, current_user=Depends(get_current_user)):
	return await get_chat_controller(chat_id, current_user)


@router.get("/{chat_id}/messages")
async def get_chat_messages(
	chat_id: str,
	current_user=Depends(get_current_user),
	page: int = Query(default=1, ge=1),
	limit: int = Query(default=100, ge=1, le=200),
):
	return await get_chat_messages_controller(chat_id, current_user, page=page, limit=limit)


@router.get("/{chat_id}/files")
async def get_chat_files(chat_id: str, current_user=Depends(get_current_user)):
	return await get_chat_files_controller(chat_id, current_user)


@router.put("/{chat_id}/title")
async def update_chat_title(chat_id: str, payload: ChatTitleUpdate, current_user=Depends(get_current_user)):
	return await update_chat_title_controller(chat_id, payload, current_user)


@router.delete("/{chat_id}")
async def delete_chat(chat_id: str, current_user=Depends(get_current_user)):
	return await delete_chat_controller(chat_id, current_user)


@router.delete("/{chat_id}/messages")
async def clear_chat_messages(chat_id: str, current_user=Depends(get_current_user)):
	return await clear_chat_messages_controller(chat_id, current_user)

