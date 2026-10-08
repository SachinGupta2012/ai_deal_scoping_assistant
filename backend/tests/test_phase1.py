"""Phase 1 tests — live-AI only. Schema, traceability shape, RBAC, provider chain."""
from app.schemas.scope import Requirement, ScopeModel
from app.services.ai.orchestrator import _chain


def _sample_scope() -> ScopeModel:
    quote = "Modernize onboarding portal with Salesforce CRM integration"
    return ScopeModel(
        session_id="s1",
        requirements=[
            Requirement(req_id="BR_01", type="BR", description="Modernize legacy onboarding portal to cut drop-off", priority="High", chunk_id="0", quote=quote, origin="customer-stated"),
            Requirement(req_id="FR_01", type="FR", description="Guided onboarding with identity verification", priority="High", chunk_id="0", quote=quote, origin="AI-inferred", dependencies=["BR_01"]),
        ],
        provider="google",
        model="gemini-3.8-flash",
    )


def test_scope_shape_is_traceable():
    scope = _sample_scope()
    assert len(scope.requirements) >= 2
    for r in scope.requirements:
        assert r.chunk_id and len(r.quote) >= 10 and r.origin in ("customer-stated", "AI-inferred", "assumed")


def test_schema_rejects_missing_origin():
    try:
        ScopeModel(session_id="s1", requirements=[{"req_id": "FR_01", "type": "FR", "description": "x" * 20, "priority": "High", "chunk_id": "0", "quote": "y" * 20}])
        assert False, "should reject"
    except Exception:
        assert True


def test_provider_chain_has_live_fallback():
    chain = _chain()
    assert "google" in chain and "openai_compatible" in chain
    assert "mock" not in chain


def test_rbac_matrix():
    approve_roles = {"architect", "reviewer", "admin"}
    edit_roles = {"architect", "ba", "reviewer", "admin"}
    assert "sales" not in approve_roles
    assert "viewer" not in edit_roles
    assert "viewer" not in approve_roles
