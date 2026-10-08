"""OpenAI-compatible adapter — Groq, OpenRouter, Together, Ollama, any base_url.
Swap AI by changing .env only: AI_BASE_URL + AI_MODEL + AI_API_KEY. No code change."""
import json
import httpx
from app.core.config import settings
from app.schemas.scope import ScopeModel
from app.services.ai.base import AIProvider

SYSTEM = """You are a solution-scope analyst. Return ONLY valid JSON with this shape:
{"requirements":[{"req_id":"FR_01","type":"FR","description":"...","priority":"High","chunk_id":"0","quote":"verbatim<=200chars","origin":"customer-stated|AI-inferred|assumed","dependencies":[],"questions":[]}],
 "assumptions":[{"asm_id":"ASM_01","text":"...","related_req_ids":[],"needs_review":true}],
 "questions":[{"q_id":"Q_01","text":"...","related_req_ids":[],"blocking":false}],
 "objectives":[]} Rules: output must be JSON."""


def _resolve() -> tuple[str, str, str]:
    if settings.AI_PROVIDER == "openai_compatible":
        return settings.AI_BASE_URL, settings.AI_API_KEY, settings.AI_MODEL
    # legacy groq keys
    return "https://api.groq.com/openai/v1", settings.GROQ_API_KEY, settings.GROQ_MODEL


class OpenAICompatibleProvider(AIProvider):
    name = "openai_compatible"

    def analyze(self, session_id: str, normalized_md: str, chunks: list) -> ScopeModel:
        base_url, api_key, model = _resolve()
        if not api_key:
            raise RuntimeError("AI_API_KEY (or GROQ_API_KEY) is not set")
        chunk_map = "\n".join(f"[{c['idx']}] {c['text'][:400]}" for c in chunks[:20])
        body = {
            "model": model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Return JSON. CHUNKS:\n{chunk_map}\n\nFULL:\n{normalized_md[:12000]}"},
            ],
        }
        r = httpx.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=body,
            timeout=settings.AI_TIMEOUT,
        )
        r.raise_for_status()
        data = json.loads(r.json()["choices"][0]["message"]["content"])
        return ScopeModel(session_id=session_id, provider="openai_compatible", model=model, **data)
