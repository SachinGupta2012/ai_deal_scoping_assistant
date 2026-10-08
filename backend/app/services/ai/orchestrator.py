"""Orchestrator: live AI only. Primary -> legacy fallback. Fails loudly, no silent mock."""
import hashlib
from app.core.config import settings
from app.services.ai.google_genai import GoogleGenAIProvider
from app.services.ai.openai_compatible import OpenAICompatibleProvider


def _chain() -> list[str]:
    primary = settings.AI_PROVIDER
    fallback = "openai_compatible" if primary == "google" else "google"
    return [primary, fallback]


def run_analysis(session_id: str, normalized_md: str, chunks: list):
    providers = {"google": GoogleGenAIProvider(), "openai_compatible": OpenAICompatibleProvider()}
    # legacy aliases from earlier .env values
    if settings.AI_PROVIDER in ("gemini",):
        providers["gemini"] = providers["google"]
    if settings.AI_PROVIDER in ("groq",):
        providers["groq"] = providers["openai_compatible"]
    order = _chain()
    if settings.AI_PROVIDER in ("gemini", "groq"):
        order = [settings.AI_PROVIDER] + [o for o in order if o != settings.AI_PROVIDER]
    input_hash = hashlib.sha256(normalized_md.encode()).hexdigest()[:12]
    last_err = None
    for name in dict.fromkeys(order):
        key = name if name in providers else ("google" if name == "gemini" else "openai_compatible")
        try:
            result = providers[key].analyze(session_id, normalized_md, chunks)
            result.prompt_version = "extract_v1"
            return result, {"provider": result.provider, "model": result.model, "input_hash": input_hash}
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Live AI failed (no mock fallback): {last_err}")
