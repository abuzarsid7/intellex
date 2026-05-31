"""Async MongoDB connection helpers using Motor.

This module provides an async connection lifecycle compatible with FastAPI
startup/shutdown events. It intentionally does not import or register
models/collections — that belongs in the service/controller layer.
"""

import logging
import sys
from typing import Optional

import certifi
from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings


logger = logging.getLogger("intellex.database")


_client: Optional[AsyncIOMotorClient] = None


async def connect_to_mongo() -> None:
	"""Create an AsyncIOMotorClient and verify connectivity.

	Exits the process on fatal connection failure to mimic the Node behavior.
	"""
	global _client
	if _client is not None:
		return

	if not settings.MONGO_URI:
		logger.error("MONGO_URI not set in environment")
		sys.exit(1)

	try:
		_client = AsyncIOMotorClient(settings.MONGO_URI, tlsCAFile=certifi.where())
		# Verify the server is reachable
		await _client.admin.command("ping")
		logger.info("MongoDB Connected")
	except Exception:
		logger.exception("Failed to connect to MongoDB")
		sys.exit(1)


async def close_mongo_connection() -> None:
	"""Close the Motor client if it exists."""
	global _client
	if _client is None:
		return

	try:
		_client.close()
		logger.info("MongoDB connection closed")
	except Exception:
		logger.exception("Error closing MongoDB connection")
	finally:
		_client = None


def get_client() -> AsyncIOMotorClient:
	"""Return the active Motor client or raise if not connected."""
	if _client is None:
		raise RuntimeError("MongoDB client is not connected. Call connect_to_mongo() first.")
	return _client


def get_database(name: Optional[str] = None):
	"""Return a Motor database instance.

	If `name` is provided it is used; otherwise the default database from the
	connection string is returned. If no default is available, this will raise
	so callers must explicitly pass a database name.
	"""
	client = get_client()
	if name:
		return client[name]

	default_db = client.get_default_database()
	if default_db is not None:
		return default_db

	raise RuntimeError(
		"No default database found in MONGO_URI; please provide a database name to get_database()."
	)


__all__ = [
	"connect_to_mongo",
	"close_mongo_connection",
	"get_client",
	"get_database",
]

