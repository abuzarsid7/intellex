
from __future__ import annotations

from fastapi import HTTPException, status

from app.schemas.auth_schema import LoginRequest, RegisterRequest
from app.services.auth.auth_service import login_user, register_user


async def register(payload: RegisterRequest):
	try:
		user = await register_user(payload)
		token = user.pop("token", None)

		return {
			"success": True,
			"message": "User registered successfully",
			"access_token": token,
			"token_type": "bearer",
			"user": user,
		}
	except ValueError as exc:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


async def login(payload: LoginRequest):
	try:
		user = await login_user(payload)
		token = user.pop("token", None)

		return {
			"success": True,
			"message": "Logged in successfully",
			"access_token": token,
			"token_type": "bearer",
			"user": user,
		}
	except ValueError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


async def logout():
	return {"success": True, "message": "Logged out successfully"}


async def get_profile(current_user):
	if not current_user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

	return {"success": True, "user": current_user}

