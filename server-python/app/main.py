from contextlib import asynccontextmanager
from importlib import import_module
import logging
import os
import time

import uvicorn
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.core.database import close_mongo_connection, connect_to_mongo
from app.services.chat.chat_service import ensure_chat_storage_indexes
from app.services.files.file_service import ensure_file_storage_indexes


load_dotenv()


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("intellex.backend")


def _build_allowed_origins() -> list[str]:
    origins = [
        os.getenv("CLIENT_URL"),
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    return [origin for origin in origins if origin]


def _load_router(module_path: str, prefix: str) -> APIRouter:
    module = import_module(module_path)
    router = getattr(module, "router", None)
    if router is not None:
        return router

    logger.info("Router not yet defined in %s; registering an empty router for now", module_path)
    return APIRouter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Intellex FastAPI backend")
    await connect_to_mongo()
    await ensure_chat_storage_indexes()
    await ensure_file_storage_indexes()
    yield
    await close_mongo_connection()
    logger.info("Shutting down Intellex FastAPI backend")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info("%s %s -> %s in %.2fms", request.method, request.url.path, response.status_code, elapsed_ms)
    return response


def _register_router(module_path: str, prefix: str) -> None:
    router = _load_router(module_path, prefix)
    if getattr(router, "prefix", ""):
        app.include_router(router)
        return

    app.include_router(router, prefix=prefix)


_register_router("app.api.routes.auth_routes", "/api/auth")
_register_router("app.api.routes.chat_routes", "/api/chat")
_register_router("app.api.routes.upload_routes", "/api/upload")


@app.get("/")
async def root():
    return {"message": "Intellex FastAPI Backend Running"}


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=os.getenv("ENV", "development") == "development")


if __name__ == "__main__":
    main()