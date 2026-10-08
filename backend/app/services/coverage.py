"""Deterministic coverage — no LLM. Reqs x (capabilities + integrations + AI use cases)."""
from app.schemas.prd import CoverageModel


def _ids(item) -> list:
    if isinstance(item, dict):
        return item.get("included_req_ids") or item.get("related_req_ids") or []
    return getattr(item, "included_req_ids", None) or getattr(item, "related_req_ids", []) or []


def _cid(item, fallback: str) -> str:
    if isinstance(item, dict):
        return item.get("capability_id") or item.get("int_id") or item.get("uc_id") or "?"
    return getattr(item, "capability_id", None) or getattr(item, "int_id", None) or getattr(item, "uc_id", None) or fallback


def compute_coverage(session_id: str, requirement_ids: list, capabilities: list,
                     integrations: list | None = None, ai_use_cases: list | None = None) -> CoverageModel:
    req_set = set(requirement_ids)
    covered: set = set()
    unsupported_caps: list = []
    unsupported_int: list = []
    unsupported_ai: list = []
    for cap in capabilities:
        valid = [i for i in _ids(cap) if i in req_set]
        if not valid:
            unsupported_caps.append(_cid(cap, "?"))
        covered.update(valid)
    for it in integrations or []:
        valid = [i for i in _ids(it) if i in req_set]
        if not valid:
            unsupported_int.append(_cid(it, "?"))
        covered.update(valid)
    for uc in ai_use_cases or []:
        valid = [i for i in _ids(uc) if i in req_set]
        if not valid:
            unsupported_ai.append(_cid(uc, "?"))
        covered.update(valid)
    uncovered = sorted(req_set - covered)
    total = len(req_set)
    pct = round(len(covered) / total * 100, 1) if total else 0.0
    return CoverageModel(
        session_id=session_id,
        total_requirements=total,
        covered_req_ids=sorted(covered),
        uncovered_req_ids=uncovered,
        unsupported_capabilities=unsupported_caps,
        unsupported_integrations=unsupported_int,
        unsupported_ai_use_cases=unsupported_ai,
        coverage_pct=pct,
    )
