
from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from app.controllers.auth_controller import get_profile, login, logout, register
from app.middleware.auth_middleware import get_current_user
from app.schemas.auth_schema import LoginRequest, RegisterRequest


router = APIRouter()


@router.post("/signup")
async def signup(payload: RegisterRequest, response: Response):
	return await register(payload, response)


@router.post("/login")
async def signin(payload: LoginRequest, response: Response):
	return await login(payload, response)


@router.post("/logout")
async def signout(response: Response):
	return await logout(response)


@router.get("/profile")
async def profile(current_user=Depends(get_current_user)):
	return await get_profile(current_user)
