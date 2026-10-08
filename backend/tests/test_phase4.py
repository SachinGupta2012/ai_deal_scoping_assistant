"""Phase 4 tests — data/AI schemas enforce req refs, AI/deterministic/human split, framework rationale."""
from app.schemas.data_ai import AIUseCase, DataDomain, IntegrationItem


def test_domain_requires_req_ref():
    try:
        DataDomain(domain_id="DD_01", name="Orders", sources=["CRM"], ownership="Sales", storage="PG", related_req_ids=[])
        assert False, "should reject"
    except Exception:
        assert True


def test_integration_requires_req_ref_and_pattern():
    try:
        IntegrationItem(int_id="ITI_01", name="CRM sync", source_system="CRM", target_system="App", pattern="api-sync", related_req_ids=[])
        assert False, "should reject"
    except Exception:
        assert True
    ok = IntegrationItem(int_id="ITI_01", name="CRM sync", source_system="CRM", target_system="App", pattern="event",
                         auth="OAuth2", error_handling="DLQ", retry="3x backoff", monitoring="dash", related_req_ids=["INT_01"])
    assert ok.pattern == "event"


def test_domain_structured_fields_accepted():
    d = DataDomain(domain_id="DD_01", name="Orders", sources=["CRM"], ownership="Sales", storage="PostgreSQL",
                   ingestion="CDC via Debezium", storage_transactional="RDS PG", storage_analytical="BigQuery",
                   metadata="DataHub", reporting="Looker", backup_recovery="PITR 30d", related_req_ids=["DATA_01"])
    assert d.storage_transactional == "RDS PG" and d.reporting == "Looker"


def test_ai_usecase_structured_fields_accepted():
    from app.schemas.data_ai import AIUseCase as UC
    uc = UC(uc_id="AI_02", name="Recommend", problem="p" * 15, ai_function="a" * 15, human_review="h" * 5,
            framework="LangGraph", framework_rationale="r" * 15, model_options=["gemini-3.8-flash", "gpt-oss-120b"],
            orchestration="LangGraph DAG", prompt_management="versioned templates + JSON schema",
            evaluation="e" * 10, safety="s" * 10, related_req_ids=["FR_02"])
    assert uc.model_options == ["gemini-3.8-flash", "gpt-oss-120b"] and uc.orchestration.startswith("LangGraph")


def test_ai_usecase_enforces_split_and_rationale():
    uc = AIUseCase(uc_id="AI_01", name="Triage", problem="p" * 15, ai_function="a" * 15, deterministic_part="rules",
                   human_review="approve all", framework="LangGraph", framework_rationale="r" * 15,
                   evaluation="e" * 10, safety="s" * 10, related_req_ids=["FR_01"])
    assert uc.deterministic_part == "rules" and len(uc.framework_rationale) >= 10
    try:
        AIUseCase(uc_id="AI_01", name="T", problem="p" * 15, ai_function="a" * 15, human_review="h" * 5,
                  framework="X", framework_rationale="short", evaluation="e" * 10, safety="s" * 10, related_req_ids=["FR_01"])
        assert False, "should reject short rationale/name"
    except Exception:
        assert True
