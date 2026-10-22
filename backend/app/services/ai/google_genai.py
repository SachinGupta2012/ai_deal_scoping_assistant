"""Google GenAI adapter — works with any Gemini model via config. No model hardcoded."""
import json
from google import genai
from app.core.config import settings
from app.schemas.scope import ScopeModel
from app.services.ai.base import AIProvider

SYSTEM = """You are a solution-scope analyst. Extract structured requirements from customer text.
Return ONLY valid JSON matching this shape:
{"requirements":[{"req_id":"FR_01","type":"FR","description":"...","priority":"High","chunk_id":"0","quote":"verbatim<=200chars","origin":"customer-stated|AI-inferred|assumed","dependencies":[],"questions":[]}],
 "assumptions":[{"asm_id":"ASM_01","text":"...","related_req_ids":[],"needs_review":true}],
 "questions":[{"q_id":"Q_01","text":"...","related_req_ids":[],"blocking":false}],
 "objectives":[]}
Rules: every requirement needs chunk_id+quote+origin. Missing info -> assumption/question, never invent. IDs sequential by type."""


def _api_key() -> str:
    return settings.AI_API_KEY or settings.GEMINI_API_KEY


def _model() -> str:
    return settings.AI_MODEL if settings.AI_PROVIDER == "google" else settings.GEMINI_MODEL


class GoogleGenAIProvider(AIProvider):
    name = "google"

    def analyze(self, session_id: str, normalized_md: str, chunks: list) -> ScopeModel:
        key = _api_key()
        if not key:
            raise RuntimeError("AI_API_KEY (or GEMINI_API_KEY) is not set")
        client = genai.Client(api_key=key)
        chunk_map = "\n".join(f"[{c['idx']}] {c['text'][:400]}" for c in chunks[:20])
        last_err: Exception | None = None
        for _ in range(settings.AI_MAX_RETRIES + 1):
            try:
                resp = client.models.generate_content(
                    model=_model(),
                    contents=f"{SYSTEM}\n\nCHUNKS:\n{chunk_map}\n\nFULL:\n{normalized_md[:12000]}",
                    config={"response_mime_type": "application/json", "temperature": 0.1},
                )
                data = json.loads(resp.text)
                return ScopeModel(session_id=session_id, provider="google", model=_model(), **data)
            except Exception as e:
                last_err = e
        raise RuntimeError(f"GoogleGenAI failed after retries: {last_err}")
