"""Architecture generator — mock or live provider chain, constrained to catalog services."""
import json
from app.core.config import settings
from app.schemas.architecture import ArchitectureModel
from app.services.ai.cache import input_hash
from app.services.ai.live_json import generate_json
from app.services.cloud_catalog import catalog_for
from app.services.mock_provider import mock_architecture

SYSTEM = """You are a cloud solution architect. Input: approved scope + platform + allowed service catalog.
Return ONLY valid JSON:
{"platform_rationale":"...>=20chars","components":[{"component_id":"COMP_01","name":"...","layer":"frontend|backend|api|database|storage|iam|messaging|integration|ai_ml|observability|security|deployment|environments|availability|backup_dr","cloud_service":"<from catalog>","supported_req_ids":["FR_01"],"purpose":"...","rationale":"...","tradeoffs":"...","dependencies":[],"security":"..."}],
 "mermaid":"graph TD\\n  COMP_01[Web App]-->COMP_02[API]"}
Rules: cloud_service MUST come from catalog; every component >=1 req ID copied exactly; cover frontend,backend,api,database,iam,observability,security,deployment minimum."""


def _payload(scope: dict, platform: str) -> str:
    reqs = scope.get("requirements", [])
    req_line = ", ".join(f"{r['req_id']}({r['type']}): {r['description'][:120]}" for r in reqs)
    return f"REQUIREMENTS: {req_line}\nCATALOG({platform}): {json.dumps(catalog_for(platform))}"


def generate_architecture(session_id: str, scope: dict, platform: str, scope_version_no: int) -> ArchitectureModel:
    if settings.USE_MOCK_AI or settings.AI_PROVIDER == "mock":
        return mock_architecture(session_id, scope, platform, scope_version_no)
    user = f"Return JSON architecture.\n{_payload(scope, platform)[:15000]}"
    data, meta = generate_json("arch_v1", input_hash(platform, json.dumps(scope)), SYSTEM, user, temperature=0.2)
    return ArchitectureModel(session_id=session_id, platform=platform, scope_version_no=scope_version_no, provider=meta["provider"], model=meta["model"], **data)
