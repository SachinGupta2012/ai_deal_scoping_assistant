"""Deterministic FR-5 estimator. No LLM-generated numbers."""
from app.schemas.estimation import (
    ComplexityProfile,
    EstimateConfig,
    EstimationModel,
    RoleAllocation,
    WorkstreamEstimate,
)


def _req_ids(requirements: list[dict]) -> list[str]:
    return [r.get("req_id", "") for r in requirements if r.get("req_id")]


def _ids_from(items: list[dict], key: str) -> list[str]:
    ids: set[str] = set()
    for item in items:
        ids.update(i for i in item.get(key, []) if isinstance(i, str))
    return sorted(ids)


def _rate_map(config: EstimateConfig) -> dict[str, float]:
    return {r.role: r.rate_per_week for r in config.role_rates}


def _blended_rate(roles: list[RoleAllocation], rates: dict[str, float]) -> float:
    return round(sum(r.allocation_pct * rates.get(r.role, 0) for r in roles), 2)


def _band(score: float) -> str:
    if score <= 10:
        return "Low"
    if score <= 24:
        return "Medium"
    return "High"


def _ws_band(base: float) -> str:
    if base < 5:
        return "Low"
    if base < 12:
        return "Medium"
    return "High"


def _round(value: float) -> float:
    return round(value, 1)


def _timeline(effort: float, config: EstimateConfig) -> float:
    return _round(effort / config.team_capacity_pw_per_week)


def _workstream(
    idx: int,
    name: str,
    req_ids: list[str],
    base_low: float,
    high_multiplier: float,
    roles: list[RoleAllocation],
    rates: dict[str, float],
    config: EstimateConfig,
    drivers: list[str],
    assumptions: list[str] | None = None,
    dependencies: list[str] | None = None,
    confidence: str = "Medium",
) -> WorkstreamEstimate:
    low = _round(base_low / config.productivity_factor)
    high = _round(low * high_multiplier)
    return WorkstreamEstimate(
        workstream_id=f"WS_{idx:02d}",
        name=name,
        related_req_ids=sorted(set(req_ids)),
        complexity=_ws_band(base_low),
        effort_low_pw=low,
        effort_high_pw=high,
        timeline_low_weeks=_timeline(low, config),
        timeline_high_weeks=_timeline(high, config),
        blended_rate_per_week=_blended_rate(roles, rates),
        roles=roles,
        drivers=drivers,
        assumptions=assumptions or [],
        dependencies=dependencies or [],
        confidence=confidence,
    )


def _sum_cost(workstreams: list[WorkstreamEstimate], attr: str) -> float:
    return round(sum(getattr(w, attr) * w.blended_rate_per_week for w in workstreams), 2)


def calculate_estimate(
    session_id: str,
    scope: dict,
    scope_version_no: int,
    config: EstimateConfig | None = None,
) -> EstimationModel:
    cfg = config or EstimateConfig()
    requirements = scope.get("requirements", [])
    prd = scope.get("prd") or {}
    data_ai = scope.get("data_ai") or {}
    architecture = scope.get("architecture") or {}
    capabilities = prd.get("capabilities") or []
    integrations = data_ai.get("integrations") or []
    domains = data_ai.get("data_domains") or []
    ai_use_cases = data_ai.get("ai_use_cases") or []
    req_ids = _req_ids(requirements)
    nfr_ids = [r["req_id"] for r in requirements if r.get("type") == "NFR"]
    sec_ids = [r["req_id"] for r in requirements if r.get("type") == "SEC"]
    int_ids = [r["req_id"] for r in requirements if r.get("type") == "INT"]
    data_ids = [r["req_id"] for r in requirements if r.get("type") == "DATA"]
    high_ids = [r["req_id"] for r in requirements if r.get("priority") == "High"]
    cap_count = len(capabilities) or len([r for r in requirements if r.get("type") in ("BR", "FR")])
    integration_count = len(integrations) or len(int_ids)
    data_count = len(domains) or len(data_ids)
    ai_count = len(ai_use_cases)
    score = cap_count * 2 + integration_count * 3 + data_count * 2 + ai_count * 4 + len(nfr_ids) + len(sec_ids) * 2 + len(high_ids)
    complexity = ComplexityProfile(
        capability_count=cap_count,
        integration_count=integration_count,
        data_domain_count=data_count,
        ai_use_case_count=ai_count,
        nfr_count=len(nfr_ids),
        security_req_count=len(sec_ids),
        high_priority_count=len(high_ids),
        complexity_score=score,
        complexity_band=_band(score),
    )
    rates = _rate_map(cfg)
    missing: list[str] = []
    required_roles = {
        "Solution Architect",
        "Product/BA",
        "Frontend Engineer",
        "Backend Engineer",
        "Data/Integration Engineer",
        "AI Engineer",
        "QA Engineer",
        "DevOps Engineer",
        "Delivery Manager",
    }
    missing.extend(f"Missing weekly rate for {role}" for role in sorted(required_roles - set(rates)))
    if not capabilities:
        missing.append("PRD capabilities not generated; using requirement counts as sizing proxy")
    if not architecture:
        missing.append("Architecture not generated; deployment and cloud complexity confidence reduced")
    if not data_ai:
        missing.append("Data/AI strategy not generated; integration, data, and AI sizing may be incomplete")
    open_questions = scope.get("questions") or []
    blocking = [q for q in open_questions if q.get("blocking")]
    if blocking:
        missing.append(f"{len(blocking)} blocking clarification question(s) unresolved")
    if open_questions:
        missing.append(f"{len(open_questions)} open clarification question(s) unresolved")
    assumptions_need_review = [a for a in scope.get("assumptions", []) if a.get("needs_review", True)]
    if assumptions_need_review:
        missing.append(f"{len(assumptions_need_review)} assumption(s) need review")
    cap_req_ids = _ids_from(capabilities, "included_req_ids") or [i for i in req_ids if i.startswith(("BR_", "FR_"))]
    data_req_ids = sorted(set(_ids_from(integrations, "related_req_ids") + _ids_from(domains, "related_req_ids") + int_ids + data_ids))
    ai_req_ids = _ids_from(ai_use_cases, "related_req_ids")
    arch_req_ids = _ids_from(architecture.get("components") or [], "supported_req_ids")
    confidence = "Low" if blocking or len(missing) >= 4 else ("Medium" if missing else "High")
    ws_confidence = "Low" if confidence == "Low" else "Medium"
    workstreams = [
        _workstream(
            1,
            "Discovery + Architecture",
            sorted(set(req_ids + arch_req_ids)),
            2 + cap_count * 0.3 + len(nfr_ids) * 0.2 + len(sec_ids) * 0.4,
            1.35,
            [RoleAllocation(role="Solution Architect", allocation_pct=0.5), RoleAllocation(role="Product/BA", allocation_pct=0.3), RoleAllocation(role="Delivery Manager", allocation_pct=0.2)],
            rates,
            cfg,
            [f"{cap_count} capability area(s)", f"{len(nfr_ids)} NFR(s)", f"{len(sec_ids)} security/compliance requirement(s)"],
            ["Architecture choices must be validated by qualified architects"],
            confidence=ws_confidence,
        ),
        _workstream(
            2,
            "Experience + Core Platform",
            cap_req_ids,
            3 + cap_count * 1.2 + len(nfr_ids) * 0.3,
            1.45,
            [RoleAllocation(role="Frontend Engineer", allocation_pct=0.35), RoleAllocation(role="Backend Engineer", allocation_pct=0.45), RoleAllocation(role="Product/BA", allocation_pct=0.2)],
            rates,
            cfg,
            [f"{cap_count} capability/capabilities", f"{len(high_ids)} high-priority requirement(s)"],
            ["UI complexity is estimated from capability count until detailed wireframes exist"],
            confidence=ws_confidence,
        ),
        _workstream(
            3,
            "Data + Integration",
            data_req_ids,
            1 + integration_count * 1.4 + data_count * 1.1,
            1.5,
            [RoleAllocation(role="Data/Integration Engineer", allocation_pct=0.65), RoleAllocation(role="Backend Engineer", allocation_pct=0.25), RoleAllocation(role="Solution Architect", allocation_pct=0.1)],
            rates,
            cfg,
            [f"{integration_count} integration(s)", f"{data_count} data domain(s)"],
            ["External API readiness and migration volumes can change this range"],
            confidence=ws_confidence,
        ),
        _workstream(
            4,
            "AI Capabilities",
            ai_req_ids,
            ai_count * 1.8,
            1.7,
            [RoleAllocation(role="AI Engineer", allocation_pct=0.6), RoleAllocation(role="Backend Engineer", allocation_pct=0.25), RoleAllocation(role="Product/BA", allocation_pct=0.15)],
            rates,
            cfg,
            [f"{ai_count} AI use case(s)", "Evaluation and human-review paths included"],
            ["AI estimates exclude paid model usage and production token costs"],
            confidence=ws_confidence,
        ),
        _workstream(
            5,
            "Testing + Hardening",
            sorted(set(req_ids)),
            1.5 + cap_count * 0.4 + integration_count * 0.4 + ai_count * 0.5 + len(sec_ids) * 0.4,
            1.55,
            [RoleAllocation(role="QA Engineer", allocation_pct=0.55), RoleAllocation(role="Backend Engineer", allocation_pct=0.2), RoleAllocation(role="Frontend Engineer", allocation_pct=0.15), RoleAllocation(role="DevOps Engineer", allocation_pct=0.1)],
            rates,
            cfg,
            ["Regression, integration, NFR, and security validation"],
            ["Formal security testing scope may require a separate specialist estimate"],
            confidence=ws_confidence,
        ),
        _workstream(
            6,
            "Deployment + Handover",
            sorted(set(arch_req_ids + req_ids)),
            1.5 + (0.5 if architecture else 1.0) + len(sec_ids) * 0.2,
            1.3,
            [RoleAllocation(role="DevOps Engineer", allocation_pct=0.45), RoleAllocation(role="Solution Architect", allocation_pct=0.25), RoleAllocation(role="Delivery Manager", allocation_pct=0.3)],
            rates,
            cfg,
            ["Environment setup, release readiness, and handover"],
            ["Production access, CI/CD, and cloud guardrails are available on time"],
            confidence=ws_confidence,
        ),
    ]
    if ai_count == 0:
        workstreams[3].drivers.append("No AI use cases identified yet; effort remains zero until AI scope is added")
    total_low = _round(sum(w.effort_low_pw for w in workstreams))
    total_high = _round(sum(w.effort_high_pw for w in workstreams))
    base_low = _sum_cost(workstreams, "effort_low_pw")
    base_high = _sum_cost(workstreams, "effort_high_pw")
    contingency_low = round(base_low * cfg.contingency_pct, 2)
    contingency_high = round(base_high * cfg.contingency_pct, 2)
    risks = []
    if missing:
        risks.append("Estimate confidence reduced by unresolved inputs")
    if integration_count:
        risks.append("Integration effort may change after API contracts and environments are confirmed")
    if ai_count:
        risks.append("AI effort may change after evaluation thresholds and human-review policy are approved")
    return EstimationModel(
        session_id=session_id,
        scope_version_no=scope_version_no,
        config=cfg,
        complexity=complexity,
        workstreams=workstreams,
        total_effort_low_pw=total_low,
        total_effort_high_pw=total_high,
        timeline_low_weeks=_round(sum(w.timeline_low_weeks for w in workstreams)),
        timeline_high_weeks=_round(sum(w.timeline_high_weeks for w in workstreams)),
        base_rom_low=base_low,
        base_rom_high=base_high,
        contingency_amount_low=contingency_low,
        contingency_amount_high=contingency_high,
        rom_low=round(base_low + contingency_low, 2),
        rom_high=round(base_high + contingency_high, 2),
        confidence=confidence,
        missing_inputs=missing,
        risks=risks,
        assumptions=[
            "Effort is expressed in person-weeks",
            "Timeline assumes workstreams run in the listed sequence",
            "ROM excludes taxes, cloud consumption, software licenses, and model token usage",
        ],
        calculation_rules=[
            "Complexity score = capabilities*2 + integrations*3 + data_domains*2 + AI_use_cases*4 + NFRs + security*2 + high_priority",
            "Effort is calculated from visible scope counts and divided by productivity_factor",
            "Timeline per workstream = effort person-weeks / team_capacity_pw_per_week",
            "ROM = sum(workstream effort * blended role rate) * (1 + contingency_pct)",
        ],
    )
