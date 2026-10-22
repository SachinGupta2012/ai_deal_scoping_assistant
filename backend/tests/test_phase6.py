"""Phase 6 tests — change impact, quality gate, package export."""
from app.schemas.package import ChangeImpactRequest
from app.services.change_impact import analyze_change_impact
from app.services.package_assembler import DISCLAIMER, assemble_package
from app.services.quality_gate import run_quality_gate


def _complete_scope():
    return {
        "requirements": [
            {"req_id": "BR_01", "type": "BR", "description": "Modernize onboarding", "priority": "High", "origin": "customer-stated"},
            {"req_id": "FR_01", "type": "FR", "description": "Guided onboarding", "priority": "High", "origin": "customer-stated"},
            {"req_id": "NFR_01", "type": "NFR", "description": "P95 under 3 minutes", "priority": "High", "origin": "customer-stated"},
            {"req_id": "INT_01", "type": "INT", "description": "CRM API", "priority": "Medium", "origin": "customer-stated"},
            {"req_id": "DATA_01", "type": "DATA", "description": "Customer data", "priority": "Medium", "origin": "customer-stated"},
            {"req_id": "SEC_01", "type": "SEC", "description": "SOC2 logging", "priority": "High", "origin": "customer-stated"},
        ],
        "assumptions": [],
        "questions": [],
        "objectives": ["Prepare package"],
        "prd": {
            "overview": "Reviewed scope",
            "capabilities": [
                {"capability_id": "CAP_01", "name": "Onboarding", "included_req_ids": ["BR_01", "FR_01"]},
                {"capability_id": "CAP_02", "name": "Compliance", "included_req_ids": ["NFR_01", "SEC_01"]},
            ],
            "coverage": {"coverage_pct": 100.0, "uncovered_req_ids": [], "unsupported_capabilities": [], "unsupported_integrations": [], "unsupported_ai_use_cases": []},
            "risks": [],
        },
        "architecture": {
            "platform": "aws",
            "platform_rationale": "AWS catalog selected",
            "components": [
                {"component_id": "COMP_01", "name": "API", "cloud_service": "API Gateway", "supported_req_ids": ["FR_01"]},
                {"component_id": "COMP_02", "name": "Logs", "cloud_service": "CloudWatch + X-Ray", "supported_req_ids": ["NFR_01", "SEC_01"]},
            ],
            "mermaid": "graph TD\n A-->B",
            "validation": {"off_catalog": [], "missing_layers": []},
        },
        "data_ai": {
            "coverage": {"coverage_pct": 100.0, "uncovered_req_ids": [], "unsupported_capabilities": [], "unsupported_integrations": [], "unsupported_ai_use_cases": []},
            "data_domains": [{"domain_id": "DD_01", "name": "Customer", "related_req_ids": ["DATA_01"]}],
            "integrations": [{"int_id": "ITI_01", "name": "CRM", "related_req_ids": ["INT_01"]}],
            "ai_use_cases": [{"uc_id": "AI_01", "name": "Extract", "related_req_ids": ["FR_01"], "evaluation": "schema", "safety": "review", "human_review": "approve", "privacy": "local"}],
        },
        "estimate": {
            "total_effort_low_pw": 10,
            "total_effort_high_pw": 15,
            "timeline_low_weeks": 4,
            "timeline_high_weeks": 6,
            "rom_low": 100000,
            "rom_high": 150000,
            "confidence": "High",
            "risks": [],
            "config": {"currency": "USD"},
            "workstreams": [{"workstream_id": "WS_01", "name": "Core", "related_req_ids": ["FR_01", "INT_01"], "effort_low_pw": 5, "effort_high_pw": 8}],
        },
    }


def test_change_impact_maps_requirement_to_outputs():
    impact = analyze_change_impact("s1", _complete_scope(), ChangeImpactRequest(changed_req_ids=["FR_01"]))
    assert "CAP_01" in impact.affected_capability_ids
    assert "COMP_01" in impact.affected_component_ids
    assert "WS_01" in impact.affected_workstream_ids
    assert "estimate" in impact.affected_outputs and "package" in impact.affected_outputs
    assert "INT_01" in impact.unaffected_req_ids


def test_quality_gate_passes_complete_scope():
    gate = run_quality_gate("s1", _complete_scope())
    assert gate.status == "Pass"
    assert gate.issues == []


def test_quality_gate_blocks_missing_estimate_and_uncovered_high():
    scope = _complete_scope()
    scope.pop("estimate")
    scope["data_ai"]["coverage"]["uncovered_req_ids"] = ["FR_01"]
    scope["data_ai"]["coverage"]["coverage_pct"] = 80.0
    gate = run_quality_gate("s1", scope)
    assert gate.status == "Blocked"
    assert any(i.category == "missing-estimate" for i in gate.issues)
    assert any(i.category == "coverage" and i.severity == "blocker" for i in gate.issues)


def test_package_contains_mandatory_disclaimer(tmp_path, monkeypatch):
    import app.services.package_assembler as assembler

    monkeypatch.setattr(assembler, "save_package", lambda session_id, markdown: str(tmp_path / "package.md"))
    gate = run_quality_gate("s1", _complete_scope())
    package = assemble_package("s1", _complete_scope(), gate)
    assert DISCLAIMER in package.markdown
    assert package.quality_gate.status == "Pass"
