from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr


class UserBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=6)


class UserOut(UserBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class UserInDB(UserOut):
    hashed_password: str
