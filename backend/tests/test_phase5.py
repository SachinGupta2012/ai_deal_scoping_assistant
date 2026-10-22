"""Phase 5 tests — deterministic estimation and ROM calculations."""
from app.schemas.estimation import EstimateConfig, RoleRate
from app.services.estimation import calculate_estimate


def _scope():
    return {
        "requirements": [
            {"req_id": "BR_01", "type": "BR", "description": "Modernize onboarding", "priority": "High"},
            {"req_id": "FR_01", "type": "FR", "description": "Guided onboarding", "priority": "High"},
            {"req_id": "NFR_01", "type": "NFR", "description": "P95 under 3 minutes", "priority": "High"},
            {"req_id": "INT_01", "type": "INT", "description": "Salesforce API", "priority": "Medium"},
            {"req_id": "DATA_01", "type": "DATA", "description": "Customer profile data", "priority": "Medium"},
            {"req_id": "SEC_01", "type": "SEC", "description": "SOC2 logging", "priority": "High"},
        ],
        "assumptions": [{"asm_id": "ASM_01", "text": "API access will be available", "needs_review": True}],
        "questions": [{"q_id": "Q_01", "text": "Which IdP is approved?", "blocking": False}],
        "prd": {
            "capabilities": [
                {"capability_id": "CAP_01", "included_req_ids": ["FR_01", "BR_01"]},
                {"capability_id": "CAP_02", "included_req_ids": ["FR_01", "INT_01"]},
            ]
        },
        "architecture": {
            "components": [
                {"component_id": "COMP_01", "supported_req_ids": ["FR_01", "NFR_01"]},
                {"component_id": "COMP_02", "supported_req_ids": ["SEC_01"]},
            ]
        },
        "data_ai": {
            "data_domains": [{"domain_id": "DD_01", "related_req_ids": ["DATA_01"]}],
            "integrations": [{"int_id": "ITI_01", "related_req_ids": ["INT_01"]}],
            "ai_use_cases": [{"uc_id": "AI_01", "related_req_ids": ["FR_01"]}],
        },
    }


def test_estimate_generates_visible_workstreams_and_rom():
    estimate = calculate_estimate("s1", _scope(), 3)
    assert estimate.total_effort_low_pw > 0
    assert estimate.rom_high > estimate.rom_low > 0
    assert len(estimate.workstreams) == 6
    assert "ROM = sum" in estimate.calculation_rules[-1]


def test_rate_change_changes_rom():
    base = calculate_estimate("s1", _scope(), 3)
    cfg = EstimateConfig(role_rates=[RoleRate(role=r.role, rate_per_week=r.rate_per_week * 2) for r in EstimateConfig().role_rates])
    changed = calculate_estimate("s1", _scope(), 3, cfg)
    assert changed.rom_low == base.rom_low * 2


def test_contingency_changes_rom_without_changing_effort():
    low_contingency = calculate_estimate("s1", _scope(), 3, EstimateConfig(contingency_pct=0.1))
    high_contingency = calculate_estimate("s1", _scope(), 3, EstimateConfig(contingency_pct=0.3))
    assert high_contingency.total_effort_low_pw == low_contingency.total_effort_low_pw
    assert high_contingency.rom_low > low_contingency.rom_low


def test_missing_outputs_reduce_confidence():
    scope = {"requirements": _scope()["requirements"], "questions": [{"q_id": "Q_01", "text": "Need API docs", "blocking": True}]}
    estimate = calculate_estimate("s1", scope, 1)
    assert estimate.confidence == "Low"
    assert any("blocking" in item for item in estimate.missing_inputs)
