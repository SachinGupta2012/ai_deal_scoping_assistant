"""Data/AI generator — mock or live provider chain."""
import json
from app.core.config import settings
from app.schemas.data_ai import DataAIStrategyModel
from app.services.ai.cache import input_hash
from app.services.ai.live_json import generate_json
from app.services.mock_provider import mock_data_ai

SYSTEM = """You are a data + integration + AI strategist. Input: approved scope JSON.
Return ONLY valid JSON:
 {"data_domains":[{"domain_id":"DD_01","name":"...","sources":[],"ownership":"...","ingestion":"...","storage":"...","storage_transactional":"...","storage_analytical":"...","quality_rules":[],"metadata":"...","governance":"...","retention":"...","privacy":"...","reporting":"...","backup_recovery":"...","related_req_ids":["DATA_01"]}],
 "integrations":[{"int_id":"ITI_01","name":"...","source_system":"...","target_system":"...","pattern":"api-sync|event|batch|file","auth":"...","error_handling":"...","retry":"...","monitoring":"...","sync_notes":"...","related_req_ids":["INT_01"]}],
 "ai_use_cases":[{"uc_id":"AI_01","name":"...","problem":"...","ai_function":"...","deterministic_part":"...","human_review":"...","framework":"...","framework_rationale":"...>=10chars","model_options":[],"orchestration":"...","prompt_management":"...","retrieval_needs":"...","evaluation":"...","safety":"...","privacy":"...","monitoring":"...","related_req_ids":["FR_01"]}],
 "data_flow_mermaid":"graph TD\\n  DD_01[Orders]-->ITI_01[Sync]-->AI_01[Recommend]"}
Rules: copy req IDs exactly; never leave related_req_ids empty; framework_rationale must say WHY."""


def generate_data_ai(session_id: str, scope: dict, scope_version_no: int) -> DataAIStrategyModel:
    if settings.USE_MOCK_AI or settings.AI_PROVIDER == "mock":
        return mock_data_ai(session_id, scope, scope_version_no)
    scope_json = json.dumps(scope)
    user = f"Return JSON data/integration/AI strategy for:\n{scope_json[:15000]}"
    data, meta = generate_json("data_ai_v1", input_hash(scope_json), SYSTEM, user, temperature=0.2)
    return DataAIStrategyModel(session_id=session_id, provider=meta["provider"], model=meta["model"], scope_version_no=scope_version_no, **data)
