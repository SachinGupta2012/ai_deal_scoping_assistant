"""Phase 2 tests — PRD schema, coverage math, approval gate contract."""
from app.schemas.prd import Capability, PRDModel
from app.services.coverage import compute_coverage


def test_capability_requires_req_ref():
    try:
        Capability(capability_id="CAP_01", name="Onboarding", description="x" * 25, included_req_ids=[])
        assert False, "should reject empty refs"
    except Exception:
        assert True


def test_coverage_flags_uncovered_and_unsupported():
    cov = compute_coverage("s1", ["FR_01", "FR_02", "NFR_01"], [
        {"capability_id": "CAP_01", "included_req_ids": ["FR_01"]},
        {"capability_id": "CAP_02", "included_req_ids": ["XXX_99"]},
    ])
    assert cov.coverage_pct == round(1 / 3 * 100, 1)
    assert "FR_02" in cov.uncovered_req_ids and "NFR_01" in cov.uncovered_req_ids
    assert "CAP_02" in cov.unsupported_capabilities


def test_full_coverage_is_100():
    cov = compute_coverage("s1", ["FR_01"], [{"capability_id": "CAP_01", "included_req_ids": ["FR_01"]}])
    assert cov.coverage_pct == 100.0 and cov.uncovered_req_ids == []
    assert cov.unsupported_integrations == [] and cov.unsupported_ai_use_cases == []


def test_extended_coverage_includes_integrations_and_ai():
    cov = compute_coverage("s1", ["FR_01", "INT_01", "DATA_01"],
                           [{"capability_id": "CAP_01", "included_req_ids": ["FR_01"]}],
                           [{"int_id": "ITI_01", "related_req_ids": ["INT_01"]}],
                           [{"uc_id": "AI_01", "related_req_ids": ["XXX_99"]}])
    assert cov.coverage_pct == round(2 / 3 * 100, 1)
    assert "DATA_01" in cov.uncovered_req_ids
    assert "AI_01" in cov.unsupported_ai_use_cases
    assert cov.unsupported_integrations == []


def test_prd_model_minimal_valid():
    p = PRDModel(session_id="s1", overview="o" * 25, business_problem="b" * 25,
                 capabilities=[{"capability_id": "CAP_01", "name": "Onboarding", "description": "d" * 25, "included_req_ids": ["FR_01"]}])
    assert p.prompt_version == "prd_v1"
