"""Simple in-memory cache with TTL for conversations.

This cache stores arbitrary Python objects (e.g. ORM instances) in a
process-local dictionary together with an expiry timestamp. TTL defaults to
300 seconds but can be overridden by the `CACHE_TTL` environment variable
(value in seconds).

API:
- `get_conversation(conversation_id)` -> object | None
- `set_conversation(conversation_id, obj)` -> None
- `invalidate_conversation(conversation_id)` -> None
"""
from typing import Any, Optional, Dict, Tuple
import time
import threading
import os

_LOCK = threading.Lock()
# store mapping: id -> (value, expiry_timestamp)
_CONVERSATION_CACHE: Dict[int, Tuple[Any, float]] = {}


def _default_ttl() -> int:
    try:
        return int(os.getenv("CACHE_TTL", "300"))
    except Exception:
        return 300


def get_conversation(conversation_id: int) -> Optional[Any]:
    """Return cached object or None if missing/expired."""
    now = time.time()
    with _LOCK:
        entry = _CONVERSATION_CACHE.get(conversation_id)
        if not entry:
            return None
        value, expiry = entry
        if expiry is not None and now >= expiry:
            # expired
            _CONVERSATION_CACHE.pop(conversation_id, None)
            return None
        return value


def set_conversation(conversation_id: int, obj: Any) -> None:
    """Store object with TTL (default 300s)."""
    ttl = _default_ttl()
    expiry = time.time() + ttl if ttl > 0 else None
    with _LOCK:
        _CONVERSATION_CACHE[conversation_id] = (obj, expiry)


def invalidate_conversation(conversation_id: int) -> None:
    with _LOCK:
        _CONVERSATION_CACHE.pop(conversation_id, None)
