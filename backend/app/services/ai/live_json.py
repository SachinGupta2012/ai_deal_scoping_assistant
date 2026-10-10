"""Provider-chain JSON generation with cache and fallback."""
import json
from dataclasses import dataclass
from typing import Any

import httpx
from google import genai

from app.core.config import settings
from app.services.ai.cache import get_cached, set_cached


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    model: str
    api_key: str
    base_url: str = ""
    kind: str = "openai"


def live_chain() -> list[str]:
    if settings.USE_MOCK_AI or settings.AI_PROVIDER == "mock":
        return ["mock"]
    if settings.AI_PROVIDER and settings.AI_PROVIDER not in ("live_chain", "auto"):
        first = settings.AI_PROVIDER
        rest = [p.strip() for p in settings.AI_PROVIDER_CHAIN.split(",") if p.strip()]
        return list(dict.fromkeys([first] + rest))
    return [p.strip() for p in settings.AI_PROVIDER_CHAIN.split(",") if p.strip()]


def _config(name: str) -> ProviderConfig | None:
    if name == "cloudflare":
        if not settings.CLOUDFLARE_ACCOUNT_ID:
            return None
        return ProviderConfig(
            name="cloudflare",
            model=settings.CLOUDFLARE_MODEL,
            api_key=settings.CLOUDFLARE_API_TOKEN,
            base_url=f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/ai/v1",
        )
    if name == "openrouter":
        return ProviderConfig(
            name="openrouter",
            model=settings.OPENROUTER_MODEL,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
    if name == "groq":
        return ProviderConfig(
            name="groq",
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
    if name in ("google", "gemini"):
        return ProviderConfig(name="google", model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY or settings.AI_API_KEY, kind="google")
    if name == "openai_compatible":
        return ProviderConfig(name="openai_compatible", model=settings.AI_MODEL, api_key=settings.AI_API_KEY, base_url=settings.AI_BASE_URL)
    return None


def _call_openai(cfg: ProviderConfig, system: str, user: str, temperature: float) -> dict[str, Any]:
    if not cfg.api_key:
        raise RuntimeError(f"{cfg.name} API key is not configured")
    if not cfg.model:
        raise RuntimeError(f"{cfg.name} model is not configured")
    body = {
        "model": cfg.model,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system + " Output must be JSON."},
            {"role": "user", "content": user},
        ],
    }
    r = httpx.post(
        f"{cfg.base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {cfg.api_key}"},
        json=body,
        timeout=settings.AI_TIMEOUT,
    )
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def _call_google(cfg: ProviderConfig, system: str, user: str, temperature: float) -> dict[str, Any]:
    if not cfg.api_key:
        raise RuntimeError("google API key is not configured")
    client = genai.Client(api_key=cfg.api_key)
    resp = client.models.generate_content(
        model=cfg.model,
        contents=f"{system}\n\n{user}",
        config={"response_mime_type": "application/json", "temperature": temperature},
    )
    return json.loads(resp.text)


def generate_json(prompt_version: str, payload_hash: str, system: str, user: str, temperature: float = 0.2) -> tuple[dict[str, Any], dict[str, Any]]:
    attempts: list[dict[str, str]] = []
    for name in live_chain():
        cfg = _config(name)
        if not cfg:
            attempts.append({"provider": name, "error": "not configured"})
            continue
        cached = get_cached(prompt_version, payload_hash, cfg.name, cfg.model)
        if cached is not None:
            return cached, {"provider": cfg.name, "model": cfg.model, "cache_hit": True, "attempts": attempts}
        try:
            data = _call_google(cfg, system, user, temperature) if cfg.kind == "google" else _call_openai(cfg, system, user, temperature)
            set_cached(prompt_version, payload_hash, cfg.name, cfg.model, data)
            return data, {"provider": cfg.name, "model": cfg.model, "cache_hit": False, "attempts": attempts}
        except Exception as e:
            attempts.append({"provider": cfg.name, "model": cfg.model, "error": str(e)[:300]})
    raise RuntimeError(f"Live AI failed for all configured providers: {attempts}")
