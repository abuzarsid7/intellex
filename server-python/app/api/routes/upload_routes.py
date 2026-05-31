
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.controllers.upload_controller import upload_pdf
from app.middleware.auth_middleware import get_current_user


router = APIRouter()


@router.post("/")
async def upload_file(
	file: UploadFile = File(...),
	chat_id: str | None = Form(default=None),
	chatId: str | None = Form(default=None),
	current_user=Depends(get_current_user),
):
	if not file:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded")

	effective_chat_id = chat_id or chatId
	return await upload_pdf(file, chat_id=effective_chat_id, current_user=current_user)

