"""PRD generator — mock or live provider chain."""
import json
from app.core.config import settings
from app.schemas.prd import PRDModel
from app.services.ai.cache import input_hash
from app.services.ai.live_json import generate_json
from app.services.mock_provider import mock_prd

SYSTEM = """You are a product-requirements author. Input is an approved scope model (JSON).
Return ONLY valid JSON matching:
{"overview":"...","business_problem":"...","objectives":[],"personas":[],"journeys":[],
 "capabilities":[{"capability_id":"CAP_01","name":"...","description":"...>=20chars","included_req_ids":["FR_01"],"priority":"High","dependencies":[],"scope_kind":"customer-requested"}],
 "nfr_summary":[],"integrations":[],"dependencies":[],"assumptions":[],"risks":[],"out_of_scope":[],"open_questions":[]}
Rules: capabilities cover requirements; copy req IDs exactly; label scope_kind honestly."""


def generate_prd(session_id: str, scope_payload: dict, scope_version_no: int) -> PRDModel:
    if settings.USE_MOCK_AI or settings.AI_PROVIDER == "mock":
        return mock_prd(session_id, scope_payload, scope_version_no)
    scope_json = json.dumps(scope_payload)
    user = f"Return JSON PRD for APPROVED_SCOPE:\n{scope_json[:15000]}"
    data, meta = generate_json("prd_v1", input_hash(scope_json), SYSTEM, user, temperature=0.2)
    return PRDModel(session_id=session_id, provider=meta["provider"], model=meta["model"], scope_version_no=scope_version_no, **data)
