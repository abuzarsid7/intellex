
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
	name: str = Field(..., min_length=1)
	email: EmailStr
	password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
	email: EmailStr
	password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"
	expires_in: Optional[str] = None


class ProfileOut(BaseModel):
	id: str = Field(..., alias="_id")
	name: str
	email: EmailStr
	created_at: datetime
	updated_at: datetime

	class Config:
		allow_population_by_field_name = True
		orm_mode = True

