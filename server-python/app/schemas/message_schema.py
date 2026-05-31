from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    chatId: str = Field(..., description="Chat id as string", alias="chatId")
    role: Literal["user", "assistant"]
    content: str


class MessageCreate(MessageBase):
    pass


class MessageOut(MessageBase):
    id: str = Field(..., alias="_id")
    createdAt: datetime

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
