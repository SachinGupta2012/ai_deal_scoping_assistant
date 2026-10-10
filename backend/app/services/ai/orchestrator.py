"""Orchestrator: mock by default, live AI when explicitly configured."""
from app.core.config import settings
from app.services.mock_provider import mock_scope
from app.schemas.scope import ScopeModel
from app.services.ai.cache import input_hash
from app.services.ai.live_json import generate_json, live_chain


def _chain() -> list[str]:
    return live_chain()


SYSTEM = """You are a solution-scope analyst. Extract structured requirements from customer text.
Return ONLY valid JSON matching this shape:
{"requirements":[{"req_id":"FR_01","type":"FR","description":"...","priority":"High","chunk_id":"0","quote":"verbatim<=200chars","origin":"customer-stated|AI-inferred|assumed","dependencies":[],"questions":[]}],
 "assumptions":[{"asm_id":"ASM_01","text":"...","related_req_ids":[],"needs_review":true}],
 "questions":[{"q_id":"Q_01","text":"...","related_req_ids":[],"blocking":false}],
 "objectives":[]}
Rules: every requirement needs chunk_id+quote+origin. Missing info -> assumption/question, never invent. IDs sequential by type."""


def run_analysis(session_id: str, normalized_md: str, chunks: list):
    if settings.USE_MOCK_AI or settings.AI_PROVIDER == "mock":
        result = mock_scope(session_id, normalized_md, chunks)
        payload_hash = input_hash(normalized_md)
        return result, {"provider": "mock", "model": result.model, "input_hash": payload_hash, "cache_hit": False}
    chunk_map = "\n".join(f"[{c['idx']}] {c['text'][:400]}" for c in chunks[:20])
    user = f"Return JSON. CHUNKS:\n{chunk_map}\n\nFULL:\n{normalized_md[:12000]}"
    payload_hash = input_hash(normalized_md)
    data, meta = generate_json("extract_v1", payload_hash, SYSTEM, user, temperature=0.1)
    result = ScopeModel(session_id=session_id, provider=meta["provider"], model=meta["model"], prompt_version="extract_v1", **data)
    return result, {**meta, "input_hash": payload_hash}
