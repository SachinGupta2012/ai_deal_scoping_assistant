"""FR-2 schemas — PRD + functional scope. Every capability refs >=1 reviewed req ID."""
from typing import List, Literal
from pydantic import BaseModel, Field

ScopeKind = Literal["customer-requested", "AI-interpretation", "recommended-enhancement", "assumption-needs-confirmation", "out-of-scope"]


class Capability(BaseModel):
    capability_id: str = Field(pattern=r"^CAP_[0-9]{2,}$")
    name: str = Field(min_length=3)
    description: str = Field(min_length=20)
    included_req_ids: List[str] = Field(min_length=1)
    priority: Literal["High", "Medium", "Low"] = "Medium"
    dependencies: List[str] = []
    scope_kind: ScopeKind = "customer-requested"


class PRDModel(BaseModel):
    session_id: str
    overview: str = Field(min_length=20)
    business_problem: str = Field(min_length=20)
    objectives: List[str] = []
    personas: List[str] = []
    journeys: List[str] = []
    capabilities: List[Capability]
    nfr_summary: List[str] = []
    integrations: List[str] = []
    dependencies: List[str] = []
    assumptions: List[str] = []
    risks: List[str] = []
    out_of_scope: List[str] = []
    open_questions: List[str] = []
    provider: str = ""
    model: str = ""
    prompt_version: str = "prd_v1"
    scope_version_no: int = 0


class CoverageModel(BaseModel):
    session_id: str
    total_requirements: int
    covered_req_ids: List[str] = []
    uncovered_req_ids: List[str] = []
    unsupported_capabilities: List[str] = []
    unsupported_integrations: List[str] = []
    unsupported_ai_use_cases: List[str] = []
    coverage_pct: float = 0.0
