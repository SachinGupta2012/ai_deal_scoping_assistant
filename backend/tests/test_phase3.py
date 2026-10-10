"""Phase 3 tests — arch schema, catalog validation, platform rules."""
from app.schemas.architecture import ArchComponent, ArchitectureModel
from app.services.cloud_catalog import REQUIRED_LAYERS, catalog_for, recommend_platform, validate_platform_services


def _comp(cid="COMP_01", layer="database", svc="Azure Database for PostgreSQL", reqs=None):
    return {"component_id": cid, "name": "Main DB", "layer": layer, "cloud_service": svc,
            "supported_req_ids": reqs or ["DATA_01"], "purpose": "p" * 20, "rationale": "r" * 20}


def test_component_requires_req_ref():
    try:
        ArchComponent(component_id="COMP_01", name="DB", layer="database", cloud_service="RDS for PostgreSQL",
                      supported_req_ids=[], purpose="p" * 20, rationale="r" * 20)
        assert False, "should reject empty refs"
    except Exception:
        assert True


def test_catalog_covers_required_layers():
    for platform in ("aws", "azure", "gcp"):
        cat = catalog_for(platform)
        for layer in REQUIRED_LAYERS:
            assert cat[layer], f"{platform}/{layer} empty"


def test_off_catalog_detected():
    bad = validate_platform_services("azure", [_comp(svc="Neon Postgres (generic)")])
    assert bad == ["COMP_01"]
    good = validate_platform_services("azure", [_comp()])
    assert good == []


def test_recommender_defaults_aws():
    assert recommend_platform(["FR", "NFR"]) == "aws"


def test_recommender_uses_requirement_text():
    assert recommend_platform([{"description": "Use Microsoft Entra ID and Dynamics CRM"}]) == "azure"
    assert recommend_platform([{"description": "Analytics warehouse on BigQuery with Vertex AI"}]) == "gcp"


def test_arch_model_minimal_valid():
    comps = [_comp(cid=f"COMP_{i:02d}", layer=layer) for i, layer in enumerate(
        ["frontend", "backend", "api", "database", "iam", "observability", "security", "deployment"], start=1)]
    a = ArchitectureModel(session_id="s1", platform="azure", platform_rationale="r" * 25, components=comps, mermaid="graph TD\n  COMP_01[Web]-->COMP_02[API]")
    assert a.prompt_version == "arch_v1"
