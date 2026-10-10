"""Data/AI generator — live AI only, config-driven like arch/prd generators."""
import json
import httpx
from google import genai
from app.core.config import settings
from app.schemas.data_ai import DataAIStrategyModel
from app.services.mock_provider import mock_data_ai

SYSTEM = """You are a data + integration + AI strategist. Input: approved scope JSON.
Return ONLY valid JSON:
 {"data_domains":[{"domain_id":"DD_01","name":"...","sources":[],"ownership":"...","ingestion":"...","storage":"...","storage_transactional":"...","storage_analytical":"...","quality_rules":[],"metadata":"...","governance":"...","retention":"...","privacy":"...","reporting":"...","backup_recovery":"...","related_req_ids":["DATA_01"]}],
 "integrations":[{"int_id":"ITI_01","name":"...","source_system":"...","target_system":"...","pattern":"api-sync|event|batch|file","auth":"...","error_handling":"...","retry":"...","monitoring":"...","sync_notes":"...","related_req_ids":["INT_01"]}],
 "ai_use_cases":[{"uc_id":"AI_01","name":"...","problem":"...","ai_function":"...","deterministic_part":"...","human_review":"...","framework":"...","framework_rationale":"...>=10chars","model_options":[],"orchestration":"...","prompt_management":"...","retrieval_needs":"...","evaluation":"...","safety":"...","privacy":"...","monitoring":"...","related_req_ids":["FR_01"]}],
 "data_flow_mermaid":"graph TD\\n  DD_01[Orders]-->ITI_01[Sync]-->AI_01[Recommend]"}
Rules: copy req IDs exactly; never leave related_req_ids empty; framework_rationale must say WHY."""


def _google(scope_json: str, model: str) -> dict:
    client = genai.Client(api_key=settings.AI_API_KEY or settings.GEMINI_API_KEY)
    resp = client.models.generate_content(
        model=model,
        contents=f"{SYSTEM}\n\nAPPROVED_SCOPE:\n{scope_json[:15000]}",
        config={"response_mime_type": "application/json", "temperature": 0.2},
    )
    return json.loads(resp.text)


def _openai_compatible(scope_json: str, model: str, base: str, key: str) -> dict:
    body = {
        "model": model, "temperature": 0.2, "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM + " Output must be JSON."},
            {"role": "user", "content": f"Return JSON data/integration/AI strategy for:\n{scope_json[:15000]}"},
        ],
    }
    r = httpx.post(f"{base.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {key}"}, json=body, timeout=settings.AI_TIMEOUT)
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def generate_data_ai(session_id: str, scope: dict, scope_version_no: int) -> DataAIStrategyModel:
    if settings.USE_MOCK_AI or settings.AI_PROVIDER == "mock":
        return mock_data_ai(session_id, scope, scope_version_no)
    scope_json = json.dumps(scope)
    if settings.AI_PROVIDER == "openai_compatible":
        data = _openai_compatible(scope_json, settings.AI_MODEL, settings.AI_BASE_URL, settings.AI_API_KEY)
        provider, model = "openai_compatible", settings.AI_MODEL
    elif settings.AI_PROVIDER in ("groq",):
        data = _openai_compatible(scope_json, settings.GROQ_MODEL, "https://api.groq.com/openai/v1", settings.GROQ_API_KEY)
        provider, model = "openai_compatible", settings.GROQ_MODEL
    else:
        model = settings.AI_MODEL if settings.AI_PROVIDER == "google" else settings.GEMINI_MODEL
        data = _google(scope_json, model)
        provider = "google"
    return DataAIStrategyModel(session_id=session_id, provider=provider, model=model, scope_version_no=scope_version_no, **data)
