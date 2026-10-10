"""PRD generator — live AI only. Reads approved ScopeVersion, writes versioned PRD."""
import json
import httpx
from google import genai
from app.core.config import settings
from app.schemas.prd import PRDModel
from app.services.mock_provider import mock_prd

SYSTEM = """You are a product-requirements author. Input is an approved scope model (JSON).
Return ONLY valid JSON matching:
{"overview":"...","business_problem":"...","objectives":[],"personas":[],"journeys":[],
 "capabilities":[{"capability_id":"CAP_01","name":"...","description":"...>=20chars","included_req_ids":["FR_01"],"priority":"High","dependencies":[],"scope_kind":"customer-requested"}],
 "nfr_summary":[],"integrations":[],"dependencies":[],"assumptions":[],"risks":[],"out_of_scope":[],"open_questions":[]}
Rules: capabilities cover requirements; copy req IDs exactly; label scope_kind honestly."""


def _google(scope_json: str, model: str) -> dict:
    client = genai.Client(api_key=settings.AI_API_KEY or settings.GEMINI_API_KEY)
    resp = client.models.generate_content(
        model=model,
        contents=f"{SYSTEM}\n\nAPPROVED_SCOPE:\n{scope_json[:15000]}",
        config={"response_mime_type": "application/json", "temperature": 0.2},
    )
    return json.loads(resp.text)


def _openai_compatible(scope_json: str, model: str) -> dict:
    base = settings.AI_BASE_URL if settings.AI_PROVIDER == "openai_compatible" else "https://api.groq.com/openai/v1"
    key = settings.AI_API_KEY or settings.GROQ_API_KEY
    body = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM + " Output must be JSON."},
            {"role": "user", "content": f"Return JSON PRD for APPROVED_SCOPE:\n{scope_json[:15000]}"},
        ],
    }
    r = httpx.post(f"{base.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {key}"}, json=body, timeout=settings.AI_TIMEOUT)
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def generate_prd(session_id: str, scope_payload: dict, scope_version_no: int) -> PRDModel:
    if settings.USE_MOCK_AI or settings.AI_PROVIDER == "mock":
        return mock_prd(session_id, scope_payload, scope_version_no)
    scope_json = json.dumps(scope_payload)
    if settings.AI_PROVIDER == "openai_compatible":
        model = settings.AI_MODEL
        data = _openai_compatible(scope_json, model)
        provider = "openai_compatible"
    elif settings.AI_PROVIDER in ("groq",):
        model = settings.GROQ_MODEL
        data = _openai_compatible(scope_json, model)
        provider = "openai_compatible"
    else:
        model = settings.AI_MODEL if settings.AI_PROVIDER == "google" else settings.GEMINI_MODEL
        data = _google(scope_json, model)
        provider = "google"
    return PRDModel(session_id=session_id, provider=provider, model=model, scope_version_no=scope_version_no, **data)
