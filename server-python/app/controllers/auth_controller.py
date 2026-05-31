
from __future__ import annotations

from fastapi import HTTPException, Response, status

from app.core.config import settings
from app.schemas.auth_schema import LoginRequest, RegisterRequest
from app.services.auth.auth_service import login_user, register_user


COOKIE_MAX_AGE = 7 * 24 * 60 * 60


def _cookie_kwargs() -> dict[str, object]:
	return {
		"httponly": True,
		"secure": str(getattr(settings, "NODE_ENV", "development")).lower() == "production",
		"samesite": "strict",
		"max_age": COOKIE_MAX_AGE,
		"path": "/",
	}


def _set_auth_cookies(response: Response, token: str) -> None:
	response.set_cookie("token", token, **_cookie_kwargs())
	response.set_cookie(
		"logged_in",
		"true",
		httponly=False,
		secure=_cookie_kwargs()["secure"],
		samesite="strict",
		max_age=COOKIE_MAX_AGE,
		path="/",
	)


def _clear_auth_cookies(response: Response) -> None:
	response.delete_cookie("token", path="/")
	response.delete_cookie("logged_in", path="/")


async def register(payload: RegisterRequest, response: Response):
	try:
		user = await register_user(payload)
		token = user.pop("token", None)
		if token:
			_set_auth_cookies(response, token)

		return {
			"success": True,
			"message": "User registered successfully",
			"user": user,
		}
	except ValueError as exc:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


async def login(payload: LoginRequest, response: Response):
	try:
		user = await login_user(payload)
		token = user.pop("token", None)
		if token:
			_set_auth_cookies(response, token)

		return {
			"success": True,
			"message": "Logged in successfully",
			"user": user,
		}
	except ValueError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


async def logout(response: Response):
	_clear_auth_cookies(response)
	return {"success": True, "message": "Logged out successfully"}


async def get_profile(current_user):
	if not current_user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

	return {"success": True, "user": current_user}

