
from __future__ import annotations

from fastapi import Request
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.services.auth.auth_service import get_user_profile


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
	request: Request,
	credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
	token = None
	if credentials and credentials.scheme.lower() == "bearer":
		token = credentials.credentials
	else:
		token = request.cookies.get("token")

	if not token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

	if not settings.JWT_SECRET:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT secret is not configured")

	try:
		payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
		user_id = payload.get("id")
		if not user_id:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		return await get_user_profile(user_id)
	except JWTError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
