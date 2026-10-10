"""Mock mode tests — seeded flow works without paid AI."""
from app.core.config import settings
from app.services.arch_generator import generate_architecture
from app.services.ai.orchestrator import _chain, run_analysis
from app.services.coverage import compute_coverage
from app.services.data_ai_generator import generate_data_ai
from app.services.estimation import calculate_estimate
from app.services.package_assembler import DISCLAIMER, assemble_package
from app.services.prd_generator import generate_prd
from app.services.quality_gate import run_quality_gate


def test_mock_chain_is_default(monkeypatch):
    monkeypatch.setattr(settings, "USE_MOCK_AI", True)
    monkeypatch.setattr(settings, "AI_PROVIDER", "mock")
    assert _chain() == ["mock"]


def test_mock_flow_generates_traceable_outputs(monkeypatch):
    monkeypatch.setattr(settings, "USE_MOCK_AI", True)
    monkeypatch.setattr(settings, "AI_PROVIDER", "mock")
    text = "Modernize onboarding portal with Salesforce CRM integration, SOC2 logging, and AI-assisted review."
    scope, meta = run_analysis("s1", text, [{"idx": "0", "text": text}])
    payload = scope.model_dump()
    prd = generate_prd("s1", payload, 1)
    arch = generate_architecture("s1", {**payload, "prd": prd.model_dump()}, "aws", 2)
    data_ai = generate_data_ai("s1", {**payload, "prd": prd.model_dump(), "architecture": arch.model_dump()}, 3)
    assert meta["provider"] == "mock"
    assert prd.provider == "mock" and prd.capabilities[0].included_req_ids
    assert arch.provider == "mock" and arch.components[0].supported_req_ids
    assert data_ai.provider == "mock" and data_ai.ai_use_cases[0].related_req_ids


def test_full_mock_pipeline_reaches_package_export(tmp_path, monkeypatch):
    import app.services.package_assembler as assembler

    monkeypatch.setattr(settings, "USE_MOCK_AI", True)
    monkeypatch.setattr(settings, "AI_PROVIDER", "mock")
    monkeypatch.setattr(assembler, "save_package", lambda session_id, markdown: str(tmp_path / "package.md"))
    text = "Modernize onboarding portal with Salesforce CRM integration, SOC2 logging, and AI-assisted review."
    scope, _ = run_analysis("s1", text, [{"idx": "0", "text": text}])
    payload = scope.model_dump()
    req_ids = [r["req_id"] for r in payload["requirements"]]
    prd = generate_prd("s1", payload, 1).model_dump()
    prd["coverage"] = compute_coverage("s1", req_ids, prd["capabilities"]).model_dump()
    arch = generate_architecture("s1", {**payload, "prd": prd}, "aws", 2).model_dump()
    data_ai = generate_data_ai("s1", {**payload, "prd": prd, "architecture": arch}, 3).model_dump()
    data_ai["coverage"] = compute_coverage("s1", req_ids, prd["capabilities"], data_ai["integrations"], data_ai["ai_use_cases"]).model_dump()
    merged = {**payload, "prd": prd, "architecture": arch, "data_ai": data_ai}
    merged["estimate"] = calculate_estimate("s1", merged, 4).model_dump()
    gate = run_quality_gate("s1", merged)
    package = assemble_package("s1", merged, gate)
    assert gate.status == "Review Required"
    assert DISCLAIMER in package.markdown
    assert package.export_path.endswith("package.md")
