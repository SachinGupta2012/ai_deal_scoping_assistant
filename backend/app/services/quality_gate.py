"""FR-6 quality gate checks before export."""
from app.schemas.package import QualityGateModel, QualityIssue


def _issue(idx: int, severity: str, category: str, message: str, related_ids: list[str] | None = None) -> QualityIssue:
    return QualityIssue(issue_id=f"QG_{idx:02d}", severity=severity, category=category, message=message, related_ids=related_ids or [])


def run_quality_gate(session_id: str, scope: dict) -> QualityGateModel:
    issues: list[QualityIssue] = []
    idx = 1
    requirements = scope.get("requirements", [])
    req_ids = [r.get("req_id", "") for r in requirements if r.get("req_id")]
    high_ids = [r.get("req_id") for r in requirements if r.get("priority") == "High"]
    prd = scope.get("prd") or {}
    arch = scope.get("architecture") or {}
    data_ai = scope.get("data_ai") or {}
    estimate = scope.get("estimate") or {}
    coverage = data_ai.get("coverage") or prd.get("coverage") or {}
    uncovered = coverage.get("uncovered_req_ids", req_ids if req_ids else [])
    coverage_pct = float(coverage.get("coverage_pct", 0.0))
    if not prd:
        issues.append(_issue(idx, "blocker", "missing-output", "PRD and functional scope have not been generated.")); idx += 1
    if not arch:
        issues.append(_issue(idx, "blocker", "missing-output", "Architecture has not been generated.")); idx += 1
    if not data_ai:
        issues.append(_issue(idx, "blocker", "missing-output", "Data/integration/AI strategy has not been generated.")); idx += 1
    if not estimate:
        issues.append(_issue(idx, "blocker", "missing-estimate", "Estimate and ROM have not been generated.")); idx += 1
    high_uncovered = sorted(set(high_ids).intersection(uncovered))
    if high_uncovered:
        issues.append(_issue(idx, "blocker", "coverage", "High-priority requirements are uncovered.", high_uncovered)); idx += 1
    if uncovered:
        issues.append(_issue(idx, "warning", "coverage", "Some requirements are not covered by downstream outputs.", uncovered)); idx += 1
    unsupported = (
        coverage.get("unsupported_capabilities", [])
        + coverage.get("unsupported_integrations", [])
        + coverage.get("unsupported_ai_use_cases", [])
    )
    if unsupported:
        issues.append(_issue(idx, "warning", "unsupported-output", "Some outputs reference unsupported requirement IDs.", unsupported)); idx += 1
    validation = arch.get("validation") or {}
    if validation.get("off_catalog"):
        issues.append(_issue(idx, "warning", "architecture", "Architecture includes off-catalog services.", validation["off_catalog"])); idx += 1
    if validation.get("missing_layers"):
        issues.append(_issue(idx, "warning", "architecture", "Architecture is missing required layers.", validation["missing_layers"])); idx += 1
    int_req_ids = [r.get("req_id") for r in requirements if r.get("type") == "INT"]
    planned_int_req_ids = sorted({rid for item in data_ai.get("integrations", []) for rid in item.get("related_req_ids", [])})
    missing_integrations = sorted(set(int_req_ids) - set(planned_int_req_ids))
    if missing_integrations:
        issues.append(_issue(idx, "warning", "integration", "Integration requirements are missing from the integration plan.", missing_integrations)); idx += 1
    for ai in data_ai.get("ai_use_cases", []):
        missing = [f for f in ("evaluation", "safety", "human_review", "privacy") if not ai.get(f)]
        if missing:
            issues.append(_issue(idx, "warning", "ai-governance", f"AI use case {ai.get('uc_id')} is missing {', '.join(missing)}.", [ai.get("uc_id", "")])); idx += 1
    open_questions = scope.get("questions", [])
    if open_questions:
        issues.append(_issue(idx, "warning", "open-questions", "Open clarification questions remain unresolved.", [q.get("q_id", "") for q in open_questions])); idx += 1
    review_assumptions = [a.get("asm_id", "") for a in scope.get("assumptions", []) if a.get("needs_review", True)]
    if review_assumptions:
        issues.append(_issue(idx, "warning", "assumptions", "Assumptions still need stakeholder validation.", review_assumptions)); idx += 1
    if estimate.get("missing_inputs"):
        issues.append(_issue(idx, "warning", "estimate", "Estimate has missing or unresolved inputs.", estimate.get("missing_inputs", []))); idx += 1
    if estimate and estimate.get("rom_high", 0) < estimate.get("rom_low", 0):
        issues.append(_issue(idx, "blocker", "estimate", "ROM high is lower than ROM low.", [])); idx += 1
    if estimate and estimate.get("total_effort_high_pw", 0) < estimate.get("total_effort_low_pw", 0):
        issues.append(_issue(idx, "blocker", "estimate", "Effort high is lower than effort low.", [])); idx += 1
    if any(i.severity == "blocker" for i in issues):
        status = "Blocked"
    elif issues:
        status = "Review Required"
    else:
        status = "Pass"
    return QualityGateModel(
        session_id=session_id,
        status=status,
        coverage_pct=coverage_pct,
        uncovered_req_ids=uncovered,
        open_question_count=len(open_questions),
        assumptions_needing_review=len(review_assumptions),
        estimate_confidence=estimate.get("confidence", ""),
        issues=issues,
        summary=f"Coverage {coverage_pct}%, Uncovered {len(uncovered)}, Open Q {len(open_questions)}, Issues {len(issues)}, Status: {status}",
    )
