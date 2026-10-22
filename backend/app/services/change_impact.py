"""Deterministic change-impact graph."""
from app.schemas.package import ChangeImpactModel, ChangeImpactRequest


OUTPUTS = ["prd", "architecture", "data_ai", "estimate", "quality_gate", "package"]


def _intersects(ids: list[str], changed: set[str]) -> bool:
    return bool(changed.intersection(ids or []))


def analyze_change_impact(session_id: str, scope: dict, request: ChangeImpactRequest) -> ChangeImpactModel:
    req_ids = [r.get("req_id", "") for r in scope.get("requirements", []) if r.get("req_id")]
    changed = set(request.changed_req_ids)
    reasoning: list[str] = []
    for asm_id in request.changed_assumption_ids:
        for asm in scope.get("assumptions", []):
            if asm.get("asm_id") == asm_id:
                related = [i for i in asm.get("related_req_ids", []) if i in req_ids]
                changed.update(related)
                reasoning.append(f"{asm_id} maps to requirement(s): {', '.join(related) or 'none specified'}")
    caps = (scope.get("prd") or {}).get("capabilities", [])
    comps = (scope.get("architecture") or {}).get("components", [])
    data_ai = scope.get("data_ai") or {}
    domains = data_ai.get("data_domains", [])
    integrations = data_ai.get("integrations", [])
    ai_use_cases = data_ai.get("ai_use_cases", [])
    workstreams = (scope.get("estimate") or {}).get("workstreams", [])
    affected_caps = [c.get("capability_id") for c in caps if _intersects(c.get("included_req_ids", []), changed)]
    affected_comps = [c.get("component_id") for c in comps if _intersects(c.get("supported_req_ids", []), changed)]
    affected_domains = [d.get("domain_id") for d in domains if _intersects(d.get("related_req_ids", []), changed)]
    affected_integrations = [i.get("int_id") for i in integrations if _intersects(i.get("related_req_ids", []), changed)]
    affected_ai = [a.get("uc_id") for a in ai_use_cases if _intersects(a.get("related_req_ids", []), changed)]
    affected_ws = [w.get("workstream_id") for w in workstreams if _intersects(w.get("related_req_ids", []), changed)]
    affected_outputs: set[str] = set()
    if affected_caps:
        affected_outputs.add("prd")
    if affected_comps or any(k in request.config_changes for k in ("cloud", "platform")):
        affected_outputs.add("architecture")
    if affected_domains or affected_integrations or affected_ai:
        affected_outputs.add("data_ai")
    estimate_keys = {"rate_card", "contingency_pct", "productivity_factor", "team_capacity_pw_per_week", "currency"}
    if affected_ws or changed or estimate_keys.intersection(request.config_changes):
        affected_outputs.add("estimate")
    if changed or affected_outputs or request.config_changes:
        affected_outputs.update(["quality_gate", "package"])
    if request.config_changes:
        reasoning.append(f"Config changes affect: {', '.join(sorted(request.config_changes.keys()))}")
    if changed:
        reasoning.append(f"Changed requirements drive downstream graph traversal: {', '.join(sorted(changed))}")
    return ChangeImpactModel(
        session_id=session_id,
        changed_req_ids=sorted(changed.intersection(req_ids)),
        changed_assumption_ids=request.changed_assumption_ids,
        config_changes=request.config_changes,
        affected_req_ids=sorted(changed.intersection(req_ids)),
        unaffected_req_ids=sorted(set(req_ids) - changed),
        affected_capability_ids=sorted(i for i in affected_caps if i),
        affected_component_ids=sorted(i for i in affected_comps if i),
        affected_data_domain_ids=sorted(i for i in affected_domains if i),
        affected_integration_ids=sorted(i for i in affected_integrations if i),
        affected_ai_use_case_ids=sorted(i for i in affected_ai if i),
        affected_workstream_ids=sorted(i for i in affected_ws if i),
        affected_outputs=sorted(affected_outputs),
        unaffected_outputs=[o for o in OUTPUTS if o not in affected_outputs],
        reasoning=reasoning or ["No mapped downstream impact found for the submitted change."],
    )
