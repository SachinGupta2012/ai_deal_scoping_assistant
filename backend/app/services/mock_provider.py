"""Deterministic mock generation for free local demos."""
from app.schemas.architecture import ArchitectureModel
from app.schemas.data_ai import AIUseCase, DataAIStrategyModel, DataDomain, IntegrationItem
from app.schemas.prd import Capability, PRDModel
from app.schemas.scope import Assumption, ClarificationQuestion, Requirement, ScopeModel
from app.services.cloud_catalog import catalog_for


def _quote(text: str) -> str:
    cleaned = " ".join((text or "Customer provided requirements for a scoped delivery package.").split())
    return cleaned[:180] if len(cleaned) >= 10 else "Customer provided requirements for a scoped delivery package."


def _has(text: str, *needles: str) -> bool:
    lower = text.lower()
    return any(n.lower() in lower for n in needles)


def mock_scope(session_id: str, normalized_md: str, chunks: list) -> ScopeModel:
    quote = _quote(normalized_md)
    chunk_id = str(chunks[0]["idx"]) if chunks else "0"
    requirements = [
        Requirement(req_id="BR_01", type="BR", description="Improve the customer-facing workflow and reduce manual delivery effort", priority="High", chunk_id=chunk_id, quote=quote, origin="customer-stated"),
        Requirement(req_id="FR_01", type="FR", description="Provide a guided browser workflow with reviewable customer inputs and approvals", priority="High", chunk_id=chunk_id, quote=quote, origin="AI-inferred", dependencies=["BR_01"]),
        Requirement(req_id="NFR_01", type="NFR", description="Support a responsive local browser experience with auditable processing steps", priority="High", chunk_id=chunk_id, quote=quote, origin="AI-inferred"),
        Requirement(req_id="DATA_01", type="DATA", description="Store submitted customer requirements and generated scoping outputs with traceability", priority="Medium", chunk_id=chunk_id, quote=quote, origin="AI-inferred"),
    ]
    if _has(normalized_md, "salesforce", "crm", "api", "integration"):
        requirements.append(Requirement(req_id="INT_01", type="INT", description="Integrate with the stated external CRM or business system through a governed API", priority="Medium", chunk_id=chunk_id, quote=quote, origin="customer-stated"))
    if _has(normalized_md, "soc2", "security", "compliance", "privacy", "audit"):
        requirements.append(Requirement(req_id="SEC_01", type="SEC", description="Apply security, audit logging, and compliance controls to scoped outputs", priority="High", chunk_id=chunk_id, quote=quote, origin="customer-stated"))
    if _has(normalized_md, "ai", "rag", "model", "assistant", "llm"):
        requirements.append(Requirement(req_id="FR_02", type="FR", description="Use AI assistance for structured extraction while keeping human review mandatory", priority="High", chunk_id=chunk_id, quote=quote, origin="customer-stated"))
    assumptions = [
        Assumption(asm_id="ASM_01", text="Customer stakeholders will validate scope, assumptions, and commercial inputs before use", related_req_ids=["BR_01"], needs_review=True)
    ]
    questions = [
        ClarificationQuestion(q_id="Q_01", text="Confirm target production volume, approved identity provider, and integration API readiness", related_req_ids=["NFR_01"], blocking=False)
    ]
    return ScopeModel(
        session_id=session_id,
        requirements=requirements,
        assumptions=assumptions,
        questions=questions,
        objectives=["Create a traceable scoping package", "Identify gaps before final proposal review"],
        provider="mock",
        model="deterministic-seeded",
    )


def mock_prd(session_id: str, scope: dict, scope_version_no: int) -> PRDModel:
    reqs = scope.get("requirements", [])
    req_ids = [r["req_id"] for r in reqs]
    core_ids = [r["req_id"] for r in reqs if r.get("type") in ("BR", "FR")] or req_ids[:1]
    int_ids = [r["req_id"] for r in reqs if r.get("type") in ("INT", "DATA")] or req_ids[:1]
    nfr_ids = [r["req_id"] for r in reqs if r.get("type") in ("NFR", "SEC")] or req_ids[:1]
    capabilities = [
        Capability(capability_id="CAP_01", name="Scoping Workspace", description="Browser workspace for reviewing requirements, assumptions, questions, and approvals", included_req_ids=core_ids, priority="High"),
        Capability(capability_id="CAP_02", name="Connected Delivery Outputs", description="Generate PRD, architecture, data strategy, estimates, and package outputs from reviewed scope", included_req_ids=sorted(set(core_ids + int_ids)), priority="High"),
        Capability(capability_id="CAP_03", name="Governance and Validation", description="Track coverage, source traceability, unresolved questions, risks, and review gates", included_req_ids=nfr_ids, priority="High"),
    ]
    return PRDModel(
        session_id=session_id,
        overview="AI-assisted deal scoping workspace grounded in reviewed customer requirements.",
        business_problem="Sales and delivery teams need a faster, traceable way to convert messy customer inputs into validated planning outputs.",
        objectives=scope.get("objectives") or ["Create a reviewed scope model", "Generate connected planning outputs"],
        personas=["Sales / Presales", "Solution Architect", "Delivery Manager", "Product / BA"],
        journeys=["Enter customer inputs", "Review and approve scope", "Generate outputs", "Validate quality", "Export package"],
        capabilities=capabilities,
        nfr_summary=[r["description"] for r in reqs if r.get("type") == "NFR"],
        integrations=[r["description"] for r in reqs if r.get("type") == "INT"],
        dependencies=["Reviewed source requirements", "Stakeholder validation"],
        assumptions=[a.get("text", "") for a in scope.get("assumptions", [])],
        risks=["Unresolved integration or volume inputs may change estimates"],
        out_of_scope=["Final contractual quotation"],
        open_questions=[q.get("text", "") for q in scope.get("questions", [])],
        provider="mock",
        model="deterministic-seeded",
        scope_version_no=scope_version_no,
    )


def _first(ids: list[str]) -> list[str]:
    return ids[:1] or ["BR_01"]


def mock_architecture(session_id: str, scope: dict, platform: str, scope_version_no: int) -> ArchitectureModel:
    reqs = scope.get("requirements", [])
    req_ids = [r["req_id"] for r in reqs] or ["BR_01"]
    by_type = {t: [r["req_id"] for r in reqs if r.get("type") == t] for t in ("BR", "FR", "NFR", "INT", "DATA", "SEC")}
    catalog = catalog_for(platform)
    layers = [
        ("frontend", "Scoping Web App", _first(by_type["FR"] or by_type["BR"])),
        ("backend", "Scoping API", _first(by_type["FR"] or req_ids)),
        ("api", "External API Edge", _first(by_type["INT"] or by_type["FR"] or req_ids)),
        ("database", "Scope Store", _first(by_type["DATA"] or req_ids)),
        ("iam", "Identity and Access", _first(by_type["SEC"] or req_ids)),
        ("observability", "Audit Observability", _first(by_type["NFR"] or by_type["SEC"] or req_ids)),
        ("security", "Security Controls", _first(by_type["SEC"] or by_type["NFR"] or req_ids)),
        ("deployment", "Release Pipeline", _first(by_type["NFR"] or req_ids)),
    ]
    components = []
    for idx, (layer, name, supported) in enumerate(layers, start=1):
        service = (catalog.get(layer) or [layer])[0]
        components.append({
            "component_id": f"COMP_{idx:02d}",
            "name": name,
            "layer": layer,
            "cloud_service": service,
            "supported_req_ids": supported,
            "purpose": f"Provide {name.lower()} capability for the reviewed scope.",
            "rationale": f"{service} is selected from the approved {platform.upper()} catalog for this layer.",
            "tradeoffs": "Mock recommendation requires architect validation before production use.",
            "dependencies": [],
            "security": "Use managed identity, encrypted storage, secrets management, and audit logging.",
        })
    mermaid = "graph TD\n  COMP_01[Scoping Web App]-->COMP_02[Scoping API]\n  COMP_02-->COMP_04[Scope Store]\n  COMP_02-->COMP_06[Audit Observability]"
    return ArchitectureModel(
        session_id=session_id,
        platform=platform,
        platform_rationale=f"Mock mode selected {platform.upper()} using deterministic catalog-backed defaults.",
        components=components,
        mermaid=mermaid,
        provider="mock",
        model="deterministic-seeded",
        scope_version_no=scope_version_no,
    )


def mock_data_ai(session_id: str, scope: dict, scope_version_no: int) -> DataAIStrategyModel:
    reqs = scope.get("requirements", [])
    req_ids = [r["req_id"] for r in reqs] or ["BR_01"]
    data_ids = [r["req_id"] for r in reqs if r.get("type") == "DATA"] or req_ids[:1]
    int_ids = [r["req_id"] for r in reqs if r.get("type") == "INT"] or data_ids
    ai_ids = [r["req_id"] for r in reqs if r.get("type") in ("FR", "BR")] or req_ids[:1]
    return DataAIStrategyModel(
        session_id=session_id,
        data_domains=[
            DataDomain(domain_id="DD_01", name="Scope Model", sources=["Customer input", "Approved requirements"], ownership="Delivery team", ingestion="Text/upload normalization", storage="Managed PostgreSQL", storage_transactional="Scoped session tables", storage_analytical="Exported package snapshots", quality_rules=["Every output traces to reviewed requirement IDs"], metadata="Version hash and actor audit logs", governance="Human approval before downstream generation", retention="Local demo retention only", privacy="No external calls in mock mode", reporting="Coverage and quality gate summaries", backup_recovery="Database backups per environment", related_req_ids=data_ids)
        ],
        integrations=[
            IntegrationItem(int_id="ITI_01", name="Customer System Connector", source_system="Customer system", target_system="Scoping API", pattern="api-sync", auth="OAuth2 or approved service credentials", error_handling="Reject unsupported payloads with reviewable errors", retry="Backoff for transient API failures", monitoring="Audit log and operational metrics", sync_notes="Mock mode records the intended integration plan only", related_req_ids=int_ids)
        ],
        ai_use_cases=[
            AIUseCase(uc_id="AI_01", name="Scope Extraction Assistance", problem="Customer inputs are unstructured and require normalization", ai_function="Extract candidate requirements, assumptions, risks, and questions", deterministic_part="IDs, coverage, estimates, quality gate, and package calculations", human_review="Architect or reviewer approves scope before downstream generation", framework="Custom structured-output workflow", framework_rationale="The solution needs deterministic validation and traceability more than complex agent behavior", model_options=["mock deterministic provider", "Gemini", "OpenAI-compatible"], orchestration="Linear reviewed workflow", prompt_management="Versioned prompts and Pydantic validation", retrieval_needs="Customer source text and reviewed scope model", evaluation="Schema validation plus traceability and coverage checks", safety="Human review required for all planning outputs", privacy="Mock mode keeps data local; live mode requires customer approval", monitoring="Audit logs and quality gate issues", related_req_ids=ai_ids)
        ],
        data_flow_mermaid="graph TD\n  IN[Customer Input]-->DD_01[Scope Model]\n  DD_01-->ITI_01[Integration Plan]\n  DD_01-->AI_01[AI Assistance]",
        provider="mock",
        model="deterministic-seeded",
        scope_version_no=scope_version_no,
    )
