
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Optional


load_dotenv()


class Settings:
	PORT: int = int(os.getenv("PORT", "8000"))
	MONGO_URI: Optional[str] = os.getenv("MONGO_URI")
	MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "intellex")
	JWT_SECRET: str = os.getenv("JWT_SECRET", "")
	JWT_EXPIRE: str = os.getenv("JWT_EXPIRE", "7d")
	CLIENT_URL: Optional[str] = os.getenv("CLIENT_URL", "http://localhost:5173")

	CHROMA_PATH: Path = Path(os.getenv("CHROMA_PATH", "chroma-data"))
	CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "intellex_documents")
	CHROMA_TOP_K: int = int(os.getenv("CHROMA_TOP_K", "4"))


settings = Settings()


__all__ = ["settings", "Settings"]
