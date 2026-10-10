"""Small file-backed cache for AI JSON responses."""
import hashlib
import json
import os
from typing import Any

from app.core.config import settings


def input_hash(*parts: str) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update((part or "").encode("utf-8"))
    return h.hexdigest()[:16]


def cache_key(prompt_version: str, payload_hash: str, provider: str, model: str) -> str:
    raw = f"{prompt_version}|{payload_hash}|{provider}|{model}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _path(key: str) -> str:
    return os.path.join(settings.AI_CACHE_DIR, f"{key}.json")


def get_cached(prompt_version: str, payload_hash: str, provider: str, model: str) -> dict[str, Any] | None:
    if not settings.AI_CACHE_ENABLED:
        return None
    path = _path(cache_key(prompt_version, payload_hash, provider, model))
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def set_cached(prompt_version: str, payload_hash: str, provider: str, model: str, payload: dict[str, Any]) -> None:
    if not settings.AI_CACHE_ENABLED:
        return
    os.makedirs(settings.AI_CACHE_DIR, exist_ok=True)
    path = _path(cache_key(prompt_version, payload_hash, provider, model))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
