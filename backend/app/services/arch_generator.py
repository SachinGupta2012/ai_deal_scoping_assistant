"""Architecture generator — live AI only, constrained to catalog services."""
import json
import httpx
from google import genai
from app.core.config import settings
from app.schemas.architecture import ArchitectureModel
from app.services.cloud_catalog import catalog_for

SYSTEM = """You are a cloud solution architect. Input: approved scope + platform + allowed service catalog.
Return ONLY valid JSON:
{"platform_rationale":"...>=20chars","components":[{"component_id":"COMP_01","name":"...","layer":"frontend|backend|api|database|storage|iam|messaging|integration|ai_ml|observability|security|deployment|environments|availability|backup_dr","cloud_service":"<from catalog>","supported_req_ids":["FR_01"],"purpose":"...","rationale":"...","tradeoffs":"...","dependencies":[],"security":"..."}],
 "mermaid":"graph TD\\n  COMP_01[Web App]-->COMP_02[API]"}
Rules: cloud_service MUST come from catalog; every component >=1 req ID copied exactly; cover frontend,backend,api,database,iam,observability,security,deployment minimum."""


def _payload(scope: dict, platform: str) -> str:
    reqs = scope.get("requirements", [])
    req_line = ", ".join(f"{r['req_id']}({r['type']}): {r['description'][:120]}" for r in reqs)
    return f"REQUIREMENTS: {req_line}\nCATALOG({platform}): {json.dumps(catalog_for(platform))}"


def _google(scope: dict, platform: str, model: str) -> dict:
    client = genai.Client(api_key=settings.AI_API_KEY or settings.GEMINI_API_KEY)
    resp = client.models.generate_content(
        model=model,
        contents=f"{SYSTEM}\n\n{_payload(scope, platform)[:15000]}",
        config={"response_mime_type": "application/json", "temperature": 0.2},
    )
    return json.loads(resp.text)


def _openai_compatible(scope: dict, platform: str, model: str, base: str, key: str) -> dict:
    body = {
        "model": model, "temperature": 0.2, "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM + " Output must be JSON."},
            {"role": "user", "content": f"Return JSON architecture.\n{_payload(scope, platform)[:15000]}"},
        ],
    }
    r = httpx.post(f"{base.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {key}"}, json=body, timeout=settings.AI_TIMEOUT)
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def generate_architecture(session_id: str, scope: dict, platform: str, scope_version_no: int) -> ArchitectureModel:
    if settings.AI_PROVIDER == "openai_compatible":
        data = _openai_compatible(scope, platform, settings.AI_MODEL, settings.AI_BASE_URL, settings.AI_API_KEY)
        provider, model = "openai_compatible", settings.AI_MODEL
    elif settings.AI_PROVIDER in ("groq",):
        data = _openai_compatible(scope, platform, settings.GROQ_MODEL, "https://api.groq.com/openai/v1", settings.GROQ_API_KEY)
        provider, model = "openai_compatible", settings.GROQ_MODEL
    else:
        model = settings.AI_MODEL if settings.AI_PROVIDER == "google" else settings.GEMINI_MODEL
        data = _google(scope, platform, model)
        provider = "google"
    return ArchitectureModel(session_id=session_id, platform=platform, scope_version_no=scope_version_no, provider=provider, model=model, **data)
