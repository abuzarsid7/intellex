
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from bson import ObjectId
from jose import jwt

from app.core.config import settings
from app.core.database import get_database
from app.schemas.auth_schema import LoginRequest, ProfileOut, RegisterRequest, TokenResponse


USERS_COLLECTION = "users"
JWT_ALGORITHM = "HS256"
MONGO_DB_NAME = settings.MONGO_DB_NAME


def _users_collection():
	return get_database(MONGO_DB_NAME)[USERS_COLLECTION]


def _serialize_user(user: Dict[str, Any]) -> Dict[str, Any]:
	created_at = user.get("created_at") or user.get("createdAt") or user.get("created_at")
	updated_at = user.get("updated_at") or user.get("updatedAt") or user.get("updated_at")

	return {
		"_id": str(user["_id"]),
		"name": user.get("name"),
		"email": user.get("email"),
		"created_at": created_at,
		"updated_at": updated_at,
	}


def hash_password(password: str) -> str:
	salt = bcrypt.gensalt(rounds=10)
	return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_token(user_id: str) -> str:
	expires_in = settings.JWT_EXPIRE or "7d"
	if expires_in.endswith("d"):
		expiration = datetime.now(timezone.utc) + timedelta(days=int(expires_in[:-1] or 7))
	elif expires_in.endswith("h"):
		expiration = datetime.now(timezone.utc) + timedelta(hours=int(expires_in[:-1] or 0))
	elif expires_in.endswith("m"):
		expiration = datetime.now(timezone.utc) + timedelta(minutes=int(expires_in[:-1] or 0))
	else:
		expiration = datetime.now(timezone.utc) + timedelta(days=7)

	payload = {"id": user_id, "exp": expiration}
	return jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)


async def register_user(request: RegisterRequest) -> Dict[str, Any]:
	if not request.name or not request.email or not request.password:
		raise ValueError("Please provide name, email, and password")

	users = _users_collection()
	existing_user = await users.find_one({"email": request.email.lower()})
	if existing_user:
		raise ValueError("User already exists with this email")

	now = datetime.now(timezone.utc)
	user_document = {
		"name": request.name.strip(),
		"email": request.email.lower(),
		"password": hash_password(request.password),
		"created_at": now,
		"updated_at": now,
	}

	result = await users.insert_one(user_document)
	created_user = await users.find_one({"_id": result.inserted_id})
	if not created_user:
		raise ValueError("Failed to create user")

	serialized_user = _serialize_user(created_user)
	serialized_user["token"] = generate_token(serialized_user["_id"])
	return serialized_user


async def login_user(request: LoginRequest) -> Dict[str, Any]:
	if not request.email or not request.password:
		raise ValueError("Please provide email and password")

	users = _users_collection()
	user = await users.find_one({"email": request.email.lower()})
	if not user or not user.get("password"):
		raise ValueError("Invalid credentials")

	if not verify_password(request.password, user["password"]):
		raise ValueError("Invalid credentials")

	serialized_user = _serialize_user(user)
	serialized_user["token"] = generate_token(serialized_user["_id"])
	return serialized_user


async def get_user_profile(user_id: str) -> ProfileOut:
	users = _users_collection()
	try:
		object_id = ObjectId(user_id)
	except Exception as exc:
		raise ValueError("Invalid user id") from exc

	user = await users.find_one({"_id": object_id})
	if not user:
		raise ValueError("User not found")

	return ProfileOut(**_serialize_user(user))


def build_token_response(user_id: str) -> TokenResponse:
	return TokenResponse(
		access_token=generate_token(user_id),
		token_type="bearer",
		expires_in=settings.JWT_EXPIRE,
	)


__all__ = [
	"hash_password",
	"verify_password",
	"generate_token",
	"register_user",
	"login_user",
	"get_user_profile",
	"build_token_response",
]
