from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatBase(BaseModel):
	title: Optional[str] = Field(default="New Chat", min_length=1)
	description: Optional[str] = None


class ChatCreate(ChatBase):
	pass


class ChatListQuery(BaseModel):
	page: int = Field(default=1, ge=1)
	limit: int = Field(default=50, ge=1, le=100)


class ChatMessageRequest(BaseModel):
	chat_id: str = Field(..., alias="chatId")
	message: str = Field(..., min_length=1)
	use_rag: bool = Field(default=False, alias="useRAG")


class ChatTitleUpdate(BaseModel):
	title: str = Field(..., min_length=1)


class ChatIdRequest(BaseModel):
	chat_id: str = Field(..., alias="chatId")


class ChatAnswerResponse(BaseModel):
	chat_id: str = Field(..., alias="chatId")
	user_message: dict
	assistant_message: dict
	answer: str
	retrieval: dict
	prompt: str


class ChatOut(ChatBase):
	id: str = Field(..., alias="_id")
	userId: str
	createdAt: datetime
	updatedAt: datetime

	class Config:
		allow_population_by_field_name = True
		orm_mode = True
